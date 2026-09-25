#!/usr/bin/env python3
"""Render the project's models as figures.

Two of these are measured from a real hand, one is a simulation. They are kept in
separate files and labelled as such on the figure itself, because the difference is
the whole point: the layout figure is still a model, the confusion figure is a
measurement of one person's thumb on one pad.

    python3 scripts/plot_models.py --session ../../session-stand/messung/s12.jsonl \
        --out models

The default job set and ``--only confusion`` require ``--session``. Rendering requires
the optional dependencies in ``requirements-plot.txt``; evaluator/session failures
propagate as a non-zero command status and are not reported as written figures.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
W_MM, H_MM = 224.0, 148.0
SECTORS = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
ANG = {s: i * 45 for i, s in enumerate(SECTORS)}
# Measured on this operator's own hand, 21 s, 9007 samples: resting fingers.
REST_JITTER_MM = 0.4
# Measured bbox of the same hand's natural thumb excursions.
HAND_ENVELOPE = (24.6, 18.2)



def load_plotting():
    """Load the optional plotting stack only when a figure is requested."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle, Wedge
    return plt, Circle, Wedge

def fig_layout(out: Path) -> None:
    """The compass primitive as it is actually drawn on the pad."""
    cx, cy = W_MM / 2, H_MM / 2
    # The compass is ~40 mm on a 224 mm pad: drawn to scale on the full pad it is a
    # dot. Main axes zoom to the working area, inset carries the full-pad context.
    fig, ax = plt.subplots(figsize=(10, 9))
    ax.set_xlim(cx - 46, cx + 46)
    ax.set_ylim(cy - 46, cy + 46)
    ax.set_aspect("equal")
    ax.set_facecolor("#1c1c22")
    fig.patch.set_facecolor("#1c1c22")
    cx, cy = W_MM / 2, H_MM / 2
    colours = plt.cm.tab10(np.linspace(0, 1, 8))

    for r, style, tag in ((12.0, "--", "12 mm  (ergonomic arm)"),
                          (20.0, ":", "20 mm  (accuracy arm)")):
        ax.add_patch(Circle((cx, cy), r, fill=False, ec="#ffd166", ls=style, lw=1.8))
        ax.annotate(tag, xy=(cx - r * .70, cy + r * .70),
                    xytext=(cx - 44, cy + 40 - (12 if r == 12 else 22)),
                    color="#ffd166", fontsize=9.5, ha="left", va="center",
                    arrowprops=dict(arrowstyle="-", color="#ffd166", lw=.8, alpha=.7))

    ew, eh = HAND_ENVELOPE
    ax.add_patch(Rect := plt.Rectangle((cx - ew / 2, cy - eh / 2), ew, eh,
                                      fill=False, ec="#ef476f", lw=2, alpha=.9))
    ax.annotate(f"natural hand envelope {ew} x {eh} mm (MEASURED)",
                xy=(cx - ew / 2, cy - eh / 2), xytext=(cx - 44, cy - 33),
                color="#ef476f", fontsize=9.5, ha="left", va="center",
                arrowprops=dict(arrowstyle="-", color="#ef476f", lw=.8, alpha=.7))

    for i, s in enumerate(SECTORS):
        a = math.radians(ANG[s])
        mid = 30.0
        for r in (12.0, 20.0):
            px, py = cx + r * math.cos(a), cy + r * math.sin(a)
            ax.add_patch(Circle((px, py), 2.2, color=colours[i], ec="w", lw=.8, zorder=5))
        ax.text(cx + mid * math.cos(a), cy + mid * math.sin(a), s,
                color=colours[i], fontsize=11, ha="center", va="center", weight="bold")
        # wedge showing the sector's angular half-width at the 12 mm arm
        w = Wedge((cx, cy), 12.0, ANG[s] - 22.5, ANG[s] + 22.5,
                  color=colours[i], alpha=.18)
        ax.add_patch(w)
    ax.add_patch(Circle((cx, cy), 2.0, color="#eeeeee", zorder=6))

    ax.text(cx, cy + 45, "COMPASS PRIMITIVE - 8 sectors, 224 x 148 mm pad",
            color="w", fontsize=14, ha="center", va="top", weight="bold")
    ax.text(cx, cy - 45,
            f"resting-finger jitter {REST_JITTER_MM} mm (MEASURED)  ->  at 12 mm: "
            f"{12 / REST_JITTER_MM:.0f}:1 signal-to-noise.  The sensor is not the "
            f"error source; the hand is.",
            color="#8d99ae", fontsize=9, ha="center")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.spines["left"].set_color("#3a3a44")
    ax.spines["bottom"].set_color("#3a3a44")
    ax.tick_params(colors="#6b7280", labelsize=8)
    ins = ax.inset_axes([0.70, 0.02, 0.28, 0.24])
    ins.set_xlim(0, W_MM); ins.set_ylim(0, H_MM); ins.set_aspect("equal")
    ins.add_patch(plt.Rectangle((0, 0), W_MM, H_MM, fill=False, ec="#3a3a44", lw=1))
    ins.add_patch(Circle((cx, cy), 46, fill=False, ec="#4cc9f0", lw=1, ls="--"))
    ins.set_facecolor("#1c1c22")
    ins.set_xticks([]); ins.set_yticks([])
    ins.text(W_MM / 2, H_MM - 5, "full pad 224x148", color="#6b7280", fontsize=7,
             ha="center")
    for sp in ins.spines.values():
        sp.set_color("#3a3a44")
    fig.tight_layout()
    fig.savefig(out, dpi=130, facecolor=fig.get_facecolor())
    plt.close(fig)


