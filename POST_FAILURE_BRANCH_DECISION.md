# Post-Failure Branch Decision

**Decision status:** `FROZEN — RESEARCH ONLY`
**Decision date:** 2026-09-25
**Single next branch:** Temporal Set-Flow (TSF)
**Immediate prerequisite:** Test 0, repair of the synthetic scientific comparator
**Implementation status:** none; this decision authorizes no code, tests, device access, or product claim

## Decision

Temporal Set-Flow (TSF) is the single frozen next research branch after the post-failure
audit of `SYNTH-BRANCH-1`. TSF is an identity-free description of whole-field temporal
deformation after ephemeral adjacent-set assignment and explicit rigid nuisance removal.
It is not a renamed static Contact Field descriptor, a selected-finger path, an ordered
Elastic Word template, or a hardware-ready decoder.

The current Contact Field and Elastic Word implementations remain rejected/control-only. The
audit invalidates use of the old run's favorable null and Elastic results as promotion
evidence, but it does not establish that every redesign is impossible.

The next executable action is **Test 0: repair the scientific comparator before implementing
TSF**. A passing Test 0 only makes a TSF synthetic falsifier scientifically meaningful; it
does not implement, advance, or promote TSF. RCI and SOS are later comparators. Dwell,
topology, and raw-field branches remain on hold pending an independent arming/observability
or raw-interface prerequisite.

## Why `SYNTH-BRANCH-1` is structurally audited and non-promotional

The completed run and its exact metrics remain preserved in `SYNTH_BRANCH_1_RESULTS.md`.
They are historical outputs, not repaired evidence. The post-failure audit found structural
failures in the harness:

1. **Ground-truth null leakage forced abstention.** Both recognizer paths used
   `expected_output is None` to force every null to abstain. Reported zero null false
   commits therefore did not test recognizer safety.
2. **The declared disjoint split families were not independent.** Train, calibration, and
   test called shared generator functions with different labels/seeds. This is reseeding,
   not independent generator-family evidence.
3. **Calibration was generated but unused.** The run therefore did not demonstrate that
   calibration data selected acceptance, normalization, priors, or thresholds.
4. **Training was one exemplar per class.** Selecting a single `next(...)` training row is a
   prototype match, not a learned or robust class distribution.
5. **Contact Field cardinality leaked labels.** The descriptor included count while class
   index determined five versus six points, so cardinality parity exposed class identity.
6. **Elastic severe nuisance was nearly duplicate.** Its inserted point was only `0.0001`
   coordinate units from a neighbor before resampling; perfect invariance to that transform
   is not credible severe-nuisance evidence.

These are non-compensable integrity defects. No threshold change, additional favorable
metric, or later implementation can rehabilitate this run.

### What remains valid

- The run is a deterministic record of what the frozen implementation did on its generated
  inputs.
- The exact reported values remain reproducible historical facts, including Contact Field
  macro recall `0.585`, balanced accuracy `0.585`, coverage `0.8`, wrong-commit rate `0.28`,
  conditional accepted-event error `0.35`, null false-commit rate `0.0`, null upper bound
  `0.013347160654775625`, and nuisance recalls `0.9625/0.7625/0.3375/0.0`.
- The exact Elastic values likewise remain recorded: macro recall and balanced accuracy
  `1.0`, lower bound `0.9983118898757506`, coverage `0.8888888888888888`, wrong-commit and
  accepted-event error `0.0`, null upper bound `0.013347160654775625`, and recall `1.0` in
  every reported nuisance stratum.
- The poor generated-positive behavior of the current Contact Field implementation is
  sufficient to keep that implementation rejected; the audit does not need to credit its
  forced-null result in order to reject it.
- Elastic remains useful only as a control. Its perfect score does not establish anonymous
  segmentation, generalization, safe rejection, or end-to-end behavior.
- The run provides no hardware, human, WPM, correction, fatigue, privacy-retention, or
  text-accuracy evidence.

### What cannot be credited

- No reported null false-commit rate or null confidence bound as recognizer safety evidence.
- No calibration/generalization claim from the generated calibration split.
- No independent train/calibration/test family claim.
- No robust learned-class claim from a single exemplar per class.
- No Contact Field representation claim free of cardinality leakage.
- No severe-nuisance robustness claim for Elastic.
- No branch promotion, comparator superiority, product claim, or hardware claim.

