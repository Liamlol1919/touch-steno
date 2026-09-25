#!/usr/bin/env python3
"""Measure correction-cue adherence without inventing text-output latency.

The guided correction task records contact frames and a `corr_undo` cue. That proves
detector motion began after the cue, not that a Plover/text sink repaired the output. The
reported motion metric is therefore `cue_to_detected_undo_motion_ms`; text-repair latency
requires an explicit typed repair log on the same monotonic clock.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kinematics  # noqa: E402
import session_manifest  # noqa: E402


def summarize_corrections(manifest: list[dict], events: list[dict],
                          repair_events: list[dict] | None = None) -> dict:
    """Summarize corr_undo cues and optional typed text-repair events."""
    undo_cues = [r for r in manifest if r.get("label") == "corr_undo"]
    correction_records = [r for r in manifest if r.get("correction_block")]
    exposure_s = sum(max(0.0, float(r["t_end"]) - float(r["t_start"]))
                      for r in correction_records)
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
        motion_status = "DETECTED" if motion is not None else "MISSING"
        repair_status = ("NOT_LOGGED" if repair_events is None else
                         "OBSERVED" if repair_t is not None else "MISSING")
        detail.append({
            "label": cue.get("label"), "t_start": t0, "t_end": t1,
            "cue_to_detected_undo_motion_ms": round(motion_latency_ms, 1)
            if motion_latency_ms is not None else None,
            "text_repair_latency_ms": round((repair_t - t0) * 1000.0, 1)
            if repair_t is not None else None,
            "motion_status": motion_status,
            "repair_status": repair_status,
            "status": f"{motion_status}/{repair_status}",
        })

    motion_count = sum(d["motion_status"] == "DETECTED" for d in detail)
    repair_count = sum(d["repair_status"] == "OBSERVED" for d in detail)
    return {
        "undo_cues": len(detail),
        "motion_observed": motion_count,
        "text_repairs_observed": repair_count,
        "text_output_source": "typed_repair_log" if repair_events is not None else None,
        "correction_exposure_s": round(exposure_s, 3),
        "detected_motion_per_min": round(motion_count / exposure_s * 60.0, 2)
        if exposure_s > 0 else None,
        "text_repairs_per_min": round(repair_count / exposure_s * 60.0, 2)
        if exposure_s > 0 and repair_events is not None else None,
        "detail": detail,
    }


def load_repair_events(path: Path | None) -> list[dict] | None:
    if path is None:
        return None
    records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()
               if line.strip()]
    for record in records:
        try:
            timestamp = float(record["t"])
        except (KeyError, TypeError, ValueError):
            raise SystemExit("repair log records require numeric t") from None
        if not math.isfinite(timestamp):
            raise SystemExit("repair log t must be finite")
        if record.get("type") != "text_repair" or record.get("action") != "undo":
            raise SystemExit("repair log requires type=text_repair action=undo")
        if record.get("clock") != "monotonic":
            raise SystemExit("repair log requires clock=monotonic")
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
                    help="typed JSONL text_repair/undo events on a monotonic clock")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    report = evaluate(args.capture, args.repair_log)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"## {report['session']}  undo cues {report['undo_cues']}")
        print(f"  detected undo motion: {report['motion_observed']} "
              f"({report['detected_motion_per_min']}/min over correction exposure)")
        if report["text_output_source"]:
            print(f"  typed text repairs: {report['text_repairs_observed']} "
                  f"({report['text_repairs_per_min']}/min)")
        else:
            print("  typed text repairs: unavailable without --repair-log")
        for cue in report["detail"]:
            print(f"  {cue['status']:<20} "
                  f"motion_ms={cue['cue_to_detected_undo_motion_ms']} "
                  f"text_ms={cue['text_repair_latency_ms']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
