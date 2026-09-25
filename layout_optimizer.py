#!/usr/bin/env python3
"""Optimise the phoneme->zone assignment for the 4-finger touch-steno topology.

Topology (40 zones on a 224x148 mm pad, origin bottom-left, y up):

    left thumb   16 zones   polar fan, 4 rings x 4 sectors   (mirrored)
    right thumb  16 zones   polar fan, 4 rings x 4 sectors
    left index    4 zones   2x2 grid
    right index   4 zones   2x2 grid

39 ARPAbet phonemes + 1 SPACE symbol are assigned to those 40 zones.

Objective (all four components normalised against a random-layout reference, so
the weights below are directly interpretable):

    w_phys * normalised time      per-stroke cost + point-to-point movement +
                                  digit/hand switch penalties + return-to-rest
    w_err  * normalised error     corpus-derived confusability x spatial
                                  adjacency (neighbouring zones are confusable)
    w_learn * normalised learn    articulatory proximity x zone distance
                                  (related sounds sit together -> fewer rules)
    w_sym  * (1 - symmetry)       class-wise left/right mirror consistency
                                  (each hand carries the same inventory, learned once)

No measurement from this repository is read or used. Every constant below is a
declared model parameter with a provenance label: Fitts' law coefficients are
the published Shannon-form values, everything else is an explicit modelling
assumption, not a measurement of any person or device.

Usage:
    python3 layout_optimizer.py
    python3 layout_optimizer.py --iters 400000 --restarts 4 --seed 7 --out layout.json
    python3 layout_optimizer.py --self-test
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import random
import re
import sys
import time
import urllib.request
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

# --------------------------------------------------------------------------- #
# corpus sources
# --------------------------------------------------------------------------- #

FREQ_URL = "https://norvig.com/ngrams/count_1w.txt"  # 333 333 words, Google Web 1T counts
CMU_URL = ("https://raw.githubusercontent.com/cmusphinx/cmudict/master/"
           "cmudict.dict")                              # 135 166 ARPAbet pronunciations
CACHE_ENV = "TOUCH_STENO_CACHE"
DEFAULT_CACHE = Path(__file__).resolve().parent / ".cache" / "corpus"
FETCH_TIMEOUT = 120
N_SOURCES = 2
VOWELS = {"AA", "AE", "AH", "AO", "AW", "AY", "EH", "ER", "EY",
          "IH", "IY", "OW", "OY", "UH", "UW"}

# --------------------------------------------------------------------------- #
# phoneme inventory: class, place, manner, voicing, F1/F2 (Hz, adult US averages)
# --------------------------------------------------------------------------- #

PLACE_ORDER = ["bilabial", "labiodental", "interdental", "alveolar",
               "postalveolar", "palatal", "velar", "uvular", "glottal"]
MANNER_ORDER = ["vowel", "glide", "liquid", "nasal", "stop", "affricate", "fricative"]


@dataclass(frozen=True)
class Phoneme:
    symbol: str
    cls: str
    place: str
    manner: str
    voiced: bool
    f1: float
    f2: float
    rounded: bool


def _p(sym, cls, place, manner, voiced, f1=0.0, f2=0.0, rounded=False):
    return Phoneme(sym, cls, place, manner, voiced, f1, f2, rounded)


INVENTORY: dict[str, Phoneme] = {
    # class            symbol  place          manner      voiced   F1     F2
    p.symbol: p for p in [
        _p("P", "LABIAL", "bilabial", "stop", False),
        _p("B", "LABIAL", "bilabial", "stop", True),
        _p("M", "LABIAL", "bilabial", "nasal", True),
        _p("W", "LABIAL", "bilabial", "glide", True),
        _p("F", "LABIODENTAL", "labiodental", "fricative", False),
        _p("V", "LABIODENTAL", "labiodental", "fricative", True),
        _p("TH", "INTERDENTAL", "interdental", "fricative", False),
        _p("DH", "INTERDENTAL", "interdental", "fricative", True),
        _p("T", "ALVEOLAR", "alveolar", "stop", False),
        _p("D", "ALVEOLAR", "alveolar", "stop", True),
        _p("S", "ALVEOLAR", "alveolar", "fricative", False),
        _p("Z", "ALVEOLAR", "alveolar", "fricative", True),
        _p("N", "ALVEOLAR", "alveolar", "nasal", True),
        _p("L", "ALVEOLAR", "alveolar", "liquid", True),
        _p("CH", "POSTALVEOLAR", "postalveolar", "affricate", False),
        _p("JH", "POSTALVEOLAR", "postalveolar", "affricate", True),
        _p("SH", "POSTALVEOLAR", "postalveolar", "fricative", False),
        _p("ZH", "POSTALVEOLAR", "postalveolar", "fricative", True),
        _p("R", "POSTALVEOLAR", "postalveolar", "liquid", True),
        _p("Y", "PALATAL", "palatal", "glide", True),
        _p("K", "VELAR", "velar", "stop", False),
        _p("G", "VELAR", "velar", "stop", True),
        _p("NG", "VELAR", "velar", "nasal", True),
        _p("HH", "GLOTTAL", "glottal", "fricative", False),
        _p("AA", "VOWEL_OPEN", "vowel", "vowel", True, 730, 1090),
        _p("AE", "VOWEL_OPEN", "vowel", "vowel", True, 660, 1720),
        _p("AH", "VOWEL_OPEN", "vowel", "vowel", True, 640, 1190),
        _p("AW", "VOWEL_OPEN", "vowel", "vowel", True, 700, 1200),
        _p("AY", "VOWEL_OPEN", "vowel", "vowel", True, 660, 1900),
        _p("AO", "VOWEL_MID", "vowel", "vowel", True, 570, 840, True),
        _p("EH", "VOWEL_MID", "vowel", "vowel", True, 530, 1840),
        _p("ER", "VOWEL_MID", "vowel", "vowel", True, 490, 1350, True),
        _p("EY", "VOWEL_MID", "vowel", "vowel", True, 450, 2100),
        _p("OW", "VOWEL_MID", "vowel", "vowel", True, 480, 900, True),
        _p("OY", "VOWEL_MID", "vowel", "vowel", True, 570, 860, True),
        _p("IH", "VOWEL_CLOSE", "vowel", "vowel", True, 390, 1990),
        _p("IY", "VOWEL_CLOSE", "vowel", "vowel", True, 270, 2290),
        _p("UH", "VOWEL_CLOSE", "vowel", "vowel", True, 440, 1020, True),
        _p("UW", "VOWEL_CLOSE", "vowel", "vowel", True, 300, 870, True),
    ]
}
PHONEMES: list[str] = sorted(INVENTORY)          # 39, alphabetical (baseline order)
SPACE = "SPACE"
CLASSES: list[str] = sorted({p.cls for p in INVENTORY.values()}) + ["BOUNDARY"]
SPACE_CLASS = "BOUNDARY"


# --------------------------------------------------------------------------- #
# topology
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class Zone:
    zid: str
    digit: str          # lt | rt | li | ri
    x: float            # mm, pad centre of the zone
    y: float
    width: float        # mm, the smaller in-zone extent (effective target width)
    ring: int = -1      # thumb ring index, -1 for index-finger zones
    sector: int = -1
    left_half: bool = False


PAD_W, PAD_H = 224.0, 148.0
# rest position of each digit on the pad; the right side is the model, the left is
# its exact mirror about the pad centre line
ANCHORS = {"rt": (128.0, 9.0), "lt": (96.0, 9.0),
           "ri": (194.0, 6.0), "li": (30.0, 6.0)}
THUMB_RING_R = (21.0, 31.0, 41.0, 51.0)     # 10 mm radial thickness per ring
THUMB_FAN = (0.0, 112.0)       # degrees from +x, counter-clockwise, right thumb
THUMB_SECTORS = 4
INDEX_CENTRE = (194.0, 72.0)   # centre of the 2x2 index-finger block (right hand)
INDEX_PITCH = 28.0
REST_WIDTH_MM = 15.0           # landing width assumed for the return to rest
TARGET_FLOOR_MM = 10.0         # NN/g one-hand thumb floor, for the feasibility report
GEO_TOL_MM = 0.1               # coordinates are stored rounded to 0.01 mm

# --- per-digit kinematic frames ------------------------------------------- #
# A finger does not travel in a straight line between two pads: the thumb
# circumducts (polar motion around the CMC) and the index finger flexes around the
# MCP. Each digit therefore gets its own polar frame, and a same-digit move is
# priced on the path it actually travels, and the tangential part of that path is
# charged at a premium: a thumb sweeps sideways more slowly than it extends
# radially. TANGENTIAL_PENALTY is that premium, and it is the one kinematic constant
# rom_capture.py measures: penalty = (mean radial speed) / (mean tangential speed).
# A value of 1.0 means the digit moves at the same speed in every direction.
# JOINTS are design inputs: the thumb CMC sits at the pad edge, the index MCP on it,
# so the index's reach is measured from the joint, not from the fingertip.
JOINTS = {"rt": (128.0, 9.0), "lt": (96.0, 9.0),      # thumb CMC == its rest position
          "ri": (196.0, 2.0), "li": (28.0, 2.0)}      # index MCP sits at the pad edge
TANGENTIAL_PENALTY = {"rt": 1.35, "lt": 1.35, "ri": 1.15, "li": 1.15}
# Declared MAX reach envelope per digit, checked against every zone. These are
# reach ceilings, not comfort radii: the thumb is inside the published one-hand grip
# max-reach range (51.8-61.4 mm), the index is a flat-palm flexion of ~85 mm.
ENVELOPE_MM = {"rt": 56.0, "lt": 56.0, "ri": 90.0, "li": 90.0}
# measured comfortable reach: the outer ring may not sit further out than this
COMFORT_RING_MM = [THUMB_RING_R[-1]]


def _mirror_x(x: float) -> float:
    return PAD_W - x


def build_topology() -> list[Zone]:
    """40 zones: 4 thumb rings x 4 sectors per thumb, 2x2 per index finger.

    The left half is the exact mirror image of the right half, so every zone has a
    mirror partner and the symmetry term of the objective is well defined."""
    zones: list[Zone] = []
    ring_gap = THUMB_RING_R[1] - THUMB_RING_R[0]
    fan0, fan1 = THUMB_FAN
    dth = math.radians((fan1 - fan0) / THUMB_SECTORS)
    for hand in ("rt", "lt"):
        for ring, r in enumerate(THUMB_RING_R):
            for sec in range(THUMB_SECTORS):
                ang = math.radians(fan0 + (sec + 0.5) * (fan1 - fan0) / THUMB_SECTORS)
                x = ANCHORS["rt"][0] + r * math.cos(ang)
                y = ANCHORS["rt"][1] + r * math.sin(ang)
                if hand == "lt":
                    x = _mirror_x(x)
                s = sec if hand == "rt" else THUMB_SECTORS - 1 - sec
                # the effective target width is the straight-line extent of the
                # sector, i.e. its chord - that is also what separates two neighbours
                zones.append(Zone(f"{hand}_r{ring}_s{s}", hand, round(x, 2), round(y, 2),
                                  round(min(2 * r * math.sin(dth / 2), ring_gap), 2),
                                  ring, s, x < PAD_W / 2))
    for hand in ("ri", "li"):
        cx = INDEX_CENTRE[0] if hand == "ri" else _mirror_x(INDEX_CENTRE[0])
        for row in range(2):
            for col in range(2):
                x = cx + (col - 0.5) * INDEX_PITCH
                y = INDEX_CENTRE[1] + (0.5 - row) * INDEX_PITCH
                zones.append(Zone(f"{hand}_{row}{col}", hand, round(x, 2), round(y, 2),
                                  INDEX_PITCH, -1, -1, x < PAD_W / 2))
    assert len(zones) == 40, len(zones)
    return zones


def mirror_of(zones: list[Zone]) -> list[int]:
    """zone index -> index of its left/right mirror image."""
    inv = {"rt": "lt", "lt": "rt", "ri": "li", "li": "ri"}
    out = []
    for z in zones:
        cand = [i for i, o in enumerate(zones) if o.digit == inv[z.digit]]
        out.append(min(cand, key=lambda i: abs((zones[i].x - _mirror_x(z.x)) ** 2
                                                + (zones[i].y - z.y) ** 2)))
    return out


GEOMETRY_SOURCE = "declared design inputs (no hand profile loaded)"


HAND_PROFILE: dict = {}


def apply_profile(profile: dict) -> dict:
    """Override the declared geometry with measured values.

    The profile describes the RIGHT hand only; the left half is always its exact
    mirror, so the symmetry term of the objective stays well defined. Returns the
    list of fields that were actually overridden, for the report.

    Expected keys (all optional):
        pad_mm          [w, h]
        thumb.rest      [x, y]   rest position of the right thumb tip
        thumb.joint     [x, y]   right thumb CMC
        thumb.rings     [r0..r3] ring radii
        thumb.fan_deg   [a0, a1] circumduction range
        thumb.reach_mm  comfortable reach; the outer ring may not exceed it
        thumb.max_reach_mm  absolute maximum reach, used as the envelope check
        thumb.tangential_penalty  radial speed / tangential speed (1.0 = isotropic)
        index.rest      [x, y]
        index.joint     [x, y]   right index MCP
        index.centre    [x, y]   centre of the 2x2 block
        index.pitch     mm
        index.reach_mm
        index.tangential_penalty
    """
    global PAD_W, PAD_H, THUMB_RING_R, THUMB_FAN, INDEX_CENTRE, INDEX_PITCH
    global ENVELOPE_MM, TANGENTIAL_PENALTY, ANCHORS, JOINTS, GEOMETRY_SOURCE
    global COMFORT_RING_MM
    HAND_PROFILE.update(profile)
    GEOMETRY_SOURCE = "measured hand profile"
    used = []
    if "pad_mm" in profile:
        PAD_W, PAD_H = float(profile["pad_mm"][0]), float(profile["pad_mm"][1])
        used.append("pad_mm")
    th, ix = profile.get("thumb", {}), profile.get("index", {})
    for key, target in (("rest", "anchor"), ("joint", "joint"), ("rings", "rings"),
                        ("fan_deg", "fan"), ("tangential_penalty", "pen")):
        if key not in th:
            continue
        used.append(f"thumb.{key}")
        if target == "anchor":
            ANCHORS["rt"] = tuple(float(v) for v in th[key])
        elif target == "joint":
            JOINTS["rt"] = tuple(float(v) for v in th[key])
        elif target == "rings":
            THUMB_RING_R = tuple(float(v) for v in th[key])
        elif target == "fan":
            THUMB_FAN = tuple(float(v) for v in th[key])
        else:
            TANGENTIAL_PENALTY["rt"] = float(th[key])
    if "reach_mm" in th:
        COMFORT_RING_MM[0] = float(th["reach_mm"])
        used.append("thumb.reach_mm")
    if "max_reach_mm" in th:
        ENVELOPE_MM["rt"] = float(th["max_reach_mm"])
        used.append("thumb.max_reach_mm")
    for key, target in (("rest", "anchor"), ("joint", "joint"), ("centre", "centre"),
                        ("tangential_penalty", "pen")):
        if key not in ix:
            continue
        used.append(f"index.{key}")
        val = float(ix[key]) if key == "tangential_penalty" else tuple(float(v) for v in ix[key])
        if target == "anchor":
            ANCHORS["ri"] = val
        elif target == "joint":
            JOINTS["ri"] = val
        elif target == "centre":
            INDEX_CENTRE = val
        else:
            TANGENTIAL_PENALTY["ri"] = val
    if "pitch" in ix:
        INDEX_PITCH = float(ix["pitch"])
        used.append("index.pitch")
    if "reach_mm" in ix:
        used.append("index.reach_mm")
    if "max_reach_mm" in ix:
        ENVELOPE_MM["ri"] = float(ix["max_reach_mm"])
        used.append("index.max_reach_mm")
    # the left hand is always the exact mirror of the measured right hand
    ANCHORS["lt"] = (_mirror_x(ANCHORS["rt"][0]), ANCHORS["rt"][1])
    ANCHORS["li"] = (_mirror_x(ANCHORS["ri"][0]), ANCHORS["ri"][1])
    JOINTS["lt"] = (_mirror_x(JOINTS["rt"][0]), JOINTS["rt"][1])
    JOINTS["li"] = (_mirror_x(JOINTS["ri"][0]), JOINTS["ri"][1])
    TANGENTIAL_PENALTY["lt"] = TANGENTIAL_PENALTY["rt"]
    TANGENTIAL_PENALTY["li"] = TANGENTIAL_PENALTY["ri"]
    ENVELOPE_MM["lt"] = ENVELOPE_MM["rt"]
    ENVELOPE_MM["li"] = ENVELOPE_MM["ri"]
    return used


def load_profile(path: Path) -> dict:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"{path}: hand profile must be a JSON object")
    return data


PROFILE_TEMPLATE = json.dumps({
    "_how_to_measure": [
        "RIGHT hand only; the left half of the pad is always its exact mirror.",
        "pad_mm: active area of the pad, width x height.",
        "thumb.rest: where the right thumb tip rests when the hand lies flat and relaxed.",
        "thumb.joint: the right thumb CMC, i.e. the base the thumb rotates about.",
        "thumb.rings: 4 radii, evenly spaced is best; the spacing is the zone depth.",
        "thumb.fan_deg: the angular range the thumb tip can sweep, 0 deg = towards the "
        "pad's right edge, 90 deg = straight up, 180 deg = towards the other hand.",
        "thumb.reach_mm: comfortable (not maximum) reach of the thumb tip.",
        "thumb.reach_mm vs thumb.max_reach_mm: comfortable versus maximum. The rings "
        "are placed inside the comfortable reach, the envelope check uses the maximum.",
        "thumb.tangential_penalty: mean radial speed / mean tangential speed of the "
        "thumb tip. 1.0 would mean it sweeps sideways as fast as it extends.",
        "index.rest / index.joint: fingertip rest position and the MCP knuckle.",
        "index.centre / index.pitch: centre of the 2x2 block and its zone size.",
        "index.reach_mm: comfortable upward reach of the index tip, palm flat.",
    ],
    "pad_mm": [224.0, 148.0],
    "thumb": {"rest": [128.0, 6.0], "joint": [128.0, 6.0],
              "rings": [21.0, 31.0, 41.0, 51.0], "fan_deg": [0.0, 112.0],
              "reach_mm": 51.0, "max_reach_mm": 56.0,
              "tangential_penalty": 1.35},
    "index": {"rest": [194.0, 6.0], "joint": [196.0, 2.0],
              "centre": [194.0, 72.0], "pitch": 28.0,
              "reach_mm": 85.0, "max_reach_mm": 90.0,
              "tangential_penalty": 1.15},
}, indent=2) + "\n"


# --------------------------------------------------------------------------- #
# model parameters
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class Params:
    """Every constant is a declared model input. Nothing here is a measurement
    taken from this repository or from a person."""
    fitts_b_ms: float = 150.0        # literature: Fitts 1954 Shannon form, b ~ 0.15 s/bit
    fitts_a_ms: float = 60.0         # literature: Fitts 1954 Shannon form, a ~ 0.06 s
    stroke_ms: float = 55.0          # assumption: lift + contact + segmentation per stroke
    switch_digit_ms: float = 45.0    # assumption: thumb <-> index on the same hand
    switch_hand_ms: float = 95.0     # assumption: crossing to the other hand
    err_range_mm: float = 25.0       # assumption: confusion decays with this distance
    conf_sharpen: float = 3.0        # assumption: exponent on context cosine
    w_phys: float = 0.40
    w_err: float = 0.20
    w_learn: float = 0.25
    w_sym: float = 0.15
    rest_per_word: float = 1.0       # assumption: one boundary marker per word


PROVENANCE = [
    ("fitts_a_ms / fitts_b_ms", "Fitts (1954) Shannon formulation, published coefficients",
     "literature"),
    ("stroke_ms", "lift + contact + segmentation overhead per stroke", "model assumption"),
    ("switch_digit_ms / switch_hand_ms", "digit and hand transition penalties",
     "model assumption"),
    ("err_range_mm", "spatial decay of zone-adjacency confusion", "model assumption"),
    ("conf_sharpen", "exponent applied to corpus context cosine", "model assumption"),
    ("pad / anchor / ring geometry", "224x148 mm pad, model topology", "design input"),
    ("w_phys / w_err / w_learn / w_sym", "component weights of the objective",
     "design input"),
]


# --------------------------------------------------------------------------- #
# corpus
# --------------------------------------------------------------------------- #

@dataclass
class Corpus:
    words: list[tuple[str, list[str], int]]   # (word, phones, frequency)
    total_tokens: int
    covered_tokens: int
    phones_seen: list[str]
    n_syllables: int
    syllables_per_token: float
    syllables_per_word: float
    provenance: dict

    # filled by build_matrices
    w: list[list[float]] = None               # (n+1) x (n+1) transition weights
    strokes: float = 0.0
    phones_total: float = 0.0
    word_total: float = 0.0

    @property
    def n_symbols(self) -> int:
        return len(self.phones_seen) + 1        # + SPACE


def _fetch(url: str, dest: Path, offline: bool) -> Path:
    if dest.is_file() and dest.stat().st_size > 0:
        return dest
    if offline:
        raise SystemExit(f"offline and no cached {dest.name}; run once without --offline")
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"  fetching {url}", file=sys.stderr)
    with urllib.request.urlopen(url, timeout=FETCH_TIMEOUT) as r:
        data = r.read()
    tmp = dest.with_suffix(dest.suffix + ".part")
    tmp.write_bytes(data)
    tmp.replace(dest)
    return dest


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_corpus(n_words: int, cache: Path, offline: bool) -> Corpus:
    freq_file = _fetch(FREQ_URL, cache / "count_1w.txt", offline)
    cmu_file = _fetch(CMU_URL, cache / "cmudict.dict", offline)

    freq: list[tuple[str, int]] = []
    with freq_file.open(encoding="utf-8", errors="ignore") as f:
        for line in f:
            parts = line.split()
            if len(parts) != 2 or not parts[0].isascii() or not parts[0].isalpha():
                continue
            try:
                freq.append((parts[0].lower(), int(parts[1])))
            except ValueError:
                continue
    freq.sort(key=lambda kv: -kv[1])
    freq = freq[:n_words]

    pron: dict[str, list[str]] = {}
    variant = re.compile(r"\(\d+\)$")
    with cmu_file.open(encoding="utf-8", errors="ignore") as f:
        for line in f:
            parts = line.split()
            if len(parts) < 2:
                continue
            key = variant.sub("", parts[0])
            if key in pron:
                continue
            phones = [re.sub(r"[012]$", "", p) for p in parts[1:] if p != "#"]
            if all(p in INVENTORY for p in phones) and phones:
                pron[key] = phones

    words, seen, total = [], Counter(), 0
    dropped_unknown = 0
    for w, c in freq:
        ph = pron.get(w)
        if not ph:
            dropped_unknown += 1
            continue
        words.append((w, ph, c))
        total += c
        seen.update(ph)
    if not words:
        raise SystemExit("corpus join produced no words")

    syl = sum(sum(1 for p in ph if p in VOWELS) * c for _, ph, c in words)
    phones_seen = sorted(p for p in seen if p in INVENTORY)
    missing = sorted(set(INVENTORY) - set(phones_seen))
    if missing:
        print(f"  note: not attested in the {n_words} most frequent words: "
              f"{' '.join(missing)}", file=sys.stderr)
    requested_tokens = sum(c for _, c in freq)
    return Corpus(
        words=words,
        total_tokens=requested_tokens,
        covered_tokens=total,
        phones_seen=phones_seen,
        n_syllables=syl,
        syllables_per_token=syl / total,
        syllables_per_word=sum(sum(1 for p in ph if p in VOWELS)
                              for _, ph, _ in words) / len(words),
        provenance={
            "frequency_source": FREQ_URL,
            "pronunciation_source": CMU_URL,
            "frequency_sha256": _sha256(freq_file),
            "pronunciation_sha256": _sha256(cmu_file),
            "words_requested": n_words,
            "words_used": len(words),
            "words_dropped": dropped_unknown,
            "token_coverage": round(total / requested_tokens, 4),
        },
    )


def corpus_transitions(corpus: Corpus) -> None:
    """Undirected transition weights over the symbol stream
    REST p1..pn SPACE | REST p1'.. ; a word is one lift-to-rest round trip."""
    syms = corpus.phones_seen + [SPACE]
    idx = {s: i for i, s in enumerate(syms)}
    n = len(syms)
    rest = n                       # REST is the pseudo-symbol n
    size = n + 1
    w = [[0.0] * size for _ in range(size)]
    strokes = 0.0
    phone_total = 0.0
    word_total = 0.0
    for _, ph, c in corpus.words:
        # one word is: lift to rest, spell the phones, mark the boundary, return to
        # rest. The trailing REST is what makes the word-final return a real cost.
        seq = [rest] + [idx[p] for p in ph] + [idx[SPACE], rest]
        for a, b in zip(seq, seq[1:]):
            w[a][b] += c
            w[b][a] += c
        strokes += c * (len(ph) + 2)     # phones, boundary, return to rest
        phone_total += c * len(ph)
        word_total += c
    corpus.w = w
    corpus.strokes = strokes
    corpus.phones_total = phone_total
    corpus.word_total = word_total


