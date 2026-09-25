# Measured Feasibility Review — the 4-finger / 16-zone thumb architecture

**Author:** Agent 2. **Date:** 2026-09-25 05:29 CEST.
**Subject under review:** the architecture from the user's design notes and chat
(`SYSTEMKOMPENDIUM.md`, design chat of 2026-09-25 03:00–04:40), in short:

> 2 thumbs as 8-way compasses with a "double ring" (16 radial zones + neutral each),
> 2 index fingers with 4 zones each, the remaining 6 fingers resting as a stable anchor.
> Per hand Ω = 84, both hands Ω = 84 × 84 = **7056 syllables/words in one stroke**.
> Vectors should take ~40 ms. Threshold proposal from the chat: >2 mm displacement,
> >80 mm/s velocity, and a "dominance filter" that subtracts the ~65 % enslavement of
> neighbours from the ring finger.

This review does not reject the design. It puts measured numbers on the three places
where the design currently rests on assumption, and proposes the smallest change that
makes each one defensible. All numbers are from `MEASURED_BIOMECHANICS.md` (3 real
PTH-660 sessions, 91 Hz) and are reproducible with
`python3 scripts/real_session_evidence.py <sessions>`.

## 1. Summary of verdicts

| design claim | measured reality | verdict |
|---|---|---|
| 16 radial zones per thumb = 4 bits | reliable angular classes at 3σ noise: **1.5–2.8 bits** depending on thumb radius | **over-provisioned**; 8 zones is the defensible number |
| 40 ms vector gesture | resting fingers produce **7 consecutive frames** (77 ms) above 30–40 mm/s | **too fast**; 88 ms is the measured floor |
| "dominance filter" removes the 65 % enslavement | true for the long-finger row (cos θ = +0.88…+0.97), **false** for thumb↔thumb and index↔index (cos θ = −0.17…−0.31) | **works in the finger row, fails on the two channels the design depends on most** |
| 6 fingers rest as a "stable anchor" | resting fingers drift **11.5 mm in 20 s** and emit isolated spikes up to **190 mm/s** | usable as an anchor, but the decoder must not assume stillness |
| Ω = 7056 states / 12.78 bits per stroke | the channel delivers ≈ **4.4–5.6 bits** at 3σ, not 12.78 | **capacity ≠ usable states**; state count is not the bottleneck |

None of this says "do not build it". It says the *first* build should be the
8-zone, 88 ms, single-thumb version, because that version is inside the measured
operating envelope, and every measurement infrastructure we need to justify the
16-zone version is exactly the same infrastructure.

## 2. How many angular classes does a thumb actually have?

Resting-finger position noise, measured worst case over 17 resting contacts:
**step p99 = 0.56 mm, step max = 1.48 mm** per frame (≈ 11 ms). For a thumb moving on an
arc of radius r, the angular noise is `step / r`:

| thumb radius r | angular σ (p99 step) | angular σ (max step) | 16 zones = 22.5° | margin at p99 | **reliable bits at 3σ** |
|---:|---:|---:|---:|---:|---:|
| 12 mm | 2.68° | 7.06° | 22.5° | 8.4 | **1.48** |
| 16 mm | 2.01° | 5.30° | 22.5° | 11.2 | **1.90** |
| 20 mm | 1.61° | 4.24° | 22.5° | 14.0 | **2.22** |
| 25 mm | 1.29° | 3.39° | 22.5° | 17.5 | **2.54** |
| 30 mm | 1.07° | 2.83° | 22.5° | 21.0 | **2.81** |

(`bits = log2(zone_width / (3σ))`; negative = the zone grid is not resolvable.)

The 8-way compass (45° zones) at r = 20 mm sits at 45 / (3 × 1.61) = **9.3σ**, i.e.
~2.9 bits, comfortably resolvable. The 16-way grid at the same radius is at 4.7σ by the
p99 figure and at **1.8σ by the worst observed frame** — one bad frame and the class is
wrong. A touch surface does not get a "3σ is enough" discount here, because the class is
decided by a *gesture*, not by a stationary pointing task, and the user is moving.

To make 16 zones work you must shrink the noise: `σ ≤ 0.47°` ⇒ `step ≤ 0.16 mm` at
r = 20 mm. If the noise were white, averaging k frames gives `0.56/√k ≤ 0.16` ⇒
**k ≥ 12 frames ≈ 132 ms**. That is a third of the design's 40 ms budget spent purely
on noise reduction, before the persistence floor (§3) is added.

**Recommendation:** design the thumb channel as **8 directions + neutral (9 states)**.
Keep the 16-zone grid as a *future* option that becomes reachable if a calibration shows
per-frame noise below 0.16 mm — and put that number in the acceptance criteria so it is
a measurement, not a hope.

