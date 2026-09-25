# Offline Branch Red-Team Decision

**Decision date:** 2026-09-25  
**Evidence boundary:** the earlier static comparison is superseded by the completed frozen `SYNTH-BRANCH-1` synthetic run. This remains offline synthetic evidence only; no hardware replay, human session, WPM, correction, text-accuracy, or external integration evidence was produced.
**Decision:** reject Contact Field as the current primary representation; retain Elastic Word as a synthetic control/fallback; keep FCPT arithmetic-only with its selectable-thumb primitive rejected. No branch is promoted to product.

## 1. Decision and hard vetoes

1. **Contact Field — rejected as the current primary representation (`nextgen/contact_field.py`).** The frozen synthetic run clears basic discriminability but fails wrong-commit, conditional accepted-event error, and nuisance-retention requirements. It is not a product candidate and requires redesign or an explicit hold decision.
2. **Elastic Word — synthetic control/fallback only (`nextgen/elastic_word.py`).** It passes the frozen recognition comparator, but remains non-end-to-end because anonymous-contact segmentation and path construction are absent.
3. **FCPT — reject current primitive; hold arithmetic only (`nextgen/fcpt.py`).** The run has 27 modeled-cost settings and no recognition metrics. Modeled cost is not accuracy, and the stable selected-thumb primitive remains rejected.

The earlier static weighted comparison is retained below as historical design context, not as the current branch decision. The completed frozen result is recorded in `SYNTH_BRANCH_1_RESULTS.md`.

The hard vetoes are non-compensable:

- A branch requiring stable single-contact attribution cannot advance because of implementation quality or a favorable score. For the recorded capture/device-as-used condition, the FCPT replay contract produced 0 key events and 24 `ambiguous_attribution` NACKs. This rejects the current FCPT primitive; it does not prove that every future capture arrangement is impossible.
- Elastic Word cannot become end-to-end while an anonymous contact field cannot be segmented into a defensible single continuous writer path. Its template comparator is not that constructor.
- No offline score, synthetic pass, or comparator operation may be cited as evidence of hardware observability, human WPM, fatigue behavior, error/correction throughput, or end-to-end text accuracy.
- A branch cannot advance if its event identity, event timing, false-commit behavior, or correction lifecycle is undefined. Abstention is not a safe recognizer without a calibrated wrong-or-abstain boundary.
- The weighted score orders research only. It cannot compensate a hard veto or convert an `IMPLEMENTED` utility into `MEASURED` or `HUMAN` evidence.

## 2. Exact weighted comparison

Ratings are 0–10 research-priority judgments grounded in the implemented artifact and repository evidence, not product or human-performance scores. The weighted total is the sum of `weight × rating / 10`.

| Criterion | Weight | Contact Field | Elastic Word | FCPT | Decision rationale |
|---|---:|---:|---:|---:|---|
| Observability | 25 | **8** | 3 | 1 | Contact descriptors never consume order, tracking identity, or finger labels. Elastic consumes an ordered path it cannot derive from anonymous contacts. FCPT's current primitive requires stable selected-contact attribution. |
| Anatomy | 15 | **5** | 6 | 2 | Whole-field geometry is at least aligned with anonymous input but physically unvalidated. A familiar writing articulation may be easier to learn, but execution on this input and its correction behavior are unknown. FCPT reach and targetability are unvalidated. |
| Information / grammar value | 15 | **4** | 6 | 7 | Elastic can map paths to word-like events; FCPT explicitly weights symbol transitions. Contact has rich geometry but no semantic mapping or demonstrated grammar advantage. |
| Timing / correction | 15 | **3** | 4 | 4 | None has a complete event lifecycle. Contact has only a shape score; Elastic has thresholded comparison but no segmentation/repair; FCPT models nominal movement arithmetic but no observed recognition or correction path. |
| Learnability | 10 | **3** | 7 | 3 | Handwriting has a familiar motor skill, though eyes-free reliability is unknown. Arbitrary field and target-grid bindings have no demonstrated learnability. |
| Implementation | 10 | **7** | 8 | 9 | FCPT has the strongest deterministic arithmetic path. Elastic is bounded and simple. Contact lacks a maximum cardinality; its triangle and flattened feature paths grow as O(n³). |
| Privacy | 5 | **10** | 9 | 10 | None performs I/O or telemetry. All retain or may expose sensitive geometry if a caller persists, logs, or links it. A module's lack of I/O is not a full retention or consent guarantee. |
| Testability | 10 | **8** | 8 | 9 | Each has focused synthetic unit tests and no runtime coupling. FCPT has the strongest arithmetic coverage. None tests the decisive segmentation, recognition, false-commit, correction, or cross-session question. |
| **Weighted total** | **100** | **61.0** | **59.0** | **48.0** | Contact narrowly leads because observability has 25% weight. This is research priority, not validation. |

