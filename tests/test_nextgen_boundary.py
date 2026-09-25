import json
from dataclasses import replace

import pytest

from nextgen.boundary import (
    CONTRACT_VERSION,
    BoundaryEmitter,
    accept_event,
)
from nextgen.english_steno import Stroke


def test_sequences_are_monotonic_across_keys_and_nacks():
    emitter = BoundaryEmitter()

    events = [
        emitter.emit_key(Stroke("ST", ("S-", "T-")), "left"),
        emitter.emit_nack(event_id="decode-failed", reason="ambiguous"),
        emitter.emit_key(Stroke("E", ("-E",)), "right"),
    ]

    assert [event.sequence for event in events] == [1, 2, 3]
    assert emitter.last_sequence == 3
    assert all(event.contract_version == CONTRACT_VERSION for event in events)


def test_consumer_refuses_unknown_contract_version():
    event = BoundaryEmitter().emit_key(Stroke("A", ("A-",)), "left")

    result = accept_event(replace(event, contract_version="en-steno-key/999"))

    assert not result.ok
    assert "contract version" in result.reason


def test_nack_has_no_stroke_and_consumer_refuses_it():
    event = BoundaryEmitter().emit_nack(reason="decode failed")

    assert event.state == "nack"
    assert event.stroke == ()
    result = accept_event(event)
    assert not result.ok
    assert "NACK" in result.reason


def test_invalid_side_is_rejected_with_allowed_values():
    with pytest.raises(ValueError, match="left.*right.*bilateral"):
        BoundaryEmitter().emit_key(Stroke("A", ("A-",)), "middle")


def test_serialised_event_contains_exactly_contract_fields():
    event = BoundaryEmitter().emit_key(Stroke("AE", ("A-", "-E")), "bilateral")

    payload = event.to_dict()
    encoded = json.dumps(payload)

    assert set(payload) == {
        "contract_version",
        "event_id",
        "sequence",
        "side",
        "stroke",
        "state",
        "source",
    }
    assert not any(
        forbidden in encoded.lower()
        for forbidden in ("coordinate", "tracking", "timestamp", "pressure")
    )


def test_bilateral_requires_keys_from_both_sides():
    emitter = BoundaryEmitter()
    left_only = Stroke("A", ("A-",))

    with pytest.raises(ValueError, match="both left and right"):
        emitter.emit_key(left_only, "bilateral")
    with pytest.raises(ValueError, match="both left and right"):
        emitter.emit_key(("A-",), "bilateral")

    accepted = emitter.emit_key(("A-", "-E"), "bilateral")
    assert accepted.side == "bilateral"
    assert accepted.sequence == 1
    assert accept_event(accepted).ok
