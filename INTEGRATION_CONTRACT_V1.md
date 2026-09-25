# English Steno Process-Local Contract V1 Proposal

**Artifact status:** `DESIGN` proposal only  
**Proposed contract identifier:** `touchsteno.english-steno-key-event.v1`  
**Scope:** one producer process to one local consumer process; live delivery only  
**Current implementation status:** not implemented by `nextgen/` or any integration target

This document closes the proposed wire shape and rejection behavior for a future
process-local boundary between a touch-steno source and an application consumer. It
supersedes the earlier loose event sketch in `INTEGRATION_TARGETS.md` as a **design
proposal only**. It does not describe current runtime behavior, does not modify an
external repository, and does not claim that the current `nextgen/` prototype already
speaks this contract.

## Evidence boundary

The current `nextgen/` prototype is `IMPLEMENTED` only for its bounded Simplex-10
transport: a 32-word, ten-bit `[10,5,4]` codebook; unique correction of one arbitrary
contact substitution; NACK for distance two, a nearest-codeword tie, or the all-zero
observation; and a 32-entry English profile with side-specific steno key labels.

Those facts make the prototype a compatible source for the semantic content proposed
below. They do not implement this envelope, stream epoch, contiguous sequence, event
ID, profile/layout handshake, NACK or RESET records, consumer validation, restart
handling, or replay prohibition. No hardware usability, anatomical side truth, Plover
runtime behavior, dictionary coverage, WPM, or correction-time claim follows from this
document.

## 1. Boundary and ownership

The proposed direction remains one-way:

```text
PTH-660 raw contacts
  -> touch-steno capture, segmentation, [10,5,4] decode, profile mapping, NACK
  -> this proposed process-local contract
  -> consumer validation, translation/action policy, UI state, graph mutation
```

The source is the sole owner of device access, contact segmentation, decoding, profile
mapping, source ordering, and local diagnostic behavior. The consumer may not open the
same device, request raw contacts, run a second decoder, remap steno keys, or infer a
missing event. The literal `source` field is an assertion inside the contract, not
authentication; a future implementation must use an OS-owned process-local endpoint or
equivalent peer authentication.

This contract is not a network protocol and does not authorize publication, telemetry,
durable retention, or external-repository changes.

## 2. Closed v1 schema

A connection consists of exactly one accepted `hello`, followed by zero or more ordered
`event` records. A new connection always starts with a new `hello`. No event is valid
before it.

Every serialized object is a closed JSON object. Unknown fields, duplicate JSON keys,
unknown nested objects, wrong JSON types, non-finite numbers, and unbounded strings or
arrays are protocol errors. There are no extension fields in v1.

### 2.1 `hello`

```json
{
  "contract_version": "touchsteno.english-steno-key-event.v1",
  "message_type": "hello",
  "source": "touch-steno",
  "stream_epoch": "opaque-fresh-epoch",
  "profile_id": "nextgen.english-steno.simplex10.v1",
  "layout_fingerprint": "0000000000000000000000000000000000000000000000000000000000000000"
}
```

Required rules:

- `contract_version` is the exact string above. An unknown version is rejected; there is
  no downgrade or compatibility guess.
- `source` is the exact string `touch-steno`.
- `stream_epoch` is a fresh high-entropy opaque value for one producer incarnation and
  one live connection. It is not a process ID, user ID, device ID, path, session name,
  timestamp, contact ID, or stable installation identity.
- `profile_id` identifies the frozen semantic profile. The proposed value names the
  current 32-entry Simplex-10 English profile; it does not claim that current code
  registers or emits it.
- `layout_fingerprint` is exactly 64 lowercase hexadecimal characters. It is an opaque
  source-owned digest of the frozen key-profile semantics, not raw geometry, calibration,
  or an archived layout file. The all-zero value above is documentation syntax, not a
  deployable fingerprint. A future implementation must freeze and register the real
  digest before connection.
- The consumer has an explicit allowlist for the exact contract, profile, and
  fingerprint. A missing, unknown, or mismatched value rejects the connection. The
  consumer never falls back to `input_zones.json`, a geometry cache, key-string
  heuristics, or a second decoder.

### 2.2 Ordered `event` envelope

Every `key`, `nack`, and `reset` uses the same outer envelope:

```json
{
  "contract_version": "touchsteno.english-steno-key-event.v1",
  "message_type": "event",
  "source": "touch-steno",
  "stream_epoch": "opaque-fresh-epoch",
  "event_id": "opaque-fresh-event-id",
  "sequence": 1,
  "kind": "key",
  "payload": {
    "keys": ["S-", "T-"],
    "distance": 0,
    "corrected": false
  }
}
```

Outer-field rules:

