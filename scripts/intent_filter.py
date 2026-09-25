#!/usr/bin/env python3
"""Intent filter: measured PTH-660 rest/driver separation + per-pair coupling subtraction.

This is the "step 2 trigger" from the design chat, but with every constant taken from
MEASURED_BIOMECHANICS.md instead of from intuition:

  * an event candidate is K consecutive frames with speed >= MIN_SPEED_MM_S
    (measured: rest worst run is 7 frames at 30-40 mm/s, 5 at 60 mm/s -> K = 8 is the
    first setting with zero false activations on 17 resting contacts);
  * inside an event, the contact with the largest accumulated displacement is the mover;
  * every other contact is suppressed as "dragged" if its displacement is explained by a
    per-pair linear fit (measured r^2: finger row 0.62-0.92, cross-hand 0.72-0.74,
    thumb<->thumb only 0.10-0.25 -> those stay *reported* instead of silently dropped).

The filter is deliberately conservative: it never emits a key, it emits ranked event
candidates with their suppressed followers, so a human can audit what it would have done.

Usage:
    python3 scripts/intent_filter.py session.jsonl [session.jsonl ...]
    python3 scripts/intent_filter.py --json session.jsonl
    python3 scripts/intent_filter.py --min-speed 60 --min-run 5 session.jsonl
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kinematics  # noqa: E402

# Measured operating point (MEASURED_BIOMECHANICS.md section 3).
MIN_SPEED_MM_S = 40.0
MIN_RUN_FRAMES = 8
# A follower is called "explained" when the per-pair fit explains at least this share of
# its energy. Finger row 0.62-0.92, cross-hand 0.72-0.74, thumb<->thumb 0.10-0.25.
MIN_R2_TO_SUPPRESS = 0.5


def steps_of(payload: list[dict]) -> list[dict[str, tuple[float, float, float]]]:
    """Per-frame (dx, dy, speed) per contact, only for consecutive frames."""
    prev: dict[str, tuple[float, float, float]] = {}
    rows: list[dict[str, tuple[float, float, float]]] = []
    for fr in payload:
        t = float(fr["t"])
        row: dict[str, tuple[float, float, float]] = {}
        for tid, (x, y, _m) in fr["c"].items():
            x, y = float(x), float(y)
            old = prev.get(tid)
            if old is not None:
                dt = t - old[2]
                if dt > 0:
                    d = math.hypot(x - old[0], y - old[1])
                    row[tid] = (x - old[0], y - old[1], d / dt)
            prev[tid] = (x, y, t)
        rows.append(row)
    return rows


def fit_pairs(rows, exclude_mover_frame: bool = True) -> dict[tuple[str, str], dict]:
    """Per-pair least-squares fit of follower step on mover step."""
    acc: dict[tuple[str, str], list[tuple[float, float]]] = {}
    for row in rows[1:]:
        if not row:
            continue
        a = max(row, key=lambda k: math.hypot(row[k][0], row[k][1]))
        for b, sb in row.items():
            if b == a:
                continue
            if math.hypot(sb[0], sb[1]) <= 0.01:
                continue
            acc.setdefault((a, b), []).append((row[a][0], row[a][1], sb[0], sb[1]))
    out: dict[tuple[str, str], dict] = {}
    for (a, b), pts in acc.items():
        n = len(pts)
        if n < 40:
            continue
        ax = [p[0] for p in pts] + [p[1] for p in pts]
        bx = [p[2] for p in pts] + [p[3] for p in pts]
        m = 2 * n          # both x and y components are in the sample
        ma, mb = sum(ax) / m, sum(bx) / m
        cov = sum((ax[i] - ma) * (bx[i] - mb) for i in range(m))
        va = sum((v - ma) ** 2 for v in ax)
        vb = sum((v - mb) ** 2 for v in bx)
        r = cov / math.sqrt(va * vb) if va > 0 and vb > 0 else 0.0
        out[(a, b)] = {"n_frames": n, "r": r, "r2": r * r,
                        "slope": (cov / va) if va > 0 else 0.0}
    return out


def detect_events(rows, min_speed: float, min_run: int) -> list[tuple[int, int, set[str]]]:
    """Maximal runs of >= min_run consecutive frames where some contact is fast.

    Returns (start_frame, end_frame, contacts_involved).
    """
    events = []
    run: list[set[str]] = []
    for i, row in enumerate(rows):
        fast = {k for k, (_dx, _dy, v) in row.items() if v >= min_speed}
        if fast:
            run.append(fast)
            if len(run) == min_run:
                involved = set().union(*run)
                events.append((i - min_run + 1, i, involved))
        else:
            run = []
    return events


def analyse(path: Path, min_speed: float, min_run: int) -> dict:
    payload = kinematics._strip_uninit_leads(kinematics._load(path))
    rows = steps_of(payload)
    pairs = fit_pairs(rows)
    events = detect_events(rows, min_speed, min_run)
    out_events = []
    for start, end, involved in events:
        acc: dict[str, list[float]] = {}
        mover_frames: dict[str, int] = {}
        acc_vec = [0.0, 0.0]        # mover displacement accumulated inside the window
        for row in rows[start + 1:end + 1]:
            if not row:
                continue
            a = max(row, key=lambda k: math.hypot(row[k][0], row[k][1]))
            mover_frames[a] = mover_frames.get(a, 0) + 1
            for tid, (dx, dy, _v) in row.items():
                p = acc.setdefault(tid, [0.0, 0.0])
                p[0] += dx
                p[1] += dy
                if tid == a:
                    acc_vec[0] += dx
                    acc_vec[1] += dy
        if not acc:
            continue
        ranked = sorted(acc.items(),
                        key=lambda kv: mover_frames.get(kv[0], 0), reverse=True)
        mover = ranked[0][0] if ranked else None
        suppressed, reported = [], []
        for tid, (sx, sy) in ranked:
            if tid == mover:
                continue
            fit = pairs.get((mover, tid)) or pairs.get((tid, mover))
            if fit and fit["r2"] >= MIN_R2_TO_SUPPRESS:
                suppressed.append({"tid": tid,
                                   "displacement_mm": round(math.hypot(sx, sy), 2),
                                   "r2": round(fit["r2"], 3),
                                   "slope": round(fit["slope"], 3)})
            else:
                reported.append({"tid": tid,
                                 "displacement_mm": round(math.hypot(sx, sy), 2),
                                 "r2": round(fit["r2"], 3) if fit else None})
        out_events.append({
            "t_start": round(payload[start]["t"], 3),
            "t_end": round(payload[end]["t"], 3),
            "duration_ms": round((payload[end]["t"] - payload[start]["t"]) * 1000, 1),
            "mover": mover,
            "mover_displacement_mm": round(math.hypot(*acc[mover]), 2) if mover else None,
            # Vector accumulated *inside* the event window. Consumers must use this rather
            # than re-reading positions at t_start/t_end: a lookup by timestamp can cross a
            # block boundary and silently measure the vector between two different gestures.
            "mover_dx_mm": round(acc_vec[0], 3) if mover else None,
            "mover_dy_mm": round(acc_vec[1], 3) if mover else None,
            "suppressed_as_dragged": suppressed,
            "unexplained_contacts": reported,
        })
    return {"session": path.name, "frames": len(payload),
            "min_speed_mm_s": min_speed, "min_run_frames": min_run,
            "pair_fits": len(pairs), "events": out_events}


def main() -> int:
    global MIN_R2_TO_SUPPRESS
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("sessions", nargs="+", type=Path)
    ap.add_argument("--min-speed", type=float, default=MIN_SPEED_MM_S)
    ap.add_argument("--min-run", type=int, default=MIN_RUN_FRAMES)
    ap.add_argument("--min-r2", type=float, default=MIN_R2_TO_SUPPRESS)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    results = [analyse(p, args.min_speed, args.min_run) for p in args.sessions]
    if args.json:
        print(json.dumps(results, indent=2))
        return 0
        n_sup = sum(len(e["suppressed_as_dragged"]) for e in r["events"])
        n_rep = sum(len(e["unexplained_contacts"]) for e in r["events"])
        print(f"\n## {r['session']}  frames={r['frames']}  "
              f"rule: >= {r['min_speed_mm_s']} mm/s for {r['min_run_frames']} frames  "
              f"({r['min_run_frames']/91*1000:.0f} ms)  pair fits: {r['pair_fits']}")
        print(f"events: {len(r['events'])}  suppressed-as-dragged: {n_sup}  "
              f"unexplained (kept): {n_rep}")
        print("|t_start_s|dur_ms|mover|disp_mm|suppressed (r2)|unexplained (r2)|")
        print("|---:|---:|---:|---:|---|---|")
        for e in r["events"][:40]:
            sup = ", ".join(f"{s['tid']}:{s['displacement_mm']}mm(r2={s['r2']})"
                            for s in e["suppressed_as_dragged"]) or "-"
            rep = ", ".join(f"{u['tid']}:{u['displacement_mm']}mm"
                            f"(r2={u['r2'] if u['r2'] is not None else 'n/a'})"
                            for u in e["unexplained_contacts"]) or "-"
            print(f"|{e['t_start']}|{e['duration_ms']}|{e['mover']}|"
                  f"{e['mover_displacement_mm']}|{sup}|{rep}|")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


def detect_reversal_events(rows, min_speed: float, min_run: int,
                           turn_deg: float = 90.0) -> list[dict]:
    """Out-and-back events: close on a direction reversal instead of waiting for silence.

    The measured problem (BENCHMARK_RESULTS.md addendum): on a surface that cannot signal a
    release, consecutive gestures can run back to back, and the persistence window then merges
    them. A reversal is a segmentation landmark that needs no lift signal, and it lets the
    return leg be fast - which matters, because a sub-gate return costs 0.67s for a 20mm arc.

