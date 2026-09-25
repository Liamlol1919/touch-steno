#!/usr/bin/env python3
"""Compare two no-lift segmentation strategies for the same gesture family.

The measured constraint (BENCHMARK_RESULTS.md addendum, compass_geometry.py): consecutive
gestures must return to a common reference, otherwise repositioning rotates the direction
estimate by a constant 67.5 degrees. Two ways to pay for that return:

  A. sub-gate return   the return moves slower than the 40mm/s detection gate, so it is
                       never itself an event. Cost: a 20mm return at 30mm/s takes 0.67s,
                       which caps the usable rate.
  B. fast return + reversal   the return is fast (well above the gate) and the event closes
                       on the direction reversal, which is a segmentation landmark that needs
                       no lift signal. Precedent: hierarchic marking menus have encoded
                       hierarchy through in-stroke reversals since 1993 (Kurtenbach & Buxton),
                       and W13 ranks reversal segmentation second only to dwell/timeout
                       grouping for a 91Hz no-lift surface.

This script measures both on the same synthetic task, so the trade-off is a number rather
than a preference.

Usage:
    python3 scripts/out_and_back_eval.py
    python3 scripts/out_and_back_eval.py --json
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
R = 20.0
SECTORS = ("E", "NE", "N", "NW", "W", "SW", "S", "SE")
VEC = {n: (math.cos(math.radians(i * 45)), -math.sin(math.radians(i * 45)))
       for i, n in enumerate(SECTORS)}


def build(length_s, rate_hz, return_speed_mm_s, seed=5, block_s=6.0):
    """Out stroke, then a return to centre at `return_speed_mm_s`, then rest."""
    rng = random.Random(seed)
    frames, manifest = [], []
    t = x = y = 0.0
    n_len = max(6, int(length_s / DT))
    n_ret = max(4, int(R / (return_speed_mm_s * DT)))
    n_gest = max(8, int(rate_hz * block_s))
    period = 1.0 / rate_hz

    def push():
        nonlocal t
        frames.append({"t": round(t, 6),
                       "c": {"1": [round(x, 4), round(y, 4), 2.0]}})
        t += DT

    t0 = t
    for _ in range(int(1.5 / DT)):
        x += rng.gauss(0, 0.05)
        y += rng.gauss(0, 0.05)
        push()
    manifest.append({"t_start": t0, "t_end": t, "label": "rest_0", "rest": True})

    for k in range(n_gest):
        sec = SECTORS[k % 8]
        tgt = (VEC[sec][0] * R, VEC[sec][1] * R)
        t0 = t
        for j in range(n_len):
            f = (j + 1) / n_len
            e = min(1.0, f * 1.4)
            x = tgt[0] * e + rng.gauss(0, 0.04)
            y = tgt[1] * e + rng.gauss(0, 0.04)
            push()
        manifest.append({"t_start": t0, "t_end": t, "label": f"sector_{sec}",
                         "sector": sec})
        for j in range(n_ret):
            f = (j + 1) / n_ret
            x = tgt[0] * (1 - f) + rng.gauss(0, 0.03)
            y = tgt[1] * (1 - f) + rng.gauss(0, 0.03)
            push()
        for _ in range(max(0, int((period - length_s - n_ret * DT) / DT))):
            x += rng.gauss(0, 0.05)
            y += rng.gauss(0, 0.05)
            push()
    return frames, manifest


def label_at(manifest, t):
    for rec in manifest:
        if rec.get("t_start") is not None and rec["t_start"] <= t < rec["t_end"]:
            return rec
    return None


def evaluate(frames, manifest, mode: str):
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "s.jsonl"
        with kinematics.Recorder(path, force=True) as rec:
            for fr in frames:
                rec.frame(fr["t"], {int(k): tuple(v) for k, v in fr["c"].items()})
        payload = kinematics._strip_uninit_leads(kinematics._load(path))
        rows = intent_filter.steps_of(payload)
        times = [float(f["t"]) for f in payload]
        evs = []
        if mode == "reversal":
            evs = intent_filter.detect_reversal_events(
                rows, intent_filter.MIN_SPEED_MM_S, intent_filter.MIN_RUN_FRAMES)
            spans = [(times[e["start"]], times[min(e["end"], len(times) - 1)])
                     for e in evs]
        else:
            res = intent_filter.analyse(
                path, intent_filter.MIN_SPEED_MM_S, intent_filter.MIN_RUN_FRAMES)
            spans = [(e["t_start"], e["t_end"]) for e in res["events"]]
            # Carry the mover vector for BOTH modes. Leaving it empty in persistence mode
            # silently reported accuracy 0.0 instead of measuring it - the fourth harness
            # bug of this project, same shape as the third.
            evs = [{"start": 0, "t_start": e["t_start"],
                    "dx_mm": e["mover_dx_mm"], "dy_mm": e["mover_dy_mm"]}
                   for e in res["events"]]
        cued = [r for r in manifest if r.get("sector")]
        detected = correct = 0
        for g in cued:
            span = next((s for s in spans if s[0] < g["t_end"] and s[1] > g["t_start"]),
                        None)
            if span is None:
                continue
            detected += 1
            hit = next((e for e in evs
                        if abs(e.get("t_start", times[e["start"]]) - span[0]) < 0.03),
                       None)
            if hit is not None:
                sec = stroke_decoder.sector_of(hit["dx_mm"], hit["dy_mm"])
                if sec == g["sector"]:
                    correct += 1
        rest_blocks = [(r["t_start"], r["t_end"]) for r in manifest
                       if (r.get("label") or "").startswith("rest_")]
        rest_events = sum(1 for a, b in spans
                          if any(s <= a <= e2 for s, e2 in rest_blocks))
    return {"cued": len(cued), "detected": detected,
            "rate_ratio": round(detected / len(cued), 2) if cued else None,
            "sector_acc": round(correct / detected, 2) if detected else None,
            "rest_events": rest_events, "events": len(spans)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rates", type=float, nargs="+", default=[1, 2, 3, 4])
    ap.add_argument("--length-ms", type=float, default=250.0)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    rows = []
    for rate in args.rates:
        # A: sub-gate return at 30mm/s (below the 40mm/s gate)
        fa, man_a = build(args.length_ms / 1000.0, rate, 30.0)
        a = evaluate(fa, man_a, "persistence")
        # B: fast return at 200mm/s, closed on the reversal
        fb, man_b = build(args.length_ms / 1000.0, rate, 200.0)
        b = evaluate(fb, man_b, "reversal")
        rows.append({"rate_hz": rate,
                     "A_subgate_30mm_s": a, "B_fast_200mm_s_reversal": b})
    if args.json:
        print(json.dumps({"length_ms": args.length_ms, "rows": rows}, indent=2))
        return 0
    print(f"gesture {args.length_ms:.0f}ms out-stroke, R={R:.0f}mm compass\n")
    print("|rate|A sub-gate 30mm/s: detected/acc/rest|B fast 200mm/s + reversal: "
          "detected/acc/rest|")
    print("|---:|---|---|")
    for r in rows:
        a, b = r["A_subgate_30mm_s"], r["B_fast_200mm_s_reversal"]
        print(f"|{r['rate_hz']}|{a['detected']}/{a['cued']} "
              f"acc {a['sector_acc']} rest {a['rest_events']}|"
              f"{b['detected']}/{b['cued']} acc {b['sector_acc']} "
              f"rest {b['rest_events']}|")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
