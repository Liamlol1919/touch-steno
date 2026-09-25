#!/usr/bin/env python3
"""Offline raw-capture analysis for the cued bimanual protocol.

This module intentionally stops before intent filtering, anatomical identity inference,
mover selection, or suppression. Tracking IDs are contact-episode keys only. Cued hand
labels remain schedule metadata, never labels for a tracking ID.
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kinematics  # noqa: E402
import session_manifest  # noqa: E402

SCHEMA = "chordtouch.bimanual_coupling_analysis"
VERSION = 1
MIN_EPISODE_SAMPLES = 2
MIN_LAG_OVERLAP = 40


def _finite(value: float, name: str) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


def _validate_frames(frames: list[dict]) -> list[dict]:
    previous_t = None
    out = []
    for frame in frames:
        t = _finite(frame["t"], "frame timestamp")
        if previous_t is not None and t <= previous_t:
            raise ValueError("frame timestamps must be strictly increasing")
        contacts = {}
        for tid, value in frame["c"].items():
            if not isinstance(value, (list, tuple)) or len(value) != 3:
                raise ValueError("contact tuples must contain x, y, major")
            x, y, major = (_finite(v, f"contact {tid}") for v in value)
            contacts[str(tid)] = (x, y, major)
        out.append({"t": t, "c": contacts})
        previous_t = t
    return out


def contact_episodes(frames: list[dict], session_id: str = "session") -> list[dict]:
    """Split contact lifetimes at every absent-to-present transition."""
    frames = _validate_frames(frames)
    episodes: list[dict] = []
    active: dict[str, dict] = {}
    previous_ids: set[str] = set()
    for frame_index, frame in enumerate(frames):
        current_ids = set(frame["c"])
        for tid in current_ids - previous_ids:
            episode_index = sum(1 for row in episodes if row["tracking_id"] == tid)
            episode = {
                "trajectory_key": f"{session_id}::{tid}::{episode_index}",
                "tracking_id": tid,
                "episode_index": episode_index,
                "entered_before_capture": frame_index == 0,
                "t_start": frame["t"],
                "t_end": frame["t"],
                "samples": [],
            }
            episodes.append(episode)
            active[tid] = episode
        for tid in current_ids:
            x, y, major = frame["c"][tid]
            episode = active[tid]
            episode["t_end"] = frame["t"]
            episode["samples"].append({"t": frame["t"], "x": x, "y": y, "major": major})
        previous_ids = current_ids
    return episodes


def _summary(values: list[float]) -> dict:
    if not values:
        return {"n": 0, "min": None, "p05": None, "median": None, "mean": None,
                "p95": None, "max": None, "sd": None, "mad": None}
    ordered = sorted(values)
    p05 = ordered[max(0, math.ceil(0.05 * len(ordered)) - 1)]
    p95 = ordered[min(len(ordered) - 1, math.ceil(0.95 * len(ordered)) - 1)]
    median = statistics.median(ordered)
    return {"n": len(ordered), "min": ordered[0], "p05": p05,
            "median": median, "mean": statistics.fmean(ordered), "p95": p95,
            "max": ordered[-1],
            "sd": statistics.stdev(ordered) if len(ordered) > 1 else None,
            "mad": statistics.median(abs(value - median) for value in ordered)}


def _block_rates(cues: list[dict], rate_hz: float) -> dict:
    duration = sum(float(cue["t_end"]) - float(cue["t_start"]) for cue in cues)
    valid = sum(cue["valid"] for cue in cues)
    onsets = sum(cue["raw_new_episode_count"] for cue in cues)
    realized = valid / duration if duration else None
    return {"cued_cycle_hz": rate_hz, "valid_cycles": valid,
            "raw_new_episodes": onsets,
            "realized_cycle_hz": realized,
            "cycle_rate_ratio": realized / rate_hz if realized is not None and rate_hz else None,
            "contact_onset_hz": onsets / duration if duration else None,
            "basis": "valid_cues / sum(measured_cue_durations)"}


def _interval_summary(cues: list[dict]) -> dict | None:
    samples = []
    directions = {"left_to_right": [], "right_to_left": []}
    for previous, current in zip(cues, cues[1:]):
        if not previous["valid"] or not current["valid"]:
            continue
        if current["event_index"] != previous["event_index"] + 1:
            continue
        if len(previous["onsets"]) != 1 or len(current["onsets"]) != 1:
            continue
        left = previous["associated_cued_hands"]
        right = current["associated_cued_hands"]
        if left == right or left[0] not in ("left", "right") or right[0] not in ("left", "right"):
            continue
        delta = current["onsets"][0]["t"] - previous["onsets"][0]["t"]
        samples.append(delta)
        directions[f"{left[0]}_to_{right[0]}"].append(delta)
    if not samples:
        return None
    summary = _summary(samples)
    return {"anatomical_inter_hand_verified": False,
            "definition": "onset interval between adjacent valid cues with opposite cued sides",
            "direction_counts": {key: len(value) for key, value in directions.items()},
            "samples_s": samples, "summary_s": summary,
            "by_cued_direction_s": {key: {"n": len(value),
                                          "mean": statistics.fmean(value) if value else None,
                                          "sd": statistics.stdev(value) if len(value) > 1 else None}
                                    for key, value in directions.items()}}


def _steps(episode: dict, start: float, end: float) -> list[tuple[float, float, float]]:
    samples = [sample for sample in episode["samples"]
               if start <= sample["t"] < end]
    out = []
    for previous, current in zip(samples, samples[1:]):
        dt = current["t"] - previous["t"]
        if dt > 0:
            out.append(((previous["t"] + current["t"]) / 2.0,
                        current["x"] - previous["x"], current["y"] - previous["y"]))
    return out


def _paired_steps(first: list[tuple[float, float, float]],
                  second: list[tuple[float, float, float]]) -> list[tuple[float, float, float, float, float]]:
    if not first or not second:
        return []
    all_times = [row[0] for row in first] + [row[0] for row in second]
    tolerance = statistics.median([abs(b - a) for a, b in zip(sorted(all_times), sorted(all_times)[1:])]) / 2.0 \
        if len(all_times) > 1 else 0.001
    tolerance = max(tolerance, 1e-6)
    out = []
    second_index = 0
    for t, ax, ay in first:
        while second_index < len(second) and second[second_index][0] < t - tolerance:
            second_index += 1
        if second_index >= len(second):
            break
        st, bx, by = second[second_index]
        if abs(st - t) <= tolerance:
            out.append((t, ax, ay, bx, by))
    return out


def _profile(first: list[tuple[float, float, float]],
             second: list[tuple[float, float, float]], max_lag: int = 5) -> dict:
    sequence = _paired_steps(first, second)
    if len(sequence) < MIN_LAG_OVERLAP:
        return {"n_overlap_samples": len(sequence), "profile": [], "zero_lag_r": None,
                "zero_lag_centered_pearson_r": None, "peak_r": None,
                "peak_lag_frames": None, "zero_lag_half_width_frames": None,
                "status": "insufficient_overlap"}
    values = []
    for lag in range(-max_lag, max_lag + 1):
        pairs = []
        for i in range(len(sequence) - abs(lag)):
            j = i + lag if lag > 0 else i
            k = i - lag if lag < 0 else i
            ax, ay = sequence[j][1:3]
            bx, by = sequence[k][3:5]
            pairs.append((ax, ay, bx, by))
        numerator = sum(a * c + b * d for a, b, c, d in pairs)
        da = sum(a * a + b * b for a, b, c, d in pairs)
        db = sum(c * c + d * d for a, b, c, d in pairs)
        value = numerator / math.sqrt(da * db) if da > 0 and db > 0 else None
        values.append({"lag_frames": lag, "r": value})
    zero = next(row["r"] for row in values if row["lag_frames"] == 0)
    finite = [row for row in values if row["r"] is not None]
    peak = max(finite, key=lambda row: (abs(row["r"]), -abs(row["lag_frames"]))) if finite else None
    centered = None
    if zero is not None:
        first = [row[1:3] for row in sequence]
        second = [row[3:5] for row in sequence]
        ax = [component for pair in first for component in pair]
        bx = [component for pair in second for component in pair]
        m_a, m_b = statistics.fmean(ax), statistics.fmean(bx)
        cov = sum((ax[i] - m_a) * (bx[i] - m_b) for i in range(len(ax)))
        va = sum((value - m_a) ** 2 for value in ax)
        vb = sum((value - m_b) ** 2 for value in bx)
        centered = cov / math.sqrt(va * vb) if va > 0 and vb > 0 else None
    half_width = None
    if zero is not None and abs(zero) > 0:
        for row in values:
            if row["lag_frames"] >= 0 and row["r"] is not None and abs(row["r"]) < 0.5 * abs(zero):
                half_width = row["lag_frames"]
                break
    return {"n_overlap_samples": len(sequence), "profile": values,
            "zero_lag_r": zero, "zero_lag_centered_pearson_r": centered,
            "peak_r": peak["r"] if peak else None,
            "peak_lag_frames": peak["lag_frames"] if peak else None,
            "zero_lag_half_width_frames": half_width, "status": "ok"}


def _validate_manifest(records: list[dict]) -> list[dict]:
    if not records:
        raise ValueError("manifest is empty")
    ids = set()
    result = []
    for record in records:
        cue_id = record.get("cue_id")
        if not isinstance(cue_id, str) or cue_id in ids:
            raise ValueError("bimanual manifest requires unique cue_id values")
        ids.add(cue_id)
        if record.get("bimanual_mode") not in ("alternating", "simultaneous", "rest"):
            raise ValueError("unknown bimanual mode")
        if record.get("t_start") is None or record.get("t_end") is None or record["t_end"] <= record["t_start"]:
            raise ValueError("manifest intervals must be complete and increasing")
        if record.get("event_provenance") != "expected_cue_schedule":
            raise ValueError("bimanual events must use expected_cue_schedule provenance")
        events = record.get("events")
        hands = record.get("event_hands")
        if not isinstance(events, list) or not isinstance(hands, list) or len(events) != len(hands):
            raise ValueError("events and event_hands must have equal cardinality")
        result.append(record)
    result.sort(key=lambda row: row["t_start"])
    for previous, current in zip(result, result[1:]):
        if current["t_start"] < previous["t_end"]:
            raise ValueError("manifest intervals overlap")
    return result


def analyse(frames: list[dict], records: list[dict], session_id: str = "session") -> dict:
    """Return raw, unfiltered bimanual timing and pair statistics."""
    frames = _validate_frames(frames)
    records = _validate_manifest(records)
    session_ids = {record.get("session_id") for record in records if record.get("session_id") is not None}
    if len(session_ids) > 1:
        raise ValueError("manifest contains multiple session IDs")
    session_id = next(iter(session_ids), session_id)
    episodes = contact_episodes(frames, session_id)
    blocks: dict[int, list[dict]] = {}
    rests = []
    for record in records:
        if record["bimanual_mode"] == "rest":
            rests.append(record)
        else:
            blocks.setdefault(record["block_index"], []).append(record)
    block_reports = []
    for block_index, cues in sorted(blocks.items()):
        cues.sort(key=lambda row: row["event_index"])
        cue_reports = []
        for record in cues:
            expected = len(record["events"])
            onsets = []
            for episode in episodes:
                if not episode["entered_before_capture"] and record["t_start"] <= episode["t_start"] < record["t_end"]:
                    onsets.append({"trajectory_key": episode["trajectory_key"],
                                   "t": episode["t_start"],
                                   "relative_s": episode["t_start"] - record["t_start"],
                                   "associated_cued_side": (record["event_hands"][0]
                                                           if record["bimanual_mode"] == "alternating" and expected == 1
                                                           else None)})
            onsets.sort(key=lambda row: row["t"])
            valid = len(onsets) == expected and all(
                sum(1 for sample in episode["samples"] if record["t_start"] <= sample["t"] < record["t_end"]) >= MIN_EPISODE_SAMPLES
                for episode in episodes if not episode["entered_before_capture"] and record["t_start"] <= episode["t_start"] < record["t_end"])
            failure = None
            if not onsets:
                failure = "no_new_contact"
            elif len(onsets) != expected:
                failure = "extra_contact" if len(onsets) > expected else "missing_contact"
            elif not valid:
                failure = "one_frame_contact"
            for onset, offset in zip(onsets, record["events"]):
                onset["latency_s"] = onset["t"] - (record["t_start"] + float(offset))
            active_keys = [episode["trajectory_key"] for episode in episodes
                           if episode["t_start"] < record["t_end"] and episode["t_end"] >= record["t_start"]]
            cue_reports.append({"cue_id": record["cue_id"], "event_index": record["event_index"],
                                "t_start": record["t_start"], "t_end": record["t_end"],
                                "expected_offsets_s": record["events"],
                                "expected_times_s": [record["t_start"] + float(value) for value in record["events"]],
                                "associated_cued_hands": record["event_hands"],
                                "raw_new_episode_count": len(onsets), "onsets": onsets,
                                "active_trajectory_keys": active_keys, "valid": valid,
                                "failure": failure})
        rate = float(cues[0]["rate_hz"])
        start = min(cue["t_start"] for cue in cues)
        end = max(cue["t_end"] for cue in cues)
        interval = _interval_summary(cue_reports) if cues[0]["bimanual_mode"] == "alternating" else None
        simultaneous = []
        if cues[0]["bimanual_mode"] == "simultaneous":
            for cue in cue_reports:
                if cue["valid"] and len(cue["onsets"]) == 2:
                    simultaneous.append(abs(cue["onsets"][1]["t"] - cue["onsets"][0]["t"]))
        pairs = []
        for first, second in combinations(episodes, 2):
            if first["t_start"] >= end or second["t_start"] >= end or first["t_end"] <= start or second["t_end"] <= start:
                continue
            a_steps, b_steps = _steps(first, start, end), _steps(second, start, end)
            if len(a_steps) < MIN_LAG_OVERLAP or len(b_steps) < MIN_LAG_OVERLAP:
                continue
            profile = _profile(a_steps, b_steps)
            pairs.append({"trajectory_keys": [first["trajectory_key"], second["trajectory_key"]],
                          "lag_convention": "positive means first trajectory step precedes second",
                          **profile})
        block_reports.append({"block_index": block_index, "mode": cues[0]["bimanual_mode"],
                              "rate_hz": rate, "condition_index": cues[0]["condition_index"],
                              "condition_order": cues[0].get("condition_order"),
                              "t_start": start, "t_end": end,
                              "cue_ids": [cue["cue_id"] for cue in cue_reports],
                              "cues": cue_reports, "rates": _block_rates(cue_reports, rate),
                              "alternating_intervals": interval,
                              "simultaneous_onset_error_s": _summary(simultaneous),
                              "raw_pair_coupling": pairs})
    return {"schema": SCHEMA, "version": VERSION,
            "input": {"frame_count": len(frames), "session_id": session_id,
                      "episode_count": len(episodes)},
            "identity": {"status": "unverified", "tracking_id_scope": "single_contact_episode_within_one_session",
                         "anatomical_labels_emitted": False,
                         "reason": "manifest contains cued sides, not a validated tracking-ID-to-hand mapping"},
            "raw_trajectories": episodes, "blocks": block_reports,
            "rest": [{"cue_id": record["cue_id"], "t_start": record["t_start"],
                      "t_end": record["t_end"], "raw_new_episode_count": sum(
                          1 for episode in episodes if not episode["entered_before_capture"]
                          and record["t_start"] <= episode["t_start"] < record["t_end"])}
                     for record in rests],
            "warnings": ["raw analysis only; no intent suppression or anatomical identity inference"]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("session", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    manifest_path = args.session.with_name(args.session.stem + ".manifest.jsonl")
    if not manifest_path.exists():
        raise SystemExit(f"manifest fehlt: {manifest_path}")
    report = analyse(kinematics._load(args.session), session_manifest.load(manifest_path))
    text = json.dumps(report, indent=2, sort_keys=True, allow_nan=False)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text + "\n", encoding="utf-8")
    elif args.json:
        print(text)
    else:
        print(f"blocks: {len(report['blocks'])}; trajectories: {len(report['raw_trajectories'])}")
        for block in report["blocks"]:
            print(f"  block {block['block_index']} {block['mode']} {block['rate_hz']}Hz "
                  f"valid={block['rates']['valid_cycles']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
