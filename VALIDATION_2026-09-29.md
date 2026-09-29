# Validation Snapshot — 2026-09-29 14:51 CEST

After synchronising with the current `origin/main` (commit `7bc0e90`), the core tools were executed again.

## Commands and results

```text
python3 layout_optimizer.py --self-test   -> 0 failure(s), 20 invariants PASS
python3 rom_capture.py --self-test        -> 0 failure(s), synthetic evdev PASS
python3 -m unittest discover -s tests -v  -> 30 tests, OK
```

`pytest` is not installed in the environment (`No module named pytest`), so the unittest runner was used.

## What this does and does not establish

- The layout optimiser invariants, deterministic delta evaluation, annealing baseline comparison and layout bijection checks pass in this environment.
- The hand-reader synthetic evdev path, contact lifecycle, palm rejection, phase separation, reach handling and profile round-trip pass.
- The untracked RCI test file is present locally from the parallel research worker and is **not** part of this commit; it was not modified or claimed as Agent-1 work.
- No live PTH-660 measurement was run. The environment still has no connected tablet event node in this iteration.
- The optimiser's WPM output remains a model output, not a measured typing speed. The README's warning remains valid.
