#!/usr/bin/env python3
"""Replay measured cued trials through the process-local steno contract.

Provenance: the companion fixture is derived from 24 measured cued trials in
one session, covering 8 classes with thumb-compass labels, with one operator
and no error bars.  The control experiment is still unrun.  These are
thumb-compass trials, not a whole-hand field gesture.

Run the self-contained fixture with one argument::

    python scripts/contract_replay.py tests/fixtures/contract_replay_capture.jsonl

For a live session, pass the raw capture and its session manifest as two
arguments::

    python scripts/contract_replay.py session.jsonl manifest.jsonl

This exercises the CONTRACT, not the recogniser.  A key can only be emitted when
the manifest explicitly carries a profile stroke; compass truth is never mapped
or guessed into a key.  Consequently this replay makes no accuracy claim.
"""
from __future__ import annotations

import argparse
import json
import math
import secrets
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from nextgen.boundary import (
    NACK_REASONS,
    PROFILE_ID,
    BoundaryConsumer,
    BoundaryEmitter,
    ContractError,
    ContractEvent,
)

JsonObject = dict[str, object]
PROVENANCE = (
    "24 measured cued trials; 8 classes with thumb-compass labels (not a whole-hand "
    "field gesture); one operator; one session; no error bars; control experiment still unrun"
)
CONTRACT_CAVEAT = (
    "CONTRACT replay, not recogniser validation: keys would come only from explicit "
    "manifest strokes, never fresh recognition, so no accuracy claim is made"
)


@dataclass(frozen=True)
class ReplayResult:
    hello: JsonObject
    events: tuple[JsonObject, ...]
    summary: JsonObject


def load_jsonl(path: Path) -> list[JsonObject]:
    """Load a JSONL file and identify malformed records with their line number."""
    records: list[JsonObject] = []
    with Path(path).open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"{path}:{line_number}: expected a JSON object")
            records.append(value)
    return records


def load_fixture(path: Path, *, limit: int | None = None) -> tuple[JsonObject, list[JsonObject]]:
    """Load the compact derived fixture's header and measured trial records."""
    records = load_jsonl(path)
    headers = [record for record in records if record.get("record") == "header"]
    trials = [record for record in records if record.get("record") == "trial"]
    if len(headers) != 1 or len(headers) + len(trials) != len(records):
        raise ValueError("fixture must contain exactly one header and otherwise trial records")
    if limit is not None:
        if limit < 1:
            raise ValueError("limit must be positive")
        trials = trials[:limit]
    return headers[0], trials


def _manifest_trial(record: Mapping[str, object]) -> JsonObject:
    return {
        key: value
        for key, value in record.items()
        if key not in {"record", "contact_field"}
    }


def _derive_capture_trials(
    capture_path: Path, manifest_records: Sequence[Mapping[str, object]]
) -> list[JsonObject]:
    """Join raw frames to the half-open windows of measured manifest trials."""
    frames = load_jsonl(capture_path)
    derived: list[JsonObject] = []
    for manifest in manifest_records:
        start = manifest.get("t_start")
        end = manifest.get("t_end")
        if type(start) not in (int, float) or type(end) not in (int, float):
            raise ValueError(f"manifest trial {manifest.get('cue_id')!r} lacks numeric timestamps")
        tracks: dict[str, list[list[float]]] = {}
        for frame in frames:
            timestamp = frame.get("t")
            contacts = frame.get("c")
            if (
                type(timestamp) not in (int, float)
                or not start <= timestamp < end
                or not isinstance(contacts, Mapping)
            ):
                continue
            for contact_id, values in contacts.items():
                if (
                    not isinstance(contact_id, str)
                    or not isinstance(values, list)
                    or len(values) != 3
                    or any(type(value) not in (int, float) for value in values)
                    or any(not math.isfinite(value) for value in values)
                ):
                    raise ValueError(f"invalid contact field in {capture_path}")
                tracks.setdefault(contact_id, []).append(
                    [timestamp, values[0], values[1], values[2]]
                )
        trial = dict(manifest)
        trial["contact_field"] = [
            {"contact_id": contact_id, "samples": samples}
            for contact_id, samples in tracks.items()
        ]
        derived.append(trial)
    return derived


def prepare_inputs(
    capture_path: Path,
    manifest_path: Path | None,
    *,
    limit: int | None = None,
) -> tuple[list[JsonObject], list[JsonObject]]:
    """Return paired capture and manifest trials from raw or derived inputs.

    The repository fixture is self-contained, so ``manifest_path`` may be
    omitted.  A derived manifest may be supplied as an override.  The original
    raw ``s12.jsonl`` and ``s12.manifest.jsonl`` may instead be supplied
    directly; practice trials are then excluded and raw contacts are joined by
    timestamp.
    """
    capture_records = load_jsonl(capture_path)
    is_derived = any(record.get("record") == "header" for record in capture_records)
    if is_derived:
        _, capture_trials = load_fixture(capture_path, limit=limit)
        if manifest_path is None:
            return capture_trials, [_manifest_trial(trial) for trial in capture_trials]
        _, manifest_trials = load_fixture(manifest_path, limit=limit)
        return capture_trials, [_manifest_trial(trial) for trial in manifest_trials]

    if manifest_path is None:
        raise ValueError("a manifest is required when replaying a raw capture")
    manifest_records = load_jsonl(manifest_path)
    complete = [
        record
        for record in manifest_records
        if record.get("practice") is not True
        and type(record.get("t_start")) in (int, float)
        and type(record.get("t_end")) in (int, float)
    ]
    if limit is not None:
        if limit < 1:
            raise ValueError("limit must be positive")
        complete = complete[:limit]
    return _derive_capture_trials(capture_path, complete), complete


