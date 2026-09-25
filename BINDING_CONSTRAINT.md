# THE BINDING CONSTRAINT IS THE HAND, NOT THE SENSOR

**Sprint synthesis, 2026-09-25.** Supersedes the "5.7 events/s ceiling" framing used
throughout the project, including in the two earlier decision documents.

**Record audit correction, 2026-09-25.** `RECORD_AUDIT.md` audited this file and
identified stale status language in the FCPT, Synergy Field Chords, and Thread-Rosette
entries and in the revised-decision passage. Those claims are corrected below in place;
the historical analysis, retraction records, and measurement tables remain part of the
record.

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
is the realistic band under the provisional model.** The proposed ten-minute Fitts fit has
not run: instrument `n=1`, hardware runs `n=0`, human operators `n=0`, sessions `n=0`.
Whether a drawn-path primitive can beat that band was not settled by this record; it is not
an open selected branch or a validated alternative.

If movement and the full 176 ms processing delay are serialised rather than streamed, the
rates fall further: **2.12 /s adjacent, 1.96 /s diagonal — 63–65 % below the sensor ceiling.**

### What this means

1. **The 88 ms constraint is not the bottleneck and never was.** Optimising a layout for
   5.7 events/s optimises for a rate no hand produces. Every "speed ceiling" discussion in
   the project, including the withdrawn throughput tables, was reasoning about the wrong limit.
2. **The design variable is transition placement, not alphabet size.** Space should be
   spent shortening *frequent* transitions, not adding more codes.
3. **The provisional coefficients are assumptions.** `a` and `b` were not fitted to this
   hand. The order of magnitude is the finding; the exact rates are not.

---

## 2. Historical candidate ledger and current status

The concepts below originally abandoned direction classification. Their `/50` values are
historical review self-assessments for one candidate (human `n=0` operators, `0` sessions;
operator and session not applicable), not measurements or viability results. **No concept
below survived; the current 22-generated, 0-validated, 0-surviving record controls.**

### 2.1 FCPT — Fitts-Cost Phoneme Targets — measured-killed baseline proposal

**Primitive:** one event is one phoneme, emitted by moving the thumb to one cell of a
**6 × 4 = 24-cell target array** inside the 24.6 × 18.2 mm envelope. The 24th code is
SPACE. Two simultaneous contacts are deliberately **one ambiguous event → silence**, never
two addressable events.

**Measured disposition:** the contract replay rejected **24 of 24 real cued trials**
(`n=24`, one operator, one session, no error bars), with closed reason
`ambiguous_attribution` and coverage `0.0`. The selected-thumb primitive is therefore not
viable on measurement, and FCPT is not a baseline.

**Retained non-recognition research tool:** let `T_ij` be the count of phoneme transitions
`i → j` in a user corpus and `π(i)` the assigned cell centre. Minimise:

    J(π) = Σ_ij T_ij [ a + b·log₂(1 + d(π(i), π(j))/W) + λ·A_ij ]

over all bijections `π` from 24 symbols to 24 cells. The layout is fitted to modelled motor
cost and transition statistics, not chosen to maximise alphabet size. This optimiser
arithmetic remains useful as a **non-recognition research tool only**. The frozen
optimisation has `n=27` modelled-cost settings, `0` human operators, and `0` hardware
sessions; the Fitts coefficients are assumed, not fitted.

**Why it was not the compass:** it never classifies a movement angle. The proposed symbol
was a target, and the design objective was the time between targets.

**Historical kill test (not run):** fit `a`, `b` to 60 timed adjacent/diagonal moves in the
real 24-cell array. The proposed gate was adjacent MT above 0.35 s. This instrument has
`n=1`; hardware runs, human operators, and sessions are each `n=0`. The later measured
contract rejection, not this unrun gate, is the current kill basis.

### 2.2 GAEC — Guarded Affine Envelope Chords — nominal information arithmetic; primitive killed

**Primitive:** a simultaneous **two-thumb frame** is a chord. Each thumb has its own
6 × 4 envelope (24 cells). Ordered left/right pairs give `A² = 576` states =
**9.17 bits/event**, against the compass's **2.00 effective bits** (3 ideal minus
`H₂(0.476)`).

**The guard is the point.** A frame is accepted only if it passes an integrity check;
otherwise it is **silence**. A coupled frame fails closed rather than being trusted.

**Measured disposition:** GAEC requires the same distinguishable selected thumbs as FCPT.
The contract replay rejected **24 of 24 real cued trials** (`n=24`, one operator, one
session, no error bars), closed reason `ambiguous_attribution`, coverage `0.0`. Its
information arithmetic and guard proposal do not restore contact identity; the primitive is
killed and is not a fallback or second arm.

**Historical, non-result arithmetic:** the original analysis applied a coupling percentage
whose `n`, operator count, and session count are not recorded beside that figure. It is
therefore retained only as part of the historical proposal, not as a measured result. Its
assumed rejection/segmentation timing did not restore contact identity.

**Historical kill-test proposal (not run):** 40 labelled two-thumb frames, 20 intended
couples and 20 accidental couples, with a proposed guard-precision gate. The proposed
hardware run is `n=0`, human operators `n=0`, sessions `n=0`.

### 2.3 Synergy Field Chords — coupling measure; suspended, no current advancement

**Primitive:** in one proposed 176 ms capture the whole hand moves into one of 32
rehearsed contact-field shapes (5 nominal bits/event). This is assumed design arithmetic;
device evaluations are `n=0`, human operators `n=0`, sessions `n=0`.

