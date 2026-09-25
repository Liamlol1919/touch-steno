# W4 — Zero-Force Text Input & Intent-Detection Algorithms (with exact citations)

> Rule followed: ONLY numbers actually seen in a source are reported, each with its source URL. Otherwise `NOT FOUND`. No guessing.

---

## 1. "Zero-Lift" / "Zero force" / "0-force" touch typing, lift vector, "carry" finger

### 1.1 Exact-term findings

| Searched term | Finding |
|---|---|
| `"zero force touch typing"` | NOT FOUND as a named published system. No paper/system found under this exact name. |
| `"zero-lift typing"` | NOT FOUND as a named published system. |
| `"0-force"` (text input) | NOT FOUND as a named published system. |
| `"no-lift chord"` | NOT FOUND as a named published system. |
| `"touch typing without force"` | NOT FOUND as a named phrase; closest are "resting finger", "hands-down", "eyes-free", "three-state touch" systems below. |
| `"lift vector"` (typing intent) | NOT FOUND. The term does not appear in the typing sources found. Do not use it as a cited concept. |
| `"carry finger" / "designated carry finger"` | NOT FOUND. No published typing system found using a designated "carry" finger. Closest is FingerWorks' "resting finger hypotheses" (null-output home-row chain) — different concept. |

What DOES exist under different names: **resting-finger / hands-down / eyes-free ten-finger typing on continuous touch surfaces**. The systems below are the citable prior art for "0-force" (rest + type without lift discipline).

### 1.2 Published resting-finger / hands-down systems