def _layout_fingerprint() -> str:
    """Import the registered profile digest without a placeholder fallback."""
    try:
        from nextgen import profile_fingerprint
    except ModuleNotFoundError as exc:
        if exc.name == "nextgen.profile_fingerprint":
            raise RuntimeError(
                "required module nextgen.profile_fingerprint is missing; refusing "
                "to substitute a placeholder layout fingerprint"
            ) from exc
        raise
    return profile_fingerprint.layout_fingerprint()


def _contains_contacts(capture_trial: Mapping[str, object] | None) -> bool:
    if capture_trial is None:
        return False
    count = capture_trial.get("contact_count")
    if type(count) is int and count > 0:
        return True
    field = capture_trial.get("contact_field")
    return isinstance(field, list) and any(
        isinstance(track, Mapping) and bool(track.get("samples")) for track in field
    )


def _emit_trial(
    emitter: BoundaryEmitter,
    manifest_trial: Mapping[str, object],
    capture_trial: Mapping[str, object] | None,
) -> ContractEvent:
    """Emit only an explicit manifest stroke; otherwise emit a closed NACK."""
    if not _contains_contacts(capture_trial):
        return emitter.emit_nack("invalid_observation")

    stroke = manifest_trial.get("stroke")
    if stroke is None:
        return emitter.emit_nack("ambiguous_attribution")
    distance = manifest_trial.get("distance")
    if (
        not isinstance(stroke, list)
        or not stroke
        or any(not isinstance(key, str) for key in stroke)
        or type(distance) is not int
        or distance not in (0, 1)
    ):
        return emitter.emit_nack("invalid_observation")
    try:
        return emitter.emit_key(tuple(stroke), distance=distance)
    except ContractError:
        return emitter.emit_nack("invalid_observation")


def replay(
    capture_trials: Sequence[Mapping[str, object]],
    manifest_trials: Sequence[Mapping[str, object]],
    *,
    stream_epoch: str | None = None,
) -> ReplayResult:
    """Emit one boundary event per measured trial and mechanically consume it."""
    fingerprint = _layout_fingerprint()
    epoch = stream_epoch or secrets.token_hex(32)
    emitter = BoundaryEmitter(
        epoch,
        profile_id=PROFILE_ID,
        layout_fingerprint=fingerprint,
    )
    consumer = BoundaryConsumer(
        epoch,
        profile_id=PROFILE_ID,
        layout_fingerprint=fingerprint,
    )
    hello_result = consumer.accept_hello(emitter.hello)
    if not hello_result.ok:
        raise RuntimeError(f"boundary rejected the hello handshake: {hello_result.reason}")

    capture_by_id = {
        trial.get("cue_id"): trial
        for trial in capture_trials
        if isinstance(trial.get("cue_id"), str)
    }
    event_dicts: list[JsonObject] = []
    nacks: Counter[str] = Counter()
    keys = 0
    for manifest_trial in manifest_trials:
        cue_id = manifest_trial.get("cue_id")
        capture_trial = capture_by_id.get(cue_id) if isinstance(cue_id, str) else None
        event = _emit_trial(emitter, manifest_trial, capture_trial)
        result = consumer.consume(event)
        expected_acceptance = event.kind == "key"
        if result.ok != expected_acceptance or (
            not expected_acceptance
            and result.reason != "NACK refused; text synthesis is forbidden"
        ):
            raise RuntimeError(f"boundary rejected emitted event: {result.reason}")
        if event.kind == "key":
            keys += 1
        else:
            nacks[event.payload.reason] += 1
        event_dicts.append(event.to_dict())

    trials = len(manifest_trials)
    summary: JsonObject = {
        "trials": trials,
        "keys": keys,
        "nacks_by_reason": {reason: nacks[reason] for reason in sorted(NACK_REASONS)},
        "coverage_fraction": keys / trials if trials else 0.0,
        "provenance": PROVENANCE,
        "scope": CONTRACT_CAVEAT,
    }
    return ReplayResult(emitter.hello.to_dict(), tuple(event_dicts), summary)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "capture",
        type=Path,
        help="self-contained derived fixture, or raw capture with a separate manifest",
    )
    parser.add_argument(
        "manifest",
        type=Path,
        nargs="?",
        help="optional manifest override; required for a raw capture (live: capture manifest)",
    )
    parser.add_argument("--limit", type=int, help="replay only the first N measured trials")
    args = parser.parse_args(argv)
    capture_trials, manifest_trials = prepare_inputs(
        args.capture, args.manifest, limit=args.limit
    )
    result = replay(capture_trials, manifest_trials)
    print(json.dumps(result.hello, separators=(",", ":"), sort_keys=True))
    for event in result.events:
        print(json.dumps(event, separators=(",", ":"), sort_keys=True))
    print("SUMMARY " + json.dumps(result.summary, separators=(",", ":"), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
