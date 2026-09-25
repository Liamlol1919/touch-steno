import json
import sys
import tempfile
import unittest
from types import SimpleNamespace
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import evaluate_session  # noqa: E402
import guided_calibration  # noqa: E402
import make_benchmark  # noqa: E402
import session_manifest  # noqa: E402


class TestSessionManifest(unittest.TestCase):
    def test_normalizes_legacy_paired_records(self):
        records = [
            {"label": "tempo_1hz", "t_start": 1.0, "events": [0.0],
             "event_provenance": "expected_cue_schedule"},
            {"label": "tempo_1hz", "t_end": 1.5},
        ]
        normalized = session_manifest.normalize_records(records)
        self.assertEqual(normalized, [{
            "label": "tempo_1hz", "t_start": 1.0, "t_end": 1.5,
            "events": [0.0], "event_provenance": "expected_cue_schedule",
        }])

    def test_preserves_complete_records_and_drops_open_tail(self):
        records = [
            {"label": "noise_rest", "t_start": 0.0, "t_end": 1.0, "rest": True},
            {"label": "sector_N", "t_start": 2.0, "sector": "N"},
        ]
        normalized = session_manifest.normalize_records(records)
        self.assertEqual(len(normalized), 1)
        self.assertEqual(normalized[0]["label"], "noise_rest")

    def test_evaluator_loads_legacy_manifest(self):
        with tempfile.TemporaryDirectory() as td:
            session = Path(td) / "guided.jsonl"
            manifest = session.with_suffix(".manifest.jsonl")
            session.write_text("", encoding="utf-8")
            manifest.write_text(
                json.dumps({"label": "sector_E", "t_start": 1.0}) + "\n" +
                json.dumps({"label": "sector_E", "t_end": 1.5}) + "\n",
                encoding="utf-8",
            )
            loaded = evaluate_session.load_manifest(session)
        self.assertEqual(loaded[0]["t_end"], 1.5)

    def test_guided_chord_labels_use_peak_aligned_strokes(self):
        events = [
            {"t_start": 1.0, "label": "chord_both_thumbs"},
            {"t_start": 2.0, "label": "single_left_thumb"},
            {"t_start": 3.0, "label": "chord_both_thumbs"},
        ]
        strokes = [
            {"t_start": 1.0, "chord_contacts": ["2"]},
            {"t_start": 2.0, "chord_contacts": []},
        ]
        self.assertEqual(
            evaluate_session.score_chords(events, strokes),
            {"tp": 1, "fp": 0, "fn": 1},
        )
    def test_tempo_event_marks_are_matched_one_to_one(self):
        record = {
            "label": "tempo_1hz", "t_start": 0.0, "t_end": 2.0,
            "rate_hz": 1.0, "events": [0.0, 0.5],
        }
        result = evaluate_session.score_tempo(record, [{"t_start": 0.25}])
        self.assertEqual(result["mode"], "one_to_one_cues")
        self.assertEqual(result["events"], 1)
        self.assertEqual(result["missed"], 1)
        self.assertEqual(result["merged"], 1)

    def test_guided_aggregate_tempo_is_labelled_as_block_count(self):
        record = {
            "label": "tempo_2hz", "t_start": 0.0, "t_end": 2.0,
            "rate_hz": 2.0, "reps": 4,
        }
        result = evaluate_session.score_tempo(record, [{"t_start": 0.5}, {"t_start": 1.5}])
        self.assertEqual(result["mode"], "aggregate_block_count")
        self.assertEqual(result["events"], 2)
        self.assertEqual(result["cued_gestures"], 4)
    def test_guided_tempo_tasks_include_expected_cue_schedule(self):
        args = SimpleNamespace(task="tempo", rates=[2.0], seconds_per_rate=2.0)
        task = guided_calibration.build_tasks(args)[0]
        self.assertEqual(task["events"], [0.0, 0.5, 1.0, 1.5])
        self.assertEqual(task["event_provenance"], "expected_cue_schedule")

    def test_guided_tempo_score_labels_expected_schedule(self):
        record = {
            "label": "tempo_1hz", "t_start": 10.0, "t_end": 12.0,
            "rate_hz": 1.0, "events": [0.0, 1.0],
            "event_provenance": "expected_cue_schedule",
        }
        result = evaluate_session.score_tempo(
            record, [{"t_start": 10.1}, {"t_start": 11.1}])
        self.assertEqual(result["mode"], "one_to_one_cues")
        self.assertEqual(result["cue_provenance"], "expected_cue_schedule")
        self.assertEqual(result["events"], 2)

    def test_guided_tempo_rejects_non_positive_duration(self):
        args = SimpleNamespace(task="tempo", rates=[1.0], seconds_per_rate=0.0)
        with self.assertRaises(ValueError):
            guided_calibration.build_tasks(args)

    def test_synthetic_tempo_marks_are_explicitly_ground_truth(self):
        _frames, manifest = make_benchmark.build(7, 0, [2.0], 0, 0)
        tempo = next(row for row in manifest if row["label"] == "tempo_2.0hz")
        self.assertEqual(tempo["event_provenance"], "synthetic_ground_truth")




if __name__ == "__main__":
    unittest.main()
