import contextlib
import copy
import io
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from nextgen.contract_v1 import (  # noqa: E402
    CONTRACT_VERSION,
    LAYOUT_FINGERPRINT,
    NACK_REASONS,
    PROFILE_ID,
    PROFILE_KEY_TUPLES,
    RESET_REASONS,
    SOURCE,
    STENO_KEYS,
    ConsumerState,
    ContractError,
    validate_message,
)
from nextgen.english_steno import STROKE_LIBRARY  # noqa: E402


EPOCH = "epoch-0123456789abcdef"
OTHER_EPOCH = "epoch-fedcba9876543210"
STALE_LAYOUT = "f" * 64


def hello(
    *,
    contract_version=CONTRACT_VERSION,
    epoch=EPOCH,
    source=SOURCE,
    profile_id=PROFILE_ID,
    layout_fingerprint=LAYOUT_FINGERPRINT,
):
    return {
        "contract_version": contract_version,
        "message_type": "hello",
        "source": source,
        "stream_epoch": epoch,
        "profile_id": profile_id,
        "layout_fingerprint": layout_fingerprint,
    }


def event(
    sequence=1,
    *,
    event_id=None,
    epoch=EPOCH,
    kind="key",
    payload=None,
):
    if event_id is None:
        event_id = f"event-{int(sequence):04d}-0123456789abcdef"
    if payload is None:
        payload = {"keys": ["A-"], "distance": 0, "corrected": False}
    return {
        "contract_version": CONTRACT_VERSION,
        "message_type": "event",
        "source": SOURCE,
        "stream_epoch": epoch,
        "event_id": event_id,
        "sequence": sequence,
        "kind": kind,
        "payload": payload,
    }


def encoded(value):
    return json.dumps(value, separators=(",", ":"))


class TestClosedVocabularies(unittest.TestCase):
    def test_exact_contract_and_profile_identifiers(self):
        self.assertEqual(CONTRACT_VERSION, "touchsteno.english-steno-key-event.v1")
        self.assertEqual(SOURCE, "touch-steno")
        self.assertEqual(PROFILE_ID, "nextgen.english-steno.simplex10.v1")
        self.assertRegex(LAYOUT_FINGERPRINT, r"[0-9a-f]{64}")

    def test_closed_key_nack_and_reset_vocabularies(self):
        self.assertEqual(STENO_KEYS, frozenset({
            "#", "S-", "T-", "K-", "P-", "W-", "H-", "R-", "A-", "O-", "*",
            "-E", "-U", "-F", "-R", "-P", "-B", "-L", "-G", "-T", "-S", "-D",
            "-Z",
        }))
        self.assertEqual(NACK_REASONS, frozenset({
            "distance_gt_1", "nearest_tie", "all_zero", "invalid_observation",
            "ambiguous_attribution",
        }))
        self.assertEqual(RESET_REASONS, frozenset({
            "contact_id_change", "interrupted", "cancelled",
        }))

    def test_pinned_tuple_order_matches_prototype_source_semantics(self):
        self.assertEqual(
            PROFILE_KEY_TUPLES,
            tuple(stroke.keys for stroke in STROKE_LIBRARY),
        )
        self.assertEqual(len(PROFILE_KEY_TUPLES), 32)
        self.assertEqual(len(set(PROFILE_KEY_TUPLES)), 32)


