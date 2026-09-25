"""Ten-contact English steno transport and Plover-boundary codec.

This module is intentionally independent from the legacy experimental
scripts. A physical word is a ten-bit contact mask. The hardcoded affine
[10, 5, 4] code has minimum Hamming distance four: it corrects one arbitrary
substituted contact bit and rejects the proven radius-two neighborhood. It does
not claim two-error correction.

Each of the 32 codewords is assigned a canonical English steno stroke. The
stroke key labels use the English stenotype system inspected in the pinned
Plover source. An outline is an ordered sequence of strokes. Plover consumes
the emitted key events; this module does not bundle or modify a dictionary.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

FINGER_NAMES = (
    "LT", "LI", "LM", "LR", "LL",
    "RT", "RI", "RM", "RR", "RL",
)

# Plover's English stenotype system. The source uses side-specific labels for
# left-bank, thumb, and right-bank keys; a custom machine adapter must preserve
# these labels rather than collapsing duplicate letters.
STENO_KEYS = frozenset({
    "#", "S-", "T-", "K-", "P-", "W-", "H-", "R-", "A-", "O-", "*",
    "-E", "-U", "-F", "-R", "-P", "-B", "-L", "-G", "-T", "-S", "-D", "-Z",
})


@dataclass(frozen=True)
class Stroke:
    """One canonical English steno stroke and its side-specific Plover keys."""

    notation: str
    keys: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.notation or not self.keys:
            raise ValueError("stroke notation and keys are required")
        if len(set(self.keys)) != len(self.keys):
            raise ValueError("stroke keys must be unique")
        unknown = set(self.keys) - STENO_KEYS
        if unknown:
            raise ValueError(f"unknown Plover steno keys: {sorted(unknown)}")


# A bounded custom transport profile. Every entry is a valid canonical English
# steno stroke. The profile is deliberately small and versioned; a production
# Plover system can replace it with a larger custom key layout without changing
# the transport or transaction interfaces.
STROKE_LIBRARY: tuple[Stroke, ...] = (
    Stroke("A", ("A-",)),
    Stroke("E", ("-E",)),
    Stroke("U", ("-U",)),
    Stroke("AE", ("A-", "-E")),
    Stroke("AU", ("A-", "-U")),
    Stroke("EU", ("-E", "-U")),
    Stroke("H", ("H-",)),
    Stroke("R", ("R-",)),
    Stroke("L", ("-L",)),
    Stroke("D", ("-D",)),
    Stroke("T", ("-T",)),
    Stroke("S", ("-S",)),
    Stroke("Z", ("-Z",)),
    Stroke("P", ("P-",)),
    Stroke("F", ("-F",)),
    Stroke("B", ("-B",)),
    Stroke("G", ("-G",)),
    Stroke("K", ("K-",)),
    Stroke("W", ("W-",)),
    Stroke("O", ("O-",)),
    Stroke("ST", ("S-", "T-")),
    Stroke("PH", ("P-", "H-")),
    Stroke("TH", ("T-", "H-")),
    Stroke("KW", ("K-", "W-")),
    Stroke("KWR", ("K-", "W-", "-R")),
    Stroke("TPR", ("T-", "P-", "-R")),
    Stroke("SPR", ("S-", "P-", "-R")),
    Stroke("TPL", ("T-", "P-", "-L")),
    Stroke("STPH", ("S-", "T-", "P-", "H-")),
    Stroke("ST-PLT", ("S-", "T-", "-P", "-L", "-T")),
    Stroke("*", ("*",)),
    Stroke("#", ("#",)),
)

if len(STROKE_LIBRARY) != 32:
    raise RuntimeError("English steno profile must contain exactly 32 strokes")
if len({s.notation for s in STROKE_LIBRARY}) != 32:
    raise RuntimeError("English steno profile contains duplicate notation")

# The ten columns are a rank-5 binary generator with d_min=4. The affine
# offset removes the zero physical word from the profile. The column-to-finger
# permutation is a fixed design seed, not a measured ergonomic optimum.
CODE_COLUMNS: tuple[int, ...] = (21, 26, 9, 8, 11, 6, 22, 14, 31, 4)
CODE_OFFSET = 84
COLUMN_TO_FINGER: tuple[int, ...] = (7, 3, 6, 8, 2, 4, 5, 9, 1, 0)


def _parity(value: int) -> int:
    return value.bit_count() & 1


def _build_message_masks() -> tuple[int, ...]:
    masks: list[int] = []
    for message in range(32):
        raw = 0
        for column_index, column in enumerate(CODE_COLUMNS):
            if _parity(message & column):
                raw |= 1 << column_index
        raw ^= CODE_OFFSET
        physical = 0
        for column_index, finger_index in enumerate(COLUMN_TO_FINGER):
            if raw & (1 << column_index):
                physical |= 1 << finger_index
        if physical == 0:
            raise RuntimeError("affine profile must not contain the zero word")
        masks.append(physical)
    return tuple(masks)


MESSAGE_MASKS: tuple[int, ...] = _build_message_masks()


def hamming(left: int, right: int) -> int:
    """Return the number of differing ten-bit contact positions."""
    return (left ^ right).bit_count()


def minimum_distance() -> int:
    """Return the exact codebook minimum distance."""
    return min(
        hamming(left, right)
        for index, left in enumerate(MESSAGE_MASKS)
        for right in MESSAGE_MASKS[index + 1:]
    )


@dataclass(frozen=True)
class DecodeResult:
    """Result of decoding one observed contact mask."""

    status: str
    message_id: int | None
    stroke: Stroke | None
    distance: int
    corrected: bool
    observed_mask: int
    expected_mask: int | None = None

    @property
    def ok(self) -> bool:
        return self.status == "OK"


class StenoCodec:
    """Encode/decode English steno outlines over a ten-contact codebook."""

    def __init__(self) -> None:
        if minimum_distance() != 4:
            raise RuntimeError("the English transport code must have d_min=4")
        if len(set(MESSAGE_MASKS)) != 32 or 0 in MESSAGE_MASKS:
            raise RuntimeError("the English transport profile is not 32 nonzero words")
        self._by_notation = {stroke.notation: index for index, stroke in enumerate(STROKE_LIBRARY)}
        self._by_message = {mask: index for index, mask in enumerate(MESSAGE_MASKS)}

    def minimum_distance(self) -> int:
        return minimum_distance()

    @property
    def codebook(self) -> tuple[tuple[int, Stroke], ...]:
        return tuple(zip(MESSAGE_MASKS, STROKE_LIBRARY))

    def encode_stroke(self, notation: str) -> int:
        """Return the ten-bit physical mask for one exact profile notation."""
        try:
            message = self._by_notation[notation]
        except KeyError as exc:
            raise ValueError(f"stroke not in English steno profile: {notation}") from exc
        return MESSAGE_MASKS[message]

    def decode_mask(self, observed_mask: int) -> DecodeResult:
        """Correct at most one contact substitution; NACK ties and distance > 1."""
        if not isinstance(observed_mask, int) or isinstance(observed_mask, bool):
            raise TypeError("observed_mask must be an integer")
        if not 0 <= observed_mask <= 0x3FF:
            return DecodeResult("NACK", None, None, 3, False, observed_mask)
        distances = [(hamming(observed_mask, expected), index)
                     for index, expected in enumerate(MESSAGE_MASKS)]
        best_distance = min(distance for distance, _ in distances)
        winners = [index for distance, index in distances if distance == best_distance]
        if len(winners) != 1 or best_distance > 1:
            return DecodeResult("NACK", None, None, best_distance, False, observed_mask)
        message = winners[0]
        return DecodeResult(
            status="OK",
            message_id=message,
            stroke=STROKE_LIBRARY[message],
            distance=best_distance,
            corrected=best_distance == 1,
            observed_mask=observed_mask,
            expected_mask=MESSAGE_MASKS[message],
        )

    def encode_outline(self, outline: str) -> tuple[int, ...]:
        """Encode slash-separated canonical stroke notation."""
        if not isinstance(outline, str) or not outline.strip():
            raise ValueError("outline must contain at least one stroke")
        parts = outline.strip().split("/")
        if any(not part for part in parts):
            raise ValueError("outline contains an empty stroke")
        return tuple(self.encode_stroke(part) for part in parts)

    def decode_outline(self, masks: Iterable[int]) -> tuple[DecodeResult, ...]:
        """Decode an ordered physical outline without guessing on NACK."""
        return tuple(self.decode_mask(mask) for mask in masks)

    def plover_json(self, outline: str) -> dict:
        """Return a versioned Plover-compatible stroke/outline event payload."""
        results = self.decode_outline(self.encode_outline(outline))
        if not all(result.ok for result in results):
            raise ValueError("cannot emit Plover events from an invalid outline")
        return {
            "v": 1,
            "type": "outline",
            "strokes": [
                {
                    "v": 1,
                    "type": "stroke",
                    "keys": list(result.stroke.keys),
                    "notation": result.stroke.notation,
                }
                for result in results
            ],
        }
