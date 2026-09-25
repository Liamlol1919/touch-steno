# RCI Synthetic Falsifier Decision

**Decision status:** `FROZEN — RCI IS THE SINGLE FRESH DESIGN-ONLY BRANCH; SOS HELD`  
**Evidence class:** `DESIGN` only  
**Protocol to freeze on implementation:** `RCI-SYNTHETIC-FALSIFIER-1`, version 1  
**Implementation status:** RCI is `UNIMPLEMENTED`; no executable primitive, manifest, test result, or performance result exists  
**Product/hardware status:** no promotion and no hardware, human, WPM, correction, latency, text-accuracy, privacy-by-retention, or product claim

## Decision and non-revival boundary

Rest-Censored Innovation (RCI) is the single fresh post-failure research branch selected
after the Temporal Set-Flow (TSF) falsifier. This document freezes the design and its first
falsifier contract. Implementation may begin only after this decision is recorded, and the
manifest must be frozen before any RCI test result is inspected.

RCI is a new, narrower hypothesis. It recognizes a bounded scalar excursion of a
timestamped unordered point set from an explicitly captured and then immutable empirical
set-rest measure. It does **not** use slot/TID, a per-contact baseline, adjacent matching,
selected-contact or writer attribution, rigid/non-rigid residual flow, or any TSF feature,
manifest, prototype, threshold, or implementation.

TSF remains **HELD/REJECTED** after its frozen falsifier. The exact historical failure is
preserved: positive accuracy `0.0`, best `rigid_motion` control
`0.3333333333333333`, observed margin `-0.3333333333333333`, paired session-clustered lower
95% bound `-0.6666666666666666`, and `claim=none`. RCI does not revive, retune, rename, or
inherit a passing result from TSF.

Spatiotemporal Occupancy Sketch (SOS) remains **HOLD / UNIMPLEMENTED**. It receives no
parallel implementation, automatic advancement, or performance credit from this decision.

## Exact primitive

### Decision observation

For one RCI decision unit, the recognizer receives only:

1. an event-local opaque alignment ID used to attach the eventual serialized decision; and
2. two contiguous streams of strictly increasing timestamps, each frame an unordered finite
   set of two-dimensional points:
   - `C`, the explicitly requested rest-capture stream; and
   - `O`, the online stream beginning only after `LOCKED_REST`.

The decision path excludes class, expected output, null/OOD status, nuisance name, truth,
split, session/user identity, cue, palm label, anatomical label, stable writer, contact
lifetime, array order, source slot, TID, TID magnitude, and device identity. Pressure,
ellipse/contact major, tool type, and language context are also excluded from this first
primitive. A point order used only to make floating-point accumulation deterministic is not
retained and carries no semantics.

No RCI decision may be serialized from truth, labels, split metadata, or nuisance metadata.
For every recognizer and control, the candidate, confidence, and acceptance bit must be
serialized **before** the harness joins truth for scoring.

### Explicit pooled empirical rest measure

`REST_CAPTURE` accepts only a contiguous, valid capture of at least 30 frames spanning at
least `1.0 s`, with 2–12 points per frame and adjacent gaps from `0.1` through `50 ms`.
Chronologically split the accepted capture into its first two thirds, `C_A`, and final
third, `C_B`. Pool every coordinate occurrence from `C_A` into the empirical set-rest
measure

\[
\mu_R = \frac{1}{m}\sum_{i=1}^{m}\delta_{r_i},
\qquad r_i=(x_i,y_i),\quad (r_i)\in C_A.
\]

A coordinate repeated in many frames remains many empirical mass occurrences. It is never
a neutral point for finger 0, contact 1, slot 1, or a selected writer. RCI has no per-contact
baseline, neutral-point list, sliding baseline, EWMA, recent-frame baseline, or online
update.

For the empirical energy distance between set measures,

\[
D_E(\mu,\nu)=
2\mathbb{E}\|X-Y\|
-\mathbb{E}\|X-X'\|
-\mathbb{E}\|Y-Y'\|,
\]

where \(X,X'\) are independent draws from \(\mu\), \(Y,Y'\) are independent draws from
\(\nu\), and the two expectations use independent cross-measure draws. Compute the immutable
robust rest location and scale from the final capture third:

\[
b=\operatorname{median}_{i\in C_B}D_E(\mu_{C_i},\mu_R),
\]

\[
s=\max\left(1.4826\,\operatorname{MAD}_{i\in C_B}
D_E(\mu_{C_i},\mu_R),10^{-12}\right).
\]

The empirical pairwise self-term of \(\mu_R\) may be cached once. No cross-frame nearest
neighbor, assignment, match, or correspondence is computed or retained.

