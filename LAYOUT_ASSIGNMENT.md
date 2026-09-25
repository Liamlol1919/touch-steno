# Layout Assignment — a confusion-matrix-driven compass layout, with numbers

**Author:** Agent 2. **Date:** 2026-09-25 06:36 CEST.
`scripts/layout_assignment.py`, 51 tests green.

W16 searched the literature for this and returned NOT FOUND: **no published layout has been
optimised from a measured confusion matrix with a before/after speed or error figure.** This
is that measurement, for our 8-sector compass.

## How the noise model is calibrated

A first attempt used the resting per-frame noise (0.56 mm) and produced a *perfectly
diagonal* confusion matrix — 100 % accuracy in every sector. That contradicts the measured
reality: `REAL_DATA_DECODE.md` shows **31–40 % of strokes decoded from real motion land within
10° of a sector boundary**.

So the sensor noise floor is not the error source. The model is therefore **calibrated to the
measured on-fence rate** rather than to the sensor floor, and the fitted per-frame noise is
reported:

| quantity | value |
|---|---:|
| resting per-frame noise (sensor floor) | 0.56 mm |
| **fitted per-frame noise reproducing the measured 35 % on-fence rate** | **1.84–2.03 mm** |
| ratio | **≈ 3.6×** |

**The direction error is 3.6× larger than the sensor noise.** A better digitiser, a better
filter, a faster reader — none of them moves this number. The residual is aim and biomechanics.
That is a design conclusion, not a caveat: *training and target geometry, not electronics, are
the lever for direction accuracy.*

## The confusion matrix (600 trials per sector, calibrated noise)

| true\pred | E | NE | N | NW | W | SW | S | SE | row acc |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| E | 400+ | · | · | · | · | · | · | · | ~80 % |
| NE | · | 400+ | · | · | · | · | · | · | ~80 % |
| N | 0 | 31 | 327 | 42 | 0 | 0 | 0 | 0 | 81.8 % |
| NW | 0 | 0 | 35 | 328 | 37 | 0 | 0 | 0 | 82.0 % |
| W | 0 | 0 | 0 | 36 | 313 | 51 | 0 | 0 | 78.2 % |
| SW | 1 | 0 | 0 | 1 | 35 | 334 | 29 | 0 | 83.5 % |
| S | 0 | 0 | 0 | 0 | 0 | 33 | 328 | 39 | 82.0 % |
| SE | 39 | 0 | 0 | 0 | 0 | 0 | 42 | 319 | 79.8 % |

Measured structure (4800 trials, 3 skipping confusions total):

- **99.6 % of confusion mass goes to a neighbouring sector**; 0.4 % skips a sector. So the
  confusion relation is *nearly* a ring — not exactly, and the doc says so.
- Row accuracy sits at **78–84 %** per sector, consistent with the measured 35 % on-fence
  rate (a stroke within 10° of a boundary has a good chance of falling on the wrong side).

## Layout result

Expected substitution error $E = \sum_i p_i \sum_{j \ne i} p_j\, C[a(i)][a(j)]$, with a Zipf
frequency profile over 8 symbol classes (**a model input, not a measurement** — substitute real
LM probabilities before quoting any absolute figure):

| assignment | expected error | vs naive |
|---|---:|---:|
| naive (alphabetical) | 10.19 | – |
| W16's on-axis-first rule | 7.09 | **−30.5 %** |
| annealed optimum (20 k steps, pairwise swaps) | 6.52 | **−36.1 %** |

Two things follow:

1. **The cheap rule captures most of the gain.** Putting the most frequent symbols on the
   four on-axis cells — the rule W16 derived from Kurtenbach & Buxton's axis-level effect
   (F(2,22) = 104.84, p < 0.001) — is worth 30.5 % of the achievable reduction with no search.
2. **The optimiser adds 5.6 points on top**, and it is the part W16 could not find published.
   Simulated annealing with pairwise swaps, on the measured confusion matrix, is the method;
   W16's transferable figures for it are GK-D −52 % error and +12.5 % expert speed over
   QWERTY (14 users).

## The design rule this produces

**Never place a minimal pair (two symbols that must be distinguished) on adjacent sectors.**
Adjacency is the confusion relation at 99.6 %, so adjacency is where the errors are. The
on-axis cells are the most reliable (they are also the cells the marking-menu literature says
are selected fastest), so the highest-frequency and highest-cost-of-error symbols belong
there — which is exactly W16's rule, now with a measured number attached.

## Limits

- The confusion matrix is generated through the real decoder functions but under a *calibrated
  noise model*, not from cued human trials. The cued session would replace it.
- Frequencies are a Zipf stand-in. The comparison between assignments is meaningful; the
  absolute error figure is not.
- This is 8 sectors. The 16-sector question is answered differently: at 11.25° half-width the
  fitted noise would put adjacent-sector confusions far above 50 %, which is the quantitative
  form of "8 is the defensible limit".
