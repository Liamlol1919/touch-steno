# Decision: hole mask vs. software coupling suppression

**Author:** Agent 2. **Date:** 2026-09-25 05:46 CEST.
**Status:** this closes the question the measurement plan deliberately left open
("Loch-Maske vs. Zero-Lift-Vektor … erst damit sind Schwellen *gemessen statt geraten*").

## Decision

**Build the software coupling-suppression path first. Do not build a hole mask.**

Not because a mask cannot help — because the evidence says the mask targets the coupling we
can already remove in software, and pays speed for it. The single coupling class that
software cannot remove is thumb↔thumb, and that one is cheap to isolate geometrically later
if the measurement still calls for it.

## The evidence, in the order that decided it

### 1. We measured which couplings are large

`MEASURED_BIOMECHANICS.md` §4 and `VECTOR_DESIGN_CRITIQUE.md` §4a–4b, on three PTH-660
sessions with 20 distinct contacts:

| pair class | β (magnitude) | r² (predictability) | suppressible by signed linear subtraction? |
|---|---:|---:|---|
| long-finger neighbours (55↔56↔57, 61↔62↔64) | 0.63–0.74 | 0.62–0.92 | **yes**, residual 0.29–0.62 |
| cross-hand / whole-body (73→55, 73→56) | — | 0.72–0.74 | **yes**, despite being mirrored |
| thumb ↔ thumb (81↔82) | 0.49–0.63 | **0.10–0.25** | **no** — 87–95 % survives |
| thumb ↔ finger rows | 0.01–0.04 | — | already below the rest noise floor |

The expensive couplings — the ones that corrupt steno chords — are the *correctable* ones.
A per-pair signed regression removes 62–92 % of the finger-row follower energy.

### 2. The filter works in practice, not just in theory

`scripts/intent_filter.py` on the ten-finger session: **175 follower contacts suppressed**
with r² between 0.55 and 0.93, zero fingers lost that should have fired. On the thumb session
it suppresses **zero** — exactly what the r² = 0.10–0.25 measurement predicted. The filter's
behaviour is the measurement, not a tuned heuristic.

### 3. The literature says the mask buys accuracy and costs speed

W7 (`W7_PHYSICAL_MASKS_HAND_ERGONOMICS.md`, sourced numbers only):

- one controlled anchored-hand touchscreen study (avionic Fitts, n = 24, 0.8–2 cm targets)
  found **no benefit of a bezel anchor over freehand**, while adding vibration *raised* the
  error rate from 10.3 % to 16.6 % (https://doi.org/10.1080/10447318.2023.2212225);
- keyguards improved accuracy at a cost in speed (both p < 0.01) in an n = 1 study;
- a software "invisible keyguard" cut overlap errors by 50–75 % without hardware;
- gesture keyboards already cut errors 37–52 % in software alone;
- **no** published capacitive hole-mask finger-rest accuracy number exists, and capacitive
  sensing cannot see through thick insulating walls without retuning.

### 4. The measured baseline the mask would have to beat is already low

The rest state is cleaner than the design assumed. With an adaptive ~200 ms baseline
(`REST_MODEL.md`), 17 resting contacts produced a worst-case residual of **5.04 mm** and a
worst-case supra-threshold run of **1 frame** at 40 mm/s. A detector at 2 frames of
drift-relative motion has zero false activations on every resting contact we recorded. A
physical mask is a second line of defence against a problem the software path already solves
in the measurements we have.

## What the mask would still be for

If, after training, the remaining false-trigger rate is dominated by the thumb pair, the
minimal geometry is **thumb separation only** — not a full finger-row mask. The
finger-row part of a mask is aimed at couplings that per-pair regression already removes at
r² > 0.6, so it would pay speed cost for suppression we can do for free.

## What would reverse this decision

Stated in advance, so the decision is falsifiable rather than rhetorical:

1. **Chord-on-cue session** (`guided_calibration.py --task chord`): if a real two-thumb chord
   is *not* separable from the mirrored drag, and the thumb-pair r² stays ≤ 0.25 across
   sessions, then thumb geometry is justified and the mask moves up the roadmap.
2. **Training-session data**: if a trained user's rest residual rises far above 5.04 mm, the
   software idle gate weakens and a physical rest/stop gains value.
3. **A direct mask prototype measured against bare touch** — W7's recommendation and ours:
   report substitution/deletion rate and WPM for both, same operator, same targets. Until
   that exists, any claim in either direction is opinion.

## Cost check

| path | what it costs | what it buys | evidence status |
|---|---|---|---|
| per-pair coupling regression | a calibration session per user | removes 62–92 % of the dominant coupling | **measured on 3 sessions** |
| adaptive drift baseline | a sliding window parameter | 4× lower latency at equal false-trigger rate | **measured on 3 sessions** |
| thumb separation geometry | a 3D-printed part, possible retuning | addresses the one r² ≤ 0.25 case | **not measured, no literature** |
| full hole mask | 3D part + calibration + speed cost | targets already-suppressible coupling | literature says small gain, real speed cost |

The ordering follows the evidence, and the two cheapest items at the top are already
implemented and measured.

## Related

- `MEASURED_BIOMECHANICS.md` — the measurements
- `VECTOR_DESIGN_CRITIQUE.md` §4, §4a, §4b — coupling structure and predictability
- `REST_MODEL.md` — the drift baseline that makes the idle gate safe
- `MEASURED_INTENT_FILTER.md` — the filter that implements the suppression
- `CROSS_VALIDATION.md` §1.3, §1.7 — literature cross-checks and the axis-alignment rule
- W7 — the physical-aid evidence with its NOT FOUND gaps
- Issues #1–#6 — open items for agent 1