def fig_confusion(session: Path, out: Path) -> None:
    """The measured confusion matrix. Errors land opposite, not scattered."""
    result = subprocess.run([sys.executable, str(ROOT / "scripts" / "evaluate_session.py"),
                             str(session)], capture_output=True, text=True)
    if result.returncode != 0:
        detail = result.stderr.strip() or f"exit status {result.returncode}"
        raise SystemExit(f"evaluate_session failed: {detail}")
    pairs = re.findall(r"^\s+([NESW]+)->([NESW]+):\s+(\d+)$", result.stdout, re.M)
    if not pairs:
        raise SystemExit("evaluate_session produced no confusion matrix")
    m = {p[0]: {} for p in pairs}
    for a, b, n in pairs:
        m[a][b] = int(n)
    tot = sum(int(p[2]) for p in pairs)
    vmax = max(int(p[2]) for p in pairs)
    cell = np.full((8, 8), np.nan)
    for i, t in enumerate(SECTORS):
        for j, p in enumerate(SECTORS):
            if p in m.get(t, {}):
                cell[i, j] = m[t][p]

    fig, ax = plt.subplots(figsize=(9.5, 8))
    im = ax.imshow(np.nan_to_num(cell, nan=0.0), cmap="magma", vmin=0, vmax=vmax)
    ax.set_xticks(range(8), SECTORS)
    ax.set_yticks(range(8), SECTORS)
    ax.set_xlabel("decoded direction", color="w")
    ax.set_ylabel("requested direction (true)", color="w")
    ax.set_title(f"MEASURED confusion - 63 strokes, one thumb, 12 mm\n"
                 f"accuracy {sum(m[t][t] for t in SECTORS if t in m) / tot:.1%}"
                 f"   |   not a simulation",
                 color="w", fontsize=13, pad=14)
    for i in range(8):
        for j in range(8):
            v = cell[i, j]
            if np.isnan(v):
                continue
            opp = (i + 4) % 8
            if j == opp and v > 0:
                ax.text(j, i, f"{int(v)}\n180°", ha="center", va="center",
                        color="#4cc9f0", fontsize=9, weight="bold")
            else:
                ax.text(j, i, f"{int(v)}", ha="center", va="center",
                        color="w" if v < vmax * .6 else "k")
    cb = fig.colorbar(im, ax=ax, fraction=.046)
    cb.set_label("strokes", color="w")
    cb.ax.yaxis.set_tick_params(color="w", labelsize=8)
    fig.patch.set_facecolor("#1c1c22")
    fig.tight_layout()
    fig.savefig(out, dpi=130, facecolor=fig.get_facecolor())
    plt.close(fig)


