# W22 — Seconds-per-correction for fast text entry

Rule: every number below was seen in a source. Each row carries its source URL.
Where no source number exists the entry is NOT FOUND. No guessing.
No arithmetic below is presented as a sourced value; derived mappings are labeled DERIVED.

## 1. STENOGRAPHY: measured correction behaviour in real dictation

| setting | what was timed | value | unit | source URL | how it maps to our need |
|---|---|---|---|---|---|
| Plover FAQ speed table | Professional stenographer typical speed (not a correction time) | 225 | WPM | https://plover.wiki/index.php/FAQ | Context rate at which any correction must fit; NOT a per-correction time |
| Plover FAQ speed table | Steno world record (not a correction time) | 370 | WPM | https://plover.wiki/index.php/FAQ | Upper-bound stream speed; NOT a per-correction time |
| Plover FAQ speed table | Amateur stenographer (not a correction time) | 160+ | WPM | https://plover.wiki/index.php/FAQ | Lower-bound trained-steno rate; NOT a per-correction time |
| Plover FAQ speed table | Experienced professionals sustained transcription (not a correction time) | 300 | WPM | https://plover.wiki/index.php/FAQ | Sustained stream that corrections must not break; NOT a per-correction time |
| Plover FAQ speed table | Fastest QWERTY typists, comparable material (not a correction time) | 200–230 | WPM | https://plover.wiki/index.php/FAQ | QWERTY ceiling for comparison; NOT a per-correction time |
| Plover FAQ speed table | Average QWERTY / fast QWERTY / handwriting / avg speech (not correction times) | 40 / 120 / 30 / 200 | WPM | https://plover.wiki/index.php/FAQ | Baselines only; NOT per-correction times |
| Plover / stenotype asterisk `*` undo | Time to execute one asterisk correction stroke | NOT FOUND | ms | https://opensteno.org/learn-plover/lesson-1-fingers-and-keys.html ; https://www.otdude.com/ot-practice/an-occupational-therapist-begins-to-learn-stenography-with-plover | Mechanism exists (single stroke deletes previous word; "much faster than holding backspace") but no measured ms found |
| Court-reporting certification legs | Per-correction time; corrections per minute | NOT FOUND | — | https://www.ncra.org/certification/NCRA-Certifications/registered-professional-reporter | Only accuracy floors are published (RPR legs 180 WPM literary / 200 WPM jury charge / 225 WPM Q&A at 95%; RMR up to 260 WPM at 95%; CRR 200 WPM at 96%; broadcast/CART up to 225 WPM at 97.5% — values as reported in secondary summaries https://mtdsreporters.com/blog/guide-to-court-reporter-certifications and https://www.nvra.org/certifications, and Tri-C proficiency catalog https://catalog.tri-c.edu/programs/certified-stenowriting-certificate-proficiency/certified-stenowriting-certificate-proficiency.pdf); no per-correction seconds |
| Steno record accuracy | Per-correction time at record speed | NOT FOUND | — | https://www.uslegalsupport.com/blog/celebrating-stenography-where-it-started-and-how-its-changed-over-time | Record cited as 360 WPM at 97% accuracy; gives an error residual, NOT a correction latency |
| Steno mistranslate / untranslate / scopist edit | ms cost of fixing one mistranslate | NOT FOUND | ms | https://planetdepos.com/appreciating-a-court-reporters-skill-sets ; https://en.wikipedia.org/wiki/Stenotype | Mechanism described only qualitatively; no timing |
| Stenographer "kata" / audio-correction drill / dictionary-hit latency | Time per correction event | NOT FOUND | ms | — | No source found |

Finding §1: no source found measures steno per-correction seconds, corrections/min, or corrected-vs-uncorrected throughput ratio.

## 2. GENERAL FAST TYPING: detection + fix latency, and correction factors in WPM standards

