#!/usr/bin/env python3
"""Aggregate privacy-minimized local language-layer events.

Input is JSONL with only ``stroke``, ``untranslate``, ``undo``, and signed ``word`` events.
The tool does not import Plover, infer text, measure correction time, or emit WPM.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

SCHEMA = "touchsteno.language_layer_metrics"
VERSION = 1
ALLOWED = {
    "stroke": {"event"},
    "untranslate": {"event"},
    "undo": {"event"},
    "word": {"event", "delta"},
}


def _reject_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _validate_record(record: object) -> dict:
    if not isinstance(record, dict):
        raise ValueError("event record must be an object")
    event = record.get("event")
    if event not in ALLOWED:
        raise ValueError("unknown language event")
    if set(record) != ALLOWED[event]:
        raise ValueError(f"unexpected fields for {event}")
    if event == "word":
        delta = record["delta"]
        if isinstance(delta, bool) or not isinstance(delta, int) or delta not in (-1, 1):
            raise ValueError("word delta must be integer +1 or -1")
    return dict(record)


def load_events(path: Path) -> list[dict]:
    """Load and validate a local JSONL event log."""
    records = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            record = json.loads(line, object_pairs_hook=_reject_duplicate_keys)
            records.append(_validate_record(record))
        except (json.JSONDecodeError, ValueError) as exc:
            raise ValueError(f"line {line_number}: {exc}") from None
    return records


def summarize(records: list[dict]) -> dict:
    """Return aggregate counts and rates without copying any input fields."""
    validated = [_validate_record(record) for record in records]
    strokes = sum(record["event"] == "stroke" for record in validated)
    untranslates = sum(record["event"] == "untranslate" for record in validated)
    undos = sum(record["event"] == "undo" for record in validated)
    words = 0
    additions = removals = 0
    for record in validated:
        if record["event"] != "word":
            continue
        delta = record["delta"]
        if words + delta < 0:
            raise ValueError("word removal precedes a word addition")
        words += delta
        additions += delta > 0
        removals += delta < 0
    if untranslates > strokes or undos > strokes:
        raise ValueError("untranslate/undo count exceeds accepted strokes")
    return {
        "schema": SCHEMA,
        "version": VERSION,
        "event_counts": {
            "input_strokes": strokes,
            "untranslate_events": untranslates,
            "undo_events": undos,
            "word_additions": additions,
            "word_removals": removals,
            "final_words": words,
        },
        "derived": {
            "untranslate_events_per_100_strokes": round(100.0 * untranslates / strokes, 2)
            if strokes else None,
            "undo_events_per_100_strokes": round(100.0 * undos / strokes, 2)
            if strokes else None,
            "strokes_per_word": round(strokes / words, 3) if words else None,
        },
        "privacy": {"raw_text": False, "steno_outlines": False,
                    "coordinates": False, "identifiers": False},
        "measurement_scope": {"basis": "local_jsonl_event_counts",
                               "user_correction_time": False,
                               "plover_performance": False, "wpm": False},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("events", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    try:
        report = summarize(load_events(args.events))
    except (OSError, ValueError) as exc:
        raise SystemExit(str(exc)) from None
    text = json.dumps(report, indent=2, sort_keys=True, allow_nan=False)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
