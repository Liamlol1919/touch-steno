#!/usr/bin/env python3
"""The decisive field-separability experiment, as one runnable session.

Why this exists. The gate measurements killed every single-thumb concept: U = 0.9491 on
s12.jsonl and 0.9980 on tempo.jsonl means no contact is identifiable, and the major axis
spans 0.5 mm so the contact ellipse cannot carry even three registers.

But a permutation-invariant field descriptor still separated the 8 sector classes of
s12.jsonl at 45.8% against a 12.5% chance level. That is the first positive result in the
project, and it has exactly one fatal weakness: those labels were produced by a THUMB
COMPASS. The field descriptor may simply be reading the thumb's deformation of the
ten-point cloud, which would make it a single-thumb concept wearing a disguise.

This session produces the control that weakness calls for: cued FIELD-LEVEL gestures that
are not directional thumb movements. If separability survives here, a field-based input
method is real. If it collapses to chance, the earlier 45.8% was a thumb artefact and the
design space is closed for good.

The gestures are whole-hand shape changes, deliberately unlike a compass:
  FINGERSPREAD   spread the fingers wide, then close them
  FIST           close all fingers into a fist, then open
  HOLLOW         cup the palm, then flatten it
  RIDGE          raise the outer edge of the hand, then lower it
  TWIST          rotate the whole hand about the forearm axis
  PINCH          bring thumb and index together, then apart
  FLAT/SPREAD    alternate the two extremes, cued one at a time
  STILL          deliberately do nothing (the null class)

STILL is included on purpose: a null class is what separates a real gesture code from a
detector that fires on drift.

Usage:
    python3 scripts/field_gesture_probe.py --seconds 40
    python3 scripts/field_gesture_probe.py --replay messung/field.jsonl \\
        --manifest messung/field.manifest.jsonl

The operator needs a hand on the pad for the whole run. Nothing needs to be accurate or
fast; the cue simply says which shape to make.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CANDIDATE_SRC = [ROOT / "src", ROOT.parent / "commindv2" / "src", ROOT.parent / "commind" / "src"]

# label -> (cue text, practice?)
GESTURES = [
    ("spread",   "SPREAD the fingers wide, then close them", False),
    ("fist",     "CLOSE all fingers into a fist, then open", False),
    ("hollow",   "CUP the palm, then flatten it", False),
    ("ridge",    "RAISE the outer edge of the hand, then lower it", False),
    ("twist",    "TWIST the whole hand about your forearm", False),
    ("pinch",    "BRING thumb and index together, then apart", False),
    ("flat",     "LAY the hand completely flat and relax", False),
    ("still",    "DO NOTHING AT ALL - this is the null class", False),
    ("spread",   "SPREAD again - practice", True),
    ("fist",     "FIST again - practice", True),
]


def resolve_reader_src(explicit=None):
    for c in ([Path(explicit)] if explicit else []) + CANDIDATE_SRC:
        if (c / "wacom_touch.py").is_file():
            return c
    raise SystemExit("wacom_touch.py not found; pass --src <dir>")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--seconds", type=float, default=4.0,
                    help="seconds per cue")
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--device")
    ap.add_argument("--src")
    ap.add_argument("--out", type=Path, default=ROOT / "messung" / "field.jsonl")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--replay", type=Path)
    ap.add_argument("--manifest", type=Path)
    args = ap.parse_args()

    if args.replay:
        if not args.manifest:
            print("--replay needs --manifest")
            return 1
        print("Re-analysing an existing capture with field_separability.py:\n")
        cmd = [sys.executable, str(ROOT / "scripts" / "field_separability.py"),
               "--session", str(args.replay), "--manifest", str(args.manifest)]
        return subprocess.call(cmd)

    sys.path.insert(0, str(resolve_reader_src(args.src)))
    from wacom_touch import WacomTouchReader

    seq = []
    for _ in range(args.reps):
        for label, cue, practice in GESTURES:
            seq.append((label, cue, practice))

    out = args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    manifest = out.with_suffix(".manifest.jsonl")

    frames: list[dict] = []

    def on_geometry(g: dict) -> None:
        frames.append({"t": time.monotonic(),
                       "c": {str(k): list(v) for k, v in g.items()}})

    reader = WacomTouchReader(path=args.device, on_geometry=on_geometry)
    try:
        dev = reader.open()
    except SystemExit as exc:
        print(f"ERROR: {exc}")
        return 1
    print(f"Device: {dev.name} ({reader.path})")
    print(f"\n{'=' * 68}")
    print("Put BOTH HANDS on the pad. Keep them there for the whole run.")
    print("These are NOT compass directions. Move the whole hand shape.")
    print(f"{len(seq)} cues at {args.seconds:.0f}s each, ~{len(seq) * args.seconds:.0f}s total.")
    print(f"{'=' * 68}\n")
    input("Press ENTER when your hands are in position...")

    stop = threading.Event()
    threading.Thread(target=reader.run, kwargs={"stop": stop}, daemon=True).start()
    log = manifest.open("w", encoding="utf-8")
    try:
        for i, (label, cue, practice) in enumerate(seq, 1):
            print(f"\n--- {i}/{len(seq)} {'UEBUNG ' if practice else ''}---")
            print(f"  >>> {cue}")
            t0 = time.monotonic()
            time.sleep(args.seconds)
            t1 = time.monotonic()
            log.write(json.dumps({"label": f"field_{label}", "cue": cue,
                                  "practice": practice, "seconds": args.seconds,
                                  "t_start": t0, "t_end": t1}) + "\n")
            log.flush()
    except KeyboardInterrupt:
        print("\naborted - files kept")
    finally:
        stop.set()
        time.sleep(0.3)
        reader.close()
        log.close()

    out.write_text("".join(json.dumps(f) + "\n" for f in frames), encoding="utf-8")
    print(f"\nraw:      {out}")
    print(f"manifest: {manifest}")
    print(f"frames:   {len(frames)}")

    print("\nNow the decisive number:\n")
    cmd = [sys.executable, str(ROOT / "scripts" / "field_separability.py"),
           "--session", str(out), "--manifest", str(manifest)]
    return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(main())
