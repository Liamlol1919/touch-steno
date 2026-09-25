# W11 Verification: Keyless/Touch Performance Ceiling

CLAIM under test: "Nobody has published a touch/steno/chording performance number between roughly 17 WPM (keyless chording) and 180 WPM (professional stenography certification). The best flat-surface typing is 38-55 WPM."

Method: primary sources only (peer-reviewed papers via DOI, vendor pages, App Store listings, Guinness). Web general search was unavailable (auth failure); scholarly metadata via OpenAlex/Crossref APIs + direct page fetches. All WPM burst conversions computed in code, not mental math.

## 1. Commercial touch stenography products

### 1a. Fleksy + Guinness touchscreen record (2014, Marcel Fernandes Filho, Samsung Galaxy S4)
- System: Fleksy virtual keyboard (touch typing, no lift-to-send steno)
- Device: Samsung Galaxy S4 (touchscreen phone)
- Input method: tap typing on glass (autocorrect/predictive REQUIRED OFF per Guinness rules)
- WPM: 25-word standard passage in 17 s = ~88 WPM (word-count); ~113 WPM under standard 5-char definition (160-char passage). Computed, see note.
- Error rate: NONE measured/reported. Pass/fail only; retries allowed; no corrected/uncorrected error rate published.
- Source URL: https://www.guinnessworldrecords.com/news/2014/5/fastest-touch-screen-text-message-record-officially-broken-with-fleksy-keyboard-57380/
- Status: vendor-adjacent record / self-reported burst, confirmed by Guinness as an event. NOT peer-reviewed. NOT sustained text entry. NO error rate.
- Verdict on refutation: DOES NOT REFUTE (fails both "sustained" and "measured error rate" criteria).

### 1b. Fleksy teen record on iPhone (18.19 s)
- System: Fleksy app on iPhone
- Device: iPhone (touchscreen)
- Input method: tap typing on glass
- WPM: 25 words / 18.19 s = ~82.5 WPM (computed)
- Error rate: NONE published.
- Source URL: https://en.wikipedia.org/wiki/Swype (Use records section, citing CNN/Guinness); https://en.wikipedia.org/wiki/Fleksy (Awards section)
- Status: self-reported burst record. NOT peer-reviewed. NO error rate.
- Verdict: DOES NOT REFUTE.

### 1c. Swype records (Franklin Page, Samsung Omnia II / Galaxy S)
- System: Swype gesture keyboard
- Device: Samsung i8000 Omnia II (2010), Samsung Galaxy S (2010)
- Input method: finger-slide gesture typing on touchscreen
- WPM: 35.54 s -> ~42.2 WPM; improved 25.94 s -> ~57.8 WPM (computed; Wikipedia itself states "nearly 58 words per minute"). Below 60 either way.
- Error rate: NONE published.
- Source URL: https://en.wikipedia.org/wiki/Swype
- Status: vendor-employee burst record. NOT peer-reviewed. NO error rate. Below threshold regardless.
- Verdict: DOES NOT REFUTE.

### 1d. Swype creator claim (Cliff Kushler, CTO/founder)
- System: Swype
- Device: touchscreen phones (generic)
- Input method: gesture typing
- WPM: claimed "over 50", personally "55 WPM"
- Error rate: NONE published.
- Source URL: https://en.wikipedia.org/wiki/Swype
- Status: vendor-claim. NOT peer-reviewed. NO error rate.
- Verdict: DOES NOT REFUTE (also numerically inside the claimed 38-55 ceiling).

### 1e. Steno Keyboard (iPad) / Steno Keyboard Pocket (iPhone) — current stenotype-on-glass apps
- System: Steno Keyboard / Steno Keyboard Pocket (Plover-dictionary-compatible steno custom keyboard)
- Device: iPad / iPhone (capacitive touchscreen)
- Input method: multi-touch steno chords on glass; iPhone version explicitly uses chord-then-Translate two-step rhythm ("chord, translate, chord, translate") because clean chord lift-off is unreliable on small glass
- WPM: NO NUMBER PUBLISHED (no speed claim anywhere on product site, App Store page, or support pages)
- Error rate: NONE published.
- Source URLs: https://stenokeyboard.app/ ; https://apps.apple.com/us/app/steno-keyboard-pocket/id6792498937
- Status: vendor product pages. No performance claim at all.
- Verdict: DOES NOT REFUTE (no number to evaluate).

### 1f. iStenoPad / StenoPad / StenoVid (older stenotype-on-glass apps)
- System: iStenoPad and similar iPad steno apps
- Device: iPad (touchscreen)
- Input method: steno chords on glass
- WPM: NO NUMBER FOUND. iStenoPad returns zero results on the current App Store search API (delisted/dead); no paper in OpenAlex for "stenotype touchscreen glass ipad" (count 0); no WPM in any retrievable primary source.
- Error rate: NONE.
- Source URLs: App Store search API (no listing); OpenAlex work search (0 results)
- Status: dead products, no citable performance number.
- Verdict: DOES NOT REFUTE.

