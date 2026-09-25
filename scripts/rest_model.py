#!/usr/bin/env python3
"""Rest-state model: is a drift-relative baseline usable, and what is its noise floor?

The design premise is "drift instead of absolute position": features measured relative to
a per-contact neutral point. That only works if the residual around a *moving* baseline is
small, and MEASURED_BIOMECHANICS.md already showed a fixed baseline cannot work: a resting
finger drifts 11.5 mm within 20 s, which is larger than every displacement threshold anyone
proposed.

This script measures the alternative directly. For each contact it compares baselines:

  fixed      neutral = the first sample of the contact (what a naive setup does)
  ewma       neutral = exponential moving average with time constant tau
  recent     neutral = mean of the last W samples (sliding window)

and reports, per group (REST / MOVER, proxy labels as in MEASURED_BIOMECHANICS.md), the
distribution of the residual |p - neutral| after a warm-up, plus how many "8-frame runs
above 40 mm/s relative to the baseline" each baseline produces. The run count is the
false-trigger estimate: a baseline is only useful if it *reduces* rest runs without
shrinking mover runs.

Usage:
    python3 scripts/rest_model.py session.jsonl [session.jsonl ...]
    python3 scripts/rest_model.py --json session.jsonl ...
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kinematics  # noqa: E402

MIN_SPEED_MM_S = 40.0
MIN_RUN_FRAMES = 8
WARMUP_S = 1.0          # ignore the first second: hand placement is not a rest sample
TAUS = (0.5, 1.0, 2.0, 4.0)
WINDOWS = (9, 19, 39)


def contact_series(payload: list[dict]) -> dict[str, list[tuple[float, float, float]]]:
    series: dict[str, list[tuple[float, float, float]]] = {}
    for fr in kinematics._strip_uninit_leads(payload):
        t = float(fr["t"])
        for tid, (x, y, _m) in fr["c"].items():
            tid = str(tid)
            series.setdefault(tid, []).append((t, float(x), float(y)))
    return series


def residuals(pts, mode, param):
    """Yield (t, |p - neutral|) after warm-up, plus the per-step speed of the residual."""
    if not pts:
        return []
    out = []
    if mode == "fixed":
        t0, nx, ny = pts[0]
        for t, x, y in pts:
            if t - t0 >= WARMUP_S:
                out.append((t, math.hypot(x - nx, y - ny)))
        return out
    if mode == "ewma":
        alpha = 1.0 - math.exp(-1.0 / (param * 91.0))   # 91 Hz measured
        t0, nx, ny = pts[0]
        t_prev, prev_res = t0, 0.0
        for t, x, y in pts:
            if t - t0 < WARMUP_S:
                nx += alpha * (x - nx)
                ny += alpha * (y - ny)
                continue
            r = math.hypot(x - nx, y - ny)
            out.append((t, r))
            nx += alpha * (x - nx)
            ny += alpha * (y - ny)
        return out
    if mode == "recent":
        hist = []
        for t, x, y in pts:
            hist.append((t, x, y))
            if len(hist) > param:
                hist.pop(0)
            if len(hist) == param and t - pts[0][0] >= WARMUP_S:
                mx = sum(h[1] for h in hist) / param
                my = sum(h[2] for h in hist) / param
                out.append((t, math.hypot(x - mx, y - my)))
        return out
    raise ValueError(mode)


def runs_from_residuals(res, threshold_mm_s, dt=1.0 / 91.0):
    """Longest run of consecutive samples whose residual moves faster than threshold."""
    best = run = 0
    prev = None
    for t, r in res:
        if prev is not None:
            v = (r - prev) / dt
            run = run + 1 if abs(v) > threshold_mm_s else 0
            best = max(best, run)
        prev = r
    return best


def analyse(path: Path, mover_path: float, rest_path: float) -> dict:
    payload = kinematics._load(path)
    series = contact_series(payload)
    stats = kinematics.analyze(payload)
    rows = []
    for tid, pts in series.items():
        c = stats.get(tid)
        if not c or c["n_frames"] < 50:
            continue
        group = "MOVER" if c["path_mm"] > mover_path else (
            "REST" if c["path_mm"] < rest_path else None)
        if group is None:
            continue
        for mode, params in (("fixed", (0,)), ("ewma", TAUS), ("recent", WINDOWS)):
            for p in params:
                res = residuals(pts, mode, p)
                if not res:
                    continue

                vals = sorted(r for _t, r in res)
                rows.append({
                    "tid": tid, "group": group, "mode": mode, "param": p,
                    "res_p99_mm": quantile(vals, 0.99),
                    "res_max_mm": vals[-1],
                    "residual_run": runs_from_residuals(res, MIN_SPEED_MM_S),
                })
    return {"session": path.name, "rows": rows}


VELOCITY_GRID = (10.0, 20.0, 30.0, 40.0, 60.0)
PERSISTENCE_GRID = (1, 2, 3, 4, 5, 8)


def max_run(flags):
    best = run = 0
    for f in flags:
        run = run + 1 if f else 0
        best = max(best, run)
    return best


def separation_grid(sessions, window, min_frames=50):
    """Worst REST run vs best MOVER run for the residual feature, per threshold.

    A rule (threshold, k) is clean when rest_worst_run < k <= mover_best_run: a resting
    contact never produces k consecutive supra-threshold residual frames, while at least
    one driven contact does.
    """
    rest: dict[float, int] = {}
    mover: dict[float, int] = {}
    counts = {"REST": 0, "MOVER": 0}
    for path in sessions:
        payload = kinematics._load(path)
        series = contact_series(payload)
        stats = kinematics.analyze(payload)
        for tid, pts in series.items():
            st = stats.get(tid)
            if not st or st["n_frames"] < min_frames:
                continue
            group = ("MOVER" if st["path_mm"] > 100 else
                     "REST" if st["path_mm"] < 20 else None)
            if group is None:
                continue
            res = residuals(pts, "recent", window)
            if len(res) < 10:
                continue
            counts[group] += 1
            for thr in VELOCITY_GRID:
                flags = [False] * len(res)
                for i in range(1, len(res)):
                    v = (res[i][1] - res[i - 1][1]) * 91.0
                    flags[i] = abs(v) > thr
                run = max_run(flags)
                target = mover if group == "MOVER" else rest
                target[thr] = max(target.get(thr, 0), run)
    rows = []
    for thr in VELOCITY_GRID:
        rr, mr = rest.get(thr, 0), mover.get(thr, 0)
        for k in PERSISTENCE_GRID:
            rows.append({"velocity_mm_s": thr, "persistence_frames": k,
                         "rest_worst_run": rr, "mover_best_run": mr,
                         "clean": rr < k <= mr})
    return rows, counts


def quantile(vals, q):
    if not vals:
        return float("nan")
    i = min(len(vals) - 1, int(q * len(vals)))
    return vals[i]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("sessions", nargs="+", type=Path)
    ap.add_argument("--mover-path", type=float, default=100.0)
    ap.add_argument("--rest-path", type=float, default=20.0)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    data = [analyse(p, args.mover_path, args.rest_path) for p in args.sessions]
    if args.json:
        print(json.dumps(data, indent=2))
        return 0
    agg: dict[tuple[str, str, object], dict] = {}
    for s in data:
        for r in s["rows"]:
            key = (r["group"], r["mode"], r["param"])
            a = agg.setdefault(key, {"n": 0, "p99": [], "max": [], "runs": []})
            a["n"] += 1
            a["p99"].append(r["res_p99_mm"])
            a["max"].append(r["res_max_mm"])
            a["runs"].append(r["residual_run"])
    print(f"{'group':>6} {'baseline':>8} {'param':>6} {'n':>3} "
          f"{'res_p99_worst':>14} {'res_max_worst':>13} {'max_resid_run':>14} {'rest_fires@40mm_s':>18}")
    for (group, mode, param), a in sorted(
            agg.items(), key=lambda kv: (kv[0][0], kv[0][1], str(kv[0][2]))):
        worst_run = max(a["runs"])
        fires = sum(1 for r in a["runs"] if r >= MIN_RUN_FRAMES)
        print(f"{group:>6} {mode:>8} {str(param):>6} {a['n']:>3} "
              f"{max(a['p99']):>14.3f} {max(a['max']):>13.3f} "
              f"{worst_run:>14} {fires:>10}/{a['n']}")
    print("\nRead: a baseline earns its place only if res_max_worst drops AND")
    print("max_resid_run (8 = would fire at 40 mm/s) goes to 0 for REST while MOVER")
    print("runs stay long. 'fixed' is the naive baseline and is expected to lose.")

    for window in (9, 19, 39):
        rows, counts = separation_grid(args.sessions, window)
        clean = [r for r in rows if r["clean"]]
        print(f"\n## sliding-window baseline W={window} frames "
              f"(~{window/91*1000:.0f} ms) — residual-speed separation "
              f"[REST n={counts['REST']}, MOVER n={counts['MOVER']}]")
        print("|velocity_mm_s|persistence|rest_worst_run|mover_best_run|clean|")
        print("|---:|---:|---:|---:|---|")
        for r in rows:
            print(f"|{r['velocity_mm_s']:.0f}|{r['persistence_frames']}|"
                  f"{r['rest_worst_run']}|{r['mover_best_run']}|"
                  f"{'yes' if r['clean'] else ''}|")
        if clean:
            best = min(clean, key=lambda r: (r["persistence_frames"],
                                             r["velocity_mm_s"]))
            print(f"  -> lowest-latency clean rule: v>{best['velocity_mm_s']:.0f} mm/s "
                  f"for {best['persistence_frames']} frames "
                  f"(~{best['persistence_frames']/91*1000:.0f} ms)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
