#!/usr/bin/env python3
"""Labelled synthetic benchmark calibrated to the measured PTH-660 statistics.

The project has thresholds, a coupling model and a decoder, but no accuracy measurement,
and no public baseline exists for any of it (W9: hit-rate/undo-rate NOT FOUND). This script
generates a session with *known ground truth* whose noise and motion statistics are taken
from the real recordings, so the full pipeline can be scored offline without a tablet.

Calibration (from MEASURED_BIOMECHANICS.md, three real sessions):
  frame rate          91 Hz (dt = 11.0 ms)
  rest step p99       0.56 mm      rest speed p99  57 mm/s
  rest drift          ~0.5 mm/s sustained
  mover step          1.0-2.5 mm per frame (measured p99 1.92, max 2.76)
  finger coupling     parallel, slope 0.65
  thumb coupling      mirrored, slope -0.33

Tasks generated: N-sector compass gestures (8 sectors, axis-aligned), a tempo ramp, and
chord/single alternation. Ground truth is written as a manifest normalized through
`session_manifest.py`, so the same analysis path applies to synthetic and guided records;
their tempo provenance differs.

Usage:
    python3 scripts/make_benchmark.py --out /tmp/bench.jsonl
    python3 scripts/evaluate_session.py /tmp/bench.jsonl
"""
from __future__ import annotations

import argparse
import json
import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kinematics  # noqa: E402

DT = 0.011                      # 91 Hz
REST_STEP_P99 = 0.56            # mm
REST_SPEED_P99 = 57.4           # mm/s
REST_DRIFT_MM_S = 0.5
MOVER_PEAK_MM_S = 220.0
COUPLING_FINGER = 0.65
COUPLING_THUMB = -0.33
SECTORS = ("E", "NE", "N", "NW", "W", "SW", "S", "SE")
SECTOR_VEC = {name: (math.cos(math.radians(i * 45)),
                      -math.sin(math.radians(i * 45)))
              for i, name in enumerate(SECTORS)}


def track(pair, major=2.0):
    """rest_track/stroke_track return (xs, ys); wrap them in the dict shape we emit."""
    xs, ys = pair
    return {"x": list(xs), "y": list(ys), "major": major}


def rest_track(n, rng, drift=0.0):
    """A resting finger: quantisation noise + optional slow drift."""
    xs, ys = [], []
    x = y = 0.0
    vx = vy = 0.0
    for _ in range(n):
        vx += rng.gauss(0, 0.25)
        vy += rng.gauss(0, 0.25)
        vx *= 0.92
        vy *= 0.92
        x += vx * 0.01 + drift * DT * rng.uniform(0.5, 1.5)
        y += vy * 0.01 + drift * DT * rng.uniform(0.5, 1.5)
        xs.append(x)
        ys.append(y)
    return xs, ys


def stroke_track(n, start_x, start_y, target_x, target_y, rng, coupling=None,
                 coupling_map=None):
    """A moving finger: eased travel to the target with per-frame jitter."""
    xs, ys = [], []
    x, y = start_x, start_y
    for i in range(n):
        t = (i + 1) / n
        ease = min(1.0, t * 1.4)              # quick onset, settle
        tx = start_x + (target_x - start_x) * ease
        ty = start_y + (target_y - start_y) * ease
        jx = rng.gauss(0, REST_STEP_P99 * 0.25)
        jy = rng.gauss(0, REST_STEP_P99 * 0.25)
        x, y = tx + jx, ty + jy
        xs.append(x)
        ys.append(y)
    return xs, ys


