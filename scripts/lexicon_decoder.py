#!/usr/bin/env python3
"""Decode a word from bounded per-character candidates and a lexicon.

The decoder is a search layer above the sensor candidate seam. It never chooses a
character greedily, never commits text, and never receives an intended/target word. A
reachable word is scored from the supplied sensor confidence at every position; an optional
word prior is used only to break an exact sensor-score tie.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

SCHEMA = "touchsteno.lexicon_decode"
VERSION = 1
MAX_CANDIDATES = 3


def _finite_positive(value: Any, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a positive finite number")
    value = float(value)
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be a positive finite number")
    return value


def _validate_positions(positions: list[list[dict]]) -> None:
    if not positions:
        raise ValueError("positions must not be empty")
    for position, candidates in enumerate(positions):
        if not isinstance(candidates, list) or not 1 <= len(candidates) <= MAX_CANDIDATES:
            raise ValueError(
                f"position {position} must contain one to {MAX_CANDIDATES} candidates"
            )
        seen: set[str] = set()
        for candidate in candidates:
            if not isinstance(candidate, dict):
                raise ValueError(f"position {position} candidates must be objects")
            text = candidate.get("text")
            if not isinstance(text, str) or len(text) != 1:
                raise ValueError(f"position {position} candidate text must be one character")
            if text in seen:
                raise ValueError(f"position {position} contains duplicate candidate text")
            seen.add(text)
            _finite_positive(candidate.get("confidence"),
                             f"position {position} candidate confidence")


def _validate_language_scores(language_scores: dict[str, float] | None) -> None:
    if language_scores is None:
        return
    if not isinstance(language_scores, dict):
        raise ValueError("language_scores must be an object or null")
    for word, score in language_scores.items():
        if not isinstance(word, str) or not word:
            raise ValueError("language score keys must be non-empty words")
        if isinstance(score, bool) or not isinstance(score, (int, float)):
            raise ValueError("language scores must be finite numbers")
        if not math.isfinite(float(score)):
            raise ValueError("language scores must be finite numbers")


def decode_word(positions: list[list[dict]], lexicon: list[str],
                language_scores: dict[str, float] | None = None) -> dict:
    """Return reachable lexicon words ranked by sensor score and tie-break prior.

    ``positions[i]`` is a top-1..top-3 sensor candidate list. Each candidate must have a
    one-character ``text`` and a positive finite ``confidence``. ``language_scores`` is
    optional and is consulted only when two reachable words have the same sensor score.
    The returned ``selected`` item is a reversible proposal, not a text commit.
    """
    if not isinstance(positions, list):
        raise ValueError("positions must be a list")
    if not isinstance(lexicon, list) or not lexicon:
        raise ValueError("lexicon must be a non-empty list")
    _validate_positions(positions)
    _validate_language_scores(language_scores)
    words = set()
    for word in lexicon:
        if not isinstance(word, str) or not word:
            raise ValueError("lexicon words must be non-empty strings")
        words.add(word)
    if len(words) != len(lexicon):
        raise ValueError("lexicon words must be unique")

    by_length: dict[int, list[str]] = {}
    for word in sorted(words):
        by_length.setdefault(len(word), []).append(word)

    ranked: list[dict] = []
    for word in by_length.get(len(positions), []):
        path: list[int] = []
        chosen: list[dict] = []
        sensor_score = 0.0
        for candidates in positions:
            matches = [
                (index, candidate)
                for index, candidate in enumerate(candidates)
                if candidate["text"] == word[len(path)]
            ]
            if not matches:
                break
            index, candidate = min(
                matches,
                key=lambda item: (-float(item[1]["confidence"]), item[1]["text"]),
            )
            path.append(index)
            chosen.append(dict(candidate))
            sensor_score += math.log(float(candidate["confidence"]))
        else:
            language_score = (float(language_scores.get(word, 0.0))
                              if language_scores is not None else None)
            ranked.append({
                "text": word,
                "sensor_score": sensor_score,
                "language_score": language_score,
                "candidate_indices": path,
                "provenance": chosen,
            })

    language_available = language_scores is not None
    if language_available:
        ranked.sort(key=lambda row: (-row["sensor_score"],
                                     -row["language_score"], row["text"]))
    else:
        ranked.sort(key=lambda row: (-row["sensor_score"], row["text"]))

    if not ranked:
        status = "unreachable"
    elif len(ranked) == 1:
        status = "resolved"
    else:
        first, second = ranked[0], ranked[1]
        sensor_tie = math.isclose(first["sensor_score"], second["sensor_score"],
                                 rel_tol=0.0, abs_tol=1e-12)
        prior_tie = (not language_available or
                     math.isclose(first["language_score"], second["language_score"],
                                  rel_tol=0.0, abs_tol=1e-12))
        status = "ambiguous" if sensor_tie and prior_tie else "resolved"

    return {
        "schema": SCHEMA,
        "version": VERSION,
        "status": status,
        "language_available": language_available,
        "reachable_word_count": len(ranked),
        "selected": ranked[0] if ranked else None,
        "ranked": ranked,
    }


def _load_wordlist(path: Path) -> list[str]:
    words = [line.strip() for line in path.read_text(encoding="utf-8").splitlines()]
    return [word for word in words if word]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="JSON object with positions and optional lexicon")
    parser.add_argument("--wordlist", type=Path, help="newline-delimited lexicon")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("positions"), list):
        raise SystemExit("input must be an object containing a positions list")
    lexicon = payload.get("lexicon")
    if args.wordlist is not None:
        if lexicon is not None:
            raise SystemExit("provide lexicon in input or --wordlist, not both")
        lexicon = _load_wordlist(args.wordlist)
    if lexicon is None:
        raise SystemExit("input requires lexicon or --wordlist")
    report = decode_word(payload["positions"], lexicon, payload.get("language_scores"))
    text = json.dumps(report, indent=2, sort_keys=True, allow_nan=False)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
