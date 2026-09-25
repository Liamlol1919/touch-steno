# W3 — Reusable open-source code for a 0-force chorded touch-stenotype system on Linux (Wacom PTH-660, evdev multi-touch)

Date: 2026-09-25. Method: web search + direct repo-page reads (`webfetch`) on 2026-09-25.
**VERIFIED** = the repo page was read directly this session (name/URL/license-badge/readme confirmed).
**UNVERIFIED** = identified via search snippets / docs only; URL not invented but page not fully read — re-check before depending on it.
Last-activity: GitHub pages fetched as logged-out markdown did not expose commit dates in readable form, so exact
last-commit dates are mostly **not captured** below (marked "n/c"). Star/fork counts captured where visible.

Target pipeline for reference: `kernel evdev (Wacom PTH-660 touch) → slot/tracking-ID contact tracker → finger/chord
classifier → steno translator (Plover machine plugin or standalone) → uinput text injection → optional LM autocorrect`.

---

## 1. Touch / multi-touch gesture and chord recognition (Linux, Python/C++)

### 1.1 python-evdev — VERIFIED
- URL: https://github.com/gvalkov/python-evdev
- License: BSD-3-Clause (badge on repo page)
- Language: Python (C extension)
- What it is: Python bindings for the Linux input subsystem (`/dev/input/event*`), **including `evdev.UInput`** for emitting events.
- Pipeline use: **primary read path** for raw `ABS_MT_SLOT / ABS_MT_TRACKING_ID / ABS_MT_POSITION_X/Y` frames AND the
  **primary write path** (`UInput`) for injecting key/text events. Has PyPI package (`evdev`); ~390 stars / 125 forks.

### 1.2 libevdev (C) + python-libevdev — license VERIFIED via upstream docs, repo URLs UNVERIFIED
- URLs: https://gitlab.freedesktop.org/libevdev/libevdev and https://gitlab.freedesktop.org/libevdev/python-libevdev
  (move notice seen at https://github.com/whot/python-libevdev)
- License: MIT (stated on freedesktop libevdev docs and Homebrew formula; current stable ~1.13.7)
- Language: C (+ Python wrapper)
- What it is: Wrapper over evdev ioctls; normalizes quirks, exposes per-device/per-slot state, handles `SYN_DROPPED`
  resync, and can create uinput devices.
- Pipeline use: use instead of (or under) python-evdev if SYN_DROPPED/slot-state handling gets painful; the Python
  wrapper's docs explicitly cover slot state and fake-multitouch devices. PyPI package `libevdev` (pip install).

### 1.3 libinput — UNVERIFIED (URL from distro upstream metadata, page not read this session)
- URL: https://gitlab.freedesktop.org/libinput/libinput
- License: MIT (upstream states MIT; **UNVERIFIED** this session — confirm on page)
- Language: C
- What it is: Full input stack for Wayland/compositors: touchpad/touchscreen gesture state machines (swipe/pinch),
  tap-to-click, palm detection.
- Pipeline use: **reference, not reuse** — its swipe/pinch recognizers assume gesture (not static chord) semantics and
  it sits under the compositor; but read its gesture docs/source for debouncing, threshold, and touch-frame logic.
  Touchégg (1.6) consumes libinput gestures.

### 1.4 mtdev (Multitouch Protocol Translation Library) — VERIFIED
- URL: https://github.com/rydberg/mtdev (canonical site http://bitmath.org/code/mtdev/)
- License: MIT (README: "Multitouch Protocol Translation Library (MIT license)")
- Language: C
- What it is: Translates all kernel MT variants (type A w/o tracking, type A with tracking, type B) into slotted
  type-B protocol.
- Pipeline use: only needed if you ever target a type-A device; the PTH-660 is type-B, so this is a **fallback
  normalizer**. Kivy consumes it (1.7).

### 1.5 python-uinput — VERIFIED
- URL: https://github.com/tuomasjjrasanen/python-uinput (maintained fork https://github.com/pyinput/python-uinput exists — UNVERIFIED)
- License: GPL-3.0 (GPLv3+, README + badge)
- Language: Python (C extension over `libsuinput` bundled in-repo)
- What it is: "Pythonic API to Linux uinput module" — create virtual keyboards/mice/joysticks, `emit_click`/`emit_combo`.
- Pipeline use: alternative text-injection backend to `python-evdev.UInput`; pick ONE (recommend python-evdev to keep
  deps to one package). GPL-3.0 copyleft note if linked/redistributed.

### 1.6 linuxwacom: input-wacom (VERIFIED) + libwacom (VERIFIED) + xf86-input-wacom (UNVERIFIED)
- URLs: https://github.com/linuxwacom/input-wacom (VERIFIED, GPL-2.0 badge, C, kernel driver/backports),
  https://github.com/linuxwacom/libwacom (VERIFIED, C, tablet-description database library; SPDX not confirmed from
  fetched text — treat as UNVERIFIED, historically MIT-style/HPND),
  https://github.com/linuxwacom/xf86-input-wacom (UNVERIFIED, X.Org driver).
