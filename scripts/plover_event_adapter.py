#!/usr/bin/env python3
"""Semantic callback adapter for a local Plover integration.

This module deliberately does not import Plover or inspect translation objects. A Plover
hook supplies semantic callbacks; the adapter forwards only counters/deltas to the recorder.
"""
from __future__ import annotations

from language_event_recorder import LanguageEventRecorder


class PloverEventAdapter:
    """Forward privacy-safe semantic Plover events to a local recorder."""

    def __init__(self, recorder: LanguageEventRecorder):
        self.recorder = recorder

    def stroke_received(self, _stroke: object) -> None:
        self.recorder.stroke()

    def untranslate_received(self, _translation: object) -> None:
        self.recorder.untranslate()

    def undo_received(self, _command: object) -> None:
        self.recorder.undo()

    def word_delta(self, delta: int) -> None:
        self.recorder.word(delta)
