#!/usr/bin/env python3
"""End-to-end latency budget: where the milliseconds actually go.

The project quotes an 88 ms event window as its cost, but that is only one stage. A
committed stroke has to travel through filtering, detection, descriptor, confidence and the
sink. This measures each stage on a recorded session so the total can be compared against
the 0.24 s/word budget of a 250 WPM target (CROSS_VALIDATION 1.4).

Everything is measured on the existing recordings, so it runs without a tablet. What it
cannot measure is the sensor's own latency, which is not observable from the logged stream -
that is stated explicitly rather than assumed to be zero.

Usage:
    python3 scripts/latency_budget.py session.jsonl [session.jsonl ...]
    python3 scripts/latency_budget.py --json session.jsonl
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import intent_filter  # noqa: E402
import kinematics  # noqa: E402
import stroke_decoder  # noqa: E402

FRAME_MS = 1000.0 / 91.0     # measured median frame interval
DETECTOR_MS = intent_filter.MIN_RUN_FRAMES * FRAME_MS
TARGET_250_WPM_WORD_MS = 240.0
TARGET_150_WPM_WORD_MS = 400.0


def timed(fn, *a, **kw):
    t0 = time.perf_counter()
    out = fn(*a, **kw)
    return out, (time.perf_counter() - t0) * 1000.0


def analyse(path: Path) -> dict:
    stages = {}
    raw, stages["load"] = timed(kinematics._load, path)
    clean, stages["init_filter"] = timed(kinematics._strip_uninit_leads, raw)
    _stats, stages["analyze"] = timed(kinematics.analyze, clean)
    events, stages["detect"] = timed(
        intent_filter.analyse, path, intent_filter.MIN_SPEED_MM_S,
        intent_filter.MIN_RUN_FRAMES)
    mapping = stroke_decoder.DEFAULT_MAP
    decoded, stages["decode"] = timed(stroke_decoder.analyse, path, mapping)
    total_cpu = sum(stages.values())

    # algorithmic latency: the event window itself, plus the descriptor's own
    # windowed displacement (the same window the detector needs).
    durations = [e["duration_ms"] for e in events["events"]]
    dur = {
        "min": round(min(durations), 1) if durations else None,
        "p50": round(statistics.median(durations), 1) if durations else None,
        "p95": round(sorted(durations)[int(0.95 * (len(durations) - 1))], 1)
        if durations else None,
        "max": round(max(durations), 1) if durations else None,
    }
    words = []
    # assume the decoded events are syllables at the observed rate
    if events["events"]:
        span = events["events"][-1]["t_end"] - events["events"][0]["t_start"]
        if span > 0:
            words.append(span)
    return {
        "session": path.name,
        "frames": len(raw),
        "events": len(events["events"]),
        "strokes": decoded["decoded"],
        "cpu_ms_per_stage": {k: round(v, 1) for k, v in stages.items()},
        "cpu_ms_total": round(total_cpu, 1),
        "cpu_us_per_frame": round(total_cpu * 1000 / max(1, len(raw)), 1),
        "event_duration_ms": dur,
        "fixed_pipeline_latency_ms": round(DETECTOR_MS, 1),
        "sensor_latency_ms": "NOT MEASURABLE from the logged stream (stated, not assumed 0)",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("sessions", nargs="+", type=Path)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    reports = [analyse(p) for p in args.sessions]
    if args.json:
        print(json.dumps(reports, indent=2))
        return 0
    for r in reports:
        print(f"\n## {r['session']}  frames {r['frames']}  events {r['events']}")
        print("CPU per stage (ms): " +
              ", ".join(f"{k}={v}" for k, v in r["cpu_ms_per_stage"].items()))
        print(f"  total {r['cpu_ms_total']} ms  ->  {r['cpu_us_per_frame']} us/frame "
              f"(a 91 Hz budget is 10989 us/frame)")
        d = r["event_duration_ms"]
        print(f"  event duration ms: min {d['min']} p50 {d['p50']} p95 {d['p95']} max {d['max']}")
        print(f"  fixed algorithmic latency: {r['fixed_pipeline_latency_ms']} ms "
              f"(the persistence window)")
        print(f"  sensor latency: {r['sensor_latency_ms']}")
        budget250 = TARGET_250_WPM_WORD_MS
        headroom = budget250 - r["fixed_pipeline_latency_ms"]
        print(f"  250 WPM word budget {budget250:.0f} ms -> algorithmic headroom "
              f"{headroom:.0f} ms ({headroom/budget250*100:.0f}% of the word)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
