# VERTICAL SLICE — Field-Set Word Entry

**STATUS: KILLED.** This concept's only supporting figure, class-mean top-1 0.4583, was
withdrawn after a permutation null test. It is no longer a candidate concept awaiting an
acceptance test. The specification is preserved for possible revival only if a future
measurement supports it; it is not evidence that the design works.

**This is the ninth retraction in the project; the null test lives in
`scripts/field_null_test.py`.**

Everything else in this repository was generated, scored and killed. This concept was
formerly the survivor of last resort, not because it scored well, but because the measured
gate numbers did not close it. The null test has now closed it.

---

## 1. Why this and nothing else

| Measured | Value | What it kills |
|---|---|---|
| U (contact ambiguity, lower bound) | 0,9491 / 0,9980 vs a 0,10 gate | every concept that needs to know **which** contact moved |
| Major-axis dynamic range | 0,5 mm | every concept using contact-ellipse geometry |
| Field separability, 8 compass classes | **withdrawn: 0,4583; permutation null mean 0,5685, one-sided p = 0,9460** | the concept is **KILLED** |

The withdrawn figure came from 24 measured cued trials, 8 compass classes, 3 per class, one
operator, one session, n=63 strokes, thumb-compass labels, with no error bars. Under 1000
permutations, the observed value was below the null mean; descriptor dimension was 57. The
result is an artifact of fitting a 57-dimensional descriptor to 24 samples, not evidence
that a hand carries class information. This design is killed by the null test, not by its
own specification.

## 2. The primitive

**One touch-down to lift-off. The whole ten-contact field deforms into one of K shapes. The
shape names a word.** Not a compass. Not a traced letter. The symbol is a **configuration of
the hand**, and the decoder never asks which finger did what.

## 3. Encoding

**One event → one word.** No letter layer, no syllable layer, no chord algebra.

- Vocabulary: **K = 32 words** in the first slice. 32 shapes is within reach for a
  hand-deformation vocabulary and keeps the class-mean classifier's variance acceptable at
  the sample sizes one person can produce.
- `log₂ 32 = 5 bits/event`, so at the certified 5,7 events/s ceiling the arithmetic is
  **28,5 bits/s** — a ceiling, not a rate.
- The descriptor is **permutation-invariant**: sorted radii from the centroid, the sorted
  pairwise-distance multiset, bounding-box aspect, and log contact count. Contact order,
  TID, major, minor and orientation are **excluded by construction**, because those are
  exactly the quantities the gate measurements disqualified.
- Word spelling is handled by a session dictionary mapping the accepted shape to a word.
  Out-of-vocabulary words are a **separate escape gesture**, not a guess.

**This deliberately abandons the "1–2 strokes per 5-letter word" premise.** The
token-weighted, pinned-corpus English figure needs **4.189 events per 5-letter word at 3
events per syllable**, which is 109.5 percent (about 110 percent) over the 2-event cap.
At **2 events per syllable**, the same corpus arithmetic needs **2.79 events per
5-letter word**, 39.7 percent (about 40 percent) over the cap. A syllable-level code
therefore cannot honour that premise at any alphabet size. A word-level code sidesteps
it, and pays for it by requiring the user to remember which shape means which word.

> **Overshoot correction (2026-09-25):** the audit found that the prior 39 percent
> overshoot had been attached to the 4.189 count. The correct 39.7 percent pairing is
> 2.79 events per 5-letter word at 2 events per syllable, over the 2-event cap.

## 4. State machine

Five states, no cross-event history beyond the committed buffer.

1. **ARMED** — holds the last stable reference cloud (the unordered point set).
2. **MOVING** — accumulates the current cloud; computes the descriptor each frame; tracks
   the field's best-fit similarity transform to the reference.
3. **SETTLED** — movement energy falls below the segmentation floor for ≥88 ms.
4. **CLASSIFY** — descriptor → nearest class centroid among the K trained prototypes.
5. **EMIT or ABSTAIN** — emit only if (a) the margin over the runner-up clears the
   calibrated threshold, (b) contact count matches a trained prototype, and (c) no
   assignment ambiguity was flagged. **Otherwise: silence, and the buffer does not advance.**

The abstain path is not a fallback. It is the design's primary safety property: a wrong word
is worse than no word, and the user must be able to trust that a committed word is plausible.
Threshold is learned per session, never hardcoded.

**Event boundary:** movement energy below threshold for 88 ms, not contact lift. Lift is
unusable — with ten contacts resting, an all-up gap essentially never occurs.

---

## 5. Five-axis self-critique

Scored honestly, before any test.

