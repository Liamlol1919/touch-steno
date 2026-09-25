# Compass Radius — the design surface, derived from our own noise

**Author:** Agent 2. **Date:** 2026-09-25 06:58 CEST.
`scripts/compass_surface.py`. Inputs are measured, not literature: per-frame noise fitted to
the 35 % on-fence rate observed on real motion (`LAYOUT_ASSIGNMENT.md`), the 8-frame evidence
floor (`SEPARATION_MODEL.md`), and the mandatory return leg.

## The two effects, and they point the same way

1. **Decoding accuracy improves with radius.** The per-frame noise is fixed (2.03 mm/frame),
   so a longer arc puts more signal into every frame. This is the opposite of what I expected
   when I first tested it: I assumed more frames would average the noise away, and measured
   the reverse — at a fixed compass radius, a longer window means a *smaller* step per frame,
   so SNR falls. **Accuracy is bought with amplitude, not with duration.**
2. **Repositioning contamination also improves with radius.** The displacement between
   neighbouring sector targets grows while the detection-window path does not, so the
   contamination fraction falls (55.2° residual error at r = 8 mm, 13.0° at r = 50 mm).

The only thing opposing a large radius is **time**: the return leg is 2r long, so the cycle
grows linearly with r.

## The surface

| r (mm) | accuracy | sector pitch (mm) | contamination error | return (ms) | cycle limit (Hz) | WPM equivalent |
|---:|---:|---:|---:|---:|---:|---:|
| 8 | 0.421 | 6.1 | 55.2° | 27 | 8.72 | 349 |
| 12 | 0.576 | 9.2 | 43.8° | 40 | 7.81 | 312 |
| **20** (current) | **0.822** | 15.3 | 29.9° | 67 | 6.47 | 259 |
| 25 | 0.904 | 19.1 | 24.7° | 83 | 5.84 | 233 |
| **30** | **0.957** | 23.0 | 21.0° | 100 | 5.32 | 213 |
| 40 | 0.990 | 30.6 | 16.0° | 133 | 4.52 | 181 |
| 50 | 1.000 | 38.3 | 13.0° | 167 | 3.93 | 157 |

## What it says about the design

- **The current r = 20 mm is a defensible operating point but not the best one.** It sits at
  82 % direction accuracy. r = 30 mm buys **+13.5 accuracy points** for **−18 % cycle rate**.
- **r = 12 mm and below are not viable**: 58 % accuracy at best, and the sector pitch (9.2 mm)
  is only 16× the resting per-frame step — the detector would be reading its own noise.
- **The choice is a product decision, not a technical one**, because of what the language
  layer can absorb. W9 makes the case that the dictionary and the correction path are the
  multiplier; the 360 WPM source attributes the entire speed margin to memorised short forms.
  Trading 18 % of the event rate for 13.5 accuracy points is a good trade **if** the LM
  absorbs the residual 4.3 %, and a bad one if it does not.

## The condition attached to every number in that table

The WPM column assumes a **600 mm/s return**, which is far above the 40 mm/s detection gate.
That return is only separable by reversal segmentation (`intent_filter.detect_reversal_events`),
and that path is currently the weaker of the two strategies
(`MEASURED_INTENT_FILTER.md` / `out_and_back_eval.py`). With a sub-gate return the cycle is
`1/(t_out + 2r/30)`, which at r = 20 mm is 1.5 Hz and at r = 30 mm is 1.2 Hz — and the
speed ceiling collapses accordingly.

So the surface above is **conditional on the reversal path working**. The cued session
(`--task sectors` at several radii, plus `--task tempo`) is what decides both the radius and
the return strategy together. They cannot be chosen independently.

## What would falsify this

- If the cued sector session shows per-sector accuracy far below the table at the same
  radius, the fitted noise is optimistic and the curve shifts left (smaller radius needed).
- If the fitted noise turns out to be dominated by *bias* rather than variance, a bias fit
  would help and the whole surface would be re-derived. Measured: it is not bias
  (|bias|/sd ≈ 0.02 at every noise level), so this is unlikely.
- If thumb reach on a 224 × 148 mm pad with both hands down cannot reach 30 mm from the wrist
  pivot in a comfortable posture, the row is unreachable regardless of the arithmetic. That
  is a measurement, and it is in the cued protocol as a feasibility check, not an assumption.
