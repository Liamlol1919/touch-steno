import itertools
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from nextgen.english_steno import (  # noqa: E402
    MESSAGE_MASKS,
    STENO_KEYS,
    STROKE_LIBRARY,
    StenoCodec,
    hamming,
    minimum_distance,
)


class TestEnglishStenoTransport(unittest.TestCase):
    def setUp(self):
        self.codec = StenoCodec()

    def test_profile_is_32_nonzero_unique_words_with_distance_four(self):
        self.assertEqual(len(MESSAGE_MASKS), 32)
        self.assertEqual(len(set(MESSAGE_MASKS)), 32)
        self.assertNotIn(0, MESSAGE_MASKS)
        self.assertEqual(minimum_distance(), 4)
        self.assertEqual({stroke.notation for stroke in STROKE_LIBRARY}, {
            stroke.notation for stroke in STROKE_LIBRARY
        })

    def test_every_stroke_uses_only_known_english_steno_keys(self):
        for stroke in STROKE_LIBRARY:
            self.assertTrue(set(stroke.keys) <= STENO_KEYS)
            self.assertEqual(len(stroke.keys), len(set(stroke.keys)))

    def test_all_one_bit_errors_correct_and_two_bit_errors_nack(self):
        for expected in MESSAGE_MASKS:
            self.assertEqual(self.codec.decode_mask(expected).distance, 0)
            for bit in range(10):
                corrected = self.codec.decode_mask(expected ^ (1 << bit))
                self.assertTrue(corrected.ok)
                self.assertEqual(corrected.expected_mask, expected)
                self.assertTrue(corrected.corrected)
            for left, right in itertools.combinations(range(10), 2):
                result = self.codec.decode_mask(expected ^ (1 << left) ^ (1 << right))
                self.assertEqual(result.status, "NACK")

        outline = "A/ST/PH/KW/*"
        masks = self.codec.encode_outline(outline)
        results = self.codec.decode_outline(masks)
        self.assertTrue(all(result.ok for result in results))
        self.assertEqual("/".join(result.stroke.notation for result in results), outline)

    def test_plover_payload_contains_side_specific_keys(self):
        payload = self.codec.plover_json("ST/PH")
        self.assertEqual(payload["v"], 1)
        self.assertEqual(payload["type"], "outline")
        self.assertEqual(payload["strokes"][0]["keys"], ["S-", "T-"])
        self.assertEqual(payload["strokes"][1]["keys"], ["P-", "H-"])

    def test_cli_round_trips_printed_binary_masks(self):
        encoded = subprocess.run(
            [sys.executable, "-m", "nextgen.cli", "encode", "ST/PH"],
            cwd=ROOT, check=True, capture_output=True, text=True,
        )
        masks = json.loads(encoded.stdout)["masks"]
        decoded = subprocess.run(
            [sys.executable, "-m", "nextgen.cli", "decode", ",".join(masks)],
            cwd=ROOT, check=True, capture_output=True, text=True,
        )
        report = json.loads(decoded.stdout)
        self.assertEqual(report["status"], "OK")
        self.assertEqual(
            "/".join(item["notation"] for item in report["results"]),
            "ST/PH",
        )

    def test_invalid_outline_does_not_emit_text(self):
        with self.assertRaises(ValueError):
            self.codec.encode_outline("ST/NOT-A-STROKE")
        with self.assertRaises(ValueError):
            self.codec.encode_outline("ST//PH")


if __name__ == "__main__":
    unittest.main()
