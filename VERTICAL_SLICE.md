# VERTICAL SLICE — Field-Set Word Entry

**This is the one concept the evidence leaves open.** It is concrete and implementable
offline. It is **not validated**, and its single acceptance test has not been run. Both
statements are load-bearing.

Everything else in this repository was generated, scored and killed. This is the survivor of
last resort — not because it scored well, but because it is the only direction the measured
gate numbers do not close.

---

## 1. Why this and nothing else

| Measured | Value | What it kills |
|---|---|---|
| U (contact ambiguity, lower bound) | 0,9491 / 0,9980 vs a 0,10 gate | every concept that needs to know **which** contact moved |
| Major-axis dynamic range | 0,5 mm | every concept using contact-ellipse geometry |
| Field separability, 8 compass classes | **0,4583 vs 0,1250 chance**, upper 95 % 0,6212 | — this is what survives |

The surviving signal uses **no contact identity, no TID, no ellipse, and no direction
class**. It is the shape the ten-point cloud takes, which is detectable without knowing
which point is which. U rules out identity channels; it does not rule this one out.

---

## 2. The primitive

**One touch-down to lift-off. The whole ten-contact field deforms into one of K shapes.
The shape names a word.**

Not a compass. Not a traced letter. The symbol is a **configuration of the hand**, and the
decoder never asks which finger did what.

---

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

**This deliberately abandons the "1–2 strokes per 5-letter word" premise.** Measured
English needs 4,189 events per 5-letter word at 3 events per syllable, so a syllable-level
code cannot honour that premise at any alphabet size. A word-level code sidesteps it, and
pays for it by requiring the user to remember which shape means which word.

---

## 4. State machine

Five states, no cross-event history beyond the committed buffer.

1. **ARMED** — holds the last stable reference cloud (the unordered point set).
2. **MOVING** — accumulates the current cloud; computes the descriptor each frame; tracks
   the field's best-fit similarity transform to the reference.
3. **SETTLED** — movement energy falls below the segmentation floor for ≥88 ms.
4. **CLASSIFY** — descriptor → nearest class centroid among the K trained prototypes.
5. **EMIT or ABSTAIN** — emit only if (a) the margin over the runner-up clears the
   calibrated threshold, (b) contact count matches a trained prototype, and (c) no
   assignment ambiguity was flagged. **Otherwise: silence, and the buffer does not
   advance.**

The abstain path is not a fallback. It is the design's primary safety property: a wrong word
is worse than no word, and the user must be able to trust that a committed word is
plausible. Threshold is learned per session, never hardcoded.

**Event boundary:** movement energy below threshold for 88 ms, not contact lift. Lift is
unusable — with ten contacts resting, an all-up gap essentially never occurs.

---

## 5. Five-axis self-critique

Scored honestly, before any test.

| Axis | Score | The objection |
|---|---|---|
| Hand anatomy / biomechanics | **5/10** | whole-hand shape control is unmeasured; fatigue over a long session is entirely unmeasured |
| Contact identity / observability | **6/10** | the one axis with positive evidence, but n=24 from one hand in one session, and the labels were thumb-compass cues |
| Timing / throughput / corrections | **3/10** | a whole-hand shape change is far slower than the 176 ms floor allows; realistic rate unknown, possibly 0,3–0,8 /s |
| Learnability / eyes-free | **4/10** | 32 arbitrary hand shapes is a real memory load with no compositional structure, and no tactile confirmation exists |
| Implementation / privacy / validation | **7/10** | fully offline, cheap to compute, low privacy risk; validation rests on one operator |
| **Total** | **25/50** | lowest surviving score in the project, stated plainly |

---

## 6. The number that decides it

**Held-out class-mean separability on field gestures that are NOT a thumb compass.**

Current value on thumb-compass labels: 0,4583 against 0,1250 chance — but those labels are
exactly the confound. **The value on the real task is unmeasured.**

- **FATAL:** class-mean top-1 at or below chance, upper 95 % bound included. That would
  mean the descriptor was reading the thumb all along, and this concept dies with every
  other single-contact idea.
- **VIABLE:** upper 95 % bound comfortably above chance on non-compass field gestures. Then
  a field-based method is real and this is the only surviving direction.

**The 45,8 % is not evidence for this concept. It is the reason to run the test.**

---

## 7. The single acceptance test

```bash
python3 scripts/field_gesture_probe.py
```

Cued whole-hand shapes — spread, fist, cup, ridge, twist, pinch, flat, and **STILL** as an
explicit null class — then the separability script on the result. Under three minutes of
cues. The null class is included so a detector that merely fires on drift cannot pass.

The verdict is fixed before the run so it cannot be reinterpreted afterwards.

---

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
unidentifiable rather than merely unmeasured**. The 45,8 % is a same-session, same-subject
result from compass labels that may not transfer. Timing figures are arithmetic ceilings at
the sensor event rate; whole-hand shapes are far slower and the real rate is unmeasured.

**This concept has never been run. It is a specification, not a result.**