def context_similarity(corpus: Corpus) -> list[list[float]]:
    """Cosine similarity of per-offset context distributions -> corpus confusability.

    Two phonemes that substitute for each other (P/B, S/SH, IH/IY) share their
    left and right context distributions; this is the data-derived confusion
    weight used by the error term. No articulatory knowledge is used here."""
    syms = corpus.phones_seen
    idx = {s: i for i, s in enumerate(syms)}
    n = len(syms)
    offs = (-2, -1, 1, 2)
    vec = [[[0.0] * n for _ in offs] for _ in range(n)]
    for _, ph, c in corpus.words:
        ids = [idx[p] for p in ph]
        L = len(ids)
        for i, s in enumerate(ids):
            for k, off in enumerate(offs):
                j = i + off
                if 0 <= j < L:
                    vec[s][k][ids[j]] += c
    norms = [[math.sqrt(sum(x * x for x in vec[s][k])) for k in range(len(offs))]
             for s in range(n)]
    sim = [[0.0] * n for _ in range(n)]
    for a in range(n):
        for b in range(a, n):
            acc = 0.0
            for k in range(len(offs)):
                na, nb = norms[a][k], norms[b][k]
                if na > 0 and nb > 0:
                    acc += sum(x * y for x, y in zip(vec[a][k], vec[b][k])) / (na * nb)
            acc /= len(offs)
            sim[a][b] = sim[b][a] = acc
    return sim


