import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import lexicon_recovery  # noqa: E402
import lm_recovery  # noqa: E402


class TestLexiconRecovery(unittest.TestCase):
    def _model(self, words):
        return lm_recovery.char_bigram_model(words)

    def test_observed_column_candidates_do_not_receive_target_answer(self):
        sectors = ("E", "NE", "N", "NW", "W", "SW", "S", "SE")
        confusion = {truth: {observed: 0 for observed in sectors} for truth in sectors}
        for truth in sectors:
            confusion[truth]["E"] = 1
        report = lexicon_recovery.evaluate_channel(
            confusion, trials=1, radius_mm=12.0, seed=5,
            words=["cat"], model=self._model(["cat"]))
        self.assertEqual(report["conditioning"], "observed-sector-column")
        self.assertEqual(report["top3_symbol_availability"], 0.6667)
        self.assertEqual(report["word_reachability_rate"], 0.0)
        self.assertEqual(report["unreachable_rate"], 1.0)
        self.assertEqual(report["correction_opportunities_per_word"], 1.0)
        self.assertEqual(report["selected_word_accuracy"], 0.0)

    def test_identity_channel_resolves_target_without_correction(self):
        sectors = ("E", "NE", "N", "NW", "W", "SW", "S", "SE")
        confusion = {truth: {observed: int(truth == observed) for observed in sectors}
                     for truth in sectors}
        report = lexicon_recovery.evaluate_channel(
            confusion, trials=1, radius_mm=20.0, seed=5,
            words=["cat"], model=self._model(["cat"]))
        self.assertEqual(report["top1_symbol_accuracy"], 1.0)
        self.assertEqual(report["top3_symbol_availability"], 1.0)
        self.assertEqual(report["word_reachability_rate"], 1.0)
        self.assertEqual(report["selected_word_accuracy"], 1.0)
        self.assertEqual(report["correction_opportunities_per_word"], 0.0)

    def test_legacy_recovery_run_uses_the_shared_channel_helpers(self):
        words = ["cat", "cot", "act", "ace"]
        result = lm_recovery.run(2, 12.0, 5, words, self._model(words))
        self.assertEqual(result["words"], 2)
        self.assertIn("lm_word_accuracy", result)

    def test_shared_candidates_are_normalized_from_the_observed_column(self):
        sectors = ("E", "NE", "N", "NW", "W", "SW", "S", "SE")
        confusion = {truth: {observed: 0 for observed in sectors} for truth in sectors}
        for truth in sectors:
            confusion[truth]["E"] = 1
        candidates = lm_recovery.top_candidates("E", confusion)
        self.assertEqual(len(candidates), 3)
        self.assertEqual([row["text"] for row in candidates], ["a", "c", "e"])
        self.assertTrue(all(row["source"] == "observed-sector-column"
                            for row in candidates))
    def test_unequal_detection_rows_use_uniform_prior_posterior(self):
        sectors = ("E", "NE", "N", "NW", "W", "SW", "S", "SE")
        confusion = {truth: {observed: 0 for observed in sectors} for truth in sectors}
        confusion["N"].update({"E": 9, "N": 1})
        confusion["S"].update({"E": 1})
        candidates = lm_recovery.top_candidates("E", confusion)
        by_text = {row["text"]: row["confidence"] for row in candidates}
        self.assertGreater(by_text["c"], by_text["t"])
        self.assertAlmostEqual(sum(row["confidence"] for row in candidates), 1.0)

    def test_top1_metrics_are_posterior_not_observed_label(self):
        sectors = ("E", "NE", "N", "NW", "W", "SW", "S", "SE")
        confusion = {truth: {observed: 0 for observed in sectors} for truth in sectors}
        confusion["E"]["E"] = 1
        confusion["NW"]["E"] = 1
        report = lexicon_recovery.evaluate_channel(
            confusion, trials=1, radius_mm=12.0, seed=5,
            words=["eee"], model=self._model(["eee"]))
        self.assertEqual(report["top1_word_accuracy"], 0.0)
        self.assertEqual(report["observed_word_accuracy"], 1.0)
        self.assertEqual(report["top3_word_reachability_rate"], 1.0)
        self.assertEqual(report["selected_word_accuracy_conditional_reachable"], 1.0)


if __name__ == "__main__":
    unittest.main()
