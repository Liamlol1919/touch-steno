import json
import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import reshape_probe  # noqa: E402


class ReshapeProbeTest(unittest.TestCase):
    @staticmethod
    def frame(timestamp, count):
        return {
            "t": timestamp,
            "c": {
                str(index): [float(index), 1.0, 2.0, 1.0, 0.25]
                for index in range(count)
            },
        }

    def test_postures_are_the_six_named_postures(self):
        self.assertEqual(
            reshape_probe.POSTURE_LABELS,
            ("STILL", "FIST", "ONE_FINGER", "TWO_FINGER", "SPREAD_HOLD", "HOVER_THUMB"),
        )
        self.assertEqual(len(reshape_probe.POSTURES), 6)
        self.assertTrue(all(cue for _label, cue in reshape_probe.POSTURES))

    def test_manifest_writer_emits_one_parseable_record_per_cue(self):
        records = [
            {
                "label": f"reshape_{label.lower()}",
                "posture": label,
                "cue": cue,
                "practice": False,
                "t_start": float(index),
                "t_end": float(index) + 1.0,
            }
            for index, (label, cue) in enumerate(reshape_probe.POSTURES)
        ]
        path = Path(self._temp_name())
        try:
            self.assertEqual(reshape_probe.write_manifest(path, records), 6)
            parsed = [json.loads(line) for line in path.read_text().splitlines()]
        finally:
            path.unlink(missing_ok=True)
        self.assertEqual(len(parsed), 6)
        self.assertEqual([row["posture"] for row in parsed], list(reshape_probe.POSTURE_LABELS))
        self.assertTrue(all(row["cue"] for row in parsed))
        self.assertTrue(all(row["practice"] is False for row in parsed))

    def test_analyser_reports_contact_mean_and_u_lower_bound(self):
        frames = [self.frame(0.1, 1), self.frame(0.2, 2), self.frame(0.3, 3)]
        manifest = [{
            "label": "reshape_two_finger", "posture": "TWO_FINGER",
            "cue": "hold two fingers", "practice": False,
            "t_start": 0.0, "t_end": 1.0,
        }]
        report = reshape_probe.analyse(frames, manifest)
        summary = report["postures"]["TWO_FINGER"]
        self.assertEqual(summary["trials"], 1)
        self.assertAlmostEqual(summary["mean_contact_count"], 2.0)
        self.assertAlmostEqual(summary["frames_with_two_or_more_fraction"], 2 / 3)
        self.assertAlmostEqual(summary["U_lower_bound"], 2 / 3)
        self.assertIn("LOWER bound", report["note"])

    def test_window_with_too_few_samples_is_rejected(self):
        frames = [self.frame(0.1, 1), self.frame(0.2, 1)]
        manifest = [{
            "label": "reshape_still", "posture": "STILL",
            "cue": "hold still", "practice": False,
            "t_start": 0.0, "t_end": 1.0,
        }]
        summary = reshape_probe.analyse(frames, manifest)["postures"]["STILL"]
        self.assertTrue(summary["rejected"])
        self.assertEqual(summary["trials"], 0)
        self.assertIn("fewer than 3 usable samples", summary["reason"])

    def test_all_singleton_and_ten_contact_sets_bound_u(self):
        singleton = [self.frame(0.1, 1), self.frame(0.2, 1), self.frame(0.3, 1)]
        ten = [self.frame(0.1, 10), self.frame(0.2, 10), self.frame(0.3, 10)]
        manifest = [{
            "label": "reshape_hover_thumb", "posture": "HOVER_THUMB",
            "cue": "hover thumb", "practice": False,
            "t_start": 0.0, "t_end": 1.0,
        }]
        singleton_u = reshape_probe.analyse(singleton, manifest)["postures"]["HOVER_THUMB"]["U_lower_bound"]
        ten_u = reshape_probe.analyse(ten, manifest)["postures"]["HOVER_THUMB"]["U_lower_bound"]
        self.assertAlmostEqual(singleton_u, 0.0)
        self.assertAlmostEqual(ten_u, 1.0)

    @staticmethod
    def _temp_name():
        import tempfile
        return tempfile.NamedTemporaryFile(delete=False).name


if __name__ == "__main__":
    unittest.main()
