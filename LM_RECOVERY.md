# LM Recovery — what the language layer actually buys, and what it costs

**Author:** Agent 2. **Date:** 2026-09-25 08:05 CEST, **corrected 08:20 CEST —
the recovery table is RETRACTED, see 'RETRACTION' below.**
`scripts/lm_recovery.py` (experiment) + `scripts/candidate_ranking.py` (the ranker).
This is the experiment behind the claim that the language layer is the **correctness**
lever rather than only the speed lever — and it shows the claim is true, incomplete, and
that the missing piece is a number nobody has.

## Setup, stated before the results

- The channel is the **measured** sector confusion matrix (`layout_assignment.build_confusion`,
  calibrated to the 35 % on-fence rate seen on real motion), sampled per character. No noise
  is invented.
- Eight sectors map to eight letters through a fixed table. This matters: an earlier version
  fed literal sector names into a character model, every candidate got the same unigram
  floor, and the LM "scored" 1.0 at every radius.
- The language model is an interpolated character bigram built from a real word list
  (`/usr/share/dict/linux.words`, 20 k words), not an invented lexicon.
- Target words are drawn from the same list.
- The baseline is the candidate the sensor actually produced — sampled from the row, not the
  row's mode, which is the diagonal by construction and reported 100 % accuracy in the first
  broken version.
- 1200 words per radius.

## Result

| radius | geometric word accuracy | LM word accuracy | retracted characters | usable WPM @0.3 s/corr | @1.0 s/corr |
|---:|---:|---:|---:|---:|---:|
| **12 mm** | ~~0.068~~ | ~~0.888~~ | ~~31.6 %~~ | ~~22.9~~ | ~~0.0~~ |
| **15 mm** | ~~0.155~~ | ~~1.000~~ | ~~10.2 %~~ | ~~34.5~~ | ~~21.6~~ |
| **20 mm** | ~~0.395~~ | ~~1.000~~ | ~~0.0 %~~ | ~~40.0~~ | ~~40.0~~ |
| 30 mm | ~~0.845~~ | ~~1.000~~ | ~~0.0 %~~ | ~~66.7~~ | ~~66.7~~ |

*(struck through: retracted above, conditioning error — read the correction before using
any number in this table)*