| setting | what was timed | value | unit | source URL | how it maps to our need |
|---|---|---|---|---|---|
| Typing-test standard (SpeedTypingOnline equations) | Word definition for WPM | 5 | characters = 1 word (spaces, numbers, letters, punctuation included; Shift/Backspace excluded) | https://www.speedtypingonline.com/typing-equations | Defines the unit in which the correction penalty below is expressed |
| Typing-test standard (SpeedTypingOnline equations) | Net WPM formula | Net = Gross − (uncorrected errors / minutes) | WPM | https://www.speedtypingonline.com/typing-equations | THE actual correction factor used: 1 WPM deducted per uncorrected error per minute. Example sourced verbatim: 80 gross WPM for 2 min with 8 uncorrected errors → error rate 4/min → net 76 WPM |
| Typing-test standard (SpeedTypingOnline equations) | Penalty weight | 1 | WPM lost per mistake per minute | https://www.speedtypingonline.com/typing-equations | Correction factor, NOT a seconds-per-correction measure |
| Typing-test standard (SpeedTypingOnline equations) | Which errors are penalized | only uncorrected errors; corrected errors get no extra penalty beyond time already lost | rule (no numeric latency) | https://www.speedtypingonline.com/typing-equations | Standard explicitly states: corrected-error time cost is "already built in" via rhythm disruption + function-key presses that "take time to press and do not count as a keyed entry"; worked example: 20 WPM for 1 min with 20 corrected errors still yields error-free text, and penalizing all errors would wrongly give 0 WPM. Per-correction seconds: NOT FOUND |
| Typing-test standard (SpeedTypingOnline equations) | Accuracy definition | correct chars / total entries × 100; counts ALL errors whether corrected or not | % | https://www.speedtypingonline.com/typing-equations | Accuracy (likelihood next char is right) vs Net WPM (productivity); NOT a latency |
| KLM / GOMS (Card–Moran–Newell) | Mental preparation operator M | 1.35 | s | https://en.wikipedia.org/wiki/Keystroke-level_model | Candidate cost of one re-plan/re-detect step IF a correction needs an M; sourced as model constant, NOT as a measured correction |
| KLM / GOMS scope | Error modeling | model "only predict[s] behaviour of experts without errors"; "GOMS does not account for errors"; KLM "execution of the method has to be error-free"; KLM prediction RMSE 21% | statement | https://en.wikipedia.org/wiki/Keystroke-level_model | Standards bodies for KLM give NO correction factor; per-correction seconds: NOT FOUND |
| Karat et al. 1999 via WPM article | Transcription rate, average computer users | 32.5 | WPM | https://en.wikipedia.org/wiki/Words_per_minute | Baseline speed; NOT correction time |
| Karat et al. 1999 via WPM article | Composition rate | 19.0 | WPM | https://en.wikipedia.org/wiki/Words_per_minute | Baseline speed; NOT correction time |
| Karat et al. 1999 via WPM article | Fast / moderate / slow groups | 40 / 35 / 23 | WPM | https://en.wikipedia.org/wiki/Words_per_minute | Baseline speeds; NOT correction times |
| French university cohort, sentence copy, n=1301 (Pinet et al. 2022) | Most-proficient group mean speed | 80, IQR 20 | WPM | https://pmc.ncbi.nlm.nih.gov/articles/PMC9356123/ | Speed at which their 12% error-inclusive rate was observed; NOT a per-correction time |
| Same cohort | Most-proficient accuracy | 88, IQR 4.3 | % | https://pmc.ncbi.nlm.nih.gov/articles/PMC9356123/ | Accuracy inclusive of corrections (IDS distance); NOT a latency |
| Same cohort | Least-proficient group mean speed | 54, IQR 18 | WPM | https://pmc.ncbi.nlm.nih.gov/articles/PMC9356123/ | Speed at which their 20% error-inclusive rate was observed; NOT a per-correction time |
| Same cohort | Least-proficient accuracy | 79, IQR 8.3 | % | https://pmc.ncbi.nlm.nih.gov/articles/PMC9356123/ | Accuracy inclusive of corrections; NOT a latency |
| Same paper, citing prior typewriter studies | Typewriter error rates (Grudin 1983; Salthouse 1986) | typically under 3.2 | % | https://pmc.ncbi.nlm.nih.gov/articles/PMC9356123/ | Historical error residual; NOT a correction time |
| Same paper, citing Logan 1999 | Single-typist 1.3M keystrokes error rate | 0.3 | % | https://pmc.ncbi.nlm.nih.gov/articles/PMC9356123/ | Historical error residual; NOT a correction time |
| Same paper, methods | Per-correction / inter-keystroke correction latency | NOT FOUND | ms | https://pmc.ncbi.nlm.nih.gov/articles/PMC9356123/ | Timing params defined (RT = stimulus to first keystroke; IKI = between keystrokes) but no per-correction seconds reported |
| BiAffect in-the-wild keyboard, 128 adults, 2948 daily observations (Liu et al., JMIR 2024) | Mean daily backspace rate (backspaces / all keypresses) | 0.161, SD 0.062 | proportion | https://pmc.ncbi.nlm.nih.gov/articles/PMC11558221 | Correction FREQUENCY (rate), NOT seconds per correction |
| Same study | Mood-disorder group backspace rate | 0.165, SD 0.066 | proportion | https://pmc.ncbi.nlm.nih.gov/articles/PMC11558221 | Subgroup rate; NOT a latency |
| Same study | Healthy-control backspace rate; group difference | 0.145, SD 0.051; P=.11 n.s. | proportion | https://pmc.ncbi.nlm.nih.gov/articles/PMC11558221 | No group effect; NOT a latency |
| Same study, 3-class mixture | Mean backspace rates Low/Medium/High; SD; shares | 0.112 / 0.180 / 0.268; SD 0.048; 37.5% / 54.4% / 8.1% (n=47/72/9) | proportion | https://pmc.ncbi.nlm.nih.gov/articles/PMC11558221 | Distribution of correction frequency; NOT seconds per correction |
| Classroom timed writings (Joyner et al. 1993 via ODU review) | Uncorrected-error frequency at 39–49 gross WPM | 0.5–0.75 | uncorrected errors/min | https://digitalcommons.odu.edu/cgi/viewcontent.cgi?article=1352&context=ots_masters_projects | Observed residual rate, NOT max-sustainable rate and NOT per-correction seconds |
| Keystroke-level error-detection + backspace-press + retype latency in fast typists | Measured ms per corrected character | NOT FOUND | ms | — | No keystroke-level study consulted reports a per-corrected-character detection-to-fix latency or its distribution |