## 3. The 40 ms vector is inside the resting distribution

Measured longest run of consecutive frames above a speed threshold, pooled over all
sessions (`MEASURED_BIOMECHANICS.md` §3):

| speed threshold | worst resting run | best driven run |
|---:|---:|---:|
| 30 mm/s | 7 frames (77 ms) | 168 frames |
| 40 mm/s | 7 frames (77 ms) | 147 frames |
| 60 mm/s | 5 frames (55 ms) | 53 frames |
| 80 mm/s | 4 frames (44 ms) | 23 frames |

A 40 ms gesture is 3.6 frames. At 30–40 mm/s a *resting* finger already produces 7
consecutive such frames. So a 40 ms vector cannot be distinguished from resting noise by
duration or speed alone; it can only be distinguished by *amplitude* (how far it goes,
§4) or by a persistence requirement.

**Recommendation:** the event detector uses **v ≥ 40–60 mm/s sustained for k = 8 frames
(≈ 88 ms)**. A thumb vector is then defined as the *direction of the accumulated
displacement over that window*, not as the instantaneous direction of the first frames.
The design keeps its 8-way compass; it loses 48 ms of latency.

Is that fatal for 250 WPM? Not determinable from the persistence window alone. The 88 ms
window sets detection latency and requires sustained supra-threshold evidence; it is not
an event-rate ceiling. The corrected synthetic sweep found 150–350 ms gestures detectable
with 100% direction accuracy at realized cue rates of 1.01–1.48 Hz; the sub-gate return,
not the requested 1–6 Hz grid, determines that realized rate. 100 ms gestures were not
detected and 500 ms gestures became less reliable. Real touch throughput, segmentation
and training remain to be measured with a cued session.

## 4. The dominance filter works on the finger row and fails on the thumbs

This is the most consequential measurement in the project so far, so it is worth being
precise about what was measured. For every frame we take the contact with the largest
step as the *mover* a, and for every other contact b record the step vector. From those
we estimate:

