#!/usr/bin/env python3
"""Calibration honesty check: fit coupling on one session, apply it to another.

`intent_filter.analyse` currently estimates the per-pair regressions on the same session it
decodes, which flatters the suppression numbers. A real deployment calibrates once and then
decodes, so the honest question is: how much of the suppression survives when the fit comes
from a *different* session?

Method: for every ordered pair present in both sessions, fit the signed slope on session A,
apply it on session B (residual = step_b - s*step_a), and compare with (a) the fit made on B
itself and (b) no fit at all. A calibration is only useful if cross-session suppression is
still clearly better than the uncalibrated baseline.

FINDING (measured, 2026-09-25): cross-session transfer of the per-pair coupling calibration
does not work on tracking IDs. Contact IDs are unique per touch and are never reused across
sessions -- the ten-finger session used IDs 55-74, the index session 136-150 -- so a fit
learned in one session has *no counterpart* in another. Every cross-session lookup in the
table below comes back empty.

Consequence for the architecture: the coupling model is per-session unless contact identity
is anatomical rather than evdev-transient. Three ways out, in order of cost:
  1. recalibrate at the start of every session (scripts/guided_calibration.py) -- cheap, and
     what the current MVP assumes;
  2. identify contacts by position relative to a per-session hand frame instead of by ID --
     removes the ID problem, costs a small hand-localisation step;
  3. solve finger identity properly (the SpeciFingers / CapContact line of work) -- the only
     option that makes the model portable across sessions and postures, and the most
     expensive. Note that this is exactly the capability agent 1's report lists as "open" for
     the PTH-660.

Usage:
    python3 scripts/calibration_transfer.py calibrate.jsonl apply.jsonl [apply2.jsonl ...]
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kinematics  # noqa: E402

MIN_FRAMES = 40


def steps_of(payload):
    prev = {}
    rows = []
    for fr in payload:
        t = float(fr["t"])
        row = {}
        for tid, (x, y, _m) in fr["c"].items():
            x, y = float(x), float(y)
            old = prev.get(tid)
            if old is not None and t - old[2] > 0:
                row[tid] = (x - old[0], y - old[1])
            prev[tid] = (x, y, t)
        rows.append(row)
    return rows


def pair_samples(rows):
    """(mover, follower) -> [ (ax, ay, bx, by) ] over frames where mover leads."""
    acc = {}
    for row in rows[1:]:
        if not row:
            continue
        a = max(row, key=lambda k: math.hypot(*row[k]))
        for b, (bx, by) in row.items():
            if b == a:
                continue
            if math.hypot(bx, by) <= 0.01:
                continue
            ax, ay = row[a]
            if math.hypot(ax, ay) <= 0.01:
                continue
            acc.setdefault((a, b), []).append((ax, ay, bx, by))
    return acc


def fit(pts):
    m = 2 * len(pts)
    ax = [p[0] for p in pts] + [p[1] for p in pts]
    bx = [p[2] for p in pts] + [p[3] for p in pts]
    ma, mb = sum(ax) / m, sum(bx) / m
    cov = sum((ax[i] - ma) * (bx[i] - mb) for i in range(m))
    va = sum((v - ma) ** 2 for v in ax)
    vb = sum((v - mb) ** 2 for v in bx)
    r = cov / math.sqrt(va * vb) if va > 0 and vb > 0 else 0.0
    return (cov / va if va > 0 else 0.0), r, len(pts)


def residual_energy(pts, slope):
    """RMS follower step before and after subtracting slope*leader."""
    raw = sq = 0.0
    n = 0
    for ax, ay, bx, by in pts:
        raw += bx * bx + by * by
        rx, ry = bx - slope * ax, by - slope * ay
        sq += rx * rx + ry * ry
        n += 1
    if n == 0:
        return float("nan"), float("nan")
    return math.sqrt(raw / n), math.sqrt(sq / n)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("calibrate", type=Path)
    ap.add_argument("apply", nargs="+", type=Path)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    cal = kinematics._strip_uninit_leads(kinematics._load(args.calibrate))
    cal_fits = {k: fit(v) for k, v in pair_samples(steps_of(cal)).items()
                if len(v) >= MIN_FRAMES}
    report = []
    for target in args.apply:
        pay = kinematics._strip_uninit_leads(kinematics._load(target))
        samples = pair_samples(steps_of(pay))
        rows = []
        for key, pts in sorted(samples.items(), key=lambda kv: -len(kv[1])):
            if len(pts) < MIN_FRAMES:
                continue
            s_self, r_self, n = fit(pts)
            s_cal = cal_fits[key][0] if key in cal_fits else None
            raw, res_self = residual_energy(pts, s_self)
            res_cal = residual_energy(pts, s_cal)[1] if s_cal is not None else None
            rows.append({"mover": key[0], "follower": key[1], "n_frames": n,
                         "slope_own": round(s_self, 3), "r_own": round(r_self, 3),
                         "slope_calib": round(s_cal, 3) if s_cal is not None else None,
                         "raw_rms_mm": round(raw, 4),
                         "residual_own_rms_mm": round(res_self, 4),
                         "residual_calib_rms_mm": round(res_cal, 4) if res_cal else None,
                         "calib_in_pairs": s_cal is not None})
        report.append({"apply": target.name, "rows": rows})
    if args.json:
        print(json.dumps({"calibrate": args.calibrate.name, "report": report},
                         indent=2))
        return 0
    print(f"calibration source: {args.calibrate.name} ({len(cal_fits)} pair fits)")
    for r in report:
        print(f"\n## applied to {r['apply']}")
        print("|mover|follower|n|slope_own|r_own|slope_calib|raw_rms|res_own|res_calib|")
        print("|---|---|---:|---:|---:|---:|---:|---:|---:|")
        for row in r["rows"][:20]:
            print(f"|{row['mover']}|{row['follower']}|{row['n_frames']}|"
                  f"{row['slope_own']}|{row['r_own']}|"
                  f"{row['slope_calib'] if row['slope_calib'] is not None else '-'}|"
                  f"{row['raw_rms_mm']}|{row['residual_own_rms_mm']}|"
                  f"{row['residual_calib_rms_mm'] if row['residual_calib_rms_mm'] else '-'}|")
    print("\nRead: residual_calib close to residual_own means calibration transfers;")
    print("residual_calib close to raw_rms means it does not. Pairs with '-' have no")
    print("calibration counterpart, which is the per-user cost of a different session.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
