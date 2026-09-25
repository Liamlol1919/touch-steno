# Record Consistency Audit

**Audit date:** 2026-09-25  
**Scope:** every Markdown document and every root text document, plus the Git history of commit `56fb218`. Root JSON manifests and dependency files are machine-readable/configuration artifacts rather than record documents. `nextgen/` and `tests/test_nextgen_boundary.py` were excluded.  
**Current state used as the comparison baseline:** 22 candidates generated, 0 validated, 0 surviving signals; the field null test observed class-mean `0.4583` against a `0.5685` null mean with one-sided `p = 0.9460` over 1,000 permutations, seed `20260925`, descriptor dimension 57, from 24 measured cued trials, 8 compass classes, 3 per class, one operator, one session, and `n=63` strokes; `field_gesture_probe.py`, `reshape_probe.py`, and `fitts_probe.py` have never run on hardware.

## Verdict

The record is **not internally consistent as a whole**.

There is a clear, well-cited current spine: `KILLED_BRANCHES.md`, the field-retraction sections of `ARCHIVE.md` and `BINDING_CONSTRAINT.md`, and `MEASURED_REJECTION.md` agree that the `0.4583` result is withdrawn and that no signal survives. Eight of the nine named retractions have a dated source that says what is withdrawn and on what basis. The 22.7% bimanual retraction does not meet that standard: its only retraction entry explicitly says that the sample, operator, session, and date cannot be recovered.

The inconsistency is mostly caused by historical documents continuing to be described as current, linked as authoritative, or omitted from the indexes. The most serious stale statements select and recommend concepts that later measurements killed, call a failed TSF prototype “not killed,” and make RCI the next executable direction even though the current record has no surviving signal and the next physical opportunity is the three never-run instruments plus the never-run control. There is also one real cross-document arithmetic mismatch around the 39% event overshoot, and a requested `2.585` modifier figure is absent while the documents consistently use `1.585`.

## 1. Root-document inventory and reachability

### Method and legend

Before this report was created, the root record set contained **77 Markdown documents and two root text documents**. This report is the new 78th root Markdown document and is necessarily absent from the pre-existing indexes. For archive coverage, `A` means that `ARCHIVE.md` contains a literal filename reference; a code-span mention counts because the archive uses code spans and table cells as its index. For README coverage, `R` means reachable by recursively following relative Markdown document links from `README.md`; `N` means not reachable. The new audit is excluded from its own reachability result. The archive does not reference itself, and README reachability includes `ARCHIVE.md` through `DESIGN_DECISION.md:30-31`.

No two pre-existing root documents are byte-for-byte duplicates: all 79 pre-existing hashes are distinct. No substantive duplicate was found. `ARCHIVE.md`, `DESIGN_DECISION.md`, `BINDING_CONSTRAINT.md`, and `KILLED_BRANCHES.md` overlap in governance, but have distinct roles: document-set index, compatibility index, synthesis/decision record, and branch-status register.