- What they are: the kernel driver that makes the PTH-660 emit standard evdev MT events; the ID database (sizes,
  features, SVG layouts) used by libinput/desktop toolkits.
- Pipeline use: no code reuse in the app itself; use `libwacom-list-devices` / data files to confirm the PTH-660
  touch surface geometry and that the kernel exposes `ABS_MT_*` slots. PTH-660 multitouch arrives as ordinary
  type-B evdev — everything above (1.1/1.2) just works.

### 1.7 Touchégg — VERIFIED
- URL: https://github.com/JoseExposito/touchegg
- License: GPL-3.0 (source "available under GPL v3"; COPYING in repo)
- Language: C++
- What it is: Daemon turning libinput touchpad/touchscreen gestures (swipe/pinch/tap XML-configured) into desktop actions.
- Pipeline use: **architectural reference only** — its per-gesture config/animation model is overkill for static chords;
  do NOT fork it. Note: X11-only. ~4.1k stars.

### 1.8 Kivy input providers (mtdev + hidinput) — UNVERIFIED (docs/snippets only)
- URL: https://github.com/kivy/kivy
- License: MIT (per Kivy licensing docs; UNVERIFIED this session)
- Language: Python (+C providers)
- What it is: Cross-platform UI toolkit whose Linux input stack (`kivy.input.providers.mtdev`, `hidinput`,
  `probesysfs`) already solves "enumerate /dev/input/event*, read MT slots, de-jitter, calibrate" in Python.
- Pipeline use: if you want a calibration/visualizer UI for free, reuse Kivy's providers/postprocessing
  (`dejitter`, `retain`, `double-tap`) as patterns or as a debug harness — not as the hot path.

### 1.9 Hammer.js (note — likely OUT of scope) — UNVERIFIED
- URL not listed (never invent). Commonly `hammerjs/hammer.js` (web touch-gesture lib, MIT).
- What it is: DOM-pointer gesture recognizer (swipe/pinch/tap) for browsers.
- Pipeline use: none for evdev/Wacom; listed only because "Hammer" was named in the brief. Skip.

Slot/tracking-ID handling summary: implement contact tracking on `ABS_MT_SLOT` + `ABS_MT_TRACKING_ID` (`-1` = lift)
framed by `SYN_REPORT`, using 1.1 (simple) or 1.2 (resync/state for free). No chord-recognition library was found —
that layer is custom (hold-together window + contact-count/position → steno stroke).

---

## 2. ML finger identification from touch contacts (code-public? yes/no)

### 2.1 CapFingerId (Le et al., IUI'19) — VERIFIED, code PUBLIC
- URL: https://github.com/interactionlab/CapFingerId
- License: MIT (badge on repo page)
- Language: Python (Jupyter notebooks: `01-Importing and Preparing Data.ipynb`, `02-Classification.ipynb`)
- What it is: 455,709 capacitive images + CNNs classifying which finger(s) touched (thumb/index-focused combos,
  >92% left/right-thumb position-invariant accuracy).