The valid decision is therefore narrow: **reject the current Contact Field implementation;
retain Elastic as control/fallback only; preserve exact metrics; invalidate promotion credit;
repair the comparator next.**

## Non-compensable hard vetoes

The following apply before and after TSF is designed:

1. **Decision isolation.** A recognizer receives only its declared observation (timestamped
   unordered coordinate sets and allowed sensor-native fields). It never receives class,
   expected output, null/OOD status, nuisance label, split, session identity, or a
   label-derived null flag. Ground truth is joined only after its decision is serialized.
2. **Independent evidence splits.** Train, calibration, and test require independently
   implemented generator families, not one function under three names and seeds.
3. **Proper split use.** Training fits representations/models; calibration alone selects
   thresholds, margins, normalization, priors, and abstention; test is untouched until the
   frozen protocol runs. Calibration generation without consumption cannot count as use.
4. **Count matching and multiplicity checks.** Classes have matched cardinality
   distributions, and count-only controls must fail to solve the class task. Any cardinality
   or class-family association voids that run.
5. **No forced abstention.** An intentionally always-positive recognizer must fail the null
   gate; null rejection must emerge from frozen recognizer behavior.
6. **Identity freedom.** Slot, TID, array order, slot reuse, and TID magnitude cannot enter
   features, state, baselines, matching, event IDs, logs, errors, or retained data. Temporary
   adjacent assignment is recomputed from scratch and never becomes a persistent track.
7. **No selected-contact revival.** A branch requiring a named finger, thumb, stable mover,
   or anatomical identity remains vetoed under the recorded attribution failure.
8. **No split overlap or test tuning.** Generator-family sharing, prototype copying across
   splits, or choosing gates after test results voids the experiment.
9. **No synthetic safety substitution.** Synthetic palm/rest/burst cases can falsify code
   behavior but cannot prove hardware palm rejection or absence of risk.
10. **No duplicate or stale commit.** A repeated frame/stream or replay cannot create a
    second semantic event. Tentative state cannot cross a timestamp gap, burst, sleep,
    reconnect, malformed burst, new stream epoch, or identity-irrelevant configuration
    change; a fresh explicit rest acquisition must re-arm.
11. **No language-model rescue.** Lexical plausibility cannot turn ambiguous, stale,
    null-contaminated, or physically invalid observations into commits.
12. **No privacy leakage.** Raw coordinates, slot/TID data, temporal flow features, and
    calibration/rest templates are biometric-like and source-local. They are not exported by
    ordinary telemetry and are released after the decision, with no durable resume mode.
13. **No false evidence language.** Compute time is not human latency. No WPM, correction
    throughput, anatomy, reach, fatigue, privacy-by-retention, product, or hardware claim
    follows from this design or a synthetic pass.

A single hard-veto failure is non-compensable.

## Test 0 — immediate scientific-comparator repair

Test 0 precedes all TSF implementation. Its acceptance evidence must show that:

1. Recognizer decisions are produced and serialized without labels, expected output, null
   flags, split metadata, or nuisance metadata; only then are labels joined for scoring.
2. A deliberately broken recognizer that always returns a confident positive class fails the
   null false-commit gate. Its false commits are visible in the output.
3. Train, calibration, and test come from independently implemented generator families with
   different base shapes, temporal mechanisms, and nuisance transformations. They share no
   generation function or copied prototype.
4. Classes have identical or predeclared matched cardinality distributions. A count-only
   recognizer cannot recover the class labels, and other nuisance-only controls are reported.
5. Training uses the declared train family and aggregates all allowed training exemplars;
   it does not select one prototype per class.
6. Calibration data alone fixes all thresholds, confidence/abstention margins, normalization,
   and priors. Test labels and examples do not participate.
7. Test metrics use session-clustered confidence intervals or a predeclared cluster bootstrap;
   correlated frames from one session are not treated as independent observations.
8. A shuffled-label recognizer is at chance, and randomized slot/order permutations do not
   change semantic decisions or event counts.

Passing these checks validates the evidence boundary, not TSF. If any check fails, the run is
void and the comparator remains under repair.

## Frozen TSF primitive