def fig_reachability(out: Path) -> None:
    """What the language layer can actually buy: the top-k candidate ceiling."""
    sys.path.insert(0, str(ROOT / "scripts"))
    import random
    import layout_assignment as la  # noqa: E402
    import lm_recovery as lr  # noqa: E402

    words = lr.load_words(lr.DEFAULT_WORDLIST, limit=20000)
    sector_of = {v: k for k, v in lr.SECTOR_LETTER.items()}
    pool = [w for w in words if all(ch in sector_of for ch in w)]
    sigma = la.calibrate_sigma(trials=300, seed=3)
    radii = [12, 15, 20, 30]
    res = {}
    for radius in radii:
        conf = la.build_confusion(600, 5, sigma, radius_mm=radius)

        def sample(ts, rng):
            row = conf[ts]
            tot = sum(row.values()) or 1
            r, acc = rng.random(), 0.0
            for sec, n in row.items():
                acc += n / tot
                if r <= acc:
                    return sec
            return ts

        def top(obs, k):
            col = {t: conf[t][obs] for t in conf if conf[t].get(obs)}
            tot = sum(col.values()) or 1
            cs = sorted(((dict(lr.SECTOR_LETTER)[t], n / tot)
                         for t, n in col.items() if n), key=lambda kv: -kv[1])
            return [c for c, _ in cs[:k]]

        by_first: dict[str, list[str]] = {}
        for w in pool:
            by_first.setdefault(w[0], []).append(w)
        rng = random.Random(4)
        hit = {1: 0, 2: 0, 3: 0, 4: 0}
        geo = n = 0
        for _ in range(400):
            w = rng.choice(pool)
            n += 1
            obs = [sample(sector_of[ch], rng) for ch in w]
            geo += all(dict(lr.SECTOR_LETTER)[o] == c for o, c in zip(obs, w))
            for k in hit:
                if any(len(c) == len(w) and all(c[i] in top(obs[i], k)
                                               for i in range(len(w)))
                       for c in by_first.get(w[0], [])):
                    hit[k] += 1
        res[radius] = (geo / n, {k: v / n for k, v in hit.items()}, n)

    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor("#1c1c22")
    ax.set_facecolor("#1c1c22")
    for k, col in ((1, "#ef476f"), (2, "#ffd166"), (3, "#06d6a0"), (4, "#4cc9f0")):
        ys = [res[r][1][k] for r in radii]
        ax.plot(radii, ys, "o-", color=col, lw=2.5, label=f"top-{k} candidates")
    ys = [res[r][0] for r in radii]
    ax.plot(radii, ys, "s--", color="white", lw=1.8, label="top-1 as decoded now")
    ax.fill_between(radii, [res[r][0] for r in radii], [res[r][1][3] for r in radii],
                    color="#06d6a0", alpha=.10)
    ax.annotate("the gap the language layer\nwould have to close",
                xy=(12, res[12][1][3]), xytext=(13.4, .45),
                color="#06d6a0", fontsize=10,
                arrowprops=dict(arrowstyle="->", color="#06d6a0"))
    ax.set_xlabel("thumb excursion radius (mm)", color="w")
    ax.set_ylabel("word recovered from a 20k lexicon", color="w")
    ax.set_title("DECODER CEILING - simulated channel, measured 12 mm arm\n"
                 "the correct symbol is in the top-3 96.8% of the time, "
                 "but greedy character models recover none of it",
                 color="w", fontsize=12)
    ax.legend(facecolor="#2a2a33", edgecolor="#3a3a44", labelcolor="w")
    ax.grid(color="#3a3a44", alpha=.5)
    ax.tick_params(colors="#9ca3af")
    for s in ax.spines.values():
        s.set_color("#3a3a44")
    fig.tight_layout()
    fig.savefig(out, dpi=130, facecolor=fig.get_facecolor())
    plt.close(fig)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--session", type=Path, help="measured s12.jsonl")
    ap.add_argument("--out", type=Path, default=ROOT / "models")
    ap.add_argument("--only", choices=["layout", "confusion", "reach"])
    args = ap.parse_args()
    if args.session is None and args.only not in {"layout", "reach"}:
        ap.error("--session is required for the confusion figure or the default job set")
    global np, plt, Circle, Wedge
    try:
        import numpy as np
        plt, Circle, Wedge = load_plotting()
    except ModuleNotFoundError as exc:
        ap.error("plot_models.py requires the optional dependencies; "
                 "install requirements-plot.txt")
    args.out.mkdir(parents=True, exist_ok=True)
    jobs = {
        "layout": lambda: fig_layout(args.out / "01_kompass_primitiv.png"),
        "confusion": lambda: fig_confusion(args.session, args.out / "02_confusion_gemessen.png"),
        "reach": lambda: fig_reachability(args.out / "03_decoder_decke.png"),
    }
    for name, fn in jobs.items():
        if args.only and args.only != name:
            continue
        fn()
        print(f"geschrieben: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
