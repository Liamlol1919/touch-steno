#!/usr/bin/env python3
"""Real PTH-660 evidence: measured separation between resting and moving contacts.

Replaces the *guessed* thresholds in EXPERIMENT_PROTOCOL.md / SYNTHETIC_BASELINE.md
with numbers measured on this machine. Pure stdlib; reads the JSONL produced by
``tools/kinematics.py --record`` (one JSON object per SYN frame).

Method (and its limits, stated up front):
  * Proxy labels are *contact level*, not per-frame intent labels. A contact is
    labelled MOVER if its session path exceeds ``--mover-path`` (default 100 mm)
    and REST if it stays below ``--rest-path`` (default 20 mm). Contacts in
    between are MID and are excluded from every statistic. The label comes from
    what the operator was told to do during that session (move a finger / keep
    hands still), not from ground-truth keypress annotation.
  * Therefore the output answers two questions that *are* robust under those
    labels: (a) what does a resting finger actually emit, (b) what separates that
    from a finger that is being driven. It does NOT measure keystroke accuracy.

Usage:
    python3 scripts/real_session_evidence.py SESSION.jsonl [SESSION.jsonl ...]
    python3 scripts/real_session_evidence.py --json SESSION.jsonl ...
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kinematics  # noqa: E402

# Velocity thresholds (mm/s) evaluated for the persistence analysis. Chosen to
# bracket the measured resting-finger p99 (~26 mm/s) and the mover p99 (~100+ mm/s).
VELOCITY_GRID = (10.0, 20.0, 30.0, 40.0, 60.0, 80.0, 100.0)
# Minimum number of consecutive supra-threshold frames for a candidate event.
PERSISTENCE_GRID = (1, 2, 3, 5, 8, 12)


def load(path: Path) -> list[dict]:
    return kinematics._strip_uninit_leads(kinematics._load(path))


def quantile(sorted_vals: list[float], q: float) -> float:
    if not sorted_vals:
        return float("nan")
    i = min(len(sorted_vals) - 1, int(q * len(sorted_vals)))
    return sorted_vals[i]


def per_frame_series(payload: list[dict]) -> dict[str, list[tuple[float, float]]]:
    """tid -> [(speed_mm_s, step_mm), ...] for consecutive frames only."""
    out: dict[str, list[tuple[float, float]]] = {}
    prev: dict[str, tuple[float, float, float]] = {}
    for fr in payload:
        t = float(fr["t"])
        for tid, (x, y, _m) in fr["c"].items():
            old = prev.get(tid)
            if old is not None:
                dt = t - old[2]
                if dt > 0:
                    step = math.hypot(x - old[0], y - old[1])
                    out.setdefault(tid, []).append((step / dt, step))
        prev = {tid: (float(x), float(y), t)
                for tid, (x, y, _m) in fr["c"].items()}
    return out


def max_run(flags: list[bool]) -> int:
    best = run = 0
    for f in flags:
        run = run + 1 if f else 0
        best = max(best, run)
    return best


def frame_timing(payload: list[dict]) -> dict:
    dts = sorted(b["t"] - a["t"] for a, b in zip(payload, payload[1:]))
    return {
        "frames": len(payload),
        "duration_s": payload[-1]["t"] - payload[0]["t"] if payload else 0.0,
        "dt_min_ms": dts[0] * 1000 if dts else float("nan"),
        "dt_p01_ms": quantile(dts, 0.01) * 1000,
        "dt_p50_ms": quantile(dts, 0.50) * 1000,
        "dt_p99_ms": quantile(dts, 0.99) * 1000,
        "dt_max_ms": dts[-1] * 1000 if dts else float("nan"),
        "hz_median": 1.0 / quantile(dts, 0.50) if dts else float("nan"),
    }


def label_of(stats: dict, mover_path: float, rest_path: float) -> str:
    if stats["path_mm"] > mover_path:
        return "MOVER"
    if stats["path_mm"] < rest_path:
        return "REST"
    return "MID"


def analyse(path: Path, mover_path: float, rest_path: float) -> dict:
    payload = load(path)
    result = kinematics.analyze(payload)
    series = per_frame_series(payload)
    timing = frame_timing(payload)
    contacts = {}
    for tid in (k for k in result if k not in ("coupling", "coupling_n")):
        c = result[tid]
        group = label_of(c, mover_path, rest_path)
        speeds = sorted(s for s, _ in series.get(tid, []))
        steps = sorted(d for _, d in series.get(tid, []))
        runs = {str(v): max_run([s >= v for s, _ in series.get(tid, [])])
                for v in VELOCITY_GRID}
        contacts[tid] = {
            "group": group,
            "n_frames": c["n_frames"],
            "active_s": c["active_s"],
            "path_mm": c["path_mm"],
            "drift_mm": c["drift_mm"],
            "drift_dxdy": c["drift"],
            "peak_mm_s": c["peak_mm_s"],
            "mean_mm_s": c["mean_mm_s"],
            "step_p50_mm": quantile(steps, 0.50),
            "step_p99_mm": quantile(steps, 0.99),
            "step_max_mm": steps[-1] if steps else 0.0,
            "speed_p50_mm_s": quantile(speeds, 0.50),
            "speed_p99_mm_s": quantile(speeds, 0.99),
            "speed_max_mm_s": speeds[-1] if speeds else 0.0,
            "max_run_frames_by_velocity": runs,
        }
    return {"session": path.name, "timing": timing, "contacts": contacts,
            "coupling": result["coupling"], "coupling_n": result["coupling_n"]}


def group_summary(sessions: list[dict], min_frames: int) -> dict:
    """Pool contacts across sessions; report the two numbers that set thresholds."""
    pool: dict[str, dict[str, list[float]]] = {
        g: {"speed_p99": [], "speed_max": [], "step_p99": [], "step_max": [],
            "drift": [], "run": {str(v): [] for v in VELOCITY_GRID}}
        for g in ("REST", "MOVER")
    }
    for s in sessions:
        for c in s["contacts"].values():
            g = c["group"]
            if g not in pool or c["n_frames"] < min_frames:
                continue
            pool[g]["speed_p99"].append(c["speed_p99_mm_s"])
            pool[g]["speed_max"].append(c["speed_max_mm_s"])
            pool[g]["step_p99"].append(c["step_p99_mm"])
            pool[g]["step_max"].append(c["step_max_mm"])
            pool[g]["drift"].append(c["drift_mm"])
            for v in VELOCITY_GRID:
                pool[g]["run"][str(v)].append(
                    c["max_run_frames_by_velocity"][str(v)])
    out = {}
    for g, d in pool.items():
        if not d["speed_max"]:
            out[g] = {}
            continue
        out[g] = {
            "contacts": len(d["speed_max"]),
            "speed_p99_mm_s_max": max(d["speed_p99"]),
            "speed_max_mm_s_max": max(d["speed_max"]),
            "step_p99_mm_max": max(d["step_p99"]),
            "step_max_mm_max": max(d["step_max"]),
            "drift_mm_max": max(d["drift"]),
            "run_worst_by_velocity": {v: max(r) for v, r in d["run"].items()},
        }
    return out


def separation_table(sessions: list[dict], min_frames: int) -> list[dict]:
    """Worst-case REST vs best-case MOVER per velocity threshold / persistence.

    A candidate rule (v, k) fires when a contact has k consecutive frames with
    speed >= v. False-positive risk = longest such run among REST contacts;
    true-positive headroom = longest such run among MOVER contacts.
    """
    rows = []
    for v in VELOCITY_GRID:
        for k in PERSISTENCE_GRID:
            rest_runs, mover_runs = [], []
            for s in sessions:
                for c in s["contacts"].values():
                    if c["n_frames"] < min_frames:
                        continue
                    run = c["max_run_frames_by_velocity"][str(v)]
                    (rest_runs if c["group"] == "REST" else mover_runs
                     if c["group"] == "MOVER" else []).append(run)
            if not rest_runs or not mover_runs:
                continue
            rows.append({
                "velocity_mm_s": v,
                "persistence_frames": k,
                "rest_worst_run": max(rest_runs),
                "rest_fires": max(rest_runs) >= k,
                "mover_best_run": max(mover_runs),
                "mover_fires": max(mover_runs) >= k,
            })
    return rows


def md_table(rows: list[dict], header: str) -> str:
    keys = list(rows[0]) if rows else []
    out = [header, "|" + "|".join(keys) + "|",
           "|" + "|".join("---:" for _ in keys) + "|"]
    for r in rows:
        out.append("|" + "|".join(str(r[k]) for k in keys) + "|")
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("sessions", nargs="+", type=Path)
    ap.add_argument("--mover-path", type=float, default=100.0,
                    help="path_mm above which a contact counts as MOVER")
    ap.add_argument("--rest-path", type=float, default=20.0,
                    help="path_mm below which a contact counts as REST")
    ap.add_argument("--min-frames", type=int, default=50,
                    help="ignore contacts shorter than this (placement flicks)")
    ap.add_argument("--json", action="store_true", help="emit JSON instead of Markdown")
    args = ap.parse_args()

    sessions = [analyse(p, args.mover_path, args.rest_path) for p in args.sessions]
    summary = group_summary(sessions, args.min_frames)
    table = separation_table(sessions, args.min_frames)
    if args.json:
        print(json.dumps({"sessions": sessions, "summary": summary,
                          "separation": table}, indent=2))
        return 0
    for s in sessions:
        t = s["timing"]
        print(f"\n## {s['session']}")
        print(f"frames {t['frames']}  duration {t['duration_s']:.1f}s  "
              f"median {t['hz_median']:.0f} Hz  dt p01/p50/p99/max "
              f"{t['dt_p01_ms']:.1f}/{t['dt_p50_ms']:.1f}/{t['dt_p99_ms']:.1f}/"
              f"{t['dt_max_ms']:.0f} ms")
        rows = [{"tid": tid, "grp": c["group"], "n": c["n_frames"],
                 "path": round(c["path_mm"], 1), "drift": round(c["drift_mm"], 2),
                 "step_p99": round(c["step_p99_mm"], 3),
                 "step_max": round(c["step_max_mm"], 3),
                 "v_p99": round(c["speed_p99_mm_s"], 1),
                 "v_max": round(c["speed_max_mm_s"], 1)}
                for tid, c in s["contacts"].items()]
        print(md_table(rows, "\n|tid|group|frames|path_mm|drift_mm|step_p99_mm|"
                            "step_max_mm|v_p99_mm_s|v_max_mm_s|"))
    print("\n## pooled groups (contacts >= "
          f"{args.min_frames} frames)")
    print(json.dumps(summary, indent=2))
    print("\n## separation: rule (velocity, persistence) vs measured runs")
    print(md_table(table, "\n|velocity_mm_s|persistence_frames|rest_worst_run|"
                          "rest_fires|mover_best_run|mover_fires|"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
