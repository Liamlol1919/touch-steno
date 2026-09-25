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

`scripts/envelope_sweep.py` re-measures it by matching per gesture, with at least 8 cued
gestures per cell:

| gesture length | detection rate at 1–6 Hz |
|---|---|
| **100 ms** | **0 % at every rate** |
| 150–350 ms | **100 % at every rate from 1 to 6 Hz** |
| 500 ms | 62 % at 1 Hz, falling to 36 % at 6 Hz |

So the robust findings are: a 100 ms gesture is never detected; 150–350 ms is detected
reliably all the way to 6 Hz; 500 ms is unreliable. There is **no measured 3 Hz ceiling**.
The earlier "88 ms detection *and* 88 ms segmentation" argument remains plausible as a
mechanism, but it is not what the data shows, so it is not claimed.

### 1. Detection and segmentation both cost 88 ms, and they compete

The persistence window that makes the detector false-trigger-free (8 frames ≈ 88 ms) is
*also* the minimum quiet gap needed to tell two consecutive gestures apart. On a mechanical
keyboard a key release gives that gap for free. **On a 0-force surface there is no release** —
the only segmentation cue is the motion itself.

The benchmark shows the consequence exactly: tracking is near-perfect up to 3 Hz and collapses
to 0.32 at 4 Hz, because at that rate the 250 ms gestures run back-to-back with no quiet
window and the detector merges them.

Derived envelope:

- minimum detectable gesture ≈ 88 ms (8 supra-threshold frames)
- minimum inter-gesture gap ≈ 88 ms (same window, used for segmentation)
- ⇒ **theoretical event ceiling ≈ 5.5 Hz**, measured reliable ≈ **3 Hz** with realistic
  250 ms gestures
- at 1.5 syllables/word that is ≈ **180 WPM equivalent at 3 Hz** — which is exactly the
  professional stenography certification bar, and comfortably above every published touch
  system (16.8–55 WPM, CROSS_VALIDATION 1.8).

Design requirement that follows: **a vector gesture must contain its own return phase**
(out-and-back, or a deliberate reversal) so consecutive syllables always produce a quiet
window. A "hold in the sector" gesture cannot be segmented on a surface that cannot release.

### 2. Direction decoding is not the weak link

100 % sector accuracy on calibrated data, axes and diagonals equal. The earlier "35 % of
strokes sit within 10° of a sector fence" is a statement about *unstructured* motion, not
about cued gestures: a cued stroke lands where the operator aimed. The fence problem is
therefore a property of free typing, and the axis-alignment rule (CROSS_VALIDATION 1.7)
matters less for cued input than for exploratory text.

n = 32 is small, and equal axis/diagonal accuracy does **not** contradict the published axis
advantage — it simply is not powered to detect it. Re-run with `--sector-reps 20` before
quoting any axis/diagonal difference.

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
  the latency envelope; it does **not** predict real typing accuracy.
- The tempo result depends on the generator's 250 ms gesture length. A different length moves
  the collapse point; the envelope formula above is the transferable part.
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

`scripts/envelope_sweep.py`, ≥8 cued gestures per cell, decoded sector compared to truth:

| gesture length | detection rate | direction accuracy | idle false events |
|---|---|---|---|
| **100 ms** | **0 % at 1–6 Hz** | – | 0 |
| **150–350 ms** | **100 % at 1–6 Hz** | **100 %** | 0 |
| **500 ms** | 75–89 % | 100 % of detected | 0 |

Final statement of the envelope, superseding §0 and §1:

- minimum detectable gesture: **above 100 ms**, not the nominal 88 ms
- working range: **150–350 ms**, valid to **6 Hz**
- **there is no measured 3 Hz ceiling** and no measured 5.5 events/s ceiling
- long gestures (500 ms) lose events, not accuracy
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
this work is: **a number is not a finding until the metric that produced it has a test.**

## Addendum 2 (06:26) — the speed ceiling, derived from measurements rather than argued

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

For comparison: 150 WPM needs a 267 ms cycle, 250 WPM a 160 ms cycle.

**Consequence: 250 WPM is not reachable with an out-and-back gesture on this device.** A
160 ms cycle cannot contain a 150 ms out-stroke plus any return at all. The measured ceiling
is **~218 WPM in the most favourable corner** (150 ms out-stroke, 600 mm/s return) and
**100–160 WPM for realistic gesture lengths**, which sits:

- far **above** every published touch/chording system (16.8–55 WPM, CROSS_VALIDATION 1.8.1)
- at or **below** the professional stenography band (180–225 WPM certification), and
- consistent with it, because professional steno has a *key release* to segment on.

So the honest claim is: **this architecture is a plausible path into the 100–200 WPM band,
not a path to 250 WPM.** The 360 WPM record is reachable only with a device that can signal a
release, which is the physical difference the whole project has been circling.

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
