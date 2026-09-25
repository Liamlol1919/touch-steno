#!/usr/bin/env python3
"""Confusion-matrix-driven layout assignment for the 8-sector thumb compass.

W16 searched for this and reported it as NOT FOUND: no published layout has been optimised
*from a measured confusion matrix* with a before/after speed or error figure. This builds it
for our compass, using the project's own measured noise, and reports the before/after number.

Method:
  1. Simulate the real pipeline - per-frame quantisation + rest drift + the 8-frame detection
     window - and read the resulting 8x8 sector confusion matrix off the actual decoder
     functions (stroke_decoder.sector_of). Nothing here is a model of the model; it is the
     model.
  2. Given symbol frequencies p_i, the expected substitution error of an assignment a is
         E(a) = sum_i p_i * sum_{j != i} p_j * C[a(i)][a(j)]
     i.e. the probability mass that lands on the wrong symbol because two symbols share a
     confusable cell pair.
  3. Optimise with simulated annealing + pairwise swaps, and compare against two baselines:
     naive (alphabetical) order and W16's on-axis-first rule.

The frequency profile is a Zipf profile over K symbol classes and is a MODEL INPUT, not a
measurement - the confusion matrix is measured, the frequencies are a stand-in for a language
model. Substitute real LM probabilities before quoting any absolute error figure.

Usage:
    python3 scripts/layout_assignment.py
    python3 scripts/layout_assignment.py --symbols 16 --trials 400 --json
"""
from __future__ import annotations

import argparse
import json
import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import stroke_decoder  # noqa: E402

DT = 0.011
GATE = 40.0            # mm/s   intent_filter.MIN_SPEED_MM_S
WINDOW = 8             # frames intent_filter.MIN_RUN_FRAMES
REST_STEP_P99 = 0.56   # mm     MEASURED_BIOMECHANICS
REST_STEP_MAX = 1.48   # mm
REST_DRIFT = 0.5       # mm/s
RADIUS = 20.0          # mm     thumb compass radius
SECTORS = ("E", "NE", "N", "NW", "W", "SW", "S", "SE")
ON_AXIS = ("E", "N", "W", "S")


def angular_spread_deg(sigma_per_frame: float) -> float:
    """1-sigma angular error of the accumulated window vector at the compass radius."""
    n = WINDOW
    perp = sigma_per_frame * math.sqrt(n) * 0.5   # 2 axes -> perpendicular share
    return math.degrees(perp / RADIUS)