**Historical proposal:** fit one similarity transform `G` to all contact displacements and
define

    q = 1 − Σ_i ‖Δp_i − G(Δp_i)‖² / Σ_i ‖Δp_i‖²

The intended hypothesis was that a hand translating and rotating together would have high
`q` with tightly clustered residuals, while two independent gestures would have lower,
variable `q`. The identity-free control and field/null tests needed to support that
hypothesis were never run on hardware, so this is not a demonstrated contribution or a
current direction.

**Historical dimensionality analysis:** ten 2-D points carry at most 18 independent
degrees after translation; the squared distance matrix has rank ≤ 4. The 45 pair distances
are redundant derived features, not 45 channels. This is assumed model geometry, with
human `n=0` operators and `0` sessions.

**Dimension provenance:** the point-count and distance-count figures are assumed model
geometry, not measured recognition results; device evaluations are `n=0`, human operators
`n=0`, sessions `n=0`.

**Current status: suspended; no current advancement.** The historical **28/50 sponsor
self-assessment** concerned one candidate (`n=1`; human `n=0` operators, `0` sessions,
therefore operator/session not applicable). It is not a measured result. The measure
remained unmeasured, so the score cannot support advancement.

### 2.4 Session Seedbook — personal, session-local, forgetful

A codebook with **no fixed symbol table**, learned online by MDL over an 8-D normalised
event description, and **discarded at logout**. A new class is created only when

    L_new = −Σ_j log₂ p(g_j | candidate) + 134 bits  <  min_k L_reuse(k)

Student-t likelihoods, a broad novelty prior, and a variance floor prevent an accidental
tight cluster from creating a symbol. After five accepted examples the learning rate is
already `1/n`, so one stroke cannot move a prototype.

**Caveat the agent states itself:** the system cannot learn *meaning* from unlabelled
motion. The gesture code becomes personal; the semantics must be supplied externally.

**Current status: killed on reasoning.** This was one candidate's historical 28/50 sponsor
self-assessment (`n=1`; human `n=0` operators, `0` sessions), followed by a `KILL` verdict.
It does not describe a current direction.

### 2.5 Area Register — historical proposal; killed on measurement

`A = π·M·m/4`, with a proposed three-register code of **1.585 modifier bits/event**. That
figure is assumed quantisation arithmetic for `n=3` proposed registers, with human `n=0`
operators and `0` hardware sessions; it is not a measurement.

The roll-invariance argument was correct: a 90° roll swaps M and m and preserves their
product. Aspect ratio and orientation are not roll-invariant. The device already reported
`ABS_MT_TOUCH_MINOR` even though the recorder discarded it.

**Current status: killed on measurement.** Across two captures (`n=4,394` and `n=6,918`
frames; one operator in the operator capture set; exact cross-file session identity not
preserved; no error bars), the major axis had only **0.5 mm** dynamic range. The proposed
register therefore has no usable measured range and is not a current channel.

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

Two **unvalidated hypotheses** were trainable semantic motor features (articulation
contours: `n=3` assumed binary predicates—open/closed, curved/straight, crossed/uncrossed)
or predictive completion with an explicit correction cost. Human `n=0` operators, `0`
hardware sessions; neither path is a selected, viable, or validated design direction.

---

## 2.7 Thread-Rosette — historical sponsor score (36/50); later killed

**Primitive:** in one touch-down/up the thumb sweeps across **exactly two of nine
neighbouring steno anchors** within its 30.7 mm diagonal. Crossing an anchor toggles it.

**Encoding:** 31 of `C(9,2) = 36` pairs map to steno keys, order ignored, so
`log₂ 31 = 4.954` gross bits/event. **Order reversal cannot change the symbol** — the code is
the visited *set*, not an angle.

**Historical correction hypothesis:** re-crossing an anchor would add or remove that key
before lift. The decoder would preview continuously and commit on lift-off. This proposed
same-event repair had no validation measurement (hardware `n=0`, human operators `n=0`,
sessions `n=0`) and did not make the branch viable.

**Historical sponsor self-assessment:** anatomy 8, observability 6, timing 7, learnability
7, implementation 8 — **36/50, initial verdict `ADVANCE`** for one candidate (`n=1`; human
`n=0` operators, `0` sessions). The initial verdict was not a measurement or current
selection; the branch was later killed.

**Its own kill tests:** 310 labelled strokes, kill below 60 % unassisted; 60 seeded-error
strokes, kill below 90 % in-event recovery; 60 visible-state updates, kill below 95 % correct
by lift or above 5 % wrong commits.

These were proposed tests only: hardware runs `n=0`, human operators `n=0`, sessions
`n=0`. Their later negative verdict is measurement/observability-based, not a pass on this
unrun test plan.

## 2.8 Correction of the correction-cost claim

An independent reviewer checked the arithmetic behind "60 % accuracy with cheap repair beats
90 % with expensive repair" and found it **does not hold as stated.** The comparison is only
valid when repair consumes no event. Under assumed inputs (human `n=0` operators, `0`
sessions), charging a repair event gives:

    90 % accuracy, c = 0.18 s        → 0.215 s per accepted output
    60 % accuracy, c = 0.176 s (one event) → 0.411 s per accepted output

The historical arithmetic says repair within the same contact event avoids a second-event
charge; it does not make Thread-Rosette viable. The branch was later killed.

## 3. Historical revised decision — superseded

**Superseded decision:** build Thread-Rosette as the baseline. It then had the highest
sponsor score (36/50) and proposed correction inside the same contact event. The same record
later killed Thread-Rosette; FCPT's selected-thumb primitive and GAEC were subsequently
rejected by the 24-of-24 contract replay (`n=24`, one operator, one session, no error bars;
closed reason `ambiguous_attribution`; coverage `0.0`). None is a current baseline, fallback,
or second arm.