| Root document | One-line purpose | A | R |
|---|---|:---:|:---:|
| `AGENT2_RESEARCH_LOG.md` | Chronological Agent 2 build, correction, and measurement log. | Y | Y |
| `AGENTIC_META_PLAN.md` | Autonomous product-engineering operating plan and branch registry. | N | Y |
| `AGENTIC_STATE.md` | Append-oriented current implementation and evidence ledger. | N | Y |
| `ARCHIVE.md` | Index of current, superseded, and retracted record material. | N | Y |
| `BENCHMARK_RESULTS.md` | Synthetic benchmark results, retractions, and corrected detection envelope. | Y | Y |
| `BIMANUAL_ANALYSIS.md` | Offline raw-contact bimanual episode and coupling analysis contract. | Y | Y |
| `BINDING_CONSTRAINT.md` | Sprint synthesis, gate evidence, corrections, branch verdicts, and execution record. | Y | Y |
| `BRANCH_REDTEAM.md` | Offline adversarial audit of the frozen synthetic branch comparison. | N | N |
| `CANDIDATE_RANKING.md` | Confidence/language candidate-ranking seam without text commit. | N | Y |
| `CODE_REFERENCES.md` | Curated reusable source repositories and integration cautions. | Y | Y |
| `COMPASS_SURFACE.md` | Modeled radius/accuracy/cycle design surface conditioned on measured inputs. | Y | N |
| `COMPREHENSIVE_RESEARCH_REPORT.md` | Broad HCI, hardware, ergonomics, and architecture literature report. | Y | Y |
| `CORRECTION_THROUGHPUT.md` | Human stopwatch protocol for measuring repair time. | Y | Y |
| `CROSS_VALIDATION.md` | Literature-to-project-measurement comparison and synthesis. | Y | Y |
| `CUED_SESSION_PROTOCOLS.md` | Hardware cued-session blocks, outputs, and decision gates. | Y | Y |
| `DECISION_HOLEMASK_VS_SOFTWARE.md` | Decision favoring software coupling suppression over a physical mask. | Y | N |
| `DECODER_DESIGN.md` | Reversible contact-to-stroke decoder and state-machine design. | Y | Y |
| `DESIGN_DECISION.md` | Compatibility index directing readers to current design records. | Y | Y |
| `DESIGN_DECISION_FINAL.md` | Historical three-finalist comparison and build decision. | Y | Y |
| `EXPERIMENT_PROTOCOL.md` | Reproducible device capture, threshold, and ergonomic protocol. | Y | Y |
| `FIVE_HOURS_REPORT.md` | Same-day accounting of work, retractions, gaps, and session failures. | Y | N |
| `INTEGRATION_CONTRACT_V1.md` | Frozen process-local English steno event contract. | Y | Y |
| `INTEGRATION_TARGETS.md` | Cross-repository ownership and evidence boundaries. | Y | Y |
| `KILLED_BRANCHES.md` | Consolidated branch kill/hold register and nine retractions. | N | N |
| `LANGUAGE_CAPTURE_RUNBOOK.md` | Operator consent, capture, validation, retention, and deletion runbook. | Y | Y |
| `LANGUAGE_CORPUS_MANIFEST.md` | Held-out corpus privacy, split, hash, and retention contract. | Y | Y |
| `LANGUAGE_LAYER_METRICS.md` | Privacy-minimized local language-layer event counters. | Y | Y |
| `LAYOUT_ASSIGNMENT.md` | Synthetic calibrated confusion-matrix layout assignment experiment. | Y | N |
| `LEXICON_DECODING.md` | Lexicon-constrained candidate decoding boundary. | Y | Y |
| `LEXICON_RECOVERY.md` | Correctly conditioned synthetic top-3 lexicon reachability benchmark. | Y | Y |
| `LM_RECOVERY.md` | Historical language-recovery experiment and its explicit retraction. | Y | N |
| `LOOP.md` | Two-agent GitHub coordination operating instructions. | N | N |
| `MEASURED_BIOMECHANICS.md` | PTH-660 timing, rest, motion, and coupling measurements. | Y | Y |
| `MEASURED_INTENT_FILTER.md` | Intent detector replay over the three real sessions. | Y | Y |
| `MEASURED_REJECTION.md` | Real-capture contract rejection and field-null measurement record. | N | N |
| `NOVELTY_STATEMENT.md` | Prior-art/novelty boundary for project measurements. | Y | N |
| `PLOVER_BRIEFS.md` | Layered dictionary outline/translation validation boundary. | Y | Y |
| `POST_FAILURE_BRANCH_DECISION.md` | Historical post-failure selection of RCI and holds on other branches. | N | N |
| `PRIVACY_TELEMETRY.md` | Opt-in aggregate-only telemetry export contract. | Y | Y |
| `RAW_FRAME_SCHEMA.md` | Versioned raw contact-frame JSONL schema. | Y | Y |
| `RCI_FALSIFIER_DECISION.md` | Frozen RCI design-only primitive and proposed falsifier contract. | N | N |
| `README.md` | Repository entry point and deliverable index. | N | Y |
| `REAL_DATA_DECODE.md` | First replay of the closed decoder pipeline on three real sessions. | Y | N |
| `RECOMMENDED_ARCHITECTURES.md` | Architecture options and conditional implementation roadmap. | Y | Y |
| `RESEARCH_LOG.md` | Chronological Agent 1 work and correction log. | Y | Y |
| `REST_MODEL.md` | Sliding-baseline rest model measured on recorded sessions. | Y | N |
| `SCIENTIFIC_COMPARATOR_TEST0_RESULTS.md` | Frozen synthetic comparator-integrity result. | N | N |
| `SEPARATION_MODEL.md` | Detector/coupling separation rules checked against recordings. | Y | N |
| `SYNTHETIC_BASELINE.md` | Deterministic pre-hardware synthetic intent sanity check. | Y | Y |
| `SYNTH_BRANCH_1_RESULTS.md` | Frozen, audited synthetic branch-comparison outputs. | N | N |
| `SYSTEMKOMPENDIUM.md` | Historical full-system walkthrough, partly in German. | Y | N |
| `SYSTEM_COMPARISON_MATRIX.md` | Cross-system literature comparison. | N | Y |
| `TRAINING_PATH.md` | Evidence-gated training and evaluation progression. | Y | Y |
| `TSF_FALSIFIER_RESULTS.md` | Frozen synthetic TSF falsifier failure. | N | N |
| `VECTOR_DESIGN_CRITIQUE.md` | Measurement-backed critique of the 4-finger/16-zone proposal. | Y | N |
| `VERTICAL_SLICE.md` | Preserved specification and kill record for the field-set concept. | Y | N |
| `W1_ACADEMIC_ENSLAVEMENT.md` | Sourced academic finger-enslavement literature review. | N | N |
| `W2_STENO_HARDWARE.md` | Sourced stenography/chording hardware numbers. | N | N |
| `W3_OPEN_SOURCE.md` | Verified open-source component and license inventory. | N | N |
| `W4_ZERO_FORCE_ALGORITHMS.md` | Sourced zero-force input and intent-detection literature. | N | N |
| `W5_POINTING_MOTOR_LIMITS.md` | Sourced pointing and motor-control limits. | N | N |
| `W6_THUMB_BIMANUAL_VIABILITY.md` | Sourced thumb-direction and bimanual viability review. | N | N |
| `W7_PHYSICAL_MASKS_HAND_ERGONOMICS.md` | Sourced physical-mask and hand-ergonomics review. | N | N |
| `W8_LAYOUT_VECTOR_DECODING.md` | Sourced layout, vector decoding, and chord-disambiguation review. | N | N |
| `W9_STENO_LANGUAGE_LAYER.md` | Sourced language-layer and dictionary review. | N | N |
| `W10_STENO_ON_TOUCH.md` | Sourced machine-stenography-on-touch literature review. | Y | N |
| `W11_VERIFY_KEYLESS_CEILING.md` | Historical keyless/touch ceiling literature check. | Y | N |
| `W12_DRIFT_AND_ENSLAVEMENT_PRIOR_ART.md` | Prior-art search for drift and finger-coupling evidence. | N | N |
| `W13_GESTURE_SEGMENTATION_NOLIFT.md` | Prior-art search for gesture segmentation without lift-off. | N | N |
| `W14_DIRECTION_ACCURACY_ROOTCAUSE.md` | Simulation-led diagnosis of direction-error mechanisms. | Y | N |
| `W16_LAYOUT_OPTIMISATION.md` | Prior-art review of layout optimization methods. | N | N |
| `W17_FEEDBACK_AND_HAPTICS.md` | Prior-art review of feedback and sensory substitution. | N | N |
| `W18_BIMANUAL_AND_DRIFT.md` | External bimanual, drift, fatigue, and support evidence review. | N | N |
| `W19_CORRECTION_LATENCY.md` | Literature search for correction-latency evidence. | N | N |
| `W20_THUMB_REACH.md` | Sourced thumb reach and comfort evidence. | N | N |
| `W22_CORRECTION_TIME.md` | Literature search for seconds-per-correction evidence. | N | N |
| `models_confusion_analysis.md` | Folded/unfolded analysis of the real compass capture. | N | N |
| `RESEARCH_STARTED_AT.txt` | Timestamp recording research start. | N | N |
| `requirements-plot.txt` | Optional plotting dependencies for the model-figure script. | N | N |