def articulatory_proximity(ph: Phoneme, ph2: Phoneme) -> float:
    """1.0 = maximally distant, 0.0 = the same sound shape. Ground truth for the
    learn term, independent of the corpus."""
    if ph.cls == ph2.cls == "SPACE" or ph.symbol == ph2.symbol:
        return 0.0
    v1, v2 = ph.symbol in VOWELS, ph2.symbol in VOWELS
    if v1 != v2:
        return 1.0
    if v1 and v2:
        d1 = math.hypot(math.log2(ph.f1 / ph2.f1), math.log2(ph.f2 / ph2.f2))
        return min(1.0, d1 / 2.0)
    place = abs(PLACE_ORDER.index(ph.place) - PLACE_ORDER.index(ph2.place)) / (len(PLACE_ORDER) - 1)
    man = abs(MANNER_ORDER.index(ph.manner) - MANNER_ORDER.index(ph2.manner)) / (len(MANNER_ORDER) - 1)
    voice = 0.0 if ph.voiced == ph2.voiced else 1.0
    return 0.5 * place + 0.2 * man + 0.3 * voice


# --------------------------------------------------------------------------- #
# cost model
# --------------------------------------------------------------------------- #

COMPONENTS = ("time", "error", "learn", "sym")
N_COMP = len(COMPONENTS)


