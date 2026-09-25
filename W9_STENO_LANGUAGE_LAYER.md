# W9 — Steno Language Layer: Dictionaries, Briefs, Errors, Plover Pipeline

> Method note: `websearch` integration returned `No search results found` for all queries
> (`steno dictionary size`, `plover`, `stenography`, etc.) on 2026-09-25.
> All numbers below were obtained via direct `webfetch` of primary docs/repos/Wikipedia/NCRA/Guinness.
> Rule enforced: ONLY numbers literally seen in a fetched source are reported, each with its source URL.
> Everything else is explicitly marked NOT FOUND. No guessing.

Claim under test (prompt): verified court reporter 360 WPM / 97.2% accuracy from ~100,000 memorized short forms, not faster fingers.
Verified adjacent fact: Guinness lists Mark Kislingbury, Houston Texas, 30 July 2004, 360 WPM with 97.23% accuracy
(see §3 table). The "~100,000 short forms" figure itself was NOT FOUND in any fetched source.

---

## 1. Steno dictionaries: size, hit-rate, coverage

### 1a. Dictionary size — measured numbers found

| item | number | unit | source URL | relevance |
|---|---|---|---|---|
| Plover bundled English dictionary size | over 150 thousand | entries | https://www.artofchording.com/introduction/theories-and-dictionaries.html | Only exact bundled-dict entry count found; "in order to cover most of the English language" |
| Plover claim: write speed enabled | over 200 | WPM | https://plover.readthedocs.io/en/latest/index.html | Ceiling the stock dictionary+engine is documented for |
| Open Steno claim: court reporters write | over 200 | WPM | https://opensteno.org/ | Same ceiling claim from project homepage |
| RPR certification legs | 180 / 200 / 225 | WPM (Literary / Jury Charge / Testimony-Q&A, 5-min each) | https://www.ncra.org/certification/NCRA-Certifications/registered-professional-reporter | Defines what "real dictation coverage" must sustain |
| RPR pass threshold | 95 | % accuracy each leg | https://www.ncra.org/certification/NCRA-Certifications/registered-professional-reporter | Accuracy floor for certified dictation |
| RPR transcription limits | 3 / 75 | min (attach notes / transcribe after dictation) | https://www.ncra.org/certification/NCRA-Certifications/registered-professional-reporter | Correction workflow is offline + time-boxed, not live-typed |
| RPR Written Knowledge Test | 120 items (100 scored), 110 min, scaled 70 to pass | items/min/score | https://www.ncra.org/certification/NCRA-Certifications/registered-professional-reporter | Language-knowledge bar, not speed |
| NAIT (Canada, NCRA-approved) diploma speeds | 225 | WPM two-voice, 95% accuracy | https://en.wikipedia.org/wiki/Court_reporter | Independent confirmation of 225 WPM / 95% pair |
| BC Official Reporter designation | 200+ | WPM shorthand | https://en.wikipedia.org/wiki/Court_reporter | Lower-bound professional bar |
| US licensing exams (general) | 180 / 200 / 225 | WPM | https://en.wikipedia.org/wiki/Court_reporter | Same triple as NCRA |
| US training time, basic skills | 2 to 4 | years | https://en.wikipedia.org/wiki/Court_reporter | Language-layer learning cost; fingers are the fast part to learn, dictionary mastery is not |
| Stenotype paper columns | 22 | columns, order `STKPWHRAO*EUFRPBLGTSDZ` | https://en.wikipedia.org/wiki/Stenotype | Fixed key inventory the dictionary must compress language onto |
| Top cited human max (COCRA via Wikipedia) | up to 375 | WPM | https://en.wikipedia.org/wiki/Stenotype | Upper bound cited for steno; no hit-rate attached |
| Guinness fastest realtime (Kislingbury) | 360 | WPM | https://www.guinnessworldrecords.com/world-records/fastest-realtime-court-reporter-%28stenotype-writing%29 | Anchors the 360 claim in prompt (97.23% — see §3) |
| Court-reporter learning curve cited | 10 to 15-year-old machines still resold $350+; student ~$1500, top ~$5000 (Oct 2013) | USD | https://en.wikipedia.org/wiki/Stenotype | Economic context only; not language gain |

### 1b. Hit-rate / coverage fraction — NOT FOUND

