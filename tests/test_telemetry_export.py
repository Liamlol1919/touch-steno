import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import kinematics  # noqa: E402
import telemetry_export  # noqa: E402


class TestTelemetryExport(unittest.TestCase):
    def _session(self, root: Path) -> Path:
        path = root / "private-session-name.jsonl"
        with kinematics.Recorder(path) as recorder:
            for i in range(100):
                recorder.frame(i * 0.011, {1: (10.0, 10.0, 2.0),
                                           2: (30.0, 12.0, 2.0)})
        return path

    def test_export_contains_only_aggregate_privacy_safe_fields(self):
        with tempfile.TemporaryDirectory() as td:
            path = self._session(Path(td))
            report = telemetry_export.export_telemetry([path], min_frames=1)
        encoded = json.dumps(report)
        self.assertEqual(report["schema"], "touchsteno.telemetry")
        self.assertEqual(report["privacy"]["raw_coordinates"], False)
        self.assertEqual(report["privacy"]["contact_ids"], False)
        self.assertEqual(report["privacy"]["session_names"], False)
        self.assertNotIn("private-session-name", encoded)
        self.assertNotIn('"1"', encoded)
        self.assertNotIn('"2"', encoded)
        self.assertIn("contact_groups", report)

    def test_export_writes_strict_json_without_nan(self):
        with tempfile.TemporaryDirectory() as td:
            path = self._session(Path(td))
            out = Path(td) / "telemetry.json"
            report = telemetry_export.export_telemetry([path], min_frames=1)
            out.write_text(json.dumps(report, allow_nan=False), encoding="utf-8")
            self.assertEqual(json.loads(out.read_text(encoding="utf-8"))["version"], 1)


if __name__ == "__main__":
    unittest.main()
