#!/usr/bin/env python3
"""Score the pipeline against labelled ground truth: confusion matrix, accuracy, WPM.

This is the measurement the project has been missing. Every threshold so far was justified
by distributions (rest vs mover, coupling r^2) but never by an accuracy number. With a
labelled session - synthetic (make_benchmark.py) or a cued real one
(guided_calibration.py, which writes the same manifest format) - the full pipeline can be
scored:

  * sector confusion matrix (was the decoded direction the cued one?)
  * axis-vs-diagonal accuracy, because the literature says axes are the reliable half
  * chord detection: true chord vs single, from the peak-alignment criterion
  * false events inside rest blocks (the idle false-trigger rate)
  * event rate and the WPM it implies, per tempo block

Usage:
    python3 scripts/evaluate_session.py session.jsonl
    python3 scripts/evaluate_session.py --json session.jsonl
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import intent_filter  # noqa: E402
import kinematics  # noqa: E402
import stroke_decoder  # noqa: E402

AXES = {"E", "N", "W", "S"}


def load_manifest(path: Path) -> list[dict]:
    mpath = path.with_suffix(".manifest.jsonl")
    if not mpath.exists():
        raise SystemExit(f"manifest fehlt: {mpath}")
    out = []
    for line in mpath.read_text(encoding="utf-8").splitlines():
        if line.strip():
            out.append(json.loads(line))
    return out


def label_at(manifest, t):
    """Half-open [t_start, t_end) lookup.

    Closed intervals made an event starting exactly on a block boundary inherit the
    *previous* block's label, which produced a fake 0% sector accuracy and a systematic
    one-sector rotation in the confusion matrix. Boundaries belong to the later block.
    """
    for rec in manifest:
        if rec.get("t_start") is not None and rec["t_start"] <= t < rec["t_end"]:
            return rec
    return None


def full_coverage_map():
    """Map every descriptor the decoder can emit, so scoring sees all events.

    This is an *evaluation* map: the key is a placeholder, the point is that no event is
    silently dropped before it can be scored. The production sector->syllable assignment
    stays a separate, swappable table (see stroke_decoder.DEFAULT_MAP).
    """
    out = {}
    for s in stroke_decoder.SECTORS:
        for band, _limit in stroke_decoder.BANDS:
            for k in range(0, 4):
                tag = f"chord{k}" if k else "single"
                out[f"{s}|{band}|{tag}"] = f"{s[0]}{k}"
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("session", type=Path)
    ap.add_argument("--map", type=Path,
                    help="explicit descriptor->key map; default is full coverage")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    manifest = load_manifest(args.session)
    mapping = (json.loads(args.map.read_text(encoding="utf-8")) if args.map
               else full_coverage_map())
    decoded = stroke_decoder.analyse(args.session, mapping)
    events = intent_filter.analyse(args.session, intent_filter.MIN_SPEED_MM_S,
                                   intent_filter.MIN_RUN_FRAMES)

    # attach the ground-truth label to every decoded stroke and every event
    strokes, evs = [], []
    for s in decoded["strokes"]:
        lab = label_at(manifest, s["t_start"])
        s["label"] = (lab or {}).get("label")
        strokes.append(s)
    for e in events["events"]:
        lab = label_at(manifest, e["t_start"])
        e["label"] = (lab or {}).get("label")
        evs.append(e)

    # Validation: a block shorter than the detector window cannot be scored honestly,
    # because the event window necessarily starts after the gesture has ended. Those
    # events are excluded and counted, not silently attributed to the wrong label.
    min_block_s = intent_filter.MIN_RUN_FRAMES * 0.011
    too_short = [r for r in manifest
                 if (r.get("t_end", 0) - r.get("t_start", 0)) < min_block_s]

    axis_hits = axis_total = diag_hits = diag_total = 0
    conf = Counter()
    for s in strokes:
        lab = s["label"] or ""
        if not lab.startswith("sector_"):
            continue
        blk = label_at(manifest, s["t_start"]) or {}
        if (blk.get("t_end", 0) - blk.get("t_start", 0)) < min_block_s:
            continue
        truth = lab.split("_", 1)[1]
        pred = s["sector"]
        conf[(truth, pred)] += 1
        hit = truth == pred
        if truth in AXES:
            axis_total += 1
            axis_hits += hit
        else:
            diag_total += 1
            diag_hits += hit

    # --- chord detection ---
    chord_tp = chord_fp = chord_fn = 0
    for e in evs:
        lab = e["label"] or ""
        is_true = lab in ("chord_both", "single_only")
        got_chord = bool(e["unexplained_contacts"])
        if lab == "chord_both":
            chord_tp += got_chord
            chord_fn += (not got_chord)
        elif lab == "single_only":
            chord_fp += got_chord
    # --- idle false triggers ---
    rest_blocks = [(r["t_start"], r["t_end"]) for r in manifest
                   if (r.get("label") or "").startswith("rest_")]
    rest_events = sum(1 for e in evs
                      if any(s <= e["t_start"] <= e2 for s, e2 in rest_blocks))
    rest_seconds = sum(b - a for a, b in rest_blocks)

    # --- tempo: achieved vs cued event rate ---
    tempo = []
    for r in manifest:
        if not (r.get("label") or "").startswith("tempo_"):
            continue
        want = r.get("rate_hz", 0.0)
        n = sum(1 for e in evs if r["t_start"] <= e["t_start"] <= r["t_end"])
        dur = r["t_end"] - r["t_start"]
        got = n / dur if dur else 0.0
        tempo.append({"label": r["label"], "cued_hz": want,
                      "detected_hz": round(got, 2), "events": n,
                      "ratio": round(got / want, 2) if want else None})

    sectors_total = axis_total + diag_total
    result = {
        "session": args.session.name,
        "strokes_decoded": len(strokes),
        "events": len(evs),
        "sector_samples": sectors_total,
        "sector_accuracy": round((axis_hits + diag_hits) / sectors_total, 3)
        if sectors_total else None,
        "axis_accuracy": round(axis_hits / axis_total, 3) if axis_total else None,
        "diagonal_accuracy": round(diag_hits / diag_total, 3) if diag_total else None,
        "chord": {"tp": chord_tp, "fp": chord_fp, "fn": chord_fn},
        "idle_false_events": rest_events,
        "idle_seconds": round(rest_seconds, 1),
        "idle_events_per_min": round(rest_events / rest_seconds * 60, 2)
        if rest_seconds else None,
        "tempo": tempo,
        "blocks_shorter_than_window": len(too_short),
        "min_block_s": round(min_block_s, 3),
        "confusion": {f"{a}->{b}": n for (a, b), n in sorted(conf.items())},
    }
    if args.json:
        print(json.dumps(result, indent=2))
        return 0
    print(f"## {result['session']}")
    print(f"  events {result['events']}  strokes decoded {result['strokes_decoded']}")
    print(f"  sector accuracy {result['sector_accuracy']} "
          f"(axis {result['axis_accuracy']}, diagonal {result['diagonal_accuracy']}, "
          f"n={sectors_total})")
    c = result["chord"]
    print(f"  chord detection tp={c['tp']} fp={c['fp']} fn={c['fn']}")
    print(f"  idle false events {result['idle_false_events']} in "
          f"{result['idle_seconds']}s -> {result['idle_events_per_min']}/min")
    if result["blocks_shorter_than_window"]:
        print(f"  excluded {result['blocks_shorter_than_window']} block(s) shorter than "
              f"the {result['min_block_s']*1000:.0f}ms detector window")
    if tempo:
        print("  tempo: cued vs detected events/s")
        for t in tempo:
            print(f"    {t['label']:<12} cued {t['cued_hz']:>4}  got {t['detected_hz']:>5}  "
                  f"ratio {t['ratio']}")
    if result["confusion"]:
        print("  confusion (truth->pred):")
        for k, v in result["confusion"].items():
            print(f"    {k}: {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