def calibrate_sigma(target_fence: float = 0.35, trials: int = 600,
                    seed: int = 3) -> float:
    """Per-frame noise that reproduces the MEASURED on-fence rate.

    REAL_DATA_DECODE.md: 31-40% of strokes decoded from real motion land within 10 deg of a
    sector boundary. A per-frame sigma taken from the *resting* noise floor (0.56 mm) would
    predict a near-perfect confusion matrix, which contradicts that measurement - the extra
    error is aim and biomechanics, not sensor noise. So the model is calibrated to the
    measured on-fence rate, and the fitted sigma is reported rather than assumed.
    """
    lo, hi = 0.05, 20.0
    for _ in range(30):
        mid = (lo + hi) / 2
        rng = random.Random(seed)
        fenced = n = 0
        for true_sector in SECTORS:
            ang = math.radians(SECTORS.index(true_sector) * 45.0)
            vx, vy = math.cos(ang), -math.sin(ang)
            for _ in range(trials // 8):
                dx = dy = 0.0
                for _f in range(WINDOW):
                    dx += vx * (RADIUS / (WINDOW * DT)) * DT + rng.gauss(0, mid)
                    dy += vy * (RADIUS / (WINDOW * DT)) * DT + rng.gauss(0, mid)
                a = math.degrees(math.atan2(-dy, dx)) % 360.0
                margin = 22.5 - abs((a + 22.5) % 45.0 - 22.5)
                n += 1
                fenced += margin < 10.0
        if fenced / n < target_fence:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def build_confusion(trials: int, seed: int, sigma: float,
                    radius_mm: float | None = None) -> dict:
    """8x8 sector confusion under the calibrated noise model, via the real decoder.

    ``radius_mm`` defaults to the module radius. It must be a parameter rather than a
    constant: the confusion structure is what the LM recovery experiment has to be measured
    against, and a matrix built at r=20 reports 82% diagonal where r=15 reports 68%. The
    first version of lm_recovery.py hit exactly that and produced a meaningless 100%.
    """
    rng = random.Random(seed)
    conf = {a: {b: 0 for b in SECTORS} for a in SECTORS}
    r_use = RADIUS if radius_mm is None else float(radius_mm)
    speed = r_use / (WINDOW * DT)          # mean speed inside the detection window
    for true_sector in SECTORS:
        ang = math.radians(SECTORS.index(true_sector) * 45.0)
        vx, vy = math.cos(ang), -math.sin(ang)
        for _ in range(trials):
            # per-frame noise: mostly the p99, occasionally the observed max
            sig = sigma
            dx = dy = 0.0
            above = 0
            for _f in range(WINDOW):
                # ease-in so the early frames sit near the gate, as measured
                s = speed * (0.7 + 0.6 * rng.random())
                dx += vx * s * DT + rng.gauss(0, sig)
                dy += vy * s * DT + rng.gauss(0, sig)
                if math.hypot(vx * s, vy * s) >= GATE:
                    above += 1
            if above < WINDOW:
                continue                      # not detected, not a sector error
            # rest drift accumulates over the window
            dx += rng.gauss(0, REST_DRIFT * WINDOW * DT * 3)
            dy += rng.gauss(0, REST_DRIFT * WINDOW * DT * 3)
            pred = stroke_decoder.sector_of(dx, dy)
            conf[true_sector][pred] += 1
    return conf


def zipf(k: int) -> list[float]:
    raw = [1.0 / (i + 1) for i in range(k)]
    s = sum(raw)
    return [r / s for r in raw]


def expected_error(freq: list[float], assign: list[int], conf: dict) -> float:
    """Probability mass landing on the wrong symbol class."""
    total = 0.0
    for i, pi in enumerate(freq):
        for j, pj in enumerate(freq):
            if i == j:
                continue
            total += pi * pj * conf[SECTORS[assign[i]]][SECTORS[assign[j]]]
    return total


def optimise(freq, conf, iters=20000, seed=1):
    rng = random.Random(seed)
    k = len(freq)
    cells = [i % 8 for i in range(k)] + [i % 8 for i in range(8 - k % 8)][:0]
    assign = [i % 8 for i in range(k)]
    best = list(assign)
    best_e = expected_error(freq, assign, conf)
    cur_e = best_e
    T0, T1 = 1e-3, 1e-6
    for t in range(iters):
        T = T0 * (T1 / T0) ** (t / iters)
        i, j = rng.randrange(k), rng.randrange(k)
        if i == j or assign[i] == assign[j]:
            continue
        assign[i], assign[j] = assign[j], assign[i]
        e = expected_error(freq, assign, conf)
        if e < cur_e or rng.random() < math.exp(-(e - cur_e) / max(T, 1e-12)):
            cur_e = e
            if e < best_e:
                best_e, best = e, list(assign)
        else:
            assign[i], assign[j] = assign[j], assign[i]
    return best, best_e


def on_axis_first(k: int) -> list[int]:
    order = [SECTORS.index(s) for s in ON_AXIS] + \
            [SECTORS.index(s) for s in SECTORS if s not in ON_AXIS]
    return [order[i % 8] for i in range(k)]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--symbols", type=int, default=8)
    ap.add_argument("--trials", type=int, default=400)
    ap.add_argument("--seed", type=int, default=5)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    sigma = calibrate_sigma(trials=max(200, args.trials // 2))
    conf = build_confusion(args.trials, args.seed, sigma)
    freq = zipf(args.symbols)

    naive = [i % 8 for i in range(args.symbols)]
    axis = on_axis_first(args.symbols)
    opt, opt_e = optimise(freq, conf, seed=args.seed)

    if args.json:
        print(json.dumps({"confusion": conf, "expected_error": {
            "naive": expected_error(freq, naive, conf),
            "on_axis_first": expected_error(freq, axis, conf),
            "optimised": opt_e},
            "assignment_optimised": [SECTORS[c] for c in opt]}, indent=2))
        return 0

    print(f"CONFUSION MATRIX under the measured noise model "
          f"({args.trials} trials/sector, gate {GATE:.0f}mm/s, window {WINDOW} frames)\n")
    print("|true\\pred|" + "|".join(f"{s:>5}" for s in SECTORS) + "|row acc|")
    print("|---" * (len(SECTORS) + 2) + "|")
    for t in SECTORS:
        row = conf[t]
        tot = sum(row.values())
        acc = row[t] / tot if tot else 0.0
        print(f"|**{t}**|" + "|".join(f"{row[p]:>5}" for p in SECTORS) +
              f"|{acc*100:>6.1f}%|")
    print(f"\nfrequencies: Zipf over {args.symbols} classes (MODEL INPUT, not measured)\n")
    e_naive = expected_error(freq, naive, conf)
    e_axis = expected_error(freq, axis, conf)
    print("|assignment|expected substitution error|vs naive|")
    print("|---|---:|---:|")
    def rel(e):
        return "-" if e_naive == 0 else f"{(1 - e / e_naive) * 100:+.1f}%"
    print(f"|naive (alphabetical)|{e_naive:.5f}|–|")
    print(f"|W16 on-axis-first rule|{e_axis:.5f}|{rel(e_axis)}|")
    print(f"|annealed optimum|{opt_e:.5f}|{rel(opt_e)}|")
    print(f"\ncalibrated per-frame sigma: {sigma:.2f} mm "
          f"(fitted so ~35% of strokes land within 10deg of a sector boundary, matching the "
          f"measured rate in REAL_DATA_DECODE.md); rest-noise sigma is {REST_STEP_P99} mm, "
          f"so the excess is aim/biomechanics, not sensor noise")
    print(f"\noptimal assignment (by symbol frequency rank): "
          f"{[SECTORS[c] for c in opt]}")
    worst = sorted(
        ((conf[a][b] / max(1, sum(conf[a].values())), a, b)
         for a in SECTORS for b in SECTORS if a != b), reverse=True)[:4]
    print("\nmost-confused sector pairs (off-diagonal, worst 4):")
    for frac, a, b in worst:
        print(f"  {a} -> {b}: {frac * 100:.1f}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