| System / algorithm | Parameter | Value | Unit | Source URL | Relevance |
|---|---|---|---|---|---|
| ResType (Li et al., CHI 2023) — invisible adaptive keyboard leveraging resting fingers | calibration smoothing window | 100 | ms (5 frames) | https://dl.acm.org/doi/10.1145/3544548.3581055 | Core zero-force primitive: rest-to-calibrate latency |
| ResType | calibration latency range | 100–120 | ms | https://dl.acm.org/doi/10.1145/3544548.3581055 | Time from stable rest to refit F/J |
| ResType | pitch-angle reject threshold (adjacent home-row pair) | 60.0 | degrees | https://dl.acm.org/doi/10.1145/3544548.3581055 | Rejects thumb/thenar touches; keeps 99.8% of calibrations |
| ResType | neighbor pitch, home-row touches (mean) | 17.8 (SD 13.2, min 0.0, max 62.0) | degrees | https://dl.acm.org/doi/10.1145/3544548.3581055 | Empirical basis for 60° threshold |
| ResType | pitch, unintentional vs adjacent home-row (mean) | 81.8 (SD 6.2, min 60.5, max 90.0) | degrees | https://dl.acm.org/doi/10.1145/3544548.3581055 | Separation that makes 60° work |
| ResType | min distance within home row (mean) | 2.26 (SD 0.46) | cm | https://dl.acm.org/doi/10.1145/3544548.3581055 | Keep-8-closest filter basis |
| ResType | distance home-row to other touches (mean) | 5.15 (SD 1.14) | cm | https://dl.acm.org/doi/10.1145/3544548.3581055 | Far-touch rejection basis |
| ResType | index/middle/ring presence in calibration | >99.8 | % cases | https://dl.acm.org/doi/10.1145/3544548.3581055 | Which fingers reliably rest |
| ResType | max touchpoints kept after closest-filter | 8 | count | https://dl.acm.org/doi/10.1145/3544548.3581055 | Algorithm step 2 |
| ResType | decoder top-1 / top-3 accuracy | 96.3 / 99.0 | % | https://dl.acm.org/doi/10.1145/3544548.3581055 | Speed comes from decode, not precision |
| ResType | Day-1 → Day-5 speed (ResType) | 30.18 (SD 8.37) → 41.26 (SD 7.91), +36.7% | WPM | https://dl.acm.org/doi/10.1145/3544548.3581055 | Measured zero-force-adjacent speed |
| ResType | Day-5 tablet keyboard | 36.36 (SD 9.47) | WPM | https://dl.acm.org/doi/10.1145/3544548.3581055 | Baseline beaten by 13.5% |
| ResType | Day-5 physical keyboard (same participants) | 47.58 (SD 12.27) | WPM | https://dl.acm.org/doi/10.1145/3544548.3581055 | ResType = 86.7% of physical |
| ResType | mean word UER ResType / ResTypeStatic | 1.55 (SD 1.36) / 0.84 (SD 1.21) | % words | https://dl.acm.org/doi/10.1145/3544548.3581055 | Error cost of invisibility |
| ResType | mean word CER ResType / ResTypeStatic | 14.09 / 8.35 | % words | https://dl.acm.org/doi/10.1145/3544548.3581055 | Correction burden |
| TOAST (Shi et al. 2018) eyes-free tabletop | pick-up speed | 41.4 | WPM, CER 0.6% char | https://doi.org/10.1145/3191765 | Hands-down eyes-free baseline |
| TOAST | after <10 min practice | 44.6 | WPM, no accuracy loss | https://doi.org/10.1145/3191765 | Learnability |
| TOAST | Markov-Bayesian top-1 gain (pooled) | 86.2 → 92.1 | % | https://doi.org/10.1145/3191765 | Relative-position decoding gain |
| Findlater et al. CHI 2011 flat-glass experts (N=20) | unrestricted (no feedback) mean | 58.5 (SD 18.0, range 31.3–92.7); text also 59 | WPM | http://faculty.washington.edu/wobbrock/pubs/chi-11.02.pdf ; http://faculty.washington.edu/wobbrock/pubs/interactions-12.pdf | Ideal flat-surface ceiling, experts |
| Findlater 2011 | same participants physical keyboard | 85 | WPM | http://faculty.washington.edu/wobbrock/pubs/interactions-12.pdf | Flat = ~31% slower than physical |
| Findlater 2011 | asterisk-feedback + visible keyboard | 27–28 | WPM | http://faculty.washington.edu/wobbrock/pubs/interactions-12.pdf | Realistic corrected speed |
| Findlater 2011 | fingers down at trial start (resting) | M 5.08 (SD 2.94, range 0–10) | fingers | http://faculty.washington.edu/wobbrock/pubs/chi-11.02.pdf | Users DO rest between sequences |
| Findlater 2011 | touches / text length ratio | M 1.07 (SD 0.07) | ratio | http://faculty.washington.edu/wobbrock/pubs/chi-11.02.pdf | ~7% extra (rest/brush) touches |
| Findlater 2011 | non-finger (palm/arm) touches per trial | M 8.24 (SD 4.41); ~1 per word | count | http://faculty.washington.edu/wobbrock/pubs/chi-11.02.pdf | Why palm rejection matters |
| Findlater 2011 | presses within key bounds (visible kbd) | 81.5 | % | http://faculty.washington.edu/wobbrock/pubs/chi-11.02.pdf | Raw hit rate before personalization |
| Findlater 2011 | user-dependent model, no-keyboard asterisk | 90 | % classification | http://faculty.washington.edu/wobbrock/pubs/chi-11.02.pdf | Personalization requirement |
| KeySense (2026) hands-down + LLM decoder | decoder top-1 vs baselines | 84.8 vs 75.7 and 79.3 | % | https://doi.org/10.1145/3772318.3790964 | Timing-isolated taps + language decode |
| KeySense | speed KeySense vs hover keyboard | 28.3 vs 26.2, p<0.01 | WPM | https://doi.org/10.1145/3772318.3790964 | Small but significant gain |
| KeySense | NASA-TLX physical demand median | 1.5 vs 4.0 | scale points | https://doi.org/10.1145/3772318.3790964 | Ergonomic case for resting |
| TypeAnywhere (CHI 2022) finger-sequence-only | Day-5 table mean / desktop | 70.6 / 87.8 (80.4%) | WPM | https://faculty.washington.edu/wobbrock/pubs/chi-22.03.pdf | No-location decoding ceiling |
| TypeAnywhere | best performer Day 5 / lap condition | 91.4 / 43.9 | WPM | https://faculty.washington.edu/wobbrock/pubs/chi-22.03.pdf | Lap = soft-surface penalty |
| TypeAnywhere | offline CER neural vs n-gram | 1.6 vs 5.3 | % char | https://faculty.washington.edu/wobbrock/pubs/chi-22.03.pdf | Language-model leverage |
| FingerWorks US6677932 | resting-hand hypothesis chain | 5 simultaneous touches → 5 resting hypotheses, null keycode, home-row coords | count/design | https://www.freepatentsonline.com/6677932.html | Earliest "carry-like" construct (but NOT called carry finger) |
| US9207794 rest heuristic | rest count threshold | 6 or more fingers | count | https://exa.ai/library/legal/patent/77d7w01ckv2600pqhkhwjb | If ≥6 initial contacts, bias to resting |
| US9207794 rest heuristic | rest duration threshold | 0.1 | s | https://exa.ai/library/legal/patent/77d7w01ckv2600pqhkhwjb | Below this → overlapping keystrokes, not rest |
| US9377871 intent factors | factors | time + surface area + distance from home/rest | design (exact numeric cutoffs NOT FOUND in excerpt) | https://patents.justia.com/patent/9377871 | Framework for zero-force filter |