Let \(d_i=D_E(\mu_{C_i},\mu_R)\) in capture order. Reject rest acquisition if either
\(\operatorname{median}_{C_B}d-\operatorname{median}_{C_A}d>3s\), or the ordinary
least-squares slope of \(d_i\) against elapsed capture time multiplied by capture duration
is greater than \(3s\). This exact directed-drift rule is evaluated before `LOCKED_REST`.
A slow incipient excursion, event, palm placement, or non-idle transition therefore causes
recapture or rejection, not a poisoned rest lock.

### Scalar innovation curve

Let \(\mu_{O_t}\) be the empirical measure of online frame \(O_t\). The frame innovation is

\[
z_t=\operatorname{clip}\left(
\frac{D_E(\mu_{O_t},\mu_R)-b}{s},0,8\right).
\]

The scalar curve is the only temporal observation of change. It is recomputed from the
current set and the locked rest measure; it is not a point trajectory or a flow field.
Rest drift, the current event, a palm, an aborted candidate, a slow gesture, and an
uncertain frame never mutate \(\mu_R\), \(b\), or \(s\).

The bounded event record uses the following frozen fields: peak `z`; area under `z` divided
by observed frame count; rise duration as a fraction and bounded frame count of candidate
duration; hold fraction above the calibration-selected entry level; return duration as a
fraction and bounded frame count; local-maximum count; final innovation residual;
integrated residual after first peak; peak-to-final residual ratio; and a binary
bounded-return-complete flag. Absolute coordinates, point identities, contacts, labels, and
unbounded timing traces are not features or retained output.

The first classifier is a nearest-centroid classifier over train-fitted class centroids.
Standard scaling uses every allowed training exemplar. Training uses every permitted
exemplar, never one prototype per class. A future manifest may replace the classifier only
by a new decision; it may not change it after test inspection.

### Exact state machine

```text
DISCONNECTED
  -> REST_CAPTURE
  -> LOCKED_REST
  -> ARMED
  -> TENTATIVE
  -> SETTLING
  -> SETTLED
  -> EMIT once or ABSTAIN
  -> REQUIRES_FRESH_REST_CAPTURE

Malformed input, add/drop, gap, burst, duplicate, restart, reconnect,
sleep/wake, stale/new epoch, or non-idle transition:
  -> QUARANTINED
  -> NACK/RESET visibility
  -> REQUIRES_FRESH_REST_CAPTURE
```

- **`REST_CAPTURE`:** explicit acquisition only. No class/null/palm cue requests it. Enforce
  capture duration, frame gap, cardinality, finiteness, duplicate-point, contiguity, and
  directed-drift rules. Emit nothing.
- **`LOCKED_REST`:** atomically freeze \(\mu_R,b,s\), clear candidate buffers, and re-arm only
  a new lifecycle. Erase the rest measure on disconnect or reset; no durable resume exists.
- **`ARMED`:** require every online frame to have the locked cardinality. Count is a validity
  invariant, never a class feature. Entry level is the calibration-selected value frozen in
  the manifest.
- **`TENTATIVE`:** accumulate only the bounded scalar curve and fixed event record. A peak,
  final distance, single coherent fragment, or event update never commits.
- **`SETTLING`:** require \(D_E(\mu_{O_t},\mu_R)\le b+3s\) for 8 consecutive valid frames,
  with no gap above `50 ms`. Candidate duration is at most `1.5 s`; expiry causes visible
  abstention/reset, not a rest update or extended wait.
- **`SETTLED`:** serialize the decision before truth join. Emit at most one semantic attempt;
  otherwise abstain. Confidence, return quality, or structural invalidity may cause
  abstention, but truth may not.
- **Terminal/quarantine:** every emit, abstain, or quarantine requires a fresh explicit rest
  capture. No tentative state crosses a timestamp gap, malformed or saturated burst,
  duplicate, add/drop, sleep/wake, reconnect, stale/new epoch, profile/layout change, or
  identity-irrelevant configuration transition.

The locked cardinality is unchanged online. Supported capture cardinality is 2–12, but the
first primary task uses matched strata 3, 4, 6, and 8 with identical class distributions.
A palm already present during valid explicit capture may be included in the local rest
measure; that is not a software palm/anatomy claim. Palm add/remove/reposition after lock
must not commit.

The exact serialized semantic decision contains only the opaque alignment ID, candidate,
confidence, and acceptance bit. Any structural refusal remains visible through closed reason
codes and NACK/reset, without coordinates, timing traces, cardinality histories, or identity
data. This design does not claim exactly-once delivery across process restart.

