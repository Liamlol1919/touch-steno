# Cross-Validation — literature numbers vs our PTH-660 measurements

**Author:** Agent 2. **Date:** 2026-09-25 05:33 CEST.
**Purpose:** put the independently-sourced literature numbers (worker research, W1/W2/W4/W6)
next to the numbers we measured on the actual tablet (`MEASURED_BIOMECHANICS.md`,
`VECTOR_DESIGN_CRITIQUE.md`) and mark where they agree, where they disagree, and where only
we have data at all.

Sources referenced by short name; full URLs live in the corresponding `W*.md` files.

## 1. Where literature and measurement agree

### 1.1 Enslavement magnitude

| source | quantity | value | our measurement | agreement |
|---|---|---|---|---|
| Zatsiorsky, Li & Latash 2000, *Exp Brain Res* 131:187–195 (force, isometric) | slave finger force during single-finger MVC | up to **67.5 %** of its own MVC | **β = 0.55–0.74** for long-finger neighbours (position, on glass) | same order; our values sit just above the isometric figure, which is expected because a light touch on glass needs less force and therefore less stabilization |
| Häger-Ross & Schieber 2000, *J Neurosci* 20(22):8542–8550 | finger **individuation index** (1 = perfect) | thumb 0.983–0.991, index 0.974–0.982, middle 0.935–0.937, little 0.943–0.945, **ring 0.898–0.907** | index and thumb are our least-coupled / best-predictable movers; ring is the worst | **confirmed**, and it independently justifies the user's decision to make thumb + index the active set and the ring a rest anchor |
| Häger-Ross & Schieber 2000 | **stationarity index** (how much a finger moves when *others* move) | thumb 0.994–0.996, index 0.967–0.973, middle 0.925–0.941, **ring 0.905–0.908** | resting contacts drift up to **11.5 mm / 20 s** on our glass | same ordering, our absolute drift is the new part |
| Park et al. 2017, *Front Hum Neurosci* 11:318 | enslaving index ranking, flexion | I, M < L < **R** (ring worst) | same | confirmed |

The literature and our glass measurements agree on the ordering and on the magnitude. That
is the strongest external validation in this repo so far: **the design's choice of
thumb + index as the active channels is the one the motor-control literature
independently supports.**

### 1.2 Speed limit on independence

Häger-Ross & Schieber measured that finger individuation and stationarity **degrade
significantly when movement is externally paced at 3 Hz** versus self-paced ~2 Hz
(II: F = 46.7, p < 0.001; SI: F = 49.9, p < 0.001). Their subjects naturally chose
~2 Hz (range 0.7–3.3 Hz).

Consequence for the speed target: at 250 WPM a syllable/chord every ~200–400 ms is
≈ 2.5–5 events per second per hand. The literature says finger *independence* already
degrades at 3 Hz in a simple cyclic task. Our 88 ms event floor (§2 below) corresponds to
11.4 events/s, i.e. **well past the frequency at which independent finger control is
already measurably degrading.** This is not an argument against the target — the two-thumb
design deliberately does not ask the long fingers to alternate — but it *is* an argument
against spending design effort on a ten-finger layout, and against assuming the
finger-independence literature transfers to 5–10 Hz chording.

### 1.3 Direction resolution: literature caps breadth at 8

W6 (marking-menu literature): expert error stays under 10 % for **breadth 8, depth 2**, and
becomes error-prone beyond that; the M3 finger-gesture study reached 64 commands at ~3 %
error / 0.7 s and 512 commands at 8.85 % / 1.0 s. The A-Coord pen study found **4 levels
→ 9.4 % errors, 8 levels → 18.2 %** ("twice as many errors").

Our independent derivation from the tablet's own noise (VECTOR_DESIGN_CRITIQUE §2) lands
in the same place: a 16-way thumb grid is 1.5–2.8 reliable bits at 3σ, an 8-way grid is
2.9–3.0. **Two independent routes — published psychophysics and our sensor noise — agree
that 8 is the honest per-level maximum and 16 is a stretch.**

## 2. Where only we have data

