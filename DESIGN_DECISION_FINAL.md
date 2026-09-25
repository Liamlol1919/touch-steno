# FINAL DESIGN DECISION (SUPERSEDED) — three finalists, one vertical slice

**Sprint:** 2026-09-25, 22 ideation agents across three waves, 10 independent five-axis
critics, 50+ scored critique passes.
**Predecessor:** the direction-quantisation frame was closed in the previous document —
10 candidates, 10–21 / 50, every one killed.

**STATUS: SUPERSEDED. No finalist in this document was selected for build, and no
fallback survives.** The selection (F2) and the fallback (F1) were both killed later the
same day. The comparison, the scores and the reasoning are kept unedited because a
decision that was made and then overturned is part of the record; only the passages that
present the selection, the fallback or the vertical slice as live have been corrected.

**Correction note — 2026-09-25, added after `RECORD_AUDIT.md` section 3.** The audit found
this document still presenting (a) a live selection — "DECISION: build F2, keep F1 as the
fallback" — and (b) a live fallback — "F1 stays the fallback … a working 5-bit-per-event
system". Neither exists in the current record. The project closed at **22 candidates
generated, 0 validated, 0 surviving signals**, and the two branches this document ranks
first are both on the kill register (`KILLED_BRANCHES.md`).

---

## The three finalists

All three abandon direction classification. They differ in *what an event is*.

### F1 — Epoch 4×2 Space–Time Lattice

**Primitive:** the thumb selects one of 16 cells in a 4×4 grid inside its natural
24.6 × 18.2 mm envelope, while the *onset phase* inside a repeating 176 ms epoch selects
one of 2 slots.

**Encoding:** `log₂(16 × 2) = 5.00 bits/event`. Exact 32-token code table (A–Z, space,
backspace, enter, escape, cancel, silence). Rate ceiling 5 × 5.68 = **28.4 payload bits/s**.

**State machine:** ARMED tracks the epoch phase and the hand-aligned origin. A cell is
committed only if the timing error is under **44 ms**; otherwise the decoder emits silence.

**The arithmetic that matters:** the E and L phase centres are 88 ms apart, leaving 44 ms to
each boundary. For 1 % phase error you need motor timing σ_t ≤ **18.9 ms**; for 0.5 % you
need ≤ 17.1 ms. **No σ_t has ever been measured on this hand.** The 0.4 mm median is a
position statistic and says nothing about timing.

**Confidence: MEDIUM-LOW.** The code table is exact and the concept is fully buildable, but
it requires learning a 4×4 grid — which collides with the "no arbitrary learned positions"
constraint — and its eyes-free viability is unargued.

### F2 — Continuous Elastic Token (word-as-event)

**Primitive:** the thumb makes **one continuous pen-down → pen-up gesture that spells a
whole word**. The gesture is never classified as a direction, letter or digit.

**Encoding:** one event → one word. The decoder stores the full 224 Hz trajectory,
normalises translation, scale and speed, resamples to 40 points, and ranks a template
dictionary at lift-off. `log₂(128) = 7 bits/event` → **39.8 bits/s**.

**The capacity margin:** one event is 39.4 samples. A conservative 1.6 mm coordinate grid
gives 7.45 raw bits/sample = **293 bits per event**, against the 7 bits a 128-word
vocabulary needs. The raw path carries roughly **40× the required information**.

**Why that margin is not yet a result:** consecutive trajectory samples are strongly
correlated, motor repeatability across repetitions is unmeasured, and the natural envelope
is not a guaranteed signal power. The defensible statement is *"a path contains hundreds of
raw bits per event, far above what a phoneme or word code needs"* — **not** that 293 bits
are available to a decoder.

**State machine:** pending trajectory only. No cross-event state, no inter-letter
segmentation. The boundary is lift-off, which is unambiguous on this hardware.

**The critical design decision:** **"no word" is a first-class output.** Below a confidence
floor the decoder emits nothing and the user does not advance. A bad recognition becomes a
rejection, not a confident wrong word.

**Confidence: LOW-MEDIUM.** Unmeasured, and the recogniser does not exist.

### F3 — Full Contact Field Census

