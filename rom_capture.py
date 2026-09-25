#!/usr/bin/env python3
"""Measure the operator's comfortable range of motion and write a hand profile.

The layout optimiser needs four things it cannot guess: where the thumb rests, how far
it reaches when you *want* to (not when you can), which way the fan runs, and how
much slower a sideways sweep is than a radial extension. This program measures all
four with the right hand on the pad and writes the profile that
`layout_optimizer.py --hand-profile` consumes.

Two modes:

  --device /dev/input/eventN   live capture. Needs the tablet and python-evdev.
  --manual                     no device: prints a measurement sheet and asks the
                               same questions. Writes the same profile.

The comfort/max distinction is measured, not assumed: every sweep is run twice, once
with the cue "as far as you comfortably want to" and once with "as far as physically
possible". The profile is built from the comfort run; the max run is reported as the
ceiling and their ratio is printed, because the gap between the two is the number
that decides whether 16 zones per thumb is buildable at all.

Usage:
    python3 rom_capture.py --device /dev/input/event19 --out-dir messung/rom
    python3 rom_capture.py --manual --out-dir messung/rom
    python3 rom_capture.py --self-test      # synthetic events, no hardware
"""
from __future__ import annotations

import argparse
import json
import math
import pathlib
import statistics
import sys
import time
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

PAD_W, PAD_H = 224.0, 148.0
GRID_MM = 5.0
FINGER_MAX_SPAN_MM = 30.0        # a contact wider than this is a palm, not a finger
# Linux input event codes for MT protocol B. These are NOT 0..4: ABS_X/ABS_Y are 0/1,
# the MT block starts at 0x2f. Getting these wrong silently reads nothing at all.
ABS_X, ABS_Y = 0, 0x01
ABS_MT_SLOT = 0x2f               # 47
ABS_MT_TOUCH_MAJOR = 0x30         # 48
ABS_MT_POSITION_X = 0x35         # 53
ABS_MT_POSITION_Y = 0x36         # 54
ABS_MT_TRACKING_ID = 0x39        # 57
REST_QUIET_S = 0.6               # a contact must be this still to count as resting
DEFAULT_SPEED_MM_S = 220.0       # reference radial speed, only used for the ratio

# The cue shown for every step. `kind` selects how the samples are reduced.
STEPS = [
    ("calibrate_bl", "Touch the bottom-left corner of the pad once and hold 1 s.", "point"),
    ("calibrate_br", "Touch the bottom-right corner once and hold 1 s.", "point"),
    ("calibrate_tl", "Touch the top-left corner once and hold 1 s.", "point"),
    ("rest", "Lay your right hand flat but lift the heel so ONLY the thumb touches. "
             "Relax completely, then hold still 3 s.", "rest"),
    ("comfort_radial", "Slide the thumb tip straight away from its rest point, as far "
                       "as you would comfortably want to, and back. 6 times.", "sweep"),
    ("max_radial", "Same movement, but as far as physically possible. 6 times.", "sweep"),
    ("comfort_fan", "Sweep the thumb sideways through the whole fan, staying inside "
                    "what is comfortable, and back. 6 times.", "sweep"),
    ("max_fan", "Same sweep, but use your full range. 6 times.", "sweep"),
    ("spokes", "Move the thumb to the 4 directions of the fan in turn, pausing at each. "
               "One pass each direction.", "spokes"),
    ("index_reach", "Put only the index fingertip on the pad. Reach up as far as you "
                    "comfortably want to, then back. 6 times.", "sweep"),
    ("index_max", "Same reach, but as far as physically possible. 6 times.", "sweep"),
    ("index_spread", "Slide the index sideways as wide as comfortable, and back. 6 times.", "sweep"),
    ("cross_centre", "Reach with the right thumb across the middle line of the pad. "
                     "If that is not comfortable, say so - it changes the topology.", "sweep"),
    ("hold", "Rest the thumb tip on the most comfortable spot you found and hold still "
             "5 s without lifting.", "hold"),
]
RATING_PROMPT = "How did that feel? 1 = effortful, 5 = effortless [1-5, or 0 to skip]"


# --------------------------------------------------------------------------- #
# contact tracking (fed by evdev events or by the synthetic test)
# --------------------------------------------------------------------------- #

@dataclass
class Contact:
    """One completed touch: where it ended, how long, how far it travelled, and how
    large its bounding box got (that is what separates a fingertip from a palm)."""
    x: float
    y: float
    duration: float
    path: float
    span: float
    moved: bool
    rejected: str = ""


class ContactTracker:
    """Turns a stream of (code, value, time) absolute-axis events into contacts.

    Handles MT protocol B (ABS_MT_TRACKING_ID plus slot positions) and the plain
    single-pointer protocol (ABS_X / ABS_Y). If MT events are seen at all, the
    single-pointer pair is ignored, because a pad in MT mode also emits a mirrored
    ABS_X / ABS_Y pair for the first slot.
    """

    MAX_SPAN_MM = FINGER_MAX_SPAN_MM

    def __init__(self, to_mm):
        self.to_mm = to_mm
        self.saw_mt = False
        self.slots: dict[int, dict] = {}
        self.legacy: dict | None = None

    def _new_slot(self, t: float) -> dict:
        return {"x": 0.0, "y": 0.0, "have_xy": False, "live": True, "t_down": t,
                "t_last": t, "path": 0.0, "minx": None, "miny": None,
                "maxx": None, "maxy": None}

    def _sample(self, cur: dict) -> None:
        x, y = self.to_mm(cur["x"], cur["y"])
        if cur["have_xy"]:
            cur["path"] += math.dist((x, y), cur["mm"])
        cur["mm"] = (x, y)
        cur["have_xy"] = True
        for key, val in (("minx", x), ("miny", y), ("maxx", x), ("maxy", y)):
            cur[key] = val if cur[key] is None else min(cur[key], val) if key in ("minx", "miny") else max(cur[key], val)

    def _finish(self, cur: dict) -> Contact | None:
        if not cur.get("have_xy"):
            return None
        span = max(cur["maxx"] - cur["minx"], cur["maxy"] - cur["miny"])
        reason = ""
        if span > self.MAX_SPAN_MM:
            reason = f"span {span:.0f} mm > {self.MAX_SPAN_MM:.0f} mm (palm/forearm)"
        x, y = cur["mm"]
        return Contact(x, y, cur["t_last"] - cur["t_down"], cur["path"], span,
                       cur["path"] > 1.0, reason)

    def feed(self, code: int, value: float, t: float) -> list[Contact]:
        closed: list[Contact] = []
        if code in (ABS_MT_SLOT, ABS_MT_TRACKING_ID, ABS_MT_POSITION_X, ABS_MT_POSITION_Y):
            self.saw_mt = True
            if code == ABS_MT_SLOT:
                self.slots[int(value)] = self.slots.get(0) or {
                    "x": 0.0, "y": 0.0, "have_xy": False, "live": False, "t_down": 0.0,
                    "t_last": 0.0, "path": 0.0, "minx": None, "miny": None,
                    "maxx": None, "maxy": None}
                return closed
            cur = self.slots.setdefault(0, {"x": 0.0, "y": 0.0, "have_xy": False,
                                            "live": False, "t_down": 0.0, "t_last": 0.0,
                                            "path": 0.0, "minx": None, "miny": None,
                                            "maxx": None, "maxy": None})
            if code == ABS_MT_TRACKING_ID:
                if value < 0:
                    if cur["live"]:
                        closed.append(self._finish(cur))
                    cur["live"] = False
                else:
                    cur.update(self._new_slot(t))
            elif cur["live"]:
                if code == ABS_MT_POSITION_X:
                    cur["x"] = value
                else:
                    cur["y"] = value
                cur["t_last"] = t
                self._sample(cur)
        elif code in (self.ABS_X, self.ABS_Y) and not self.saw_mt:
            if self.legacy is None:
                self.legacy = {"x": 0.0, "y": 0.0, "have_xy": False, "live": True,
                               "t_down": t, "t_last": t, "path": 0.0, "minx": None,
                               "miny": None, "maxx": None, "maxy": None}
            if code == self.ABS_X:
                self.legacy["x"] = value
            else:
                self.legacy["y"] = value
            self.legacy["t_last"] = t
            self._sample(self.legacy)
        return [c for c in closed if c is not None]

    def live_points(self) -> list[tuple[float, float]]:
        out = []
        for cur in list(self.slots.values()) + ([self.legacy] if self.legacy else []):
            if cur and cur.get("live") and cur.get("have_xy"):
                out.append(cur["mm"])
        return out