### 1g. CharaChorder One (300 WPM) / Lite (250 WPM) — EXCLUDED, documented for completeness
- System: CharaChorder One / Lite chorded entry
- Device: dedicated hardware with 9 physical 5-directional switches per hand (One) / traditional-style switches (Lite)
- Input method: physical-switch chording (NOT a touch surface, capacitive pad, or keyless/force-less input)
- WPM: manufacturer-claimed 300 / 250 WPM; founder reportedly banned from online typing competitions
- Error rate: NO independent measured error rate found.
- Source URL: https://en.wikipedia.org/wiki/Chorded_keyboard (Commercial devices section)
- Status: vendor-claim on PHYSICAL hardware. Out of scope by device definition.
- Verdict: EXCLUDED FROM SCOPE (physical switches, not touch/keyless).

## 2. Stylus/finger handwriting recognition on tablets (2024-2026 absolute numbers)

### 2a. Handwriting for Text Input in XR (TVCG 2024, peer-reviewed, n=72)
- System: digital-ink handwriting app with recognition, pen-like XR controllers on physically aligned vs mid-air surfaces
- Device: VR / video-see-through AR with surface alignment (stylus-analogous pen input)
- Input method: handwriting (stylus/finger-formed script) + recognizer
- WPM: simple sentences 17.85 WPM; complex sentences 15.07 WPM (sustained 10-minute sessions x2, 10+10 sentences each)
- Error rate: 0.51% MSD ER (simple), 1.74% MSD ER (complex) — measured.
- Source URL: https://doi.org/10.1109/tvcg.2024.3372124
- Status: peer-reviewed (IEEE TVCG).
- Verdict: SUPPORTS CLAIM (order of magnitude below 60; recognition accuracy improved, but human handwriting speed itself is the ceiling).

### 2b. Adult handwriting copying baselines
- System: human handwriting (pen on paper; upper bound for any recognizer pipeline since recognizer cannot be faster than the hand)
- Device: N/A (motor baseline)
- Input method: handwriting
- WPM: adult copying mean 68 letters/min ~= 13 WPM; range 26-113 letters/min ~= 5-20 WPM; police-record peak 120-155 chars/min, absolute max 190 chars/min ~= 38 WPM
- Error rate: N/A (motor speeds, transcription-fidelity studies)
- Source URL: https://en.wikipedia.org/wiki/Words_per_minute (Handwriting section)
- Status: peer-reviewed literature summarized in encyclopedia (Hardcastle & Matthews 1991; occupational-therapy adult norms; Zaviani & Wallen 2006).
- Verdict: SUPPORTS CLAIM (fastest human handwriting ~= 38 WPM, still below 60).

### 2c. Handwriting RECOGNITION accuracy vs ENTRY RATE distinction (2024-2026)
- Character/word accuracy of modern recognizers (offline Chinese, MNIST, ICDAR-line models) is 95-99%+ in benchmarks (e.g., 2.61% error Chinese handwriting contest), but these are RECOGNITION accuracies on fixed image sets, NOT text-entry WPM.
- No 2024-2026 source found reporting sustained stylus/finger text ENTRY above 60 WPM with a measured entry error rate. The text-entry studies (cf. 2a) report ~15-18 WPM.
- Source URL: https://en.wikipedia.org/wiki/Handwriting_recognition (Results since 2009 section)
- Status: peer-reviewed recognition benchmarks; none is an entry-rate counterexample.
- Verdict: DOES NOT REFUTE.

### 2d. Samsung / Google stylus typing speeds
- Samsung S Pen / Google Gboard handwriting/stylus input: NO sustained-WPM-with-error-rate number found in any primary source checked (vendor pages publish no WPM; no OpenAlex text-entry study above threshold found).
- Verdict: NO COUNTEREXAMPLE FOUND in this sub-area.

## 3. Multi-touch chord keyboards, touch typing research, HCI studies

