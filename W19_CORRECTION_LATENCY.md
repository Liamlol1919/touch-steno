# W19 — Latency cost of correction in fast text entry

Scope: narrow decision-relevant question — can a post-hoc correction path hide a
cycle-time-derived speed ceiling at 3–5 input events/s?
ESTABLISHED inputs (do not re-derive, given by project):
evidence floor 88 ms (8 frames at 91 Hz); out-and-back 150–250 ms + sub-gate
return = cycle 180–280 ms = 3.3–5.5 events/s ≈ 100–218 WPM; record stenographer
360 WPM with ~100,000 memorised short forms attributed to dictionary, not fingers;
free-motion event supply 0.9–2.6 events/s.

Rule followed below: every number is quoted from a source with its URL.
Where no source number exists the entry is NOT FOUND. No guessing.

## 1. Stenography: correction speed / cost / corrected-vs-uncorrected ratio

| system | correction mechanism | latency / cost | throughput effect | source URL |
|---|---|---|---|---|
| Plover / stenotype (general) | asterisk (`*`) single stroke deletes previous word; described as "much faster overall if you make mistakes" vs holding QWERTY backspace; Plover lesson: "use the `*` key to undo Plover's unexpected output" | correction time in ms: NOT FOUND; correction rate (corrections/min): NOT FOUND | NOT FOUND (no measured WPM delta with vs without asterisk correction found) | https://www.otdude.com/ot-practice/an-occupational-therapist-begins-to-learn-stenography-with-plover ; https://opensteno.org/learn-plover/lesson-1-fingers-and-keys.html |
| Court reporting certification (NCRA RPR) | post-session transcription: "three minutes to attach steno notes and then 75 minutes to transcribe" a 5-min take; pass at 95% accuracy on each leg; legs are 180 WPM literary, 200 WPM jury charge, 225 WPM Q&A | correction time per error in ms: NOT FOUND | accuracy floor, not a throughput delta: 95% on each of 180 / 200 / 225 WPM legs | https://www.ncra.org/certification/NCRA-Certifications/registered-professional-reporter ; https://catalog.tri-c.edu/programs/certified-stenowriting-certificate-proficiency/certified-stenowriting-certificate-proficiency.pdf |
| Court reporting (advanced / realtime) | RMR legs "up to 260 words per minute with 95% accuracy"; CRR "five minutes of real-time testimony at 200 words per minute with 96% accuracy"; broadcast/CART master: "22.5 minute dictation at variable speeds up to 225 wpm" passed "with a minimum score of 97.5%" | correction time in ms: NOT FOUND | NOT FOUND as WPM cost; only pass/fail accuracy thresholds listed | https://mtdsreporters.com/blog/guide-to-court-reporter-certifications ; https://www.nvra.org/certifications |
| Steno record / professional level | Mark Kislingbury record "360 words per minute (WPM) at 97% accuracy" (US Legal Support); Plover FAQ table: professional 225 WPM, steno world record 370 WPM, fastest QWERTY ~200–230 WPM, amateur steno 160+ WPM | audio-correction / kata time: NOT FOUND; dictionary-hit latency: NOT FOUND | corrected-vs-uncorrected output ratio: NOT FOUND | https://www.uslegalsupport.com/blog/celebrating-stenography-where-it-started-and-how-its-changed-over-time ; https://plover.wiki/index.php/FAQ |
| Steno error mechanism (CAT / dictionary) | single missed/extra key yields "mistranslate (wrong word) or untranslate (no dictionary match)"; "Words that are not in the reporter's dictionary will be translated phonetically or will appear in stenotype"; some reporters "use scopists to translate and edit" | ms cost of a mistranslate fix: NOT FOUND | NOT FOUND | https://planetdepos.com/appreciating-a-court-reporters-skill-sets ; https://en.wikipedia.org/wiki/Stenotype |

Finding §1: no source found that measures steno correction latency in ms,
corrections per minute, correction time, or corrected/uncorrected throughput ratio.
Katas, audio-correction drills, and dictionary-hit timings: NOT FOUND.

## 2. Predictive text / LM decoder: added latency in ms, perceptibility, WPM effect