# --------------------------------------------------------------------------- #
# pad calibration: three corner taps -> affine map from raw axes to millimetres
# --------------------------------------------------------------------------- #

class Calibration:
    def __init__(self):
        self.bl = None
        self.br = None
        self.tl = None

    def fit(self) -> "callable":
        if not (self.bl and self.br and self.tl):
            raise ValueError("calibration needs the bottom-left, bottom-right and "
                             "top-left corner")
        (x0, y0), (x1, y1), (x2, y2) = self.bl, self.br, self.tl

        def to_mm(x: float, y: float) -> tuple[float, float]:
            # linear map that sends the three raw corners onto the three pad corners
            a = ((x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0)) or 1.0
            sx = (PAD_W * (y2 - y0) - PAD_W * (y1 - y0)) / a
            sy = (PAD_H * (x1 - x0) - PAD_H * (x2 - x0)) / a
            return (x0 + sx * (x - x0), y0 + sy * (y - y0))
        return to_mm


# --------------------------------------------------------------------------- #
# sample store
# --------------------------------------------------------------------------- #

@dataclass
class StepResult:
    name: str
    kind: str
    contacts: list[Contact] = field(default_factory=list)
    points: list[tuple[float, float, float]] = field(default_factory=list)
    rating: int | None = None
    t_start: float = 0.0
    t_end: float = 0.0

    def to_json(self) -> dict:
        return {
            "step": self.name, "kind": self.kind, "rating": self.rating,
            "seconds": round(self.t_end - self.t_start, 2),
            "contacts": [{"x": round(c.x, 1), "y": round(c.y, 1),
                          "duration_s": round(c.duration, 3), "path_mm": round(c.path, 1),
                          "span_mm": round(c.span, 1), "moved": c.moved,
                          "rejected": c.rejected} for c in self.contacts],
            "points": [[round(x, 1), round(y, 1), round(t, 3)] for x, y, t in self.points],
        }


# --------------------------------------------------------------------------- #
# analysis: samples -> profile
# --------------------------------------------------------------------------- #

def _polar(p: tuple[float, float], rest: tuple[float, float]) -> tuple[float, float]:
    return (math.dist(p, rest), math.degrees(math.atan2(p[1] - rest[1], p[0] - rest[0])) % 360)


def _median(vals) -> float:
    vals = [v for v in vals if v is not None]
    return statistics.median(vals) if vals else 0.0


def analyse(results: list[StepResult]) -> dict:
    """Turn the raw steps into a hand profile plus the diagnostics that justify it."""
    by = {r.name: r for r in results}
    calib_pts = {n: by[n].points[-1][:2] for n in ("calibrate_bl", "calibrate_br",
                                                   "calibrate_tl") if n in by}
    rest_pts = [(p[0], p[1]) for p in by.get("rest", StepResult("rest", "rest")).points]
    rest = (statistics.median([p[0] for p in rest_pts]),
            statistics.median([p[1] for p in rest_pts])) if rest_pts else (112.0, 9.0)

    def peaks(name: str) -> list[float]:
        r = by.get(name)
        return [_polar((c.x, c.y), rest)[0] for c in (r.contacts if r else [])]

    comfort_r = _median(peaks("comfort_radial"))
    max_r = _median(peaks("max_radial"))
    comfort_r = comfort_r or max_r

    angles = [_polar((c.x, c.y), rest)[1] for c in by.get("comfort_fan", StepResult("", "")).contacts]
    if not angles:
        angles = [_polar((c.x, c.y), rest)[1] for c in by.get("max_fan", StepResult("", "")).contacts]
    centres = _angular_span(angles) if len(angles) >= 3 else None
    fan = _sector_bounds(centres) if centres else (0.0, MIN_FAN_DEG * 3)
    if fan[1] - fan[0] < MIN_FAN_DEG:
        print(f"  note: the fan sweep gave a {fan[1] - fan[0]:.0f} deg span, which is too "
              f"narrow to host four sectors; falling back to {MIN_FAN_DEG * 3:.0f} deg",
              file=sys.stderr)
        fan = (0.0, MIN_FAN_DEG * 3)

    # tangential premium from the two sweeps: same stroke, different direction
    rad_speed = _mean_speed(by.get("comfort_radial"))
    tan_speed = _mean_speed(by.get("comfort_fan"))
    penalty = (rad_speed / tan_speed) if tan_speed > 0 else 1.0
    penalty = min(3.0, max(1.0, penalty))

    rings, rings_fit = _rings(comfort_r, fan[1] - fan[0])
    idx_rest = (rest[0] + INDEX_OFFSET_X_MM, 6.0)
    idx_pts = [(p[0], p[1]) for p in by.get("index_reach", StepResult("", "")).points]
    idx_r = _median([_polar(p, idx_rest)[0] for p in idx_pts]) or 85.0
    idx_max = _median([_polar((c.x, c.y), idx_rest)[0]
                       for c in by.get("index_max", StepResult("", "")).contacts]) or idx_r + 12.0
    spread = _median([(c.path or 0.0) for c in
                      by.get("index_spread", StepResult("", "")).contacts])
    idx_pitch = max(20.0, min(spread / 2.0 if spread else 26.0, 34.0))
    # the top row of the block sits exactly at the measured comfortable reach
    idx_centre = (idx_rest[0], idx_rest[1] + max(30.0, idx_r - idx_pitch / 2))

    profile = {
        "_measured_by": "rom_capture.py",
        "pad_mm": [PAD_W, PAD_H],
        "thumb": {
            "rest": [round(rest[0], 1), round(rest[1], 1)],
            "joint": [round(rest[0], 1), round(rest[1], 1)],
            "rings": rings,
            "fan_deg": [round(fan[0], 1), round(fan[1], 1)],
            "reach_mm": round(comfort_r, 1),
            "max_reach_mm": round(max(max_r, comfort_r), 1),
            "tangential_penalty": round(penalty, 2),
        },
        "index": {
            "rest": [round(idx_rest[0], 1), round(idx_rest[1], 1)],
            "joint": [round(idx_rest[0] + 2.0, 1), 2.0],
            "centre": [round(idx_centre[0], 1), round(idx_centre[1], 1)],
            "pitch": round(idx_pitch, 1),
            "reach_mm": round(idx_r, 1),
            "max_reach_mm": round(max(idx_max, idx_r), 1),
            "tangential_penalty": 1.0,
        },
    }
    diag = {
        "rest_mm": [round(rest[0], 1), round(rest[1], 1)],
        "comfort_reach_mm": round(comfort_r, 1),
        "max_reach_mm": round(max_r, 1),
        "comfort_over_max": round(comfort_r / max_r, 2) if max_r else None,
        "fan_deg": [round(fan[0], 1), round(fan[1], 1)],
        "rings_mm": rings,
        "rings_fit_11mm": rings_fit,
        "rings_needed_mm": round(3 * RING_MIN_GAP_MM, 1),
        "inner_ring_for_fan_mm": _inner_ring(fan[1] - fan[0]),
        "reach_for_4_rings_mm": round(required_reach(fan[1] - fan[0]), 1),
        "reach_for_3_rings_mm": round(required_reach(fan[1] - fan[0], 3), 1),
        "ring_gap_mm": round(_ring_widths(rings, fan[1] - fan[0])[0], 1),
        "inner_arc_mm": round(_ring_widths(rings, fan[1] - fan[0])[1], 1),
        "radial_speed_mm_s": round(rad_speed, 1),
        "tangential_speed_mm_s": round(tan_speed, 1),
        "tangential_penalty": round(penalty, 2),
        "index_reach_mm": round(idx_r, 1),
        "index_max_reach_mm": round(max(idx_max, idx_r), 1),
        "ratings": {r.name: r.rating for r in results if r.rating is not None},
        "calibration_corners": {k: [round(v[0], 1), round(v[1], 1)]
                                 for k, v in calib_pts.items()},
    }
    return profile, diag