The single most useful thing in this repo is the gap: the literature has **no** measurement
of what a *resting* finger does on a flat touch surface in mm and mm/s. W1 searched
explicitly for it and returned NOT FOUND (only clinical tremor bounds, not
resting-on-surface behaviour). Our contribution:

| quantity | our value | literature |
|---|---|---|
| resting per-frame step p99 (worst of 17 contacts) | **0.56 mm** | NOT FOUND |
| resting per-frame speed p99 / max | **57 / 190 mm/s** | NOT FOUND |
| resting net drift over 20 s | **11.5 mm** | NOT FOUND |
| threshold + persistence that separates rest from drive | **v ≥ 40–60 mm/s for 8 consecutive frames** | NOT FOUND |
| coupling *predictability* per contact pair (r, r²) | **0.10–0.92** across pairs | NOT FOUND (literature has force correlations, not position-vector regressions) |
| reader init artefact magnitude | **260 mm phantom drift, 19972 mm/s phantom peak** | driver-specific, none |

This matters because the whole "0-force" literature reasons about *force* and *dwell*,
while a capacitive pad like the PTH-660 exposes only *position and area*. Our numbers are
the missing bridge from one domain to the other.

## 3. Where literature and measurement disagree — or appear to

### 3.1 "The 65 % coupling" is not one number

Both the design chat and several summaries quote "65 % enslavement" as if it were a
constant. Measured, it is a **distribution over contact pairs**, spanning β = 0.01 to
0.74, and its *structure* is what matters:

- long-finger neighbours: β 0.63–0.74, r² 0.62–0.92 → subtractable;
- cross-hand (whole-body): r² 0.72–0.74 → subtractable, and it is a *nuisance* signal;
- thumb↔thumb: β 0.49–0.63, **r² 0.10–0.25** → resists subtraction;
- thumb↔finger rows: β 0.01–0.04 → already below the rest noise floor.

A single global "65 %" constant would therefore *over*-suppress the cross-group pairs and
*under*-suppress the thumbs. It has to become a per-pair calibration.

### 3.2 The 2 mm / 80 mm/s thresholds from the design chat

The chat proposes >2 mm displacement and >80 mm/s velocity. Measured: resting contacts
already reach 1.48 mm steps and 190 mm/s spikes, and drift 11.5 mm over 20 s. So:

- **80 mm/s** is above the resting p99 (57) but *below* the resting max (190) → it is
  not a safe gate by itself; it needs the persistence condition.
- **2 mm** is above the resting per-frame step max (1.48) but *far below* the resting
  20-second drift (11.5) → it only works as a *windowed* displacement, never since
  touch-down.

The numbers are not wrong so much as *unqualified*: they are single-frame gates and the
resting distribution is heavy-tailed. Our v ≥ 40–60 mm/s ∧ 8-frame rule is the version
that holds across all three sessions.

### 3.3 Thumb ROM is not the constraint; timing is

W6 found generous thumb range of motion (CMC radial abduction 62.9°, palmar abduction
61.2°, MCP flexion 60°, IP flexion 88°; circumduction components 27°/67°/10°). So the
physical excursion comfortably fits 8 radial directions, even 16 in principle. The binding
constraints are elsewhere and all three are measured or literature-backed:

