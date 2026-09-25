# THE BINDING CONSTRAINT IS THE HAND, NOT THE SENSOR

**Sprint synthesis, 2026-09-25.** Supersedes the "5.7 events/s ceiling" framing used
throughout the project, including in the two earlier decision documents.

---

## 1. The finding that reorganises the project

The project has treated **~88 ms detection + ~88 ms segmentation = 5.7 events/s** as *the*
speed limit. It is not. It is a ceiling the hand can never reach.

Applying Fitts' law to a thumb moving between targets inside the measured
**24.6 × 18.2 mm** natural envelope, with provisional coefficients
`a = 0.150 s`, `b = 0.120 s/bit`, `ID = log₂(1 + D/W)`:

| Transition | Distance D | Target width W | ID | Movement time | Event rate |
|---|---|---|---|---|---|
| Adjacent cell | 4.0 mm | 3.0 mm | 1.222 | 0.2967 s | **3.37 /s** |
| Diagonal neighbour | 5.66 mm | 3.0 mm | 1.529 | 0.3335 s | **3.00 /s** |
| Farthest corner | 23.3 mm | 3.0 mm | 3.133 | 0.5260 s | **1.90 /s** |
| All 576 pairs equally likely | — | 3.0 mm | — | 0.3917 s | 2.55 /s |

**To reach 5.7 events/s the movement time would have to be ≤ 0.176 s.** For a 4 mm adjacent
target that requires `ID ≤ 0.2167`, hence

    W ≥ 4 / (2^0.2167 − 1) = **24.7 mm**

— a single target wider than the entire 24.6 mm envelope, with 24 targets required.

### RETRACTION of the word "impossible"

An independent reviewer supplied the counter-argument, and it is correct: **Fitts' law prices
the time to *aim at* a target, not the time to *draw a curved path*.** The W ≥ 24.7 mm result
therefore bounds **target-to-target aiming** — the FCPT geometry — and does **not** bound
concepts whose primitive is a drawn form rather than a target hit. A parametric loop drawn
from a common home with a large effective target width is a different motor problem and Fitts
does not settle it.

The corrected claim: **for a 24-cell target array, 5.7 events/s is unreachable and 2.1–3.4/s
is the realistic band.** Whether a drawn-path primitive can beat that band is **open** and
requires the same ten-minute Fitts fit plus a separate drawing-time measurement. I stated a
conclusion where an assumption about the primitive was required; that was wrong.

If movement and the full 176 ms processing delay are serialised rather than streamed, the
rates fall further: **2.12 /s adjacent, 1.96 /s diagonal — 63–65 % below the sensor ceiling.**

### What this means

1. **The 88 ms constraint is not the bottleneck and never was.** Optimising a layout for
   5.7 events/s optimises for a rate no hand produces. Every "speed ceiling" discussion in
   the project, including the withdrawn WPM tables, was reasoning about the wrong limit.
2. **The design variable is transition placement, not alphabet size.** Space should be
   spent shortening *frequent* transitions, not adding more codes.
3. **The provisional coefficients are assumptions.** `a` and `b` were not fitted to this
   hand. The order of magnitude is the finding; the exact rates are not.

---

## 2. What survives, and what each buys

Every concept below abandons direction classification. Scores are out of 50 on the
five-axis contract.

### 2.1 FCPT — Fitts-Cost Phoneme Targets — **the new baseline**

**Primitive:** one event is one phoneme, emitted by moving the thumb to one cell of a
**6 × 4 = 24-cell target array** inside the 24.6 × 18.2 mm envelope. The 24th code is
SPACE. Two simultaneous contacts are deliberately **one ambiguous event → silence**, never
two addressable events.

**The optimiser — this is the novel part.** Let `T_ij` be the count of phoneme
transitions `i → j` in a user corpus and `π(i)` the assigned cell centre. Minimise

    J(π) = Σ_ij T_ij [ a + b·log₂(1 + d(π(i), π(j))/W) + λ·A_ij ]

