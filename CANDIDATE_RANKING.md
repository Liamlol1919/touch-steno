# Candidate Ranking

`scripts/candidate_ranker.py` is the first language-layer seam for the ambiguous
compass decoder. It ranks candidates; it does not translate text or commit a stroke.

```bash
python3 scripts/candidate_ranker.py candidates.json \
  --language-scores language-scores.json \
  --out ranking.json
```

Candidate input is a JSON list:

```json
[
  {"text": "cat", "confidence": 0.82, "source": "decoder"},
  {"text": "cut", "confidence": 0.74, "source": "decoder"}
]
```

The optional language-score object maps candidate text to a log-score. The ranker combines
confidence and language score with explicit non-negative weights, preserves the original
candidate provenance, and marks whether language evidence was available.

No language model is bundled. The output is deliberately a ranked list so a future Plover/LM
adapter, correction policy and real-radius benchmark can consume the same contract. This is
a correctness seam, not a measured accuracy improvement.

## Word-level search

For the corrected top-3 sensor channel, `scripts/lexicon_decoder.py` consumes the same
provenance-preserving candidate records and performs a lexicon-constrained search. It
returns reversible proposals with explicit `resolved`, `ambiguous`, and `unreachable`
states. The optional word prior only breaks exact sensor-score ties; it does not turn the
greedy character ranker into a text commit. See [LEXICON_DECODING.md](LEXICON_DECODING.md).
