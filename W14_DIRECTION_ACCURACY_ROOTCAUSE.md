# W14 — Direction-accuracy root cause: numbers, not narrative

Frame clock used throughout: 91 Hz → `dt = 10.9890 ms`, 8-frame window `T8 = 87.9121 ms`.
Computed with `python3` (`/tmp/opencode_calc1.py`, `calc3.py`, `calc3b.py`, `calc3c.py`,
`calc1b.py`, `calc4.py`, `calc4b.py`, `calc4c.py`). No external sources cited; every number
below is program output or direct arithmetic on program output. Noise `sigma` values are
*assumed sweeps* (not measured) — stated wherever they appear.

Baseline: chance on 8 sectors = 0.125. Sector half-width = 22.5°.

## 1. Ease-in profile: is the first 88 ms direction a good estimate of the full stroke?

Result: for motion along a **fixed heading, exactly yes regardless of speed profile**.
The displacement over any sub-interval is colinear with the full displacement; verified
numerically (30° straight stroke, D=15 mm: first-8 and full directions both 30.0° for ramp
and raised-cosine profiles). So ease-in *alone* cannot rotate a sector decision.

It matters only through two second-order channels: (a) SNR — the early slice is short, so
endpoint noise is a larger fraction; (b) curvature — if heading changes during the stroke,
the early slice points somewhere else.

(b) quantified with a constant-speed stroke whose heading rotates linearly by `curve_total`
over the stroke (program output):

| total heading change | T=150 ms: first-8 vs full bias | T=350 ms: bias | flips 22.5°? |
|---|---|---|---|
| 20° | −4.14° | −7.49° | no / no |
| 45° | −9.31° | −16.85° | no / no |
| 90° | −18.63° | −33.70° | no / **yes (350 ms only)** |

Reading: the first-88 ms direction is a good (<~5°) estimate of the full-stroke direction
only if total heading change is ≲20° on a 150 ms stroke, ≲10° on a 350 ms stroke
(long strokes dilute the early slice: 8/14 frames vs 8/32 frames). A sector flip from
curvature alone needs a large hook (~90° total on a slow stroke). **Cannot determine
analytically whether B strokes hook** — measurement that settles it: log per-frame (x,y),
compute heading(t) and `angle(first-8 vector) − angle(full vector)` per gesture; histogram
tells you if curvature or noise dominates.

## 2. Rest-drift contamination (0.5 mm/s)

Drift displacement over the window: `0.5 × 0.087912 = 0.043956 mm`
(single frame: `0.005495 mm`). Stroke displacement in 88 ms:

| speed | disp in 88 ms | drift/disp | worst-case rotation atan(drift/disp) |
|---|---|---|---|
| 40 mm/s | 3.5165 mm | 1.250% | 0.716° |
| 60 mm/s | 5.2747 mm | 0.833% | 0.477° |
| 100 mm/s | 8.7912 mm | 0.500% | 0.286° |
| 150 mm/s | 13.1868 mm | 0.333% | 0.191° |
| 200 mm/s | 17.5824 mm | 0.250% | 0.143° |

Worst case assumes drift exactly perpendicular to motion. Drift needed to reach a sector
boundary (22.5°) from center: `disp × tan(22.5°)`:

| speed | needed drift disp | needed drift speed | factor over observed 0.5 mm/s |
|---|---|---|---|
| 40 mm/s | 1.4566 mm | 16.57 mm/s | 33.1× |
| 100 mm/s | 3.6414 mm | 41.42 mm/s | 82.8× |
| 200 mm/s | 7.2829 mm | 82.84 mm/s | 165.7× |

Simulation check (straight stroke, `sigma=0`, 0.5 mm/s drift perpendicular, 5000 trials):
accuracy 1.000 for every estimator, both D=10/T=200 and D=5/T=150, centered and
near-boundary (2.5° margin) cues. **Verdict: ruled out as primary cause.** Drift is
1–2 orders of magnitude too small to rotate a 45° sector decision. Measurement that would
confirm: static-contact position log; the number to beat is ~16–83 mm/s sustained
perpendicular drift over 88 ms.

## 3. Speed gate (≥40 mm/s) × ease-in: how many frames pass?

"10-frame ease covering 20 mm" (Tease = 109.89 ms, avg 182 mm/s) — per-frame mean speeds:

- constant velocity: all 182.0 → **10/10 pass**
- linear velocity ramp 0→peak: 18.2, 54.6, 91.0, … 345.8 → **9/10 pass** (only frame 1 blocked)
- raised cosine: 44.5, 129.3, … 44.5 → **10/10 pass**
- smoothstep cubic: 51.0, 138.3, … 51.0 → **10/10 pass**

So for large/fast strokes the gate barely bites. It bites for small/slow strokes.
Full-stroke sweep (frames ≥40, longest consecutive run; detection needs run ≥8):

| D | T | ramp n≥40 / run / 8-ok | cos n≥40 / run / 8-ok | cubic n≥40 / run / 8-ok |
|---|---|---|---|---|
| 5 mm | 150 ms | 6/6 F | 6/6 F | 6/6 F |
| 5 mm | 200 ms | 4/4 F | 6/6 F | 0/0 F |
| 8 mm | 200 ms | 9/9 T | 9/9 T | 10/10 T |
| 8 mm | 350 ms | 4/4 F | 8/8 T | 0/0 F |
| 10 mm | 200 ms | 11/11 T | 10/10 T | 12/12 T |
| 10 mm | 350 ms | 10/10 T | 12/12 T | 8/8 T |
| 20 mm | any 150–350 | 12–21 / T | 10–19 / T | 12–24 / T |

