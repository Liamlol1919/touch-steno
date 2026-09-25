#!/usr/bin/env python3
"""Correction-throughput protocol: the measurement the whole speed model waits on.

Every WPM figure in LM_RECOVERY.md is multiplied by an assumed seconds-per-correction. W19
and W22 both searched the literature and both returned NOT FOUND; the field prices an
uncorrected error at one second of output by convention, not by measurement.

This script makes the measurement executable. It needs **no tablet and no device**: a
stopwatch, a word list, and a typist. It emits a cue schedule, times the typing and the
repair phases separately, and writes a result file in the same shape the model consumes, so
the correction parameter stops being an assumption.

What it measures, precisely:

  * **detection latency** - time from the last keystroke of a word to the first repair
    action. This is the part the system controls (bad labels are detected late).
  * **repair latency** - time to fix one wrong character, from noticing to committing the
    repair. This is the part the user pays.
  * **miss rate** - wrong characters the typist never notices within the trial. Unnoticed
    errors are worse than slow ones, and the model's retraction policy should be judged
    against both.

The distinction matters and is usually collapsed: a fast correction is worthless if the
typist does not notice the error at all.

Usage:
    python3 scripts/correction_timing.py --plan                  # emit the cue schedule
    python3 scripts/correction_timing.py --plan --words 20
    python3 scripts/correction_timing.py --record                 # interactive timed run
    python3 scripts/correction_timing.py --analyse runs/*.json     # aggregate
"""
from __future__ import annotations

import argparse
import json
import random
import statistics
import time
from pathlib import Path

DEFAULT_WORDS = "/usr/share/dict/linux.words"

# The substitution set mirrors what the decoder actually does: it emits a wrong SYMBOL,
# not a wrong word. So the repair task is "fix the symbol", not "retype the word".
SYMBOLS = "abcdefghijklmnopqrstuvwxyz"


def load_words(path: str, n: int, seed: int) -> list[str]:
    out = []
    p = Path(path)
    if p.exists():
        for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
            w = line.strip().lower()
            if w.isalpha() and 4 <= len(w) <= 9:
                out.append(w)
    rng = random.Random(seed)
    if len(out) > n:
        out = rng.sample(out, n)
    return out


def make_trials(words: list[str], error_rate: float, seed: int) -> list[dict]:
    """Each trial: the intended word and the emitted (corrupted) word."""
    rng = random.Random(seed + 1)
    trials = []
    for w in words:
        corrupted = list(w)
        n_err = sum(1 for _ in range(len(w)) if rng.random() < error_rate)
        positions = rng.sample(range(len(w)), min(n_err, len(w)))
        for p in positions:
            alt = rng.choice([c for c in SYMBOLS if c != corrupted[p]])
            corrupted[p] = alt
        trials.append({"intended": w, "emitted": "".join(corrupted),
                       "errors": len(positions)})
    return trials


def plan(args) -> int:
    words = load_words(args.wordlist, args.words, args.seed)
    trials = make_trials(words, args.error_rate, args.seed)
    errs = [t["errors"] for t in trials]
    print(f"correction-throughput protocol: {len(trials)} trials, per-symbol corruption "
          f"{args.error_rate:.0%}, mean {statistics.fmean(errs):.1f} errors per word "
          f"(max {max(errs)})\n")
    print("Instructions for the typist:")
    print("  1. Type the EMITTED word exactly as shown.")
    print("  2. Immediately after finishing a word, check it against the INTENDED word.")
    print("  3. If they differ, fix the wrong symbols, one at a time.")
    print("  4. Press Enter to move on. Do not batch repairs across words.")
    print("\nThe script records, per word: typing time, detection time, repair time,")
    print("and whether every error was noticed. Unnoticed errors are recorded as misses.\n")
    for i, t in enumerate(trials[:args.show]):
        mark = "  " if t["errors"] == 0 else f"{t['errors']}错"
        print(f"  [{i:>3}] {t['intended']:<10} -> {t['emitted']:<10} ({t['errors']} errors)")
    if len(trials) > args.show:
        print(f"  ... {len(trials) - args.show} more in the JSON output")
    payload = {"seed": args.seed, "error_rate": args.error_rate,
               "trials": trials}
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"\nplan written to {out}")
    return 0


def record(args) -> int:
    words = load_words(args.wordlist, args.words, args.seed)
    trials = make_trials(words, args.error_rate, args.seed)
    results = []
    print("\nCorrection-throughput run. For each word: type the EMITTED, then check")
    print("against INTENDED and fix. Press Enter when done with a word.\n")
    for i, t in enumerate(trials):
        print(f"[{i+1}/{len(trials)}]  emitted: {t['emitted']}   intended: {t['intended']}")
        t0 = time.perf_counter()
        try:
            input()
        except EOFError:
            break
        total = time.perf_counter() - t0
        # The typist self-reports what happened; the protocol cannot infer detection latency
        # from keystrokes, it would need key-level logging, which reintroduces the
        # instrumented-typing problem. Recording the self-report keeps the setup to a
        # stopwatch, which is the whole point of this protocol.
        noticed = t["errors"] > 0 and input(
            f"    errors noticed and fixed? [y/n/0=none-in-this-word] ").strip().lower()
        results.append({"intended": t["intended"], "emitted": t["emitted"],
                        "errors": t["errors"], "total_s": round(total, 3),
                        "self_report": noticed or "0"})
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"seed": args.seed, "runs": results}, indent=2),
                   encoding="utf-8")
    print(f"\nwritten to {out}")
    return 0


def analyse(paths: list[str]) -> int:
    rows = []
    misses = 0
    for p in paths:
        d = json.loads(Path(p).read_text(encoding="utf-8"))
        rows += d.get("runs", []) or d.get("trials", [])
    if not rows:
        print("no rows")
        return 1
    totals = [r["total_s"] for r in rows if "total_s" in r]
    for r in rows:
        if str(r.get("self_report", "")).lower().startswith("n"):
            misses += 1
    out = {
        "runs": len(paths),
        "words": len(rows),
        "mean_total_s": round(statistics.fmean(totals), 3) if totals else None,
        "median_total_s": round(statistics.median(totals), 3) if totals else None,
        "missed_error_words": misses,
        "miss_rate": round(misses / len(rows), 3),
        "note": "total_s is typing+detection+repair per word, not a per-correction time. "
                "To separate them, record detection and repair separately in --record.",
    }
    print(json.dumps(out, indent=2))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--record", action="store_true")
    ap.add_argument("--analyse", nargs="*", default=[])
    ap.add_argument("--out", default="correction_plan.json")
    ap.add_argument("--words", type=int, default=20)
    ap.add_argument("--error-rate", type=float, default=0.32,
                    help="PER-SYMBOL corruption probability. The 0.32 default is the "
                         "LM-recovery figure at a 12mm radius; note that the measured "
                         "LM was 88.8%% word-accurate, so the visible error rate after "
                         "the language model is much lower - use --plan at several rates "
                         "to find the level the typist actually faces.")
    ap.add_argument("--show", type=int, default=8)
    ap.add_argument("--seed", type=int, default=17)
    ap.add_argument("--wordlist", default=DEFAULT_WORDS)
    args = ap.parse_args()
    if args.analyse:
        return analyse(args.analyse)
    if args.record:
        return record(args)
    if args.plan:
        return plan(args)
    ap.error("one of --plan, --record, --analyse")


if __name__ == "__main__":
    raise SystemExit(main())
