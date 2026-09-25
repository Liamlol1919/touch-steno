# Synthetic Intent Baseline

`scripts/synthetic_intent_benchmark.py` is a deterministic pre-hardware sanity check for the zero-force event layer. It is **not** a PTH-660 benchmark and contains no user-performance claim.

## What it models

- one-finger tap with a short velocity/displacement impulse;
- one-finger directional drift;
- resting hand with Gaussian sensor noise;
- large-area palm contact;
- a master/index movement with a synchronized ring-finger displacement; a conservative burst guard keeps the first/highest-scoring event and suppresses the dependent contact.

The baseline detector requires:

```text
peak_speed >= min_peak_speed
max_displacement >= max(rest_radius, min_displacement)
min_area <= contact_area < palm_area
min_duration <= event_age <= max_duration
```

The burst guard is intentionally conservative: it prevents a synchronized ring contact from becoming a second character in the fixture, but it would also suppress a genuine two-finger chord unless a separate chord policy runs before it. The real system must distinguish **dependent motion** from **intentional simultaneous chord** using a learned coupling matrix and a chord grammar; this synthetic heuristic is not sufficient.

The current defaults are arbitrary test fixtures, not literature-derived universal thresholds. They must be replaced by a per-user sweep after `scripts/audit_input.py` has captured a real PTH-660 stream.

## Running

```bash
python3 scripts/synthetic_intent_benchmark.py
python3 scripts/synthetic_intent_benchmark.py --json
python3 -m unittest discover -s tests -v
```

The expected test contract is:

- tap and drift produce a detection;
- rest and palm produce no detection;
- a coupled ring contact is not emitted as an independent intent in the fixture.

## Why this exists

A pure velocity threshold is easy to implement but can turn a ring finger dragged by a moving middle finger into a key. A first improvement is to require a stable per-contact baseline, a minimum event duration and a palm-area gate. The next real experiment must measure the same features on PTH-660 and evaluate ROC/PR, false activations per minute and latency.

## Known limitations

- synthetic coordinates are not calibrated to the PTH-660 active area;
- no noise model for finger slip, sweat, pressure or contact-area hysteresis;
- no actual finger-ID confidence;
- no enslavement covariance learned from a person;
- the ring-coupling fixture tests suppression logic only, not anatomical ground truth;
- the detector does not yet implement HMM/LM decoding or Plover output.

Therefore the result must be labelled `synthetic`, never `measured`.
