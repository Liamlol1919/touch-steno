# Research Log / TODO

## Iteration 1 — 2026-09-25 05:07–05:13 CEST

- [x] Arbeitsverzeichnis und GitHub-Repository angelegt.
- [x] HCI-Suche zu Flat-Surface-/Eyes-free-Eingabe gestartet.
- [x] Plover, 8VIM, Dasher, Linux Wacom, libinput und uinput geprüft.
- [x] Vier Pflicht-Deliverables erstellt.
- [x] Initialer Commit `f7e239d` und Push auf `Liamlol1919/touch-steno`.
- [x] Code-Integrationsdetails und Palm-Rejection-Belege ergänzt; Push `7d0374d`.
- [x] Upstream-Repositories geklont und Commit-SHAs dokumentiert (`references/UPSTREAM_SNAPSHOT.md`).
- [ ] PTH-660 anschließen und `scripts/audit_input.py` ausführen.
- [ ] Eventknoten, `ABS_MT_*`-Achsen und Treiberarbitration protokollieren.
- [ ] Original-PDFs der noch markierten Twiddler/Flat-Glass-Benchmarkwerte prüfen.
- [ ] Plover-Abhängigkeiten in einer isolierten Umgebung installieren.
- [ ] Ersten Zero-Force-Prototyp implementieren.

## Iteration 2 — 2026-09-25 05:17–05:21 CEST

- [x] Plover-/8VIM-/DasherCore-/Linux-Repositories mit festen SHAs lokal geklont.
- [x] `scripts/synthetic_intent_benchmark.py` implementiert: Tap, Drift, Rest, Palm, Ring-Kopplung.
- [x] `SYNTHETIC_BASELINE.md` als ausdrücklich nicht gemessene Baseline ergänzt.
- [x] Synchronisierten Ringfinger-Burst-Guard ergänzt; echte Chord-Unterdrückung als dokumentiertes Risiko markiert.
- [x] Drei Standardbibliothek-Tests implementiert und erfolgreich ausgeführt.
- [x] PTH-660 weiterhin nicht angeschlossen; keine Hardwarebehauptung ergänzt.

- [x] `DECODER_DESIGN.md` mit Zustandsmaschine, Featurevertrag, Enslavement-Score und Plover-Bridge ergänzt.
- [x] Agent-2-Commit `2a52201` mit `SYSTEMKOMPENDIUM.md` per Rebase integriert; keine fremde Datei überschrieben.

## Next iteration

- [ ] Cued PTH-660 run: `guided_calibration.py --task sectors`, then evaluate the real session.
- [ ] Cued tempo run: measure deliberate event rate per gesture; do not infer it from 88 ms latency.
- [ ] Cued chord run: calibrate peak-ratio and lag thresholds; keep chords unimplemented until then.
- [x] Stabilize a versioned raw-event JSONL schema and legacy replay path.
- [x] Add per-user rest/palm covariance calibration and replayable threshold sweeps.
- [x] Define correction/undo metrics with explicit motion-versus-text provenance.
- [x] Define opt-in privacy-safe aggregate telemetry for raw sessions.
- [x] Normalize `guided_calibration.py` paired manifest records and make `evaluate_session.py`
  use one-to-one synthetic tempo/chord matching; legacy guided tempo remains aggregate mode.
- [x] Add expected per-event cue timestamps to guided tempo capture; evaluator labels them
  `expected_cue_schedule`, distinct from observed hardware timing.

## Iteration 3 — 2026-09-25 06:18–06:24 CEST

- [x] Fast-forwarded local work to remote `18c4d34` after checking `git fetch`; no local collision.
- [x] Audited open issues #1–#12 and incorporated Agent 2's documented 3 Hz retraction.
- [x] Removed the unsupported `1/88 ms = 11.4 events/s` ceiling from `wpm_ceiling.py` and its tests.
- [x] Reframed 88 ms as evidence/latency; retained day-0 2.56 events/s as an untrained baseline only.
- [x] Corrected contradictory benchmark, cross-validation and vector-design prose.
- [x] Added five rate-budget tests; targeted tests and `py_compile` passed.
- [ ] PTH-660 cued hardware data remains outstanding; no hardware result was added.

## Collaboration

Agent 1 maintains the research synthesis and architecture documents. Agent 2 maintains the
measurement/decoder/benchmark side. Shared writes are published through the authenticated
GitHub API after checking the remote head; no local branch is assumed authoritative.

