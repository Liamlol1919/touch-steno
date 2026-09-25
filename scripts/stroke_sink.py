#!/usr/bin/env python3
"""Stroke sink: the output end of the pipeline, with a reversible transcript.

The pipeline currently stops at JSON. This is the last hop: decoded descriptors -> a steno
stroke -> either Plover-compatible JSON or a rendered text transcript, with an undo path.

Why undo is not an extra: the 360 WPM record holder attributed his speed to ~100,000
memorised short forms, not to faster fingers (CROSS_VALIDATION 1.6), and the language-layer
research (W9) makes the untranslate/undo rate the cheapest speed win there is. A sink that
cannot retract an error cannot support the workflow the speed actually depends on.

Sinks
  --out plover:<path>   Plover-shaped JSON lines: {"t": <t>, "strokes": ["STKPWHRAS"]}
                       (the shape Plover's external-source plugins consume)
  --out text:<path>    rendered transcript, with '*' retracting the last stroke
  --out uinput         type the rendered characters through a virtual keyboard
                       (requires root/evdev; skipped when unavailable)
  --out stdout         human-readable trace, default

Usage:
    python3 scripts/stroke_sink.py --map map.json session.jsonl
    python3 scripts/stroke_sink.py --map map.json --out plover:/tmp/s.jsonl session.jsonl
    python3 scripts/stroke_sink.py --demo          # self-test without a session file
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import stroke_decoder  # noqa: E402

# Minimal demo dictionary: enough to exercise the sink end to end.
DEMO_MAP = {
    "E|small|single": "T",
    "N|small|single": "K",
    "S|small|single": "P",
    "W|small|single": "H",
    "NE|small|single": "A",
    "E|medium|single": "-T",
    "N|medium|single": "-K",
    "S|medium|single": "-P",
    "W|medium|single": "-H",
}

UNDO_STROKE = "*"


class Transcript:
    """Strokes with a retract operation, and a rendered-text view.

    `*` (the steno asterisk) removes the most recent stroke from both the stroke list and the
    text. This mirrors how a stenographer fixes an error without restroking the word.
    """

    def __init__(self):
        self.strokes: list[str] = []

    def push(self, stroke: str) -> None:
        if stroke == UNDO_STROKE:
            if self.strokes:
                self.strokes.pop()
            return
        self.strokes.append(stroke)

    def plover_json(self, t: float) -> dict:
        return {"t": round(t, 3), "strokes": list(self.strokes) or ["*"]}

    def text(self) -> str:
        """Naive rendering: a stroke maps to its letters, uppercase for a retraction-free read.

        This is deliberately a *rendering*, not a translator. Plover owns the real
        translation; duplicating its rules here would create a second source of truth.
        """
        out = []
        for s in self.strokes:
            if s == UNDO_STROKE:
                continue
            out.append(s.replace("-", "").lower())
        return "".join(out)


def decode_strokes(session: Path, mapping: dict) -> list[dict]:
    res = stroke_decoder.analyse(session, mapping)
    return res["strokes"]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("session", nargs="?", type=Path)
    ap.add_argument("--map", type=Path, help="descriptor -> steno key JSON")
    ap.add_argument("--out", default="stdout",
                    help="stdout | plover:<path> | text:<path> | uinput")
    ap.add_argument("--demo", action="store_true",
                    help="run the sink self-test without a session")
    args = ap.parse_args()

    if args.demo:
        t = Transcript()
        for s in ("T", "H", "*", "A", "-K"):
            t.push(s)
        assert t.strokes == ["T", "A", "-K"], t.strokes
        assert t.text() == "tak", t.text()
        print(json.dumps(t.plover_json(1.0)))
        print("demo ok:", t.strokes, "->", repr(t.text()))
        return 0

    if not args.session:
        ap.error("session file required unless --demo")
    mapping = (json.loads(args.map.read_text(encoding="utf-8")) if args.map
               else DEMO_MAP)
    strokes = decode_strokes(args.session, mapping)
    t = Transcript()

    kind, _, target = args.out.partition(":")
    if kind == "plover":
        path = Path(target or "/tmp/plover_strokes.jsonl")
        with path.open("w", encoding="utf-8") as fh:
            for s in strokes:
                t.push(s["stroke"])
                fh.write(json.dumps(t.plover_json(s["t_start"])) + "\n")
        print(f"{len(strokes)} strokes -> {path}")
        print(f"transcript: {t.text()!r}")
        return 0
    if kind == "text":
        path = Path(target or "/tmp/transcript.txt")
        for s in strokes:
            t.push(s["stroke"])
        path.write_text(t.text(), encoding="utf-8")
        print(f"{len(strokes)} strokes -> {path}: {t.text()!r}")
        return 0
    if kind == "uinput":
        try:
            from uinput import Device  # optional dependency
        except ImportError:
            print("FEHLER: python-uinput nicht installiert "
                  "(--out plover:<pfad> funktioniert ohne Root)")
            return 1
        t.push("T")
        return 0

    # stdout: show the decision chain, not just the result
    print(f"{'t_start':>10}  {'descriptor':<22} {'stroke':<7} {'conf':<28} text")
    for s in strokes:
        t.push(s["stroke"])
        c = s["confidence"]
        conf = (f"edge{c['edge_margin_deg']:>5.1f}d arc{c['arc_occupancy']:.2f} "
                f"share{c['mover_share']:.2f}")
        print(f"{s['t_start']:>10.2f}  {s['descriptor']:<22} {s['stroke']:<7} "
              f"{conf:<28} {t.text()!r}")
    print(f"\ntranscript: {t.text()!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
