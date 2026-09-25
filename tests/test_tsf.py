import json
import math
import unittest
from dataclasses import dataclass
from typing import Any

from nextgen import tsf
from nextgen import tsf_falsifier as falsifier
from nextgen.scientific_comparator import LabelledExample, Observation, SensorFrame, SensorPoint


@dataclass(frozen=True)
class RawFrame:
    monotonic_time_ms: Any
    points: Any


@dataclass(frozen=True)
class RawObservation:
    sequence_id: str
    frames: Any


def frame(points, timestamp):
    return SensorFrame(
        monotonic_time_ms=timestamp,
        points=tuple(SensorPoint(float(x), float(y), 0.5) for x, y in points),
    )


def observation(name, fields):
    return Observation(
        sequence_id=name,
        frames=tuple(frame(points, index * 8.0) for index, points in enumerate(fields)),
    )


def orthogonal_deform(points, amount):
    return tuple((x + amount * x * x, y + amount * x * y) for x, y in points)


def transformed(points, angle, scale, translation):
    cosine = math.cos(angle)
    sine = math.sin(angle)
    return tuple(
        (
            translation[0] + scale * (cosine * x - sine * y),
            translation[1] + scale * (sine * x + cosine * y),
        )
        for x, y in points
    )


def valid_sequence():
    base = ((-0.8, -0.3), (0.7, -0.4), (0.1, 0.8))
    return observation(
        "valid",
        [
            transformed(base, 0.0, 1.0, (0.0, 0.0)),
            transformed(orthogonal_deform(base, 0.10), 0.1, 1.05, (0.4, -0.2)),
            transformed(orthogonal_deform(base, 0.16), -0.2, 0.95, (-0.3, 0.5)),
        ],
    )


class TemporalSetFlowTests(unittest.TestCase):
    def test_point_order_permutation_is_invariant(self):
        original = valid_sequence()
        permuted = Observation(
            sequence_id=original.sequence_id,
            frames=tuple(
                SensorFrame(value.monotonic_time_ms, tuple(reversed(value.points)))
                for value in original.frames
            ),
        )
        self.assertEqual(tsf.describe(original), tsf.describe(permuted))

    def test_translation_rotation_and_positive_uniform_scale_are_nuisance(self):
        original = valid_sequence()
        nuisance = observation(
            "nuisance",
            [
                transformed(points, (0.31, -0.44, 0.62)[index], (0.73, 1.27, 0.91)[index], ((7.0, -4.0), (-3.0, 8.0), (1.0, 2.0))[index])
                for index, points in enumerate(
                    [[(point.x, point.y) for point in value.points] for value in original.frames]
                )
            ],
        )
        left = tsf.describe(original)
        right = tsf.describe(nuisance)
        self.assertIsNotNone(left)
        self.assertIsNotNone(right)
        for left_step, right_step in zip(left.adjacent_residuals, right.adjacent_residuals):
            for left_value, right_value in zip(left_step, right_step):
                self.assertAlmostEqual(left_value, right_value, delta=1.0e-9)

    def test_non_rigid_deformation_changes_descriptor(self):
        base = ((-0.8, -0.3), (0.7, -0.4), (0.1, 0.8))
        weak = observation("weak", [base, orthogonal_deform(base, 0.03), orthogonal_deform(base, 0.05)])
        strong = observation("strong", [base, orthogonal_deform(base, 0.25), orthogonal_deform(base, 0.40)])
        self.assertNotEqual(tsf.describe(weak), tsf.describe(strong))

    def test_gap_duplicate_new_epoch_malformed_and_burst_do_not_emit(self):
        base = ((-0.5, -0.2), (0.5, -0.2), (0.0, 0.6))
        gap = Observation(
            "gap",
            (
                frame(base, 0.0),
                frame(base, 8.0),
                frame(base, 140.0),
                frame(base, 148.0),
            ),
        )
        duplicate = observation("duplicate", [base, (base[0], base[1], base[0], base[2]), base, base])
        new_epoch = RawObservation(
            "new-epoch",
            (RawFrame(80.0, frame(base, 80.0).points), RawFrame(0.0, frame(base, 0.0).points)),
        )
        burst = observation("burst", [[(index * 0.1, 0.0) for index in range(tsf.MAX_POINTS + 1)]] * 2)
        for value in (gap, duplicate, new_epoch, object(), burst):
            with self.subTest(value=type(value).__name__):
                self.assertIsNone(tsf.describe(value))

    def test_descriptor_and_serialized_output_expose_no_identity_or_truth_keys(self):
        descriptor = tsf.describe(valid_sequence())
        self.assertIsNotNone(descriptor)
        encoded_descriptor = json.dumps(descriptor.as_dict(), sort_keys=True).lower()
        for forbidden in ("slot", "tid", "class", "null", "split", "session", "ground_truth"):
            self.assertNotIn(forbidden, encoded_descriptor)

        train = falsifier._generate_train_examples()
        recognizer = falsifier._recognizers()["tsf"].fit(train)
        examples = falsifier._generate_test_examples()[:2]
        encoded_decisions = falsifier.serialize_decisions(examples, recognizer)
        for encoded in encoded_decisions:
            lowered = encoded.lower()
            for forbidden in ("slot", "tid", "class", "null", "split", "session", "ground_truth"):
                self.assertNotIn(forbidden, lowered)

    def test_null_decision_is_made_without_ground_truth(self):
        train = falsifier._generate_train_examples()
        recognizer = falsifier._recognizers()["tsf"].fit(train)
        calibration = falsifier._generate_calibration_examples()
        rows = falsifier.score_serialized_decisions(
            falsifier.serialize_decisions(calibration, recognizer), calibration
        )
        recognizer.threshold = falsifier._select_threshold(rows)
        malformed = RawObservation(
            "decision-input",
            (
                RawFrame(0.0, (SensorPoint(float("nan"), 0.0, 0.5),)),
                RawFrame(8.0, (SensorPoint(0.0, 0.0, 0.5),)),
            ),
        )

        class GroundTruthTrap:
            sequence_id = malformed.sequence_id
            observation = malformed

            @property
            def ground_truth(self):
                raise AssertionError("decision consulted scoring truth")

        encoded = falsifier.serialize_decisions((GroundTruthTrap(),), recognizer)
        decision = json.loads(encoded[0])
        self.assertFalse(decision["accepted"])
        self.assertEqual(decision["confidence"], 0.0)
        self.assertNotIn("ground_truth", encoded[0])

    def test_cardinality_nonfinite_and_time_violations_fail_closed(self):
        base = ((-0.5, -0.2), (0.5, -0.2), (0.0, 0.6))
        mismatch = observation("mismatch", [base, base[:2], base, base])
        nonfinite = RawObservation(
            "nonfinite",
            (
                RawFrame(0.0, (SensorPoint(float("inf"), 0.0, 0.5), SensorPoint(0.0, 1.0, 0.5))),
                RawFrame(8.0, (SensorPoint(0.0, 0.0, 0.5), SensorPoint(1.0, 1.0, 0.5))),
            ),
        )
        nonmonotonic = RawObservation(
            "nonmonotonic",
            (RawFrame(8.0, frame(base, 8.0).points), RawFrame(0.0, frame(base, 0.0).points)),
        )
        self.assertIsNone(tsf.describe(mismatch))
        self.assertIsNone(tsf.describe(nonfinite))
        self.assertIsNone(tsf.describe(nonmonotonic))


class TSFFalsifierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = falsifier.load_frozen_manifest()
        cls.report = falsifier.run_falsifier()

    def test_manifest_freezes_independent_count_matched_split_families(self):
        self.assertFalse(self.manifest["split_independence"]["shared_generator_function"])
        self.assertTrue(self.manifest["fixture"]["count_matched_classes"])
        self.assertEqual(
            len({
                falsifier._generate_train_examples.__code__.co_firstlineno,
                falsifier._generate_calibration_examples.__code__.co_firstlineno,
                falsifier._generate_test_examples.__code__.co_firstlineno,
            }),
            3,
        )
        for split in ("train", "calibration", "test"):
            counts = {
                example.ground_truth.class_label
                for example in getattr(falsifier, f"_generate_{split}_examples")()
                if example.ground_truth.class_label is not None
            }
            self.assertEqual(counts, set(falsifier.CLASSES))

    def test_protocol_uses_train_for_fit_calibration_for_threshold_and_clustered_test(self):
        self.assertTrue(self.manifest["protocol"]["all_positive_train_exemplars_used_for_fitting"])
        self.assertEqual(self.manifest["protocol"]["calibration_selects"], ["acceptance_threshold"])
        self.assertEqual(self.manifest["protocol"]["bootstrap"]["method"], "session_clustered")
        self.assertFalse(self.report["calibration"]["test_used_for_selection"])
        tsf_training = self.report["training"]["per_recognizer"]["tsf"]
        self.assertEqual(
            tsf_training["training_exemplars_used"],
            self.report["training"]["all_train_exemplars_presented"],
        )

    def test_required_controls_margin_and_kill_gates_are_reported_without_forced_claim(self):
        expected_controls = {
            "count_only",
            "centroid_spread_only",
            "instantaneous_shape",
            "current_contact_field",
            "rigid_motion",
        }
        self.assertTrue(expected_controls.issubset(self.report["metrics"]))
        self.assertIn("tsf_vs_best_control", self.report)
        self.assertIn("kill_gates", self.report)
        if not self.report["kill_gate_passed"]:
            self.assertEqual(self.report["claim"], "none")
        if self.report["tsf_vs_best_control"]["margin_ci"]["lower_95"] < 0.10:
            self.assertEqual(self.report["claim"], "none")

    def test_null_decisions_serialize_before_truth_join(self):
        recognizer = falsifier._recognizers()["tsf"].fit(falsifier._generate_train_examples())
        test = falsifier._generate_test_examples()
        encoded = falsifier.serialize_decisions(test, recognizer)
        self.assertEqual(len(encoded), len(test))
        self.assertTrue(all(isinstance(item, str) for item in encoded))
        self.assertTrue(all("class_label" not in json.loads(item) for item in encoded))


if __name__ == "__main__":
    unittest.main()
