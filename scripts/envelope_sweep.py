#!/usr/bin/env python3
"""Operating envelope: detection accuracy and event rate over gesture length x cue rate.

Two design numbers in this project are currently single points: the 88 ms detection window
and the "3 Hz reliable" tempo result. Both are really functions of two variables - how long
the operator's gesture is, and how fast they repeat it - and the useful artifact is the
surface between them, not two isolated dots.

For each (gesture length, cue rate) pair this generates a small labelled session, runs the
full pipeline, and reports:
  rate_ratio    detected events/s divided by cued events/s (segmentation quality)
  sector_acc    direction accuracy on the cued sectors
  idle_fp       false events during the rest block (false-trigger cost)
  merged        fraction of cued gestures that produced no separate event (the failure mode
                at high rates: back-to-back motion merges because there is no quiet window)

Everything is synthetic but calibrated to the measured PTH-660 statistics, so this maps the
*algorithmic* envelope. Real numbers need the cued session on the device.

Usage:
    python3 scripts/envelope_sweep.py
    python3 scripts/envelope_sweep.py --json
"""
from __future__ import annotations

import argparse
import json
import math
import random
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import intent_filter  # noqa: E402
import kinematics  # noqa: E402
import stroke_decoder  # noqa: E402

DT = 0.011
REST_DRIFT = 0.5
SECTORS = ("E", "NE", "N", "NW", "W", "SW", "S", "SE")
VEC = {name: (math.cos(math.radians(i * 45)), -math.sin(math.radians(i * 45)))
       for i, name in enumerate(SECTORS)}
DETECTOR_WINDOW_S = intent_filter.MIN_RUN_FRAMES * DT


def build(length_s, rate_hz, seed, rest_s=1.5):
    """Rest block, then evenly spaced cued sector strokes, contacts continuous."""
    rng = random.Random(seed)
    frames, manifest = [], []
    x = y = 0.0
    t = 0.0
    # Fixed 6 s block per cell so every rate gets a usable sample size. The first version
    # used rate*(4+length), which left n=3 per cell at 4-6 Hz - too small to conclude from.
    block_s = 6.0
    n_gest = max(8, int(rate_hz * block_s))
    period = 1.0 / rate_hz

    def push():
        nonlocal t
        frames.append({"t": round(t, 6),
                       "c": {"1": [round(x, 4), round(y, 4), 2.0]}})
        t += DT

    # rest block
    t0 = t
    n_rest = int(rest_s / DT)
    for _ in range(n_rest):
        x += rng.gauss(0, 0.05) + REST_DRIFT * DT * rng.uniform(0.5, 1.5)
        y += rng.gauss(0, 0.05)
        push()
    manifest.append({"t_start": t0, "t_end": t, "label": "rest_0", "rest": True})

    n_len = max(3, int(length_s / DT))
    for k in range(n_gest):
        t0 = t
        target = VEC[SECTORS[k % 8]]
        sx, sy = x, y
        for j in range(n_len):
            f = (j + 1) / n_len
            ease = min(1.0, f * 1.4)
            x = sx + (target[0] * 20.0 - sx) * ease + rng.gauss(0, 0.04)
            y = sy + (target[1] * 20.0 - sy) * ease + rng.gauss(0, 0.04)
            push()
        manifest.append({"t_start": t0, "t_end": t,
                         "label": f"sector_{SECTORS[k % 8]}",
                         "sector": SECTORS[k % 8]})
        gap = period - length_s
        for _ in range(max(0, int(gap / DT))):
            x += rng.gauss(0, 0.05)
            y += rng.gauss(0, 0.05)
            push()
    return frames, manifest


def label_at(manifest, t):
    for rec in manifest:
        if rec.get("t_start") is not None and rec["t_start"] <= t < rec["t_end"]:
            return rec
    return None


def measure(frames, manifest, tmp: Path) -> dict:
    raw = tmp / "s.jsonl"
    with kinematics.Recorder(raw, force=True) as rec:
        for fr in frames:
            rec.frame(fr["t"], {int(k): tuple(v) for k, v in fr["c"].items()})
    events = intent_filter.analyse(raw, intent_filter.MIN_SPEED_MM_S,
                                   intent_filter.MIN_RUN_FRAMES)
    mapping = {}
    for s in stroke_decoder.SECTORS:
        for band, _l in stroke_decoder.BANDS:
            for k in range(4):
                tag = f"chord{k}" if k else "single"
                mapping[f"{s}|{band}|{tag}"] = s
    decoded = stroke_decoder.analyse(raw, mapping)

    # Match each cued gesture to an event whose window overlaps it. Counting events per
    # block conflates "detected" with "merged"; matching per gesture does not.
    evs = events["events"]
    cued_all = [r for r in manifest if r.get("sector")]
    matched, correct = [], 0
    for g in cued_all:
        hit = next((e for e in evs
                    if e["t_start"] < g["t_end"] and e["t_end"] > g["t_start"]), None)
        if hit is None:
            continue
        matched.append(g)
        lab = label_at(manifest, hit["t_start"]) or {}
        if lab.get("sector") == g["sector"]:
            correct += 1
    detected = len(matched)
    sector_ev = [e for e in evs
                 if (label_at(manifest, e["t_start"]) or {}).get("label", "")
                 .startswith("sector_")]
    rest_ev = [e for e in events["events"]
               if (label_at(manifest, e["t_start"]) or {}).get("label", "")
               .startswith("rest_")]
    cued = [r for r in manifest if r.get("sector")]
    span = manifest[-1]["t_end"] - manifest[0]["t_end"] if manifest else 0
    hits = 0
    for st in decoded["strokes"]:
        lab = label_at(manifest, st["t_start"])
        if lab and lab.get("sector") == st["sector"]:
            hits += 1
    return {
        "cued_gestures": len(cued_all),
        "detected": detected,
        "missed": len(cued_all) - detected,
        "rate_ratio": round(detected / len(cued_all), 2) if cued_all else None,
        "sector_acc": round(correct / detected, 3) if detected else None,
        "idle_fp": len(rest_ev),
        "span_s": round(span, 2),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--lengths-ms", type=float, nargs="+",
                    default=[100, 150, 200, 250, 350, 500])
    ap.add_argument("--rates", type=float, nargs="+",
                    default=[1, 2, 3, 4, 5, 6])
    ap.add_argument("--seed", type=int, default=11)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    rows = []
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        for L in args.lengths_ms:
            for r in args.rates:
                frames, man = build(L / 1000.0, r, args.seed)
                m = measure(frames, man, tmp)
                m["length_ms"] = L
                m["rate_hz"] = r
                m["over_window"] = L / 1000.0 > DETECTOR_WINDOW_S
                rows.append(m)
    if args.json:
        print(json.dumps({"detector_window_s": round(DETECTOR_WINDOW_S, 3),
                          "rows": rows}, indent=2))
        return 0
    print(f"detector window {DETECTOR_WINDOW_S*1000:.0f} ms; "
          f"rows are length_ms x rate_hz\n")
    print("|len_ms|rate|detected/cued|rate_ratio|sector_acc|idle_fp|")
    print("|---:|---:|---:|---:|---:|---:|")
    for m in rows:
        print(f"|{m['length_ms']}|{m['rate_hz']}|{m['detected']}/{m['cued_gestures']}|"
              f"{m['rate_ratio']}|{m['sector_acc']}|{m['idle_fp']}|")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
