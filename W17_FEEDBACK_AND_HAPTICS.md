# W17 — Sensory substitution & feedback for a 0-force typing surface

Scope: 0-force surface, no tactile confirmation, 31–40% of strokes within 10° of a
sector boundary (premise, PTH-660 measurement, not re-verified here). Only numbers
actually seen in a fetched source are reported, each with its source URL. Everything
else is marked NOT FOUND. No guessing.

Sources actually fetched and text-extracted (via curl + pdftotext):
- Tinwala & MacKenzie 2009 (TIC-STH): https://www.yorku.ca/mack/IEEE-TIC2009.pdf
- Tinwala & MacKenzie 2010 (NordiCHI): https://www.yorku.ca/mack/nordichi2010.pdf
- Tinwala & MacKenzie 2008 LetterScroll (CHI EA): https://www.yorku.ca/mack/chi2008-p3153.pdf
  + abstract page: https://www.yorku.ca/mack/chi2008-tinwala.html
- Hoggan PhD thesis 2010 (contains CHI 2008 / CHI 2009 experiments in Ch.6):
  https://theses.gla.ac.uk/1863/1/2010hoganphd.pdf
- Carter et al. 2013 UltraHaptics (UIST): https://research-information.bris.ac.uk/ws/files/12013908/paper.pdf
- Sridhar et al. 2015 AirType (CHI, mid-air typing, NO ultrasound used):
  http://handtracker.mpi-inf.mpg.de/projects/HandDexterity/content/AirType_CHI2015.pdf
- Basdogan et al. 2020 surface-haptics review (HTML): https://ar5iv.org/html/2004.13864v1
- DOI-only (closed, abstracts via OpenAlex, no full-text numbers extracted):
  https://doi.org/10.1145/1868914.1868972 ,
  https://doi.org/10.1145/1357054.1357300 ,
  https://doi.org/10.1145/1518701.1519045 ,
  https://doi.org/10.1007/978-3-642-12654-3_24 (No-Look Notes — numbers NOT FOUND, closed)

Method note: WPM = words per minute; MSD = minimum string distance error rate;
KSPC = keystrokes per character; "phrases correct %" = % of phrases submitted
exactly matching the presented phrase. Hoggan thesis statistics are from the thesis
text/figures as extracted; figure-image-only values are not reported.

---

## Q1. AUDIO feedback: measured effect on touch typing speed / error

### Table Q1

