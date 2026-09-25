import json
from dataclasses import replace

import pytest

from nextgen.boundary import (
    CONTRACT_VERSION,
    EVENT_FIELDS,
    HELLO_FIELDS,
    KEY_PAYLOAD_FIELDS,
    LAYOUT_FINGERPRINT,
    NACK_PAYLOAD_FIELDS,
    NACK_REASONS,
    PROFILE_ID,
    RESET_PAYLOAD_FIELDS,
    RESET_REASONS,
    SOURCE,
    BoundaryConsumer,
    BoundaryEmitter,
    ContractError,
    accept_event,
    loads_record,
)
from nextgen.english_steno import Stroke

STREAM_EPOCH = "epoch-7f6b9d2c4a1e8f03b5d7c9e2a4f6081"
FINGERPRINT = "a1b2c3d4e5f60718293a4b5c6d7e8f90112233445566778899aabbccddeeff00"


def make_emitter() -> BoundaryEmitter:
    return BoundaryEmitter(
        STREAM_EPOCH,
        profile_id=PROFILE_ID,
        layout_fingerprint=FINGERPRINT,
    )


def make_consumer(emitter: BoundaryEmitter) -> BoundaryConsumer:
    consumer = BoundaryConsumer(
        emitter.stream_epoch,
        profile_id=emitter.profile_id,
        layout_fingerprint=emitter.layout_fingerprint,
    )
    assert consumer.accept_hello(emitter.hello).ok
    return consumer


def test_hello_handshake_is_exact_and_required_before_events():
    emitter = make_emitter()
    consumer = BoundaryConsumer(
        STREAM_EPOCH,
        profile_id=PROFILE_ID,
        layout_fingerprint=FINGERPRINT,
    )

    assert emitter.hello.to_dict() == {
        "contract_version": CONTRACT_VERSION,
        "message_type": "hello",
        "source": SOURCE,
        "stream_epoch": STREAM_EPOCH,
        "profile_id": PROFILE_ID,
        "layout_fingerprint": FINGERPRINT,
    }
    assert set(emitter.hello.to_dict()) == HELLO_FIELDS
    event = emitter.emit_key(Stroke("ST", ("S-", "T-")), distance=0, event_id="event-hello-1")
    assert not consumer.consume(event).ok
    assert consumer.accept_hello(emitter.hello).ok
    assert consumer.consume(event).ok


def test_ordered_envelope_contains_all_v1_fields_and_payload():
    event = make_emitter().emit_key(
        Stroke("ST", ("S-", "T-")),
        distance=1,
        corrected=True,
        event_id="event-envelope-1",
    )

    assert set(event.to_dict()) == EVENT_FIELDS
    assert event.to_dict()["message_type"] == "event"
    assert event.to_dict()["kind"] == "key"
    assert set(event.to_dict()["payload"]) == KEY_PAYLOAD_FIELDS
    assert event.to_dict()["payload"] == {
        "keys": ["S-", "T-"],
        "distance": 1,
        "corrected": True,
    }
    assert "side" not in event.to_dict()
    assert "state" not in event.to_dict()


def test_sequences_are_monotonic_across_key_nack_and_reset():
    emitter = make_emitter()
    events = [
        emitter.emit_key(Stroke("ST", ("S-", "T-")), distance=0, event_id="event-order-1"),
        emitter.emit_nack("nearest_tie", event_id="event-order-2"),
        emitter.emit_reset("interrupted", event_id="event-order-3"),
        emitter.emit_key(Stroke("*", ("*",)), distance=0, event_id="event-order-4"),
    ]

    assert [event.sequence for event in events] == [1, 2, 3, 4]
    assert emitter.last_sequence == 4
    assert all(event.contract_version == CONTRACT_VERSION for event in events)


@pytest.mark.parametrize("reason", sorted(NACK_REASONS))
def test_every_closed_nack_reason_is_accepted_without_synthesised_text(reason):
    emitter = make_emitter()
    event = emitter.emit_nack(reason, event_id=f"event-nack-{reason}")

    assert event.kind == "nack"
    assert set(event.to_dict()["payload"]) == NACK_PAYLOAD_FIELDS
    assert event.to_dict()["payload"] == {"reason": reason}
    result = accept_event(
        event,
        stream_epoch=STREAM_EPOCH,
        profile_id=PROFILE_ID,
        layout_fingerprint=FINGERPRINT,
        expected_sequence=1,
    )
    assert not result.ok
    assert not hasattr(result, "text")