An event starts after `min_run` supra-threshold frames and watches for the first later frame
whose direction turns by more than `turn_deg` from the accumulated direction. The returned
event ends on the preceding out-leg frame, so the return vector never enters the stroke.
    """
    events: list[dict] = []
    run: list[set[str]] = []
    for i, row in enumerate(rows):
        fast = {k for k, (_dx, _dy, v) in row.items() if v >= min_speed}
        if not fast:
            run = []
            continue
        run.append(fast)
        if len(run) < min_run:
            continue
        start = i - min_run + 1
        acc: dict[str, list[float]] = {}
        for r in rows[start:i + 1]:
            for tid, (dx, dy, _v) in r.items():
                p = acc.setdefault(tid, [0.0, 0.0])
                p[0] += dx
                p[1] += dy
        if not acc:
            continue
        mover = max(acc, key=lambda k: math.hypot(*acc[k]))
        mx, my = acc[mover]
        mmag = math.hypot(mx, my)
        # look for a reversal in the frames after the window
        for j in range(i + 1, min(i + 1 + 4 * min_run, len(rows))):
            r = rows[j]
            if mover not in r:
                break
            rx, ry = r[mover][0], r[mover][1]
            if mmag <= 0 or math.hypot(rx, ry) <= 0:
                continue
            cosang = (mx * rx + my * ry) / (mmag * math.hypot(rx, ry))
            if math.degrees(math.acos(max(-1.0, min(1.0, cosang)))) > turn_deg:
                events.append({"start": start, "end": j - 1, "mover": mover,
                               "dx_mm": round(mx, 3), "dy_mm": round(my, 3),
                               "displacement_mm": round(mmag, 2),
                               "turn_deg": round(math.degrees(
                                   math.acos(max(-1.0, min(1.0, cosang)))), 1)})
                run = []
                break
        else:
            if i - start + 1 >= min_run and i + 1 not in [e["end"] for e in events]:
                events.append({"start": start, "end": i, "mover": mover,
                               "dx_mm": round(mx, 3), "dy_mm": round(my, 3),
                               "displacement_mm": round(mmag, 2), "turn_deg": None})
    return events
