"""Closed, offline validation for the English steno process-local contract V1.

This module has no transport, device, Plover, logging, or persistence integration.
It validates bounded JSON messages and implements one consumer's in-memory live
stream state.  Rejected records never advance the stream or accepted-key state.
"""
from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
import json
import re
from typing import Any, Final


CONTRACT_VERSION: Final = "touchsteno.english-steno-key-event.v1"
SOURCE: Final = "touch-steno"
PROFILE_ID: Final = "nextgen.english-steno.simplex10.v1"

# SHA-256 of the UTF-8 newline-joined, comma-separated ordered key tuples below.
# It identifies frozen semantic key layout only, never hardware geometry.
LAYOUT_FINGERPRINT: Final = (
    "d76911b189446a70a067ed53491221242b13598d37a44f699a826f8725306ea2"
)

MESSAGE_TYPES: Final = frozenset({"hello", "event"})
EVENT_KINDS: Final = frozenset({"key", "nack", "reset"})
STENO_KEYS: Final = frozenset({
    "#", "S-", "T-", "K-", "P-", "W-", "H-", "R-", "A-", "O-", "*",
    "-E", "-U", "-F", "-R", "-P", "-B", "-L", "-G", "-T", "-S", "-D", "-Z",
})
NACK_REASONS: Final = frozenset({
    "distance_gt_1", "nearest_tie", "all_zero", "invalid_observation",
    "ambiguous_attribution",
})
RESET_REASONS: Final = frozenset({
    "contact_id_change", "interrupted", "cancelled",
})

# Order is part of the profile contract; a tuple is never treated as a set.
PROFILE_KEY_TUPLES: Final[tuple[tuple[str, ...], ...]] = (
    ("A-",),
    ("-E",),
    ("-U",),
    ("A-", "-E"),
    ("A-", "-U"),
    ("-E", "-U"),
    ("H-",),
    ("R-",),
    ("-L",),
    ("-D",),
    ("-T",),
    ("-S",),
    ("-Z",),
    ("P-",),
    ("-F",),
    ("-B",),
    ("-G",),
    ("K-",),
    ("W-",),
    ("O-",),
    ("S-", "T-"),
    ("P-", "H-"),
    ("T-", "H-"),
    ("K-", "W-"),
    ("K-", "W-", "-R"),
    ("T-", "P-", "-R"),
    ("S-", "P-", "-R"),
    ("T-", "P-", "-L"),
    ("S-", "T-", "P-", "H-"),
    ("S-", "T-", "-P", "-L", "-T"),
    ("*",),
    ("#",),
)
_ALLOWED_PROFILE_TUPLES: Final = frozenset(PROFILE_KEY_TUPLES)

HELLO_FIELDS: Final = frozenset({
    "contract_version", "message_type", "source", "stream_epoch",
    "profile_id", "layout_fingerprint",
})
EVENT_FIELDS: Final = frozenset({
    "contract_version", "message_type", "source", "stream_epoch", "event_id",
    "sequence", "kind", "payload",
})
KEY_PAYLOAD_FIELDS: Final = frozenset({"keys", "distance", "corrected"})
NACK_PAYLOAD_FIELDS: Final = frozenset({"reason"})
RESET_PAYLOAD_FIELDS: Final = frozenset({"reason"})

MAX_JSON_BYTES: Final = 4096
MAX_JSON_DEPTH: Final = 4
MAX_STRING_BYTES: Final = 256
MAX_ARRAY_ITEMS: Final = 32
MAX_OBJECT_FIELDS: Final = 8
MAX_OPAQUE_ID_CHARS: Final = 128
MAX_SEQUENCE: Final = (1 << 63) - 1
MAX_EVENTS_PER_STREAM: Final = 65_536
MAX_RETIRED_EPOCHS: Final = 1_024

_FINGERPRINT_RE: Final = re.compile(r"[0-9a-f]{64}\Z")
_OPAQUE_ID_RE: Final = re.compile(r"[A-Za-z0-9._~-]{16,128}\Z")
_ZERO_FINGERPRINT: Final = "0" * 64


class ContractError(ValueError):
    """A bounded, value-free description of a closed-contract rejection."""


def _reject_constant(_value: str) -> None:
    raise ContractError("non-finite JSON number")


def _reject_float(_value: str) -> None:
    raise ContractError("JSON number has the wrong type")


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ContractError("duplicate JSON object key")
        result[key] = value
    return result


