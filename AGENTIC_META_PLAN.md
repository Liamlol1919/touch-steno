# Autonomous 10× Product-Engineering Meta-Plan

**Status:** active operating plan  
**Scope:** one coordinating agentic loop, English product artifacts, no user input required for ordinary work  
**Safety:** no destructive repository operations, no fabricated measurements, no privacy-invasive telemetry

## 1. Objective

Scale the clean-room English steno sprint from a single vertical slice into a broad, evidence-gated product program without allowing the loop to optimize against a single experiment, a single user, or a single metric.

The loop must produce progressively stronger evidence while keeping every claim reversible and auditable.

## 2. The 10× contract

| Dimension | Sprint slice | 10× autonomous target |
|---|---:|---:|
| Raw concepts | 5 | 500 |
| Consolidated candidates | 2 | 100 |
| Minimal prototypes | 1 | 30 |
| Integrated prototypes | 1 | 10 |
| Independent red-team reviews | 3 | 50 |
| Product finalists | 1 | 3 |
| Evidence classes | 4 | 8 |
| Hardware protocols | 1 | 10 |
| Replayable test suites | 1 | 20 |
| Decision gates | 3 | 30 |

The numerical targets are planning targets, not claims that all artifacts will succeed.

## 3. One coordinating agentic loop

The loop is sequential and stateful. Parallel workers may investigate independent branches, but exactly one coordinator owns state, prioritization, integration, and publication.

```text
INGEST
  -> EXPAND
  -> CRITIQUE
  -> NARROW
  -> BUILD
  -> VERIFY
  -> RED_TEAM
  -> DECIDE
  -> PUBLISH
  -> MEASURE
  -> REPEAT
```

### INGEST

- Fetch the remote head and inspect the clean working tree.
- Read open GitHub issues, current decision records, and the last published evidence.
- Classify every input as `constraint`, `hypothesis`, `evidence`, `risk`, or `unknown`.
- Never promote an unknown into a constraint without an explicit decision record.

### EXPAND

- Generate concepts across at least six independent families per iteration:
  - information theory and coding;
  - hand biomechanics and motor learning;
  - English steno and syllable grammar;
  - anonymous-contact state estimation;
  - temporal/control systems;
  - bimanual coordination and safety.
- Every concept must include a primitive, mathematical encoding, state machine, failure model, learning path, privacy boundary, and kill tests.
- Legacy code may be read for interfaces and provenance, but new product hypotheses start in the isolated `nextgen/` workspace.

### CRITIQUE

Each candidate receives five independent reviews:

1. anatomy and biomechanics;
2. observability and identity;
3. timing, throughput, and correction;
4. eyes-free learning and fatigue;
5. implementation, privacy, safety, and validation.

A candidate cannot advance on average score alone. Any hard veto is non-compensable.

### NARROW

- Consolidate raw ideas only when their physical signals or algebra are genuinely distinct.
- Keep a lineage ledger from every raw fragment to its parent candidate.
- Reduce the active set only after the critique matrix is written.
- Preserve rejected candidates and the reason for rejection; never delete a failed idea silently.

### BUILD

- Build the smallest executable vertical slice for the current candidate.
- Keep sensor evidence, steno symbols, dictionary lookup, and text output as separate layers.
- No language model may promote an ambiguous sensor observation into a confident symbol.
- Every artifact gets a version, provenance, and replay path.

### VERIFY

Required verification ladder:

```text
syntax/import
  -> unit tests
  -> exhaustive finite-state tests
  -> property/metamorphic tests
  -> synthetic replay
  -> real captured replay
  -> hardware session
  -> human eyes-free session
```

A lower level cannot be cited as evidence for a higher level.

### RED-TEAM

- Attack the current candidate with failure injection, adversarial inputs, alternate anatomies, timing shifts, contact loss, palm contamination, and stale state.
- Require a written answer to every failure: prevented, detected, corrected, or explicitly unresolved.
- Do not add complexity to hide a failed test; change the model or reject the candidate.

### DECIDE

Exactly one of:

- `PROMOTE`: evidence clears the declared gate;
- `HOLD`: useful but blocked by a named unknown;
- `PIVOT`: preserve the learning, replace the physical method;
- `REJECT`: falsified, unsafe, or not implementable.

Every decision stores evidence, uncertainty, reversibility, and the next falsification test.

### PUBLISH

- Write the decision to `AGENTIC_STATE.md` and the relevant technical document.
- Create or update one GitHub issue per active decision; do not create duplicate issues.
- Publish through the authenticated GitHub API after checking the remote head.
- Never publish raw coordinates, transcripts, or private calibration data.

### MEASURE

- Use a fixed corpus and fixed protocol per experiment family.
- Keep calibration and evaluation sessions separate.
- Report raw and corrected counts, latency distributions, false activations, uncertainty, and exclusions.
- Record hardware, driver, firmware, dictionary, code, and configuration versions.

## 3A. Cross-project orchestration