| item | number | unit | source URL | relevance |
|---|---|---|---|---|
| Main-dictionary hit rate in live dictation | NOT FOUND | — | — | No fetched source gives % of words resolved by main dict |
| Personal-briefs/outlines hit rate | NOT FOUND | — | — | No fetched source gives % from personal/job dictionaries |
| Fraction of words from each dictionary layer | NOT FOUND | — | — | No fetched source partitions output by dictionary priority |
| Measured dictionary coverage on a dictation corpus (OOV/untran rate) | NOT FOUND | — | — | Plover docs define `untranslate/untran` but give no corpus rate; see Plover §4 |
| Professional personal dictionary size (entries) | NOT FOUND | — | — | "~100,000 short forms" from prompt NOT FOUND in any fetched source |
| Stock commercial theory dictionary size (StenEd/Phoenix/Magnum entries) | NOT FOUND | — | — | Vendors named but no entry counts fetched |

What *is* documented about layering (no numbers): Plover translator searches a **dictionary stack in descending priority**, longest-outline-first; longest searchable span = longest entry across all dicts in stack; first hit wins; no conflicts (see §4). Source: https://plover.readthedocs.io/en/latest/design.html

---

## 2. Briefs and outlines: mechanism, speed gain, published measurement

Mechanism (sourced, non-numeric):

