#!/usr/bin/env python3
"""Export opt-in aggregate telemetry without raw contact or session identifiers."""
from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import real_session_evidence  # noqa: E402
import raw_schema  # noqa: E402

TELEMETRY_SCHEMA = "touchsteno.telemetry"
TELEMETRY_VERSION = 1


def _finite(value):
    if value is None:
        return None
    value = float(value)
    return value if math.isfinite(value) else None


def _median(values):
    clean = [_finite(v) for v in values]
    clean = [v for v in clean if v is not None]
    return _finite(statistics.median(clean)) if clean else None


def export_telemetry(paths: list[Path], min_frames: int = 50) -> dict:
    """Return aggregate timing and contact-group statistics only.

    No path, session name, contact ID, coordinate, timestamp, user ID, or text field is
    copied into the result. Raw JSONL remains a separate, explicitly controlled artifact.
    """
    reports = [real_session_evidence.analyse(path, 100.0, 20.0) for path in paths]
    groups = real_session_evidence.group_summary(reports, min_frames)
    timing = {
        "sessions": len(reports),
        "frames_total": sum(r["timing"]["frames"] for r in reports),
        "duration_s_total": _finite(sum(r["timing"]["duration_s"] for r in reports)),
        "hz_median": _median([r["timing"]["hz_median"] for r in reports]),
        "dt_p50_ms_median": _median([r["timing"]["dt_p50_ms"] for r in reports]),
        "dt_p99_ms_median": _median([r["timing"]["dt_p99_ms"] for r in reports]),
    }
    return {
        "schema": TELEMETRY_SCHEMA,
        "version": TELEMETRY_VERSION,
        "privacy": {
            "opt_in": True,
            "raw_coordinates": False,
            "contact_ids": False,
            "session_names": False,
            "user_ids": False,
            "text_content": False,
        },
        "provenance": {
            "raw_frame_schema": raw_schema.SCHEMA,
            "raw_frame_version": raw_schema.VERSION,
            "source_sessions": len(reports),
        },
        "timing": timing,
        "contact_groups": groups,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("sessions", nargs="+", type=Path)
    ap.add_argument("--min-frames", type=int, default=50)
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()
    report = export_telemetry(args.sessions, args.min_frames)
    text = json.dumps(report, indent=2, sort_keys=True, allow_nan=False)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
