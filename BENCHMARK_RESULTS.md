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
| **tempo tracking 4 Hz** | **0.32** | **collapse** |
| **tempo tracking 5 Hz** | **0.31** | **collapse** |
| chord detection | tp 2, fp 0, **fn 4** | the weak spot, see below |

## The three findings that matter

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
