# Bimanual Coupling Analysis

`scripts/bimanual_coupling.py` is the offline analyzer for the cued bimanual capture. It
consumes the raw recorder JSONL and its sibling `.manifest.jsonl` file:

```bash
python3 scripts/bimanual_coupling.py messung/bimanual-coupling.jsonl --json
```

The analyzer is deliberately raw. It does not run intent suppression, select a dominant
mover, fit anatomical identity, or transfer a model across sessions.

## Identity boundary

A tracking ID is scoped to one contact episode:

```text
session_id :: tracking_id :: episode_index
```

A disappearance followed by reappearance creates a new episode even if the numeric ID is
reused. The report always contains:

```json
"identity": {
  "status": "unverified",
  "anatomical_labels_emitted": false
}
```

For an alternating cue, an onset may carry `associated_cued_side`; this is the instructed
side, not proof of the contact's anatomy. Simultaneous onsets remain unordered and their
individual side is `null`.

## Measurements

Per block:

- valid cue cycles and realized cycle rate;
- raw new-contact onset count/rate;
- per-cue onset latency relative to expected cue times;
- adjacent alternating-cue interval spread, stratified by cued direction;
- simultaneous onset absolute and ordinal timing error;
- raw pair lag/correlation profiles with overlap counts.

Raw trajectories retain decoded samples and contact-episode keys. Pair statistics require at
least 40 overlapping consecutive step samples; insufficient or constant data produce `null`
with a reason rather than a fabricated zero.

`simultaneous_onset_error_s` is a descriptive timing measure. It is not a pass/fail
synchronization threshold. No result is a PTH-660 performance, WPM, pressure, anatomy, or
cross-session identity claim.
