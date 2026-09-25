"""Authoritative process-local English steno V1 boundary.

The wire schema is defined by ``INTEGRATION_CONTRACT_V1.md``.  A consumer must
refuse a NACK as a translation request and must never synthesise text for one;
silence is a valid outcome.  This module does not accept ``plover_json()`` output.
It emits the side-specific keys of one committed profile stroke per event and
omits notation, masks, and outline data.
"""

from __future__ import annotations

import json
import re
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import TypeAlias
from uuid import uuid4

from .english_steno import STROKE_LIBRARY, Stroke

CONTRACT_VERSION = "touchsteno.english-steno-key-event.v1"
SOURCE = "touch-steno"
PROFILE_ID = "nextgen.english-steno.simplex10.v1"

# The proposal's all-zero example is explicitly not a deployable fingerprint.
# Keep the unfinished gate visible rather than presenting documentation syntax
# as a registered profile.  Callers must supply the frozen digest explicitly.
LAYOUT_FINGERPRINT: str | None = None

MESSAGE_TYPES = frozenset({"hello", "event"})
EVENT_KINDS = frozenset({"key", "nack", "reset"})
NACK_REASONS = frozenset(
    {
        "distance_gt_1",
        "nearest_tie",
        "all_zero",
        "invalid_observation",
        "ambiguous_attribution",
    }
)
RESET_REASONS = frozenset({"contact_id_change", "interrupted", "cancelled"})

HELLO_FIELDS = frozenset(
    {
        "contract_version",
        "message_type",
        "source",
        "stream_epoch",
        "profile_id",
        "layout_fingerprint",
    }
)
EVENT_FIELDS = frozenset(
    {
        "contract_version",
        "message_type",
        "source",
        "stream_epoch",
        "event_id",
        "sequence",
        "kind",
        "payload",
    }
)
KEY_PAYLOAD_FIELDS = frozenset({"keys", "distance", "corrected"})
NACK_PAYLOAD_FIELDS = frozenset({"reason"})
RESET_PAYLOAD_FIELDS = frozenset({"reason"})

_PROFILE_TUPLES = frozenset(stroke.keys for stroke in STROKE_LIBRARY)
_FINGERPRINT_PATTERN = re.compile(r"[0-9a-f]{64}")
_MAX_OPAQUE_LENGTH = 256
_MAX_RECORD_BYTES = 4096

StrokeValue: TypeAlias = Stroke | tuple[str, ...]


class ContractError(ValueError):
    """A record violates the closed V1 schema or handshake rules."""