## Independent generator families

Train, calibration, and test use separately implemented generator families. They may share
only observation validation, decision serialization, scoring, and session-cluster bootstrap
infrastructure—not base-field, rest, event-law, nuisance, prototype, or descriptor
generation code. Public class names and semantic roles may be shared; implementation and
constants may not. No split may copy a prototype or call another split's generator.

The first fixture has three balanced synthetic classes and chance accuracy \(1/3\). Class
roles describe distinct bounded scalar excursion programs, not steno, anatomy, intent, or
product outcomes.

1. **Train — `harmonic_ring_excursion_A`:** independently randomized nonconvex harmonic-ring
   rest fields. Train class laws are independently implemented eased single excursion,
   clipped shoulder excursion, and two-peak excursion. Nuisances are class-independent
   jitter, per-frame point-order randomization, translation, proper rotation, and positive
   whole-set scale.
2. **Calibration — `mixture_cloud_transition_B`:** independently generated, rejection-separated
   two-component point mixtures, not polygons and not train fields. The same three class
   roles use different laws: asymmetric logistic rise/decay, piecewise-linear
   ramp/hold/return, and clipped damped oscillation. This family is consumed only to select
   entry and acceptance parameters.
3. **Test — `sequential_gap_motion_C`:** independently generated points by sequential
   placement in randomized convex hulls, with irregular interiors and nonuniform gaps. The
   three roles use independently implemented piecewise-polynomial controls,
   two-piece exponential controls, and asymmetric spline return. It calls neither train nor
   calibration generation code.

Every family supplies its own rest capture, all nuisance strata, nulls, and lifecycle attacks.
The exact seeds, class-conditional laws, nuisance levels, and session counts must be frozen
canonically in the manifest before test results are inspected. The first fixture is 8 train
sessions, 4 calibration sessions, and 6 untouched test sessions, with every class balanced
within each session. All permitted training exemplars contribute to scaling and centroid
fitting. Calibration alone selects the tentative entry level and candidate acceptance
threshold. It does not select the feature definition, robust \(b/s\) policy, return band,
window, cardinality rules, generator composition, classifier family, or gates. Any test
selection sets `test_used_for_selection=false`; otherwise the run is void.

## Matched count, nuisance, null, and attack bank

### Count and nuisance matching

Positive, core-null, and nuisance strata use the same predeclared cardinality mixture
3/4/6/8 for every class, including parity and palm-at-rest strata. Per-frame counts are equal
online to locked count. Count-only is a control and lifecycle validity check, never an RCI
feature. A count-only classifier must remain within `0.05` of chance, and no class may
associate with cardinality, parity, base-field family, or nuisance stratum.

For each class and nuisance seed, positives and core nulls match, where structurally possible,
cardinality, point jitter, rest residual, peak energy discrepancy, area under the scalar
curve, centroid path length, and rigid-motion magnitude. Matched positive and null duration
distributions overlap. A dedicated `slow_positive` stratum completes in `0.60–0.90 s`; a
dedicated `slow_null` has matched peak, area, path, and duration but does not return. A
`speed_duration_only` control must remain at or near chance.

The nuisance matrix includes independent jitter and settling; whole-set translation, proper
rotation/reflection policy, positive scale, and slow re-centering; point-order randomization;
rest drift; palm present at capture and palm add/remove/reposition after lock; add/drop;
incomplete and open-set scalar programs; and class-independent rest-lock quality strata.
Class-conditional balance is audited for every nuisance seed.

### Null and structural attack bank

The independently generated null/attack bank includes:

- locked-rest jitter, slow jitter, and slow nonreturning drift;
- rapid rigid motion and slow recentering at matched magnitudes;
- palm-at-rest and palm-placement nulls, with centroid and edge insertion/removal variants;
- aborted/incomplete excursions and open-set scalar programs;
- added/dropped points and changed locked cardinality;
- duplicate whole frames and repeated streams;
- bursts of 1, 2, 5, 20, and 100 frames;
- gaps of 50, 100, 250, and 660 ms;
- empty, singleton, duplicate-coordinate, nonfinite, over-limit, and malformed frames;
- reverse/nonmonotonic timestamp attacks;
- sleep/wake, reconnect, stale epoch, new epoch, duplicate stream, and replay;
- late-start slow motion at the capture/online boundary that would poison an adaptive
  baseline;
- profile/layout/configuration transitions.

A valid null decision is not forced by `expected_output`, a null flag, or nuisance metadata.
Attack cases may have a different required rejection shape, but no case may reveal that
required shape to the recognizer.

## Controls

