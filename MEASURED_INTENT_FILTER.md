# Measured Intent Filter — the "step 2 trigger", with measured constants

**Author:** Agent 2. **Date:** 2026-09-25 05:37 CEST.
`scripts/intent_filter.py` implements the trigger the design chat asked for
(„Geschwindigkeits- und Dominanz-Filter … während der echte Anschlag sofort durchgeht"),
but every constant comes from `MEASURED_BIOMECHANICS.md` instead of from intuition.

## What it does

```text
evdev SYN frames (mm, tracking-id)
  -> strip reader init artefacts ([0,0,0] lead frames)      kinematics._strip_uninit_leads
  -> per-frame step vector + speed per contact              scripts/intent_filter.steps_of
  -> event candidate: >= 8 consecutive frames with speed >= 40 mm/s
  -> mover = contact with the largest per-frame step
  -> for every other contact: per-pair signed regression fit, suppress if r^2 >= 0.5
  -> emit ranked events: mover + suppressed followers + unexplained contacts
```

It **never emits a key**. It emits auditable event candidates, so the first thing a human
does with the output is check whether the filter saw what the operator intended. That is
deliberate: `DECODER_DESIGN.md` requires a reversible path, and an irreversible trigger
cannot be debugged.

## Measured constants and where they come from

| constant | value | evidence |
|---|---|---|
| `MIN_SPEED_MM_S` | 40 | rest speed p99 = 57 mm/s, rest runs at 20 mm/s reach 13 frames — a lower gate is inside the rest distribution (MEASURED §2/§3) |
| `MIN_RUN_FRAMES` | 8 (≈ 88 ms at 91 Hz) | rest worst run is 7 frames at 30–40 mm/s and 5 at 60 mm/s; every driven contact runs 19–278 frames (MEASURED §3) |
| `MIN_R2_TO_SUPPRESS` | 0.5 | finger row r² = 0.62–0.92 (suppressible), cross-hand 0.72–0.74, thumb↔thumb 0.10–0.25 (not suppressible) (CROSS_VALIDATION §1) |
| initial-artifact filter | both coords ≠ 0 | reader seeds new tracking ids with `[0,0,0]` and reports 2–3 frames before x/y arrive (MEASURED §6) |

## Result on the three real sessions

| session | frames | events | events/s | suppressed as dragged | unexplained (kept) |
|---|---:|---:|---:|---:|---:|
| test | 3845 | 108 | 2.56 | 175 | 797 |
| test-daumen | 1643 | 46 | 2.55 | 0 | — |
| test-zeige | 1400 | 14 | 0.91 | 1 | — |

Two things to read from this:

1. **The finger row suppresses cleanly, the thumbs do not.** In `test` (ten fingers down)
   the filter suppresses 175 follower contacts with r² between 0.55 and 0.93. In
   `test-daumen` (thumbs driven) it suppresses **zero**, exactly as the r² = 0.10–0.25
   measurement predicted. The filter's behaviour is the measurement, not a heuristic.
2. **The free-motion event rate is 2.56 events/s.** In an unstructured session with ten
   fingers resting, the measured detector finds ~2.6 distinct supra-threshold events per
   second. If every event were one syllable, that is ~150 syllables/min ≈ **85–110 WPM**;
   a syllable architecture needing 1.5–2 events per syllable would land lower. This is a
   day-0 baseline, not a ceiling.

That second number is the most important one in this document, and it is measured rather
than argued: **the bottleneck for 150–250 WPM is not the 88 ms detector latency, it is how
many genuinely distinct supra-threshold events a hand produces per second.** 250 WPM would
need 4–8 syllables/s, i.e. roughly 2–3× the event rate that free finger motion produced
here. Whether a trained user can produce that is a training question, not a sensor
question — and it is exactly what the slow-stroke and chord-on-cue sessions in
VECTOR_DESIGN_CRITIQUE §8 are designed to answer.

## Usage

```bash
python3 scripts/intent_filter.py session.jsonl                 # table
python3 scripts/intent_filter.py --json session.jsonl           # machine readable
python3 scripts/intent_filter.py --min-speed 60 --min-run 5 session.jsonl   # sweep
python3 scripts/kinematics.py --record --seconds 20 --out s.jsonl           # capture
```

## Known limits

- Events are delimited by the persistence rule, not by gesture boundaries: two gestures
  90 ms apart merge into one event. A chord-grammar layer is still required.
- The pair fits are estimated from the same session they are applied to, so the output is
  optimistic; a real deployment calibrates on a separate session.
- `MIN_R2_TO_SUPPRESS` is a global cut; per-pair calibrated thresholds (with an
  uncertainty estimate) are the honest next step.
- Proxy labels: "suppressed" means "explained by a fitted linear relation to the mover",
  not "known to be unintentional".