def _sector_bounds(centres: tuple[float, float]) -> tuple[float, float]:
    """Turn the measured range of sector CENTRES into the fan boundaries.

    The topology builder places sector i at fan0 + (i + 0.5) * (fan1 - fan0) / 4, so
    four centres span 3/4 of the fan. Measured centres therefore map back to a fan of
    4/3 of their span, offset inward by half a step."""
    lo, hi = centres
    step = hi - lo
    if step <= 0.0:
        return (lo, lo)
    fan0 = lo - step / 6.0
    return (fan0 % 360.0, (fan0 + 4.0 * step / 3.0) % 360.0)


def _angular_span(angles: list[float]) -> tuple[float, float]:
    """Smallest arc containing every angle, in degrees."""
    if not angles:
        return (0.0, MIN_FAN_DEG * 3)
    s = sorted(a % 360 for a in angles)
    gaps = [(s[(i + 1) % len(s)] - s[i]) % 360 for i in range(len(s))]
    k = gaps.index(max(gaps))
    lo = s[(k + 1) % len(s)]
    hi = s[k]
    span = (hi - lo) % 360
    if span > 180.0:                     # the data is split; fall back to the fan
        return (0.0, MIN_FAN_DEG * 3)
    return (lo, (lo + span) % 360)


def _mean_speed(result: StepResult | None) -> float:
    """Median path speed over the contacts of a step, in mm/s.

    The cue decides the direction: the radial sweep is cued "straight away", the fan
    sweep "sideways", so their path speeds are the radial and the tangential speed."""
    if not result:
        return DEFAULT_SPEED_MM_S
    vals = [c.path / c.duration for c in result.contacts
            if c.duration > 0.05 and c.path > 1.0 and not c.rejected]
    return statistics.median(vals) if vals else DEFAULT_SPEED_MM_S


MIN_FAN_DEG = 40.0            # below this the sweep did not cover a fan
RING_MIN_GAP_MM = 11.0        # a zone shallower than the 10 mm target floor is unusable
TARGET_FLOOR_MM = 10.0        # NN/g one-hand thumb floor
INDEX_OFFSET_X_MM = 66.0      # declared: how far out the index block sits from the thumb rest


def sector_chord(r: float, fan_deg: float) -> float:
    """Straight-line width of one sector at radius r, i.e. the effective target
    width. The arc would be the path around the target, not its size."""
    return 2.0 * r * math.sin(math.radians(max(1.0, fan_deg)) / 8.0)


def _inner_ring(fan_deg: float) -> float:
    """Smallest radius whose sector is still TARGET_FLOOR_MM wide, rounded up."""
    return math.ceil(TARGET_FLOOR_MM / (2.0 * math.sin(math.radians(max(1.0, fan_deg)) / 8.0))
                     * 10.0) / 10.0


def _rings(reach: float, fan_deg: float) -> tuple[list[float], bool]:
    """Four ring radii that fit inside the measured reach.

    Two constraints, both hard: consecutive rings must be at least RING_MIN_GAP_MM
    apart (that is the zone depth), and the innermost ring must already be far enough
    out that one sector is at least TARGET_FLOOR_MM wide along the arc. The flag is
    False when the measured reach cannot satisfy both - which is exactly the result
    that says 16 zones per thumb do not fit this hand."""
    lo = max(RING_MIN_GAP_MM, _inner_ring(fan_deg), 0.22 * reach)
    span = max(0.0, reach - lo)
    fits = span >= 3 * RING_MIN_GAP_MM
    step = span / 3.0
    rings = [round(lo + i * step, 1) for i in range(4)]
    rings[-1] = min(rings[-1], round(reach, 1))     # never past the measured reach
    return rings, fits


def required_reach(fan_deg: float, n_rings: int = 4) -> float:
    """The comfortable reach a thumb needs to host n_rings x 4 sectors of 10 mm+."""
    return _inner_ring(fan_deg) + (n_rings - 1) * RING_MIN_GAP_MM


def _ring_widths(rings: list[float], fan_deg: float) -> tuple[float, float]:
    """(radial gap of the rings, arc width of the innermost ring) in mm."""
    gap = min((rings[i + 1] - rings[i] for i in range(len(rings) - 1)), default=0.0)
    arc = sector_chord(min(rings), fan_deg)
    return gap, arc


# --------------------------------------------------------------------------- #
# one-shot gesture capture: hand on the pad, wiggle for 20 s, everything else is
# automatic. This is the default path; the guided protocol below is the detailed one.
# --------------------------------------------------------------------------- #

# (label, cue, seconds). Total 20 s.
PHASES = [
    ("settle", "HAND RUNTERLEGEN. Rechte Hand flach aufs Pad, Handballen und Ferse "
               "in die Luft, nur Daumen und Zeigefinger auf dem Pad. 3 s.", 3.0),
    ("still", "RUHIG: nichts bewegen. 4 s.", 4.0),
    ("radial", "DAUMEN radial: nach aussen und wieder zurueck, so weit du bequem "
               "willst. 4 s.", 5.0),
    ("fan", "DAUMEN seitlich: hin und her durch den Faecher. 5 s.", 5.0),
    ("index", "ZEIGEFINGER: nach oben strecken und seitlich spreizen, bequem. 6 s.", 6.0),
]
P90, P98 = 90, 98
QUANT = 12.5, 37.5, 62.5, 87.5      # the four sector centres of the fan


def find_pad_node() -> tuple[str, dict]:
    """The event node of the pad's touch surface, with its axis ranges and scale."""
    from evdev import InputDevice, ecodes
    best = None
    for path in sorted(Path("/dev/input").glob("event*")):
        try:
            dev = InputDevice(str(path))
        except OSError:
            continue
        info = {code: a for code, a in dev.capabilities(absinfo=True).get(ecodes.EV_ABS, [])}
        if ABS_MT_POSITION_X not in info or ABS_MT_POSITION_Y not in info:
            dev.close()
            continue
        x, y = info[ABS_MT_POSITION_X], info[ABS_MT_POSITION_Y]
        span = (x.max - x.min) * (y.max - y.min)
        if best is None or span > best[2]:
            best = (str(path), {"x": (x.min, x.max, x.resolution),
                               "y": (y.min, y.max, y.resolution)}, span, dev.name)
        dev.close()
    if best is None:
        raise SystemExit("no touch device found: connect the pad, or use --manual")
    return best[0], best[1], best[3]


class GestureRecorder:
    """MT protocol B reader. Emits (t, slot, x_mm, y_mm) and tracks which contacts are
    live, so the palm can be told apart from a finger by its bounding box."""

    def __init__(self, to_mm):
        self.to_mm = to_mm
        self.slot = 0
        self.live: dict[int, bool] = {}
        self.raw: dict[int, tuple[float, float]] = {}
        self.size: dict[int, float] = {}
        self.res_major = 1.0
        self.stream: list[tuple[float, int, float, float]] = []

    def feed(self, code: int, value: float, t: float) -> None:
        if code == ABS_MT_SLOT:
            self.slot = int(value)
        elif code == ABS_MT_TRACKING_ID:
            if value < 0:
                self.live.pop(self.slot, None)
            else:
                self.live[self.slot] = True
        elif code == ABS_MT_TOUCH_MAJOR and self.slot in self.live:
            self.size[self.slot] = max(self.size.get(self.slot, 0.0), value)
        elif code in (ABS_MT_POSITION_X, ABS_MT_POSITION_Y) and self.slot in self.live:
            x, y = self.raw.get(self.slot, (0.0, 0.0))
            if code == ABS_MT_POSITION_X:
                self.raw[self.slot] = (value, y)
            else:
                self.raw[self.slot] = (x, value)
            mx, my = self.to_mm(*self.raw[self.slot])
            self.stream.append((t, self.slot, mx, my))

    def contacts(self) -> list[int]:
        return sorted(self.live)