def _parse(raw: str | bytes) -> dict[str, Any]:
    if not isinstance(raw, (str, bytes)):
        raise ContractError("message must be UTF-8 JSON text or bytes")
    if isinstance(raw, bytes):
        if len(raw) > MAX_JSON_BYTES:
            raise ContractError("JSON message is too large")
        try:
            raw = raw.decode("utf-8", "strict")
        except UnicodeDecodeError as exc:
            raise ContractError("message is not valid UTF-8") from exc
    elif len(raw) > MAX_JSON_BYTES:
        raise ContractError("JSON message is too large")
    elif len(raw.encode("utf-8")) > MAX_JSON_BYTES:
        raise ContractError("JSON message is too large")

    try:
        value = json.loads(
            raw,
            object_pairs_hook=_unique_object,
            parse_constant=_reject_constant,
            parse_float=_reject_float,
        )
    except ContractError:
        raise
    except (json.JSONDecodeError, RecursionError) as exc:
        raise ContractError("message is not bounded valid JSON") from exc
    if not isinstance(value, dict):
        raise ContractError("top-level JSON value must be an object")
    return value


def _check_bounded_value(value: Any, depth: int = 1) -> None:
    if depth > MAX_JSON_DEPTH:
        raise ContractError("JSON nesting is too deep")
    if value is None or isinstance(value, bool):
        return
    if isinstance(value, str):
        try:
            size = len(value.encode("utf-8"))
        except UnicodeEncodeError as exc:
            raise ContractError("JSON string is not valid Unicode") from exc
        if size > MAX_STRING_BYTES:
            raise ContractError("JSON string is too long")
        return
    if isinstance(value, int):
        return
    if isinstance(value, list):
        if len(value) > MAX_ARRAY_ITEMS:
            raise ContractError("JSON array is too long")
        for item in value:
            _check_bounded_value(item, depth + 1)
        return
    if isinstance(value, Mapping):
        if len(value) > MAX_OBJECT_FIELDS:
            raise ContractError("JSON object has too many fields")
        for item in value.values():
            _check_bounded_value(item, depth + 1)
        return
    raise ContractError("JSON value has an unsupported type")


def _check_exact_fields(value: Any, expected: frozenset[str]) -> None:
    if not isinstance(value, Mapping) or set(value) != expected:
        raise ContractError("JSON object does not match the closed schema")


def _check_string(value: Any) -> str:
    if not isinstance(value, str):
        raise ContractError("closed schema field has the wrong type")
    return value


def _check_opaque_id(value: Any) -> str:
    value = _check_string(value)
    if not 16 <= len(value) <= MAX_OPAQUE_ID_CHARS or _OPAQUE_ID_RE.fullmatch(value) is None:
        raise ContractError("opaque process-local identifier is invalid")
    return value


def _check_common(value: Mapping[str, Any]) -> None:
    if value.get("contract_version") != CONTRACT_VERSION:
        raise ContractError("contract version is not accepted")
    if value.get("source") != SOURCE:
        raise ContractError("source is not accepted")


def _validate_key_payload(payload: Any, require_profile_tuple: bool) -> None:
    _check_exact_fields(payload, KEY_PAYLOAD_FIELDS)
    keys = payload["keys"]
    if not isinstance(keys, list) or not keys or len(keys) > MAX_ARRAY_ITEMS:
        raise ContractError("key array has the wrong size or type")
    if any(not isinstance(key, str) or key not in STENO_KEYS for key in keys):
        raise ContractError("key array contains a non-canonical key")
    distance = payload["distance"]
    corrected = payload["corrected"]
    if type(distance) is not int or distance not in (0, 1):
        raise ContractError("key distance is not in the closed range")
    if type(corrected) is not bool or corrected != bool(distance):
        raise ContractError("key correction disposition is inconsistent")
    if require_profile_tuple and tuple(keys) not in _ALLOWED_PROFILE_TUPLES:
        raise ContractError("key tuple does not exactly match the profile")


def _validate_nack_payload(payload: Any) -> None:
    _check_exact_fields(payload, NACK_PAYLOAD_FIELDS)
    reason = _check_string(payload["reason"])
    if reason not in NACK_REASONS:
        raise ContractError("NACK reason is not in the closed vocabulary")


def _validate_reset_payload(payload: Any) -> None:
    _check_exact_fields(payload, RESET_PAYLOAD_FIELDS)
    reason = _check_string(payload["reason"])
    if reason not in RESET_REASONS:
        raise ContractError("RESET reason is not in the closed vocabulary")