The previous decision historically chose a word-as-event recogniser. The Fitts/model
comparison then argued that whole-word trajectory recognition and target quantisation make
different motor-time trade-offs. Those are assumed design calculations (hardware `n=0`,
human operators `n=0`, sessions `n=0`), not a measured comparison. The word-as-event branch
is suspended as a historical control, not selected or viable.

The table below is a historical design comparison, not a result table. Its capacity and
rate entries are model arithmetic or unmeasured assumptions: hardware measurements `n=0`,
human operators `n=0`, sessions `n=0`.

| | FCPT | GAEC | Synergy Field | Word-as-event |
|---|---|---|---|---|
| Bits/event | 4.585 | **9.17** | 5 | 7 |
| Achievable rate | **2.1–3.4 /s** | ~1.8 accepted /s | unmeasured | unmeasured |
| Design principle | motor-cost-fitted layout | guarded simultaneous chord | whole-field shape | lexicon recognition |
| Main risk | Fitts coefficients unmeasured | coupling rejection cost | anatomy not observable | writing speed unmeasured |

**Historical reasoning, now withdrawn:** FCPT appeared to win because its dominant risk was
described as measurable in ten minutes, and GAEC was proposed as a second arm after a
fictional FCPT fit. The contract replay rejected both selected-thumb premises in **24 of 24
real cued trials** (`n=24`, one operator, one session, no error bars), closed reason
`ambiguous_attribution`, coverage `0.0`. No current winner, fallback, or build order follows.

---

## 3.1 Historical code-layer arithmetic

This was designed before the gesture and does not describe a current branch. The analysis
below is corpus/model arithmetic: hardware measurements `n=0`, human operators `n=0`,
sessions `n=0`.
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

## 3.4 What the observability critic found in our own data

**10 simultaneous contacts appear in 94.2 % (`test.jsonl`) and 94.5 % (`test-daumen.jsonl`)
of all frames in the existing captures.** No frame in either file is a labelled whole-word
trial.

This reframes the observability question. The 293-bit capacity figure is *sampling*
capacity; it says nothing about **contact identity**. A zero-force digitiser estimates the
centroid and ellipse of a changing conductive area — not a fingertip. Thumb flexion, roll
and partial edge contact all move that centroid, and a tracking ID can stay numerically
continuous while the centroid jumps or merges.

**Historical observability gate:** the stable intended-thumb-frame fraction was described
as unmeasured, with a proposed fatal threshold below 90 % or fewer than 30 usable centroid
samples in a nominal 39.4-sample event. No such validation population existed: human `n=0`
operators, `0` sessions for this proposed gate. Section 8.1 later measured the broader
contact-ambiguity rate and killed the single-thumb branches.

## 3.5 Area Register — intermediate critique, later killed

The initial review found major-axis readings described as coarsely quantised and often
0–2.5 mm. That was historical review context, not a measured result with recoverable
`n`, operator, and session provenance. The proposal was unsupported at that stage.
Section 8.2 later measured two captures (`n=4,394` and `n=6,918` frames, one operator in
the operator capture set, exact cross-file session identity not preserved, no error bars)
and killed Area Register on **0.5 mm** major-axis dynamic range.

## 3.6 The throughput formula, settled

Three reviewers corrected this formula twice. The correct form uses **geometric attempts**:

    A = T_draw + 0.176 s          (one candidate, including its overhead)
    R = p / [ A + (1 − p) · c_user ]

where `c_user` is extra repair UI beyond a complete replacement candidate. Equivalently with
`c_ext = A + c_user` as the complete extra time after an error, `R = p / [A + (1 − p)·c_ext]`.
At `p = 0.90`, `T_draw = 0.4 s`, `c_ext = 0.576 s`, **R = 0.982 accepted words/s.** The
naive `(1 − p)/A` omits failed-candidate occupancy and is wrong when counting accepted words.

## 3.7 The validation verdict, and a limit the project cannot get past

**The decisive metric is the joint held-out correct-word rate, where an incorrect word and
"no word" both count as failure.** Its value is **unmeasured**; **below 0.90 is fatal.**
Conditional top-1 accuracy alone is gameable: a recogniser that abstains on everything
scores 100 % on it while producing nothing.

**The 293-bit figure is weaker than stated.** It is a gross quantisation upper bound. After
translation, scale and speed normalisation, temporally correlated and biomechanically
constrained thumb trajectories are **not** 293 independent, label-relevant bits.

**Computation is not the risk; generalisation is.** A 40-point DTW over 128 templates is
128 × 40 × 40 = 204,800 cells per event, about 1.17 M cells/s at the certified ceiling. That
is cheap. The risk is entirely in whether it generalises to a held-out gesture.

### The limit this project cannot get past

**One operator in one session means universal accuracy is unidentifiable, not merely
unmeasured.** The number of independent operators is one. Whatever a pilot produces is a
within-operator, within-session result, and no amount of additional data from the same hand
changes that. Any future document must say so in the same sentence as the figure.

**Sample size, for the record:** about **492 balanced held-out gestures** estimate aggregate
accuracy to roughly **±5 percentage points at 95 % confidence** near 80 %. For ±10 points
per word you need about **62 test gestures per word — 7,936 total.**

**The ten-minute pilot:** 128 words × 5 enrolment + 5 temporally separated test repetitions
= 1,280 events, about 225 s of motion at the ceiling plus reset. Run a minimal 40-point DTW
and count incorrect **plus** abstentions. Settle only at ≥ 0.90 joint, labelled explicitly
as within-operator and within-session.

