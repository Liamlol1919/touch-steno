# Recommended Architectures for a Wacom PTH-660

## Decision summary

| Architecture | Feasibility on PTH-660 | Speed potential | Complexity | Verdict |
|---|---:|---:|---:|---|
| A. Rest-gated tap-sequence + Plover | high after adapter | 35–80 WPM plausible research target; 100+ needs strong model and training | medium–high | **Primary** |
| B. QWERTY finger-identity Bayesian decoder | medium | 30–60 WPM initially; 60–100 if contacts are stable | high | **Primary experiment** |
| C. Micro-drift directional gestures | high | 40–100 WPM if gestures are short and word-level | medium | **Primary alternative** |
| D. 8VIM/Cirrin-style word gesture + LM | high | 40+ WPM after training is plausible, not guaranteed | medium | **Fastest MVP candidate** |
| E. Dasher/Predictive zoom fallback | high | low for expert typing, high accessibility value | low–medium | **Fallback, not main path** |

These are engineering estimates, not literature guarantees. The required 150–250 WPM should be a stretch target only after a measured baseline shows low false-trigger rate and correction cost.
The speed ranges in this table are unmeasured engineering hypotheses. No PTH-660 corrected
WPM result exists yet; the current synthetic envelope realizes about 1.01–1.48 Hz for
150–350 ms gestures with a sub-gate return.
Training progression, acceptance gates and the starter Plover brief deliverable are defined in
[TRAINING_PATH.md](TRAINING_PATH.md). No speed range in this table is a PTH-660 result.

## A. Rest-gated tap-sequence + Plover (recommended primary)

### Interaction

1. The hand is calibrated into a neutral contact configuration.
2. The finger-to-steno-slot mapping is learned from the user's contact geometry.
3. A short movement/area change or explicit activation gesture arms the input.
4. One or more contacts produce a **candidate stroke**, not immediately a stroke.
5. Plover-compatible dictionary lookup emits words and translations.
6. A short undo/confirm policy prevents accidental text.

### Data path

```text
contacts -> palm gate -> per-finger rest model -> tap/drift events
         -> candidate stroke -> Plover stroke parser -> dictionary/LM
         -> uinput text + reversible candidate UI
```

### Why it fits

Plover already solves the hardest linguistic/backend problem: stroke lookup, dictionaries, translations, formatting, and output plugins. The research project should replace only the **key source** with a touch adapter. This makes it possible to compare a 0G decoder against a known reference engine.

### Required experiments

- mapping by contact ID vs. geometry cluster;
- 2-, 4-, 6-contact chords vs. sequential stroke;
- contact area threshold vs. velocity threshold;
- per-user calibration vs. universal thresholds;
- false stroke/minute while idle;
- raw/corrected WPM and KSPC.

### Risks

Plover's standard keyboard semantics may encode simultaneous transitions that a 0G sensor cannot disambiguate. A sequential or “roll-up” chord format may be superior even if it is not canonical steno. Keep an internal event log so a new decoder can be tested independently.

## B. QWERTY finger-identity Bayesian decoder

### Interaction

The user learns a QWERTY-like touch typing posture. Contacts are assigned to left/right fingers using a calibrated geometry model. Each contact-down/up pair is a noisy observation of a key class. A temporal decoder outputs the most likely character sequence.

### Model

```text
P(key sequence | observations) ∝
  P(observations | key sequence, user) × P(key sequence | language model)
```

Use an HMM or left-to-right weighted finite-state model. A personal model can include:

- preferred finger for each key;
- key target as ellipse/contact blob;
- approach direction and speed;
- left/right hand confidence;
- common digraphs and timing.

### Why it fits

It reuses a well-known motor model and can be evaluated against QWERTY. It also matches TypeAnywhere's insight that tap identity may be more valuable than exact position. It is the clearest way to test whether a 150-WPM-like QWERTY target is possible on a surface without key travel.

### Failure modes

- resting contacts are interpreted as keys;
- a finger loses its ID during drift or lift;
- palm contact is confused with little finger;
- language model masks a physical error.

### Mitigation

Never commit a character from a single ambiguous contact. Use confidence bands, a commit delay only for ambiguous cases, and an explicit “armed” mode. Log sensor data with decoded alternatives.

## C. Micro-drift directional gestures

Each contact is anchored conceptually at its initial rest point. A short out-stroke moves
toward a calibrated sector or branch, followed by a sub-threshold return to the neutral
reference. The return is part of the gesture contract, not an optional cleanup: without it,
repositioning contaminates the next direction estimate.

