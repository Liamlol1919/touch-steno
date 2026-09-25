# W16 — Layout optimisation methods for a noise-aware 8×2 gesture layout

Scope: Q1 layout optimisation algorithms + published optimised-vs-baseline gains; Q2 8-dir×2-band assignment under sensor noise;
Q3 confusion-matrix-driven layout; Q4 sector-type discriminability beyond marking menus.
Rule followed: every number below was seen in the cited source. Otherwise marked NOT FOUND. No inferred numbers.

## Q1. How keyboard / steno / gesture layouts are actually optimised + published optimised-vs-hand-designed results

### Q1a. Methods observed in sources

- Fitts law + digraph-frequency assignment (MacKenzie/Soukoreff/Zhang model): x-y key coords + Fitts MT + Hick-Hyman RT (novice 0.951 s, expert 0 s) + 27×27 digraph probabilities, WPM = (1/MT)×60/5.
  Source: https://www.yorku.ca/mack/BIT3.html
- OPTI/free optimisation (MacKenzie & Zhang 1999): place frequent letters centre, infrequent perimeter to minimise digraph-weighted movement.
  Source: https://www.yorku.ca/mack/mhci2013g.html (summarises MacKenzie & Zhang 1999)
- Metropolis / simulated annealing on Fitts-digraph energy (Zhai, Hunter & Smith 2000/2002: digraph springs, Metropolis keyboard, ATOMIK; Raynal & Vigouroux 2005 GA variant cited in later work).
  Sources: https://acm.org/pubs/articles/proceedings/uist/354401/p119-zhai/p119-zhai.pdf (via https://ixdf.org/literature/author/shumin-zhai listing); https://arxiv.org/pdf/2201.04593 (cites Zhai et al. 2000/2002 + Raynal & Vigouroux 2005)
- Carpalx triad model + simulated annealing: effort = kb·base + kp·penalty + ks·stroke over character triads; published weights kb=0.3555, kp=0.6423, ks=0.4268, k1/k2/k3 position decay; finger/row/hand penalties + stroke path.
  Sources: https://mk.bcgsc.ca/carpalx ; https://mk.bcgsc.ca/carpalx/?colemak= ; https://gitlab.com/lykt/carpalx/-/commit/91a19de1e631c41f60c5fd29b6ca7b6bdf6da5c0
