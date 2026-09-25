# Lexicon-Constrained Decoding

`scripts/lexicon_decoder.py` implements the corrected language-layer seam for issue #22.
It sits above the sensor candidate records and searches the supplied lexicon instead of
choosing each character greedily.

## Input contract

`positions` is one list per character position. Each position contains one to three
sensor candidates with a one-character `text`, a positive finite `confidence`, and optional
provenance fields:

```json
{
  "positions": [
    [
      {"text": "c", "confidence": 0.62, "source": "sensor", "slot": 0},
      {"text": "e", "confidence": 0.23, "source": "sensor", "slot": 0},
      {"text": "t", "confidence": 0.15, "source": "sensor", "slot": 0}
    ],
    [{"text": "a", "confidence": 0.71, "source": "sensor", "slot": 0}],
    [{"text": "t", "confidence": 0.66, "source": "sensor", "slot": 0}]
  ],
  "lexicon": ["cat", "cot", "cut"]
}
```

The decoder requires the same number of positions as the word length. It rejects malformed
records, duplicate candidates, duplicate lexicon entries, non-positive confidence, and
non-finite prior values. It does not accept a target word or ground-truth field.

## Search and output

For every lexicon word of matching length, the decoder sums the log sensor confidence of the
candidate selected at each position. Words missing a candidate at any position are
unreachable and are not returned. The optional `language_scores` object is a word prior;
it is consulted only when reachable words have the same sensor score. Thus the prior cannot
silently override stronger sensor evidence.

The report contains:

- `status`: `resolved`, `ambiguous`, or `unreachable`;
- `selected`: the best reversible proposal, or `null` when no word is reachable;
- `ranked`: all reachable words with sensor/prior scores, candidate indices, and copied
  candidate provenance;
- `reachable_word_count` and whether language evidence was available.

`selected` is not a text commit. Plover emission, correction policy, and any user-facing
commit remain separate reversible stages.

## Scope and evidence

This module implements the search contract; it does not establish a new accuracy, WPM,
correction-rate, or PTH-660 result. The reachable-set measurements in `LM_RECOVERY.md` remain
ceilings until this decoder is connected to a correctly conditioned candidate stream and
re-measured. The existing greedy recovery numbers remain withdrawn.
