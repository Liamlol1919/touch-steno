# Chordtouch Research

Research and implementation notes for high-speed text input on a continuous touch surface, with emphasis on a Wacom PTH-660.

## Deliverables

- [COMPREHENSIVE_RESEARCH_REPORT.md](COMPREHENSIVE_RESEARCH_REPORT.md) — HCI evidence, models, null-force analysis, architecture and source protocol.
- [SYSTEM_COMPARISON_MATRIX.md](SYSTEM_COMPARISON_MATRIX.md) — stenography, chord, gesture and tap-sequence systems.
- [RECOMMENDED_ARCHITECTURES.md](RECOMMENDED_ARCHITECTURES.md) — five implementable architectures and PTH-660 deployment plan.
- [CODE_REFERENCES.md](CODE_REFERENCES.md) — reusable open-source repositories and integration ideas.
- [EXPERIMENT_PROTOCOL.md](EXPERIMENT_PROTOCOL.md) — reproducible PTH-660 sensor, intent and ergonomics protocol.
- [RESEARCH_LOG.md](RESEARCH_LOG.md) and [AGENT2_RESEARCH_LOG.md](AGENT2_RESEARCH_LOG.md) — living project and measurement logs.
- [DECODER_DESIGN.md](DECODER_DESIGN.md) — state machine, feature contract, enslavement model and Plover bridge.
- [SYNTHETIC_BASELINE.md](SYNTHETIC_BASELINE.md) and [BENCHMARK_RESULTS.md](BENCHMARK_RESULTS.md) — explicitly synthetic checks and the corrected gesture-length envelope.
- [MEASURED_BIOMECHANICS.md](MEASURED_BIOMECHANICS.md), [MEASURED_INTENT_FILTER.md](MEASURED_INTENT_FILTER.md) and [CROSS_VALIDATION.md](CROSS_VALIDATION.md) — measured PTH-660 distributions and evidence limits.
- `scripts/audit_input.py` — safe evdev capability/event audit.
- `scripts/synthetic_intent_benchmark.py`, `scripts/make_benchmark.py`, `scripts/envelope_sweep.py` and `scripts/wpm_ceiling.py` — deterministic analysis tools; synthetic results are not hardware claims.
- `scripts/session_manifest.py` and `tests/test_session_manifest.py` — shared normalization
  for complete and legacy paired cue manifests.
- `scripts/session_runner.py` and [CUED_SESSION_PROTOCOLS.md](CUED_SESSION_PROTOCOLS.md) —
  hardware-aware, dry-run-capable cued measurement sessions including bimanual coupling.
- [BIMANUAL_ANALYSIS.md](BIMANUAL_ANALYSIS.md) and `scripts/bimanual_coupling.py` —
  offline raw-contact timing, episode, and unfiltered pair analysis.
- [RAW_FRAME_SCHEMA.md](RAW_FRAME_SCHEMA.md) and `scripts/raw_schema.py` — versioned raw-frame
  JSONL contract with legacy replay compatibility.
- `scripts/identity_dataset_check.py` — identity-capture gate; `VALID` requires an explicit
  operator-confirmed finger-to-tracking-ID mapping.
- [TRAINING_PATH.md](TRAINING_PATH.md) — staged cued-training gates, Plover brief scope and
  evidence boundaries.
- `scripts/correction_metrics.py` and `tests/test_correction_metrics.py` — separates
  cue-to-undo-motion latency from explicitly logged text-repair latency.
- [CORRECTION_THROUGHPUT.md](CORRECTION_THROUGHPUT.md) and
  `scripts/correction_throughput.py` — local human repair-interval measurement.
- [PRIVACY_TELEMETRY.md](PRIVACY_TELEMETRY.md) and `scripts/telemetry_export.py` — opt-in,
  aggregate-only telemetry export with no raw coordinates or identifiers.
- `scripts/rest_calibration.py` and `tests/test_rest_calibration.py` — local per-user rest
  covariance/sweep artifact with source hashes and replay comparison.
- [PLOVER_BRIEFS.md](PLOVER_BRIEFS.md) and `scripts/plover_dictionary_check.py` — layered
  Plover JSON outline/translation validation with collision lint.
- [LANGUAGE_LAYER_METRICS.md](LANGUAGE_LAYER_METRICS.md) and
 `scripts/language_layer_metrics.py` — privacy-minimized local untranslate/undo/strokes-per-word counts.
 `scripts/language_event_recorder.py` — local semantic event producer for future Plover hook adapters.
- [CANDIDATE_RANKING.md](CANDIDATE_RANKING.md) and `scripts/candidate_ranker.py` —
  confidence/language ranked candidates without committing text.
- [LEXICON_DECODING.md](LEXICON_DECODING.md) and `scripts/lexicon_decoder.py` —
  top-3 candidate search over a lexicon without committing text.
- [LEXICON_RECOVERY.md](LEXICON_RECOVERY.md) and `scripts/lexicon_recovery.py` —
  correctly conditioned observed-sector benchmark for reachability and correction actions.
- `tests/` — standard-library unit tests for decoder invariants, measured constants and benchmark artefacts.

## Important evidence note

The current documents are a research starting point, not a final PTH-660 performance claim.
Most published surface/chording results are below 150 WPM. The measured hardware numbers
and synthetic benchmark results are kept separate. In particular, the 88 ms persistence
window is an evidence/latency requirement, not a measured event-rate ceiling; deliberate
throughput must be measured with a cued device session.

## Repository coordination

The research remote is `Liamlol1919/touch-steno`. The two agents coordinate shared writes
through the authenticated GitHub API (`scripts/gh_commit.py`) to avoid stale local pushes.
Before each publication, fetch and inspect the remote head and open issues.
