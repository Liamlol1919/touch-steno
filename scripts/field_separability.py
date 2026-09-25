#!/usr/bin/env python3
"""Does the ten-contact field carry usable symbol information, or is it nuisance redundancy?

The gate measurements killed every single-thumb concept: U = 0.9491 on s12.jsonl and
0.9980 on tempo.jsonl means there is no identifiable thumb. The adversary's point is that
U rules out identity channels but does NOT automatically rule out identity-FREE field
statistics. This script tests exactly that, on the real cued captures, with no new session
and no hand required.

The test: build permutation-invariant field descriptors for every cued trial, then measure
held-out class separability against chance.

  - K-class top-1 accuracy, leave-one-repetition-out.
  - The upper 95% confidence bound on that accuracy.
  - If the bound is at or below 1/K, the field descriptor carries no symbol and the design
    space is dead. For K=8 that is 12.5%.

Permutation invariance matters: contacts have no stable identity here, so a descriptor that
depends on contact order is measuring the tracker, not the hand.

Usage:
    python3 scripts/field_separability.py \
        --session ../../session-stand/messung/s12.jsonl \
        --manifest ../../session-stand/messung/s12.manifest.jsonl
    python3 scripts/field_separability.py --session tempo.jsonl --manifest tempo.manifest.jsonl
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
from itertools import combinations
from pathlib import Path


def load(session: Path, manifest: Path | None):
    frames = []
    for line in session.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        d = json.loads(line)
        t = d.get("t")
        c = d.get("c") or {}
        pts = []
        for v in c.values():
            v = list(v) + [-1.0] * (3 - len(v))
            pts.append((float(v[0]), float(v[1])))
        frames.append((t, pts))
    cues = []
    if manifest and manifest.is_file():
        for line in manifest.read_text().splitlines():
            if line.strip():
                cues.append(json.loads(line))
    return frames, cues


def descriptor(pts):
    """Permutation-invariant descriptor of one contact field.

    Built only from the sorted coordinate set, never from contact order:
      - n, the contact count
      - centroid and spread, translation- and rotation-free summaries
      - the sorted multiset of radii from the centroid
      - pairwise distances, sorted
      - the occupancy bounding box aspect
    Returns None when there are too few contacts to say anything.
    """
    n = len(pts)
    if n < 2:
        return None
    xs = sorted(p[0] for p in pts)
    ys = sorted(p[1] for p in pts)
    cx = statistics.fmean(p[0] for p in pts)
    cy = statistics.fmean(p[1] for p in pts)
    radii = sorted(math.hypot(p[0] - cx, p[1] - cy) for p in pts)
    spread = radii[-1]
    if spread <= 0:
        return None
    norm_r = [r / spread for r in radii]
    # rotation-free: pairwise distances, sorted
    ds = sorted(math.hypot(pts[i][0] - pts[j][0], pts[i][1] - pts[j][1])
                for i, j in combinations(range(n), 2))
    mx = statistics.fmean(ds) or 1.0
    norm_d = [d / mx for d in ds]
    box_w = xs[-1] - xs[0]
    box_h = ys[-1] - ys[0]
    aspect = (box_w / box_h) if box_h > 0 else 0.0
    return ([math.log1p(n)] + norm_r + norm_d + [aspect])


def q_coordination(pts, prev_pts):
    """q from the sprint: how rigidly did the whole field move?

    1 - sum ||dp_i - G(dp_i)||^2 / sum ||dp_i||^2, with G the best similarity
    transform (scale + rotation) that maps the previous displacement set onto the
    current one. High q = the field moved as one body.
    """
    if prev_pts is None or len(pts) < 2 or len(prev_pts) != len(pts):
        return None
    dp = [(c[0] - p[0], c[1] - p[1]) for c, p in zip(sorted(pts), sorted(prev_pts))]
    # map current onto previous by scale*rotation (least squares in 2-D)
    num = sum(a[0] * b[0] + a[1] * b[1] for a, b in zip(dp, dp))
    den = sum(a[0] * a[0] + a[1] * a[1] for a in dp)
    if den <= 0:
        return None
    scale = 1.0
    resid = 0.0
    # optimal rotation via the complex-product trick
    zr = sum(a[0] * b[0] + a[1] * b[1] for a, b in zip(dp, dp))
    zi = sum(a[1] * b[0] - a[0] * b[1] for a, b in zip(dp, dp))
    if abs(zr) + abs(zi) < 1e-9:
        return None
    resid = max(0.0, den - math.hypot(zr, zi))
    return 1.0 - resid / den


def wilson_upper(k, n, z=1.645):
    """Upper 95% bound on a binomial proportion (one-sided Wilson)."""
    if n == 0:
        return 1.0
    p = k / n
    d = 1 + z * z / n
    centre = p + z * z / (2 * n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return min(1.0, (centre + half) / d)


def nearest_classifier(train, test):
    """1-NN with z-scored features; returns predicted class index."""
    if not train:
        return None
    dim = len(train[0][1])
    mu = [statistics.fmean(v[1][j] for v in train) for j in range(dim)]
    sd = [statistics.pstdev([v[1][j] for v in train]) or 1.0 for j in range(dim)]
    best, bd = None, float("inf")
    for ci, vec in test:
        d = sum(((vec[j] - mu[j]) / sd[j]) ** 2 for j in range(dim))
        if d < bd:
            bd, best = d, ci
    return best


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--session", type=Path, required=True)
    ap.add_argument("--manifest", type=Path)
    ap.add_argument("--json", type=Path)
    args = ap.parse_args()

    frames, cues = load(args.session, args.manifest)
    if not frames or not cues:
        print("need both a session and a manifest with cued labels")
        return 1

    trials = []
    for cue in cues:
        if cue.get("practice"):
            continue
        a = cue.get("t_start")
        b = cue.get("t_end")
        if a is None or b is None:
            continue
        win = [(t, p) for t, p in frames if a <= t <= b]
        if len(win) < 3:
            continue
        # The LAST frame of a cue window is the lift-off, where the field is empty.
        # Sample the fullest frame instead: the ten-contact field at its peak.
        peak = max(win, key=lambda tp: (len(tp[1]), tp[0]))[1]
        d = descriptor(peak)
        if d is None:
            continue
        trials.append((cue.get("label") or cue.get("sector") or "?", d))

    classes = sorted({t[0] for t in trials})
    K = len(classes)
    if K < 2:
        print(f"only {K} class(es); cannot test separability")
        return 1
    chance = 1.0 / K

    # leave-one-out 1-NN
    correct = 0
    for i, (ci, vi) in enumerate(trials):
        train = [(c, v) for j, (c, v) in enumerate(trials) if j != i]
        if nearest_classifier(train, [(ci, vi)]) == ci:
            correct += 1
    acc = correct / len(trials)
    upper = wilson_upper(correct, len(trials))

    byc = {}
    for c, v in trials:
        byc.setdefault(c, []).append(v)
    means = {}
    for c, vs in byc.items():
        means[c] = [statistics.fmean(v[j] for v in vs) for j in range(len(vs[0]))]
    ncm = 0
    for c, v in trials:
        best = min(means, key=lambda cc: sum((a - b) ** 2
                                             for a, b in zip(means[cc], v)))
        ncm += (best == c)
    ncm_acc = ncm / len(trials)
    ncm_upper = wilson_upper(ncm, len(trials))

    verdict = ("KILL - field descriptor is at or below chance; ten contacts are nuisance "
               "redundancy, not information" if max(upper, ncm_upper) <= chance * 1.15
               else "not separated enough to be useful yet; a stronger descriptor or a "
                    "controlled reshaping experiment is required")

    res = {"session": str(args.session), "trials": len(trials), "classes": K,
           "chance": round(chance, 4),
           "one_nn_top1": round(acc, 4), "one_nn_upper95": round(upper, 4),
           "nearest_class_mean_top1": round(ncm_acc, 4),
           "nearest_class_mean_upper95": round(ncm_upper, 4),
           "verdict": verdict}
    print("=" * 68)
    print(f"session            {args.session.name}")
    print(f"trials / classes   {len(trials)} / {K}")
    print(f"chance             {chance:.4f}  ({chance:.1%})")
    print(f"1-NN top-1         {acc:.4f}   upper95 {upper:.4f}")
    print(f"class-mean top-1   {ncm_acc:.4f}   upper95 {ncm_upper:.4f}")
    print(f"VERDICT            {verdict}")
    print("=" * 68)
    if args.json:
        args.json.write_text(json.dumps(res, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
