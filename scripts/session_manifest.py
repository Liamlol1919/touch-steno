#!/usr/bin/env python3
"""Normalize session cue manifests to one complete JSON object per cue.

The capture path historically emitted a start-only line followed by an end-only
line. Synthetic benchmarks emit one complete object. Downstream scoring must not
silently treat those formats as equivalent, so this module is the single boundary
that accepts both and returns only complete half-open cue intervals.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable


def normalize_records(records: Iterable[dict]) -> list[dict]:
    """Return complete records from complete or paired manifest records.

    A paired record is matched by ``label``. Incomplete start records are ignored
    because they can remain after an interrupted capture and have no scoreable end.
    """
    complete: list[dict] = []
    open_records: dict[str, dict] = {}
    for record in records:
        label = record.get("label")
        has_start = record.get("t_start") is not None
        has_end = record.get("t_end") is not None
        if has_start and has_end:
            complete.append(dict(record))
        elif has_start and label is not None:
            open_records[label] = dict(record)
        elif has_end and label is not None:
            start = open_records.pop(label, None)
            if start is not None:
                merged = dict(start)
                merged["t_end"] = record["t_end"]
                complete.append(merged)
    return complete


def load(path: Path) -> list[dict]:
    """Load and normalize a JSONL manifest path."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)
    records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()
               if line.strip()]
    return normalize_records(records)
