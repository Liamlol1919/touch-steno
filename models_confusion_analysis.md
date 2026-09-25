# Compass models: confusion analysis

## Scope and measured capture

This analysis concerns the real capture `s12.jsonl`: 24 measured cued trials (3 per class), 8 compass classes, one operator, one session, and `n=63` strokes. The capture has **no error bars**. The confusion table reported by `scripts/evaluate_session.py` was:

```text
    E->E 4, E->W 3 | N->N 3, N->S 3 | S->S 3, S->N 4
    W->W 4, W->E 4 | NE->NE 4, NE->SW 4 | SW->SW 4, SW->NE 2
    NW->NW 4, NW->SE 4 | SE->SE 4, SE->NW 3
```

These are observed counts, not estimates with uncertainty intervals.

## Error structure

The off-diagonal mass is concentrated on antipodal pairs, with **N as the one exception**. The antipodal counts visible in the table are `E->W 3`, `W->E 4`, `N->S 3`, `S->N 4`, `NE->SW 4`, `SW->NE 2`, `NW->SE 4`, and `SE->NW 3`. In the reported capture, N also scatters across E, S, SE, SW, and W, so N must not be described as a clean antipodal-only class. The diagonal counts are `E->E 4`, `W->W 4`, `N->N 3`, `S->S 3`, `NE->NE 4`, `SW->SW 4`, `NW->NW 4`, and `SE->SE 4`: the diagonal is nearly split evenly for every direction.

## Folded and unfolded comparison

The antipodal fold reduces the label space from 8 classes to 4: N/S, E/W, NE/SW, and NW/SE. Its chance level is therefore 25%, versus 12.5% unfolded. The descriptor's folded and unfolded classifications must be computed from the same descriptors, with the fold applied to both each training label and its held-out test label. `scripts/field_separability.py --fold-antipodal` now reports both result sets in one run and uses the script's existing one-sided 95% Wilson upper bound for both.

The unfolded `s12.jsonl` nearest-class-mean run is 45.83% (`11/24`) with an upper 95% bound of 62.12%; the recorded 1-NN result is 100% and remains untrustworthy with three trials per class in a high-dimensional descriptor space. The paired folded run was executed as `python3 scripts/field_separability.py --session /home/lilat320/Projekte/session-stand/messung/s12.jsonl --manifest /home/lilat320/Projekte/session-stand/messung/s12.manifest.jsonl --fold-antipodal` (run from the repository root; the script's own usage line shows the same files as `../../session-stand/messung/s12.jsonl` relative to `scripts/`). It produced **4 classes**, a **25% chance level**, a folded class-mean top-1 of **50.00%** with an upper 95% bound of **65.92%**, and a folded 1-NN top-1 of 100% with an upper 95% bound of 100%. The recorded folded output was:

```text
ANTIPODAL FOLD WARNING: a folded class cannot distinguish a direction from its opposite, so a wrong symbol is indistinguishable from a correct one.
folded classes     4
folded chance      0.2500  (25.0%)
folded 1-NN top-1  1.0000   upper95 1.0000
folded class-mean  0.5000   upper95 0.6592
```

**The result does not favour folding.** Folded class-mean accuracy rises only 4.17 points, from 45.83% to 50.00%, and its upper bound rises with it, from 62.12% to 65.92%. The two intervals overlap almost entirely, and the descriptor cannot separate the four antipodal classes any better than it separated the eight compass classes.

24 trials and only 3 per class are far too few to separate the unfolded and folded results cleanly, and the Wilson bounds overlap. The 4.17-point difference is therefore not a secure performance improvement, and in any case it measures a different target rather than a better one.

## Why folded accuracy is not a quality measure

Folding trades a detectable error for an undetectable one. If a user intends N but the system produces S, the N/S folded prediction is correct-looking even though the wrong symbol was produced. The same applies to E/W, NE/SW, and NW/SE. Consequently, folded accuracy is **not comparable to unfolded accuracy as a quality measure**: it changes the target and rewards a specific failure mode instead of resolving it.

These measurements are from **thumb-compass labels in one session with one operator**. They do **not** transfer to a whole-hand field gesture. The control experiment comparing a thumb compass with an actual whole-hand field gesture is still unrun; no WPM, hardware-performance, or general-input claim follows from this analysis.
