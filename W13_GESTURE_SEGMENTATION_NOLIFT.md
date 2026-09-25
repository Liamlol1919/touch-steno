# W13 — Gesture segmentation WITHOUT lift-off (0-force capacitive pad)

Method note: websearch API returned HTTP 401, HAL (hal.science) and ACM DL blocked
automated fetch (Anubis bot-wall / 403). Numbers below come ONLY from sources
actually fetched and read: open PDFs via arXiv + faculty.washington.edu
($1, EdgeWrite, Debard CNN touch, spotting ANN, Neverova), prior-worker PDFs in
/tmp/workers/pdf (Kurtenbach, Zhao), and OpenAlex/Crossref API abstracts.
Everything else is marked NOT FOUND. No guesses.

Established context (not re-litigated): 91 Hz pad, ephemeral tracking IDs,
88 ms / 8-frame persistence window (zero false activations on 17 resting
contacts; same window needed between gestures), ~3 Hz reliable event rate at
250 ms gestures, collapse at 4–5 Hz, ~5.5 events/s theory. Neighbour coupling
parallel r² 0.62–0.92 (regressible); thumb–thumb mirrored r² 0.10–0.25 (not).

## 1. Systems that segment repeated gestures with no lift-off

| system | segmentation mechanism | gesture duration | accuracy/error | source URL |
|---|---|---|---|---|
| Lee & Kim 1999 threshold-HMM | threshold model = weak model of all trained gestures; likelihood is adaptive threshold confirming provisional match; states merged by relative entropy | NOT FOUND (durations not in abstract) | 93.14% reliability extracting trained gestures from continuous hand motion | https://doi.org/10.1109/34.799904 |
| Quikwriting / Cirrin / Edge Keyboards (via Wobbrock EdgeWrite 2003 related work) | NO lift between characters; segmentation by exiting one screen region and entering another (region-crossing) | NOT FOUND (no timing in this source) | NOT FOUND (no accuracy in this source) | https://faculty.washington.edu/wobbrock/pubs/uist-03.pdf |
| SHARK2 (Kristensson & Zhai 2004) | shorthand gesture on stylus keyboard, tracing → recall; multi-channel recognition incl. language model (dictionary disambiguation channel, i.e. segmentation by recognition, not by lift) | NOT FOUND | vocab 10,000–20,000 words supported (accuracy NOT FOUND in abstract) | https://doi.org/10.1145/1029632.1029640 |
| Continuous EdgeWrite (proposed, Wobbrock et al. 2003) | dictionary-based disambiguation INSTEAD of explicit user segmentation (stated design goal for the continuous version) | NOT FOUND (unbuilt at publication) | NOT FOUND | https://faculty.washington.edu/wobbrock/pubs/uist-03.pdf |
| Zhao & Balakrishnan 2004 simple-mark menus | TIMEOUT grouping of successive marks: marks within threshold = one multi-level selection; pause longer = new selection; abort by timeout or abort gesture (circle/pigtail) | inter-mark mean 0.481 s, SD 0.377 s, median 0.375 s; 95% < 1.156 s, 99% < 1.875 s; recommended grouping threshold 1–2 s; drawing 1.79 s simple / 1.97 s compound; total 2.92 s / 3.09 s | significant main effect technique on total time F1,11=5.11 p<0.05, on drawing F1,11=17.73 p<.0001 | https://doi.org/10.1145/1029632.1029639 |
| Neverova et al. 2016 (vision/depth, NOT touch) | quantity-of-movement (QOM) segmentation of depth stream → Improved Depth Motion Map → ConvNet | NOT FOUND (window-size problem explicitly discussed: durations vary) | Mean Jaccard Index 0.2655, 3rd place ChaLearn LAP 2016 | https://arxiv.org/abs/1608.06338 |
| Hernandez et al. 2013 real-time spotting (data glove, NOT touch) | 2 ANNs in series (communicative vs non-communicative); segmentation = find begin/end in continuous data; CyberGlove II 22 sensors + 2-state button used in segmentation | NOT FOUND (durations not extracted) | >99% (10 gestures), >96% (30 gestures) | https://arxiv.org/abs/1309.2084 |
| Motion Correlation (Velloso et al., TOCHI 2017) | user mimics a presented motion; selection by correlation of system output with user input; review of 5 prior gaze/gesture works + algorithm guidelines | NOT FOUND | NOT FOUND (review/guidelines, no single number in abstract) | https://doi.org/10.1145/3064937 |
| Debard et al. 2018 touch CNN (IMU-free touch) | NONE for streams: isolated-gesture classifier; authors state "next challenge … is the segmentation of a data flux in order to recognize multiple gestures at once" | 104 samples ≡ 1200 ms fits 95% of multi-touch gestures | 89.96% CNN on 6591-gesture/27-user multi-touch set (73.00% no sampling, 80.95% uniform); 99.38% user-independent on MMG (9600 gestures, 20 users, 16 classes) vs 98.0% SOTA; 1.5 ms GPU / 5 ms CPU per gesture | https://arxiv.org/abs/1802.09901 |

