import math
import unittest

from nextgen.contact_field import (
    describe_field,
    field_motion_score,
    normalize_field,
    pairwise_distances,
    pairwise_geometry,
    translate_normalize,
)


class ContactFieldNormalizationTests(unittest.TestCase):
    def test_translation_and_positive_uniform_scale_normalization(self):
        field = [(1.0, 2.0), (3.0, 2.0), (2.0, 4.0)]
        translated = translate_normalize(field)
        self.assertAlmostEqual(math.fsum(x for x, _ in translated), 0.0, places=14)
        self.assertAlmostEqual(math.fsum(y for _, y in translated), 0.0, places=14)

        normalized = normalize_field(field)
        rms = math.sqrt(math.fsum(x * x + y * y for x, y in normalized) / len(normalized))
        self.assertAlmostEqual(rms, 1.0, places=14)

        moved_scaled = [(7.0 * x - 13.0, 7.0 * y + 4.0) for x, y in field]
        moved_normalized = normalize_field(moved_scaled)
        for actual, expected in zip(moved_normalized, normalized):
            self.assertAlmostEqual(actual[0], expected[0], places=14)
            self.assertAlmostEqual(actual[1], expected[1], places=14)

    def test_coincident_and_degenerate_inputs_are_rejected(self):
        for field in ([(1.0, 1.0), (1.0, 1.0)], [(0.0, 0.0)], []):
            with self.subTest(field=field):
                with self.assertRaises(ValueError):
                    normalize_field(field)

    def test_non_finite_contact_is_rejected(self):
        with self.assertRaises(ValueError):
            normalize_field([(0.0, 0.0), (math.inf, 1.0)])


class ContactFieldDescriptorTests(unittest.TestCase):
    def setUp(self):
        self.field = [(-1.0, 0.0), (1.0, 0.0), (0.0, 1.0)]

    def test_descriptor_is_invariant_to_permutation_translation_scale_and_rotation(self):
        theta = 0.73
        cos, sin = math.cos(theta), math.sin(theta)
        transformed = [
            (
                8.0 * (cos * x - sin * y) + 19.0,
                -8.0 * (sin * x + cos * y) - 11.0,
            )
            for x, y in self.field
        ]
        permuted = [transformed[2], transformed[0], transformed[1]]
        baseline = describe_field(self.field)
        actual = describe_field(permuted)
        self.assertEqual(actual.contact_count, baseline.contact_count)
        for actual_value, expected_value in zip(
            actual.normalized_pair_distances, baseline.normalized_pair_distances
        ):
            self.assertAlmostEqual(actual_value, expected_value, places=14)
        for actual_triangle, expected_triangle in zip(
            actual.normalized_triangles, baseline.normalized_triangles
        ):
            for actual_value, expected_value in zip(actual_triangle, expected_triangle):
                self.assertAlmostEqual(actual_value, expected_value, places=14)
        for left, right in zip(actual.normalized_radii, baseline.normalized_radii):
            self.assertAlmostEqual(left, right, places=14)

    def test_variable_cardinality_is_explicit_and_never_padded_or_truncated(self):
        two = describe_field([(0.0, 0.0), (2.0, 0.0)])
        four = describe_field([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)])
        five = describe_field([(x, y) for x in range(3) for y in range(2)])

        self.assertEqual((two.contact_count, four.contact_count, five.contact_count), (2, 4, 6))
        self.assertEqual(len(two.normalized_pair_distances), 1)
        self.assertEqual(len(four.normalized_pair_distances), 6)
        self.assertEqual(len(four.normalized_triangles), 4)
        self.assertEqual(len(five.feature_vector()), 1 + 6 + 15 + 3 * 20)
        self.assertNotEqual(len(four.feature_vector()), len(five.feature_vector()))

    def test_pairwise_summaries_use_normalized_distance_geometry(self):
        field = self.field
        distances = pairwise_distances(field)
        triangles = pairwise_geometry(field)
        self.assertEqual(len(distances), 3)
        for value, expected in zip(distances, (1.5, 1.5, math.sqrt(4.5))):
            self.assertAlmostEqual(value, expected, places=14)
        self.assertEqual(len(triangles), 1)
        for actual, expected in zip(triangles[0], (1.0 / math.sqrt(2.0), 1.0 / math.sqrt(2.0), 1.0)):
            self.assertAlmostEqual(actual, expected, places=14)

        theta = 1.1
        cos, sin = math.cos(theta), math.sin(theta)
        rotated = [(cos * x - sin * y, sin * x + cos * y) for x, y in field]
        for actual, expected in zip(pairwise_distances(rotated), distances):
            self.assertAlmostEqual(actual, expected, places=14)
        for actual, expected in zip(pairwise_geometry(rotated)[0], triangles[0]):
            self.assertAlmostEqual(actual, expected, places=14)


class FieldMotionScoreTests(unittest.TestCase):
    def test_score_is_bounded_and_invariant_to_each_field_nuisance_transform(self):
        previous = [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0)]
        current = [(0.0, 0.0), (0.7, 0.0), (0.0, 0.7)]
        score = field_motion_score(previous, current)

        theta = -0.47
        cos, sin = math.cos(theta), math.sin(theta)
        transformed = lambda field: [
            (5.0 * (cos * x - sin * y) + 100.0, 5.0 * (sin * x + cos * y) - 30.0)
            for x, y in field
        ]
        self.assertAlmostEqual(
            field_motion_score(transformed(previous), transformed(current)), score, places=14
        )
        self.assertTrue(0.0 <= score <= 1.0)

    def test_identical_normalized_field_has_score_one(self):
        field = [(2.0, 3.0), (4.0, 3.0), (3.0, 5.0)]
        self.assertEqual(field_motion_score(field, field), 1.0)

    def test_different_cardinalities_are_handled_without_order_matching(self):
        two = [(0.0, 0.0), (1.0, 0.0)]
        added = [(0.0, 0.0), (0.5, 0.0), (1.0, 0.0)]
        score = field_motion_score(two, added)
        self.assertGreater(score, 0.0)
        self.assertLessEqual(score, 1.0)

    def test_degenerate_pair_has_zero_score_instead_of_unbounded_error(self):
        self.assertEqual(
            field_motion_score([(0.0, 0.0), (0.0, 0.0)], [(0.0, 0.0), (1.0, 0.0)]),
            0.0,
        )


if __name__ == "__main__":
    unittest.main()