def _validate_message_object(
    value: Mapping[str, Any], *, require_profile_tuple: bool = True
) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ContractError("message must be a JSON object")
    message_type = value.get("message_type")
    if message_type == "hello":
        _check_exact_fields(value, HELLO_FIELDS)
    elif message_type == "event":
        _check_exact_fields(value, EVENT_FIELDS)
    else:
        raise ContractError("message type is not in the closed vocabulary")
    _check_bounded_value(value)
    if message_type == "hello":
        _check_common(value)
        _check_opaque_id(value["stream_epoch"])
        if value["profile_id"] != PROFILE_ID:
            raise ContractError("profile is not accepted")
        fingerprint = _check_string(value["layout_fingerprint"])
        if _FINGERPRINT_RE.fullmatch(fingerprint) is None:
            raise ContractError("layout fingerprint format is invalid")
        return dict(value)

    _check_common(value)
    _check_opaque_id(value["stream_epoch"])
    _check_opaque_id(value["event_id"])
    sequence = value["sequence"]
    if type(sequence) is not int or not 1 <= sequence <= MAX_SEQUENCE:
        raise ContractError("event sequence is outside the closed range")
    kind = value["kind"]
    payload = value["payload"]
    if kind == "key":
        _validate_key_payload(payload, require_profile_tuple)
    elif kind == "nack":
        _validate_nack_payload(payload)
    elif kind == "reset":
        _validate_reset_payload(payload)
    else:
        raise ContractError("event kind is not in the closed vocabulary")
    return dict(value)


def validate_message(raw: str | bytes) -> dict[str, Any]:
    """Validate one serialized contract message and return its plain object.

    The returned dictionary is a fresh, JSON-shaped value.  It is never retained
    by :class:`ConsumerState`; accepted semantic state is reduced to bounded,
    immutable key data and counters.
    """
    return _validate_message_object(_parse(raw))


def validate_json_object(raw: str | bytes) -> dict[str, Any]:
    """Descriptive alias for strict contract-message validation."""
    return validate_message(raw)


@dataclass(frozen=True, slots=True)
class AcceptedEvent:
    """One accepted non-text event reduced to its closed semantic fields."""

    kind: str
    sequence: int
    keys: tuple[str, ...] = ()
    distance: int | None = None
    corrected: bool | None = None
    reason: str | None = None


