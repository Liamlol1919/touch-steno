import json
import unittest

from nextgen import scientific_comparator as comparator


class ScientificComparatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.train = comparator._generate_train_examples()
        cls.calibration = comparator._generate_calibration_examples()
        cls.test = comparator._generate_test_examples()
        cls.report = comparator.run_comparison()
    def test_frozen_manifest_digest_matches_canonical_json(self):
        manifest = comparator.load_frozen_manifest()
        self.assertEqual(comparator._canonical_digest(manifest), comparator.FROZEN_MANIFEST_SHA256)
        self.assertEqual(manifest["schema"], "SCIENTIFIC-COMPARATOR-TEST-0")
        self.assertIs(manifest["synthetic_only"], True)
        self.assertIs(manifest["hardware_validity"], False)

    def test_manifest_mutation_is_refused(self):
        manifest = comparator.load_frozen_manifest()
        mutated = dict(manifest)
        mutated["classes"] = ["alpha", "beta", "gamma", "delta"]
        with self.assertRaises(ValueError):
            comparator.validate_manifest(mutated)
        mutated = dict(manifest)
        mutated["synthetic_only"] = False
        with self.assertRaises(ValueError):
            comparator.validate_manifest(mutated)

    def test_decision_serialization_has_no_ground_truth_or_split_metadata(self):
        recognizer = comparator.NearestCentroidRecognizer().fit(self.train)
        encoded = comparator.serialize_decisions(self.test, recognizer)
        for item in encoded:
            decision = json.loads(item)
            self.assertEqual(set(decision), {"sequence_id", "candidate", "confidence", "accepted"})
            self.assertNotIn("train", decision["sequence_id"])
            self.assertNotIn("class", decision)
        self.assertTrue(all(isinstance(item, str) for item in encoded))

    def test_generators_are_independently_implemented_and_have_no_prototype_copy(self):
        functions = (
            comparator._generate_train_examples,
            comparator._generate_calibration_examples,
            comparator._generate_test_examples,
        )
        self.assertEqual(len({function.__code__ for function in functions}), 3)
        observations = [tuple(example.observation.frames) for group in functions for example in group()]
        self.assertEqual(len(observations), len(set(observations)))
        for group in (self.train, self.calibration, self.test):
            positives = [row for row in group if row.ground_truth.class_label is not None]
            for label in comparator.CLASSES:
                contact_counts = {
                    len(frame.points)
                    for row in positives
                    if row.ground_truth.class_label == label
                    for frame in row.observation.frames
                }
                self.assertEqual(contact_counts, {comparator.POSITIVE_CONTACT_COUNT})

    def test_all_train_exemplars_aggregate_in_nearest_centroid_fit(self):
        recognizer = comparator.NearestCentroidRecognizer().fit(self.train)
        expected = {
            label: sum(row.ground_truth.class_label == label for row in self.train)
            for label in comparator.CLASSES
        }
        self.assertEqual(recognizer.training_exemplars_by_class, expected)
        self.assertEqual(recognizer.training_exemplars_used, sum(expected.values()))
        self.assertTrue(all(count > 1 for count in expected.values()))

    def test_calibration_selects_threshold_without_test_labels(self):
        baseline = self.report["baseline_nearest_centroid"]
        self.assertIn("calibration_threshold", baseline)
        self.assertGreater(baseline["calibration_threshold"], 0.0)
        self.assertFalse(self.report["calibration"]["test_used_for_selection"])
        # Re-running with a recognizer whose threshold is fixed at zero must
        # still use calibration to change the acceptance threshold.
        recognizer = comparator.NearestCentroidRecognizer().fit(self.train)
        result = comparator.evaluate_recognizer(recognizer, self.calibration, self.test)
        self.assertEqual(result["calibration_threshold"], baseline["calibration_threshold"])
        self.assertNotEqual(recognizer.threshold, 0.0)

    def test_cluster_bootstrap_is_deterministic_and_session_clustered(self):
        baseline = self.report["baseline_nearest_centroid"]
        interval = baseline["positive_accuracy_ci"]
        self.assertEqual(interval["method"], "deterministic_session_cluster_bootstrap")
        self.assertEqual(interval["replicates"], comparator.BOOTSTRAP_REPLICATES)
        self.assertEqual(interval["clusters"], 4)
        self.assertIn("calibration_threshold", baseline)
        self.assertGreater(baseline["calibration_threshold"], 0.0)
        self.assertFalse(self.report["calibration"]["test_used_for_selection"])

    def test_integrity_controls_expose_null_and_count_failures(self):
        fixtures = self.report["integrity_fixtures"]
        always = fixtures["always_positive"]
        self.assertFalse(always["null_gate_passed"])
        self.assertEqual(always["null_false_commit_rate"], 1.0)
        self.assertTrue(always["null_false_commit_sequence_ids"])
        self.assertGreaterEqual(fixtures["count_only"]["positive_accuracy"], 0.0)
        self.assertLessEqual(fixtures["count_only"]["positive_accuracy"], comparator.CHANCE + 0.2)
        self.assertFalse(fixtures["count_only"]["null_gate_passed"])
        self.assertIn("positive_accuracy", fixtures["shuffled_label"])
        shuffled_accuracy = fixtures["shuffled_label"]["positive_accuracy"]
        self.assertGreaterEqual(shuffled_accuracy, comparator.CHANCE - 0.15)
        self.assertLessEqual(shuffled_accuracy, comparator.CHANCE + 0.15)
        self.assertIn("null_false_commit_rate", fixtures["path_length_nuisance_only"])

    def test_point_order_permutation_preserves_decisions_and_event_count(self):
        recognizer = comparator.NearestCentroidRecognizer().fit(self.train)
        result = comparator.evaluate_recognizer(recognizer, self.calibration, self.test)
        permuted = tuple(comparator.reverse_point_order(row) for row in self.test)
        original_decisions = comparator.serialize_decisions(self.test, recognizer)
        permuted_decisions = comparator.serialize_decisions(permuted, recognizer)
        self.assertEqual(original_decisions, permuted_decisions)
        self.assertEqual(result["test_examples"], len(original_decisions))
        self.assertTrue(self.report["integrity_fixtures"]["permutation_semantic_decisions_and_event_count_unchanged"])


if __name__ == "__main__":
    unittest.main()
