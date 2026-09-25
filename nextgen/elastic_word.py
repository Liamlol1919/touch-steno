"""Bounded, deterministic elastic matching for synthetic word trajectories.

The prototype consumes ordered two-dimensional points.  It removes translation
and uniform scale, resamples by cumulative arc length, and compares the result
to a normalized template.  A match is returned only when its bounded distance
is at or below the caller's explicit threshold; otherwise the result abstains.

This module has no input/output, device, or text-production side effects.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from numbers import Real
from typing import Iterable


Point = tuple[float, float]
Trajectory = tuple[Point, ...]

MIN_TRAJECTORY_POINTS = 2
MAX_TRAJECTORY_POINTS = 4096
MIN_RESAMPLE_POINTS = 2
MAX_RESAMPLE_POINTS = 1024
DEFAULT_SAMPLE_COUNT = 32
DEFAULT_ABSTENTION_DISTANCE = 0.25


@dataclass(frozen=True, slots=True)
class TemplateScore:
    """A bounded template comparison with an explicit accept/abstain result.

    ``distance`` and ``score`` are both in ``[0, 1]``.  ``accepted`` is true
    only when ``distance <= threshold``.  Consequently, callers that do not
    want a forced word event can require ``accepted`` before using the score.
    """

    distance: float
    score: float
    threshold: float
    accepted: bool

    @property
    def abstained(self) -> bool:
        """Whether the distance failed the abstention threshold."""

        return not self.accepted


def validate_trajectory(
    trajectory: Iterable[tuple[Real, Real]],
    *,
    min_points: int = MIN_TRAJECTORY_POINTS,
    max_points: int = MAX_TRAJECTORY_POINTS,
) -> Trajectory:
    """Return an immutable copy of a valid two-dimensional trajectory.

    Points must contain exactly two finite, non-boolean real coordinates.  The
    point-count limits bound normalization and scoring work.  Coordinate limits
    are intentionally not imposed: translation and scale are handled later.
    """

    _validate_count("min_points", min_points, minimum=1)
    _validate_count("max_points", max_points, minimum=min_points)

    if isinstance(trajectory, (str, bytes, bytearray)):
        raise TypeError("trajectory must be an iterable of 2-D points")
    try:
        source = iter(trajectory)
    except TypeError as exc:
        raise TypeError("trajectory must be an iterable of 2-D points") from exc

    validated: list[Point] = []
    for index, point in enumerate(source):
        if index >= max_points:
            raise ValueError(f"trajectory must not exceed {max_points} points")
        if isinstance(point, (str, bytes, bytearray)):
            raise TypeError(f"point {index} must contain exactly two real coordinates")
        try:
            coordinates = iter(point)
            x = next(coordinates)
            y = next(coordinates)
        except StopIteration as exc:
            raise ValueError(
                f"point {index} must contain exactly two coordinates"
            ) from exc
        except TypeError as exc:
            raise TypeError(
                f"point {index} must contain exactly two real coordinates"
            ) from exc
        try:
            next(coordinates)
        except StopIteration:
            pass
        except TypeError as exc:
            raise TypeError(
                f"point {index} must contain exactly two real coordinates"
            ) from exc
        else:
            raise ValueError(f"point {index} must contain exactly two coordinates")

        if (
            isinstance(x, bool)
            or isinstance(y, bool)
            or not isinstance(x, Real)
            or not isinstance(y, Real)
        ):
            raise TypeError(f"point {index} must contain two real coordinates")
        try:
            fx, fy = float(x), float(y)
        except (OverflowError, ValueError) as exc:
            raise ValueError(f"point {index} coordinates must be finite") from exc
        if not math.isfinite(fx) or not math.isfinite(fy):
            raise ValueError(f"point {index} coordinates must be finite")
        validated.append((fx, fy))

    if len(validated) < min_points:
        raise ValueError(f"trajectory must contain at least {min_points} points")

    if all(validated[index] == validated[index - 1] for index in range(1, len(validated))):
        raise ValueError("trajectory must have positive total arc length")

    return tuple(validated)


def resample_trajectory(
    trajectory: Iterable[tuple[Real, Real]],
    sample_count: int = DEFAULT_SAMPLE_COUNT,
) -> Trajectory:
    """Resample a validated trajectory at equal cumulative-arc-length positions."""

    points = validate_trajectory(trajectory)
    _validate_count(
        "sample_count", sample_count, minimum=MIN_RESAMPLE_POINTS
    )
    if sample_count > MAX_RESAMPLE_POINTS:
        raise ValueError(
            f"sample_count must not exceed {MAX_RESAMPLE_POINTS}"
        )
    cumulative = [0.0]
    for index in range(1, len(points)):
        dx = points[index][0] - points[index - 1][0]
        dy = points[index][1] - points[index - 1][1]
        cumulative.append(cumulative[-1] + math.hypot(dx, dy))

    total_length = cumulative[-1]
    if not math.isfinite(total_length):
        raise ValueError("trajectory coordinate range is too large")
    last_source = len(points) - 2
    source_index = 0
    result: list[Point] = []
    denominator = sample_count - 1

    for sample_index in range(sample_count):
        distance = total_length * sample_index / denominator
        while (
            source_index < last_source
            and distance > cumulative[source_index + 1]
        ):
            source_index += 1

        start = points[source_index]
        end = points[source_index + 1]
        segment_length = cumulative[source_index + 1] - cumulative[source_index]
        fraction = (distance - cumulative[source_index]) / segment_length
        result.append(
            (
                start[0] + (end[0] - start[0]) * fraction,
                start[1] + (end[1] - start[1]) * fraction,
            )
        )

    return tuple(result)


def normalize_trajectory(
    trajectory: Iterable[tuple[Real, Real]],
    sample_count: int = DEFAULT_SAMPLE_COUNT,
) -> Trajectory:
    """Resample a trajectory and normalize translation and uniform scale.

    The coordinate midpoint is translated to the origin, then the larger
    bounding-box span scales the trajectory into ``[-0.5, 0.5]`` on both axes.
    The smaller span is only stretched proportionally, preserving shape.
    """

    points = resample_trajectory(trajectory, sample_count)
    min_x = min(point[0] for point in points)
    max_x = max(point[0] for point in points)
    min_y = min(point[1] for point in points)
    max_y = max(point[1] for point in points)
    scale = max(max_x - min_x, max_y - min_y)
    center_x = min_x + (max_x - min_x) * 0.5
    center_y = min_y + (max_y - min_y) * 0.5

    # Validation above guarantees a positive span and finite arithmetic.
    return tuple(
        ((point[0] - center_x) / scale, (point[1] - center_y) / scale)
        for point in points
    )


def bounded_distance(
    left: Iterable[tuple[Real, Real]],
    right: Iterable[tuple[Real, Real]],
) -> float:
    """Return normalized pointwise RMS distance in ``[0, 1]``.

    Each input is independently translation/scale normalized and resampled.
    The raw RMS distance is divided by the maximum possible diagonal length,
    ``sqrt(2)``, so a direct ``[0, 1]`` threshold remains meaningful.
    """

    return _normalized_rms_distance(
        normalize_trajectory(left), normalize_trajectory(right)
    )


def score_template(
    candidate: Iterable[tuple[Real, Real]],
    template: Iterable[tuple[Real, Real]],
    *,
    sample_count: int = DEFAULT_SAMPLE_COUNT,
    threshold: float = DEFAULT_ABSTENTION_DISTANCE,
) -> TemplateScore:
    """Score a candidate and abstain unless distance meets ``threshold``.

    ``threshold`` is an explicit maximum normalized RMS distance in ``[0, 1]``.
    The similarity score is ``1 - distance``.  Equality is accepted; callers
    wanting a strict threshold can reject equality in their own policy.
    """

    if (
        isinstance(threshold, bool)
        or not isinstance(threshold, Real)
        or not math.isfinite(float(threshold))
        or not 0.0 <= float(threshold) <= 1.0
    ):
        raise ValueError("threshold must be a finite real number in [0, 1]")
    first = normalize_trajectory(candidate, sample_count)
    second = normalize_trajectory(template, sample_count)
    distance = _normalized_rms_distance(first, second)
    return TemplateScore(
        distance=distance,
        score=1.0 - distance,
        threshold=float(threshold),
        accepted=distance <= float(threshold),
    )


def _normalized_rms_distance(first: Trajectory, second: Trajectory) -> float:
    if first == second:
        return 0.0
    squared_error = math.fsum(
        (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2
        for a, b in zip(first, second)
    )
    distance = math.sqrt(squared_error / len(first) / 2.0)
    if distance <= 8.0 * math.ulp(1.0):
        return 0.0
    return min(1.0, distance)


def _validate_count(name: str, value: int, *, minimum: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer")
    if value < minimum:
        raise ValueError(f"{name} must be at least {minimum}")
