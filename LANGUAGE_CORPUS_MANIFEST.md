# Held-Out Language Corpus Manifest

`scripts/language_corpus_manifest.py` validates the local boundary required by issue #24.
It does not read or publish reference text, steno outlines, coordinates, or identifiers.

Create a manifest next to the local files:

```json
{
  "schema": "touchsteno.language_corpus_manifest",
  "version": 1,
  "corpus_id": "p01-heldout",
  "consent": true,
  "split": "held_out",
  "reference_file": "reference.txt",
  "reference_sha256": "<sha256>",
  "event_log": "events.jsonl",
  "event_log_sha256": "<sha256>",
  "retention_until": "2099-01-01"
}
```

Both file paths must be relative to the manifest directory and must not escape it. The
validator verifies both SHA-256 hashes, explicit consent, held-out split status, retention
metadata, and the semantic event-log schema through `language_layer_metrics.py`.

```bash
python3 scripts/language_corpus_manifest.py messung/manifest.json --json
```

Output contains only schema/version, validity, event-log validity, and concise errors. It
never copies paths or file contents. A valid manifest proves local structure and consent
metadata only; it does not prove translation accuracy, human correction time, or WPM.
