# FINAL DESIGN DECISION — three finalists, one vertical slice

**Sprint:** 2026-09-25, 22 ideation agents across three waves, 10 independent five-axis
critics, 50+ scored critique passes.
**Predecessor:** the direction-quantisation frame was closed in the previous document —
10 candidates, 10–21 / 50, every one killed.

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

**F2 is the only finalist that clears 30.** F1 is the most *buildable*; F2 is the most
*promising*. They fail differently: F1's weakness is learnability, F2's is that everything
about it is unmeasured.

---

## DECISION: build F2, keep F1 as the fallback

**Vertical slice:** one stroke, one word, lexicon-constrained, with a confidence floor and
an explicit no-word outcome.

**Why F2 over F1, despite F1 scoring lower on confidence:**

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

**Why F1 stays the fallback:** it has an exact code table, needs no recogniser, and can be
built and measured in an afternoon. If F2's handwriting recogniser fails, F1 is a working
5-bit-per-event system with a defined code, and its single unknown — motor timing σ_t — is
measurable in ten minutes.

---

## The vertical slice, concretely

| Component | Decision |
|---|---|
| Primitive | one pen-down → pen-up gesture = one whole word |
| Decoder | 224 Hz trajectory → normalise (translation, scale, speed) → resample 40 points → rank a 128-template dictionary |
| Event boundary | lift-off; unambiguous, no inter-letter segmentation |
| No-word outcome | **first-class**; below confidence floor, emit nothing and do not advance |
| Correction | a word-level recogniser allows whole-word replacement; correction cost is unmeasured and must be logged from the first run |
| Second channel | contact ellipse area `A = π·major·minor/4` as a **state modifier**, not a symbol. Roll-invariant, structurally immune to the 180° error. The device already reports `ABS_MT_TOUCH_MINOR`; the recorder currently discards it. |

### The three killing tests, in order

1. **First-pass recognition, no feedback, no retry.** 30 uncued common words, one
   pen-down. **Kill if >2 words wrong, or if the user pauses or backtracks to define
   letter boundaries.**
2. **Resting-hand observability.** 8 × 10 with the other fingers and palm resting.
   **Kill if >5 % of strokes lose usable trajectory continuity.**
3. **Ellipse separability, offline replay.** 3 min resting, 4 min of 20 curl/release
   repetitions, 3 min median/MAD threshold. **Kill the ellipse channel if fewer than
   18/20 repetitions cross the same hysteresis band, or if resting frames cross it.**

---

## What is explicitly not claimed

- **No WPM.** Never measured. The 28–40 bits/s figures are capacity ceilings, not typing
  rates.
- **No seconds-per-correction.** Absent from the literature and unmeasured here.
- **No Plover integration.** The path to text is a template/lexicon decoder, not Plover.
- **No universal accuracy.** The 47.6 % is one person, one session, one thumb, n = 63,
  with no error bars.
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
