import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROBE = ROOT / "scripts" / "field_gesture_probe.py"


class FieldGestureProbeStartupTest(unittest.TestCase):
    def assert_clean_error(self, result, offending_path):
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")
        self.assertNotIn("Traceback", result.stdout)
        lines = [line for line in result.stdout.splitlines() if line.strip()]
        self.assertEqual(len(lines), 1)
        self.assertTrue(lines[0].startswith("ERROR:"))
        self.assertIn(str(offending_path), lines[0])

    def test_nonexistent_device_is_a_single_clear_error(self):
        with tempfile.TemporaryDirectory() as temporary:
            missing_device = Path(temporary) / "missing-device"
            output = Path(temporary) / "output.jsonl"
            result = subprocess.run(
                [
                    sys.executable,
                    str(PROBE),
                    "--device",
                    str(missing_device),
                    "--out",
                    str(output),
                    "--reps",
                    "0",
                    "--seconds",
                    "0",
                ],
                capture_output=True,
                text=True,
                check=False,
            )

        self.assert_clean_error(result, missing_device)
        self.assertIn("--device", result.stdout)

    def test_nonexistent_replay_capture_is_a_single_clear_error(self):
        with tempfile.TemporaryDirectory() as temporary:
            missing_capture = Path(temporary) / "missing-capture.jsonl"
            manifest = Path(temporary) / "manifest.jsonl"
            manifest.write_text("{}\n", encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(PROBE),
                    "--replay",
                    str(missing_capture),
                    "--manifest",
                    str(manifest),
                ],
                capture_output=True,
                text=True,
                check=False,
            )

        self.assert_clean_error(result, missing_capture)

    def test_malformed_replay_capture_is_a_single_clear_error(self):
        with tempfile.TemporaryDirectory() as temporary:
            capture = Path(temporary) / "malformed-capture.jsonl"
            capture.write_text('{"t": 0, "c": {}\n', encoding="utf-8")
            manifest = Path(temporary) / "manifest.jsonl"
            manifest.write_text("{}\n", encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(PROBE),
                    "--replay",
                    str(capture),
                    "--manifest",
                    str(manifest),
                ],
                capture_output=True,
                text=True,
                check=False,
            )

        self.assert_clean_error(result, capture)
        self.assertIn("invalid JSONL", result.stdout)


if __name__ == "__main__":
    unittest.main()