class Objective:
    """Four additive components over the assignment symbol -> zone.

    All pair terms factor as (symbol matrix entry) * (zone matrix entry), so a swap
    only touches the terms of the two moved symbols.
    """

    def __init__(self, corpus: Corpus, zones: list[Zone], params: Params):
        self.corpus = corpus
        self.zones = zones
        self.params = params
        self.syms = corpus.phones_seen + [SPACE]
        self.n = len(self.syms)
        self.index = {s: i for i, s in enumerate(self.syms)}
        self.rest = self.n                                   # pseudo-symbol index
        self.nz = len(zones)
        self.anchor = ANCHORS
        self.mirror = mirror_of(zones)
        self.frames = self._kinematic_frames()
        self.cls = [INVENTORY[s].cls if s in INVENTORY else SPACE_CLASS for s in self.syms]
        self.cls_ids = {c: i for i, c in enumerate(CLASSES)}
        self.cls_of = [self.cls_ids[c] for c in self.cls]
        self.cls_size = [0] * len(CLASSES)
        for c in self.cls_of:
            self.cls_size[c] += 1
        # a class with a single symbol cannot be mirrored; excluding it keeps the
        # symmetry score honest instead of permanently penalising the layout
        self.sym_classes = [c for c in range(len(CLASSES)) if self.cls_size[c] >= 2]
        self.sym_weight_total = sum(self.cls_size[c] for c in self.sym_classes) or 1
        self.mirror_bit = [1 << self.mirror[z] for z in range(self.nz)]
        self.cls_lmask = [0] * len(CLASSES)
        self.cls_rmask = [0] * len(CLASSES)
        self.cls_score = [0.0] * len(CLASSES)
        self.sym_total = 0.0
        self._build_matrices()
        self.wfac = [0.0] * N_COMP
        self.ref = None
        self.set_weights(params)

    # -- kinematics ----------------------------------------------------- #
    def _kinematic_frames(self) -> None:
        """(radius, angle) of every zone and of the digit's rest position, in the
        digit's own polar frame around its joint. Indexed like the move table, i.e.
        0..nz-1 for zones and nz+k for the rest position of REST_ORDER[k]."""
        self.rest_digit = ["rt", "lt", "ri", "li"]
        self.point_digit = [z.digit for z in self.zones] + list(self.rest_digit)
        self.point_xy = [(z.x, z.y) for z in self.zones] + [ANCHORS[d] for d in
                                                             self.rest_digit]
        self.point_w = [z.width for z in self.zones] + [REST_WIDTH_MM] * 4
        self.polar = []
        for digit, (x, y) in zip(self.point_digit, self.point_xy):
            jx, jy = JOINTS[digit]
            self.polar.append((math.dist((x, y), (jx, jy)),
                               math.atan2(y - jy, x - jx)))

    def _effective_distance(self, i: int, j: int) -> float:
        """Effective movement distance in mm between two points of the move table.

        Same digit: the polar path, with the tangential part charged at the digit's
        measured tangential premium. Different digit or hand: the two radial
        segments from and to the rest positions, because the finger lifts and
        re-approaches instead of sliding across the pad."""
        chord = math.dist(self.point_xy[i], self.point_xy[j])
        da, db = self.point_digit[i], self.point_digit[j]
        if da != db:
            # a different finger or hand: the stroke lifts and re-approaches, so the
            # path is two ballistic segments instead of one slide
            return (math.dist(self.point_xy[i], ANCHORS[da])
                    + math.dist(ANCHORS[db], self.point_xy[j]))
        (ra, ta), (rb, tb) = self.polar[i], self.polar[j]
        dth = abs(ta - tb)
        if dth > math.pi:
            dth = 2 * math.pi - dth
        # polar path: radial change plus the swept arc at the tangential premium,
        # never below the straight line the finger could in principle cut
        sweep = 0.5 * (ra + rb) * dth * TANGENTIAL_PENALTY[da]
        return max(chord, abs(ra - rb) + sweep)

    # -- setup ---------------------------------------------------------- #
    def _build_matrices(self) -> None:
        p, n, nz = self.params, self.n, self.nz
        d = [[0.0] * nz for _ in range(nz)]
        for i in range(nz):
            for j in range(nz):
                d[i][j] = math.dist((self.zones[i].x, self.zones[i].y),
                                    (self.zones[j].x, self.zones[j].y))
        # movement: Fitts on the kinematic path, harmonic target width, switch penalty
        npts = nz + len(self.rest_digit)
        mv = [[0.0] * npts for _ in range(npts)]
        for i in range(npts):
            di, wi = self.point_digit[i], self.point_w[i]
            for j in range(npts):
                w = 2.0 / (1.0 / wi + 1.0 / self.point_w[j])
                bits = math.log2(1.0 + self._effective_distance(i, j) / w)
                dj = self.point_digit[j]
                sw = 0.0 if di == dj else (p.switch_digit_ms if di[1] == dj[1]
                                            else p.switch_hand_ms)
                mv[i][j] = p.fitts_a_ms + p.fitts_b_ms * bits + sw
        self.move_tab = mv
        # every zone returns to the rest position of its own digit
        self.rest_move = [mv[i][nz + self.rest_digit.index(self.zones[i].digit)]
                          for i in range(nz)]
        self.d_tab = d
        diag = math.hypot(PAD_W, PAD_H)
        self.geo_tab = [[x / diag for x in row] for row in d]     # learn term
        self.err_tab = [[math.exp(-((x / p.err_range_mm) ** 2)) for x in row] for row in d]
        # symbol matrices
        ctx = context_similarity(self.corpus)
        nph = len(self.corpus.phones_seen)
        wc = [[0.0] * (self.rest + 1) for _ in range(self.rest + 1)]
        for a in range(self.n):
            for b in range(self.n):
                c = ctx[a][b] if a < nph and b < nph else 0.0
                v = max(0.0, c) ** p.conf_sharpen
                wc[a][b] = v
        self.wc = wc
        lw = [[0.0] * (self.rest + 1) for _ in range(self.rest + 1)]
        raw = 0.0
        for a in range(self.n):
            pa = INVENTORY.get(self.syms[a])
            for b in range(a, self.n):
                pb = INVENTORY.get(self.syms[b])
                if pa is None or pb is None:
                    continue
                v = 1.0 - articulatory_proximity(pa, pb)
                if pa.cls == pb.cls:
                    v += 0.25
                lw[a][b] = lw[b][a] = v
                raw = max(raw, v)
        if raw > 0:
            for a in range(self.n):
                for b in range(self.n):
                    lw[a][b] /= raw
        self.lw = lw
        # transition weight matrix (already symmetric, corpus counted)
        self.W = self.corpus.w
        # flat partner lists: (partner, transition weight, confusability, learn weight)
        self.partners = [
            [(u, self.W[s][u], self.wc[s][u], self.lw[s][u])
             for u in range(self.n) if u != s]
            for s in range(self.n)]

    def set_weights(self, params: Params) -> None:
        self.params = params
        self.weights = [params.w_phys, params.w_err, params.w_learn, params.w_sym]

    def normalise(self, raw: list[float], ref: list[float]) -> None:
        self.wfac = [wt / r if r > 0 else 0.0 for wt, r in zip(self.weights, ref)]

    # -- evaluation ----------------------------------------------------- #
    def _rest_pairs(self, s: int, i: int) -> float:
        """Time contribution of every REST transition touching symbol s at zone i."""
        return self.W[s][self.rest] * self.rest_move[i]

    def full(self, zone_of: list[int]) -> list[float]:
        w, n, rest = self.W, self.n, self.rest
        mv, err, geo = self.move_tab, self.err_tab, self.geo_tab
        t = e = l = 0.0
        for a in range(n):
            ia = zone_of[a]
            t += self._rest_pairs(a, ia)
            wa, wea, la = w[a], self.wc[a], self.lw[a]
            for b in range(a + 1, n):
                ib = zone_of[b]
                t += wa[b] * mv[ia][ib]
                e += wea[b] * err[ia][ib]
                l += la[b] * geo[ia][ib]
        st = self.cls_size
        # symmetry
        sym = 0.0
        for c in self.sym_classes:
            sym += st[c] * self._class_score(zone_of, c)
        return [t, e, l, 1.0 - sym / self.sym_weight_total]

    def _class_score(self, zone_of: list[int], c: int) -> float:
        """Authoritative, mask-free class mirror score (used by full())."""
        left, right = set(), set()
        for s, cs in enumerate(self.cls_of):
            if cs == c:
                z = zone_of[s]
                (left if self.zones[z].left_half else right).add(z)
        denom = min(len(left), len(right))
        if denom == 0:
            return 0.0
        return sum(1 for z in left if self.mirror[z] in right) / denom

    def _mirror_mask(self, mask: int) -> int:
        out, m = 0, mask
        while m:
            b = m & -m
            out |= self.mirror_bit[b.bit_length() - 1]
            m ^= b
        return out

    def _score_mask(self, c: int) -> float:
        left, right = self.cls_lmask[c], self.cls_rmask[c]
        denom = min(bin(left).count("1"), bin(right).count("1"))
        if denom == 0:
            return 0.0
        return bin(left & self._mirror_mask(right)).count("1") / denom

    def _move_bit(self, c: int, old: int, new: int) -> None:
        """Move class c's occupancy from zone old to zone new."""
        if self.zones[old].left_half:
            self.cls_lmask[c] &= ~(1 << old)
            self.cls_rmask[c] &= ~(1 << new)
        else:
            self.cls_rmask[c] &= ~(1 << old)
            self.cls_lmask[c] &= ~(1 << new)
        if self.zones[new].left_half:
            self.cls_lmask[c] |= 1 << new
        else:
            self.cls_rmask[c] |= 1 << new

    def sync(self, zone_of: list[int]) -> None:
        """Rebuild the incremental symmetry state from an assignment."""
        self.cls_lmask = [0] * len(CLASSES)
        self.cls_rmask = [0] * len(CLASSES)
        for s in range(self.n):
            z = zone_of[s]
            if self.zones[z].left_half:
                self.cls_lmask[self.cls_of[s]] |= 1 << z
            else:
                self.cls_rmask[self.cls_of[s]] |= 1 << z
        for c in self.sym_classes:
            self.cls_score[c] = self._score_mask(c)
        self._recount_sym()

    def _recount_sym(self) -> None:
        self.sym_total = (sum(self.cls_size[c] * self.cls_score[c] for c in self.sym_classes)
                          / self.sym_weight_total)

    def commit(self, zone_of: list[int], s: int, t: int) -> None:
        """Accept a swap: update the assignment and the symmetry state together."""
        i, j = zone_of[s], zone_of[t]
        zone_of[s], zone_of[t] = j, i
        cs, ct = self.cls_of[s], self.cls_of[t]
        if cs == ct:
            return                      # the class keeps the same zone set
        self._move_bit(cs, i, j)
        self._move_bit(ct, j, i)
        self.cls_score[cs] = self._score_mask(cs)
        self.cls_score[ct] = self._score_mask(ct)
        self._recount_sym()

    def weighted(self, raw: list[float]) -> float:
        return sum(f * v for f, v in zip(self.wfac, raw))

    def delta(self, zone_of: list[int], s: int, t: int) -> list[float]:
        """Change of every component if symbols s and t exchange zones.

        The (s,t) pair itself is invariant: all three pair terms are symmetric in
        the two zones, so the pair contributes the same before and after."""
        i, j = zone_of[s], zone_of[t]
        mv, err, geo = self.move_tab, self.err_tab, self.geo_tab
        rm = self.rest_move
        Wsr, Wtr = self.W[s][self.rest], self.W[t][self.rest]
        mvi, mvj, erri, errj, geoi, geoj = mv[i], mv[j], err[i], err[j], geo[i], geo[j]
        dt = de = dl = 0.0
        for u, ws, we, le in self.partners[s]:
            if u == t:
                continue
            z = zone_of[u]
            dt += ws * (mvj[z] - mvi[z])
            de += we * (errj[z] - erri[z])
            dl += le * (geoj[z] - geoi[z])
        for u, ws, we, le in self.partners[t]:
            if u == s:
                continue
            z = zone_of[u]
            dt += ws * (mvi[z] - mvj[z])
            de += we * (erri[z] - errj[z])
            dl += le * (geoi[z] - geoj[z])
        dt += Wsr * (rm[j] - rm[i]) + Wtr * (rm[i] - rm[j])
        cs, ct = self.cls_of[s], self.cls_of[t]
        if cs == ct:
            dsym = 0.0
        else:
            old = self.cls_score[cs] * self.cls_size[cs] + self.cls_score[ct] * self.cls_size[ct]
            lm, rm_ = self.cls_lmask, self.cls_rmask
            keep = (lm[cs], rm_[cs], lm[ct], rm_[ct])
            self._move_bit(cs, i, j)
            self._move_bit(ct, j, i)
            new = self._score_mask(cs) * self.cls_size[cs] + self._score_mask(ct) * self.cls_size[ct]
            lm[cs], rm_[cs], lm[ct], rm_[ct] = keep
            dsym = -(new - old) / self.sym_weight_total
        return [dt, de, dl, dsym]

    def sym_score(self, zone_of: list[int]) -> float:
        """Mirror score of the whole layout, computed from scratch."""
        return (sum(self.cls_size[c] * self._class_score(zone_of, c)
                    for c in self.sym_classes) / self.sym_weight_total)

    # -- derived report values ------------------------------------------ #
    def time_report(self, zone_of: list[int]) -> dict:
        w, mv = self.W, self.move_tab
        n = self.n
        move_ms = 0.0
        for a in range(n):
            ia = zone_of[a]
            move_ms += w[a][self.rest] * self.rest_move[ia]
            for b in range(a + 1, n):
                move_ms += w[a][b] * mv[ia][zone_of[b]]
        per_stroke = self.params.stroke_ms
        overhead_ms = per_stroke * self.corpus.strokes
        total_ms = move_ms + overhead_ms
        ms_per_word = total_ms / self.corpus.word_total
        strokes = self.corpus.strokes / self.corpus.word_total
        # the best case the stroke count itself allows: every transition free
        ceil_ms = overhead_ms / self.corpus.word_total
        return {
            "total_hours": round(total_ms / 3.6e6, 1),
            "ms_per_word": round(ms_per_word, 1),
            "ms_per_word_movement": round(move_ms / self.corpus.word_total, 1),
            "ms_per_word_stroke_overhead": round(overhead_ms / self.corpus.word_total, 1),
            "ms_per_stroke": round(ms_per_word / strokes, 1),
            "strokes_per_word": round(strokes, 3),
            "phones_per_word": round(self.corpus.phones_total / self.corpus.word_total, 3),
            "model_wpm": round(60000.0 / ms_per_word, 1),
            "stroke_count_ceiling_wpm": round(60000.0 / ceil_ms, 1),
            "note": "model, not measured: no person, device or session is involved",
        }


