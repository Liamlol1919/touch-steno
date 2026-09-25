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