- Pipeline use: **closest reusable prior art** for "which finger is this blob" from capacitive data; reuse the
  preprocessing + small-CNN baseline shape, then retrain on Wacom `ABS_MT_*` features (position/ellipse/major/minor
  if exposed) instead of raw capacitance frames. Dataset is phone-scale — expect a domain gap to PTH-660.

### 2.2 SpeciFingers (Huang et al., IMWUT'24) — VERIFIED, code PUBLIC (pipeline scripts + model)
- URL: https://github.com/iscas-MMSketch/SpeciFingers
- License: none found in repo (no LICENSE file; scripts + `model.py` + `raw_log_data.zip` + `environment.yml`) — assume all-rights-reserved until clarified
- Language: Python (PyTorch-style encoder-decoder workflow)
- What it is: Finger identification AND error correction from capacitive raw data on touchscreens (official paper impl).
- Pipeline use: borrow the encoder-decoder identification architecture and error-correction framing (mis-touch
  modeling maps directly onto chord-typo correction); cannot blindly reuse weights (phone digitizer ≠ Wacom).
  Contact authors re license before reusing code verbatim.

### 2.3 CapContact (Streli & Holz, CHI'21) — VERIFIED, code PUBLIC but NON-COMMERCIAL data/code
- URL: https://github.com/eth-siplab/CapContact
- License: CC-BY-NC-SA-4.0 (code + dataset; research-only, contact lab for commercial use)
- Language: Python (`train.py` / `inference.py`, PyTorch)
- What it is: 8× super-resolution of true finger-contact masks from single capacitive images (FTIR ground truth).
- Pipeline use: relevant only if PTH-660 blobs merge under multi-finger chords and you need sub-blob separation;
  otherwise skip — it solves contact-*shape* super-resolution, not finger *identity*. NC clause blocks commercial reuse.

### 2.4 FingerPose (andypotato) — VERIFIED, code PUBLIC, but WRONG MODALITY (camera, not capacitive)
- URL: https://github.com/andypotato/fingerpose
- License: MIT (badge)
- Language: JavaScript (TensorFlow.js; rule-based curl/direction estimator over 21 MediaPipe hand landmarks)
- What it is: Classifies camera-tracked hand poses ("victory", "thumbs-up", custom `GestureDescription`s).
- Pipeline use: do NOT use for contact→finger ID (needs a camera + MediaPipe Hands); at most borrow the *idea* of
  declarative gesture descriptions for chord definitions. Listed to prevent confusion: "FingerPose" ≠ capacitive finger ID.

No-code papers (UNVERIFIED, no repo asserted): several capacitive-finger-ID papers have no public implementation
found this session — treat as citations only, not reusable code.

---

## 3. Stenotype software (Plover, plugins, dictionaries, bridges)

### 3.1 Plover engine — VERIFIED
- URL: https://github.com/opensteno/plover
- License: GPL-2.0-or-later ("GPLv2+ as of 3.1.0"; badge GPL-2.0)
- Language: Python
- What it is: The open-source stenotype engine (200+ WPM goal): machine layer → translation/dictionary lookup →
  formatting → output. ~2.6k stars.
- Pipeline use: **two integration options**: (a) write a custom *machine plugin* exposing touch chords as steno
  strokes and get translation/formatting/output free; (b) reimplement a minimal JSON-dictionary lookup standalone
  (only if Plover's weight/event loop is a problem). Prefer (a).

### 3.2 Plover machine-plugin API (which API to implement) — UNVERIFIED details (docs not fully read this session)
- Docs: `Plugin Development` (plover.wiki) + `plover.readthedocs.io` plugin-dev/setup (both seen in search; contents not fully read)
- API surface (confirm against installed Plover source before coding): setuptools entry point group
  `plover.machine` naming a class subclassing `plover.machine.base.ThreadedStenotypeBase` (or `StenotypeBase`);
  implement `start_capture()` / `stop_capture()` / `add_callback()`, declare `KEYS_LAYOUT` (steno key order) and
  `ACTIONS`, and call the stroke callback with lists of pressed steno keys per chord. Example skeleton:
  `paulfioravanti/plover-practice-plugin` (seen in search — UNVERIFIED).
- Registry/wiring: https://github.com/opensteno/plover_plugins_registry (VERIFIED page read; JSON list that feeds
  Plover's Plugins Manager; no license badge visible) — publish under your PyPI name + PR here for one-click install.
- Reference machine plugin: https://github.com/opensteno/plover-stenograph (VERIFIED page read; USB/Wi-Fi Stenograph
  machines; license badge not visible in fetched text — check repo) — copy its plugin scaffolding
  (`setup.cfg` entry points, machine class, packaging) for the touch machine.