Arithmetic: Contact Field `200+75+60+45+30+70+50+80 = 610/10 = 61.0`; Elastic Word `75+90+90+60+70+80+45+80 = 590/10 = 59.0`; FCPT `25+30+105+60+30+90+50+90 = 480/10 = 48.0`.

## 3. Contact Field — rejected current representation

### Implemented capabilities

- Validates and copies finite two-dimensional contact coordinates without reading tracking identity or input order.
- Normalizes translation and positive uniform scale.
- Builds explicit cardinality, sorted centroid radii, sorted normalized pairwise distances, and triangle summaries.
- The descriptor's sorted distance summaries are invariant to contact permutation and planar rotation/reflection for ordinary finite inputs.
- Provides a symmetric directed-Hausdorff shape-similarity score over two independently normalized fields.

### Missing layers

- No maximum cardinality or fixed-dimensional cross-cardinality model; public feature length varies with count and triangle generation/storage is O(n³).
- No temporal input, frame rate, onset/lift, duration, velocity, persistence, or continuity gate.
- No palm/resting/tool/phantom/contact-quality filter; the API consumes only XY and ignores available device metadata.
- No classifier, lexicon/grammar mapping, learned class inventory, open-set/no-word decision, runner-up margin, or confidence calibration.
- No event emission, NACK, correction, undo/retract, or end-to-end text boundary.
- No resource limit, direct-descriptor invariant validation, robust extreme-scale normalization, or a privacy-safe derived-data boundary.

### Privacy, anatomy, and timing risks

- Stable high-precision normalized geometry can be linked or reconstructed as biometric-like hand posture. “Identity-free” means IDs are not read; it does not mean unlinkable or anonymous.
- Anonymous planar fields cannot identify the intended thumb or recover contact correspondence, mover/follower order, handedness, or out-of-plane twist/hollow cues.
- A palm, sleeve, reader-init phantom, split/merged contact, or added resting point changes the centroid, RMS scale, and entire descriptor. Equal weighting can either let palm contamination dominate or dilute a small active-finger change.
- The current “motion” score is shape similarity: translation and scale are erased, independent rotation is inconsistent, and a fixed deformation has the same score at 1 ms or 500 ms. It cannot support a timing or literal motion claim.
- Invalid, malformed, empty, or maximally dissimilar states can collapse to score zero; callers cannot diagnose rejection reason.

### Exact next kill tests

1. **Literal motion contract:** compare `A=[(0,0),(1,0)]` with the same shape at `x+100`; if translation is erased, require score `1.0` and rename/document the function as shape similarity, or require a strict decrease for a motion metric. Current output is `1.0` and fails a literal motion claim.
2. **Independent rotation nuisance:** compare `[(0,0),(2,0)]` with `[(0,0),(0,2)]`; if rotation is a nuisance, require score `1.0` consistently with the descriptor. Current output is `0.0`.
3. **Resource and dimension bound:** freeze a maximum observed count; reject `limit+1`, and assert current dimensions before any redesign (`n=10`: 416; `n=20`: 3,631). The current unbounded behavior kills any claim of computational boundedness.
4. **Invalid-state contract:** for empty, singleton, coincident, NaN, infinite, and malformed 3D input, require a typed invalid result or reasoned exception, never the same value as a valid severe mismatch. Current `ValueError` paths become `0.0`.
5. **Palm/phantom null replay:** replay measured reader initialization frames and add/remove a centroid palm point while leaving finger points fixed. Require both observations to be equal after a declared upstream gate or both rejected; current midpoint insertion changes a two-point field by about 22.5%.
6. **Timing oracle:** compress one deformation into 1 frame and spread it over 10, 50, and 500 frames. The current score should remain identical, demonstrating blindness; a timing-aware event must be implemented before throughput claims.
7. **Synthetic recognition gate `SYNTH-CF-1`:** on frozen held-out K=8 raw point fields, require macro recall at least 0.25 with one-sided 95% lower bound above 0.125 chance; full descriptor must exceed the best nuisance-only control by at least 0.10 macro recall with lower bound above zero; null/drift wrong commits must have upper 95% bound at most 0.01; at coverage at least 0.80, conditional accepted-event error must be at most 0.025; nuisance-stratum recall must retain at least 80% of clean recall and remain above chance. Kill the representation if discriminability or control-margin gates fail; hold for segmentation/calibration if only false-commit, coverage, or nuisance gates fail.
8. **Privacy linkability test:** transform one consented field by translation, rotation, and scale in a later session and compare descriptors. Exact stability demonstrates biometric-like linkability, not unlinkability. Any persistence remains blocked until consent, retention, access, and deletion rules are applied to derived data.

