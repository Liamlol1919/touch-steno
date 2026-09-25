#!/usr/bin/env python3
"""STARTUP smoke check only: this proves startup, not experimental results.

This program produces no measurement. The field-gesture, reshape, and Fitts
instruments it checks have never been run on hardware. A real-device check is
performed only when a readable Wacom finger device is present; otherwise that
hardware-start path is reported as NOT VERIFIED.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Protocol

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
HARDWARE_READ_SECONDS = 0.5


class ResultLike(Protocol):
    returncode: int
    stdout: str
    stderr: str


@dataclass(frozen=True)
class CommandResult:
    returncode: int
    stdout: str
    stderr: str


PASS = "PASS"
FAIL = "FAIL"
UNVERIFIED = "UNVERIFIED"

_DETECT_CODE = r'''
import importlib.util
import json
import sys
from pathlib import Path

module_path, module_name = sys.argv[1:]
spec = importlib.util.spec_from_file_location(module_name, module_path)
module = importlib.util.module_from_spec(spec)
sys.modules[module_name] = module
spec.loader.exec_module(module)
try:
    source = module.resolve_reader_src()
except (OSError, SystemExit) as exc:
    print(json.dumps({"reason": f"reader source is unavailable: {exc}"}))
    raise SystemExit(1)
sys.path.insert(0, str(source))
try:
    import wacom_touch
    device_path = wacom_touch.find_device()
    device = wacom_touch.WacomTouchReader(path=device_path).open()
except SystemExit:
    print(json.dumps({"reason": "no real Wacom finger device is present"}))
    raise SystemExit(1)
except PermissionError:
    print(json.dumps({"reason": "a Wacom finger device is present but is not readable"}))
    raise SystemExit(1)
except OSError as exc:
    print(json.dumps({"reason": f"no readable Wacom finger device: {exc}"}))
    raise SystemExit(1)
print(json.dumps({"path": device_path, "name": device.name}))
'''

_HARDWARE_PROBE_CODE = r'''
import importlib.util
import select
import sys
import time
from pathlib import Path

module_path, tool, device_path, output_path, module_name, read_seconds = sys.argv[1:]
read_seconds = float(read_seconds)

spec = importlib.util.spec_from_file_location(module_name, module_path)
module = importlib.util.module_from_spec(spec)
sys.modules[module_name] = module
spec.loader.exec_module(module)


class StartupBoundary(BaseException):
    def __init__(self, payload):
        super().__init__(payload)
        self.payload = payload


source = module.resolve_reader_src()
sys.path.insert(0, str(source))
import wacom_touch
from evdev import ecodes


class ProbeReader:
    last = None

    def __init__(self, *args, **kwargs):
        self.real = wacom_touch.WacomTouchReader(*args, **kwargs)
        ProbeReader.last = self

    def open(self, *args, **kwargs):
        device = self.real.open(*args, **kwargs)
        if device.name != wacom_touch.DEVICE_NAME:
            raise RuntimeError(f"not the real Wacom finger device: {device.name}")

        events_read = 0
        contact_states = 0
        last_contacts = -1
        deadline = time.monotonic() + read_seconds
        while time.monotonic() < deadline:
            remaining = deadline - time.monotonic()
            ready, _, _ = select.select([device.fd], [], [], max(0.0, remaining))
            if not ready:
                break
            for event in device.read():
                events_read += 1
                before = dict(self.real._raw)
                self.real.process(event)
                if self.real._raw != before or event.type == ecodes.EV_SYN:
                    contact_states += 1
                last_contacts = len(self.real._raw)

        if events_read == 0:
            raise RuntimeError("reader opened but emitted no events during the startup read")
        if contact_states == 0:
            raise RuntimeError("reader emitted no contact-state event during the startup read")
        contacts = max(0, last_contacts)
        payload = (
            f"STATUS: PASS device={device_path} name={device.name} "
            f"events={events_read} contact_states={contact_states} contacts={contacts}"
        )
        raise StartupBoundary(payload)


wacom_touch.WacomTouchReader = ProbeReader
common = ["--device", device_path, "--out", output_path]
try:
    if tool == "field_gesture_probe.py":
        sys.argv = [module_path, *common, "--reps", "0", "--seconds", "0"]
        module.main()
    elif tool == "reshape_probe.py":
        module.main([*common, "--reps", "0", "--ready-seconds", "0"])
    elif tool == "fitts_probe.py":
        module.main([
            "--mode", "capture", *common, "--trials", "0", "--practice", "0"
        ])
    else:
        raise RuntimeError(f"unknown instrument: {tool}")
except StartupBoundary as boundary:
    if ProbeReader.last is not None:
        ProbeReader.last.real.close()
    print(boundary.payload)
    raise SystemExit(0)
except (OSError, RuntimeError, SystemExit, ValueError) as exc:
    if ProbeReader.last is not None:
        ProbeReader.last.real.close()
    print(f"ERROR: {exc}".replace("\n", " "))
    raise SystemExit(1)
'''


def _nonempty_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def _has_traceback(text: str) -> bool:
    lowered = text.lower()
    return "traceback (most recent call last)" in lowered or "\ntraceback:" in lowered


def classify_result(
    result: ResultLike,
    expectation: str = "success",
    *,
    required_text: tuple[str, ...] = (),
    unverified_reason: str | None = None,
) -> str:
    """Classify a subprocess-style result without opening a device.

    ``unverified_reason`` is intentionally checked first: an unavailable
    hardware path is UNVERIFIED, never a silent pass.
    """
    if unverified_reason:
        return UNVERIFIED
    if expectation not in {"success", "clear-error"}:
        raise ValueError(f"unknown expectation: {expectation}")
    output = f"{result.stdout or ''}\n{result.stderr or ''}"
    if _has_traceback(output):
        return FAIL

    if expectation == "success":
        if result.returncode != 0:
            return FAIL
        return PASS if all(text.lower() in output.lower() for text in required_text) else FAIL

    if result.returncode == 0 or _nonempty_lines(result.stderr or ""):
        return FAIL
    error_lines = [line for line in _nonempty_lines(output) if line.lower().startswith("error:")]
    return PASS if len(error_lines) == 1 else FAIL


def exit_code_for_statuses(statuses: list[str]) -> int:
    """Return non-zero only when a checked property genuinely failed."""
    return 1 if FAIL in statuses else 0


def classify_hardware_result(result: ResultLike | None) -> str:
    if result is None:
        return UNVERIFIED
    return classify_result(
        result,
        "success",
        required_text=("STATUS: PASS", "device=", "events=", "contacts="),
    )


def status_line(tool: str, check: str, status: str, detail: str = "") -> str:
    suffix = f" | {detail}" if detail else ""
    return f"STARTUP CHECK | {status} | {tool} | {check}{suffix}"


def emit(tool: str, check: str, status: str, detail: str = "") -> None:
    print(status_line(tool, check, status, detail), flush=True)


def _run(command: list[str], *, timeout: float = 10.0) -> CommandResult:
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
        return CommandResult(completed.returncode, completed.stdout, completed.stderr)
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout.decode() if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        stderr = exc.stderr.decode() if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        return CommandResult(124, stdout, stderr)


def _load_module(path: Path, name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _detect_device() -> tuple[str | None, str | None]:
    field_probe = SCRIPTS / "field_gesture_probe.py"
    result = _run([
        sys.executable,
        "-c",
        _DETECT_CODE,
        str(field_probe),
        "_startup_smoke_detect_field",
    ])
    try:
        payload = json.loads(result.stdout.strip() or "{}")
    except json.JSONDecodeError:
        payload = {}
    if result.returncode == 0 and payload.get("path"):
        return str(payload["path"]), None
    reason = payload.get("reason")
    if not isinstance(reason, str) or not reason:
        reason = "no readable Wacom finger device could be detected"
    return None, reason


def _import_result(path: Path) -> CommandResult:
    code = (
        "import runpy,sys; "
        "runpy.run_path(sys.argv[1], run_name='startup_smoke_import')"
    )
    return _run([sys.executable, "-c", code, str(path)])


def _check_no_device(tool: str, path: Path, temporary: Path) -> list[str]:
    statuses: list[str] = []
    missing_device = temporary / f"{tool}.missing-device"
    missing_capture = temporary / f"{tool}.missing-capture.jsonl"
    missing_manifest = temporary / f"{tool}.missing-manifest.jsonl"
    output = temporary / f"{tool}.output.jsonl"

    if tool == "field_gesture_probe.py":
        command = [
            sys.executable, str(path), "--device", str(missing_device),
            "--out", str(output), "--reps", "0", "--seconds", "0",
        ]
    elif tool == "reshape_probe.py":
        command = [
            sys.executable, str(path), "--device", str(missing_device),
            "--out", str(output), "--reps", "1", "--seconds", "0.01",
            "--settle-seconds", "0.01", "--ready-seconds", "0",
        ]
    else:
        command = [
            sys.executable, str(path), "--mode", "capture", "--device", str(missing_device),
            "--out", str(output), "--trials", "0", "--practice", "0",
        ]

    result = _run(command)
    status = classify_result(result, "clear-error")
    if str(missing_device) not in result.stdout + result.stderr:
        status = FAIL
    statuses.append(status)
    emit(
        tool,
        "nonexistent device",
        status,
        "rejected with one clear ERROR line and no traceback"
        if status == PASS else "check did not meet the required single-error contract",
    )
    return statuses


def _check_missing_capture(temporary: Path) -> str:
    path = SCRIPTS / "field_gesture_probe.py"
    missing_capture = temporary / "field.missing-capture.jsonl"
    missing_manifest = temporary / "field.missing-manifest.jsonl"
    result = _run([
        sys.executable, str(path), "--replay", str(missing_capture),
        "--manifest", str(missing_manifest),
    ])
    status = classify_result(result, "clear-error")
    if str(missing_capture) not in result.stdout + result.stderr:
        status = FAIL
    emit(
        "field_gesture_probe.py",
        "nonexistent capture",
        status,
        "reported with one clear ERROR line and no traceback"
        if status == PASS else "missing capture was not reported by the required contract",
    )
    return status


def _probe_hardware(tool: str, device_path: str, temporary: Path) -> str:
    path = SCRIPTS / tool
    output = temporary / f"{tool}.hardware-output.jsonl"
    result = _run([
        sys.executable,
        "-c",
        _HARDWARE_PROBE_CODE,
        str(path),
        tool,
        device_path,
        str(output),
        f"_startup_smoke_hardware_{path.stem}",
        str(HARDWARE_READ_SECONDS),
    ], timeout=HARDWARE_READ_SECONDS + 5.0)
    status = classify_hardware_result(result)
    if status == PASS:
        contacts = "ZERO contacts" if "contacts=0 " in result.stdout else "reported contacts"
        detail = f"opened the real device, read events, and observed {contacts}"
    else:
        detail = "instrument could not open and read the real device without starting a session"
    emit(tool, "hardware open/read", status, detail)
    return status


def main() -> int:
    tools = (
        "field_gesture_probe.py",
        "reshape_probe.py",
        "fitts_probe.py",
    )
    all_statuses: list[str] = []

    print(status_line("all", "scope", "INFO", "startup only; no measurement is produced"))
    print(status_line(
        "all",
        "instrument history",
        "INFO",
        "the three checked instruments have never been run on hardware",
    ))

    with tempfile.TemporaryDirectory(prefix="touch-steno-startup-") as temp_name:
        temporary = Path(temp_name)
        device_path, unavailable_reason = _detect_device()

        for tool in tools:
            path = SCRIPTS / tool
            import_result = _import_result(path)
            import_status = classify_result(import_result, "success")
            if import_status == PASS and (import_result.stdout or import_result.stderr):
                import_status = FAIL
            all_statuses.append(import_status)
            emit(
                tool,
                "module import",
                import_status,
                "imported cleanly with no device present"
                if import_status == PASS else "module import did not complete cleanly",
            )

            help_result = _run([sys.executable, str(path), "--help"])
            help_status = classify_result(help_result, "success", required_text=("usage:",))
            all_statuses.append(help_status)
            emit(
                tool,
                "CLI help",
                help_status,
                "parsed and printed help without a traceback"
                if help_status == PASS else "CLI help did not parse and print cleanly",
            )

            all_statuses.extend(_check_no_device(tool, path, temporary))

        all_statuses.append(_check_missing_capture(temporary))

        if device_path is None:
            for tool in tools:
                status = UNVERIFIED
                all_statuses.append(status)
                emit(
                    tool,
                    "hardware open/read",
                    status,
                    f"hardware startup NOT VERIFIED: {unavailable_reason}; no hardware check was run",
                )
        else:
            print(status_line(
                "all",
                "real device",
                "INFO",
                f"startup read only on {device_path}; no session is started",
            ))
            for tool in tools:
                all_statuses.append(_probe_hardware(tool, device_path, temporary))

    failed = sum(status == FAIL for status in all_statuses)
    unverified = sum(status == UNVERIFIED for status in all_statuses)
    print(status_line(
        "all",
        "summary",
        FAIL if failed else "INFO",
        f"startup only; no measurement; failures={failed}; not verified={unverified}",
    ))
    return exit_code_for_statuses(all_statuses)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(status_line(
            "startup checker",
            "execution",
            FAIL,
            f"startup checker error: {str(exc).replace(chr(10), ' ')}",
        ))
        raise SystemExit(1)