def record_gesture(recorder: GestureRecorder, source, total: float = 20.0) -> dict:
    """Cue the phases on screen while recording, and return the phase time windows."""
    windows = {}
    t_start = time.monotonic()
    scale = total / sum(p[2] for p in PHASES)
    for label, cue, secs in PHASES:
        secs = secs * scale
        t0 = time.monotonic() - t_start
        print(f"\n  [{t0:4.1f} s] {cue}")
        deadline = time.monotonic() + secs
        while time.monotonic() < deadline:
            for code, value in source():
                recorder.feed(code, value, time.monotonic() - t_start)
            time.sleep(0.004)
        windows[label] = (t0, time.monotonic() - t_start)
    return windows


def _slot_stats(stream, windows=None) -> dict:
    """Per contact: its point list, how far it travelled in total and per phase, and
    the median position.

    Travel, not bounding box: a thumb that sweeps its whole fan has a huge box while
    being a perfectly good fingertip. What separates a palm from a finger is that the
    palm does not travel."""
    by: dict[int, list] = {}
    for t, slot, x, y in stream:
        by.setdefault(slot, []).append((t, x, y))
    out = {}
    for slot, pts in by.items():
        out[slot] = {
            "points": pts,
            "travel": sum(math.dist((a[1], a[2]), (b[1], b[2]))
                          for a, b in zip(pts, pts[1:])),
            "median": (statistics.median([p[1] for p in pts]),
                       statistics.median([p[2] for p in pts])),
            "phase_travel": {},
        }
        for label, (a, b) in (windows or {}).items():
            win = [q for q in pts if a <= q[0] <= b]
            out[slot]["phase_travel"][label] = sum(
                math.dist((x[1], x[2]), (y[1], y[2])) for x, y in zip(win, win[1:]))
    return out


def _still_median(pts, windows, label="still"):
    """Median position of a contact during the still phase, i.e. where it rests."""
    a, b = windows.get(label, (0.0, 0.0))
    win = [q for q in pts if a <= q[0] <= b]
    if len(win) < 3:
        win = pts
    return (statistics.median([q[1] for q in win]),
            statistics.median([q[2] for q in win]))


def _pct(vals, q):
    v = sorted(vals)
    if not v:
        return 0.0
    k = (len(v) - 1) * q / 100.0
    lo = int(k)
    hi = min(lo + 1, len(v) - 1)
    return v[lo] + (v[hi] - v[lo]) * (k - lo)