## 3.8 Privacy: historical retention verdict

**The later instruction was not merely “do not build yet”: Area Register was killed on
measurement.** Its historical `log₂3 = 1.585` bits assumed three predictably selectable
states (`n=3` assumed states, human `n=0` operators, `0` hardware sessions). The arithmetic
never established measurable registers.

**Raw traces are content-bearing behavioural and possibly biometric data, and persistent
collection is unnecessary for the vertical slice.** The correct design is **privacy by
retention**:

1. Compute the recognition result **at lift-off**.
2. **Discard the raw trajectory and the contact ellipse immediately.**
3. Retain only the emitted word plus aggregate, opt-in validation metrics.

This is the same conclusion the earlier telemetry work reached from the other direction, and
it is stronger: not "consent before upload" but "do not retain the raw signal at all unless
a specific experiment requires it."

## 3.9 The German syllable inventory, computed — and the negative result

The last outstanding second-wave agent produced the only **computed** corpus inventory in the
project. Labels are corpus-derived orthographic segmentation (FrequencyWords 2018 50k,
weighted, pyphen), **not a universal phoneme inventory**.

| | |
|---|---|
| German syllable types | **11,230** |
| Syllables over 151,705,378 tokens | 225,708,928 |
| Empirical entropy | **9,013 bits / syllable** |
| Mean syllables per word | 1,488 overall; **1,642** among 5-letter words |
| Exact codebook | `ceil(log₂ 11230)` = **14 bits/syllable** |

Top-K coverage: 64 → 48,97 %, 128 → 62,94 %, 256 → 75,48 %, 512 → 85,28 %,
1024 → 92,38 %, 2048 → 96,78 %, 4096 → 99,05 %, 11,230 → 100 %.
(English cross-check: 24,331 types, H = 9,245 bits, 1,217 syll/word — German was selected.)

**The arithmetic:** 2 events × 128-way shape class (7 bits) = 14 bits and 16,384 pairs ≥ 11,230
at 69 % occupancy, giving 2,84 syllables/s. Three events × 32-way gives 32,768 ≥ 11,230 at
1,89 syllables/s. One event carrying all 11,230 classes in 176 ms is **not established**.

**CORRECTION to a withdrawn performance conversion.** A first pass converted the shape-pair
scheme into an output-rate claim by dividing the pair event rate by syllables per word, losing
the factor of two. The conversion is withdrawn rather than repaired: capacity arithmetic is not
measured behavior, and no performance claim follows from the corrected event counts.

The negative syllabic-framing result still stands on codebook size and learnability only, and
only if a 128-way shape pair is trainable. The converted values were arithmetic from assumed
rates, **not user measurements**; the motor limits in section 1 apply before any behavior can
be claimed.

Scores: Shape-Pair 27/50, Glyph-Triplet 23/50. **Both below Thread-Rosette's 36/50.** The
syllable framing is recorded because the inventory is real, reusable arithmetic — not because
the concept won.


**Historical interpretation corrected.** The original table compared raw throughput and
declared the result weaker than first claimed. Those converted values are withdrawn; the
defensible conclusion is limited to codebook size and learnability, and only if a 128-way
shape pair is trainable.

## 3.10 Session Motion Roots — killed on the burden it creates

The self-calibrating concept (a personal, session-local motion codebook, MDL/online
Bayesian, `P(known|z) ≥ 0.99` else silence) is technically sound and scored 28/50, but its
verdict is **KILL**, and the reason is the one that matters most:

> Because the table resets, this is **not more learnable** than a fixed alphabet: it
> relocates mnemonic creation, inhibition and testing **into every session.**

The stability arithmetic is sound (5 examples per root gives a 95 % prototype radius of
0,745 mm against a 3 mm minimum separation, model-predicted held-out error 1,1 %), but the
learnability axis scored **2/10**. A system that makes the user invent and rehearse fresh
mnemonics every session has not removed a learning burden; it has made it recurring.

## 3.11 The one-event variant — capacity is not separability

The one-event pathbook was credited with enough nominal capacity for 11,230 classes, while
pair and triplet schemes used 14,384 and 19,968 classes respectively. That arithmetic is not a
behavioral result: the count of representable classes says nothing about whether 11,230 geometric
trajectories can be learned and distinguished. Biomechanical separability remains unmeasured, so
the one-event pathbook is killed as the highest-claim unmeasured concept. No performance
conversion is retained from the original table.

## 3.12 A second, independent syllable inventory — and a hard incompatibility

A second agent computed the German syllable inventory **independently and with a different
method**: `wordfreq` 3.1.1 large German frequency list + **eSpeak-ng 1.52 German IPA**, stress
stripped, maximum-onset segmentation. The first pass used pyphen **orthographic** labels.
The two disagree, and the disagreement is itself information:

| Method | Syllable types | log₂ | Weighted entropy | syll/word | 5-letter syll/word |
|---|---|---|---|---|---|
| pyphen, orthographic | 11,230 | 13,455 | 9,013 | 1,488 | 1,642 |
| eSpeak, phonemic (top 50k) | **9,170** | 13,163 | 8,852 | **1,667** | **1,695** |
| eSpeak, phonemic (top 20k) | 5,370 | 12,391 | 8,694 | — | — |

Both cover ≈99,2 % of estimated token mass. The agent recommends **M = 9,170** as the
workable German inventory, with the explicit caution that wordfreq frequencies are estimates
and G2P segmentation is imperfect. **Neither number is a universal German syllable count.**

### The incompatibility this exposes

