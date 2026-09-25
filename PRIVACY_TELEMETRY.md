# Privacy-Safe Telemetry

Raw PTH-660 contact traces are per-user biometric data. They are not committed to this
repository. Telemetry is a separate, opt-in aggregate export intended for reproducible
threshold discussions.

## Default export contract

`scripts/telemetry_export.py` emits one object with:

- schema `touchsteno.telemetry`, version 1;
- aggregate frame counts and timing summaries;
- pooled REST/MOVER contact-group summaries;
- raw-frame schema/version provenance;
- privacy flags stating that coordinates, contact IDs, session names, user IDs and text
  content are absent.

The exporter never copies raw frames or per-contact identifiers. It does not provide a
raw-data switch; raw JSONL remains a separately controlled artifact.

```bash
python3 scripts/telemetry_export.py session.jsonl [more.jsonl ...] \
  --consent --out telemetry.json
```

The explicit `--consent` flag is required; without it the CLI refuses to export.

## Consent and retention

- Obtain explicit consent before recording or exporting telemetry.
- Store raw traces and aggregate exports separately with restricted access.
- Use pseudonymous session labels only; do not put user names in filenames or metadata.
- Set a deletion date for raw traces and derived telemetry.
- Do not upload raw traces to issues, pull requests or public telemetry artifacts.
- A public report should cite aggregate schema/version and measurement provenance, not
  session names or contact-level records.

The exporter is a technical boundary, not legal advice or a substitute for a local privacy
review.
