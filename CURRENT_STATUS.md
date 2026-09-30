# Current Research Status — 2026-09-30

## What is now solid

- The repository has a reproducible, offline self-test for the layout optimiser.
- The hand reader has MT-protocol-B slot isolation, axis-order safety, palm-span safety and step-boundary flushing.
- Rejected hand profiles are refused by both `load_profile()` and `apply_profile()`.
- Diagnostic runs require an explicit non-measurement source label.
- A single runner reports technical failures separately from stale provenance.

## Current blocking evidence gap

There is still no accepted live PTH-660 hand recording. The committed `hand_profile.json` is deliberately `REJECTED`, and the historical `layout.json` must not be presented as a current measured result. A new ROM capture must satisfy the still-phase and contact-lifecycle gates before it can feed the optimiser.

## Next concrete task

Run `rom_capture.py --device ...` with only the thumb/index touching and the heel off the pad, then retain the raw JSONL, diagnostic output, profile status and provenance audit together. Do not overwrite the historical layout until the new profile is accepted.