### Documents referenced by neither index

The following **27 pre-existing Markdown documents and two pre-existing text documents** are neither literally referenced by `ARCHIVE.md` nor reachable recursively from `README.md` (this new report adds a 28th unindexed Markdown file by construction):

`BRANCH_REDTEAM.md`, `KILLED_BRANCHES.md`, `LOOP.md`, `MEASURED_REJECTION.md`, `POST_FAILURE_BRANCH_DECISION.md`, `RCI_FALSIFIER_DECISION.md`, `SCIENTIFIC_COMPARATOR_TEST0_RESULTS.md`, `SYNTH_BRANCH_1_RESULTS.md`, `TSF_FALSIFIER_RESULTS.md`, `W12_DRIFT_AND_ENSLAVEMENT_PRIOR_ART.md`, `W13_GESTURE_SEGMENTATION_NOLIFT.md`, `W16_LAYOUT_OPTIMISATION.md`, `W17_FEEDBACK_AND_HAPTICS.md`, `W18_BIMANUAL_AND_DRIFT.md`, `W19_CORRECTION_LATENCY.md`, `W1_ACADEMIC_ENSLAVEMENT.md`, `W20_THUMB_REACH.md`, `W22_CORRECTION_TIME.md`, `W2_STENO_HARDWARE.md`, `W3_OPEN_SOURCE.md`, `W4_ZERO_FORCE_ALGORITHMS.md`, `W5_POINTING_MOTOR_LIMITS.md`, `W6_THUMB_BIMANUAL_VIABILITY.md`, `W7_PHYSICAL_MASKS_HAND_ERGONOMICS.md`, `W8_LAYOUT_VECTOR_DECODING.md`, `W9_STENO_LANGUAGE_LAYER.md`, `models_confusion_analysis.md`, `RESEARCH_STARTED_AT.txt`, and `requirements-plot.txt`.

This is a discoverability failure, not proof that each file lacks internal value. It is especially serious for `KILLED_BRANCHES.md` and `MEASURED_REJECTION.md`, which contain the current retraction and rejection record, and for the frozen result documents that determine the status of later branches.

## 2. The nine retractions

All nine are findable in the numbered “Retractions in force” list in `KILLED_BRANCHES.md:45-53`. The list itself is undated, so the “when” test is satisfied only when a named source document supplies a date. Entries 1, 2, and 4–9 have such backing. Entry 3 does not.