## 4. Elastic Word — control/fallback research branch

### Implemented capabilities

- Validates an already ordered finite XY trajectory and bounds input and output sample counts.
- Rejects wholly constant paths and immutable-copies accepted input.
- Resamples a polyline at equal cumulative arc length and normalizes translation plus positive uniform scale.
- Computes a bounded pointwise RMS dissimilarity and a per-template accept/abstain result with an explicit threshold.

### Missing layers

- No timestamps, contact identity, tracking continuity, writer selection, onset/lift, frame-gap guard, minimum usable-sample policy, or segmentation state machine.
- No dictionary, class ranking, runner-up margin, open-set/OOD policy, or calibrated confidence; `score = 1 - distance` is not a probability.
- No correction state, whole-word replacement, undo/retract, or measurement of repair time/events.
- No recorder adapter or anonymous-contact-to-writer-path constructor.
- The code default is 32 samples while the design record declares 40, creating a version ambiguity.

### Privacy, anatomy, and timing risks

- Two noisy points can become a full normalized trajectory; sample count after interpolation is not evidence quality. A tap, dither, or tracking jump can look like a word.
- A long frame gap is joined as one chord, and contacts with different identities can be stitched because the API has no temporal/contact metadata.
- The comparator sees anonymous centroids, not anatomical thumb paths; palm, flexion, rolling edge contact, and centroid jumps are unresolved.
- Pointwise progress after arc-length resampling is not temporally elastic. Pause, hesitation, backtracking, and local speed information are discarded; D4-like bounding-box normalization can also collapse intended handedness distinctions.
- Finite input can become non-finite during resampling: `[(0,0),(1e308,0)]` with three samples can overflow in `total_length * sample_index`.
- The pure module writes nothing, but cannot guarantee lift-off-only processing, raw-buffer disposal, or privacy-by-retention in an absent integration.

### Exact next kill tests

1. **Finite-output property:** use `[(0,0),(1e308,0)]`, subnormals, large offsets, plateaus, and alternating traces; every returned coordinate must be finite or invalid arithmetic must raise a documented early error. The mandatory seed currently exposes overflow.
2. **Event-quality gate:** reject or mark unusable a two-sample 0.56 mm jitter, resting noise plus one jitter sample, a valid word plus `[0,0]`, and a valid word plus a tracking jump. Current validation accepts the short nonconstant cases.
3. **Recorder replay:** inject measured initialization artifacts, contact-ID swap, two simultaneous movers, and a 660 ms gap. Require no cross-contact stitching and abstention on discontinuity. The current XY-only API cannot satisfy this contract.
4. **Transform-group declaration:** require invariance only for positive uniform scale plus translation; separately characterize arbitrary rotation, reflection, quarter-turn, anisotropic scale, shear, and curved nonuniform resampling. Collisions are acceptable only if the semantic policy explicitly accepts them.
5. **Synthetic recognition gate `SYNTH-EW-1`:** on frozen held-out K=8 path classes plus aborted/incomplete/null events, require macro recall at least 0.25 with one-sided 95% lower bound above 0.125; null/aborted wrong commits upper 95% bound at most 0.01; at coverage at least 0.80, conditional accepted-event error at most 0.025; dropout and pause/backtrack strata remain above chance; nuisance recall retains at least 80% of clean recall. Kill if discriminability fails; hold for segmentation/calibration if only safety gates fail.
6. **Open-set and ambiguity gate:** hold out 20% of classes and test genuine out-of-dictionary paths; require no accepted word unless an explicit open-set calibration clears a frozen false-commit bound. Test every template pair and require abstention on overlapping neighborhoods. A one-template threshold cannot satisfy this.
7. **End-to-end fallback prerequisite:** define and test an anonymous-contact-to-single-writer-path constructor, then version a one-repair policy. Until both exist, Elastic remains a control and not an operational fallback.
8. **Privacy lifecycle test:** instrument the complete integration, not the pure module, and require release of raw XY, timestamps, contact IDs, ellipse data, buffers, exceptions, and telemetry copies after lift-off; only approved emitted events and aggregate metrics may remain.

