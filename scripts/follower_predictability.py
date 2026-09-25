#!/usr/bin/env python3
"""How predictable is a follower's motion from its leader's motion?

The magnitude coupling (beta) in ``real_session_evidence.vector_coupling`` answers
"how far does the follower move?". A dominance filter needs the stronger property:
"how much of the follower's motion can be predicted away?". That is the squared
Pearson correlation r^2 between the two step vectors; the residual factor after a
least-squares fit ``step_b ~ s * step_a`` is ``sqrt(1 - r^2)``.

Result on the three PTH-660 sessions (see VECTOR_DESIGN_CRITIQUE.md 4a):
    long-finger neighbours   r = +0.79 .. +0.96   -> 62..92 % of energy explained
    thumb<->thumb, idx<->idx r = -0.32 .. -0.50   -> 10..25 % of energy explained
The mirrored pairs stay reproducible in sign across sessions but resist suppression.

Usage:
    python3 scripts/follower_predictability.py session.jsonl [session.jsonl ...]
    python3 scripts/follower_predictability.py --json session.jsonl ...
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kinematics  # noqa: E402

MIN_FRAMES = 40


def step_rows(payload: list[dict]) -> list[dict[str, tuple[float, float]]]:
    prev: dict[str, tuple[float, float, float]] = {}
    rows = []
    for fr in payload:
        t = float(fr["t"])
        row: dict[str, tuple[float, float]] = {}
        for tid, (x, y, _m) in fr["c"].items():
            x, y = float(x), float(y)
            old = prev.get(tid)
            if old is not None and t - old[2] > 0:
                row[tid] = (x - old[0], y - old[1])
            prev[tid] = (x, y, t)
        rows.append(row)
    return rows


def pair_predictability(rows, a: str, b: str) -> dict:
    ax: list[float] = []
    bx: list[float] = []
    for row in rows[1:]:
        if a not in row or b not in row:
            continue
        if math.hypot(*row[a]) <= 0.01:
            continue
        if max(row, key=lambda k: math.hypot(*row[k])) != a:
            continue                      # a is not the leader in this frame
        ax += [row[a][0], row[a][1]]
        bx += [row[b][0], row[b][1]]
    n = len(ax)
    if n < 2 * MIN_FRAMES:
        return {"mover": a, "follower": b, "n_frames": n // 2}
    ma, mb = sum(ax) / n, sum(bx) / n
    cov = sum((ax[i] - ma) * (bx[i] - mb) for i in range(n))
    va = sum((v - ma) ** 2 for v in ax)
    vb = sum((v - mb) ** 2 for v in bx)
    r = cov / math.sqrt(va * vb) if va > 0 and vb > 0 else 0.0
    return {"mover": a, "follower": b, "n_frames": n // 2,
            "r": r, "r2": r * r,
            "slope": (cov / va) if va > 0 else 0.0,
            "residual_factor": math.sqrt(max(0.0, 1.0 - r * r))}


def analyse(path: Path) -> list[dict]:
    payload = kinematics._strip_uninit_leads(kinematics._load(path))
    rows = step_rows(payload)
    acc: dict[tuple[str, str], dict] = {}
    for i in range(1, len(rows)):
        row = rows[i]
        if not row:
            continue
        a = max(row, key=lambda k: math.hypot(*row[k]))
        for b in row:
            if b != a:
                acc.setdefault((a, b), None)
    out = []
    for (a, b) in acc:
        st = pair_predictability(rows, a, b)
        if st.get("r") is not None:
            out.append(st)
    out.sort(key=lambda s: -s["r2"])
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("sessions", nargs="+", type=Path)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--top", type=int, default=12)
    args = ap.parse_args()
    allrows = []
    for p in args.sessions:
        allrows += analyse(p)
    allrows.sort(key=lambda s: -s["r2"])
    if args.json:
        print(json.dumps(allrows, indent=2))
        return 0
    print("|session|mover|follower|n_frames|r|r2_explained|residual_factor|slope|")
    print("|---|---|---:|---:|---:|---:|---:|---:|")
    for p in args.sessions:
        for s in analyse(p)[:args.top]:
            print(f"|{p.name}|{s['mover']}|{s['follower']}|{s['n_frames']}|"
                  f"{s['r']:+.3f}|{s['r2']*100:.1f}%|{s['residual_factor']:.2f}|"
                  f"{s['slope']:+.3f}|")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