| # | Retraction | What is withdrawn | Underlying basis and provenance | When | Finding |
|---:|---|---|---|---|---|
| 1 | 88% language recovery | The `6.8% -> 88.8%` recovery table and downstream correction/typing-rate arithmetic (`KILLED_BRANCHES.md:45`; `LM_RECOVERY.md:98-107,155-158`). | Intended-sector-conditioned candidates leaked the answer. The experiment used 1,200 generated words per radius and a 20,000-word list; human operators and hardware sessions were 0 (`LM_RECOVERY.md:18-24`; `KILLED_BRANCHES.md:45`). | `LM_RECOVERY.md:98`: 2026-09-25 08:20. | **Complete.** |
| 2 | Fitts “impossible” overreach | Generalization from target-to-target aiming to every drawn-path primitive (`BINDING_CONSTRAINT.md:31-43`; `KILLED_BRANCHES.md:46`). | Provisional coefficients with 0 fitted hand trials, 0 operators, and 0 sessions; the result bounds aiming, not drawing (`BINDING_CONSTRAINT.md:13-15,55-56`; `KILLED_BRANCHES.md:46`). | `BINDING_CONSTRAINT.md:3`: 2026-09-25 sprint synthesis. | **Complete.** |
| 3 | 22.7% bimanual multiplication | The arithmetic claim is named, but no underlying measurement is identified (`KILLED_BRANCHES.md:47`). | The entry explicitly says there is **no recoverable sample size, operator, or session provenance**. | **Missing.** The only retraction entry has no date, and the cited `W6_THUMB_BIMANUAL_VIABILITY.md`/`CUED_SESSION_PROTOCOLS.md` do not contain a dated 22.7% retraction. | **Incomplete: measurement, n/operator/session, and date are all missing.** |
| 4 | Correction-cost premise | “Lower accuracy plus cheap repair beats higher accuracy plus expensive repair” when repair consumes another event (`BINDING_CONSTRAINT.md:197-208`; `KILLED_BRANCHES.md:48`). | Design arithmetic, not a user measurement; human n=0, operators=0, sessions=0; repair-time inputs were assumptions. | `BINDING_CONSTRAINT.md:3`: 2026-09-25. | **Complete.** |
| 5 | Throughput formula | Naive `(1−p)/A` accepted-output accounting because it omits failed-candidate occupancy (`BINDING_CONSTRAINT.md:307-317`; `KILLED_BRANCHES.md:49`). | Human n=0, operators=0, sessions=0; the replacement is geometric-attempt accounting, not a user result. | `BINDING_CONSTRAINT.md:3`: 2026-09-25. | **Complete.** |
| 6 | Incorrect `2^9.476` and companion exponentials | `716.8`, `1071.6`, and later `1024.9`; retained corrections are `712.30` and `1041.42` (`BINDING_CONSTRAINT.md:268-276,784-788`; `KILLED_BRANCHES.md:50`). | Corpus/codebook arithmetic over 725,119,374 English and 151,705,378 German tokens; human operators and sessions=0. It is not a device or human result. | `BINDING_CONSTRAINT.md:3`: 2026-09-25. | **Complete.** |
| 7 | Syllable typing-rate arithmetic | The first conversion and later complete user-facing ladder; only structural corpus event counts survive (`BINDING_CONSTRAINT.md:390-408,747-764`; `KILLED_BRANCHES.md:51`). | Combined event-rate ceilings, segmentation assumptions, and syllable inventories without human validation; human n=0, operators=0, sessions=0. | `BINDING_CONSTRAINT.md:3`: 2026-09-25. | **Complete.** |
| 8 | German/English weighting mismatch | The claim that English is materially easier as a cross-language comparison until weighting is matched (`BINDING_CONSTRAINT.md:823-842`; `KILLED_BRANCHES.md:52`). | English is token-weighted; the German figure may be an unweighted pyphen count. Corpus n is 725,119,374 English and 151,705,378 German tokens; operators and sessions=0. | `BINDING_CONSTRAINT.md:3`: 2026-09-25. | **Complete as a provisional withdrawal.** |
| 9 | `0.4583` field separability | The observed class-mean result as evidence; the ten-contact design space is closed (`ARCHIVE.md:14-24`; `BINDING_CONSTRAINT.md:651-684`; `KILLED_BRANCHES.md:53,55-57`). | 1,000 permutations, seed 20260925, 57 dimensions, observed `0.4583` below null mean `0.5685`, one-sided `p=0.9460`; 24 trials, 8 classes, 3/class, one operator, one session, `n=63`, no error bars. | `ARCHIVE.md:14`: 2026-09-25. | **Complete.** |

## 3. Stale live/promising/current claims

The following statements remain in root documents and conflict with the current 22/0/0 record, the killed vertical slice, the closed ten-contact design space, the failed TSF falsifier, or the current priority of the never-run physical instruments. They are quoted, not corrected here.

