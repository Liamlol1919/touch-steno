# W5 — Pointing / Motor-Control Limits for Thumb Direction Selection

Research question: can a thumb reliably select many discrete directions/zones on a touch surface (e.g. 8-way vs 16-way compass)?

Rule followed: every number below was seen in the cited source. Otherwise marked NOT FOUND. No guessing.

---

## 1. Fitts' law and pointing accuracy

### 1.1 Formulas (exact)

| Item | Formula / value | Source URL |
|---|---|---|
| Original Fitts ID | `ID = log2(2D / W)` bits | https://en.wikipedia.org/wiki/Fitts%27s_law |
| Shannon form (MacKenzie, ISO 9241) | `ID = log2(D / W + 1)` | https://en.wikipedia.org/wiki/Fitts%27s_law |
| Movement time | `MT = a + b·ID` (a = intercept/delay, b = slope, device-dependent by regression) | https://en.wikipedia.org/wiki/Fitts%27s_law |
| Effective width (Crossman 1956 / Fitts & Peterson 1964) | `We = 4.133 × SDx` where SDx = SD of selection x-coordinates along approach axis | https://en.wikipedia.org/wiki/Fitts%27s_law |
| Effective ID / throughput | `IDe = log2(D / We + 1)`; `IP (TP) = IDe / MT` — ISO 9241-9 recommended throughput | https://en.wikipedia.org/wiki/Fitts%27s_law |
| Meaning of We | We spans 96% of distribution if normal; if observed error = 4% then We = W; if error > 4% then We > W; if error < 4% then We < W | https://en.wikipedia.org/wiki/Fitts%27s_law |
| Throughput definition (MacKenzie 2018) | `TP = ID / MT`, units bits/s; thesis that TP is approximately independent of A/W | https://www.yorku.ca/mack/hhci2018.html |
| Welford 2-factor variant | `MT = a + b1·log2(D) + b2·log2(W)`; Shannon-inspired nested form compared by F-test | https://en.wikipedia.org/wiki/Fitts%27s_law |
| 2D W-models listed | status-quo (horizontal W), sum (H+W), area (H×W), smaller-of, W-model (effective width along movement direction) | https://en.wikipedia.org/wiki/Fitts%27s_law |

### 1.2 Concrete MT / W / TP values — Fitts (1954) 1-oz stylus serial tapping, re-reported by MacKenzie (2018), Table 17.1

Conditions: 4 amplitudes × 4 widths; each MT mean from >600 observations over 16 participants; ID range 1–7 bits; MT range 180–731 ms.

| A (in) | W (in) | We (in) | ER (%) | ID (bits) | MT (ms) | TP (bits/s) | Source URL |
|---|---|---|---|---|---|---|---|
| 2 | 0.25 | 0.243 | 3.35 | 4 | 392 | 10.20 | https://www.yorku.ca/mack/hhci2018.html |
| 2 | 0.50 | 0.444 | 1.99 | 3 | 281 | 10.68 | https://www.yorku.ca/mack/hhci2018.html |
| 2 | 1.00 | 0.725 | 0.44 | 2 | 212 | 9.43 | https://www.yorku.ca/mack/hhci2018.html |
| 2 | 2.00 | 1.020 | 0.00 | 1 | 180 | 5.56 | https://www.yorku.ca/mack/hhci2018.html |
| 4 | 0.25 | 0.244 | 3.41 | 5 | 484 | 10.33 | https://www.yorku.ca/mack/hhci2018.html |
| 4 | 0.50 | 0.468 | 2.72 | 4 | 372 | 10.75 | https://www.yorku.ca/mack/hhci2018.html |
| 4 | 1.00 | 0.812 | 1.09 | 3 | 260 | 11.54 | https://www.yorku.ca/mack/hhci2018.html |
| 4 | 2.00 | 1.233 | 0.08 | 2 | 203 | 9.85 | https://www.yorku.ca/mack/hhci2018.html |
| 8 | 0.25 | 0.235 | 2.78 | 6 | 580 | 10.34 | https://www.yorku.ca/mack/hhci2018.html |
| 8 | 0.50 | 0.446 | 2.05 | 5 | 469 | 10.66 | https://www.yorku.ca/mack/hhci2018.html |
| 8 | 1.00 | 0.914 | 2.38 | 4 | 357 | 11.20 | https://www.yorku.ca/mack/hhci2018.html |
| 8 | 2.00 | 1.576 | 0.87 | 3 | 279 | 10.75 | https://www.yorku.ca/mack/hhci2018.html |
| 16 | 0.25 | 0.247 | 3.65 | 7 | 731 | 9.58 | https://www.yorku.ca/mack/hhci2018.html |
| 16 | 0.50 | 0.468 | 2.73 | 6 | 595 | 10.08 | https://www.yorku.ca/mack/hhci2018.html |
| 16 | 1.00 | 0.832 | 1.30 | 5 | 481 | 10.40 | https://www.yorku.ca/mack/hhci2018.html |
| 16 | 2.00 | 1.519 | 0.65 | 4 | 388 | 10.31 | https://www.yorku.ca/mack/hhci2018.html |
| Mean | — | — | — | — | 391.5 | 10.10 | https://www.yorku.ca/mack/hhci2018.html |
| SD | — | — | — | — | 157.3 (40.2% of mean) | 1.33 (13.2% of mean) | https://www.yorku.ca/mack/hhci2018.html |