The external integration targets are registered in `INTEGRATION_TARGETS.md` as
`REFERENCE_ONLY`; they are not imported runtime components and their current behavior is
never inferred from an unavailable public checkout. The dated `touch-steno`
`SYSTEMKOMPENDIUM.md` snapshot is secondary evidence for the source-side role, not a license
to implement any listed target.

The ownership direction is one-way:

```text
PTH-660 evdev
  -> touch-steno capture, segmentation, [10,5,4] decode, English profile, NACK, sequencing
  -> versioned, process-local, side-specific English steno key/NACK event
  -> commindv2 connection, deduplication, translation/action policy, UI, graph mutation
```

`commind` is a documentation/concept canon and a future semantic/graph reference, not a
runtime authority. Raw contacts never leave touch-steno. commindv2 must not open the same
evdev device or run a second decoder. The archived `input_zones.json` is historical evidence,
never an implicit layout authority or compatibility shortcut.

The closed design proposal is recorded in `INTEGRATION_CONTRACT_V1.md` and is now paired
with the bounded offline validator in `nextgen/contract_v1.py` plus conformance tests. It
defines a `DESIGN`-only, process-local `hello` plus ordered `key`/`nack`/`reset` records,
an epoch, contiguous sequence, opaque event identity, pinned profile/layout fingerprint,
strict privacy allowlist, and fail-closed duplicate, gap, stale-layout, restart, and replay
rejection. The validator is implemented offline; it is not runtime behavior. Freezing the
concrete profile/fingerprint and authorizing an isolated runtime integration remain separate
decisions.

## 3B. Innovation branch registry

The registry is intentionally a research inventory. A branch can be explored in the concept,
mathematics, and evidence ledgers, but it is **never silently implemented** by adding code,
tests, a device reader, or a second decoder. `AGENTIC_STATE.md` must record a branch's status
and evidence class before it can advance.

| Branch | Primitive / hypothesis | Current status | Next falsification or evidence gate |
|---|---|---|---|
| **Simplex-10 transport** (product baseline) | The existing ten-bit transport and one-bit correction contract remain the clean-room English steno baseline. | **IMPLEMENTED PROTOTYPE.** Its finite codec, 32-entry key profile, and Plover-shaped JSON are executable; hardware usability and the proposed process-local envelope remain unproved. | Run the real PTH-660 anatomy, identity, false-commit, posture-drift, and held-out chord study; freeze the exact profile identifier/layout fingerprint before any adapter. |
| **Contact-field / permutation-invariant gesture representation** | Represent a gesture by the shape of its anonymous contact field, aiming to remove contact-ID and finger-order sensitivity while retaining coupled-field information. | **PRIMARY OFFLINE RESEARCH CANDIDATE / HOLD — not human-validated.** The weighted red-team score is 61/100. Ordinary synthetic normalization and permutation/rotation-invariant geometry are implemented, but cardinality, segmentation, timing, palm/rest, confidence, correction, and cross-session layers are missing. | Run the frozen `SYNTH-BRANCH-1` K=8 held-out protocol: require macro recall ≥0.25 above chance with a positive control margin, null wrong commits ≤0.01 upper 95% bound, accepted-event error ≤0.025 at coverage ≥0.80, and ≥80% nuisance-retention. Kill the representation for failed discriminability; hold for failed segmentation/calibration safety gates. |
| **Continuous elastic word-as-event recognition** | Treat one continuous trajectory as an elastic word event, with normalization and confidence-gated rejection rather than letter-by-letter decoding. | **CONTROL/FALLBACK OFFLINE RESEARCH BRANCH / HOLD — synthetic only.** The weighted red-team score is 59/100. Resampling, translation/scale normalization, bounded RMS scoring, and per-template abstention are executable; segmentation, dictionary/OOD decoding, timing, held-out words, and correction are absent. | Run the matching frozen K=8 plus null protocol and recorder-replay test. Require the same chance/safety gates, ≥80% nuisance-retention, and a versioned segmentation/one-repair contract. It cannot become an end-to-end fallback until an anonymous-contact-to-single-writer-path constructor exists. |
| **FCPT / Fitts-cost phoneme targets** | Place phoneme targets to minimize measured transition cost using Fitts-style distance/width terms. | **REJECT CURRENT SELECTABLE-THUMB PRIMITIVE; HOLD ARITHMETIC ONLY.** The weighted red-team score is 48/100, and stable single-contact attribution is a non-compensable veto under the recorded 0-key-event/24-ambiguous-NACK capture condition. Deterministic layout arithmetic is retained, but anatomy, timing, error, correction, and the anatomy penalty are unvalidated. | First test exhaustive 2–4-symbol optimality, intercept invariance, and greedy-versus-exhaustive gaps. For 24 symbols, require ≥5% held-out modeled-cost advantage over row-major and median random in ≥24/27 frozen parameter settings, plus ≥0.75 bootstrap placement overlap. Passing these gates retains arithmetic only; revival still requires a new identity-free input primitive. |

