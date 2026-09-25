#!/usr/bin/env python3
"""Probe whether reshaping the hand reduces contact ambiguity.

This instrument has never been run on hardware. It exists because the
resting-hand condition produced zero contract coverage. No result may be claimed
until it runs.

Capture one cued posture at a time after the hand has settled, then re-derive the
same report offline with ``--analyse``. The raw contact stream has no anatomical
slot identity, so U is a lower bound on the fraction of usable, active frames in
which two or more contacts could be the same input.
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
import threading
import time
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from nextgen.profile_fingerprint import LAYOUT_FINGERPRINT  # noqa: E402
import raw_schema  # noqa: E402

MIN_USABLE_SAMPLES = 3
CANDIDATE_SRC = [ROOT / "src", ROOT.parent / "commindv2" / "src", ROOT.parent / "commind" / "src"]

# The order is deliberate: it starts with the known failing baseline and then
# spans isolated contact through a broad hand reshape.
POSTURES = (
    ("STILL", "LAY THE WHOLE HAND FLAT ON THE PAD AND HOLD STILL"),
    ("FIST", "CLOSE THE WHOLE HAND INTO A FIST AND HOLD IT"),
    ("ONE_FINGER", "LIFT EVERY FINGER EXCEPT THE INDEX; HOLD ONLY THE INDEX DOWN"),
    ("TWO_FINGER", "HOLD ONLY THE INDEX AND MIDDLE FINGERS DOWN; LIFT THE OTHERS"),
    ("SPREAD_HOLD", "SPREAD THE FINGERS WIDE AND HOLD THEM SPREAD ON THE PAD"),
    ("HOVER_THUMB", "HOVER THE THUMB ABOVE THE PAD; KEEP THE OTHER FINGERS UP"),
)
POSTURE_LABELS = tuple(label for label, _cue in POSTURES)
POSTURE_CUES = dict(POSTURES)


def resolve_reader_src(explicit: str | Path | None = None) -> Path:
    """Locate a directory containing the sibling checkout's reader."""
    candidates = ([Path(explicit)] if explicit else []) + CANDIDATE_SRC
    for candidate in candidates:
        if (candidate / "wacom_touch.py").is_file():
            return candidate
    raise SystemExit(
        "wacom_touch.py not found; pass --src <dir> (searched: "
        + ", ".join(str(candidate) for candidate in candidates)
        + ")"
    )


def build_tasks(reps: int = 2, seconds: float = 4.0,
                settle_seconds: float = 2.0, practice_reps: int = 0) -> list[dict]:
    """Build a balanced cue sequence, optionally preceded by practice rounds."""
    if reps <= 0 or seconds <= 0 or settle_seconds <= 0 or practice_reps < 0:
        raise ValueError("reps, seconds, and settle_seconds must be positive")
    tasks: list[dict] = []
    for repetition in range(practice_reps + reps):
        for label, cue in POSTURES:
            tasks.append({
                "label": f"reshape_{label.lower()}",
                "posture": label,
                "cue": cue,
                "practice": repetition < practice_reps,
                "seconds": float(seconds),
                "settle_seconds": float(settle_seconds),
            })
    return tasks


