#!/usr/bin/env python3
"""Re-measure lexicon decoding from correctly conditioned observed-sector candidates.

The target word is used only to choose the source distribution and to score the result after
decoding. It is never passed to ``decode_word``. Candidate records are built from
P(true sector | observed sector), using the column of the confusion matrix.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import layout_assignment as la  # noqa: E402
import lexicon_decoder  # noqa: E402
import lm_recovery as lr  # noqa: E402

SCHEMA = "touchsteno.lexicon_recovery"
VERSION = 1


def _word_scores(model, words: list[str]) -> dict[str, float]:
    scores = {}
    for word in words:
        previous = None
        score = 0.0
        for char in word:
            score += model.logp(previous, char)
            previous = char
        scores[word] = score
    return scores


def evaluate_channel(confusion: dict, trials: int, radius_mm: float, seed: int,
                     words: list[str], model, *,
                     confusion_trials_per_sector: int | None = None) -> dict:
    """Evaluate observed-sector candidate generation and lexicon search."""
    letter_of = dict(lr.SECTOR_LETTER)
    sector_of = {letter: sector for sector, letter in lr.SECTOR_LETTER.items()}
    pool = [word for word in words if all(char in sector_of for char in word)]
    if not pool:
        return {"schema": SCHEMA, "version": VERSION, "error": "no word uses mapped letters",
                "letters": sorted(set(letter_of.values()))}
    language_scores = _word_scores(model, pool)
    rng = random.Random(seed)
    top1_word_hits = observed_word_hits = selected_hits = reachable = 0
    selected_reachable_hits = ambiguous = unreachable = 0
    correction_opportunities = 0
    top3_symbols = top1_symbols = total_symbols = 0
    reachable_word_total = 0
    for _ in range(trials):
        target = rng.choice(pool)
        positions = []
        observed_word = []
        top1_word = []
        for char in target:
            observed = lr.sample_observed(sector_of[char], confusion, rng)
            candidates = lr.top_candidates(observed, confusion, letter_of)
            positions.append(candidates)
            observed_word.append(letter_of[observed])
            top1_word.append(candidates[0]["text"] if candidates else None)
            total_symbols += 1
            top1_symbols += bool(candidates and candidates[0]["text"] == char)
            top3_symbols += char in {candidate["text"] for candidate in candidates}
        report = lexicon_decoder.decode_word(positions, pool, language_scores)
        reachable_word_total += report["reachable_word_count"]
        is_reachable = target in {row["text"] for row in report["ranked"]}
        reachable += is_reachable
        ambiguous += report["status"] == "ambiguous"
        unreachable += report["status"] == "unreachable"
        selected = report["selected"]
        selected_text = selected["text"] if selected else None
        selected_hits += selected_text == target
        selected_reachable_hits += is_reachable and selected_text == target
        if report["status"] != "resolved" or selected_text != target:
            correction_opportunities += 1
        top1_word_hits += top1_word == list(target)
        observed_word_hits += observed_word == list(target)
    denominator = max(1, trials)
    return {
        "schema": SCHEMA,
        "version": VERSION,
        "radius_mm": radius_mm,
        "seed": seed,
        "trials": trials,
        "wordlist_size": len(words),
        "lexicon_size": len(pool),
        "conditioning": "observed-sector-column",
        "true_sector_prior": "uniform",
        "confusion_trials_per_sector": confusion_trials_per_sector,
        "synthetic_but_calibrated": True,
        "language_prior": "character-bigram-from-supplied-lexicon",
        "top1_symbol_accuracy": round(top1_symbols / max(1, total_symbols), 4),
        "top3_symbol_availability": round(top3_symbols / max(1, total_symbols), 4),
        "top1_word_accuracy": round(top1_word_hits / denominator, 4),
        "top1_word_reachability_rate": round(top1_word_hits / denominator, 4),
        "top3_word_reachability_rate": round(reachable / denominator, 4),
        "observed_word_accuracy": round(observed_word_hits / denominator, 4),
        "word_reachability_rate": round(reachable / denominator, 4),
        "selected_word_accuracy": round(selected_hits / denominator, 4),
        "selected_word_accuracy_conditional_reachable": round(
            selected_reachable_hits / max(1, reachable), 4),
        "ambiguous_rate": round(ambiguous / denominator, 4),
        "ambiguous_rate_reachable": round(ambiguous / max(1, reachable), 4),
        "unreachable_rate": round(unreachable / denominator, 4),
        "mean_reachable_words": round(reachable_word_total / denominator, 4),
        "correction_opportunities_per_word": round(
            correction_opportunities / denominator, 4),
    }


def run(trials: int, radius_mm: float, seed: int, words: list[str], model) -> dict:
    sigma = la.calibrate_sigma(trials=300, seed=3)
    confusion_trials = max(200, trials // 20)
    confusion = la.build_confusion(confusion_trials, seed, sigma,
                                   radius_mm=radius_mm)
    return evaluate_channel(
        confusion, trials, radius_mm, seed, words, model,
        confusion_trials_per_sector=confusion_trials)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trials", type=int, default=2000)
    parser.add_argument("--radii", type=float, nargs="+", default=[12.0, 15.0, 20.0])
    parser.add_argument("--seed", type=int, default=5)
    parser.add_argument("--wordlist", default=lr.DEFAULT_WORDLIST)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    words = lr.load_words(args.wordlist)
    if not words:
        print(f"no word list at {args.wordlist}; pass --wordlist")
        return 1
    model = lr.char_bigram_model(words)
    report = [run(args.trials, radius, args.seed, words, model)
              for radius in args.radii]
    if args.json:
        print(json.dumps(report, indent=2, allow_nan=False))
    else:
        for row in report:
            if "error" in row:
                print(row["error"])
                continue
            print(json.dumps(row, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