over all bijections `π` from 24 symbols to 24 cells. The layout is **fitted to motor cost
and transition statistics**, not chosen to maximise alphabet size. That is a different
organising principle from anything the project has used.

**Why it is not the compass:** it never classifies a movement angle. The symbol is a
*target*, and the design objective is the *time between* targets.

**Kill test (10 min):** fit `a`, `b` to 60 timed adjacent/diagonal moves in the real 24-cell
array. **Kill if the fitted adjacent MT exceeds 0.35 s** — that would put the rate below
2.9/s and make any density argument moot.

### 2.2 GAEC — Guarded Affine Envelope Chords — the highest information rate

**Primitive:** a simultaneous **two-thumb frame** is a chord. Each thumb has its own
6 × 4 envelope (24 cells). Ordered left/right pairs give `A² = 576` states =
**9.17 bits/event**, against the compass's **2.00 effective bits** (3 ideal minus
`H₂(0.476)`).

**The guard is the point.** A frame is accepted only if it passes an integrity check;
otherwise it is **silence**. A coupled frame fails closed rather than being trusted.

**The honest cost:** the project's 68 % involuntary-coupling figure means accepting only
~32 % of frames. At 5.7 events/s that is **1.82 chords/s**, and 1.82 × 9.17 = **16.7
useful bits/s** — still better than the compass's 2.00 bits/event, but only if rejection
happens *before* the 176 ms segmentation cost is paid. If rejection is post-segmentation,
the rate is not survivable for steno-like density.

**Kill test:** 40 labelled two-thumb frames, 20 intended-couples and 20 coupled
accidentally. **Kill if guard precision < 95 % at a rejection rate that leaves fewer than
1.5 accepted chords/s.**

### 2.3 Synergy Field Chords — the coupling test made measurable

**Primitive:** in one 176 ms capture the whole hand moves into one of 32 rehearsed
contact-field shapes. 5 nominal bits/event.

**The contribution is the measure, not the alphabet.** Fit one similarity transform `G` to
all contact displacements and define

    q = 1 − Σ_i ‖Δp_i − G(Δp_i)‖² / Σ_i ‖Δp_i‖²

A hand translating and rotating together has **high `q` with tightly clustered residuals**;
two independent gestures have lower, variable `q`. **This is the first concrete test in the
project that can distinguish "the hand moved as one" from "two independent gestures"** —
which every bimanual concept has needed and none had.

**Honest dimensionality:** ten 2-D points carry at most **18 independent degrees** after
translation; the squared distance matrix has **rank ≤ 4**. The 45 pair distances are
redundant derived features, not 45 channels.

**Score 28/50, verdict ADVANCE.**

### 2.4 Session Seedbook — personal, session-local, forgetful

A codebook with **no fixed symbol table**, learned online by MDL over an 8-D normalised
event description, and **discarded at logout**. A new class is created only when

    L_new = −Σ_j log₂ p(g_j | candidate) + 134 bits  <  min_k L_reuse(k)

Student-t likelihoods, a broad novelty prior, and a variance floor prevent an accidental
tight cluster from creating a symbol. After five accepted examples the learning rate is
already `1/n`, so one stroke cannot move a prototype.

**Caveat the agent states itself:** the system cannot learn *meaning* from unlabelled
motion. The gesture code becomes personal; the semantics must be supplied externally.

### 2.5 Area Register — the one usable discarded channel

`A = π·M·m/4`, three registers (short/ordinary/long) = **1.585 modifier bits/event**.

**It is the only contact-ellipse concept that is roll-invariant by construction**: a 90°
roll swaps M and m and preserves their product. Aspect ratio is *not* (a roll gives `1/r`);
orientation is *not* (a roll moves it two bins and produces a wrong symbol).

**The device already reports `ABS_MT_TOUCH_MINOR`; the recorder discards it.** No new driver
code is needed — the parser drops it today. None of the three geometry features is
certified for a cold or sweaty hand.

