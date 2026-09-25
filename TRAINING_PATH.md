# Training Path

This document separates four different kinds of progress:

1. sensor and intent safety;
2. deliberate motor tempo;
3. stroke/Plover translation;
4. long-session language-layer performance.

A higher WPM number is not a training result unless the task, error rate, false-trigger rate,
and correction policy are recorded. Current PTH-660 recordings are unstructured free motion;
there is no translated Plover WPM result yet.

## Evidence anchors

These are reference points, not PTH-660 predictions:

| reference | measured result | transfer caveat |
|---|---:|---|
| Twiddler experts | 47 WPM after roughly 25 hours | physical chording device |
| Twiddler novice/protocol cited by TypeAnywhere | 26 WPM after 400 minutes | different protocol and device |
| mini-QWERTY longitudinal study | 31.72 WPM session 1 → 60.03 WPM session 20 | compact mechanical keyboard |
| TapType | 19.2 WPM after 30 minutes, 0.6% CER; experts >25 WPM | wrist-IMU ten-finger system |
| mechanical-steno world record | 360 WPM at 97.23% | mechanical stenotype, not capacitive touch |

The number of personal briefs behind the 360 WPM record is **NOT FOUND** in the fetched
sources. Do not turn it into a required entry count.

## Staged ladder and gates

The gates below are project acceptance gates. They are not literature-derived performance
claims.

### Stage 0 — safety and calibration

**Tasks:** `guided_calibration.py --task noise`, then a short `--task sectors` session.

**Gate:**

- no spontaneous text during 30 minutes of rest/palm/normal posture;
- raw schema and manifest replay successfully;
- per-user rest/palm parameters are recorded;
- any false candidate is visible in the replay and can be retracted.

Do not proceed to speed training while idle safety is unresolved.

### Stage 1 — familiarization and deliberate gestures

**Tasks:** repeated 8-sector cues at the selected radius/return pair, then `--task tempo`.

**Gate:**

- sector direction is decoded from the event vector, not from a block label;
- one-to-one cue/event matching is reported;
- correction/undo is practiced on every error;
- WPM, CER/WER, false events/minute and P95 commit latency are published together.

The synthetic 150–350 ms envelope is not a substitute for this cued gate.

### Stage 2 — stroke and dictionary fluency

**Tasks:** fixed text corpus with a versioned Plover dictionary stack; add user briefs only
after logging untranslates and correction events.
Use `scripts/language_layer_metrics.py` for local untranslate/undo/strokes-per-word counts;
it does not replace a held-out translation corpus or human repair-time measurement.

**Gate:**

- translation accuracy and untranslate rate are measured on a held-out corpus;
- outline collisions are linted;
- the user can recover from `*`/`=undo` without stopping the capture;
- the same raw replay produces the same translated output.

### Stage 3 — sustained language-layer work

**Tasks:** 15-minute blocks with 5-minute breaks, then longer sessions. Alternate normal
text with deliberate correction drills; record effort, pain, numbness and fatigue.

**Gate:**

- raw and corrected WPM, CER/WER, KSPC, corrections/minute and false activations/minute;
- no unresolved pain/numbness/fatigue;
- improvement is reported against the same corpus and dictionary version.

A 360 WPM mechanical-steno record is a human-capability anchor, not a forecast for this
surface. The language layer is a likely multiplier, but the PTH-660 motor and return costs
must still be measured.

## Starter brief deliverable

The first language asset is a small, versioned Plover JSON dictionary, not an untracked list
of shortcuts:

```json
{
  "KAT": "cat",
  "KAT/HROG": "catalog"
}
```

Scope:

- one starter brief set for the target corpus/domain;
- outline collision lint against the stock dictionary;
- explicit priority order for stock, theory, domain and user layers;
- a reproducible build step from source briefs to JSON;
- a changelog and rollback path;
- metrics for strokes/word, untranslate rate, corrections/minute and WPM.

Plover loads dictionaries in priority order and resolves the longest outline first. The
project must therefore keep user briefs conflict-free and reviewable rather than silently
overriding stock entries. The exact production hit rate and brief-count benefit remain
**NOT FOUND**; measure them locally.

## Timeline statement

The 25-hour Twiddler result is a reminder that chording fluency is learned, not configured
in an afternoon. The PTH-660 project should plan in repeated calibration, cued practice,
dictionary growth and correction evaluation. No weekend-sized schedule should be presented
as evidence for 150–250 WPM.

## References

- `W9_STENO_LANGUAGE_LAYER.md` — sourced Plover formats, dictionary stack and unresolved
  language-layer metrics.
- `COMPREHENSIVE_RESEARCH_REPORT.md` — Twiddler, mini-QWERTY and TapType learning curves.
- `CROSS_VALIDATION.md` — 360 WPM human anchor and hardware/model separation.
- `CUED_SESSION_PROTOCOLS.md` — capture order and provenance requirements.
- `REAL_DATA_DECODE.md` — current PTH-660 recordings are free motion, not translated text.