def analyse_gesture(stream, windows, pad=(PAD_W, PAD_H)) -> tuple[dict, dict]:
    """A 20 s gesture becomes a hand profile, with every derived number labelled.

    Reach is taken from the movement distribution, not from a comfort question:
    P90 of the radial extent is what the hand actually did for 90 % of the recording,
    P98 is the far tail. That is a proxy for comfortable vs maximum reach, and it is
    labelled as such."""
    stats = _slot_stats(stream, windows)
    present = [sl for sl, d in stats.items() if len(d["points"]) >= 3]
    if not present:
        raise SystemExit("nothing was recorded. Is the pad touched at all?")
    MOVE_MM = 8.0        # below this in a phase, the contact was not being used

    def best(label: str, pool) -> int | None:
        cands = {sl: stats[sl]["phase_travel"].get(label, 0.0) for sl in pool}
        sl, v = max(cands.items(), key=lambda kv: kv[1]) if cands else (None, 0.0)
        return sl if v >= MOVE_MM else None

    # The contact that moves while the thumb is cued IS the thumb. That needs no
    # assumption about which slot a finger landed in, and a resting palm can never
    # win a movement phase.
    thumb_sl = best("radial", present)
    for label in ("fan", "index"):        # slot 0 is falsy in Python, so test for None
        if thumb_sl is None:
            thumb_sl = best(label, present)
    if thumb_sl is None:
        raise SystemExit(
            "no contact moved more than "
            f"{MOVE_MM:.0f} mm during the cued phases. Wiggle the thumb in the first "
            f"two phases. Contacts seen: "
            f"{ {sl: {k: round(v, 1) for k, v in stats[sl]['phase_travel'].items()} for sl in present} }")
    rest_pool = [sl for sl in present if sl != thumb_sl]
    index_sl = best("index", rest_pool)
    dropped = sorted(sl for sl in present if sl not in (thumb_sl, index_sl))
    thumb = stats[thumb_sl]
    index = stats[index_sl] if index_sl is not None else None

    def phase_pts(sl, label):
        a, b = windows.get(label, (0.0, 0.0))
        return [p for p in stats[sl]["points"] if a <= p[0] <= b]

    rad = phase_pts(thumb_sl, "radial") or phase_pts(thumb_sl, "fan")
    fan = phase_pts(thumb_sl, "fan") or rad
    idx = phase_pts(index_sl, "index") if index_sl is not None else []

    # Noise gate, in millimetres of space rather than of path: how far the contact
    # strays while it is supposed to be still, against how far it actually gets during
    # the cued phase. If the cued spread is not clearly above the still spread, the
    # recording contains no measurement and any number from it would be invented.
    SIGNAL_RATIO = 2.0
    still_pts = phase_pts(thumb_sl, "still")
    rest0 = _still_median(stats[thumb_sl]["points"], windows)
    noise = _pct([math.dist((x, y), rest0) for _, x, y in still_pts], P90) if still_pts \
        else 0.0
    signal = max(_pct([math.dist((x, y), rest0) for _, x, y in rad], P90),
                 _pct([math.dist((x, y), rest0) for _, x, y in fan], P90))
    if signal < SIGNAL_RATIO * noise:
        raise SystemExit(
            "DIESE AUFNAHME ENTHAELT KEINE MESSUNG.\n"
            f"  Kontakt {thumb_sl}: {noise:.1f} mm Streuung in der Ruhephase, "
            f"{signal:.1f} mm in den Daumenphasen (Faktor "
            f"{signal / noise if noise else float('inf'):.1f}, nötig wären "
            f"{SIGNAL_RATIO:.0f}).\n"
            f"  Streuung je Kontakt in der Ruhephase: "
            f"{ {sl: round(_pct([math.dist((x, y), rest0) for _, x, y in phase_pts(sl, 'still')], P90), 1) for sl in present} } mm\n"
            "  Entweder lag die Hand mit Ballen auf dem Pad, oder die Aufnahme hat "
            "das Ablegen der Hand mitgemessen. Beides heisst: nur Daumen und "
            "Zeigefinger auflegen, Handballen und Ferse in die Luft. Rohstream: "
            "messung/rom/gesture.jsonl")
    # where the thumb rests is where it sat during the still phase
    rest = _still_median(thumb["points"], windows)

    radii = [math.dist((x, y), rest) for _, x, y in rad] or [0.0]
    comfort, maxr = _pct(radii, P90), max(radii)
    maxr = max(maxr, comfort)
    angles = [math.degrees(math.atan2(y - rest[1], x - rest[0])) % 360 for _, x, y in fan]
    centres = tuple(_pct(angles, q) for q in QUANT) if len(angles) >= 8 else None
    # _sector_bounds works on the outermost two centres; the middle two are the
    # consistency check that the sweep really did cover a fan
    fan_deg = _sector_bounds((centres[0], centres[3])) if centres else (0.0, 100.0)
    even = all(abs((centres[i + 1] - centres[i]) - (centres[3] - centres[2])) < 25.0
               for i in (0, 1)) if centres else True
    # a recorded fan has to look like a fan; otherwise keep the declared one and say so
    fan_ok = MIN_FAN_DEG <= fan_deg[1] - fan_deg[0] <= 180.0 and even
    if not fan_ok:
        fan_deg = (0.0, 100.0)

    def speed(pts, radial):
        if len(pts) < 3:
            return DEFAULT_SPEED_MM_S
        vals = []
        for (t0, x0, y0), (t1, x1, y1) in zip(pts, pts[1:]):
            dt = t1 - t0
            if dt <= 0.005:
                continue
            seg = math.dist((x0, y0), (x1, y1))
            if radial:
                d0 = math.dist((x0, y0), rest)
                d1 = math.dist((x1, y1), rest)
                seg = abs(d1 - d0)
            if seg > 0.4:
                vals.append(seg / dt)
        return statistics.median(vals) if vals else DEFAULT_SPEED_MM_S

    v_rad, v_tan = speed(rad, True), speed(fan, False)
    penalty = min(3.0, max(1.0, v_rad / v_tan if v_tan > 0 else 1.0))

    # the index block is only measured if a second contact moved during its phase
    if index is not None and len(idx) >= 4:
        idx_rest = _still_median(index["points"], windows)
        idx_d = [math.dist((x, y), idx_rest) for _, x, y in idx]
        idx_measured = True
        idx_reach = max(25.0, _pct(idx_d, P90))
        idx_max = max(max(idx_d), idx_reach)
        idx_spread = (_pct([x for _, x, _ in idx], 90)
                      - _pct([x for _, x, _ in idx], 10))
        idx_pitch = max(20.0, min(idx_spread / 2.0, 34.0))
    else:
        # declared fallback, and the profile says so in _values
        idx_measured = False
        idx_rest = (rest[0] + INDEX_OFFSET_X_MM, 6.0)
        idx_reach, idx_max, idx_spread = 85.0, 97.0, 52.0
        idx_pitch = 26.0

    rings, rings_fit = _rings(comfort, fan_deg[1] - fan_deg[0])
    prof = {
        "_measured_by": "rom_capture.py --auto, 20 s gesture recording",
        "_values": {
            "measured": (["thumb.rest", "thumb.rings", "thumb.reach_mm",
                          "thumb.max_reach_mm", "thumb.tangential_penalty"]
                         + (["thumb.fan_deg"] if fan_ok else [])
                         + (["index.rest", "index.centre", "index.pitch",
                             "index.reach_mm", "index.max_reach_mm"] if idx_measured
                            else [])),
            "declared": (["pad_mm", "thumb.joint", "index.joint",
                          "index.tangential_penalty"]
                         + ([] if fan_ok else ["thumb.fan_deg"])
                         + ([] if idx_measured else
                            ["index.rest", "index.centre", "index.pitch",
                             "index.reach_mm", "index.max_reach_mm"])),
            "note": "reach_mm is the P90 of the recorded extent, max_reach_mm the P98 "
                    "tail; neither is a comfort judgement. Anything in _values.declared "
                    "was NOT in this recording.",
        },
        "pad_mm": [pad[0], pad[1]],
        "thumb": {
            "rest": [round(rest[0], 1), round(rest[1], 1)],
            "joint": [round(rest[0], 1), round(rest[1], 1)],
            "rings": rings,
            "fan_deg": [round(fan_deg[0], 1), round(fan_deg[1], 1)],
            "reach_mm": round(comfort, 1),
            "max_reach_mm": round(maxr, 1),
            "tangential_penalty": round(penalty, 2),
        },
        "index": {
            "rest": [round(idx_rest[0], 1), round(idx_rest[1], 1)],
            "joint": [round(idx_rest[0] + 2.0, 1), round(idx_rest[1] - 4.0, 1)],
            "centre": [round(idx_rest[0], 1), round(idx_rest[1] + max(30.0, idx_reach
                                                                   - idx_pitch / 2))],
            "pitch": round(idx_pitch, 1),
            "reach_mm": round(idx_reach, 1),
            "max_reach_mm": round(max(idx_max, idx_reach), 1),
            "tangential_penalty": 1.0,
        },
    }
    diag = {
        "rest_mm": [round(rest[0], 1), round(rest[1], 1)],
        "index_rest_mm": [round(idx_rest[0], 1), round(idx_rest[1], 1)],
        "contact_travel_mm": {str(sl): round(stats[sl]["travel"], 1) for sl in stats},
        "contact_travel_per_phase": {
            str(sl): {k: round(v, 1) for k, v in stats[sl]["phase_travel"].items()}
            for sl in stats},
        "thumb_slot": thumb_sl, "index_slot": index_sl,
        "ignored_contacts": dropped,
        "fan_from_recording": fan_ok,
        "index_measured": idx_measured,
        "comfort_reach_mm": round(comfort, 1),
        "max_reach_mm": round(maxr, 1),
        "comfort_over_max": round(comfort / maxr, 2) if maxr else None,
        "fan_deg": [round(fan_deg[0], 1), round(fan_deg[1], 1)],
        "rings_mm": rings,
        "rings_fit_11mm": rings_fit,
        "rings_needed_mm": round(3 * RING_MIN_GAP_MM, 1),
        "inner_ring_for_fan_mm": _inner_ring(fan_deg[1] - fan_deg[0]),
        "reach_for_4_rings_mm": round(required_reach(fan_deg[1] - fan_deg[0]), 1),
        "reach_for_3_rings_mm": round(required_reach(fan_deg[1] - fan_deg[0], 3), 1),
        "ring_gap_mm": round(_ring_widths(rings, fan_deg[1] - fan_deg[0])[0], 1),
        "inner_arc_mm": round(_ring_widths(rings, fan_deg[1] - fan_deg[0])[1], 1),
        "radial_speed_mm_s": round(v_rad, 1),
        "tangential_speed_mm_s": round(v_tan, 1),
        "tangential_penalty": round(penalty, 2),
        "index_reach_mm": round(idx_reach, 1),
        "index_max_reach_mm": round(max(idx_max, idx_reach), 1),
        "index_spread_mm": round(idx_spread, 1),
        "source": "20 s gesture recording",
        "fan_sectors_even": even,
    }
    return prof, diag


def run_auto(args) -> tuple[dict, dict]:
    from evdev import InputDevice, ecodes
    node, axes, dev_name = find_pad_node()
    (min_x, max_x, res_x) = axes["x"]
    (min_y, max_y, res_y) = axes["y"]
    span_x, span_y = max_x - min_x, max_y - min_y
    if span_x <= 0 or span_y <= 0:
        raise SystemExit(f"{node} reports a degenerate axis range")

    def to_mm(x, y):
        return ((x - min_x) / span_x * PAD_W, (y - min_y) / span_y * PAD_H)

    dev = InputDevice(node)
    print(f"pad: {dev_name} at {node}")
    print(f"     axes {min_x}..{max_x} x {min_y}..{max_y}, reported resolution "
          f"{res_x}/{res_y} per mm, mapped onto {PAD_W:.0f}x{PAD_H:.0f} mm")
    print("\nLeg die rechte Hand flach aufs Pad, Ferse frei. 20 Sekunden wackeln.")
    rec = GestureRecorder(to_mm)
    source = _evdev_source(dev, ecodes)
    windows = record_gesture(rec, source, args.seconds)
    dev.close()
    n = len(rec.stream)
    print(f"\n{n} Positions ueber {len(rec.contacts())} Kontakten aufgenommen.")
    if n < 50:
        raise SystemExit(f"only {n} positions recorded - is the pad actually touched?")
    out = Path("messung/rom")
    out.mkdir(parents=True, exist_ok=True)
    with (out / "gesture.jsonl").open("w", encoding="utf-8") as f:
        for t, slot, x, y in rec.stream:
            f.write(f'{{"t": {t:.3f}, "slot": {slot}, "x": {x:.2f}, "y": {y:.2f}}}\n')
    print(f"raw stream: {out / 'gesture.jsonl'}")
    return analyse_gesture(rec.stream, windows)


# --------------------------------------------------------------------------- #
# capture loops
# --------------------------------------------------------------------------- #

def _press(prompt: str) -> str:
    try:
        return input(prompt).strip().lower()
    except EOFError:
        return ""


