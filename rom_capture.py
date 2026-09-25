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
import statistics
import sys
import time
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

PAD_W, PAD_H = 224.0, 148.0
GRID_MM = 5.0
FINGER_MAX_SPAN_MM = 30.0        # a contact wider than this is a palm, not a finger
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

    ABS_X, ABS_Y, ABS_MT_ID, ABS_MT_X, ABS_MT_Y = 0, 1, 2, 3, 4
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
        if code in (self.ABS_MT_ID, self.ABS_MT_X, self.ABS_MT_Y):
            self.saw_mt = True
            cur = self.slots.setdefault(0, {"x": 0.0, "y": 0.0, "have_xy": False,
                                            "live": False, "t_down": 0.0, "t_last": 0.0,
                                            "path": 0.0, "minx": None, "miny": None,
                                            "maxx": None, "maxy": None})
            if code == self.ABS_MT_ID:
                if value < 0:
                    if cur["live"]:
                        closed.append(self._finish(cur))
                    cur["live"] = False
                else:
                    cur.update(self._new_slot(t))
            elif cur["live"]:
                if code == self.ABS_MT_X:
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


def run_manual(args) -> list[StepResult]:
    """No device: ask the same questions and synthesise the samples.

    The numbers the operator supplies are the measurement; the derived profile is
    identical in shape to the device run so both feed the optimiser the same way.
    """
    print("Manual mode. Answer with the numbers you measured (see the sheet).")
    rest = (float(_press("Thumb rest position, x mm from the left edge: ") or 128),
            float(_press("Thumb rest position, y mm from the bottom edge: ") or 9))
    comfort = float(_press("Comfortable thumb reach from that point, mm: ") or 50)
    maxr = float(_press("Absolute maximum thumb reach, mm: ") or 55)
    fan0 = float(_press("Fan start angle, deg (0 = towards the right edge, 90 = up): ") or 0)
    fan1 = float(_press("Fan end angle, deg: ") or 112)
    pen = _press("Sideways sweep vs radial extension: same (1) / harder (2) / "
                 "much harder (3): ") or "2"
    idx_reach = float(_press("Comfortable index reach up the pad, mm: ") or 85)
    idx_max = float(_press("Absolute maximum index reach up the pad, mm: ") or 95)
    idx_spread = float(_press("Index sideways spread, mm: ") or 52)
    rating = _ask_rating()
    results = []
    mk = StepResult("rest", "rest")
    mk.points = [(rest[0], rest[1], 0.0)]
    mk.rating = rating
    results.append(mk)
    for name, kind, val in (("comfort_radial", "sweep", comfort), ("max_radial", "sweep", maxr)):
        r = StepResult(name, kind)
        r.contacts = [Contact(rest[0] + val * math.cos(math.radians(45)),
                               rest[1] + val * math.sin(math.radians(45)),
                               0.6, 2 * val, 4.0, True)]
        r.points = [(c.x, c.y, 0.0) for c in r.contacts]
        results.append(r)
    # the fan sweep is synthesised from the operator's own fan angles, so the ring
    # solver sees the fan that will actually be built
    for name, kind, val, dur in (("comfort_fan", "sweep", comfort, 1.0),
                                 ("max_fan", "sweep", maxr, 1.0)):
        r = StepResult(name, kind)
        for k in range(4):
            deg = fan0 + (k + 0.5) * (fan1 - fan0) / 4.0
            rad = math.radians(deg)
            r.contacts.append(Contact(rest[0] + val * math.cos(rad),
                                      rest[1] + val * math.sin(rad),
                                      dur, 2.0 * val * (fan1 - fan0) / 180.0, 4.0, True))
        r.points = [(c.x, c.y, 0.0) for c in r.contacts]
        results.append(r)
    fr = StepResult("index_reach", "sweep")
    fr.points = [(rest[0] + INDEX_OFFSET_X_MM, 6.0 + idx_reach, 0.0)]
    fr.contacts = [Contact(fr.points[0][0], fr.points[0][1], 0.6, 2 * idx_reach, 4.0, True)]
    results.append(fr)
    fm = StepResult("index_max", "sweep")
    fm.contacts = [Contact(rest[0] + INDEX_OFFSET_X_MM, 6.0 + idx_max, 0.6, 2 * idx_max, 4.0, True)]
    results.append(fm)
    fs = StepResult("index_spread", "sweep")
    fs.contacts = [Contact(rest[0] + INDEX_OFFSET_X_MM, 40.0, 0.6, idx_spread, 4.0, True)]
    results.append(fs)
    results.append(StepResult("spokes", "spokes"))
    results.append(StepResult("cross_centre", "sweep"))
    results.append(StepResult("hold", "hold"))
    prof, diag = analyse(results)
    # the operator's own word for the sideways sweep becomes the tangential premium
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
    print(f"fan           {diag['fan_deg'][0]:.0f}..{diag['fan_deg'][1]:.0f} deg, "
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
          f"maximum {diag['index_max_reach_mm']} mm")
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
    seq = [(ContactTracker.ABS_MT_ID, 1, 0.0), (ContactTracker.ABS_MT_X, 100.0, 0.0),
           (ContactTracker.ABS_MT_Y, 200.0, 0.0), (ContactTracker.ABS_MT_X, 120.0, 0.1),
           (ContactTracker.ABS_MT_ID, -1, 0.2)]
    out = []
    for code, val, t in seq:
        out += tr.feed(code, val, t)
    check("contact closes on TRACKING_ID -1", len(out) == 1, f"n={len(out)}")
    check("contact carries the last position", out and (out[0].x, out[0].y) == (120.0, 200.0))
    live = ContactTracker(lambda x, y: (x, y))
    live.feed(ContactTracker.ABS_MT_ID, 1, 0.0)
    live.feed(ContactTracker.ABS_MT_X, 5.0, 0.0)
    live.feed(ContactTracker.ABS_MT_Y, 6.0, 0.0)
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
    raw = [[(ContactTracker.ABS_MT_ID, 1.0), (ContactTracker.ABS_MT_X, 100.0),
            (ContactTracker.ABS_MT_Y, 200.0), (ContactTracker.ABS_MT_X, 130.0),
            (ContactTracker.ABS_MT_X, 160.0), (ContactTracker.ABS_MT_ID, -1.0)]] * 3
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
        for code, val in ((ContactTracker.ABS_MT_ID, 1.0), (ContactTracker.ABS_MT_X, 0.0),
                           (ContactTracker.ABS_MT_Y, 0.0), (ContactTracker.ABS_MT_X, dx),
                           (ContactTracker.ABS_MT_ID, -1.0)):
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
    print(f"  {len(fails)} failure(s)")
    return 1 if fails else 0


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--device", help="/dev/input/eventN of the pad (live capture)")
    ap.add_argument("--manual", action="store_true", help="ask the questions instead")
    ap.add_argument("--seconds", type=float, default=8.0, help="seconds per step")
    ap.add_argument("--out-dir", type=Path, default=Path("messung/rom"))
    ap.add_argument("--sheet", type=Path, help="also write a printable pad overlay here")
    ap.add_argument("--raw", action="store_true", help="device already reports millimetres")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args(argv)

    if args.self_test:
        print("self-test:")
        return self_test()
    if args.sheet:
        write_sheet(args.sheet)
        if not (args.device or args.manual):
            return 0
    if not (args.device or args.manual):
        ap.error("pick --device (live) or --manual (no hardware)")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    if args.manual:
        results, profile, diag = run_manual(args)
    else:
        results = run_device(args)
        profile, diag = analyse(results)
    prof_path = args.out_dir / "hand_profile.json"
    prof_path.write_text(json.dumps(profile, indent=2), encoding="utf-8")
    raw_path = args.out_dir / "rom_steps.json"
    raw_path.write_text(json.dumps([r.to_json() for r in results], indent=2), encoding="utf-8")
    print(f"wrote {prof_path}")
    print(f"wrote {raw_path}")
    if diag:
        print_diag(diag)
    print(f"\nuse it:  python3 layout_optimizer.py --hand-profile {prof_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
