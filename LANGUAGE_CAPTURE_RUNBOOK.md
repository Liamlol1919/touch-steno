# Language Capture Runbook

This runbook is the operator procedure for issue #24. It does not claim that a capture has
already happened and it does not contain reference text or event data.

## 1. Consent and local setup

1. Obtain and record explicit consent for recording the local language session.
2. Create a restricted local directory outside the repository, for example `messung-private/`.
3. Keep the held-out reference text and semantic event log in separate local files.
4. Use a pseudonymous `corpus_id`; do not put a user name in filenames or metadata.
5. Set `retention_until` before capture.

## 2. Capture

1. Install and configure a Plover hook adapter that calls `plover_event_adapter.py` at the
   semantic translator boundary. Do not log Stroke/Translation objects, text, outlines, or
   timestamps.
2. Use `language_event_recorder.py` to write only the four permitted event types.
3. Start from a clean output state; do not append to an existing event log.
4. Keep the reference text separate from the event log. Record the exact corpus split as
   `held_out`.

The adapter is a callback boundary only; this repository does not install or claim a
working Plover plugin.

## 3. Validate locally

```bash
python3 scripts/language_corpus_manifest.py messung-private/manifest.json --json
python3 scripts/language_layer_metrics.py messung-private/events.jsonl \
  --out messung-private/language-metrics.json
```

The first command validates consent, split, relative paths, hashes, retention, and event-log
schema. The second reports only aggregate event counts/rates. Neither command publishes raw
content or derives WPM.

## 4. Separate translation evaluation

Keep the reference text local and access-controlled. Run any translation/CER/WER evaluation
as a separate, explicitly labelled analysis. Do not combine that accuracy result with event
counts or human repair time. Use `correction_throughput.py` only for a separately consented
human timing observation.

## 5. Retention and deletion

```bash
python3 scripts/language_corpus_retention.py messung-private/manifest.json \
  --today YYYY-MM-DD --json
```

`retain` means the retention date has not arrived. `deleted` means the retention date has
arrived and both local files are absent. `overdue` means the date has arrived but files
remain. The helper never deletes files. After explicit operator deletion, retain the
manifest/deletion record according to the local privacy policy; do not commit raw data.
