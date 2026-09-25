# Cued session protocols — what to run, and what each one decides

**Author:** Agent 2. **Date:** 2026-09-25 06:50 CEST.
All of them are in `scripts/guided_calibration.py`. They exist because the project's central
limitation is that every accuracy number so far is synthetic-but-calibrated, and because each
open question has a specific measurement attached to it.

| task | command | question it answers | status |
|---|---|---|---|
| `sectors` | `--task sectors` | 8-sector confusion matrix, axes vs diagonals, split by gesture length | **highest value** |
| `tempo` | `--task tempo` | can a trained user reach 3–5 events/s deliberately? (free motion gives 0.9–2.6) | **highest value** |
| `correction` | `--task correction` | corrections/min and repair latency at the target event rate | **the one number that decides the speed ceiling** (W19: NOT FOUND in the literature) |
| `chord` | `--task chord` | is a real two-finger chord separable from a mirrored drag? | chord criterion is unvalidated |
| `noise` | `--task noise` | per-user rest floor → the per-user gate (SEPARATION_MODEL) | cheap, 60 s |
| `identity` | `--task identity` | labelled (contact-id, anatomical label) pairs for portable calibration | validate with `identity_dataset_check.py` |

## Order that maximises information per minute

1. **`noise`** (60 s) — smallest unit, and it immediately yields a per-user gate from the
   table in `SEPARATION_MODEL.md`. Everything else is safer once this is known.
2. **`sectors`** (~2 min for 4 repetitions) — the accuracy number the whole report is missing.
3. **`tempo`** (~2 min) — the training question behind the speed target.
4. **`correction`** (~3 min) — the open number from W19.
5. **`chord`**, **`identity`** — only after the above, because they are the most expensive
   interpretation per minute of capture.

## Scoring, and the trap to avoid

`scripts/evaluate_session.py <session.jsonl>` scores against the sidecar manifest. Three
things learned the hard way, all of which produced confident wrong numbers:

- **Match per gesture, never per block.** Counting events per block invents rate ceilings.
- **Compare the decoded direction to the truth**, not a block label to a block label — that
  comparison is trivially true and measures nothing.
- **Report the realised rate, not the requested one.** A generator that cannot realise the
  requested rate will happily report a clean result at a rate it never produced
  (`BENCHMARK_RESULTS.md` addendum 3).

Every one of those is now pinned by a test. When scoring a cued session, check the realised
rate before quoting any rate-dependent number.

## Recording hygiene

- Keep the raw JSONL. The traces are the evidence; the manifest is only the label.
- For `identity`, run `scripts/identity_dataset_check.py` and require exit 0 before using the
  capture for anything.
- Note the date and the hand. Every coupling and rest number in this repo is single-hand and
  per-session; a claim that outlives one session needs a new capture, not a new argument.

## What no protocol can substitute for

The *cross-session* transfer of the coupling model, and anything across hands. Tracking IDs
are ephemeral (issue #9), so the coupling matrix is rebuilt per session by necessity, and the
only route to portability is the finger-identity model, which needs the `identity` capture
plus a model. Until then, calibrate at the start of each session and say so.