### 3.3 Steno dictionaries — VERIFIED (representative set)
- https://github.com/didoesdigital/steno-dictionaries (VERIFIED; GPL-2.0 badge; JSON, Plover theory; actively
  maintained; explicitly recommended OVER Plover's bundled `main.json`, unmaintained since ~2018) — use
  `dict.json` + `fingerspelling.json` + `numbers.json` + `punctuation.json` (+ computer-use/navigation helpers).
- Plover built-in `plover/assets/main.json` (inside 3.1 — UNVERIFIED path, but format is certain): baseline fallback.
- Formats: Plover JSON (`{"KAT": "cat", "KAT/HROG": "catalog", "-S": "{^s}"}`) is the interop standard; RTF/CRE
  dictionaries importable; `.ctdict` is a CAT-system format, not native — convert, don't adopt.
- Also seen (UNVERIFIED): `openstenoproject/awesome-plover` (curated plugins/dicts list).

### 3.4 Touch/steno bridges — none found as a finished product
- No open-source "multitouch-screen → Plover machine" bridge surfaced in search. The touch machine plugin is
  greenfield; 3.2's scaffolding + 3.3's dictionaries are the reuse story, not a ready bridge.

---

## 4. Offline text prediction / autocorrect / LM engines (Python or C++)

### 4.1 KenLM — VERIFIED
- URL: https://github.com/kpu/kenlm
- License: LGPL-family (repo shows LICENSE + LGPL-2.1/GPL-3.0 texts; query lib usable under LGPL terms — confirm file for your linking mode)
- Language: C++ with Python module (`python/kenlm.pyx`; `import kenlm; model.score(...)`)
- What it is: Fast/small n-gram LM querying + on-disk estimation (`lmplz`), binary mmap format, ARPA support.
- Pipeline use: **offline word/steno-sequence scorer** for chord disambiguation and post-correction ranking.
- Wheels: NO official PyPI wheels — build from source (`cmake`, needs Boost for estimation). ~2.8k stars.

### 4.2 SymSpell (C# original) + symspellpy (Python port) — both VERIFIED
- URLs: https://github.com/wolfgarbe/SymSpell (MIT, C#) and https://github.com/mammothb/symspellpy (MIT, Python port of v6.7.2, ~876 stars)
- What they are: Symmetric-Delete spelling correction + compound-aware multi-word correction + word segmentation;
  microsecond-scale lookup, frequency dictionaries included (`frequency_dictionary_en_82_765.txt`).
- Pipeline use: **lightweight chord-typo corrector** (steno mis-stroke ≈ spelling error): `lookup_compound` over the
  translated words + `word_segmentation` for fingerspelled runs. No training, no GPU, trivially offline.
- Wheels: `symspellpy` ships on PyPI (`pip install symspellpy`) as pure Python — installs anywhere; original C# is a
  NuGet package (irrelevant on Linux/Python path except as algorithm reference).

### 4.3 OpenFst (+ Python wrappers) — VERIFIED (core repo)
- URL: https://github.com/google-research/openfst (Apache-2.0 badge; C++17; Bazel/CMake; optional `pywrapfst`)
- Language: C++ (+ Python via `pywrapfst`; third-party `jpuigcerver/openfst-python` — UNVERIFIED)
- What it is: Weighted finite-state transducer library (compose/determinize/minimize/shortest-path) — the machinery
  under classical speech/IME decoders.