class TestStrictMessageValidation(unittest.TestCase):
    def test_valid_hello_and_every_event_variant(self):
        self.assertEqual(validate_message(encoded(hello())), hello())
        variants = (
            event(payload={"keys": ["S-", "T-"], "distance": 0, "corrected": False}),
            event(kind="nack", payload={"reason": "nearest_tie"}),
            event(kind="reset", payload={"reason": "interrupted"}),
        )
        for record in variants:
            with self.subTest(kind=record["kind"]):
                self.assertEqual(validate_message(encoded(record)), record)

    def test_every_closed_nack_and_reset_reason_validates(self):
        for kind, reasons in (("nack", NACK_REASONS), ("reset", RESET_REASONS)):
            for reason in reasons:
                with self.subTest(kind=kind, reason=reason):
                    record = event(kind=kind, payload={"reason": reason})
                    self.assertEqual(validate_message(encoded(record)), record)
            with self.subTest(kind=kind, reason="unknown"):
                with self.assertRaises(ContractError):
                    validate_message(encoded(event(
                        kind=kind, payload={"reason": "unknown"},
                    )))

    def test_all_pinned_tuples_and_special_keys_validate(self):
        for keys in PROFILE_KEY_TUPLES:
            with self.subTest(keys=keys):
                record = event(payload={
                    "keys": list(keys), "distance": 0, "corrected": False,
                })
                self.assertEqual(validate_message(encoded(record)), record)

    def test_exact_schema_rejects_missing_wrong_and_unknown_fields(self):
        mutations = []
        missing = hello()
        del missing["source"]
        mutations.append(missing)
        mutations.append(hello(source="other-source"))
        mutations.append(hello(contract_version="touchsteno.unknown.v1"))
        mutations.append(event(payload={"keys": ["A-"]}))
        mutations.append(event(payload={
            "keys": ["A-"], "distance": 0, "corrected": False, "confidence": 1,
        }))
        for record in mutations:
            with self.subTest(record=record):
                with self.assertRaises(ContractError):
                    validate_message(encoded(record))

    def test_unknown_privacy_fields_are_rejected_at_top_level(self):
        prohibited = {
            "x": 1,
            "y": 2,
            "coordinates": [[1, 2]],
            "contact_id": "secret-contact",
            "device_path": "/dev/input/event0",
            "text": "private translated text",
            "pressure": 0.5,
            "calibration": {"threshold": 1},
            "event_log_path": "/tmp/old-events.jsonl",
            "replay": True,
        }
        for field, value in prohibited.items():
            with self.subTest(field=field):
                record = event()
                record[field] = value
                with self.assertRaises(ContractError) as raised:
                    validate_message(encoded(record))
                self.assertNotIn(str(value), str(raised.exception))
                self.assertNotIn(field, str(raised.exception))

    def test_unknown_privacy_fields_are_rejected_in_payloads(self):
        for kind, payload in (
            ("key", {"keys": ["A-"], "pressure": 0.5}),
            ("nack", {"reason": "all_zero", "contact_id": "secret"}),
            ("reset", {"reason": "cancelled", "path": "/tmp/private"}),
        ):
            with self.subTest(kind=kind):
                with self.assertRaises(ContractError):
                    validate_message(encoded(event(kind=kind, payload=payload)))

    def test_duplicate_json_keys_are_rejected_at_any_object_depth(self):
        duplicate_payload = (
            '{"contract_version":"' + CONTRACT_VERSION + '",'
            '"message_type":"event","source":"touch-steno",'
            '"stream_epoch":"' + EPOCH + '","event_id":"event-0001-0123456789abcdef",'
            '"sequence":1,"kind":"key","payload":{"keys":["A-"],'
            '"distance":0,"corrected":false,"corrected":true}}'
        )
        with self.assertRaisesRegex(ContractError, "duplicate"):
            validate_message(duplicate_payload)

    def test_top_level_must_be_object_and_nesting_is_closed(self):
        for raw in ("[]", "null", '"A-"', "1"):
            with self.subTest(raw=raw):
                with self.assertRaises(ContractError):
                    validate_message(raw)
        with self.assertRaises(ContractError):
            validate_message(encoded(event(payload={
                "keys": ["A-"], "distance": 0, "corrected": False,
                "nested": {"coordinates": {"x": 1}},
            })))

    def test_wrong_json_types_and_boolean_integers_are_rejected(self):
        malformed = [
            event(sequence=True),
            event(sequence=1.0),
            event(sequence="1"),
            event(payload={"keys": "A-", "distance": 0, "corrected": False}),
            event(payload={"keys": ["A-"], "distance": False, "corrected": False}),
            event(payload={"keys": ["A-"], "distance": 0, "corrected": 0}),
            event(kind="nack", payload={"reason": []}),
            event(kind="reset", payload={"reason": {}}),
        ]
        for record in malformed:
            with self.subTest(record=record):
                with self.assertRaises(ContractError):
                    validate_message(encoded(record))

    def test_non_finite_and_fractional_numbers_are_rejected(self):
        for numeric in ("NaN", "Infinity", "-Infinity", "1.0"):
            with self.subTest(numeric=numeric):
                raw = encoded(hello()).replace(
                    '"layout_fingerprint":' + json.dumps(LAYOUT_FINGERPRINT),
                    '"sequence":' + numeric + ',"layout_fingerprint":'
                    + json.dumps(LAYOUT_FINGERPRINT),
                )
                with self.assertRaises(ContractError):
                    validate_message(raw)

    def test_strings_arrays_objects_and_total_bytes_are_bounded(self):
        invalid = [
            hello(epoch="e" * 129),
            hello(layout_fingerprint="A" * 64),
            event(payload={
                "keys": ["A-"] * 33, "distance": 0, "corrected": False,
            }),
            event(payload={
                "keys": ["A-"] * 32, "distance": 0, "corrected": False,
            }),
        ]
        for record in invalid:
            with self.subTest(record=record):
                with self.assertRaises(ContractError):
                    validate_message(encoded(record))
        with self.assertRaises(ContractError):
            validate_message(" " * 4097)

    def test_correction_disposition_is_exactly_tied_to_distance(self):
        for distance, corrected in ((0, True), (1, False), (2, False), (-1, False)):
            with self.subTest(distance=distance, corrected=corrected):
                with self.assertRaises(ContractError):
                    validate_message(encoded(event(payload={
                        "keys": ["A-"], "distance": distance,
                        "corrected": corrected,
                    })))

    def test_key_tuple_must_match_whole_ordered_profile_tuple(self):
        invalid_keys = (["T-", "S-"], ["S-"], ["A-", "-E", "-U"], ["*", "A-"])
        for keys in invalid_keys:
            with self.subTest(keys=keys):
                with self.assertRaises(ContractError):
                    validate_message(encoded(event(payload={
                        "keys": keys, "distance": 0, "corrected": False,
                    })))


