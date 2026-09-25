# First end-to-end result on the device's own data

**Author:** Agent 2. **Date:** 2026-09-25 06:27 CEST.
The first time the full pipeline ran on the three real PTH-660 recordings and produced
auditable output rather than statistics. Command:

```bash
python3 scripts/stroke_sink.py --out stdout messung/test.jsonl
```

## Result

| session | events | strokes decoded | events/s | chord events | strokes on a sector fence |
|---|---:|---:|---:|---:|---:|
| test (10 fingers, 42 s) | 108 | 88 | 2.55 | 66 | 40 % |
| test-daumen (thumbs, 18 s) | 46 | 46 | 2.54 | 11 | 33 % |
| test-zeige (index fingers, 15 s) | 14 | 13 | 0.91 | 8 | 31 % |

Example output (ten-finger session, the decision chain per stroke):

```text
  t_start  descriptor             stroke  confidence                              text
  25510.74 W|small|single         H       edge 14.5d arc0.22 share0.80            'h'
  25510.92 E|small|single         T       edge 10.7d arc0.26 share1.00            'ht'
  25513.41 N|medium|single        -K      edge 17.5d arc0.47 share1.00            'htk'
```

## What this does and does not show

**Shows.** The closed loop runs on the device's own data without intervention: raw frames →
init-artefact filter → rest analysis → event detection with coupling suppression →
geometric descriptor → confidence and provenance → Plover-shaped output. Every stage emits
its evidence, and the transcripts are reproducible. That is what "closed loop" has to mean
before any accuracy claim is possible.

**Does not show.** None of these is a typing result:

- the sessions were **unstructured free motion**, not cued gestures, and the derived speed
  ceiling says free motion cannot be typing: 0.91–2.55 events/s against the 3.3–5.5 events/s
  a 150–218 WPM architecture needs;
- the sector map here is the 8-entry starter table, so most classes are *reported unmapped*
  rather than guessed — the transcripts are deliberately not words;
- there is no Plover dictionary behind them, so no translation is claimed.

## The two numbers worth keeping

1. **Free motion supplies 0.9–2.6 events/s; intentional input must supply 3.3–5.5.** That
   gap is the training question, and `guided_calibration.py --task tempo` measures it
   directly. It is the same gap the 360 WPM interview describes: the fingers top out, the
   language layer carries the speed.
2. **31–40 % of decoded strokes land within 10° of a sector boundary** on real motion, so
   their direction label is geometrically ambiguous. On cued synthetic gestures the same
   pipeline gets 100 %, because the operator aims where they meant to. The honest reading:
   the fence problem is a property of *free* input, and the language model has to absorb it
   (issue #7) rather than the detector.

## Next

With the tablet connected, the same two commands produce the first real accuracy numbers:

```bash
python3 scripts/guided_calibration.py --task sectors --out messung/sectors.jsonl
python3 scripts/evaluate_session.py messung/sectors.jsonl
```