- Pipeline use: only if you build a real steno→text lattice decoder (chord confusion model ∘ dictionary ∘ LM);
  overkill for v1 — prefer KenLM scoring + SymSpell correction first. No wheels; build from source.

### 4.4 BerkeleyLM — repo page read, license UNVERIFIED
- URL: https://github.com/adampauls/berkeleylm
- License: not visible on repo page (old Google-Code export, `ant` build) — treat as UNKNOWN; do not assume GPL
- Language: Java
- What it is: Java n-gram LM toolkit (fast queries, compact storage).
- Pipeline use: none recommended — Java-only, stale upstream, uncertain license. KenLM dominates it on every axis
  for this project. Listed because the brief asked; verdict: skip.

### 4.5 NLTK word models — UNVERIFIED (not searched this session; no URL asserted)
- What it is: `nltk` Python package (PyPI `nltk`) with MLE/Kneser-Ney LM module (`nltk.lm`), frequency distributions,
  and sample corpora for bootstrapping a unigram/bigram prior in pure Python.
- License: Apache-2.0 (UNVERIFIED this session — confirm before vendoring corpora; corpus licenses vary).
- Pipeline use: v0 baseline scorer/corrector before committing to KenLM's build chain; pure-Python + PyPI wheels
  make it the fastest thing to prototype with. Do not ship Gutenberg-derived frequency lists without checking terms.

---

## 5. Shortlist — the 8 most directly reusable repos (and why)

1. **https://github.com/gvalkov/python-evdev** (BSD-3-Clause, Python) — read MT slots/tracking IDs AND emit via
   `UInput` with a single dependency. The I/O foundation.
2. **https://github.com/opensteno/plover** (GPL-2.0-or-later, Python) — translation, dictionaries, formatting, and
   output for free once the touch layer speaks "strokes"; implement the touch panel as a `plover.machine` plugin.
3. **https://github.com/didoesdigital/steno-dictionaries** (GPL-2.0, JSON data) — maintained Plover-theory
   dictionaries replacing stale `main.json`; the linguistic content of the translator.
4. **https://github.com/kpu/kenlm** (LGPL-family, C++/Python) — offline n-gram scorer for ranking ambiguous chords
   and correcting steno mis-strokes at the sequence level.
5. **https://github.com/mammothb/symspellpy** (MIT, Python) — zero-training typo/compound corrector for the
   translated text layer; PyPI-installable, fastest path to "forgiving" chords.
6. **https://gitlab.freedesktop.org/libevdev/python-libevdev** (MIT, Python; UNVERIFIED page) — swap-in if raw
   evdev handling frays: per-slot state + SYN_DROPPED resync handled by the library.
7. **https://github.com/interactionlab/CapFingerId** (MIT, Python) — only public MIT-licensed capacitive finger-ID
   code+data; template for the finger/chord classifier and its evaluation protocol.
8. **https://github.com/opensteno/plover-stenograph** (license n/c, Python) — closest existing machine-plugin
   scaffolding to clone for the custom touch machine (packaging, entry points, device-thread pattern).

Honorable mentions: `linuxwacom/input-wacom` + `libwacom` (driver/ID truth for the PTH-660, no app code to reuse);
`rydberg/mtdev` (type-A fallback); `wolfgarbe/SymSpell` (algorithm upstream of #5);
`iscas-MMSketch/SpeciFingers` (stronger model, but no usable license); `eth-siplab/CapContact` (NC-locked, wrong
sub-problem); `google-research/openfst` (decoder-grade, defer to v2).

Suggested v1 stack: python-evdev (I/O) → custom slot tracker + centroid/chord classifier (seeded by CapFingerId
patterns, calibrated per-user) → Plover custom machine + Di's dictionaries → symspellpy correction → optional KenLM
rescoring. Nothing on this list decodes MTF tracking IDs into finger identities on a Wacom out of the box — the
chord/finger layer is the novel component to build and evaluate.
