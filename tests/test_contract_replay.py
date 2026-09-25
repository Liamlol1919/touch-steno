"""End-to-end mechanical checks for the offline contract replay fixture.

Provenance: 24 measured cued trials, 8 classes with thumb-compass labels, one
operator, one session, no error bars; the control experiment is still unrun.
These are thumb-compass trials, not a whole-hand field gesture.  The checks
exercise the CONTRACT, not the recogniser, and make no accuracy claim.  A key
would have to come from the manifest rather than fresh recognition.
"""
from __future__ import annotations

import json
from pathlib import Path

from nextgen.boundary import (
    CONTRACT_VERSION,
    EVENT_FIELDS,
    HELLO_FIELDS,
    KEY_PAYLOAD_FIELDS,
    NACK_PAYLOAD_FIELDS,
    NACK_REASONS,
    SOURCE,
    ContractEvent,
    Hello,
)
from scripts.contract_replay import load_fixture, main

FIXTURE = Path(__file__).parent / "fixtures" / "contract_replay_capture.jsonl"


def test_fixture_replay_has_only_closed_ordered_contract_records(capsys):
    header, capture_trials = load_fixture(FIXTURE)

    assert main([str(FIXTURE)]) == 0
    output_lines = capsys.readouterr().out.splitlines()
    hello_dict = json.loads(output_lines[0])
    event_dicts = [json.loads(line) for line in output_lines[1:-1]]
    summary = json.loads(output_lines[-1].removeprefix("SUMMARY "))

    assert "no error bars" in header["provenance"]
    assert "control experiment still unrun" in header["provenance"]
    assert set(hello_dict) == HELLO_FIELDS
    parsed_hello = Hello.from_dict(hello_dict)
    assert parsed_hello.to_dict() == hello_dict
    assert parsed_hello.contract_version == CONTRACT_VERSION
    assert parsed_hello.source == SOURCE

    parsed_events = [ContractEvent.from_dict(event) for event in event_dicts]
    assert [event.sequence for event in parsed_events] == list(range(1, len(parsed_events) + 1))
    assert all(set(event) == EVENT_FIELDS for event in event_dicts)
    assert all(event.stream_epoch == parsed_hello.stream_epoch for event in parsed_events)

    for event in event_dicts:
        payload = event["payload"]
        assert isinstance(payload, dict)
        assert "text" not in event
        assert "text" not in payload
        if event["kind"] == "nack":
            assert set(payload) == NACK_PAYLOAD_FIELDS
            assert payload["reason"] in NACK_REASONS
        else:
            assert event["kind"] == "key"
            assert set(payload) == KEY_PAYLOAD_FIELDS

    key_count = sum(event["kind"] == "key" for event in event_dicts)
    nack_count = sum(event["kind"] == "nack" for event in event_dicts)
    assert summary["trials"] == len(event_dicts) == len(capture_trials)
    assert summary["keys"] == key_count
    assert sum(summary["nacks_by_reason"].values()) == nack_count
    assert key_count + nack_count == summary["trials"]
    assert summary["coverage_fraction"] == key_count / summary["trials"]
