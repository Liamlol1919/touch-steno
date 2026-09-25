# LM Recovery — what the language layer actually buys, and what it costs

**Author:** Agent 2. **Date:** 2026-09-25 08:05 CEST.
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
| **12 mm** | **0.068** | **0.888** | **31.6 %** | 22.9 | **0.0** |
| **15 mm** | **0.155** | **1.000** | 10.2 % | 34.5 | 21.6 |
| **20 mm** | **0.395** | 1.000 | 0.0 % | 40.0 | 40.0 |
| 30 mm | 0.845 | 1.000 | 0.0 % | 66.7 | 66.7 |

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

## The number nobody has

Every WPM figure in the table is multiplied by an assumed seconds-per-correction. W19 searched
the literature for that number and returned **NOT FOUND**: there is no published measurement
of correction throughput at this event rate, for steno or for LM-assisted input.

So the project's decisive input is currently an assumption, and it sits on the critical path:

- at 0.3 s/correction, 15 mm is viable (34.5 WPM) and 12 mm is marginal (22.9);
- at 1.0 s/correction, 12 mm is dead and 15 mm yields 21.6 WPM;
- at 2.0 s/correction, even 15 mm collapses to 3.3 WPM.

The architecture conclusion depends entirely on where in that range reality falls, and we
cannot currently say. This is now the highest-value measurement in the project, and unlike
everything else it is **cheap**: it does not need the tablet, only a stopwatch and a list of
words — a human correction-throughput measurement in the plain sense.

## What would change the picture

Three things, in order of leverage:

1. **A measured correction rate.** The whole table scales with it. If the user can correct
   in 0.3 s, the language layer makes 12–15 mm viable. If it is 2 s, no language layer
   rescues them.
2. **Cheaper correction.** Batching (retract a word, not a character), speculative commit with
   delayed visual verification, or accepting the wrong letter and fixing later. The current
   model retracts single characters; word-level retraction would cut the correction count by
   roughly the word length.
3. **A better channel.** The only escape from the trade: an input primitive whose accuracy
   does not depend on excursion radius (COMPASS_SURFACE addendum, option 3). Untested.

## Honest limits

- The LM is a character bigram — the weakest useful model. A stronger LM would recover more,
  and would also retract less, so both columns move in our favour.
- The model is trained on the same lexicon the targets come from, which is optimistic. A real
  deployment faces a broader and partly unseen vocabulary.
- Words are decoded independently except for the bigram context; no beam search, no
  lookahead, no error model over the channel.
- The confusion matrix is synthetic-but-calibrated. The cued session replaces it.

Even with all four caveats pointing the same way, the qualitative result is robust: **at an
ergonomic radius the language layer converts a 6–16 %-accurate channel into something usable
only if corrections are cheap, and the cost of corrections is the unmeasured quantity that
decides the product.**
