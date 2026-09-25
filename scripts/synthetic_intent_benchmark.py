#!/usr/bin/env python3
"""Synthetic zero-force intent benchmark.

This is a *model sanity check*, not a PTH-660 performance claim. It compares a
velocity-only detector with a detector that also rejects large-area contacts and
requires a stable rest baseline. It uses deterministic synthetic traces so the
threshold behavior can be tested before the real tablet is connected.
"""
from __future__ import annotations
from dataclasses import dataclass, field
import argparse
import json
import math
import random
from typing import Iterable


@dataclass
class Sample:
    t: float
    finger: str
    x: float
    y: float
    area: float
    label: str


@dataclass
class Config:
    hz: float = 120.0
    rest_radius: float = 1.2
    min_peak_speed: float = 20.0
    min_displacement: float = 1.5
    min_duration: float = 0.035
    max_duration: float = 0.60
    min_area: float = 2.0
    palm_area: float = 8.0
    coupled_speed_ratio: float = 0.45


@dataclass
class Track:
    finger: str
    t0: float
    x: float
    y: float
    area: float
    label: str
    last_t: float = 0.0
    last_x: float = 0.0
    last_y: float = 0.0
    peak_speed: float = 0.0
    max_displacement: float = 0.0
    triggered: bool = False


@dataclass
class Detection:
    finger: str
    t: float
    kind: str
    score: float
    label: str


def trace(kind: str, cfg: Config, rng: random.Random) -> Iterable[Sample]:
    """Generate one labeled trace; coordinates are arbitrary mm-like units."""
    dt = 1.0 / cfg.hz
    duration = 0.8
    if kind == "tap":
        # Baseline, sharp short displacement, return and settle.
        start = 0.20
        for n in range(round(duration / dt)):
            t = n * dt
            if t < start:
                x, y, area = 0.0, 0.0, 3.0
            elif t < start + 0.07:
                x, y, area = 4.0, 0.0, 3.8
            elif t < start + 0.16:
                x, y, area = 0.0, 0.0, 3.0
            else:
                x, y, area = 0.0, 0.0, 3.0
            yield Sample(t, "index", x, y, area, kind)
    elif kind == "drift":
        start = 0.20
        for n in range(round(duration / dt)):
            t = n * dt
            if t < start:
                x, y, area = 0.0, 0.0, 3.0
            elif t < start + 0.20:
                u = (t - start) / 0.20
                x, y, area = 4.0 * u, 1.5 * u, 3.2
            else:
                x, y, area = 4.0, 1.5, 3.0
            yield Sample(t, "index", x, y, area, kind)
    elif kind == "rest":
        for n in range(round(duration / dt)):
            t = n * dt
            yield Sample(t, "index", rng.gauss(0, 0.10), rng.gauss(0, 0.10), 3.0, kind)
    elif kind == "palm":
        for n in range(round(duration / dt)):
            t = n * dt
            x, y = rng.gauss(0, 0.25), rng.gauss(0, 0.25)
            yield Sample(t, "palm", x, y, 12.0 + rng.gauss(0, 0.3), kind)
    elif kind == "ring_coupled":
        # Master finger moves; ring follows with a smaller but sharp component.
        for n in range(round(duration / dt)):
            t = n * dt
            if t < 0.2:
                x = y = 0.0
            else:
                x = 4.0 * min(1.0, (t - 0.2) / 0.2)
                y = 0.0
            yield Sample(t, "index", x, y, 3.0, kind)
            yield Sample(t, "ring", x * cfg.coupled_speed_ratio, 0.0, 3.0, kind)
    else:
        raise ValueError(kind)


def detect(samples: Iterable[Sample], cfg: Config) -> list[Detection]:
    tracks: dict[str, Track] = {}
    detections: list[Detection] = []
    for s in samples:
        if s.finger not in tracks:
            tracks[s.finger] = Track(s.finger, s.t, s.x, s.y, s.area, s.label)
            tr = tracks[s.finger]
            tr.last_t, tr.last_x, tr.last_y = s.t, s.x, s.y
            continue
        tr = tracks[s.finger]
        dt = max(1e-9, s.t - tr.last_t)
        dx, dy = s.x - tr.last_x, s.y - tr.last_y
        speed = math.hypot(dx, dy) / dt
        displacement = math.hypot(s.x - tr.x, s.y - tr.y)
        tr.peak_speed = max(tr.peak_speed, speed)
        tr.max_displacement = max(tr.max_displacement, displacement)
        if (not tr.triggered and tr.peak_speed >= cfg.min_peak_speed
                and tr.max_displacement >= max(cfg.rest_radius, cfg.min_displacement)
                and s.area >= cfg.min_area
                and s.area < cfg.palm_area
                and cfg.min_duration <= s.t - tr.t0 <= cfg.max_duration):
            tr.triggered = True
            detections.append(Detection(s.finger, s.t, "intent", tr.peak_speed, s.label))
        tr.last_t, tr.last_x, tr.last_y = s.t, s.x, s.y
    return detections


def score(expected: list[str], detections: list[Detection], kinds: tuple[str, ...]) -> dict:
    allowed = sum(expected.count(k) for k in kinds)
    false = [d for d in detections if d.label not in kinds]
    hit = allowed - len(false)
    return {
        "expected": allowed,
        "detected": len(detections),
        "false_positive": len(false),
        "recall": hit / allowed if allowed else None,
        "false_events": len([d for d in false]),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    cfg = Config()
    rng = random.Random(args.seed)
    expected = ["tap", "drift", "rest", "palm", "ring_coupled"]
    results = {}
    for kind in expected:
        detections = detect(trace(kind, cfg, rng), cfg)
        if kind in {"rest", "palm"}:
            false_detections = list(detections)
        elif kind == "ring_coupled":
            false_detections = [d for d in detections if d.finger == "ring"]
        else:
            false_detections = []
        results[kind] = {
            "detections": [
                {"finger": d.finger, "t": round(d.t, 4), "score": round(d.score, 3)}
                for d in detections
            ],
            "false_positive": len(false_detections) > 0,
        }
    report = {
        "warning": "Synthetic sanity check; not a PTH-660 measurement.",
        "config": cfg.__dict__,
        "results": results,
    }
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        for kind, result in results.items():
            print(f"{kind:14s} detections={len(result['detections'])} false={result['false_positive']} {result['detections']}")


if __name__ == "__main__":
    main()
