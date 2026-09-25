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

## 05:33–05:47 — falsification, filter, WPM, rest model, decision
- 17 evidence tests (`tests/test_measured_evidence.py`): rest never fires, mover fires,
  5-frame burst does not, 250 WPM/2-events-per-syllable exceeds the ceiling (pinned as an
  invariant). 20/20 with agent 1's tests.
- `scripts/intent_filter.py`: the "step 2 trigger" the design chat asked for, with measured
  constants (v>=40 mm/s, k>=8 frames, per-pair signed regression, r^2>=0.5). Suppresses 175
  followers in the ten-finger session, 0 in the thumb session — as the r^2 predicted.
- KEY MEASUREMENT: free-motion event rate is 2.56 events/s, not the 11.4/s latency ceiling.
- `scripts/wpm_ceiling.py`: 250 WPM only fits under the ceiling with 1 event per syllable.
- Verified the 360 WPM human record (Kislingbury, Guinness, 97.23%): ~6 strokes/s, so the
  detector has ~1.8x headroom over a world-record human. Corrected my own pessimistic
  framing; the binding constraint is the language layer.
- `scripts/guided_calibration.py`: the four falsification tests are now runnable
  (tempo ramp, 8-sector compass with axis metadata, chord-vs-single, rest floor), with a
  sidecar manifest and `--merge` for labelled frames.
- `scripts/rest_model.py` + REST_MODEL.md: the "drift instead of position" premise survives
  only with an adaptive baseline. Sliding W=19 (~209 ms) cuts the REST residual max from
  11.96 mm to 5.04 mm and drops the required persistence from 8 frames to 2 (~4x latency).
- W5/W6/W7/W8/W9/W10 worker research integrated. W5 and W6 independently conclude 8-way is
  the defensible limit; W7 finds no evidence for a capacitive hole mask; W9 turns the
  language layer into a prioritised backlog.
- DECISION_HOLEMASK_VS_SOFTWARE.md: software suppression first, no hole mask, with
  reversal criteria stated in advance.
- Orchestration switched from `git push` to `scripts/gh_commit.py` (GitHub API from the
  current remote head) so the two agents never fight over local git state.
- Open issues for agent 1: #1 thresholds, #2 init artefact, #3 coupling classes (+correction),
  #4 40ms vs 88ms, #5 WPM ceiling (+correction), #6 training path.
