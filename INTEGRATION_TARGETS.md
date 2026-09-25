# Integration Targets

## Status and evidence class

This document records the external repositories as **reference-only integration targets**.
The integration status for every listed target is `REFERENCE_ONLY`. No listed repository is
vendored, forked, executed, or modified by this project, and none is a runtime authority for
the current product slice.

The evidence used for this boundary is limited to the dated `touch-steno`
`SYSTEMKOMPENDIUM.md` snapshot and the recorded repository/project notes. The public
`commindv2` and `commind` repositories were not directly inspectable through the available
public GitHub endpoints. Their current implementation is therefore not inferred here.

## Targets

### `touch-steno` — source-side target

- **URL:** <https://github.com/Liamlol1919/touch-steno> (cross-repository snapshot evidence is
  recorded in the dated `touch-steno/SYSTEMKOMPENDIUM.md` material).
- **Evidence class:** `REFERENCE_ONLY`.
- **Verified role:** touch-steno owns PTH-660 capture, contact segmentation, `[10,5,4]`
  decoding, the English steno profile mapping, NACK handling, sequencing, and local replay.
- **Inferred integration role:** source-side event authority for the PTH-660 pipeline. It is
  the only component that may read the device and turn raw contacts into a decoded English
  steno event.
- **Boundary:** its decoder and event semantics are not copied, replaced, or run a second time
  by the application consumer.

### `commindv2` — application-consumer target

- **URL:** <https://github.com/Liamlol1919/commindv2>.
- **Evidence class:** `REFERENCE_ONLY`.
- **Verified role:** the eventual application consumer is responsible for connection
  negotiation, event deduplication, translation/action policy, UI state, and graph mutation.
- **Inferred integration role:** destination-side consumer of already-decoded events, not a
  capture or decoding authority.
- **Hard boundary:** commindv2 must not open the same evdev device as touch-steno, recreate the
  `[10,5,4]` decoder, or request raw contacts from the consumer boundary.

### `commind` — concept and documentation target

- **URL:** <https://github.com/Liamlol1919/commind>.
- **Evidence class:** `REFERENCE_ONLY`.
- **Verified role:** documentation and concept canon, with possible future semantic/graph
  orchestration ideas.
- **Inferred integration role:** a non-runtime reference for vocabulary, semantic concepts, and
  future graph-orchestration design discussions.
- **Hard boundary:** it is not a current event producer, decoder, device owner, or authority for
  runtime behavior. Its current implementation is unknown from the available evidence.

## Ownership matrix

| Capability / artifact | touch-steno | commindv2 | commind | This project |
|---|---|---|---|---|
| PTH-660 evdev access and raw contacts | Owns; sole runtime owner | Must not access or duplicate | Must not access or duplicate | Must not bypass or mirror |
| Contact segmentation | Owns | Consumes decoded result only | Reference only | Documents and gates |
| `[10,5,4]` decoding | Owns | Must not run a second decoder | Reference only | Defines research boundary |
| English steno profile mapping | Owns | Consumes key events | Reference only | Reviews profile contract |
| NACK, sequencing, local replay | Owns | Applies consumer policy to received events | Reference only | Does not duplicate decoder replay |
| Connection negotiation | Boundary owner | Owns consumer negotiation | Reference only | Documents the boundary |
| Deduplication | Sequence-aware source metadata | Owns consumer deduplication | Reference only | Tests only at a future boundary |
| Translation/action policy, UI state | Not source responsibility | Owns | Reference only | Keeps policy downstream |
| Graph mutation | Not source responsibility | Owns | Concept reference only | No runtime integration now |
| Semantics and graph concepts | Not a runtime authority | May consume | Canon/reference | Research interpretation only |
| Raw contact privacy | Keeps raw contacts local | Receives no raw contacts | No runtime access | Enforces documentation boundary |

Ownership is one-way: touch-steno produces the contracted event and commindv2 consumes it.
A consumer-side policy, UI action, or graph mutation never causes the source to reinterpret or
re-export raw contacts.

## Historical event contract sketch (superseded as design only)

The following loose sketch is retained as prior history. It was never a protocol
implementation or a promise that either external repository exposes it.
`INTEGRATION_CONTRACT_V1.md` now supersedes it **only as the closed `DESIGN` proposal**
for a process-local `hello` and ordered `key`/`nack`/`reset` contract. The proposal is
not current runtime behavior in this project or either external target.

```text
EnglishStenoKeyEvent {
  contract_version: string
  event_id: opaque process-local identifier
  sequence: monotonic integer
  side: "left" | "right" | "bilateral"
  stroke: canonical English steno key-event representation
  state: "key" | "nack"
  source: "touch-steno"
}
```

Required interpretation:

- The transport is **versioned** and **process-local**; it is not a network publication, raw
  contact stream, or a second device connection.
- The event is **side-specific** where side is available. A bilateral representation must
  preserve the side relationship rather than flattening away which side produced a key.
- `state: "nack"` is an explicit source event and must not be silently converted to a key.
- Sequence and event identity are for ordering/deduplication in the consumer; they do not expose
  device identity, tracking IDs, coordinates, pressure, or contact lifetimes.
- The exact v1 representation and fail-closed rules are now specified in
  `INTEGRATION_CONTRACT_V1.md`, but remain unimplemented design rather than runtime
  compatibility.

## Privacy boundary

Raw contact frames, coordinates, areas, tracking IDs, device paths, calibration data, and
contact-lifetime details remain inside touch-steno. Only records permitted by the strict
allowlist in `INTEGRATION_CONTRACT_V1.md` may cross the proposed process-local boundary.
No reference target is authorized to collect raw contacts, replay private captures, or infer
anatomical identity. Any future event extension requires an explicit privacy review and a
versioned compatibility decision.

## Compatibility warning: archived `input_zones.json`

The archived `input_zones.json` is historical layout evidence, not a current cross-project
layout authority. It must not be copied into a new runtime, silently treated as the commindv2
layout, or used to resolve a mismatch between the source decoder and the application. In
particular, a self-consistent archived file cannot prove that a second consumer is using the
same keyboard, segmentation, or decoder semantics. `INTEGRATION_CONTRACT_V1.md` names
the source-owned profile/layout fingerprint as the proposal's source of truth and rejects
stale-layout ambiguity rather than adding a compatibility shim.

## No-implementation policy

This target register is documentation only. Do not implement, vendor, fork, connect to, open a
device from, or modify any listed external repository as part of this reference registration.
The next admissible work is offline contract conformance design after an explicit
implementation decision. Any runtime implementation requires a separate decision and must
retain the ownership, privacy, and no-second-decoder boundaries above.