### Feature vector

\[
\mathbf f = [\Delta x, \Delta y, \theta, \|\Delta p\|, v_{peak}, d_{area}, duration]
\]

Sector decision with a deadband:

```text
if radius <= deadband: idle
else: normalize vector, compare to learned sector prototypes
```

Use a polar or DTW recognizer only for sequences that need it; it should not replace a simple low-latency sector classifier for the first prototype.

### Why it fits

It exploits the continuous surface instead of pretending it has discrete keys. It is compatible with 8VIM/Cirrin-like word-level gestures and needs only one reliable contact. It also offers a natural way to reject a resting hand: no displacement, no event.

### Failure modes

- tremor and surface slip create false direction;
- hand repositioning makes absolute position irrelevant but requires re-anchoring;
- gesture vocabulary becomes too large;
- words with common prefixes are hard to separate.

### Mitigation

Use bounded vocabulary or a character/word-level recognizer, per-user neutral calibration, and a confidence-based fallback. Keep the first version to 8 sectors and a short word/prefix grammar.

## D. 8VIM / Cirrin-style word gesture with language model

### Interaction

One finger enters a neutral center, traverses a sector and branch, and returns/ends according to the word gesture grammar. The decoder maps the trajectory to a prefix/word candidate.

### Advantages

- high information density per motion;
- little finger count;
- eyes-free potential after training;
- no need to resolve ten independent 0G contacts;
- the gesture engine and editor can be reused conceptually from open source.

### Risks

- 8pen/8VIM claims and implementations are not equivalent to independent scientific benchmarks;
- touchpad dimensions and finger width alter trajectories;
- a resting contact can still be detected as “in center”; center-in/center-out semantics are useful for this;
- word recognition without visual feedback can be difficult to debug.

### Recommended boundary

Use as a **fast mode** for common words and command vocabulary, not as the only input method. Add audio or haptic feedback externally and always expose a correction mechanism.

## E. Dasher-style predictive continuous fallback

A predictive zoom/word-selection mode is valuable for users who cannot hold a stable chord or need an accessible escape path. It is not expected to match elite steno/QWERTY speed. Its benefit is graceful degradation: when the touch decoder has low confidence, the user can intentionally enter a single-pointer predictive mode.

## Cross-cutting software modules

```text
capture/       Linux evdev/libinput or Wacom SDK
tracking/      contact IDs, association, smoothing
rest_model/    calibration, idle detection, palm gate
features/      position, velocity, area, pressure, direction
intent/        tap, drift, chord, gesture candidates
decoder/       HMM / WFST / gesture / Plover adapter
language/      dictionary, n-gram, user model
output/        uinput, clipboard, editor, accessibility API
telemetry/     raw event log and privacy-safe metrics
ui/            armed/idle/commit state, calibration, correction
```

## PTH-660 deployment plan

### Phase 0: sensor audit (1–2 days)

- capture `libinput debug-events` while idle, palm resting, one-finger taps, two-finger taps;
- record tool type, contact IDs, x/y, pressure, major/minor axes if exposed;
- verify whether touch is exposed by the installed Wacom driver;
- test Bluetooth vs USB and pen proximity arbitration;
- record a 10-minute idle false-trigger baseline.

### Phase 1: minimal viable gesture (1–2 weeks)

- 8 directional sectors;
- one active contact;
- out-and-back gesture with a sub-gate return;
- rest calibration;
- deadband + velocity/area gate;
- on-screen state and `uinput` output;
- collect raw and corrected WPM.

### Phase 2: Plover adapter (2–4 weeks)

- map strokes from ordered tap/drift events;
- load Plover dictionaries;
- compare sequence and simultaneous chord encodings;
- add explicit undo and candidate preview.

### Phase 3: QWERTY Bayesian baseline (3–6 weeks)

- collect labeled touch typing sessions;
- train personal HMM/online model;
- compare per-finger contact identity and geometric position;
- evaluate raw/corrected WPM, KSPC and false activations.

## Acceptance criteria for the first public prototype

- no spontaneous text during 30 minutes of normal resting/typing posture;
- report P95 onset-to-evidence and commit latency separately; committed latency must include
  the measured 88 ms evidence floor and is not accepted below it;
- correction rate and false-trigger rate are published;
- a calibration and reset path always works;
- a full text-entry session can be recovered after any ambiguous event;
- no claim of 150–250 WPM before long-session, corrected-speed measurements.