| Field | Closed rule |
|---|---|
| `contract_version` | Exact v1 identifier. |
| `message_type` | Exact string `event`. |
| `source` | Exact string `touch-steno`. |
| `stream_epoch` | Exact value accepted by the current `hello`; it cannot change in the stream. |
| `event_id` | Fresh high-entropy opaque value, unique within the epoch and never reused. It is not derived from sequence, a contact mask, a user, a device, or a path. |
| `sequence` | Integer at least 1. The first event is 1; every next event is exactly the previous value plus 1. |
| `kind` | Exactly `key`, `nack`, or `reset`. |
| `payload` | Exactly the object defined for that kind; fields from other kinds are forbidden. |

The source assigns a sequence only after resolving one source transaction. Key, NACK,
and RESET all consume one sequence. A NACK or RESET is therefore visible to ordering
and validation and can never disappear between transport and consumer policy.

### 2.3 `key` payload

A key payload has exactly these fields:

```json
{"keys":["S-","T-"],"distance":0,"corrected":false}
```

- `keys` is a non-empty ordered array of canonical side-specific English steno labels.
  Duplicate letters are never collapsed: left-bank labels end in `-`, right-bank labels
  begin with `-`, and the special labels are `#` and `*`.
- The only v1 labels are `#`, `S-`, `T-`, `K-`, `P-`, `W-`, `H-`, `R-`, `A-`, `O-`,
  `*`, `-E`, `-U`, `-F`, `-R`, `-P`, `-B`, `-L`, `-G`, `-T`, `-S`, `-D`, and `-Z`.
- The array must exactly equal one key tuple in the pinned 32-stroke profile, in that
  profile's order. The consumer validates the whole tuple; it does not accept an
  arbitrary subset, reorder labels, or infer a stroke from spelling.
- One event is one committed profile stroke, not a slash-separated outline. The consumer
  may assemble an ordered outline from accepted events, but a source must not batch an
  outline into one opaque field.
- `distance` is either 0 for an exact codeword or 1 for the prototype's unique
  one-substitution repair. `corrected` is true exactly when `distance` is 1. No
  confidence score, observed mask, expected mask, or contact evidence is permitted.
- A `*` key is the normal downstream steno correction/undo request. It is not a NACK or
  RESET.

The current `nextgen` key tuples can supply this payload, but the current `plover_json()`
outline wrapper is not the v1 event. The proposal deliberately carries keys rather than
notation or text and emits one stroke per event.

There is no separate hand-side or `bilateral` field in v1. Side is encoded in each
canonical key label, and the current prototype can contain mixed-bank keys in one
profile stroke. The repository has not established trustworthy anatomical hand
attribution for a separate side field. `left`, `right`, `bilateral`, `unknown`, and
`global` sketches therefore are not silently accepted as runtime semantics; bilateral
composition requires a later versioned contract decision with an explicit representation.

### 2.4 `nack` payload

A NACK payload has exactly one field:

```json
{"reason":"distance_gt_1"}
```

The closed v1 reason set is:

- `distance_gt_1`
- `nearest_tie`
- `all_zero`
- `invalid_observation`
- `ambiguous_attribution`

A NACK contains no key array, notation, best guess, observed mask, or expected mask.
It consumes a sequence number. It may drive a non-textual diagnostic state, but it must
not translate, insert or delete text, invoke an action, or mutate UI or graph state.
A NACK does not undo an earlier key.

### 2.5 `reset` payload

A RESET payload has exactly one field:

```json
{"reason":"contact_id_change"}
```

The closed v1 reason set is:

- `contact_id_change`
- `interrupted`
- `cancelled`

A RESET consumes a sequence number and clears tentative, uncommitted source/consumer
state for the current stream. It does not retract an already accepted key, undo a `*`,
translate text, perform an action, or mutate a graph. An incomplete or interrupted chord
must not fabricate a key; the source may account for the closed transaction with RESET.
This proposal does not claim that the current prototype emits RESET.

## 3. Ordering, identity, and rejection

A consumer validates in this order: syntax and exact schema; authenticated local peer;
accepted `hello`; contract/profile/fingerprint match; duplicate and epoch checks;
contiguous sequence; kind-specific payload; then downstream policy. No rejected record
may cause a semantic side effect.

| Condition | Required result |
|---|---|
| Event before accepted `hello` | Reject; no event state is created. |
| Unknown version, source, profile, or fingerprint | Reject connection; no fallback. |
| Event epoch differs from accepted `hello` | Reject stream as stale or foreign. |
| Sequence is not exactly previous sequence plus 1 | Quarantine the stream; do not reorder, fill, renumber, or apply the record. |
| `event_id` already committed in the epoch | Reject as duplicate; apply no side effect and require a fresh epoch. |
| Same sequence or event ID with conflicting content | Reject stream as a protocol violation. |
| Lower, skipped, or future sequence | Reject stream; no buffering or optimistic action. |
| Payload keys do not exactly match the pinned profile tuple | Reject record and quarantine the stream. |
| Producer process restarts or reconnects | Require a fresh high-entropy epoch and a fresh `hello`; reset consumer stream state. |
| Layout/profile changes | End the current stream and handshake with a new epoch and allowlisted pair. |
| Any replay or retained event is presented as live | Reject; v1 has no consumer-bound replay mode. |