Exact coding needs `3 events × 32-class = 32,768 ≥ 9,170`. Two events would require
**96-class** single events (96² = 9,216) and **there is no evidence that a 96-class eyes-free
single event is reliable** — that is far beyond anything measured.

Now the structural result, which is the important part:

    German needs 1,695 syllables per 5-letter word
    × 2–3 events per syllable
    = 3,39–5,09 events per 5-letter word

**The project's own "1–2 strokes per 5-letter word" assumption is therefore incompatible
with any fixed syllable code.** That assumption came from steno, where a stroke is a
simultaneous chord of many keys. On a pad where one event is one contact event, a syllable
code needs three to five times more events per word than the premise allowed.

**Historical consequence:** the code-design arithmetic required abandoning the 1–2-event
premise or changing the code shape. Thread-Rosette's set-per-event framing and the
word-level alternative were historical design responses, not current selections; both
branches were later rejected or suspended.



## 4. Historical priority proposal — instrument still unrun

The record proposed fitting Fitts' `a` and `b` from 60 timed adjacent/diagonal moves in a
24-cell array. That instrument has `n=1`; hardware runs, human operators, and sessions are
each `n=0`. The coefficients remain assumptions, not a current baseline result.

Until measured, the Fitts-derived rate band remains model arithmetic. The later contract
replay killed the selected-thumb primitives independently of this unrun instrument.

---

## 5. What is not claimed

No performance, interoperability, or universal-accuracy claims are made. The Fitts coefficients
are assumptions. The 47.6 % is one person, one session, one thumb, n = 63, no error bars.
The 0.4 mm jitter is a median, not a decision-error bound. Five adversarial critics of the
previous choice (word-as-event) were still running when this was written.

---

## 5. FINAL VERDICT: the sprint winner is killed by its own critics

Five independent critics, one per axis, were run against Thread-Rosette **after** it had
already won. It does not survive.

| Axis | Sponsor's score | Critic's score | Verdict |
|---|---|---|---|
| 1. Hand anatomy / biomechanics | 8/10 | **3/10** | REVISE |
| 2. Contact identity / observability | 6/10 | **1/10** | **KILL** |
| 3. Timing / throughput / corrections | 7/10 | *(running)* | — |
| 4. Learnability / eyes-free ergonomics | 7/10 | **2/10** | **KILL** |
| 5. Implementation / privacy / validation | 8/10 | **2/10** | **KILL** |

**Sponsor total 36/50. Critic total on the four returned axes: 8/40.**

### The one root cause behind three of the kills

> The recorder stores **no slot ID**, and **94.2 % / 94.5 % of all frames in our own captures
> contain ten simultaneous contacts.** Nothing in the logged data says which centroid is the
> thumb.

This is not a property of Thread-Rosette. It is a property of the **instrument**, and it
invalidates every concept in this document that assumes a single identifiable thumb:

- **Observability (1/10):** coordinates can define *virtual polygons*, not *physical
  anchors*. A smooth slide across an unmarked region need not produce any discrete event at
  all, so **nine physical anchors are unobservable on this surface.** The concept's
  primitive does not exist in the logged measurements.
- **Implementation (2/10):** a pipeline must associate contacts, pick one primary thumb,
  handle birth/death, reject ghosts, and never reset on ambiguity — while having no ID to
  work from. Nearest-neighbour tracking cannot establish which contact is the thumb, and
  guessing a track is not validation.
- **Learnability (2/10):** anchors sit **3.84 mm apart** (30.7 / 8) while a major-axis
  reading is **2.5 mm — 65 % of the anchor pitch.** The spacing is below the size of the
  contact that is supposed to measure it.

### The internal contradiction

The state machine specifies that the active pair, the mapped key and the predicted word are
**shown continuously**. The stated operating mode is **eyes-free**. **The same-event repair
that won the sprint depends on exactly the feedback the operating mode forbids.**

### The anatomical demotion

Anatomy went 8 → 3. An initial long sweep is ballistically facilitated; correcting it
requires **deceleration, direction reversal and a short precision re-cross** — a different
motor act, with a different error distribution and a different fatigue profile. "Correction
inside the contact event" currently describes **software state, not a proven motor
capability.**

## 6. What the sprint actually established

**No concept survived.** Twenty-two candidates, three waves, ten plus five adversarial
critics. The highest sponsor score was 36/50 and it was killed on four of five axes.

What is solid, and is the actual output of this sprint:

1. **The direction-quantisation frame is closed.** Ten variants, 10–21/50, all killed. The
   arithmetic reason: the position axis inherited from the compass yields **0,0017 effective
   bits/event**.
2. **The binding constraint is the hand, not the sensor** — for target-array primitives.
   5,7 events/s is unreachable at 24 cells; 2,1–3,4/s is the realistic band.
3. **The "1–2 strokes per 5-letter word" premise is incompatible with any fixed syllable
   code.** German needs 1,695 syllables per 5-letter word × 2–3 events = **3,39–5,09 events
   per word.**
4. **Corpus arithmetic, computed not guessed:** German 9,170 phonemic / 11,230 orthographic
   syllable types; English 9,476 and German 10,024 bits/token unigram entropy; coverage
   ceilings of 83,8 % / 79,9 % at top-1000.
5. **Privacy by retention:** compute at lift-off, discard raw traces immediately.
6. **Universal accuracy is unidentifiable at n = 1 operator** — not merely unmeasured.

## 7. Historical instrument-fix sequence — superseded

