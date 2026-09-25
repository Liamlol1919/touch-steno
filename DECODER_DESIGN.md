# Decoder Design: From PTH-660 Contacts to Reversible Strokes

## Scope

This document defines the first production-shaped decoder boundary. It is an implementation design, not a claim that the thresholds have been validated on a PTH-660.

## Non-negotiable invariants

1. No text is emitted from a single low-confidence contact.
2. Every output has a recoverable provenance record and an undo path.
3. Resting hand and palm contacts are not silently reinterpreted as key presses.
4. A contact-ID change is an event boundary, not an invisible reset.
5. A language model may reorder candidates, but it may not hide a sensor-level failure.
6. The same raw event stream must be replayable offline.

## State machine

```text
DISCONNECTED
    |
    v
CALIBRATING --timeout/error--> DISCONNECTED
    |
    v
IDLE
  | rest drift / explicit arm
  v
ARMED
  | tap, chord or micro-drift
  v
TENTATIVE
  | high-confidence complete stroke
  v
COMMITTED --backspace/timeout--> TENTATIVE
  |
  | long pause
  v
IDLE
```

### `IDLE`

- contacts may exist;
- no stroke is being accumulated;
- per-contact baseline and contact class are updated;
- the UI may show “idle / palm on surface” but must not insert text.

### `ARMED`

A deliberate activation gesture starts a short input window. A possible activation is a multi-contact pattern, a calibrated palm/knuckle command, or a physical/Wacom control. The exact policy must be selected by the hardware study; a language model must not silently arm the system.

### `TENTATIVE`

The decoder collects candidate contacts and emits a ranked set of stroke hypotheses. The user can cancel with the physical emergency gesture. A tentative hypothesis is shown in a high-contrast candidate area or announced externally.

### `COMMITTED`

Only a complete stroke that satisfies the grammar and confidence policy reaches Plover/output. A short time window is allowed for a correction gesture, but it must be explicit in the UI.

## Feature contract

Every contact frame should preserve at least:

```json
{
  "t_ns": 123456789,
  "slot": 0,
  "tracking_id": 17,
  "tool_type": "finger",
  "x": 1240,
  "y": 820,
  "pressure": null,
  "touch_major": null,
  "touch_minor": null,
  "width_major": null,
  "orientation": null,
  "source": "linux-evdev"
}
```

Derived per-contact features:

- `v_peak`, `v_mean`, `acceleration_peak`;
- displacement relative to calibrated neutral point;
- area rise, area drop and hysteresis state;
- duration and time since last release;
- distance to nearest contact;
- contact count and simultaneous-release count;
- confidence from finger identity and driver confidence, if available;
- ring/little-finger dependency score.

## Candidate scoring

For a candidate key/chord \(c\), use a likelihood-ratio score rather than a hard threshold:

\[
s(c)=\log\frac{p(x_{t_1:t_n}\mid c,\text{user})}
{p(x_{t_1:t_n}\mid \text{rest/background},\text{user})}.
\]

A practical first version is a weighted cost:

```text
cost = w_v * velocity_error
     + w_d * displacement_error
     + w_a * area_error
     + w_i * identity_error
     + w_c * chord_ambiguity
     + w_g * grammar_error
     - w_l * language_prior
```

Weights are calibrated per user and per device mode. They must not be treated as physically universal.

## Enslavement decision

A contact is not suppressed merely because another contact moved. Compute a dependency score:

\[
D_{r,m} =
\exp\left(
-\frac{
\|\Delta p_r-\beta_{r\leftarrow m}\Delta p_m\|^2
+ \lambda_a |A_r-A_m|^2
+ \lambda_t |t_r-t_m|^2
}{2\sigma^2}
\right).
\]

`D` close to 1 means “explained by movement of m”. It is evidence against an independent ring-finger event. The coefficients \((\beta,\lambda_a,\lambda_t,\sigma)\) are per-user hypotheses and require data. A real chord decoder should run before final suppression and maintain a whitelist of known chords.

## Plover bridge

The bridge should expose one small, testable protocol:

```json
{"v":1,"type":"stroke","keys":["S","T"],"confidence":0.91,"event_id":"..."}
{"v":1,"type":"cancel","event_id":"..."}
{"v":1,"type":"reset","reason":"contact-id-change"}
```

Plover-specific mapping belongs outside the contact classifier:

```text
touch decoder -> validated stroke keys -> Plover Stroke.from_keys()
              -> Translator -> dictionary -> Formatter -> uinput
```

For a 0G surface, consider a new layout overlay rather than silently changing the user's `main.json`. The first prototype should use a dedicated `user.json` or separate machine configuration and preserve a one-command reset.

## Replay and metrics

Every candidate/committed record should reference the raw-event window. The replay command must reproduce detector decisions without a live device. The minimum metrics are:

- false activations/minute in `IDLE`;
- precision/recall/F1 for tap and drift candidates;
- P50/P95 detection latency;
- contact-ID switch count;
- independent-chord versus dependent-finger confusion;
- raw/corrected WPM, CER/WER and KSPC;
- recovery time after a false event.

## Open engineering questions

- Can the actual PTH-660 stream expose touch area and stable contact IDs on the target Linux version?
- Does Bluetooth produce the same axes and timing as USB?
- Is a static palm gate sufficient, or is a learned per-user contact-classifier required?
- How should a real two-finger chord override dependency suppression?
- Should activation be a gesture, a physical Wacom control, or a short sustained forearm mode?
- How much does a passive reference strip improve accuracy without increasing hand strain?