## Iteration 4 — 2026-09-25 06:28–06:35 CEST

- [x] Added shared manifest normalization for complete and legacy paired cue records.
- [x] Fixed guided capture to run the reader thread and write complete per-cue records.
- [x] Fixed guided chord labels, rest labels and peak-aligned chord scoring.
- [x] Removed stale benchmark rows and qualified synthetic 100–218 WPM as conditional.
- [x] Added manifest/chord regression tests; targeted tests and `py_compile` passed.
- [ ] Cued PTH-660 data and deliberate user throughput remain unmeasured.

The corrected sub-gate envelope realizes 1.01–1.48 Hz for 150–350 ms synthetic gestures.
The separate 100–218 WPM figures are conditional fast-return cycle-model outputs, not
measured PTH-660 throughput.

## Iteration 5 — 2026-09-25 06:40–06:45 CEST

- [x] Added expected per-event cue schedules to guided tempo tasks.
- [x] Kept legacy guided manifests on the explicit aggregate fallback.
- [x] Added provenance and one-to-one schedule tests; guided schedule is not observed timing.
- [ ] A cued PTH-660 run is still required to measure actual user throughput.

## Iteration 6 — 2026-09-25 06:45–06:52 CEST

- [x] Added explicit `touchsteno.raw_frame` v1 encoding.
- [x] Kept legacy `{t,c}` recordings readable through the canonical loader.
- [x] Added fail-closed handling for unknown schema/version values.
- [x] Added recorder round-trip, legacy compatibility and schema documentation.
- [ ] Raw sessions still require a privacy review and real-device capture.

## Iteration 7 — 2026-09-25 06:50–06:57 CEST

- [x] Identity validator now requires explicit operator-confirmed finger-to-tracking-ID mapping.
- [x] Unique lift without mapping returns `UNVERIFIED`; wrong mapping returns `CONTAMINATED`.
- [x] Added attribution, ambiguity, shallow-lift and mapping tests.
- [ ] A real identity capture with confirmed mapping is still required.

The cue label is not anatomical attribution. Issue #9 remains open until a confirmed
mapping is collected and the resulting identity model is evaluated across sessions.

## Iteration 8 — 2026-09-25 07:02–07:08 CEST

- [x] Added opt-in `suppression_decision()` requiring both r² and temporal sharpness.
- [x] Kept shipped magnitude-only suppression unchanged pending cued two-hand evidence.
- [x] Added sharp/broad/low-magnitude policy tests and documented the opt-in boundary.
- [ ] Issue #16 cued alternating-vs-simultaneous session remains necessary for adoption.

## Iteration 9 — 2026-09-25 07:04–07:10 CEST

- [x] Made compass return speed/strategy an explicit conditional model input.
- [x] Kept the 600 mm/s default for compatibility; added sub-gate-return output and tests.
- [x] Prevented radius WPM figures from being read independently of return strategy.
- [ ] Issue #17 radius decision still requires cued reach and return-strategy measurements.
- [x] Corrected the sub-gate-return arithmetic: 0.70 Hz at r=20 mm and 0.48 Hz at r=30 mm;
  earlier one-return-leg figures were withdrawn.

## Iteration 10 — 2026-09-25 07:07–07:15 CEST

- [x] Added `TRAINING_PATH.md` with staged gates from safety to sustained language work.
- [x] Separated sourced learning curves from PTH-660 performance hypotheses.
- [x] Scoped a versioned Plover JSON starter-brief deliverable with collision lint and metrics.
- [x] Marked personal brief count behind the 360 WPM record as NOT FOUND.
- [ ] Cued PTH-660 training measurements remain outstanding.

## Iteration 11 — 2026-09-25 07:12–07:20 CEST

- [x] Removed reintroduced 11.4-Hz/5.5-Hz/150+-WPM-headroom prose from cross-validation.
- [x] Restated the realized synthetic envelope and synthetic-only direction result.
- [x] Kept human 360 WPM as an anchor, not a PTH-660 throughput claim.
- [x] Full suite remains green; no new hardware evidence was added.

## Iteration 12 — 2026-09-25 07:16–07:24 CEST

- [x] Added `correction_metrics.py` for replayable corr_undo analysis.
- [x] Kept cue-to-undo-motion latency separate from text-repair latency.
- [x] Text repair metrics require an explicit timestamped repair log; absence is explicit.
- [x] Added correction metric tests and updated the cued protocol/README.
- [ ] A real cued correction capture and text-sink repair log remain outstanding.
- [x] Hardened correction metrics: motion is named as detected-event latency, rates use total
  correction exposure, and text repair requires typed monotonic undo records.

