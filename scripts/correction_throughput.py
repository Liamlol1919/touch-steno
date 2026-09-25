#!/usr/bin/env python3
"""Summarize human correction-throughput observations from a local JSONL log.

This tool measures the missing seconds-per-correction input; it does not simulate a user or
claim a benchmark result. Each record should contain correction_seconds and may contain
observation_seconds for a session-level rate.
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
from pathlib import Path

SCHEMA = "touchsteno.correction_throughput"
VERSION = 1


def summarize(records: list[dict]) -> dict:
    durations = []
    observation_seconds = None
    for record in records:
        value = record.get("correction_seconds")
        if not isinstance(value, (int, float)) or not math.isfinite(float(value)) or value <= 0:
            raise ValueError("correction_seconds must be a positive finite number")
        durations.append(float(value))
        if record.get("observation_seconds") is not None:
            obs = float(record["observation_seconds"])
            if not math.isfinite(obs) or obs <= 0:
                raise ValueError("observation_seconds must be positive finite")
            observation_seconds = obs if observation_seconds is None else max(observation_seconds, obs)
    durations.sort()
    if not durations:
        return {"schema": SCHEMA, "version": VERSION, "observations": 0,
                "observation_seconds": observation_seconds,
                "median_seconds": None, "p95_seconds": None,
                "mean_seconds": None, "corrections_per_minute": None}
    p95 = durations[min(len(durations) - 1, int(0.95 * len(durations)))]
    return {
        "schema": SCHEMA, "version": VERSION, "observations": len(durations),
        "observation_seconds": observation_seconds,
        "median_seconds": round(statistics.median(durations), 3),
        "p95_seconds": round(p95, 3), "mean_seconds": round(statistics.fmean(durations), 3),
        "corrections_per_minute": round(len(durations) / observation_seconds * 60.0, 2)
        if observation_seconds else None,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("log", type=Path, help="JSONL observations")
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()
    records = [json.loads(line) for line in args.log.read_text(encoding="utf-8").splitlines()
               if line.strip()]
    report = summarize(records)
    text = json.dumps(report, indent=2, sort_keys=True, allow_nan=False)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
