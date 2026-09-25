#!/usr/bin/env python3
"""How much does a language model recover from the measured sector error?

This is the experiment behind the claim that the language layer is the **correctness**
lever, not just the speed lever. At an ergonomic compass radius (12-15 mm) the direction
decoder is 0.58-0.68 accurate, so 32-42 % of labels are wrong before any language
processing. If a language model does not measurably reduce that, the claim is wrong and the
correctness has to come from somewhere else.

Method, all reproducible offline:

  1. Take the *measured* sector confusion matrix (layout_assignment.build_confusion), which
     is calibrated to the 35 % on-fence rate observed on real motion. For each cued sector
     the row IS the candidate distribution, so no noise is invented.
  2. Build a character bigram model from a real word list (/usr/share/dict/linux.words, or a
     Hunspell dictionary, or an explicit --wordlist), because an invented lexicon would
     flatter the result.
  3. Target text is drawn from the SAME lexicon, so the model is not being tested on words
     it has never seen.
  4. Decode twice: geometrically (take the modal candidate) and with the language model
     (candidate_ranking.decode_stream), and report both.

The result is a lower bound on what a real LM achieves, because a bigram over characters is
the weakest useful model, and an upper bound on what it can achieve, because the candidate
set is already the true posterior from the sensor.

Usage:
    python3 scripts/lm_recovery.py
    python3 scripts/lm_recovery.py --trials 20000 --radius 15 --json
"""
from __future__ import annotations

import argparse
import json
import math
import random
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import candidate_ranking as cr  # noqa: E402
import layout_assignment as la  # noqa: E402

DEFAULT_WORDLIST = "/usr/share/dict/linux.words"
HUNSPELL = "/usr/share/hunspell/en_AG.dic"


def load_words(path: str, min_len=3, max_len=9, limit=20000) -> list[str]:
    words = []
    p = Path(path)
    if not p.exists():
        return words
    for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
        w = line.strip()
        if not w or not w.isalpha():
            continue
        w = w.lower()
        if min_len <= len(w) <= max_len:
            words.append(w)
    words = sorted(set(words))
    rng = random.Random(7)
    if len(words) > limit:
        words = rng.sample(words, limit)
    return words


def char_bigram_model(words: list[str], alpha: float = 0.6) -> cr.SymbolModel:
    uni = Counter()
    bi = Counter()
    for w in words:
        padded = "^" + w + "$"
        for c in padded:
            uni[c] += 1
        for a, b in zip(padded, padded[1:]):
            bi[(a, b)] += 1
    return cr.SymbolModel.from_counts(dict(uni), dict(bi), alpha=alpha)


# A fixed, documented sector->letter map. The experiment needs a channel the language model
# actually has statistics for: feeding literal sector names ("E", "NE", ...) into a
# character model over English words gives every candidate the same unigram floor, so the
# geometric term alone decides and the LM appears to score 1.0 at every radius.
SECTOR_LETTER = {"E": "e", "NE": "n", "N": "t", "NW": "a",
                 "W": "o", "SW": "i", "S": "c", "SE": "m"}



def sample_observed(truth_sector: str, confusion: dict, rng: random.Random) -> str:
    """Sample the sensor observation from P(observed | intended sector)."""
    row = confusion[truth_sector]
    total = sum(row.values()) or 1
    threshold = rng.random() * total
    cumulative = 0
    for sector, count in row.items():
        cumulative += count
        if threshold <= cumulative:
            return sector
    return truth_sector


def top_candidates(observed: str, confusion: dict,
                   letter_of: dict[str, str] | None = None) -> list[dict]:
    """Return top-3 P(true sector | observed sector) records."""
    mapping = SECTOR_LETTER if letter_of is None else letter_of
    column = {truth: row.get(observed, 0) for truth, row in confusion.items()}
    total = sum(column.values()) or 1
    candidates = [
        {"text": mapping[truth], "confidence": count / total,
         "source": "observed-sector-column", "observed_sector": observed,
         "true_sector": truth}
        for truth, count in column.items() if count and truth in mapping
    ]
    return sorted(candidates, key=lambda row: (-row["confidence"], row["text"]))[:3]

def sample_from(cands: list[tuple[str, float]], rng: random.Random) -> str:
    r = rng.random()
    acc = 0.0
    for sym, w in cands:
        acc += w
        if r <= acc:
            return sym
    return cands[-1][0]