- `β` = mean |step_b| / mean |step_a| (how much of the leader's motion appears in b),
- `cos θ` = mean cosine of the angle between the two step vectors (+1 = parallel,
  −1 = mirrored),
- `s` = least-squares slope of `step_b ≈ s · step_a`.

| pair (session) | β | cos θ | s | n frames | reading |
|---|---:|---:|---:|---:|---|
| 64 → 61 (test) | 0.74 | **+0.915** | +0.69 | 301 | parallel drag |
| 61 → 64 (test) | 0.74 | **+0.905** | +0.67 | 253 | parallel drag |
| 57 → 66 (test) | 0.70 | **+0.945** | +0.64 | 93 | parallel drag |
| 56 → 57 (test) | 0.69 | **+0.972** | +0.68 | 170 | parallel drag |
| 55 → 56 (test) | 0.64 | **+0.875** | +0.55 | 137 | parallel drag |
| **81 → 82 (daumen)** | **0.63** | **−0.243** | −0.15 | 331 | **mirrored** |
| **82 → 81 (daumen)** | **0.55** | **−0.166** | −0.09 | 210 | **mirrored** |
| **142 → 141 (zeige)** | **0.61** | **−0.311** | −0.20 | 111 | **mirrored** |
| **141 → 142 (zeige)** | **0.49** | **−0.210** | −0.16 | 89 | **mirrored** |

### 4a. How predictable is the follower, really?

The β column above measures magnitude only. The question the decoder actually needs
answered is *predictability*: if the leader's motion is known, how much of the follower's
motion can be predicted away? That is the squared Pearson correlation r² between the two
step vectors (flattened x,y), and the residual factor after a least-squares fit is
`sqrt(1 − r²)`.

| pair | n frames | r | r² (energy explained) | residual factor `sqrt(1−r²)` |
|---|---:|---:|---:|---:|
| 64 → 61 (test) | 312 | **+0.958** | 91.8 % | **0.29** |
| 56 → 57 (test) | 191 | +0.936 | 87.6 % | 0.35 |
| 61 → 64 (test) | 305 | +0.901 | 81.2 % | 0.43 |
| 55 → 56 (test) | 213 | +0.786 | 61.8 % | 0.62 |
| 81 → 82 (daumen) | 418 | **−0.495** | 24.5 % | **0.87** |
| 141 → 142 (zeige) | 118 | −0.404 | 16.3 % | 0.92 |
| 142 → 141 (zeige) | 141 | −0.381 | 14.5 % | 0.93 |
| 82 → 81 (daumen) | 315 | −0.323 | 10.4 % | 0.95 |

Quantify the damage for the compass: at r = 20 mm one zone of an 8-way grid is a
7.85 mm arc. The measured mirrored β of 0.55 displaces the other thumb by ≈ 4.3 mm, i.e.
**more than half a zone**. Because the direction is only ~40 % anti-correlated, the fit
cannot cancel it: 87–95 % of that displacement survives the subtraction. For a two-thumb
chord this is a systematic, class-changing error, not a small bias.

### 4b. The sign is not the criterion — |r| is

Running the full pair sweep with `scripts/follower_predictability.py` overturned the
simple "parallel = correctable, mirrored = not" reading. In `test.jsonl` the pairs
**73 → 55 (r = −0.858, 73.6 % explained)** and **73 → 56 (r = −0.848, 71.8 %)** are
strongly *mirrored* and yet suppress almost as well as the best parallel pairs,
because the filter only needs the signed coefficient. Those two contacts sit ~100 mm
apart in x (73 at 132 mm, 55 at 34 mm), i.e. they are the cross-hand pair, and a
−0.86 correlation there is the signature of **whole-body/forearm motion**, not of
neighbouring-digit enslavement. That is a nuisance signal to model first, and it is
cheap to model: one global motion component explains it.

Corrected rule, and the one the decoder should implement:

> Estimate a signed regression coefficient per contact pair from calibration data and
> suppress by `step_b − s·step_a`. Suppression quality is **r², not the sign**.
> Parallel pairs reach r² = 0.62–0.92 (finger row) and mirrored pairs reach
> r² = 0.72–0.74 (cross-hand body motion). The thumb↔thumb pair is the genuinely hard
> case at r² = 0.10–0.25.

This is a better outcome for the architecture than the first reading suggested: there
is exactly **one** measured pair class that resists suppression (thumb↔thumb), and
time-multiplexing or thumb geometry is only needed for that one.
**Long-finger neighbours are dragged parallel, and that is predictable.** A per-frame
least-squares fit `step_b ≈ s · step_a` reaches correlations of **r = +0.79 … +0.96**
(0.51–0.73 slope). That means 62–92 % of the follower's motion energy is explained by
the leader, and a single subtraction collapses the residual to 0.29–0.62 of the
original. The "dominance filter" from the design chat is therefore *implementable* for
the finger row, and we now know its coefficient range and its residual factor.

**Thumb↔thumb and index↔index are not.** The follower moves about as far (β 0.49–0.63)
but *anti*-correlated with the leader: **r = −0.32 … −0.50**, slope −0.19 … −0.33.
Two things follow, and the second one corrects an earlier over-statement of ours:

1. The relation is **not absent — it is mirrored and reproducible in sign** across two
    different sessions (daumen: −0.495 / −0.323; zeige: −0.404 / −0.381). A linear
    model is still fittable, with a *negative* coefficient.
2. But it explains only **10–25 % of the follower's energy** versus 62–92 % for the
    finger row. In residual terms the linear filter suppresses ≈ 91 % of finger-row
    follower motion and only ≈ 10–24 % of thumb-pair follower motion (residual factor
    0.29–0.62 vs 0.87–0.95). "Not correctable by linear subtraction" is the accurate
    statement; "not correctable at all" would have been wrong. See
    `scripts/follower_predictability.py` for the exact computation and §4a.



Three ways out, in the order I would test them:

1. **Time-multiplex the thumbs**: only one thumb is the active channel per stroke; the
   other thumb is a rest anchor. This removes the mirrored pair from the equation
   entirely. Cost: the per-hand state count drops from 84 to "thumb-active" plus a much
   smaller index-only set, but §5 shows the state count was never the constraint.
2. **Learn the 2×2 thumb coupling matrix** from calibration sessions (a 2×2 matrix plus
   a cos θ per entry) and subtract the *measured* linear map, including its sign
   convention. This works only if the mirrored relation is stable across postures — an
   open measurement, not yet taken.
3. **Separate the thumbs spatially**, which is exactly what a physical mask or a
   thumb-rest rail does. Given that intra-row coupling is 0.6–0.74 and is *correctable*,
   while thumb↔thumb coupling is 0.5–0.6 and is *not*, this is a different trade than the
   design assumed: **the mask's value is in separating the thumbs, not the fingers.**

That last point inverts one of the design's assumptions. The fingers are the couplings
that software can fix; the thumbs are the ones that may need geometry.

## 5. The state count is not the bottleneck — reliability is

The design derives Ω = 84 × 84 = 7056 states = 12.78 bits per stroke and argues that this
is ample. It is ample. The problem is the *other* direction: the channel cannot carry
12.78 bits reliably.

Using the measured per-channel reliability from §2 and §4:

| channel | classes | reliable bits at 3σ (r = 20 mm) |
|---|---:|---:|
| thumb, 8-way + neutral | 9 | ≈ 2.9 |
| index, 4-way + neutral (90° zones) | 5 | ≈ 2.3 |
| per hand | 45 nominal | ≈ 5.2 |
| both hands, one stroke | 2025 nominal | ≈ 10.4 measured-reliable |

So the honest number is ~10 reliable bits per stroke if both hands act at once, and
~5.2 if only one hand does. Both exceed the context-free information needed for many
text syllables, but the state count is not evidence of usable throughput. Gesture length,
segmentation, finger independence, language coverage and correction cost must be measured
separately. The useful consequence remains: **cutting the thumb from 16 zones to 8 costs
1 bit, and buys a detector that actually fires correctly.** The 7056 figure was never the
scarce resource.

## 6. The "6 fingers as a stable anchor" assumption, restated honestly

Measured: a resting contact drifts up to **11.5 mm over 20 s** (≈ 0.5 mm/s sustained, and
this is the `test-zeige` session where the operator drove their index fingers), and emits
isolated single-frame spikes up to **190 mm/s** when the hand settles or repositions.

That is fine for an anchor — the hand does not wander off the pad, which is the thing the
anchor is for — but two design rules follow:

- Anything that integrates displacement **from touch-down** is invalid (§2 of
  `MEASURED_BIOMECHANICS.md`). All features must be windowed.
- The rest-state model in `DECODER_DESIGN.md` should be a *drift-tolerant* per-contact
  distribution (e.g. running position mean/variance per contact id), not a fixed neutral
  point with a small deadband. With 0.5 mm/s of drift, a fixed neutral point slowly
  charges the deadband budget and eventually a resting finger becomes a "displacement".

## 7. What to build first (measured-consistent MVP)

| parameter | design intent | MVP value | why |
|---|---|---|---|
| thumb zones | 16 + neutral | **8 + neutral** | 9.3σ vs 1.8σ worst-frame margin (§2) |
| second thumb ring (inner/outer) | simultaneous | **time-divided** or dropped | mirrored coupling, not correctable (§4) |
| event window | ~40 ms | **8 frames ≈ 88 ms** | above every measured resting run (§3) |
| velocity gate | >80 mm/s | **≥ 40 mm/s, 8 frames** | 80 mm/s alone is inside the rest spike range |
| displacement | >2 mm | **≥ 7.9 mm over 88 ms** (one 8-way zone at r=20) | rest drift is 11.5 mm/20 s; windowed only |
| follower suppression | fixed 65 % | **measured per-pair matrix, parallel pairs only** | β 0.55–0.69, cos θ > 0.87 for fingers; mirrored for thumbs (§4) |
| chord policy | simultaneous two-thumb | **one active thumb per stroke** until mirrored coupling is characterised | removes the unfixable case |

Every row is a *measurement-backed* narrowing. None of them changes the architecture's
shape: still 2 thumbs + 2 index fingers as the active set, still a vector/compass concept,
still vector-shaped steno input. They make it fire correctly on day one and keep every
path to the 16-zone version open, with a stated acceptance criterion for when it becomes
justified.

## 8. Falsification tests (what would change this review)

1. **Slow-stroke session**: operator performs 8-way thumb gestures at a deliberately slow,
   even pace. If the per-zone confusion matrix at 88 ms is worse than ~5 % diagonal, the
   event window is too short and the whole budget must be re-derived.
2. **Repeated thumb-pair session**: three sessions of the same thumb task on different
   days. If `cos θ` for 81↔82 changes sign or magnitude by more than ~0.15 between
   sessions, option 2 in §4 is dead and only time-multiplexing or geometry remains.
3. **Noise-floor session**: hands resting, no task, 60 s. If per-frame step p99 exceeds
   0.9 mm, every σ-based number in §2 degrades and the thumb radius must grow (or the
   grid shrink to 6–8 zones).
4. **Chord-on-cue session**: operator performs real two-thumb chords on cue. This is the
   one measurement that tests whether a real chord is separable from a mirrored drag, and
   it is the single highest-value missing experiment in the project.

## 9. Relation to the rest of the repo

- `MEASURED_BIOMECHANICS.md` — the measurements this review is built on.
- `scripts/real_session_evidence.py` — reproduces every table; `--json` for automation.
- Issue #1 — thresholds in `EXPERIMENT_PROTOCOL.md` / synthetic benchmark vs measured.
- Issue #3 — the two coupling classes, and the decoder hole for mirrored followers.
- Issue #4 — the 40 ms vs 88 ms decision.
- `DECODER_DESIGN.md` (Agent 1) — the state machine this MVP plugs into; the
  `IDLE → ARMED → TENTATIVE → COMMITTED` flow is compatible with the 88 ms window
  (`TENTATIVE` simply begins at frame 1 of the window and commits at frame 8).
