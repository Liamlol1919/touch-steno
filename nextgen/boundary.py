"""Versioned, process-local boundary for decoded English steno events.

Serialised events contain exactly the seven contract fields. They never contain raw
contacts, coordinates, tracking identifiers, or timestamps beyond the caller-supplied
``event_id``. A NACK is an explicit event, not a stroke.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import TypeAlias

from .english_steno import Stroke

CONTRACT_VERSION = "en-steno-key/1"
SOURCE = "touch-steno"
_ALLOWED_SIDES = ("left", "right", "bilateral")

StrokeValue: TypeAlias = Stroke | tuple[str, ...]


@dataclass(frozen=True)
class KeyEvent:
    """The complete, versioned event shape exposed by the source boundary."""

    contract_version: str
    event_id: str
    sequence: int
    side: str
    stroke: tuple[str, ...]
    state: str
    source: str

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-compatible mapping with exactly the seven contract fields."""
        return asdict(self)


@dataclass(frozen=True)
class ConsumerResult:
    """Outcome of consuming one event; it deliberately has no text field."""

    ok: bool
    reason: str | None = None


class BoundaryEmitter:
    """Emit canonical key and NACK events for one process.

    A ``bilateral`` side is valid only when the canonical keys contain both a
    side-specific left key and a side-specific right key. Thumb keys are neutral and
    do not establish a bilateral relationship. A declared left or right stroke also
    may not contain keys from the opposite side.
    """

    def __init__(self) -> None:
        self.last_sequence = 0

    def emit_key(
        self,
        stroke: StrokeValue,
        side: str,
        event_id: str | None = None,
    ) -> KeyEvent:
        """Emit one decoded key event as a canonical key tuple."""
        if side not in _ALLOWED_SIDES:
            allowed = ", ".join(repr(value) for value in _ALLOWED_SIDES)
            raise ValueError(f"side must be one of {allowed}; got {side!r}")

        keys = self._canonical_keys(stroke)
        left = any(key.endswith("-") for key in keys)
        right = any(key.startswith("-") for key in keys)
        if side == "bilateral" and not (left and right):
            raise ValueError("bilateral side requires both left and right stroke keys")
        if side == "left" and right:
            raise ValueError("left side cannot contain right-side stroke keys")
        if side == "right" and left:
            raise ValueError("right side cannot contain left-side stroke keys")

        return self._event(
            side=side,
            stroke=keys,
            state="key",
            event_id=event_id,
        )

    def emit_nack(
        self,
        event_id: str | None = None,
        reason: str | None = None,
    ) -> KeyEvent:
        """Emit a NACK without stroke content.

        ``reason`` is source-side diagnostic context only; the exact contract has no
        reason field, so it is intentionally not included in the event.
        """
        del reason
        return self._event(
            side="bilateral",
            stroke=(),
            state="nack",
            event_id=event_id,
        )

    def _event(
        self,
        *,
        side: str,
        stroke: tuple[str, ...],
        state: str,
        event_id: str | None,
    ) -> KeyEvent:
        self.last_sequence += 1
        return KeyEvent(
            contract_version=CONTRACT_VERSION,
            event_id=event_id if event_id is not None else str(self.last_sequence),
            sequence=self.last_sequence,
            side=side,
            stroke=stroke,
            state=state,
            source=SOURCE,
        )

    @staticmethod
    def _canonical_keys(stroke: StrokeValue) -> tuple[str, ...]:
        if isinstance(stroke, Stroke):
            return stroke.keys
        if not isinstance(stroke, tuple):
            raise TypeError("stroke must be an EnglishSteno Stroke or a canonical key tuple")
        # Stroke performs the existing public transport validation, including membership
        # in STENO_KEYS, without reaching into any private transport attributes.
        Stroke("".join(key.strip("-") for key in stroke), stroke)
        return stroke


def accept_event(event: KeyEvent) -> ConsumerResult:
    """Accept a known-version key event and reject incompatible or NACK events.

    This function never returns or synthesises text for a NACK: its result type has no
    text field, and NACK handling always produces ``ok=False``.
    """
    if event.contract_version != CONTRACT_VERSION:
        return ConsumerResult(False, f"unknown contract version: {event.contract_version!r}")
    if event.state == "nack":
        return ConsumerResult(False, "NACK event; text synthesis is forbidden")
    if event.state != "key":
        return ConsumerResult(False, f"unknown event state: {event.state!r}")
    if event.side not in _ALLOWED_SIDES:
        return ConsumerResult(False, f"invalid side: {event.side!r}")
    if not event.stroke:
        return ConsumerResult(False, "key event has no stroke")
    return ConsumerResult(True)
