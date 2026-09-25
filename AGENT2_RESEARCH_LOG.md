# Agent 2 research log (laptop)

Tick-based log. Each entry: what was measured/decided, what was pushed, what is next.

## 05:21–05:29 — bootstrap + hardware evidence
- Cloned `touch-steno` (agent 1 already had 4 deliverables + synthetic baseline + tests).
- Uploaded `SYSTEMKOMPENDIUM.md` (user's own design compendium, 1017 lines).
- Built `scripts/kinematics.py` (port of commindv2 recorder/analyzer) and
  `scripts/real_session_evidence.py`; ran them on 3 real PTH-660 sessions.
- Pushed `MEASURED_BIOMECHANICS.md`: 91 Hz timing, rest noise floor (step p99 0.56 mm,
  speed p99 57 mm/s, drift 11.5 mm/20 s), persistence separation (v=40-60 mm/s, k=8),
  coupling beta 20-68% intra-finger-row vs 1-4% cross-group.
- Found + filtered the reader init artefact ([0,0,0] lead frames).
- Added direction-resolved coupling: finger row is PARALLEL (cos +0.88..+0.97), thumb↔thumb
  and index↔index are MIRRORED (cos -0.17..-0.31) => linear dominance filter does not work
  on the two channels the user's 16-zone architecture depends on.
- Pushed `VECTOR_DESIGN_CRITIQUE.md` (measured feasibility review of the 4-finger/16-zone design).
- Opened issues #1-#4 for agent 1 (thresholds, init artefact, two coupling classes, 40ms vs 88ms).
- Launched 4 research workers (muse-spark): academic enslavement, steno hardware,
  open-source, zero-force algorithms. All delivered; W1 verified against
  Hager-Ross & Schieber 2000 (PMC6773164) and Zatsiorsky 2000 (PMID 10766271).

## 05:47–06:05 — decoder, calibration limit, novelty, confidence
- `scripts/stroke_decoder.py`: the seam between the measured event layer and the language
  layer. Two measured findings while building it: contact count is NOT a chord criterion
  (108/108 events would be chords with ten fingers down; ~7 unexplained contacts per event),
  and peak alignment + magnitude is the criterion that works. A test caught a 45-degree
  rotation in the sector table.
- `scripts/pipeline_replay.py`: all stages audited against each other. AUDIT PASSED on 3
  sessions. Caught the chord-counting bug end-to-end.
- `scripts/calibration_transfer.py`: the per-pair coupling does NOT transfer across sessions
  at all - tracking IDs are never reused (55-74 vs 136-150). The coupling model is
  per-session unless contact identity is anatomical. Added `--task identity` to the guided
  harness so the labelled dataset is a scripted 5-minute session.
- W12 prior-art pass -> NOVELTY_STATEMENT.md: enslavement and drift compensation are known;
  what is new is the quantified resting operating point in mm and the per-pair regression
  suppression of touch-point covariation. Recorded what we must NOT claim.
- W9 -> language layer is the 40->150 WPM lever (issue #7). W10 -> nobody has published
  keyless steno above 16.8 WPM / 17.4% error; best flat sequential is 38-55 WPM. Success
  criterion reframed (CROSS_VALIDATION 1.8).
- Verified the 360 WPM record (Kislingbury, 97.23%) and corrected my own pessimistic WPM
  framing: the detector has 1.8x headroom over a world-record human.
- `scripts/rest_model.py` + REST_MODEL.md: the drift premise survives only with an adaptive
  baseline (W=19: 11.96 -> 5.04mm) and the persistence drops from 8 frames to 2.
- DECISION_HOLEMASK_VS_SOFTWARE.md: software suppression first, no hole mask, with
  reversal criteria.
- Orchestration moved to `scripts/gh_commit.py` (GitHub API) - no local git state, no
  conflicts with agent 1. Note: do NOT `git reset --hard` after a gh commit, it silently
  reverts to a stale local copy (this happened once and cost 6 tests).
- 29 tests green. 9 issues open for agent 1, still no replies.

## 06:02–06:10 — benchmark, first accuracy numbers, closed loop
- `scripts/make_benchmark.py` + `scripts/evaluate_session.py`: the first *scored* run in the
  project. Synthetic session calibrated to the three real recordings, same manifest format
  as the guided harness so synthetic and real cued data score identically.
- RESULTS: sector accuracy 1.00 (n=32), 0 idle false events in 9.7 s, tempo tracking
  0.97-0.99 at 1-3 Hz, COLLAPSE to 0.32 at 4-5 Hz, chord detection tp2/fp0/fn4 (reported
  broken, not tuned).
- KEY ENVELOPE: the 88 ms persistence window that makes the detector false-trigger-free is
  also the minimum quiet gap needed to segment two consecutive gestures. A mechanical key
  gives that gap by releasing; a 0-force surface cannot. => ~88 ms per gesture AND per gap,
  theoretical ceiling ~5.5 events/s, measured reliable ~3 Hz with 250 ms gestures, i.e.
  ~180 WPM equivalent at 1.5 syllables/word - exactly the steno certification bar.
  CONSEQUENCE: a vector gesture must contain its own return phase. 'Move and hold in the
  sector' cannot be segmented on this surface at any speed.
- The benchmark found three bugs that code review AND the pipeline audit had missed, two of
  which produced a confidently wrong accuracy number: direction labels rotated one sector
  (timestamp lookup straddling block boundaries), ground truth off by one block (closed vs
  half-open intervals), contacts teleporting between cues. All three pinned with tests.
  This is the argument for a scored benchmark: the pipeline passed every other check.
- `scripts/stroke_sink.py` closes the loop: Plover JSON, text transcript, optional uinput,
  with a retract path (the 360 WPM source makes undo/untranslate the cheapest speed win).
- 36 tests green, pipeline end-to-end on all three real sessions and the benchmark.

## 06:10–06:14 — latency, envelope, and a retraction
- `scripts/latency_budget.py`: CPU cost 90-289 us/frame against a 91Hz budget of
  10989 us/frame = 1-3% utilisation. The dominant cost is the 88ms detection window, not
  compute. Sensor latency is explicitly NOT measurable from the logged stream and is stated
  as such rather than assumed zero. Regression test pins the pipeline under 25% of a frame.
- `scripts/stroke_sink.py`: the output hop (Plover JSON / transcript / optional uinput) with
  a '*' retract path, because the 360 WPM source makes undo the cheapest speed win.
- `scripts/envelope_sweep.py`: measured the (gesture length x cue rate) surface per gesture.
- RETRACTION: the "3 Hz ceiling" from the previous entry was a metric artifact (events per
  block instead of per-gesture matching). Re-measured: 100ms gestures 0% detected at every
  rate; 150-350ms 100% detected at 1-6 Hz; 500ms 62%->36%. No 3Hz ceiling exists. The
  useful envelope is 150-350ms. Correction posted to issue #11 and BENCHMARK_RESULTS.md §0.
  I am recording the retraction rather than quietly fixing the number, because a confidently
  wrong headline is worse than a gap.
- Also unresolved and NOT claimed: direction accuracy differs between the two synthetic
  generators (0.19-1.0 vs 1.00). No direction-accuracy capability is quoted from either until
  the cued real session settles it.

## 06:18–06:21 — envelope corrected, return phase quantified
- Third metric bug found and fixed: sector_acc compared a block label to a block label, so
  the reported 'direction accuracy' never looked at the decoded direction. Real error was
  2-20deg, i.e. every sector inside its 22.5deg half-width.
- Root cause of the generator discrepancy: chaining sector targets without a return produces
  a CONSTANT 67.5deg direction error (1/8 correct); from a common centre, 0.0deg (8/8).
- Final envelope: 100ms 0% detected; 150-350ms 100% detection AND 100% direction accuracy at
  1-6Hz; 500ms 75-89% detection, 100% accuracy of those; zero idle false events everywhere.
  No 3Hz ceiling, no 5.5 ev/s ceiling - both retracted.
- `scripts/compass_geometry.py`: the repositioning contamination exceeds the 22.5deg
  half-width at EVERY thumb-plausible radius (r<=25mm), and even r=30mm leaves only 1.5deg
  margin. So the return phase is mandatory, not an optimisation.
- 42 tests, each envelope claim and each previously-wrong metric now pinned.
- Rule adopted and recorded: a number is not a finding until the metric that produced it has
  a test. The harness, not the pipeline, was the weak link.

## 06:22–06:24 — reversal segmentation vs sub-gate return
- W13 (gesture segmentation without lift-off) independently brackets the measured window:
  Beats reports 355ms mean touch execution, our envelope works to 350ms, and the $1 family
  needs ~600ms for fast gestures, exactly where our measurement degrades. Marking menus have
  encoded hierarchy through in-stroke direction reversals since 1993.
- `intent_filter.detect_reversal_events`: an event closes on a direction reversal, which needs
  no lift signal. Compared against the sub-gate-return strategy on the same task:
  - A sub-gate 30mm/s return + persistence: acc 1.00 at 1-4 Hz, but the return costs 0.67s for
    a 20mm arc, which does not fit in a 250ms period
  - B fast 200mm/s return + reversal: acc 1.00 at 1-2 Hz, 0.83/0.79 at 3-4 Hz
  - idle false events 0 in every cell of both
  => B is under-tuned, not wrong: it is the only option whose timing survives high rates.
  Neither wins yet; the turn threshold needs calibration against the cued session.
- Fourth harness bug (same shape as the third): the comparison left the mover vector empty in
  persistence mode, so strategy A's accuracy printed 0.0 without ever being measured. Found
  because I re-read the output instead of trusting it.
- Process slip worth recording: I committed while a test was failing, because the failure was
  hidden behind a pipe (`unittest | tail` returns tail's exit code). Caught it in the same
  minute and amended. Verifying the test exit code explicitly from now on.
- 44 tests green.

## 06:24–06:26 — the speed ceiling, and two more of my own wrong claims
- Hypothesis 'the reversal threshold is under-tuned': WRONG. turn_deg 30-120 give identical
  results; only 150 breaks. The threshold is not the limiter.
- The real limiter is the CYCLE BUDGET: accuracy holds at 1.00 while the cue rate is below
  1/(t_out + t_return) and collapses above it, because the next out-stroke starts during the
  return and contaminates its first 8 frames.
- Derived ceiling: out 150ms + return 33ms = 183ms cycle = 5.45 ev/s = 218 WPM (best corner);
  250ms out = 141 WPM; 350ms out = 104 WPM. 150 WPM needs a 267ms cycle, 250 WPM a 160ms one -
  and a 160ms cycle cannot contain a 150ms out-stroke plus a return. So 250 WPM is NOT
  reachable with out-and-back on this device.
- Honest claim now measured: a plausible path into 100-200 WPM - above every published touch
  system (16.8-55 WPM), at or below professional steno (180-225 WPM), consistently, because
  professional steno has a key release to segment on. The 0G surface spends its speed budget
  on the return stroke. Filed as issue #14, superseding #4, #5, #11.
- Process: I also committed once while a test was failing (failure hidden behind a pipe).
  Caught in the same minute, fixed, amended. Checking exit codes explicitly now.

## 06:33–06:37 — separation model, a reverted hypothesis, and a filled research gap
- SEPARATION_MODEL.md + scripts/separation_model.py: the six-step model written down and
  CHECKED rather than restated. Worst resting run per gate, pooled over 17 contacts:
  13 frames at 20mm/s, 7 at 40 (1 frame margin), 5 at 60, 3 at 100.
- Hypothesis: raising the gate to 60mm/s is free safety (latency comes from k, not the gate).
  MEASURED: it costs long-gesture detection - 350ms drops to 0.67-0.75, 500ms to 0.00. The
  literature says real gestures average 355ms, exactly the band 60mm/s loses. REVERTED to 40,
  trade-off recorded in code and doc. Issue #15 closed with the measurement.
- W16 (layout optimisation) returned an explicit NOT FOUND: no layout optimised from a
  measured confusion matrix with before/after figures. Filled it:
  LAYOUT_ASSIGNMENT.md + scripts/layout_assignment.py. Result: on-axis-first rule -30.5%,
  annealed optimum -36.1%, and 99.6% of confusion mass goes to a NEIGHBOURING sector.
- The calibration produced the most useful number of this block: the fitted per-frame
  direction noise is 1.84-2.03mm against a 0.56mm sensor floor - a factor of 3.6. The
  direction error is aim and biomechanics, not electronics. Sensing work does not improve
  direction accuracy; training and target geometry do. That reinforces the language-layer and
  training priority (issue #7) with a number rather than an argument.
- A test of mine asserted confusion forms a hard ring; it caught a 2-sector skip in 3 of 4800
  trials. The claim is now the measured 99.6% share, not a property.
- Triage: closed #4, #5, #10, #11 as superseded (kept, not deleted, so the retraction history
  stays auditable). 11 open, all actionable and none carrying a retracted number.
- 51 tests green.

## 06:38–06:44 — layout, a sixth rejected hypothesis, and issue triage
- LAYOUT_ASSIGNMENT.md + scripts/layout_assignment.py: W16 reported as NOT FOUND that no
  layout was ever optimised from a MEASURED confusion matrix. Filled it. The calibration
  produced the block's most useful number: fitted direction noise 1.84-2.03mm/frame against a
  0.56mm sensor floor - a factor of 3.6. The direction error is aim and biomechanics, not
  electronics, which is why the lever is training and language layer, not sensing.
  Result: on-axis-first rule -30.5%, annealed optimum -36.1%, 99.6% of confusion mass goes to
  a NEIGHBOURING sector -> never place a minimal pair on adjacent cells.
- Sixth hypothesis tested and rejected: collinearity as a suppression veto. The premise
  (enslavement is collinear) holds for the strongest pairs (cos 0.88-0.97) but not the
  population - measured cost 24/159 real suppressions and ALL 57 benchmark suppressions.
  Reverted, cos kept as a diagnostic. CROSS_VALIDATION 1.11 now lists all six rejections.
- Chord issue closed with a measurement: a controlled generator detects 10/10 chords
  regardless of peer speed, so the reported fn=4 was a scoring artifact, not a detector
  failure. Chord support is UNVALIDATED rather than absent - a different engineering posture.
- Issue #1 fixed by me: the protocol's threshold sweep (2-40mm/s, 1-12mm, 0.5-3mm) sat
  BELOW the measured rest noise. Regridded with a persistence axis and the coupling between
  gate and window stated.
- Issue #2 closed as MIS-SCOPED by me: audit_input.py records raw evdev events, not
  assembled contacts, so the init artefact cannot occur there. Checking saved wasted work.
- Issue #13 verified closed by agent1's own commit (out-and-back adopted, 88ms latency floor
  accepted, WPM labelled unmeasured).
- 58 tests green in the MERGED tree (mine + agent1's session_manifest work). Note: my local
  tree was stale until I re-synced - tests must be run against origin/main, not a local copy.
- Remaining open: #14 (speed ceiling wording), #12, #9, #7, #6 - all legitimately
  agent1-side or hardware-blocked.

## 06:45–06:50 — sampling precision, dataset validation, and the last open number
- Quantified the sampling precision behind every coupling claim: within a session it is TIGHT
  (r=+0.958, n=312, Fisher 95% CI [+0.947,+0.966]); across sessions it is NOT MEASURABLE
  (tracking IDs are ephemeral); across hands/days there is ZERO data (327 pair fits, one
  operator). The honest phrasing is now in NOVELTY_STATEMENT: the model is well determined
  within a session and completely undetermined outside it.
- W19 (correction latency) returned an explicit NOT FOUND: no published number says a
  3-5 events/s input can be corrected after the fact without the undo path becoming the
  bottleneck. That negative result IS the finding - it is the one open number that decides
  whether the 100-218 WPM ceiling is reachable, and it is a measurement, not a literature
  question.
- Added --task correction to the guided harness: alternating sector stroke and deliberate
  undo, so corrections/min and repair latency can be read off a cued stream.
- scripts/identity_dataset_check.py: validates a finger-identity capture before it trains
  anything. The label is only the cue; a sloppy session silently poisons the dataset. Checks
  the presence GAP of each contact per cue and reports VALID/MISSING/AMBIGUOUS. Exit 0 only
  if every cue is valid, so it can gate a pipeline step. Two bugs found and fixed in the
  process (whole-window absence instead of a gap; a test fixture whose manifest window closed
  before the lift).
- CUED_SESSION_PROTOCOLS.md: the six tasks in one place, ordered by information per minute,
  with the three scoring traps that produced wrong numbers pinned.
- W18 (bimanual/drift/fatigue) still running; it targets the largest untested assumption -
  every measurement so far is within-hand.
- 73 tests green in the merged tree after agent1's schema-version work; verified the old
  captures still load and analyse.

## 06:45–06:55 — dataset validation, correction task, and a seventh rejected hypothesis
- identity_dataset_check.py: validates a finger-identity capture before it trains anything.
  The label is only the cue; nothing verified the operator lifted the right finger. Checks the
  presence GAP per cue, reports VALID/MISSING/AMBIGUOUS, exits non-zero unless all valid.
  Clean capture 6/6 VALID; 3-frame jitter MISSING; two fingers at once AMBIGUOUS.
- --task correction added: alternating sector stroke and deliberate undo, because W19 found
  NO published number for correction throughput at 3-5 events/s - the one number that
  decides whether the 100-218 WPM ceiling is reachable.
- CUED_SESSION_PROTOCOLS.md: the six tasks in one place, ordered by information per minute,
  with the three scoring traps that produced wrong numbers pinned.
- W18 (bimanual/drift/fatigue) ranked body drift as the primary threat. TESTED AND REJECTED:
  a static-anchor rigid fit (translation + in-plane rotation) removes only ~20% of the
  cross-hand anti-correlation (73->55: -0.858 -> -0.660) and leaves within-hand couplings
  untouched. So the cross-hand structure is NOT simple rigid-body motion.
  - trap 1: fitting on ALL contacts reported -0.858 -> +0.602, a convincing false
    confirmation; when every contact moves together the fit reads the gesture as rotation.
  - trap 2: the normal equations returned half the true omega; caught by a rotation test.
- Consequence: bimanual interference, not drift, is the top open hardware question. W18 has
  the protocol (alternating vs simultaneous two-hand taps, cross-correlation at lag 0/1).
- 76 tests green.

## 06:54–06:57 — the compass radius: the first layout surface from our own noise
- Tested whether the 3.6x direction error is BIAS (correctable) or VARIANCE (only trainable):
  |mean|/sd = 0.02 at every noise level. It is variance. A bias model has nothing to fix -
  closed option, pinned by a test.
- Then tested the assumption that a longer accumulation window averages the noise away.
  REVERSED: at fixed compass radius a longer window means a smaller step per frame, so SNR
  falls. Accuracy 0.822 at 8 frames -> 0.461 at 40. Accuracy is bought with AMPLITUDE, not
  duration.
- COMPASS_SURFACE.md: radius x accuracy x contamination x cycle cost, from the measured
  2.03mm/frame noise. r=20mm gives 0.822 accuracy; r=30mm gives 0.957 for -18% cycle rate.
  r<=12mm is not viable (0.576, sector pitch only ~16x the resting step).
- Both accuracy AND contamination improve with radius; only the return leg (linear in r)
  opposes it. Every WPM figure is conditional on a 600mm/s return, i.e. on reversal
  segmentation being the working strategy - so radius and return strategy cannot be chosen
  independently.
- Filed as issue #17: the radius choice is a product decision (does the LM absorb the
  residual error?) and the reach feasibility is a measurement, not an assumption.
- 79 tests green.

## 06:58–07:05 — temporal signatures, a premise overturned, and a tool review
- Coupling classes differ in temporal SHAPE: within-hand 64->61 r(lag0)=+0.958 half-width
  2 frames (~22ms, sharp = immediate mechanical transmission); cross-hand 73->55 r(lag0)=-0.859
  half-width 5 frames (~55ms, persistent = sustained coordination). BOTH peak at lag 0, so
  there is no latency a decoder can wait out. Shipped lag_profile + half_width_frames,
  documented as step 4b in SEPARATION_MODEL, answered issue #16.
- Premise overturned by our own data: the measured natural gesture envelope is a ~12mm radius
  (thumb bboxes 24.6x18.2mm and 20.6x15.9mm; index similar). The accuracy-optimal 30mm radius
  is 2.5x larger. Stated as a LOWER BOUND because the sessions were exploratory, not cued.
  Three resolutions offered in COMPASS_SURFACE.md; it is a product decision.
- Hardened scripts/gh_commit.py: a non-fast-forward ref update now re-reads the remote head
  and REBUILDS the commit on it (3 attempts, then stop). Forcing a stale-parent push would be
  wrong, and the failure cost one addendum once.
- Reviewed agent1's new scripts/rest_calibration.py: it independently reproduces my numbers
  (40 mm/s, 8 frames, rest_worst_run 7) - the strongest cross-check so far. Its objective has
  one gap: clean only means no rest false activation, so it selects (60, 5) without noticing
  that 60 mm/s stops detecting 350-500 ms gestures. Filed as a review issue.

## 07:55–08:00 — the radius is settled, and the architecture re-orders itself
- W20 (thumb reach) triangulated with our own recordings and COMPASS_SURFACE: the design
  radius is 12-15mm, not 20 or 30. W20's 90%-comfort patch is ~3.8x10.1mm, the 70%-box
  ~21.9x30.4mm, and a 60mm sweep (r=30) fits in neither. Our measured envelope (24.6x18.2mm)
  lands ON the 70% box from a completely different posture and population.
- THE CONSEQUENCE: at an ergonomic radius the compass has 32-42% label error. The language
  layer is no longer the speed lever (issue #7) but the CORRECTNESS lever. Filed as a new
  issue with a three-task order: ranked-candidate decoding with an LM, correction policy,
  and a benchmark run at the real radius with the label noise in it.
- Also retired the 'train the larger excursion' option: it asks the hand to leave its
  measured comfort envelope, which is not a speed/accuracy trade.
- Reviewed agent1's rest_calibration.py: it independently reproduces my rest numbers
  (40 mm/s, 8 frames, worst run 7) - the strongest cross-check so far. Its objective only
  knows the rest criterion, so it selects (60,5) while 60 mm/s stops detecting 350-500ms
  gestures; filed with the suggestion to add gesture coverage as a second column.
- Privacy: removed hardcoded personal home paths from two shipped files; raw captures are
  now reached only via TOUCH_STENO_SESSIONS and the test skips cleanly without it. Verified
  0 raw jsonl files ever committed.

## 08:01–08:08 — built the language layer, then measured what it actually buys
- scripts/candidate_ranking.py: ranked-candidate decoding. Geometric confidence enters as a
  log-likelihood offset so sensor and language share units; commit-vs-retract by POSTERIOR,
  not absolute log-prob (an absolute floor retracted 5 of 5 demo strokes - the unigram floor
  of a modest lexicon is already below any sensible absolute threshold).
- scripts/lm_recovery.py: the experiment, through the MEASURED confusion matrix and a real
  20k word list. Results at 12/15/20/30mm: geometric word accuracy 0.068/0.155/0.395/0.845;
  LM 0.888/1.0/1.0/1.0; retracted 31.6/10.2/0/0%; usable WPM at 1s/correction
  0.0/21.6/40/66.7.
- The claim from the previous cycle holds AND is incomplete: the LM really does rescue
  accuracy, but it converts label noise into correction work, and that is the bottleneck. At
  12mm the user owes 0.95 corrections/s; at 1s each the usable rate is ZERO.
- The system only runs correction-free at r>=20mm - the edge of the comfort envelope. So the
  binding constraint moved again: from sensor noise, to geometry, to now correction
  throughput - a number W19 established is NOT in the literature, and which is the cheapest
  measurement in the project (stopwatch + word list, no tablet).
- Four bugs found in my own code during this build, each producing a confident wrong number:
  sector names fed to a character model (LM scored 1.0 everywhere); confusion row MODE
  measured instead of the SAMPLED outcome (100% baseline); sigma scaled with radius and
  inverted (perfectly diagonal matrix); absolute commit floor (retracted everything).
  build_confusion now takes the radius as a parameter and is verified against
  COMPASS_SURFACE (diagonal 0.627/0.731/0.855/0.971 vs 0.576/0.681/0.822/0.957).
- Three of my own new tests were wrong and are corrected to assert the real property. The
  useful discovery: the model is deliberately CONSERVATIVE - interpolation weights a bigram
  at 0.65, so a near-certain unigram cannot be overruled. That is right for a steno decoder,
  which would otherwise turn clear signals into wrong ones, and it is now pinned.
- 110 tests green. Filed the decisive-open-number issue.