| File and line | Verbatim stale claim | Why it is stale |
|---|---|---|
| `ARCHIVE.md:57` | “## Tier 3 — current, and the live design surface” | The tier still presents multiple historical documents as a live design surface after the sprint record says no branch survived. |
| `ARCHIVE.md:72` | “an open design decision, still open” | `DECISION_HOLEMASK_VS_SOFTWARE.md:4-9` says the question is closed and directs software suppression first. |
| `ARCHIVE.md:106` | “the one concept the evidence leaves open — unvalidated” | `VERTICAL_SLICE.md:3-6,113-114,164-183` says the concept is killed and the acceptance test produced no result. |
| `ARCHIVE.md:134-136` | “the optimiser is the strongest idea in the project (recommendation)” | `KILLED_BRANCHES.md:24-25` rejects the selected-thumb primitive and suspends only non-recognition arithmetic; no fitted hardware coefficients exist. |
| `DESIGN_DECISION.md:10-12` | “the final design comparison and decision record: the three finalists, their trade-offs, the selected vertical slice, fallback, kill tests” | The compatibility index calls a killed selection authoritative. `VERTICAL_SLICE.md:3-6` now says the selected slice is killed. |
| `DESIGN_DECISION.md:24-25` | “The surviving design work and decisions are recorded in `DESIGN_DECISION_FINAL.md` and `BINDING_CONSTRAINT.md`” | `BINDING_CONSTRAINT.md:546-547,813-821` says no concept survived. “Surviving” here is false if read as a surviving design direction. |
| `DESIGN_DECISION_FINAL.md:98-100` | “F2 is the only finalist that clears 30. F1 is the most buildable; F2 is the most promising.” | Later critics and the kill register rejected both selected-contact primitives. Prominence as a historical score is not current viability. |
| `DESIGN_DECISION_FINAL.md:104-107` | “DECISION: build F2, keep F1 as the fallback” / “Vertical slice: one stroke, one word” | The selected vertical slice is now killed and its acceptance test was void because the pad was empty (`VERTICAL_SLICE.md:3-13,156-168`). |
| `DESIGN_DECISION_FINAL.md:122-125` | “F1 stays the fallback” / “it is a working 5-bit-per-event system” | `KILLED_BRANCHES.md:21,24-25` records the lattice and selectable-thumb primitives as killed by measurement. |
| `BINDING_CONSTRAINT.md:65` | “FCPT — Fitts-Cost Phoneme Targets — the new baseline” | Later in the same record the current selected-thumb primitive is killed; `KILLED_BRANCHES.md:24-25` is the consolidated status. |
| `BINDING_CONSTRAINT.md:127` | “Score 28/50, verdict ADVANCE.” | This is the Synergy Field Chords row. `KILLED_BRANCHES.md:26` changes it to “Suspended; no current advancement.” |
| `BINDING_CONSTRAINT.md:190-191` | “36/50, verdict ADVANCE. Highest of every concept generated in this sprint.” | Thread-Rosette was later killed by its critics and measurement; `BINDING_CONSTRAINT.md:494-497,546-547` and `KILLED_BRANCHES.md:29` say so. |
| `BINDING_CONSTRAINT.md:230-233` | “FCPT wins” / “GAEC ... should be built as a second arm once FCPT's fitted a and b exist” | The current capture rejected the attribution premise needed by both selected-thumb branches; the coefficients still have not been fitted. |
| `LM_RECOVERY.md:6-8` | “the language layer is the correctness lever ... and it shows the claim is true, incomplete” | This is a calibrated synthetic/model result, not a validated hardware signal. It remains in a document without a top-level superseded banner, despite the 0-signal record. |
| `LM_RECOVERY.md:43-47` | “The claim holds, and it is not the whole story.” / “The language model does recover accuracy.” | The same document retracts those numbers at `98-107`; the unstruck live claim is internally stale. |
| `LM_RECOVERY.md:147-153` | “The language layer is still potentially the correctness lever” | This remains a proposal based on synthetic-but-calibrated reachability, not a surviving validated direction. |
| `CROSS_VALIDATION.md:200-203` | “The language layer is a proven lever ... They should be built in parallel” | No current candidate is validated and no signal survives. The cited evidence does not establish a project language-layer result. |
| `VECTOR_DESIGN_CRITIQUE.md:255` | “the language layer is the correctness lever, not the speed lever” | This is an inference from a calibrated confusion model, not a validated current direction. |
| `COMPASS_SURFACE.md:157-160` | “Option 3 ... is the only one that escapes the trade, and it deserves a design pass.” | The ten-contact design space is closed and the reshape control has never run; it is an unrun instrument, not a surviving design pass. |
| `AGENT2_RESEARCH_LOG.md:286-287` | “THE CONSEQUENCE: at an ergonomic radius the compass has 32-42% label error. The language layer is no longer the speed lever ... but the CORRECTNESS lever.” | Historical log entry, but still stated as a consequence; later record has 0 validated candidates and 0 surviving signals. |
| `AGENTIC_STATE.md:10-11` | “Open falsification test: None executed” / “Next executable action: Implement only the frozen RCI design” | RCI is design-only and the current physical priority is the three never-run instruments and never-run control. This is stale as the current next action. |
| `AGENTIC_META_PLAN.md:186` | “SINGLE FRESH DESIGN-ONLY BRANCH; UNIMPLEMENTED.” | This still makes RCI the live selected branch even though the consolidated record gives no surviving signal and the next physical evidence has not been collected. |
| `POST_FAILURE_BRANCH_DECISION.md:3-7` | “RCI SELECTED AS THE SINGLE FRESH DESIGN-ONLY BRANCH” / “Single next branch: Rest-Censored Innovation (RCI)” | This is a historical decision record but is not marked superseded and remains orphaned. It conflicts with the current physical-instrument priority. |
| `RCI_FALSIFIER_DECISION.md:3-6,11-14` | “RCI IS THE SINGLE FRESH DESIGN-ONLY BRANCH” / “Implementation may begin only after this decision is recorded” | It is unimplemented design only, not a validated or surviving direction. The document is orphaned and still authorizes implementation as the next step. |
| `SYNTH_BRANCH_1_RESULTS.md:63` | “`RCI_FALSIFIER_DECISION.md` now selects RCI as the single fresh design-only branch” | Historical result document; selection does not make RCI validated, and the current state remains 0 validated. |
| `TSF_FALSIFIER_RESULTS.md:86` | “RCI is the single fresh design-only branch” | The TSF result itself is a failure, and RCI selection is historical rather than evidence of a current surviving direction. |
| `KILLED_BRANCHES.md:74-76` | “TSF is also not killed, but it is only a frozen research design” | This conflicts with `TSF_FALSIFIER_RESULTS.md:3-14,71-79`, which says the completed frozen falsifier failed and the implementation is held/rejected. |
| `scripts/field_null_test.py:6-9` | “That is the only positive result in the project. It has never been tested against a null.” | The script exists to perform that test; after the test, this introductory text is stale. The later commit did not modify the script. |