def test_unknown_nack_reason_is_refused():
    with pytest.raises(ContractError, match="unknown NACK reason"):
        make_emitter().emit_nack("decode-failed", event_id="event-bad-nack")


@pytest.mark.parametrize("reason", sorted(RESET_REASONS))
def test_every_closed_reset_reason_is_accepted(reason):
    event = make_emitter().emit_reset(reason, event_id=f"event-reset-{reason}")

    assert event.kind == "reset"
    assert set(event.to_dict()["payload"]) == RESET_PAYLOAD_FIELDS
    assert event.to_dict()["payload"] == {"reason": reason}


def test_unknown_reset_reason_is_refused():
    with pytest.raises(ContractError, match="unknown RESET reason"):
        make_emitter().emit_reset("timeout", event_id="event-bad-reset")


def test_consumer_refuses_unknown_contract_version():
    emitter = make_emitter()
    event = emitter.emit_key(Stroke("A", ("A-",)), distance=0, event_id="event-version-1")
    consumer = make_consumer(emitter)

    result = consumer.consume(replace(event, contract_version="touchsteno.english-steno-key-event.v999"))

    assert not result.ok
    assert "contract version" in result.reason
    assert consumer.last_sequence == 0


def test_serialized_records_match_the_exact_privacy_allowlist():
    emitter = make_emitter()
    records = [
        emitter.hello.to_dict(),
        emitter.emit_key(Stroke("AE", ("A-", "-E")), distance=0, event_id="event-privacy-1").to_dict(),
        emitter.emit_nack("all_zero", event_id="event-privacy-2").to_dict(),
        emitter.emit_reset("cancelled", event_id="event-privacy-3").to_dict(),
    ]

    assert set(records[0]) == HELLO_FIELDS
    for event in records[1:]:
        assert set(event) == EVENT_FIELDS
        expected_payload = {
            "key": KEY_PAYLOAD_FIELDS,
            "nack": NACK_PAYLOAD_FIELDS,
            "reset": RESET_PAYLOAD_FIELDS,
        }[event["kind"]]
        assert set(event["payload"]) == expected_payload
        json.dumps(event)


def test_consumer_commits_nack_ordering_but_never_returns_text():
    emitter = make_emitter()
    consumer = make_consumer(emitter)
    nack = emitter.emit_nack("invalid_observation", event_id="event-nack-order")
    key = emitter.emit_key(Stroke("A", ("A-",)), distance=0, event_id="event-after-nack")

    nack_result = consumer.consume(nack)
    key_result = consumer.consume(key)

    assert not nack_result.ok
    assert key_result.ok
    assert consumer.last_sequence == 2
    assert not hasattr(nack_result, "text")


def test_replayed_event_is_rejected_and_quarantines_the_stream():
    emitter = make_emitter()
    consumer = make_consumer(emitter)
    first = emitter.emit_key(Stroke("A", ("A-",)), distance=0, event_id="event-replay-1")
    second = emitter.emit_key(Stroke("E", ("-E",)), distance=0, event_id="event-replay-2")

    assert consumer.consume(first).ok
    assert not consumer.consume(first).ok
    assert consumer.quarantined
    assert not consumer.consume(second).ok


def test_key_tuple_must_match_the_pinned_profile_exactly():
    emitter = make_emitter()

    with pytest.raises(ContractError, match="pinned profile tuple"):
        emitter.emit_key(("A-", "T-"), distance=0, event_id="event-tuple-1")


def test_zero_fingerprint_documentation_placeholder_is_not_deployable():
    assert LAYOUT_FINGERPRINT is None
    with pytest.raises(ContractError, match="all-zero"):
        BoundaryEmitter(
            STREAM_EPOCH,
            profile_id=PROFILE_ID,
            layout_fingerprint="0" * 64,
        )


def test_json_loader_rejects_duplicate_keys():
    with pytest.raises(ContractError, match="duplicate JSON key"):
        loads_record('{"contract_version":"x","contract_version":"y"}')