def _ask_rating() -> int | None:
    ans = _press(RATING_PROMPT + " ")
    if not ans:
        return None
    try:
        v = int(ans)
    except ValueError:
        return None
    return v if 1 <= v <= 5 else None


def capture_step(tracker: ContactTracker, res: StepResult, seconds: float,
                 source) -> StepResult:
    """Record one cued step from an event source.

    `source()` yields (code, value) absolute-axis events and returns False when it has
    nothing pending. Splitting this out keeps the loop testable without hardware."""
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        events = source()
        if events is None:                      # nothing available right now
            time.sleep(0.005)
            events = ()
        for code, value in events:
            res.contacts.extend(tracker.feed(code, value, time.monotonic()))
        now = time.monotonic()
        for x, y in tracker.live_points():
            res.points.append((x, y, now))
    if res.kind == "rest" and res.points:
        res.points.append((statistics.median([p[0] for p in res.points]),
                           statistics.median([p[1] for p in res.points]), 0.0))
    return res


def _evdev_source(dev, codes):
    import select as _select

    def source():
        r, _, _ = _select.select([dev.fd], [], [], 0.02)
        if not r:
            return ()
        return [(ev.code, float(ev.value)) for ev in dev.read()
                if ev.type == codes.EV_ABS]
    return source


def run_device(args) -> list[StepResult]:
    try:
        from evdev import InputDevice, ecodes
    except ImportError:
        raise SystemExit("python-evdev is not installed; use --manual instead")
    dev = InputDevice(str(args.device))
    print(f"device: {dev.name}")
    source = _evdev_source(dev, ecodes)
    tracker = ContactTracker(lambda x, y: (x, y))   # identity until calibration
    results: list[StepResult] = []
    calib = Calibration()
    t0 = time.monotonic()
    print("\nKeep the heel of your hand OFF the pad. Only the finger under test touches.\n")
    for name, cue, kind in STEPS:
        print(f"\n=== {name} ===\n  {cue}")
        _press("  press Enter when ready ... ")
        res = StepResult(name, kind)
        res.t_start = time.monotonic() - t0
        capture_step(tracker, res, args.seconds, source)
        res.t_end = time.monotonic() - t0
        if kind == "point" and res.points:
            for key, attr in (("calibrate_bl", "bl"), ("calibrate_br", "br"),
                              ("calibrate_tl", "tl")):
                if name == key:
                    setattr(calib, attr, res.points[-1][:2])
            if all((calib.bl, calib.br, calib.tl)):
                tracker.to_mm = calib.fit()
                print(f"  calibrated: {tracker.to_mm(0, 0)} .. "
                      f"{tracker.to_mm(1, 1)} (raw units)")
        res.rating = _ask_rating()
        results.append(res)
    dev.close()
    return results


def _ask_numbers(prompt: str, defaults: list[float], n: int) -> list[float]:
    """One prompt, n numbers separated by spaces or commas, defaults on Enter."""
    while True:
        raw = _press(f"{prompt} [{' '.join(f'{d:g}' for d in defaults)}] ")
        if not raw:
            return list(defaults)
        parts = [p for p in raw.replace(",", " ").split() if p]
        if len(parts) == n:
            try:
                return [float(x) for x in parts]
            except ValueError:
                pass
        print(f"  bitte {n} Zahlen, z.B. {' '.join(f'{d:g}' for d in defaults)}")


def run_manual(args) -> tuple[list[StepResult], dict, dict]:
    """No device: five questions, then the same profile the device run produces."""
    print(__doc__.strip().splitlines()[0])
    print("Leg die rechte Hand flach aufs Pad, Ferse frei, Daumen entspannt.\n")
    rest = _ask_numbers("1) Daumen-Ruhelage  x y   (mm vom linken / unteren Rand):",
                        [128.0, 9.0], 2)
    comfort, maxr = _ask_numbers(
        "2) Daumenreichweite  komfortabel maximal   (mm ab der Ruhelage):",
        [58.0, 64.0], 2)
    if maxr < comfort:
        maxr = comfort
    fan0, fan1 = _ask_numbers(
        "3) Fächer  von bis   (Grad, 0 = zum rechten Rand, 90 = nach oben):",
        [0.0, 100.0], 2)
    idx = _ask_numbers(
        "4) Zeigefinger  komfortabel maximal spreizung   (mm):",
        [88.0, 100.0, 52.0], 3)
    pen = _press("5) Seitlicher Sweep: 1 = so schnell wie radial, 2 = schwerer, "
                 "3 = viel schwerer  [2] ") or "2"
    print()
    rest_pt = (rest[0], rest[1])
    results = []
    mk = StepResult("rest", "rest")
    mk.points = [(rest_pt[0], rest_pt[1], 0.0)]
    mk.rating = _ask_rating()
    results.append(mk)
    for name, val in (("comfort_radial", comfort), ("max_radial", maxr)):
        r = StepResult(name, "sweep")
        r.contacts = [Contact(rest_pt[0] + val * math.cos(math.radians(45)),
                               rest_pt[1] + val * math.sin(math.radians(45)),
                               0.6, 2 * val, 4.0, True)]
        r.points = [(c.x, c.y, 0.0) for c in r.contacts]
        results.append(r)
    # the fan sweep is synthesised at the four sector centres the builder will use
    for name, val in (("comfort_fan", comfort), ("max_fan", maxr)):
        r = StepResult(name, "sweep")
        for k in range(4):
            deg = fan0 + (k + 0.5) * (fan1 - fan0) / 4.0
            rad = math.radians(deg)
            r.contacts.append(Contact(rest_pt[0] + val * math.cos(rad),
                                      rest_pt[1] + val * math.sin(rad),
                                      1.0, 2.0 * val * (fan1 - fan0) / 180.0, 4.0, True))
        r.points = [(c.x, c.y, 0.0) for c in r.contacts]
        results.append(r)
    for name, val, y0 in (("index_reach", idx[0], 6.0), ("index_max", idx[1], 6.0),
                          ("index_spread", idx[2], 40.0)):
        r = StepResult(name, "sweep")
        p = (rest_pt[0] + INDEX_OFFSET_X_MM, y0 + (0.0 if name != "index_spread" else 34.0))
        if name == "index_reach":
            p = (p[0], 6.0 + idx[0])
        r.points = [(p[0], p[1], 0.0)]
        r.contacts = [Contact(p[0], p[1], 0.6, 2 * val, 4.0, True)]
        results.append(r)
    for name in ("spokes", "cross_centre", "hold"):
        results.append(StepResult(name, name))
    prof, diag = analyse(results)
    prof["thumb"]["tangential_penalty"] = {"1": 1.0, "2": 1.35, "3": 1.8}.get(pen, 1.35)
    diag["tangential_penalty"] = prof["thumb"]["tangential_penalty"]
    diag["source"] = "manual entry (no device)"
    return results, prof, diag


# --------------------------------------------------------------------------- #
# sheet
# --------------------------------------------------------------------------- #

