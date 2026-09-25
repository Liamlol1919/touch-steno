#!/usr/bin/env python3
"""Kinematik-Messinstrument fuer den PTH-660 (Schritt 1, reine Messung).

Macht das Tablet zum Messgeraet: pro Finger (Tracking-ID) Trajektorie,
Delta, Geschwindigkeit, Drift — aufnehmen (Recorder, JSONL) und auswerten
(analyze). Kein Trigger, kein Filter: nur die Messgrundlage fuer die
spaetere Paradigma-Entscheidung (Loch-Maske vs. Zero-Lift-Vektor).

--record braucht evdev (lazy import wie tools/press_capture.py);
--analyze/--diff sind rein (stdlib, kein Geraet, kein evdev, kein Qt).
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import threading
import time
from pathlib import Path

import raw_schema  # noqa: E402

class Recorder:
    """Writes one versioned raw contact-frame JSONL record per SYN frame.

    v1 records contain ``schema``, ``version``, ``t`` and ``c``. Contact IDs
    are string keys and an empty ``c`` is legal. Legacy unversioned recordings
    remain readable through ``_load``.
    """

    def __init__(self, out_path, force: bool = False):
        self.path = Path(out_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.path.exists() and not force:
            raise FileExistsError(
                f"{self.path} existiert bereits — nur mit force ueberschreibbar")
        self._fh = self.path.open("w", encoding="utf-8")

    def frame(self, t: float,
              contacts: dict[int, tuple[float, float, float]]) -> None:
        c = {str(tid): [float(x), float(y), float(m)]
             for tid, (x, y, m) in contacts.items()}
        self._fh.write(json.dumps(raw_schema.encode_frame(t, c)) + "\n")

    def close(self) -> None:
        if self._fh is None:
            return
        self._fh.flush()
        self._fh.close()
        self._fh = None

    def __enter__(self) -> "Recorder":
        return self

    def __exit__(self, *exc) -> bool:
        self.close()
        return False


def _strip_uninit_leads(payload: list[dict]) -> list[dict]:
    """Fuehrende Reader-Init-Artefakte pro Kontakt verwerfen.

    WacomTouchReader legt neue Kontakte bei TRACKING_ID mit (0,0,0) an und
    meldet 1-2 SYN-Frames Default-Positionen, bevor ABS_MT_POSITION_x/y
    einlaufen (z.B. [0,0,0] -> [0,135.75,0] -> [223.6,135.75,0]). Diese
    Samples wuerden path/peak/drift mit hunderten mm Muell belasten.

    Regel: pro tid alle Samples VOR dem ersten Sample mit beiden
    Koordinaten != 0.0 verwerfen. Hat ein Kontakt nie beide Koordinaten
    gesetzt (Kantenkontakt auf x=0 bzw. y=0), bleibt er vollstaendig.
    """
    first_real: dict[str, int] = {}
    for i, fr in enumerate(payload):
        for tid, (x, y, _m) in fr["c"].items():
            if tid not in first_real and x != 0.0 and y != 0.0:
                first_real[tid] = i
    out = []
    for i, fr in enumerate(payload):
        c = {tid: v for tid, v in fr["c"].items()
             if tid not in first_real or i >= first_real[tid]}
        out.append({"t": fr["t"], "c": c})
    return out


def analyze(payload: list[dict]) -> dict:
    """Auswertung eines Recorder-Payloads (eine JSONL-Zeile = ein Frame).

    Return-Shape (Vertrag fuer CLI + Tests), Kontakt-Keys = tid als String:
      {tid: {n_frames:int, active_s:float, start:[x,y], end:[x,y],
             path_mm:float, drift_mm:float, drift:[dx,dy],
             peak_mm_s:float, mean_mm_s:float},
       "coupling": {a: {b: mm_pro_frame}},
       "coupling_n": {a: n}}

    Fuehrende Reader-Init-Artefakte pro Kontakt werden verworfen
    (siehe _strip_uninit_leads).
    coupling beschreibt Finger-Kopplung OHNE Schwellenwert:
    coupling[a][b] = Mittelwert von |step_b| (mm/Frame) ueber alle
    Frame-Uebergaenge, in denen a die groesste Per-Frame-Bewegung hat
    (Gleichstand: kleinste tid). Uebergaenge ohne Bewegung (max. Schritt 0)
    zaehlen nicht; coupling_n[a] = Anzahl der gezaehlten Uebergaenge.
    War a nie der Mover, gibt es keinen Eintrag fuer a.
    """
    payload = _strip_uninit_leads(payload)
    series: dict[str, list[tuple[float, float, float]]] = {}
    frames: list[dict[str, tuple[float, float]]] = []
    prev: dict[str, tuple[float, float]] = {}
    for fr in payload:
        t = float(fr["t"])
        cur: dict[str, tuple[float, float]] = {}
        for tid, (x, y, _m) in fr["c"].items():
            tid = str(tid)
            cur[tid] = (float(x), float(y))
            # Nur Folge-Frames zaehlen als Schritt/Luecke = neuer Kontaktabschnitt
            if tid in prev:
                step = math.hypot(float(x) - prev[tid][0],
                                  float(y) - prev[tid][1])
                if step:
                    series.setdefault(tid, []).append(
                        (t, float(x), float(y), step))
            else:
                series.setdefault(tid, []).append((t, float(x), float(y), 0.0))
        frames.append(cur)
        prev = cur

    out: dict = {}
    for tid, pts in series.items():
        path = sum(step for *_, step in pts)
        peak = max((step / (t1 - t0) if t1 > t0 else 0.0)
                   for (t0, _x0, _y0, _), (t1, _x1, _y1, step)
                   in zip(pts, pts[1:])) if len(pts) > 1 else 0.0
        t_first, x0, y0, _ = pts[0]
        t_last, x1, y1, _ = pts[-1]
        active = t_last - t_first
        out[tid] = {
            "n_frames": len(pts),
            "active_s": active,
            "start": [x0, y0],
            "end": [x1, y1],
            "path_mm": path,
            "drift_mm": math.hypot(x1 - x0, y1 - y0),
            "drift": [x1 - x0, y1 - y0],
            "peak_mm_s": peak,
            "mean_mm_s": path / active if active > 0 else 0.0,
        }

    sums: dict[str, dict[str, float]] = {}
    counts: dict[str, int] = {}
    for prev, cur in zip(frames, frames[1:]):
        steps = {tid: math.hypot(x - prev[tid][0], y - prev[tid][1])
                 for tid, (x, y) in cur.items() if tid in prev}
        if not steps or max(steps.values()) <= 0:
            continue
        mover = max(sorted(steps), key=steps.__getitem__)
        acc = sums.setdefault(mover, {})
        for tid, step in steps.items():
            acc[tid] = acc.get(tid, 0.0) + step
        counts[mover] = counts.get(mover, 0) + 1

    out["coupling"] = {a: {b: s / counts[a] for b, s in acc.items()}
                       for a, acc in sums.items()}
    out["coupling_n"] = counts
    return out


def _load(path: Path) -> list[dict]:
    payload = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                payload.append(raw_schema.decode_record(json.loads(line)))
    return payload


def _tid_key(tid: str):
    return (0, int(tid)) if tid.isdigit() else (1, 0)


class _Live:
    """Letzter Frame pro tid fuer die Terminal-Tabelle (Thread-safe):
    (x, dx, dy, |v|) gegenueber dem Frame davor; Startwerte 0."""

    def __init__(self):
        self._lock = threading.Lock()
        self._rows: dict = {}

    def update(self, contacts: dict, now: float) -> None:
        with self._lock:
            rows = {}
            for tid, (x, y, _m) in contacts.items():
                old = self._rows.get(tid)
                if old is None:
                    dx = dy = v = 0.0
                else:
                    ox, oy = old[0], old[1]
                    dx, dy = x - ox, y - oy
                    dt = now - old[5]
                    v = math.hypot(dx, dy) / dt if dt > 0 else 0.0
                rows[tid] = (x, y, dx, dy, v, now)
            self._rows = rows

    def snapshot(self) -> dict:
        with self._lock:
            return dict(self._rows)


def _print_live(live: _Live, remaining: float) -> None:
    rows = live.snapshot()
    print(f"--- noch {remaining:4.0f}s ---")
    if not rows:
        print("  (keine Kontakte)")
        return
    print("  rang  tid      x_mm    dx     dy    |v| mm/s")
    order = sorted(rows, key=lambda tid: rows[tid][0])  # X-Rang: links->rechts
    for rank, tid in enumerate(order, 1):
        x, _y, dx, dy, v, _ = rows[tid]
        print(f"  {rank:>4}  {tid:>3}  {x:8.1f}  {dx:+.2f}  {dy:+.2f}  {v:7.2f}")


def _print_analysis(res: dict) -> None:
    tids = sorted((k for k in res if k not in ("coupling", "coupling_n")),
                  key=_tid_key)
    print("Kontakt  frames  aktiv_s   start(mm)        end(mm)          "
          "path_mm  drift_mm  drift(mm)         peak   mean  (mm/s)")
    for tid in tids:
        c = res[tid]
        print(f"{tid:>7}  {c['n_frames']:>6}  {c['active_s']:>7.3f}   "
              f"({c['start'][0]:7.2f},{c['start'][1]:7.2f})  "
              f"({c['end'][0]:7.2f},{c['end'][1]:7.2f})  "
              f"{c['path_mm']:>7.3f}  {c['drift_mm']:>8.3f}  "
              f"({c['drift'][0]:+7.2f},{c['drift'][1]:+7.2f})  "
              f"{c['peak_mm_s']:>6.2f}  {c['mean_mm_s']:>6.2f}")
    coupling = res.get("coupling") or {}
    if coupling:
        bs = sorted({b for acc in coupling.values() for b in acc},
                    key=_tid_key)
        print("\nCoupling (mm/Frame, Mover a -> mitgezogen b):")
        print("  a\\b  n  " + "  ".join(f"{b:>7}" for b in bs))
        for a in sorted(coupling, key=_tid_key):
            acc = coupling[a]
            cells = "  ".join(
                f"{acc[b]:>7.3f}" if b in acc else f"{'-':>7}" for b in bs)
            print(f"  {a:>3}  {res['coupling_n'][a]:>1}  {cells}")


def _print_diff(ra: dict, rb: dict) -> None:
    tids = sorted({k for r in (ra, rb)
                   for k in r if k not in ("coupling", "coupling_n")},
                  key=_tid_key)
    print("Delta B-A (drift_mm / path_mm / peak_mm_s):")
    print("  Kontakt  d_drift_mm  d_path_mm  d_peak_mm_s")
    for tid in tids:
        a, b = ra.get(tid), rb.get(tid)
        if a is None or b is None:
            print(f"  {tid:>7}  nur in {'A' if b is None else 'B'}")
            continue
        print(f"  {tid:>7}  {b['drift_mm'] - a['drift_mm']:>+10.3f}  "
              f"{b['path_mm'] - a['path_mm']:>+9.3f}  "
              f"{b['peak_mm_s'] - a['peak_mm_s']:>+11.3f}")


def _record(args) -> int:
    ROOT = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(ROOT / "src"))
    from wacom_touch import WacomTouchReader  # lazy: --analyze/--diff bleiben rein

    try:
        rec = Recorder(args.out, force=args.force)
    except OSError as exc:
        print(f"FEHLER: {exc}")
        return 1

    live = _Live()

    def on_contacts(contacts):
        now = time.monotonic()
        rec.frame(now, contacts)
        live.update(contacts, now)

    reader = WacomTouchReader(path=args.device, on_contacts=on_contacts)
    try:
        dev = reader.open()
    except SystemExit as exc:
        print(f"FEHLER: {exc}")
        return 1
    print(f"Device: {dev.name} ({reader.path})")
    print(f"Aufnahme laeuft {args.seconds:.0f}s — Finger tippen/bewegen, "
          f"Loslassen beendet einen Kontakt.")
    stop = threading.Event()
    th = threading.Thread(target=reader.run, kwargs={"stop": stop},
                          daemon=True)
    th.start()
    deadline = time.monotonic() + args.seconds
    try:
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            time.sleep(min(1.0, remaining))
            _print_live(live, max(remaining, 0.0))
    except KeyboardInterrupt:
        print("\nAbbruch — Auswertung des bisher Geschriebenen.")
    stop.set()
    th.join(timeout=2.0)   # Reader-Thread zuerst raus, sonst _dev=None-Race
    reader.close()
    rec.close()
    print(f"\nGeschrieben: {rec.path}")
    _print_analysis(analyze(_load(rec.path)))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Kinematik-Messinstrument PTH-660: Trajektorien "
                    "aufnehmen/auswerten (nur Messung, kein Trigger).")
    ap.add_argument("--record", action="store_true",
                    help="Live-Aufnahme ins JSONL (--seconds/--out/--device)")
    ap.add_argument("--analyze", metavar="FILE",
                    help="JSONL auswerten: Per-Finger + Coupling-Tabelle")
    ap.add_argument("--diff", nargs=2, metavar=("A", "B"),
                    help="zwei JSONL vergleichen (Delta B-A pro Finger)")
    ap.add_argument("--seconds", type=float, default=20.0)
    ap.add_argument("--out", default="/tmp/kinematics.jsonl")
    ap.add_argument("--device", default=None)
    ap.add_argument("--force", action="store_true",
                    help="--out duerf eine bestehende Datei ueberschreiben")
    args = ap.parse_args()

    if args.record:
        return _record(args)
    if args.analyze:
        _print_analysis(analyze(_load(Path(args.analyze))))
        return 0
    if args.diff:
        ra, rb = (analyze(_load(Path(p))) for p in args.diff)
        _print_diff(ra, rb)
        return 0
    ap.error("Modus waehlen: --record, --analyze FILE oder --diff A B")


if __name__ == "__main__":
    raise SystemExit(main())