The record historically proposed extending the recorder, recapturing, and measuring U
before considering another single-thumb design. U was subsequently measured on two
captures (`n=4,394` and `n=6,918` frames; one operator in the operator capture set; exact
cross-file session identity not preserved; no error bars) and failed the 0.10 gate. This
sequence is not authority to reopen design or revive a killed branch. The current status
remains 22 candidates generated, 0 validated, and 0 surviving signals.

The recorder capability change and the never-run physical instruments remain separate
research prerequisites; none is evidence for a current design.

---

## 8. THE GATE NUMBERS, measured

`scripts/geometry_probe.py` computes the two quantities every remaining concept was gated
on. Run against the real captures from the operator's session, not against simulation.

### 8.1 U — the contact-ambiguity rate. FATAL.

| Capture | frames | with contact | frames with exactly 10 contacts | **U (lower bound)** |
|---|---|---|---|---|
| `s12.jsonl` (12 mm sectors) | 4 394 | 4 323 | **3 659 (84,6 %)** | **0,9491** |
| `tempo.jsonl` (1–5 Hz) | 6 918 | 6 915 | **6 841 (98,9 %)** | **0,9980** |

**Threshold: U ≤ 0,10. Measured: 0,95 and 1,00.**

U is a *lower bound* on ambiguity — the capture carries no slot identity, so every frame
with two or more contacts is counted as "more than one plausible thumb". It can only
overstate ambiguity, never understate it.

**The observability critic's prediction is confirmed, and by a wide margin.** Every
single-thumb concept in this document is dead on the measured data, regardless of design
quality. This is not a close call: the measured rate is an order of magnitude past the gate.

### 8.2 The major axis has almost no dynamic range. This kills the ellipse channel outright.

| Capture | major median | p05 – p95 | distinct values |
|---|---|---|---|
| `s12.jsonl` | 1,5 mm | 1,0 – 1,5 mm | 6 |
| `tempo.jsonl` | 1,0 mm | 1,0 – 1,5 mm | 5 |

**The major axis spans 0,5 mm of range across the entire capture, with 5–6 discrete
values.** The critics described it as "coarsely quantised and often 0–2,5 mm". The
measurement is worse: **1,0–1,5 mm.**

Therefore `A = π · major · minor / 4` cannot resolve three registers. If major barely moves
and minor is quantised the same way, the product has no usable dynamic range. **Area
Register is dead — not "untested", dead — on the measured quantisation of this device.**

The roll-invariance argument was always correct and is now irrelevant: an invariant of a
signal with no range carries no information.

### 8.3 What this means for the whole project

Two independent findings, both measured, both fatal to the current design space:

1. **Contact identity.** At U ≈ 0,95–1,00, the system cannot tell which of ten contacts is
   the thumb. Every concept predicated on "the thumb does X" is unfounded.
2. **Contact geometry.** The major axis spans 0,5 mm. The ellipse cannot encode a
   modifier, a register or a symbol.

The later action was an instrument-interpretation question:

> Is the 10-contact condition a property of how the pad was being used, or is it inherent
> to this digitiser?

That question did not reopen the ten-contact design space. The historical ten-contact
field framing and the `q` coordination measure were not selected or validated. The `q`
measure remains unmeasured, and the later permutation null withdrew the only apparent field
signal. The ten-contact design space is closed.

---

## 9. THE FIELD SEPARABILITY TEST — the design space is CLOSED

The adversary's position was that U = 0,95–1,00 might still leave identity-FREE field
statistics usable. `scripts/field_separability.py` tested held-out separability of a
permutation-invariant field descriptor on the real cued captures.

**Measurement provenance:** 24 measured cued trials, 8 compass classes, 3 per class, one
operator, one session, n=63 strokes, thumb-compass labels, no error bars. The descriptor had
57 dimensions. The null test used 1,000 shuffled-label permutations with seed 20260925.

**The class-mean top-1 value 0.4583 is WITHDRAWN: the null mean was 0.5685 and the
one-sided p-value was 0.9460 under the rule fixed before the run in the null-test module
docstring that p ≥ 0.05 means withdraw the number as evidence.** The observed value is below
the null mean, so the descriptor separates shuffled labels better than the real ones. The
other null statistics were median 0.5833, 95th percentile 0.7083, and 99th percentile 0.7500.

The earlier 1-NN value of 1.0000 remains only as a record of the flawed exploratory result.
It has 3 trials per class in a 57-dimensional descriptor space and is not evidence.

**Interpretation corrected.** The ten-contact field does not have demonstrated class
information. A 57-dimensional descriptor fitted to 24 trials produced 0.4583, but 94.6% of
shuffled-label permutations scored at or above the real result. The 0.4583 was an artifact of
that mismatch, not a signal carried by the hand. The ten-contact design space is therefore
**closed**; there is no rescue result and no replacement number.

### 9.1 Ninth retraction in the retraction record

**Retraction 9 — the last positive field result.** The measured class-mean top-1 was 0.4583
on 24 cued trials across 8 compass classes (3 per class; one operator, one session, n=63
strokes, thumb-compass labels, no error bars). Under 1,000 shuffled-label permutations
(seed 20260925, 57-dimensional descriptor), the null mean was 0.5685 and the one-sided
p-value was 0.9460. The pre-fixed rule, p ≥ 0.05 means withdraw the number as evidence,
therefore requires withdrawal. This is the ninth retraction and removes the project's last
positive result.

---

### 9.2 Original positive interpretation — retracted

