# Layout Provenance Audit — 2026-09-29

## Finding

The current core contains a reproducibility/provenance inconsistency:

- `hand_profile.json` is explicitly marked `REJECTED — not a usable measurement, do not optimise from this file`.
- `layout.json` still has `geometry.source: "measured hand profile"` and embeds an older profile with reach 58 mm / fan 0–100° and a different index pitch/centre.
- Running the optimiser against the current repository inputs does not reproduce the committed layout byte-for-byte or metric-for-metric.

This does not prove the committed layout is wrong. It proves that the committed layout must not be described as a current result derived from an accepted measurement without an explicit historical label.

## Evidence

```text
python3 audit_layout_provenance.py
layout source : measured hand profile
profile status: REJECTED - not a usable measurement, do not optimise from this file
PROVENANCE WARNING: layout.json says 'measured hand profile', but hand_profile.json is REJECTED
PROVENANCE WARNING: embedded profile status differs from current hand_profile.json
PROVENANCE WARNING: embedded profile provenance differs from current hand_profile.json
```

The default and profile-explicit optimiser runs both completed successfully, but produced different objective/throughput values and different assignments than the committed `layout.json`. The differences are expected when the geometry inputs differ, and the provenance mismatch is the actionable issue.

## Interpretation

- The optimiser self-test and the synthetic hand-reader self-test still pass.
- No PTH-660 session was performed in this audit.
- The current model WPM is not a measured typing speed.
- A rejected profile must not silently become a “measured” input to a future layout run.

## Guard added after the audit

The optimiser now refuses a profile whose JSON status starts with `REJECTED`:

```bash
python3 layout_optimizer.py --hand-profile hand_profile.json
# exits non-zero and prints the rejection reason
```

A deliberately labelled diagnostic run is possible only with:

```bash
python3 layout_optimizer.py --hand-profile hand_profile.json \
  --allow-rejected-profile --out diagnostic-layout.json
```

That run labels `geometry.source` as `rejected hand profile (diagnostic)`, not as a measured profile. The ROM self-test also routes through the same safe loader.


1. Re-run the guided ROM capture with the heel of the hand off the pad, only the measured digit/index touching, and no movement during the settling and still phases.
2. Verify the new profile is accepted by `rom_capture.py`; retain the rejected file as an archive with its reason.
3. Regenerate `layout.json` with the accepted profile and an explicit commit of the input profile hash.
4. Add `--strict` provenance check to the release/CI gate:

```bash
python3 audit_layout_provenance.py --strict
```

5. Keep the historical layout under an archive name or annotate it with its source commit; do not silently overwrite it.

The audit script is intentionally conservative: it reports the mismatch without modifying the layout, because choosing a replacement layout requires an accepted physical measurement and a research decision.
