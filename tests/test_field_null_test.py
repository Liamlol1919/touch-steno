import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import field_null_test as fnt  # noqa: E402

LABELS = [f"c{i // 3}" for i in range(24)]  # 8 classes, 3 per class


class TestPermutationFunction(unittest.TestCase):
    def test_fixed_seed_returns_the_same_assignments(self):
        first = fnt.permuted_labels(LABELS, 16, seed=20260925)
        second = fnt.permuted_labels(LABELS, 16, seed=20260925)
        self.assertEqual(first, second)
        self.assertEqual(len(first), 16)

    def test_a_different_seed_returns_a_different_draw(self):
        first = fnt.permuted_labels(LABELS, 16, seed=1)
        second = fnt.permuted_labels(LABELS, 16, seed=2)
        self.assertNotEqual(first, second)

    def test_every_assignment_is_a_permutation_of_the_original_labels(self):
        for assignment in fnt.permuted_labels(LABELS, 32, seed=7):
            self.assertEqual(sorted(assignment), sorted(LABELS))


class TestNullDistribution(unittest.TestCase):
    def _trials(self):
        return [(label, [float(i), float(i * i + 1.0), float(-i)])
                for i, label in enumerate(LABELS)]

    def test_null_has_the_requested_number_of_samples(self):
        trials = self._trials()
        for n in (1, 5, 30):
            null = fnt.null_distribution(trials, n, seed=3)
            self.assertEqual(len(null), n)
            for acc in null:
                self.assertGreaterEqual(acc, 0.0)
                self.assertLessEqual(acc, 1.0)

    def test_null_is_reproducible_for_a_fixed_seed(self):
        trials = self._trials()
        self.assertEqual(fnt.null_distribution(trials, 10, seed=11),
                         fnt.null_distribution(trials, 10, seed=11))


class TestPValue(unittest.TestCase):
    # Three of these five values (0.5, 0.5, 1.0) are at or above 0.5.
    NULL = [0.0, 0.25, 0.5, 0.5, 1.0]

    def test_fraction_at_or_above_observed(self):
        self.assertAlmostEqual(fnt.one_sided_p_value(self.NULL, 0.5), 3 / 5)

    def test_observed_above_the_whole_null_is_zero(self):
        self.assertEqual(fnt.one_sided_p_value(self.NULL, 1.5), 0.0)

    def test_observed_below_the_whole_null_is_one(self):
        self.assertEqual(fnt.one_sided_p_value(self.NULL, -0.5), 1.0)

    def test_empty_null_is_rejected(self):
        with self.assertRaises(ValueError):
            fnt.one_sided_p_value([], 0.5)


class TestQuantile(unittest.TestCase):
    def test_nearest_rank(self):
        values = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
        self.assertEqual(fnt.quantile(values, 0.5), 5.0)
        self.assertEqual(fnt.quantile(values, 0.95), 10.0)
        self.assertEqual(fnt.quantile(values, 0.0), 1.0)


class TestChanceConcentration(unittest.TestCase):
    """A descriptor set carrying no class information must not separate anything.

    Every class here is the same descriptor vector, so the classifier has nothing to
    separate: the true labels and every permutation of them must all land on 1/8.
    """

    FLAT = [[0.5, 0.25, 1.0, 0.75] for _ in range(24)]

    def _trials(self):
        return sorted(zip(LABELS, self.FLAT), key=lambda t: t[0])

    def test_observed_and_null_both_sit_at_chance(self):
        trials = self._trials()
        self.assertAlmostEqual(fnt.class_mean_top1(trials), 1 / 8)
        null = fnt.null_distribution(trials, 40, seed=5)
        self.assertEqual(len(null), 40)
        for acc in null:
            self.assertAlmostEqual(acc, 1 / 8)

    def test_p_value_of_a_chance_result_against_its_own_null_is_one(self):
        trials = self._trials()
        null = fnt.null_distribution(trials, 20, seed=5)
        self.assertAlmostEqual(fnt.one_sided_p_value(null, fnt.class_mean_top1(trials)),
                               1.0)


if __name__ == "__main__":
    unittest.main()
