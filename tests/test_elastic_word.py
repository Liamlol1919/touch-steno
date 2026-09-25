import math
import unittest

from nextgen import elastic_word


class ElasticWordTests(unittest.TestCase):
    def test_validation_returns_finite_immutable_copy(self):
        source = [[0, 1], [2, 3]]

        validated = elastic_word.validate_trajectory(source)

        self.assertEqual(validated, ((0.0, 1.0), (2.0, 3.0)))
        self.assertIsInstance(validated, tuple)
        self.assertIsInstance(validated[0], tuple)
        source[0][0] = 99
        self.assertEqual(validated[0][0], 0.0)

    def test_validation_rejects_malformed_degenerate_and_unbounded_input(self):
        invalid_cases = (
            ([], ValueError),
            ([(0.0, 0.0)], ValueError),
            ([(0.0, 0.0), (0.0, 0.0)], ValueError),
            ([(0.0,), (1.0, 1.0)], ValueError),
            ([(0.0, 0.0, 0.0), (1.0, 1.0, 1.0)], ValueError),
            ([(0.0, float("nan")), (1.0, 1.0)], ValueError),
            ([(0.0, float("inf")), (1.0, 1.0)], ValueError),
            ([(0.0, True), (1.0, 1.0)], TypeError),
            ("not a trajectory", TypeError),
            (42, TypeError),
        )
        for trajectory, error_type in invalid_cases:
            with self.subTest(trajectory=trajectory):
                with self.assertRaises(error_type):
                    elastic_word.validate_trajectory(trajectory)

    def test_validation_stops_after_configured_point_limit(self):
        consumed = 0

        def points():
            nonlocal consumed
            while True:
                consumed += 1
                yield (float(consumed), 0.0)

        with self.assertRaisesRegex(ValueError, "not exceed 3"):
            elastic_word.validate_trajectory(points(), max_points=3)
        self.assertEqual(consumed, 4)

    def test_resampling_uses_cumulative_arc_length(self):
        trajectory = [(0.0, 0.0), (0.9, 0.0), (1.0, 1.0)]

        sampled = elastic_word.resample_trajectory(trajectory, sample_count=5)

        diagonal = math.sqrt(101.0)
        expected = (
            (0.0, 0.0),
            ((9.0 + diagonal) / 40.0, 0.0),
            (0.95 - 0.45 / diagonal, 0.5 - 4.5 / diagonal),
            (0.975 - 0.225 / diagonal, 0.75 - 2.25 / diagonal),
            (1.0, 1.0),
        )
        for actual, expected_point in zip(sampled, expected):
            for actual_coordinate, expected_coordinate in zip(
                actual, expected_point
            ):
                self.assertAlmostEqual(actual_coordinate, expected_coordinate)

    def test_normalization_removes_translation_uniform_scale_and_density(self):
        sparse = [(0.0, 0.0), (1.0, 0.0), (3.0, 2.0)]
        dense_transformed = [
            (4.0 * x - 20.0, 4.0 * y + 11.0)
            for x, y in ((0.0, 0.0), (0.3, 0.0), (1.0, 0.0), (2.0, 1.0), (3.0, 2.0))
        ]

        first = elastic_word.normalize_trajectory(sparse, sample_count=17)
        second = elastic_word.normalize_trajectory(dense_transformed, sample_count=17)

        self.assertEqual(len(first), 17)
        for actual, expected in zip(first, second):
            self.assertAlmostEqual(actual[0], expected[0], places=12)
            self.assertAlmostEqual(actual[1], expected[1], places=12)
        self.assertAlmostEqual(max(abs(value) for point in first for value in point), 0.5)

    def test_normalization_rejects_invalid_sample_counts_and_huge_range(self):
        with self.assertRaises(TypeError):
            elastic_word.normalize_trajectory([(0.0, 0.0), (1.0, 0.0)], True)
        with self.assertRaises(ValueError):
            elastic_word.normalize_trajectory([(0.0, 0.0), (1.0, 0.0)], 1)
        with self.assertRaises(ValueError):
            elastic_word.normalize_trajectory(
                [(0.0, 0.0), (1.0, 0.0)],
                elastic_word.MAX_RESAMPLE_POINTS + 1,
            )
        with self.assertRaisesRegex(ValueError, "range is too large"):
            elastic_word.normalize_trajectory(
                [(-1e308, 0.0), (1e308, 0.0)], sample_count=2
            )

    def test_bounded_distance_is_zero_for_equivalent_shapes(self):
        template = [(0.0, 0.0), (1.0, 0.0), (3.0, 2.0)]
        candidate = [(9.0, -4.0), (12.0, -4.0), (18.0, 2.0)]

        distance = elastic_word.bounded_distance(candidate, template)

        self.assertEqual(distance, 0.0)
        self.assertTrue(0.0 <= distance <= 1.0)

    def test_template_score_accepts_close_shape_and_abstains_from_far_shape(self):
        template = [(0.0, 0.0), (1.0, 0.0), (2.0, 1.0)]
        close = [(10.0, 5.0), (11.0, 5.0), (12.0, 6.0)]
        far = [(0.0, 1.0), (1.0, 0.0)]

        accepted = elastic_word.score_template(close, template, threshold=0.01)
        rejected = elastic_word.score_template(far, template, threshold=0.25)

        self.assertTrue(accepted.accepted)
        self.assertFalse(accepted.abstained)
        self.assertEqual(accepted.score, 1.0 - accepted.distance)
        self.assertLessEqual(accepted.distance, accepted.threshold)
        self.assertFalse(rejected.accepted)
        self.assertTrue(rejected.abstained)
        self.assertGreater(rejected.distance, rejected.threshold)
        self.assertGreaterEqual(rejected.score, 0.0)
        self.assertLessEqual(rejected.score, 1.0)

    def test_threshold_is_inclusive_and_must_be_bounded(self):
        trajectory = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0)]
        exact = elastic_word.score_template(trajectory, trajectory, threshold=0.0)

        self.assertTrue(exact.accepted)
        for threshold in (-0.01, 1.01, float("nan"), float("inf"), "0.2"):
            with self.subTest(threshold=threshold):
                with self.assertRaises(ValueError):
                    elastic_word.score_template(
                        trajectory, trajectory, threshold=threshold
                    )


if __name__ == "__main__":
    unittest.main()