Additional fits reported on same page:

| Item | Value | Source URL |
|---|---|---|
| MT–ID regression fit | 96.6% of variance explained by model | https://www.yorku.ca/mack/hhci2018.html |
| Task difficulties | 1 bit to 7 bits across conditions | https://www.yorku.ca/mack/hhci2018.html |

### 1.3 Pointing error sigma vs target size/distance; small-target MT/W on touch

| Claim | Status |
|---|---|
| sigma_a (endpoint SD in mm or degrees) scaling law with D and W | NOT FOUND — sources give We=4.133·SDx adjustment and TP constancy, not a sigma_a(D,W) equation in mm/deg. |
| Touch-specific small-target MT/W table (e.g. 5 mm vs 10 mm on phone) | NOT FOUND as Fitts MT table. Closest touch numbers are button-size error studies in §1.4. |

### 1.4 Touch target-size error numbers (standing vs walking)

Conradi et al. 2015, touch buttons on mobile (small 5×5 mm and other sizes):

| Finding | Source URL |
|---|---|
| Time-on-task: highly significant difference between small button (5×5 mm) and all other button sizes (p < 0.01) | https://doi.org/10.1016/j.promfg.2015.07.182 |
| Walking had highly significant influence for button sizes 5×5 mm and 8×8 mm (p < 0.01) | https://doi.org/10.1016/j.promfg.2015.07.182 |
| Error count: influence of button size (5×5 mm) vs other sizes (p < 0.01); highly significant influence of walking (p < 0.01) | https://doi.org/10.1016/j.promfg.2015.07.182 |
| Even in bigger buttons error count increased significantly while walking (p = 0.041) | https://doi.org/10.1016/j.promfg.2015.07.182 |
| Authors: 8×8 mm applicable while standing but still triggers high errors; only 14×14 mm showed low error rates while walking and standing | https://doi.org/10.1016/j.promfg.2015.07.182 |

Hand-size correlate:

| Finding | Source URL |
|---|---|
| 11 hand features tested; thumb length correlates significantly with touch accuracy and accounts for about 12% of touch error variance | https://doi.org/10.1145/3338286.3340115 |

---

## 2. Psychophysics of 2D directional pointing (4 / 8 / 16 / 24 directions)

No source found giving a full accuracy-vs-N curve (4→8→16→24) or a confusion matrix for thumb-on-touchsurface directional flicks. Best available proxies are radial / marking-menu breadth studies.

### 2.1 What was actually measured