(usable WPM assumes 4.5 characters per word and an event rate of 3/s; correction cost is the
user's time per correction.)

## What this settles

**The claim holds, and it is not the whole story.**

1. **The language model does recover accuracy.** At 12 mm the raw channel gets 6.8 % of words
   right; with the bigram it reaches 88.8 %. At 15 mm, 15.5 % → 100 %. The sensor layer is
   nowhere near sufficient on its own, exactly as the radius analysis implied.

2. **But it converts label noise into correction work**, and that work is what kills it. At
   12 mm the model needs 0.95 corrections per second at a 3 events/s input. At one second per
   correction the usable rate is **0 WPM** — the system is not slow, it is unusable.

3. **The system only runs correction-free at r ≥ 20 mm**, which is at the edge of the 70 %
   comfort envelope (COMPASS_SURFACE). Below that, correctness is bought with the user's
   attention, and attention is the resource the steno design was supposed to *save*.

## The number nobody has — and what can replace it

W19 and W22 both searched the literature for seconds-per-correction and both returned
**NOT FOUND**. W22 went further and found that the field actively avoids pricing it:

- typing-test standards compute `Net WPM = Gross WPM − (uncorrected errors / minutes)`
  (https://www.speedtypingonline.com/typing-equations) — i.e. they **deduct one second of
  output per uncorrected error**. That is a *convention*, not a measurement, and it is the
  closest thing the field has to a correction cost.
- KLM/GOMS prices a mental re-plan at M = 1.35 s but does not tie it to correction.
- No source found measures per-correction seconds in steno, in general fast typing, or in
  touch-IME correction.

So the assumption can be **bounded** rather than merely acknowledged:

| basis | seconds/correction | status |
|---|---:|---|
| typing-test convention (1 s per uncorrected error) | **1.0** | shared convention, not measured here |
| sensitivity band used in the table above | 0.3 / 1.0 / 2.0 | our own bracket |
| correction frequencies available | 0.5–0.75 uncorrected errors/min at 39–49 GWPM; 0.161 backspace proportion | measured, from other studies |

Using the field's own convention as the anchor rather than a number we invented, the 15 mm
row lands at **21.6 WPM** and the 12 mm row at **0 WPM**. The design conclusion does not
change — 12 mm still does not survive a 1 s correction — but the estimate now has a source
and a defensible spread instead of an invented parameter.

W22 also flagged several numbers that are frequently substituted for a correction latency
(prediction-check dwell 0.45 s, T9 inspection 0.50 s, reading fixation 0.20–0.25 s, key press
0.26 s, decode 59 ms). **None was measured as a human correction on a surface with no
visible keys**, and combining them would be guessing. They are recorded here only to prevent a
silent substitution later.

The direct measurement remains worth doing and is now precisely specified: a stopwatch, a
word list, and a typist. Type N words at the target rate, repair the retractions, and time
both. Ten minutes yields the distribution the whole table is missing.

The architecture conclusion depends entirely on where in that range reality falls, and we
cannot currently say. This is now the highest-value measurement in the project, and unlike
everything else it is **cheap**: it does not need the tablet, only a stopwatch and a list of
words — a human correction-throughput measurement in the plain sense.

## RETRACTION (2026-09-25 08:20): the recovery numbers in the table above are wrong

The headline "6.8 % -> 88.8 % of words" does not survive a second look, and the reason is a
conditioning error in my own experiment.

**What was wrong.** The candidate set for each character was built from the row of the
*intended* sector. That hands the language model the answer: the true symbol is usually the
modal entry of its own row, so the model was ranking a set that already contained the truth
at the top with a large probability. Fixed to condition on the *observed* sector —
P(true | observed), which needs the confusion matrix transposed — the result collapses:

| radius | geometric word accuracy | LM word accuracy | gain |
|---:|---:|---:|---:|
| 12 mm | 0.065 | 0.069 | +0.004 |
| 15 mm | 0.153 | 0.153 | 0.000 |
| 20 mm | 0.374 | 0.374 | 0.000 |
| 30 mm | 0.838 | 0.838 | 0.000 |

**And it is not the model's fault.** With an oracle prefix (the true previous letters given
to the model) the recovery is unchanged: 0.068 at 12 mm, 0.184 at 15 mm. So neither error
propagation nor model quality explains the failure — the greedy per-character model simply
cannot exploit this channel.

## The corrected finding: the information IS in the channel

Two measurements locate the problem precisely.

**Per character, how often is the true symbol even available?**

| radius | top-1 | top-2 | top-3 | top-5 |
|---:|---:|---:|---:|---:|
| 12 mm | 0.617 | 0.808 | **0.968** | 0.994 |
| 15 mm | 0.720 | 0.868 | **0.992** | 0.999 |
| 20 mm | 0.852 | 0.932 | **0.999** | 1.000 |

**Per word, is the target word reachable in a 20k lexicon given the top-k candidates?**

| radius | geometric | top-2 reachable | **top-3 reachable** | top-4 |
|---:|---:|---:|---:|---:|
| 12 mm | 0.102 | 0.400 | **0.853** | 0.945 |
| 15 mm | 0.190 | 0.502 | **0.960** | 0.985 |
| 20 mm | 0.448 | 0.705 | **0.998** | 1.000 |

So the corrected statement is:

> At a 12 mm radius the top-1 reading is right 62 % of the time per character, but the true
> symbol is inside the top-3 **96.8 %** of the time, and the target word is inside the set of
> lexicon words consistent with the top-3 candidates **85 %** of the time.

**The language layer is still potentially the correctness lever, but it is a different
algorithm than the one implemented here.** It requires:

1. keeping the **top-3** candidates from the sensor, not the top-1;
2. a **word-level constrained search** over a lexicon, not a greedy character model;
3. the lexicon constraint doing the work, with a language prior only to break ties among
   the reachable words.

Everything measured here about the retraction policy, the correction load and the WPM table
is downstream of a wrong experiment, and is therefore withdrawn with it. The word-level
retraction result (1.87 -> 0.92 actions per word) was measured on the same flawed
conditioning and must be re-measured once the decoder is correct.

**What survives unchanged:** the radius analysis and its comfort evidence (three independent
lines), the 91 Hz timing, the 88 ms evidence floor, the coupling structure and its temporal
signatures, and the decision that seconds-per-correction is unmeasured in the literature.

## Implementation status

`scripts/lexicon_decoder.py` now implements the corrected search boundary: it consumes
bounded top-3 sensor candidates, searches a supplied lexicon word-by-word, preserves
candidate provenance, and uses a word prior only for exact sensor-score ties. It returns a
reversible proposal, not committed text. This is an implementation result, not a new
accuracy or WPM measurement; the existing greedy recovery table remains withdrawn.

## What would change the picture

Three things, in order of leverage:

1. **A measured correction rate.** The usable-WPM calculation still needs real
   seconds-per-correction observations.
2. **A conditioned end-to-end re-measurement.** Feed the decoder candidate sets generated
   from observed sectors, then measure reachable-word selection, ambiguity, correction load,
   and usable rate. Do not reuse the withdrawn greedy-character table.
3. **A better channel.** An input primitive whose accuracy does not depend on excursion
   radius remains untested (COMPASS_SURFACE addendum, option 3).

## Honest limits

- The top-3 availability and reachable-word figures are ceilings from a calibrated,
  synthetic-but-measured confusion experiment, not PTH-660 results.
- The lexicon search has not yet been connected to a real cued candidate stream.
- The decoder does not measure correction cost, user acceptance, or Plover output.
- The confusion matrix and candidate priors need replacement by cued hardware data.

The corrected conclusion is limited but useful: at an ergonomic radius, the channel often
retains the target symbol in a small candidate set; whether a word-level decoder can select
the right reachable word, and whether corrections are affordable, remains to be measured.
