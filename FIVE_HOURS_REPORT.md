# Five hours, two agents — what actually happened

**Window:** 2026-09-25, roughly 06:00–10:00 CEST
**Involved:** Agent 1 (main build path), Agent 2 (research / modelling / evaluation), the
user as the measurement subject
**State:** 86 commits, 24 issues, 125+ tests green

---

## 1. The verdict first

**No input system was built.** No steno decoder exists that turns a real stroke into text.
That was the original question. It remains open.

What exists is a **defensible re-framing of the problem plus a measurement instrument**. That
is not a product, and five hours is a lot for it.

---

## 2. The one thing that matters: real hand data

The user supplied roughly an hour of real measurements — the most valuable raw material of
the entire period. It overturned a central assumption of the project.

| Measurement | Value | Consequence |
|---|---|---|
| Sector accuracy, 12 mm, right thumb | **47.6 %** | the model assumed 58–68 % — assumption unconfirmed |
| Resting-finger jitter, 9007 samples | **0.4 mm** median | the sensor works correctly |
| Signal at 12 mm excursion | **~30 : 1** | **the sensor is excluded as an error source** |
| 20 mm arm | 0 events | 31 blocks fell under the 88 ms detector window |
| Natural thumb envelope | 24.6 × 18.2 mm | larger than the 12 mm working assumption |

**The remaining error belongs to the hand, not the device.** Nobody knew this before. The
project models had assumed a direction-error rate and optimised underneath it.

The error structure is **not noise but a pattern**: every failure lands on the exact 180°
opposite (NE↔SW, NW↔SE, S↔N, W↔E). That is solvable, and it is not yet solved.

---

## 3. A correction Agent 2 forced on itself

Agent 2 published the cycle's headline claim:

> "The language layer lifts word accuracy from 6.8 % to 88.8 %."

and withdrew it **the same morning**. The candidate set for each character had been built
from the row of the *intended* sector, which hands the model the answer. Corrected to
P(true | observed), the gain collapses to roughly zero, and with an **oracle prefix** — the
true preceding letters supplied — it stays at roughly zero. So it is neither model quality
nor error propagation: a greedy per-character model simply cannot exploit this channel.

Withdrawn along with it: the retraction policy, the correction load (1.87 → 0.92
actions/word), and **every WPM figure**. All of it was downstream of the same error.

This was worth doing because the retraction was made publicly and recorded in the repository
(`LM_RECOVERY.md`, issue #20) rather than the number being quietly replaced.

**Agent 1 then fixed the conditioning** rather than repeating the mistake:
`lexicon_recovery.py` builds candidates from the *observed* sector column and releases the
target word only for scoring afterwards (`conditioning: observed-sector-column`).

---

## 4. The one load-bearing model result

`lexicon_recovery.py`, 2000 trials per radius, 20k lexicon, correctly conditioned:

| Radius | Top-1 word | true symbol in top-3 | word reachable in lexicon | **decoder selects correctly** | unreachable | corrections/word |
|---|---|---|---|---|---|---|
| 12 mm | 6.8 % | 96.3 % | 80.7 % | **73.6 %** | 14.5 % | 0.264 |
| 15 mm | 15.5 % | 99.1 % | 94.9 % | **89.2 %** | 3.0 % | 0.108 |
| 20 mm | 38.5 % | 99.9 % | 99.5 % | **96.3 %** | ~0 % | 0.038 |

**The information is in the channel:** at 12 mm the true symbol is inside the top-3
candidates 96.3 % of the time. The naive decoder takes top-1 and throws away 80 % of it. A
word-level lexicon search recovers it.

**Stated in every file:** the channel is synthetic, calibrated through
`layout_assignment.py`. These are **not** PTH-660 measurements. And the measured 47.6 % sits
**below** the 12 mm model assumption, so the curve describes a channel whose error rate is
not validated against reality.

---

## 5. What was actually built

| Artefact | Size | Purpose |
|---|---|---|
| `guided_calibration.py` | ~370 lines | cued measurement, radius arm, self-paced mode |
| `session_runner.py` | 223 lines | an entire session in one command |
| `lexicon_decoder.py` | 188 lines | word-level lexicon decoder |
| `lexicon_recovery.py` | 152 lines | correctly conditioned benchmark |
| `layout_assignment.py` | 237 lines | sector layout against a confusion matrix |
| `correction_timing.py` | — | stopwatch protocol, no tablet required |
| `plot_models.py` + `models/*.png` | 3 figures | layout, measured confusion, decoder ceiling |
| Measurement tasks | 6 | noise, palm, sectors, tempo, correction, chord, identity |

Evidence in the repository: 3 rendered figures, 8 markdown documents, 24 issues (20 closed),
125+ green tests.

---

## 6. What does not exist

- **No steno decoder.** Nothing turns real strokes into steno symbols or text.
  `stroke_decoder.py` produces direction vectors, not words.
- **No end-to-end text output.** There is no demo in which a movement becomes text.
- **No usable WPM figure.** Every extrapolation was withdrawn and not replaced.
  Seconds-per-correction does not exist in the literature and was never measured here.
- **No degrees-of-freedom survey.** The quoted 68 % co-movement comes from model assumptions,
  not measurement.
- **No 20 mm data arm.** That run failed at the 88 ms threshold, not because of the user.

---

## 7. Where the time went

The user lost roughly an hour to **mistakes Agent 2 introduced**:

1. **Four command lines with flags that do not exist** in a session plan written elsewhere.
   It would have aborted on the first step.
2. **`--task sectors` had no radius parameter** — the 12-vs-20 mm question, which was treated
   as decisive, was not measurable. Added afterwards.
3. **No `--force`**, so existing files blocked every rerun.
4. **An output buffer in the runner** that swallowed every live instruction.
5. **A 1.5 s countdown per sector** — not enough time to read and execute a cue.
6. **A carriage-return redraw** that produced dozens of duplicate lines on the user's
   terminal.

Items 1–3 surfaced because the commands were **never executed before being recommended** —
only checked against `--help` and inspected statically. That is the actual error: a check
that cannot cover the class of failure that mattered.

---

## 8. Honest scorecard

| Question | Answer |
|---|---|
| Did the measurement improve the project? | **Yes.** Error source localised, pattern identified, an assumption disproved |
| Is the central hypothesis supported? | **Partly.** Synthetic-but-calibrated, not validated against a real hand |
| Is there a usable system? | **No** |
| Was the original question answered? | **No.** "Where is the optimised steno model" — it does not exist |
| Was the time wasted? | **The research share, no. The build and documentation volume, yes.** |

**The ordering was wrong.** Thirty issues, instruments and hypotheses first, and the decoder
never. The question "where is the steno model" belonged on day one, not day five.

---

## 9. What to build next

A steno decoder: a Plover steno table over the sector vectors, runnable against the measured
63 strokes. No further measurement, no tablet. The output will be wrong — 47.6 % does not
make readable text — but it will show whether the principle holds, and today that is unknown.

Only once text exists does it make sense to optimise accuracy, undo and tempo.

---

## Appendix: state of the working directory

The local working tree is **5 commits behind `origin/main`** and carries uncommitted changes
to `scripts/guided_calibration.py` — the same file both agents worked on. Both agents operate
in the same directory; that is the cause of the failed pulls and the duplicated work.

**Before further work:** commit or stash, then `git pull --rebase`, then merge
`scripts/guided_calibration.py` by hand.