**Primitive:** one simultaneous 10-contact state is **one** observation — a 40-D vector of
ten (x, y, major-axis) triples plus ten occupancy bits. No contact is decoded separately.

**Encoding:** a session codebook over occupancy patterns; 64 tokens = 6 coded bits/event,
**34.2 coded bits/s**. A linear head extracts weighted coordinate, major-axis and occupancy
contrasts.

**Honest dimensionality statement:** ten 2-D points carry at most 18 independent degrees
after translation; the squared distance matrix has rank ≤ 4 in 2-D. The 45 pair distances
are **redundant derived features, not 45 independent channels.** A linear classifier cannot
represent pair distances, angles, products or nearest-neighbour identity.

**The variant that treats coupling as signal:** Coupled-Edge Tensor uses the ring–little
edge as the intended feature instead of an error. **It has the weakest foundation of the
three** — the pad reports contacts, not anatomy, so "ring and little" must be approximated
by nearest-same-hand-outer-pair, and the concept may collapse into a disguised rest-pose
detector.

**Confidence: LOW.**

---

## Scoring against the five axes

| Axis (max 10) | F1 Lattice | F2 Word-as-Event | F3 Field Census |
|---|---|---|---|
| 1. Hand anatomy / biomechanics | 6 | **8** | 5 |
| 2. Contact identity / observability | 5 | **7** | 4 |
| 3. Timing / throughput / corrections | 4 | 6 | 5 |
| 4. Learnability / eyes-free | 3 | **7** | 4 |
| 5. Implementation / privacy / validation | **8** | 7 | 6 |
| **Total / 50** | **26** | **35** | **24** |

**Score provenance — read this before using the table.** These are **sponsor
self-assessments**, one scored candidate per column (`n=1` candidate, human `n=0`
operators, `0` sessions, operator and session not applicable). They are review scores, not
measurements, and they are not evidence of viability. The adversarial reviews produced
different numbers and **both sets are retained, unharmonised**: F1 is recorded as `26/50`
here and `25/50` in `BINDING_CONSTRAINT.md` (a one-point discrepancy the record keeps
rather than resolves); F2 additionally has a later static red-team research-priority total
of `59/100`; F3 has `24/50` here and a later static red-team research-priority total of
`61/100` (different scale, `n=1` candidate, human `n=0`). The clearest warning comes from
the sprint winner Thread-Rosette, which the same record scored `36/50` on sponsor
self-assessment and `11/50` across five adversarial critics (`n=1` candidate, `n=5`
critics, human `n=0`) — and which was then killed by measurement. **A score is not a
viability result.**

**As scored here, F2 was the only finalist that cleared 30, F1 was the most *buildable*,
and F2 the most *promising*; they were expected to fail differently — F1 on learnability,
F2 on everything being unmeasured.** That ranking is retained as history. It is not a
viability statement: later critics and the kill register rejected **both** selected-contact
primitives. F1 (Epoch 4×2 Space–Time Lattice) and F2 (Continuous Elastic Token) are both
listed in `KILLED_BRANCHES.md`, and F3's recorded implementation was rejected by
measurement and audit. None of the three is a live direction.

---

## The decision as it was made on 2026-09-25 — overturned the same day

> **The selection recorded below did not stand, and no successor selection was made.**
> Nothing here was built. The project closed at 22 candidates generated, 0 validated,
> 0 surviving signals.

**Selection as recorded (superseded):** build F2, keep F1 as the fallback.

**Vertical slice as recorded (killed):** one stroke, one word, lexicon-constrained, with a
confidence floor and an explicit no-word outcome. The one-stroke-one-word concept was
later carried forward as `VERTICAL_SLICE.md` and is **KILLED** by the permutation null
test on its only supporting evidence — the withdrawn class-mean `0.4583`, against a
permutation null mean **0.5685** with one-sided **p = 0.9460** (1,000 permutations, seed
20260925, descriptor dimension 57; from `n=24` measured cued trials, 8 compass classes, 3
per class, one operator, one session, `n=63` strokes, thumb-compass labels, no error bars).
The null test lives in `scripts/field_null_test.py`. See `KILLED_BRANCHES.md` retraction 9
and `MEASURED_REJECTION.md`.

