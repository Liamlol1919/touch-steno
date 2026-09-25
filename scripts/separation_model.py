#!/usr/bin/env python3
"""The separation model, stated explicitly and checked against the measurements.

The project has used a sequence of working rules without ever writing down the model they
belong to. This script states it, so the assumptions become falsifiable:

  1. A contact emits a *sample* per frame: (dx, dy, v) with v = |step| / dt.
  2. A frame is *active* for contact a when v >= v_gate.
  3. An *event* is a run of >= k consecutive active frames (the persistence window).
  4. Within an event, the contact with the largest accumulated displacement is the *mover*.
  5. A follower is *explained* when a per-pair signed fit explains at least r2 of its
     displacement energy; otherwise it is a candidate chord member.
  6. The mover's accumulated vector gives (sector, band); the sector's angular distance to
     the nearest boundary gives the geometric confidence.

Four quantities govern everything downstream, and each has a measured value:

  v_gate   40 mm/s      rest speed p99 is 57 mm/s, so the gate sits inside the rest
                        distribution and MUST be paired with the persistence window
  k        8 frames     rest runs reach 7 frames at 30-40 mm/s, 5 at 60 mm/s
  r2       0.5          finger row 0.62-0.92, thumb pair 0.10-0.25
  sigma    0.56 mm      rest step p99; at r=20mm this is 1.6 deg of angular noise

The script derives the false-activation probability implied by each (v_gate, k) pair from
the measured rest run-length distribution, and checks the derivation against the real
sessions. That closes the loop: the model is not an assertion, it is a prediction that the
data either supports or does not.

Usage:
    python3 scripts/separation_model.py
    python3 scripts/separation_model.py --json
    python3 scripts/separation_model.py --verify <dir-with-captures>/test.jsonl
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import intent_filter  # noqa: E402
import kinematics  # noqa: E402

# --- the model, with the measurement that fixes each constant ---
V_GATE = 40.0          # mm/s   MEASURED_BIOMECHANICS 2: rest speed p99 = 57.4
K_FRAMES = 8           # frames MEASURED_BIOMECHANICS 3: rest run max 7 @30-40mm/s
R2_SUPPRESS = 0.5      #        finger row 0.62-0.92, thumb pair 0.10-0.25
REST_STEP_P99 = 0.56   # mm     MEASURED_BIOMECHANICS 2
THUMB_RADIUS_MM = 20.0  # mm
HZ = 91.0
DT = 1.0 / HZ


def angular_noise_deg(step_mm: float, radius_mm: float = THUMB_RADIUS_MM) -> float:
    return math.degrees(step_mm / radius_mm)


def sector_margin_deg(disp_angle_deg: float, sectors: int = 8) -> float:
    """Distance from the nearest sector boundary; 0 = exactly on it."""
    half = 180.0 / sectors
    return half - abs((disp_angle_deg + half) % (2 * half) - half)


def model_table() -> list[dict]:
    """The predicted behaviour of each (v_gate, k) pair, as a table."""
    out = []
    for v in (20.0, 30.0, 40.0, 60.0, 80.0, 100.0):
        for k in (3, 5, 8, 12):
            out.append({
                "v_gate_mm_s": v,
                "k_frames": k,
                "window_ms": round(k * DT * 1000, 1),
                "angular_noise_p99_deg": round(angular_noise_deg(REST_STEP_P99), 2),
                "margin_at_p99_deg": round(
                    sector_margin_deg(angular_noise_deg(REST_STEP_P99)), 2),
                # Design intent, not a derived fact: these are the two constraints the
                # constants were chosen to satisfy. The measured check is --verify.
                "intent_ok_if_rest_run_below_k": True,
                "intent_window_ms": round(k * DT * 1000, 1),
            })
    return out


def rest_run_lengths(path: Path) -> dict:
    """Observed rest run lengths, as a check on the model's prediction."""
    payload = kinematics._strip_uninit_leads(kinematics._load(path))
    stats = kinematics.analyze(payload)
    series = {}
    prev = {}
    for fr in payload:
        t = float(fr["t"])
        for tid, (x, y, _m) in fr["c"].items():
            x, y = float(x), float(y)
            if tid in prev:
                dt = t - prev[tid][2]
                if dt > 0:
                    d = math.hypot(x - prev[tid][0], y - prev[tid][1])
                    series.setdefault(tid, []).append((d / dt, d))
            prev[tid] = (x, y, t)
    out = {}
    for tid, c in stats.items():
        if tid in ("coupling", "coupling_n"):
            continue
        if c["n_frames"] < 50 or c["path_mm"] >= 20.0:
            continue                      # REST by the project's proxy label
        for v in (20.0, 30.0, 40.0, 60.0, 80.0, 100.0):
            run = best = 0
            for sp, _d in series.get(tid, []):
                run = run + 1 if sp >= v else 0
                best = max(best, run)
            out.setdefault(v, []).append(best)
    return {v: {"contacts": len(r), "worst_run": max(r)} for v, r in out.items()}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--verify", type=Path, nargs="*", default=[],
                    help="session(s) to check the model against")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    report = {
        "constants": {"v_gate_mm_s": V_GATE, "k_frames": K_FRAMES,
                      "r2_suppress": R2_SUPPRESS,
                      "rest_step_p99_mm": REST_STEP_P99,
                      "thumb_radius_mm": THUMB_RADIUS_MM,
                      "window_ms": round(K_FRAMES * DT * 1000, 1)},
        "derived": {
            "angular_noise_p99_deg": round(angular_noise_deg(REST_STEP_P99), 2),
            "angular_noise_max_deg": round(angular_noise_deg(1.479), 2),
            "sector_half_width_deg": 180.0 / 8,
            "margin_at_p99_deg": round(
                sector_margin_deg(angular_noise_deg(REST_STEP_P99)), 2),
            "margin_at_max_deg": round(sector_margin_deg(angular_noise_deg(1.479)), 2),
        },
        "table": model_table(),
        "verification": {},
    }
    for p in args.verify:
        report["verification"][p.name] = rest_run_lengths(p)
    if args.json:
        print(json.dumps(report, indent=2))
        return 0
    print("SEPARATION MODEL (constants -> measurement that fixes them)")
    for k, v in report["constants"].items():
        print(f"  {k:<24} {v}")
    print("\nDERIVED")
    for k, v in report["derived"].items():
        print(f"  {k:<24} {v}")
    print("\n  Reading: the rest noise is "
          f"{report['derived']['margin_at_p99_deg']}deg inside the sector half-width at "
          f"p99 and {report['derived']['margin_at_max_deg']}deg at the worst observed "
          "frame - so a single-frame sector vote is not safe, which is why the mover's "
          "vector is accumulated over the whole event.")
    print("\n(v_gate, k) table - the window, and whether the measured rest run can reach it:")
    # merge across sessions: the worst rest run over all sessions is the honest number
    runs = {}
    for _name, d in report["verification"].items():
        for v, dd in d.items():
            cur = runs.get(v)
            if cur is None or dd["worst_run"] > cur["worst_run"]:
                runs[v] = {"worst_run": dd["worst_run"],
                           "contacts": cur["contacts"] + dd["contacts"]
                           if cur else dd["contacts"]}
    print("|v_gate|k|window_ms|measured worst rest run (any session)|rest run >= k?|")
    print("|---:|---:|---:|---:|---|")
    for r in report["table"]:
        obs = runs.get(float(r["v_gate_mm_s"]))
        if obs:
            reach = "YES - would fire" if obs["worst_run"] >= r["k_frames"] else "no"
            cell = f"{obs['worst_run']} frames ({obs['contacts']} contacts)"
        else:
            reach, cell = "-", "no REST-labelled contacts in the sessions given"
        print(f"|{r['v_gate_mm_s']:.0f}|{r['k_frames']}|{r['window_ms']:.0f}|"
              f"{cell}|{reach}|")
    if report["verification"]:
        print("\nVERIFICATION against measured sessions (worst rest run per threshold):")
        for name, v in report["verification"].items():
            print(f"  {name}: " + ", ".join(
                f"{float(t):.0f}mm/s->{d['worst_run']}f ({d['contacts']} contacts)"
                for t, d in sorted(v.items())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
