import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import correction_metrics  # noqa: E402
import kinematics  # noqa: E402


class TestCorrectionMetrics(unittest.TestCase):
    def setUp(self):
        self.manifest = [{"label": "corr_undo", "cue_id": "correction-0000",
                          "t_start": 1.0, "t_end": 2.0, "correction_block": True}]
        self.events = [{"t_start": 1.3}]

    def test_motion_without_repair_log_is_not_text_repair(self):
        report = correction_metrics.summarize_corrections(self.manifest, self.events)
        cue = report["detail"][0]
        self.assertEqual(cue["motion_status"], "DETECTED")
        self.assertEqual(cue["repair_status"], "NOT_LOGGED")
        self.assertEqual(cue["cue_to_detected_undo_motion_ms"], 300.0)
        self.assertIsNone(cue["text_repair_latency_ms"])
        self.assertIsNone(report["text_output_source"])

    def test_explicit_repair_event_reports_separate_latency(self):
        report = correction_metrics.summarize_corrections(
            self.manifest, self.events,
            [{"t": 1.5, "type": "text_repair", "action": "undo",
              "cue_id": "correction-0000", "clock": "monotonic"}])
        cue = report["detail"][0]
        self.assertEqual(cue["motion_status"], "DETECTED")
        self.assertEqual(cue["repair_status"], "OBSERVED")
        self.assertEqual(cue["cue_to_detected_undo_motion_ms"], 300.0)
        self.assertEqual(cue["text_repair_latency_ms"], 500.0)
        self.assertEqual(report["text_output_source"], "typed_repair_log")

    def test_missing_motion_is_explicit(self):
        report = correction_metrics.summarize_corrections(self.manifest, [])
        self.assertEqual(report["detail"][0]["motion_status"], "MISSING")
        self.assertEqual(report["detected_motion_per_min"], 0.0)

    def test_repair_log_requires_typed_monotonic_undo(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "repair.jsonl"
            path.write_text(json.dumps({"t": 1.5, "type": "other",
                                        "action": "undo", "cue_id": "correction-0000",
                                        "clock": "monotonic"}) + "\n",
                            encoding="utf-8")
            with self.assertRaises(SystemExit):
                correction_metrics.load_repair_events(path)
    def test_repair_loader_returns_validated_records(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "repair.jsonl"
            record = {"t": 1.5, "type": "text_repair", "action": "undo",
                      "cue_id": "correction-0000", "clock": "monotonic"}
            path.write_text(json.dumps(record) + "\n", encoding="utf-8")
            self.assertEqual(correction_metrics.load_repair_events(path), [record])

    def test_evaluate_uses_motion_detector_and_manifest(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            capture = root / "capture.jsonl"
            with kinematics.Recorder(capture) as recorder:
                for i in range(20):
                    recorder.frame(1.0 + i * 0.011,
                                   {1: (float(i * 2), 0.0, 1.0)})
            manifest = root / "capture.manifest.jsonl"
            manifest.write_text(json.dumps({
                "label": "corr_undo", "cue_id": "correction-0000",
                "t_start": 1.0, "t_end": 2.0, "correction_block": True,
            }) + "\n", encoding="utf-8")
            report = correction_metrics.evaluate(capture)
        self.assertEqual(report["undo_cues"], 1)
        self.assertEqual(report["motion_observed"], 1)
        self.assertEqual(report["detail"][0]["motion_status"], "DETECTED")


if __name__ == "__main__":
    unittest.main()