def run(trials: int, radius: float, seed: int, words: list[str],
        model: cr.SymbolModel) -> dict:
    """Decode real words through the noisy sector channel, with and without the LM.

    The Bayesian flow, in full, because getting it wrong is what made an earlier version
    report a perfect recovery:

      1. a target letter's sector S is known;
      2. the SENSOR delivers an observation: obs ~ P(obs | S), read off the row of S;
      3. the candidate set is what that observation could have been: P(true | obs), which
         needs the COLUMN of obs - not the row, which would tell the model the answer;
      4. the geometric baseline is the observation itself; the LM ranks the candidates.
    """
    sigma = la.calibrate_sigma(trials=300, seed=3)
    conf = la.build_confusion(max(200, trials // 20), seed, sigma, radius_mm=radius)

    letter_of = dict(SECTOR_LETTER)
    sector_of = {v: k for k, v in SECTOR_LETTER.items()}


    pool = [w for w in words if all(c in sector_of for c in w)]
    if not pool:
        return {"error": "no word uses the mapped letters",
                "letters": sorted(set(letter_of.values()))}
    rng = random.Random(seed)

    geo_hits = lm_hits = 0
    committed = retracted = words_total = 0
    prev_letter = None
    for _ in range(trials):
        word = rng.choice(pool)
        words_total += 1
        geo_word, lm_word = [], []
        for ch in word:
            obs = sample_observed(sector_of[ch], conf, rng)
            cands = top_candidates(obs, conf)
            if not cands:
                geo_word.append(ch)
                lm_word.append(ch)
                continue
            geo_word.append(letter_of[obs])       # what the sensor alone says
            scored = model.score([(c["text"], c["confidence"]) for c in cands], prev_letter)
            post = cr.posterior(scored)
            if post[0][1] >= model.commit_posterior and cr.margin(scored) >= model.margin_floor:
                lm_word.append(post[0][0])
                prev_letter = post[0][0]
            else:
                retracted += 1
                lm_word.append(post[0][0])          # a retraction still has a best guess
        geo_hits += geo_word == list(word)
        lm_hits += lm_word == list(word)
        committed += len(word)
    n = max(1, words_total)
    return {
        "radius_mm": radius,
        "words": words_total,
        "lexicon_size": len(words),
        "geometric_word_accuracy": round(geo_hits / n, 3),
        "lm_word_accuracy": round(lm_hits / n, 3),
        "characters_committed": committed,
        "characters_retracted": retracted,
        "retract_rate": round(retracted / max(1, committed), 3),
    }


# A correction is a user action, not a model action. The number that decides whether the
# language layer is actually usable is therefore corrections per second, not word accuracy.
def correction_load(res: dict, events_per_s: float) -> dict:
    rate = res.get("retract_rate", 0.0) or 0.0
    corrections_s = rate * events_per_s
    mean_word_len = 4.5
    # usable words/s if a correction costs `seconds_per_correction` of user time and
    # corrections can overlap with typing
    out = {"corrections_per_s": round(corrections_s, 2)}
    for sec in (0.3, 1.0, 2.0):
        overhead = rate * mean_word_len * sec
        gross = events_per_s / mean_word_len
        out[f"usable_words_per_s_at_{sec}s_per_correction"] = round(
            max(0.0, gross * (1.0 - overhead)) * 60.0, 1)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--trials", type=int, default=20000)
    ap.add_argument("--radius", type=float, default=15.0)
    ap.add_argument("--seed", type=int, default=5)
    ap.add_argument("--wordlist", default=DEFAULT_WORDLIST)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    words = load_words(args.wordlist)
    if not words:
        print(f"no word list at {args.wordlist}; pass --wordlist")
        return 1
    model = char_bigram_model(words)
    res = run(args.trials, args.radius, args.seed, words, model)
    if args.json:
        print(json.dumps(res, indent=2))
        return 0
    if "error" in res:
        print(res["error"])
        return 1
    print(f"radius {res['radius_mm']}mm  lexicon {res['lexicon_size']} words  "
          f"words decoded {res['words']}")
    print(f"  geometric word accuracy (sampled) : {res['geometric_word_accuracy']}")
    print(f"  LM word accuracy                  : {res['lm_word_accuracy']}")
    print(f"  retracted characters              : {res['characters_retracted']} "
          f"({res['retract_rate']})")
    for ev_s in (3.0, 5.0):
        load = correction_load(res, ev_s)
        print(f"  at {ev_s:.0f} events/s: {load['corrections_per_s']} corrections/s -> "
              + "  ".join(f"{v} wpm@{k.split('_at_')[1][:-8]}s"
                          for k, v in load.items() if k.startswith("usable")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