Every learned control receives the same observation boundary, rest lifecycle, train family,
all allowed train exemplars, calibration family, calibration-only entry/acceptance
selection, test family, null bank, and clustered scorer. Mandatory controls are:

1. `count_only`;
2. `locked_rest_centroid_path` — centroid displacement, path, and return;
3. `rigid_similarity_motion` — centroid, covariance change, proper rotation, and scale;
4. `instantaneous_shape` — first/current permutation-invariant set shape;
5. `current_contact_field` — the rejected current implementation, used only as a control;
6. `energy_peak` — maximum \(D_E(\mu_{O_t},\mu_R)\) only;
7. `energy_peak_area` — peak and area only;
8. `speed_duration_only` — peak/path speed and duration only;
9. `no_return_energy_curve` — RCI scalar curve with return/lifecycle information removed;
10. `mismatched_locked_rest` — a label-independent wrong locked rest measure, to test whether
    the immutable correct rest carries evidence.

Integrity controls are `always_positive` (must fail the null gate), `shuffled_label` (must
remain at chance), independent per-frame point-order permutations, and randomized
slot/TID reassignment. The mismatch permutation must not change descriptor, model input,
state, semantic decision, acceptance bit, event count, serialized closed reason, event-ID
behavior, or timing outcome.

RCI must beat every predeclared learned control; a best-control choice made after test is
forbidden. SOS is not implemented as a control or second branch. A fixed occupancy-difference
summary may be a declared nuisance control only if it is not the SOS branch and does not
replace the mandatory temporal/static controls.

## Metrics and uncertainty

The frozen report must include joint positive correct rate with abstention counted as
failure; macro recall and per-class recall; conditional accepted-event error; coverage;
overall and family-specific null false-commit rate; wrong-commit rate; semantic event-count
distribution; slow-positive, slow-null, palm-at-rest, palm-placement, rest-drift, rigid-motion,
and malformed/attack strata; count-only chance recovery; every RCI-minus-control macro-recall
margin; and all structural/privacy outcomes.

Primary uncertainty is a deterministic paired session-cluster bootstrap with 4096
replicates and a manifest-frozen seed. Resample whole synthetic sessions, never individual
frames or events. Report one-sided 95% session-clustered lower bounds for recall and margins,
and upper bounds for false commits and accepted-event error. The number of test session
clusters remains an explicit synthetic limitation; bootstrap replicates do not broaden the
population claim.

## Hard vetoes

Any one failure is non-compensable and forces `claim=none`:

1. **Decision isolation:** any label, expected output, null/OOD flag, nuisance metadata,
   split, session/user identity, cue, or test information crosses the decision path.
2. **Independent splits:** any split shares a generator function, prototype, base field,
   rest template, event-law implementation, or descriptor exemplar.
3. **Proper split use:** training omits any allowed exemplar; calibration does not actually
   select entry/acceptance parameters; or test affects any parameter, model, threshold, or
   gate.
4. **Count leakage:** count, parity, or generator family predicts class; count-only exceeds
   `0.40` positive accuracy; or null/positive cardinality distributions are unmatched where
   matching is required.
5. **Forced null rejection:** a recognizer receives truth-derived abstention, rest, or event
   state; `always_positive` does not visibly fail nulls.
6. **Identity leakage:** slot, TID, array order as semantics, stable correspondence, selected
   contact/writer, contact lifetime, anatomy, or identity proxy enters features, state,
   baselines, matching, event IDs, logs, errors, or retained data.
7. **Forbidden TSF flow:** RCI uses adjacent matching, per-contact baselines, rigid/non-rigid
   residual flow, or any TSF residual/feature path.
8. **Mutable or poisoned rest:** \(\mu_R,b,s\) changes after lock; a candidate/null/palm/
   slow/unknown frame updates rest; a directed-drift capture locks; or a fresh capture edits
   rather than replaces the lifecycle model.
9. **Lifecycle breach:** tentative state bridges a gap, burst, malformed/saturated frame,
   add/drop, duplicate, restart, sleep/wake, reconnect, epoch, or configuration transition.
10. **False commit:** any valid rest, slow drift, palm-placement, open-set, burst, gap,
    duplicate, replay, stale-epoch, reconnect, or malformed case produces an accepted
    semantic attempt. Duplicate/replayed input produces a second semantic effect.
11. **Comparator shortcut:** speed, duration, rigid motion, shape, energy peak/area, count, or
    return removal explains the class; integrity controls or matched nuisance gates fail.
12. **Privacy crossing:** raw coordinates, rest measure, timestamp trace, scalar curve,
    learned model, confidence model, or rest parameters enter ordinary telemetry, semantic
    output, errors, or durable cross-restart state.