| Finding | Numbers | Source URL |
|---|---|---|
| Breadths × depths tested (hierarchic marking menus) | Breadths 4, 8, 12 crossed with depths 1–4, plus mixed-breadth config; both pen and mouse | https://www.research.autodesk.com/app/uploads/2023/03/the-limits-of-expert.pdf_recyw5wL6ekPqcE4Q.pdf |
| Error < 10% bound | For either device (mouse or pen), error rates below 10% for up to breadth 8 and depth 2 | https://www.research.autodesk.com/app/uploads/2023/03/the-limits-of-expert.pdf_recyw5wL6ekPqcE4Q.pdf |
| Device effect on errors | Subjects produced significantly more errors with mouse than pen, F(1,11)=6.41, p < .05 | https://www.research.autodesk.com/app/uploads/2023/03/the-limits-of-expert.pdf_recyw5wL6ekPqcE4Q.pdf |
| Mouse vs pen divergence | Mouse and pen error percentages began to differ once breadth reached 8 items | https://www.research.autodesk.com/app/uploads/2023/03/the-limits-of-expert.pdf_recyw5wL6ekPqcE4Q.pdf |
| Response-time effect | Breadth and depth affected response time; reported F(2,22)=104.84, p < .001 for time | https://www.research.autodesk.com/app/uploads/2023/03/the-limits-of-expert.pdf_recyw5wL6ekPqcE4Q.pdf |
| Breadth–depth tradeoff to stay under 10% error (Zhao & Balakrishnan 2004, simple-mark technique) | Breadth 4 per level → at most 4 levels deep; breadth 8 per level → at most 2 levels | https://synteraction.org/assets/files/Zhao%20and%20Balakrishnan%20-%202004%20-%20Simple%20vs.%20compound%20mark%20hierarchical%20marking%20menu.pdf |
| Flower menus review statement | Performance degrades as menu size increases; 12 items seems maximum to ensure acceptable error rate | https://hal.sorbonne-universite.fr/hal-01894182v1/document |
| Marking vs menu speed (real-work case study) | Using a mark on average 3.5× faster than selection using the menu | https://doi.org/10.1145/191666.191759 |
| M3 gesture menu vs traditional marking menus | M3 faster and less error-prone by factor of two (expert performance experiment) | https://doi.org/10.1145/3173574.3173823 |
| M3 learning | Users transitioned to recall-based execution of a dozen commands after three 10-minute practice sessions | https://doi.org/10.1145/3173574.3173823 |
| Directional (angular) Fitts effect, pie-menu motivation (Boritz et al. 1991) | Right-handed subjects showed variations in Fitts parameters with target angle; left-handed showed no effect; high correlation of data with standard Fitts (size+distance only) | https://graphicsinterface.org/wp-content/uploads/gi1991-28.pdf |
| Handedness asymmetry paraphrase | For right-handed users selecting left-most item significantly harder than right-most; no upper↔lower difference (citing Boritz et al. 1991) | https://en.wikipedia.org/wiki/Fitts%27s_law |

### 2.2 Explicitly NOT FOUND

| Item | Status |
|---|---|
| Accuracy for 4 vs 8 vs 16 vs 24 discrete thumb directions (same device/task) | NOT FOUND |
| Confusion matrix (e.g. diagonal vs orthogonal errors) for directional flicks | NOT FOUND |
| Accuracy-vs-number-of-directions curve with % correct at 8 / 16 | NOT FOUND |
| Proprioception / wrist-vs-finger pointing angular error in degrees | NOT FOUND |
| Non-visual directional pointing numbers for thumb compass | NOT FOUND |

Note: orthogonal-vs-diagonal advantage (Pantes et al. 2009) appeared only as a citing sentence in a search snippet, without extractable numbers — treated as NOT FOUND for numbers.

---

## 3. Multi-finger rhythmic movement limits

### 3.1 Hager-Ross & Schieber (2000) — independence at self-paced ~2 Hz vs paced 3 Hz

Paper: “Quantifying the Independence of Human Finger Movements: Comparisons of Digits, Hands, and Movement Frequencies,” J. Neurosci. 20(22):8542. DOI URL: https://doi.org/10.1523/jneurosci.20-22-08542.2000