- Genetic algorithm / quadratic assignment (Onsorodi & Korhan 2020; Light & Anderson 1993 SA; Walker 2003 GA; Yang & Mali SA; Dell'Amico et al. GA+SA for Arabic — as surveyed in PLOS ONE paper).
  Source: https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0226611
- Hill climbing / key-swap local search: reported as phase 3 "Pareto front expansion — swap two keys per layout, ~200 passes" in Smith et al. 2015 (same operator as Dunlop & Levine 2012).
  Source: https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/43271.pdf
- Multi-objective Pareto optimisation (Dunlop & Levine CHI 2012: speed + familiarity + spell-checking; Bi et al. CHI 2014 Pareto/Metropolis for correction vs completion; Smith et al. CHI 2015 clarity + speed + QWERTY-similarity).
  Sources: https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/43271.pdf ; https://dl.acm.org/doi/10.1145/2207676.2208659
- Constrained / quasi-optimisation (Bi, Smith & Zhai CHI 2010: each letter ≤1 slot from QWERTY; Bi & Zhai CHI 2016 IJQwerty: one-swap bound, swap I↔J).
  Sources: https://dl.acm.org/doi/10.1145/1753326.1753367 ; https://research.google/pubs/quasi-qwerty-soft-keyboard-optimization
- Gesture-clarity objective (Smith, Bi & Zhai CHI 2015): average minimum distance between word gestures in 40k lexicon ("nearest neighbour"); gesture speed via Cao & Zhai CLC model converted to WPM = 60000/G; QWERTY similarity = Manhattan distance of key positions.
  Source: https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/43271.pdf
- Hand-designed gesture alphabets (Goldberg & Richardson 1993 Unistrokes: frequent letters → straight lines, exploit direction, eyes-free, "sloppiness space"; Graffiti: resemble Roman letters).
  Sources: https://www.yorku.ca/mack/chi2008b.html (summarises Goldberg & Richardson 1993); design-only, no empirical test per https://oplclaw.com/paper/76070
- Steno method: fixed phonetic/chord layout in steno order `#STKPWHRAO*EUFRPBLGTSDZ`, left onset / centre vowel / right coda; one chord ≈ syllable/word.
  Sources: https://www.artofchording.com/layout/chorded-keyboard.html ; https://en.wikipedia.org/wiki/Stenotype

### Q1b. Published optimised-vs-baseline results (only numbers seen in source)

| system / method | optimisation | baseline | speed gain (as stated) | error gain (as stated) | source URL |
|---|---|---|---|---|---|
| OPTI soft keyboard (MacKenzie & Zhang CHI 1999) | Fitts+digraph free optimisation, frequent-centre | QWERTY soft | predicted upper bound 58.2 wpm, "about 35%" over QWERTY; empirical 17.0 wpm → 44.3 wpm by session 20 (5 users, 20×45-min sessions); surpassed QWERTY after session 10 (~4 h practice); power-law R²=0.997, bound at ~session 50 | NOT FOUND (no OPTI-vs-QWERTY error comparison in sources consulted) | https://oplclaw.com/paper/76434 ; context https://www.yorku.ca/mack/mhci2013g.html |
| QWERTY soft expert prediction (same model) | — (reference) | — | expert 43.2 wpm; novice 8.9 wpm | — | https://www.yorku.ca/mack/BIT3.html |
| Fitaly soft (model prediction only) | hand/commercial digraph optimisation, 2 space bars | QWERTY 43.2 wpm | expert 55.9 wpm; paper states "a full 24.8% higher than the 43.2 wpm expert prediction" (verbatim; arithmetic not recomputed here) | NOT FOUND | https://www.yorku.ca/mack/BIT3.html |
| JustType soft (model prediction only) | letter-grouping for disambiguation | QWERTY 43.2 wpm | expert 44.2 wpm, "just 2.3% faster than QWERTY" (verbatim) | NOT FOUND | https://www.yorku.ca/mack/BIT3.html |
| Dvorak-as-soft (model prediction only) | two-hand touch-typing optimum, reused as soft | QWERTY 43.2 wpm | expert 38.7 wpm (below QWERTY); novice 8.7 vs 8.9 wpm | NOT FOUND | https://www.yorku.ca/mack/BIT3.html |
| 6-layout quick/novice test, n=24, phrase "the quick brown fox jumped over the lazy dogs", paper facsimile + stopwatch | none (test of above) | QWERTY 20.2 wpm (SD 4.9) | ABC 10.6 (1.7); Dvorak 8.5 (2.0); Fitaly 8.2 (2.2); Telephone 8.1 (1.9); JustType 7.3 (1.5); mean 10.5 wpm; keyboard effect F(5,23)=184.3, p<.0001; QWERTY = 46.8% of predicted expert 43.2 wpm | NOT FOUND (error rates not recorded — stated verbatim) | https://www.yorku.ca/mack/BIT3.html |
| GK gesture keyboards (Smith, Bi & Zhai CHI 2015), 40k lexicon, simulated annealing + Pareto; 4×32-thread machines ~3 weeks | clarity = mean nearest-neighbour gesture distance; speed = CLC; similarity = Manhattan | QWERTY | clarity-only GK-C 0.543 vs QWERTY 0.391 key widths (+38.8% stated); speed-only GK-S +24.4% stated; joint GK-D +17.9% clarity and +13.0% speed stated; expert-level entry GK-D +12.5%, GK-T +6.0% over QWERTY stated | GK-D and GK-T "reduce error rates by 52% and 37% over Qwerty, respectively" (abstract verbatim); Fig.7 caption variant in same PDF: "GK-D's and GK-T's average error rate is 52% and 31% less than Qwerty's" (verbatim; discrepancy preserved, not resolved); 14-participant Nexus-5 gesture study, 22 words | https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/43271.pdf ; index https://research.google/pubs/optimizing-touchscreen-keyboards-for-gesture-typing |
| Quasi-QWERTY (Bi, Smith & Zhai CHI 2010), ≤1-slot move constraint | constrained Fitts+digraph | QWERTY + freely optimised | "about half the movement efficiency" of free optimisation via 1-step constraint (verbatim); novice tapping (n=12, 19 words, tablet): initial entry 2110 ms/word QWERTY vs 3234 quasi vs 4705 free | error 2.9% QWERTY vs 2.3% quasi vs 1.4% free | https://oplclaw.com/paper/77951 ; primary https://dl.acm.org/doi/10.1145/1753326.1753367 |
| Interlaced QWERTY iQwerty (Zhai & Kristensson CHI 2008) | row-shift QWERTY to cut shape collisions | QWERTY / ATOMIK / alphabetic | visual search on paper (n=12, 19 words): QWERTY 60.6 vs iQwerty 68.3 ("only marginally increasing … (12.7% longer)" verbatim); ATOMIK 83, alphabetic 80.5; difficulty QWERTY 1.9 vs alphabetic 4.1 vs ATOMIK 4.8 | identical word traces: QWERTY 135 vs iQwerty 14 ("more than an order of magnitude better" verbatim); ATOMIK 77, alphabetic 25 | https://oplclaw.com/paper/77353 |
| Octopus / T+ / Curve phone variants (Cuaresma & MacKenzie MHCI 2013), n=12, 4×9 within-subjects | layout variants (not SA/GA) | standard QWERTY soft | Octopus 54.7 vs QWERTY 54 wpm ("1.4% faster" verbatim); T+ 38.7 vs Curve 35.3 wpm ("about 9.6% faster" verbatim); grand mean 45.7 wpm; phrase effect F(8,64)=29.0, p<.0001; Octopus +187% first→last iteration; Octopus ahead by 4th phrase, 70 wpm at 9th phrase | NOT FOUND (no error-rate comparison in excerpt consulted) | https://www.yorku.ca/mack/mhci2013g.html |
| GA keyboard (Onsorodi & Korhan PLOS ONE 2020) | genetic algorithm on quadratic-assignment / finger-travel distance | QWERTY | "average of 6.04% improvement" in travelled distance over QWERTY across texts (verbatim; model distance, NOT user WPM) | NOT FOUND (no user speed/error test) | https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0226611 |
| Carpalx QGMLWB / Colemak / Dvorak (model effort, NOT user test) | simulated annealing on triad effort | QWERTY effort 3.000 (=1.0 base +1.0 penalty +1.0 path) | Colemak total 1.842; Dvorak 2.098 (+13.9% over Colemak); QWERTY +62.9% over Colemak; base QWERTY +190.7% over Colemak; "destroys QWERTY and improves effort over Colemak by 5%" for QGMLWB (verbatim); distance/penalty/stroke optimised to 0.38/0.57/0.72 vs QWERTY 1.0 | NOT FOUND (effort model only; no WPM/error experiment) | https://mk.bcgsc.ca/carpalx ; https://mk.bcgsc.ca/carpalx/?colemak= |
| Dvorak vs QWERTY physical, direct digraph measure (Lewis et al./Santa Fe 98-05-041E), n=8, 45–81 wpm | DSK hand-alternation/home-row | QWERTY | "4.0% superiority for the Dvorak keyboard" on high-frequency digraphs (verbatim) | NOT FOUND | https://www.santafe.edu/research/results/working-papers/the-standard-and-dvorak-keyboards-revisited-direct |
| Dvorak retraining GSA 1956 (Strong), 10+10 typists | DSK retraining | QWERTY supplementary training, equal time | short-term result favoured standard arrangement; widely cited as "no advantage once equal extra practice" (interpretation contested; long-term DSK suggestion noted in secondary review) | NOT FOUND (no clean error-gain number in sources consulted) | https://archive.org/details/AComparativeExperimentInSimplifiedKeyboardRetrainingAndStandardKeyboardSupplementaryTraining ; review https://doi.org/10.1007/bf03392452 |
| Navy 1944 / Tacoma / Chicago anecdotes (via 1988 review of Dvorak literature) | DSK | QWERTY | Navy: "24.2 vs 8.1 n.w.p.m." net speed, "83 vs 157.6 h" training (verbatim); Tacoma: "1/3 the [time]" (verbatim fragment); review estimates: Gentner & Norman 5–10%, Norman & Fisher 5%, Kinkead 2.6%, Yamada 15–20% timed copy / 25–50% production (all verbatim ranges from review); Navy study "run under Dvorak's own supervision, so not independent" (verbatim caveat from SSD Nodes summary) | NOT FOUND (no controlled error comparison) | https://doi.org/10.1007/bf03392452 ; caveat https://www.ssdnodes.com/learn/colemak-vs-dvorak-vs-qwerty |
| Unistrokes vs Graffiti longitudinal (Castellucci & MacKenzie CHI 2008), n=10, 20×15-phrase sessions, errors corrected so error rate 0% by design | hand-designed alphabets (frequent→straight strokes vs resemble-Roman) | each other (no QWERTY arm) | session-1→20: Graffiti 4.0 (SD 1.44) → 11.4 (3.60) wpm; Unistrokes 4.1 (2.18) → 15.8 (4.02) wpm; Technique main effect on entry speed NS: F(1,8)=2.05, p>.05; Session×Technique F(19,152)=2.26, p<.005; stroke duration Unistrokes faster: F(1,8)=8.21, p<.05 (means 284 vs 459 ms; ratio 0.620, cf. Cao & Zhai 0.618); prep time NS: F(1,8)=1.57, p>.05 | correction rate (backspaces/phrase length): Graffiti flat mean 26.2% (SD 2.6); Unistrokes 43.4% (16.4) → 16.3% (10.0) | https://www.yorku.ca/mack/chi2008b.html |
| Steno certification / throughput | fixed chord layout, syllable packing + briefs (NOT an optimisation experiment) | n/a | court-reporter thresholds: "approximately 180, 200, and 225 wpm" for literary/jury/testimony (verbatim); NOT a baseline-beating gain | NOT FOUND | https://en.wikipedia.org/wiki/Stenotype |
| Steno layout optimisation with measured speed/error vs baseline | — | — | NOT FOUND | NOT FOUND | — |

Notes on Q1:
- Light & Anderson 1993 (SA), Walker 2003 (GA), Yang & Mali (SA), Dell'Amico et al. (GA+SA Arabic), Iseri & Eksioglu (digraph costs), Karrenbauer & Oulasvirta (model) appear only as citations inside the PLOS ONE survey; no standalone speed/error numbers were verified — treat optimisation-family existence as established, gains as NOT FOUND beyond the rows above.
- Dunlop & Levine 2012 Pareto method is established (https://dl.acm.org/doi/10.1145/2207676.2208659) but no verified speed/error-vs-QWERTY number was found in consulted excerpts; secondary thesis excerpt claims "64% of Qwerty speed on first use … 85% within four sessions" without primary verification — NOT FOUND for this report.
- Bi & Zhai IJQwerty 2016 (one-swap I↔J): method + "reduces word error rate and improves input speed once expert; initial search similar to QWERTY" claimed in secondary summary (https://oplclaw.com/paper/80404); exact WPM/error percentages NOT FOUND in consulted excerpts.

## Q2. Assigning symbols to (direction, band) cells to maximise separability under sensor noise

- 8 directions × 2 magnitude bands with Fisher-discriminant / confusion-matrix-based cell assignment: NOT FOUND. No publication found that assigns an alphabet to 16 direction×magnitude cells by maximising discriminability given measured per-frame position/angular noise.
- Closest published analogue (same lab lineage, different problem): Smith et al. 2015 gesture-clarity objective = mean distance to nearest-neighbour word gesture over a 40k lexicon, optimised by simulated annealing + Pareto. This is separability-maximisation over key positions for whole-word traces, NOT over 16 discrete direction×band cells and NOT conditioned on measured sensor noise. Gains above (52%/37% error, +12.5%/+6.0% speed) belong to that problem.
  Source: https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/43271.pdf
- Closest confusion-counting analogue: SHARK2 sokgraph analysis on ATOMIK vs QWERTY, 20k lexicon — counts of identical-shape pairs: shape-only 1117 pairs; +scale 519; +end position 522; +start&end 493 (of which "284 pairs (58%) … are Roman numerals" verbatim). Used to motivate location channel, NOT to reassign symbols to cells.
  Source: http://pokristensson.com/pubs/KristenssonZhaiUIST2004.pdf
- Personalised Fitts-digraph optimisation (Metropolis) for single-input/AAC keyboards: personalised 7.86 vs optimised 7.29 wpm ("averaged 0.57 wpm greater" verbatim; computational efficiency p<0.001 ηp²=0.02; exposure 7.83 vs 7.32; block 8.11 vs 7.05). Optimises travel time, NOT noise-conditioned cell separability.
  Source: https://arxiv.org/pdf/2201.04593

## Q3. Layout designed FROM a measured confusion matrix

- Direct hit (most-confusable symbols → most-distinguishable cells or vice versa, with measured gain): NOT FOUND in consulted sources.
- What WAS found and is adjacent:
  - Gesture clarity (Smith et al. 2015) uses computed geometric confusability (nearest-neighbour distance), not a measured human/sensor confusion matrix. Gain numbers as in Q1b.
  - iQwerty (Zhai & Kristensson 2008) uses computed shape-collision counts (135→14 identical traces), not a measured confusion matrix. Gain numbers as in Q1b.
  - Dunlop & Levine (2012) include a spell-checking/tap-ambiguity objective in Pareto optimisation, but no measured-confusion-matrix assignment + user gain was verified — NOT FOUND.
  - Goldberg & Richardson Unistrokes "well distinguished in sloppiness space" is a design claim without a published confusion-matrix optimisation step or gain — NOT FOUND beyond the Graffiti-vs-Unistrokes longitudinal numbers in Q1b.
  - No Fisher-discriminant layout optimisation paper was found — NOT FOUND.

## Q4. Sector-type discriminability (axes vs diagonals vs near/far body) beyond the given marking-menu result

Established axis/diagonal effects (measured, with URLs):

| contrast | result (verbatim) | source URL |
|---|---|---|
| hierarchic marking, breadth-12, depths 2–4, on-axis-only (a1, e.g. "12-3-9-3") vs mixed (a2) vs off-axis-only (a3, e.g. "1-2-1-2"), n=12, pen+mouse | axis level significant on RT: F(2,22)=104.84, p<.001; on % errors: F(2,22)=36.2, p<.001; device×off-axis on RT: F(2,22)=6.93, p<.05 ("response time on worse off-axis targets did not degrade as badly with pen as with mouse" verbatim); design rule verbatim: "frequently used items could be placed at on-axis locations" | https://www.billbuxton.com/MMExpert.html |
| mark ≈3.5× faster than menu in real app (one user 0.2 s mark vs 0.7 s menu, menu pop 1/3 s subtracted; 15k selections/36 h → 1.25 h saved); pen 1.69 s vs mouse 2.07 s overall: F(1,11)=19.7, p<.001; errors mouse>pen: F(1,11)=6.41, p<.05; breadth×depth on error: F(6,66)=12.28, p<.001; ≤10% error up to breadth-8 depth-2 either device | same as above | https://www.billbuxton.com/MMExpert.html |
| single pen strokes (Cao & Zhai CHI 2007): line orientation | "diagonal line along wrist rotation direction was somewhat faster … but horizontal and vertical lines were more accurate" (verbatim); "right-handed users are faster at drawing straight lines in 45° and 225° orientations. However, diagonal directions were also found to be more error-prone" (verbatim); "Angles in middle of range (around 67.5°) were more error prone than more extreme angles. Neither start angle nor direction showed significant [effects]" (verbatim) | https://caoxiang.net/papers/chi2007_pengesture.pdf ; https://dl.acm.org/doi/pdf/10.1145/1240624.1240850 |
| same study: stroke length | length effects on % error E: F(5,45)=25.2, p<.001; on attempts A: F(5,45)=22.4, p<.001; "Both E and A decreased as length increased … harder to maintain same relative accuracy with smaller-sized gestures" (verbatim) | same as above |
| M3 touchscreen marking (Bi et al./Zhai mobile, finger, vs stylus literature): depth-1 {0.6 s, 0.35%}, depth-2 {0.7 s, 2.91%~3%}, depth-3 {1.0 s, 8.85%~9%} for 8/64/512 commands; vs Kurtenbach & Buxton orig. depth-2 {1.4 s, 7%} depth-3 {2.3 s, 17%}; vs Zhao & Balakrishnan orig. {2.3 s, 10%} {3.6 s, 17%}; vs multi-stroke {2.3 s, 4%} {3.4 s, 7%} | depth effect, NOT a sector-anisotropy result; included to bound depth confound | https://storage.googleapis.com/gweb-research2023-media/pubtools/4163.pdf |
| near-body vs far-from-body sector discriminability | NOT FOUND. No measured near/far-body anisotropy found in consulted sources. | — |
| 2-level magnitude-band discriminability (short vs long flick) | NOT FOUND. No measured short/long radial-magnitude confusion matrix found in consulted sources. | — |

## Most transferable methods to a noise-aware 8×2 gesture layout (ranked)

1. Multi-objective simulated annealing + Pareto front expansion on (a) nearest-neighbour gesture separability and (b) Fitts/CLC-digraph movement cost, with key-swap local search. Supporting number: GK-D −52% error and +12.5% expert speed over QWERTY (GK-T −37% / +6.0%) in a 14-user gesture study; clarity-only +38.8%, speed-only +24.4% bound the single objectives. Transfer: replace "key positions on grid" with "symbols assigned to 16 direction×band cells", replace Euclidean word-trace distance with Mahalanobis/Fisher distance using the given per-frame noise (p99 0.56 mm, max 1.48 mm → 1.6°/4.2° at 20 mm) and the mandatory-centre-return transition model; keep Pareto + swap-two-keys expansion (~200 passes) and the 40k-lexicon/frequency weighting. Source: https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/43271.pdf
2. Constrained (quasi-) optimisation bounding displacement from a familiar baseline + explicit novice visual-search costing (Hick-Hyman). Supporting number: ≤1-slot constraint keeps "about half" the free-optimisation movement gain while cutting novice search from 4705 ms/word (free) to 3234 ms/word (quasi) vs 2110 ms/word QWERTY (n=12); errors 1.4% free / 2.3% quasi / 2.9% QWERTY. Transfer: constrain alphabet→cell reassignment to preserve any already-learned compass mapping and jointly minimise Hick-Hyman search + Fitts return-to-centre cost, since centre-return is mandatory and un-centred chaining otherwise injects a constant 67.5° bias (given). Sources: https://dl.acm.org/doi/10.1145/1753326.1753367 ; https://oplclaw.com/paper/77951
3. On-axis priority rule from marking-menu + pen-stroke anisotropy. Supporting numbers: axis-level effect F(2,22)=104.84 (RT) and F(2,22)=36.2 (errors), both p<.001; pen degrades less than mouse off-axis, F(2,22)=6.93, p<.05; independent pen-gesture result: H/V more accurate, diagonals (45°/225°) faster but more error-prone, mid-angles ~67.5° worst. Transfer: assign highest-frequency / highest-cost-of-error symbols to on-axis cells first; avoid placing minimal pairs across the ~67.5° mid-angle boundary and across the 8-vs-16-sector decision boundary given 31–40% of real strokes fall within 10° of a boundary (given). Sources: https://www.billbuxton.com/MMExpert.html ; https://caoxiang.net/papers/chi2007_pengesture.pdf

## Explicit NOT FOUND list

- No published 8-direction × 2-band symbol-to-cell optimisation maximising separability under measured capacitive-pad noise (no Fisher-discriminant cell assignment paper found).
- No published layout built FROM a measured sensor/human confusion matrix with a before/after speed + error gain (nearest-neighbour "clarity" and collision counts are computed, not measured-matrix-driven).
- No measured near-body vs far-from-body sector discriminability; no measured short-vs-long radial magnitude-band confusion.
- No steno/chord layout optimisation with a controlled optimised-vs-baseline speed + error gain.
- No verified Dunlop-Levine-2012 or IJQwerty-2016 user speed/error percentages in consulted excerpts (method established, numbers NOT FOUND).

DONE
