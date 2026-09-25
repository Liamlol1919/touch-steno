#!/usr/bin/env python3
"""Create a local, replayable per-user rest calibration sidecar.

This is an offline analysis artifact. It does not change intent_filter.py's production
constants and it never reads a live device. Raw inputs remain local; only aggregate
covariance, sweep rows, source hashes and a declared selection are written.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kinematics  # noqa: E402
import rest_model  # noqa: E402

SCHEMA = "touchsteno.rest_calibration"
VERSION = 1


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def covariance(points: list[tuple[float, float]]) -> dict:
    if len(points) < 2:
        return {"n": len(points), "mean": [None, None], "matrix": None}
    mx = statistics.fmean(x for x, _y in points)
    my = statistics.fmean(y for _x, y in points)
    dx = [x - mx for x, _y in points]
    dy = [y - my for _x, y in points]
    return {
        "n": len(points),
        "mean": [mx, my],
        "matrix": [[statistics.fmean(a * a for a in dx),
                     statistics.fmean(a * b for a, b in zip(dx, dy))],
                    [statistics.fmean(a * b for a, b in zip(dx, dy)),
                     statistics.fmean(b * b for b in dy)]],
    }


def _tagged_separation(rest_sources, mover_sources, window, min_frames):
    rest, mover = {}, {}
    for group, sources, target in (("REST", rest_sources, rest),
                                   ("MOVER", mover_sources, mover)):
        for path in sources:
            payload = kinematics._load(path)
            series = rest_model.contact_series(payload)
            stats = kinematics.analyze(payload)
            for tid, points in series.items():
                stat = stats.get(tid)
                if not stat or stat["n_frames"] < min_frames:
                    continue
                residual = rest_model.residuals(points, "recent", window)
                if len(residual) < 10:
                    continue
                for velocity in rest_model.VELOCITY_GRID:
                    flags = [False] * len(residual)
                    for i in range(1, len(residual)):
                        v = (residual[i][1] - residual[i - 1][1]) * 91.0
                        flags[i] = abs(v) > velocity
                    target[velocity] = max(target.get(velocity, 0), rest_model.max_run(flags))
    rows = []
    for velocity in rest_model.VELOCITY_GRID:
        rr, mr = rest.get(velocity, 0), mover.get(velocity, 0)
        for persistence in rest_model.PERSISTENCE_GRID:
            rows.append({"velocity_mm_s": velocity, "persistence_frames": persistence,
                         "rest_worst_run": rr, "mover_best_run": mr,
                         "clean": rr < persistence <= mr})
    return rows


def _rest_covariance(rest_sources, min_frames):
    contacts = []
    for path in rest_sources:
        payload = kinematics._load(path)
        series = rest_model.contact_series(payload)
        stats = kinematics.analyze(payload)
        for tid, points in series.items():
            stat = stats.get(tid)
            if stat and stat["n_frames"] >= min_frames:
                contacts.append({"source": path.name, "contact_id": tid,
                                "position_covariance": covariance([(x, y) for _t, x, y in points])})
    return contacts


def calibrate_user(rest_sources, mover_sources=(), *, user_label="local",
                   windows=rest_model.WINDOWS, min_frames=50,
                   gesture_coverage=None, min_gesture_coverage=1.0) -> dict:
    """Return a local calibration artifact with provenance and a declared choice.

    ``gesture_coverage`` is an optional mapping ``(velocity, persistence) -> fraction``.
    Without it, selection is explicitly marked rest-clean-only; callers must not mistake
    that for gesture-length coverage.
    """
    rest_sources = [Path(p) for p in rest_sources]
    mover_sources = [Path(p) for p in mover_sources]
    coverage = gesture_coverage or {}
    candidates = []
    for window in windows:
        rows = _tagged_separation(rest_sources, mover_sources, window, min_frames)
        for row in rows:
            row["gesture_coverage"] = coverage.get(
                (row["velocity_mm_s"], row["persistence_frames"]))
        candidates.append({"window_frames": window, "rows": rows})
    def eligible(row):
        if not row["clean"]:
            return False
        return (gesture_coverage is None or
                (row["gesture_coverage"] is not None and
                 row["gesture_coverage"] >= min_gesture_coverage))
    clean = [dict(row, window_frames=window)
             for candidate in candidates for row in candidate["rows"] if eligible(row)]
    selected = min(clean, key=lambda row: (row["persistence_frames"],
                                           row["velocity_mm_s"])) if clean else None
    sources = rest_sources + mover_sources
    return {
        "schema": SCHEMA, "version": VERSION, "user_label": user_label,
        "source_count": len(sources),
        "source_sha256": {str(path): file_sha256(path) for path in sources},
        "windows": list(windows), "min_frames": min_frames,
        "gesture_coverage_source": "caller" if gesture_coverage is not None else None,
        "min_gesture_coverage": (min_gesture_coverage
                                 if gesture_coverage is not None else None),
        "selection_basis": "rest_clean_and_gesture_coverage" if gesture_coverage is not None
                       else "rest_clean_only",
        "rest_covariance": _rest_covariance(rest_sources, min_frames),
        "candidates": candidates, "selected": selected,
        "production_defaults_unchanged": {
            "velocity_mm_s": rest_model.MIN_SPEED_MM_S,
            "persistence_frames": rest_model.MIN_RUN_FRAMES,
        },
    }


def replay_sweep(artifact: dict, rest_sources, mover_sources=()) -> dict:
    """Recompute a calibration artifact and compare source hashes/selection."""
    coverage = {(row["velocity_mm_s"], row["persistence_frames"]): row["gesture_coverage"]
                for candidate in artifact["candidates"] for row in candidate["rows"]
                if row.get("gesture_coverage") is not None}
    current = calibrate_user(rest_sources, mover_sources,
                            min_gesture_coverage=artifact.get("min_gesture_coverage", 1.0),
                            windows=artifact["windows"],
                            min_frames=artifact["min_frames"],
                            gesture_coverage=coverage or None)
    return {"source_hashes_match": artifact["source_sha256"] == current["source_sha256"],
            "selected": current["selected"], "candidates": current["candidates"]}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rest", nargs="+", type=Path, required=True)
    ap.add_argument("--mover", nargs="*", type=Path, default=[])
    ap.add_argument("--user-label", default="local")
    ap.add_argument("--out", type=Path)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    artifact = calibrate_user(args.rest, args.mover, user_label=args.user_label)
    text = json.dumps(artifact, indent=2, sort_keys=True, allow_nan=False)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text + "\n", encoding="utf-8")
    elif args.json:
        print(text)
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
