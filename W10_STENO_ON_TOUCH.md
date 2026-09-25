# W10 — Machine stenography on a flat 0-force touch surface

Research date: 2026-09-25. Rule: ONLY numbers seen in a source, each with its URL. Otherwise NOT FOUND. No guessing, no derived arithmetic presented as measured.

## 0. Reference: what a mechanical steno machine does (baseline)

| system | device | input | WPM | error rate | source URL |
|---|---|---|---|---|---|
| US RPR test, literary / jury charge / testimony | mechanical stenotype | chording, trained reporter | 180 / 200 / 225 (pass thresholds, "very high accuracy") | NOT FOUND (exact % in this source) | https://en.wikipedia.org/wiki/Stenotype |
| Certified court reporter qualification | mechanical stenotype | chording | up to 200 | 97.5% overall accuracy required | https://amkreporting.com/faqs-about-court-reporters/ |
| Top professionals (COCRA, via Wikipedia) | mechanical stenotype | chording | up to 375 | NOT FOUND | https://en.wikipedia.org/wiki/Stenotype |
| Shorthand speed records (JCR) | stenotype | chording | 300 for 5 min (Dom Tursi); 360 for 1 min | NOT FOUND | https://www.thejcr.com/2013/07/11/high-speed-chase/ |
| What the hardware gives that 0G glass does not | mechanical stenotype: hard acrylic keys, key travel + individual sensitivity adjustment, simultaneous multi-key depression ("stroking"), key identification by position/depression, internal stroke translation | — | — | — | https://en.wikipedia.org/wiki/Stenotype |

## 1. Steno / chording attempts on touchscreen, tablet, touchpad

| system | device | input | WPM | error rate | source URL |
|---|---|---|---|---|---|
| iStenoPad app + silicone overlay (steno on iPad) | iPad touchscreen (+ $45 silicone overlay) | 22-key steno layout, multi-touch chords | NOT FOUND (no numbers; author: "very slow, very inaccurate, very frustrating"; overlay "mushy", slides, "couldn't feel the difference between a hit or a miss") | NOT FOUND (no numbers; pros "discarded it as too inaccurate and unwieldy" — qualitative) | http://plover.stenoknight.com/2012/02/istenopad-overlay-bust.html |
| touch-steno-keyboard (CosmicDNA, React/web) | any touchscreen w/ browser (Android/iOS/Windows tablets) | multi-touch steno chords | NOT FOUND | NOT FOUND | https://github.com/CosmicDNA/touch-steno-keyboard |
| ASETNIOP (touchscreen chord keyboard, 10 input points) | touchscreen phones/tablets (also concept for projection/glove) | 10-finger chords, release-to-register + autocorrect | Vendor concept claim "up to 80"; author self-report ~80 on ASETNIOP vs ~100 on QWERTY; user self-reports: 50+ after 5 days; 37 after <30 min; expected ~30 after a couple hours. NO peer-reviewed measurement. | NOT FOUND (controlled error rate) | https://newatlas.com/asetniop-chorded-keyboard-concept/24477/ ; https://www.asetniop.com/faq/ |
| Chording Glove (Rosenberg; 5-finger, keyless but NOT a flat surface — worn glove) | glove, no keyboard | 5-finger chords, 97-char map | 16.8 avg after 11 h use | 17.4% (character error) | https://www.obscure.org/rosenberg/toc.pdf ; https://dl.acm.org/doi/pdf/10.1145/302979.302984 |
| Twiddler one-handed chording keyboard (Lyons et al. 2004; PHYSICAL keys — tactile baseline, not 0G) | handheld 12-button pad | one-handed chording | 47 avg after ~25 h practice; 67 fastest subject | NOT FOUND (in retrieved excerpt) | https://dl.acm.org/doi/10.1109/ISWC.2004.19 ; https://faculty.cc.gatech.edu/~thad/p/030_10_MTE/twiddler-iswc.pdf |
| Senorita chorded keyboard (Rakhmetulla et al. 2020) | touchscreen (sighted/low-vision study) | chorded tapping | 9.3 (single session, 10 phrases); 8.23 referenced for Senorita baseline | 2.2%; 2% baseline | https://dl.acm.org/doi/fullHtml/10.1145/3313831.3376576 |
| Simultaneous multi-finger STENO chords on a 0G surface with published WPM + error rate | — | — | NOT FOUND | NOT FOUND | — |

Recognition method on glass (what exists): capacitive multi-touch contact blobs; chord registered on release (ASETNIOP: "producing a letter happens when you release the key… as long as you press both keys down before releasing either"; "press all ten fingers down… recalibrate the tracking circles"). No finger-identity sensing — contacts are located, fingers are inferred. Sources: https://www.asetniop.com/faq/ ; https://hackaday.com/2012/07/21/chorded-keyboard-for-touchscreens/

## 2. What the mechanical machine provides that 0G does not

