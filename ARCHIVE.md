# ARCHIVE — index of the document set

**Created:** 2026-09-25, during the design sprint. 58 Markdown files had accumulated at
the repository root over roughly two weeks of parallel agent work. This file says which
ones still carry weight, which are superseded, and which are retracted. Nothing is deleted:
an archive that deletes is a history that lies.

## How to read this repository

There is no single document. The claims live in the files below, and several of them
contradict each other by design — a retracted number is kept next to its correction so the
correction is auditable.

> **Ninth retraction — repository entry-point correction (2026-09-25):** the reported
> contact-field class-mean top-1 score of 0.4583 existed, but it has been **withdrawn as
> evidence** and the contact-field branch is **killed**. In the measurement from 24 cued
> trials (8 compass classes, 3 per class; one operator, one session, n=63 strokes;
> thumb-compass labels; no error bars), a 57-dimensional descriptor scored 0.4583 against
> a 1000-permutation null mean of 0.5685, median 0.5833, 95th percentile 0.7083, and
> 99th percentile 0.7500 (seed 20260925). The observed score was below the null mean;
> the predeclared one-sided decision rule `p >= 0.05` gave **p = 0.9460**, requiring
> withdrawal. The ten-contact field design space is therefore **closed**: 22 candidates
> were generated, 0 validated, and 0 signals survive. See
> `scripts/field_null_test.py`.

**Record correction (2026-09-25):** `RECORD_AUDIT.md` §3 found four stale claims in this
index—the live Tier 3 framing, the supposedly open hole-mask decision, the supposedly open
vertical slice, and the optimiser priority claim. They were corrected here; the audit did
not revive any killed branch.


**Before quoting any number, check which tier it is in.**

---

## Tier 1 — load-bearing. Change these only with evidence.

| File | What it settles |
|---|---|
| `MEASURED_BIOMECHANICS.md` | measured speeds, radii, hand dimensions from this machine |
| `COMPASS_SURFACE.md` | the radius design surface, derived from measured noise |
| `W14_DIRECTION_ACCURACY_ROOTCAUSE.md` | where direction error actually comes from |
| `W10_STENO_ON_TOUCH.md` | machine stenography on a 0-force surface |
| `DECODER_DESIGN.md` | contacts → reversible strokes |
| `VECTOR_DESIGN_CRITIQUE.md` | feasibility of the 4-finger / 16-zone design |
| `NOVELTY_STATEMENT.md` | what is known, what we measured, what is ours |
| `RECOMMENDED_ARCHITECTURES.md` | the architecture options considered |
| `KILLED_BRANCHES.md` | consolidated branch kill/hold register and the nine retractions in force |
| `MEASURED_REJECTION.md` | current real-capture contract rejection and field-null measurement record |

## Tier 2 — measured this session, one operator, not yet replicated

| File | What it holds |
|---|---|
| `FIVE_HOURS_REPORT.md` | the accounting of one day: built, measured, retracted, missing |
| `models/01_kompass_primitiv.png` | the primitive as drawn on the real pad |
| `models/02_confusion_gemessen.png` | 63 measured strokes, 47.6 %, 180° error pattern |
| `models/03_decoder_decke.png` | what the language layer can buy — simulated channel |
| `CROSS_VALIDATION.md` | literature numbers against our measurements |
| `models_confusion_analysis.md` | folded and unfolded analysis of the 63-stroke real compass capture |

**Standing caveat:** the confusion matrix, the 47.6 % and the 0.4 mm jitter come from **one
person, one session, one thumb**. `n = 63`. No error bars are claimed for them.

## Tier 3 — sprint-closed historical document set; retained for discoverability, not current work

The sprint closed with 22 candidate records, human `n=0` operators and `0` sessions:
0 candidates were validated and 0 signals survive. Nothing in this tier is current work or
a live design surface. The files remain listed so readers can find the historical records.

| File | Role |
|---|---|
| `LEXICON_RECOVERY.md` | the conditioned benchmark — the honest version of the language claim |
| `LEXICON_DECODING.md` | the word-level decoder |
| `LM_RECOVERY.md` | **contains a retraction**; read the retraction section first |
| `LAYOUT_ASSIGNMENT.md` | confusion-matrix-driven sector layout |
| `CUED_SESSION_PROTOCOLS.md` | what to run on real hardware and what each block yields |
| `CROSS_VALIDATION.md`, `LANGUAGE_LAYER_METRICS.md` | how good the decoder is |
| `CORRECTION_THROUGHPUT.md` | the stopwatch protocol — seconds per correction, still unmeasured |
| `BIMANUAL_ANALYSIS.md`, `MEASURED_INTENT_FILTER.md` | multi-finger behaviour |
| `SEPARATION_MODEL.md`, `REST_MODEL.md` | the decision rules |
| `EXPERIMENT_PROTOCOL.md`, `TRAINING_PATH.md`, `PLOVER_BRIEFS.md` | how to evaluate and what to build |
| `PRIVACY_TELEMETRY.md`, `RAW_FRAME_SCHEMA.md` | consent and data format |
| `DECISION_HOLEMASK_VS_SOFTWARE.md` | **closed decision:** build the software coupling-suppression path first; do not build a hole mask. See this decision record. |
| `CANDIDATE_RANKING.md` | confidence and language candidate-ranking seam retained without a text commit |

