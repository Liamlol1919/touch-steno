# Rest-State Model — validating "drift instead of position" with measurements

**Author:** Agent 2. **Date:** 2026-09-25 05:44 CEST.
`scripts/rest_model.py` — stdlib only, reproducible on the three recorded sessions.

## The question

The design premise is "drift instead of absolute position": measure features relative to a
per-contact neutral point. `MEASURED_BIOMECHANICS.md` §2 already killed the naive version of
that idea — a resting finger drifts **11.5 mm in 20 s**, which is larger than every
displacement threshold anyone proposed for this project. So the premise only survives if the
neutral point *follows* the hand. This document measures whether it does, and with which
baseline.

## Method

For every contact, after a 1 s warm-up (hand placement is not a rest sample), compute the
residual `|p − neutral|` and the rate of change of that residual, then report the worst
residual and the longest run of consecutive frames whose residual moves faster than a
threshold. Three baselines:

| baseline | definition |
|---|---|
| `fixed` | neutral = first sample of the contact (the naive implementation) |
| `ewma` | neutral = exponential moving average, τ ∈ {0.5, 1, 2, 4} s |
| `recent` | neutral = mean of the last W samples, W ∈ {9, 19, 39} frames |

Groups use the same proxy labels as `MEASURED_BIOMECHANICS.md`: REST = path < 20 mm,
MOVER = path > 100 mm, contacts shorter than 50 frames excluded.

## Result 1: the baseline matters, and the winner is the sliding window

Worst case over 17 REST and 20 MOVER contacts:

| group | baseline | param | residual p99 (mm) | residual max (mm) | worst run @40 mm/s | would fire (≥8 frames) |
|---|---|---|---:|---:|---:|---:|
| REST | fixed | – | 11.778 | 11.955 | 2 | 0/17 |
| REST | ewma | 0.5 s | 5.653 | 6.463 | 2 | 0/17 |
| REST | **recent** | **W=19** | **2.276** | **5.040** | **1** | **0/17** |
| REST | recent | W=9 | 1.454 | 3.854 | 4 | 0/17 |
| REST | recent | W=39 | 4.632 | 5.868 | 1 | 0/17 |
| MOVER | fixed | – | 30.804 | 35.843 | 27 | 20/20 |
| MOVER | ewma | 0.5 s | 17.613 | 22.143 | 25 | 20/20 |
| MOVER | **recent** | **W=19** | **12.733** | **14.455** | **21** | **18/20** |
| MOVER | recent | W=9 | 6.546 | 8.440 | 9 | 5/20 |
| MOVER | recent | W=39 | 17.760 | 21.586 | 32 | 20/20 |

- The naive `fixed` baseline loses: it carries the full 11.96 mm of drift into the feature.
- **W=19 (≈209 ms) is the sweet spot**: it cuts the REST residual max by 2.4× versus fixed
  (11.96 → 5.04 mm) while keeping MOVER runs long (21 frames) and 18/20 movers detected.
- **W=9 is too tight** — it maximises apparent separation but only 5/20 movers survive,
  which is a detector that ignores its user.
- W=39 recovers all movers but hands back most of the drift advantage.

## Result 2: the latency win, and its honest caveat

Separation grid for the residual feature at W=19 (worst REST run vs best MOVER run):

| residual speed threshold | REST worst run | MOVER best run | lowest clean persistence | latency |
|---:|---:|---:|---:|---:|
| 30 mm/s | 9 | 29 | none | – |
| 40 mm/s | 1 | 21 | k = 2 | **≈22 ms** |
| 60 mm/s | 0 | 16 | k = 1 | **≈11 ms** |

Compare with the position-velocity detector documented in `MEASURED_BIOMECHANICS.md` §3,
which needs 8 consecutive frames (≈88 ms) at 40 mm/s. The drift-relative feature reaches the
same zero-false-trigger property at **2 frames instead of 8 — a 4× latency reduction**, and at
60 mm/s even a single frame suffices.

**Caveat, stated plainly:** a 19-frame sliding baseline smooths the signal by construction, so
"2 frames" is 2 frames *of a smoothed derivative*, not 22 ms of raw sensor reaction. The
mover runs also drop (21 instead of 53) for the same reason. The comparison is fair — both
groups get the identical filter — but the latency figure should be read as *feature latency*,
and the real end-to-end number still has to be measured with the guided tempo session.

## What this changes

1. **The design's "drift instead of position" premise survives, but only with an adaptive
   baseline.** Anyone implementing the drift feature with a fixed neutral point will get the
   11.96 mm worst case and conclude the premise is wrong.
2. **The recommended rest-state model is a ~200 ms sliding window per contact**, with the
   window length as a calibration parameter (not a constant): fast drifts want a longer
   window, fast intentional strokes want a shorter one.
3. **A 4× latency reduction is on the table** for the same safety level, which matters
   because latency is the budget that ultimately limits the event rate (§1.4 of
   `CROSS_VALIDATION.md`).
4. It also gives the decoder a **drift-tolerant idle gate**: with W=19 the REST residual
   never exceeds 5.04 mm, so an idle check of "residual < 3 mm" is safe with ~40 % margin,
   while a fixed-baseline check would need 12 mm and would swallow real gestures.

## Open items

- W=19 was chosen on 17/20 contacts from one hand in one session shape. Per-user and
  per-posture window selection needs the guided rest session
  (`scripts/guided_calibration.py --task noise`).
- The sliding window is a boxcar; a Kalman filter on position and velocity per contact would
  probably dominate it and is the natural next implementation.
- MOVER coverage at W=19 is 18/20, not 20/20. The two missed contacts should be identified
  before this becomes the production detector.

## Per-user calibration artifact

`scripts/rest_calibration.py` creates a local sidecar from explicit rest and mover sources:

```bash
python3 scripts/rest_calibration.py --rest rest.jsonl --mover mover.jsonl \
  --user-label local --out calibration.json
```

The artifact records source SHA-256 hashes, rest-position covariance, every window/threshold
sweep row, the deterministic selected candidate, and the unchanged production defaults
(`40 mm/s`, 8 frames). `replay_sweep()` recomputes the sweep and compares source hashes. This
is calibration evidence, not an automatic change to `intent_filter.py`; a user-specific
operating point must be reviewed before deployment.

The artifact can also accept a caller-supplied `gesture_coverage` mapping keyed by
`(velocity_mm_s, persistence_frames)`. If supplied, selection requires both rest-clean and
the requested minimum gesture coverage; without it, `selection_basis` is explicitly
`rest_clean_only` and the result must not be read as a full 150–350 ms envelope validation.