| system | feedback channel | condition | WPM | error rate | source URL |
|---|---|---|---|---|---|
| Graffiti strokes, finger on iPhone, 12 participants, eyes-free under table vs eyes-on | speech per character + non-speech sounds + vibration on unrecognized stroke | eyes-free | 7.60 | MSD 0.4% overall | https://www.yorku.ca/mack/IEEE-TIC2009.pdf |
| same | same | eyes-on | 7.00 | MSD 0.4% overall | https://www.yorku.ca/mack/IEEE-TIC2009.pdf |
| same | same (adjusted rate incl. corrections) | eyes-free adjusted | 9.50 | NOT FOUND separately | https://www.yorku.ca/mack/IEEE-TIC2009.pdf |
| same | same (adjusted) | eyes-on adjusted | 8.30 | NOT FOUND separately | https://www.yorku.ca/mack/IEEE-TIC2009.pdf |
| Graffiti + word-level correction, iPhone 3G, 12 participants, all eyes-free (device under table) | Immediate: speech per character + speech per word at SPACE, NO correction algorithm | Immediate | 8.34 | final MSD 2.5% | https://www.yorku.ca/mack/nordichi2010.pdf |
| same | OneLetter: valid first stroke required (vibration pulse blocks invalid first stroke), first letter spoken, rest = click, speech per word, correction ON | OneLetter | 10.6 (+27% vs Immediate) | final MSD 3.5% | https://www.yorku.ca/mack/nordichi2010.pdf |
| same | Delayed: click per stroke only, speech per word at double-tap SPACE, correction ON, no first-stroke gate | Delayed | 11.1 (+33% vs Immediate) | final MSD 7.0% | https://www.yorku.ca/mack/nordichi2010.pdf |
| same, all 3 modes pooled | mixed | all eyes-free | 10.0 overall; maxima 21.5 (OneLetter), 20.8 (Delayed), 16.9 (Immediate) | 4.3% overall (accuracy 95.7%) | https://www.yorku.ca/mack/nordichi2010.pdf |
| LetterScroll wheel, 7 blindfolded participants, earphones, speech per character | speech-only (M1 mouse only) | blindfolded | 2.9 | ~3.4% both methods | https://www.yorku.ca/mack/chi2008-p3153.pdf |
| same | speech-only (M4 mouse + keyboard vowels) | blindfolded | 4.4 ("33% faster than M1" as stated) | ~3.4% both methods | https://www.yorku.ca/mack/chi2008-p3153.pdf |
| LetterScroll pooled | speech-only | blindfolded | 3.6 overall | NOT FOUND separately | https://www.yorku.ca/mack/chi2008-p3153.pdf |
| QWERTY PDA soft keyboard, 12 participants, stereo-speaker crossmodal earcons (rhythm+texture+spatial) + standard visual highlight | visual + audio | lab | exact WPM NOT FOUND in extractable text (stated: significantly lower than physical; better than no-feedback standard) | 82.5% phrases correct | https://theses.gla.ac.uk/1863/1/2010hoganphd.pdf |
| same | visual + audio (speakers, noisy subway) | mobile | exact WPM NOT FOUND in extractable text (stated: comparable to standard touchscreen, i.e. no benefit) | 70.0% phrases correct | https://theses.gla.ac.uk/1863/1/2010hoganphd.pdf |
| same audio keyboard | visual + audio | lab / mobile | NOT FOUND (figures only) | KSPC 1.08 lab / 1.03 mobile | https://theses.gla.ac.uk/1863/1/2010hoganphd.pdf |
| pitch mapping of keys (e.g. pitch encodes key identity/position) | NOT FOUND | NOT FOUND | NOT FOUND | NOT FOUND | NOT FOUND |

