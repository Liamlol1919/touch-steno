# Agentic State Ledger

**Loop:** 10× autonomous product-engineering meta-plan  
**Current phase:** 3 — Frozen `SYNTH-BRANCH-1` comparison complete; redesign/hold
**Evidence class of current product slice:** `IMPLEMENTED`
**Active candidate:** Clean English steno transport plus offline contract validator
**Promoted offline research branch:** None; no branch is promoted to product
**Rejected/hold branches:** Contact Field representation rejected as current primary, pending redesign/hold; FCPT current selectable-thumb primitive rejected, arithmetic only
**Open falsification test:** Contact Field redesign must declare a fresh representation and evidence boundary before any new comparator
**Next executable action:** Hold and redesign the Contact Field representation if justified; do not inflate claims, retune to erase failed gates, or promote Elastic Word from synthetic control/fallback status

## Decisions

- English steno is the product language.
- German steno is out of scope.
- Prior experiments are archived and not used to fit the new product.
- The coordinator may publish ordinary code/docs/issues autonomously.
- Hardware, consent, privacy, destructive operations, and unsupported performance claims require explicit human intervention.

## Evidence boundary

The current `nextgen/` code proves a ten-bit transport, one-bit correction contract, canonical English steno stroke profile, and Plover JSON boundary. It does not prove Plover runtime translation, hardware usability, WPM, correction time, or complete English vocabulary coverage.

## Contract decision

`INTEGRATION_CONTRACT_V1.md` is paired with the implemented offline validator in
`nextgen/contract_v1.py` and its conformance tests. The contract closes a process-local
`hello` plus ordered `key`/`nack`/`reset` records with a fresh stream epoch, exact contract
version, pinned source/profile/layout fingerprint, contiguous sequence, opaque event ID,
canonical side-specific English steno keys, strict privacy allowlist, and fail-closed
duplicate, gap, stale-layout, restart, and replay rejection. The validator is pure and
bounded; it does not connect to a device, socket, Plover, or external repository. The
prototype and contract validator are `IMPLEMENTED` offline; runtime integration remains
unimplemented.

## Innovation branch decisions

- **Simplex-10:** retain as the **IMPLEMENTED PROTOTYPE** product baseline. Its next gate is
  real anatomy/identity/false-commit and held-out chord evidence, plus a frozen profile
  identifier and layout fingerprint before any adapter.
The completed frozen `SYNTH-BRANCH-1` run supersedes the earlier static comparison. Its exact results and gate evaluation are recorded in `SYNTH_BRANCH_1_RESULTS.md`.

- **Contact-field:** **REJECTED AS CURRENT PRIMARY REPRESENTATION; REDESIGN/HOLD.** The frozen run reports macro recall `0.585`, coverage `0.8`, wrong-commit rate `0.28`, conditional accepted-event error `0.35`, null false-commit upper95 `0.013347160654775625`, and nuisance recall `0.9625` clean, `0.7625` mild, `0.3375` moderate, and `0.0` severe. It clears basic discriminability but fails the wrong-commit/accepted-error and nuisance requirements; no hold label overrides those failed gates.
- **Word-as-event / Elastic Word:** **SYNTHETIC CONTROL/FALLBACK / HOLD.** The frozen comparator reports macro recall `1.0`, coverage `0.8888888888888888`, wrong-commit rate `0.0`, conditional accepted-event error `0.0`, and nuisance recall `1.0` in every stratum. The reported null upper95 is `0.013347160654775625`; regardless of that bound, the result does not establish anonymous-contact segmentation, end-to-end event construction, correction, or product readiness.
- **FCPT:** **CURRENT SELECTABLE-THUMB PRIMITIVE REJECTED; ARITHMETIC HELD.** The frozen run has 27 modeled-cost settings and `recognition_metrics=null`. Modeled cost is not recognition accuracy, hardware evidence, or human evidence.

No branch is promoted to product. Synthetic comparator results are not hardware, human, WPM, correction, or text-accuracy evidence.

## Reference integration targets

- **touch-steno** — <https://github.com/Liamlol1919/touch-steno>; `REFERENCE_ONLY` dated
  snapshot evidence. It owns PTH-660 capture, segmentation, `[10,5,4]` decoding, English
  steno profile mapping, NACK, sequencing, and local replay.
- **commindv2** — <https://github.com/Liamlol1919/commindv2>; `REFERENCE_ONLY`. It is the
  eventual application consumer for connection negotiation, deduplication, translation/action
  policy, UI state, and graph mutation.
- **commind** — <https://github.com/Liamlol1919/commind>; `REFERENCE_ONLY`. It is a
  documentation/concept canon and future semantic/graph reference, not a runtime authority.

The ownership boundary is one-way and process-local: touch-steno is the sole PTH-660
capture/decoder owner and emits only versioned, side-specific English steno key/NACK events.
Raw contacts never leave touch-steno. commindv2 must not open the same evdev device or run a
second decoder. The archived `input_zones.json` is historical evidence, not a layout
authority or compatibility shim. The contract proposal is complete at the documentation
level; the next action remains explicitly gated and no external repository or runtime path
is implemented by this state update.
