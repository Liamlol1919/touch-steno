#!/usr/bin/env python3
"""Measure the two numbers every remaining input concept is gated on.

Why this exists. Five adversarial critics killed every candidate in the design sprint, and
three of those kills shared one root cause: the instrument. Two facts were established and
neither is yet a number:

  1. U - the fraction of event frames in which more than one contact is a plausible thumb.
     The observability critic's threshold is U <= 10%. Above that, every single-thumb
     concept is dead regardless of how clever the design is. Nothing in the repository
     measures this, because the recorder stored no slot ID and no minor axis.

  2. Whether the contact ellipse carries usable classes at all. The device reports
     ABS_MT_TOUCH_MINOR and ABS_MT_ORIENTATION and the reader used to discard both. The
     derived area A = pi*major*minor/4 is roll-invariant, but whether it separates into
     distinct registers is a separate question: major reads coarsely and often spans only
     0-2.5 mm, so the product of two coarse values may not carry three levels.

Both are answerable in one short session and neither needs a new design.

Usage:
    python3 scripts/geometry_probe.py --seconds 60
    python3 scripts/geometry_probe.py --seconds 60 --json messung/geometry.json
    python3 scripts/geometry_probe.py --replay messung/geometry.jsonl

The operator's job: rest the hand naturally for part of the run, and perform a few brief
curled/flat thumb posture changes for the ellipse part. Nothing needs to be accurate.
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
import threading
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CANDIDATE_SRC = [ROOT / "src", ROOT.parent / "commindv2" / "src", ROOT.parent / "commind" / "src"]

U_THRESHOLD = 0.10                 # observability critic: fatal above this
ELLIPSE_SCREEN_MM = 0.8            # 2x the 0.4 mm median jitter; a screen, not a bound


def resolve_reader_src(explicit=None):
    for c in ([Path(explicit)] if explicit else []) + CANDIDATE_SRC:
        if (c / "wacom_touch.py").is_file():
            return c
    raise SystemExit("wacom_touch.py not found; pass --src <dir>")


def rec5(v):
    """Normalise a contact record to five fields.

    Captures taken before the reader change store [x, y, major] only. Those files
    must still analyse: the geometry comes back as unknown (-1), never as zero, so a
    legacy capture can never be mistaken for a measurement of a zero-size ellipse.
    """
    v = list(v)
    while len(v) < 5:
        v.append(-1.0)
    return tuple(v[:5])


def classify(c: dict) -> dict:
    """Summarise one SYN frame."""
    n = len(c)
    areas, aspects, majors, minors = [], [], [], []
    for _tid, raw in c.items():
        _x, _y, major, minor, orient = rec5(raw)
        majors.append(major)
        minors.append(minor)
        if major > 0 and minor > 0:
            areas.append(math.pi * major * minor / 4.0)
            aspects.append(major / minor)
    return {
        "n": n,
        "area_med": statistics.median(areas) if areas else None,
        "aspect_med": statistics.median(aspects) if aspects else None,
        "major_med": statistics.median(majors) if majors else None,
        "minor_med": statistics.median(minors) if minors else None,
        "orient_vals": sorted({round(rec5(v)[4], 3) for v in c.values()}),
    }


def record(args) -> list[dict]:
    sys.path.insert(0, str(resolve_reader_src(args.src)))
    from wacom_touch import WacomTouchReader  # lazy: keeps --replay device-free

    frames: list[dict] = []
    if not args.quiet:
        print("RESTING for 30 s: hand flat, do nothing.\n", flush=True)
        print("Then CURL exercises: about 20 times, curl the thumb tip and release,\n"
              "roughly one per second. Nothing needs to be accurate.\n", flush=True)

    def on_geometry(g: dict) -> None:
        frames.append({"t": time.monotonic(),
                       "c": {str(k): list(v) for k, v in g.items()}})

    reader = WacomTouchReader(path=args.device, on_geometry=on_geometry)
    try:
        dev = reader.open()
    except SystemExit as exc:
        print(f"ERROR: {exc}")
        return []
    print(f"Device: {dev.name} ({reader.path})")
    stop = threading.Event()
    threading.Thread(target=reader.run, kwargs={"stop": stop}, daemon=True).start()
    if not args.quiet:
        print(f"Recording {args.seconds:.0f} s. Put a hand on the pad now.\n", flush=True)
    time.sleep(args.seconds)
    stop.set()
    time.sleep(0.3)
    reader.close()
    return frames


def _stats(vals, digits=3):
    if not vals:
        return None
    s = sorted(vals)
    return {"median": round(statistics.median(s), digits),
            "p05": round(s[int(.05 * (len(s) - 1))], digits),
            "p95": round(s[int(.95 * (len(s) - 1))], digits),
            "distinct": len(set(round(x, digits) for x in s))}


def analyse(frames: list[dict]) -> dict:
    if not frames:
        return {"error": "no frames captured"}
    summ = [classify({int(k): v for k, v in f["c"].items()}) for f in frames]
    counts = Counter(s["n"] for s in summ)
    active = [s for s in summ if s["n"] > 0]
    multi = [s for s in active if s["n"] >= 2]

    # U is a LOWER bound: without slot identity every frame with 2+ contacts is
    # ambiguous, so this can only overstate ambiguity, never understate it.
    u = len(multi) / len(active) if active else 1.0

    areas = [s["area_med"] for s in active if s["area_med"]]
    aspects = [s["aspect_med"] for s in active if s["aspect_med"]]
    majors = [s["major_med"] for s in active if s["major_med"] is not None and s["major_med"] > 0]
    geometry_known = bool(areas)

    return {
        "frames": len(summ),
        "frames_with_contact": len(active),
        "contacts_per_frame_histogram": dict(sorted(counts.items())),
        "U_lower_bound": round(u, 4),
        "U_threshold": U_THRESHOLD,
        "U_verdict": ("FATAL - every single-thumb concept is dead" if u > U_THRESHOLD
                      else "survives this screen"),
        "geometry_fields_present": geometry_known,
        "major_axis_mm": _stats(majors),
        "ellipse_area_mm2": _stats(areas, 4),
        "aspect_major_over_minor": _stats(aspects),
        "notes": [
            "U is a LOWER bound: the capture carries no slot identity, so every "
            "frame with two or more contacts is counted as ambiguous.",
            "Ellipse area is roll-invariant by construction (a 90-degree roll "
            "swaps the axes and preserves their product), but these numbers only "
            "DESCRIBE the distribution. Whether it splits into registers needs a "
            "labelled curled-versus-rested run; this probe deliberately does not "
            "assume one.",
        ],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--seconds", type=float, default=60.0)
    ap.add_argument("--device")
    ap.add_argument("--src")
    ap.add_argument("--out", type=Path, help="write raw JSONL here")
    ap.add_argument("--json", type=Path, help="write the summary here")
    ap.add_argument("--replay", type=Path, help="re-analyse an existing JSONL")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    if args.replay:
        frames = [json.loads(l) for l in args.replay.read_text().splitlines() if l.strip()]
        frames = [{"t": f.get("t", i / 224.0), "c": f["c"]} for i, f in enumerate(frames)]
    else:
        frames = record(args)
        if args.out:
            args.out.write_text("".join(json.dumps(f) + "\n" for f in frames), encoding="utf-8")
            print(f"\nraw: {args.out}")

    res = analyse(frames)
    print("\n" + "=" * 68)
    print(f"frames                {res.get('frames')}")
    print(f"frames with contact   {res.get('frames_with_contact')}")
    print(f"contacts/frame        {res.get('contacts_per_frame_histogram')}")
    print(f"U (lower bound)       {res.get('U_lower_bound')}   threshold {U_THRESHOLD}")
    print(f"U verdict             {res.get('U_verdict')}")
    print(f"geometry in capture   {res.get('geometry_fields_present')}")
    print(f"major axis mm         {res.get('major_axis_mm')}")
    print(f"ellipse area mm^2     {res.get('ellipse_area_mm2')}")
    print(f"aspect major/minor    {res.get('aspect_major_over_minor')}")
    print("=" * 68)
    for n in res.get("notes", []):
        print(f"note: {n}")
    if args.json:
        args.json.write_text(json.dumps(res, indent=2), encoding="utf-8")
        print(f"summary: {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