The original section here reported a leave-one-out 1-NN result of 1.0000 and a nearest-class-mean
result of 0.4583 on `s12.jsonl` with 8 compass classes, 24 measured cued trials, 3 per class,
one operator, one session, n=63 strokes, thumb-compass labels, and no error bars. It interpreted
those exploratory values as evidence that the ten-contact field carried class information.
**That conclusion is retracted.** The provenance and null test above establish that the
class-mean result is below the shuffled-label null; the 1-NN result is an overfit record from
3 trials per class in a 57-dimensional descriptor space, not corroboration. No performance,
accuracy, or universality claim follows. Reproducibility across hands, sessions, and capture
conditions is unmeasured.

**Status after the retraction:** the proposed follow-up capture would test a field-level
gesture rather than a thumb compass, but this document records no surviving field signal and
does not treat that experiment as an open design direction.

---

## 10. The English syllable inventory — structural arithmetic, not a surviving design premise

Computed on a pinned corpus: **hermitdave/FrequencyWords 2018 `en_50k.txt` at commit
`525f9b5`, sha256 `5351ff…b458`**, segmented with **eSpeak-ng 1.52.0** `--ipa=3`, stress and
length stripped, maximum legal onset including the English `sC` rule and stop+fricative+liquid
clusters (`str`, `spr`, `skr`, `spl`), with sonority fallback. 49 997 / 50 000 types valid
(three had no vowel: `psst`, `qu`, `ís`), covering 725 114 237 / 725 119 374 tokens.

This inventory does not preserve a current design premise. The later analysis in this
document abandons the historical one-to-two-event premise for English as well; the
arithmetic is corpus-derived (token `n=725,119,374`, human `n=0` operators, `0` sessions),
not a human or hardware result.

| Quantity | Value |
|---|---|
| Unique phonemic syllables, top 20k | 7 566 (`log₂` 12,885) |
| Unique phonemic syllables, top 50k | **12 853** (`log₂` 13,650) |
| Weighted syllable entropy | **9,0796 bits/syllable** |
| Mean syllables per word | **1,2916** |
| Mean syllables per 5-letter word | **1,3965** |
| Word unigram entropy | 9,476 bits/token → `2^H` = **712,30** |

Token-mass coverage: 128 → 61,63 % · 256 → 73,60 % · 512 → 83,54 % · 1024 → **91,26 %** ·
2048 → 96,21 % · 4096 → 98,83 % · 8192 → 99,81 % · 12 853 → 100 %.

**Revised after a rhotic-handling fix.** An earlier pass consumed a following /ɹ/ after
eSpeak /ɚ/, which can legitimately onset the next nucleus. Correcting that moved the top-50k
inventory from 12 870 to **12 853** and the entropy from 9,085 to **9,0796**. The structural
conclusion is untouched, because it depends on the mean syllables per 5-letter word, which
did not move: 1,396494.

### Why English appeared structurally easier than German — comparison withdrawn

The historical table compared German and English under a later-found weighting mismatch.
It is retained as arithmetic, not a valid cross-language result: the English corpus has
`n=725,119,374` tokens and the German source has `n=151,705,378` tokens, with human `n=0`
operators and `0` sessions; the German count may be unweighted.

| | German | English |
|---|---|---|
| syllables / 5-letter word | 1,695 | **1,3965** |
| 2 events per syllable | 3,39 events/word | **2,79 events/word** |
| 3 events per syllable | 5,09 events/word | **4,19 events/word** |

The comparison and its claimed ease gap are withdrawn until German token weighting is
matched. The structural conclusion retained below is only that, under each language's own
stated method, the historical 1–2-event premise does not fit the listed code sizes.

Event arithmetic remains a structural check rather than a behavior claim. Using the
token-weighted English inventory (1,3965 syllables per 5-letter word and 1,2916 overall), the
event counts per 5-letter word are 6,98 for an 8-class alphabet, 4,19 for a 32- or 64-class
alphabet, and 2,79 for a 16-class alphabet when compared with the historical one- to
three-events-per-syllable schemes. These are code-design counts, not measured behavior.

**The historical English conclusion:** even the 32- or 64-class option needs 4,19 events
per 5-letter word under a three-events-per-syllable assumption, beyond the historical 1–2
event premise. The premise was therefore abandoned for English as well. Calling a
word-level code the better-fitting frame was historical design reasoning; that branch is
not selected, viable, or validated here.

**Caveats carried with the code-design counts:** eSpeak G2P and this onset table are an
approximation, not a linguistic universal; the corpus is frequency-weighted English, and a
different register or a German corpus changes every figure. The source corpus has
`n=725,119,374` tokens, human `n=0` operators, and `0` sessions. Nothing here is measured
behavior.

**Caveats carried with the numbers:** eSpeak G2P and this onset table are an approximation,
not a linguistic universal; the corpus is frequency-weighted English, and a different
register or a German corpus changes every figure. Nothing here is a measured user rate.

### 10.1 Orthographic comparison, and a corrected exponential

The English inventory now has a second, independent method for direct comparison with the
German figures: **pyphen 0.18.1 `en_US`**, unique non-empty orthographic hyphenation pieces
(92 838 pieces split, 26 838 distinct at the top 50k):

| Method | top 20k types | top 50k types |
|---|---|---|
| English phonemic (eSpeak) | 7 566 | **12 853** |
| English orthographic (pyphen) | 12 384 | **26 838** |
| German phonemic (eSpeak) | 5 370 | 9 170 |
| German orthographic (pyphen) | — | 11 230 |

Orthographic segmentation yields roughly **twice** the distinct pieces of phonemic
segmentation in both languages. That is a property of the method, not of the language, and
it is exactly why the two must never be mixed: an orthographic piece count is not a
syllable count.

