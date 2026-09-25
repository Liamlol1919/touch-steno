# Plover Brief Validation

`scripts/plover_dictionary_check.py` validates layered Plover JSON dictionaries before
they enter a user configuration. It does not translate text and does not claim a speed
improvement.

```bash
python3 scripts/plover_dictionary_check.py \
  main.json theory-briefs.json user-briefs.json \
  --out dictionary-check.json
```

The checker reports:

- duplicate JSON keys (which standard JSON parsers may silently overwrite);
- invalid steno outlines;
- empty/non-string translations;
- the same outline appearing in multiple dictionary layers;
- entry count and layer files.

Plover resolves dictionary layers by priority and uses longest-first outline lookup. A
collision is therefore a data-quality failure, not a harmless duplicate: the checker exits
non-zero and leaves the source dictionaries unchanged.

The checker is intentionally format validation only. Import, theory design, and speed gains
require separate measurements. Runtime untranslate/undo counts are handled separately by
[`scripts/language_layer_metrics.py`](LANGUAGE_LAYER_METRICS.md); that tool does not measure
import time, accuracy, Plover performance, or WPM.
