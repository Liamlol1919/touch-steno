# Language-Layer Metrics

`scripts/language_layer_metrics.py` aggregates a local, privacy-minimized JSONL event log.
It is an offline counter, not a Plover integration and not a text-accuracy benchmark.

## Input

One event per nonblank line:

```json
{"event":"stroke"}
{"event":"untranslate"}
{"event":"undo"}
{"event":"word","delta":1}
{"event":"word","delta":-1}
```

- `stroke`: one accepted language-layer stroke, including correction strokes.
- `untranslate`: one actual translator fallback/dictionary miss, not an internal failed prefix lookup.
- `undo`: one executed user correction command.
- `word`: signed output-word delta; phrase outlines emit one delta per output word.

Unknown fields and privacy-sensitive fields (`text`, `outline`, `coordinates`, `session`,
`user_id`, timestamps, and correction durations) are rejected. Start each log at a clean
session boundary; a removal before an addition is invalid.

```bash
python3 scripts/language_layer_metrics.py events.jsonl \
  --out language-layer-metrics.json
```

`scripts/language_event_recorder.py` is the small local producer boundary. A future Plover
hook adapter may call `stroke()`, `untranslate()`, `undo()`, and `word(delta)`; the recorder
does not import Plover and accepts no text, outline, timestamp, coordinate, or identifier.

## Output and limits

The aggregate report contains:

- input strokes;
- untranslate and undo events per 100 strokes;
- word additions/removals/final words;
- strokes per final word, including correction overhead;
- explicit privacy and scope flags.

Empty denominators are `null`; they are never fabricated as zero efficiency. The report does
not contain source paths, text, outlines, coordinates, identifiers, or per-event details.

These are local event counts, not human correction time, Plover performance, accuracy, or WPM.
Use `correction_throughput.py` for seconds per correction. Use a separate held-out reference
corpus for translation/CER/WER. No public baseline or speed gain is implied.