Since both generators detect 100%, B strokes must live in the passing regime
(roughly D≳8–10 mm at these durations). Consequence: the gate **delays** the window start
(index of first 8-run, 0-based; ms = frames×10.989):

- D=10/T=200: ramp delay 7 fr (76.9 ms), cos delay 4 fr (44.0 ms)
- D=8/T=200: ramp 9 fr (98.9 ms), cos 5 fr (54.9 ms)
- D=20/T=200: ramp 4 fr (44.0 ms), cos 3 fr (33.0 ms)
- D=10/T=350: ramp 22 fr (241.8 ms), cos 10 fr (109.9 ms)

**Verdict: the gate does not explain direction error directly, but it decides *which*
segment the "first 8" window actually is** — for eased strokes it is mid-stroke, not onset,
and for slow strokes it sits near the velocity peak. Any fix to the estimator must account
for this shift (the window is already speed-selected). Measurement that settles the real
operating point: per-frame speed trace per gesture; count sub-gate prefix length and record
where the firing 8-run sits inside the stroke.

## 4. Estimator: first-8 vs weighted vs last-8 vs full-stroke

Simulations: straight ramp stroke + isotropic per-frame position noise `sigma` (assumed
sweep) + 0.5 mm/s drift; score vs cued sector. Key mechanism: true first-8 displacement on
a ramp is small (D=10/T=200 → 1.932 mm; D=5/T=150 → 1.717 mm; D=20/T=200 → 3.864 mm;
D=25/T=275 → 2.555 mm), so endpoint noise (`0.3·√2 = 0.424 mm` at sigma=0.3) is
11–25% of the measured vector (equivalent angle 6–14°) — while the full stroke is 5–10×
longer with the same endpoint noise.

Centered cue (0°, 22.5° margin), sigma=0.3:

| stroke | first-8 | full | last-8 | speed-weighted (whole event) |
|---|---|---|---|---|
| D=5/T=150 | 0.876 | 1.000 | 0.9998 | 0.9958 |
| D=10/T=200 | 0.921 | 1.000 | 1.000 | 1.000 |
| D=20/T=200 | 0.9996 | 1.000 | 1.000 | 1.000 |
| D=25/T=275 (A-like) | 0.9795 | 1.000 | 1.000 | 1.000 |

Off-center / near-boundary cues degrade faster and show the estimator gap better
(cue 30°, 7.5° margin): sigma 0.3 → first-8 0.721 / full 0.999 / last-8 0.984;
sigma 0.6 → 0.531 / 0.935 / 0.851; sigma 1.0 → 0.376 / 0.820 / 0.734.
Near-boundary cue 20° (2.5° margin), sigma 0.4: first-8 0.553 / full 0.775 / last-8 0.697.
Averaging per-frame *unit* directions over the first 8 is consistently worse than the
endpoint vector (e.g. 0.565 vs 0.721 at cue 30°/sigma 0.3) — equal votes for slow noisy
frames amplify noise; do not do this.

Two related A-vs-B facts (arithmetic on computed windows): A strokes are 25 frames
(274.7 ms); at 100 mm/s that is 27.5 mm vs B's first-8 slice of 8.8 mm (3.1× more
displacement, ~3× smaller endpoint-noise angle). If A accumulates over the whole event
(and can use the 0.65× follower as a second sample), its SNR advantage alone predicts the
1.00 vs 0.19–0.50 direction. The 0.19–0.50 band itself is reproducible in simulation only
with large sigma (0.4–1.0 mm) and/or near-boundary cues and/or unit-voting — i.e. **the
stated 0.5 mm/s drift cannot produce it; unmeasured position jitter or curvature must
dominate**. I cannot determine which analytically. Measurement that settles it: static
jitter log (fit sigma per axis), then replay the four estimators on recorded strokes and
report accuracy vs cue and vs true full-displacement (these differ for hooked strokes —
e.g. a 45° hook over the stroke puts the full vector 29.7° off the cue: first-8 scores
1.00 vs cue while full scores 0.00; define ground truth before comparing).

## Ranked fixes for an ease-in stroke (largest expected gain first)

1. **Accumulate over the whole event (or last-8 / speed-weighted over the whole event),
   not the first 8.** Measured gain in simulation: +0.08 (centered) to +0.28 (off-center,
   sigma 0.3, D=10/T=200: 0.72→1.00) absolute sector accuracy; last-8 captures most of it
   (+0.26). Rationale: uses 5–10× more displacement with the same endpoint noise and
   weights the high-SNR peak-velocity segment the gate already selected.
2. **Remove any per-frame direction averaging/voting; use the endpoint displacement vector
   (optionally speed-weighted).** Unit-voting cost ~0.16 absolute in the same setup
   (0.72→0.56). If the code normalizes per-frame vectors before summing, this is a bug-class fix.
3. **Account for gate delay (cause 3):** start the direction window at peak speed or.delay-compensated position, not at stroke onset assumption. No accuracy number attaches to this
   alone — it determines what segment fix #1 sees.
4. **Ease-in shaping (cause 1):** only helps via SNR/curvature; straightening the early
   heading (keep total heading change ≲10–20°) caps bias at ≲5–9°. Smaller lever than #1.
5. **Rest-drift suppression (cause 2): last.** At 0.25–1.25% of signal and ≤0.72° worst
   rotation, it cannot flip sectors; skip unless static logs show drift 30×+ larger.

What I could not determine analytically: the true per-frame position noise sigma, the true
heading(t) curvature of B strokes, and whether the implementation sums displacements or
unit directions — all three change the ranking magnitude (not the order). The single
measurement that settles all of it: timestamped per-frame (x, y) per contact for a sample
of B strokes plus static holds; recompute first-8 / full / last-8 / speed-weighted vectors
offline and score vs cue.