At frame \(t\), the observation is an unordered coordinate set \(P_t\) with monotonic time and
no semantic identity. Between only adjacent frames \(P_{t-1}\) and \(P_t\), TSF may compute a
gated minimum-cost bipartite assignment. The assignment is an ephemeral computational device:
it estimates short-lived displacement and is discarded before the next frame. It is never a
tracking ID and cannot span add/drop, dropout, gap, reconnect, or rest events.

Before encoding, TSF fits and removes a declared rigid nuisance group: translation, the
policy-declared rotation/reflection transform, and positive uniform scale. A gated assignment
that fails the frozen cost/ambiguity rule is marked unknown and cannot silently become flow.
The semantic observation is the ordered sequence of **non-rigid residual whole-field
deformation** within a bounded event window. Classification uses deformation evolution,
not one instantaneous final shape.

A future implementation must freeze the transform policy, matching cost and ambiguity gate,
window duration/cardinality, residual features, classifier, and controls. No such choices or
performance numbers are established by this document.

## TSF state and observation model

```text
DISCONNECTED
  -> REST_CAPTURE
  -> LOCKED_REST
  -> TRACKING / ARMED
  -> TENTATIVE
  -> SETTLED
  -> EMIT once or ABSTAIN
```

- `REST_CAPTURE` / `LOCKED_REST`: establish an explicit per-session rest condition and
  calibration. No semantic event is emitted. Calibration and rest models are local,
  session-scoped, non-exported, and erased on disconnect.
- `TRACKING / ARMED`: maintain only a bounded rolling observation window. Assignments are
  recomputed per adjacent frame and never persisted as identities.
- `TENTATIVE`: accumulate a temporally ordered non-rigid residual-flow motif against the
  locked rest model. A peak, final shape, or one coherent fragment cannot commit.
- `SETTLED`: require a declared complete event boundary and return/stability condition.
  Emit at most one semantic attempt or abstain.
- A timestamp gap, malformed/saturated burst, sleep/wake, reconnect, new epoch, profile or
  layout change, or non-idle calibration transition destroys tentative state and enters
  quarantine. Only a fresh explicit rest acquisition can re-arm.

The existing strict lifecycle requirements remain mandatory: contiguous sequence, fresh
stream epoch, independent opaque event ID, fail-closed gap/duplicate/stale/restart/replay
handling, NACK/reset visibility, and no semantic effect from rejected or duplicate input.
The current process-local contract does not establish cross-restart exactly-once delivery;
claims remain bounded to its implemented lifecycle and at-most-one source emission attempt.
The existing privacy allowlist and no-raw-boundary rules also remain mandatory.

## Why TSF is distinct

- **Not static Contact Field:** TSF consumes an ordered sequence after nuisance removal;
  the rejected branch summarizes one unordered field. Adding time to the same static
  descriptor or learning from its count feature is not TSF.
- **Not a selected-finger trajectory:** TSF represents the deformation of the whole
  anonymous set. No anatomy, stable writer, or persistent correspondence is claimed.
- **Not Elastic Word:** Elastic expects an already ordered path and its severe transform is
  near-duplicate. TSF constructs only ephemeral adjacent assignments, explicitly separates
  rigid from non-rigid field motion, and is not a word-like path template.
- **Not count or shape memorization:** count, centroid/spread, instantaneous shape,
  q/coherence, and current Contact Field are mandatory controls. TSF survives only if
  non-rigid temporal deformation adds a predeclared margin over all of them.
- **Not language inference:** the output is a bounded field event, not text, steno, word, or
  WPM evidence.

## Synthetic falsifier for TSF

After Test 0 passes, freeze a new manifest before inspecting results. Independent split
families generate classes from **temporal deformation operators applied to randomized rest
fields**, not class-specific static polygons or copied descriptors.

The protocol must include:

- multiple randomized rest fields and count-matched classes;
- rest jitter/settling, matched palm add/remove/reposition, whole-hand rigid shifts/rotations/
  scale, slow re-centering, dropout/addition, permutation and slot-reassignment attacks;
- reader-init patterns; duplicate whole frames; bursts of 1, 2, 5, 20, and 100 frames; gaps
  of 50, 100, 250, and 660 ms; sleep/reconnect and new-epoch attacks;