class TestConsumerOrderingAndIdentity(unittest.TestCase):
    def setUp(self):
        self.state = ConsumerState()

    def connect(self, *, epoch=EPOCH, state=None):
        target = self.state if state is None else state
        self.assertIsNone(target.accept(encoded(hello(epoch=epoch))))
        return target

    def test_event_before_hello_creates_no_event_state(self):
        with self.assertRaisesRegex(ContractError, "hello"):
            self.state.accept(encoded(event()))
        self.assertFalse(self.state.hello_accepted)
        self.assertFalse(self.state.quarantined)
        self.assertEqual(self.state.last_sequence, 0)
        self.assertEqual(self.state.accepted_keys, ())
        self.connect()

    def test_connection_accepts_exactly_one_hello(self):
        self.connect()
        with self.assertRaises(ContractError):
            self.state.accept(encoded(hello()))
        self.assertTrue(self.state.quarantined)

    def test_profile_and_layout_hello_values_use_exact_allowlists(self):
        with self.assertRaises(ContractError):
            self.state.accept(encoded(hello(profile_id="unknown.profile")))
        self.assertFalse(self.state.hello_accepted)
        with self.assertRaisesRegex(ContractError, "layout"):
            self.state.accept(encoded(hello(layout_fingerprint=STALE_LAYOUT)))
        self.assertFalse(self.state.hello_accepted)
        with self.assertRaisesRegex(ContractError, "layout"):
            self.state.accept(encoded(hello(layout_fingerprint="0" * 64)))
        self.assertFalse(self.state.hello_accepted)
        self.connect()

    def test_epoch_mismatch_rejects_without_key_mutation(self):
        self.connect()
        accepted = self.state.accept(encoded(event(1)))
        self.assertEqual(accepted.keys, ("A-",))
        with self.assertRaises(ContractError):
            self.state.accept(encoded(event(2, epoch=OTHER_EPOCH)))
        self.assertTrue(self.state.quarantined)
        self.assertEqual(self.state.accepted_keys, (("A-",),))
        self.assertEqual(self.state.last_sequence, 1)

    def test_gap_and_future_sequences_quarantine_without_apply(self):
        for sequence in (2, 99):
            with self.subTest(sequence=sequence):
                state = ConsumerState()
                self.connect(epoch=f"epoch-gap-{sequence:04d}-abcdef", state=state)
                with self.assertRaises(ContractError):
                    state.accept(encoded(event(sequence)))
                self.assertTrue(state.quarantined)
                self.assertEqual(state.accepted_keys, ())
                self.assertEqual(state.last_sequence, 0)

    def test_lower_sequence_is_rejected_without_apply(self):
        self.connect()
        self.state.accept(encoded(event(1)))
        self.state.accept(encoded(event(2)))
        with self.assertRaisesRegex(ContractError, "sequence"):
            self.state.accept(encoded(event(
                1, event_id="event-lower-0001-abcdef",
            )))
        self.assertTrue(self.state.quarantined)
        self.assertEqual(self.state.last_sequence, 2)

    def test_duplicate_event_id_and_exact_replay_are_rejected(self):
        self.connect()
        record = event(1)
        self.state.accept(encoded(record))
        with self.assertRaisesRegex(ContractError, "identifier"):
            self.state.accept(encoded(copy.deepcopy(record)))
        self.assertTrue(self.state.quarantined)
        self.assertEqual(self.state.accepted_keys, (("A-",),))
        self.assertEqual(self.state.last_sequence, 1)

    def test_same_sequence_with_conflicting_content_is_rejected(self):
        self.connect()
        self.state.accept(encoded(event(1)))
        conflicting = event(
            1,
            event_id="event-conflict-0001-abcdef",
            payload={"keys": ["-E"], "distance": 0, "corrected": False},
        )
        with self.assertRaisesRegex(
            ContractError, r"^event sequence is not contiguous$"
        ):
            self.state.accept(encoded(conflicting))
        self.assertEqual(self.state.accepted_keys, (("A-",),))

    def test_invalid_profile_tuple_quarantines_without_accepted_key(self):
        self.connect()
        record = event(1, payload={
            "keys": ["T-", "S-"], "distance": 0, "corrected": False,
        })
        with self.assertRaisesRegex(ContractError, "profile"):
            self.state.accept(encoded(record))
        self.assertTrue(self.state.quarantined)
        self.assertEqual(self.state.accepted_keys, ())
        self.assertEqual(self.state.last_sequence, 0)

    def test_nack_and_reset_each_consume_sequence_without_key_mutation(self):
        self.connect()
        self.state.accept(encoded(event(1)))
        accepted_keys = self.state.accepted_keys
        nack = self.state.accept(encoded(event(
            2, kind="nack", payload={"reason": "distance_gt_1"},
        )))
        reset = self.state.accept(encoded(event(
            3, kind="reset", payload={"reason": "contact_id_change"},
        )))
        self.assertEqual((nack.kind, nack.sequence, nack.reason), ("nack", 2, "distance_gt_1"))
        self.assertEqual((reset.kind, reset.sequence, reset.reason), ("reset", 3, "contact_id_change"))
        self.assertEqual(self.state.accepted_keys, accepted_keys)
        self.assertEqual(self.state.last_sequence, 3)
        self.assertEqual(self.state.nack_count, 1)
        self.assertEqual(self.state.reset_count, 1)
        self.state.accept(encoded(event(4, payload={
            "keys": ["-E"], "distance": 1, "corrected": True,
        })))
        self.assertEqual(self.state.accepted_keys, (("A-",), ("-E",)))

    def test_steno_star_is_a_key_not_a_nack_or_reset(self):
        self.connect()
        accepted = self.state.accept(encoded(event(payload={
            "keys": ["*"], "distance": 0, "corrected": False,
        })))
        self.assertEqual(accepted.kind, "key")
        self.assertEqual(accepted.keys, ("*",))
        self.assertEqual(self.state.nack_count, 0)
        self.assertEqual(self.state.reset_count, 0)

    def test_syntax_rejection_does_not_advance_committed_state(self):
        self.connect()
        self.state.accept(encoded(event(1)))
        malformed = event(2, kind="nack", payload={
            "reason": "all_zero", "contact_id": "private-contact",
        })
        with self.assertRaises(ContractError):
            self.state.accept(encoded(malformed))
        self.assertEqual(self.state.last_sequence, 1)
        self.assertEqual(self.state.accepted_keys, (("A-",),))
        self.assertEqual(self.state.accept(encoded(event(2))).sequence, 2)