Detail (Tinwala 2010, https://www.yorku.ca/mack/nordichi2010.pdf): 12 participants
(18–40 y, mean 26.6 SD 6.8; computer 2–12 h/day mean 6.7 SD 2.7; 6 regular touchscreen
users; 8 had tried Graffiti, none expert). 432 phrases total (12 × 3 modes × 3 blocks × 4).
Entry speed: block effect F2,18=6.2 p<.05; mode effect F2,18=32.3 p<.0001; post hoc
Immediate–OneLetter and Immediate–Delayed p<.0001. Final error: mode effect F2,18=8.2
p<.005; Delayed 7.0% = 2× OneLetter (3.5%), 2.8× Immediate (2.5%); Immediate–Delayed
and OneLetter–Delayed p<.0001, Immediate–OneLetter n.s. KSPC overall 1.27; Immediate
1.45, OneLetter 1.21 (−16.6%), Delayed 1.17 (−19.3%); F2,18=51.8 p<.0001. Correction
("system help"): 14.9% of entered text corrected overall (Delayed 15.6%, OneLetter
14.2%, n.s. between them); raw→corrected error decrease 70.3% overall (OneLetter
76.7%, Delayed 64.0%). Candidate list: 2.43 words/word overall; OneLetter 1.89,
Delayed 2.96 (+56.0%, p<.05). Intended word ranked 1st or 2nd 94.2% overall (OneLetter
95.3%, Delayed 93.2%); ranked 1st: OneLetter 77.0%, Delayed 82.0%. Playback: two-tone
bell, words spoken cyclically with 600 ms silence gaps; gestures: north-stroke restart,
left-swipe discard, tap accept. Adjusted rates (playback time removed) improve both
modes ~10%. SPACE = double-tap (counted as one stroke in KSPC).
Detail (Tinwala 2009, https://www.yorku.ca/mack/IEEE-TIC2009.pdf): mode effect
F1,11=6.8 p<.05 (eyes-free 8% faster, no degradation); adjusted F1,3=21.8 p<.0001
(9.50 vs 8.30, +15%); KSPC 1.36 eyes-free vs 1.24 eyes-on (+9%); overall accuracy
99.6% (MSD 0.4%). Feedback mapping: recognized stroke → spoken letter + click;
unrecognized → vibration pulse; delete stroke → eraser-rubbing sound.
Audio-masking limit (Hoggan Exp.5, https://theses.gla.ac.uk/1863/1/2010hoganphd.pdf):
audio KSPC significantly worse at 94–96 dB vs lower noise; audio WPM significantly
worse at 90–92 dB; tactile not significantly degraded until 100–102 dB (KSPC F(2,22)=
4.79; WPM F(2,22)=11.43). At 71–110 dB noise, audio and visual WPM significantly
below tactile (F(2,22)=2.91), and at 91–110 dB audio KSPC significantly above tactile
(F(2,22)=11.1). Subway-speaker audio (Exp.4b) gave no mobile benefit; author
attributes it to masking and notes earphones were NOT tested (headphone delivery =
NOT FOUND for typing WPM).

Does audio help or hurt with no visible keys? Measured: helps in quiet eyes-free use
(Tinwala eyes-free ≥ eyes-on; word-level audio + correction 10.0–11.1 wpm), hurts or
goes neutral in high noise (≥90–96 dB) and on a noisy train via speakers. No-effects
beyond these conditions: NOT FOUND.

---

## Q2. VIBRATION / HAPTIC feedback: effect on accuracy, key-press perception, typing speed

### Table Q2

| system | feedback channel | condition | WPM | error rate | source URL |
|---|---|---|---|---|---|
| QWERTY soft keyboard vs physical, 12 participants, built-in actuator whole-device vibration (fingertip-over/click/slip tactons) + visual highlight | tactile touchscreen | lab | 17 | 82.7% phrases correct (physical 88.25%) | https://theses.gla.ac.uk/1863/1/2010hoganphd.pdf |
| same | tactile touchscreen | mobile (subway) | 15.1 | 80.0% phrases correct (physical 89.6%) | https://theses.gla.ac.uk/1863/1/2010hoganphd.pdf |
| same | standard touchscreen, visual highlight only (no audio/tactile) | lab | 14 | 69.6% phrases correct | https://theses.gla.ac.uk/1863/1/2010hoganphd.pdf |
| same | standard touchscreen, visual only | mobile | 12.6 | 65.8% phrases correct | https://theses.gla.ac.uk/1863/1/2010hoganphd.pdf |
| same | physical keyboard | mobile | 19+ ("over 19") | 89.6% phrases correct | https://theses.gla.ac.uk/1863/1/2010hoganphd.pdf |
| PDA + 2 localized C2 actuators (left/right spatial) | tactile-localized | lab / mobile | 19.15 mobile (lab value figure-only, NOT FOUND in text) | PDA counts as stated: 25.3 lab / 24.4 mobile of 30 (text also states 23.8 lab / 24.5 mobile — discrepancy in source); physical 26.4 lab / 26.9 mobile of 30 | https://theses.gla.ac.uk/1863/1/2010hoganphd.pdf |
| same PDA | tactile-localized | lab / mobile | NOT FOUND (figures) | KSPC 1.20 lab / 1.24 mobile | https://theses.gla.ac.uk/1863/1/2010hoganphd.pdf |
| key-press perception (focal-point count, Carter): 0/1/2 ultrasound foci, 9 participants | mid-air ultrasound | lab walk-up, 5-min practice | n/a (not typing) | 0-point 100%; 1-point 100% (7/9) and 87.5% (2/9) | https://research-information.bris.ac.uk/ws/files/12013908/paper.pdf |
| tacton roughness identity (Hoggan Ch.4, not typing) | vibration parameter ID | lab | n/a | frequency-varying 81% vs waveform-varying 73%; instrument exception: harp 30%, others 80%+ | https://theses.gla.ac.uk/1863/1/2010hoganphd.pdf |

Detail (Hoggan Exp.4a(i), https://theses.gla.ac.uk/1863/1/2010hoganphd.pdf): keyboard
effect on accuracy F(2,22)=96.9 p<.001 (physical ≈ tactile > standard; tactile −5.5pp vs
physical lab, −9.6pp mobile; 1.6–2.8 more phrases wrong than physical). Time/phrase:
physical 13–17 s; tactile 20 s lab / 22 s mobile; standard 25–27 s; keyboard effect
F(2,22)=69.78 p<.001; mobility effect F(1,11)=9.48 p=.003. KSPC: keyboard effect
F(2,22)=6.58 p<.0001, tactile HIGHEST (users corrected more errors; standard users left
errors uncorrected — no penalty for errors in protocol). Workload (NASA TLX):
keyboard effect F(2,22)=111.35 p<.001; standard > physical and standard > tactile;
physical ≈ tactile overall; mental/physical demand, frustration, annoyance higher and
perceived performance lower on standard (each factor p<.001). Lab WPM 14 (standard)
vs 17 (tactile) per discussion section. Tactile took 22% longer than physical on average
(per conclusions).
Detail (Exp.4a(ii) C2, same URL): keyboard effect on accuracy F(3,33)=84.6 p<.0001
(physical, PDA-C2, tactile > standard; no sig diff among the three); KSPC effect
F(3,33)=4.82 p=.003 (tactile-whole-device highest; PDA-C2 ≈ physical ≈ standard);
time/phrase: keyboard F(3,33)=70.41, mobility F(1,11)=10.24 p=.001, interaction
F(3,33)=2.92 p=.03; PDA 17.5 s lab → 17.9 s mobile (flat across mobility, unlike all
other keyboards); PDA WPM 19.15 mobile ≈ physical. Annoyance: PDA-C2
significantly MORE annoying than physical or original tactile (F(2,22)=35.4 p<.0001);
author suggests users could not adjust force.
Vibration masking limit (Exp.5, same URL): tactile KSPC significantly worse at
8.19–8.37 g/s vs lower vibration and tactile WPM significantly worse at 8.01–8.19 g/s
(KSPC F(2,22)=34; WPM F(2,22)=23.1); audio degrades later on the vibration axis at
9.18–9.45 g/s. At 8.1–10.8 g/s, tactile WPM significantly below audio (F(2,22)=4.9)
and tactile KSPC above audio (F(2,22)=8.22).

Does a vibrator on a tablet change typing speed? Measured yes: whole-device
vibration 14→17 WPM lab (+3.0, +21%) and 12.6→15.1 WPM mobile (+2.5, +20%);
phrase time −5–6 s; +13–14pp phrases-correct. Localized dual-actuator: up to 19.15
WPM mobile, time ≈ physical, at the cost of higher annoyance.

---

## Q3. ULTRASOUND HAPTICS as a feedback channel

### Table Q3

| system | feedback channel | condition | WPM | error rate | source URL |
|---|---|---|---|---|---|
| UltraHaptics 2-focus discrimination, 9 participants, 112 trials, hand 200 mm above array, foci at 2/3/4/5 cm and 1 cm separations | focused ultrasound 40 kHz, modulated | 3 cm separation, different modulation frequencies | n/a (perception, not typing) | 86% correct count (≈10/12) vs 31% (≈2.5/8) same-frequency | https://research-information.bris.ac.uk/ws/files/12013908/paper.pdf |
| same | same | 1 cm separation | n/a | no significant same-vs-different difference (p=.071) | https://research-information.bris.ac.uk/ws/files/12013908/paper.pdf |
| same | same | 2, 3, 4, 5 cm, same vs different frequency | n/a | different-frequency significantly more accurate (p≤.041); ANOVA same-freq F(4,32)=15.236 p<.001, diff-freq F(4,32)=45.416 p<.001 | https://research-information.bris.ac.uk/ws/files/12013908/paper.pdf |
| UltraHaptics frequency ID, 4 participants, 3×42 trials, pairs 4–63/4–250/16–250 Hz at 3/4/5 cm | focused ultrasound | lab with training + per-trial correct/incorrect | n/a | exact ID % NOT FOUND in extractable text (trend stated only) | https://research-information.bris.ac.uk/ws/files/12013908/paper.pdf |
| mid-air 10-finger typing (AirType), 10 participants, monitor visual + auditory feedback, NO ultrasound | none (visual + auditory only) | lab | peak 22.25 (SD 8.9); range 13–38.1 | 2.3% avg (SD 0.04); selection threshold <15% (Damerau) | http://handtracker.mpi-inf.mpg.de/projects/HandDexterity/content/AirType_CHI2015.pdf |
| ultrasound per-key confirmation typing study | NOT FOUND | NOT FOUND | NOT FOUND | NOT FOUND | NOT FOUND |
| ultrasound localisation in degrees | NOT FOUND | NOT FOUND | n/a | NOT FOUND | NOT FOUND |

Detail (Carter, https://research-information.bris.ac.uk/ws/files/12013908/paper.pdf):
focal points ~1 cm diameter (wavelength of 40 kHz sound); prior work spaced foci
50 mm apart; mic scans at 200/400 mm heights, mic 20 mm above array for SPL;
absolute SPL 72.6 dB (1 focus) / 71.7 dB (2 foci); display holes 0.5 mm/25% open
−2.4 dB vs 1 mm/64% −4.8 dB vs 0.2 mm/11% undetectable; hand frequency JND cited
12–25%; second study height 200 mm, 10-min training day 1, sessions day 1 pm + day 2
am/pm, 1 × 2-min break per session (first study: 5 × 2-min breaks per 20 trials,
1-min cap per trial, white noise masking, dominant hand only).
Machine context (review, https://ar5iv.org/html/2004.13864v1): fingertip spatial
resolution 1–2 mm; Pacinian peak sensitivity 200–300 Hz within 10–1000 Hz; temporal
and spatial summation apply; localized vibrotactile pulse demos: 3 ms / 1 mm amplitude
/ 20 mm spot (4 EM actuators, 420×420×2 mm plate); 7 µm / 5.2 mm spot (32 piezo,
148×210×0.5 mm); 50×50 mm² spot (34 EM actuators, 268×170×0.7 mm); net tangential
forces: asymmetric friction up to 100 mN, electrovibration + 1 kHz oscillation up to
0.45 N, combined friction + 30 kHz in-plane up to 0.4 N, modal driving force up to
0.05 N; ultrasonic devices typically 27–60 kHz, ~1–2.3 µm, 4–150 V (e.g. 400 mW at
150 Vpp / 1.5 µm / 31 kHz on 93×65×0.9 mm glass); ERM = large lags, fixed
displacement; LRA = faster but narrow band; piezo = high force, high voltage, brittle.
Assessment for per-key confirmation: with ~1 cm foci and no discrimination gain at
1 cm separation (p=.071) vs 86% only at 3 cm with different frequencies, adjacent-key
confirmation on a key grid is NOT supported by the measured evidence; only coarse
multi-region cues are. Typing-through-ultrasound measured evidence: NOT FOUND
(AirType explicitly lists UltraHaptics as future work, p.519–520 of that PDF).

---

## Q4. VISUAL vs AUDITORY vs HAPTIC for eyes-free text entry (comparative)

### Table Q4

| system | feedback channel | condition | WPM | error rate | source URL |
|---|---|---|---|---|---|
| Graffiti iPhone, Immediate vs OneLetter vs Delayed (all eyes-free, see Q1) | audio(+tactile gate in OneLetter) | eyes-free | 8.34 / 10.6 / 11.1 | 2.5% / 3.5% / 7.0% | https://www.yorku.ca/mack/nordichi2010.pdf |
| QWERTY PDA, visual-only vs visual+audio vs visual+tactile, 12 participants, subway vibration+noise mapped to performance | visual only | 0–3.6 g/s; 50–70 dB | exact WPM NOT FOUND in text (figures only) | baseline; KSPC rises with disturbance (vibration F(2,22)=14.8; noise F(2,22)=30.7) | https://theses.gla.ac.uk/1863/1/2010hoganphd.pdf |
| same | visual + tactile (C2) | 8.1–10.8 g/s vibration | significantly LOWER WPM than audio (F(2,22)=4.9); tactile KSPC > audio (F(2,22)=8.22) | accuracy falls toward visual-only at extremes | https://theses.gla.ac.uk/1863/1/2010hoganphd.pdf |
| same | visual + audio (earpiece) | 71–110 dB noise | significantly LOWER WPM than tactile (F(2,22)=2.91); audio KSPC > tactile at 91–110 dB (F(2,22)=11.1) | accuracy falls toward visual-only at extremes | https://theses.gla.ac.uk/1863/1/2010hoganphd.pdf |
| same | visual only as fallback | extreme noise AND vibration | similar to degraded audio/tactile (author conclusion) | NOT FOUND numerically | https://theses.gla.ac.uk/1863/1/2010hoganphd.pdf |
| No-Look Notes eyes-free multi-touch (Bonner et al. 2010) | audio + tactile (claimed) | eyes-free | NOT FOUND (closed: https://doi.org/10.1007/978-3-642-12654-3_24) | NOT FOUND | NOT FOUND |
| Hoggan "Audio or tactile feedback: which modality when" (CHI 2009) full speed/error curves | NOT FOUND in full text (closed: https://doi.org/10.1145/1518701.1519045; abstract only: audio degrades ≥94 dB, tactile ≥9.18 g/s) | NOT FOUND | NOT FOUND | NOT FOUND | NOT FOUND |

Tinwala DELAYED detail (the prompt's "delayed feedback increased the rate"):
"Delayed" = word-level feedback (click per stroke, word spoken at double-tap SPACE,
correction if needed) with NO per-character validation gate. It was fastest (11.1 wpm,
+33% over Immediate 8.34) precisely because users never stopped to confirm the first
character; but final error was worst (7.0% vs 2.5%/3.5%) and candidate lists longest
(2.96 vs 1.89 words, +56%). OneLetter (first-stroke gate + vibration block + spoken
first letter) kept 10.6 wpm with 3.5% error and 76.7% raw-error reduction.
Follow-ups to Tinwala 2010 found in fetched sources: NOT FOUND (no citation graph
pulled; NordiCHI paper text contains no follow-up data).
Eyes-free visual-vs-nonvisual (Tinwala 2009): eyes-free 7.60 ≥ eyes-on 7.00 (+8%,
F1,11=6.8 p<.05) with audio+tactile substitution — i.e. removing vision did NOT degrade
Graffiti throughput in that setup.
Cross-study comparison caveat: Tinwala = Graffiti strokes + correction, Hoggan =
QWERTY + no dictionary correction; numbers are NOT directly comparable.

---

## Q5. Typing with NO feedback at all (our actual condition)

| system | feedback channel | condition | WPM | error rate | source URL |
|---|---|---|---|---|---|
| literal zero-feedback typing (no visual AND no audio AND no tactile) | none | any | NOT FOUND | NOT FOUND | NOT FOUND |
| closest baseline 1: standard soft QWERTY, visual highlight only (no audio/tactile), 12 participants | visual only | lab | 14 | 69.6% phrases correct (= 30.4% phrase-error) | https://theses.gla.ac.uk/1863/1/2010hoganphd.pdf |
| closest baseline 1 | visual only | mobile subway | 12.6 | 65.8% phrases correct (= 34.2% phrase-error) | https://theses.gla.ac.uk/1863/1/2010hoganphd.pdf |
| closest baseline 2: Exp.5 visual-only keyboard across disturbance bins | visual only | 0–10.8 g/s; 50–110 dB | NOT FOUND numerically in text | KSPC/error curves figure-only; degrades least-steeply but from lowest base | https://theses.gla.ac.uk/1863/1/2010hoganphd.pdf |
| closest baseline 3: Tinwala Immediate WITHOUT correction (still had per-char speech + click) — NOT zero feedback | audio, no correction | eyes-free | 8.34 | 2.5% final MSD (Graffiti + careful entry, not comparable to QWERTY) | https://www.yorku.ca/mack/nordichi2010.pdf |

Interpretation for the 0G surface: the nearest measured "no confirmation" QWERTY
condition still had visual key highlight and still lost ~30–34% of phrases with
12.6–14 WPM from novices. Removing the last channel (vision) as well has NO
measured point in the fetched set — expect worse, unquantified here. Note the KSPC
trap: standard/visual-only KSPC looked "good" only because participants skipped
corrections (errors left in); phrase-correct % is the honest metric there.

---

## Recommendation for the 0G surface with ambiguous sector labels

Best measured evidence: **word-level DELAYED auditory feedback (click per stroke +
spoken word at commit) fused with a dictionary error corrector, PLUS a first-stroke
gate with vibrotactile block** — i.e. Tinwala's OneLetter/Delayed hybrid:

- Fastest measured eyes-free touchscreen-text number in set: Delayed 11.1 wpm
  (maxima 20.8–21.5 wpm), overall 10.0 wpm at 95.7% final accuracy with 14.9% of
  text system-corrected and 70.3% raw-error reduction
  (https://www.yorku.ca/mack/nordichi2010.pdf). This is the only setup whose input
  distribution resembles ours (boundary-ambiguous strokes absorbed by regex + MSD
  search over a 9,000-word BNC dictionary, intended word in top-2 94.2%).
- Safety correction for the error side: Delayed alone doubles–triples final error
  (7.0% vs 2.5–3.5%). The OneLetter gate (require one valid stroke per word,
  vibration pulse otherwise, speak first letter) recovers nearly all of it (3.5%,
  76.7% correction gain, list 1.89 vs 2.96) for −0.5 wpm. For a safety-critical
  ergonomic question with 31–40% geometrically ambiguous strokes, take the gate.
- Whole-device vibration alone (no LM needed) buys +21% lab / +20% mobile WPM
  and +13–14pp phrase accuracy on QWERTY
  (https://theses.gla.ac.uk/1863/1/2010hoganphd.pdf). Localized dual-actuator
  reaches ≈ physical-keyboard speed (19.15 wpm mobile) but with significantly
  higher annoyance (F(2,22)=35.4, p<.0001).
- Ultrasound is NOT recommended as the confirmation channel: measured two-point
  discrimination needs ~3 cm separation even with different modulation frequencies
  (86% vs 31%; nothing at 1 cm, p=.071; foci ~1 cm)
  (https://research-information.bris.ac.uk/ws/files/12013908/paper.pdf). No measured
  ultrasound typing study was found; the one mid-air typing study measured 22.25
  peak WPM WITHOUT any haptics
  (http://handtracker.mpi-inf.mpg.de/projects/HandDexterity/content/AirType_CHI2015.pdf).

Costs:
- Latency (ms budgets for click/vibration/speech loops): NOT FOUND numerically in
  fetched sources. Qualitative from review
  (https://ar5iv.org/html/2004.13864v1): ERMs have "large actuation lags" and fixed
  displacement; LRAs faster but narrow-band; piezos need very high voltage and are
  brittle; ultrasonic resonance needs tracking/closed-loop or feed-forward
  compensation. Hoggan latency-specific paper
  (https://doi.org/10.1109/whc.2011.5945463): numbers NOT FOUND (closed).
- Throughput cost of correction UI: ~10% (adjusted rates), 600 ms inter-word gaps
  in playback, cyclic lists averaging 2.43 candidates
  (https://www.yorku.ca/mack/nordichi2010.pdf).
- User acceptance: standard (no-feedback) keyboards score significantly worse on
  mental/physical demand, frustration, annoyance, and perceived performance than
  tactile or physical (F(2,22)=111.35)
  (https://theses.gla.ac.uk/1863/1/2010hoganphd.pdf); strong localized actuators
  significantly annoy vs weak ones (above); speaker audio fails in noise (no mobile
  gain; dead ≥90–96 dB) — earpiece delivery in mobile typing is unmeasured
  (NOT FOUND).
- Hardware: tactile = existing ERM/LRA sufficient for the +20% gain; localized C2 =
  expensive, non-standard, annoying at fixed force; ultrasonic = array + 4–150 V
  drive + ~0.4 W scale power + acoustically transparent display (0.5 mm holes /
  25% open cost −2.4 dB) for a channel that cannot resolve adjacent keys; audio =
  speakers free but masked, earphones unmeasured for typing.

Bottom line: ship (1) per-stroke click with <audio-only, no per-char speech>, (2)
first-sector anchor gate with vibration block (OneLetter pattern), (3) word-commit
speech + dictionary correction with top-2 auditory playback, (4) whole-device
vibration using the existing actuator — and do NOT spend hardware budget on
ultrasound per-key confirmation (measured resolution 3 cm, foci 1 cm) or on
speaker-only audio for noisy use.

DONE

---

## Agent-2 reading, and what it changes here (2026-09-25 06:44)

The measured numbers in this file point somewhere uncomfortable for the obvious design, so
the conclusion is stated explicitly rather than left implicit.

**Audio feedback is weaker than expected.** On a touch keyboard with visual highlighting,
stereo earcons via speakers gave 82.5 % phrases correct in the lab, but the same system on a
noisy subway gave 70.0 % and **no better than standard touchscreens** — i.e. no benefit in the
condition a mobile user actually lives in. Tactile feedback *hurt* more than audio at high
vibration (8.1–10.8 g/s): lower WPM, F(2,22) = 4.9, and tactile KSPC worse than audio
(F(2,22) = 8.22). Ultrasound haptics resolves foci at ~1 cm with 3 cm localisation — coarser
than a 22.5° sector on a 20 mm compass, so per-key ultrasound confirmation is not actionable
here.

**What this means for a 0-force compass:**

1. **The sector fence is a sensory problem, not only a decoder problem.** 31–40 % of real
   strokes land within 10° of a boundary, and the feedback channel that would normally tell
   the user "that was ambiguous" is exactly the one that degrades in noise. Visual feedback
   is unavailable — there is no visible keyboard.
2. **Therefore the disambiguator has to be the language model and the correction path, not
   the feedback channel.** This raises the priority of the LM/brief work (issue #7) again,
   and it means the *undo* path is not a convenience — on this surface it is the primary
   error-recovery mechanism, because the user often cannot tell that an event was ambiguous
   until text appears.
3. **Device vibration is available and free.** The PTH-660 is a tablet with an actuator; a
   whole-device pulse on commit is implementable without new hardware. It is worth testing
   against a silent baseline, with the caveat that this file's evidence for tactiles is
   measured under *handheld vibration*, not a desk-resting tablet.
4. **Do not budget for per-key ultrasound.** Resolution is below the discrimination the
   gesture itself requires.

The concrete experiment this implies, and the one we still cannot run without the tablet:
a three-arm comparison — silent, per-stroke click, per-stroke click + device pulse — with the
cued-sector session, scoring both direction accuracy and *user-perceived confidence*, since
the second is what the sector-fence problem actually costs.