1. **noise vs zone width** (our measurement: 16 zones = 1.5–2.8 bits at 3σ),
2. **persistence latency** (our measurement: 8 frames ≈ 88 ms to avoid resting triggers),
3. **simultaneity** (W6, Buxton/ToCHI2H review: "simultaneous independent timing for the
   two hands could not be achieved even when parallel control was encouraged by training").

Point 3 deserves emphasis because it targets the heart of the design: the 7056-state
figure requires *simultaneous, independent* left- and right-thumb selection, and the HCI
record says independent bimanual timing is the hard part, not the easy part. Bimanual
gains in the literature come from **coupled or asymmetric** roles, not from two hands
choosing independently at the same instant.

That is a stronger objection to the 7056 architecture than the noise argument, and it
came from outside our data.

## 4. The speed target, restated with everything we now know

| evidence | value | source |
|---|---|---|
| best measured surface/mobile typing, large sample | **36–38 WPM** (two-thumb 38, one-finger 29; 2.3 % uncorrected error; autocorrect +9) | 37,370-participant mobile study (W6) |
| best measured touch/chording system in our literature set | 44.6 WPM (TOAST), 47 WPM (Twiddler experts after ~25 h) | W2, W6 |
| best measured 10-finger passive tap system with IMU | 70.6 WPM after 2.5 h / 5 days | TypeAnywhere (W2) |
| our event budget at the measured 88 ms floor | ≈ 11.4 events/s ≈ 5.7–7.6 syllables/s ≈ 340–450 WPM **theoretical, error-free** | derived, VECTOR_DESIGN_CRITIQUE §3 |
| our measured mover speeds | peak 133–309 mm/s, mean 16–40 mm/s, sustained runs 19–278 frames | MEASURED_BIOMECHANICS §3 |
| our measured free-motion event rate | **2.56 events/s** (108 events in 42.3 s, ten fingers down) | MEASURED_INTENT_FILTER |

### 1.4 The WPM decision, computed rather than asserted

`scripts/wpm_ceiling.py` turns the measured numbers into the required event rate for each
target. Inputs: detector ceiling 1/88 ms = **11.4 events/s**, measured free-motion rate
**2.56 events/s**, syllables/word 1.5–2.0, events/syllable 1.0–2.0.

| target | need (best case: 1 ev/syll, 1.5 syll/word) | × detector ceiling | × measured free motion |
|---|---:|---:|---:|
| 150 WPM | 3.75 ev/s | 0.33× | **1.46×** |
| 200 WPM | 5.00 ev/s | 0.44× | **1.95×** |
| 250 WPM | 6.25 ev/s | 0.55× | **2.44×** |
| 250 WPM, 1.5 ev/syll | 9.38 ev/s | 0.82× | 3.66× |
| 250 WPM, 2.0 ev/syll | 12.50 ev/s | **1.10× (over ceiling)** | 4.88× |
| 250 WPM, 2 syll/word + 2 ev/syll | 16.67 ev/s | **1.47× (over ceiling)** | 6.51× |

Decisions that follow, stated as constraints rather than opinions:

1. **250 WPM is only physically reachable with a one-event-per-syllable encoding.** With a
    2–3 event syllable it needs 12.5–16.7 events/s and *exceeds* the 88 ms detector
    ceiling. That is not a tuning problem: no threshold tuning recovers an event rate the
    detector cannot sample.
2. **Every target needs a deliberate event rate 1.5–2.4× above what free finger motion
    produced** in the measured session. That gap is a *training* requirement, and it is
    the single most important thing to measure next: a rhythm/tempo session with the
    operator tapping deliberately at increasing rates.
3. The binding constraint is therefore neither the sensor (11.4/s headroom) nor the
    channel capacity (~10 reliable bits), but **the user's sustainable deliberate event
    rate per hand**, and the independence degradation that starts around 3 Hz.

### 1.6 The human anchor: 360 WPM is a verified human record

This section corrects the tone of 1.4. The table there says 250 WPM needs 2.44× the
event rate that *untrained free motion* produced. That is true but misleading if read as
"the target is biomechanically unreachable". It is not.

Verified primary source: New York Magazine's interview with **Mark Kislingbury**, who holds
the Guinness world record for fastest real-time court reporter — **360 words in one minute
at 97.23 % accuracy** (set at the NCRA convention, 2004; he later trained at 450 WPM for
stretches). https://nymag.com/speed/2016/12/how-to-type-360-words-a-minute.html

Three facts from that interview that settle the architecture question:

1. **A 23-key mechanical steno machine sustains 360 WPM.** 360 WPM with word-level
    shortcuts is ≈ **6 strokes/s**. Our 250 WPM target needs 6.25 events/s. Those are the
    same number. The 88 ms detector ceiling is 11.4 events/s, i.e. **1.8× the record
    rate**. The sensor and the detector are not the constraint; they have roughly a
    factor of two of headroom over a world-record human.
2. **Steno is one simultaneous chord per syllable** — "you push them all at once. That's
    where the speed comes in." So the "1 event per syllable" requirement in 1.4 is not a
    compromise forced by our detector; it is *the proven steno model*. The design's
    one-event encoding is aligned with 180 years of stenographic practice.
3. **The speed came from the dictionary, not the fingers.** "The reason I'm so fast is
    that I don't write every syllable. I memorize a shortcut for each common name, phrase,
    word" — he reports ~100,000 memorized short forms, and explicitly credits his system
    rather than talent. He also notes "your fingers just physically top out on any
    keyboard", i.e. the motor channel saturates long before the language layer does.

Consequences for this project:

- **Drop the framing that 150–250 WPM is a speculative target.** It is a *demonstrated
  human rate* on a chorded device, and our sensing budget covers it with ~1.8× margin.
  What is unproven is whether a *new* user reaches it on a 0G surface, and how long
  training takes — which is exactly what the tempo session measures.
- **The binding constraint is the language layer, not the motor layer.** Plover
  dictionaries, an LM, and per-user shortcuts are the levers that moved Kislingbury from
  200 to 360 WPM. That re-prioritises the work: decoder effort belongs in the dictionary/LM
  and in the correction path, not in squeezing more events out of the fingers.
- **The free-motion 2.56 events/s is an untrained baseline**, and should be labelled as
  such. It is the "day 0" number, not a ceiling.

Open question this raises for agent 1: `RECOMMENDED_ARCHITECTURES.md` and
`COMPREHENSIVE_RESEARCH_REPORT.md:13` both currently frame 150–250 WPM as not evidenced.
That framing is right for *published touch/steno research on 0G surfaces* and wrong as a
statement about human capability. Please separate the two explicitly: "no published
0G-surface system reaches this rate" is true; "this rate is beyond human capability" is
false, and a 360 WPM steno record exists.

### 1.8 The caveat that matters most: nobody has shown keyless steno works

1.6 established that a *human* sustains 360 WPM on a 23-key mechanical steno machine. W10
(`W10_STENO_ON_TOUCH.md`) establishes the uncomfortable companion fact: **that performance has
never been reproduced on a 0-force surface**, and the closest published numbers are far below
the steno bar.

| evidence | number | source |
|---|---:|---|
| best flat-surface **sequential** typing, two thumbs | 38 WPM, 2.3 % uncorrected error (n = 37,370) | mobile typing study |
| best flat-surface sequential typing, ten fingers **with local haptics** | 55.1 WPM | W10 |
| best **keyless chording** found (instrumented glove, not glass) | **16.8 WPM, 17.4 % error** | https://www.obscure.org/rosenberg/toc.pdf |
| real steno-on-glass attempt (iStenoPad, 2012) | qualitative failure: drift, wrong keys, hit/miss indistinguishable without looking; **no numbers published** | http://plover.stenoknight.com/2012/02/istenopad-overlay-bust.html |
| ASETNIOP (touchscreen chord keyboard) | ~30 WPM after hours; 37–50+ WPM are **vendor anecdotes**, no error rate, no peer review | https://www.asetniop.com/faq/ |
| peer-reviewed chording **with physical keys** (Twiddler) | 47 WPM average, 67 max, after ~25 h | ISWC 2004 |
| mechanical stenography, expert | 180–225 WPM required for certification; record 360 WPM at 97.23 % | NCRA / Guinness |

So the gap is not "can a human do it" (yes) and not "is our sensor fast enough" (yes, 1.8×
headroom over the record rate). The gap is: **does removing key travel, key force and the
per-key depression event preserve any of it?** On the published evidence, the best keyless
chording result is 16.8 WPM at a 17.4 % error rate, and the best flat-surface sequential
typing is 38–55 WPM — 4–6× below the 180–225 WPM certification bar. Nobody has published a
number between those.

This reframes the project's success criterion honestly:

- **Not** "reach 150–250 WPM on a 0G pad" (no precedent, and 1.6/1.7 give the headroom, but
  nobody has closed the substitution).
- **Rather:** how far above the published keyless-chording floor (16.8 WPM / 17.4 % error) and
  the flat-surface sequential band (38–55 WPM) can a per-user coupling model with an
  adaptive rest baseline get? That is measurable, falsifiable, and a real contribution
  even if the answer is "60 WPM".

The honest claim this project can make today: *we have removed the two failure modes that
made a previous on-glass steno attempt fail* — drift (adaptive baseline, 11.96 → 5.04 mm
residual) and neighbour enslavement (per-pair suppression, 175 followers removed at
r² 0.55–0.93) — and the *next* measurable step is the cued chord session, which no
published system has. That is a defensible research position, and it is a smaller claim
than 360 WPM.

### 1.7 A concrete layout rule that follows: put the targets on the axes

Kurtenbach & Buxton 1993 (verified directly, https://www.billbuxton.com/MMExpert.html,
InterCHI '93, 482–487) report that **on-axis menu items are selected faster and with fewer
errors than off-axis items**: axis level had a significant effect on response time
(F(2,22) = 104.84, p < 0.001) and on error rate (F(2,22) = 36.2, p < 0.001), with
pen > mouse (F(1,11) = 19.7, p < 0.001 for time; F(1,11) = 6.41, p < 0.05 for errors).

For an 8-way thumb compass this is actionable and currently missing from the design notes:

- **align the 8 sectors to the cardinal and intercardinal axes** (N, NE, E, SE, S, SW, W,
  NW), not to a rotated 22.5° offset grid — the axes are the reliable half;
- expect the **four diagonals to carry most of the error budget**, and either give them
  more LM prior weight, or restrict the high-frequency set to the four axes and use the
  diagonals as modifiers;
- a 16-way grid would place every target at a 11.25° offset where the axis advantage is
  largely gone, which is a second, independent reason to prefer 8.

Measured counterpart: our own movers cluster in arbitrary directions, so the *decoder*
should be tested on a confusion matrix split by sector (axes vs diagonals), not only on an
overall diagonal. That split belongs in the slow-stroke session of
`VECTOR_DESIGN_CRITIQUE.md` §8.

Reading these together: the *sensing* side has enough headroom for 150+ WPM. The
*decoding and human* side is where every published system actually lands, at 36–70 WPM.
Agent 1's report already refused to quote 150–250 WPM as an evidenced property
(`COMPREHENSIVE_RESEARCH_REPORT.md:13`); this document now agrees with that from the
hardware side as well, and identifies why: not sensor bandwidth, but simultaneity,
individuation at high frequency, and per-stroke reliability.

## 5. What this changes in the plan

1. **Keep** thumb + index as the active set — now backed by Häger-Ross & Schieber, not
   just by intuition.
2. **Ship 8-way, not 16-way** per thumb in the first build, with the measured
   3σ-margin argument and the marking-menu literature agreeing.
3. **Budget 88 ms**, and stop quoting 40 ms until a slow-stroke session shows the
   confusion matrix can hold (VECTOR_DESIGN_CRITIQUE §8 test 1).
4. **Make the coupling model per-pair and signed**; judge it by r², not by a global
   constant, and give the whole-body component its own term.
5. **Do not depend on simultaneous independent two-thumb selection** for the first
   architecture. Sequential or coupled thumb roles reach the same state count with a
   mechanism the literature says humans can actually execute.
6. **Reuse the one real advantage we have**: the coupling/persistence model is per-user,
   per-hand and cheap to recalibrate. Published systems have no access to it; a
   re-calibration protocol is a legitimate product feature, not an implementation detail.

## 6. Provenance

- Our measurements: `MEASURED_BIOMECHANICS.md`, `VECTOR_DESIGN_CRITIQUE.md`,
  reproducible via `scripts/kinematics.py`, `scripts/real_session_evidence.py`,
  `scripts/follower_predictability.py`.
- Literature: `W1_ACADEMIC_ENSLAVEMENT.md`, `W2_STENO_HARDWARE.md`,
  `W3_OPEN_SOURCE.md`, `W4_ZERO_FORCE_ALGORITHMS.md`,
  `W6_THUMB_BIMANUAL_VIABILITY.md`. Two primary sources were fetched and verified
  directly during this work (PMC6773164, PMID 10766271); the rest are worker-sourced and
  should be spot-checked before any external publication.
- Open issues against agent 1: #1 thresholds, #2 init artefact, #3 coupling classes
  (with a correction comment), #4 40 ms vs 88 ms.