# --------------------------------------------------------------------------- #
# search
# --------------------------------------------------------------------------- #

def random_reference(obj: Objective, seed: int, samples: int = 96) -> list[float]:
    rng = random.Random(seed ^ 0x5EED)
    acc = [0.0] * N_COMP
    zone_of = list(range(obj.n))
    for _ in range(samples):
        rng.shuffle(zone_of)
        raw = obj.full(zone_of)
        for c in range(N_COMP):
            acc[c] += raw[c]
    return [a / samples for a in acc]


def anneal(obj: Objective, seed: int, iters: int, restarts: int, verbose: bool):
    rng = random.Random(seed)
    n = obj.n
    zone_of = list(range(n))
    rng.shuffle(zone_of)
    obj.sync(zone_of)
    best_state = list(zone_of)
    best_raw = obj.full(zone_of)
    best_obj = obj.weighted(best_raw)
    start_obj = best_obj
    history = []
    t_start = _temperature(obj, zone_of, rng)
    for r in range(restarts):
        if r:
            zone_of = list(range(n))
            rng.shuffle(zone_of)
            obj.sync(zone_of)
            cur_obj = obj.weighted(obj.full(zone_of))
        else:
            cur_obj = best_obj
        t0, t1 = t_start, 0.004 * t_start
        for it in range(iters):
            temp = t0 * (t1 / t0) ** (it / max(1, iters - 1))
            s = rng.randrange(n)
            t = rng.randrange(n)
            if s == t:
                continue
            d = obj.weighted(obj.delta(zone_of, s, t))
            if d <= 0.0 or rng.random() < math.exp(-d / temp):
                obj.commit(zone_of, s, t)
                cur_obj += d
                if cur_obj < best_obj - 1e-12:
                    best_obj = cur_obj
                    best_state = list(zone_of)
                    best_raw = obj.full(zone_of)
        if verbose:
            print(f"  restart {r + 1}/{restarts}: best {best_obj:.4f}", file=sys.stderr)
        history.append(round(best_obj, 6))
    best_raw = polish(obj, best_state)
    best_obj = obj.weighted(best_raw)
    return best_state, best_raw, best_obj, history, start_obj