### 2.6 The false premise, stated by the learnability analysis

> A near-zero-learning encoder **cannot** be simultaneously eyes-free and high-density
> without accepting wrong text.

The project's implicit premise — *learn once, then high-density eyes-free arbitrary text* —
requires one of: substantial motor training, vision, or prediction-with-confirmation.
A fair 8-output comparison gives 3 bits/symbol in **every** case; what differs is the
learning cost, not the information. Direction, shape and finger identity each need 8
bindings. Timing needs 8 labels *plus 7 ordered thresholds* — **15 landmarks, 1.875 per
emitted symbol** — and is prohibited as input. Semantics remove the *arbitrary* codebook but
never the motor-to-text association.

Two viable paths exist: **trainable semantic motor features** (articulation contours: three
binary predicates — open/closed, curved/straight, crossed/uncrossed — giving 3 bits from
three *reusable* rules instead of eight arbitrary sectors), or **accept predictive
completion with an explicit correction cost**.

---

## 2.7 Thread-Rosette — the highest-scoring concept of the sprint (36/50)

**Primitive:** in one touch-down/up the thumb sweeps across **exactly two of nine
neighbouring steno anchors** within its 30.7 mm diagonal. Crossing an anchor toggles it.

**Encoding:** 31 of `C(9,2) = 36` pairs map to steno keys, order ignored, so
`log₂ 31 = 4.954` gross bits/event. **Order reversal cannot change the symbol** — the code is
the visited *set*, not an angle.

**The correction insight, which is the real contribution:** re-crossing an anchor **adds or
removes** that key *before lift*. The decoder previews continuously and commits only on
lift-off. **A wrong key is repaired inside the same contact event**, so correction costs no
additional event — which is exactly the condition under which low raw accuracy can beat high
raw accuracy.

**Scores:** anatomy 8, observability 6, timing 7, learnability 7, implementation 8 —
**36/50, verdict ADVANCE.** Highest of every concept generated in this sprint.

**Its own kill tests:** 310 labelled strokes, kill below 60 % unassisted; 60 seeded-error
strokes, kill below 90 % in-event recovery; 60 visible-state updates, kill below 95 % correct
by lift or above 5 % wrong commits.

## 2.8 Correction of the correction-cost claim

An independent reviewer checked the arithmetic behind "60 % accuracy with cheap repair beats
90 % with expensive repair" and found it **does not hold as stated.** The comparison is only
valid when repair consumes no event. Charging a repair event:

    90 % accuracy, c = 0.18 s        → 0.215 s per accepted output
    60 % accuracy, c = 0.176 s (one event) → 0.411 s per accepted output

**90 % wins.** The "low accuracy plus cheap repair" advantage exists only for repairs that
happen *within* the same contact event. Thread-Rosette is the concept that earns that
advantage by construction; concepts that spend an event on repair do not have it.

## 3. Revised decision

**Build Thread-Rosette as the baseline.** It scores highest (36/50) and, unlike every other
concept, its correction mechanism is *inside* the same contact event rather than a second
event. FCPT remains the strongest target-array fallback; GAEC carries the most information
per event and becomes a second arm once Fitts coefficients are fitted.

The previous decision chose a word-as-event recogniser. The Fitts analysis undermines it:
a recogniser that must resolve a whole word's trajectory competes for exactly the motor
time that makes the word recognisable, and the crossover calculation for the continuous
channel shows that below **≈7.1 Hz** of independent shape bandwidth — plausible for smooth
thumb paths — **trajectory coding loses to quantised targets even before vocabulary errors**.

| | FCPT | GAEC | Synergy Field | Word-as-event |
|---|---|---|---|---|
| Bits/event | 4.585 | **9.17** | 5 | 7 |
| Achievable rate | **2.1–3.4 /s** | ~1.8 accepted /s | unmeasured | unmeasured |
| Design principle | motor-cost-fitted layout | guarded simultaneous chord | whole-field shape | lexicon recognition |
| Main risk | Fitts coefficients unmeasured | coupling rejection cost | anatomy not observable | writing speed unmeasured |

