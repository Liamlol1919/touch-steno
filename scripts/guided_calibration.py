#!/usr/bin/env python3
"""Guided calibration capture: the four experiments that can falsify our design.

VECTOR_DESIGN_CRITIQUE.md section 8 lists the four falsification tests. This script makes
them runnable: it cues each task on the terminal, records the tablet stream with a
timestamped task manifest, and writes a labelled JSONL so the analysis has ground truth
instead of proxy labels.

The manifest is a sidecar file (one JSON object per line) aligned to the recording:
    {"t_start": ..., "t_end": ..., "task": ..., "target": ..., "rep": ...}
The raw contact frames go to a second file; `merge` stitches them into labelled frames.

Tasks
  tempo      deliberate short strokes at 1, 2, 3, 4, 5 events/s -> the number that decides
             whether 150-250 WPM is reachable at all (CROSS_VALIDATION 1.4)
  sectors    8-way thumb compass, one sector per cue, N repetitions -> confusion matrix,
             split axes vs diagonals (CROSS_VALIDATION 1.5)
  chord      two-thumb chords on cue, alternating with single-thumb strokes -> tests
             whether a real chord is separable from the mirrored drag (the one pair class
             with r^2 = 0.10-0.25)
  noise      hands resting, no task -> the per-user rest floor, which every threshold
             must be re-derived against

Usage
  python3 scripts/guided_calibration.py --task tempo  --out messung/tempo.jsonl
  python3 scripts/guided_calibration.py --task sectors --out messung/sectors.jsonl
  python3 scripts/guided_calibration.py --merge messung/tempo.jsonl

Requires the tablet. Without a device it exits 1 with a clear message, exactly like
tools/kinematics.py --record.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kinematics  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SECTORS_8 = ("N", "NE", "E", "SE", "S", "SW", "W", "NW")
SECTOR_ANGLE = {name: i * 45.0 for i, name in enumerate(SECTORS_8)}


def resolve_reader_src(explicit):
    """Locate a directory containing wacom_touch.py.

    The reader lives in the commindv2 checkout, not in this research repo. Probe
    order: explicit --src, this repo's src/, then sibling checkouts, so calibration
    runs on the laptop without hardcoding a home path.
    """
    candidates = []
    if explicit:
        candidates.append(Path(explicit))
    candidates += [ROOT / "src", ROOT.parent / "commindv2" / "src",
                   ROOT.parent / "commind" / "src"]
    for c in candidates:
        if (c / "wacom_touch.py").is_file():
            return c
    raise SystemExit("wacom_touch.py nicht gefunden — mit --src <pfad> angeben "
                     "(gesucht: " + ", ".join(str(c) for c in candidates) + ")")


def cue(text: str, seconds: float = 1.0) -> None:
    sys.stdout.write(f"\r  {text}  ")
    sys.stdout.flush()
    time.sleep(seconds)


def build_tasks(args) -> list[dict]:
    """Each task is a dict: label, cue text, duration, and target metadata."""
    tasks: list[dict] = []
    if args.task == "tempo":
        for rate in args.rates:
            n = max(4, int(round(rate * args.seconds_per_rate)))
            tasks.append({"label": f"tempo_{rate}hz", "cue": f"{rate} EVENTS/S",
                          "seconds": args.seconds_per_rate, "rate_hz": rate,
                          "reps": n})
    elif args.task == "sectors":
        for rep in range(args.reps):
            order = SECTORS_8 if rep % 2 == 0 else tuple(reversed(SECTORS_8))
            for name in order:
                tasks.append({"label": f"sector_{name}", "cue": f"THUMB -> {name}",
                              "seconds": args.sector_seconds, "sector": name,
                              "sector_angle_deg": SECTOR_ANGLE[name],
                              "axis": name in ("N", "E", "S", "W")})
    elif args.task == "chord":
        for rep in range(args.reps):
            tasks.append({"label": "chord_both_thumbs", "cue": "BOTH THUMBS",
                          "seconds": args.chord_seconds, "chord": True})
            tasks.append({"label": "single_left_thumb", "cue": "LEFT THUMB ONLY",
                          "seconds": args.chord_seconds, "chord": False})
    elif args.task == "noise":
        tasks.append({"label": "noise_rest", "cue": "REST - DO NOT MOVE",
                      "seconds": args.rest_seconds, "rest": True})
    elif args.task == "identity":
        # Finger-identity dataset: labelled (contact-id, anatomical label) pairs. This is
        # the prerequisite for portable calibration, because cross-session transfer on
        # tracking IDs fails completely (scripts/calibration_transfer.py).
        for rep in range(args.reps):
            for f in ("thumb", "index", "middle", "ring", "little"):
                tasks.append({"label": f"identity_{f}",
                              "cue": f"LIFT + REPLACE {f.upper()}",
                              "seconds": args.identity_seconds, "finger": f})
    return tasks


def record(args, tasks: list[dict]) -> int:
    sys.path.insert(0, str(resolve_reader_src(getattr(args, "src", None))))
    from wacom_touch import WacomTouchReader  # lazy: analysis paths stay device-free

    out = Path(args.out)
    manifest = out.with_suffix(".manifest.jsonl")
    # Open the device BEFORE creating any file: a missing tablet must not leave
    # zero-byte capture artefacts behind.
    try:
        reader = WacomTouchReader(path=args.device)
        dev = reader.open()
    except SystemExit as exc:
        print(f"FEHLER: {exc}")
        return 1
    rec = kinematics.Recorder(out, force=args.force)
    log = manifest.open("w", encoding="utf-8")
    print(f"Device: {dev.name} ({reader.path})")
    print(f"Task '{args.task}' — {len(tasks)} cues, ~"
          f"{sum(t['seconds'] for t in tasks):.0f}s. Manifest: {manifest.name}")
    cue("READY", 2.0)
    try:
        for t in tasks:
            t0 = time.monotonic()
            log.write(json.dumps({"t_start": t0, "label": t["label"],
                                  "cue": t["cue"], **t}) + "\n")
            log.flush()
            cue(t["cue"], t["seconds"])
            log.write(json.dumps({"t_end": time.monotonic(), "label": t["label"]}) + "\n")
            log.flush()
            cue("...", 0.15)
    except KeyboardInterrupt:
        print("\nAbbruch.")
    rec.close()
    log.close()
    print(f"\nGeschrieben: {out} + {manifest}")
    return 0


def merge(args) -> int:
    """Attach task labels to frames, writing <out>.labelled.jsonl."""
    raw = kinematics._load(Path(args.merge))
    manifest_path = Path(args.merge).with_suffix(".manifest.jsonl")
    if not manifest_path.exists():
        print(f"FEHLER: Manifest fehlt ({manifest_path}) — erst aufnehmen.")
        return 1
    spans: list[tuple[float, float, str]] = []
    open_at: dict[str, float] = {}
    for line in manifest_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        if "t_start" in rec and "t_end" not in rec:
            open_at[rec["label"]] = rec["t_start"]
        elif "t_end" in rec and "t_start" not in rec:
            start = open_at.pop(rec["label"], None)
            if start is not None:
                spans.append((start, rec["t_end"], rec["label"]))
    labelled = Path(args.merge).with_suffix(".labelled.jsonl")
    n_lab = n_tot = 0
    with labelled.open("w", encoding="utf-8") as fh:
        for fr in raw:
            t = float(fr["t"])
            label = next((lab for s, e, lab in spans if s <= t <= e), None)
            fh.write(json.dumps({"t": t, "c": fr["c"], "task": label}) + "\n")
            n_tot += 1
            n_lab += label is not None
    print(f"{n_lab}/{n_tot} Frames mit Label -> {labelled}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--src", default=None,
                    help="directory containing wacom_touch.py (default: probe this "
                         "repo's src/ and sibling commind* checkouts)")
    ap.add_argument("--task", choices=("tempo", "sectors", "chord", "noise",
                                   "identity"))
    ap.add_argument("--out", default="messung/calibration.jsonl")
    ap.add_argument("--device", default=None)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--merge", metavar="RAW_JSONL")
    ap.add_argument("--seconds-per-rate", type=float, default=15.0)
    ap.add_argument("--rates", type=float, nargs="+",
                    default=[1.0, 2.0, 3.0, 4.0, 5.0])
    ap.add_argument("--sector-seconds", type=float, default=1.5)
    ap.add_argument("--chord-seconds", type=float, default=1.5)
    ap.add_argument("--reps", type=int, default=4)
    ap.add_argument("--rest-seconds", type=float, default=60.0)
    ap.add_argument("--identity-seconds", type=float, default=2.0)
    args = ap.parse_args()
    if args.merge:
        return merge(args)
    if not args.task:
        ap.error("--task oder --merge angeben")
    return record(args, build_tasks(args))


if __name__ == "__main__":
    raise SystemExit(main())