class TestRestartReplayAndNoTextEffects(unittest.TestCase):
    def test_restart_requires_fresh_epoch_and_rejects_old_stream_replay(self):
        state = ConsumerState()
        state.accept(encoded(hello()))
        old_event = event(1)
        state.accept(encoded(old_event))

        restarted = state.restart()
        with self.assertRaisesRegex(ContractError, "retired"):
            restarted.accept(encoded(hello()))
        self.assertFalse(restarted.hello_accepted)
        restarted.accept(encoded(hello(epoch=OTHER_EPOCH)))
        with self.assertRaisesRegex(ContractError, "epoch"):
            restarted.accept(encoded(event(
                1, epoch=EPOCH, event_id="event-restart-replay-abcdef",
            )))
        self.assertTrue(restarted.quarantined)
        self.assertEqual(restarted.accepted_keys, ())

    def test_fresh_epoch_restarts_with_empty_accepted_key_state(self):
        state = ConsumerState()
        state.accept(encoded(hello()))
        state.accept(encoded(event(1)))
        restarted = state.restart()
        restarted.accept(encoded(hello(epoch=OTHER_EPOCH)))
        self.assertEqual(restarted.stream_epoch, OTHER_EPOCH)
        self.assertEqual(restarted.last_sequence, 0)
        self.assertEqual(restarted.accepted_keys, ())
        accepted = restarted.accept(encoded(event(1, epoch=OTHER_EPOCH)))
        self.assertEqual(accepted.keys, ("A-",))

    def test_replay_resume_and_event_log_fields_are_rejected(self):
        for field, value in (
            ("replay", True),
            ("resume_cursor", 1),
            ("event_log_path", "/tmp/old.jsonl"),
            ("retained_event", event()),
        ):
            with self.subTest(field=field):
                state = ConsumerState()
                state.accept(encoded(hello()))
                record = event()
                record[field] = value
                with self.assertRaises(ContractError):
                    state.accept(encoded(record))
                self.assertEqual(state.accepted_keys, ())

    def test_no_semantic_text_output_or_consumer_mutation_for_nack_reset(self):
        state = ConsumerState()
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            state.accept(encoded(hello()))
            state.accept(encoded(event(1)))
            before = state.accepted_keys
            state.accept(encoded(event(
                2, kind="nack", payload={"reason": "invalid_observation"},
            )))
            state.accept(encoded(event(
                3, kind="reset", payload={"reason": "cancelled"},
            )))
            self.assertEqual(state.accepted_keys, before)
        self.assertEqual(stdout.getvalue(), "")
        self.assertEqual(stderr.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
