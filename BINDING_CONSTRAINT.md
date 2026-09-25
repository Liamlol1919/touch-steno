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

## 3.4 What the observability critic found in our own data

**10 simultaneous contacts appear in 94.2 % (`test.jsonl`) and 94.5 % (`test-daumen.jsonl`)
of all frames in the existing captures.** No frame in either file is a labelled whole-word
trial.

This reframes the observability question. The 293-bit capacity figure is *sampling*
capacity; it says nothing about **contact identity**. A zero-force digitiser estimates the
centroid and ellipse of a changing conductive area — not a fingertip. Thumb flexion, roll
and partial edge contact all move that centroid, and a tracking ID can stay numerically
continuous while the centroid jumps or merges.

**The number that decides observability: the stable intended-thumb-frame fraction.** Its
value is **unmeasured**. Fatal below **90 %**, or with fewer than **30 usable centroid
samples** inside a nominal 39.4-sample event.

**The minor axis is recoverable live at each 224 Hz `SYN_REPORT` with no extra latency —
but not retrospectively from existing JSONL.** The recorder has to change before it can be
measured.

## 3.5 The Area Register is weaker than claimed

The same review found that **current major-axis readings are coarsely quantised and often
0–2.5 mm.** If major itself spans only a few millimetres in 0.5 mm units, then
`major × minor` is **not yet a credible three-level modifier.** The roll-invariance argument
is correct; the claim that the product resolves into short/ordinary/long registers is
currently unsupported. Area Register moves from *proposed* to *untested and possibly
unresolvable with this hardware's current quantisation*.

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

## 3.8 Privacy: the verdict is retention, not collection

**Do not build the area modifier yet.** `log₂3 = 1.585` bits assumes three predictably
selectable states; with unmeasured, unlabelled thresholds it is only quantisation
arithmetic, and tripling the class count can destabilise an already-unknown base recogniser.

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

**CORRECTION to a figure the author itself withdrew.** A first pass reported ≈52 WPM for the
shape-pair scheme. That was wrong: it divided the pair event rate by syllables/word and lost
the factor of 2. The correct comparison against the stated "1–2 strokes per 5-letter word"
ceiling (`5.682 × 60 = 341` WPM at one stroke/word, `170.5` at two):

| Scheme | events / 5-letter word | arithmetic WPM |
|---|---|---|
| Shape-Pair (2 events) | 1,642 syll/word × 2 = 3,284 | **103,8** |
| Shape-Pair, general text | 1,488 × 2 = 2,976 | **114,6** |
| Glyph-Triplet (3 events) | 1,642 × 3 = 4,927 | **69,2** |
| Glyph-Triplet, general text | 1,488 × 3 = 4,464 | **76,4** |

**The negative result survives the correction but is weaker than stated:** syllable framing
still does not reach one-event word codes in raw throughput (104–115 WPM against a 341 WPM
arithmetic ceiling). It may only win on **codebook size and learnability**, and only if a
128-way shape pair is genuinely trainable. All of these are arithmetic ceilings at the
certified event rate, **not** user rates — the motor limits in section 1 apply on top.

Scores: Shape-Pair 27/50, Glyph-Triplet 23/50. **Both below Thread-Rosette's 36/50.** The
syllable framing is recorded because the inventory is real, reusable arithmetic — not because
the concept won.

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

## 3.11 The one-event variant, and the complete WPM ladder

The agent's final split separates three regimes, and the first one changes the picture:

| Scheme | bits/event | capacity | WPM, 5-letter | WPM, general |
|---|---|---|---|---|
| **One-event Pathbook** — one geometric trajectory per syllable | 14 | 11,230 exactly | **207,7** | **229,2** |
| Onset-Coda Pair — two 128-way path classes | 7+7 | 16,384 | 103,8 | 114,6 |
| Glyph-Triplet — three 32-way classes | 15 | 32,768 | 69,2 | 76,4 |

**The one-event case has enough capacity.** 11,230 classes from ~39 samples is arithmetically
possible, and it reaches 207,7 WPM on the 5-letter subset — well above the pair scheme. The
agent's own caveat is the whole answer: **biomechanical separability across 11,230 path
templates is unmeasured**, and it is very likely that one event is not realistic at the full
inventory. This is the concept to kill first, because it is the one carrying the highest
claim.

