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
| `bimanual` | `--task bimanual` | paced left/right thumb alternation vs simultaneous contact; raw cross-hand coupling capture for issues #16/#18 | **highest unanswered hardware question** |
| `chord` | `--task chord` | is a real two-finger chord separable from a mirrored drag? | chord criterion is unvalidated |
| `noise` | `--task noise` | per-user rest floor → the per-user gate (SEPARATION_MODEL) | cheap, 60 s |
| `palm` | `--task palm` | palm-contact rest floor and false-trigger baseline | **required companion to noise** |
| `identity` | `--task identity` | labelled (contact-id, anatomical label) pairs for portable calibration | validate with `identity_dataset_check.py` |

## Order that maximises information per minute

1. **`noise`** (60 s) — smallest unit, and it immediately yields a per-user gate from the
   table in `SEPARATION_MODEL.md`. Everything else is safer once this is known.
2. **`palm`** (60 s) — captures palm contact separately from finger rest.
3. **`sectors`** (~2 min for 4 repetitions) — the accuracy number the whole report is missing.
4. **`bimanual`** (~5 min) — counterbalanced 1/2/3 Hz alternating-vs-simultaneous two-thumb
   capture; run only with stable pad placement and explicit session/hand provenance.
5. **`tempo`** (~2 min) — the training question behind the speed target.
6. **`correction`** (~3 min) — the open number from W19; run `scripts/correction_metrics.py`.
7. **`chord`**, **`identity`** — only after the above, because they are the most expensive
   interpretation per minute of capture.

## Bimanual coupling capture

This is a raw two-thumb interference capture, not a correction-throughput or same-hand chord
test. The default schedule is six 40-second blocks at 1/2/3 Hz, separated by 10-second rest
blocks:

1. 1 Hz alternating, starting left;
2. 1 Hz simultaneous;
3. 2 Hz simultaneous;
4. 2 Hz alternating, starting right;
5. 3 Hz alternating, starting left;
6. 3 Hz simultaneous.

Run it with explicit provenance:

```bash
python3 scripts/guided_calibration.py --task bimanual \
  --bimanual-rates 1 2 3 --bimanual-seconds 40 --bimanual-rest-seconds 10 \
  --session-id p01-2026-09-25 --dominant-hand right \
  --out messung/bimanual-coupling.jsonl
```

Every cue stores `bimanual_mode`, `rate_hz`, `events`, `event_hands`,
`event_provenance=expected_cue_schedule`, `hand_provenance`, `session_id`, `dominant_hand`,
and a unique `cue_id`. Expected times are targets relative to `t_start`, not observed
participant timestamps. The cued left/right label is not proof that a driver tracking ID is
anatomical left/right; identity attribution remains a separate within-session analysis.

The hardware-free plan is:

```bash
python3 scripts/session_runner.py --dry-run --quick \
  --session-id dry-run --dominant-hand unknown
```

It prints the bimanual command without creating capture or manifest files. Do not add this
task to generic sector/tempo scoring yet. A later analyzer must report realized rate,
inter-hand interval spread, simultaneous onset error, and raw coupling before any follower
suppression. This protocol produces no bimanual result by itself; stop for pain, numbness,
cramp, or unusual reach.

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