- A *theory* = rules mapping chords to sounds/words (e.g. how "thought" is stroked); a *dictionary* = computer file implementing a theory. Source: https://www.artofchording.com/introduction/theories-and-dictionaries.html
- Theories span stroke-intensive (Phoenix: phonetic, easier, more strokes) → memory-intensive (Magnum Steno / Stanley's personal dict: less movement, more mental effort) → middle (StenEd: phonetic base + shortcuts for most common words/phrases). Plover theory rooted in StenEd, leaning memory-intensive, 100% free. Source: https://www.artofchording.com/introduction/theories-and-dictionaries.html
- Historically reporters invented briefs on the fly and mixed theories (hurting readability by others); current theories are designed for CAT translation via a standardized vendor dictionary, forcing one theory + vendor combos, plus students/reporters add significant personal entries/briefs. Source: https://en.wikipedia.org/wiki/Stenotype
- Example compressions on steno paper: `this/of/from` → `th/f/fr`; `machine/shorthand` → `mn/shand`. Source: https://en.wikipedia.org/wiki/Stenotype

| item | number | unit | source URL | relevance |
|---|---|---|---|---|
| Speed gain with vs without briefs/outlines | NOT FOUND | — | — | No fetched source publishes an A/B WPM delta |
| Strokes-saved per brief / outline-length distribution | NOT FOUND | — | — | No fetched source gives strokes-per-word with/without |
| Phrase outlines (multi-word single-stroke) frequency effect | NOT FOUND | — | — | Described qualitatively only |
| Optimal brief count vs recall tradeoff curve | NOT FOUND | — | — | Only qualitative: memory-intensive = less movement at cost of mental effort (Art of Chording URL above) |
| Time to learn briefs to reach 180/200/225 WPM | NOT FOUND as brief-specific number | — | — | Only whole-skill number exists: 2–4 years basic skills — https://en.wikipedia.org/wiki/Court_reporter |

---

## 3. Steno error rates, correction, WPM-vs-accuracy

### 3a. Measured / threshold numbers found

| item | number | unit | source URL | relevance |
|---|---|---|---|---|
| Guinness record accuracy (Kislingbury, 2004) | 97.23 | % at 360 WPM | https://www.guinnessworldrecords.com/world-records/fastest-realtime-court-reporter-%28stenotype-writing%29 | Only jointly-measured WPM+accuracy point found; matches prompt's "97.2%" to 2 decimals |
| RPR pass accuracy | 95 | % per leg (180/200/225 WPM) | https://www.ncra.org/certification/NCRA-Certifications/registered-professional-reporter | Certification error budget: 5% per 5-min leg |
| NAIT diploma accuracy | 95 | % at 225 WPM two-voice | https://en.wikipedia.org/wiki/Court_reporter | Same 95% floor, Canadian program |
| RPR speed triple | 180 / 200 / 225 | WPM | https://www.ncra.org/certification/NCRA-Certifications/registered-professional-reporter | The only standardized WPM ladder found |
| RPR correction window | 75 (+3 attach) | min post-dictation edit | https://www.ncra.org/certification/NCRA-Certifications/registered-professional-reporter | Pro correction is post-hoc transcription, not live re-stroke |
| Plover translator stroke buffer | 100 | strokes (default) | https://plover.readthedocs.io/en/latest/design.html | Window within which undo/retrospective commands can operate |
| Plover undo macro | `=undo` (plus `=retro_toggle_asterisk`) | macro names | https://plover.readthedocs.io/en/latest/design.html | Live correction primitive: removes/modifies most recent stroke |
| Plover steno-paper order (error-domain width) | 22 | keys `STKPWHRAO*EUFRPBLGTSDZ` | https://en.wikipedia.org/wiki/Stenotype | Every mistroke lands inside this alphabet; conflicts resolved by dictionary priority, not N-best |

### 3b. Correction methods (sourced qualitatively; rates NOT FOUND)

- Live: `*` (asterisk) undo stroke / `=undo` macro; retrospective add-asterisk `=retro_toggle_asterisk`. Source: https://plover.readthedocs.io/en/latest/design.html
- Post-hoc: CAT edit + scopist/proofreader pass; realtime CAT output increases demand for simultaneous scopists; CAT software converts steno→text via dictionary so scopist needs no shorthand-theory knowledge; misstroked words appear as untranslated steno. Source: https://en.wikipedia.org/wiki/Stenotype
- RPR model: attach notes (3 min) → transcribe/edit (75 min) → submit. Source: NCRA URL above.
- Audio correction / "katas" as named steno drills: NOT FOUND in any fetched source (term "kata" does not appear in Plover docs or fetched pages).

| item | number | unit | source URL | relevance |
|---|---|---|---|---|
| Live undo rate (undos per 100 strokes) | NOT FOUND | — | — | No fetched source logs `*` frequency in dictation |
| Untranslated-outline (untran) rate | NOT FOUND | — | — | Concept defined (https://plover.readthedocs.io/en/latest/design.html) but no corpus % found |
| Mistranslate (wrong-word, silent) rate vs untran rate | NOT FOUND | — | — | No fetched confusion-matrix data |
| Scopist edit rate / post-edit WER reduction | NOT FOUND | — | — | Described as role only |
| Audio-backup correction usage rate | NOT FOUND | — | — | Mentioned only as recorder workflow, no rate |
| WPM-vs-accuracy tradeoff curve (slope) | NOT FOUND | — | — | Only two points exist (95% @ 180–225; 97.23% @ 360 record) — not a curve; do not interpolate |
| Dictation word-error-rate on broadcast/court test sets | NOT FOUND | — | — | No fetched benchmark |

---

## 4. Plover specifically: formats, build, translator pipeline, performance/limits

### 4a. Dictionary formats — what exists (sourced)

Plover doc page: https://plover.readthedocs.io/en/latest/dict_formats.html

| item | number | unit | source URL | relevance |
|---|---|---|---|---|
| JSON dictionary — most common Plover format; `{ "KAT": "cat", "KAT/HROG": "catalog", ... }`, outline keys in canonical steno notation strokes separated by `/`, values in Plover translation language | n/a (format) | — | https://plover.readthedocs.io/en/latest/dict_formats.html | Default authoring/storage format; matches internal storage almost exactly |
| RTF/CRE dictionary — interchange format (`{\rtf1\ansi\cxrev100\cxdict {\*\cxs KAT}cat ...}`); Plover reads subset; entry metadata (comments, usage history) NOT readable by Plover; slow to parse, not recommended for maintenance | n/a (format) | — | https://plover.readthedocs.io/en/latest/dict_formats.html | Bridge for pro personal dictionaries; known perf caveat |
| Proprietary native formats via plugins: `.sgdct` (Case CATalyst), `.dct` (digitalCAT), `.dix` (Eclipse) | 3 plugin packages | — | https://plover.readthedocs.io/en/latest/dict_formats.html + plugin repos `plover-casecat-dictionary`, `plover-digitalcat-dictionary`, `plover-eclipse-dictionary` (github.com/marnanel/...) | Import path for commercial personal briefs |
| Programmatic (Python) dictionaries via `plover-python-dictionary` plugin: required `LONGEST_KEY: int`, required `lookup(outline: Tuple[str]) -> str` (raise KeyError if none), optional `reverse_lookup(translation) -> List[Tuple[str]]` | 1 / 1 / 0-1 | required attrs/funcs | https://plover.readthedocs.io/en/latest/dict_formats.html | For regular systems (symbols, syllabic theory); computes on the fly |
| `.dict` / `.ctdict` / `.dict.gz` as Plover formats | NOT FOUND | — | https://plover.readthedocs.io/en/latest/dict_formats.html | Those extensions are NOT listed in Plover docs; do not claim Plover support. Plover extensions seen: `.json`, `.rtf` (by extension sniffing) + `.py` via plugin |
| Dictionary detection rule | file extension | — | https://plover.readthedocs.io/en/latest/design.html (`main.json` → JSON, `main.rtf` → RTF/CRE) | How loaders are selected |
| Bundled dictionary size | over 150 thousand (see §1) | entries | https://www.artofchording.com/introduction/theories-and-dictionaries.html | Scale the lookup path must handle |

### 4b. How dictionaries are built / managed (sourced)

- Dictionaries loaded at startup in user-config order; format by extension. Source: https://plover.readthedocs.io/en/latest/design.html
- Dictionary stack = list in descending priority; lookup tries topmost first, then down. Source: https://plover.readthedocs.io/en/latest/design.html
- Longest-first outline search: longest possible stroke run first, then N−1, …, down to last stroke; bound = longest entry across whole stack. Source: https://plover.readthedocs.io/en/latest/design.html
- Loader requirements: outlines→exactly one translation in Plover translation language; valid steno notation for active system; translation = exactly one macro OR sequence of non-macro actions; longest key known+fixed. Source: https://plover.readthedocs.io/en/latest/design.html
- No-conflict rule: each outline has exactly one translation; higher-priority entry overrides (not augments) lower ones; some CAT systems allow conflicts, Plover does not. Source: https://plover.readthedocs.io/en/latest/design.html
- Reverse lookup (Lookup tool, Suggestions): dictionaries expose `reverse` / `casereverse` maps; programmatic dicts optionally implement `reverse_lookup`. Sources: https://plover.readthedocs.io/en/latest/api/steno_dictionary.html and https://plover.readthedocs.io/en/latest/dict_formats.html
- User tooling: Add Translation / Dictionary Editor / Translation Language (`{^s}`, `{^}`, casing, orthography, metas). Sources: https://plover.readthedocs.io/en/latest/dictionaries.html and https://plover.readthedocs.io/en/latest/translation_language.html (index listing)
- System definition (theories as code): designing-steno-systems guide + `plover.system` API. Sources: https://plover.readthedocs.io/en/latest/system_dev.html and https://plover.readthedocs.io/en/latest/api/system.html

### 4c. Translator pipeline — concrete modules/files (sourced)

Top-level design: https://plover.readthedocs.io/en/latest/design.html — four phases: **capture → translation → formatting → rendering**, engine wires them; UI separate.

| stage | concrete file / class / symbol | source URL |
|---|---|---|
| Capture: machine plugins (Keyboard HID / Serial UART steno writers); physical→logical steno keys per active `system` | `plover.machine.*`, `plover.machine.keyboard_capture`, `plover.machine.keymap`; `plover.system`; hardware comms doc | https://plover.readthedocs.io/en/latest/design.html, https://plover.readthedocs.io/en/latest/api/engine.html, https://plover.readthedocs.io/en/latest/hardware_communication.html |
| Translation: `Translator` consumes strokes, buffer lookup, macros | `plover/translation.py` : `Translator` (`translate`, `translate_stroke`, `translate_macro`, `translate_translation`, `untranslate_translation`, `lookup`, `set_dictionary/get_dictionary`, `set_min_undo_length`, `flush`, `get_state/set_state/clear_state`), `Translation` (`strokes/rtfcre/english/replaced/formatting/is_retrospective_command/has_undo`), `Macro(name/stroke/cmdline)` | https://plover.readthedocs.io/en/latest/api/translation.html and https://github.com/openstenoproject/plover/blob/main/plover/translation.py |
| Dictionaries: single + collection, priority, filters, longest-key | `plover/steno_dictionary.py` : `StenoDictionary` (`load/save/create`, `__getitem__/__setitem__/__delitem__/__contains__/get`, `reverse/casereverse/reverse_lookup/casereverse_lookup`, `longest_key`, `_load/_save`, `enabled/readonly/timestamp/path`), `StenoDictionaryCollection` (`dicts/set_dicts/first_writable/set/save`, `lookup/raw_lookup/lookup_from_all/raw_lookup_from_all/reverse_lookup/casereverse_lookup`, `filters/add_filter/remove_filter`, `longest_key`) | https://plover.readthedocs.io/en/latest/api/steno_dictionary.html |
| Data model: stroke/outline, RTF/CRE notation, normalization | `plover/steno.py` : `Stroke` (`steno_keys/rtfcre/is_correction/normalize_stroke/normalize_steno/steno_to_sort_key`), `normalize_stroke/normalize_steno/sort_steno_strokes`; `plover_stroke.BaseStroke` | https://plover.readthedocs.io/en/latest/api/steno.html |
| Formatting: actions (text/backspaces/key-combos + state: caps/spacing), metas, orthography | `plover/formatting.py` (`Action`), `plover/orthography.py`, metas/commands/macros plugin docs | https://plover.readthedocs.io/en/latest/api/formatting.html, https://plover.readthedocs.io/en/latest/api/orthography.html, https://plover.readthedocs.io/en/latest/design.html |
| Rendering: engine commands vs OS keystroke output, minimal diff (`cat`→`catalog` = +4 chars, not delete+retype); key-combos not undoable | `plover/output.py`, `plover/oslayer/*` (`keyboardcontrol`, `controller`, `wmctrl`), `plover/key_combo.py` | https://plover.readthedocs.io/en/latest/design.html, https://plover.readthedocs.io/en/latest/api/output.html |
| Engine wiring + hooks | `plover/engine.py` : `StenoEngine` (`hook_connect`), hooks (`stroked`, disconnects, config changes) | https://plover.readthedocs.io/en/latest/api/engine.html and https://plover.readthedocs.io/en/latest/design.html |
| Config / resources / registry / suggestions | `plover/config.py`, `plover/resource.py`, `plover/registry.py`, `plover/suggestions.py`, `plover/gui_qt/*`, `plover_stroke`, `plover_python_dictionary_lib` | https://plover.readthedocs.io/en/latest/index.html (API index) |
| Repo root (versioned source of all above) | `github.com/openstenoproject/plover` (`plover/`, `test/`, `doc/`, `linux/`, `windows/`, `osx/`) — 2.6k stars / 306 forks at fetch time; GPLv2+ since 3.1.0 | https://github.com/openstenoproject/plover |

Control-flow recap (design doc): strokes → translator buffer (100 default) → longest-first stack lookup → macro (mutate buffer) or formatting ops → formatter (actions + state) → renderer (commands run on engine; text via OS keystrokes) → undo via `*` reverts insertions/deletions. Unmatched outline → `untranslate/untran` signal to add an entry or fix stroking. Source: https://plover.readthedocs.io/en/latest/design.html

### 4d. Measured performance / known accuracy limitations

| item | number | unit | source URL | relevance |
|---|---|---|---|---|
| Translator throughput / lookup latency benchmark | NOT FOUND | — | — | No timing numbers in fetched docs; only qualitative "RTF can be slow to parse" |
| End-to-end WPM benchmark of Plover engine | NOT FOUND | — | — | Only capability claim "over 200 WPM and beyond" (https://github.com/openstenoproject/plover) / "over 200 WPM" (https://plover.readthedocs.io/en/latest/index.html) — not a measurement |
| Translation accuracy / WER on a test set | NOT FOUND | — | — | No published Plover accuracy number fetched |
| Known limitation: single translation per outline (no conflicts) | 1 | translation/outline | https://plover.readthedocs.io/en/latest/design.html | Caps language-model expressiveness vs CAT systems with conflict stacks |
| Known limitation: RTF dictionaries slow to parse / ill-defined | qualitative | — | https://plover.readthedocs.io/en/latest/dict_formats.html | Real perf trap when importing pro dictionaries |
| Known limitation: RTF entry metadata (comments, usage history) unreadable | qualitative | — | https://plover.readthedocs.io/en/latest/dict_formats.html | Loses frequency priors that could rank suggestions |
| Known limitation: undo cannot revert key-combinations | qualitative | — | https://plover.readthedocs.io/en/latest/design.html | Some macros/commands are one-way |
| Known limitation: translation must be exactly-one-macro OR non-macro sequence | qualitative | — | https://plover.readthedocs.io/en/latest/design.html | Constrains dictionary authoring |
| Dictionary build/validation perf, `test/` coverage numbers | NOT FOUND | — | https://github.com/openstenoproject/plover (lists `test/` but no figures fetched) | Would need local `pytest` run, out of scope for this fetch-only pass |

---

## 5. What would we have to build (40 → 150+ WPM, language side only)

Ranked by expected WPM gain per effort. Assumes fingers/chording already sustain ~40 WPM and the bottleneck is strokes-per-word + misses + corrections.

1. **Top-2000 frequency briefs + phrase outlines (biggest lever).** Ship a layered personal dictionary: 1-stroke briefs for the most common words and 1-stroke multi-word phrases (`New York Times`-class: `TPHU/KWRORBG/TAOEUPLS` is 3 strokes today — see https://plover.readthedocs.io/en/latest/api/steno.html). Priority above stock dict so longest-first + top-priority wins (mechanism: https://plover.readthedocs.io/en/latest/design.html). Expected: converts 2–4-stroke common items to 1 stroke; this is the entire pro speed story (StenEd middle-ground = phonetic base + common-word shortcuts; Magnum = harder/more-text-per-move — https://www.artofchording.com/introduction/theories-and-dictionaries.html). Measure: strokes/word and untran rate before/after on fixed corpus.
2. **Kill untranslates on the target domain (coverage pass).** Log every `untranslate/untran` (defined: https://plover.readthedocs.io/en/latest/design.html), sort by frequency on the actual dictation domain, add entries until OOV rate < threshold. Expected: each untran currently costs a stop-spell-restroke cycle; domain jobs (legal/medical/captioning) concentrate misses. Plover's bundled 150k+ covers general English (https://www.artofchording.com/introduction/theories-and-dictionaries.html) but not jargon — that gap is where 40→80 lives.
3. **Orthography + suffix folding discipline.** Route all inflections through suffix keys + `plover/orthography.py` rules instead of separate entries (e.g. `-S` → `{^s}` pattern from https://plover.readthedocs.io/en/latest/dict_formats.html). Expected: fewer outlines to memorize, fewer misstrokes on endings, smaller effective dictionary to master vs the 2–4-year whole-skill cost (https://en.wikipedia.org/wiki/Court_reporter).
4. **Conflict-free prefix design (work around Plover's 1-translation limit).** Because Plover overrides rather than stacking same-outline translations (https://plover.readthedocs.io/en/latest/design.html), reserve outline namespaces per layer (stock < theory-briefs < job-briefs < user-briefs) and lint collisions in CI. Expected: eliminates silent wrong-word substitutions, the most expensive error class (no number available — hence lint, not tuning).
5. **Retrospective-correction fluency (`*`, `=undo`, `=retro_toggle_asterisk`).** Train undo-last-stroke and asterisk-fix as reflex inside the 100-stroke buffer window (https://plover.readthedocs.io/en/latest/design.html). Expected: converts errors from full-word restrokes to single-gesture repairs.
6. **Offline scopist loop modeled on RPR (3-min attach + 75-min transcribe at 95% bar).** Record steno notes + audio; scope after, not during; track % to 95%-per-5-min-leg (https://www.ncra.org/certification/NCRA-Certifications/registered-professional-reporter). Expected: separates speed practice (no stopping) from accuracy practice (deliberate edit), mirroring how certification is actually structured.
7. **Import, don't hand-build: RTF/CRE + `.sgdct`/`.dct`/`.dix` pro dictionaries.** Use the three plugins + RTF path (https://plover.readthedocs.io/en/latest/dict_formats.html) to inherit years of brief engineering; pre-convert RTF to JSON at build time to avoid the documented slow-parse path. Expected: shortcut to pro brief coverage without re-deriving theory.
8. **Programmatic dictionaries for regular classes (numbers, symbols, affixes).** Implement `LONGEST_KEY` + `lookup` (+optional `reverse_lookup`) via `plover-python-dictionary` (https://plover.readthedocs.io/en/latest/dict_formats.html) instead of enumerating entries. Expected: infinite regular coverage at zero memorization; keeps JSON layer for irregulars only.
9. **Lookup/suggestion instrumentation (close the measurement gap).** Emit per-stroke: stack depth hit, outline length, untran flag, undo flag; report strokes/word, untran %, undo %, WPM @ estimated accuracy. Expected: no public numbers exist for hit-rate/undo-rate (see NOT FOUND rows) — first local dashboard turns language work from lore into hill-climbing toward 150+.
10. **Benchmark against the only fixed ladder available (180/200/225 @ 95%).** Use RPR legs as regression tests long before chasing 360 @ 97.23% (https://www.guinnessworldrecords.com/world-records/fastest-realtime-court-reporter-%28stenotype-writing%29). Expected: 150 WPM is 83% of the 180 literary leg — a coverage+briefs problem, not a finger-speed problem, consistent with the prompt's thesis.

What NOT to build first: a faster key detector, N-key/ergonomic hardware swaps, or a neural post-corrector — all lose to one more brief layer and one fewer untran per minute at the 40→150 stage.

---
*Sources fetched 2026-09-25. Where a number appears, its URL is in-row. Where it says NOT FOUND, no fetched source contained it and no value is asserted.*
