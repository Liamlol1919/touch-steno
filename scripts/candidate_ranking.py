#!/usr/bin/env python3
"""Candidate ranking: turn ambiguous gestures into text with a language model.

The measurement chain forced this module's existence. At an ergonomic compass radius
(12-15 mm, triangulated in COMPASS_SURFACE.md) the direction decoder is 0.58-0.68 accurate,
i.e. **32-42 % label error by construction**, and that is outside the hand's comfort
envelope to improve. So the language layer is the correctness lever, not the speed lever.

What this does, and does not, do:

  DOES   score a *ranked candidate set* for one gesture and pick the best symbol under a
         character/bigram model, and report whether the pick was unambiguous.
  DOES   auto-retract when the best candidate is still too weak to commit, which is the
         behaviour W17 argues for: on a 0G surface the feedback channel degrades in noise and
         there is no visible keyboard, so the correction path is the primary recovery.
  DOES NOT translate steno outlines. Plover owns that (CODE_REFERENCES: opensteno/plover is
         GPL-2.0 and is the documented integration point). This module ranks *sectors* and
         *symbols*, and the mapping from symbol to outline stays data, not code.

The model is deliberately a plain interpolated bigram with a frequency prior, implemented
here so the whole chain is testable offline with stdlib only. Swapping in a real LM is a
change behind the same interface: ``score(candidates) -> [(symbol, logprob)]``.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass, field


@dataclass
class SymbolModel:
    """Interpolated symbol model with a unigram prior.

    ``log P(s) = log( (1-a) * P_uni(s) + a * P_bi(prev, s) )``

    A tiny unigram prior matters more than it looks: without it the first stroke of a
    session has no history and the model would be uniform, which is precisely where a
    noisy decoder is least able to recover.
    """

    unigram: dict[str, float]
    bigram: dict[tuple[str, str], float] = field(default_factory=dict)
    alpha: float = 0.65          # weight on the bigram when a predecessor exists
    # Decision thresholds. These are POSTERIOR thresholds, not absolute log-probabilities:
    # with a symbol inventory this size a perfectly ordinary symbol sits near log p = -1.6, so
    # an absolute floor would reject almost everything. The first version did exactly that and
    # retracted five of five demo strokes.
    commit_posterior: float = 0.55   # top candidate must hold this much of the candidate mass
    margin_floor: float = 0.8        # nats between best and runner-up

    @classmethod
    def from_counts(cls, uni: dict[str, int], bi: dict[tuple[str, str], int],
                    **kw) -> "SymbolModel":
        tot_u = sum(uni.values()) or 1
        tot_b = sum(bi.values()) or 1
        return cls(unigram={k: v / tot_u for k, v in uni.items()},
                   bigram={k: v / tot_b for k, v in bi.items()}, **kw)

    def logp(self, prev: str | None, sym: str) -> float:
        pu = self.unigram.get(sym, 1e-7)
        if prev is not None:
            ctx = (prev, sym)
            if ctx in self.bigram:
                pb = self.bigram[ctx]
                mix = (1.0 - self.alpha) * pu + self.alpha * pb
                return math.log(max(mix, 1e-9))
        return math.log(max(pu, 1e-9))

    def score(self, candidates: list[tuple[str, float]],
              prev: str | None) -> list[tuple[str, float]]:
        """Rank (symbol, geometric_confidence) candidates by combined score.

        The geometric confidence enters as a log-likelihood offset: a candidate decoded at
        0.2 certainty is treated as being 1.6 nats worse than one at 0.8. That keeps the
        sensor and the language in the same units instead of letting a confident-looking
        geometric guess override a strong language prior.
        """
        out = []
        for sym, conf in candidates:
            geo = math.log(max(min(conf, 0.999), 1e-3))
            out.append((sym, self.logp(prev, sym) + geo))
        out.sort(key=lambda kv: -kv[1])
        return out


def posterior(scored: list[tuple[str, float]]) -> list[tuple[str, float]]:
    """Normalise combined log-probabilities into a posterior over the candidate set.

    Scale-free, which is the point: the decision must not depend on how many symbols the
    lexicon happens to contain.
    """
    if not scored:
        return []
    top = max(lp for _s, lp in scored)
    weights = [(s, math.exp(lp - top)) for s, lp in scored]
    total = sum(w for _s, w in weights) or 1.0
    return [(s, w / total) for s, w in weights]


def margin(scored: list[tuple[str, float]]) -> float:
    """Log-prob gap between the best and the runner-up.

    This is the decision statistic for commit-vs-retract. A small margin means the language
    model could not separate the candidates, so committing would be a coin flip with extra
    steps.
    """
    if len(scored) < 2:
        return float("inf")
    return scored[0][1] - scored[1][1]


def decode_stream(strokes: list[tuple[str, float, list[tuple[str, float]]]],
                  model: SymbolModel, margin_floor: float | None = None):
    """Decode a stream, retracting strokes the model cannot commit.

    ``strokes`` is a list of (timestamp, geometric_confidence, candidates) where candidates
    is a list of (symbol, confidence). Returns the committed text plus a decision log, so
    every retraction is auditable rather than silent.
    """
    mf = model.margin_floor if margin_floor is None else margin_floor
    text: list[str] = []
    log: list[dict] = []
    prev: str | None = None
    for t, geo, cands in strokes:
        scored = model.score(cands, prev)
        if not scored:
            log.append({"t": t, "action": "no_candidate"})
            continue
        best, best_lp = scored[0]
        gap = margin(scored)
        post = posterior(scored)
        p_top = dict(post)[best]
        if p_top < model.commit_posterior or gap < mf:
            log.append({"t": t, "action": "retract", "would_have_been": best,
                        "best_logp": round(best_lp, 3), "posterior": round(p_top, 3),
                        "margin": round(gap, 3),
                        "reason": "posterior too low" if p_top < model.commit_posterior
                                  else "margin too small"})
            if text:
                text.pop()             # undo the previous committed symbol
                prev = text[-1] if text else None
            continue
        text.append(best)
        prev = best
        log.append({"t": t, "action": "commit", "symbol": best,
                    "best_logp": round(best_lp, 3), "posterior": round(p_top, 3),
                    "margin": round(gap, 3)})
    return "".join(text), log


def _demo() -> None:
    # Tiny synthetic lexicon so the module is runnable with no corpus.
    uni = {"a": 40, "b": 12, "c": 30, "d": 6, "e": 50, "i": 25, "o": 35, "n": 20}
    bi = {("a", "b"): 8, ("b", "e"): 6, ("e", "a"): 5, ("a", "c"): 7,
          ("c", "t"): 9, ("t", "e"): 8, ("e", "n"): 12, ("n", "d"): 6,
          ("d", "o"): 4, ("o", "m"): 5, ("i", "n"): 7, ("n", "e"): 9}
    model = SymbolModel.from_counts(uni, bi)
    # stroke 1: 'e' wins on frequency, 'a' is close -> committed on margin alone is fragile
    strokes = [
        (0.00, 0.6, [("e", 0.55), ("a", 0.35)]),
        (0.09, 0.5, [("n", 0.45), ("i", 0.30)]),
        (0.18, 0.4, [("d", 0.35), ("o", 0.30)]),   # weak pair -> retract
        (0.27, 0.8, [("o", 0.75), ("d", 0.20)]),
        (0.36, 0.7, [("m", 0.65)]),
    ]
    text, log = decode_stream(strokes, model)
    print("committed:", repr(text))
    for e in log:
        print("  ", e)


if __name__ == "__main__":
    _demo()