The explicit hardware ceiling from the project's own "1–2 strokes per 5-letter word"
assumption is **341 / 170,5 WPM**, independent of how words are segmented into syllables.

**Every figure in this table is an arithmetic ceiling at the certified event rate, not a
user rate.** Section 1's motor limits apply on top of all of them, and none has been
measured on this hand.

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

**Consequence:** any design in this space must either abandon the 1–2 stroke premise,
adopt a chord-style event where one frame carries a set, or use a word-level code instead of
a syllable-level one. Thread-Rosette is a **set-per-event** design and therefore sits on the
right side of this constraint; fixed syllable codes do not.

**WPM ceilings, all arithmetic at 5,7 events/s and all invalid as user rates:** 1 event → 202,
2 events → 101, 3 events → 67 WPM for the 5-letter average.

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
  primitive does not exist in the hardware.
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

## 7. The next action is an instrument fix, not a design

Every remaining concept is blocked on the same missing signal. Before any further design
work:

1. **Extend the recorder** to store **slot/tracking ID, minor axis and orientation.** The
   device already reports all three; the parser discards them. This cannot be done
   retrospectively — the existing JSONL does not contain it.
2. **Recapture** with the hand in a known, labelled pose.
3. **Measure U**, the fraction of event frames with more than one plausible thumb. The
   observability critic's threshold: **U ≤ 10 %** is required; above that every
   single-thumb concept is dead regardless of design.
4. **Only then** re-open design.

**Any concept proposed before step 1 is arithmetic about a sensor that cannot report what
the concept needs.**

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

The next action is therefore **not** another design round. It is a hardware-claim question
that only the operator can answer, and it should be asked before any further design work:

> Is the 10-contact condition a property of how the pad is being used — a resting hand
> placed flat, with the thumb among nine other contacts — or is it inherent to this
> digitiser? A ten-finger rest is a legitimate ergonomic choice, but it means the input
> method must be built for a **ten-contact field**, not for a single thumb. Every
> single-thumb concept in this document, including the sprint winner, was answering a
> question the device was never being asked.

The `q` coordination measure from section 2.3 — distinguishing a hand that moved as one
from two independent gestures — is the only approach in this document that was designed for
a ten-contact field rather than against it. It remains unmeasured and is now the most
promising surviving direction precisely because it stops pretending there is one thumb.

---

## 9. THE FIELD SEPARABILITY TEST — the design space is NOT dead

The adversary's position was that U = 0,95–1,00 might still leave identity-FREE field
statistics usable, and that the decisive test is held-out class separability of a
permutation-invariant field descriptor, with the field code killed if the upper 95 %
confidence bound sits at or below chance.

`scripts/field_separability.py` runs exactly that test, offline, on the real cued captures.

**The descriptor is permutation-invariant by construction:** sorted radii from the centroid,
the sorted pairwise-distance multiset, the occupancy bounding-box aspect, and log contact
count. It never uses contact order, TID, major axis, minor axis or orientation — precisely
the quantities the gate measurements disqualified.

**Result on `s12.jsonl`, 8 sector classes, 24 cued trials, chance 12,5 %:**

| Classifier | top-1 | upper 95 % |
|---|---|---|
| leave-one-out 1-NN | 1,0000 | 1,0000 |
| **nearest class mean (the honest one)** | **0,4583** | **0,6212** |

**The nearest-class-mean result is 45,8 % against a 12,5 % chance level, with an upper 95 %
bound of 62,1 % — comfortably and significantly above chance.**

The 1-NN figure of 1,0000 is reported for completeness and should **not** be trusted: with
3 trials per class in a high-dimensional descriptor space, 1-NN can overfit. The
class-mean classifier is the lower-variance estimate and it is the one to believe.

**Interpretation.** The ten-contact field **does carry class information**, even though no
individual contact is identifiable. A single-thumb design is therefore not the only option,
and the pessimistic reading of the gate numbers was too strong: U rules out *identity*
channels, not *field* channels.

**How the information is carried, almost certainly:** the field descriptor is
translation- and rotation-free, yet still separates eight directional classes, so the
discriminating structure must be the *shape the whole field takes* when the thumb moves
within it — a deformation of the ten-point cloud that is detectable without knowing which
point is the thumb. That is exactly the property the `q`-style coordination measure was
designed to capture, and it is now demonstrated rather than hypothesised.