## 5. FCPT — reject current primitive, hold arithmetic only

### Implemented capabilities

- A fixed 24-cell, 6-by-4 model-space geometry.
- Explicitly assumption-only finite intercept, slope, and target-width parameters.
- Directed positive corpus weighting and deterministic Shannon-form movement arithmetic.
- Bounded exhaustive assignment for at most four symbols and deterministic partial-cost greedy assignment for larger tables.
- Layout and objective validation at the optimizer boundary, plus no device, network, or file I/O.

### Missing layers

- No stable selected-thumb/contact observability; the current primitive is hard-vetoed by the recorded 0-event/24-ambiguous replay condition.
- No anatomical penalty, handedness, posture, fatigue, confusion, reach, or per-user geometry despite the project's higher-level FCPT concept requiring an anatomy term.
- No observed coefficients, effective-width fit, recognition latency, dwell/lift, error, correction, overlap, or language compiler.
- The default greedy search ranks unnormalized activated partial sums, not the complete final objective. The constant intercept can affect the greedy result even though it cannot change a complete layout's relative objective.
- Public `CostObjective` invariants and extreme finite arithmetic are incomplete; corpus size and symbol-string length are unbounded.

### Privacy, anatomy, and timing risks

- Nominal center distance with a scalar 3 mm width is not a hit-region, diagonal-width, hand-shape, or fatigue model. The 24.6-by-18.2 mm envelope, pitch, and orientation are assumptions.
- The model omits the documented anatomy penalty and all confusions/corrections; a lower movement sum can increase wrong commits or repair time.
- The transition count is not time, error probability, or throughput. A nominal `1/mean_cost` is an arithmetic inversion, not human events per second.
- The module has no I/O, but corpus symbols and assignments can reveal language, phoneme inventory, or encoded text through default representations and caller logs.

### Exact next kill tests

1. **Intercept invariance:** for fixed directed 3–4 symbol corpora, compare intercepts 0 and 10 with the same slope. Complete-layout ranking must be unchanged; a different greedy result directly falsifies its final-objective interpretation.
2. **Greedy/exhaustive falsifier:** for fixed-seed directed weighted three-symbol corpora, compare greedy with exhaustive results. Report the first strict greedy cost gap; any strict gap falsifies an unqualified optimizer claim and requires replacement or disclosure.
3. **Exact small-table oracle:** exhaustive search must recover the known synthetic optimum for every generated 2–4 symbol case. Failure rejects the arithmetic optimizer hypothesis.
4. **24-symbol held-out layout gate:** on disjoint train/calibration/test transition corpora, the selected layout must beat row-major and the median seeded-random bijection by at least 5% held-out mean modeled cost in at least 24 of 27 parameter settings (`intercept {0.10,0.15,0.20}`, `slope {0.08,0.12,0.16}`, `width {2.5,3.0,3.5} mm`), with no setting more than 2% worse than row-major. Bootstrap symbol-placement overlap must be at least 0.75. Failure rejects or replaces the optimizer hypothesis.
5. **Anatomy-contract audit:** either implement and validate the claimed anatomy penalty or remove it from the branch contract. Offline arithmetic cannot validate anatomy.
6. **Real-device primitive test:** any revival requires a new identity-free event primitive and a consented anatomy/identity/false-commit study. Passing optimizer gates never revives the selected-thumb primitive.
7. **Human arithmetic fit test:** after observability is solved, fit the registered 60-move adjacent/diagonal study with residuals and confidence intervals and compare actual corrected events per second. Any nominal-layout win that loses after recognition errors and correction falsifies throughput claims.

## 6. Shared synthetic comparison protocol: `SYNTH-BRANCH-1`

This protocol compares research candidates under a common split and reporting envelope. It does **not** claim hardware validity.

### Freeze and split