| Finding (abstract, exact) | Source URL |
|---|---|
| 10 right-handed subjects; motion of all five digits recorded with video + instrumented glove; one finger moved at a time | https://doi.org/10.1523/jneurosci.20-22-08542.2000 |
| Compared (1) digits, (2) right vs left hand, (3) self-paced vs externally paced 3 Hz | https://doi.org/10.1523/jneurosci.20-22-08542.2000 |
| Thumb, index, little typically more highly individuated than middle or ring fingers | https://doi.org/10.1523/jneurosci.20-22-08542.2000 |
| Dominant-hand fingers NOT more independent than nondominant | https://doi.org/10.1523/jneurosci.20-22-08542.2000 |
| Self-paced movements at ~2 Hz more highly individuated than externally paced 3 Hz movements | https://doi.org/10.1523/jneurosci.20-22-08542.2000 |
| Angular motion greatest at middle joint; increased proximal/distal joint motion during 3 Hz movements | https://doi.org/10.1523/jneurosci.20-22-08542.2000 |

| Item | Status |
|---|---|
| % independence penalty at 3 Hz / error-rate numbers per finger | NOT FOUND (paper reports rank-order/qualitative “more individuated,” no % table extracted) |
| Maximum sustainable oscillation Hz per finger (index vs ring etc.) | NOT FOUND in this paper |

Corroborating citation that enslaving exists:

| Finding | Source URL |
|---|---|
| Cannot move a single digit without changing others’ positions (citing Hager-Ross & Schieber 2000; Li et al. 2004; Schieber & Santello 2004) | https://pmc.ncbi.nlm.nih.gov/articles/PMC2637388/ |

### 3.2 Maximum voluntary tapping frequency (single index finger, auditory-cued flexion)

Study: 9 right-handed healthy subjects, age 27.4 ± 4.8 yr; 24-channel NIRS; conditions 25% ME / 50% ME / maximal effort (ME).

| Condition | Tapping frequency (mean ± SD) | Source URL |
|---|---|---|
| 25% of maximal effort | 1.61 ± 0.18 Hz | https://doi.org/10.2114/jpa.23.105 |
| 50% of maximal effort | 3.23 ± 0.36 Hz | https://doi.org/10.2114/jpa.23.105 |
| Maximal effort (ME) | 6.46 ± 0.72 Hz | https://doi.org/10.2114/jpa.23.105 |
| Cortical correlate | [tHb] ME-vs-rest 1.19 ± 0.93 mmol·mm, significantly higher than 25% ME (0.04 ± 0.04) or 50% ME (0.08 ± 0.11), p < 0.05; ~29.8-fold [tHb] increase 50% ME→ME vs ~2-fold 25%→50% | https://doi.org/10.2114/jpa.23.105 |

| Item | Status |
|---|---|
| Sustained multi-finger alternating-tap max Hz with error rates | NOT FOUND |
| Per-finger max Hz table (index/middle/ring/little) with numbers | NOT FOUND (Aoki-Uchino 2010 compares young vs elderly tapping but abstract gives no Hz numbers; treated as NOT FOUND) |

Practical reading (not a new number): the only hard Hz anchors found are ~2 Hz comfortable self-paced individuated movement, degradation at paced 3 Hz, and ~6.5 Hz single-finger maximal burst. Nothing found supports sustained independent multi-finger rhythm above ~3 Hz without individuation loss.

---

## 4. Motor learning: time/trials to plateau; chorded/gesture speeds

### 4.1 Twiddler one-handed chording (Lyons et al. / Clarkson et al.)

