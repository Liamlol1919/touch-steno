import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import language_event_recorder  # noqa: E402
import language_layer_metrics  # noqa: E402


class TestLanguageEventRecorder(unittest.TestCase):
    def test_recorder_produces_metrics_compatible_event_stream(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "events.jsonl"
            with language_event_recorder.LanguageEventRecorder(path) as recorder:
                recorder.stroke()
                recorder.untranslate()
                recorder.word(1)
                recorder.undo()
                recorder.word(-1)
                recorder.stroke()
                recorder.word(1)
            records = language_layer_metrics.load_events(path)
            report = language_layer_metrics.summarize(records)
        self.assertEqual(report["event_counts"]["input_strokes"], 2)
        self.assertEqual(report["event_counts"]["final_words"], 1)
        self.assertEqual(report["derived"]["strokes_per_word"], 2.0)

    def test_recorder_rejects_invalid_word_delta_and_negative_balance(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "events.jsonl"
            with language_event_recorder.LanguageEventRecorder(path) as recorder:
                with self.assertRaises(ValueError):
                    recorder.word(0)
                with self.assertRaises(ValueError):
                    recorder.word(-1)
                recorder.word(1)
                recorder.word(-1)

    def test_recorder_refuses_existing_log_without_overwrite(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "events.jsonl"
            path.write_text("", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                language_event_recorder.LanguageEventRecorder(path)
            with language_event_recorder.LanguageEventRecorder(path, overwrite=True):
                pass

    def test_output_contains_no_private_fields(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "private-session-name.jsonl"
            with language_event_recorder.LanguageEventRecorder(path) as recorder:
                recorder.stroke()
            raw = path.read_text(encoding="utf-8")
            self.assertNotIn("private-session-name", raw)
            self.assertEqual(json.loads(raw), {"event": "stroke"})


if __name__ == "__main__":
    unittest.main()
