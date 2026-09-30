# Validation Snapshot — 2026-09-30 03:50 CEST

## Core checks

```text
python3 run_core_checks.py --allow-stale-layout → Exit 0
python3 -m unittest discover -s tests -q         → 54 tests, OK
```

The offline core run passed the layout optimiser and hand-reader self-tests. The
provenance check still reports the known stale layout: `layout.json` embeds an
older measured profile while the current `hand_profile.json` is `REJECTED`.
That is why the run used `--allow-stale-layout`; without the flag the runner
correctly returns Exit 2.

## Fixes covered by the current suite

- independent MT slot state;
- X/Y axis-order safety and true palm spans;
- step-boundary contact flush;
- legacy-to-MT transition;
- rejected profile refusal and case-insensitive status checks;
- accepted/fallback profile status semantics;
- core-check exit-code precedence;
- explicit diagnostic source labels (`rejected hand profile (diagnostic)`);
- accepted vs. declared-fallback profile statuses;
- accepted-profile loading and case-insensitive REJECTED checks;
- read-only hardware preflight and optional `--require-hardware` gate.
