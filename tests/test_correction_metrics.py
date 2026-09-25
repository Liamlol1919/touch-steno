import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import correction_metrics  # noqa: E402


class TestCorrectionMetrics(unittest.TestCase):
    def setUp(self):
        self.manifest = [{"label": "corr_undo", "t_start": 1.0, "t_end": 2.0}]
        self.events = [{"t_start": 1.3}]

    def test_motion_without_repair_log_is_not_text_repair(self):
        report = correction_metrics.summarize_corrections(self.manifest, self.events)
        self.assertEqual(report["detail"][0]["status"], "MOTION_ONLY")
        self.assertEqual(report["detail"][0]["motion_latency_ms"], 300.0)
        self.assertIsNone(report["detail"][0]["text_repair_latency_ms"])
        self.assertIsNone(report["text_output_source"])

    def test_explicit_repair_event_reports_separate_latency(self):
        report = correction_metrics.summarize_corrections(
            self.manifest, self.events, [{"t": 1.5}])
        cue = report["detail"][0]
        self.assertEqual(cue["status"], "REPAIR_OBSERVED")
        self.assertEqual(cue["motion_latency_ms"], 300.0)
        self.assertEqual(cue["text_repair_latency_ms"], 500.0)
        self.assertEqual(report["text_output_source"], "repair_log")

    def test_missing_motion_is_explicit(self):
        report = correction_metrics.summarize_corrections(self.manifest, [])
        self.assertEqual(report["detail"][0]["status"], "NO_MOTION")
        self.assertEqual(report["motion_observed_per_min"], 0.0)

    def test_repair_log_requires_timestamps(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "repair.jsonl"
            path.write_text(json.dumps({"time": 1.5}) + "\n", encoding="utf-8")
            with self.assertRaises(SystemExit):
                correction_metrics.load_repair_events(path)


if __name__ == "__main__":
    unittest.main()
