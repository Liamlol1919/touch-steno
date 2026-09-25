# System Comparison Matrix

> **Method:** Publicly available research and project pages were checked during the initial pass. WPM values are not directly comparable unless the paper reports corrected/uncorrected speed, participant expertise, task language, and training. `?` means no verified value in the current pass, not zero.

| System / family | Input unit | Fingers / contacts | Sensor / device | Reported speed / learning evidence | Touch-flat transfer | Main risk / recommendation |
|---|---|---:|---|---|---|---|
| **Plover / OpenSteno** | stroke → word/syllable | 2 hands, 6-key steno | physical steno keyboard or emulated keyboard | Professional stenographers can reach high sustained rates; lab/user rates depend strongly on dictionary and machine. | **High with adapter**: preserve Plover dictionaries/translations; replace physical key source with candidate chords. | Excellent decoder/backend, but standard steno layout has ambiguous simultaneous keys and is not a proven 0G direct-touch interface. |
| **Standard stenotype** | chord/stroke | 2×3 keys | mechanical keyboard | high potential; expert-specific | Low directly, high via virtual keyboard | Mechanical key travel is the missing affordance. |
| **Twiddler** | one-handed chord sequence | thumb + 1–3 fingers | key switches | expert study: 47 WPM after ~25 h; TypeAnywhere review cites 26 WPM after 400 min for another Twiddler protocol | Medium: map discrete taps/postures | strong chording evidence, but not a 0G direct-touch result; steep learning curve |
| **CharaChorder** | multi-key chord | 3–7 fingers | mechanical multi-key board | marketed as ergonomic chording; independently controlled benchmark is limited | Medium: chord detector + Plover-like dictionary | Good vocabulary model; hardware semantics must be re-created in software. |
| **ASETNIOP** | one-handed chord set | multiple fingers/key switches | chorded device | specialized; no universal WPM | Medium | useful layout reference, not a ready touch pipeline |
| **Taipo / BAT / FrogPad / Artsey** | reduced-key / one-handed chords | 4–8 fingers | key matrix | highly variable, often niche research prototypes | Low–medium | inspect for layout optimization, not production driver code |
| **8pen** | word-shaped gesture / sector path | one finger | touch screen | project documentation claims familiar blind typing; >40 WPM is a project claim after mastery | **High geometrically** but not zero-force: touch position is finger-relative | Best open-source conceptual reference for word gestures. Add rest-state, palm gate and LM calibration. |
| **8VIM** | 8-sector gesture + Vim editing | one finger | Android touch IME | repository claims >40 WPM for trained users; not independent benchmark | Medium | Apache-2.0, Android-specific; gesture engine/layout can be ported conceptually, not blindly. |
| **Cirrin** | word-level unistroke | 1 pointer | pen/touch | word-level recognition; speed depends on vocabulary and corrections | High | useful for gesture recognizer and shape templates; no multi-finger identity |
| **Dasher** | continuous directional pointing → word | one pointer / gaze / touch | mouse, touch, eye/head tracking | information-efficient AAC; not a typing WPM benchmark | High for one pointer; low for 10-finger typing | best fallback/editor for low-control users; continuous motion conflicts with zero-force rest rejection |
| **ShapeWriter / Swype-style** | word trajectory | 1 finger | touchscreen | commercial systems are usually not open; published shape/word-gesture results vary | Medium–high | shape recognizer and LM patterns transferable; commercial source/license is not assumed |
| **TOAST** | spatial tap sequence decoded spatially | 1–many fingers? large surface | large touchscreen | 44.6 WPM average reported in related TypeAnywhere text | Medium; surface-size mismatch | strong model of Markov-Bayesian decoding |
| **Typing on Flat Glass** | QWERTY key classification | 10 fingers | touch surface | expert patterns; no universal WPM in current source pass | **High** | strongest direct precedent for contact geometry and personal models |
| **TapType** | inertial tap + 10-finger QWERTY prior | 10 fingers | wrist accelerometer | CHI 2022 system; reported performance must be extracted from full paper | Low with PTH-660, high with added IMU | strong evidence that tap identity can replace spatial keys |
| **TypeAnywhere** | finger-tap sequence | fingers + thumb chords | finger/wearable sensors | 70.6 WPM average after 2.5 h/5 days, 1.50% CER; best 91.4 WPM; 43.9 WPM on lap | Medium–high | architecture reference for tap sequences + LM; exact 44.6 WPM belongs to cited TOAST |
| **Typing on an Invisible Keyboard** | QWERTY-style invisible touch | touch contacts | touchscreen | 31.3 → 37.9 WPM after practice; visible comparison 41.6 WPM | High | realistic learning curve baseline |
| **FineType** | fine-grained finger combination/posture | one hand | wrist sensors | 35.1 WPM; 5.1% character error reported | Medium | recent benchmark; extra sensors improve identity |
| **BiTipText** | fingertip chord/tap | two hands | fingertip hardware | 23.4 WPM | Low directly, medium as posture/chord idea | not evidence for high-speed standard typing |
| **No-Look Notes** | multi-touch pie/segment | multiple contacts | touchscreen | 1.33 WPM cited in later accessibility work | High concept, low speed | robust accessibility baseline, not high-speed target |
| **Physical QWERTY** | key | 10 fingers | mechanical keyboard | typical expert reference ~50 WPM in cited HCI work; 150–250 possible for trained users in favorable settings | **Baseline only** | provides target and fatigue comparison, not a flat-surface solution |

## Normalized interpretation

- **Raw gesture rate is not word rate.** One word gesture may encode several letters, but can require correction, a slow first pass, or a target selection.
- **“Blind”/eyes-free is not “zero-force.”** A finger can hover or maintain posture in a device with buttons; continuous 0G introduces palm rejection and contact identity problems.
- **Reported WPM is a result for a trained population under a task protocol.** It is not a hardware property.
- The most useful comparison for PTH-660 is: **Typing on Flat Glass + TypeAnywhere/TapType decoder + Plover dictionary**, with a separate 8VIM/Dasher fallback.

## Open-source status snapshot

| Project | License | Reuse status |
|---|---|---|
| Plover | GPL-2.0 | strong backend reuse, but GPL implications for linked application |
| 8VIM | Apache-2.0 | gesture layout/IME concepts; Android code |
| Dasher | GPL (classic repo) or MIT for modern DasherCore lineage; verify per repo | prediction/editor concepts; license must be checked at selected commit |
| Linux Wacom/libinput | GPL / LGPL / MIT components (component-specific) | driver integration, not a text-entry UI |
| Wacom Feel Multi-Touch | proprietary SDK/driver terms | API reference only unless redistribution rights are confirmed |