def _temperature(obj: Objective, zone_of: list[int], rng: random.Random) -> float:
    """Scale-free start temperature: mean |delta| of random swaps in the current state."""
    acc, n = 0.0, min(200, 24 * obj.n)
    for _ in range(n):
        s, t = rng.randrange(obj.n), rng.randrange(obj.n)
        if s == t:
            continue
        acc += abs(obj.weighted(obj.delta(zone_of, s, t)))
    return max(acc / n, 1e-9)


def polish(obj: Objective, zone_of: list[int], max_pass: int = 40) -> list[float]:
    """Best-improvement hill climb down to a swap-local optimum."""
    n = obj.n
    obj.sync(zone_of)
    raw = obj.full(zone_of)
    for _ in range(max_pass):
        cur = obj.weighted(raw)
        bs, bt, bd = -1, -1, 0.0
        for s in range(n):
            for t in range(s + 1, n):
                d = obj.weighted(obj.delta(zone_of, s, t))
                if d < bd - 1e-12:
                    bs, bt, bd = s, t, d
        if bs < 0:
            break
        obj.commit(zone_of, bs, bt)
        raw = obj.full(zone_of)
        if abs(obj.weighted(raw) - (cur + bd)) > 1e-6:
            raise AssertionError("hill climb drifted from the incremental delta")
    return raw


# --------------------------------------------------------------------------- #
# baselines
# --------------------------------------------------------------------------- #

def baselines(obj: Objective, corpus: Corpus) -> list[tuple[str, list[int]]]:
    n = obj.n
    out: list[tuple[str, list[int]]] = []
    # 1. inventory order (alphabetical ARPAbet) over the zone list
    out.append(("inventory-order", [i for i in range(n)]))
    # 2. reversed
    out.append(("reversed", list(range(n - 1, -1, -1))))
    # 3. frequency greedy: the most-used symbol onto the cheapest zone, where
    #    cheapest = lowest mean movement cost to and from every other zone
    ease = sorted(range(obj.nz), key=lambda z: sum(obj.move_tab[z][j]
                                                   for j in range(obj.nz)))
    order = sorted(range(n), key=lambda s: (-corpus.w[s][obj.rest], s))
    greedy = [0] * n
    for rank, s in enumerate(order):
        greedy[s] = ease[rank]
    out.append(("frequency-greedy", greedy))
    # 4. random reference
    rng = random.Random(11)
    rnd = list(range(n))
    rng.shuffle(rnd)
    out.append(("random", rnd))
    return out


# --------------------------------------------------------------------------- #
# report
# --------------------------------------------------------------------------- #

def layout_rows(obj: Objective, zone_of: list[int]) -> list[dict]:
    rows = []
    for z, zone in enumerate(obj.zones):
        s = next(i for i, zz in enumerate(zone_of) if zz == z)
        rows.append({
            "zone": zone.zid, "digit": zone.digit,
            "x_mm": zone.x, "y_mm": zone.y, "width_mm": zone.width,
            "ring": zone.ring, "sector": zone.sector,
            "symbol": obj.syms[s], "class": obj.cls[s],
            "reach_mm": round(math.dist((zone.x, zone.y), obj.anchor[zone.digit]), 1),
        })
    return rows


def ascii_map(obj: Objective, zone_of: list[int], digit: str, cell: float = 6.0) -> str:
    zs = [i for i, z in enumerate(obj.zones) if z.digit == digit]
    by_zone = {zone_of[s]: s for s in range(obj.n)}
    xs = [obj.zones[i].x for i in zs]
    ys = [obj.zones[i].y for i in zs]
    ax, ay = obj.anchor[digit]
    x0, x1 = min(min(xs), ax) - cell, max(max(xs), ax) + cell
    y0, y1 = min(min(ys), ay) - cell, max(max(ys), ay) + cell
    cols = max(1, int((x1 - x0) / cell) + 1)
    rowsn = max(1, int((y1 - y0) / cell) + 1)
    grid = [["   " for _ in range(cols)] for _ in range(rowsn)]
    def put(px: float, py: float, text: str) -> None:
        c = min(cols - 1, max(0, int(round((px - x0) / cell))))
        r = min(rowsn - 1, max(0, rowsn - 1 - int(round((py - y0) / cell))))
        grid[r][c] = text
    for s, z in by_zone.items():
        zone = obj.zones[z]
        put(zone.x, zone.y, obj.syms[s][:3].ljust(3))
    put(ax, ay, " @ ")
    head = f"  {digit}  (x {x0:.0f}..{x1:.0f} mm, y {y0:.0f}..{y1:.0f} mm, @ = rest)"
    body = "\n".join("  " + "|".join(cells) for cells in grid)
    return head + "\n" + body


def family_tightness(obj: Objective, zone_of: list[int]) -> float:
    """Mean normalised within-class distance: how tight the learnable families are."""
    groups: dict[str, list[int]] = {}
    for s, c in enumerate(obj.cls):
        groups.setdefault(c, []).append(zone_of[s])
    tot, n = 0.0, 0
    for c, zs in groups.items():
        if len(zs) < 2:
            continue
        for a in range(len(zs)):
            for b in range(a + 1, len(zs)):
                tot += obj.geo_tab[zs[a]][zs[b]]
                n += 1
    return tot / n if n else 0.0


def vowel_grid(obj: Objective, zone_of: list[int]) -> dict:
    """How systematic is the vowel block? F1 should follow the ring, F2 the sector."""
    by_zone = {zone_of[s]: s for s in range(obj.n)}
    rows = []
    for z, s in by_zone.items():
        zone = obj.zones[z]
        if zone.ring < 0 or not (s < obj.n and obj.syms[s] in VOWELS):
            continue
        rows.append((INVENTORY[obj.syms[s]].f1, INVENTORY[obj.syms[s]].f2,
                     zone.ring, zone.sector, obj.syms[s]))
    if len(rows) < 4:
        return {"n": len(rows), "r_f1_ring": None, "r_f2_sector": None}

    def pearson(a, b):
        n = len(a)
        ma, mb = sum(a) / n, sum(b) / n
        va = math.sqrt(sum((x - ma) ** 2 for x in a))
        vb = math.sqrt(sum((x - mb) ** 2 for x in b))
        if va == 0 or vb == 0:
            return None
        return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / (va * vb)
    return {
        "n": len(rows),
        "r_f1_ring": round(pearson([r[0] for r in rows], [r[2] for r in rows]) or 0.0, 3),
        "r_f2_sector": round(pearson([r[1] for r in rows], [r[3] for r in rows]) or 0.0, 3),
    }


def confusable_report(obj: Objective, zone_of: list[int], top: int = 12) -> list[dict]:
    pairs = []
    n = obj.n
    nph = len(obj.corpus.phones_seen)
    for a in range(n):
        for b in range(a + 1, n):
            w = obj.wc[a][b] if a < nph and b < nph else 0.0
            if w <= 0:
                continue
            d = obj.d_tab[zone_of[a]][zone_of[b]]
            same = obj.zones[zone_of[a]].digit == obj.zones[zone_of[b]].digit
            pairs.append({"a": obj.syms[a], "b": obj.syms[b], "confusability": round(w, 4),
                          "zone_distance_mm": round(d, 1), "same_digit": same})
    pairs.sort(key=lambda r: -r["confusability"])
    return pairs[:top]


def fmt_pct(a, b):
    if a == 0:
        return "  n/a"
    return f"{(b - a) / abs(a) * 100:+6.1f} %"


