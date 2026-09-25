#!/usr/bin/env python3
"""One-shot session runner: get every cued measurement out of one hour with the user.

Why this exists. The session plan written by hand had four commands whose flags did not
exist, and it would have failed at the first one. This runner verifies each step, records
what happened, and **keeps going when a step fails** — because a session interrupted at minute
40 must still yield the blocks that already completed.

It also refuses to pretend: if the tablet is absent, the hardware-dependent steps are marked
SKIPPED rather than silently producing empty files, and the summary says so.

Usage:
    python3 scripts/session_runner.py --quick          # highest-value blocks, including bimanual
    python3 scripts/session_runner.py                  # full sequence
    python3 scripts/session_runner.py --out messung --json report.json
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent

DRY_RUN = False

# Issue #17 is a comfort-vs-accuracy decision and the comfort half has no instrument
# anywhere in the repo. These are the questions that actually decide it, asked once per
# radius block, answered in the user's own words.
COMFORT_TEMPLATE = {
    "_instructions": "Fill one block per radius run, immediately after it, before "
                     "talking about accuracy. Ratings 1-5, 5 = effortless. Verbatim "
                     "notes matter more than the numbers.",
    "blocks": {
        "r12": {
            "radius_mm": 12,
            "comfort_1_5": None,
            "cramp_where": None,
            "anchor_held": None,
            "return": "quick flick / slow deliberate / mixed",
            "could_repeat_without_cue": None,
            "notes": None,
        },
        "r20": {
            "radius_mm": 20,
            "comfort_1_5": None,
            "cramp_where": None,
            "anchor_held": None,
            "return": "quick flick / slow deliberate / mixed",
            "could_repeat_without_cue": None,
            "notes": None,
        },
    },
    "undo": {
        "_instructions": "After the correction block: could you perform the undo "
                         "gesture on request, unaided, within 10 minutes of practice?",
        "learned_unaided": None,
        "seconds_to_first_success": None,
        "notes": None,
    },
    "free_text": "Anything about anchors, hand position, or what felt learnable "
                 "that no question above asked for.",
}


def have_tablet() -> str | None:
    """Return the finger device path if present, else None."""
    try:
        import evdev  # type: ignore
        for path in evdev.list_devices():
            try:
                dev = evdev.InputDevice(path)
            except OSError:
                continue
            name = dev.name
            dev.close()
            if "Wacom" in name and "Finger" in name:
                return path
    except Exception:
        return None
    return None


def run(label: str, cmd: list[str], results: list, timeout: int = 300,
        dry_run: bool | None = None) -> bool:
    if dry_run is None:
        dry_run = DRY_RUN
    if dry_run:
        print(f"[dry] {label}: {' '.join(cmd)}")
        results.append({"step": label, "cmd": cmd, "ok": None, "dry": True})
        return True
    t0 = time.monotonic()
    print(f"\n>>> {label}\n    {' '.join(cmd)}", flush=True)
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        ok = p.returncode == 0
        tail = (p.stdout or p.stderr or "").strip().splitlines()[-3:]
    except subprocess.TimeoutExpired:
        ok, tail = False, ["TIMEOUT"]
    dt = time.monotonic() - t0
    print(f"    {'OK' if ok else 'FAILED'} in {dt:.0f}s")
    for line in tail:
        print(f"    | {line}")
    results.append({"step": label, "cmd": cmd, "ok": ok, "seconds": round(dt, 1),
                     "tail": tail})
    return ok

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=Path("messung"))
    ap.add_argument("--quick", action="store_true",
                    help="noise, palm, sectors at both radii, bimanual coupling, tempo - the decisive blocks")
    ap.add_argument("--json", type=Path)
    ap.add_argument("--device")
    ap.add_argument("--session-id", default=None,
                    help="pseudonymous ID stored in bimanual cue metadata")
    ap.add_argument("--dominant-hand", choices=("left", "right", "ambidextrous", "unknown"),
                    default="unknown")
    ap.add_argument("--dry-run", action="store_true",
                    help="print every command without running anything")
    ap.add_argument("--comfort", type=Path,
                    help="write the comfort questionnaire template here; the operator "
                         "or agent fills it in from the user's own answers. The "
                         "subjective half of issue #17 exists nowhere else.")
    args = ap.parse_args()
    global DRY_RUN
    DRY_RUN = args.dry_run
    out = args.out
    out.mkdir(parents=True, exist_ok=True)
    results: list[dict] = []

    tablet = args.device or have_tablet()
    dev = tablet
    if args.dry_run and not dev:
        dev = "DRY_RUN_DEVICE"
        print("dry-run: no tablet required; printing hardware plan")
    if not dev:
        print("NO TABLET FOUND (expected 'Wacom Intuos Pro M Finger').")
        print("Hardware steps will be SKIPPED. The stopwatch correction test still works:")
        print(f"  python3 {SCRIPTS/'correction_timing.py'} --plan --words 20")
        print(f"  python3 {SCRIPTS/'correction_timing.py'} --record --out {out/'correction.json'}")
        results.append({"step": "device", "ok": False,
                        "detail": "no Wacom finger device"})
    else:
        print(f"tablet: {tablet or 'DRY_RUN_DEVICE'}")
        run("audit input (5 s)", ["python3", str(SCRIPTS / "audit_input.py"),
                                  "--watch", "--seconds", "5", "--device", dev], results)

        session_id = args.session_id or f"session-{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}"
        g = ["python3", str(SCRIPTS / "guided_calibration.py"), "--device", dev]
        run("rest floor 60 s", g + ["--task", "noise", "--out", str(out / "noise.jsonl")],
            results, timeout=180)
        run("palm 60 s", g + ["--task", "palm", "--out", str(out / "palm.jsonl")],
            results, timeout=180)
        # The radius comparison is the decision in issue #17. Both arms, small radius first.
        for r in (12, 20):
            run(f"sectors r={r} mm", g + ["--task", "sectors", "--reps", "4",
                                          "--radius-mm", str(r),
                                          "--out", str(out / f"sectors-r{r}.jsonl")],
                results, timeout=300)
        run("bimanual 1/2/3 Hz", g + ["--task", "bimanual",
                                       "--bimanual-rates", "1", "2", "3",
                                       "--bimanual-seconds", "40",
                                       "--bimanual-rest-seconds", "10",
                                       "--session-id", session_id,
                                       "--dominant-hand", args.dominant_hand,
                                       "--out", str(out / "bimanual-coupling.jsonl")],
            results, timeout=360)
        run("tempo 1-5 Hz", g + ["--task", "tempo", "--rates", "1", "2", "3", "4", "5",
                                  "--out", str(out / "tempo.jsonl")],
            results, timeout=300)
        run("correction on pad", g + ["--task", "correction",
                                      "--out", str(out / "correction.jsonl")],
            results, timeout=300)
        if not args.quick:
            run("chord", g + ["--task", "chord", "--out", str(out / "chord.jsonl")],
                results, timeout=300)
            run("identity", g + ["--task", "identity", "--reps", "3",
                                 "--out", str(out / "identity.jsonl")], results, timeout=300)

    # stopwatch part: no tablet needed
    run("stopwatch plan", ["python3", str(SCRIPTS / "correction_timing.py"),
                           "--plan", "--words", "20",
                           "--out", str(out / "correction_plan.json")], results)

    # The rest floor is a separate deliverable from the raw noise/palm files.
    rest_files = [str(out / n) for n in ("noise.jsonl", "palm.jsonl")
                  if (out / n).exists()]
    if rest_files:
        run("rest floor (from noise+palm)", ["python3", str(SCRIPTS / "rest_calibration.py"),
                                             "--rest", *rest_files, "--user-label", "session",
                                             "--out", str(out / "rest.json")],
            results, timeout=180)

    if args.comfort:
        args.comfort.write_text(json.dumps(COMFORT_TEMPLATE, indent=2), encoding="utf-8")
        print(f"\ncomfort questionnaire written to {args.comfort}")
        print("Ask these after each sectors block and fill the answers in verbatim.")

    ev = ["python3", str(SCRIPTS / "evaluate_session.py")]
    for name in ("sectors-r12", "sectors-r20", "tempo"):
        p = out / f"{name}.jsonl"
        if p.exists():
            run(f"evaluate {name}", ev + [str(p)], results, timeout=180)

    ok = sum(1 for r in results if r.get("ok") is True)
    bad = [r["step"] for r in results if r.get("ok") is False]
    summary = {"out": str(out), "steps": results, "ok": ok, "failed": bad,
               "tablet": tablet}
    if args.json:
        args.json.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("\n" + "=" * 64)
    print(f"session summary: {ok} ok, {len(bad)} failed -> {bad}")
    print("raw JSONL stays local (biometric). Do not commit messung/.")
    print("=" * 64)
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
