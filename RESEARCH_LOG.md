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
- [ ] Add per-user rest/palm covariance calibration and replayable threshold sweeps.
- [ ] Define opt-in privacy-safe telemetry and correction/undo metrics.
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
