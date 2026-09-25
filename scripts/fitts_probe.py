#!/usr/bin/env python3
"""Fit the Fitts coefficients a and b for this thumb on this pad. AIMING ONLY.

Every rate table in this project used `a = 0.150 s` and `b = 0.120 s/bit`. Those are
planning values, not measurements. This script is the instrument that replaces them,
or refuses to.

WHAT THIS MEASURES, PRECISELY. One thing: the time a thumb takes to move from one
small target to another small target after a visual cue, where both targets sit
inside the measured natural thumb envelope of 24.6 x 18.2 mm. Fitts' law
MT = a + b*ID with ID = log2(1 + D/W) prices AIMING at a target. It does not price
drawing a curved path, tracing a loop, or any primitive whose event is a drawn form
rather than a target hit. A retracted claim in this project used Fitts to argue that
5.7 events/s is unreachable; the retraction was right, and the instrument below is
the aiming half of that argument only. Do not use a, or b, or any rate printed here to
bound a drawn-path concept.

STATUS: THIS INSTRUMENT HAS NEVER BEEN RUN ON HARDWARE. No Fitts coefficient for
this hand exists. The task, the grid, the onset rule, the settle rule and the fit are
implemented and unit-tested against synthetic data; the numbers are not. Until a real
session is captured and fitted, `a = 0.150` / `b = 0.120` remain assumptions, and
every rate derived from them in this repository inherits that status.

THE TASK. A 6 x 4 = 24-cell target array with cell centres 4.0 mm apart, the same
geometry as the FCPT concept, laid out centred on the origin. Cell pitch 4.0 mm with a
3.0 mm target width spans 23.0 x 15.0 mm including the outer target edges, which fits
inside the 24.6 x 18.2 mm envelope. The operator is cued one cell at a time; the order
is randomised and seeded, never shown in advance; a short practice set runs first and
is flagged `practice` in the manifest and excluded from the fit. Movement time is
measured from movement onset to settle inside the cued target, so the reaction time
that follows the cue is outside the measured window by construction.

Usage
-----
Capture (needs the tablet, the reader checkout, and roughly ten minutes):

    python3 scripts/fitts_probe.py --mode capture --trials 60 --practice 4 \
        --out messung/fitts_2026-09-25.jsonl

Analyse (no device, no reader, no hardware of any kind):

    python3 scripts/fitts_probe.py --mode analyse --in messung/fitts_2026-09-25.jsonl
    python3 scripts/fitts_probe.py --mode analyse --in messung/fitts.jsonl \
        --json messung/fitts_summary.json

Analyse refuses to print a fit from fewer than 20 usable trials. It reports the
residual sum of squares and every residual, because a bad fit is information about
this hand and this pad, not noise to be hidden behind an R^2.

The rate table is printed separately from the fit, is derived from the fitted
coefficients, and is never a measured typing rate. The 176 ms processing delay is
shown as its own column because every published figure in this project conflated the
movement time with the processing time.
"""
from __future__ import annotations

import argparse
import json
import math
import random
import statistics
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CANDIDATE_SRC = [ROOT / "src", ROOT.parent / "commindv2" / "src", ROOT.parent / "commind" / "src"]

SCHEMA = "touchsteno.fitts_probe"

# --- task geometry -------------------------------------------------------------
# 6 x 4 cells, centres 4.0 mm apart, inside the measured natural thumb envelope.
GRID_COLS = 6
GRID_ROWS = 4
CELL_PITCH_MM = 4.0
TARGET_WIDTH_MM = 3.0
ENVELOPE_MM = (24.6, 18.2)          # measured thumb bbox, COMPASS_SURFACE.md

# --- temporal rule -------------------------------------------------------------
ONSET_MM = 0.8                      # deviation from the pre-cue rest position
SETTLE_RADIUS_MM = TARGET_WIDTH_MM / 2.0
SETTLE_HOLD_S = 0.12                # contact must stay inside this long
REACTION_S = 0.35                   # cue -> earliest legal movement
DEFAULT_SETTLE_WINDOW_S = 0.8       # rest on the previous target before the cue
DEFAULT_TRIAL_TIMEOUT_S = 4.0

