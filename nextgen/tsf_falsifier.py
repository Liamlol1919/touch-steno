"""Frozen synthetic falsifier for the bounded Temporal Set-Flow prototype.

Split generators are deliberately separate implementations.  Training fits all
positive exemplars, calibration selects acceptance thresholds only, and test
metrics use deterministic session-clustered bootstrap.  This is evidence about a
synthetic fixture only; it makes no hardware, human, WPM, correction, product,
Plover, network, or external-repository claim.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
import statistics
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Protocol, Sequence

from nextgen.contact_field import describe_field
from nextgen.scientific_comparator import (
    GroundTruth,
    LabelledExample,
    Observation,
    SensorFrame,
    SensorPoint,
)
from nextgen.tsf import MAX_POINTS, TemporalSetFlow, describe, estimate_rigid_motion

CLASSES = ("alpha", "beta", "gamma")
FRAME_COUNT = 5
FRAME_INTERVAL_MS = 8.0
BOOTSTRAP_REPLICATES = 256
BOOTSTRAP_SEED = 20260925
MIN_MARGIN = 0.10
MIN_POSITIVE_ACCURACY = 0.80
MANIFEST_NAME = "tsf_falsifier_manifest.json"
FROZEN_MANIFEST_SHA256 = "a95f0d18832362b314417c557d615be4802cc869010617113fb75100090ffe7e"

Point = tuple[float, float]
Feature = tuple[float, ...]


def _canonical_digest(manifest: dict[str, Any]) -> str:
    encoded = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def validate_manifest(manifest: dict[str, Any]) -> None:
    digest = _canonical_digest(manifest)
    if digest != FROZEN_MANIFEST_SHA256:
        raise ValueError(
            f"manifest digest mismatch: expected {FROZEN_MANIFEST_SHA256}, got {digest}"
        )


def load_frozen_manifest(path: str | Path | None = None) -> dict[str, Any]:
    manifest_path = Path(path) if path is not None else Path(__file__).resolve().parents[1] / MANIFEST_NAME
    with manifest_path.open("r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    if not isinstance(manifest, dict):
        raise ValueError("frozen manifest must be an object")
    validate_manifest(manifest)
    return manifest


@dataclass(frozen=True)
class _RawFrame:
    monotonic_time_ms: float
    points: tuple[Any, ...]


@dataclass(frozen=True)
class _RawObservation:
    sequence_id: str
    frames: tuple[Any, ...]


def _sensor_point(point: Point, pressure: float) -> SensorPoint:
    return SensorPoint(point[0], point[1], pressure)


def _observation(sequence_id: str, frames: Sequence[Sequence[Point]]) -> Observation:
    return Observation(
        sequence_id=sequence_id,
        frames=tuple(
            SensorFrame(
                monotonic_time_ms=index * FRAME_INTERVAL_MS,
                points=tuple(
                    _sensor_point(point, 0.35 + index * 0.03) for point in points
                ),
            )
            for index, points in enumerate(frames)
        ),
    )


def _unit(direction: tuple[float, float]) -> tuple[float, float]:
    length = math.hypot(*direction)
    if length <= 0.0:
        raise ValueError("direction must be non-zero")
    return direction[0] / length, direction[1] / length


def _similarity(
    points: Sequence[Point], angle: float, scale: float, translation: tuple[float, float]
) -> tuple[Point, ...]:
    cosine = math.cos(angle)
    sine = math.sin(angle)
    return tuple(
        (
            translation[0] + scale * (cosine * x - sine * y),
            translation[1] + scale * (sine * x + cosine * y),
        )
        for x, y in points
    )


def _orthogonal_deform(
    points: Sequence[Point], direction: tuple[float, float], amount: float
) -> tuple[Point, ...]:
    dx, dy = _unit(direction)
    result: list[Point] = []
    for x, y in points:
        projection = dx * x + dy * y
        delta = amount * projection
        result.append((x + delta * dx, y + delta * dy))
    return tuple(result)


def _shear_deform(points: Sequence[Point], amount: float) -> tuple[Point, ...]:
    return tuple((x + amount * y, y + 0.35 * amount * x) for x, y in points)


def _class_direction(index: int) -> tuple[float, float]:
    return _unit((math.cos(index * math.tau / 3.0), math.sin(index * math.tau / 3.0)))


def _tsf_feature(descriptor: TemporalSetFlow | None) -> Feature | None:
    if descriptor is None or len(descriptor.adjacent_residuals) < 2:
        return None
    step_summaries: list[tuple[float, ...]] = []
    for values in descriptor.adjacent_residuals:
        records = [values[index : index + 3] for index in range(2, len(values), 3)]
        if not records:
            return None
        signed_projection = [record[1] for record in records]
        signed_axis = [record[2] for record in records]
        magnitudes = [record[0] for record in records]
        step_summaries.append(
            (
                statistics.fmean(magnitudes),
                max(magnitudes),
                statistics.fmean(signed_projection),
                statistics.fmean(signed_axis),
            )
        )
    feature: list[float] = []
    for column in range(4):
        series = [step[column] for step in step_summaries]
        feature.extend((statistics.fmean(series), statistics.pstdev(series)))
    first_projection = [step[2] for step in step_summaries]
    feature.append(step_summaries[-1][2] - step_summaries[0][2])
    feature.append(step_summaries[-1][3] - step_summaries[0][3])
    feature.append(first_projection[-1] * first_projection[0])
    return tuple(feature)


def _field_feature(observation: Any, *, current: bool) -> Feature | None:
    try:
        frames = observation.frames
        frame = frames[-1] if current else frames[0]
        points = tuple((float(point.x), float(point.y)) for point in frame.points)
        descriptor = describe_field(points)
    except (AttributeError, IndexError, TypeError, ValueError, OverflowError):
        return None
    values = descriptor.feature_vector()
    padded = values + (0.0,) * max(0, 310 - len(values))
    return padded[:310]


def _centroid_spread_feature(observation: Any) -> Feature | None:
    if describe(observation) is None:
        return None
    try:
        first = observation.frames[0].points
        last = observation.frames[-1].points
        first_points = tuple((float(point.x), float(point.y)) for point in first)
        last_points = tuple((float(point.x), float(point.y)) for point in last)
    except (AttributeError, IndexError, TypeError, ValueError, OverflowError):
        return None
    features: list[float] = []
    centers: list[Point] = []
    for points in (first_points, last_points):
        center = (
            statistics.fmean(point[0] for point in points),
            statistics.fmean(point[1] for point in points),
        )
        centered = [(x - center[0], y - center[1]) for x, y in points]
        centers.append(center)
        features.extend(
            (
                math.sqrt(statistics.fmean(x * x + y * y for x, y in centered)),
                statistics.pstdev(x for x, _ in centered),
                statistics.pstdev(y for _, y in centered),
                abs(statistics.fmean(x * x for x, _ in centered) - statistics.fmean(y * y for _, y in centered)),
            )
        )
    reference = max(features[0], features[4], 1.0e-12)
    features.append(math.hypot(centers[1][0] - centers[0][0], centers[1][1] - centers[0][1]) / reference)
    return tuple(features)


def _rigid_feature(observation: Any) -> Feature | None:
    motion = estimate_rigid_motion(observation)
    if motion is None:
        return None
    result: list[float] = []
    for column in range(3):
        series = [step[column] for step in motion]
        result.extend((statistics.fmean(series), statistics.pstdev(series)))
    return tuple(result)


@dataclass(frozen=True)
class FalsifierDecision:
    candidate: str
    confidence: float
    accepted: bool


class FalsifierRecognizer(Protocol):
    threshold: float

    def decide(self, observation: Any) -> FalsifierDecision: ...


class _FeatureRecognizer:
    """Nearest-centroid recognizer with a fail-closed missing-feature decision."""

    def __init__(self, name: str, extractor: Callable[[Any], Feature | None]) -> None:
        self.name = name
        self._extractor = extractor
        self.threshold = 0.5
        self.training_exemplars_used = 0
        self.training_exemplars_by_class: dict[str, int] = {}
        self._centroids: dict[str, Feature] = {}
        self._scale: Feature | None = None

    def fit(self, train: Sequence[LabelledExample]) -> "_FeatureRecognizer":
        by_class: dict[str, list[Feature]] = {name: [] for name in CLASSES}
        for example in train:
            feature = self._extractor(example.observation)
            label = example.ground_truth.class_label
            if label in by_class and feature is not None:
                by_class[label].append(feature)
        if any(not values for values in by_class.values()):
            raise ValueError(f"{self.name} needs every positive class in training")
        self._centroids = {
            label: tuple(statistics.fmean(column) for column in zip(*values))
            for label, values in by_class.items()
        }
        all_values = [value for values in by_class.values() for value in values]
        self._scale = tuple(
            max(1.0e-9, statistics.pstdev(column)) for column in zip(*all_values)
        )
        self.training_exemplars_used = len(train)
        self.training_exemplars_by_class = {
            label: len(values) for label, values in by_class.items()
        }
        return self

    def decide(self, observation: Any) -> FalsifierDecision:
        feature = self._extractor(observation)
        if feature is None or self._scale is None or any(
            not math.isfinite(value) for value in feature
        ):
            return FalsifierDecision(CLASSES[0], 0.0, False)
        distances = {
            label: math.sqrt(
                math.fsum(
                    ((value - center) / scale) ** 2
                    for value, center, scale in zip(feature, centroid, self._scale)
                )
                / len(feature)
            )
            for label, centroid in self._centroids.items()
        }
        candidate = min(CLASSES, key=lambda label: (distances[label], label))
        confidence = math.exp(-0.5 * distances[candidate])
        return FalsifierDecision(candidate, confidence, confidence >= self.threshold)


class _CountOnlyRecognizer(_FeatureRecognizer):
    def __init__(self) -> None:
        super().__init__("count_only", self._count)

    @staticmethod
    def _count(observation: Any) -> Feature | None:
        try:
            count = len(observation.frames[0].points)
        except (AttributeError, IndexError, TypeError):
            return None
        return (math.log1p(count),) if 0 < count <= MAX_POINTS else None

    def decide(self, observation: Any) -> FalsifierDecision:
        feature = self._count(observation)
        if feature is None:
            return FalsifierDecision(CLASSES[0], 0.0, False)
        return FalsifierDecision(CLASSES[0], 1.0 / len(CLASSES), 1.0 / len(CLASSES) >= self.threshold)


def _generate_train_examples() -> tuple[LabelledExample, ...]:
    """Family A: triangles with independent axis-code orthogonal pulses."""
    rng = random.Random(1101)
    rows: list[LabelledExample] = []
    for session_index in range(2):
        for replicate in range(2):
            for class_index, label in enumerate(CLASSES):
                base = ((-0.7, -0.4), (0.75, -0.35), (0.0, 0.8))
                direction = _class_direction(class_index)
                frames: list[list[Point]] = []
                for step in range(FRAME_COUNT):
                    amount = 0.07 + 0.025 * math.sin(step * 1.1 + class_index) + 0.012 * replicate
                    deformed = _orthogonal_deform(base, direction, amount)
                    frames.append(
                        list(
                            _similarity(
                                deformed,
                                rng.uniform(-0.35, 0.35),
                                rng.uniform(0.82, 1.18),
                                (rng.uniform(-4.0, 4.0), rng.uniform(-3.0, 3.0)),
                            )
                        )
                    )
                rows.append(
                    LabelledExample(
                        _observation(f"train-{session_index}-{replicate}-{label}", frames),
                        GroundTruth(f"train-session-{session_index}", label),
                    )
                )
        rest_base = ((-0.6, -0.3), (0.65, -0.3), (0.0, 0.7))
        if session_index == 0:
            rigid = _similarity(rest_base, 0.2, 1.1, (2.0, -1.0))
            null_frames = [list(rigid) for _ in range(FRAME_COUNT)]
        else:
            null_frames = [
                [
                    (x + rng.uniform(-0.004, 0.004), y + rng.uniform(-0.004, 0.004))
                    for x, y in rest_base
                ]
                for _ in range(FRAME_COUNT)
            ]
        rows.append(
            LabelledExample(
                _observation(f"train-null-{session_index}", null_frames),
                GroundTruth(f"train-session-{session_index}", None),
            )
        )
        if session_index == 1:
            burst = [(-0.8 + index * 0.13, math.sin(index)) for index in range(MAX_POINTS + 1)]
            rows.append(
                LabelledExample(
                    _observation("train-null-burst", [burst for _ in range(FRAME_COUNT)]),
                    GroundTruth("train-session-1", None),
                )
            )
            dropping = [list(base) for base in (rest_base, rest_base, rest_base[:2], rest_base, rest_base)]
            rows.append(
                LabelledExample(
                    _observation("train-null-dropout", dropping),
                    GroundTruth("train-session-1", None),
                )
            )
    return tuple(rows)


def _generate_calibration_examples() -> tuple[LabelledExample, ...]:
    """Family B: diamonds with an independent alternating shear family."""
    rng = random.Random(2202)
    rows: list[LabelledExample] = []
    for session_index in range(2):
        for class_index, label in enumerate(CLASSES):
            base = ((0.0, -0.75), (0.7, 0.0), (0.0, 0.75), (-0.7, 0.0), (0.0, 0.0))
            direction = _class_direction(class_index)
            frames: list[list[Point]] = []
            for step in range(FRAME_COUNT):
                signed = 0.055 if (step + class_index) % 2 == 0 else -0.055
                deformed = _shear_deform(
                    _orthogonal_deform(base, direction, signed), signed
                )
                frames.append(
                    list(
                        _similarity(
                            deformed,
                            rng.uniform(-0.5, 0.5),
                            rng.uniform(0.75, 1.25),
                            (rng.uniform(-6.0, 6.0), rng.uniform(-5.0, 5.0)),
                        )
                    )
                )
            rows.append(
                LabelledExample(
                    _observation(f"cal-{session_index}-{label}", frames),
                    GroundTruth(f"cal-session-{session_index}", label),
                )
            )
        if session_index == 0:
            palm = ((-0.8, -0.55), (0.85, -0.5), (0.9, 0.6), (0.0, 0.85), (-0.9, 0.55))
            palm_frames = [
                list(_similarity(palm, 0.1 * step, 1.0 + 0.01 * step, (0.2 * step, -0.1 * step)))
                for step in range(FRAME_COUNT)
            ]
        else:
            palm = ((-0.6, -0.3), (0.6, -0.3), (0.0, 0.7))
            palm_frames = [
                [(x + rng.uniform(-0.008, 0.008), y + rng.uniform(-0.008, 0.008)) for x, y in palm]
                for _ in range(FRAME_COUNT)
            ]
        rows.append(
            LabelledExample(
                _observation(f"cal-null-{session_index}", palm_frames),
                GroundTruth(f"cal-session-{session_index}", None),
            )
        )
    gap_times = (0.0, 8.0, 16.0, 200.0, 24.0)
    gap = ((-0.5, -0.2), (0.5, -0.2), (0.0, 0.6))
    rows.append(
        LabelledExample(
            _RawObservation(
                "cal-null-gap",
                tuple(
                    _RawFrame(
                        gap_times[index],
                        tuple(_sensor_point(point, 0.5) for point in gap),
                    )
                    for index in range(FRAME_COUNT)
                ),
            ),
            GroundTruth("cal-session-1", None),
        )
    )
    duplicate = ((-0.5, -0.2), (0.5, -0.2), (-0.5, -0.2), (0.0, 0.6))
    rows.append(
        LabelledExample(
            _observation("cal-null-duplicate", [duplicate for _ in range(FRAME_COUNT)]),
            GroundTruth("cal-session-1", None),
        )
    )
    return tuple(rows)


def _generate_test_examples() -> tuple[LabelledExample, ...]:
    """Family C: asymmetric hexagons with independent local pinching."""
    rng = random.Random(3303)
    rows: list[LabelledExample] = []
    base = ((-0.8, -0.35), (-0.25, -0.7), (0.45, -0.45), (0.85, 0.1), (0.2, 0.75), (-0.55, 0.45))
    for session_index in range(3):
        for class_index, label in enumerate(CLASSES):
            direction = _unit((0.45 + class_index * 0.2, 0.9 - class_index * 0.25))
            frames: list[list[Point]] = []
            for step in range(FRAME_COUNT):
                amount = 0.06 + 0.02 * math.sin(step * 0.9 + class_index * 0.8)
                deformed: list[Point] = []
                for point_index, (x, y) in enumerate(base):
                    projection = direction[0] * x + direction[1] * y
                    local_phase = 0.45 * math.sin(2.5 * projection + class_index + point_index * 0.2)
                    deformed.append((x + amount * direction[0] * local_phase, y + amount * direction[1] * local_phase))
                frames.append(
                    list(
                        _similarity(
                            tuple(deformed),
                            rng.uniform(-0.7, 0.7),
                            rng.uniform(0.7, 1.3),
                            (rng.uniform(-8.0, 8.0), rng.uniform(-7.0, 7.0)),
                        )
                    )
                )
            rows.append(
                LabelledExample(
                    _observation(f"test-{session_index}-{label}", frames),
                    GroundTruth(f"test-session-{session_index}", label),
                )
            )

        burst = [(-0.9 + index * 0.12, math.cos(index * 0.7)) for index in range(MAX_POINTS + 2)]
        burst_observation = _observation(f"test-null-burst-{session_index}", [burst for _ in range(FRAME_COUNT)])
        malformed_point = SensorPoint(float("nan"), 0.0, 0.5)
        malformed = _RawObservation(
            f"test-null-malformed-{session_index}",
            tuple(
                _RawFrame(
                    index * FRAME_INTERVAL_MS,
                    tuple(_sensor_point(point, 0.5) for point in base[:3])
                    if index != FRAME_COUNT - 1
                    else (malformed_point,),
                )
                for index in range(FRAME_COUNT)
            ),
        )
        reconnect = _RawObservation(
            f"test-null-reconnect-{session_index}",
            tuple(
                _RawFrame(
                    (40.0, 0.0, 8.0, 16.0, 24.0)[index],
                    tuple(_sensor_point(point, 0.5) for point in base),
                )
                for index in range(FRAME_COUNT)
            ),
        )
        new_epoch = _RawObservation(
            f"test-null-new-epoch-{session_index}",
            tuple(
                _RawFrame(
                    (-20.0, 0.0, 8.0, 16.0, 24.0)[index],
                    tuple(_sensor_point(point, 0.5) for point in base),
                )
                for index in range(FRAME_COUNT)
            ),
        )
        dropped = [list(base) for _ in range(FRAME_COUNT)]
        dropped[2] = dropped[2][:4]
        nulls = (
            (burst_observation, "rigid_label_placeholder"),
            (burst_observation, "burst"),
            (malformed, "malformed"),
            (_observation(f"test-null-dropout-{session_index}", dropped), "dropout"),
            (reconnect, "reconnect"),
            (new_epoch, "new_epoch"),
        )
        observation, null_name = nulls[session_index]
        if null_name == "rigid_label_placeholder":
            observation = _observation(
                f"test-null-rigid-{session_index}",
                [
                    list(_similarity(base, 0.15 * step, 1.0 + 0.03 * step, (0.4 * step, -0.2 * step)))
                    for step in range(FRAME_COUNT)
                ],
            )
        rows.append(
            LabelledExample(
                observation,
                GroundTruth(f"test-session-{session_index}", None),
            )
        )
    return tuple(rows)


def serialize_decisions(
    examples: Sequence[LabelledExample], recognizer: FalsifierRecognizer
) -> tuple[str, ...]:
    """Serialize observation-only decisions before any scoring metadata is joined."""
    result: list[str] = []
    for example in examples:
        decision = recognizer.decide(example.observation)
        if decision.candidate not in CLASSES or not math.isfinite(decision.confidence):
            raise ValueError("recognizer returned an invalid decision")
        result.append(
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
    return tuple(result)


def score_serialized_decisions(
    serialized: Sequence[str], examples: Sequence[LabelledExample]
) -> list[dict[str, Any]]:
    if len(serialized) != len(examples):
        raise ValueError("decision and example counts differ")
    rows: list[dict[str, Any]] = []
    for encoded, example in zip(serialized, examples):
        decision = json.loads(encoded)
        truth = example.ground_truth
        rows.append(
            {
                "sequence_id": decision["sequence_id"],
                "session_id": truth.session_id,
                "class_label": truth.class_label,
                "candidate": decision["candidate"],
                "confidence": decision["confidence"],
                "accepted": decision["accepted"],
                "correct": bool(
                    truth.class_label is not None
                    and decision["accepted"]
                    and decision["candidate"] == truth.class_label
                ),
            }
        )
    return rows


def _select_threshold(rows: Sequence[dict[str, Any]]) -> float:
    positive = [row["confidence"] for row in rows if row["class_label"] is not None]
    null = [row["confidence"] for row in rows if row["class_label"] is None]
    if not positive or not null:
        raise ValueError("calibration needs positive and null examples")
    return 0.5 * (min(positive) + max(null))


def _cluster_bootstrap(
    rows: Sequence[dict[str, Any]], field: str, *, upper: bool = False
) -> dict[str, Any]:
    sessions = sorted({row["session_id"] for row in rows})
    rng = random.Random(BOOTSTRAP_SEED + (1 if upper else 0))
    estimates: list[float] = []
    for _ in range(BOOTSTRAP_REPLICATES):
        sampled = [rng.choice(sessions) for _ in sessions]
        sample = [row for session in sampled for row in rows if row["session_id"] == session]
        eligible = [
            row
            for row in sample
            if (row["class_label"] is None) == (field == "null_false_commit")
        ]
        if field == "null_false_commit":
            estimates.append(statistics.fmean(bool(row["accepted"]) for row in eligible) if eligible else 1.0)
        else:
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


def _margin_bootstrap(tsf_rows: Sequence[dict[str, Any]], control_rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    sessions = sorted({row["session_id"] for row in tsf_rows})
    rng = random.Random(BOOTSTRAP_SEED + 17)
    estimates: list[float] = []
    for _ in range(BOOTSTRAP_REPLICATES):
        sampled = [rng.choice(sessions) for _ in sessions]
        tsf_sample = [row for session in sampled for row in tsf_rows if row["session_id"] == session]
        control_sample = [row for session in sampled for row in control_rows if row["session_id"] == session]
        tsf_positive = [row for row in tsf_sample if row["class_label"] is not None]
        control_positive = [row for row in control_sample if row["class_label"] is not None]
        estimates.append(
            statistics.fmean(bool(row["correct"]) for row in tsf_positive)
            - statistics.fmean(bool(row["correct"]) for row in control_positive)
        )
    estimates.sort()
    return {
        "lower_95": estimates[round(0.025 * (len(estimates) - 1))],
        "upper_95": estimates[round(0.975 * (len(estimates) - 1))],
        "method": "paired_deterministic_session_cluster_bootstrap",
        "replicates": BOOTSTRAP_REPLICATES,
        "clusters": len(sessions),
    }


def _recognizers() -> dict[str, _FeatureRecognizer]:
    return {
        "tsf": _FeatureRecognizer("tsf", lambda observation: _tsf_feature(describe(observation))),
        "count_only": _CountOnlyRecognizer(),
        "centroid_spread_only": _FeatureRecognizer("centroid_spread_only", _centroid_spread_feature),
        "instantaneous_shape": _FeatureRecognizer("instantaneous_shape", lambda observation: _field_feature(observation, current=False)),
        "current_contact_field": _FeatureRecognizer("current_contact_field", lambda observation: _field_feature(observation, current=True)),
        "rigid_motion": _FeatureRecognizer("rigid_motion", _rigid_feature),
    }


def _evaluate(
    recognizer: _FeatureRecognizer,
    calibration: Sequence[LabelledExample],
    test: Sequence[LabelledExample],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    calibration_rows = score_serialized_decisions(
        serialize_decisions(calibration, recognizer), calibration
    )
    recognizer.threshold = _select_threshold(calibration_rows)
    rows = score_serialized_decisions(serialize_decisions(test, recognizer), test)
    positives = [row for row in rows if row["class_label"] is not None]
    nulls = [row for row in rows if row["class_label"] is None]
    accuracy = statistics.fmean(bool(row["correct"]) for row in positives)
    false_commit = statistics.fmean(bool(row["accepted"]) for row in nulls)
    return (
        {
            "calibration_threshold": recognizer.threshold,
            "positive_accuracy": accuracy,
            "positive_accuracy_ci": _cluster_bootstrap(rows, "accuracy"),
            "null_false_commit_rate": false_commit,
            "null_false_commit_ci": _cluster_bootstrap(rows, "null_false_commit", upper=True),
            "test_examples": len(rows),
            "decisions_serialized_before_truth_join": True,
        },
        rows,
    )


def run_falsifier() -> dict[str, Any]:
    """Run the complete bounded frozen comparison and apply conservative kill gates."""
    load_frozen_manifest()
    train = _generate_train_examples()
    calibration = _generate_calibration_examples()
    test = _generate_test_examples()
    metrics: dict[str, dict[str, Any]] = {}
    scored_by_name: dict[str, list[dict[str, Any]]] = {}
    training: dict[str, Any] = {}
    for name, recognizer in _recognizers().items():
        recognizer.fit(train)
        result, scored = _evaluate(recognizer, calibration, test)
        metrics[name] = result
        scored_by_name[name] = scored
        training[name] = {
            "training_exemplars_used": recognizer.training_exemplars_used,
            "positive_exemplars_by_class": recognizer.training_exemplars_by_class,
        }

    control_names = tuple(name for name in metrics if name != "tsf")
    best_control = max(
        control_names,
        key=lambda name: (metrics[name]["positive_accuracy"], name),
    )
    observed_margin = metrics["tsf"]["positive_accuracy"] - metrics[best_control]["positive_accuracy"]
    margin_ci = _margin_bootstrap(scored_by_name["tsf"], scored_by_name[best_control])
    gates = {
        "null_false_commit_zero": metrics["tsf"]["null_false_commit_rate"] == 0.0,
        "positive_accuracy_minimum": metrics["tsf"]["positive_accuracy"] >= MIN_POSITIVE_ACCURACY,
        "margin_lower_95_minimum": margin_ci["lower_95"] >= MIN_MARGIN,
    }
    claim = "synthetic_margin_observed" if all(gates.values()) else "none"
    return {
        "schema": "TSF-SYNTHETIC-FALSIFIER",
        "frozen_manifest": MANIFEST_NAME,
        "synthetic_only": True,
        "claim_scope": "synthetic fixture only; no device, network, Plover, hardware, human, WPM, correction, or product claim",
        "claim": claim,
        "training": {
            "split_family": "triangles_orthogonal_pulse_A",
            "all_train_exemplars_presented": len(train),
            "per_recognizer": training,
        },
        "calibration": {
            "split_family": "diamonds_alternating_shear_B",
            "selection": "acceptance_threshold_only",
            "test_used_for_selection": False,
        },
        "test": {
            "split_family": "asymmetric_hexagons_local_pinch_C",
            "session_clustered_bootstrap": True,
        },
        "metrics": metrics,
        "tsf_vs_best_control": {
            "best_control": best_control,
            "observed_margin": observed_margin,
            "margin_ci": margin_ci,
            "minimum_required_margin": MIN_MARGIN,
        },
        "kill_gates": gates,
        "kill_gate_passed": all(gates.values()),
    }


__all__ = [
    "BOOTSTRAP_REPLICATES",
    "CLASSES",
    "FalsifierDecision",
    "FalsifierRecognizer",
    "load_frozen_manifest",
    "run_falsifier",
    "serialize_decisions",
    "validate_manifest",
]
