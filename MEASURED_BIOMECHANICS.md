# Measured Biomechanics — PTH-660, this machine, this hand

**Author:** Agent 2 (laptop: `commindv2`). **Date:** 2026-09-25 05:36 CEST.
**Purpose:** replace the *guessed* thresholds in `SYNTHETIC_BASELINE.md` and
`EXPERIMENT_PROTOCOL.md` with measurements taken on the actual PTH-660
(Wacom Intuos Pro M, 224 × 148 mm, 40 units/mm) over three sessions.

**Everything in this document is `measured` unless marked `proxy` or `literature`.**
Agent 1's report is `literature`; this document is the hardware layer it asks for
(`COMPREHENSIVE_RESEARCH_REPORT.md:194` — *"PTH-660-Eventdaten auf dem
Ziel-Linux-System messen"*).

## 0. Provenance and privacy

| item | value |
|---|---|
| device | `Wacom Intuos Pro M Finger` = `/dev/input/event19` (evdev, MT protocol B) |
| driver path | `input-wacom` via `/dev/input`, reader in `commindv2/src/wacom_touch.py` |
| coordinate unit | 1 mm = 40 units; `TOUCH_MAJOR` = 2 units/mm |
| capture tool | `scripts/kinematics.py` (port of `commindv2/tools/kinematics.py`), JSONL, one line per SYN_REPORT |
| sessions | `test.jsonl` (39.4 s, 3845 frames, 20 contacts, 10 fingers down), `test-daumen.jsonl` (18.6 s, 1643 frames, 14 contacts, thumb-driven), `test-zeige.jsonl` (24.0 s, 1400 frames, 15 contacts, index-driven) |
| reproduction | `python3 scripts/real_session_evidence.py <session.jsonl> ...` |
| raw traces | **not committed** — they are per-user biometric traces. Only derived statistics are in this repo. |

`synthetic_intent_benchmark.py` is a fixture; this document is what happens when
the same questions are asked of the real device.

## 1. Frame timing (measured)

| session | frames | duration | median | dt p01 | dt p50 | dt p99 | dt max |
|---|---:|---:|---:|---:|---:|---:|---:|
| test | 3845 | 39.4 s | **91 Hz** | 7.8 ms | 10.9 ms | 19.0 ms | 114 ms |
| test-daumen | 1643 | 18.6 s | **91 Hz** | 7.7 ms | 10.9 ms | 30.1 ms | 660 ms |
| test-zeige | 1400 | 24.0 s | **91 Hz** | 7.7 ms | 11.0 ms | 101 ms | 259 ms |

Consequences for the decoder design:

- **91 Hz, not 120 Hz.** A 10 ms assumption in any model is 14 % optimistic. At 250 WPM a
  word is 240 ms ≈ 22 frames (`COMPREHENSIVE_RESEARCH_REPORT.md:118`) — that is the entire
  budget per word, including the decoder's own decision time.
- **No burst pathology.** dt never dropped below 6.9 ms, so single-frame velocity computed
  from callback timestamps is *not* contaminated by batch drains. `dt` outliers
  (114–660 ms) come from the kernel dropping frames under load; a decoder that
  divides by dt must guard `dt` (e.g. ignore `dt > 50 ms`, they are stale-duplicate frames,
  not motion).
- Timestamps are `time.monotonic()` at the `on_contacts` callback, i.e. **processing** time,
  not device time. Systematic offset cancels in differences, jitter does not.

## 2. Rest-state noise floor (measured, `proxy` labels)

Contacts labelled `REST` were, by session protocol, not being driven. Contacts with
`path_mm > 100` are `MOVER`; `path_mm < 20` is `REST`; the band between is excluded as
ambiguous. Contacts shorter than 50 frames are excluded (hand placement, see §6).

| quantity | REST (n = 17 contacts) | MOVER (n = 20 contacts) |
|---|---:|---:|
| per-frame step p99 (worst contact) | **0.56 mm** | 1.92 mm |
| per-frame step max (worst contact) | **1.48 mm** | 2.76 mm |
| per-frame speed p99 (worst contact) | **57.4 mm/s** | 208 mm/s |
| per-frame speed max (worst contact) | **190 mm/s** | 309 mm/s |
| net drift over the session (worst contact) | **11.5 mm** | 30.6 mm |
| session mean speed (worst contact) | 1.30 mm/s | 40.5 mm/s |

Three findings that change the architecture:

1. **A resting finger emits 57 mm/s and 1.5 mm steps.** Not theory — measured worst case
   across 17 resting contacts. Any single-frame velocity gate below ~60 mm/s will
   false-trigger on a resting hand.
2. **A resting finger drifts 11.5 mm within 20 s** (contacts 143/144/145 in
   `test-zeige.jsonl`, drift 10.6/11.5/12.3 mm, sustained ≈ 0.5 mm/s). Therefore
   *net displacement since touch-down* is not a valid feature. `EXPERIMENT_PROTOCOL.md:86`
   sweeps displacement up to 12 mm — a threshold anywhere in 1–12 mm is exceeded by a
   passive finger given enough time. Displacement must be measured **inside a short
   window** (see §3), never since contact start.
3. **Resting contacts are not stationary in the "quiet" sense**: they emit isolated
   supra-threshold frames when the hand settles or repositions. Peak-detection without a
   temporal condition is not viable.

## 3. What actually separates them: persistence, not peak

Candidate rule: a contact fires when it has **k consecutive frames with speed ≥ v**.
Measured longest such run per contact (pooled over the three sessions):

| v (mm/s) | worst REST run | best MOVER run | rule (v, k) with k = 5 | k = 8 | k = 12 |
|---:|---:|---:|---|---|---|
| 10 | 15 | 278 | REST fires | REST fires | REST fires |
| 20 | 13 | 175 | REST fires | REST fires | REST fires |
| 30 | 7 | 168 | REST fires | **clean** | **clean** |
| 40 | 7 | 147 | REST fires | **clean** | **clean** |
| 60 | 5 | 53 | REST fires | **clean** | **clean** |
| 80 | 4 | 23 | **clean** | **clean** | **clean** |
| 100 | 3 | 19 | **clean** | **clean** | **clean** |

**Recommended first operating point: v = 40–60 mm/s with k = 8 consecutive frames
(≈ 88 ms at 91 Hz).** Measured effect on this hardware: zero false activations on
all 17 resting contacts (their worst run is 7 frames at 30–40 mm/s, 5 frames at 60 mm/s),
while every one of the 20 driven contacts still fires. Note this is an *event-level*
criterion with a fixed cost of ~88 ms latency — that latency is the price of a
false-trigger-free rest state, and it must be budgeted explicitly against the
0.24 s/word of a 250 WPM target.

Rules at the aggressive end (v = 80–100 mm/s, k = 5) also separate cleanly, with
run-length margin 4 → 3 vs 23 → 19. Recommend starting conservative (v = 40, k = 8) and
tightening only after a session with deliberate *slow* intentional strokes, which these
three sessions do not contain.

## 4. Coupling: measured enslavement matrix (proxy label: mover by protocol)

`coupling[a][b]` = mean per-frame step of `b` over the frames where `a` has the largest
step; normalised by `a`'s own mean step this is a gain `β_b←a`. Shown: the strongest
couplings per driven contact.

**test.jsonl — all ten fingers resting, fingers driven (worst case for enslavement):**

| mover a | own step (mm/frame) | strongest followers (β) |
|---|---:|---|
| 56 | 0.801 | 57: 67 %, 55: 66 %, 66: 40 %, 61: 32 %, 64: 31 % |
| 64 | 0.776 | 61: 68 %, 62: 62 %, 66: 35 %, 57: 33 %, 63: 32 % |
| 62 | 0.748 | 64: 54 %, 61: 47 %, 63: 32 %, 55: 32 %, 65: 31 % |
| 55 | 0.542 | 56: 50 %, 57: 38 %, 62: 27 %, 63: 24 % |
| 61 | 0.559 | 64: 65 %, 62: 47 %, 63: 37 %, 65: 32 % |

**test-daumen — thumbs driven, fingers resting:**

| mover a | own step | strongest followers (β) |
|---|---:|---|
| 81 | 0.401 | 82: 56 %, then **80: 4 %, 77: 2 %, 78: 2 %, 83: 1 %** |
| 82 | 0.435 | 81: 39 %, then **80: 2 %** |
| 88 | 0.468 | 87: 4 %, 78: 3 %, 83: 2 % |
| 90 | 0.440 | 87: 2 %, 80: 1 % |

**test-zeige — index fingers driven:**

| mover a | own step | strongest followers (β) |
|---|---:|---|
| 141 | 0.425 | 142: 39 %, 139: 12 %, 138: 10 %, 140: 8 %, 146: 3 % |

The structural result, which is the first hard evidence in this project for the
hole-mask-vs-zero-lift question:

- **Intra-finger-row coupling is 20–68 %.** Driven by a middle finger, its neighbours move
  up to two-thirds as far. This is the phenomenon that has to be solved.
- **Thumb-driven motion couples to the finger row at 1–4 %** (0.005–0.017 mm/frame,
  i.e. 0.4–1.5 mm/s — below the rest noise floor of §2).
- **Cross-group coupling is symmetric and negligible** in both directions. Anatomical
  groups are mechanically independent at this scale.
- The thumb pair itself couples at 39–56 % when both thumbs are down and driven.

Design consequences:

1. Coupling is **local and group-structured**, not global. A global "zero-lift vector"
   over all contacts spends effort on the 1–4 % couplings that are already below the
   noise floor.
2. A **physical mask only has to separate adjacent fingers within a row** (the
   20–68 % band). Separating thumbs from fingers is worth ≈ 1–4 %, i.e. nothing at the
   measured noise floor. This is the first measured argument *against* spending mask
   complexity on thumb isolation.
3. The coupling matrix is **per-user and per-posture** and must be measured, not assumed.
   These numbers come from one hand in three postures over ~80 s total.

## 5. Corrections to the current documents (with citations)

| document / line | claim | measured correction |
|---|---|---|
| `EXPERIMENT_PROTOCOL.md:85` | sweep `peak_speed: 2, 4, 8, 12, 20, 40 mm/s` | the whole range up to 40 mm/s is **inside the resting noise floor** (rest p99 ≤ 57 mm/s, rest speed max 190 mm/s). Sweep should start at 40 and extend to 200; the informative band is 40–120 mm/s. |
| `EXPERIMENT_PROTOCOL.md:86` | sweep `displacement: 1, 2, 3, 5, 8, 12 mm` | a resting finger drifts **11.5 mm** in 20 s. Since-touch-down displacement is not separable; use windowed displacement with k ≥ 8 frames (≈ 88 ms). |
| `EXPERIMENT_PROTOCOL.md:89` | sweep `deadband: 0.5, 1, 2, 3 mm` | rest per-frame step p99 is 0.56 mm and max 1.48 mm; rest drift reaches 11.5 mm. A 0.5–1 mm deadband is below noise; ≥ 2 mm is above the rest step max only per frame, not over time. Deadband alone cannot work. |
| `scripts/synthetic_intent_benchmark.py:31-38` | `rest_radius=1.2, min_peak_speed=20, min_displacement=1.5, min_duration=0.035` | `min_peak_speed=20` would fire on resting contacts (measured rest runs of 13 frames at 20 mm/s). `min_duration=35 ms` ≈ 3 frames is below the 8-frame persistence needed. These are fixtures; they should carry the measured defaults or cite §3. |
| `COMPREHENSIVE_RESEARCH_REPORT.md:86` | "Schwellen wie 3–8 mm/s oder 10–30 ms sind Startwerte" | 3–8 mm/s is **two orders of magnitude below** the measured rest p99. Replace the placeholder with the §3 operating point or delete it. |
| `SYNTHETIC_BASELINE.md:22` | "would also suppress a genuine two-finger chord unless … learned coupling matrix" | still true, and now quantified: a coupling matrix can be estimated from the 80 s of data in this repo (§4). Recommend a measured `β` prior with a chord lexicon on top. |
| `COMPREHENSIVE_RESEARCH_REPORT.md:302` | "Ringfinger-Kontakte als *dependent* unterdrücken" | measurement supports a **ratio** rule rather than a fixed finger class: neighbour β up to 68 %, so "suppress ring" must be `β_b←a > 0.5` and not finger identity — the same contact can be the mover in another frame. |
| `COMPREHENSIVE_RESEARCH_REPORT.md:13` | "150–250 WPM nicht evidenzbasiert" | agreed and reinforced: the measured event latency floor is ~88 ms (§3) plus decoder time, i.e. ≤ 11 events/s before decoding. Document the budget, not a WPM number. |

## 6. Known measurement artefacts (found by the tool, not by eye)

1. **Reader init artefact.** `WacomTouchReader` seeds a new tracking ID with
   `[0, 0, 0]` and reports 1–3 SYN frames before `ABS_MT_POSITION_X/Y` arrive, e.g.
   `test-zeige.jsonl` frame 624: `[0,0,0]`, `[0,135.75,0]`, then `[223.6,135.75,0]`.
   Unfiltered, this produces a 260 mm phantom drift and a 19 972 mm/s phantom peak
   (observed). `scripts/kinematics.py::_strip_uninit_leads` drops leading samples until
   both coordinates are non-zero. **Every future analysis tool needs this filter**;
   `audit_input.py` and any ROC script must apply it or it will report nonsense.
2. **Resting contacts that move.** Contacts 143/144/145 (`test-zeige`) are labelled REST
   but drift 10–12 mm; contact 136 is 9 frames long and contains a 134 mm/s frame
   (hand placement). Proxy labels are per contact, so placement and slow settling leak
   into the REST statistics. This makes the false-trigger estimate **conservative**,
   which is the direction we want, but it must be stated wherever REST numbers are used.
3. **Frame drops.** dt up to 660 ms. Any dt-normalised quantity needs a guard; a
   "movement" across a dropped-frame gap is not a measurement.

## 7. What is still missing (open measurement work)

- No session with **deliberately slow intentional strokes**. The rest/mover separation in
  §3 therefore has no measured lower bound on mover speed; a user who intentionally
  strokes at 50 mm/s is untested.
- No **cross-session** coupling stability: β measured in one 18 s session has no
  repeat-measurement error bar yet.
- No **contact-area / TOUCH_MAJOR** statistics in this document. The reader exposes
  `TOUCH_MAJOR` in mm (`MAJOR_UNITS_PER_MM=2`); palm gate currently uses
  `PALM_MAJOR_MM=14`. That constant is a `compendium` hypothesis, not a measurement.
  Adding a major-column histogram to `kinematics.py` is the cheapest next measurement.
- No **chord** data: nothing here says whether a real two-finger chord is
  distinguishable from a mover+follower pair, which is the open question in
  `SYNTHETIC_BASELINE.md:22`. Requires a session where chords are performed on cue.

## 8. Reproduction

```bash
# capture (tablet attached)
python3 scripts/kinematics.py --record --seconds 20 --out session.jsonl
python3 scripts/kinematics.py --analyze session.jsonl
python3 scripts/kinematics.py --diff a.jsonl b.jsonl

# evidence tables used in this document
python3 scripts/real_session_evidence.py session-a.jsonl session-b.jsonl session-c.jsonl
python3 scripts/real_session_evidence.py --json session-a.jsonl > evidence.json
```

`scripts/kinematics.py` is stdlib-only and imports `wacom_touch` lazily, so
`--analyze` / `--diff` / the evidence script run without evdev or a tablet.
