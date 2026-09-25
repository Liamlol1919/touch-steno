# Benchmark Results — the first accuracy numbers in this project

**Author:** Agent 2. **Date:** 2026-09-25 06:12 CEST.
**Reproduce:** `python3 scripts/make_benchmark.py --out /tmp/bench.jsonl && python3
scripts/evaluate_session.py /tmp/bench.jsonl`

Every threshold in this project was justified by distributions (rest vs mover, coupling r²).
None was justified by an accuracy number, and no public baseline exists for any of it (W9:
hit-rate and undo-rate both NOT FOUND). This is the first scored run.

## What the benchmark is

`scripts/make_benchmark.py` generates a **labelled** session whose noise and motion statistics
are taken from the three real PTH-660 recordings: 91 Hz, rest step p99 0.56 mm, rest drift
~0.5 mm/s, mover steps 1–2.5 mm/frame, finger coupling slope +0.65, thumb coupling −0.33.
Cues: rest blocks, an 8-sector compass, a tempo ramp, and chord/single alternation. The
manifest format is identical to `guided_calibration.py`, so the same evaluation path runs on
synthetic and real cued data.

## Results

| metric | value | note |
|---|---:|---|
| **sector accuracy** | **1.00 (n = 32)** | axis 1.00, diagonal 1.00 |
| **idle false events** | **0 in 9.7 s** | 0/min |
| tempo tracking 1 Hz | 0.99 | 0.99 detected / 1.00 cued |
| tempo tracking 2 Hz | 0.98 | |
| tempo tracking 3 Hz | 0.97 | |
| tempo tracking 4 Hz | 0.33 (n=3) | **RETRACTED, see correction below** |
| tempo tracking 5 Hz | 0.67 (n=3) | **RETRACTED, see correction below** |
| chord detection | tp 2, fp 0, **fn 4** | the weak spot, see below |

## The three findings that matter

### 0. RETRACTION: the "3 Hz ceiling" was a measurement artifact

The first version of this document claimed the detector collapses above 3 Hz. **That claim is
withdrawn.** It came from counting *events per block* rather than matching each cued gesture
to its own event; at high rates consecutive gestures merge into one event, so the count-based
metric under-reports.

`scripts/envelope_sweep.py` now matches each detector event to at most one cue and reports
the rate actually realized by the generator. The corrected grid has at least 8 cues per
cell and exposes the distinction between requested and realized rate:

| gesture length | requested rates | realized rate range | detection rate | direction accuracy |
|---|---:|---:|---:|---:|
| **100 ms** | 1–6 Hz | 1.01–1.58 Hz | **0 %** | n/a |
| 150 ms | 1–6 Hz | 1.01–1.48 Hz | **100 %** | 100 % |
| 200 ms | 1–6 Hz | 1.01–1.37 Hz | **100 %** | 100 % |
| 250 ms | 1–6 Hz | 1.01–1.29 Hz | **100 %** | 100 % |
| 350 ms | 1–6 Hz | 1.01–1.14 Hz | **100 %** | 100 % |
| 500 ms | 1–6 Hz | 0.96–0.97 Hz | 75–89 % | 100 % of detected |

So the corrected synthetic sweep supports a gesture-length/detection envelope, not a
universal 3 Hz or 5.5 events/s ceiling. The sub-gate return phase makes the requested rate
unrealizable for these long gestures: the realized rate is reported explicitly rather than
silently treating the request as a measurement.

### 1. What the corrected sweep establishes: gesture length dominates

The corrected per-gesture sweep found 100% detection for 150–350 ms gestures and 100%
direction accuracy in the synthetic cells. A 100 ms gesture was never detected; 500 ms
gestures lost 11–25% of cues even at the realized rate. The useful result is therefore a
gesture-length operating envelope, not a universal 3 Hz or 5.5 events/s ceiling.

The 88 ms persistence window remains a latency and evidence requirement: each candidate
needs eight consecutive supra-threshold frames. It does **not** by itself establish an
event-rate maximum, because the rate also depends on gesture length, inter-gesture
segmentation, and the operator's deliberate rhythm. A return/reversal phase remains
sensible for held-sector gestures because the sweep shows that long holds can lose
events, but the old 3 Hz explanation is withdrawn.

The 250 WPM target is not established by this synthetic sweep. It requires a deliberate
event-rate measurement on the device; a 360 WPM mechanical-steno record demonstrates
human steno throughput, not PTH-660 touch-surface throughput.


### 2. Direction accuracy is now measured, but still synthetic