| Finding | Source URL |
|---|---|
| After 400 min practice, 10 novices averaged over 26 wpm, outperforming multitap baseline | https://doi.org/10.1109/iswc.2004.19 |
| 5 participants continued; average 47 wpm after ~25 hr practice in varying conditions | https://doi.org/10.1109/iswc.2004.19 |
| One subject 67 wpm, equivalent to last author (10-year Twiddler user) | https://doi.org/10.1109/iswc.2004.19 |
| Same numbers confirmed in journal version (10 participants, 20 sessions × 20 min multitap + 20 min chording per session) | https://doi.org/10.1207/s15327051hci2104_1 |
| Crossover: initially faster with multitap; difference negligible after 4 sessions; faster with chording by 8th session | https://doi.org/10.1207/s15327051hci2104_1 |
| Full PDF wording: “by the end of the study (20 sessions, 400 minutes)”; “participants reached an average rate of 47 wpm”; fastest 67 wpm | https://faculty.cc.gatech.edu/~thad/p/030_10_MTE/twiddler-iswc.pdf |
| Experienced Twiddler user averages 60 wpm letter-by-letter (cited in background) | Search snippet for https://dl.acm.org/doi/pdf/10.1145/985692.985777 (number seen in snippet; full PDF not re-fetched) |
| Multicharacter chords (MCCs) reported as potential speedup; forum anecdote ~17% (45→53 wpm) is NOT a peer-reviewed number — excluded from table | — |

### 4.2 8pen / other gesture sets

