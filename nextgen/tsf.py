"""Bounded, identity-free Temporal Set-Flow research primitives.

The only accepted semantic inputs are timestamped unordered point sets.  Every
adjacent matching and every derived value is local to one call: this module has
no writer, contact identity, slot, or persistent tracking state.  It is a
synthetic-research component, not a device or product implementation.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Iterable, Sequence

Point = tuple[float, float]

MIN_FRAMES = 2
MAX_FRAMES = 8
MIN_POINTS = 2
MAX_POINTS = 12
MIN_FRAME_GAP_MS = 0.1
MAX_FRAME_GAP_MS = 100.0
MAX_RESIDUAL_RATIO = 8.0
_ROUND_DIGITS = 12
_DUPLICATE_TOLERANCE = 1.0e-10
_DEGENERATE_TOLERANCE = 1.0e-12


def _canonical(value: float) -> float:
    rounded = round(float(value), _ROUND_DIGITS)
    return 0.0 if rounded == 0.0 else rounded


def _finite(value: Any) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError, OverflowError):
        return False


def _extract_frames(observation: Any) -> tuple[tuple[float, tuple[Point, ...]], ...] | None:
    """Extract only time and unordered x/y sets, failing closed on every violation."""
    try:
        raw_frames = observation.frames
        frames = tuple(raw_frames)
    except (AttributeError, TypeError, ValueError, OverflowError):
        return None
    if not MIN_FRAMES <= len(frames) <= MAX_FRAMES:
        return None

    result: list[tuple[float, tuple[Point, ...]]] = []
    previous_time: float | None = None
    for frame in frames:
        try:
            timestamp = float(frame.monotonic_time_ms)
            raw_points = tuple(frame.points)
        except (AttributeError, TypeError, ValueError, OverflowError):
            return None
        if not math.isfinite(timestamp):
            return None
        if previous_time is not None:
            gap = timestamp - previous_time
            if not MIN_FRAME_GAP_MS <= gap <= MAX_FRAME_GAP_MS:
                return None
        previous_time = timestamp

        if not MIN_POINTS <= len(raw_points) <= MAX_POINTS:
            return None
        points: list[Point] = []
        for point in raw_points:
            try:
                x = float(point.x)
                y = float(point.y)
            except (AttributeError, TypeError, ValueError, OverflowError):
                return None
            if not math.isfinite(x) or not math.isfinite(y):
                return None
            points.append((x, y))
        if any(
            math.hypot(x1 - x2, y1 - y2) <= _DUPLICATE_TOLERANCE
            for index, (x1, y1) in enumerate(points)
            for x2, y2 in points[index + 1 :]
        ):
            return None
        result.append((timestamp, tuple(sorted(points))))
    return tuple(result)


def _centroid_and_rms(points: Sequence[Point]) -> tuple[Point, float]:
    count = len(points)
    center = (
        math.fsum(point[0] for point in points) / count,
        math.fsum(point[1] for point in points) / count,
    )
    variance = math.fsum(
        (point[0] - center[0]) ** 2 + (point[1] - center[1]) ** 2
        for point in points
    ) / count
    return center, math.sqrt(variance)


def _minimum_cost_assignment(cost: Sequence[Sequence[float]]) -> tuple[int, ...]:
    """Return one deterministic minimum-cost perfect assignment (Hungarian method)."""
    size = len(cost)
    if size == 0 or any(len(row) != size for row in cost):
        raise ValueError("assignment requires a square matrix")
    row_potential = [0.0] * (size + 1)
    column_potential = [0.0] * (size + 1)
    matched_row = [0] * (size + 1)
    predecessor = [0] * (size + 1)

    for row in range(1, size + 1):
        matched_row[0] = row
        column = 0
        minimum = [math.inf] * (size + 1)
        used = [False] * (size + 1)
        while True:
            used[column] = True
            current_row = matched_row[column]
            delta = math.inf
            next_column = 0
            for candidate in range(1, size + 1):
                if used[candidate]:
                    continue
                reduced = (
                    cost[current_row - 1][candidate - 1]
                    - row_potential[current_row]
                    - column_potential[candidate]
                )
                if (
                    reduced < minimum[candidate] - _DEGENERATE_TOLERANCE
                    or (
                        abs(reduced - minimum[candidate]) <= _DEGENERATE_TOLERANCE
                        and candidate < next_column
                    )
                ):
                    minimum[candidate] = reduced
                    predecessor[candidate] = column
                if minimum[candidate] < delta - _DEGENERATE_TOLERANCE:
                    delta = minimum[candidate]
                    next_column = candidate
            if not math.isfinite(delta):
                raise ValueError("assignment has no finite solution")
            for candidate in range(size + 1):
                if used[candidate]:
                    row_potential[matched_row[candidate]] += delta
                    column_potential[candidate] -= delta
                else:
                    minimum[candidate] -= delta
            column = next_column
            if matched_row[column] == 0:
                break
        while True:
            previous = predecessor[column]
            matched_row[column] = matched_row[previous]
            column = previous
            if column == 0:
                break

    assignment = [0] * size
    for column in range(1, size + 1):
        assignment[matched_row[column] - 1] = column - 1
    return tuple(assignment)


def _normalized_assignment(
    previous: Sequence[Point], current: Sequence[Point]
) -> tuple[float, float, tuple[tuple[float, float], ...]]:
    previous_center, previous_rms = _centroid_and_rms(previous)
    current_center, current_rms = _centroid_and_rms(current)
    if previous_rms <= _DEGENERATE_TOLERANCE or current_rms <= _DEGENERATE_TOLERANCE:
        raise ValueError("point sets must have non-zero spatial extent")

    previous_normalized = tuple(
        ((x - previous_center[0]) / previous_rms, (y - previous_center[1]) / previous_rms)
        for x, y in previous
    )
    current_normalized = tuple(
        ((x - current_center[0]) / current_rms, (y - current_center[1]) / current_rms)
        for x, y in current
    )
    cost = tuple(
        tuple(
            (x1 - x2) ** 2 + (y1 - y2) ** 2
            for x2, y2 in current_normalized
        )
        for x1, y1 in previous_normalized
    )
    targets = _minimum_cost_assignment(cost)
    return previous_rms, current_rms, tuple(current_normalized[index] for index in targets)


def _procrustes(
    previous: Sequence[Point],
    current: Sequence[Point],
) -> tuple[float, float, tuple[float, ...]]:
    """Fit positive uniform scale and proper rotation after ephemeral matching."""
    previous_center, previous_rms = _centroid_and_rms(previous)
    current_rms = _centroid_and_rms(current)[1]
    if previous_rms <= _DEGENERATE_TOLERANCE or current_rms <= _DEGENERATE_TOLERANCE:
        raise ValueError("point sets must have non-zero spatial extent")

    targets = _normalized_assignment(previous, current)
    current_norm = targets[2]

    dot = 0.0
    cross = 0.0
    for source, target in zip(previous, current_norm):
        sx = (source[0] - previous_center[0]) / previous_rms
        sy = (source[1] - previous_center[1]) / previous_rms
        dot += sx * target[0] + sy * target[1]
        cross += sx * target[1] - sy * target[0]
    if abs(dot) <= _DEGENERATE_TOLERANCE and abs(cross) <= _DEGENERATE_TOLERANCE:
        raise ValueError("Procrustes transform is indeterminate")
    scale = math.hypot(dot, cross)
    angle = math.atan2(cross, dot)
    cosine = math.cos(angle)
    sine = math.sin(angle)
    values: list[float] = []
    for (x, y), (target_x, target_y) in zip(previous, current_norm):
        source_x = (x - previous_center[0]) / previous_rms
        source_y = (y - previous_center[1]) / previous_rms
        predicted_x = scale * (cosine * source_x - sine * source_y)
        predicted_y = scale * (sine * source_x + cosine * source_y)
        residual_x = target_x - predicted_x
        residual_y = target_y - predicted_y
        local_x = cosine * residual_x + sine * residual_y
        local_y = -sine * residual_x + cosine * residual_y
        values.extend((local_x, local_y))
    return scale, angle, tuple(values)


@dataclass(frozen=True)
class TemporalSetFlow:
    """Ordered, bounded non-rigid residuals for adjacent unordered sets."""

    adjacent_residuals: tuple[tuple[float, ...], ...]

    def __post_init__(self) -> None:
        if not MIN_FRAMES - 1 <= len(self.adjacent_residuals) <= MAX_FRAMES - 1:
            raise ValueError("descriptor has an invalid adjacent-step count")
        if any(
            len(step) < 5 or (len(step) - 2) % 3 != 0
            for step in self.adjacent_residuals
        ):
            raise ValueError("descriptor has a malformed adjacent step")
        if any(
            not math.isfinite(value) or abs(value) > MAX_RESIDUAL_RATIO
            for step in self.adjacent_residuals
            for value in step
        ):
            raise ValueError("descriptor values must be finite and bounded")
        canonical_steps = tuple(
            tuple(_canonical(value) for value in step)
            for step in self.adjacent_residuals
        )
        object.__setattr__(self, "adjacent_residuals", canonical_steps)

    def feature_vector(self) -> tuple[float, ...]:
        return tuple(value for step in self.adjacent_residuals for value in step)

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema": "TEMPORAL-SET-FLOW-RESEARCH",
            "adjacent_residuals": [
                {"interval": index, "values": list(step)}
                for index, step in enumerate(self.adjacent_residuals)
            ],
        }


def _step_descriptor(
    previous: Sequence[Point], current: Sequence[Point]
) -> tuple[float, ...] | None:
    try:
        _, _, residual = _procrustes(previous, current)
    except (ArithmeticError, IndexError, TypeError, ValueError):
        return None
    if not residual or not all(math.isfinite(value) for value in residual):
        return None

    previous_center, previous_rms = _centroid_and_rms(previous)
    local: list[tuple[float, float, float]] = []
    for index in range(0, len(residual), 2):
        x, y = previous[index // 2]
        source_x = (x - previous_center[0]) / previous_rms
        source_y = (y - previous_center[1]) / previous_rms
        residual_x = residual[index]
        residual_y = residual[index + 1]
        magnitude = math.hypot(residual_x, residual_y)
        tangent = source_x * residual_y - source_y * residual_x
        local.append((magnitude, source_x * residual_x + source_y * residual_y, tangent))
    magnitudes = [record[0] for record in local]
    rms = math.sqrt(math.fsum(value * value for value in magnitudes) / len(magnitudes))
    maximum = max(magnitudes)
    if not all(math.isfinite(value) for value in (rms, maximum)):
        return None
    if maximum > MAX_RESIDUAL_RATIO:
        return None
    if rms <= _DUPLICATE_TOLERANCE and maximum <= _DUPLICATE_TOLERANCE:
        return None
    ordered = tuple(sorted(local))
    return (_canonical(rms), _canonical(maximum), *(_canonical(value) for record in ordered for value in record))


def describe(observation: Any) -> TemporalSetFlow | None:
    """Describe an observation, returning ``None`` for every bounded-input failure.

    Matching is recomputed for every adjacent frame pair.  No assignment is
    returned or retained, and no observation metadata beyond frame time and x/y
    point sets is inspected.
    """
    frames = _extract_frames(observation)
    if frames is None:
        return None
    steps: list[tuple[float, ...]] = []
    for (_, previous), (_, current) in zip(frames, frames[1:]):
        if len(previous) != len(current):
            return None
        step = _step_descriptor(previous, current)
        if step is None:
            return None
        steps.append(step)
    try:
        return TemporalSetFlow(tuple(steps))
    except (TypeError, ValueError):
        return None


def estimate_rigid_motion(observation: Any) -> tuple[tuple[float, float, float], ...] | None:
    """Return best-fit centroid/scale/rotation summaries for a rigid control."""
    frames = _extract_frames(observation)
    if frames is None:
        return None
    result: list[tuple[float, float, float]] = []
    for (_, previous), (_, current) in zip(frames, frames[1:]):
        if len(previous) != len(current):
            return None
        try:
            _, angle, _ = _procrustes(previous, current)
        except (ArithmeticError, IndexError, TypeError, ValueError):
            return None
        old_center, old_rms = _centroid_and_rms(previous)
        new_center, new_rms = _centroid_and_rms(current)
        reference = max(old_rms, new_rms, _DEGENERATE_TOLERANCE)
        displacement = math.hypot(
            new_center[0] - old_center[0], new_center[1] - old_center[1]
        ) / reference
        values = (displacement, math.log(new_rms / old_rms), angle / math.pi)
        if not all(math.isfinite(value) for value in values):
            return None
        result.append(tuple(_canonical(value) for value in values))
    return tuple(result)


__all__ = [
    "MAX_FRAMES",
    "MAX_FRAME_GAP_MS",
    "MAX_POINTS",
    "MAX_RESIDUAL_RATIO",
    "MIN_FRAMES",
    "MIN_FRAME_GAP_MS",
    "MIN_POINTS",
    "TemporalSetFlow",
    "describe",
    "estimate_rigid_motion",
]