Finding §2: the only formal "correction factor" in typing-speed standards found is Net = Gross − uncorrected-errors/min (1 WPM per error/min), which deliberately adds NO extra penalty for corrected errors because the time cost is assumed already incurred — but the standard gives no seconds-per-correction number.

## 3. TOUCH / IME CORRECTION: autocorrect / LM suggestion correction time

| setting | what was timed | value | unit | source URL | how it maps to our need |
|---|---|---|---|---|---|
| Kristensson simulation params (via The Conversation, citing prior data + 37k study) | Mean time to hit a key | 0.26 | s | https://theconversation.com/do-you-use-predictive-text-chances-are-its-not-saving-you-time-and-could-even-be-slowing-you-down-170163 | Per-press cost; DERIVED mapping only: one backspace + one retype ≈ 2 presses (not sourced as a correction); detection/decision extra |
| Kristensson simulation params (same) | Mean time to look at + select a predictive suggestion | 0.45 | s | https://theconversation.com/do-you-use-predictive-text-chances-are-its-not-saving-you-time-and-could-even-be-slowing-you-down-170163 | Closest sourced proxy to "dwell/check time on an LM suggestion": 0.45 s per suggestion check |
| MobileHCI 2019, 37,000 volunteers, copy task on own phones (Palin et al.) | Mean speed by aid: predictive / no-aid / autocorrect | 33 / 35 / 43 | WPM | https://theconversation.com/do-you-use-predictive-text-chances-are-its-not-saving-you-time-and-could-even-be-slowing-you-down-170163 ; https://doi.org/10.1145/3338286.3340120 | Aid-level throughput deltas, NOT per-correction seconds |
| T9 keypad model (MacKenzie CHI 2000) | Visual inspection cost per check (parametric assumption) | 500 | ms | http://www.yorku.ca/mack/chi00.html | Sourced model value for "verify input" per word check; closest phone-era visual-verification proxy |
| Same T9 model | Effect of verifying 50% of words at 500 ms/inspection | T9 prediction falls to 35 | WPM (from 45.7 index / 40.6 thumb expert) | http://www.yorku.ca/mack/chi00.html | Quantifies how a 0.5 s/check cost collapses expert T9 throughput; NOT a measured human correction |
| Same T9 model | Expert predictions: T9 / two-key / multi-press (wait/kill) | T9 45.7/40.6; two-key 25.0/22.2; multi-press 22.5/27.2 and 20.8/24.5 | WPM (index/thumb) | http://www.yorku.ca/mack/chi00.html | Error-free expert ceiling; correction cost modeled separately via inspection param above |
| Same T9 model | Keypad timeout | 1.5 | s | http://www.yorku.ca/mack/chi00.html | System wait cost, NOT human correction time |
| LLM keyboard decoder (FLAN-T5-small, Pixel 6 on-device) | Decode compute per word | 59, SD 6.97, range 37–94 | ms/word | https://pmc.ncbi.nlm.nih.gov/articles/PMC12723528 | SYSTEM latency per word, NOT human seconds-per-correction |
| Same decoder, web prototype (Chrome → Colab T4 via ngrok) | End-to-end response incl. network | 246 (model section); 246, SD 174 (user-study section) | ms | https://pmc.ncbi.nlm.nih.gov/articles/PMC12723528 | System+network latency, NOT human correction time |
| Same decoder user study (flexible tap/gesture typing) | Mean input speed | 29.1, SD 4.9 | WPM | https://pmc.ncbi.nlm.nih.gov/articles/PMC12723528 | Throughput at 0.79% uncorrected WER; NOT per-correction seconds |
| Same study | Uncorrected word error rate | 0.79, SD 1.17 | % | https://pmc.ncbi.nlm.nih.gov/articles/PMC12723528 | Residual error after user corrections; NOT a latency |
| Same study | Decoder top-1 gesture / tap accuracy; synthetic flexible avg top-1/top-3 | 93.1 / 95.4; 88.0 / 95.0 | % | https://pmc.ncbi.nlm.nih.gov/articles/PMC12723528 | Decoder accuracy, NOT human correction time |
| Text-input latency study (Schmid et al., n=31, physical keyboard, copy+correct) | Injected system latencies tested | 20 (low) / 200 (high) | ms | https://epub.uni-regensburg.de/55007/1/text-input-latency.pdf | System-latency conditions: correction task significantly degraded at 200 ms, copy task not; NOT human per-correction seconds |
| Same study, citing Shneiderman / Ng | Acceptable end-to-end typing latency / touchscreen noticeability floor | 50–150 / below 20 noticeable | ms | https://epub.uni-regensburg.de/55007/1/text-input-latency.pdf | Perceptibility budget, NOT correction time |
| Phone "undo latency" / "tap-to-accept correction rate" / measured autocorrect-fix time | Human ms per LM-error fix | NOT FOUND | ms | — | No source consulted reports a measured human time to fix one autocorrect/LM error or its distribution |

