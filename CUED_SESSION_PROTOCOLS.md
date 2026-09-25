# Cued session protocols — what to run, and what each one decides

**Author:** Agent 2. **Date:** 2026-09-25 06:50 CEST.
All of them are in `scripts/guided_calibration.py`. They exist because the project's central
limitation is that every accuracy number so far is synthetic-but-calibrated, and because each
open question has a specific measurement attached to it.

| task | command | question it answers | status |
|---|---|---|---|
| `sectors` | `--task sectors` | 8-sector confusion matrix, axes vs diagonals, split by gesture length | **highest value** |
| `tempo` | `--task tempo` | can a trained user reach 3–5 events/s deliberately? (free motion gives 0.9–2.6) | **highest value** |
| `correction` | `--task correction` | cue-to-undo-motion latency; text-repair latency only with an explicit repair log | **highest unresolved speed number** (W19: NOT FOUND in literature) |
| `chord` | `--task chord` | is a real two-finger chord separable from a mirrored drag? | chord criterion is unvalidated |
| `noise` | `--task noise` | per-user rest floor → the per-user gate (SEPARATION_MODEL) | cheap, 60 s |
| `palm` | `--task palm` | palm-contact rest floor and false-trigger baseline | **required companion to noise** |
| `identity` | `--task identity` | labelled (contact-id, anatomical label) pairs for portable calibration | validate with `identity_dataset_check.py` |

## Order that maximises information per minute

1. **`noise`** (60 s) — smallest unit, and it immediately yields a per-user gate from the
   table in `SEPARATION_MODEL.md`. Everything else is safer once this is known.
2. **`palm`** (60 s) — captures palm contact separately from finger rest.
3. **`sectors`** (~2 min for 4 repetitions) — the accuracy number the whole report is missing.
4. **`tempo`** (~2 min) — the training question behind the speed target.
5. **`correction`** (~3 min) — the open number from W19; run `scripts/correction_metrics.py`.
6. **`chord`**, **`identity`** — only after the above, because they are the most expensive
   interpretation per minute of capture.

`correction_metrics.py --repair-log` accepts only JSONL records with numeric `t`,
`type="text_repair"`, `action="undo"`, `cue_id` matching the manifest, and
`clock="monotonic"`. A final transcript file or sensor timestamp is not treated as proof
of text repair.

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
- For `identity`, run `scripts/identity_dataset_check.py --mapping identity-map.json` and
  require exit 0 before using the capture for anything.
- Note the date and the hand. Every coupling and rest number in this repo is single-hand and
  per-session; a claim that outlives one session needs a new capture, not a new argument.

## What no protocol can substitute for

The *cross-session* transfer of the coupling model, and anything across hands. Tracking IDs
are ephemeral (issue #9), so the coupling matrix is rebuilt per session by necessity. A
validated anatomical identity model or a per-session hand-relative association could provide
portable labels; neither is currently validated for this device. Until then, calibrate at
the start of each session and say so.