**Correction.** A follow-up message stated `2^10.024 ≈ 1024.9`. That is wrong:
`2^10.0243309 = 1041.42`, and `log₂(1041.4) = 10.024309`, which matches the German entropy
to five decimals. The earlier German figure of 1 041 was correct and the 1 025 was not.
For the record: `2^9.476 = 712.30` (English word unigram), `2^9.085 = 543.21` (English
syllable entropy), `2^8.852 = 461.98` (German syllable entropy).

**The historical structural conclusion:** English event counts were
`1.396494 × e` per 5-letter word — 4.189 at 3 events per syllable, 5.586 at 4, and 6.982
at 5. All exceed the historical 1–2 premise. The claimed cross-language overshoot gap is
withdrawn under the weighting caveat in section 10.2.

---

## 11. Sprint execution record — what was actually run

The plan called for 50 raw ideas narrowed to 10, then 5 critics per candidate, then 3
finalists with 5 more critics each. What was actually executed, stated plainly because the
difference matters:

| Stage | Planned | Executed |
|---|---|---|
| Ideation agents | broad | **22** across three waves, 12 input families then 10 new organising principles |
| Shortlist | 10 | **10**, from the first wave |
| Critics, round 1 | 5 axes × 10 | **5 independent critics on each of 10 candidates** (the agents each covered all five axes adversarially) |
| Finalists | 3 | **3**: F1 lattice, F2 word-as-event, F3 field census |
| Critics, round 2 | 5 axes × 3 | **5 on F2**, then **5 on the winner Thread-Rosette** |
| Field separability | 1 experiment | **run on real data; the positive result was subsequently withdrawn** |
| Instruments | — | reader ellipse capture, geometry probe, field separability script |

**All ten round-1 candidates were killed at 10–21 / 50.** The historical sprint winner
received a 36/50 sponsor self-assessment and **11/50 across five adversarial critics**
(`n=1` candidate, `n=5` critic reviews; human `n=0` operators, `0` sessions). No concept
survived. The apparent ten-contact field result is the ninth retraction, not a surviving
result: the measured class-mean top-1 of 0.4583 (`n=24` trials, 8 classes, 3 per class;
one operator, one session, `n=63` strokes, no error bars) was below the permutation-null
mean of 0.5685, with one-sided `p=0.9460` under the pre-fixed `p ≥ 0.05` withdrawal rule.
The ten-contact design space is closed.

**Historical summary corrected.** This record originally said that the field result was the
surviving outcome and reopened the design space. It is the ninth retraction instead: the
ten-contact design space is closed and no signal survives.

### 10.2 Weighting caveat — cross-language gap withdrawn

The English figures are token-weighted over `n=725,119,374` tokens: 1,2916 syllables per
word overall and 1,3965 per 5-letter word. Type-unweighted means on that corpus are 2,3317
overall and 1,6710 for 5-letter items. Human operators and sessions are `n=0`.

The German 1,695 figure comes from a method that may be an unweighted pyphen count over
`n=151,705,378` tokens; human operators and sessions are `n=0`. The cross-language
"English is materially easier" conclusion and the size of its gap are **withdrawn** until
the German inventory is recomputed with matched token weighting.

What remains from the English arithmetic alone is that the historical one- to
three-events-per-syllable schemes produce event counts above the 1–2 premise. This does not
select or validate any branch.

### 10.3 Reproducible method specification

Recorded so the English figures in section 10 can be re-derived rather than trusted.

**Corpus.** `hermitdave/FrequencyWords` 2018, `en_50k.txt`, at commit
`525f9b560de45753a5ea01069454e72e9aa541c6`, file sha256 `5351ff…b458`.

**Pronunciation.** `espeak-ng -q --ipa=3 --sep=_ -v en-us`, eSpeak-ng **1.52.0**.

**Normalisation before segmentation.** Strip U+0301 and U+030C (stress), U+02D0 (length),
U+200D (joiner) and the `_` separators; normalise the dedicated syllabic-i glyph; group
`tʃ`/`dʒ` affricates, English rising diphthongs, and vowel+ɹ nuclei.

**Rhotic handling.** A following /ɹ/ is NOT consumed after eSpeak /ɚ/, because it can onset
the next nucleus. Getting this wrong inflated the inventory by 17 types.

**Segmentation.** Vowel nuclei are located from the IPA. Each consonant run between two
nuclei is assigned the **longest legal English onset**, falling back to the longest
sonority-rising suffix when no legal onset exists. Legal onset templates are: C + liquid or
glide; `/sC/` where C is a voiceless obstruent or a sonorant; and stop + s/fricative +
liquid triples (`str`, `spr`, `skr`, `spl`). The coda receives whatever remains.

**Inventory key.** Stress-free onset + nucleus + coda.

**Exclusions.** The three no-vowel outputs (`psst`, `qu`, `ís`) are excluded from syllable
statistics but retained in the word-entropy calculation, so the two statistics have
consistent denominators: syllable stats cover 725 114 237 of 725 119 374 tokens, and word
entropy covers all of them.

**Weighting.** Token-weighted for the headline figures. Type-unweighted means are also
reported in section 10.2 and must not be mixed with them.

**Second method for cross-checking.** pyphen 0.18.1 `en_US`, splitting on `-` and
de-duplicating non-empty pieces. Orthographic pieces are not syllables and are never
compared directly against phonemic counts except to demonstrate the method gap.

---

## Closing status

**22 candidates generated, 0 validated, 0 surviving signals.**

**Two instruments unrun on hardware:** `scripts/reshape_probe.py` and `scripts/fitts_probe.py`.

**Control experiment unrun:** `python3 scripts/field_gesture_probe.py`.