The following statements are accurate controls against those stale claims and should not be mistaken for defects: `KILLED_BRANCHES.md:3,57,68,72`; `ARCHIVE.md:14-24,139-147,158`; `BINDING_CONSTRAINT.md:546-547,645-647,813-821`; and `VERTICAL_SLICE.md:3-13,164-183`.

## 4. Cross-document arithmetic

| Audited item | Sources | Agreement finding |
|---|---|---|
| `U = 0.9491`, `U = 0.9980` | `BINDING_CONSTRAINT.md:591-596`; `MEASURED_REJECTION.md:18`; `VERTICAL_SLICE.md:21` | Agree exactly; comma-decimal formatting in the vertical slice is not a value difference. |
| `U` gate `0.10` | `BINDING_CONSTRAINT.md:596`; `MEASURED_REJECTION.md:18`; `VERTICAL_SLICE.md:21` | Agree exactly. |
| Major-axis dynamic range `0.5 mm` | `BINDING_CONSTRAINT.md:613-615,630-631`; `KILLED_BRANCHES.md:28`; `MEASURED_REJECTION.md:18`; `VERTICAL_SLICE.md:22` | Agree exactly. The `0–2.5 mm` and `1.0–1.5 mm` figures are explicitly contextual, not competing range totals. |
| `n=63` strokes, 24 trials, 8 classes, 3/class | `ARCHIVE.md:16-20,141-145`; `BINDING_CONSTRAINT.md:657-659,678-682,690-696`; `KILLED_BRANCHES.md:53,57`; `MEASURED_REJECTION.md:9-14,26`; `VERTICAL_SLICE.md:25-28,99-104,164-168`; `models_confusion_analysis.md:3-5` | Agree. Operator/session and no-error-bar caveats agree for the field result. |
| `2.585` modifier bits/event | No root-document occurrence of `2.585` or `2,585` | **Requested figure is absent.** The documents instead use `1.585` modifier bits/event at `BINDING_CONSTRAINT.md:145,352-354` and `KILLED_BRANCHES.md:28`; this is `log2(3)`. The two present sources agree. |
| `9.476` bits/token and `2^9.476` | `BINDING_CONSTRAINT.md:245-247,721,784-788`; `KILLED_BRANCHES.md:50` | Entropy agrees. Exponentiated results appear as `712`, `712.3`, and `712.30`; these are rounding only. The corrected value is consistently 712.30. |
| `12,853` English phonemic syllables | `BINDING_CONSTRAINT.md:716-730,772-775` | Current value agrees. `12,870` is explicitly identified as the superseded pre-rhotic-fix value at `726-730`. |
| `1.3965` syllables per 5-letter word | `ARCHIVE.md:149-151`; `BINDING_CONSTRAINT.md:720,736,748,825,835-837`; `VERTICAL_SLICE.md:54-56` | Agree. `1.396494` is the full-precision value in `BINDING_CONSTRAINT.md:728-730,790-793`; no substantive disagreement. |
| `4.189` events per 5-letter word | `ARCHIVE.md:149-151`; `BINDING_CONSTRAINT.md:790-793,835-837`; `VERTICAL_SLICE.md:54-56` | The event count agrees; `4.19` at `BINDING_CONSTRAINT.md:738` is rounding. **The attached 39% statement does not agree:** `ARCHIVE.md:149-151` attaches “39 percent overshoot” to `4.189`, while `BINDING_CONSTRAINT.md:742-744` attaches 39% to `2.79` events against the two-event cap. `4.189` is 2.79, not 39%, above a two-event cap (109.45% over two). This is a real cross-document arithmetic mismatch. |

## 5. Measurement-result provenance

### Audit rule

For this audit, “measured result” includes a project-generated hardware replay, a synthetic/simulated project result, and a model called a measurement. External literature rows in the `W*` documents are source studies and are not assigned this repository's operator/session counts. The relevant requirement is that each project result state its event/frame/trial/stroke/token `n`, operator count, session count, and evidence class. “Simulated” and “assumed” are treated as distinct evidence classes.