## Tier 4 — retracted or superseded. Kept for audit, do not cite as current.

| File | Status |
|---|---|
| `LM_RECOVERY.md` (recovery table) | **RETRACTED.** candidates were conditioned on the intended sector. The corrected numbers are in `LEXICON_RECOVERY.md` |
| `BENCHMARK_RESULTS.md` | first accuracy numbers, superseded by the conditioned benchmark |
| `SYNTHETIC_BASELINE.md` | synthetic pipeline baseline; no longer the reference |
| `W11_VERIFY_KEYLESS_CEILING.md` | speed-ceiling estimate, withdrawn with the WPM numbers |
| `REAL_DATA_DECODE.md` | early device read, superseded by the 63-stroke measurement |
| `LANGUAGE_CAPTURE_RUNBOOK.md`, `LANGUAGE_CORPUS_MANIFEST.md` | setup for a capture that has not happened |
| `AGENT2_RESEARCH_LOG.md`, `RESEARCH_LOG.md` | chronological logs, not sources of truth |
| `SYSTEMKOMPENDIUM.md` | the full system walkthrough, 64 KB, written before the retraction |
| `COMPREHENSIVE_RESEARCH_REPORT.md`, `CODE_REFERENCES.md` | literature and citations |
| `ARCHIVE.md` | this index of current, superseded, historical, and retracted record material |
| `README.md` | repository entry point and deliverable index |
| `RECORD_AUDIT.md` | root-record consistency audit that identified missing, stale, and incomplete provenance |
| `AGENTIC_META_PLAN.md` | partner-agent planning and branch-registry process record, not a live technical direction |
| `AGENTIC_STATE.md` | partner-agent implementation and evidence state ledger retained as a process record, not current work |
| `BRANCH_REDTEAM.md` | partner-agent adversarial process audit of the frozen synthetic branch comparison |
| `LOOP.md` | partner-agent coordination process instructions for two-agent GitHub work |
| `POST_FAILURE_BRANCH_DECISION.md` | historical process decision selecting RCI after the frozen failure |
| `RCI_FALSIFIER_DECISION.md` | historical, unimplemented RCI design and proposed-falsifier process record |
| `SCIENTIFIC_COMPARATOR_TEST0_RESULTS.md` | frozen synthetic comparator-integrity result retained as a research record |
| `SYNTH_BRANCH_1_RESULTS.md` | frozen and audited synthetic branch-comparison output retained as a research record |
| `TSF_FALSIFIER_RESULTS.md` | frozen synthetic TSF falsifier failure retained as a research record |
| `SYSTEM_COMPARISON_MATRIX.md` | cross-system literature comparison retained as a research reference |
| `W1_ACADEMIC_ENSLAVEMENT.md` | sourced academic finger-enslavement literature review |
| `W2_STENO_HARDWARE.md` | sourced stenography and chording-hardware literature review |
| `W3_OPEN_SOURCE.md` | verified open-source component and license inventory |
| `W4_ZERO_FORCE_ALGORITHMS.md` | sourced zero-force input and intent-detection literature review |
| `W5_POINTING_MOTOR_LIMITS.md` | sourced pointing and motor-control limits review |
| `W6_THUMB_BIMANUAL_VIABILITY.md` | sourced thumb-direction and bimanual viability review |
| `W7_PHYSICAL_MASKS_HAND_ERGONOMICS.md` | sourced physical-mask and hand-ergonomics review |
| `W8_LAYOUT_VECTOR_DECODING.md` | sourced layout, vector-decoding, and chord-disambiguation review |
| `W9_STENO_LANGUAGE_LAYER.md` | sourced language-layer and dictionary review |
| `W12_DRIFT_AND_ENSLAVEMENT_PRIOR_ART.md` | prior-art search for drift and finger-coupling evidence |
| `W13_GESTURE_SEGMENTATION_NOLIFT.md` | prior-art search for gesture segmentation without lift-off |
| `W16_LAYOUT_OPTIMISATION.md` | prior-art review of layout optimization methods |
| `W17_FEEDBACK_AND_HAPTICS.md` | prior-art review of feedback and sensory substitution |
| `W18_BIMANUAL_AND_DRIFT.md` | external bimanual, drift, fatigue, and support evidence review |
| `W19_CORRECTION_LATENCY.md` | literature search for correction-latency evidence |
| `W20_THUMB_REACH.md` | sourced thumb reach and comfort evidence review |
| `W22_CORRECTION_TIME.md` | literature search for seconds-per-correction evidence |
| `RESEARCH_STARTED_AT.txt` | root process timestamp recording when research started |
| `requirements-plot.txt` | optional plotting-dependency manifest for the model-figure script |

---

## House rules after this sprint