## Iteration 13 — 2026-09-25 07:21–07:30 CEST

- [x] Added typed correction repair-log validation and corrected exposure-based rates.
- [x] Fixed evaluator text mode to expose axis/diagonal keys present in its result contract.
- [x] Added CLI regression coverage for human-readable evaluation output.
- [ ] Real correction capture with a Plover/text repair log remains outstanding.
- [x] Added stable `cue_id` fields to guided tasks and repair-log association.

## Iteration 14 — 2026-09-25 07:31–07:40 CEST

- [x] Added `telemetry_export.py` with aggregate-only output and explicit privacy flags.
- [x] Added consent/retention policy and privacy tests proving no raw coordinates, IDs or
  session names enter telemetry.
- [x] Raw JSONL remains a separate restricted artifact; no raw export switch was added.
- [ ] Local privacy review and real consented capture remain outstanding.
- [x] CLI now requires explicit `--consent`; raw/aggregate boundary is enforced by code.

## Iteration 15 — 2026-09-25 07:39–07:48 CEST

- [x] Added `rest_calibration.py` sidecar with source hashes, rest covariance, full sweep rows,
  deterministic candidate selection and replay comparison.
- [x] Production `intent_filter.py` defaults remain unchanged.
- [x] Added calibration artifact tests and documented the local-only workflow.
- [ ] Real per-user rest/palm captures are still required before adopting a custom point.

## Iteration 16 — 2026-09-25 07:49–07:55 CEST

- [x] Added `guided_calibration.py --task palm` with explicit palm-rest provenance.
- [x] Added palm task tests and corrected cued-protocol ordering.
- [x] Palm baseline is now separable from generic finger-rest/noise capture.
- [ ] Real palm/rest hardware sessions remain outstanding.

## Iteration 17 — 2026-09-25 07:54–08:02 CEST

- [x] Added layered Plover JSON dictionary checker with duplicate-key, outline, translation
  and cross-layer collision validation.
- [x] Added `PLOVER_BRIEFS.md` and tests; no translation or speed claim was added.
- [x] Language-layer TODO now has a concrete format/collision gate before brief authoring.
- [ ] Real brief coverage, untranslate rate and speed delta remain unmeasured.

## Iteration 18 — 2026-09-25 08:00–08:08 CEST

- [x] Added optional gesture-length coverage to calibration candidate rows and selection.
- [x] Kept `selection_basis=rest_clean_only` explicit when coverage is absent.
- [x] Added replay-safe coverage tests; no unmeasured coverage values were fabricated.
- [ ] Real gesture-length coverage data remains required for a production operating point.

## Iteration 19 — 2026-09-25 08:06–08:14 CEST

- [x] Added `candidate_ranker.py` for confidence/language ranked candidates.
- [x] Preserved candidate provenance and explicit language-availability state.
- [x] Added `CANDIDATE_RANKING.md` and tests; no LM or accuracy claim was added.
- [ ] A real-radius labelled benchmark and Plover/LM adapter remain outstanding.

## Iteration 20 — 2026-09-25 08:11–08:20 CEST

- [x] Added local `correction_throughput.py` for human repair-interval observations.
- [x] Added strict JSONL validation, median/P95/rate reporting and protocol documentation.
- [x] No human correction-throughput result or WPM extrapolation was fabricated.
- [ ] A real multi-user correction-throughput capture remains outstanding.

## Iteration 21 — 2026-09-25

- [x] Persisted `min_gesture_coverage` in rest-calibration artifacts.
- [x] Made `replay_sweep()` reuse the recorded threshold; legacy artifacts default to `1.0`.
- [x] Added a behavioral test proving a below-threshold gesture candidate is excluded and replay preserves the selected candidate.
- [ ] Real user-specific gesture-coverage measurements remain outstanding; no hardware result was added.

## Iteration 22 — 2026-09-25

- [x] Added `lexicon_decoder.py` for bounded top-3, word-level lexicon-constrained search.
- [x] Added explicit `resolved`, `ambiguous`, and `unreachable` outcomes without text commitment.
- [x] Kept the language prior tie-only and preserved candidate provenance in the result.
- [x] Removed stale withdrawn correction/WPM claims from `LM_RECOVERY.md`.
- [ ] Correctly conditioned cued candidate capture and downstream re-measurement remain outstanding.
