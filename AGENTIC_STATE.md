# Agentic State Ledger

**Loop:** 10× autonomous product-engineering meta-plan  
**Current phase:** 4 — TSF synthetic falsifier failed; fresh post-failure branch decision required
**Evidence class of current product slice:** `IMPLEMENTED`
**Active candidate:** Clean English steno transport plus offline contract validator
**Promoted offline research branch:** None; no branch is promoted to product or hardware
**Single next research branch:** None pending a fresh post-failure branch decision
**Rejected/control/hold branches:** TSF prototype rejected/held after its frozen synthetic falsifier; Current Contact Field implementation rejected; Elastic Word control/fallback; FCPT selectable-thumb primitive rejected; RCI/SOS later comparators; dwell/topology/raw-field hold/prerequisite
**Open falsification test:** None; the first frozen TSF synthetic falsifier failed its positive-accuracy and temporal-information-margin gates
**Next executable action:** Make a fresh post-failure branch decision; do not tune or advance the rejected/held TSF prototype and make no hardware or product claim

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

`POST_FAILURE_BRANCH_DECISION.md` is the frozen post-failure authority. It records that `SYNTH-BRANCH-1` is structurally audited and non-promotional while preserving its exact metrics.

- **Contact-field:** **CURRENT IMPLEMENTATION REJECTED.** The frozen run reports macro recall `0.585`, coverage `0.8`, wrong-commit `0.28`, conditional accepted error `0.35`, null upper95 `0.013347160654775625`, and nuisance recall `0.9625/0.7625/0.3375/0.0`. Wrong-commit/error and nuisance failures are valid rejection evidence. Null safety is not credited because `expected_output is None` forced abstention, and class-count parity leaked labels. The audit does not prove every redesign impossible.
- **Word-as-event / Elastic Word:** **SYNTHETIC CONTROL/FALLBACK / HOLD; NON-PROMOTIONAL.** The exact run reports macro recall `1.0`, lower95 `0.9983118898757506`, coverage `0.8888888888888888`, error rates `0.0`, null upper95 `0.013347160654775625`, and all-stratum recall `1.0`. It is not safety/generalization/severe-nuisance evidence: nulls were forced, splits shared generators, calibration was unused, one exemplar trained each class, and severe insertion was a `0.0001`-unit near-duplicate. Anonymous path construction remains absent.
- **Temporal Set-Flow (TSF):** **BOUNDED PROTOTYPE IMPLEMENTED, RESEARCH-ONLY; FALSIFIER REJECTED/HELD.** It remains identity-free and structurally tested, but the frozen synthetic run reports positive accuracy `0.0` over 12 test examples (3-cluster, 256-replicate accuracy interval `[0.0, 0.0]`), null false-commit rate `0.0` (interval `[0.0, 0.0]`), calibration threshold `0.0834054855946207`, and `test_used_for_selection=false`. The best control was `rigid_motion` at `0.3333333333333333`; the observed TSF margin was `-0.3333333333333333`, with paired clustered margin interval `[-0.6666666666666666, 0.0]`. `kill_gate_passed=false`, so claim remains `none`. `TSF_FALSIFIER_RESULTS.md` is authoritative; no hardware, human, performance, or product claim follows.
- **RCI and SOS:** remain unimplemented later comparators and do not advance automatically. A fresh post-failure branch decision is required before selecting any next branch. **Dwell, topology, and raw-field:** hold/prerequisite for independent arming, graph stability, and target-interface observability respectively.
- **FCPT:** **CURRENT SELECTABLE-THUMB PRIMITIVE REJECTED; ARITHMETIC HELD.** The frozen run has 27 modeled-cost settings and `recognition_metrics=null`; modeled cost is not recognition or hardware evidence.

Test 0 is implemented, tested, and frozen. `SCIENTIFIC_COMPARATOR_TEST0_RESULTS.md` records canonical `FROZEN_MANIFEST_SHA256` `922524b495753bd2f4394380b850f4d788c4b38b9af4ea057e57414fe601a25f` (raw file SHA-256 `eccee106fab4b7aa19a48d0f160c4ea4a933e74b794b996da39a980747aa77c4`), runtime validation through read-only `load_frozen_manifest()`, mutation refusal with `ValueError`, the 9-test integrity pass, and the full-suite result of 286 tests with 1 skipped and 0 failed. Its nearest-centroid control achieved positive accuracy `1.0`, null false-commit rate `0.0`, calibration threshold `0.15827817469940747`, a passing null gate, and positive-accuracy interval `[1.0, 1.0]` from a 4-cluster, 256-replicate session bootstrap. The always-positive control failed with null false-commit rate `1.0`; shuffled-label, count-only, and path-length-only controls were at or below chance; point-order permutation invariance and decision-before-truth serialization were true. The frozen decisions are serialized without labels, expected output, null flags, split/session/class metadata

`TSF_FALSIFIER_RESULTS.md` records the first frozen TSF falsifier. Its canonical manifest
digest is `a95f0d18832362b314417c557d615be4802cc869010617113fb75100090ffe7e`;
all 11 TSF tests passed, but the executed result failed the positive-accuracy and paired
temporal-information-margin gates. This historical failure is not repaired by retuning or by
structural-test success.

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
