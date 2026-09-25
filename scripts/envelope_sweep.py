#!/usr/bin/env python3
"""Operating envelope: detection accuracy and event rate over gesture length x cue rate.

The useful artifact is a surface between gesture length and cue rate, not a single
"3 Hz" number. Each cell reports the requested rate, the rate actually realized by
the generator, and one-to-one cue/event matching. A detector event that spans two
cues therefore counts as one detection and one merged/missed cue, rather than proving
that every cue was recovered.

Everything is synthetic but calibrated to the measured PTH-660 statistics, so this maps
the algorithmic envelope. Real numbers need the cued session on the device.

Usage:
    python3 scripts/envelope_sweep.py
    python3 scripts/envelope_sweep.py --json
"""
from __future__ import annotations

import argparse
import json
import math
import random
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import intent_filter  # noqa: E402
import kinematics  # noqa: E402
import stroke_decoder  # noqa: E402

DT = 0.011
REST_DRIFT = 0.5
SECTORS = ("E", "NE", "N", "NW", "W", "SW", "S", "SE")
VEC = {name: (math.cos(math.radians(i * 45)), -math.sin(math.radians(i * 45)))
       for i, name in enumerate(SECTORS)}
DETECTOR_WINDOW_S = intent_filter.MIN_RUN_FRAMES * DT


def build(length_s, rate_hz, seed, rest_s=1.5, return_mm_s=30.0):
    """Rest block, then evenly spaced cued sector strokes, contacts continuous."""
    rng = random.Random(seed)
    frames, manifest = [], []
    x = y = 0.0
    t = 0.0
    # Fixed 6 s block per cell so every rate gets a usable sample size. The first version
    # used rate*(4+length), which left n=3 per cell at 4-6 Hz - too small to conclude from.
    block_s = 6.0
    n_gest = max(8, int(rate_hz * block_s))
    period = 1.0 / rate_hz

    def push():
        nonlocal t
        frames.append({"t": round(t, 6),
                       "c": {"1": [round(x, 4), round(y, 4), 2.0]}})
        t += DT

    # rest block
    t0 = t
    n_rest = int(rest_s / DT)
    for _ in range(n_rest):
        x += rng.gauss(0, 0.05) + REST_DRIFT * DT * rng.uniform(0.5, 1.5)
        y += rng.gauss(0, 0.05)
        push()
    manifest.append({"t_start": t0, "t_end": t, "label": "rest_0", "rest": True})

    n_len = max(3, int(length_s / DT))
    for k in range(n_gest):
        t0 = t
        target = VEC[SECTORS[k % 8]]
        # RETURN PHASE, as real sub-gate motion rather than a teleport. Consecutive sector
        # targets are only 15.3mm apart on a 20mm arc, so without a return the repositioning
        # vector is rotated a constant 67.5deg from the intended direction and the sector
        # estimate collapses to 1/8 correct (measured). The return speed is below the 40mm/s
        # gate so it does not itself trigger - which is what makes the return affordable.
        sx, sy = x, y
        for j in range(n_len):
            f = (j + 1) / n_len
            ease = min(1.0, f * 1.4)
            x = sx + (target[0] * 20.0 - sx) * ease + rng.gauss(0, 0.04)
            y = sy + (target[1] * 20.0 - sy) * ease + rng.gauss(0, 0.04)
            push()
        manifest.append({"t_start": t0, "t_end": t,
                         "label": f"sector_{SECTORS[k % 8]}",
                         "sector": SECTORS[k % 8]})
        # sub-gate return to the centre, then drift noise for the remaining gap
        ret_n = int(math.hypot(x - sx, y - sy) / (return_mm_s * DT)) + 1
        for j in range(ret_n):
            f = (j + 1) / ret_n
            x = x + (0.0 - x) * (1 / ret_n) + rng.gauss(0, 0.03)
            y = y + (0.0 - y) * (1 / ret_n) + rng.gauss(0, 0.03)
            push()
        gap = period - length_s - ret_n * DT
        for _ in range(max(0, int(gap / DT))):
            x += rng.gauss(0, 0.05)
            y += rng.gauss(0, 0.05)
            push()
    return frames, manifest


def label_at(manifest, t):
    for rec in manifest:
        if rec.get("t_start") is not None and rec["t_start"] <= t < rec["t_end"]:
            return rec
    return None


