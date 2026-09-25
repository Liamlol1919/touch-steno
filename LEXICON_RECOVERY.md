# Conditioned Lexicon Recovery Benchmark

`scripts/lexicon_recovery.py` is the reproducible follow-up to the retracted greedy LM
experiment. It measures the current top-3 lexicon-search boundary without passing the target
word to `lexicon_decoder.decode_word()`.

## Conditioning

For each target character:

1. The intended sector selects the row `P(observed | intended)`.
2. An observed sector is sampled from that row.
3. Each row is normalized by its detection count, then the observed-sector column is
   normalized under an explicit uniform true-sector prior. This matters because undetected
   events give rows unequal totals.
4. The resulting top-3 records are passed to the decoder; the target word is used only
   afterward to score reachability and selection.

The benchmark never conditions candidate generation on the target row after sampling. Its
`conditioning` field is always `observed-sector-column`; `true_sector_prior` records the
uniform prior used for the column posterior.

## Run

The default wordlist path is `/usr/share/dict/linux.words`; pass an explicit newline-delimited
wordlist on systems where it is absent:

```bash
python3 scripts/lexicon_recovery.py \
  --trials 2000 --radii 12 15 20 \
  --wordlist /path/to/words.txt --json
```

The confusion matrix is synthetic-but-calibrated by `layout_assignment.py`. Results are not
PTH-660 measurements.

## Reported metrics

- `top1_symbol_accuracy`: posterior top-1 character accuracy;
- `top3_symbol_availability`: target character present in the top-3 candidate set;
- `top1_word_accuracy` and `top1_word_reachability_rate`: target equals the top-1 posterior
  sequence;
- `top3_word_reachability_rate` and `word_reachability_rate`: target appears among decoder-ranked
  lexicon words;
- `observed_word_accuracy`: raw observed-sector word accuracy, retained separately;
- `selected_word_accuracy`: decoder proposal equals the target;
- `selected_word_accuracy_conditional_reachable`: selected accuracy over reachable trials;
- `ambiguous_rate` and `ambiguous_rate_reachable`: unresolved ties over all and reachable trials;
- `unreachable_rate`: no lexicon word fits the candidate sets;
- `mean_reachable_words`: average size of the reachable candidate set;
- `correction_opportunities_per_word`: one model-level repair opportunity for an unresolved,
  ambiguous, or incorrectly selected word.

The correction metric is an action count, not seconds and not WPM. Human seconds per
correction remain unmeasured. No usable-WPM extrapolation is produced by this script.