def print_report(obj: Objective, corpus: Corpus, params: Params, state: list[int],
                 raw: list[float], base_rows: list[tuple[str, list, list[float]]],
                 elapsed: float, seed: int, iters: int, restarts: int) -> None:
    ref = obj.ref
    print()
    print("=" * 78)
    print("TOUCH-STENO  phoneme layout optimisation  --  4-finger topology, 40 zones")
    print("=" * 78)
    print(f"corpus      {corpus.provenance['words_used']} of "
          f"{corpus.provenance['words_requested']} most frequent English words, "
          f"{corpus.provenance['token_coverage'] * 100:.1f} % of tokens, "
          f"{corpus.syllables_per_token:.3f} syllables/token, "
          f"{corpus.syllables_per_word:.2f} syllables/word (unweighted)")
    print(f"            freq {FREQ_URL.split('/')[-1]} sha256 "
          f"{corpus.provenance['frequency_sha256'][:12]}")
    print(f"            pron cmudict.dict   sha256 "
          f"{corpus.provenance['pronunciation_sha256'][:12]}")
    tr = obj.time_report(state)
    print(f"topology    2 thumbs x 16 (4 rings x 4 sectors) + 2 index fingers x 4 (2x2)"
          f" on {PAD_W:.0f}x{PAD_H:.0f} mm")
    print(f"            39 ARPAbet phonemes + SPACE = 40 symbols; zone widths "
          f"{min(z.width for z in obj.zones):.1f}..{max(z.width for z in obj.zones):.1f} mm")
    print(f"geometry    {GEOMETRY_SOURCE}; thumb fan {THUMB_FAN[0]:.0f}..{THUMB_FAN[1]:.0f} deg, "
          f"rings {'/'.join(f'{r:.0f}' for r in THUMB_RING_R)} mm, "
          f"reach envelope {ENVELOPE_MM['rt']:.0f} mm thumb / {ENVELOPE_MM['ri']:.0f} mm index")
    print(f"            tangential premium thumb "
          f"{TANGENTIAL_PENALTY['rt']:.2f}x / index {TANGENTIAL_PENALTY['ri']:.2f}x "
          f"(1.0 = same speed in every direction)")
    print()
    print("objective   w = " + " + ".join(
        f"{c}*{wt:.2f}" for c, wt in zip(COMPONENTS, obj.weights)) +
        "   (normalised against a 96-sample random layout)")
    print()
    hdr = (f"{'layout':<18}{'ms/word':>9}{'WPM':>6}{'time':>7}{'error':>7}{'learn':>7}"
           f"{'sym':>6}{'objective':>11}")
    print(hdr)
    print("-" * len(hdr))
    for name, st, r in base_rows:
        rr = obj.time_report(st)
        print(f"{name:<18}{rr['ms_per_word']:>9.1f}{rr['model_wpm']:>6.0f}"
              f"{r[0] / ref[0]:>7.3f}{r[1] / ref[1]:>7.3f}{r[2] / ref[2]:>7.3f}"
              f"{1 - r[3]:>6.3f}{obj.weighted(r):>11.4f}")
    print(f"{'ANNEALED':<18}{tr['ms_per_word']:>9.1f}{tr['model_wpm']:>6.0f}"
          f"{raw[0] / ref[0]:>7.3f}{raw[1] / ref[1]:>7.3f}{raw[2] / ref[2]:>7.3f}"
          f"{1 - raw[3]:>6.3f}{obj.weighted(raw):>11.4f}")
    print("  time / error / learn are normalised so that a random layout scores 1.000; "
          "sym is the mirror score, higher is better")
    print()
    st_map = {name: st for name, st, _ in base_rows}
    inv = {name: r for name, _, r in base_rows}["inventory-order"]
    print(f"vs inventory-order   time {fmt_pct(inv[0], raw[0])}   "
          f"error {fmt_pct(inv[1], raw[1])}   learn {fmt_pct(inv[2], raw[2])}   "
          f"symmetry {inv[3] - raw[3]:+.3f}   "
          f"objective {fmt_pct(obj.weighted(inv), obj.weighted(raw))}")
    print(f"search      seed {seed}, {restarts} x {iters} swaps + best-improvement polish, "
          f"{elapsed:.1f} s")
    print()
    for digit in ("lt", "rt", "li", "ri"):
        print(ascii_map(obj, state, digit))
        print()
    print(f"symmetry    class-wise mirror score {1 - raw[3]:.3f}   "
          f"family tightness (lower = tighter) {family_tightness(obj, state):.4f}   "
          f"inventory-order {family_tightness(obj, st_map['inventory-order']):.4f}")
    vg = vowel_grid(obj, state)
    print(f"vowel grid  n={vg['n']} vowels, r(F1, ring)={vg['r_f1_ring']}   "
          f"r(F2, sector)={vg['r_f2_sector']}   "
          f"(inventory-order r={vowel_grid(obj, st_map['inventory-order'])['r_f1_ring']})")
    print()
    print("most confusable pairs (corpus context) and where the annealer put them:")
    for r in confusable_report(obj, state, 8):
        print(f"  {r['a']:>3}/{r['b']:<3} conf {r['confusability']:.3f} -> "
              f"{r['zone_distance_mm']:>5.1f} mm {'same digit' if r['same_digit'] else 'split'}")
    print()
    print(f"time        {tr['ms_per_word']:.0f} ms/word = {tr['ms_per_stroke']:.0f} ms x "
          f"{tr['strokes_per_word']:.2f} strokes/word "
          f"({tr['ms_per_word_stroke_overhead']:.0f} ms overhead + "
          f"{tr['ms_per_word_movement']:.0f} ms movement)")
    print(f"throughput  model ceiling {tr['model_wpm']:.0f} WPM. With one stroke per phoneme "
          f"({tr['phones_per_word']:.2f} phones/word) the stroke count alone caps this at "
          f"{tr['stroke_count_ceiling_wpm']:.0f} WPM even if every move were free.  "
          f"[{tr['note']}]")
    print("=" * 78)


# --------------------------------------------------------------------------- #
# self test
# --------------------------------------------------------------------------- #

def geometry_report(obj: Objective) -> list[tuple[str, bool, str]]:
    """Every hard constraint the zone geometry has to satisfy, as (name, ok, detail).

    Used by the self-test (which fails on any breach) and by the main run (which
    reports the breaches but still produces a layout, because the caller may want to
    see what the optimiser does with an infeasible geometry)."""
    zones = obj.zones

    def _in_fan(i: int) -> bool:
        deg = math.degrees(obj.polar[i][1]) % 360
        lo, hi = (THUMB_FAN if zones[i].digit == "rt"
                  else (180 - THUMB_FAN[1], 180 - THUMB_FAN[0]))
        return lo - 1e-9 <= deg <= hi + 1e-9

    def _thumb_max() -> float:
        return max(obj.polar[i][0] for i, z in enumerate(zones) if z.digit in ("rt", "lt"))

    same = [(i, j) for i in range(obj.nz) for j in range(obj.nz)
            if obj.point_digit[i] == obj.point_digit[j]]
    cross = [(i, j) for i in range(obj.nz) for j in range(obj.nz)
             if obj.point_digit[i] != obj.point_digit[j]]
    return [
        ("40 zones, bijective",
         len(zones) == 40 and len({z.zid for z in zones}) == 40, ""),
        ("no zone below the 10 mm target floor",
         all(z.width >= TARGET_FLOOR_MM - GEO_TOL_MM for z in zones),
         f"min={min(z.width for z in zones):.1f} mm"),
        ("no two zones overlap",
         all(math.dist((a.x, a.y), (b.x, b.y)) >= 0.5 * (a.width + b.width) - GEO_TOL_MM
             for i, a in enumerate(zones) for b in zones[i + 1:]), ""),
        ("all zones lie on the pad",
         all(-1 <= z.x <= PAD_W + 1 and -1 <= z.y <= PAD_H + 1 for z in zones), ""),
        ("every zone is inside its digit's reach envelope",
         all(obj.polar[i][0] <= ENVELOPE_MM[z.digit] + GEO_TOL_MM
             for i, z in enumerate(zones)),
         "max " + ", ".join(
             f"{d} {max(obj.polar[i][0] for i, z in enumerate(zones) if z.digit == d):.1f}"
             f"/{ENVELOPE_MM[d]:.0f}" for d in ("rt", "lt", "ri", "li"))),
        ("thumb fans stay inside the declared circumduction range",
         all(_in_fan(i) for i, z in enumerate(zones) if z.digit in ("rt", "lt")),
         f"right fan {THUMB_FAN[0]:.0f}..{THUMB_FAN[1]:.0f} deg, left is its mirror"),
        ("no thumb ring sits outside the comfortable reach",
         _thumb_max() <= COMFORT_RING_MM[0] + GEO_TOL_MM,
         f"outer ring {_thumb_max():.1f} / comfortable {COMFORT_RING_MM[0]:.1f} mm"),
        ("effective movement distance is symmetric everywhere",
         all(abs(obj._effective_distance(i, j) - obj._effective_distance(j, i)) < 1e-9
             for i in range(obj.nz) for j in range(obj.nz)), ""),
        ("same-digit distance is never shorter than the chord",
         all(obj._effective_distance(i, j) >= obj.d_tab[i][j] - 1e-9 for i, j in same), ""),
        ("cross-digit path goes through the two rest positions",
         all(obj._effective_distance(i, j) <= obj.d_tab[i][j] + 1e-9
             or math.isclose(obj._effective_distance(i, j),
                             math.dist(obj.point_xy[i], ANCHORS[obj.point_digit[i]])
                             + math.dist(ANCHORS[obj.point_digit[j]], obj.point_xy[j]),
                             abs_tol=1e-9) for i, j in cross), ""),
        ("mirror map is an involution",
         all(obj.mirror[obj.mirror[i]] == i for i in range(obj.nz)), ""),
    ]


