import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import kinematics  # noqa: E402
import rest_calibration  # noqa: E402


class TestRestCalibration(unittest.TestCase):
    def _session(self, root: Path, moving: bool) -> Path:
        path = root / ("mover.jsonl" if moving else "rest.jsonl")
        with kinematics.Recorder(path) as recorder:
            for i in range(250):
                x = i * 0.8 if moving else 10.0 + (0.1 if i % 2 else 0.0)
                recorder.frame(i * 0.011, {1: (x, 10.0, 2.0)})
        return path

    def test_artifact_is_replayable_and_does_not_change_defaults(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            rest = self._session(root, moving=False)
            mover = self._session(root, moving=True)
            artifact = rest_calibration.calibrate_user(
                [rest], [mover], user_label="fixture", min_frames=50)
            replay = rest_calibration.replay_sweep(artifact, [rest], [mover])
        self.assertEqual(artifact["schema"], "touchsteno.rest_calibration")
        self.assertEqual(artifact["user_label"], "fixture")
        self.assertTrue(artifact["source_sha256"])
        self.assertTrue(artifact["rest_covariance"])
        self.assertEqual(artifact["production_defaults_unchanged"],
                         {"velocity_mm_s": 40.0, "persistence_frames": 8})
        self.assertTrue(replay["source_hashes_match"])
        self.assertEqual(replay["selected"], artifact["selected"])

    def test_artifact_persists_complete_sweep_rows(self):
        with tempfile.TemporaryDirectory() as td:
            rest = self._session(Path(td), moving=False)
            artifact = rest_calibration.calibrate_user([rest], min_frames=50)
        windows = {row["window_frames"] for row in artifact["candidates"]}
        self.assertEqual(windows, {9, 19, 39})
        self.assertTrue(all(row["rows"] for row in artifact["candidates"]))


if __name__ == "__main__":
    unittest.main()
