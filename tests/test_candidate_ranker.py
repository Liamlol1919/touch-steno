import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import candidate_ranker  # noqa: E402


class TestCandidateRanker(unittest.TestCase):
    def test_confidence_only_ranking_preserves_provenance(self):
        report = candidate_ranker.rank_candidates([
            {"text": "cat", "confidence": 0.8, "source": "decoder"},
            {"text": "cut", "confidence": 0.9, "source": "decoder"},
        ])
        self.assertEqual(report["selected"]["text"], "cut")
        self.assertEqual(report["ranked"][0]["candidate"]["source"], "decoder")
        self.assertFalse(report["language_available"])

    def test_language_score_can_change_selection(self):
        report = candidate_ranker.rank_candidates([
            {"text": "cat", "confidence": 0.8},
            {"text": "cut", "confidence": 0.7},
        ], {"cat": 1.0, "cut": 0.0})
        self.assertEqual(report["selected"]["text"], "cat")
        self.assertTrue(report["language_available"])

    def test_invalid_candidate_fails_closed(self):
        with self.assertRaises(ValueError):
            candidate_ranker.rank_candidates([{"text": "", "confidence": 0.5}])


if __name__ == "__main__":
    unittest.main()