There are no retries or acknowledgements in v1. An exact duplicate is not a successful
second delivery: it is rejected without semantic replay and the stream must restart.
This avoids claiming exactly-once behavior from an at-least-once process transport.

Sequence and event IDs have meaning only inside one authenticated, process-local epoch.
The contract makes no cross-restart duplicate-suppression or durable-resume claim.
Cross-restart retention would require a separate identity, retention, and privacy
decision.

## 4. Replay rule

V1 supports live process-local delivery only. It does not accept a `replay` flag, a
resume cursor, a partial stream, an event-log path, or an event copied from an earlier
epoch. Re-enqueuing a prior event, resuming after a gap, or replaying a full old stream
is rejected even if every field is internally consistent.

Source-local decoder diagnostics may use the repository's separate local raw/replay
machinery, subject to consent and retention policy. They must not masquerade as this
live contract or enqueue old contract records for a consumer. A future offline
consumer-bound replay mode requires a new contract version and an explicit
non-mutating/default-deny policy.

## 5. Strict privacy allowlist

The complete v1 boundary consists only of the exact `hello` and `event` fields above.
The allowed semantic content is limited to:

- exact protocol and source labels;
- opaque process-local epoch and event IDs;
- contiguous sequence;
- pinned profile identifier and opaque layout fingerprint;
- canonical side-specific steno keys;
- coarse distance/correction disposition;
- closed NACK/RESET reasons.

The following MUST NOT appear at any nesting depth in a live record, error envelope,
metric, or diagnostic retained at the boundary:

- coordinates, raw contact frames or arrays, geometry, bounding boxes, or trajectories;
- contact tracking IDs, slot IDs, contact lifetimes, or per-contact/anatomical identity;
- device paths, evdev node names, serials, process IDs, hardware addresses, user IDs, or
  stable installation/session identifiers;
- pressure, force, contact area/ellipse, tilt, orientation, palm/tool details, timing
  traces, timestamps, or latency values;
- calibration, thresholds, confidence models, learned parameters, or raw layout files;
- notation, outlines, translated text, dictionary candidates, graph payloads, or
  consumer action payloads.

The key sequence is necessarily content-bearing steno input. V1 does not authorize
logging or retaining it. Any persistence, telemetry, or replay proposal is a separate
privacy decision. A field-name denylist is not a substitute for the closed allowlist:
unknown fields are rejected even if their names appear harmless.

## 6. Compatibility with the current `nextgen` prototype

Compatibility is semantic and prospective, not implementation equivalence:

- The prototype's 32 canonical key tuples can be copied exactly into future v1 `key`
  payloads; the consumer must preserve the side-specific labels.
- Prototype distance 0 and unique distance 1 map to `distance` 0/1 and the corresponding
  `corrected` value.
- Prototype distance-two, nearest-tie, all-zero, and malformed completed observations
  can map to the corresponding closed NACK reasons.
- Prototype partial/interrupted behavior supplies no key and can be followed by a
  proposed RESET, but RESET is not currently implemented.
- The prototype's outline-shaped `plover_json()` output is not accepted as this event.
  A future adapter would split it into one event per stroke and omit notation, masks,
  and any non-allowlisted data.

Before any implementation is considered, the source must freeze the actual profile
identifier and layout fingerprint, define authenticated local transport ownership, and
approve an offline conformance fixture suite. Those are future gates, not accomplished
by this document.

## 7. Design-only acceptance matrix

A future implementation is conforming only if it demonstrates all of the following
without device access:

1. exact acceptance of one valid `hello` and each of the three valid event variants;
2. rejection of unknown versions, unknown fields, wrong types, duplicate JSON keys, and
   nested arbitrary data before side effects;
3. exact profile-tuple validation, including mixed-bank strokes and `*`/`#`;
4. contiguous ordering in which NACK and RESET consume sequence values;
5. duplicate, conflict, gap, stale-epoch, stale-layout, restart, and replay rejection;
6. NACK/RESET non-mutation and separation of transport correction from steno `*`;
7. recursive absence of every prohibited privacy field;
8. proof that the current prototype is adapted rather than silently accepted as the
   v1 envelope.

Until a separately authorized implementation supplies such evidence, this matrix remains
`DESIGN` and all external integration targets remain `REFERENCE_ONLY`.