**Why F2 was chosen over F1, despite F1 scoring lower on confidence** — the reasoning as it
stood on 2026-09-25, retained unedited. It is a record of the argument, not a defence of
it; reason 1 and reason 2 in particular are contradicted by the later gate measurements,
which showed the measured contact-ambiguity bound `U = 0.9491` and `U = 0.9980` against a
`0.10` gate (gate captures of `n=4,394` and `n=6,918` frames, one operator in the operator
capture set, no error bars), closing every concept that needs to know **which** contact
moved:

1. **It is the only candidate whose primitive is a motor skill the user already owns.**
   Every other finalist asks the hand to learn an arbitrary code. F2 asks it to write.
2. **It respects the no-arbitrary-positions constraint.** F1's 4×4 grid does not.
3. **Its kill test is unambiguous and cheap.** Draw 30 uncued common words, one pen-down
   each. **More than 2 wrong kills it.** Pausing or backtracking to define letter boundaries
   also kills it — that is the signature of a recogniser that is not doing the work.
4. **Its information margin is the largest and is quantified**, even if the usable fraction
   is unknown.
5. **Its failure mode is the recoverable one.** Rejection is recoverable; a confident wrong
   word is not.

**The fallback as recorded (no fallback exists).** F1 was argued to stay the fallback
because it had an exact code table, needed no recogniser, and could be "built and measured
in an afternoon", so that "if F2's handwriting recogniser fails, F1 is a working
5-bit-per-event system". **Both of those claims are withdrawn.** F1's lattice primitive
was **killed by measurement** (`KILLED_BRANCHES.md`): it inherited the compass position
axis, on which the record calculates only `0.0017` effective bits/event, and it also
requires an arbitrary learned grid. Its `5.00 bits/event` figure is therefore capacity
arithmetic, not a working system, and F1 is not a fallback. A code table is not an
operational channel; the same kill register holds the instructive parallel — Thread-Rosette
scored `36/50` on sponsor self-assessment and `11/50` across five adversarial critics
(`n=1` candidate, `n=5` critics, human `n=0`) and was killed by measurement, because the
recorder stores no slot identity (`94.2%` of `n=3,845` frames in `test.jsonl` and `94.5%`
of `n=1,643` frames in `test-daumen.jsonl` show ten simultaneous contacts).

---

## The vertical slice as specified — KILLED, specification preserved

> **Status: KILLED.** The one-stroke-one-word concept was killed by the permutation null
> test on its only supporting evidence, not by its own specification. It is preserved here
> as a record of what was designed and of a decision that was later overturned. It must
> not be cited as evidence that the design works, and it is not a live design surface.

| Component | Decision |
|---|---|
| Primitive | one pen-down → pen-up gesture = one whole word |
| Decoder | 224 Hz trajectory → normalise (translation, scale, speed) → resample 40 points → rank a 128-template dictionary |
| Event boundary | lift-off; unambiguous, no inter-letter segmentation |
| No-word outcome | **first-class**; below confidence floor, emit nothing and do not advance |
| Correction | a word-level recogniser allows whole-word replacement; correction cost is unmeasured and must be logged from the first run |
| Second channel | contact ellipse area `A = π·major·minor/4` as a **state modifier**, not a symbol. Roll-invariant, structurally immune to the 180° error. The device already reports `ABS_MT_TOUCH_MINOR`; the recorder currently discards it. |

**Provenance of the rows above:** every decoder figure in that table (224 Hz trajectory, 40
resampled points, 128-template dictionary, `39.8 bits/s` ceiling) is a **design assumption
and capacity arithmetic** — `0` human operators, `0` sessions, `0` measured runs of the
decoder. No run of this decoder exists. The **second channel** row is additionally
**killed by measurement**: the contact-ellipse area was rejected after the gate captures
showed a major-axis dynamic range of only **0.5 mm** (`n=4,394` and `n=6,918` frames, one
operator in the operator capture set, no error bars); see `KILLED_BRANCHES.md` and
`MEASURED_REJECTION.md`.

### The three killing tests, in order

1. **First-pass recognition, no feedback, no retry.** 30 uncued common words, one
   pen-down. **Kill if >2 words wrong, or if the user pauses or backtracks to define
   letter boundaries.**