- Before viewing results, freeze a manifest with code/data hashes, generator seeds, raw base shapes, classes/nulls, nuisance levels, split membership, templates/prototypes, thresholds, class chance, primary metrics, and rejection reasons.
- Use 20 training sessions, 5 calibration sessions, and 20 held-out test sessions, with 10 instances per class per test session. Split by generator/session, never by points from one generated event.
- Generate from raw geometry/control paths rather than from any prototype's feature vector. Training/calibration/test generator families must not overlap.
- Record one row per event: `task_kind, branch, split, seed, class_or_null, nuisance_level, raw_input, expected_output, candidate_output, score, threshold, accepted, elapsed_offline_time`.
- Treat an accepted wrong output as a **wrong commit**; count rejection separately. Report elapsed offline time as implementation cost only, never human latency.

### Recognition tasks

- **Contact Field:** begin with K=8 raw unordered point sets and explicit null/drift events. Vary cardinality, contact permutation, translation, uniform scale, planar rotation, coordinate noise, dropout/addition, and matched-cardinality matched-spread distractors. Compare the full descriptor with count-only, centroid/spread-only, and one-contact-deformation controls. If K=8 passes, run one frozen K=32 replication without retuning.
- **Elastic Word:** begin with K=8 control-point paths plus aborted, incomplete, and non-template nulls. Vary translation, scale, time reparameterization, sample density, coordinate noise, dropout, pause/backtracking, and distractors. Rotation is not declared a nuisance because orientation may be semantic. Calibrate only the acceptance threshold on the five calibration sessions.
- Use the same K, split, null volume, chance baseline, confidence reporting, and nuisance levels. The primary synthetic recognition metric is macro top-1 recall.

### FCPT task

- Use 24 symbols/cells with disjoint train, calibration, and test transition corpora generated from different seeded session distributions.
- Compare greedy FCPT, row-major, and 100 seeded random bijections on held-out modeled cost. Use exhaustive search only as an exact 2–4-symbol oracle.
- Evaluate the frozen layout over the 27-setting parameter grid above. Report held-out mean modeled cost, worst relative loss, and bootstrap placement stability. Do not report FCPT recognition accuracy because no recognizer exists.

### Common report and correction protocol

For recognition arms report macro recall, balanced accuracy, class-wise confusion, coverage, abstention rate, conditional accepted-event error, wrong-commit rate, null false-commit rate, nuisance-stratum results, and one-sided 95% confidence intervals. A branch is not end-to-end without a versioned correction policy. After that exists, inject one independently noisy wrong event and one branch-native repair; report recovery within one repair, extra accepted events, and abstention after failed repair. Until then, correction is `N/A`, not zero.

### Validity and stopping rules

A run is void—not a pass or fail—if the manifest changes after results are seen, generator families overlap, test data reaches training/calibration, nulls are omitted, chance is misreported, or FCPT modeled cost is compared as if it were recognition accuracy. A void run cannot advance or kill a branch; it requires a fresh frozen run.

- **Contact Field:** advance only if every `SYNTH-CF-1` gate passes. Kill/reject the current representation for failed discriminability or control margin; hold for failed segmentation/calibration safety gates.
- **Elastic Word:** advance only as control/fallback if every `SYNTH-EW-1` gate, recorder/segmentation contract, and one-repair test passes. It remains a control while the anonymous-contact path constructor is absent.
- **FCPT arithmetic:** retain only if the exhaustive, held-out 5% layout, 24/27 parameter-grid, and 0.75 bootstrap-stability gates pass. This does not revive the current primitive.

## 7. Evidence separation and next action

### Proven by the current offline implementations

- Contact Field can deterministically form ordinary synthetic normalized field summaries and a bounded shape score.
- Elastic Word can deterministically normalize an already ordered synthetic path and compare it to one selected template.
- FCPT can deterministically score and search fixed 24-cell assignments under explicitly provisional constants.

### Not proven by this review

- Any hardware observability, anatomical reach, palm/rest handling, tracking continuity, event timing, sensor recognition, WPM, text accuracy, fatigue, learnability, correction throughput, or privacy-by-retention.
- Any cross-session separability or open-set behavior; the legacy field-separability implementation is not the current `describe_field` implementation and its reported replay number is not transferable.
- Any runtime integration, English steno decode, dictionary behavior, Plover boundary, device access, or external-repository compatibility.

### Next executable action

Hold and redesign the Contact Field representation only if a new, explicitly authorized design is justified. Do not inflate the frozen synthetic result, retune thresholds to erase the failed safety/nuisance gates, or promote Elastic Word from its synthetic control status. Any future work must begin with a declared representation redesign and a fresh evidence boundary; no branch is currently promoted to product.
