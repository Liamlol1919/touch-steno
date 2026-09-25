#!/usr/bin/env python3
"""Rank decoder candidates without emitting text.

This is the language-layer seam required by issue #20: sensor confidence and an optional
language score are combined for a ranked list. The module deliberately does not translate,
commit, or invent a language model.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

SCHEMA = "touchsteno.candidate_ranking"
VERSION = 1


def rank_candidates(candidates: list[dict], language_scores: dict[str, float] | None = None,
                    confidence_weight: float = 1.0,
                    language_weight: float = 1.0) -> dict:
    """Return provenance-preserving candidates sorted by score, highest first."""
    if confidence_weight < 0 or language_weight < 0:
        raise ValueError("ranking weights must be non-negative")
    ranked = []
    language_available = language_scores is not None
    for candidate in candidates:
        text = candidate.get("text")
        confidence = float(candidate.get("confidence", 0.0))
        if not isinstance(text, str) or not text:
            raise ValueError("candidate text must be a non-empty string")
        if not math.isfinite(confidence):
            raise ValueError("candidate confidence must be finite")
        language_score = (float(language_scores.get(text, 0.0))
                          if language_available else None)
        if language_score is not None and not math.isfinite(language_score):
            raise ValueError("language score must be finite")
        total = confidence_weight * confidence
        if language_score is not None:
            total += language_weight * language_score
        ranked.append({"candidate": dict(candidate), "rank_score": total,
                       "confidence": confidence, "language_score": language_score,
                       "language_available": language_available})
    ranked.sort(key=lambda row: (-row["rank_score"], row["candidate"]["text"]))
    return {"schema": SCHEMA, "version": VERSION,
            "language_available": language_available,
            "selected": ranked[0]["candidate"] if ranked else None,
            "ranked": ranked}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("candidates", type=Path, help="JSON list of candidate objects")
    ap.add_argument("--language-scores", type=Path,
                    help="JSON object mapping candidate text to log-score")
    ap.add_argument("--confidence-weight", type=float, default=1.0)
    ap.add_argument("--language-weight", type=float, default=1.0)
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()
    candidates = json.loads(args.candidates.read_text(encoding="utf-8"))
    if not isinstance(candidates, list):
        raise SystemExit("candidates JSON must be a list")
    scores = (json.loads(args.language_scores.read_text(encoding="utf-8"))
              if args.language_scores else None)
    report = rank_candidates(candidates, scores, args.confidence_weight, args.language_weight)
    text = json.dumps(report, indent=2, sort_keys=True)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
