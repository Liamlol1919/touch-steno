# Agentic State Ledger

**Loop:** 10× autonomous product-engineering meta-plan  
**Current phase:** 3 — Innovation branch prototypes
**Evidence class of current product slice:** `IMPLEMENTED`
**Active candidate:** Clean English steno transport plus offline contract validator
**Last promoted candidate:** English steno transport plus offline contract validator in `nextgen/`
**Last rejected candidate:** Legacy sector-fitting as the product core
**Open falsification test:** Real PTH-660 anatomy, identity, and false-commit study
**Next executable action:** Red-team the three offline branch prototypes against a shared
held-out synthetic contract; do not connect, vendor, or modify any external repository

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

- **Simplex-10:** retain as the **IMPLEMENTED PROTOTYPE** baseline. Its next gate is
  real anatomy/identity/false-commit and held-out chord evidence, plus a frozen profile
  identifier and layout fingerprint before any adapter.
- **FCPT:** **OFFLINE PROTOTYPE / HOLD.** The bounded target-cost model is executable, but
  coefficients, language compiler, anatomy, and human timing remain unvalidated.
- **Word-as-event:** **OFFLINE PROTOTYPE / HOLD.** Normalization and abstention are
  executable on synthetic trajectories; segmentation, held-out words, and correction cost
  remain unvalidated.
- **Contact-field:** **OFFLINE PROTOTYPE / HOLD; current legacy scripts rejected as
  evidence.** The corrected descriptor handles variable cardinality and nuisance transforms;
  separability, false commits, and cross-session robustness remain unvalidated.

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
