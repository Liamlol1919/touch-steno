#!/usr/bin/env python3
"""Integration seam between the ranking layer and the language layer.

There are two modules and they are deliberately different, which the filenames alone do
not make obvious:

  candidate_ranker.py   (agent1)  a PURE SEAM. Takes candidates carrying text and sensor
                                  confidence, optionally combines caller-supplied language
                                  scores, and returns a ranked list with provenance. It
                                  deliberately does not translate, commit, or contain a
                                  language model.

  candidate_ranking.py  (agent2)  the LANGUAGE LAYER. An interpolated character bigram, the
                                  posterior/margin decision rule, and commit-vs-retract
                                  including word-level retraction.

Neither replaces the other, and this script is the proof that they compose: a
`candidate_ranking.SymbolModel` produces the `language_scores` that
`candidate_ranker.rank_candidates` consumes. The separation is what lets a real LM be
dropped in later without touching the decoder, and what lets the seam be tested with no
model at all.

Usage:
    python3 scripts/rank_seam_demo.py            # end-to-end on a synthetic stroke
    python3 scripts/rank_seam_demo.py --json
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import candidate_ranker as seam  # noqa: E402
import candidate_ranking as lang  # noqa: E402


def language_scores_for(candidates: list[dict], model: lang.SymbolModel,
                         prev: str | None = None) -> dict[str, float]:
    """Turn the language model's view into the dict shape the seam expects.

    The seam takes *log* scores so it can add them to its own log-domain combination
    without a second log; passing raw probabilities here would silently change the ranking.
    """
    out: dict[str, float] = {}
    for c in candidates:
        sym = c.get("text") or c.get("symbol")
        if sym:
            out[sym] = model.logp(prev, sym)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    model = lang.SymbolModel.from_counts(
        {"a": 40, "e": 50, "i": 25, "o": 35, "n": 20},
        {("a", "l"): 8, ("l", "o"): 9, ("o", "v"): 6, ("v", "e"): 12, ("e", "n"): 14,
         ("n", "d"): 7, ("d", "o"): 6})
    prev = "a"
    candidates = [
        {"text": "l", "confidence": 0.34},
        {"text": "i", "confidence": 0.30},
        {"text": "e", "confidence": 0.22},
    ]
    scores = language_scores_for(candidates, model, prev=prev)
    ranked_seam = seam.rank_candidates(candidates, language_scores=scores)
    ranked_model = model.score([(c["text"], c["confidence"]) for c in candidates], prev)

    result = {
        "seam_order": [r["candidate"]["text"] for r in ranked_seam["ranked"]],
        "seam_top": ranked_seam["selected"],
        "model_order": [s for s, _lp in ranked_model],
        "language_scores": {k: round(v, 4) for k, v in scores.items()},
    }
    if args.json:
        print(json.dumps(result, indent=2))
        return 0
    print("candidates (sensor confidence only):",
          {c["text"]: c["confidence"] for c in candidates})
    print("language log-scores            :", result["language_scores"])
    print("seam ranking (sensor + language):", result["seam_order"])
    print("model ranking (own combination):", result["model_order"])
    same = result["seam_order"] == result["model_order"]
    print(f"the two agree: {same}")
    if not same:
        print("  difference is expected: the seam is a linear combination with equal")
        print("  weights, the model is posterior-based. Both are documented; the seam")
        print("  is the integration contract, the model is one possible scorer.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
