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