The earlier 0.19–0.50 envelope result came from comparing a block label with a block label,
not the decoded direction. The metric was fixed to decode the event vector, and the
integrated corrected grid now reports 100% direction accuracy for detected synthetic cues.
That is useful pipeline evidence, not a hardware claim: sample sizes are small, the
generator uses a common-centre return, and the cued real session remains required.


### 3. Chord detection is the genuinely weak part

tp 2, fp 0, **fn 4**: most true chords were missed. The peak-alignment criterion (50 % of the
mover's peak within 2 frames) is too strict for the synthetic chord generator, where the peer
is displaced 12 mm in a different direction and therefore peaks at a different time. The
honest reading is that **the chord criterion is not yet calibrated** — the 2-frame lag window
was chosen from a theory, not from data, and the cued chord session (issue #8) is what will
calibrate it. Until then, chord support should be treated as unimplemented, not as working.

## Three bugs this benchmark found that reviews had not

1. **Direction labels were rotated by one sector.** The decoder re-read positions by timestamp
   and could straddle a block boundary. Fixed by accumulating the mover's displacement vector
   *inside* the event window (`intent_filter` now emits `mover_dx_mm` / `mover_dy_mm`), which
   is drift-robust and cannot cross a boundary.
2. **Ground-truth labels were off by one block.** The evaluation used closed intervals, so an
   event starting exactly on a boundary inherited the *previous* cue's label. That alone
   produced a fake "0 % accuracy, everything rotated 45°". Now half-open `[start, end)`.
3. **The generator teleported contacts between cues**, which is physically impossible and
   manufactured a false idle trigger. Blocks now continue from the previous end position.

Bugs 1 and 2 produced a confident, completely wrong accuracy number. That is the argument for
having a scored benchmark at all: the pipeline looked fine in every code review and in the
pipeline audit, and was still wrong.

## Honest limits of these numbers

- Synthetic data, calibrated to *this* hand and device. It validates the pipeline's logic and
  the gesture-length envelope; it does **not** predict real typing accuracy.
- The sweep's upper tested cue rate is 6 Hz, not a measured maximum. Real throughput must be
  measured with a cued tempo session and reported per gesture, not inferred from the 88 ms
  persistence window.
- Chord detection is known-broken here and is reported as such rather than tuned until the
  number looks better.

## Next measurement

Run the same evaluation on a **cued real session** (`guided_calibration.py --task sectors`,
then `evaluate_session.py`). That converts every number above from "validated on calibrated
synthetic data" to "measured on the device", and it is the first thing worth doing when the
tablet is connected again.


## Addendum (06:20) — the direction-accuracy discrepancy is explained, and so were three metric bugs

The open question from §2 — "sector accuracy 0.19–1.0 by cell, unexplained" — is now
resolved, and the resolution is a design requirement rather than a mystery.

### Root cause: gestures need a return phase, and it must be sub-gate

The two generators differed in one respect that turned out to decide everything: whether each
gesture starts from a common reference point. On a 20 mm compass the neighbouring sector
targets are only **15.3 mm apart**, so without a return the first frames of a stroke are
dominated by *repositioning*, not by the intended direction. Computed over the 8-sector
sequence:

| gesture start | direction error |
|---|---:|
| from the previous target | **a constant 67.5°** (7 of 8 sectors wrong, 1/8 correct) |
| from the common centre | **0.0°** (8/8 correct) |

A 67.5° error is 1.5 sectors — which is exactly the failure the sweep was showing. So the
return phase is not a nicety: **without it the direction estimate is systematically rotated and
the sector classifier collapses.** This is independent of, and stronger than, the segmentation
argument in §1.

The return must also stay **below the detection gate**, otherwise it triggers its own event.
Modelled at 30 mm/s against the 40 mm/s gate, a 20 mm return takes 0.67 s — affordable at low
rates, and the reason long gestures become unreliable (below).

### Corrected operating envelope

`scripts/envelope_sweep.py`, ≥8 cued gestures per cell, decoded sector compared to truth;
the requested grid is shown separately from the rate actually realized by the sub-gate
return:

| gesture length | realized cue rate | detection rate | direction accuracy | idle false events |
|---|---:|---:|---:|---:|
| **100 ms** | 1.01–1.58 Hz | **0 %** | – | 0 |
| **150–350 ms** | 1.01–1.48 Hz | **100 %** | **100 %** | 0 |
| **500 ms** | 0.96–0.97 Hz | 75–89 % | 100 % of detected | 0 |

Final statement of the sub-gate-return envelope, superseding §0 and §1:

- minimum detectable gesture: **above 100 ms**, not the nominal 88 ms
- working range in this generator: **150–350 ms**, at the **realized** rate above
- **there is no measured 3 Hz ceiling** and no measured 5.5 events/s ceiling
- long gestures (500 ms) lose events, not direction accuracy
- a **sub-gate return to a common centre is mandatory** for direction to be classifiable

### Three metric bugs, all in the evaluation harness

Every one of them produced a confident, wrong number, and none was caught by code review or by
the pipeline audit:

1. **event counting per block** instead of per gesture — invented the "3 Hz collapse" (§0).
2. **closed label intervals** — shifted ground truth by one block, faking a uniform 45° rotation.
3. **comparing the event's block label to the gesture's label** — trivially true, so the
   reported "direction accuracy" never looked at the decoded direction at all. The real error
   was 2–20°, i.e. every sector inside its 22.5° half-width.

The pattern is the finding: the *harness* is the weakest link in this project, and it has now
produced three wrong headlines in a row. It needs its own tests, and the rule for the rest of
## Addendum 2 (06:26) — synthetic out-and-back cycle budget


Two intermediate claims were wrong and are corrected first.

1. **The reversal threshold is not the problem.** Sweeping `turn_deg` over 30–120° gives
   *identical* results (acc 1.00 / 1.00 / 0.83 / 0.79 at 1/2/3/4 Hz). Only 150° breaks down
   (0.06 at 3 Hz). So "B is under-tuned" was wrong.
2. **The cycle budget is the problem.** Accuracy stays at 1.00 while the cue rate is below
   `1 / (t_out + t_return)` and collapses above it:

| return speed | return time | cycle limit | acc 1 Hz | 2 Hz | 3 Hz | 4 Hz |
|---:|---:|---:|---|---|---|---|
| 100 mm/s | 200 ms | 2.2 Hz | 1.00 | 1.00 | 0.83 | 0.62 |
| 200 mm/s | 100 ms | 2.9 Hz | 1.00 | 1.00 | 0.83 | 0.79 |
| 400 mm/s | 50 ms | 3.3 Hz | 1.00 | 1.00 | 1.00 | 0.04 |
| 600 mm/s | 33 ms | 3.5 Hz | 1.00 | 1.00 | 1.00 | 0.04 |

Above the limit the next out-stroke begins while the return is still running, so the first
8 frames of the new gesture are contaminated — hence the collapse.

### The ceiling

With the measured minimum out-stroke of 150 ms and a 20 mm return:

| out-stroke | return 600 mm/s | cycle | events/s | **WPM** (1.5 syll/word) |
|---:|---:|---:|---:|---:|
| 150 ms | 33 ms | 183 ms | 5.45 | **218** |
| 200 ms | 33 ms | 233 ms | 4.29 | 171 |
| 250 ms | 33 ms | 283 ms | 3.53 | 141 |
| 350 ms | 33 ms | 383 ms | 2.61 | 104 |

**Consequence for this synthetic out-and-back model: 250 WPM is not reachable with the
current gesture/return assumptions.** A 160 ms cycle cannot contain a 150 ms out-stroke plus
any return. The modelled ceiling is **~218 WPM in the most favourable corner** (150 ms
out-stroke, 600 mm/s return) and **100–160 WPM for realistic gesture lengths**. This is
not a PTH-660 user result; the cued real session must measure the same cycle budget.

The result sits:

- far **above** every published touch/chording system (16.8–55 WPM, CROSS_VALIDATION 1.8.1)
- at or **below** the professional stenography band (180–225 WPM certification), and
- consistent with it, because professional steno has a *key release* to segment on.

The honest claim is therefore: **this synthetic strategy is a plausible path into the
100–200 WPM band, not evidence that a PTH-660 user reaches 250 WPM.** The 360 WPM record
requires a device/surface with a release or an independently validated segmentation method.

### What would lift the ceiling

Ranked by measured effect, all derived from the table above:

1. **Shorter out-strokes** — the whole budget is linear in `t_out`, and 150 ms is already the
   detection floor. Nothing below it works.
2. **A smaller compass radius** — the return length is the other term. Halving r to 10 mm
   halves the return, but `compass_geometry.py` shows the repositioning error then exceeds the
   sector half-width by itself, so the return must stay.
3. **Not paying for a return at all** — which is only possible if the surface can signal a
   release, i.e. a different device class. This is the finding: the 0G surface spends its speed
   budget on the return stroke.