Finding §3: the only sourced human-side per-check numbers are 0.45 s/suggestion-check and 0.50 s/inspection (both partly model parameters, not keyless-surface measurements); system-side per-word decode is 59 ms on-device / 246 ms web. Human "undo latency" and tap-to-accept correction rate: NOT FOUND.

## 4. VISUAL VERIFICATION: time to detect a wrong character in a stream

| setting | what was timed | value | unit | source URL | how it maps to our need |
|---|---|---|---|---|---|
| Skilled reading eye movements | Mean fixation duration | 200–250 | ms | https://en.wikipedia.org/wiki/Eye_movement_in_reading | Lower-bound dwell per verification fixation; one fixation ≈ 0.20–0.25 s of intake |
| Same | Fixation range | 100 to over 500 | ms | https://en.wikipedia.org/wiki/Eye_movement_in_reading | Distribution width for verification dwell; NOT a correction distribution |
| Same | Saccade duration; saccade length mean (range) | 20–40; 7–9 chars (1–20) | ms; characters | https://en.wikipedia.org/wiki/Eye_movement_in_reading | Step cost/size while scanning a stream for errors |
| Same | Mean eye-movement rate while reading | every ~0.25 (quarter of a second) | s | https://en.wikipedia.org/wiki/Eye_movement_in_reading | Caps verification sampling at ~4 fixations/s; how detection scales with stream speed: faster streams force fewer fixations per character |
| Chapman–Cook / Tinker reading test via WPM article | University undergrads: ~18 paragraphs × 30 words = 540 words in 1.75 min; roman 316.3 (SD 61.4), italic 294.5 (SD 72.4); lowercase 13.4% faster than all-caps | 316.3 / 294.5 | WPM | https://en.wikipedia.org/wiki/Words_per_minute | Error-spotting throughput task (tick the awkward/spoiling word per 30-word paragraph), NOT single-character proofreading latency |
| Huey reading rates via WPM article | Silent 355 / auditory 307 / aloud 213 | WPM (5.91 / 5.12 / 3.55 words/s) | https://en.wikipedia.org/wiki/Words_per_minute | Reading-speed context for verification load; NOT error-detection latency |
| Quantz via WPM article | Very slow 234 / very rapid 438 | WPM (3.9 / 7.3 words/s) | https://en.wikipedia.org/wiki/Words_per_minute | Historical range of reading speed; NOT error-detection latency |
| Simple proofreading latency per wrong character (detect-only, keyed to stream speed) | Measured ms per wrong character as a function of WPM | NOT FOUND | ms | — | No source consulted reports detection latency per wrong character or its scaling with stream speed |