### 3a. Palin et al. 2019, "How do People Type on Mobile Devices?" (n ~ 37,000) — peer-reviewed
- System: stock touchscreen keyboards (phones/tablets)
- Device: participants' own mobile touchscreen devices
- Input method: tap typing on glass (1-2 fingers/thumbs)
- WPM: mean 36.2 WPM (as summarized on the WPM reference page citing this paper)
- Error rate: 2.3% uncorrected errors, measured.
- Source URLs: https://doi.org/10.1145/3338286.3340120 ; https://en.wikipedia.org/wiki/Words_per_minute (Alphanumeric entry section)
- Status: peer-reviewed (ACM MobileHCI '19).
- Verdict: SUPPORTS CLAIM (lands at the bottom of the claimed 38-55 band; mean, sustained, with error rate).

### 3b. Ruan et al. 2018, "Comparing Speech and Keyboard Text Entry" — peer-reviewed, laboratory UPPER BOUND
- System: built-in Apple iOS QWERTY (English) / Pinyin (Mandarin) on iPhone 6 Plus; Baidu Deep Speech 2 as speech comparator
- Device: Apple iPhone 6 Plus (touchscreen phone)
- Input method: touchscreen tap typing
- WPM: 52 WPM English, 43 WPM Mandarin — explicitly framed as keyboard "upper-bound performance" under ideal lab transcription conditions
- Error rate: measured — 11.22% corrected error rate during entry, 0.79% uncorrected in final text (English keyboard condition)
- Source URL: https://doi.org/10.1145/3161187
- Status: peer-reviewed (ACM). Sustained short-message transcription with error rates.
- Verdict: SUPPORTS CLAIM (highest peer-reviewed sustained touch number found: 52 WPM, still below 60, with measured error rates).

### 3c. KALQ optimized split-screen thumb keyboard — peer-reviewed layout, vendor-neutral
- System: KALQ split-screen thumb layout (computationally optimized)
- Device: smartphones/tablets (touchscreen)
- Input method: two-thumb tap typing on glass
- WPM: NO absolute >60 number; published claim is +34% relative speed-up over QWERTY in the underlying study; shipping app stayed in beta (Oct 2013 build as of 2017)
- Error rate: evaluated in the research program, but no >60 WPM condition reported.
- Source URL: https://en.wikipedia.org/wiki/KALQ_keyboard
- Status: peer-reviewed research project; no counterexample number.
- Verdict: DOES NOT REFUTE.

### 3d. GKOS / MessagEase touch chord keyboards
- System: GKOS (12-key touch chord, most frequent chars single-tap), MessagEase
- Device: smartphones (touchscreen)
- Input method: touch chording on glass
- WPM: only beginner-performance studies surfaced (OpenAlex: "Beginner Performance with the GKOS Chorded Keyboard"); NO published >60 WPM sustained number with error rate found.
- Error rate: studied at beginner level; no qualifying number.
- Source URLs: https://en.wikipedia.org/wiki/Chorded_keyboard (Standards/Commercial devices); OpenAlex GKOS search
- Status: peer-reviewed beginner studies + shipping apps; no counterexample number.
- Verdict: DOES NOT REFUTE.

### 3e. Other high-WPM anchors checked and excluded by device definition
- Physical stenotype certification 180/200/225 WPM; Guinness physical-steno 360 WPM at 97.23% accuracy; Plover on NKRO physical keyboards; Twiddler/Microwriter/BAT physical chorders; CharaChorder physical switches — all use physical travel/switches, NOT touch/capacitive/keyless input. They are the claim's upper anchor, not counterexamples.
- Source URLs: https://en.wikipedia.org/wiki/Stenotype ; https://en.wikipedia.org/wiki/Words_per_minute (Stenotype section); https://opensteno.org/ ; https://en.wikipedia.org/wiki/Chorded_keyboard
- Verdict: EXCLUDED FROM SCOPE (confirms 180+ pole exists only on physical keys).

## WPM conversion note (computed, not hand-derived)
- Standard 25-word Guinness passage ("The razor-toothed piranhas...") timed at 17.0 s -> 88.2 WPM (word-count basis); 160-char passage -> 112.9 WPM (5-char standard).
- 35.54 s -> 42.2 WPM; 25.94 s -> 57.8 WPM; 18.19 s -> 82.5 WPM.
- None of these burst records carries a measured error rate or sustained-entry protocol, so none satisfies the refutation criterion regardless of arithmetic basis.

## Verdict
- Highest SUSTAINED touch number WITH a measured error rate found: Ruan et al. 2018, 52 WPM (0.79% uncorrected / 11.22% corrected), peer-reviewed — below 60.
- Highest touch burst numbers (Fleksy ~82-113 WPM range depending on WPM definition) have NO measured error rate, are single-phrase bursts with autocorrect off and retries, and are NOT peer-reviewed sustained entry.
- Handwriting entry with recognition: ~15-18 WPM with measured MSD error (peer-reviewed, 2024).
- Touch steno products (Steno Keyboard family): no published WPM at all; iStenoPad-class apps: no published WPM (delisted).
- NO COUNTEREXAMPLE FOUND: no system on a touch surface, capacitive pad, or keyless/force-less input reporting sustained text entry above 60 WPM WITH a measured error rate was found after searching commercial products, handwriting literature 2024-2026, and HCI touch/chord studies.

CLAIM HOLDS

DONE