The exact scorecard, hard vetoes, branch risks, kill tests, and shared synthetic protocol are frozen in `BRANCH_REDTEAM.md`. The 61/59/48 totals order offline research only and are not hardware, human, throughput, or product scores. The research priority is `SYNTH-BRANCH-1`; Simplex-10 remains the implemented product baseline pending its own real-device gates.

Branch registration does not change the `EXTERNAL`/`REFERENCE_ONLY` evidence class of the
external repositories and does not authorize imports, device access, or runtime behavior.

## 4. Evidence classes

Every claim carries exactly one class:

1. `DESIGN`: mathematical or architectural proposal;
2. `IMPLEMENTED`: executable code exists;
3. `SYNTHETIC`: deterministic simulation only;
4. `REPLAY`: analysis of an existing capture;
5. `MEASURED`: instrumented hardware result;
6. `HUMAN`: user performance or correction result;
7. `EXTERNAL`: published prior evidence;
8. `RETRACTED`: explicitly withdrawn claim.

A claim may be cited only at its recorded class. `DESIGN` never becomes `MEASURED` because the code passes.

## 5. Ten macro-phases

### Phase 1 — Contract and archive

Freeze the clean-room boundary, archive prior evidence, define privacy rules, and create the state ledger.

### Phase 2 — Broad mathematics

Produce 500 raw concepts with lineage and no implementation commitment.

### Phase 3 — Anatomy and observability

Reject layouts that require unavailable identity, force, pressure, tilt, or visual feedback. Produce anatomy-conditioned reach and coupling models.

### Phase 4 — Steno grammar

Explore English stroke alphabets, syllable grammars, chord algebras, prefix structures, correction strokes, and dictionary boundaries. Keep German steno out of scope.

### Phase 5 — Transport prototypes

Build at least 30 minimal decoders. Include exact finite-state behavior, NACK paths, and replay logs.

### Phase 6 — Error and recovery

Inject missing contacts, extra contacts, palm contamination, delayed release, contact-ID changes, and stale state. Measure recovery rather than assuming it.

### Phase 7 — Integrated prototypes

Promote at most 10 candidates into complete offline pipelines from raw contact frames to steno outline events.

### Phase 8 — Hardware protocol

Run only consented, bounded PTH-660 sessions. Separate rest/palm, reach, sectors, chords, correction, fatigue, and interruption protocols.

### Phase 9 — Product finalists

Select three candidates using the five-axis matrix, implementation risk, evidence class, and a declared weighted decision model.

### Phase 10 — Product candidate

Only a candidate with a reproducible vertical slice, explicit unknowns, recovery path, and honest evidence boundary may be called the product candidate.

## 6. One-loop state ledger

Maintain `AGENTIC_STATE.md` with:

```text
current phase
active candidate
last promoted candidate
last rejected candidate and reason
current evidence class
open falsification test
next executable action
rollback commit/tag
```

The ledger is append-oriented. Corrections are new entries, not silent edits.

## 7. Autonomy policy

The coordinator may autonomously:

- inspect the repository and GitHub;
- create and update issues;
- create commits through the GitHub API;
- add code, tests, documentation, synthetic fixtures, and replay tools;
- run non-destructive tests and simulations;
- reject candidates and close completed issues;
- create reversible tags for major decision points.

The coordinator must not autonomously:

- delete or rewrite raw evidence;
- archive or make the GitHub repository private;
- collect hardware data without explicit consent;
- upload raw contact traces, text, or calibration profiles;
- install system packages or alter device permissions;
- claim Plover, WPM, hardware, or human performance without executed evidence;
- force-push, reset shared work, or overwrite a partner's remote changes.

## 8. Human intervention only for

- physical safety or pain/fatigue stop conditions;
- consent and privacy decisions;
- credentials or destructive repository operations;
- a contradiction between measured hardware behavior and the declared model;
- a product decision that changes the target language, hardware class, or user workflow.

Everything else proceeds autonomously through the loop.

## 9. Throughput and quality targets

The loop is optimized for **evidence gained per risky action**, not raw commit count.

Targets:

- no claim without an evidence class;
- no candidate promoted without a kill test;
- no unresolved failure hidden behind a language model;
- no duplicate GitHub issue for the same decision;
- no stale local publication after a remote change;
- no destructive action;
- every phase ends with a machine-readable test result and a human-readable decision entry.

## 10. Definition of done for a product candidate

A candidate is done only when:

- the physical input method is specified mathematically;
- anatomy and failure assumptions are explicit;
- the English steno outline contract is versioned;
- the offline path is replayable;
- Plover boundary behavior is tested or explicitly unavailable;
- correction and NACK behavior is deterministic;
- privacy and retention rules are implemented;
- synthetic and replay tests pass;
- hardware validation is either passed or explicitly marked outstanding;
- the final document states what is **not** proven.

Until then, the artifact is a prototype, not a product.
