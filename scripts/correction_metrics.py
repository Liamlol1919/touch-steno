#!/usr/bin/env python3
"""Measure correction-cue adherence without inventing text-output latency.

The guided correction task records contact frames and a `corr_undo` cue. That proves
motion happened after the cue, not that a Plover/text sink repaired the output. This
module keeps those measurements separate: motion latency is always available from the raw
stream, while text-repair latency requires an explicit repair-event log.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import intent_filter  # noqa: E402
import kinematics  # noqa: E402
import session_manifest  # noqa: E402


def summarize_corrections(manifest: list[dict], events: list[dict],
                          repair_events: list[dict] | None = None) -> dict:
    """Summarize corr_undo cues and optional explicit text-repair events."""
    undo_cues = [r for r in manifest if r.get("label") == "corr_undo"]
    repairs_by_cue: dict[tuple[float, float], float] = {}
    if repair_events is not None:
        for cue in undo_cues:
            candidates = [float(r["t"]) for r in repair_events
                          if float(cue["t_start"]) <= float(r["t"]) < float(cue["t_end"])]
            if candidates:
                repairs_by_cue[(float(cue["t_start"]), float(cue["t_end"]))] = min(candidates)

    detail = []
    for cue in undo_cues:
        t0, t1 = float(cue["t_start"]), float(cue["t_end"])
        motion = next((e for e in events if t0 <= float(e["t_start"]) < t1), None)
        motion_latency_ms = ((float(motion["t_start"]) - t0) * 1000.0
                             if motion is not None else None)
        repair_t = repairs_by_cue.get((t0, t1))
        if motion is None:
            status = "NO_MOTION"
        elif repair_events is None:
            status = "MOTION_ONLY"
        elif repair_t is None:
            status = "REPAIR_MISSING"
        else:
            status = "REPAIR_OBSERVED"
        detail.append({
            "label": cue.get("label"), "t_start": t0, "t_end": t1,
            "motion_latency_ms": round(motion_latency_ms, 1)
            if motion_latency_ms is not None else None,
            "text_repair_latency_ms": round((repair_t - t0) * 1000.0, 1)
            if repair_t is not None else None,
            "status": status,
        })

    duration = max((float(r["t_end"]) - float(r["t_start"])
                    for r in manifest), default=0.0)
    motion_count = sum(d["motion_latency_ms"] is not None for d in detail)
    repair_count = sum(d["text_repair_latency_ms"] is not None for d in detail)
    return {
        "undo_cues": len(detail),
        "motion_observed": motion_count,
        "text_repairs_observed": repair_count,
        "text_output_source": "repair_log" if repair_events is not None else None,
        "motion_observed_per_min": round(motion_count / duration * 60.0, 2)
        if duration > 0 else None,
        "text_repairs_per_min": round(repair_count / duration * 60.0, 2)
        if duration > 0 and repair_events is not None else None,
        "detail": detail,
    }


def load_repair_events(path: Path | None) -> list[dict] | None:
    if path is None:
        return None
    records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()
               if line.strip()]
    if any("t" not in record for record in records):
        raise SystemExit("repair log records require a numeric t field")
    return records


def evaluate(path: Path, repair_log: Path | None = None) -> dict:
    manifest_path = path.with_suffix(".manifest.jsonl")
    manifest = session_manifest.load(manifest_path)
    events = intent_filter.analyse(path, intent_filter.MIN_SPEED_MM_S,
                                  intent_filter.MIN_RUN_FRAMES)["events"]
    report = summarize_corrections(manifest, events, load_repair_events(repair_log))
    return {"session": path.name, **report}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("capture", type=Path)
    ap.add_argument("--repair-log", type=Path,
                    help="optional JSONL text-repair events with numeric t timestamps")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    report = evaluate(args.capture, args.repair_log)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"## {report['session']}  undo cues {report['undo_cues']}")
        print(f"  motion observed: {report['motion_observed']} "
              f"({report['motion_observed_per_min']}/min)")
        if report["text_output_source"]:
            print(f"  text repairs: {report['text_repairs_observed']} "
                  f"({report['text_repairs_per_min']}/min)")
        else:
            print("  text repairs: unavailable without --repair-log")
        for cue in report["detail"]:
            print(f"  {cue['status']:<16} motion_ms={cue['motion_latency_ms']} "
                  f"text_ms={cue['text_repair_latency_ms']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
