#!/usr/bin/env python3
"""WPM event-rate budget: how many events/s does a 150-250 WPM target need?

Inputs are measured on this PTH-660 (see MEASURED_BIOMECHANICS.md and
MEASURED_INTENT_FILTER.md) or taken from published benchmarks in CROSS_VALIDATION.md.
The model computes required event rates. The 88 ms persistence window is latency and
minimum supra-threshold evidence; it is **not** an event-rate ceiling.

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


def required_event_rate_hz(target_wpm: float, syllables_per_word: float,
                           events_per_syllable: float) -> float:
    """Return the sustained event rate required by an encoding."""
    return (target_wpm / 60.0) * syllables_per_word * events_per_syllable


def wpm_for(events_hz: float, syll_per_word: float, events_per_syll: float) -> float:
    syll_hz = events_hz / events_per_syll
    words_hz = syll_hz / syll_per_word
    return words_hz * 60.0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    rows = []
    for target in TARGETS_WPM:
        for syll in SYLL_PER_WORD:
            for eps in EVENTS_PER_SYLL:
                need_events_hz = required_event_rate_hz(target, syll, eps)
                rows.append({
                    "target_wpm": target,
                    "syllables_per_word": syll,
                    "events_per_syllable": eps,
                    "required_events_per_s": round(need_events_hz, 2),
                    "vs_measured_free_motion": round(
                        need_events_hz / MOVE_EVENT_RATE_HZ, 2),
                })
    out = {
        "measured": {
            "hz": HZ, "event_evidence_window_ms": EVENT_MS,
            "rest_run_max_ms": REST_RUN_MAX_MS,
            "free_motion_event_rate_hz": MOVE_EVENT_RATE_HZ,
            "rest_drift_mm_20s": DRIFT_MM_20S,
            "rest_speed_p99_mm_s": REST_SPEED_P99,
            "mover_speed_p99_mm_s": MOVER_SPEED_P99,
        },
        "event_evidence_window_is_rate_ceiling": False,
        "synthetic_sweep_note": (
            "150-350 ms gestures were detected with 100% direction accuracy in the "
            "sub-gate-return generator; realized cue rates were 1.01-1.48 Hz, while "
            "1-6 Hz was only the requested grid"
        ),
        "wpm_if_day0_free_motion_1_event_per_syll_1_5_syll": round(
            wpm_for(MOVE_EVENT_RATE_HZ, 1.5, 1.0), 0),
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
    print(f"  event-evidence window             {EVENT_MS:.0f} ms "
          f"({EVENT_MS/(1000.0/HZ):.0f} frames; latency, not a rate ceiling)")
    print(f"  longest resting supra-thr run    {REST_RUN_MAX_MS:.0f} ms  (detector must exceed this)")
    print(f"  day-0 free-motion event rate     {MOVE_EVENT_RATE_HZ:.2f} events/s")
    print(f"  resting speed p99 / mover p99    {REST_SPEED_P99:.0f} / {MOVER_SPEED_P99:.0f} mm/s")
    print(f"\nWPM at day-0 free motion, 1 ev/syll, 1.5 syll/word = "
          f"{out['wpm_if_day0_free_motion_1_event_per_syll_1_5_syll']:.0f}")
    print("\nREFERENCE (published): surface/two-thumb "
          f"{REF_PUB_SURFACE:.0f} | TapType-IMU {REF_TAPTYPE:.0f} | "
          f"Twiddler-experts {REF_TWIDDLER:.0f} WPM")
    print("\nWHAT EACH TARGET NEEDS (required events/s and multiple over day-0 free motion)")
    print("|target|syl/word|ev/syll|need ev/s|x free-motion|")
    print("|---:|---:|---:|---:|---:|")
    for r in rows:
        print(f"|{r['target_wpm']}|{r['syllables_per_word']}|{r['events_per_syllable']}|"
              f"{r['required_events_per_s']:.2f}|{r['vs_measured_free_motion']:.2f}x|")
    print("\nREADING: 88 ms sets evidence/latency, not a maximum event rate. The corrected")
    print("synthetic sweep realized 1.01-1.48 Hz for 150-350 ms gestures; the requested")
    print("1-6 Hz grid is not measured throughput. Targets need 1.5-6.5x the day-0 free-")
    print("motion rate, but trained deliberate throughput remains unmeasured and must be")
    print("gated by a cued tempo session rather than inferred from detector latency.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