FCPT wins because its dominant risk is **measurable in ten minutes**, and because it is the
only concept whose design objective is the actual binding constraint. GAEC carries the most
information per event and should be built as a **second arm** once FCPT's fitted `a` and `b`
exist — its guard logic is reusable.

---

## 3.1 The code layer, designed before the gesture

An independent information-theory pass produced the layer that sits under any of the above:
an **arithmetic code over a 1.6 mm cell lattice**, sized from the hand, not from convenience.

- 1.6 mm ≈ 4× the measured 0.4 mm median jitter, inside the 24.6 × 18.2 mm envelope, gives
  **15 × 11 = 165 cells** = **7.366 bits/event** (at 3× jitter: 300 cells, 8.229 bits;
  at 2×: 660 cells, 9.366 bits).
- **Measured corpus entropies, not guesses:** English unigram **9.476 bits/token**
  (725,119,374 tokens), German **10.024 bits/token** (151,705,378). One-event uniform
  vocabulary therefore needs `2^9.476 = 712` English or `2^10.024 = 1041` German entries —
  **more than 165 cells**, so rare words need a 3-event code: `165³ = 4,492,125`.
- **Coverage is the real limit:** English top-1000 covers 83.8 % of tokens, top-5000 covers
  93.7 %; German top-1000 79.9 %, top-5000 91.2 %. No one-event scheme covers general text.
- Variable-length chunks preserve entropy: a syllable at p = 0.1 costs 3.322 bits, p = 0.01
  costs 6.644, p = 0.001 costs 9.966.

**Honest limit the author states:** the actual information is
`5.7 · [log₂ M − H(symbol | decoded)]`, and without a confusion matrix the conditional
entropy is unknown. The supplied facts **cannot identify** the usable capacity. The numbers
above are planning arithmetic, not a measurement.

## 3.2 A space-time lattice is dead, and the arithmetic says why

The space-time lattice (position × onset phase) scored 25/50 and was killed. The kill is
worth recording because it is arithmetic, not opinion: the measured compass accuracy of
47.6 % gives `H₂(0.476) = 0.9983`, so the position axis contributes
`1 − 0.9983 = 0.0017` effective bits/event. **Any concept that inherits a position axis from
the compass inherits essentially zero information on that axis**, no matter how cleverly the
time axis is added.

## 3.3 Two further self-corrections, recorded

- **Critic3Timing corrected its own formula.** Steady-state word rate is
  `R = 1 / [T_draw + 0.176 + p · c_ext]`, not `(1−p)/(T_draw+0.176)`. With `T_draw = 0.8 s`
  and zero UI tail, `p = 0.10` gives 0.901 word/s and `p = 0.50` gives 0.735. The qualitative
  objection stands; the formula did not.
- **NewInformationTheory corrected its own exponentiation.** `2^9.476 = 712.3` and
  `2^10.024 = 1041.4`, not 716.8 and 1071.6. Contextual English 4.62 bits/word gives
  `2^4.62 = 24.6`, German 6.5 bits gives 90.5.

## 4. The measurement that now has top priority

**Fit Fitts' `a` and `b` for this thumb in this array.** 60 timed moves, adjacent and
diagonal, inside the real 24-cell layout. Ten minutes. Everything above rests on provisional
coefficients, and this is the one number that determines whether any of it is real.

Until it is measured, the honest statement about this project is: **the hand is slower than
the sensor, by a factor that has never been measured.**

---

## 5. What is not claimed

No WPM. No seconds-per-correction. No Plover. No universal accuracy. The Fitts coefficients
are assumptions. The 47.6 % is one person, one session, one thumb, n = 63, no error bars.
The 0.4 mm jitter is a median, not a decision-error bound. Five adversarial critics of the
previous choice (word-as-event) were still running when this was written.
