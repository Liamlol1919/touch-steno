"""Test 0's decision-isolated synthetic comparator.

This module validates an evidence boundary for a future recognizer.  It does not
implement Temporal Set-Flow and makes no hardware, human-performance, or
product claim.  It has no device, network, or file-writing dependency.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from dataclasses import dataclass, replace
import json
import math
import random
import statistics
from typing import Any, Protocol, Sequence

CLASSES = ("alpha", "beta", "gamma")
FRAME_COUNT = 5
FRAME_INTERVAL_MS = 8.0
POSITIVE_CONTACT_COUNT = 4
BOOTSTRAP_REPLICATES = 256
BOOTSTRAP_SEED = 20260925
NULL_FALSE_COMMIT_GATE = 0.0
CHANCE = 1.0 / len(CLASSES)
MANIFEST_NAME = "synthetic_comparator_manifest.json"
FROZEN_MANIFEST_SHA256 = "922524b495753bd2f4394380b850f4d788c4b38b9af4ea057e57414fe601a25f"


def _canonical_digest(manifest: dict[str, Any]) -> str:
    encoded = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def validate_manifest(manifest: dict[str, Any]) -> None:
    """Validate the immutable Test 0 manifest and reject every mutation."""
    if not isinstance(manifest, dict):
        raise ValueError("manifest must be a JSON object")
    if manifest.get("schema") != "SCIENTIFIC-COMPARATOR-TEST-0":
        raise ValueError("manifest schema is not SCIENTIFIC-COMPARATOR-TEST-0")
    if manifest.get("synthetic_only") is not True or manifest.get("hardware_validity") is not False:
        raise ValueError("manifest must remain synthetic-only with no hardware validity")
    digest = _canonical_digest(manifest)
    if digest != FROZEN_MANIFEST_SHA256:
        raise ValueError(f"manifest digest mismatch: expected {FROZEN_MANIFEST_SHA256}, got {digest}")


def load_frozen_manifest(path: str | Path | None = None) -> dict[str, Any]:
    """Read and verify the canonical frozen manifest without writing anything."""
    manifest_path = Path(path) if path is not None else Path(__file__).resolve().parents[1] / MANIFEST_NAME
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot load frozen manifest: {exc}") from exc
    validate_manifest(manifest)
    return manifest


@dataclass(frozen=True)
class SensorPoint:
    """A sensor-native point; no contact identity or class meaning is present."""

    x: float
    y: float
    pressure: float


@dataclass(frozen=True)
class SensorFrame:
    """One timestamped, unordered contact set."""

    monotonic_time_ms: float
    points: tuple[SensorPoint, ...]


@dataclass(frozen=True)
class Observation:
    """The complete decision boundary: sequence ID, time, and native points."""

    sequence_id: str
    frames: tuple[SensorFrame, ...]

    def __post_init__(self) -> None:
        if not self.sequence_id or not self.frames:
            raise ValueError("an observation needs a sequence ID and frames")
        times = [frame.monotonic_time_ms for frame in self.frames]
        if any(right <= left for left, right in zip(times, times[1:])):
            raise ValueError("frame times must be strictly monotonic")
        if any(not frame.points for frame in self.frames):
            raise ValueError("frames must contain sensor points")


@dataclass(frozen=True)
class GroundTruth:
    """Scoring-only metadata, deliberately outside ``Observation``."""

    session_id: str
    class_label: str | None


@dataclass(frozen=True)
class LabelledExample:
    observation: Observation
    ground_truth: GroundTruth


@dataclass(frozen=True)
class RecognitionDecision:
    candidate: str
    confidence: float
    accepted: bool


class Recognizer(Protocol):
    def decide(self, observation: Observation) -> RecognitionDecision: ...


def _generate_train_examples() -> tuple[LabelledExample, ...]:
    """Family A: polygonal fields translating along fixed class axes."""
    rows: list[LabelledExample] = []
    for session_index in range(4):
        for class_index, class_label in enumerate(CLASSES):
            for repetition in range(3):
                rng = random.Random(11003 + 701 * session_index + 97 * class_index + repetition)
                translation_x = (0.145, 0.0, -0.105)[class_index]
                translation_y = (0.0, 0.145, -0.105)[class_index]
                scale = 0.88 + repetition * 0.07
                offset_x = rng.uniform(-0.035, 0.035)
                offset_y = rng.uniform(-0.035, 0.035)
                frames: list[SensorFrame] = []
                for frame_index in range(FRAME_COUNT):
                    center_x = offset_x + translation_x * frame_index
                    center_y = offset_y + translation_y * frame_index
                    points = tuple(
                        SensorPoint(
                            center_x + scale * x + rng.uniform(-0.006, 0.006),
                            center_y + scale * y + rng.uniform(-0.006, 0.006),
                            0.50 + 0.04 * ((point_index + repetition) % 3),
                        )
                        for point_index, (x, y) in enumerate(
                            ((0.18, 0.0), (0.0, 0.15), (-0.16, 0.0), (0.0, -0.15))
                        )
                    )
                    frames.append(SensorFrame(frame_index * FRAME_INTERVAL_MS, points))
                sequence_number = 100 * session_index + 10 * class_index + repetition
                sequence_id = f"fixture-{sequence_number:03d}"
                rows.append(
                    LabelledExample(
                        Observation(sequence_id, tuple(frames)),
                        GroundTruth(f"train-session-{session_index}", class_label),
                    )
                )
        for null_index in range(2):
            rng = random.Random(19001 + 97 * session_index + null_index)
            side = 0.10 + null_index * 0.025
            frames = tuple(
                SensorFrame(
                    frame_index * FRAME_INTERVAL_MS,
                    (
                        SensorPoint(
                            rng.uniform(-0.015, 0.015) + (0.0 if frame_index < 3 else 0.018),
                            rng.uniform(-0.015, 0.015),
                            0.47,
                        ),
                        SensorPoint(
                            rng.uniform(-0.015, 0.015),
                            side + rng.uniform(-0.015, 0.015),
                            0.49,
                        ),
                    ),
                )
                for frame_index in range(FRAME_COUNT)
            )
            sequence_id = f"fixture-{400 + 10 * session_index + null_index:03d}"
            rows.append(
                LabelledExample(
                    Observation(sequence_id, frames),
                    GroundTruth(f"train-session-{session_index}", None),
                )
            )
    return tuple(rows)


def _generate_calibration_examples() -> tuple[LabelledExample, ...]:
    """Family B: diamond fields using eased, axis-biased temporal pulses."""
    rows: list[LabelledExample] = []
    vectors = ((0.135, 0.0), (0.0, 0.135), (-0.095, -0.095))
    for session_index in range(3):
        for class_index, class_label in enumerate(CLASSES):
            for repetition in range(2):
                rng = random.Random(31009 + 509 * session_index + 83 * class_index + 31 * repetition)
                phase = repetition * 0.7
                drift_x = rng.uniform(-0.02, 0.02)
                drift_y = rng.uniform(-0.02, 0.02)
                frames: list[SensorFrame] = []
                for frame_index in range(FRAME_COUNT):
                    eased = frame_index / (FRAME_COUNT - 1)
                    pulse = 0.75 + 0.25 * math.sin(math.pi * eased + phase)
                    center_x = drift_x + vectors[class_index][0] * eased * pulse
                    center_y = drift_y + vectors[class_index][1] * eased * pulse
                    radius = 0.12 + 0.025 * repetition
                    diamond = ((0.0, radius), (radius, 0.0), (0.0, -radius), (-radius, 0.0))
                    points = tuple(
                        SensorPoint(
                            center_x + x + rng.uniform(-0.004, 0.004),
                            center_y + y + rng.uniform(-0.004, 0.004),
                            0.52 + 0.015 * ((point_index + frame_index) % 2),
                        )
                        for point_index, (x, y) in enumerate(diamond)
                    )
                    frames.append(SensorFrame(frame_index * FRAME_INTERVAL_MS, points))
                sequence_number = 1000 + 100 * session_index + 10 * class_index + repetition
                sequence_id = f"fixture-{sequence_number:04d}"
                rows.append(
                    LabelledExample(
                        Observation(sequence_id, tuple(frames)),
                        GroundTruth(f"calibration-session-{session_index}", class_label),
                    )
                )
        for null_index in range(2):
            rng = random.Random(37009 + 101 * session_index + null_index)
            frames = tuple(
                SensorFrame(
                    frame_index * FRAME_INTERVAL_MS,
                    (
                        SensorPoint(rng.uniform(-0.01, 0.01), rng.uniform(-0.01, 0.01), 0.48),
                        SensorPoint(rng.uniform(0.08, 0.11), rng.uniform(-0.01, 0.01), 0.50),
                    ),
                )
                for frame_index in range(FRAME_COUNT)
            )
            sequence_id = f"fixture-{1400 + 10 * session_index + null_index:04d}"
            rows.append(
                LabelledExample(
                    Observation(sequence_id, frames),
                    GroundTruth(f"calibration-session-{session_index}", None),
                )
            )
    return tuple(rows)


def _generate_test_examples() -> tuple[LabelledExample, ...]:
    """Family C: rectangular fields with a rotated, alternating twist."""
    rows: list[LabelledExample] = []
    directions = ((0.13, 0.0), (0.0, 0.13), (-0.09, -0.09))
    for session_index in range(4):
        for class_index, class_label in enumerate(CLASSES):
            for repetition in range(3):
                rng = random.Random(51011 + 613 * session_index + 71 * class_index + 29 * repetition)
                start_x = rng.uniform(-0.025, 0.025)
                start_y = rng.uniform(-0.025, 0.025)
                frames: list[SensorFrame] = []
                for frame_index in range(FRAME_COUNT):
                    progress = frame_index / (FRAME_COUNT - 1)
                    center_x = start_x + directions[class_index][0] * progress
                    center_y = start_y + directions[class_index][1] * progress
                    twist = (-1.0 if frame_index % 2 else 1.0) * 0.08
                    cosine = math.cos(twist)
                    sine = math.sin(twist)
                    rectangle = ((-0.19, -0.09), (0.19, -0.09), (0.19, 0.09), (-0.19, 0.09))
                    points = tuple(
                        SensorPoint(
                            center_x + cosine * x - sine * y + rng.uniform(-0.005, 0.005),
                            center_y + sine * x + cosine * y + rng.uniform(-0.005, 0.005),
                            0.50 + 0.01 * ((point_index + repetition) % 3),
                        )
                        for point_index, (x, y) in enumerate(rectangle)
                    )
                    frames.append(SensorFrame(frame_index * FRAME_INTERVAL_MS, points))
                sequence_number = 2000 + 100 * session_index + 10 * class_index + repetition
                sequence_id = f"fixture-{sequence_number:04d}"
                rows.append(
                    LabelledExample(
                        Observation(sequence_id, tuple(frames)),
                        GroundTruth(f"test-session-{session_index}", class_label),
                    )
                )
        for null_index in range(2):
            rng = random.Random(59011 + 127 * session_index + null_index)
            frames = tuple(
                SensorFrame(
                    frame_index * FRAME_INTERVAL_MS,
                    (
                        SensorPoint(
                            rng.uniform(-0.012, 0.012) + 0.01 * (frame_index % 2),
                            rng.uniform(-0.012, 0.012),
                            0.47,
                        ),
                        SensorPoint(
                            rng.uniform(-0.012, 0.012),
                            0.14 + rng.uniform(-0.012, 0.012),
                            0.49,
                        ),
                    ),
                )
                for frame_index in range(FRAME_COUNT)
            )
            sequence_id = f"fixture-{2400 + 10 * session_index + null_index:04d}"
            rows.append(
                LabelledExample(
                    Observation(sequence_id, frames),
                    GroundTruth(f"test-session-{session_index}", None),
                )
            )
    return tuple(rows)


def _descriptor(observation: Observation) -> tuple[float, ...]:
    """Permutation-invariant center-flow descriptor shared by all families."""
    centers = [
        (
            statistics.fmean(point.x for point in frame.points),
            statistics.fmean(point.y for point in frame.points),
        )
        for frame in observation.frames
    ]
    origin_x, origin_y = centers[0]
    return tuple(
        value
        for center_x, center_y in centers
        for value in (center_x - origin_x, center_y - origin_y)
    )


def _similarity(left: Sequence[float], right: Sequence[float]) -> float:
    root_mean_square = math.sqrt(math.fsum((a - b) ** 2 for a, b in zip(left, right)) / len(left))
    return math.exp(-8.0 * root_mean_square)


class NearestCentroidRecognizer:
    """Nearest-centroid control fitted from every allowed train exemplar."""

    def __init__(self) -> None:
        self.classifier_means: dict[str, tuple[float, ...]] = {}
        self.training_exemplars_used = 0
        self.training_exemplars_by_class: dict[str, int] = {}
        self.threshold = 0.0

    def fit(self, examples: Sequence[LabelledExample]) -> "NearestCentroidRecognizer":
        grouped: dict[str, list[tuple[float, ...]]] = {class_label: [] for class_label in CLASSES}
        for example in examples:
            label = example.ground_truth.class_label
            if label in grouped:
                grouped[label].append(_descriptor(example.observation))
        self.classifier_means = {
            label: tuple(statistics.fmean(values[index] for values in vectors) for index in range(len(vectors[0])))
            for label, vectors in grouped.items()
            if vectors
        }
        self.training_exemplars_by_class = {label: len(vectors) for label, vectors in grouped.items() if vectors}
        self.training_exemplars_used = sum(self.training_exemplars_by_class.values())
        if set(self.classifier_means) != set(CLASSES) or min(self.training_exemplars_by_class.values()) < 2:
            raise ValueError("nearest-centroid fitting requires all classes and multiple exemplars")
        return self

    def decide(self, observation: Observation) -> RecognitionDecision:
        descriptor = _descriptor(observation)
        ranked = sorted(
            ((_similarity(descriptor, mean), class_label) for class_label, mean in self.classifier_means.items()),
            key=lambda item: (-item[0], item[1]),
        )
        confidence, candidate = ranked[0]
        return RecognitionDecision(candidate, confidence, confidence >= self.threshold)


@dataclass
class ShuffledLabelRecognizer:
    """Nearest-centroid integrity control trained on independently shuffled labels."""

    threshold: float = 0.0
    class_means: dict[str, tuple[float, ...]] = None  # type: ignore[assignment]

    @classmethod
    def fit(cls, examples: Sequence[LabelledExample]) -> "ShuffledLabelRecognizer":
        positives = [example for example in examples if example.ground_truth.class_label is not None]
        labels = [example.ground_truth.class_label for example in positives]
        rng = random.Random(0x5EED)
        rng.shuffle(labels)
        shuffled = [
            LabelledExample(example.observation, GroundTruth(example.ground_truth.session_id, label))
            for example, label in zip(positives, labels)
        ]
        nearest = NearestCentroidRecognizer().fit(shuffled)
        return cls(class_means=dict(nearest.classifier_means))

    def decide(self, observation: Observation) -> RecognitionDecision:
        descriptor = _descriptor(observation)
        confidence, candidate = max(
            (_similarity(descriptor, mean), class_label)
            for class_label, mean in self.class_means.items()
        )
        return RecognitionDecision(candidate, confidence, confidence >= self.threshold)


class AlwaysPositiveRecognizer:
    def decide(self, observation: Observation) -> RecognitionDecision:
        return RecognitionDecision(CLASSES[0], 1.0, True)

class CountOnlyRecognizer:
    def decide(self, observation: Observation) -> RecognitionDecision:
        candidate = CLASSES[len(observation.frames[0].points) % len(CLASSES)]
        return RecognitionDecision(candidate, CHANCE, True)


class PathLengthOnlyRecognizer:
    def decide(self, observation: Observation) -> RecognitionDecision:
        centers = [
            (statistics.fmean(point.x for point in frame.points), statistics.fmean(point.y for point in frame.points))
            for frame in observation.frames
        ]
        path_length = math.fsum(math.dist(left, right) for left, right in zip(centers, centers[1:]))
        candidate = CLASSES[min(len(CLASSES) - 1, int(path_length * 10.0) % len(CLASSES))]
        return RecognitionDecision(candidate, CHANCE, True)


def serialize_decisions(
    examples: Sequence[LabelledExample], recognizer: Recognizer
) -> tuple[str, ...]:
    """Run and JSON-serialize every decision before truth is joined for scoring."""
    serialized: list[str] = []
    for example in examples:
        decision = recognizer.decide(example.observation)
        if decision.candidate not in CLASSES or not 0.0 <= decision.confidence <= 1.0:
            raise ValueError("recognizer returned an invalid decision")
        serialized.append(
            json.dumps(
                {
                    "sequence_id": example.observation.sequence_id,
                    "candidate": decision.candidate,
                    "confidence": decision.confidence,
                    "accepted": decision.accepted,
                },
                sort_keys=True,
                separators=(",", ":"),
            )
        )
    return tuple(serialized)


def score_serialized_decisions(
    serialized_decisions: Sequence[str], examples: Sequence[LabelledExample]
) -> list[dict[str, Any]]:
    """Join already-serialized decisions to ground truth for scoring only."""
    if len(serialized_decisions) != len(examples):
        raise ValueError("decision and ground-truth lengths differ")
    scored: list[dict[str, Any]] = []
    for encoded, example in zip(serialized_decisions, examples):
        decision = json.loads(encoded)
        if decision["sequence_id"] != example.observation.sequence_id:
            raise ValueError("decision sequence IDs do not align with ground truth")
        truth = example.ground_truth
        correct = bool(truth.class_label is not None and decision["accepted"] and decision["candidate"] == truth.class_label)
        scored.append(
            {
                "sequence_id": decision["sequence_id"],
                "session_id": truth.session_id,
                "class_label": truth.class_label,
                "candidate": decision["candidate"],
                "confidence": decision["confidence"],
                "accepted": decision["accepted"],
                "correct": correct,
            }
        )
    return scored


def _select_calibration_threshold(calibration_scored: Sequence[dict[str, Any]]) -> float:
    positive_confidences = [row["confidence"] for row in calibration_scored if row["class_label"] is not None]
    null_confidences = [row["confidence"] for row in calibration_scored if row["class_label"] is None]
    if not positive_confidences or not null_confidences:
        raise ValueError("calibration needs positive and null examples")
    return 0.5 * (min(positive_confidences) + max(null_confidences))


def _cluster_bootstrap(
    scored: Sequence[dict[str, Any]], field: str, *, upper: bool = False
) -> dict[str, Any]:
    sessions = sorted({row["session_id"] for row in scored})
    rng = random.Random(BOOTSTRAP_SEED + (1 if upper else 0))
    estimates: list[float] = []
    for _ in range(BOOTSTRAP_REPLICATES):
        sampled_sessions = [rng.choice(sessions) for _ in sessions]
        sample = [row for session in sampled_sessions for row in scored if row["session_id"] == session]
        if field == "null_false_commit":
            eligible = [row for row in sample if row["class_label"] is None]
            estimates.append(statistics.fmean(bool(row["accepted"]) for row in eligible) if eligible else 1.0)
        else:
            eligible = [row for row in sample if row["class_label"] is not None]
            estimates.append(statistics.fmean(bool(row["correct"]) for row in eligible) if eligible else 0.0)
    estimates.sort()
    lower_index = round(0.025 * (len(estimates) - 1))
    upper_index = round(0.975 * (len(estimates) - 1))
    return {
        "lower_95": estimates[lower_index],
        "upper_95": estimates[upper_index],
        "method": "deterministic_session_cluster_bootstrap",
        "replicates": BOOTSTRAP_REPLICATES,
        "clusters": len(sessions),
    }


def evaluate_recognizer(
    recognizer: Recognizer,
    calibration: Sequence[LabelledExample],
    test: Sequence[LabelledExample],
) -> dict[str, Any]:
    """Calibrate on calibration only, freeze acceptance, then score test."""
    calibration_decisions = serialize_decisions(calibration, recognizer)
    calibration_scored = score_serialized_decisions(calibration_decisions, calibration)
    threshold = _select_calibration_threshold(calibration_scored)
    if hasattr(recognizer, "threshold"):
        recognizer.threshold = threshold  # type: ignore[attr-defined]

    test_decisions = serialize_decisions(test, recognizer)
    scored = score_serialized_decisions(test_decisions, test)
    positives = [row for row in scored if row["class_label"] is not None]
    nulls = [row for row in scored if row["class_label"] is None]
    false_commits = [row["sequence_id"] for row in nulls if row["accepted"]]
    null_rate = statistics.fmean(bool(row["accepted"]) for row in nulls) if nulls else 1.0
    return {
        "calibration_threshold": threshold,
        "test_examples": len(scored),
        "positive_accuracy": statistics.fmean(bool(row["correct"]) for row in positives) if positives else 0.0,
        "chance": CHANCE,
        "accepted_count": sum(bool(row["accepted"]) for row in scored),
        "null_false_commit_rate": null_rate,
        "null_false_commit_gate": NULL_FALSE_COMMIT_GATE,
        "null_gate_passed": null_rate <= NULL_FALSE_COMMIT_GATE,
        "null_false_commit_sequence_ids": false_commits,
        "positive_accuracy_ci": _cluster_bootstrap(scored, "accuracy"),
        "null_false_commit_ci": _cluster_bootstrap(scored, "null_false_commit", upper=True),
        "decisions_were_serialized_before_truth_join": True,
    }


def reverse_point_order(example: LabelledExample) -> LabelledExample:
    frames = tuple(replace(frame, points=tuple(reversed(frame.points))) for frame in example.observation.frames)
    return replace(example, observation=replace(example.observation, frames=frames))


def run_comparison() -> dict[str, Any]:
    """Run the complete bounded Test 0 fixture and its integrity controls."""
    manifest = load_frozen_manifest()
    train = _generate_train_examples()
    calibration = _generate_calibration_examples()
    test = _generate_test_examples()
    nearest = NearestCentroidRecognizer().fit(train)
    shuffled = ShuffledLabelRecognizer.fit(train)
    count_only = CountOnlyRecognizer()
    path_only = PathLengthOnlyRecognizer()
    always_positive = AlwaysPositiveRecognizer()

    baseline = evaluate_recognizer(nearest, calibration, test)
    baseline_serialized = serialize_decisions(test, nearest)
    permuted_serialized = serialize_decisions(tuple(reverse_point_order(row) for row in test), nearest)
    permutation_invariant = baseline_serialized == permuted_serialized

    return {
        "schema": "SCIENTIFIC-COMPARATOR-TEST-0",
        "claim_scope": "evidence-boundary validation only; no TSF, hardware, human, WPM, correction, or product evidence",
        "synthetic_only": True,
        "baseline_nearest_centroid": baseline,
        "training": {
            "split_family": "polygonal_field_translation_A",
            "aggregated_training_exemplars": nearest.training_exemplars_used,
            "exemplars_by_class": nearest.training_exemplars_by_class,
        },
        "calibration": {
            "split_family": "diamond_field_pulse_B",
            "selected_acceptance_threshold": baseline["calibration_threshold"],
            "test_used_for_selection": False,
        },
        "test": {
            "split_family": "rectangular_field_twist_C",
            "session_clustered_bootstrap": True,
        },
        "integrity_fixtures": {
            "always_positive": evaluate_recognizer(always_positive, calibration, test),
            "shuffled_label": evaluate_recognizer(shuffled, calibration, test),
            "count_only": evaluate_recognizer(count_only, calibration, test),
            "path_length_nuisance_only": evaluate_recognizer(path_only, calibration, test),
            "point_order_permutation_invariant": permutation_invariant,
            "permutation_semantic_decisions_and_event_count_unchanged": permutation_invariant
            and len(baseline_serialized) == len(test),
        },
    }
