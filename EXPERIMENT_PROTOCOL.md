# Experiment Protocol: PTH-660 Zero-Force Intent Decoder

## Objective

Measure whether a continuous capacitive surface can separate:

- intentional finger taps/drifts,
- resting contacts,
- palm contact,
- anatomically coupled ring/little-finger motion,
- actual errors and correction cost.

The experiment does not assume that 150–250 WPM is achievable. It measures a calibrated baseline and reports uncertainty.

## Preconditions

- fixed PTH-660, USB and Bluetooth tested separately;
- same tablet firmware, kernel, libinput, Wacom driver and compositor;
- known physical dimensions and active area;
- user consent for telemetry;
- no other touch input used during test;
- record time with `date -Is` and a monotonic event timestamp.

## Phase A — Device capability audit

1. Connect PTH-660 and run:

```bash
python3 scripts/audit_input.py
```

2. Identify the tablet event node by `name`, `phys`, `ID_INPUT_TOUCH`/`ID_INPUT_TABLET` and `libinput list-devices`.
3. Run a 30-second capture in five states: idle, palm rest, one finger, two fingers, five fingers:

```bash
python3 scripts/audit_input.py --device /dev/input/eventN \
  --watch --seconds 30 --output data/pth-touch-STATE.jsonl
```

4. Confirm whether the stream includes `ABS_MT_SLOT`, `ABS_MT_TRACKING_ID`, `ABS_MT_POSITION_X/Y`, `ABS_MT_TOUCH_MAJOR/MINOR`, `ABS_MT_PRESSURE`, `BTN_TOUCH`, pen proximity and tool type.
5. Do not claim contact area, pressure or finger identity if the axis is absent.

## Phase B — Rest baseline (no text decoding)

Collect 30 minutes of:

- hand floating above surface;
- palm placed on surface;
- full hand resting with fingers relaxed;
- forearm supported, fingers hovering;
- one finger touching without intent;
- involuntary finger adjustments.

For each active contact calculate:

- duration;
- median position and covariance;
- peak speed;
- mean/median area if present;
- number of contact-ID changes;
- contact count and distance to other contacts.

Primary outcome: false intent activations per minute, not just contact count.

## Phase C — Micro-intent classes

Use randomized prompts, 10–20 repetitions each:

| Class | Action |
|---|---|
| tap-1 | one finger taps and returns to same neutral point |
| tap-2 | two fingers tap together or near-simultaneously |
| drift-N | one finger moves N/E/S/W by a short displacement |
| drift-8 | one finger moves through one of eight sectors |
| chord | selected two/three-finger combination |
| rest | hand stays placed and relaxed |

Record video marker or external key for ground truth. The user should not have to look at the tablet for the eyes-free condition.

## Phase D — Candidate thresholds

Do not select a single universal threshold — and note that **the original sweep grid was
below the measured noise floor**. Measured on this PTH-660 over three sessions
(`MEASURED_BIOMECHANICS.md`): resting contacts reach speed p99 = 57.4 mm/s, per-frame step
p99 = 0.56 mm (max 1.48 mm) and net drift 11.96 mm over 20 s. Sweep per-user, with the grids
below, which start where the measurement says the interesting part begins:

```text
peak_speed:       20, 30, 40, 60, 80, 120 mm/s   (below 20 is inside the rest noise)
persistence:      5, 8, 12 frames                (8 = 88ms, the measured evidence floor)
displacement:     windowed, 4, 8, 12 mm           (NEVER since touch-down: rest drifts 11.96mm)
area_rise:        0.25, 0.5, 1.0, 1.5 x baseline
hold_release:     20, 40, 80, 120, 200 ms
deadband:         0.5, 1, 2, 3 mm                 (rest step p99 is 0.56mm, so 0.5 is below it)
```

The gate and the persistence window are **not independent knobs**: the measured resting
run is 13 frames at 20 mm/s, 7 at 40 mm/s and 5 at 60 mm/s, so any setting whose window
is at or below the resting run at that gate will fire on a resting hand. The current
operating point is 40 mm/s with 8 frames, which has **one frame of margin** — see
`SEPARATION_MODEL.md`, which also gives the rule for turning a per-user rest-floor session
into a gate.

For every setting calculate:

- precision/recall/F1 for intentional events;
- false activations/minute;
- median and P95 latency;
- confusion matrix by contact count;
- performance separately for each finger and hand;
- performance under palm rest and ring-finger coupling.

Select operating point by a declared objective, e.g. false activation < 0.2/min while recall > 0.90, then evaluate speed at that point. Do not optimize only for WPM.

## Phase E — Decoder comparison

Compare at least:

1. position-only nearest target;
2. velocity-peak + deadband;
3. area-rise + velocity;
4. per-finger geometric classifier;
5. probabilistic tap-sequence + LM;
6. Plover stroke adapter.

For every test publish raw and corrected WPM, CER/WER, KSPC, latency, corrections, false activations and comfort. A sentence-level LM is disabled for a baseline run and enabled for a second run.

## Phase F — Long-session ergonomics

- 15-minute blocks with 5-minute breaks;
- record perceived hand/arm effort (0–10) before and after;
- compare supported forearm vs unsupported;
- compare no overlay vs passive reference strips;
- inspect contact drift over time;
- stop if pain, numbness or unusual fatigue appears.

## Minimal data schema
Raw contact-frame JSONL uses the versioned contract in [RAW_FRAME_SCHEMA.md](RAW_FRAME_SCHEMA.md).
The per-contact experiment record below is a separate labelled/derived schema.

```json
{
  "session_id": "...",
  "device": "PTH-660",
  "driver_version": "...",
  "kernel": "...",
  "user": "pseudonymous-id",
  "state": "rest|tap|drift|chord",
  "t_mono_ms": 0,
  "slot": 0,
  "tracking_id": 0,
  "x": 0,
  "y": 0,
  "area_major": null,
  "area_minor": null,
  "pressure": null,
  "ground_truth": "unknown",
  "decoder": "velocity-v1",
  "confidence": 0.0
}
```

## Stop conditions

- repeated accidental text that cannot be immediately undone;
- loss of contact identity during a held hand pose;
- input latency blocks phrase rhythm;
- user reports pain, numbness or worsening fatigue;
- driver behavior changes after sleep/reconnect or pen proximity.
