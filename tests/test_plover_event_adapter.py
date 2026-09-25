import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import language_layer_metrics  # noqa: E402
import language_event_recorder  # noqa: E402
import plover_event_adapter  # noqa: E402


class TestPloverEventAdapter(unittest.TestCase):
    def test_adapter_forwards_only_semantic_callbacks(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "events.jsonl"
            with language_event_recorder.LanguageEventRecorder(path) as recorder:
                adapter = plover_event_adapter.PloverEventAdapter(recorder)
                adapter.stroke_received(object())
                adapter.untranslate_received(object())
                adapter.word_delta(1)
                adapter.undo_received(object())
                adapter.word_delta(-1)
            report = language_layer_metrics.summarize(
                language_layer_metrics.load_events(path))
        self.assertEqual(report["event_counts"], {
            "input_strokes": 1, "untranslate_events": 1, "undo_events": 1,
            "word_additions": 1, "word_removals": 1, "final_words": 0,
        })


if __name__ == "__main__":
    unittest.main()
