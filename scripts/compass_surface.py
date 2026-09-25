#!/usr/bin/env python3
"""The compass-radius design surface: accuracy, contamination, and cycle cost.

Two measured effects move with the radius of the thumb compass, and the design question is
where they meet:

  * Decoding accuracy IMPROVES with radius. The per-frame noise is fixed (fitted 2.03 mm/frame
    from the measured 35% on-fence rate), so a longer arc gives more signal per frame.
    LAYOUT_ASSIGNMENT.md.
  * Repositioning contamination IMPROVES with radius too, because the displacement between
    neighbouring sector targets grows while the detection-window path does not.
    compass_geometry.py.
  * The return leg gets LONGER with radius, which costs cycle time, and the cycle is what
    sets the event rate.

The only cost is time, and the trade is not obvious from any single measurement - so this
script prints the surface and leaves the choice to the cued session.

Usage:
    python3 scripts/compass_surface.py
    python3 scripts/compass_surface.py --json
"""
from __future__ import annotations

import argparse
import json
import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import compass_geometry as cg  # noqa: E402
import stroke_decoder  # noqa: E402

SECTORS = ("E", "NE", "N", "NW", "W", "SW", "S", "SE")
VEC = {name: (math.cos(math.radians(i * 45)), -math.sin(math.radians(i * 45)))
       for i, name in enumerate(SECTORS)}
SIGMA = 2.03        # mm/frame, fitted to the measured 35% on-fence rate
DT = 0.011
WINDOW = 8          # frames, the measured evidence floor
RETURN_MM_S = 600.0


def accuracy(radius_mm: float, trials: int, seed: int) -> float:
    rng = random.Random(seed)
    ok = 0
    for _ in range(trials):
        ti = rng.randrange(8)
        vx, vy = VEC[SECTORS[ti]]
        dx = dy = 0.0
        for _ in range(WINDOW):
            dx += vx * (radius_mm / (WINDOW * DT)) * DT + rng.gauss(0, SIGMA)
            dy += vy * (radius_mm / (WINDOW * DT)) * DT + rng.gauss(0, SIGMA)
        ok += stroke_decoder.sector_of(dx, dy) == SECTORS[ti]
    return ok / trials


def row(radius_mm: float, trials: int, seed: int) -> dict:
    geo = cg.analyse(radius_mm, cg.DEFAULT_WINDOW_MS, cg.DEFAULT_SPEED_MM_S)
    ret_ms = 2.0 * radius_mm / RETURN_MM_S * 1000.0
    cycle_ms = WINDOW * DT * 1000.0 + ret_ms
    return {
        "radius_mm": radius_mm,
        "accuracy": round(accuracy(radius_mm, trials, seed), 3),
        "sector_pitch_mm": geo["sector_pitch_mm"],
        "contamination": geo["contamination"],
        "contamination_error_deg": geo["residual_error_deg"],
        "return_ms": round(ret_ms, 1),
        "cycle_limit_hz": round(1000.0 / cycle_ms, 2),
        "wpm_equiv_1p5_syll": round((1000.0 / cycle_ms) / 1.5 * 60.0, 0),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--radii", type=float, nargs="+",
                    default=[8, 10, 12, 15, 20, 25, 30, 35, 40, 50])
    ap.add_argument("--trials", type=int, default=4000)
    ap.add_argument("--seed", type=int, default=11)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    rows = [row(r, args.trials, args.seed) for r in args.radii]
    if args.json:
        print(json.dumps({"sigma_mm_per_frame": SIGMA, "window_frames": WINDOW,
                          "return_mm_s": RETURN_MM_S, "rows": rows}, indent=2))
        return 0
    print(f"compass surface: sigma {SIGMA} mm/frame (fitted to the measured 35% on-fence")
    print(f"rate), window {WINDOW} frames ({WINDOW*DT*1000:.0f} ms), return "
          f"{RETURN_MM_S:.0f} mm/s\n")
    print("|r_mm|accuracy|sector_pitch_mm|contamination|contam_err_deg|return_ms|"
          "cycle_hz|WPM_equiv|")
    print("|---:|---:|---:|---:|---:|---:|---:|---:|")
    for r in rows:
        print(f"|{r['radius_mm']:.0f}|{r['accuracy']:.3f}|{r['sector_pitch_mm']:.1f}|"
              f"{r['contamination']:.2f}|{r['contamination_error_deg']:.1f}|"
              f"{r['return_ms']:.0f}|{r['cycle_limit_hz']:.2f}|"
              f"{r['wpm_equiv_1p5_syll']:.0f}|")
    best = max(rows, key=lambda r: r["accuracy"] - 0.01 * r["cycle_limit_hz"])
    print(f"\naccuracy saturates around r={max(rows, key=lambda r: r['accuracy']-0.01*r['cycle_limit_hz'])['radius_mm']:.0f}mm;")
    print("the cycle cost grows linearly with r because the return leg does.")
    print("This surface is derived from the measured noise, not from literature - the")
    print("cued sector session is what decides the operating point.")
    del best
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