| system | correction mechanism | latency / cost | throughput effect | source URL |
|---|---|---|---|---|
| LLM keyboard decoder (FLAN-T5-small 77M, Pixel 6 on-device) | LLM seq2seq decode of taps/gestures/flexible mixtures, beam-5 top-4 candidates | "processed each word in 59 milliseconds (SD = 6.97), with execution times ranging from 37 to 94 milliseconds. The on-device latency was lower than the cloud-based implementation" | decode accuracy, not WPM delta: "93.1% top-1 accuracy on user-drawn gestures" (vs SHARK2 73.2%), "95.4% on real-word tap typing data"; synthetic flexible average 88.0% top-1, 95.0% top-3 | https://pmc.ncbi.nlm.nih.gov/articles/PMC12723528 ; https://doi.org/10.1145/3706598.3714314 |
| Same decoder, web prototype (Pixel 6 Chrome → Colab T4 via ngrok) | same as above, web deployment | "average latency of 246 milliseconds, including delays caused by both computation and network communication. This latency is well within the acceptable range for a real-time typing experience" | user-study speed "29.1 WPM (SD = 4.9)", "WER was 0.79% (SD = 1.17%)"; method mix 35.9% gesture / 29.0% tap / 6.1% multi-stroke / 29.0% tap-gesture; "over 50% [of words ≥6 chars] were entered using multi-stroke gestures or tap-gestures" | https://pmc.ncbi.nlm.nih.gov/articles/PMC12723528 |
| MobileHCI 2019, 37,000 volunteers (copy task, own phones) | autocorrect vs predictive (suggestion selection) vs none | selection-look cost modelled as 0.45 s per suggestion check; keystroke 0.26 s (see next row); decoder ms: NOT FOUND in this source | "Participants who used predictive text typed an average of 33 words per minute… slower than those who didn't use an intelligent text entry method (35 words per minute) and significantly slower than participants who used autocorrect (43 words per minute)"; corpus stats "Avg = 36.2 [WPM] SD = 13.2, 75%ile: 44, Fastest: 85 WPM"; "Error rates (uncorrected) Avg = 2.34% SD = 2.08, 75%ile: 3.1%"; two-thumb mean 38 WPM | https://theconversation.com/do-you-use-predictive-text-chances-are-its-not-saving-you-time-and-could-even-be-slowing-you-down-170163 ; https://doi.org/10.1145/3338286.3340120 ; https://userinterfaces.aalto.fi/typing37k ; https://www.slideshare.net/slideshow/how-do-people-type-on-mobile-devices-observations-from-a-study-with-37000-volunteers-mobilehci-2019/178444210 |
| Kristensson & Müllner simulation of predictive-text strategy (reported in The Conversation) | type-then-look / min-word-length / perseverance=5 model | parameters "average time it takes a user to hit a key … 0.26 seconds" and "average time it takes a user to look at a predictive text suggestion and select it … 0.45 seconds" | "deep red … improvement of two words per minute compared to not using predictive text"; "predictive text could slow a user down by as much as eight words per minute"; optimum "only sought for words with at least six letters … after typing three letters" | https://theconversation.com/do-you-use-predictive-text-chances-are-its-not-saving-you-time-and-could-even-be-slowing-you-down-170163 ; https://dl.acm.org/doi/10.1145/3411764.3445566 |
| Text-input latency study (Schmid et al., 31 participants, physical keyboard, copy + correct short snippets) | manual correction under injected latency | conditions "low latency of 20 ms and … high latency of 200 ms"; cited baselines "Shneiderman et al. recommends an end-to-end latency of 50 to 150 ms for simple tasks such as typing", "Ng et al. found that latency below 20 ms can be noticed on touch screens" | "latency had no significant effect on users' performance during the copy task, but correcting texts was affected significantly by high latency"; "fast typers are more likely to notice latency than slow typers"; perceived "higher effort and frustration when typing with high latency" | https://epub.uni-regensburg.de/55007/1/text-input-latency.pdf ; https://hci.ur.de/publications/effects_of_text_input_latency_on_performance_and_task_load_2024 ; https://dl.acm.org/doi/10.1145/3626705.3627784 |
| T9 / keypad model (MacKenzie CHI 2000) | T9 prediction vs multi-press / two-key | inspection cost "each inspection takes 500 ms"; keypad timeout "1.5 seconds"; Fitts coefficients study-specific | model predictions: "T9 45.7 [wpm expert] / 40.6"; "Two-key 25.0 / 22.2"; "Multi-press – wait for timeout – timeout kill 22.5 / 27.2 [and] 20.8 / 24.5"; "If the user visually verifies input 50% of the time … each inspection takes 500 ms … T9 prediction falls to 35 wpm" | https://www.yorku.ca/mack/chi00.html |
| Expert mobile aversion model (Banovic et al., CHI 2017) | user slows down to avoid costly errors; "upper bound" (best-case top speed) vs "expected mean" (average with errors) | ms cost per error / correction latency: NOT FOUND in accessible abstract | numeric upper-bound vs expected-mean WPM values: NOT FOUND in accessible abstract | https://dl.acm.org/doi/10.1145/3025453.3025695 |

Perceptible/blocking summary from sources: 20 ms can already be noticed on
touchscreens; 50–150 ms is the cited acceptable end-to-end typing range;
200 ms significantly degrades the correction task but not the copy task;
246 ms web-decoder latency is asserted "well within acceptable range" without a
blocking threshold number; on-device 59 ms/word decode is the only measured
per-word LM latency found.

## 3. Sustained corrections-per-minute upper bound while holding speed

| claim sought | number found | source URL |
|---|---|---|
| max corrections/min a user can sustain without losing speed | NOT FOUND | — |
| observed uncorrected-error frequency in classroom timed writings (Joyner et al. 1993, cited in ODU review of >750 time writings): "speeds ranging from 39 to 49 gross words per minute while leaving uncorrected one-half to three-quarters of an error per minute" | 0.5–0.75 uncorrected errors/min at 39–49 GWPM (observed rate, NOT a maximum-sustainable bound) | https://digitalcommons.odu.edu/cgi/viewcontent.cgi?article=1352&context=ots_masters_projects |
| expert-mobile model distinguishing best-case "upper bound" speed from "expected mean" speed given error-correction cost | numeric bound: NOT FOUND in accessible record | https://dl.acm.org/doi/10.1145/3025453.3025695 |

