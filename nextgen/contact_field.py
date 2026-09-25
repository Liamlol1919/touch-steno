"""Bounded, identity-free descriptors for variable-size contact fields.

This module is an offline research prototype.  It deliberately makes no claim that
contact geometry carries symbol information and has no device or hardware interface.

Contacts have no stable identity, so all public descriptors operate on point *sets*:
input order is never interpreted as identity.  Translation is removed with the
centroid, uniform scale is removed with RMS radius about that centroid, and the
remaining summaries use only distances (and therefore cannot encode orientation).
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
import math
from typing import Iterable, Sequence

Point = tuple[float, float]


def _points(points: Iterable[Sequence[float]]) -> tuple[Point, ...]:
    """Validate and copy one contact field without assigning contact identities."""
    result: list[Point] = []
    for point in points:
        if len(point) != 2:
            raise ValueError("each contact must contain exactly two coordinates")
        x, y = float(point[0]), float(point[1])
        if not (math.isfinite(x) and math.isfinite(y)):
            raise ValueError("contact coordinates must be finite")
        result.append((x, y))
    if len(result) < 2:
        raise ValueError("a contact field needs at least two contacts")
    return tuple(result)


def translate_normalize(points: Iterable[Sequence[float]]) -> tuple[Point, ...]:
    """Return the field translated so that its contact centroid is the origin."""
    field = _points(points)
    cx = math.fsum(point[0] for point in field) / len(field)
    cy = math.fsum(point[1] for point in field) / len(field)
    return tuple((x - cx, y - cy) for x, y in field)


def scale_normalize(points: Iterable[Sequence[float]]) -> tuple[Point, ...]:
    """Remove one positive, uniform scale using RMS distance from the centroid.

    The returned field has RMS radius one.  Coincident fields have no geometric
    scale and are therefore rejected.
    """
    centered = translate_normalize(points)
    rms = math.sqrt(math.fsum(x * x + y * y for x, y in centered) / len(centered))
    if rms <= 0.0 or not math.isfinite(rms):
        raise ValueError("a contact field must have positive spatial extent")
    return tuple((x / rms, y / rms) for x, y in centered)


def normalize_field(points: Iterable[Sequence[float]]) -> tuple[Point, ...]:
    """Apply translation and scale normalization, in that order."""
    return scale_normalize(points)


def pairwise_distances(points: Iterable[Sequence[float]]) -> tuple[float, ...]:
    """Return every unordered pairwise distance as a sorted multiset."""
    field = normalize_field(points)
    return tuple(sorted(
        math.hypot(field[i][0] - field[j][0], field[i][1] - field[j][1])
        for i, j in combinations(range(len(field)), 2)
    ))


def pairwise_geometry(points: Iterable[Sequence[float]]) -> tuple[tuple[float, float, float], ...]:
    """Return sorted, normalized side lengths for every unordered contact triple.

    Each tuple contains the three distances divided by that triangle's longest
    side.  Both the unordered-triangle representation and distance-only inputs make
    this invariant to contact permutation and planar rotation.
    """
    field = normalize_field(points)
    triangles: list[tuple[float, float, float]] = []
    for i, j, k in combinations(range(len(field)), 3):
        sides = (
            math.hypot(field[i][0] - field[j][0], field[i][1] - field[j][1]),
            math.hypot(field[i][0] - field[k][0], field[i][1] - field[k][1]),
            math.hypot(field[j][0] - field[k][0], field[j][1] - field[k][1]),
        )
        longest = max(sides)
        if longest <= 0.0:  # unreachable for a positive-extent field, but explicit.
            raise ValueError("contact triple has zero extent")
        a, b, c = sorted(side / longest for side in sides)
        triangles.append((a, b, c))
    return tuple(sorted(triangles))


@dataclass(frozen=True)
class ContactFieldDescriptor:
    """Variable-cardinality, bounded geometry of one identity-free contact set.

    Feature tuple lengths depend on ``contact_count``.  This is intentional: the
    descriptor does not pad, truncate, or silently merge contacts with different
    cardinalities.  Every feature is dimensionless and the distance-based fields
    are permutation and rotation invariant.
    """

    contact_count: int
    normalized_radii: tuple[float, ...]
    normalized_pair_distances: tuple[float, ...]
    normalized_triangles: tuple[tuple[float, float, float], ...]

    def feature_vector(self) -> tuple[float, ...]:
        """Return the complete descriptor, including its explicit cardinality."""
        # Encode count logarithmically to keep downstream scalar accumulations bounded.
        return (
            (math.log1p(self.contact_count)),
            *self.normalized_radii,
            *self.normalized_pair_distances,
            *(value for triangle in self.normalized_triangles for value in triangle),
        )

    def __post_init__(self) -> None:
        """Canonicalize floating summaries so nuisance transforms compare exactly."""
        def canonical(value: float) -> float:
            value = round(float(value), 14)
            return 0.0 if value == 0.0 else value

        object.__setattr__(
            self,
            "normalized_radii",
            tuple(canonical(value) for value in self.normalized_radii),
        )
        object.__setattr__(
            self,
            "normalized_pair_distances",
            tuple(canonical(value) for value in self.normalized_pair_distances),
        )
        object.__setattr__(
            self,
            "normalized_triangles",
            tuple(
                tuple(canonical(value) for value in triangle)
                for triangle in self.normalized_triangles
            ),
        )


def describe_field(points: Iterable[Sequence[float]]) -> ContactFieldDescriptor:
    """Build a bounded descriptor for any field containing at least two contacts."""
    field = normalize_field(points)
    radii = tuple(sorted(math.hypot(x, y) for x, y in field))
    return ContactFieldDescriptor(
        contact_count=len(field),
        normalized_radii=radii,
        normalized_pair_distances=_normalized_sorted_distances(field),
        normalized_triangles=pairwise_geometry(field),
    )


def _normalized_sorted_distances(field: Sequence[Point]) -> tuple[float, ...]:
    distances = sorted(
        math.hypot(field[i][0] - field[j][0], field[i][1] - field[j][1])
        for i, j in combinations(range(len(field)), 2)
    )
    reference = max(distances)
    return tuple(distance / reference for distance in distances)


def _directed_hausdorff(first: Sequence[Point], second: Sequence[Point]) -> float:
    return max(
        min(math.hypot(a[0] - b[0], a[1] - b[1]) for b in second)
        for a in first
    )


def field_motion_score(
    previous: Iterable[Sequence[float]],
    current: Iterable[Sequence[float]],
) -> float:
    """Return shape similarity in the closed interval ``[0, 1]``.

    Each field is independently translated and scale-normalized, then compared with
    symmetric directed Hausdorff distance.  Cardinalities may differ: the symmetric
    nearest-neighbour sets make this an insertion/deletion-tolerant set score rather
    than an invalid point-for-point match.  One means identical normalized point sets;
    zero means the normalized clouds are at least one normalized unit apart (or one
    field is empty).  This is a descriptive prototype score, not a calibrated or
    device-performance metric.
    """
    try:
        old = normalize_field(previous)
        new = normalize_field(current)
    except ValueError:
        return 0.0
    distance = (_directed_hausdorff(old, new) + _directed_hausdorff(new, old)) / 2.0
    return max(0.0, min(1.0, 1.0 - distance))


__all__ = [
    "ContactFieldDescriptor",
    "describe_field",
    "field_motion_score",
    "normalize_field",
    "pairwise_distances",
    "pairwise_geometry",
    "scale_normalize",
    "translate_normalize",
]