def realized_rate_hz(cues: list[dict]) -> float | None:
    """Return the observed rate of cue starts, or None for fewer than two cues."""
    if len(cues) < 2:
        return None
    elapsed = cues[-1]["t_start"] - cues[0]["t_start"]
    return (len(cues) - 1) / elapsed if elapsed > 0 else None


def match_cues_to_events(cues: list[dict], events: list[dict]) -> tuple[list[tuple[dict, dict]], int]:
    """Greedily match each detector event to at most one overlapping cue.

    The event with the largest temporal overlap wins a cue. This is deliberately
    conservative: one long event cannot certify several back-to-back gestures.
    """
    unmatched = set(range(len(cues)))
    matches: list[tuple[dict, dict]] = []
    merged = 0
    for event in sorted(events, key=lambda e: (e["t_start"], e["t_end"])):
        candidates = []
        for i in unmatched:
            cue = cues[i]
            overlap = min(event["t_end"], cue["t_end"]) - max(event["t_start"], cue["t_start"])
            if overlap > 0:
                candidates.append((overlap, -abs(event["t_start"] - cue["t_start"]), i))
        if not candidates:
            continue
        _overlap, _distance, cue_index = max(candidates)
        cue = cues[cue_index]
        matches.append((cue, event))
        unmatched.remove(cue_index)
    merged = sum(
        1 for i in unmatched
        if any(min(e["t_end"], cues[i]["t_end"]) > max(e["t_start"], cues[i]["t_start"])
               for e in events)
    )
    return matches, merged


def measure(frames, manifest, tmp: Path) -> dict:
    raw = tmp / "s.jsonl"
    with kinematics.Recorder(raw, force=True) as rec:
        for fr in frames:
            rec.frame(fr["t"], {int(k): tuple(v) for k, v in fr["c"].items()})
    events = intent_filter.analyse(raw, intent_filter.MIN_SPEED_MM_S,
                                   intent_filter.MIN_RUN_FRAMES)["events"]

    cues = [r for r in manifest if r.get("sector")]
    matches, merged = match_cues_to_events(cues, events)
    correct = sum(
        1 for cue, event in matches
        if stroke_decoder.sector_of(event.get("mover_dx_mm") or 0.0,
                                    event.get("mover_dy_mm") or 0.0) == cue["sector"]
    )
    rest_ev = [e for e in events
               if (label_at(manifest, e["t_start"]) or {}).get("label", "")
               .startswith("rest_")]
    span = manifest[-1]["t_end"] - manifest[0]["t_start"] if manifest else 0
    return {
        "cued_gestures": len(cues),
        "detected": len(matches),
        "missed": len(cues) - len(matches),
        "merged": merged,
        "rate_ratio": round(len(matches) / len(cues), 2) if cues else None,
        "sector_acc": round(correct / len(matches), 3) if matches else None,
        "idle_fp": len(rest_ev),
        "span_s": round(span, 2),
        "realized_rate_hz": round(realized_rate_hz(cues) or 0.0, 2) if cues else None,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--lengths-ms", type=float, nargs="+",
                    default=[100, 150, 200, 250, 350, 500])
    ap.add_argument("--rates", type=float, nargs="+",
                    default=[1, 2, 3, 4, 5, 6])
    ap.add_argument("--seed", type=int, default=11)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    rows = []
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        for L in args.lengths_ms:
            for r in args.rates:
                frames, man = build(L / 1000.0, r, args.seed)
                m = measure(frames, man, tmp)
                m["length_ms"] = L
                m["requested_rate_hz"] = r
                m["over_window"] = L / 1000.0 > DETECTOR_WINDOW_S
                rows.append(m)
    if args.json:
        print(json.dumps({"detector_window_s": round(DETECTOR_WINDOW_S, 3),
                          "rows": rows}, indent=2))
        return 0
    print(f"detector window {DETECTOR_WINDOW_S*1000:.0f} ms; "
          f"rows are length_ms x requested_rate_hz\n")
    print("|len_ms|requested|realized|detected/cued|merged|rate_ratio|sector_acc|idle_fp|")
    print("|---:|---:|---:|---:|---:|---:|---:|---:|")
    for m in rows:
        print(f"|{m['length_ms']}|{m['requested_rate_hz']}|{m['realized_rate_hz']}|"
              f"{m['detected']}/{m['cued_gestures']}|{m['merged']}|"
              f"{m['rate_ratio']}|{m['sector_acc']}|{m['idle_fp']}|")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