Finding §3: no measured upper bound on corrections per minute while maintaining
speed was found in the sources consulted.

## 4. Undo / backspace behaviour in fast typing: rates and clustering

| system | correction mechanism | latency / cost | throughput effect | source URL |
|---|---|---|---|---|
| BiAffect in-the-wild keyboard, 128 adults, 2948 daily observations (Liu et al., JMIR 2024) | backspace key; "backspace rate (i.e., the percentage of backspace use in a total number of keypresses)" | "average daily backspace rate is 0.161 (SD 0.062)"; mood-disorder group "0.165 (SD 0.066)", healthy control "0.145 (SD 0.051)", group difference P=.11 n.s.; mixture phenotypes "mean backspace rates of 0.112, 0.180, and 0.268, respectively, with a SD of 0.048" (Low 37.5% / Medium 54.4% / High 8.1%) | WPM effect of backspace rate: NOT FOUND | https://www.jmir.org/2024/1/e51269 ; https://pmc.ncbi.nlm.nih.gov/articles/PMC11558221 |
| French university cohort, 1301 students, sentence-copy (Pinet et al. 2022) | free correction (no instruction on error reaction); accuracy metric includes corrections via insert/delete/substitute distance | error-inclusive rates: "around 12% for the most proficient and 20% for the least proficient typists" vs historical typewriter "typically under 3.2%" and "0.3% in a study of a single typist spanning over 1.3 million keystrokes"; group means "most proficient … 80 wpm (IQR = 20), accuracy 88% (IQR = 4.3)" vs "least … 54 wpm (IQR = 18), accuracy 79% (IQR = 8.3)" | backspace-to-WPM cost in ms: NOT FOUND | https://pmc.ncbi.nlm.nih.gov/articles/PMC9356123 |
| MobileHCI 37k copy task | backspace + autocorrect available | uncorrected error "Avg = 2.34% SD = 2.08" (see §2) | per-keystroke correction time: NOT FOUND | https://www.slideshare.net/slideshow/how-do-people-type-on-mobile-devices-observations-from-a-study-with-37000-volunteers-mobilehci-2019/178444210 |
| Correction clustering (do undos cluster after errors?) / cascade dynamics | — | measured clustering statistic: NOT FOUND; only qualitative model note that "typists never repeatedly miss backspace and cause a correction cascade; a user in danger of doing so will slow down" and efficiency claim that "backspace correction is extremely close to the Shannon bound until error rates increase above 6%, at which point it catastrophically fails" (simulated, no measured per-minute cascade rate) | NOT FOUND | https://pdfs.semanticscholar.org/9826/a93bc36d30c0070eba3ce82481a83a01fbd0.pdf |

Finding §4: measured undo/backspace *rates* exist (11–27% of keypresses across
phenotypes; ~0.16 overall; 12–20% error-inclusive keystroke mismatch in students;
2.34% uncorrected errors at 36.2 WPM in the 37k copy task), but no source found
measures whether corrections cluster after errors or the ms cost per undo at
fast-typing speeds.

## Verdict: can 3–5 events/s input be corrected after the fact without becoming the bottleneck?

The literature consulted cannot answer it. Explicitly:

- No source measures post-hoc correction throughput at 3–5 correction-relevant
  events/s (180–300/min). The closest throughput numbers are an order of
  magnitude below or in different units: 33/35/43 WPM by aid condition at
  ~0.26 s/keystroke + 0.45 s/suggestion-check; 29.1 WPM at 0.79% WER in the LLM
  flexible-typing study; 36.2 WPM at 2.34% uncorrected errors in the 37k study;
  39–49 GWPM with 0.5–0.75 uncorrected errors/min in classroom writings.
- The only measured per-unit LM latency, 59 ms/word on-device (37–94 ms range),
  is a decode cost, not a correction-throughput ceiling, and no study tests it
  against a sustained 3–5 events/s input stream or against the 88 ms evidence
  floor. The 246 ms web figure explicitly bundles network time.
- The only causal latency-on-correction result (20 vs 200 ms, n=31) says
  correction — not copying — is significantly degraded by high latency, which
  cuts against assuming correction "hides" delay, but it does not quantify a
  corrections-per-minute limit.
- Steno, the one system operating near the target rate (180–260 WPM
  certification legs at 95–96%, record 360 WPM at 97%), publishes only accuracy
  floors and a one-stroke asterisk undo mechanism, with no measured correction
  time, correction rate, or corrected/uncorrected throughput ratio.

Therefore: no number in the sources says a 3–5 events/s input can be corrected
after the fact without becoming the bottleneck. Answering it requires a direct
experiment measuring sustained corrections/min and per-correction ms at the
target event rate, not a literature inference.

DONE