2. **Resting-hand observability.** 8 × 10 with the other fingers and palm resting.
   **Kill if >5 % of strokes lose usable trajectory continuity.**
3. **Ellipse separability, offline replay.** 3 min resting, 4 min of 20 curl/release
   repetitions, 3 min median/MAD threshold. **Kill the ellipse channel if fewer than
   18/20 repetitions cross the same hysteresis band, or if resting frames cross it.**

**Execution status of these three tests: none of them was executed.** No execution record
for the first-pass recognition test, the resting-hand observability test or the ellipse
separability replay exists in the current root records (`n=0` runs, `0` operators, `0`
sessions for all three). They are retained as the pre-registered plan that was never
carried out; the concept was instead closed by the gate measurements and the null test.

**The later acceptance test ran and returned void.** The successor acceptance test,
`scripts/field_gesture_probe.py`, was executed on **2026-09-25** with
`--seconds 3 --reps 2`: 20 cues, **0 frames captured**. A direct five-second read of
`/dev/input/event19` returned **0 events** with the device openable and no process holding
it — the pad was empty. The capture is therefore **void, not failed**, and the tool
reported exactly that. **No acceptance-test result exists**: the concept is killed by the
permutation null test (null mean `0.5685`, one-sided `p = 0.9460`,
`scripts/field_null_test.py`), not by an acceptance-test pass or fail. Full account in
`VERTICAL_SLICE.md` §10 and `KILLED_BRANCHES.md`; the control experiment
`scripts/field_gesture_probe.py` itself is **not killed** and has never produced a verdict,
and the separate `reshape_probe.py` and `fitts_probe.py` instruments have never been run
on hardware.

---

## What is explicitly not claimed

- **No WPM.** Never measured. The 28–40 bits/s figures are capacity ceilings, not typing
  rates.
- **No seconds-per-correction.** Absent from the literature and unmeasured here.
- **No Plover integration.** The path to text is a template/lexicon decoder, not Plover.
- **No universal accuracy.** The 47.6 % is one person, one session, one thumb, n = 63,
  with no error bars.
- **No selected finalist.** None of F1, F2 or F3 is selected for build. F1 and F2 are
  killed (`KILLED_BRANCHES.md`); F3's recorded implementation was rejected by measurement
  and audit. The comparison and its scores survive as history only.
- **No fallback.** F1 is not a working 5-bit-per-event system and not a fallback. Its
  lattice primitive was killed on measurement; `5.00 bits/event` is capacity arithmetic
  over an axis the record values at `0.0017` effective bits/event.
- **No scores as evidence.** The five-axis table is a sponsor self-assessment
  (`n=1` candidate, human `n=0` operators, `0` sessions). Adversarial reviews produced
  different numbers and both sets are retained unharmonised.
- **The 0.4 mm jitter is motor variation, not a sensor specification**, and it is not a
  decision-error bound.
- **The 293 bits/event figure is raw observation capacity**, not usable information.
  Temporal correlation and motor repeatability are unmeasured.
- **The F3 coupled-edge variant is likely a rest-pose detector** in disguise. Recorded
  here so nobody builds it thinking it is an anatomy decoder.

## Open items the second wave did not close

Nine of the second-wave agents were still running when this document was written. Their
subjects — syllable inventories, chord algebra, motor-control/Fitts modelling, self-
calibrating codebooks, correction-cost crossover, learnability theory — may produce concepts
that beat F2. **This decision is made on completed work, not on the whole search.**

**Closing status (2026-09-25, after `RECORD_AUDIT.md` section 3).** The open items above
did not produce a surviving concept either. The second wave closed at **22 candidates
generated, 0 validated, 0 surviving signals**: the last positive result, the class-mean
`0.4583` field separability, was withdrawn by the permutation null test (null mean
`0.5685`, one-sided `p = 0.9460`, 1,000 permutations, seed 20260925, descriptor dimension
57, from `n=24` measured cued trials, 8 compass classes, 3 per class, one operator, one
session, `n=63` strokes, thumb-compass labels, no error bars;
`scripts/field_null_test.py`). **This document selects nothing and authorises nothing.**
It is kept because the selection was made, and then overturned, and that history has to
stay visible.