| Axis | Score | The objection |
|---|---|---|
| Hand anatomy / biomechanics | **5/10** | whole-hand shape control is unmeasured; fatigue over a long session is entirely unmeasured |
| Contact identity / observability | **6/10 — withdrawn** | the one axis with positive evidence rested on the withdrawn class-mean figure; n=24 from one hand in one session, and the labels were thumb-compass cues |
| Timing / throughput / corrections | **3/10** | a whole-hand shape change is far slower than the 176 ms floor allows; realistic rate unknown, possibly 0,3–0,8 /s |
| Learnability / eyes-free | **4/10** | 32 arbitrary hand shapes is a real memory load with no compositional structure, and no tactile confirmation exists |
| Implementation / privacy / validation | **7/10** | fully offline, cheap to compute, low privacy risk; validation rests on one operator |
| **Total** | **25/50** | formerly the lowest surviving score in the project; the supporting figure is withdrawn |

The observability score is retained only as a record of the original self-critique. It now
rests on a withdrawn figure and must not be treated as positive evidence.
## 6. The number that decided it — withdrawn

The class-mean separability figure **0,4583 existed, but is withdrawn** under the
permutation null test: null mean **0,5685**, one-sided p = **0,9460** (1000 permutations;
descriptor dimension 57). It was based on 24 measured cued trials, 8 compass classes,
3 per class, one operator, one session, n=63 strokes, thumb-compass labels, and no error
bars. The observed value was below the null mean, so the result is an artifact of a
57-dimensional descriptor fitted to 24 samples, not evidence for this concept. The
withdrawal rule was fixed before the run: p >= 0.05 means withdraw the figure; p = 0,9460
therefore selects withdrawal.

- **FATAL:** class-mean top-1 at or below chance, upper 95 % bound included. That would
  mean the descriptor was reading the thumb all along, and this concept dies with every
  other single-contact idea.
- **VIABLE:** upper 95 % bound comfortably above chance on non-compass field gestures. Then
  a field-based method is real and this is the only surviving direction.

**The withdrawn figure is not evidence for this concept. The concept is KILLED by the null
test.**

## 7. The single acceptance test

```bash
python3 scripts/field_gesture_probe.py
```

Cued whole-hand shapes — spread, fist, cup, ridge, twist, pinch, flat, and **STILL** as an
explicit null class — then the separability script on the result. Under three minutes of
cues. The null class is included so a detector that merely fires on drift cannot pass.

The verdict is fixed before the run so it cannot be reinterpreted afterwards.

## 8. If it passes, the next three things

1. **Scale the vocabulary honestly.** 32 words proves the channel. Text entry needs
   thousands, and the first honest test is whether separability survives K = 128, then 512,
   with the null class retained.
2. **Build the escape path.** OOV words need a real mechanism, or the system is a toy
   regardless of accuracy.
3. **Measure what was never measured:** seconds-per-correction, hands-free correction cost,
   and fatigue drift across a real session.

---
## 9. What is not claimed

No WPM. No accuracy figure. No universality. The 47,6 % sector accuracy is one person, one
session, one thumb, n = 63, no error bars, and with one operator **universal accuracy is
unidentifiable rather than merely unmeasured**. The withdrawn figure was a same-session,
same-subject result from compass labels that may not transfer. Timing figures are arithmetic
ceilings at the sensor event rate; whole-hand shapes are far slower and the real rate is
unmeasured.

**This concept is killed, not a result. Its specification is preserved for possible revival
if a future measurement supports it.**

---

## 10. Status: KILLED — the acceptance test ran and returned void because the pad was empty

`scripts/field_gesture_probe.py` was executed on 2026-09-25 with `--seconds 3 --reps 2`:
20 cues, **0 frames captured**.

The cause was established rather than assumed. A direct five-second read of
`/dev/input/event19` returned **0 events** with the device openable and no process holding
it. The digitiser was readable and unobstructed; **nothing was resting on the pad**. The
capture is therefore **void, not failed** — and the tool reported exactly that, which is the
behaviour fixed in `b96f7cc`.

**No acceptance-test result exists.** The withdrawn figure was from 24 measured cued trials,
8 compass classes, 3 per class, one operator, one session, n=63 strokes, thumb-compass labels,
with no error bars; the null test used 1000 permutations and found null mean 0,5685 versus
observed 0,4583 (descriptor dimension 57), one-sided p = 0,9460. The observed value was
below the null mean, so the concept is KILLED by the null test, not by its design. The
closing project status is: **22 candidates generated, 0 validated, 0 surviving signals.**

### What this means for the project's status

| | |
|---|---|
| Vertical slice | specified, self-scored 25/50, **KILLED by the null test** |
| Design space | **closed** |
| Compass / single-thumb families | closed on measurement, independently of this |
| Ten-contact field | **closed; the last positive signal was withdrawn** |

This document must not be cited as evidence that field-based input works. It is a
preserved specification of a killed concept, with a pre-registered acceptance test that
returned void because the pad was empty. The ninth retraction is documented here; the null
test lives in `scripts/field_null_test.py`.