def write_manifest(path: Path, records: Iterable[dict]) -> int:
    """Write one complete JSON object per cue and return the number written."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8") as stream:
        for record in records:
            stream.write(json.dumps(record, sort_keys=True) + "\n")
            count += 1
    return count


def _load_jsonl(path: Path) -> list[dict]:
    records: list[dict] = []
    with Path(path).open(encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSON in {path}:{line_number}: {exc}") from exc
    return records


def _load_frames(path: Path) -> list[dict]:
    frames: list[dict] = []
    for record in _load_jsonl(path):
        try:
            frames.append(raw_schema.decode_record(record))
        except ValueError as exc:
            raise ValueError(f"invalid raw frame in {path}: {exc}") from exc
    return frames


def _usable_frames(frames: Iterable[dict], start: float, end: float) -> list[dict]:
    """Return valid frames in the half-open measured interval."""
    usable: list[dict] = []
    for frame in frames:
        try:
            timestamp = float(frame["t"])
            contacts = frame["c"]
        except (KeyError, TypeError, ValueError):
            continue
        if not isinstance(contacts, dict) or not start <= timestamp < end:
            continue
        # Five-field geometry is preserved in the capture. Empty contact sets are
        # valid samples and must remain in the contact-count mean.
        usable.append(frame)
    return usable


def _posture(record: dict) -> str:
    posture = record.get("posture")
    if isinstance(posture, str) and posture:
        return posture
    label = str(record.get("label", "UNKNOWN"))
    return label.removeprefix("reshape_").upper()


def _trial_summary(record: dict, frames: list[dict]) -> dict:
    try:
        start = float(record["t_start"])
        end = float(record["t_end"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"manifest cue has no usable measured interval: {record}") from exc
    usable = _usable_frames(frames, start, end)
    counts = [len(frame["c"]) for frame in usable]
    active = [count for count in counts if count > 0]
    multi_active = [count for count in active if count >= 2]
    return {
        "posture": _posture(record),
        "cue": record.get("cue", POSTURE_CUES.get(_posture(record), "")),
        "practice": bool(record.get("practice", False)),
        "t_start": start,
        "t_end": end,
        "settle_seconds": record.get("settle_seconds"),
        "contact_counts": counts,
        "usable_samples": len(usable),
        "insufficient_samples": len(usable) < MIN_USABLE_SAMPLES,
        "fewer_usable_samples_than_settle_interval": len(usable) < MIN_USABLE_SAMPLES,
        "contact_count_mean": statistics.fmean(counts) if counts else None,
        "frames_with_two_or_more_fraction": (
            sum(count >= 2 for count in counts) / len(counts) if counts else None
        ),
        "active_samples": len(active),
        "U_lower_bound": (
            len(multi_active) / len(active) if active else 1.0
        ),
    }


def analyse(frames: list[dict], manifest: list[dict]) -> dict:
    """Return posture summaries, rejecting every window with fewer than 3 samples."""
    by_posture: dict[str, list[dict]] = {}
    rejected_windows: list[dict] = []
    for record in manifest:
        trial = _trial_summary(record, frames)
        by_posture.setdefault(trial["posture"], []).append(trial)
        if trial["insufficient_samples"]:
            rejected_windows.append(trial)

    postures: dict[str, dict] = {}
    for posture, trials in by_posture.items():
        scoreable = [trial for trial in trials if not trial["practice"]]
        valid = [trial for trial in scoreable if not trial["insufficient_samples"]]
        summary: dict[str, Any] = {
            "trials": len(valid),
            "rejected_trials": sum(trial["insufficient_samples"] for trial in scoreable),
            "rejected": not valid,
            "usable_samples": sum(trial["usable_samples"] for trial in valid),
            "insufficient_samples": False,
        }
        if valid:
            # Pool frames, rather than averaging per-trial means: longer valid
            # windows must carry proportionally more weight in the posture row.
            pooled_counts = [count for trial in valid for count in trial["contact_counts"]]
            pooled_active = [count for count in pooled_counts if count > 0]
            summary.update({
                "mean_contact_count": statistics.fmean(pooled_counts),
                "frames_with_two_or_more_fraction": (
                    sum(count >= 2 for count in pooled_counts) / len(pooled_counts)
                ),
                "U_lower_bound": (
                    sum(count >= 2 for count in pooled_active) / len(pooled_active)
                    if pooled_active else 1.0
                ),
            })
        elif not scoreable:
            summary["reason"] = "rejected: no non-practice measured windows"
        else:
            summary["reason"] = (
                f"rejected: every measured window has fewer than {MIN_USABLE_SAMPLES} usable samples"
            )
        postures[posture] = summary

    return {
        "layout_fingerprint": LAYOUT_FINGERPRINT,
        "postures": postures,
        "rejected_windows": rejected_windows,
        "note": (
            "U is a LOWER bound because the capture carries no slot identity: "
            "each active frame with two or more contacts is counted as ambiguous."
        ),
    }


# American spelling is a small compatibility convenience for callers.
analyze = analyse


def print_report(report: dict) -> None:
    """Print the same human-readable table for live and offline analysis."""
    print("posture       trials  mean contacts  frames >=2  U lower bound")
    print("-------------  ------  -------------  -----------  -----------")
    for posture in POSTURE_LABELS:
        summary = report["postures"].get(posture)
        if summary is None:
            continue
        if summary["rejected"]:
            print(f"{posture:<13}  REJECTED ({summary['reason']})")
            continue
        print(
            f"{posture:<13}  {summary['trials']:>6}  "
            f"{summary['mean_contact_count']:>13.3f}  "
            f"{summary['frames_with_two_or_more_fraction']:>11.3f}  "
            f"{summary['U_lower_bound']:>13.3f}"
        )
    print("\n" + report["note"])


def _ready_countdown(seconds: float = 3.0) -> None:
    for remaining in range(int(seconds), 0, -1):
        print(f"READY: {remaining}", flush=True)
        time.sleep(1.0)
    print("READY: begin the posture after each cue's settle interval.", flush=True)


def record(args: argparse.Namespace, tasks: list[dict] | None = None) -> int:
    """Capture five-field geometry frames and a complete cue manifest."""
    tasks = tasks or build_tasks(args.reps, args.seconds, args.settle_seconds,
                                 args.practice_reps)
    try:
        source = resolve_reader_src(args.src)
    except SystemExit as exc:
        print(f"ERROR: {exc}")
        return 1
    sys.path.insert(0, str(source))
    from wacom_touch import WacomTouchReader  # lazy: analysis paths stay device-free

    output = Path(args.out)
    manifest_path = output.with_suffix(".manifest.jsonl")
    if output.exists() and not args.force:
        print(f"ERROR: {output} exists; use --force to replace it")
        return 1
    if manifest_path.exists() and not args.force:
        print(f"ERROR: {manifest_path} exists; use --force to replace it")
        return 1

    frames: list[dict] = []

    def on_geometry(contacts: dict) -> None:
        # Do not reduce geometry to the three-field contact callback: the minor
        # axis and orientation are part of this instrument's raw data.
        frames.append(raw_schema.encode_frame(
            time.monotonic(), {str(key): list(value) for key, value in contacts.items()}
        ))

    # Open the device before creating files, so a missing tablet leaves no
    # zero-byte capture artefacts behind.
    try:
        reader = WacomTouchReader(path=args.device, on_geometry=on_geometry)
        device = reader.open()
    except (OSError, SystemExit) as exc:
        print(f"ERROR: {exc}")
        return 1
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    stop = threading.Event()
    thread = threading.Thread(target=reader.run, kwargs={"stop": stop}, daemon=True)
    print(f"Device: {device.name} ({reader.path})")
    print(f"Raw capture: {output}")
    print(f"Manifest: {manifest_path}")
    _ready_countdown(args.ready_seconds)

    records: list[dict] = []
    try:
        thread.start()
        with manifest_path.open("w", encoding="utf-8") as manifest_stream:
            for index, task in enumerate(tasks, 1):
                print(f"\n--- {index}/{len(tasks)} ---")
                print(f"POSTURE: {task['posture']}")
                print(f">>> {task['cue']}")
                print(
                    f"SETTLE: hold the WHOLE HAND in this posture for "
                    f"{task['settle_seconds']:.1f} s before measurement."
                )
                time.sleep(task["settle_seconds"])
                print("MEASURE NOW: keep the posture; do not change it.", flush=True)
                t_start = time.monotonic()
                time.sleep(task["seconds"])
                t_end = time.monotonic()
                trial = {**task, "t_start": t_start, "t_end": t_end}
                # The settle interval establishes the posture; the measured
                # window must contain at least three complete usable samples.
                measured = _usable_frames(frames, t_start, t_end)
                trial["usable_samples"] = len(measured)
                trial["insufficient_samples"] = len(measured) < MIN_USABLE_SAMPLES
                trial["fewer_usable_samples_than_settle_interval"] = trial["insufficient_samples"]
                trial["window_sample_floor"] = MIN_USABLE_SAMPLES
                manifest_stream.write(json.dumps(trial, sort_keys=True) + "\n")
                manifest_stream.flush()
                records.append(trial)
                print(f"window samples: {len(measured)}")
    except KeyboardInterrupt:
        print("\nAborted; retaining the completed manifest and frames.")
    finally:
        stop.set()
        thread.join(timeout=2.0)
        reader.close()

    output.write_text("".join(json.dumps(frame) + "\n" for frame in frames), encoding="utf-8")
    print(f"\nWrote {len(frames)} raw frames and {len(records)} manifest cues.")
    report = analyse(frames, records)
    print_report(report)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--analyse", nargs=2, metavar=("CAPTURE", "MANIFEST"),
                        type=Path, help="re-analyse an existing capture offline")
    parser.add_argument("--out", type=Path, default=ROOT / "messung" / "reshape.jsonl")
    parser.add_argument("--device", default=None)
    parser.add_argument("--src", default=None)
    parser.add_argument("--seconds", type=float, default=4.0)
    parser.add_argument("--settle-seconds", type=float, default=2.0)
    parser.add_argument("--reps", type=int, default=2)
    parser.add_argument("--practice-reps", type=int, default=0)
    parser.add_argument("--ready-seconds", type=float, default=3.0)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    if args.analyse:
        capture, manifest = args.analyse
        try:
            report = analyse(_load_frames(capture), _load_jsonl(manifest))
        except (OSError, ValueError) as exc:
            parser.error(str(exc))
        print_report(report)
        return 0
    try:
        return record(args)
    except ValueError as exc:
        parser.error(str(exc))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