def build(seed: int, sectors_reps: int, tempo_rates, chord_reps: int,
          rest_blocks: int) -> tuple[list[dict], list[dict]]:
    rng = random.Random(seed)
    frames: list[dict] = []
    manifest: list[dict] = []
    contacts: dict[str, dict] = {}     # tid -> {"x": [...], "y": [...], "major": m}
    t = 0.0
    order = list(range(len(contacts)))  # placeholder to keep structure obvious

    # Contacts must stay continuous across blocks: a real finger never teleports back to
    # the origin between cues. The first version did exactly that, and the jump produced a
    # false idle trigger that had nothing to do with the detector.
    carry: dict[str, tuple[float, float]] = {}

    def shift_to_carry(tracks):
        for tid, tr in tracks.items():
            if tid in carry:
                dx = carry[tid][0] - tr["x"][0]
                dy = carry[tid][1] - tr["y"][0]
                tr["x"] = [v + dx for v in tr["x"]]
                tr["y"] = [v + dy for v in tr["y"]]
            carry[tid] = (tr["x"][-1], tr["y"][-1])
        return tracks

    def emit_block(tracks, label, meta, seconds=0.0):
        tracks = shift_to_carry(tracks)
        nonlocal t
        n = max(2, int(seconds / DT)) if seconds else max(
            2, max(len(v["x"]) for v in tracks.values()))
        span = max(len(v["x"]) for v in tracks.values())
        t0 = t
        for i in range(span):
            c = {}
            for tid, tr in tracks.items():
                idx = i % len(tr["x"])
                c[tid] = [tr["x"][idx], tr["y"][idx], tr.get("major", 2.0)]
            frames.append({"t": round(t, 6), "c": c})
            t += DT
        manifest.append({"t_start": round(t0, 6), "t_end": round(t, 6),
                         "label": label, **meta})

    # 1. rest blocks (ground truth: no event)
    for b in range(rest_blocks):
        tracks = {"1": track(rest_track(220, rng, REST_DRIFT_MM_S)),
                  "2": track(rest_track(220, rng, REST_DRIFT_MM_S))}
        emit_block(tracks, f"rest_{b}", {"rest": True})

    # 2. sector compass: one thumb stroke per cue
    for rep in range(sectors_reps):
        for name in SECTORS:
            vx, vy = SECTOR_VEC[name]
            r = 20.0
            # Gesture length must exceed the detector's persistence window
            # (8 frames = 88 ms) with margin, otherwise the event window starts after the
            # gesture has finished and the measured direction points at the next block.
            n = 25                                  # ~275 ms, >= 3x the persistence window
            lead = stroke_track(n, 0.0, 0.0, vx * r, vy * r, rng)
            gain = COUPLING_THUMB if rep % 2 else COUPLING_FINGER
            foll = stroke_track(n, 0.0, 0.0, vx * r * gain, vy * r * gain, rng)
            tracks = {"1": track(lead), "2": track(foll)}
            emit_block(tracks, f"sector_{name}",
                       {"sector": name, "axis": name in ("E", "N", "W", "S")})

    # 3. tempo ramp: deliberate repeated strokes at N events/s
    for rate in tempo_rates:
        period = 1.0 / rate
        n_events = max(3, int(period * 8))       # leave room for >=250ms strokes
        span = int(n_events * period / DT)
        tracks = {"1": track(rest_track(span + 4, rng, REST_DRIFT_MM_S)),
                  "2": track(rest_track(span + 4, rng, REST_DRIFT_MM_S))}
        marks = []
        for k in range(n_events):
            t0 = k * period
            vx, vy = SECTOR_VEC[SECTORS[k % 8]]
            n = max(20, int(0.25 / DT))          # each cued stroke must clear the window
            for j in range(n):
                idx = int(t0 / DT) + j
                if idx < len(tracks["1"]["x"]):
                    f = (j + 1) / n
                    tracks["1"]["x"][idx] = vx * 20.0 * f + rng.gauss(0, 0.05)
                    tracks["1"]["y"][idx] = vy * 20.0 * f + rng.gauss(0, 0.05)
                    tracks["2"]["x"][idx] = vx * 20.0 * f * COUPLING_FINGER
                    tracks["2"]["y"][idx] = vy * 20.0 * f * COUPLING_FINGER
            marks.append(round(t0, 4))
        emit_block(tracks, f"tempo_{rate}hz", {"rate_hz": rate, "events": marks})

    # 4. chord vs single alternation
    for c in range(chord_reps):
        n = 25                                  # same reason as the sector cues
        lead = stroke_track(n, 0.0, 0.0, 12.0, 0.0, rng)
        peer = stroke_track(n, 0.0, 0.0, 0.0, 12.0, rng)
        emit_block({"1": track(lead), "2": track(peer)},
                   "chord_both", {"chord": True})
        lead2 = stroke_track(n, 0.0, 0.0, 12.0, 0.0, rng)
        peer2 = stroke_track(n, 0.0, 0.0, 1.0, 1.0, rng)     # weak, not aligned
        emit_block({"1": track(lead2), "2": track(peer2)},
                   "single_only", {"chord": False})
    del order
    return frames, manifest


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=Path("/tmp/bench.jsonl"))
    ap.add_argument("--seed", type=int, default=1234)
    ap.add_argument("--sector-reps", type=int, default=4)
    ap.add_argument("--tempo", type=float, nargs="*", default=[1, 2, 3, 4, 5])
    ap.add_argument("--chord-reps", type=int, default=6)
    ap.add_argument("--rest-blocks", type=int, default=4)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    frames, manifest = build(args.seed, args.sector_reps, args.tempo,
                              args.chord_reps, args.rest_blocks)
    with kinematics.Recorder(args.out, force=args.force) as rec:
        for fr in frames:
            rec.frame(fr["t"], {int(k): tuple(v) for k, v in fr["c"].items()})
    mpath = args.out.with_suffix(".manifest.jsonl")
    with mpath.open("w", encoding="utf-8") as fh:
        for rec in manifest:
            fh.write(json.dumps(rec) + "\n")
    print(f"{len(frames)} frames, {len(manifest)} cues -> {args.out}")
    print(f"manifest -> {mpath}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
