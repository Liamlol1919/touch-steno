#!/usr/bin/env python3
"""WPM ceiling model: how many events/s does a 150-250 WPM target actually need?

Inputs are all measured on this PTH-660 (see MEASURED_BIOMECHANICS.md and
MEASURED_INTENT_FILTER.md) or taken from the published benchmarks in
CROSS_VALIDATION.md. The model answers one question: given the measured event supply
and the measured per-event cost, what corrected WPM range is physically reachable, and
which assumption has to be true for the 250 WPM target to hold?

Run:
    python3 scripts/wpm_ceiling.py
    python3 scripts/wpm_ceiling.py --json
"""
from __future__ import annotations

import argparse
import json

# --- measured inputs (PTH-660, this hand, three sessions) ---
HZ = 91.0                 # median frame rate
EVENT_MS = 88.0           # persistence detector cost (8 frames)
REST_RUN_MAX_MS = 77.0    # longest resting supra-threshold run (must stay below)
MOVE_EVENT_RATE_HZ = 2.56  # measured free-motion events/s (10 fingers down)
DRIFT_MM_20S = 11.5       # resting net drift over 20 s
REST_SPEED_P99 = 57.0     # resting speed p99 (mm/s)
MOVER_SPEED_P99 = 130.0   # mover speed p99 (mm/s)

# --- target assumptions under test ---
TARGETS_WPM = (150, 200, 250)
# syllables per word, and events per syllable, for a 3-part syllable architecture
SYLL_PER_WORD = (1.5, 2.0)
EVENTS_PER_SYLL = (1.0, 1.5, 2.0)  # onset-only, onset+vowel, onset+vowel+coda

# published reference points
REF_PUB_SURFACE = 38.0   # two-thumb mobile typing (n=37,370)
REF_TAPTYPE = 70.6       # 10-finger passive tap, IMU, 2.5h/5d
REF_TWIDDLER = 47.0      # chorded experts, ~25h


def event_ceiling_hz() -> float:
    """Max event rate the 88 ms detector can deliver."""
    return 1.0 / (EVENT_MS / 1000.0)


def wpm_for(events_hz: float, syll_per_word: float, events_per_syll: float) -> float:
    syll_hz = events_hz / events_per_syll
    words_hz = syll_hz / syll_per_word
    return words_hz * 60.0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    ceiling = event_ceiling_hz()
    rows = []
    for target in TARGETS_WPM:
        for syll in SYLL_PER_WORD:
            for eps in EVENTS_PER_SYLL:
                need_events_hz = (target / 60.0) * syll * eps
                rows.append({
                    "target_wpm": target,
                    "syllables_per_word": syll,
                    "events_per_syllable": eps,
                    "required_events_per_s": round(need_events_hz, 2),
                    "vs_detector_ceiling": round(need_events_hz / ceiling, 2),
                    "vs_measured_free_motion": round(need_events_hz / MOVE_EVENT_RATE_HZ, 2),
                })
    out = {
        "measured": {
            "hz": HZ, "event_cost_ms": EVENT_MS,
            "rest_run_max_ms": REST_RUN_MAX_MS,
            "free_motion_event_rate_hz": MOVE_EVENT_RATE_HZ,
            "rest_drift_mm_20s": DRIFT_MM_20S,
            "rest_speed_p99_mm_s": REST_SPEED_P99,
            "mover_speed_p99_mm_s": MOVER_SPEED_P99,
        },
        "detector_event_ceiling_hz": round(ceiling, 2),
        "wpm_if_ceiling_and_1_event_per_syll_1_5_syll": round(wpm_for(ceiling, 1.5, 1.0), 0),
        "wpm_if_measured_free_motion_1_event_per_syll_1_5_syll": round(wpm_for(MOVE_EVENT_RATE_HZ, 1.5, 1.0), 0),
        "rows": rows,
        "reference_points_wpm": {
            "published_surface_two_thumb": REF_PUB_SURFACE,
            "taptype_10finger_imu": REF_TAPTYPE,
            "twiddler_experts": REF_TWIDDLER,
        },
    }
    if args.json:
        print(json.dumps(out, indent=2))
        return 0
    print("MEASURED INPUTS (PTH-660, this hand)")
    print(f"  frame rate                       {HZ:.0f} Hz")
    print(f"  detector event cost              {EVENT_MS:.0f} ms "
          f"({EVENT_MS/(1000.0/HZ):.0f} frames)")
    print(f"  longest resting supra-thr run    {REST_RUN_MAX_MS:.0f} ms  (detector must exceed this)")
    print(f"  free-motion event rate           {MOVE_EVENT_RATE_HZ:.2f} events/s")
    print(f"  resting speed p99 / mover p99    {REST_SPEED_P99:.0f} / {MOVER_SPEED_P99:.0f} mm/s")
    print(f"\n  detector ceiling (1/{EVENT_MS:.0f}ms) = {ceiling:.1f} events/s")
    print(f"  WPM at ceiling, 1 ev/syll, 1.5 syll/word = {out['wpm_if_ceiling_and_1_event_per_syll_1_5_syll']:.0f}")
    print(f"  WPM at MEASURED free motion, same assumptions = {out['wpm_if_measured_free_motion_1_event_per_syll_1_5_syll']:.0f}")
    print(f"\nREFERENCE (published): surface/two-thumb {REF_PUB_SURFACE:.0f} | "
          f"TapType-IMU {REF_TAPTYPE:.0f} | Twiddler-experts {REF_TWIDDLER:.0f} WPM")
    print("\nWHAT EACH TARGET NEEDS (events/s required, and the multiple over ceiling & free motion)")
    print("|target|syl/word|ev/syll|need ev/s|x ceiling|x free-motion|")
    print("|---:|---:|---:|---:|---:|---:|")
    for r in rows:
        print(f"|{r['target_wpm']}|{r['syllables_per_word']}|{r['events_per_syllable']}|"
              f"{r['required_events_per_s']:.2f}|{r['vs_detector_ceiling']:.2f}x|"
              f"{r['vs_measured_free_motion']:.2f}x|")
    print("\nREADING: targets at or below 150 WPM need a sustained event rate that the")
    print("measured free-motion session (2.56/s) does not reach, unless each syllable is")
    print("encoded in ~1 event and the trained user produces ~5-7 events/s deliberately.")
    print("The sensor has the headroom (11.4/s ceiling); the human event rate is the")
    print("binding constraint and is a training question, now measurable.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