No published system found that segments REPEATED gestures on a 0-force
capacitive touch surface with no lift and reports a segmentation error rate.
Closest verified mechanisms: threshold-model confirmation (93.14%,
https://doi.org/10.1109/34.799904), region-crossing (no numbers,
https://faculty.washington.edu/wobbrock/pubs/uist-03.pdf), timeout grouping
with 1–2 s threshold (numbers above, https://doi.org/10.1145/1029632.1029639).

## 2. Out-and-back / bidirectional / return-to-centre families

| system | segmentation mechanism | gesture duration | accuracy/error | source URL |
|---|---|---|---|---|
| Hierarchic marking menus, compound zig-zag (Kurtenbach & Buxton) | direction reversals INSIDE one pen-down stroke encode hierarchy levels; novice fallback: dwell ~1/3 s pops radial menu; lift selects | 0.2 s mark selection vs 0.7 s menu selection (one user); menu display ~0.15 s; pen 1.69 s vs mouse 2.07 s avg response | error rises with breadth×depth; breadth-4 → max 4 levels, breadth-8 → max 2 levels at <10% error (via Zhao citing Kurtenbach) | https://doi.org/10.1145/169059.169426 |
| Simple-mark multi-mark (Zhao & Balakrishnan 2004) | each level = separate inflection-free mark (lifts ALLOWED); grouping by 1–2 s timeout (see Table 1) | see Table 1 | see Table 1 | https://doi.org/10.1145/1029632.1029639 |
| OctoPocus (Bau & Mackay 2008) | dynamic feedforward+feedback GUIDE for single-stroke gestures (not a segmenter); adaptable to mark sets | NOT FOUND | "significantly faster", improves learning vs Help menus; mark-set adaptation beats 2-level 4-item HM menu on input time (no absolute numbers in abstract) | https://doi.org/10.1145/1449715.1449724 |
| CycloStar / clutch-free panning (Malacria et al., CHI 2010) | continuous elliptical/circling motion for clutch-free pan + integrated pan-zoom (periodic motion, no lift) | NOT FOUND (full text bot-walled) | NOT FOUND | https://doi.org/10.1145/1753326.1753724 |
| "8-direction gestures with return to centre" | NOT FOUND as a named evaluated system | NOT FOUND | NOT FOUND | NOT FOUND |
| "Gesture chimps" | NOT FOUND | NOT FOUND | NOT FOUND | NOT FOUND |
| Finger circling / circumduction / figure-8 as evaluated no-lift segmenters | NOT FOUND (circling appears only as CycloStar pan control, no segmentation numbers) | NOT FOUND | NOT FOUND | NOT FOUND |
| Bimanual rhythmic patterns with reported timing | NOT FOUND | NOT FOUND | NOT FOUND | NOT FOUND |

## 3. Rhythmic / periodic (cycle/phase) decoding

| system | segmentation mechanism | gesture duration | accuracy/error | source URL |
|---|---|---|---|---|
| Rhythmic Interaction (Ghomi et al., CHI 2012) | tap rhythms as input; 2 experiments: (i) novices reproduce patterns, algorithms recognize; (ii) rhythms memorized as efficiently as shortcuts | NOT FOUND (full text bot-walled; abstract has no numbers) | NOT FOUND (abstract: "efficiently reproduced/recognized", "as efficiently as traditional shortcuts" — no numbers) | https://doi.org/10.1145/2207676.2208579 |
| Beats — beating gestures, smartwatch (Perrault et al., CHI 2015) | pairs of simultaneous OR rapidly sequential/overlapping taps, index+middle finger, distinguished by temporal sequence + left/right position; designed to not interfere with single-touch | mean 355 ms per beating gesture | 5.5% error; thresholds: simultaneous <30 ms, sequential <400 ms; screens ~40 mm square | https://doi.org/10.1145/2702123.2702226 |
| Cycle/phase decoding of a continuous sliding gesture (e.g. per-cycle class of circling) | NOT FOUND | NOT FOUND | NOT FOUND | NOT FOUND |

## 4. Minimum touch-gesture durations from IMU-free touch systems

| system | number | source URL |
|---|---|---|
| Beats (touch, smartwatch) | 355 ms mean execution; <30 ms = simultaneous, <400 ms = sequential pair threshold | https://doi.org/10.1145/2702123.2702226 |
| Debard multi-touch CNN (touch) | 1200 ms covers 95% of gestures (104-pt cap); longer = held too long or noisy | https://arxiv.org/abs/1802.09901 |
| $1 recognizer (pen, isolated unistrokes) | fast gestures ~600 ms; medium speed (balanced) recognized best across all 3 recognizers; N=64 resample; 97% (1 template) / 99% (3+) / 99+% overall | https://doi.org/10.1145/1294211.1294238 and https://faculty.washington.edu/wobbrock/pubs/uist-07.01.pdf |
| Marking menus (pen) | 0.2 s expert mark vs 0.7 s menu; ~1/3 s dwell pops menu; 1.69 s pen vs 2.07 s mouse response | https://doi.org/10.1145/169059.169426 |
| Simple-mark grouping (pen) | median 0.375 s between marks; group marks within 1–2 s, else new selection | https://doi.org/10.1145/1029632.1029639 |
| Stroke shortcuts (Appert & Zhai 2009) | equal performance to keyboard shortcuts with practice; better recall, fewer errors (numbers NOT FOUND — full text walled) | https://doi.org/10.1145/1518701.1519052 |

## Ranking for the 91 Hz no-lift pad

1. Dwell/velocity-minimum + timeout grouping. Only mechanism with
   touch-adjacent numbers on BOTH sides of the 88 ms window: Beats
   <30 ms simultaneous / <400 ms sequential split with 5.5% error at
   355 ms mean (https://doi.org/10.1145/2702123.2702226), Zhao 1–2 s
   mark-grouping threshold from median 0.375 s / 95% <1.156 s
   (https://doi.org/10.1145/1029632.1029639), Kurtenbach ~1/3 s menu
   dwell (https://doi.org/10.1145/169059.169426). Fits the measured
   88 ms persistence floor and 250 ms / ~3 Hz gesture budget directly.
2. Out-and-back with return-to-rest (direction-reversal) encoding.
   Compound zig-zag marks encode levels inside one stroke at 0.2 s per
   mark (https://doi.org/10.1145/169059.169426); EdgeWrite shows
   corner-order (not path) recognition beating Graffiti by 18%
   (https://faculty.washington.edu/wobbrock/pubs/uist-03.pdf).
   Reversal minima are detectable at 91 Hz without any lift signal,
   and the return leg gives a free segmentation landmark.
3. Threshold-model / correlation confirmation. Lee & Kim 93.14%
   extraction from continuous motion
   (https://doi.org/10.1109/34.799904); motion-correlation principle
   for mimicry selection (https://doi.org/10.1145/3064937). Costs a
   trained model per gesture and (per Debard) stream segmentation is
   still open even at 99.38% isolated accuracy
   (https://arxiv.org/abs/1802.09901). Avoid bimanual mirrored
   designs: thumb–thumb coupling r² 0.10–0.25 is not regressible.

DONE