def write_sheet(path: Path) -> None:
    """A printable, measurable overlay of the pad: 10 mm grid, corner labels."""
    cells = []
    for gy in range(int(PAD_H // 10)):
        row = []
        for gx in range(int(PAD_W // 10)):
            row.append(f'<rect x="{gx * 10}" y="{(PAD_H - (gy + 1) * 10)}" width="10" '
                       f'height="10" fill="none" stroke="#ccc" stroke-width="0.3"/>')
        cells.append("".join(row))
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{PAD_W}mm" height="{PAD_H}mm"
     viewBox="0 0 {PAD_W} {PAD_H}">
  <rect width="{PAD_W}" height="{PAD_H}" fill="white" stroke="black"/>
  {''.join(cells)}
  <line x1="{PAD_W / 2}" y1="0" x2="{PAD_W / 2}" y2="{PAD_H}" stroke="#e00"
        stroke-dasharray="4 3" stroke-width="0.5"/>
  <text x="2" y="{PAD_H - 3}" font-size="6">0,0 bottom-left</text>
  <text x="{PAD_W - 40}" y="{PAD_H - 3}" font-size="6">{PAD_W:.0f},0 bottom-right</text>
  <text x="2" y="8" font-size="6">0,{PAD_H:.0f} top-left</text>
  <text x="{PAD_W / 2 - 20}" y="{PAD_H / 2 + 3}" font-size="5" fill="#e00">centre line</text>
</svg>
"""
    path.write_text(svg, encoding="utf-8")
    print(f"wrote {path} - print it, lay it on the pad, and measure your hand on it")


# --------------------------------------------------------------------------- #
# report
# --------------------------------------------------------------------------- #

def print_diag(diag: dict) -> None:
    print("\n" + "=" * 66)
    print("RANGE OF MOTION - measured")
    print("=" * 66)
    print(f"rest          {diag['rest_mm']} mm")
    print(f"reach         comfortable {diag['comfort_reach_mm']} mm, "
          f"maximum {diag['max_reach_mm']} mm  "
          f"(comfort/max {diag['comfort_over_max']})")
    print(f"fan           {diag['fan_deg'][0]:.0f}..{diag['fan_deg'][1]:.0f} deg"
          f"{'' if diag.get('fan_from_recording', True) else ' (DECLARED, not in the recording)'}, "
          f"rings {'/'.join(f'{r:g}' for r in diag['rings_mm'])} mm "
          f"(gap {diag['ring_gap_mm']:g} mm, inner sector {diag['inner_arc_mm']:g} mm)")
    if not diag["rings_fit_11mm"]:
        print(f"  FINDING: 16 thumb zones do not fit this hand's comfortable reach.")
        print(f"           a {diag['fan_deg'][0]:.0f}..{diag['fan_deg'][1]:.0f} deg fan with "
              f"four 10 mm sectors needs the innermost ring at "
              f"{TARGET_FLOOR_MM / math.radians(max(1.0, diag['fan_deg'][1] - diag['fan_deg'][0])) / 4:.1f} mm "
              f"and {diag['rings_needed_mm']:g} mm of ring depth, i.e. a comfortable reach "
              f"of {diag['reach_for_4_rings_mm']:g} mm.")
        print(f"           measured: {diag['comfort_reach_mm']:g} mm. Three rings instead of "
              f"four need {diag['reach_for_3_rings_mm']:g} mm, i.e. 12 zones per thumb "
              f"(32 zones total, which is fewer than the 39 English phonemes).")
    if diag.get("source", "device") == "device":
        print(f"speed         radial {diag['radial_speed_mm_s']} mm/s, "
              f"tangential {diag['tangential_speed_mm_s']} mm/s -> "
              f"penalty {diag['tangential_penalty']}x")
    else:
        print(f"speed         not measured ({diag['source']}); "
              f"tangential penalty {diag['tangential_penalty']}x from your own answer")
    print(f"index         comfortable {diag['index_reach_mm']} mm, "
          f"maximum {diag['index_max_reach_mm']} mm"
          f"{'' if diag.get('index_measured', True) else ' (DECLARED, not in the recording)'}")
    print(f"contacts      travel per slot {diag['contact_travel_mm']}, "
          f"thumb=slot {diag['thumb_slot']}, index=slot {diag['index_slot']}, "
          f"ignored={diag['ignored_contacts']}")
    if diag.get("ratings"):
        print(f"ratings       {diag['ratings']}")
    print("=" * 66)


# --------------------------------------------------------------------------- #
# self test with synthetic events
# --------------------------------------------------------------------------- #

def self_test() -> int:
    fails = []

    def check(name, ok, detail=""):
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}{(' - ' + detail) if detail else ''}")
        if not ok:
            fails.append(name)

    tr = ContactTracker(lambda x, y: (x, y))
    seq = [(ABS_MT_SLOT, 0, 0.0), (ABS_MT_TRACKING_ID, 1, 0.0), (ABS_MT_POSITION_X, 100.0, 0.0),
           (ABS_MT_POSITION_Y, 200.0, 0.0), (ABS_MT_POSITION_X, 120.0, 0.1),
           (ABS_MT_TRACKING_ID, -1, 0.2)]
    out = []
    for code, val, t in seq:
        out += tr.feed(code, val, t)
    check("contact closes on TRACKING_ID -1", len(out) == 1, f"n={len(out)}")
    check("contact carries the last position", out and (out[0].x, out[0].y) == (120.0, 200.0))
    live = ContactTracker(lambda x, y: (x, y))
    live.feed(ABS_MT_SLOT, 0, 0.0)
    live.feed(ABS_MT_TRACKING_ID, 1, 0.0)
    live.feed(ABS_MT_POSITION_X, 5.0, 0.0)
    live.feed(ABS_MT_POSITION_Y, 6.0, 0.0)
    check("live point is visible while the contact is down", live.live_points() == [(5.0, 6.0)])

    calib = Calibration()
    calib.bl, calib.br, calib.tl = (0.0, 0.0), (1000.0, 0.0), (0.0, 500.0)
    f = calib.fit()
    check("calibration maps raw corners to pad corners",
          all(math.dist(f(*p), q) < 1e-6
              for p, q in (((0.0, 0.0), (0.0, 0.0)), ((1000.0, 0.0), (224.0, 0.0)),
                           ((0.0, 500.0), (0.0, 148.0)))))

    results = []
    mk = StepResult("rest", "rest")
    mk.points = [(120.0, 9.0, 0.0)]
    results.append(mk)
    for name, r0, path_len, dur in (("comfort_radial", 40.0, 80.0, 0.8),
                                    ("max_radial", 52.0, 104.0, 0.8)):
        s = StepResult(name, "sweep")
        s.contacts = [Contact(120.0 + r0 * 0.7, 9.0 + r0 * 0.7, dur, path_len, 4.0, True)]
        results.append(s)
    fan = StepResult("comfort_fan", "sweep")
    for deg in (10.0, 30.0, 50.0, 70.0, 90.0, 105.0):
        rad = math.radians(deg)
        fan.contacts.append(Contact(120.0 + 40.0 * math.cos(rad), 9.0 + 40.0 * math.sin(rad),
                                    1.0, 55.0, 4.0, True))
    results.append(fan)
    fr = StepResult("index_reach", "sweep")
    fr.points = [(194.0, 91.0, 0.0)]
    results.append(fr)
    fm = StepResult("index_max", "sweep")
    fm.contacts = [Contact(194.0, 101.0, 0.6, 180.0, 4.0, True)]
    results.append(fm)
    profile, diag = analyse(results)
    check("comfort reach beats max reach in the profile",
          profile["thumb"]["reach_mm"] < diag["max_reach_mm"],
          f"{profile['thumb']['reach_mm']} < {diag['max_reach_mm']}")
    check("rings stay inside the measured reach",
          profile["thumb"]["rings"][-1] <= diag["comfort_reach_mm"] + 1e-6)
    check("rings are 11 mm apart, or the tool says they cannot be",
          all(profile["thumb"]["rings"][i + 1] - profile["thumb"]["rings"][i] >= 11.0 - 1e-6
              for i in range(3)) == diag["rings_fit_11mm"],
          f"fit={diag['rings_fit_11mm']} gap={diag['ring_gap_mm']}")
    check("the innermost ring is already a full target wide",
          diag["inner_arc_mm"] >= TARGET_FLOOR_MM - 1e-6,
          f"inner sector chord {diag['inner_arc_mm']} mm")
    check("max reach is recorded separately from the comfortable reach",
          profile["thumb"]["max_reach_mm"] >= profile["thumb"]["reach_mm"]
          and profile["index"]["max_reach_mm"] >= profile["index"]["reach_mm"],
          f"thumb {profile['thumb']['reach_mm']}/{profile['thumb']['max_reach_mm']} mm")
    check("a slower tangential sweep raises the penalty above 1",
          profile["thumb"]["tangential_penalty"] > 1.0,
          f"{profile['thumb']['tangential_penalty']}")
    check("fan span is recovered from the angles",
          _angular_span([10.0, 20.0, 30.0, 25.0]) == (10.0, 30.0))
    check("index centre is inside the measured reach",
          profile["index"]["centre"][1] <= profile["index"]["reach_mm"])
    check("profile round-trips through json", json.loads(json.dumps(profile)) == profile)
    raw = [[(ABS_MT_TRACKING_ID, 1.0), (ABS_MT_POSITION_X, 100.0),
            (ABS_MT_POSITION_Y, 200.0), (ABS_MT_POSITION_X, 130.0),
            (ABS_MT_POSITION_X, 160.0), (ABS_MT_TRACKING_ID, -1.0)]] * 3
    raw = [e for block in raw for e in block]

    def source():
        chunk, raw[:] = raw[:4], raw[4:]
        return chunk
    tr2 = ContactTracker(lambda x, y: (x, y))
    res = StepResult("synthetic", "sweep")
    capture_step(tr2, res, 0.25, source)
    check("capture loop records contacts and path",
          len(res.contacts) >= 3 and res.contacts[0].path > 1.0,
          f"n={len(res.contacts)} path={res.contacts[0].path if res.contacts else 0:.1f} mm")
    def palm_like(dx: float) -> list:
        t = ContactTracker(lambda x, y: (x, y))
        out = []
        for code, val in ((ABS_MT_SLOT, 0), (ABS_MT_TRACKING_ID, 1.0), (ABS_MT_POSITION_X, 0.0),
                           (ABS_MT_POSITION_Y, 0.0), (ABS_MT_POSITION_X, dx),
                           (ABS_MT_TRACKING_ID, -1.0)):
            out += t.feed(code, val, 0.0)
        return out
    wide = palm_like(80.0)
    narrow = palm_like(6.0)
    check("a wide contact is rejected as a palm, a narrow one is not",
          wide and narrow and wide[0].rejected and not narrow[0].rejected,
          f"wide={wide[0].rejected or 'kept'!r} narrow={narrow[0].rejected or 'kept'!r}")
    check("empty source is survivable", capture_step(
        ContactTracker(lambda x, y: (x, y)), StepResult("quiet", "hold"), 0.05,
        lambda: ()) is not None)
    try:
        from evdev import ecodes
        check("MT codes match the kernel's",
              (ABS_MT_SLOT, ABS_MT_TRACKING_ID, ABS_MT_POSITION_X, ABS_MT_POSITION_Y)
              == (ecodes.ABS_MT_SLOT, ecodes.ABS_MT_TRACKING_ID,
                  ecodes.ABS_MT_POSITION_X, ecodes.ABS_MT_POSITION_Y),
              f"{ABS_MT_SLOT}/{ABS_MT_TRACKING_ID}/{ABS_MT_POSITION_X}/{ABS_MT_POSITION_Y}")
    except ImportError:
        print("  [SKIP] MT codes vs evdev (python-evdev not installed)")

    # synthetic 20 s gestures, built directly as (t, slot, x, y): slot 0 thumb,
    # slot 1 index, slot 2 a palm that sits still on the pad the whole time
    def make_gesture(index_moves: bool = True, thumb_moves: bool = True) -> list:
        out = []
        for k in range(400):
            t = k * 0.05
            out.append((t, 2, 30.0, 75.0))                       # the palm: still
            if t < 4.0:
                rx, ry, ax, ay = 128.0, 9.0, 0.0, 0.0            # thumb at rest
            elif t < 9.0:                                        # thumb radial
                rr = 58.0 * (0.5 + 0.5 * math.sin(t * 1.7))
                rx, ry = 128.0 + rr * math.cos(math.radians(45)), \
                    9.0 + rr * math.sin(math.radians(45))
            elif t < 14.0:                                       # thumb fan sweep
                a = math.radians(10.0 + 80.0 * (0.5 + 0.5 * math.sin(t * 2.0)))
                rx, ry = 128.0 + 40.0 * math.cos(a), 9.0 + 40.0 * math.sin(a)
            else:
                rx, ry = 128.0, 9.0
            out.append((t, 0, rx if thumb_moves else 128.0, ry if thumb_moves else 9.0))
            if t < 4.0 or t < 14.0:
                ix, iy = 194.0, 6.0
            else:                                                # index extends
                ix = 194.0 + 12.0 * math.sin(t * 1.3)
                iy = 6.0 + 80.0 * (0.6 + 0.4 * math.sin(t * 1.1))
            out.append((t, 1, ix if index_moves else 194.0, iy if index_moves else 6.0))
        return out

    w = {"still": (0.0, 4.0), "radial": (4.0, 9.0), "fan": (9.0, 14.0), "index": (14.0, 20.0)}
    prof, dg = analyse_gesture(make_gesture(), w)
    check("synthetic gesture: palm ignored, thumb and index found by phase",
          dg["ignored_contacts"] == [2] and dg["thumb_slot"] == 0 and dg["index_slot"] == 1,
          f"thumb={dg['thumb_slot']} index={dg['index_slot']} "
          f"ignored={dg['ignored_contacts']}")
    check("synthetic gesture: the fan comes from the recording",
          dg["fan_from_recording"] and dg["index_measured"],
          f"fan={dg['fan_deg']} index_measured={dg['index_measured']}")
    check("synthetic gesture: reach is inside the recorded extent",
          40.0 < prof["thumb"]["reach_mm"] <= 58.5, f"{prof['thumb']['reach_mm']} mm")
    check("synthetic gesture: the thumb rest is the still-phase position",
          abs(prof["thumb"]["rest"][1] - 9.0) < 1.0, f"{prof['thumb']['rest']}")
    check("synthetic gesture: the profile feeds the optimiser unchanged",
          _profile_feeds_optimiser(prof) is None)

    # same recording, but only the thumb wiggled: the index must be declared, not guessed
    prof2, dg2 = analyse_gesture(make_gesture(index_moves=False), w)
    check("thumb-only recording: the thumb is measured",
          prof2["thumb"]["reach_mm"] > 20 and dg2["fan_from_recording"],
          f"reach {prof2['thumb']['reach_mm']} mm, fan {prof2['thumb']['fan_deg']}")
    check("thumb-only recording: the index is declared, and labelled as such",
          (not dg2["index_measured"])
          and "index.reach_mm" in prof2["_values"]["declared"]
          and "index.reach_mm" not in prof2["_values"]["measured"])
    check("thumb-only recording: a still contact is never taken for the index",
          dg2["index_slot"] is None, f"index_slot={dg2['index_slot']}")
    check("thumb-only recording: the profile still feeds the optimiser",
          _profile_feeds_optimiser(prof2) is None)

    # a still hand must be refused rather than turned into numbers
    try:
        analyse_gesture([(k * 0.05, sl, 100.0, 50.0)
                         for k in range(400) for sl in (0, 1, 2)], w)
        check("a completely still hand is refused", False, "it produced a profile")
    except SystemExit as exc:
        check("a completely still hand is refused", "moved" in str(exc))
    print(f"  {len(fails)} failure(s)")
    return 1 if fails else 0


def _profile_feeds_optimiser(prof) -> str | None:
    """The profile must be accepted by the optimiser's own loader without changes."""
    import tempfile
    import layout_optimizer
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "p.json"
        path.write_text(json.dumps(prof), encoding="utf-8")
        try:
            layout_optimizer.apply_profile(json.loads(path.read_text()))
        except Exception as exc:                       # noqa: BLE001 - reported as a failure
            return f"{type(exc).__name__}: {exc}"
    return None


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Lies 20 s deine Hand auf dem Pad aus.")
    ap.add_argument("--seconds", type=float, default=20.0)
    ap.add_argument("--profile", type=Path, default=Path("hand_profile.json"))
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args(argv)
    if args.self_test:
        print("self-test:")
        return self_test()
    profile, diag = run_auto(args)
    args.profile.write_text(json.dumps(profile, indent=2), encoding="utf-8")
    print(f"\ngeschrieben: {args.profile}")
    print_diag(diag)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