def self_test(corpus: Corpus, params: Params, seed: int) -> int:
    fails = []

    def check(name, ok, detail=""):
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}{(' - ' + detail) if detail else ''}")
        if not ok:
            fails.append(name)

    zones = build_topology()
    obj = Objective(corpus, zones, params)
    check("39 phonemes + SPACE", obj.n == 40, f"n={obj.n}")
    for name, ok, detail in geometry_report(obj):
        check(name, ok, detail)
    check("corpus phonemes are a subset of the inventory",
          set(corpus.phones_seen) <= set(INVENTORY))
    check("every word has >= 1 phone", all(len(ph) >= 1 for _, ph, _ in corpus.words))


    rng = random.Random(seed)
    ref = random_reference(obj, seed)
    obj.normalise(obj.full(list(range(obj.n))), ref)
    worst = 0.0
    for _ in range(200):
        st = list(range(obj.n))
        rng.shuffle(st)
        obj.sync(st)
        base = obj.full(st)
        s, t = rng.randrange(obj.n), rng.randrange(obj.n)
        d = obj.delta(st, s, t)
        st[s], st[t] = st[t], st[s]
        obj.sync(st)
        after = obj.full(st)
        for c in range(N_COMP):
            worst = max(worst, abs((after[c] - base[c]) - d[c]) / max(1.0, abs(after[c])))
    check("delta == full - full over 200 random swaps", worst < 1e-9, f"max rel err {worst:.2e}")

    ok = True
    for _ in range(40):
        st = list(range(obj.n))
        rng.shuffle(st)
        obj.sync(st)
        for _ in range(5):
            s, t = rng.randrange(obj.n), rng.randrange(obj.n)
            obj.commit(st, s, t)
        ok = ok and abs(obj.sym_total - obj.sym_score(st)) < 1e-12
    check("incremental symmetry masks == from-scratch class score", ok)

    a_state, a_raw, a_obj, _, _ = anneal(obj, seed, 4000, 2, False)
    b_state, b_raw, b_obj, _, _ = anneal(obj, seed, 4000, 2, False)
    check("deterministic for a fixed seed", a_state == b_state and abs(a_obj - b_obj) < 1e-12)
    check("annealing beats every baseline",
          all(a_obj <= obj.weighted(obj.full(st)) + 1e-9
              for _, st in baselines(obj, corpus)),
          f"annealed {a_obj:.4f}")
    check("annealed layout is a permutation",
          sorted(a_state) == list(range(obj.nz)))
    check("every component is finite",
          all(math.isfinite(x) for x in a_raw))
    print(f"  {len(fails)} failure(s)")
    return 1 if fails else 0


# --------------------------------------------------------------------------- #
# cli
# --------------------------------------------------------------------------- #

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--words", type=int, default=20000,
                    help="most frequent English words to use (default 20000)")
    ap.add_argument("--iters", type=int, default=120000, help="SA swaps per restart")
    ap.add_argument("--restarts", type=int, default=4)
    ap.add_argument("--seed", type=int, default=20260925)
    ap.add_argument("--w-phys", type=float, default=Params.w_phys)
    ap.add_argument("--w-err", type=float, default=Params.w_err)
    ap.add_argument("--w-learn", type=float, default=Params.w_learn)
    ap.add_argument("--w-sym", type=float, default=Params.w_sym)
    ap.add_argument("--cache", type=Path, default=Path(os.environ.get(CACHE_ENV, DEFAULT_CACHE)))
    ap.add_argument("--offline", action="store_true", help="fail instead of downloading")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--hand-profile", type=Path,
                    help="JSON file of measured hand geometry; see apply_profile()")
    ap.add_argument("--write-profile-template", type=Path,
                    help="write a fillable profile template and exit")
    ap.add_argument("--out", type=Path, help="write the full result as JSON")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)

    if args.write_profile_template:
        args.write_profile_template.write_text(PROFILE_TEMPLATE, encoding="utf-8")
        print(f"wrote {args.write_profile_template}", file=sys.stderr)
        return 0

    if args.hand_profile:
        used = apply_profile(load_profile(args.hand_profile))
        print(f"hand profile {args.hand_profile}: {', '.join(used) or 'no fields'}",
              file=sys.stderr)

    print("loading corpus ...", file=sys.stderr)
    corpus = load_corpus(args.words, args.cache, args.offline)
    corpus_transitions(corpus)
    params = Params(w_phys=args.w_phys, w_err=args.w_err, w_learn=args.w_learn,
                    w_sym=args.w_sym)
    zones = build_topology()

    if args.self_test:
        print("self-test:")
        return self_test(corpus, params, args.seed)

    obj = Objective(corpus, zones, params)
    breaches = [(n, d) for n, ok, d in geometry_report(obj) if not ok]
    if breaches and not args.quiet:
        print("\n!! GEOMETRY NOT BUILDABLE AS SPECIFIED - the layout below is the "
              "optimiser's answer to an infeasible geometry", file=sys.stderr)
        for name, detail in breaches:
            print(f"   - {name}{': ' + detail if detail else ''}", file=sys.stderr)
        print("", file=sys.stderr)
    ref = random_reference(obj, args.seed)
    obj.ref = ref
    obj.normalise(obj.full(list(range(obj.n))), ref)

    t0 = time.time()
    state, raw, value, history, start_obj = anneal(
        obj, args.seed, args.iters, args.restarts, verbose=not args.quiet)
    elapsed = time.time() - t0

    base_rows = []
    for name, st in baselines(obj, corpus):
        base_rows.append((name, st, obj.full(st)))

    if not args.quiet:
        print_report(obj, corpus, params, state, raw, base_rows, elapsed, args.seed,
                     args.iters, args.restarts)

    if args.out:
        rows = layout_rows(obj, state)
        result = {
            "topology": {
                "pad_mm": [PAD_W, PAD_H],
                "zones": [{"zid": z.zid, "digit": z.digit, "x": z.x, "y": z.y,
                           "width": z.width, "ring": z.ring, "sector": z.sector,
                           "reach": round(math.dist((z.x, z.y), obj.anchor[z.digit]), 1)}
                          for z in zones],
            },
            "assignment": {obj.syms[s]: obj.zones[state[s]].zid for s in range(obj.n)},
            "layout": rows,
            "objective": {
                "components_raw": {c: raw[i] for i, c in enumerate(COMPONENTS)},
                "components_normalised": {c: (raw[i] / ref[i] if ref[i] else 0.0)
                                          for i, c in enumerate(COMPONENTS)},
                "weights": dict(zip(COMPONENTS, obj.weights)),
                "value": value,
                "start_value": start_obj,
                "history": history,
            },
            "throughput_model": obj.time_report(state),
            "symmetry": 1 - raw[3],
            "family_tightness": family_tightness(obj, state),
            "vowel_grid": vowel_grid(obj, state),
            "confusable_pairs": confusable_report(obj, state, 25),
            "baselines": {name: {"raw": dict(zip(COMPONENTS, r)),
                                 "objective": obj.weighted(r),
                                 "time": obj.time_report(st)}
                          for name, st, r in base_rows},
            "corpus": {**corpus.provenance,
                       "syllables_per_token": corpus.syllables_per_token,
                       "syllables_per_word": corpus.syllables_per_word,
                       "phones": corpus.phones_seen},
            "parameters": {k: v for k, v in params.__dict__.items()},
            "geometry": {
                "source": GEOMETRY_SOURCE,
                "hand_profile": HAND_PROFILE or None,
                "pad_mm": [PAD_W, PAD_H],
                "anchors": {k: list(v) for k, v in ANCHORS.items()},
                "joints": {k: list(v) for k, v in JOINTS.items()},
                "thumb_rings": list(THUMB_RING_R), "thumb_fan_deg": list(THUMB_FAN),
                "index_centre": list(INDEX_CENTRE), "index_pitch": INDEX_PITCH,
                "envelope_mm": ENVELOPE_MM, "tangential_penalty": TANGENTIAL_PENALTY,
                "comfort_reach_mm": COMFORT_RING_MM[0],
                "rest_width_mm": REST_WIDTH_MM,
            },
            "provenance": PROVENANCE,
            "search": {"seed": args.seed, "iters": args.iters, "restarts": args.restarts,
                       "seconds": round(elapsed, 2)},
            "disclaimer": "Every number here is a model output of the declared "
                          "parameters. No measurement from any person or device is "
                          "used or claimed.",
        }
        args.out.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"wrote {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