13. **Language rescue:** language-model plausibility or lexical prior converts an invalid,
    stale, null-contaminated, or physically ambiguous observation into a commit.
14. **Evidence laundering:** any recognition, comparative, nuisance, structural, or privacy
    gate fails; or threshold/window/generator/gate relaxation after test is proposed.

## Exact `RCI-SYNTHETIC-FALSIFIER-1` gates

Before inspecting RCI test results, freeze version 1 of `RCI-SYNTHETIC-FALSIFIER-1` with
the exact observation exclusions; energy-distance, robust \(b/s\), fixed record, classifier,
lifecycle, cardinality, capture, drift, window, return/settle, and state constants; the
three independent generator implementations; 8/4/6 session sizes; the complete
count/nuisance/null/attack bank; every control and integrity attack; calibration-only
entry/acceptance selection; `test_used_for_selection=false`; bootstrap seed and 4096
replicates; all gates below; and the rule that failure of any gate yields `claim=none`.

All gates are required; none compensates for another.

### Recognition, null, and count gates

1. Joint positive correct rate, counting abstention as failure, is at least `0.90`.
2. Macro-recall one-sided 95% session-clustered lower bound is at least `0.85`.
3. Conditional accepted-event error one-sided 95% session-clustered upper bound is at most
   `0.01`.
4. Overall valid-null false-commit one-sided 95% session-clustered upper bound is at most
   `0.01`.
5. Exactly one semantic attempt is serialized for each structurally valid positive and zero
   for every structurally valid core null; quarantine/NACK is visible and non-emitting.
6. `count_only` positive accuracy is at most `0.40`, and count/parity/family balance audits
   pass.

### Comparative and nuisance gates

7. RCI exceeds **each** declared learned control by at least `0.10` observed macro recall.
8. The paired session-clustered one-sided 95% lower bound of RCI minus **each** learned
   control is greater than `0.0`.
9. Every declared nuisance stratum has at least `0.90` joint recall and remains above its
   matched nuisance-only control.
10. `slow_positive` has at least `0.90` macro recall; `slow_null`, rest-drift, and
    palm-placement nulls have exactly zero accepted commits in the frozen run.
11. `speed_duration_only` positive accuracy is at most `0.40`.
12. `always_positive` fails the null gate, `shuffled_label` is at chance, and point-order and
    randomized slot/TID attacks leave every semantic and structural result invariant.

### Structural, identity, and privacy gates

13. Locked \(\mu_R,b,s\) are exactly structurally equal before and after every online
    candidate, rejection, palm, slow case, duplicate, gap, restart, reconnect, and epoch
    attack; source audit finds no update path.
14. No semantic decision is possible before `LOCKED_REST`, and a directed-drift rest capture
    cannot lock.
15. No tentative state crosses a gap, burst, malformed frame, add/drop, duplicate,
    sleep/wake, restart, reconnect, stale/new epoch, or profile/configuration transition.
16. Repeated frames or streams never create a second semantic attempt, and replay never
    reaches the consumer boundary as live.
17. Point order, slot, TID, session/user label, and contact lifetime changes affect no
    descriptor, state transition, decision, count, event ID, log, or error.
18. No raw coordinate, rest measure, timestamp trace, scalar feature, confidence model,
    learned parameter, or rest state crosses the strict semantic boundary, enters ordinary
    telemetry, or survives reset/disconnect for durable resume.
19. No language model or lexical plausibility participates in a decision.
20. Every manifest, generator, data, control, attack, metric, and selection audit passes;
    mutation refusal and source-level no-slot/TID/no-TSF-flow checks are present.

Failure of any gate kills this frozen RCI branch. It is not repaired by test-time threshold
relaxation, a new split, replacement generator, longer window, learned rest update, or a
rename into TSF or SOS.

## Design-only resource boundary and evidence limit

These are future implementation constraints, not measurements: rest capture at most `2.0 s`,
120 frames, and 12 points/frame; online candidate at most `1.5 s` and 150 frames; settle for
8 consecutive valid frames; fixed working state \(O(|R|+F)\) with \(F\le150\); cached rest
self-energy computed once; and no per-contact history. Any future implementation must
measure and report compute separately. No compute result may be described as human latency,
ergonomics, WPM, or product performance.

A synthetic pass would establish only that this exact fixture contains the predeclared
signal under this implementation. It would require a fresh decision before any separately
consented hardware falsifier. It would not establish hardware palm safety, anatomy, fatigue,
human intent, WPM, correction throughput, text accuracy, privacy by retention, integration,
or product readiness. No RCI performance is claimed now.
