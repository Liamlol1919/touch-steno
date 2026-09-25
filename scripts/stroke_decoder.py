#!/usr/bin/env python3
"""Event -> stroke decoder bridge: turn measured events into steno strokes via Plover's model.

This is the seam between the measurement layer (`intent_filter.py`) and the language layer
(Plover / steno dictionaries). It is deliberately thin and testable:

  1. `intent_filter` emits ranked event candidates (mover, suppressed followers).
  2. this module turns an event into a *geometric descriptor*: direction sector, magnitude
     band, chord-vs-single, and the per-contact set of surviving contacts.
  3. an external mapping table assigns a steno key to each descriptor class.

The mapping table is data, not code, because the 8-vs-16-zone decision and the
sector->syllable assignment are exactly the things under experiment
(VECTOR_DESIGN_CRITIQUE.md, CROSS_VALIDATION.md 1.4/1.7). Swapping the table must not
require touching the decoder.

Reference-counts the geometry so the mapping is auditable: every descriptor class carries
the number of events that fell into it, and unassigned classes are reported loudly rather
than silently dropped (a silent drop here is the "decoder produces plausible garbage"
failure mode DECODER_DESIGN.md warns about).

Usage:
    python3 scripts/stroke_decoder.py session.jsonl
    python3 scripts/stroke_decoder.py --map my_map.json session.jsonl
    python3 scripts/stroke_decoder.py --json session.jsonl
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import intent_filter  # noqa: E402
import kinematics  # noqa: E402

# 8-way compass, axis-aligned (CROSS_VALIDATION 1.7: on-axis items are more reliable than
# off-axis ones), so the grid is N, NE, E, SE, S, SW, W, NW.
# Sector order matters: sector_of() measures atan2(-dy, dx), so index 0 is East and the
# list runs counter-clockwise. A wrong order here silently rotates every label by 45 deg.
SECTORS = ("E", "NE", "N", "NW", "W", "SW", "S", "SE")
# Magnitude bands in mm of accumulated displacement over the event window.
BANDS = (("micro", 2.0), ("small", 5.0), ("medium", 10.0), ("large", 1e9))


def sector_of(dx: float, dy: float) -> str:
    """Map a displacement vector to one of 8 axis-aligned sectors.

    Screen coords: y grows downward, so -dy makes "up" North. Returns the cardinal name a
    human would use for the on-screen direction.
    """
    ang = math.degrees(math.atan2(-dy, dx)) % 360.0
    idx = int((ang + 22.5) // 45) % 8
    return SECTORS[idx]


def band_of(disp: float) -> str:
    for name, limit in BANDS:
        if disp < limit:
            return name
    return BANDS[-1][0]


def event_descriptor(ev: dict, positions: dict[str, tuple[float, float]]) -> dict:
    """Turn one intent-filter event into a geometric descriptor.

    positions: tid -> (x, y) at the *start* of the event, for the direction reference.
    """
    # Chord means: >= 2 contacts whose motion the coupling model could NOT explain.
    # A contact the filter suppressed as "dragged" is not part of the intent, so counting
    # it would mark every event in a ten-finger session as a chord. That was measured, not
    # assumed: with the naive rule 108/108 events came out as chords.
    unexplained = [u["tid"] for u in ev["unexplained_contacts"] if u["tid"]]
    suppressed = [s["tid"] for s in ev["suppressed_as_dragged"] if s["tid"]]
    contacts = ([ev["mover"]] + unexplained + suppressed)
    contacts = [c for c in contacts if c]
    p0 = positions.get(ev["mover"])
    p1 = positions.get(ev["mover"] + "@end")
    if p0 is None or p1 is None:
        return {"descriptor": None, "reason": "no position reference for mover"}
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    disp = ev.get("mover_displacement_mm") or math.hypot(dx, dy)
    # A real chord needs a second *unexplained* mover, not merely a second contact.
    chord = len(unexplained) >= 1
    desc = f"{sector_of(dx, dy)}|{band_of(disp)}|{'chord' if chord else 'single'}"
    return {"descriptor": desc, "sector": sector_of(dx, dy),
            "band": band_of(disp), "chord": chord, "contacts": contacts,
            "unexplained": unexplained, "displacement_mm": round(disp, 2)}


SECTOR_EDGE_SAFETY_DEG = 10.0   # how close to a sector edge counts as "on the fence"


def confidence(dx, dy, disp, sector, r_mm=20.0):
    """Per-stroke confidence from measured, geometric quantities only.

    DECODER_DESIGN.md requires every emitted event to carry provenance and a confidence.
    Four components, each independently interpretable (no opaque score):

      edge_margin_deg  distance from the sector boundary; 0 = exactly on the fence.
                       This is the dominant term: the label is geometrically ambiguous
                       there, whatever the speed was.
      arc_occupancy    displacement as a fraction of the expected one-sector arc
                       (2*pi*r/8 = 15.7 mm at r=20 mm). Short strokes stay inside their
                       sector; long ones can cross into the neighbour.
      unexplained      how many contacts the coupling model could not explain; more means
                       the chord reading is ambiguous.
      mover_share      mover displacement vs the largest unexplained competitor, i.e. how
                       clearly one finger dominated the event.
    """
    mag = math.hypot(dx, dy)
    ang = math.degrees(math.atan2(-dy, dx)) % 360.0
    local = (ang - 22.5) % 45.0 - 22.5          # signed distance to nearest sector edge
    edge_margin = 22.5 - abs(local)
    sector_arc = 2.0 * math.pi * r_mm / 8.0
    arc_occupancy = min(1.0, disp / sector_arc) if sector_arc else 0.0
    return {
        "edge_margin_deg": round(edge_margin, 1),
        "on_fence": edge_margin < SECTOR_EDGE_SAFETY_DEG,
        "arc_occupancy": round(arc_occupancy, 2),
        "sector_arc_mm": round(sector_arc, 1),
    }


def chord_candidates(rows, start, end, mover, peak_ratio=0.5, max_lag=2):
    """Contacts that plausibly form an intentional chord with the mover.

    Contact count is not a chord criterion: with ten fingers resting, every measured event
    had ~7 contacts whose motion the coupling model could not explain, and 108/108 events
    would have been called chords. The criterion that survives the measurement is
    *temporal alignment plus magnitude*: a second finger counts as part of the chord when
    its own peak speed reaches `peak_ratio` of the mover's peak speed AND its peak frame is
    within `max_lag` frames of the mover's peak frame.

    Returns (chord_tids, diagnostics per contact).
    """
    window = rows[start + 1:end + 1]
    peaks: dict[str, tuple[float, int]] = {}
    for i, row in enumerate(window):
        for tid, (_dx, _dy, v) in row.items():
            if tid not in peaks or v > peaks[tid][0]:
                peaks[tid] = (v, i)
    if mover not in peaks:
        return [], {}
    mv, mi = peaks[mover]
    chord, diag = [], {}
    for tid, (v, i) in peaks.items():
        if tid == mover:
            continue
        ratio = (v / mv) if mv > 0 else 0.0
        lag = abs(i - mi)
        diag[tid] = {"peak_mm_s": round(v, 1), "ratio": round(ratio, 2),
                     "lag_frames": lag, "chord": ratio >= peak_ratio and lag <= max_lag}
        if diag[tid]["chord"]:
            chord.append(tid)
    return chord, diag


DEFAULT_MAP = {
    # A minimal, honest starter table: axes only, single-contact, two magnitude bands.
    "N|small|single": "K",
    "E|small|single": "T",
    "S|small|single": "P",
    "W|small|single": "H",
    "N|medium|single": "A",
    "E|medium|single": "O",
    "S|medium|single": "E",
    "W|medium|single": "U",
    # Everything else is deliberately unmapped and must be reported, not guessed.
}


def analyse(path: Path, mapping: dict) -> dict:
    payload = kinematics._strip_uninit_leads(kinematics._load(path))
    res = intent_filter.analyse(path, intent_filter.MIN_SPEED_MM_S,
                                intent_filter.MIN_RUN_FRAMES)
    # position index at each event boundary so we can get a start->end vector
    t_to_pos = {}
    for fr in payload:
        t = float(fr["t"])
        for tid, (x, y, _m) in fr["c"].items():
            t_to_pos.setdefault(tid, []).append((t, float(x), float(y)))
    per_tid = {tid: sorted(v) for tid, v in t_to_pos.items()}

    def pos_at(tid, t):
        seq = per_tid.get(tid, [])
        lo, hi = 0, len(seq)
        while lo < hi:
            mid = (lo + hi) // 2
            if seq[mid][0] < t:
                lo = mid + 1
            else:
                hi = mid
        return (seq[lo][1], seq[lo][2]) if lo < len(seq) else None

    rows = intent_filter.steps_of(payload)
    counts: dict[str, int] = {}
    strokes: list[dict] = []
    unmapped: dict[str, int] = {}
    chord_hist: dict[str, int] = {}
    for ev in res["events"]:
        mover = ev["mover"]
        t0 = ev["t_start"]
        # frame indices for the event window, so the chord rule can use peak timing
        starts = [i for i, fr in enumerate(payload) if t0 <= float(fr["t"]) <= ev["t_end"]]
        if not starts:
            continue
        chord_tids, diag = chord_candidates(rows, starts[0], starts[-1], mover)
        key_chord = f"chord{len(chord_tids)}" if chord_tids else "single"
        chord_hist[key_chord] = chord_hist.get(key_chord, 0) + 1
        p0 = pos_at(mover, t0)
        p1 = pos_at(mover, ev["t_end"])
        positions = {mover: p0, mover + "@end": p1} if p0 and p1 else {}
        d = event_descriptor(ev, positions)
        if not d.get("descriptor"):
            continue
        sector, band = d["sector"], d["band"]
        desc = f"{sector}|{band}|{key_chord}"
        counts[desc] = counts.get(desc, 0) + 1
        key = mapping.get(desc)
        if key is None:
            unmapped[desc] = unmapped.get(desc, 0) + 1
            continue
        conf = confidence(p1[0] - p0[0], p1[1] - p0[1], d["displacement_mm"], sector)
        comp = max((u["displacement_mm"] for u in ev["unexplained_contacts"]), default=0.0)
        mover_share = (d["displacement_mm"] /
                       max(d["displacement_mm"], comp)) if d["displacement_mm"] else 0.0
        conf["unexplained_contacts"] = len(chord_tids)
        conf["mover_share"] = round(mover_share, 2)
        strokes.append({"t_start": t0, "descriptor": desc, "stroke": key,
                        "sector": sector, "displacement_mm": d["displacement_mm"],
                        "chord_contacts": chord_tids,
                        "chord_diagnostics": diag,
                        "confidence": conf,
                        "provenance": {"source": path.name,
                                       "event_t_end": ev["t_end"],
                                       "contacts": d["contacts"],
                                       "suppressed": [s["tid"] for s in
                                                      ev["suppressed_as_dragged"]]}})
    return {"session": path.name, "events": len(res["events"]),
            "decoded": len(strokes), "descriptor_counts": counts,
            "chord_histogram": chord_hist,
            "unmapped": unmapped, "strokes": strokes}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("sessions", nargs="+", type=Path)
    ap.add_argument("--map", type=Path,
                    help="JSON mapping descriptor -> steno key (overrides starter table)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    mapping = dict(DEFAULT_MAP)
    if args.map:
        mapping = json.loads(args.map.read_text(encoding="utf-8"))
    out = [analyse(p, mapping) for p in args.sessions]
    if args.json:
        print(json.dumps(out, indent=2))
        return 0
    for r in out:
        print(f"\n## {r['session']}  events={r['events']}  decoded={r['decoded']}")
        print("descriptor counts (all events):")
        for d, n in sorted(r["descriptor_counts"].items(), key=lambda kv: -kv[1]):
            print(f"  {d:<22} {n}")
        if r["unmapped"]:
            print("UNMAPPED (reported, not guessed):")
            for d, n in sorted(r["unmapped"].items(), key=lambda kv: -kv[1]):
                print(f"  {d:<22} {n}")
        print("strokes (mapped):")
        for s in r["strokes"][:40]:
            print(f"  t={s['t_start']:>10.2f} {s['descriptor']:<22} -> {s['stroke']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
