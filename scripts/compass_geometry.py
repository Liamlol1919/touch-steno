#!/usr/bin/env python3
"""Compass geometry: why chained gestures need a return phase, at any usable radius.

Measured root cause (BENCHMARK_RESULTS.md addendum): on a thumb-sized compass, neighbouring
sector targets are close together, so a gesture that starts from the previous target is
dominated by *repositioning* rather than by the intended direction. The observed error was a
constant 67.5 degrees - 1.5 sectors - which collapses the classifier to 1/8 correct.

This script turns that observation into the design rule, as a function of thumb radius:

  sector_pitch(r)  distance between neighbouring sector targets on an arc of radius r
  window_path      how far the mover travels inside the 8-frame detection window
  contamination    sector_pitch / window_path: how much of the measured vector is repositioning
  residual_deg     the direction error that contamination implies, to be compared against the
                   sector half-width of 22.5 degrees

The conclusion the project acts on: at every thumb-plausible radius the contamination alone
exceeds the sector half-width, therefore **a return to a common reference point is mandatory**,
not an optimisation. The alternative - accepting it - would require r >= 30 mm, which is at the
edge of thumb reach on a 224x148 mm pad with two hands.

Usage:
    python3 scripts/compass_geometry.py
    python3 scripts/compass_geometry.py --json
    python3 scripts/compass_geometry.py --window-mm 8.8 --speed 100
"""
from __future__ import annotations

import argparse
import json
import math

SECTOR_HALF_WIDTH_DEG = 22.5      # 8-way axis-aligned compass
DEFAULT_WINDOW_MS = 88.0          # 8 frames at 91 Hz
DEFAULT_SPEED_MM_S = 100.0        # representative mover speed


def analyse(radius_mm, window_ms, speed_mm_s) -> dict:
    pitch = 2.0 * radius_mm * math.sin(math.radians(SECTOR_HALF_WIDTH_DEG))
    window_path = speed_mm_s * window_ms / 1000.0
    contamination = pitch / window_path if window_path else float("inf")
    residual = math.degrees(math.atan2(1.0, contamination))
    return {
        "radius_mm": radius_mm,
        "sector_pitch_mm": round(pitch, 1),
        "window_path_mm": round(window_path, 1),
        "contamination": round(contamination, 2),
        "residual_error_deg": round(residual, 1),
        "within_half_width": residual < SECTOR_HALF_WIDTH_DEG,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--radii", type=float, nargs="+",
                    default=[8, 10, 12, 15, 20, 25, 30, 40])
    ap.add_argument("--window-ms", type=float, default=DEFAULT_WINDOW_MS)
    ap.add_argument("--speed", type=float, default=DEFAULT_SPEED_MM_S)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    rows = [analyse(r, args.window_ms, args.speed) for r in args.radii]
    if args.json:
        print(json.dumps({"sector_half_width_deg": SECTOR_HALF_WIDTH_DEG,
                          "window_ms": args.window_ms,
                          "speed_mm_s": args.speed, "rows": rows}, indent=2))
        return 0
    print(f"8-way compass, half-width {SECTOR_HALF_WIDTH_DEG}deg, window "
          f"{args.window_ms:.0f}ms at {args.speed:.0f}mm/s "
          f"(path {args.speed*args.window_ms/1000:.1f}mm)\n")
    print("|radius_mm|sector_pitch_mm|contamination|residual_err_deg|within half-width|")
    print("|---:|---:|---:|---:|---|")
    for r in rows:
        print(f"|{r['radius_mm']}|{r['sector_pitch_mm']}|{r['contamination']}|"
              f"{r['residual_error_deg']}|{'yes' if r['within_half_width'] else 'NO'}|")
    worst_ok = [r for r in rows if r["within_half_width"]]
    print()
    if worst_ok:
        print(f"smallest radius that survives chained gestures: "
              f"{worst_ok[0]['radius_mm']} mm")
        print("Below that, a return to a common reference is mandatory.")
    else:
        print("No radius in range survives chained gestures: the return phase is "
              "mandatory everywhere.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