### Documents with complete provenance at the principal result

- `ARCHIVE.md:44-55` gives the standing one-person/one-session/one-thumb, `n=63`, no-error-bar caveat.
- `KILLED_BRANCHES.md:7-13,17-38,45-57` defines evidence conventions and puts provenance in the result cells.
- `MEASURED_REJECTION.md:7-14,26` tabulates n, operator, session, class count, and caveats for both real-capture results.
- `models_confusion_analysis.md:3-5,41` states 24 trials, 8 classes, one operator, one session, `n=63`, no error bars, measured real capture, and the unrun control.
- `NOVELTY_STATEMENT.md:49-69` explicitly states one hand, three sessions, one device, one operator, and the limits of within-session inference.
- `VERTICAL_SLICE.md:25-29,99-105,141-145,164-168` fully qualifies the withdrawn field result and the 47.6% comparator.
- `BINDING_CONSTRAINT.md:336-339,487-490,657-684` fully qualifies its principal human result and the ninth retraction.

### Documents or result blocks that omit at least one required field

| File and lines | Result block | Omission |
|---|---|---|
| `FIVE_HOURS_REPORT.md:22-31` | Measured sector accuracy, jitter, signal ratio, zero-event arm, and natural envelope. | No operator count, no session count beside the table, and several rows have no `n`; only jitter gives sample count. The prose calls these real measurements. |
| `MEASURED_BIOMECHANICS.md:3-8,20-23,28-33,49-62` | Three-session hardware measurements. | n and three sessions are stated and evidence class is measured, but the document says “this hand,” not an explicit operator count. |
| `MEASURED_INTENT_FILTER.md:34-40,54-60` | Replay results and free-motion event rate over three real sessions. | Frame/event n and three sessions are stated; no explicit operator count. |
| `VECTOR_DESIGN_CRITIQUE.md:14-18,37-39,69-75,109-132,235-237` | Measured feasibility, coupling, drift, and simulation results. | Contact/frame n and three real sessions are present for project data; explicit operator count is absent. Simulated trials are not consistently accompanied by `0` human operators/sessions. |
| `CROSS_VALIDATION.md:4-7,62-68,112-135,305-349,369-390` | Project measurements, calibrated synthetic envelope, and signal-chain simulations. | Mixed evidence classes are described, but project operator/session counts are not stated beside the imported measurements or simulations. |
| `DECISION_HOLEMASK_VS_SOFTWARE.md:18-21,35-38,53-58,85-92` | Three-session suppression/rest results used to close the decision. | Sessions and contacts/events are stated; explicit operator count is absent. |
| `REAL_DATA_DECODE.md:3-17,45-55` | Closed-loop replay over three real sessions. | Sessions and event n are stated; explicit operator count is absent. |
| `REST_MODEL.md:3-4,27-29,64-74,92-95` | Sliding-window replay over three recorded sessions. | Three sessions and contact n are stated; “one hand in one session shape” does not explicitly state operator count. |
| `SEPARATION_MODEL.md:3-7,44-48,57-60` | Rest/coupling rules checked over three real sessions. | n and three sessions are stated; explicit operator count is absent. The document mixes measured constants and model rules without a compact result provenance header. |
| `COMPASS_SURFACE.md:3-9,13-17,41-60,73-94,136-160` | Modeled accuracy surface plus measured natural-envelope rows. | Inputs and a model return speed are described, but the accuracy surface is not consistently labelled simulated in the result table; explicit operator count is absent. |
| `LAYOUT_ASSIGNMENT.md:17-25,45-56,69-80,82-87` | 4,800-trial calibrated confusion/layout experiment. | Synthetic/model status and trial n are stated, but `0` human operators and `0` human sessions are not stated. |
| `BENCHMARK_RESULTS.md:13-25,41-57,70-75,149-165` | Synthetic benchmark and corrected envelope. | Synthetic status and several n values are explicit, but `0` human operators and `0` human sessions are omitted. |
| `LM_RECOVERY.md:10-24,98-158` | Corrected and retracted synthetic-calibrated word/channel tables. | Generated-word n and evidence caveats are partly stated; explicit human operator/session counts are absent, and several passages call the outputs measurements. |
| `W14_DIRECTION_ACCURACY_ROOTCAUSE.md:5-7,61-64,108-149` | Simulation trials and assumed noise sweeps. | Simulation/assumption labels and some trial counts are present; explicit `0` human operators/sessions is absent. The imported `0.5 mm/s` drift input is not locally given operator/session provenance. |
| `AGENT2_RESEARCH_LOG.md:8-17,52-63,75-90` | Early real and synthetic result entries. | Three real sessions and some synthetic n are stated, but early result entries do not state operator count. A later entry at `198-202` supplies the one-operator fact, far from the result passages. |
| `EXPERIMENT_PROTOCOL.md:82-101` | Three-session measured noise-floor constants used to set the sweep. | Sessions are stated; n and operator count are absent beside the quoted p99/max/drift results. |
| `W12_DRIFT_AND_ENSLAVEMENT_PRIOR_ART.md:16-18,28-36,49-74` | Comparison table repeatedly cites the project's drift/coupling measurements. | Source-study n is not the issue; the imported project measurement's n, operator, and session are not stated in this document. |
| `BINDING_CONSTRAINT.md:584-619` | U and major-axis gate tables. | Frame n and measured class are present, but operator/session counts are not attached to these two capture results. The later field-result section is fully qualified; this is a localized omission. |
| `VERTICAL_SLICE.md:19-23` | Summary table for U and major-axis range. | The field result is qualified later, but the U/range rows omit capture/frame n, operator, and session provenance. |
| `SCIENTIFIC_COMPARATOR_TEST0_RESULTS.md:3-13,23-32,89-103` | Frozen synthetic comparator result. | Synthetic class, generated n, and generated session counts are present; explicit human operator count=0 is absent. |
| `SYNTH_BRANCH_1_RESULTS.md:3-23,25-49,55-63` | Frozen synthetic comparison outputs. | Synthetic class, generated n, and generated sessions are present; explicit human operator count=0 is absent. |
| `TSF_FALSIFIER_RESULTS.md:3-14,18-25,29-42,74-86` | Frozen synthetic falsifier failure. | Synthetic class, test n, and three generated session clusters are present; explicit human operator count=0 is absent. |
| `AGENTIC_META_PLAN.md:179-190` | Branch-registry summaries of synthetic and design results. | Evidence classes and some n appear, but the table does not consistently carry human operator/session counts with each result. |
| `AGENTIC_STATE.md:45-52` | Ledger summaries of synthetic comparator, branch, and falsifier results. | Some n and synthetic class appear, but result rows do not consistently state human operator/session counts. |
| `POST_FAILURE_BRANCH_DECISION.md:22-39,70-83` | Comparator and branch-comparison result summary. | Synthetic status is stated, but the exact n/operator/session provenance is not repeated beside the metrics and is deferred to orphaned result documents. |