# --- analysis policy -----------------------------------------------------------
MIN_TRIALS = 20                     # below this, no fit is reported
PROCESSING_DELAY_S = 0.176          # 88 ms detection + 88 ms segmentation
PLANNING_A_S = 0.150                # planning value, NOT a measurement
PLANNING_B_S_PER_BIT = 0.120        # planning value, NOT a measurement


# ------------------------------------------------------------------ grid -------
def grid_targets(cols: int = GRID_COLS, rows: int = GRID_ROWS,
                 pitch: float = CELL_PITCH_MM, width: float = TARGET_WIDTH_MM) -> list[dict]:
    """Return the 24 cued cells, centred on the origin, row 0 at the top.

    Each entry: label, x_mm, y_mm, w_mm (target width), col, row.
    """
    out = []
    for row in range(rows):
        for col in range(cols):
            out.append({
                "label": f"{chr(ord('A') + col)}{row + 1}",
                "x_mm": (col - (cols - 1) / 2.0) * pitch,
                "y_mm": (row - (rows - 1) / 2.0) * pitch,
                "w_mm": width,
                "col": col,
                "row": row,
            })
    return out


def grid_extent(cols: int = GRID_COLS, rows: int = GRID_ROWS,
                pitch: float = CELL_PITCH_MM, width: float = TARGET_WIDTH_MM) -> tuple[float, float]:
    """Total span in mm including the outer target edges: centre span + one width."""
    return ((cols - 1) * pitch + width, (rows - 1) * pitch + width)


def grid_fits_envelope(cols: int = GRID_COLS, rows: int = GRID_ROWS,
                       pitch: float = CELL_PITCH_MM, width: float = TARGET_WIDTH_MM,
                       envelope: tuple[float, float] = ENVELOPE_MM) -> bool:
    span_x, span_y = grid_extent(cols, rows, pitch, width)
    return span_x <= envelope[0] and span_y <= envelope[1]


# ------------------------------------------------------------------ maths ------
def distance(a: dict, b: dict) -> float:
    """Euclidean centre-to-centre distance in mm between two grid cells."""
    return math.hypot(a["x_mm"] - b["x_mm"], a["y_mm"] - b["y_mm"])


def fitts_id(d_mm: float, w_mm: float) -> float:
    """Shannon form ID = log2(1 + D/W). D in mm, W the target width in mm."""
    if w_mm <= 0:
        raise ValueError("target width must be positive")
    if d_mm < 0:
        raise ValueError("distance must be non-negative")
    return math.log2(1.0 + d_mm / w_mm)


