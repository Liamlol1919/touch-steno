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
