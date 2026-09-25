# Chordtouch Research

Research and implementation notes for high-speed text input on a continuous touch surface, with emphasis on a Wacom PTH-660.

## Deliverables

- [COMPREHENSIVE_RESEARCH_REPORT.md](COMPREHENSIVE_RESEARCH_REPORT.md) — HCI evidence, models, null-force analysis, architecture and source protocol.
- [SYSTEM_COMPARISON_MATRIX.md](SYSTEM_COMPARISON_MATRIX.md) — stenography, chord, gesture and tap-sequence systems.
- [RECOMMENDED_ARCHITECTURES.md](RECOMMENDED_ARCHITECTURES.md) — five implementable architectures and PTH-660 deployment plan.
- [CODE_REFERENCES.md](CODE_REFERENCES.md) — reusable open-source repositories and integration ideas.
- [EXPERIMENT_PROTOCOL.md](EXPERIMENT_PROTOCOL.md) — reproducible PTH-660 sensor, intent and ergonomics protocol.
- [RESEARCH_LOG.md](RESEARCH_LOG.md) — iteration TODO and GitHub progress log.
- [SYNTHETIC_BASELINE.md](SYNTHETIC_BASELINE.md) — reproducible synthetic zero-force detector sanity check.
- `scripts/audit_input.py` — safe evdev capability/event audit.
- `scripts/synthetic_intent_benchmark.py` — deterministic tap/drift/rest/palm/ring synthetic test.
- `tests/` — standard-library unit tests.

## Important evidence note

The current document is a research starting point, not a final performance claim. Most published surface/chording results are below 150 WPM. All benchmark values need to be checked against the original paper and normalized for corrected speed, training and task language.

## Local source repository

The user-supplied `Liamlol1919/touch-steno` repository was checked on 2026-09-25 and is currently public but empty (GitHub reports “This repository is empty”). It is used as the research remote; source-code analysis of that repository is therefore pending until it contains a commit.