- positives sharing count and, as far as the generator permits, matched instantaneous
  shape/motion-magnitude controls so temporal deformation must carry class evidence;
- nulls matched to positive rigid-motion magnitude, path length, count, and rest/q statistics
  where feasible;
- open-set/incomplete transformations and aborted events.

Compare full TSF against count-only, centroid/spread-only, instantaneous-shape, q/coherence,
rigid-motion-only, and current Contact Field controls. All use the same split, event
lifecycle, and scoring.

### Advancement gates

All gates are required; none compensates for another:

- joint correct rate counting abstention as failure is at least `0.90`;
- macro-recall one-sided 95% session-clustered lower bound is at least `0.85`;
- conditional accepted-event error one-sided 95% session-clustered upper bound is at most
  `0.01`;
- null false-commit one-sided 95% session-clustered upper bound is at most `0.01`;
- every nuisance family has at least `0.90` recall and remains above its matched control;
- full TSF exceeds the strongest predeclared control by at least `0.10` macro recall, with a
  positive paired session-clustered 95% lower bound;
- zero palm/rest/burst/reconnect null commits in the frozen run;
- permutation, slot reassignment, duplicate, gap, epoch, and replay attacks pass structurally;
- no label, null flag, slot/TID, or test-set information crosses the decision path.

These thresholds are frozen research gates, not achieved measurements.

## Exact kill criteria

Kill TSF as the next research branch if any of the following occurs:

1. Test 0 cannot establish decision isolation, always-positive null failure, independent
   generators, proper train/calibration/test use, count matching, or clustered intervals.
2. TSF requires stable contact identity, a selected finger/writer, slot/TID semantics, or a
   persistent assignment that spans more than one adjacent-frame computation.
3. Rigid nuisance removal is not identifiable under the frozen transform policy, or the
   chosen assignment becomes an identity proxy.
4. Class labels are predictable from contact count, parity, centroid/spread, final shape, or
   another nuisance-only control.
5. Full temporal TSF fails to beat the strongest declared control by `0.10` macro recall,
   or the paired session-clustered 95% lower bound of that margin is not positive.
6. A null palm, rest, burst, duplicate, gap, reconnect, new-epoch, or replay case commits.
7. Any null/OOD decision depends on `expected_output`, a null flag, labels, nuisance level,
   or split metadata.
8. Any split shares a generator function or prototype with another split, any class has
   unmatched cardinality leakage, or calibration is unused/test-tuned.
9. Permuting input order or reassigning slots changes the semantic decision, event count,
   retained state, event ID, logs, or errors.
10. A timestamp gap, burst, sleep/wake, reconnect, or new epoch resumes tentative state,
    bridges an event, or duplicates an emission.
11. Any raw coordinate, timestamp, slot/TID, matching matrix, residual flow, or calibration
    data crosses the strict semantic boundary or enters ordinary telemetry.
12. A language model or lexical plausibility is needed to convert an otherwise invalid
    observation into a commit.
13. The result fails any frozen common recognition, safety, nuisance, structural, or
    privacy gate above, or threshold relaxation is proposed to rescue it.

A synthetic pass authorizes only a separately consented hardware falsifier after a new
decision. It does not establish hardware usability, human performance, privacy by retention,
correction throughput, WPM, text accuracy, or product readiness.

## Frozen research order

| Position | Branch | Decision |
|---|---|---|
| Immediate prerequisite | **Comparator repair / Test 0** | Repair the scientific evidence boundary before TSF exists. |
| Single next branch | **Temporal Set-Flow (TSF)** | Implement only after Test 0 passes; then run one frozen synthetic falsifier. |
| Later comparators | **Rest-Censored Innovation (RCI)** | Consider only after TSF is decided; test slow excursions under locked session rest. |
| Later comparators | **Spatiotemporal Occupancy Sketch (SOS)** | Consider only after TSF is decided; test local grid-space temporal texture. |
| Hold / prerequisite | **Dwell** | No independent validated arming primitive; hold. |
| Hold / prerequisite | **Topology** | First require stable graph structure under rest jitter; otherwise stop. |
| Prerequisite hold | **Raw field** | First require a read-only capability audit proving timestamped dense target-device data; no inferred interface. |

This ordering is frozen. It is not authority to implement the later comparators or hold
branches, and it makes no hardware claim.