- Key travel + force + individual sensitivity: modern writers have microprocessors and "allow sensitivity adjustments for each individual key" (https://en.wikipedia.org/wiki/Stenotype). A flat surface gives 0 travel, 0 force threshold, no per-key breakover — a contact is only an (x,y,t) blob.
- Tactile key identification by depression: steno keys are "hard, high-luster acrylic"; home position is felt (fingers "rest along the gap between the two main rows"). On glass the iStenoPad tester reports: "The lack of haptic feedback meant that even when I looked at my fingers, they'd tend to drift around and hit the wrong keys"; "keys are too close together to allow the necessary margin of error… with such a small amount of physical feedback"; "the only way I was able to tell which keys had been hit was by reading the display" (http://plover.stenoknight.com/2012/02/istenopad-overlay-bust.html).
- Simultaneous-stroke disambiguation by mechanics: a chord is one hand motion on real keys. On a capacitive sheet, near-simultaneous contacts suffer order/timing ambiguity and drift, with no depression event to anchor "which keys are down now."

| system | device | input | WPM | error rate | source URL |
|---|---|---|---|---|---|
| Stenographic error rate WITHOUT mechanical keys (controlled study) | — | — | NOT FOUND | NOT FOUND | — |
| Flexible membrane keyboards (Shin 2005 thesis; closest to "flat-ish" physical keys) | flexible membrane full-size keyboards | ten-finger typing | NOT FOUND (exact WPM in accessible excerpt; thesis cites Hahn 2002: "flexible keyboards typically resulting in slower typing speeds and higher error rates than other full sized keyboards") | NOT FOUND (exact % in accessible excerpt; direction only: higher) | https://vtechworks.lib.vt.edu/bitstreams/118f6e0a-ea66-4d33-bbea-f24dd544ccfc/download |
| Mechanical-vs-membrane sEMG typing assessment | mechanical vs standard membrane | typing | NOT FOUND (accessible excerpt only: fragment stating greater speeds with standard membrane in that setup — inconclusive, no clean numbers retrieved) | NOT FOUND | https://www.researchgate.net/publication/283538787_Mechanical_and_Membrane_Keyboard_Typing_Assessment_Using_Surface_Electromyography_sEMG |

## 3. Keyless / contactless / projected keyboards

| system | device | input | WPM | error rate | source URL |
|---|---|---|---|---|---|
| Celluon Magic Cube / Epic laser projection keyboard | projected 63-key layout on any flat surface + optical finger tracking | hunt-and-tap on projected image | NOT FOUND (measured WPM; vendor spec only: "recognizing 350 characters per minute" — characters/min, not a measured WPM study) | NOT FOUND (peer-reviewed rate; contemporary review only: "doesn't work too well" — qualitative) | https://gadgetgreg.com/2015/09/25/less-to-carry-around-with-celluon-epic-laser-projection-keyboard/ ; https://www.wired.com/2011/10/celluon/ |
| Laser-projection first-day accuracy (unverified vendor article, NOT a study) | projected QWERTY | touch typing | NOT FOUND | ">40% error rates during first-day use" — single vendor-article claim, treat as unevidenced | https://electronics.alibaba.com/question/laser-keyboard-projector-real-world-typing-guide |
| Measured finger-identity ambiguity rate for multi-touch chords (e.g. % of chords with wrong finger attribution / ghosting) | — | — | NOT FOUND | NOT FOUND | — |

Why they fail (evidenced mechanisms, qualitative): no tactile key boundaries → fingers drift off marks (iStenoPad, above); optical/projection sensing has no depression event, so timing/order of near-simultaneous contacts is ambiguous; capacitive blobs carry position but not finger identity, so a 10-contact chord is an unlabeled set. Measured ghosting/ambiguity percentages: NOT FOUND.

## 4. Touch typing without visual or tactile key boundaries

| system | device | input | WPM | error rate | source URL |
|---|---|---|---|---|---|
| Sears et al. 1993, touchscreen lift-off keyboards | touchscreens, several sizes | novice transcription | ~10 smallest → ~20 largest | NOT FOUND (exact % in retrieved excerpt) | https://www.cs.umd.edu/~ben/papers/Sears1993Investigating.pdf |
| Aalto/Cambridge/ETH 37k-person study (Palin et al., MobileHCI 2019) | smartphones | two-thumb transcription | 38 avg two thumbs ("only ~25% slower" than physical); fastest observed 85; physical comparators: most 35–65, up to 100 | 2.3% uncorrected errors at 36.2 WPM avg (dataset paper) | https://www.aalto.fi/en/news/smartphone-typing-speeds-catching-up-with-keyboards ; https://www.researchgate.net/publication/336206445_How_do_People_Type_on_Mobile_Devices_Observations_from_a_Study_with_37000_Volunteers ; https://www.bbc.com/news/technology-49933204 (38 vs ~52) |
| Hoggan et al. CHI 2008, tactile vs non-tactile touchscreen | phone physical keyboard vs touchscreen vs tactile touchscreen | memorized sentences, "as fast as possible, limit errors" | NOT FOUND (WPM in retrieved excerpt) | physical 89.6% accuracy; haptic touchscreen 80% (81.6% w/ better hardware); non-haptic 65.8% (via secondary summary); original framing: tactile-touchscreen scores "on average 5.5% lower than the physical keyboard in the lab and 9.6% lower when mobile" | https://pages.boreas.ca/blog/piezo-haptics/studies-show-haptics-can-improve-typing-accuracy-and-reduce-input-errors-on-smartphone ; https://www.dcs.gla.ac.uk/~stephen/papers/CHI2008_eve.pdf ; https://dl.acm.org/doi/10.1145/1357054.1357300 |
| Ma et al. WHC 2015, flat keyboard, no moving keys | flat keyboard (ten-finger) | transcription w/ haptic/audio keyclick | 55.1 local haptic keyclick vs 51.8 global haptic (numbers via secondary quote of the paper; PDF not directly extractable here) | Absolute error % NOT FOUND in accessible excerpt; ANOVA: haptic significant on total error rate (F3,69=4.75, p=0.005); audio-click NOT (F1,23=0.004, p=0.949); no interaction (F3,69=1.69, p=0.178) | https://www.microsoft.com/en-us/research/wp-content/uploads/2015/06/Ma_etal_WHC2015.pdf ; https://pages.boreas.ca/blog/piezo-haptics/studies-show-haptics-can-improve-typing-accuracy-and-reduce-input-errors-on-smartphone |
| TypeBoard (Gu et al. 2021), pressure-based unintentional-touch rejection | touchscreen w/ pressure sensing | typing | +11.78% typing speed | unintentional-touch detection 98.88%; typing errors reduced (p<0.01); fatigue reduced (p<0.005) | https://dl.acm.org/doi/fullHtml/10.1145/3472749.3474770 |
| WalkType adaptive keyboard (weak source: figure caption only) | touchpad keyboard, on-line layout adaptation | typing while walking | +12% speed (caption claim) | −45.2% uncorrected errors (caption claim) | https://www.researchgate.net/figure/The-adaptive-keyboard-system_fig1_221607602 |
| Findlater et al. CHI 2012 personalized ten-finger touchscreen typing | touchscreen | ten-finger typing, stable rectangular personalized layout | Direction only in accessible excerpt: "significantly improved typing speed compared to a control condition" — exact WPM NOT FOUND | Exact % NOT FOUND in accessible excerpt | https://faculty.washington.edu/wobbrock/pubs/chi-12.03.pdf |
| Beep/audio key-click as a fix | flat keyboard | typing | NOT FOUND (no speedup evidenced) | No effect (Ma et al.: audio-click p=0.949, n.s.) | https://pages.boreas.ca/blog/piezo-haptics/studies-show-haptics-can-improve-typing-accuracy-and-reduce-input-errors-on-smartphone |

What fixes it (with numbers): localized haptic keyclick (55.1 vs 51.8 WPM; significant error reduction; audio does nothing); personalization/adaptation (+12% / −45.2% WalkType caption claims; Findlater direction only); pressure-based rejection (+11.78% speed, p<0.01 errors). None tested with simultaneous steno chords.

## Verdict

- Is a mechanical-steno-equivalent (180–225+ WPM at certification accuracy) on a 0G touch surface evidenced anywhere? NO. No controlled study found that puts simultaneous steno chords on a flat 0-force surface at any WPM with any error rate.
- Closest published results:
  - Real steno-on-glass attempt (iStenoPad, 2012): qualitative failure — drift, wrong keys, hit/miss indistinguishable without looking; no numbers. http://plover.stenoknight.com/2012/02/istenopad-overlay-bust.html
  - Touchscreen chord keyboard with numbers that are only vendor self-reports: ASETNIOP (~30 after hours, 37–50+ anecdotes, author 80; no peer review, no error rate). https://www.asetniop.com/faq/
  - Peer-reviewed chording WITH physical keys: Twiddler 47 avg / 67 max after ~25 h (buttons, not glass). https://dl.acm.org/doi/10.1109/ISWC.2004.19
  - Peer-reviewed keyless chording (glove, not glass): 16.8 WPM / 17.4% error. https://www.obscure.org/rosenberg/toc.pdf
  - Best flat-surface SEQUENTIAL typing: 38 WPM two thumbs (2.3% uncorrected) / 55.1 WPM ten-finger with local haptics — roughly 4–6x below the 180–225 WPM steno bar, and sequential, not chorded.
- What specifically changes on 0G: loss of travel/force threshold, loss of per-key depression events for chord framing, loss of tactile home-position (→ drift), contacts without finger identity (→ chord-label ambiguity), and feedback reduced to display-reading or buzzer — where haptics partly recovers sequential accuracy but audio beeps do not, and neither has been shown to recover simultaneous-chord steno performance.

DONE