Finding §4: visual intake lower bounds are sourced (0.20–0.25 s/fixation, ~4 fixations/s, 7–9 chars/saccade), but a measured "time to detect one wrong character in a stream" and its scaling with stream speed: NOT FOUND.

## Verdict: single best estimate for seconds-per-correction (fast typist, surface with no visible keys)

No source supports one.

- Per-correction seconds on a keyless surface: NOT FOUND in every setting above (steno re-strike/kata/edit; fast-typist detect-and-fix; phone LM-error undo; stream proofreading latency).
- The WPM standards found explicitly refuse to price a correction in seconds: Net = Gross − uncorrected-errors/min (https://www.speedtypingonline.com/typing-equations), with corrected-error cost left as unmeasured time already lost.
- KLM/GOMS, the only formal keystroke-timing standard consulted, models error-free experts only and prices a mental re-plan at M = 1.35 s without tying it to correction (https://en.wikipedia.org/wiki/Keystroke-level_model).
- Do NOT use as an estimate (listed only to prevent silent substitution): 0.45 s/suggestion-check (https://theconversation.com/do-you-use-predictive-text-chances-are-its-not-saving-you-time-and-could-even-be-slowing-you-down-170163), 0.50 s T9 inspection (http://www.yorku.ca/mack/chi00.html), 0.20–0.25 s reading fixation (https://en.wikipedia.org/wiki/Eye_movement_in_reading), 0.26 s/key press (https://theconversation.com/do-you-use-predictive-text-chances-are-its-not-saving-you-time-and-could-even-be-slowing-you-down-170163), 59 ms system decode (https://pmc.ncbi.nlm.nih.gov/articles/PMC12723528). None was measured as a human correction on a surface with no visible keys, and combining them would be guessing, which the brief forbids.
- What the speed model must therefore carry: an explicit free parameter for seconds-per-correction (with correction frequency from backspace/error rates: e.g. 0.161 backspace proportion https://pmc.ncbi.nlm.nih.gov/articles/PMC11558221; 12–20% error-inclusive mismatch https://pmc.ncbi.nlm.nih.gov/articles/PMC9356123/; 0.5–0.75 uncorrected errors/min at 39–49 GWPM https://digitalcommons.odu.edu/cgi/viewcontent.cgi?article=1352&context=ots_masters_projects), to be filled by a direct experiment, not by literature inference.

DONE