def _closed_object(value: object, fields: frozenset[str], label: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ContractError(f"{label} must be a JSON object")
    actual = frozenset(value)
    if actual != fields:
        missing = sorted(fields - actual)
        unknown = sorted(actual - fields)
        raise ContractError(f"{label} fields mismatch; missing={missing}, unknown={unknown}")
    return value


def _opaque_string(value: object, label: str) -> str:
    if not isinstance(value, str) or not value or len(value) > _MAX_OPAQUE_LENGTH:
        raise ContractError(f"{label} must be a bounded non-empty string")
    return value


def _fingerprint(value: object) -> str:
    if not isinstance(value, str) or _FINGERPRINT_PATTERN.fullmatch(value) is None:
        raise ContractError("layout_fingerprint must be 64 lowercase hexadecimal characters")
    if value == "0" * 64:
        raise ContractError("the proposal's all-zero layout fingerprint is not deployable")
    return value


def _profile_pair(profile_id: object, layout_fingerprint: object) -> tuple[str, str]:
    if profile_id != PROFILE_ID:
        raise ContractError(f"unknown profile_id: {profile_id!r}")
    return PROFILE_ID, _fingerprint(layout_fingerprint)


@dataclass(frozen=True)
class KeyPayload:
    """The exact Section 2.3 key payload."""

    keys: tuple[str, ...]
    distance: int
    corrected: bool

    def to_dict(self) -> dict[str, object]:
        return {"keys": list(self.keys), "distance": self.distance, "corrected": self.corrected}

    @classmethod
    def from_dict(cls, value: object) -> KeyPayload:
        data = _closed_object(value, KEY_PAYLOAD_FIELDS, "key payload")
        keys = data["keys"]
        if not isinstance(keys, (list, tuple)) or not keys or any(
            not isinstance(key, str) for key in keys
        ):
            raise ContractError("key payload keys must be a non-empty string array")
        if type(data["distance"]) is not int or data["distance"] not in (0, 1):
            raise ContractError("key payload distance must be integer 0 or 1")
        if type(data["corrected"]) is not bool:
            raise ContractError("key payload corrected must be boolean")
        if data["corrected"] != (data["distance"] == 1):
            raise ContractError("corrected must be true exactly when distance is 1")
        return cls(tuple(keys), data["distance"], data["corrected"])


@dataclass(frozen=True)
class NackPayload:
    """The exact Section 2.4 NACK payload; it carries no best guess."""

    reason: str

    def to_dict(self) -> dict[str, object]:
        return {"reason": self.reason}

    @classmethod
    def from_dict(cls, value: object) -> NackPayload:
        data = _closed_object(value, NACK_PAYLOAD_FIELDS, "NACK payload")
        if data["reason"] not in NACK_REASONS:
            raise ContractError(f"unknown NACK reason: {data['reason']!r}")
        return cls(data["reason"])


@dataclass(frozen=True)
class ResetPayload:
    """The exact Section 2.5 RESET payload."""

    reason: str

    def to_dict(self) -> dict[str, object]:
        return {"reason": self.reason}

    @classmethod
    def from_dict(cls, value: object) -> ResetPayload:
        data = _closed_object(value, RESET_PAYLOAD_FIELDS, "RESET payload")
        if data["reason"] not in RESET_REASONS:
            raise ContractError(f"unknown RESET reason: {data['reason']!r}")
        return cls(data["reason"])


Payload: TypeAlias = KeyPayload | NackPayload | ResetPayload


@dataclass(frozen=True)
class Hello:
    """The complete Section 2.1 connection handshake."""

    contract_version: str
    message_type: str
    source: str
    stream_epoch: str
    profile_id: str
    layout_fingerprint: str

    def to_dict(self) -> dict[str, object]:
        return {
            "contract_version": self.contract_version,
            "message_type": self.message_type,
            "source": self.source,
            "stream_epoch": self.stream_epoch,
            "profile_id": self.profile_id,
            "layout_fingerprint": self.layout_fingerprint,
        }

    @classmethod
    def from_dict(cls, value: object) -> Hello:
        data = _closed_object(value, HELLO_FIELDS, "hello")
        if data["contract_version"] != CONTRACT_VERSION:
            raise ContractError(f"unknown contract version: {data['contract_version']!r}")
        if data["message_type"] != "hello":
            raise ContractError("message_type must be 'hello'")
        if data["source"] != SOURCE:
            raise ContractError(f"unknown source: {data['source']!r}")
        stream_epoch = _opaque_string(data["stream_epoch"], "stream_epoch")
        profile_id, layout_fingerprint = _profile_pair(
            data["profile_id"], data["layout_fingerprint"]
        )
        return cls(
            CONTRACT_VERSION,
            "hello",
            SOURCE,
            stream_epoch,
            profile_id,
            layout_fingerprint,
        )


@dataclass(frozen=True)
class ContractEvent:
    """The common Section 2.2 envelope for key, NACK, and RESET records."""

    contract_version: str
    message_type: str
    source: str
    stream_epoch: str
    event_id: str
    sequence: int
    kind: str
    payload: Payload

    def to_dict(self) -> dict[str, object]:
        return {
            "contract_version": self.contract_version,
            "message_type": self.message_type,
            "source": self.source,
            "stream_epoch": self.stream_epoch,
            "event_id": self.event_id,
            "sequence": self.sequence,
            "kind": self.kind,
            "payload": self.payload.to_dict(),
        }

    @classmethod
    def from_dict(cls, value: object) -> ContractEvent:
        data = _closed_object(value, EVENT_FIELDS, "event")
        if data["contract_version"] != CONTRACT_VERSION:
            raise ContractError(f"unknown contract version: {data['contract_version']!r}")
        if data["message_type"] != "event":
            raise ContractError("message_type must be 'event'")
        if data["source"] != SOURCE:
            raise ContractError(f"unknown source: {data['source']!r}")
        stream_epoch = _opaque_string(data["stream_epoch"], "stream_epoch")
        event_id = _opaque_string(data["event_id"], "event_id")
        if type(data["sequence"]) is not int or data["sequence"] < 1:
            raise ContractError("sequence must be an integer at least 1")
        kind = data["kind"]
        if kind == "key":
            payload: Payload = KeyPayload.from_dict(data["payload"])
        elif kind == "nack":
            payload = NackPayload.from_dict(data["payload"])
        elif kind == "reset":
            payload = ResetPayload.from_dict(data["payload"])
        else:
            raise ContractError(f"unknown event kind: {kind!r}")
        return cls(
            CONTRACT_VERSION,
            "event",
            SOURCE,
            stream_epoch,
            event_id,
            data["sequence"],
            kind,
            payload,
        )


@dataclass(frozen=True)
class ConsumerResult:
    """Validation outcome; deliberately has no text or action field."""

    ok: bool
    reason: str | None = None


def _new_event_id() -> str:
    return uuid4().hex


class BoundaryEmitter:
    """Emit one hello and an ordered live stream for a single producer epoch.

    The caller must provide the actual frozen fingerprint.  The documentation's
    all-zero placeholder and the outline-shaped ``plover_json()`` result are not
    accepted.
    """

    def __init__(
        self,
        stream_epoch: str,
        *,
        profile_id: str,
        layout_fingerprint: str,
        event_id_factory: Callable[[], str] | None = None,
    ) -> None:
        self.stream_epoch = _opaque_string(stream_epoch, "stream_epoch")
        self.profile_id, self.layout_fingerprint = _profile_pair(
            profile_id, layout_fingerprint
        )
        self._event_id_factory = event_id_factory or _new_event_id
        self._used_event_ids: set[str] = set()
        self.last_sequence = 0
        self.hello = Hello(
            CONTRACT_VERSION,
            "hello",
            SOURCE,
            self.stream_epoch,
            self.profile_id,
            self.layout_fingerprint,
        )

    def emit_key(
        self,
        stroke: StrokeValue,
        *,
        distance: int,
        corrected: bool | None = None,
        event_id: str | None = None,
    ) -> ContractEvent:
        """Emit one committed profile stroke, never an outline or mask."""
        keys = self._canonical_keys(stroke)
        if type(distance) is not int or distance not in (0, 1):
            raise ContractError("distance must be integer 0 or 1")
        resolved_corrected = distance == 1 if corrected is None else corrected
        if type(resolved_corrected) is not bool or resolved_corrected != (distance == 1):
            raise ContractError("corrected must be true exactly when distance is 1")
        return self._event(
            "key",
            KeyPayload(keys, distance, resolved_corrected),
            event_id,
        )

    def emit_nack(
        self,
        reason: str,
        *,
        event_id: str | None = None,
    ) -> ContractEvent:
        """Emit a closed-reason NACK with no keys, guess, notation, or masks."""
        if reason not in NACK_REASONS:
            raise ContractError(f"unknown NACK reason: {reason!r}")
        return self._event("nack", NackPayload(reason), event_id)

    def emit_reset(
        self,
        reason: str,
        *,
        event_id: str | None = None,
    ) -> ContractEvent:
        """Emit a closed-reason RESET; it consumes the next sequence value."""
        if reason not in RESET_REASONS:
            raise ContractError(f"unknown RESET reason: {reason!r}")
        return self._event("reset", ResetPayload(reason), event_id)

    @staticmethod
    def _canonical_keys(stroke: StrokeValue) -> tuple[str, ...]:
        keys = stroke.keys if isinstance(stroke, Stroke) else stroke
        if not isinstance(keys, tuple) or keys not in _PROFILE_TUPLES:
            raise ContractError("keys must exactly match one ordered pinned profile tuple")
        return keys

    def _event(
        self,
        kind: str,
        payload: Payload,
        event_id: str | None,
    ) -> ContractEvent:
        candidate = _opaque_string(
            self._event_id_factory() if event_id is None else event_id,
            "event_id",
        )
        if candidate in self._used_event_ids:
            raise ContractError("event_id has already been emitted in this epoch")
        self.last_sequence += 1
        self._used_event_ids.add(candidate)
        return ContractEvent(
            CONTRACT_VERSION,
            "event",
            SOURCE,
            self.stream_epoch,
            candidate,
            self.last_sequence,
            kind,
            payload,
        )


def _event_error(
    event: ContractEvent,
    *,
    stream_epoch: str,
    profile_id: str,
    layout_fingerprint: str,
    expected_sequence: int,
    seen_event_ids: frozenset[str] | set[str],
) -> str | None:
    if event.contract_version != CONTRACT_VERSION:
        return f"unknown contract version: {event.contract_version!r}"
    if event.message_type != "event" or event.source != SOURCE:
        return "event envelope has an unknown message_type or source"
    if event.stream_epoch != stream_epoch:
        return "event epoch differs from the accepted hello"
    if profile_id != PROFILE_ID:
        return f"unknown profile_id: {profile_id!r}"
    try:
        _fingerprint(layout_fingerprint)
    except ContractError as exc:
        return str(exc)
    try:
        _opaque_string(event.event_id, "event_id")
    except ContractError as exc:
        return str(exc)
    if event.event_id in seen_event_ids:
        return "duplicate event_id; a fresh epoch is required"
    if type(event.sequence) is not int or event.sequence != expected_sequence:
        return "sequence is not exactly the previous sequence plus 1"

    if event.kind == "key":
        if not isinstance(event.payload, KeyPayload):
            return "key event payload must be a key payload"
        keys = event.payload.keys
        if not isinstance(keys, tuple) or keys not in _PROFILE_TUPLES:
            return "key payload does not exactly match a pinned profile tuple"
        if type(event.payload.distance) is not int or event.payload.distance not in (0, 1):
            return "key payload distance must be integer 0 or 1"
        if type(event.payload.corrected) is not bool or event.payload.corrected != (
            event.payload.distance == 1
        ):
            return "corrected must be true exactly when distance is 1"
    elif event.kind == "nack":
        if not isinstance(event.payload, NackPayload) or event.payload.reason not in NACK_REASONS:
            return "NACK payload has an unknown reason or shape"
    elif event.kind == "reset":
        if not isinstance(event.payload, ResetPayload) or event.payload.reason not in RESET_REASONS:
            return "RESET payload has an unknown reason or shape"
    else:
        return f"unknown event kind: {event.kind!r}"
    return None


def _normalise_event(event: ContractEvent | Mapping[str, object]) -> ContractEvent:
    return event if isinstance(event, ContractEvent) else ContractEvent.from_dict(event)


def accept_event(
    event: ContractEvent | Mapping[str, object],
    *,
    stream_epoch: str,
    profile_id: str,
    layout_fingerprint: str,
    expected_sequence: int,
    seen_event_ids: frozenset[str] | set[str] = frozenset(),
) -> ConsumerResult:
    """Validate one event and refuse NACK translation without mutating state.

    This stateless helper complements :class:`BoundaryConsumer`, which owns the
    accepted hello and contiguous-sequence state for a live connection.
    """
    try:
        normalised = _normalise_event(event)
        error = _event_error(
            normalised,
            stream_epoch=stream_epoch,
            profile_id=profile_id,
            layout_fingerprint=layout_fingerprint,
            expected_sequence=expected_sequence,
            seen_event_ids=seen_event_ids,
        )
    except (ContractError, TypeError) as exc:
        return ConsumerResult(False, str(exc))
    if error is not None:
        return ConsumerResult(False, error)
    if normalised.kind == "nack":
        return ConsumerResult(False, "NACK refused; text synthesis is forbidden")
    return ConsumerResult(True)


class BoundaryConsumer:
    """One live, process-local connection with strict hello and ordering state."""

    def __init__(
        self,
        stream_epoch: str,
        *,
        profile_id: str,
        layout_fingerprint: str,
    ) -> None:
        self.stream_epoch = _opaque_string(stream_epoch, "stream_epoch")
        self.profile_id, self.layout_fingerprint = _profile_pair(
            profile_id, layout_fingerprint
        )
        self.hello_accepted = False
        self.quarantined = False
        self.last_sequence = 0
        self._seen_event_ids: set[str] = set()
        self._seen_sequences: set[int] = set()

    def accept_hello(self, hello: Hello | Mapping[str, object]) -> ConsumerResult:
        """Accept exactly the first handshake; no event state exists before it."""
        if self.quarantined:
            return ConsumerResult(False, "connection was rejected; a fresh epoch is required")
        if self.hello_accepted:
            self.quarantined = True
            return ConsumerResult(False, "hello may only be accepted once per connection")
        try:
            normalised = hello if isinstance(hello, Hello) else Hello.from_dict(hello)
            if normalised.contract_version != CONTRACT_VERSION:
                raise ContractError(f"unknown contract version: {normalised.contract_version!r}")
            if normalised.message_type != "hello" or normalised.source != SOURCE:
                raise ContractError("hello has an unknown message_type or source")
            if normalised.stream_epoch != self.stream_epoch:
                raise ContractError("hello epoch differs from the authenticated local peer")
            if normalised.profile_id != self.profile_id:
                raise ContractError("hello profile_id does not match the consumer allowlist")
            if normalised.layout_fingerprint != self.layout_fingerprint:
                raise ContractError("hello fingerprint does not match the consumer allowlist")
        except (ContractError, TypeError) as exc:
            self.quarantined = True
            return ConsumerResult(False, str(exc))
        self.hello_accepted = True
        return ConsumerResult(True)

    def consume(self, event: ContractEvent | Mapping[str, object]) -> ConsumerResult:
        """Consume one live record, committing NACK and RESET to ordering."""
        if not self.hello_accepted:
            return ConsumerResult(False, "event before accepted hello")
        if self.quarantined:
            return ConsumerResult(False, "stream is quarantined; a fresh epoch is required")
        try:
            normalised = _normalise_event(event)
        except (ContractError, TypeError) as exc:
            self.quarantined = True
            return ConsumerResult(False, str(exc))
        error = _event_error(
            normalised,
            stream_epoch=self.stream_epoch,
            profile_id=self.profile_id,
            layout_fingerprint=self.layout_fingerprint,
            expected_sequence=self.last_sequence + 1,
            seen_event_ids=self._seen_event_ids,
        )
        if error is not None:
            self.quarantined = True
            return ConsumerResult(False, error)
        if normalised.sequence in self._seen_sequences:
            self.quarantined = True
            return ConsumerResult(False, "duplicate or conflicting sequence")

        self._seen_event_ids.add(normalised.event_id)
        self._seen_sequences.add(normalised.sequence)
        self.last_sequence = normalised.sequence
        if normalised.kind == "nack":
            return ConsumerResult(False, "NACK refused; text synthesis is forbidden")
        return ConsumerResult(True)


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ContractError(f"duplicate JSON key: {key!r}")
        result[key] = value
    return result


def _reject_nonfinite(value: str) -> None:
    raise ContractError(f"non-finite JSON number is forbidden: {value}")


def loads_record(text: str) -> dict[str, object]:
    """Parse one bounded JSON object, rejecting duplicate keys and non-finite numbers."""
    if not isinstance(text, str) or len(text.encode("utf-8")) > _MAX_RECORD_BYTES:
        raise ContractError("serialized record must be bounded text")
    value = json.loads(
        text,
        object_pairs_hook=_unique_object,
        parse_constant=_reject_nonfinite,
    )
    if not isinstance(value, dict):
        raise ContractError("serialized record must be a JSON object")
    return value