1. **No bare claim.** A number without a tier and a source is a rumour.
2. **Retraction lives next to the claim.** Never silently replace a wrong number.
3. **Measured is not simulated.** Every figure says which it is, on its face.
4. **One operator is one datum.** `n = 63` from one thumb is a measurement, not a statistic.
5. **Raw traces are biometric.** `messung/` stays local and is in `.gitignore`.

## Sprint deliverables (2026-09-25)

Added after this index was first written. These supersede the framing in most Tier 3 and
Tier 4 files.

| File | What it settles |
|---|---|
| `BINDING_CONSTRAINT.md` | **The record to read first.** Every candidate generated, every critic verdict, every correction, the measured gate numbers, the corpus arithmetic, and the eleven-section execution log |
| `VERTICAL_SLICE.md` | the historical field-set vertical slice, **killed** rather than unvalidated: its measured permutation null had mean `0.5685` and one-sided `p = 0.9460` over 1,000 permutations (seed 20260925, descriptor dimension 57) for `n=24` measured cued trials, 8 compass classes, 3 per class, one operator, one session, `n=63` strokes, thumb-compass labels, and no error bars; provenance: `scripts/field_null_test.py` |
| `DESIGN_DECISION_FINAL.md` | the three finalists and why none survived |
| `DESIGN_DECISION.md` | the earlier kill of the direction-quantisation frame |
| `FIVE_HOURS_REPORT.md` | the honest accounting of that day |
| `scripts/geometry_probe.py` | measures U and the ellipse dynamic range |
| `scripts/field_separability.py` | the withdrawn contact-field separability result; use the ninth retraction in `scripts/field_null_test.py` |
| `NEXT_SESSION.md` | runbook for the next physical session: preconditions, startup gate, the three unrun instruments, and what the session cannot establish |
| `scripts/field_gesture_probe.py` | the control experiment that has not produced a verdict |


**Cross-repository:** `commindv2` PR #1 makes `input_zones.json` the single steno layout
authority. Before it, a bare `WacomTouchReader()` silently received a different keyboard
than the app, and no test could detect it because both layouts were self-consistent.

## Cross-repository roles

touch-steno owns the input system: PTH-660 capture, segmentation, decoding, English
steno profile mapping, local replay, and measurement instruments. `commindv2` is a
`REFERENCE_ONLY` eventual consumer and is locally inspectable. `commind` is a
`REFERENCE_ONLY` concept canon and was NOT inspectable, so nothing about its implementation
may be asserted. See [INTEGRATION_TARGETS.md](INTEGRATION_TARGETS.md) for the integration
boundary and evidence limits.

[INTEGRATION_CONTRACT_V1.md](INTEGRATION_CONTRACT_V1.md) is the authoritative event contract.

## Innovation branch registry

The following four branches are research records, not silently implemented features:

1. **FCPT / Fitts-cost phoneme target layout** — its selected-thumb primitive was rejected
   by a measured contract replay with `n=24` cued trials, one operator, one session, and no
   error bars: it produced 0 key events, rejected all 24 trials as
   `ambiguous_attribution`, and obtained coverage `0.0`. The optimiser arithmetic is
   suspended only as a non-recognition research tool, and its Fitts coefficients `a` and
   `b` remain unfitted to this hand (`n=0` fitted hand trials, one operator, one session;
   unmeasured). See `KILLED_BRANCHES.md`.
2. **Continuous elastic word-as-event** — specified and self-scored 25/50; the acceptance
   test ran and returned void because the pad was empty.
3. **Contact-field / permutation-invariant gesture representation — KILLED.** The branch
   previously recorded the only surviving signal, at 0.4583 class-mean top-1. That score
   existed but was **withdrawn as evidence** after the null test on 24 measured cued trials
   (8 compass classes, 3 per class; one operator, one session, n=63 strokes; thumb-compass
   labels; no error bars): 0.4583 observed versus 0.5685 null mean over 1000 permutations,
   one-sided **p = 0.9460**, seed 20260925, descriptor dimension 57. The observed value
   was below the null mean, so the predeclared `p >= 0.05` rule kills the branch. The
   **ninth retraction** is recorded by `scripts/field_null_test.py`; this entry remains so
   the killed branch cannot be revived under a new name.

4. **English syllable-pair arithmetic** — the token-weighted, pinned-corpus figure is
   1.3965 syllables per 5-letter word. At 2 events per syllable, a fixed syllable code
   needs 2.79 events per 5-letter word, about 40 percent over the 2-event cap. At 3
   events per syllable, it needs 4.189 events per 5-letter word, about 110 percent over
   that cap.

> **Overshoot correction (2026-09-25):** the audit found that the prior 39 percent
> overshoot had been attached to the 4.189 count. The correct 39.7 percent pairing is
> 2.79 events per 5-letter word at 2 events per syllable, over the 2-event cap.
 

## Archive tag

The state at the start of the design sprint is tagged `pre-sprint-2026-09-25`. The
decision record produced during the sprint is `BINDING_CONSTRAINT.md` at the repository
root. No branch is a surviving signal after the ninth retraction recorded above.
