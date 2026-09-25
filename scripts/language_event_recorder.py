#!/usr/bin/env python3
"""Write the privacy-minimized language event stream consumed by metrics.

This is a producer boundary, not a Plover plugin. A future Plover hook adapter can call
these methods; the recorder never accepts text, outlines, timestamps, or identifiers.
"""
from __future__ import annotations

import json
from pathlib import Path


class LanguageEventRecorder:
    """Append-only local JSONL recorder for semantic language events."""

    def __init__(self, path: Path, *, overwrite: bool = False):
        self.path = Path(path)
        if self.path.exists() and not overwrite:
            raise FileExistsError(f"event log exists: {self.path}")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._file = self.path.open("w", encoding="utf-8")
        self._closed = False
        self._words = 0

    def _write(self, record: dict) -> None:
        if self._closed:
            raise RuntimeError("event recorder is closed")
        self._file.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")
        self._file.flush()

    def stroke(self) -> None:
        self._write({"event": "stroke"})

    def untranslate(self) -> None:
        self._write({"event": "untranslate"})

    def undo(self) -> None:
        self._write({"event": "undo"})

    def word(self, delta: int) -> None:
        if isinstance(delta, bool) or not isinstance(delta, int) or delta not in (-1, 1):
            raise ValueError("word delta must be integer +1 or -1")
        if self._words + delta < 0:
            raise ValueError("word removal precedes a word addition")
        self._write({"event": "word", "delta": delta})
        self._words += delta

    def close(self) -> None:
        if not self._closed:
            self._file.close()
            self._closed = True

    def __enter__(self) -> "LanguageEventRecorder":
        return self

    def __exit__(self, *exc) -> bool:
        self.close()
        return False