def ols(xs: list[float], ys: list[float]) -> dict:
    """Ordinary least squares fit of ys on xs with a free intercept.

    Returns the intercept, the slope, both standard errors, R^2, the residual sum
    of squares and the residuals themselves. The standard errors use the usual
    sigma^2 = RSS / (n - 2) estimate, so they need n > 2 to be defined.
    """
    n = len(xs)
    if n != len(ys):
        raise ValueError("xs and ys must have the same length")
    if n < 3:
        raise ValueError("ols needs at least 3 points")
    mx = statistics.fmean(xs)
    my = statistics.fmean(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx <= 0:
        raise ValueError("all x are identical; the slope is unidentifiable")
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    slope = sxy / sxx
    intercept = my - slope * mx
    residuals = [y - (intercept + slope * x) for x, y in zip(xs, ys)]
    rss = sum(r * r for r in residuals)
    sst = sum((y - my) ** 2 for y in ys)
    sigma2 = rss / (n - 2)
    se_slope = math.sqrt(sigma2 / sxx)
    se_intercept = math.sqrt(sigma2 * (1.0 / n + mx * mx / sxx))
    return {
        "n": n,
        "intercept": intercept,
        "slope": slope,
        "se_intercept": se_intercept,
        "se_slope": se_slope,
        "r_squared": (1.0 - rss / sst) if sst > 0 else None,
        "rss": rss,
        "residuals": residuals,
        "sigma": math.sqrt(sigma2),
    }


def fit_fitts(trials: list[dict], min_trials: int = MIN_TRIALS) -> dict:
    """Fit MT = a + b*ID over usable trials, or refuse with the reason.

    Excluded trials are counted and named, never silently dropped. A fit below
    `min_trials` usable trials is refused: the caller prints the refusal instead of
    a number derived from almost nothing.
    """
    usable, excluded = _usable(trials)
    res: dict = {
        "trials_total": len(trials),
        "trials_usable": len(usable),
        "trials_excluded": len(excluded),
        "excluded": excluded,
        "min_trials": min_trials,
    }
    if len(usable) < min_trials:
        res["fitted"] = False
        res["refusal"] = (
            f"refusing to report a Fitts fit: {len(usable)} usable trials, "
            f"{min_trials} required. Run a longer session; a coefficient from "
            f"almost nothing is worse than no coefficient."
        )
        return res
    try:
        fit = ols([t["id"] for t in usable], [t["mt_s"] for t in usable])
    except ValueError as exc:
        res["fitted"] = False
        res["refusal"] = f"refusing to report a Fitts fit: {exc}"
        return res
    res["fitted"] = True
    res["a_s"] = fit["intercept"]
    res["se_a_s"] = fit["se_intercept"]
    res["b_s_per_bit"] = fit["slope"]
    res["se_b_s_per_bit"] = fit["se_slope"]
    res["r_squared"] = fit["r_squared"]
    res["rss"] = fit["rss"]
    res["sigma_s"] = fit["sigma"]
    res["residuals"] = [
        {
            "label": t["label"],
            "d_mm": t["d_mm"],
            "id": t["id"],
            "mt_s": t["mt_s"],
            "predicted_s": fit["intercept"] + fit["slope"] * t["id"],
            "residual_s": r,
        }
        for t, r in zip(usable, fit["residuals"])
    ]
    return res


def predicted_rates(a_s: float, b_s: float, w_mm: float = TARGET_WIDTH_MM) -> list[dict]:
    """Rates for the three geometries this project quotes, from fitted a and b.

    These are DERIVED from the fitted coefficients. They are not measured typing
    rates and they say nothing about a drawn-path primitive.
    """
    rows = []
    for name, d in (("adjacent cell (4.0 mm)", CELL_PITCH_MM),
                    ("diagonal neighbour (5.66 mm)", CELL_PITCH_MM * math.sqrt(2.0)),
                    ("farthest corner", math.hypot((GRID_COLS - 1) * CELL_PITCH_MM,
                                                   (GRID_ROWS - 1) * CELL_PITCH_MM))):
        id_bits = fitts_id(d, w_mm)
        mt = a_s + b_s * id_bits
        serialised = mt + PROCESSING_DELAY_S
        rows.append({
            "geometry": name,
            "d_mm": d,
            "w_mm": w_mm,
            "id": id_bits,
            "mt_s": mt,
            "rate_per_s": 1.0 / mt if mt > 0 else None,
            "mt_plus_delay_s": serialised,
            "rate_with_delay_per_s": 1.0 / serialised if serialised > 0 else None,
        })
    return rows


def _usable(trials: list[dict]) -> tuple[list[dict], list[dict]]:
    """Attach D and ID from the previous cued target; split usable from excluded.

    D is measured from the previous CUED TARGET, not from the observed rest
    position, so a sloppy landing does not silently shorten the distance. Practice
    trials are excluded from the fit but still supply the starting target of the
    first measured trial, which is what the thumb physically did.
    """
    usable: list[dict] = []
    excluded: list[dict] = []
    prev = None
    for t in trials:
        label = t.get("label")
        why = None
        if t.get("practice"):
            why = "practice"
        elif t.get("status") != "ok":
            why = f"not a completed target hit: {t.get('status', 'no status')}"
        elif prev is None:
            why = "no previous cued target"
        elif not isinstance(t.get("mt_s"), (int, float)) or t["mt_s"] <= 0:
            why = "no positive movement time"
        w = t.get("w_mm", TARGET_WIDTH_MM)
        if why is None:
            d = distance(prev, t)
            usable.append({**t, "d_mm": d, "w_mm": w, "id": fitts_id(d, w)})
        else:
            excluded.append({"label": label, "reason": why})
        prev = t
    return usable, excluded


# ------------------------------------------------------------------ capture ----
def resolve_reader_src(explicit=None):
    """Locate the checkout holding wacom_touch.py: --src, then src/, then siblings."""
    candidates = [Path(explicit)] if explicit else []
    candidates += CANDIDATE_SRC
    for c in candidates:
        if (c / "wacom_touch.py").is_file():
            return c
    raise SystemExit("wacom_touch.py not found; pass --src <dir> (looked in: "
                     + ", ".join(str(c) for c in candidates) + ")")


def layout_fingerprint() -> str | None:
    """The registered layout digest, or None when it cannot be produced.

    Never a placeholder. A capture run is not aborted over a digest, but a manifest
    that cannot carry one records null instead of zeros.
    """
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    try:
        from nextgen import profile_fingerprint
    except ImportError:
        return None
    digest = profile_fingerprint.layout_fingerprint()
    return digest if isinstance(digest, str) and len(digest) == 64 else None


def target_order(labels: list[str], count: int, seed: int) -> list[str]:
    """A seeded random order with no immediate repeat, so D is never zero by fiat."""
    rng = random.Random(seed)
    seq: list[str] = []
    for _ in range(count):
        prev = seq[-1] if seq else None
        choices = [l for l in labels if l != prev] or list(labels)
        seq.append(rng.choice(choices))
    return seq


class _ContactStream:
    """Collects SYN frames from the reader; the trial loop reads the buffer."""

    def __init__(self):
        self.frames: list[dict] = []
        self.lock = threading.Lock()

    def on_geometry(self, g: dict) -> None:
        with self.lock:
            self.frames.append({"t": time.monotonic(),
                                "c": {str(k): list(v) for k, v in g.items()}})

    def view(self):
        with self.lock:
            return list(self.frames)


def _primary_point(contact: dict, ref: tuple[float, float] | None) -> tuple[float, float] | None:
    """The one contact used as the thumb: nearest to `ref` when several are down."""
    if not contact:
        return None
    pts = [(v[0], v[1]) for v in contact.values() if len(v) >= 2]
    if not pts:
        return None
    if ref is None or len(pts) == 1:
        return pts[0]
    return min(pts, key=lambda p: math.hypot(p[0] - ref[0], p[1] - ref[1]))


def _rest_position(stream: _ContactStream, start_index: int, guard_t: float) -> tuple[float, float]:
    """Median contact position over the pre-cue rest window, for the onset rule."""
    pts = []
    for f in stream.view()[start_index:]:
        if f["t"] >= guard_t:
            break
        p = _primary_point(f["c"], None)
        if p:
            pts.append(p)
    if not pts:
        return (0.0, 0.0)
    return (statistics.median(p[0] for p in pts), statistics.median(p[1] for p in pts))


def _find_onset(points: list[tuple[float, float, float]],
                rest: tuple[float, float], onset_mm: float = ONSET_MM) -> int | None:
    for i, (_, x, y) in enumerate(points):
        if math.hypot(x - rest[0], y - rest[1]) >= onset_mm:
            return i
    return None


def _find_settle(points: list[tuple[float, float, float]], onset: int,
                 target: dict, radius_mm: float = SETTLE_RADIUS_MM,
                 hold_s: float = SETTLE_HOLD_S) -> tuple[int, int] | None:
    """Index of the first sustained arrival inside the target, plus its last index."""
    for i in range(onset, len(points)):
        j = i
        inside = True
        while j < len(points) and points[j][0] - points[i][0] <= hold_s:
            _, x, y = points[j]
            if math.hypot(x - target["x_mm"], y - target["y_mm"]) > radius_mm:
                inside = False
                break
            j += 1
        if inside and points[j - 1][0] - points[i][0] >= hold_s:
            return i, j - 1
    return None


def capture_trial(stream: _ContactStream, start_index: int, target: dict,
                   practice: bool, settle_window_s: float,
                   timeout_s: float) -> tuple[dict, int]:
    """Cue one target, measure the movement, return the trial record and the new index.

    The trial is not completed by the clock: the loop runs until the contact settles
    inside the target, until the operator demonstrably stops moving, or until the
    timeout. Every exit path records a status, and `analyse` refuses to fit a
    status other than "ok".
    """
    # Rest window: the thumb sits on the PREVIOUS target while the cue is prepared.
    time.sleep(settle_window_s)
    print(f"  -> {target['label']}  ({target['x_mm']:+.0f}, {target['y_mm']:+.0f}) mm"
          f"{'   [practice]' if practice else ''}", flush=True)
    cue_t = time.monotonic()
    guard_t = cue_t + REACTION_S
    time.sleep(REACTION_S)

    rest = _rest_position(stream, start_index, guard_t)
    deadline = time.monotonic() + timeout_s
    idx = start_index
    points: list[tuple[float, float, float]] = []
    while True:
        frames = stream.view()
        while idx < len(frames):
            f = frames[idx]
            idx += 1
            if f["t"] < guard_t:
                continue
            p = _primary_point(f["c"], rest)
            if p:
                points.append((f["t"], p[0], p[1]))
        if len(points) >= 2:
            onset_i = _find_onset(points, rest)
            if onset_i is not None:
                settled = _find_settle(points, onset_i, target)
                if settled is not None:
                    arr_i, _hold_i = settled
                    # MT ends at the arrival instant. The hold window only certifies
                    # that the landing was a settle and not a pass-through, so it is
                    # not charged to the movement.
                    rec = {
                        "label": target["label"],
                        "x_mm": target["x_mm"],
                        "y_mm": target["y_mm"],
                        "w_mm": target["w_mm"],
                        "cue_t": cue_t,
                        "start_t": points[onset_i][0],
                        "end_t": points[arr_i][0],
                        "mt_s": points[arr_i][0] - points[onset_i][0],
                        "samples": arr_i - onset_i + 1,
                        "practice": practice,
                        "status": "ok",
                    }
                    return rec, idx
        if time.monotonic() >= deadline:
            break
        time.sleep(0.002)

    if len(points) >= 2 and _find_onset(points, rest) is not None:
        status = "moved but never settled in the cued target"
    elif len(points) >= 2:
        status = "no movement onset before the timeout"
    else:
        status = "no contact samples in the movement window"
    rec = {
        "label": target["label"],
        "x_mm": target["x_mm"],
        "y_mm": target["y_mm"],
        "w_mm": target["w_mm"],
        "cue_t": cue_t,
        "start_t": None,
        "end_t": None,
        "mt_s": None,
        "samples": len(points),
        "practice": practice,
        "status": status,
    }
    return rec, idx


def capture(args) -> list[dict]:
    """Run the cued session on the device and return the manifest lines."""
    sys.path.insert(0, str(resolve_reader_src(args.src)))
    from wacom_touch import WacomTouchReader  # lazy: keeps analyse device-free

    cells = grid_targets()
    by_label = {c["label"]: c for c in cells}
    labels = [c["label"] for c in cells]
    seq = target_order(labels, args.practice + args.trials, args.seed)
    practice_count = args.practice

    print(f"Grid {GRID_COLS} x {GRID_ROWS}, cell centres {CELL_PITCH_MM:.1f} mm apart, "
          f"target width {TARGET_WIDTH_MM:.1f} mm.", flush=True)
    span = grid_extent()
    print(f"Array spans {span[0]:.1f} x {span[1]:.1f} mm including target edges; "
          f"envelope {ENVELOPE_MM[0]} x {ENVELOPE_MM[1]} mm. "
          f"Fits: {grid_fits_envelope()}.", flush=True)
    print(f"{args.practice} practice trials, then {args.trials} measured. "
          f"Order is random and NOT shown in advance. Seed {args.seed}.\n", flush=True)
    print("Rest the thumb on the cued cell. Move only when the cue appears. "
          "Accuracy matters more than speed.\n", flush=True)

    stream = _ContactStream()
    reader = WacomTouchReader(path=args.device, on_geometry=stream.on_geometry)
    try:
        dev = reader.open()
    except (SystemExit, OSError) as exc:
        print(f"ERROR: no usable touch device: {exc}")
        print("Pass --device /dev/input/eventN, or check that the Wacom finger "
              "device is attached.")
        return []
    print(f"Device: {dev.name} ({reader.path})", flush=True)
    stop = threading.Event()
    threading.Thread(target=reader.run, kwargs={"stop": stop}, daemon=True).start()

    header = {
        "record": "header",
        "schema": SCHEMA,
        "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "device": dev.name,
        "device_path": str(reader.path),
        "seed": args.seed,
        "grid": {"cols": GRID_COLS, "rows": GRID_ROWS, "pitch_mm": CELL_PITCH_MM,
                 "target_width_mm": TARGET_WIDTH_MM, "envelope_mm": list(ENVELOPE_MM),
                 "extent_mm": list(span)},
        "onset_mm": ONSET_MM,
        "settle_radius_mm": SETTLE_RADIUS_MM,
        "settle_hold_s": SETTLE_HOLD_S,
        "reaction_s": REACTION_S,
        "settle_window_s": args.settle_window,
        "measures": "aiming time only; not a drawn-path primitive",
        "layout_fingerprint": layout_fingerprint(),
    }
    records = [header]
    index = 0
    try:
        for n, label in enumerate(seq, start=1):
            practice = n <= practice_count
            print(f"[{n}/{len(seq)}]", end=" ", flush=True)
            rec, index = capture_trial(stream, index, by_label[label], practice,
                                       args.settle_window, args.timeout)
            rec["n"] = n
            records.append(rec)
            if args.stream:
                print("    " + json.dumps(rec), flush=True)
        if args.frames:
            args.frames.write_text(
                "".join(json.dumps(f) + "\n" for f in stream.view()), encoding="utf-8")
            print(f"raw frames: {args.frames}")
    finally:
        stop.set()
        time.sleep(0.3)
        reader.close()
    return records


# ------------------------------------------------------------------ manifest ---
def load_manifest(path: Path) -> tuple[dict, list[dict]]:
    header: dict = {}
    trials: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        if rec.get("record") == "header":
            header = rec
        else:
            trials.append(rec)
    return header, trials


def analyse(trials: list[dict], header: dict | None = None,
            min_trials: int = MIN_TRIALS) -> dict:
    """Fit and, when the fit exists, derive the rate table. Device-free."""
    res = fit_fitts(trials, min_trials)
    res["processing_delay_s"] = PROCESSING_DELAY_S
    res["planning_coefficients_s"] = {"a": PLANNING_A_S, "b": PLANNING_B_S_PER_BIT}
    res["planning_rates"] = predicted_rates(PLANNING_A_S, PLANNING_B_S_PER_BIT)
    res["header"] = header
    if res.get("fitted"):
        res["rates"] = predicted_rates(res["a_s"], res["b_s_per_bit"])
    return res


# ------------------------------------------------------------------ report -----
def format_report(res: dict) -> str:
    header = res.get("header") or {}
    lines = ["=" * 70, "FITTS AIMING COEFFICIENTS: THIS THUMB, THIS PAD",
             "=" * 70,
             f"manifest             {res.get('manifest', 'in memory')}",
             f"device               {header.get('device', 'unknown')}",
             f"trials in manifest   {res['trials_total']}",
             f"usable               {res['trials_usable']}",
             f"excluded             {res['trials_excluded']}"]
    for e in res["excluded"]:
        lines.append(f"  excluded {str(e['label']):>5}  {e['reason']}")
    if not res.get("fitted"):
        lines += ["", res["refusal"]]
        return "\n".join(lines)

    lines += [
        f"a (intercept)        {res['a_s']:.4f} s  +/- {res['se_a_s']:.4f} (s.e.)",
        f"b (slope)            {res['b_s_per_bit']:.4f} s/bit  "
        f"+/- {res['se_b_s_per_bit']:.4f} (s.e.)",
        f"R^2                  {res['r_squared']:.4f}",
        f"residual sum of sq   {res['rss']:.6f} s^2",
        f"residual sigma       {res['sigma_s']:.4f} s",
        "",
        "DERIVED from the fitted coefficients above. NOT a measured typing rate,",
        "and not a bound on any drawn-path primitive: this fit prices aiming only.",
        "",
        f"{'geometry':<30}{'D mm':>7}{'ID bit':>8}{'MT s':>8}{'1/MT /s':>9}"
        f"{'MT+176ms':>10}{'1/(MT+d) /s':>12}",
        "-" * 84,
    ]
    for r in res["rates"]:
        lines.append(
            f"{r['geometry']:<30}{r['d_mm']:>7.2f}{r['id']:>8.3f}{r['mt_s']:>8.4f}"
            f"{r['rate_per_s']:>9.2f}{r['mt_plus_delay_s']:>10.4f}"
            f"{r['rate_with_delay_per_s']:>12.2f}")
    lines += ["",
              f"the {PROCESSING_DELAY_S * 1000:.0f} ms processing delay is shown "
              f"separately; a rate only includes it if movement and",
              "processing are serialised. Every published rate in this project "
              "conflated the two.",
              "",
              "RESIDUALS (a bad fit is information about this hand, not noise):",
              f"{'label':>6}{'D mm':>8}{'ID bit':>8}{'MT s':>9}{'fit s':>9}{'resid s':>9}",
              "-" * 49]
    for r in res["residuals"]:
        lines.append(f"{r['label']:>6}{r['d_mm']:>8.2f}{r['id']:>8.3f}{r['mt_s']:>9.4f}"
                     f"{r['predicted_s']:>9.4f}{r['residual_s']:>+9.4f}")
    lines += ["-" * 49, "",
              f"planning values a={PLANNING_A_S} s, b={PLANNING_B_S_PER_BIT} s/bit "
              "(ASSUMPTIONS, not measurements) predict:",
              f"{'geometry':<30}{'MT s':>8}{'1/MT /s':>9}{'1/(MT+d) /s':>12}"]
    for r in res["planning_rates"]:
        lines.append(f"{r['geometry']:<30}{r['mt_s']:>8.4f}{r['rate_per_s']:>9.2f}"
                     f"{r['rate_with_delay_per_s']:>12.2f}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Fit Fitts a and b for this thumb (aiming only).")
    ap.add_argument("--mode", choices=("capture", "analyse"), default="analyse")
    ap.add_argument("--trials", type=int, default=60)
    ap.add_argument("--practice", type=int, default=4)
    ap.add_argument("--seed", type=int, default=20260925)
    ap.add_argument("--device", help="evdev path, e.g. /dev/input/event19")
    ap.add_argument("--src", help="checkout containing wacom_touch.py")
    ap.add_argument("--settle-window", type=float, default=DEFAULT_SETTLE_WINDOW_S)
    ap.add_argument("--timeout", type=float, default=DEFAULT_TRIAL_TIMEOUT_S)
    ap.add_argument("--min-trials", type=int, default=MIN_TRIALS)
    ap.add_argument("--out", type=Path, help="capture: write the manifest JSONL here")
    ap.add_argument("--frames", type=Path, help="capture: also write the raw frame JSONL here")
    ap.add_argument("--stream", action="store_true", help="capture: print each trial as it lands")
    ap.add_argument("--in", dest="inp", type=Path, help="analyse: the manifest JSONL to fit")
    ap.add_argument("--json", type=Path, help="analyse: write the summary JSON here")
    args = ap.parse_args(argv)

    if args.mode == "analyse":
        if not args.inp:
            ap.error("--mode analyse needs --in <manifest.jsonl>")
        header, trials = load_manifest(args.inp)
        res = analyse(trials, header, args.min_trials)
        res["manifest"] = str(args.inp)
        print(format_report(res))
        if args.json:
            args.json.write_text(json.dumps(res, indent=2, default=str), encoding="utf-8")
            print(f"\nsummary: {args.json}")
        return 0

    records = capture(args)
    if not records:
        return 1
    if args.out:
        args.out.write_text("".join(json.dumps(r) + "\n" for r in records), encoding="utf-8")
        print(f"\nmanifest: {args.out}")
        print(f"fit it:   python3 {Path(__file__).name} --mode analyse --in {args.out}")
    else:
        print("\nno --out given, so nothing was written; the session is lost.")
    print("\nThese are aiming times on a cued target task. They are not a typing rate "
          "and they say\nnothing about a drawn-path primitive. The fit is refused "
          f"below {args.min_trials} usable trials.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