| Item | Status |
|---|---|
| 8pen WPM after N hours / learning curve with numbers | NOT FOUND (OpenAlex search “8pen gesture keyboard” returned no 8pen paper with extractable WPM; web search unavailable at fetch time) |
| General gesture/keyboard alternative anchor (MIME longitudinal study, for calibration only) | 17 wpm MIME vs 23 wpm QWERTY in-study; projected MIME overtake after 12 h practice; total error 1.7% vs 5.2% — dissertation record without DOI (https://api.openalex.org record, 2014 thesis “Optimizing Human Performance in Mobile Text Entry”). Weak anchor; not a gesture-compass number. |
| Marking-menu learning anchor | Dozen commands to recall-based execution after three 10-min sessions — https://doi.org/10.1145/3173574.3173823 |
| Trials-to-plateau universal number for “novel discrete gesture set” | NOT FOUND |

### 4.3 Summary learning table (only peer-reviewed numbers)

| Device / method | N / dose | Speed | Source URL |
|---|---|---|---|
| Twiddler chording, novices | 10 users, 400 min (20 sessions) | >26 wpm mean, beats multitap | https://doi.org/10.1109/iswc.2004.19 |
| Twiddler chording, extended | 5 users, ~25 h | 47 wpm mean | https://doi.org/10.1109/iswc.2004.19 |
| Twiddler chording, max observed | 1 user at study end; 1 author with 10 yr use | 67 wpm | https://doi.org/10.1109/iswc.2004.19 |
| Twiddler crossover | 10 users, 20 sessions | multitap faster → tie at session 4 → chording faster at session 8 | https://doi.org/10.1207/s15327051hci2104_1 |
| Marking-menu recall | M3, lab | 12 commands after 3×10 min sessions | https://doi.org/10.1145/3173574.3173823 |
| Marking speed advantage | field case study | mark 3.5× faster than menu selection | https://doi.org/10.1145/191666.191759 |

---

## 5. What this means for an 8-way vs 16-way thumb compass

Definitions: 8-way = 45° sectors; 16-way = 22.5° sectors.

- **8 is the defensible upper bound; 16 is not, on current evidence.**
- Why 8: the only controlled direction-count data found holds error **below 10% up to breadth 8** (depth ≤ 2), on both mouse and pen — https://www.research.autodesk.com/app/uploads/2023/03/the-limits-of-expert.pdf_recyw5wL6ekPqcE4Q.pdf — and explicitly caps breadth-8 hierarchies at **2 levels** to stay under 10% (breadth-4 allows 4 levels) — https://synteraction.org/assets/files/Zhao%20and%20Balakrishnan%20-%202004%20-%20Simple%20vs.%20compound%20mark%20hierarchical%20marking%20menu.pdf . A single-level 8-way compass is therefore the largest breadth with a <10% published anchor. The review gloss “12 items maximum for acceptable error” — https://hal.sorbonne-universite.fr/hal-01894182v1/document — is a ceiling, not a recommendation, and mouse/pen errors already diverge at 8 — same Kurtenbach PDF.
- Why not 16: no source found reporting acceptable error at 16 directions on a touch surface; 16-way halves the angular tolerance to ±11.25° (vs ±22.5° for 8-way), and the Fitts effective-width logic (We=4.133·SDx; 4% error ⇔ We=W — https://en.wikipedia.org/wiki/Fitts%27s_law ) implies any increase in endpoint spread directly inflates We and IDe/MT cost. Touch data show even **8×8 mm** buttons still yield high errors standing, with only **14×14 mm** low-error in both standing and walking — https://doi.org/10.1016/j.promfg.2015.07.182 — and thumb length alone explains ~12% of touch-error variance — https://doi.org/10.1145/3338286.3340115 . A 16-zone thumb compass on a small surface forces zones far narrower than these mm anchors.
- Rhythm constraint reinforces conservatism: individuated control is comfortable near **~2 Hz** and degrades at paced **3 Hz** — https://doi.org/10.1523/jneurosci.20-22-08542.2000 — while ~6.46±0.72 Hz is a single-finger maximal burst, not sustained independent multi-finger rhythm — https://doi.org/10.2114/jpa.23.105 . A design requiring fast sequential distinct thumb directions should therefore assume ≤2–3 Hz sustainable rate, which penalizes error-correction-heavy 16-way schemes more.
- Learning-cost constraint: reaching 47 wpm on a chorded discrete set took **~25 h**, with crossover only at session 8 and 26 wpm at 400 min — https://doi.org/10.1109/iswc.2004.19 / https://doi.org/10.1207/s15327051hci2104_1 . A 16-way set (4 bits/stroke vs 3 bits/stroke for 8-way) demands finer angular memory with no published learning curve found (8pen: NOT FOUND). The cheap learning win that *is* published is ~12 recallable gestures after 3×10 min — https://doi.org/10.1145/3173574.3173823 — closer to 8 than 16.
- Handedness/asymmetry caution: right-handers show angle-dependent Fitts parameters (left-handers do not) — https://graphicsinterface.org/wp-content/uploads/gi1991-28.pdf — with left-most selections harder than right-most — https://en.wikipedia.org/wiki/Fitts%27s_law . A compass should therefore not assume uniform 22.5° performance; at 16-way the “hard” diagonals/edges have no error budget left.

**Recommendation:** ship **8-way** as the reliable discrete thumb vocabulary; treat 12 as an absolute research ceiling and **16-way as experimental** until a confusion-matrix study shows <10% error at 22.5° spacing on the target surface. If more than 8 codes are needed, add a second shallow layer (depth 2) or a chord/modifier rather than splitting angles — consistent with the breadth-8/depth-2 <10% envelope above.

---

### Source list (all URLs cited)

- https://en.wikipedia.org/wiki/Fitts%27s_law
- https://www.yorku.ca/mack/hhci2018.html
- https://doi.org/10.1523/jneurosci.20-22-08542.2000
- https://pmc.ncbi.nlm.nih.gov/articles/PMC2637388/
- https://doi.org/10.2114/jpa.23.105
- https://www.research.autodesk.com/app/uploads/2023/03/the-limits-of-expert.pdf_recyw5wL6ekPqcE4Q.pdf
- https://doi.org/10.1145/169059.169426
- https://synteraction.org/assets/files/Zhao%20and%20Balakrishnan%20-%202004%20-%20Simple%20vs.%20compound%20mark%20hierarchical%20marking%20menu.pdf
- https://hal.sorbonne-universite.fr/hal-01894182v1/document
- https://graphicsinterface.org/wp-content/uploads/gi1991-28.pdf
- https://doi.org/10.1145/191666.191759
- https://doi.org/10.1145/3173574.3173823
- https://doi.org/10.1109/iswc.2004.19
- https://doi.org/10.1207/s15327051hci2104_1
- https://faculty.cc.gatech.edu/~thad/p/030_10_MTE/twiddler-iswc.pdf
- https://doi.org/10.1016/j.promfg.2015.07.182
- https://doi.org/10.1145/3338286.3340115
