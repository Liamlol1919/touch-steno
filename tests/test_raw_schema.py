import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import kinematics  # noqa: E402
import raw_schema  # noqa: E402


class TestRawFrameSchema(unittest.TestCase):
    def test_encoded_frame_has_explicit_schema_and_version(self):
        frame = raw_schema.encode_frame(1.25, {"7": [2.0, 3.0, 4.0]})
        self.assertEqual(frame["schema"], raw_schema.SCHEMA)
        self.assertEqual(frame["version"], raw_schema.VERSION)
        self.assertEqual(frame["t"], 1.25)

    def test_legacy_frame_decodes_to_canonical_shape(self):
        frame = raw_schema.decode_record({"t": "1.5", "c": {"1": [2, 3, 4]}})
        self.assertEqual(frame, {"t": 1.5, "c": {"1": [2, 3, 4]}})

    def test_v1_frame_decodes_to_canonical_shape(self):
        encoded = raw_schema.encode_frame(1.5, {"1": [2, 3, 4]})
        self.assertEqual(raw_schema.decode_record(encoded),
                         {"t": 1.5, "c": {"1": [2, 3, 4]}})

    def test_unknown_schema_fails_closed(self):
        with self.assertRaises(ValueError):
            raw_schema.decode_record({"schema": "other", "version": 1,
                                      "t": 0.0, "c": {}})

    def test_future_version_fails_closed(self):
        with self.assertRaises(ValueError):
            raw_schema.decode_record({"schema": raw_schema.SCHEMA, "version": 2,
                                      "t": 0.0, "c": {}})

    def test_recorder_round_trip_is_versioned_on_disk_and_legacy_in_memory(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "frames.jsonl"
            with kinematics.Recorder(path) as recorder:
                recorder.frame(0.25, {3: (1.0, 2.0, 3.0)})
            record = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(record["schema"], raw_schema.SCHEMA)
            self.assertEqual(kinematics._load(path),
                             [{"t": 0.25, "c": {"3": [1.0, 2.0, 3.0]}}])


if __name__ == "__main__":
    unittest.main()