**What this does NOT license.** n = 24 trials, 3 per class, one hand, one session, one
capture. The labels are directional cues the user performed as a thumb compass, so the
field descriptor may be exploiting a thumb-shaped deformation rather than anything a
user could control deliberately for text. No WPM, no accuracy claim, no universality.
Reproducibility across hands, sessions and capture conditions is entirely unmeasured.

**The next test is now precise and cheap:** re-run this same script on a capture where the
hand performs a field-level gesture that is NOT a thumb compass. If separability collapses
to chance there, the signal is a thumb artefact and the space is dead. If it holds, a
field-based input method is real.

---

## 10. The ENGLISH syllable inventory — the premise survives here, unlike German

Computed on a pinned corpus: **hermitdave/FrequencyWords 2018 `en_50k.txt` at commit
`525f9b5`, sha256 `5351ff…b458`**, segmented with **eSpeak-ng 1.52.0** `--ipa=3`, stress and
length stripped, maximum legal onset including the English `sC` rule and stop+fricative+liquid
clusters (`str`, `spr`, `skr`, `spl`), with sonority fallback. 49 997 / 50 000 types valid
(three had no vowel: `psst`, `qu`, `ís`), covering 725 114 237 / 725 119 374 tokens.

| Quantity | Value |
|---|---|
| Unique phonemic syllables, top 20k | 7 577 (`log₂` 12,887) |
| Unique phonemic syllables, top 50k | **12 870** (`log₂` 13,652) |
| Weighted syllable entropy | **9,085 bits/syllable** |
| Mean syllables per word | **1,2916** |
| Mean syllables per 5-letter word | **1,3965** |
| Word unigram entropy | 9,476 bits/token → `2^H` = **712,30** |

Token-mass coverage: 128 → 61,60 % · 256 → 73,50 % · 512 → 83,33 % · 1024 → **91,15 %** ·
2048 → 96,19 % · 4096 → 98,82 % · 8192 → 99,81 % · 12 870 → 100 %.

### Why English is structurally easier than German, and by how much

| | German | English |
|---|---|---|
| syllables / 5-letter word | 1,695 | **1,3965** |
| 2 events per syllable | 3,39 events/word | **2,79 events/word** |
| 3 events per syllable | 5,09 events/word | **4,19 events/word** |

**The "1–2 events per 5-letter word" premise is incompatible with a fixed syllable code in
German at 2 events per syllable (3,39 needed) but only *just* misses in English at 2 events
(2,79 needed) and comes close at 3 events (4,19).** A 2-event English syllable code needs
2,79 events per word where the premise allows 2 — a 39 % overshoot rather than German's 70 %.
Neither language reaches it, but English is materially closer, and English's 1,15 % top-1024
coverage is better positioned for a compact code than most designs assume.

Event arithmetic at the certified 5,7 events/s ceiling, all ceilings and not user rates:

| Event alphabet | events/syllable | syll/s | WPM (5-letter) | events/5-letter word |
|---|---|---|---|---|
| 8 classes | 5 | 1,14 | 48,98 | 6,98 |
| 16 classes | 4 | 1,425 | 61,22 | 5,59 |
| 32 or 64 classes | 3 | 1,90 | 81,63 | 4,19 |

**The honest English conclusion:** a 3-event, 32-class code reaches 81,6 WPM *arithmetically*
and needs 4,19 events per 5-letter word against a 1–2 premise. The 1–2 premise has to be
abandoned for English as well, but the overshoot is 4,19 against 2 rather than 5,09 against
2, and a word-level code remains the better-fitting frame.

**Caveats carried with the numbers:** eSpeak G2P and this onset table are an approximation,
not a linguistic universal; the corpus is frequency-weighted English, and a different
register or a German corpus changes every figure. Nothing here is a measured user rate.

### 10.1 Orthographic comparison, and a corrected exponential

The English inventory now has a second, independent method for direct comparison with the
German figures: **pyphen 0.18.1 `en_US`**, unique non-empty orthographic hyphenation pieces
(92 838 pieces split, 26 838 distinct at the top 50k):

| Method | top 20k types | top 50k types |
|---|---|---|
| English phonemic (eSpeak) | 7 577 | **12 870** |
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

**The structural conclusion is unchanged by the method:** English needs
`1.396494 × e` events per 5-letter word — **4.189** at 3 events per syllable, 5.586 at 4,
6.982 at 5. All exceed the 1–2 premise. English's lower syllable count makes the overshoot
smaller than German's, not absent.