---

## 2. Intent-detection algorithms: dwell, tap+hold, double-tap, swipe, pressure/area, velocity

| System / algorithm | Parameter | Value | Unit | Source URL | Relevance |
|---|---|---|---|---|---|
| Mozilla JSAT Gestures.jsm | DWELL_THRESHOLD | 250 | ms | https://bugzilla.mozilla.org/attachment.cgi?id=8658454 | Dwell-vs-tap boundary |
| Mozilla JSAT | SWIPE_MIN_DISTANCE | 0.4 | inch | https://bugzilla.mozilla.org/attachment.cgi?id=8658454 | Swipe distance floor |
| Mozilla JSAT | TAP_MAX_RADIUS | 0.2 | inch | https://bugzilla.mozilla.org/attachment.cgi?id=8658454 | Tap wander allowance |
| Mozilla JSAT | DIRECTNESS_COEFF (15° max between segments) | 1.44 | ratio | https://bugzilla.mozilla.org/attachment.cgi?id=8658454 | Swipe straightness gate |
| Mozilla JSAT | MAX_CONSECUTIVE_GESTURE_DELAY | 200 | ms | https://bugzilla.mozilla.org/attachment.cgi?id=8658454 | Tap-chain window |
| Microchip PTC gesture lib | tapReleaseTimeout / swipeTimeout / tapHoldTimeout range | 0–255 each (device units; ordering TAP_RELEASE < SWIPE < TAP_HOLD) | counts | https://developerhelp.microchip.com/xwiki/bin/view/applications/touch/libraries/ptc/parameter-reference/gesture/ | Tap/hold/swipe arbitration pattern |
| Microchip PTC | SEQ_TAP_DIST example | 20 | coords | https://developerhelp.microchip.com/xwiki/bin/view/applications/touch/libraries/ptc/parameter-reference/gesture/ | Double-tap proximity idea |
| Microchip PTC | factory-default ms values | NOT FOUND (vendor-configurable; docs give ranges + ordering + one worked example "swipe … within 50 ms" for value 5, scale not universal) | — | https://developerhelp.microchip.com/xwiki/bin/view/applications/touch/libraries/ptc/parameter-reference/gesture/ | Do not cite as constants |
| CleverKeys gesture spec | short_gesture_min_distance | 28 | % of key diagonal | https://cleverkeys.app/specs/gestures/gesture-system-overview-spec/ | Sub-key swipe floor |
| CleverKeys | short/long boundary (short_gesture_max_distance) | 141 | % of key diagonal | https://cleverkeys.app/specs/gestures/gesture-system-overview-spec/ | Word-swipe promotion gate |
| CleverKeys | tap_duration_threshold (touch-up path) | 150 | ms | https://cleverkeys.app/specs/gestures/gesture-system-overview-spec/ | Tap-vs-swipe time gate |
| CleverKeys | min swipe distance rule | keyWidth / 2 | px | https://cleverkeys.app/specs/gestures/gesture-system-overview-spec/ | Left-key + distance/time classifier |
| CleverKeys | swipe speed gate | NOT FOUND (spec: "no swipe_speed_threshold … never existed") | — | https://cleverkeys.app/specs/gestures/gesture-system-overview-spec/ | Evidence against speed-gating slow swipes |
| libinput touchpad pressure | AttrPressureRange example | 10:8 (down:up, device units, down ≥ up) | device pressure | https://wayland.freedesktop.org/libinput/doc/latest/touchpad-pressure-debugging.html | Hysteresis pattern for light-touch filter |
| libinput | AttrPalmPressureThreshold / AttrThumbPressureThreshold example | 150 / 100 | device pressure | https://wayland.freedesktop.org/libinput/doc/latest/touchpad-pressure-debugging.html | Palm vs thumb vs finger split |
| libinput | user configurability | NOT user-configurable; per-device quirks DB | design | https://wayland.freedesktop.org/libinput/doc/latest/touchpad-pressure.html | Must calibrate per surface |
| libinput | AttrTouchSizeRange example | 10:8 | device size | https://wayland.freedesktop.org/libinput/doc/latest/touchpad-pressure-debugging.html | Area-based variant of pressure |
| Nuance US2017/0185287 static contact | TThreshold_Low / TThreshold_High; SAThreshold size bands | thresholds exist; exact numbers NOT FOUND in publication | — | https://www.freepatentsonline.com/y2017/0185287.html | Duration+area rest detector |
| Published kPa / mm² finger-pressure intent cutoffs for typing | — | NOT FOUND (only device-unit quirks + geometric/statistical models above) | — | — | Do not invent |
| Reported error/speed for intent decoders | ResType 96.3% top-1 / 99.0% top-3; TOAST 86.2→92.1%; KeySense 84.8% vs 75.7/79.3%; TypeAnywhere 1.6% CER | see §1.2 | — | (URLs in §1.2) | Best available "error rates" for rest-tolerant decoders |