class ConsumerState:
    """Pure, process-local state for one authenticated live connection.

    ``restart`` returns a new connection state while retiring the old epoch.  A
    caller should use that method instead of sharing mutable state between a
    producer's incarnations.  This class deliberately has no hooks for actions,
    text, logging, graph mutation, I/O, or transport acknowledgements.
    """

    def __init__(
        self,
        *,
        allowed_layout_fingerprints: Iterable[str] = (LAYOUT_FINGERPRINT,),
        allowed_profiles: Iterable[str] = (PROFILE_ID,),
        _retired_epochs: Iterable[str] = (),
    ) -> None:
        fingerprints = frozenset(allowed_layout_fingerprints)
        profiles = frozenset(allowed_profiles)
        retired = frozenset(_retired_epochs)
        if not fingerprints or len(fingerprints) > MAX_ARRAY_ITEMS:
            raise ValueError("layout fingerprint allowlist must be bounded and non-empty")
        if any(
            not isinstance(item, str)
            or _FINGERPRINT_RE.fullmatch(item) is None
            or item == _ZERO_FINGERPRINT
            for item in fingerprints
        ):
            raise ValueError("layout fingerprint allowlist contains an invalid value")
        if not profiles or len(profiles) > MAX_ARRAY_ITEMS:
            raise ValueError("profile allowlist must be bounded and non-empty")
        if any(not isinstance(item, str) or item != PROFILE_ID for item in profiles):
            raise ValueError("profile allowlist contains an invalid value")
        if len(retired) > MAX_RETIRED_EPOCHS:
            raise ValueError("retired epoch set exceeds its bound")
        if any(_OPAQUE_ID_RE.fullmatch(item) is None for item in retired):
            raise ValueError("retired epoch set is invalid")

        self._allowed_layout_fingerprints = fingerprints
        self._allowed_profiles = profiles
        self._retired_epochs = retired
        self._epoch: str | None = None
        self._hello_accepted = False
        self._quarantined = False
        self._sequence = 0
        self._event_ids: set[str] = set()
        self._keys: list[tuple[str, ...]] = []
        self._nack_count = 0
        self._reset_count = 0

    @property
    def hello_accepted(self) -> bool:
        return self._hello_accepted

    @property
    def quarantined(self) -> bool:
        return self._quarantined

    @property
    def stream_epoch(self) -> str | None:
        return self._epoch

    @property
    def last_sequence(self) -> int:
        return self._sequence

    @property
    def accepted_keys(self) -> tuple[tuple[str, ...], ...]:
        return tuple(self._keys)

    @property
    def nack_count(self) -> int:
        return self._nack_count

    @property
    def reset_count(self) -> int:
        return self._reset_count

    def restart(
        self,
        *,
        allowed_layout_fingerprints: Iterable[str] | None = None,
        allowed_profiles: Iterable[str] | None = None,
    ) -> "ConsumerState":
        """Return clean state that rejects this and any earlier retired epoch."""
        if not self._hello_accepted:
            raise ContractError("cannot restart before accepting hello")
        assert self._epoch is not None
        return ConsumerState(
            allowed_layout_fingerprints=(
                self._allowed_layout_fingerprints
                if allowed_layout_fingerprints is None
                else allowed_layout_fingerprints
            ),
            allowed_profiles=(
                self._allowed_profiles if allowed_profiles is None else allowed_profiles
            ),
            _retired_epochs=self._retired_epochs | {self._epoch},
        )

    def _reject_stream(self, reason: str) -> None:
        self._quarantined = True
        raise ContractError(reason)

    def accept(
        self, message: str | bytes | Mapping[str, Any]
    ) -> AcceptedEvent | None:
        """Validate and atomically accept one serialized live message.

        A value-free ``ContractError`` is raised on rejection.  Semantic stream
        violations quarantine this state.  ``None`` represents accepted hello;
        events return an immutable data record and never translated text.
        """
        if self._quarantined:
            raise ContractError("stream is quarantined")
        if isinstance(message, Mapping):
            value = _validate_message_object(
                message, require_profile_tuple=False
            )
        else:
            value = _validate_message_object(
                _parse(message), require_profile_tuple=False
            )

        if value["message_type"] == "hello":
            if self._hello_accepted:
                self._reject_stream("connection accepts exactly one hello")
            epoch = value["stream_epoch"]
            if epoch in self._retired_epochs:
                raise ContractError("hello epoch was retired by a producer restart")
            if value["profile_id"] not in self._allowed_profiles:
                raise ContractError("hello profile is not allowlisted")
            if value["layout_fingerprint"] not in self._allowed_layout_fingerprints:
                raise ContractError("hello layout is not allowlisted")
            self._epoch = epoch
            self._hello_accepted = True
            return None

        if not self._hello_accepted:
            raise ContractError("hello must be accepted before event")
        assert self._epoch is not None

        if value["stream_epoch"] != self._epoch:
            self._reject_stream("event epoch differs from accepted hello")
        event_id = value["event_id"]
        if event_id in self._event_ids:
            self._reject_stream("event identifier was already committed")
        sequence = value["sequence"]
        if sequence != self._sequence + 1:
            self._reject_stream("event sequence is not contiguous")
        if sequence > MAX_EVENTS_PER_STREAM:
            self._reject_stream("event stream exceeds its state bound")

        kind = value["kind"]
        payload = value["payload"]
        keys: tuple[str, ...] = ()
        distance: int | None = None
        corrected: bool | None = None
        reason: str | None = None
        if kind == "key":
            keys = tuple(payload["keys"])
            if keys not in _ALLOWED_PROFILE_TUPLES:
                self._reject_stream("key tuple does not exactly match the profile")
            distance = payload["distance"]
            corrected = payload["corrected"]
        elif kind == "nack":
            reason = payload["reason"]
        else:
            reason = payload["reason"]

        self._sequence = sequence
        self._event_ids.add(event_id)
        if kind == "key":
            self._keys.append(keys)
        elif kind == "nack":
            self._nack_count += 1
        else:
            self._reset_count += 1
        return AcceptedEvent(
            kind=kind,
            sequence=sequence,
            keys=keys,
            distance=distance,
            corrected=corrected,
            reason=reason,
        )


__all__ = [
    "AcceptedEvent",
    "CONTRACT_VERSION",
    "ConsumerState",
    "ContractError",
    "EVENT_KINDS",
    "EVENT_FIELDS",
    "HELLO_FIELDS",
    "KEY_PAYLOAD_FIELDS",
    "LAYOUT_FINGERPRINT",
    "MESSAGE_TYPES",
    "NACK_PAYLOAD_FIELDS",
    "NACK_REASONS",
    "PROFILE_ID",
    "PROFILE_KEY_TUPLES",
    "RESET_PAYLOAD_FIELDS",
    "RESET_REASONS",
    "SOURCE",
    "STENO_KEYS",
    "validate_json_object",
    "validate_message",
]
