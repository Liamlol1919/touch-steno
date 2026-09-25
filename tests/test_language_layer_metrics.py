import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import language_layer_metrics  # noqa: E402


class TestLanguageLayerMetrics(unittest.TestCase):
    def test_exact_aggregate_and_correction_overhead(self):
        records = [
            {"event": "stroke"}, {"event": "stroke"}, {"event": "untranslate"},
            {"event": "word", "delta": 1}, {"event": "undo"},
            {"event": "word", "delta": -1}, {"event": "stroke"},
            {"event": "word", "delta": 1},
        ]
        report = language_layer_metrics.summarize(records)
        self.assertEqual(report["event_counts"], {
            "input_strokes": 3, "untranslate_events": 1, "undo_events": 1,
            "word_additions": 2, "word_removals": 1, "final_words": 1,
        })
        self.assertEqual(report["derived"], {
            "untranslate_events_per_100_strokes": 33.33,
            "undo_events_per_100_strokes": 33.33,
            "strokes_per_word": 3.0,
        })
        self.assertFalse(report["measurement_scope"]["wpm"])
        self.assertFalse(report["privacy"]["raw_text"])

    def test_zero_denominators_and_empty_log(self):
        report = language_layer_metrics.summarize([])
        self.assertEqual(report["event_counts"]["input_strokes"], 0)
        self.assertIsNone(report["derived"]["untranslate_events_per_100_strokes"])
        self.assertIsNone(report["derived"]["strokes_per_word"])

    def test_invalid_word_delta_and_negative_balance_fail(self):
        for delta in (0, 2, -2, 1.0, True, "1"):
            with self.assertRaises(ValueError):
                language_layer_metrics.summarize([{"event": "word", "delta": delta}])
        with self.assertRaises(ValueError):
            language_layer_metrics.summarize([{"event": "word", "delta": -1}])

    def test_unknown_or_privacy_prohibited_fields_fail(self):
        for record in ({"event": "stroke", "text": "cat"},
                       {"event": "stroke", "session": "private"},
                       {"event": "other"}):
            with self.assertRaises(ValueError):
                language_layer_metrics.summarize([record])

    def test_impossible_event_relations_fail(self):
        with self.assertRaises(ValueError):
            language_layer_metrics.summarize([{"event": "undo"}])
        with self.assertRaises(ValueError):
            language_layer_metrics.summarize([{"event": "untranslate"}])

    def test_loader_and_cli_emit_strict_aggregate_json(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "private-session-name.jsonl"
            output = root / "report.json"
            source.write_text('{"event":"stroke"}\n{"event":"word","delta":1}\n',
                              encoding="utf-8")
            old_argv = sys.argv
            try:
                sys.argv = ["language_layer_metrics.py", str(source), "--out", str(output)]
                self.assertEqual(language_layer_metrics.main(), 0)
            finally:
                sys.argv = old_argv
            report = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(report["event_counts"]["final_words"], 1)
        self.assertNotIn("private-session-name", json.dumps(report))

    def test_loader_rejects_duplicate_keys_without_echoing_record(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "events.jsonl"
            path.write_text('{"event":"stroke","event":"undo"}\n', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "line 1: duplicate JSON key"):
                language_layer_metrics.load_events(path)


if __name__ == "__main__":
    unittest.main()