---

## 3. Gesture arbitration (Android + Chromium): drag vs tap vs long-press — exact constants

> `FastTap / Spotlight / Flick / ClickDebouncer` as named Android *framework* classes: **NOT FOUND**. No AOSP classes by those names were found. The actual arbitration lives in `ViewConfiguration` + `GestureDetector` (+ Chromium port) + SystemUI falsing classifiers; app-level "click debouncers" are NOT platform constants (typical app examples 300/500/600/1000 ms are conventions, e.g. https://stackoverflow.com/questions/16534369/avoid-button-multiple-rapid-clicks — do not cite as OS constants).

| System / algorithm | Parameter | Value | Unit | Source URL | Relevance |
|---|---|---|---|---|---|
| Android ViewConfiguration (current master) | DEFAULT_LONG_PRESS_TIMEOUT | 400 | ms (older builds 500) | https://github.com/android/platform_frameworks_base/blob/master/core/java/android/view/ViewConfiguration.java | Press → long-press boundary |
| Android ViewConfiguration | TAP_TIMEOUT (wait to decide tap vs scroll) | 100 | ms | https://github.com/android/platform_frameworks_base/blob/master/core/java/android/view/ViewConfiguration.java | Tap-vs-scroll time gate |
| Android ViewConfiguration | DOUBLE_TAP_TIMEOUT (up→down) | 300 | ms | https://github.com/android/platform_frameworks_base/blob/master/core/java/android/view/ViewConfiguration.java | Tap-chain window |
| Android ViewConfiguration | DOUBLE_TAP_MIN_TIME | 40 | ms | https://github.com/android/platform_frameworks_base/blob/master/core/java/android/view/ViewConfiguration.java | Debounce floor |
| Android ViewConfiguration | DEFAULT_MULTI_PRESS_TIMEOUT | 300 | ms | https://github.com/android/platform_frameworks_base/blob/master/core/java/android/view/ViewConfiguration.java | Multi-press window |
| Android ViewConfiguration | TOUCH_SLOP (fallback; scaled by overlay) | 8 | dip | https://github.com/android/platform_frameworks_base/blob/master/core/java/android/view/ViewConfiguration.java | Wander before scroll |
| Android ViewConfiguration | DOUBLE_TAP_TOUCH_SLOP | 8 (= TOUCH_SLOP) | dip | https://github.com/android/platform_frameworks_base/blob/master/core/java/android/view/ViewConfiguration.java | First-tap wander for double-tap |
| Android ViewConfiguration | PAGING_TOUCH_SLOP | 16 (= 2× touch slop) | dip | https://github.com/android/platform_frameworks_base/blob/master/core/java/android/view/ViewConfiguration.java | Paged-scroll gate |
| Android ViewConfiguration | DOUBLE_TAP_SLOP (tap-to-tap distance) | 100 | dip | https://github.com/android/platform_frameworks_base/blob/master/core/java/android/view/ViewConfiguration.java | Second-tap proximity |
| Android ViewConfiguration | WINDOW_TOUCH_SLOP | 16 | dip | https://github.com/android/platform_frameworks_base/blob/master/core/java/android/view/ViewConfiguration.java | Outside-window dismissal |
| Android ViewConfiguration | EDGE_SLOP | 12 | dip | https://github.com/android/platform_frameworks_base/blob/master/core/java/android/view/ViewConfiguration.java | Edge-touch inset |
| Android ViewConfiguration | HANDWRITING_SLOP | 2 | dip | https://github.com/android/platform_frameworks_base/blob/master/core/java/android/view/ViewConfiguration.java | Stylus tight gate |
| Android ViewConfiguration | MINIMUM_FLING_VELOCITY | 50 | dip/s | https://github.com/android/platform_frameworks_base/blob/master/core/java/android/view/ViewConfiguration.java | Fling floor |
| Android ViewConfiguration | MAXIMUM_FLING_VELOCITY | 8000 | dip/s | https://github.com/android/platform_frameworks_base/blob/master/core/java/android/view/ViewConfiguration.java | Fling ceiling |
| Android ViewConfiguration | HOVER_TAP_TIMEOUT / HOVER_TAP_SLOP | 150 / 20 | ms / px | https://github.com/android/platform_frameworks_base/blob/master/core/java/android/view/ViewConfiguration.java | Touchpad-tap variant |
| Android ViewConfiguration | PRESSED_STATE_DURATION | 64 | ms | https://github.com/android/platform_frameworks_base/blob/master/core/java/android/view/ViewConfiguration.java | Visual press floor |
| Android ViewConfiguration | AMBIGUOUS_GESTURE_MULTIPLIER | 2.0 | × (slop & long-press scaled) | https://github.com/android/platform_frameworks_base/blob/master/core/java/android/view/ViewConfiguration.java | Classifier-uncertainty backoff |
| Android ViewConfiguration | KEY_REPEAT_TIMEOUT / KEY_REPEAT_DELAY | 400 / 50 | ms | https://github.com/android/platform_frameworks_base/blob/master/core/java/android/view/ViewConfiguration.java | Hold-to-repeat |
| Android ViewConfiguration | GLOBAL_ACTIONS_KEY_TIMEOUT | 500 | ms | https://github.com/android/platform_frameworks_base/blob/master/core/java/android/view/ViewConfiguration.java | Chord hold |
| Android GestureDetector logic | SHOW_PRESS at downTime+TAP_TIMEOUT; LONG_PRESS at downTime+longPressTimeout; TAP msg delayed DOUBLE_TAP_TIMEOUT; double-tap iff 40<Δt≤300 ms AND dist²<doubleTapSlop² AND alwaysInBiggerTapRegion; ambiguous → long-press ×2.0 | — | design | https://github.com/android/platform_frameworks_base/blob/master/core/java/android/view/GestureDetector.java | Exact arbitration recipe |
| Chromium GestureDetector Config (Android port) | shortpress / longpress / showpress | 400 / 500 / 180 | ms | https://raw.githubusercontent.com/chromium/chromium/main/ui/events/gesture_detection/gesture_detector.h | Short vs long press split |
| Chromium | double_tap_timeout / double_tap_min_time | 300 / 40 | ms | https://raw.githubusercontent.com/chromium/chromium/main/ui/events/gesture_detection/gesture_detector.h | Same as Android |
| Chromium | touch_slop / stylus_slop / double_tap_slop | 8 / 12 / 100 | dips | https://raw.githubusercontent.com/chromium/chromium/main/ui/events/gesture_detection/gesture_detector.h | Same as Android |
| Chromium | minimum/maximum fling velocity | 50 / 8000 | dips/s | https://raw.githubusercontent.com/chromium/chromium/main/ui/events/gesture_detection/gesture_detector.h | Same as Android |
| Chromium | minimum_swipe_velocity | 20 | dips/s | https://raw.githubusercontent.com/chromium/chromium/main/ui/events/gesture_detection/gesture_detector.h | Swipe floor (very low) |
| Chromium | maximum_swipe_deviation_angle | 20 | degrees (0,45] | https://raw.githubusercontent.com/chromium/chromium/main/ui/events/gesture_detection/gesture_detector.h | Axis-lock strictness |
| Chromium | two_finger_tap_max_separation / timeout | 300 / 700 | dips / ms | https://raw.githubusercontent.com/chromium/chromium/main/ui/events/gesture_detection/gesture_detector.h | Bimanual coupling hint |
| Android TouchExplorer (a11y) | EXIT_GESTURE_DETECTION_TIMEOUT | 2000 | ms | https://android.googlesource.com/platform/frameworks/base/%2B/216c181/services/java/com/android/server/accessibility/TouchExplorer.java (via search excerpt) | Gesture give-up |
| Android TouchExplorer | determineIntentTimeout | tapTimeout × 1.5 | ms (=150) | https://android.googlesource.com/platform/frameworks/base/%2B/216c181/services/java/com/android/server/accessibility/TouchExplorer.java (via search excerpt) | Intent-decision delay |
| SystemUI DoubleTapClassifier | falsing check: both taps pass SingleTap, Δt ≤ doubleTapTimeMs, \|Δx\|, \|Δy\| < doubleTapSlop | — | design | https://android.googlesource.com/platform/frameworks/base/+/android16-qpr2-release/packages/SystemUI/src/com/android/systemui/classifier/DoubleTapClassifier.java | False-touch rejector |

---

## 4. Touchscreen typing speed reality (no key travel) vs physical keyboards

| System / study | Parameter | Value | Unit | Source URL | Relevance |
|---|---|---|---|---|---|
| Dhakal et al. CHI 2018 (N=168,000, 136M keystrokes, physical baseline) | mean speed | 51.56 (SD 20.2); fastest 120+ | WPM | https://acris.aalto.fi/ws/portalfiles/portal/21495207/ELEC_Dhakal_et_al_Observations_CHI2018.pdf | Large-scale physical anchor |
| Dhakal 2018 | trained vs untrained gap | +5 | WPM | https://acris.aalto.fi/ws/portalfiles/portal/21495207/ELEC_Dhakal_et_al_Observations_CHI2018.pdf | Training effect is small |
| Dhakal 2018 | mean IKI / keypress duration | 238.66 / 111.60 | ms | https://acris.aalto.fi/ws/portalfiles/portal/21495207/ELEC_Dhakal_et_al_Observations_CHI2018.pdf | Timing floor for filters |
| Palin et al. 37,370 mobile (same lab/method) | mean speed | 36.17 (SD 13.22); 75% < 43.98; max >80 | WPM | https://userinterfaces.aalto.fi/typing37k/resources/Mobile_typing_study.pdf | Large-scale soft-keyboard anchor |
| Palin mobile | uncorrected errors | 2.34 (SD 2.08); 75% < 3.07 | % | https://userinterfaces.aalto.fi/typing37k/resources/Mobile_typing_study.pdf | vs 1.17% desktop (same method) |
| Palin mobile | error mix substitution/insertion/omission | 55.6 / 11.1 / 33.3 | % of errors | https://userinterfaces.aalto.fi/typing37k/resources/Mobile_typing_study.pdf | Substitution dominates mobile |
| Palin mobile | KSPC / backspaces per sentence | 1.18 (SD 0.18) / 1.89 (SD 1.96) | keys/char / count | https://userinterfaces.aalto.fi/typing37k/resources/Mobile_typing_study.pdf | Correction cost ≈ desktop KSPC 1.17 |
| Palin mobile | two thumbs mean | 38 | WPM (~25% below physical) | https://labo.societenumerique.gouv.fr/en/articles/the-speed-of-fragging-on-tactile-screens-is-catching-up-on-physical-keyboards/ (summary of Palin et al.) | Best mobile posture |
| Palin mobile | fastest observed | 85 | WPM | https://labo.societenumerique.gouv.fr/en/articles/the-speed-of-fragging-on-tactile-screens-is-catching-up-on-physical-keyboards/ | Mobile ceiling |
| Sears et al. 1993 lift-off touchscreen | novice XS (6.8 cm) → L (24.6 cm) | ~10 → ~20 | WPM | https://doi.org/10.1080/01449299308924362 | Size effect, no-travel baseline |
| Sears 1993 | experienced XS → L | 21 → 32 | WPM | https://doi.org/10.1080/01449299308924362 | Practice effect on glass |
| Oulasvirta et al. CHI 2013 two-thumb | speed / error | 37 / 5 | WPM / % | http://pokristensson.com/pubs/OulasvirtaEtAlCHI2013.pdf | Two-thumb focused baseline |
| STK vs SGK lab + 4-week wild | speed range / residual CER | 28–39 / 1.0–3.6 | WPM / % char | https://dl.acm.org/doi/10.1145/2702123.2702597 | Mainstream methods incl. gesture |
| Findlater CHI 2012 ten-finger tablet | conventional / adaptive speeds; gain +12.9% overall, +15.2% session 3 (26.9→31.0); UER 0.22–0.30% | see values | WPM / % | https://faculty.washington.edu/wobbrock/pubs/chi-12.03.pdf | Personalization without visual change wins |
| Invisible keyboard (Jiang/Chi 2018) | 31.3 → 37.9 (3 days) vs visible 41.6; adapted model +11.5% | — | WPM | https://doi.org/10.1145/3173574.3174013 | Invisible ≈ visible after practice |
| i'sFree eyes-free gesture | 23.27 vs 15.90 baseline (+46%); WER 2.14 vs 5.04 | — | WPM / % word | https://suwzhu.github.io/papers/chi19.pdf | Gesture eyes-free point |
| Ross 2016 iPhone4 vs BlackBerry (small N) | touchscreen higher CPM, error n.s. | qualitative (see thesis for F/p) | — | https://scholarsjunction.msstate.edu/cgi/viewcontent.cgi?article=2121&context=td | Outlier; familiarity confound — do not generalize |
| Gap summary (same-method Aalto pair) | physical 51.56 vs mobile 36.17 | ~15 gap (~30% slower) | WPM | https://acris.aalto.fi/ws/portalfiles/portal/21495207/ELEC_Dhakal_et_al_Observations_CHI2018.pdf + https://userinterfaces.aalto.fi/typing37k/resources/Mobile_typing_study.pdf | The citable "typing gap" |

Error-rate comparison (physical vs no-travel): desktop uncorrected ~1.17% (Palin-cited Dhakal) and 0.47–0.76% in lab sentence tasks vs mobile/soft 2.34% large-scale, 1.0–3.6% STK/SGK, 5% two-thumb (Oulasvirta), 0.6% CER TOAST (with decode), 1.55% word-UER ResType-invisible. So: **soft keyboards roughly double residual errors vs physical at scale, but decode + personalization can pull them back under ~1–2%.**

---

## 5. The 10 most useful numeric constants for a velocity/coupling-based intent filter

| # | Constant (adopt literally) | Value | Why it matters for zero-force |
|---|---|---|---|
| 1 | Touch-slop wander gate | **8 dip** ([ViewConfiguration](https://github.com/android/platform_frameworks_base/blob/master/core/java/android/view/ViewConfiguration.java)) | Below this, treat as rest/tap; above, scrolling/drag. Prevents rest jitter from becoming input. |
| 2 | Double-tap proximity gate | **100 dip** ([ViewConfiguration](https://github.com/android/platform_frameworks_base/blob/master/core/java/android/view/ViewConfiguration.java)) | Couples two events in space; reuse for lift-return ("same finger came back") test. |
| 3 | Fling/impulse band | **50 – 8000 dip/s** ([ViewConfiguration](https://github.com/android/platform_frameworks_base/blob/master/core/java/android/view/ViewConfiguration.java)) | Typing taps live well below fling; use 50 dip/s as intentional-flick floor. |
| 4 | Swipe floor + axis lock | **20 dip/s + 20°** ([Chromium gesture_detector.h](https://raw.githubusercontent.com/chromium/chromium/main/ui/events/gesture_detection/gesture_detector.h)) | Deliberately lax velocity floor + tight angle gate: copy for directional-stroke vs drift split. |
| 5 | Tap-vs-scroll / hold time ladder | **100 ms (tap) / 400 ms (long-press) / 40–300 ms (double-tap window)** ([ViewConfiguration](https://github.com/android/platform_frameworks_base/blob/master/core/java/android/view/ViewConfiguration.java)) | Three-rung time ladder for tap / hold / chain decisions. |
| 6 | Show-press feedback deadline | **180 ms** ([Chromium gesture_detector.h](https://raw.githubusercontent.com/chromium/chromium/main/ui/events/gesture_detection/gesture_detector.h)) | Latest moment to commit visual response without feeling laggy. |
| 7 | Dwell boundary | **250 ms** ([Mozilla JSAT](https://bugzilla.mozilla.org/attachment.cgi?id=8658454)) | Independent second source for hold-vs-tap; straddles Android 100/400 nicely. |
| 8 | Inch-based spatial gates | **tap radius 0.2 in, swipe min 0.4 in, straightness 1.44** ([Mozilla JSAT](https://bugzilla.mozilla.org/attachment.cgi?id=8658454)) | Density-independent alternative to dip slop; straightness coefficient is directly reusable. |
| 9 | Rest-tolerant calibration window | **100 ms window (5 frames), 60° pitch reject, 2.26 vs 5.15 cm** ([ResType](https://dl.acm.org/doi/10.1145/3544548.3581055)) | Only published thresholds that separate resting fingers from typing fingers on glass. |
| 10 | Rest-count + rest-time heuristic | **≥6 contacts + 0.1 s** ([US9207794](https://exa.ai/library/legal/patent/77d7w01ckv2600pqhkhwjb)) | Cheapest multi-touch "hands-down" prior: count AND time must agree before suppressing keys. Plus ambiguous-gesture backoff **×2.0** ([ViewConfiguration](https://github.com/android/platform_frameworks_base/blob/master/core/java/android/view/ViewConfiguration.java)) when classifier is unsure. |

---

## 6. NOT-FOUND log (do not cite as facts)

- Exact strings "zero force" / "0-force" / "zero-lift" / "no-lift chord" / "lift vector" / "carry finger" as named typing systems: **NOT FOUND**.
- `FastTap`, `Spotlight`, `Flick`, `ClickDebouncer` as AOSP framework classes/constants: **NOT FOUND** (app-level debounce 300–1000 ms values on StackOverflow are conventions, not OS constants).
- Universal kPa / mm² / N finger-pressure intent cutoffs for typing: **NOT FOUND** (only per-device libinput quirks + patent bands without published numbers).
- Microchip PTC factory-default tap/hold/swipe in ms: **NOT FOUND** (range 0–255 + ordering only).
- iOS touch-arbitration equivalents (tap/long-press/slop): **not searched in this pass — NOT FOUND here**.

*Methods: web search + fetches on 2026-09-25 for the listed terms; AOSP master, Chromium main, ACM DL, Aalto datasets, MS State thesis, Microchip docs, libinput docs, patents, Mozilla JSAT patch.*
