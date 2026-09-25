import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import lexicon_decoder  # noqa: E402


class TestLexiconDecoder(unittest.TestCase):
    def test_searches_beyond_top_one_and_preserves_provenance(self):
        positions = [
            [{"text": "x", "confidence": 0.8, "source": "sensor", "slot": 0},
             {"text": "c", "confidence": 0.2, "source": "sensor", "slot": 0}],
            [{"text": "a", "confidence": 0.7, "source": "sensor", "slot": 0}],
            [{"text": "t", "confidence": 0.6, "source": "sensor", "slot": 0}],
        ]
        report = lexicon_decoder.decode_word(positions, ["cat"])
        self.assertEqual(report["status"], "resolved")
        self.assertEqual(report["selected"]["text"], "cat")
        self.assertEqual(report["selected"]["candidate_indices"], [1, 0, 0])
        self.assertEqual(report["selected"]["provenance"][0]["source"], "sensor")

    def test_language_prior_only_breaks_an_exact_sensor_tie(self):
        positions = [
            [{"text": "c", "confidence": 0.5}],
            [{"text": "a", "confidence": 0.5}, {"text": "u", "confidence": 0.5}],
            [{"text": "t", "confidence": 0.5}],
        ]
        report = lexicon_decoder.decode_word(
            positions, ["cat", "cut"], {"cut": 1.0, "cat": 0.0})
        self.assertEqual(report["status"], "resolved")
        self.assertEqual(report["selected"]["text"], "cut")
        self.assertAlmostEqual(report["selected"]["sensor_score"],
                               report["ranked"][1]["sensor_score"])

    def test_no_reachable_word_returns_no_proposal(self):
        positions = [[{"text": "q", "confidence": 0.9}]]
        report = lexicon_decoder.decode_word(positions, ["cat"])
        self.assertEqual(report["status"], "unreachable")
        self.assertIsNone(report["selected"])
        self.assertEqual(report["ranked"], [])

    def test_equal_sensor_and_prior_scores_are_explicitly_ambiguous(self):
        positions = [
            [{"text": "c", "confidence": 0.5}],
            [{"text": "a", "confidence": 0.5}, {"text": "u", "confidence": 0.5}],
            [{"text": "t", "confidence": 0.5}],
        ]
        report = lexicon_decoder.decode_word(positions, ["cut", "cat"])
        self.assertEqual(report["status"], "ambiguous")
        self.assertEqual(report["selected"]["text"], "cat")
        self.assertEqual(report["reachable_word_count"], 2)

    def test_invalid_candidate_fails_closed(self):
        with self.assertRaises(ValueError):
            lexicon_decoder.decode_word([[{"text": "cc", "confidence": 0.5}]], ["cc"])
        with self.assertRaises(ValueError):
            lexicon_decoder.decode_word([[{"text": "c", "confidence": 0.0}]], ["c"])
        with self.assertRaises(ValueError):
            lexicon_decoder.decode_word([[{"text": "c", "confidence": 0.5}],
                                         [{"text": "a", "confidence": 0.5}]], ["ca", "ca"])


if __name__ == "__main__":
    unittest.main()