The omissions above are documentary, not proof that the listed results were fabricated. The strongest provenance record is concentrated in the newer kill/rejection documents; older measurement and branch-summary documents frequently rely on links instead of carrying the four fields locally.

## 6. Commit `56fb218`

### What it introduced

Commit `56fb218b2e30ae6e78cd6eb592f90e54603b7237` was committed on **2026-09-25 14:24:36 +02:00** with the message:

> `WIP: null test and kill register from an agent that died on a network timeout`

It added exactly three files:

1. `KILLED_BRANCHES.md` — 66 lines;
2. `scripts/field_null_test.py` — 322 lines;
3. `tests/test_field_null_test.py` — 104 lines.

There is one later commit in the inspected history: `5151e3d3078ab99591bb4c9465b545dec2383cc1`, committed **2026-09-25 14:32:25 +02:00**, titled `Retract the last surviving signal: the 0.4583 field separability does not beat its own null`. Its diff changes only `ARCHIVE.md`, `BINDING_CONSTRAINT.md`, `KILLED_BRANCHES.md`, `MEASURED_REJECTION.md`, and `VERTICAL_SLICE.md`; it does not change the null-test script or its test.

### Proper-description finding

**The scientific conclusion introduced by the WIP commit is properly described by later root documents, but the WIP commit is not fully integrated or fully reconciled.**

Properly described:

- the null method and decision rule: `scripts/field_null_test.py:11-58`;
- the result and full provenance: `ARCHIVE.md:14-24`, `BINDING_CONSTRAINT.md:651-684`, `KILLED_BRANCHES.md:38,53-57`, `MEASURED_REJECTION.md:5-26`, and `VERTICAL_SLICE.md:23-29,96-105,164-168`;
- the control never run and the reshape/Fitts instruments never run: `KILLED_BRANCHES.md:66-72`;
- the final project state: `ARCHIVE.md:22-24,158` and `BINDING_CONSTRAINT.md:813-821`.

Not fully documented/integrated:

- `KILLED_BRANCHES.md`, the principal register introduced by the WIP commit, is neither referenced by `ARCHIVE.md` nor reachable from `README.md`.
- `tests/test_field_null_test.py` has no later root-document reference; the later commit leaves the test file unchanged.
- The WIP-introduced script still says at `scripts/field_null_test.py:6-9` that `0.4583` “has never been tested against a null.” That introductory statement was true before execution and is false in the committed current record. The later commit describes the result but does not reconcile the script text.
- The later commit message says the vertical slice is killed and five documents were corrected, but the repository still links `DESIGN_DECISION_FINAL.md` as authoritative and retains live RCI direction documents outside both indexes. Thus the WIP's substantive retraction is documented, while the record around it is not fully closed.

## Final assessment

The record contains enough explicit correction material to prevent the old numbers from being silently reused, but it does not yet function as a self-consistent source of truth. The concrete blockers are: 27 pre-existing Markdown records outside both indexes; a killed vertical slice still presented as open/current; historical recommendations still presented as live; an RCI implementation path still presented as the next action; a direct TSF status contradiction; incomplete provenance in the 22.7% retraction; inconsistent attachment of the 39% overshoot; absent `2.585`; and a stale introductory claim inside the null-test script introduced by the WIP commit.
