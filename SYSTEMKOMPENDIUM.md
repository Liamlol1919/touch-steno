# SYSTEMKOMPENDIUM — das ganze System, Teil für Teil

> Zweck: Vollständige Dokumentation aller Komponenten von **commindv2** inklusive der
> geerbten Teile aus **stenoQT** (`~/Projekte/steno`) und **denken** (`~/Projekte/denken`)
> sowie der Konzept-Ebene aus **commind** (`~/Projekte/commind`). Eine Datei, kapitelweise
> aufgebaut. Stand: 24.09.2026 (Outline + Beleg-Anker); Detailkapitel werden Kapitel für
> Kapitel nachgeschoben.
> Belegregel: Jede Aussage trägt `[GEBAUT]` (Code in commindv2), `[GEERBT]` (Original in
> steno/denken, nicht Teil der laufenden App), `[KONZEPT]` (nur Docs/Specs), `[ARCHIV]`
> (historisch, nicht mehr gültig) oder `[WIDERSPRUCH]` (Quellen widersprechen sich).
> Alles ohne Code/Quelle ist **Hypothese**.

---

## Kapitelübersicht

| # | Kapitel | Inhalt | Kernquellen |
|---|---------|--------|-------------|
| 0 | Karte & Konventionen | Repos, Namensraum, Status-Lesart, Datenpfade | diese Datei |
| 1 | Gesamtsystem | Drei Projekte, ihre Rollen, Provenienz-Regeln | `../commind/README.md`, `SYSTEM.md` |
| 2 | Hardware & physische Ebene | PTH-660, 3D-Overlay, Geräte, Rechte | `src/overlay_layout.json`, `docs/EINGABE-SPEC.md` |
| 3 | Eingabe Rohschicht | evdev-Reader, Regionen, Chord-Assembly, Gesten | `src/wacom_touch.py`, `src/input_zones.*` |
| 4 | inputd-Daemon | Zonen-Routing, QWERTZ-Streifen, uinput-Steno | `tools/inputd.py`, `tools/steno_engine.py`, `tools/inputd_link.py` |
| 5 | App-Eingabepfade | PadBridge, Dispatcher, Plover-Layout, ChordFilter | `ui/wacom_pad.py`, `ui/pad_dispatcher.py`, `ui/steno_layout.py`, `ui/chords.py` |
| 6 | Substrat (store) | SQLite-Schema, Primitives, Tombstones, Events, FTS | `core/store.py` |
| 7 | Kernel | Ops, Settings, Profile, Bindings, Prädikate/Rollen | `core/kernel.py` |
| 8 | Darstellung | App-Shell, Canvas, Nodes, Edges, Viewport, Media | `ui/app.py`, `ui/views/*` |
| 9 | Workflow-Denksystem | Engine, Context-API, 3 Module, Persistenz | `core/workflow_engine.py`, `workflows/*` |
| 10 | Lernsystem (Kartei) | DB, FSRS, Session, Reader, Renderer, Kartei-Fenster | `core/kartei_*.py`, `ui/kartei_window.py` |
| 11 | stenoQT Original | Workbench + 18 Kartei-Module, was geerbt/entfällt | `~/Projekte/steno` |
| 12 | denken | Denksprache, Handles, Five Arrows, TAE, Science, Prototypen | `~/Projekte/denken` |
| 13 | Kognition & Konzepte | 7 Kanäle, 9 Konzepte, Spielzüge, Nordsterne | `../commind/docs/*` |
| 14 | Daten & Pfade | `.commind-data`, Workspaces, Import/Export, Medien | `core/paths.py`, `core/workspace_io.py` |
| 15 | Tests & Qualität | Testlandschaft, Gates, Messvorsätze | `tests/` (65 Dateien) |
| 16 | Widerspruchsregister & offene Fragen | Was sich widerspricht und was der User entscheiden muss | hier |
| 17 | Glossar | Zettel/Kante/Karte/Chord/Token/Workflow … | `../commind/docs/GLOSSAR.md` |

---

## 0. Karte & Konventionen

- **Vier Repos, eine Dokumentation:**
  - `~/Projekte/commindv2` — DIE laufende Anwendung (dieses Repo). Port aus steno mit
    erweitertem Eingabe-Stack. Start: `python3 -m ui.app`.
  - `~/Projekte/steno` — stenoQT Original (Workbench + Kartei, v1.4.x/v2.0.x). Nur lesen.
  - `~/Projekte/denken` — Denksprache/-werkzeuge (Docs + JS-Prototypen). Nur lesen.
  - `~/Projekte/commind` — Konzept-Repo (Doku-Kanon, kein App-Code). Lesekopien der beiden
    anderen unter `commind/STENOQT_UND_DENKEN/`.
- **Namensregel:** "steno" = die App stenoQT, "Akkorde/Steno-Chords" = die Eingabetechnik,
  "Steno-Layout" = Lapwing/Plover-Wörterbuch. Nicht austauschbar.
- **Datenpfade commindv2** (`core/paths.py`): `.commind-data/store.sqlite3` (Graph),
  `.commind-data/kartei.sqlite3` (Lernstand), `store.workflows.json` (aktiver Workflow),
  `media/` (Bilder, Hash-Namen). Git-ignored (`.gitignore`: `.commind-data/`, `*.sqlite3`).
- **Datenpfade steno Original:** `.steno-data/store.sqlite3`, `kartei.sqlite3`.
- **Provenienz:** `core/store.py`, `core/kernel.py`, `ui/chords.py` sind Verbatim-Ports aus
  steno (Header-Kommentare nennen Commit + Ausnahmen). Jede Abweichung steht im Header.

## 1. Gesamtsystem

- **Evolutionäres Stapel-Verständnis (User-Klarstellung 25.09.):** Die drei Projekte bauen
  **aufeinander auf**, es sind keine konkurrierenden Systeme:
  1. **stenoQT** (`~/Projekte/steno`) = Grundschicht: das Canvas + schon die Lernidee
     (Kartei/FSRS). ~80 % des commindv2-Codes sind daraus übernommen (Port-Header in
     `core/store.py`, `core/kernel.py`, `ui/views/*`).
  2. **commind** (`~/Projekte/commind`) = Ideenschmiede + Filter: neue kognitive Ideen
     (Kanäle, Konzepte, Workflows, denken-Fünfpfeil etc.) angeschaut, ausgewertet,
     **rausgefiltert** — was bleibt, ist in Docs gefasst (`docs/KONZEPTE.md`, `AUSGANGSLAGE.md`,
     `USER-INPUTS.md` als kanonische User-Vorgaben).
  3. **commindv2** (dieses Repo) = aktuelle Synthese: geerbter stenoQT-Kern + gefilterte
     commind-Ideen + neuer Eingabe-Stack (PTH-660/Overlay/inputd) + Workflow-Engine.
- **Kreislauf** (`../commind/README.md:18-31`): GEHIRN → WORKBENCH (Canvas-Graph) →
  optionale WORKFLOWS → KARTEI (Recall/FSRS) → zurück ins GehIRN. Zwei Aggregatzustände:
  Weite (Workbench) und Dichte (Kartei).
- **Nordsterne** (nicht verhandelbar): direktes Erfassen <2s, null Kontextwechsel, lokal
  ohne Netz/KI/Auto-Zettel, gemessen statt geraten, diagnostisch nie als Ziel.
- **commindv2 = Umsetzung, commind = Konzept-Kanon.** commind-Docs beschreiben
  Zielzustand (teils 18.09.), commindv2-Code ist Stand 23.09. — bei Divergenz gewinnt der
  Code, Konzept ist `[KONZEPT]`.
- Detail: **Kapitel 13** für Konzepte, **Kapitel 11** für steno, **Kapitel 12** für denken.

## 2. Hardware & physische Ebene

- **Wacom PTH-660 = Intuos Pro M**, Fläche 224×148 mm, gemessen 8960×5920 units = **40
  units/mm** (`src/wacom_touch.py:44-47`), TOUCH_MAJOR 2 units/mm. `[GEBAUT]`
- Drei evdev-Devices (`docs/EINGABE-SPEC.md:9-13`):
  - `Wacom Intuos Pro M Finger` (event19) → Steno + Touchpad + Zonen.
  - `Wacom Intuos Pro M Pad` (event18) → ExpressKeys BTN_0..BTN_8 (+BTN_STYLUS).
  - `Wacom Intuos Pro M Pen` (event17) → Skizzen, **noch nicht angebunden** (S6, `kind=sketch` fehlt).
- **3D-Overlay** (`src/overlay_layout.json`, Generator `tools/overlay_layout.py`):
  Feld 16.2 mm, Steg 1 mm, 5 Blöcke (L1-L5) mit gedrehten Daumentasten, Pivot (18,168).
  Druckvorlagen: `docs/overlay-*.dxf`, `docs/layout-sheet.pdf` (Generator
  `src/layout_sheet.py` schreibt auch `src/input_zones.json` + validiert Überlappungen).
- Druckmessung/Kalibrierung: `tools/pressure_view.py` (`--measure`, Perzentile, EMA).
- Rechte: `src/90-wacom.rules` (udev, MODE 0660 GROUP input) + `src/pad_install.sh`
  (evdev-Check, Regel-Install, Gerätesuche). `[GEBAUT]`
- Messwerte: 10 Finger gleichzeitig ok, Kernel-Arbitration (touch_arbitration) am Eingang
  **nicht** wirksam, EVIOCGRAB sauber (7568 Events, X11 blind) — `src/HW-TOUCH-PLUGIN.md:30-32`.

## 3. Eingabe Rohschicht (`src/`) — detailliert

Zweck dieser Schicht: aus rohen Linux-evdev-Events (ABS_MT_*) **semantische Eingaben**
machen — Steno-Chords, Wisch-Gesten, Pan-Deltas, ExpressKeys — ohne dass die App je ein
rohes Touch-Event sähe. Alles in mm, alles replay-testbar ohne Gerät.

### 3.1 Geometrie & Kalibrierung
- Device-Maße: 224×148 mm, 8960×5920 units → **40 units/mm** (`UNITS_PER_MM`),
  `MAJOR_UNITS_PER_MM=2`. Diese zwei Konstanten übersetzen alles.
- `PALM_MAJOR_MM=14.0`: Kontaktbreite darüber = Handfläche, wird verworfen
  (Fingerkuppe ~10–13 mm, Hypothese — kalibrierbar). Zwei Pfade prüfen das:
  `RegionMap.key_at` und der Reader.
- Regionen: Rechtecke `(x0,y0,x1,y1)` in mm (halboffene Kanten via `in_rect`) **plus**
  optionale Polygone (`_in_polygon`, Ray-Casting) für die schrägen Daumentasten des
  3D-Overlays. Zell-Index macht `key_at` O(1) statt O(n) — 2-mm-Zellen.

### 3.2 Chord-Assemblierung (`StrokeAssembler`)
- Modell: Ein Chord ist die **Vereinigung** aller Keys, die während der Bewegung berührt
  wurden — auch die, deren Finger schon gehoben sind (`retained`). Erst wenn **alle**
  Kontakte weg sind, wird der Stroke als `frozenset` ausgeliefert.
- Genau das macht echte Steno-Fingerführung möglich: `S-` heben, `-T` bleibt → Stroke
  enthält beide (Regressionstest `test_chord_accumulates_after_partial_lift`).
- Palm-Kontakte und Kontakte außerhalb aller Regionen ergeben `None` → kein Key.

### 3.3 Gesten (`GestureClassifier`)
- Tap vs. Wisch über **reine Distanz** (`SWIPE_DIST_MM=12`), bewusst ohne Zeitkomponente
  (User-Vorgabe "deterministisch und frei"). Startpunkt = erster Kontakt-Punkt; beim
  Loslassen entscheidet `hypot(dx,dy)`.
- Schwelle liegt über dem Steno-Raster (~15 mm), weil Steno-Griffe bis ~5 mm wandern.

### 3.4 Reader (`WacomTouchReader`)
- MT-Protokoll B: `ABS_MT_SLOT` → `ABS_MT_TRACKING_ID` verwaltet Slot→TID, Positionen/
  Major sammeln, Auswertung bei `SYN_REPORT`.
- **Touchpad-Lifetime-Regel** (zentral): ein Kontakt, der im `touchpad`-Rechteck **startet**
  und dort **keine** Steno-Taste trifft, bleibt für seine gesamte Lebensdauer ein Pan-Kontakt
  (`_tp_last`) — auch wenn er das Feld verlässt. Auf einer Steno-Taste gestartete Kontakte
  (`self._steno`) werden **nie** Pan. Beides zusammen verhindert das berüchtigte
  "halb Steno, halb Pan"-Flackern.
- Callbacks: `on_stroke` (frozenset), `on_contacts` (rohe mm-Kontakte für Zonen),
  `on_swipe` (dx,dy in mm), `on_touchpad` (Delta in mm).

### 3.5 ExpressKeys (`WacomPadButtonReader`)
- Zweites Device ("… Pad"), EV_KEY `BTN_0..BTN_8` (+`BTN_STYLUS`) → stabiler Name
  (`button_name`, Release ignoriert). Die **Aktion** lebt in `src/pad_buttons.json`, nicht
  im Reader — bewusst tweakbar ohne Code.

### 3.6 Plover-Shim (`Stenotype`)
- `StenotypeBase`-Unterklasse (verifiziert gegen AppImage: `start_capture`/`stop_capture`/
  `_notify`, **kein** `cancel_capture`; `KEYS_LAYOUT` whitespace-separiert, nicht `KEYS`).
- Grabbt das Finger-Device exklusiv für die Aufnahme; `_notify` gibt Chords in
  Steno-Reihenfolge weiter. Optional — fehlt Plover, bleibt der Reader nutzbar.

## 4. inputd-Daemon (`tools/`) — detailliert

**Engine-Entscheid (GEKLÄRT 25.09.): Die Eigen-Engine (`tools/steno_engine.py`) ist der
Standard.** Der Daemon läuft komplett Plover-frei. Der Plover-Machine-Shim in
`src/wacom_touch.py` (`Stenotype`) ist eine **optionale Alternative**, wenn man statt des
Daemons Plover als Übersetzer will. Beide lesen dasselbe Dict-Format (Plover/Lapwing-JSON)
— nur die Prioritäten der Dateien weichen leicht ab (Widerspruch W6).

Der Daemon ist der **systemweite** Eingabe-Modus: ohne commindv2-App wird das PTH-660 zur
Steno-Maschine + Tastatur + Touchpad für **alle** Programme. Er besitzt beide evdev-Devices
exklusiv (`grab`), damit Linux/X11 die rohen Touches nicht selbst als Cursor deutet.

### 4.1 Routing-Modell (`tools/inputd.py`)

Jeder Kontakt wird anhand seiner Startposition genau einer Rolle zugeordnet:

| Fläche | Verhalten | Detail |
|---|---|---|
| **Streifen oben** (`y < 80 mm`) | QWERTZ-Tastatur ODER Touchpad | Toggle per `BTN_8` + `notify-send`-Badge (`TopRouter.toggle`) |
| **Spacepad** (Daumenlücke, `spacepad.rect`) | immer Touchpad | Tap=Linksklick, Tap-Drag (0.35 s / 15 mm), 2-Finger=Scroll (REL_WHEEL/HWHEEL), Pinch=Strg+Wheel |
| **Steno-Fläche** (unten, 3D-Overlay) | Steno-Chords | `StrokeAssembler` → `steno_engine` → uinput ODER App-Socket |
| **Außerhalb** | ignoriert | bewusst ohne Wirkung (Spec-Regel) |

### 4.2 Geister- und Palm-Filterung
- **Ghost-Suppression:** der Treiber meldet einen Finger manchmal als zwei TIDs (~1–2 mm
  auseinander). Zweiter Kontakt im Umkreis `GHOST_MM=12 mm` um einen offenen → "ghost",
  kein Finger. Beförderung zum echten Finger, wenn er sich weit genug wegbewegt
  (Pinch-Start eng ist der Klassiker).
- **Palm-Drop:** `major > PALM_MAJOR_MM=14` → Kontakt wird verworfen, offene werden
  geschlossen.
- **Tap vs. Drag:** Bewegung < `TAP_MAX_MM=4` beim Loslassen = Tap (Linksklick),
  sonst nur Cursor-Bewegung (kein Dauer-Klick beim Rumgehen).

### 4.3 Zonen-Tracking (`ZoneTracker`, aus `src/input_zones.py`)
- `update(contacts)` liefert `(mode, mover)` mit `mode ∈ {create, jump, pan}`:
  `pan` gewinnt bei Mehrfachbelegung, dann `jump`, sonst `create` (Default).
- **Mover** (`MoverState`): Kontakt im Kreis → `(sektor, radius_klasse)`; Sektor 0 = rechts,
  gegen Uhrzeigersinn (Qt-y zeigt nach unten); `radius_klasse` 0=nah, 1=weit aus
  Deadzone→Radius normalisiert. Deterministisch, keine Hysterese.
- `mitspringen()`: rechter Daumen gehalten → Kamera folgt beim CREATE (Modifier).
- Zustandswechsel werden an die App gesendet (nur bei Änderung), Format siehe 4.5.

### 4.4 Steno-Übersetzung ohne Plover (`tools/steno_engine.py`)
- `stroke_to_rtfcre(frozenset)` → kanonische Chord-ID (RTFCRE-Reihenfolge
  `#STKPWHRAO*EUFRPBLGTSDZ`, Zahlenleiste `NUM_BAR` bei `#`).
- `Translator`: Multi-Stroke-Lookup (bis 10 Strokes), `*` = letzte Übersetzung zurücknehmen
  (Backspace-Modell, `segments`-Stack), Glue (`{^}`), Kapitalisierung (`{>}`, `{-|}`),
  Satzzeichen, `&x`-Einzelzeichen.
- Dict-Priorität: `user.json` > `main.json` > `lapwing-base.json` (⚠️ abweichend von
  `ui/steno_layout.py`, siehe Widerspruch W6).
- `/…`-Einträge (commind-Tokens) erzeugen **keinen** Systemtext — sie werden zurückgehalten,
  damit die App sie als Befehle sieht.
- `type_text(ui, backspaces, text)` tippt über uinput (DE/QWERTZ-Mapping `DE_TYPE_MAP`,
  Shift-Handling).

### 4.5 App-Link (`tools/inputd_link.py`)
- UNIX-Domain-Stream-Socket: `$XDG_RUNTIME_DIR/commind-input.sock`.
- JSON-Linien, Broadcast an alle verbundenen Clients:
  - `{"t":"stroke","keys":["S-","T-",…]}`
  - `{"t":"button","name":"BTN_5"}` (ohne `BTN_8` — frisst der Daemon als Toggle)
  - `{"t":"zones","mode":"pan|jump|create","mover":[sektor,radius_klasse]|null,"mitspringen":bool}`
- **Doppelwirkungsschutz:** solange mindestens ein Client verbunden ist, tippt der Daemon
  Steno **nicht** systemweit (`link.has_clients()`).

### 4.6 Debug-Werkzeuge
- `tools/touch_monitor.py` — rohe MT-Events live anzeigen.
- `tools/zones_preview.py` — Zonen/Mover-Geometrie visualisieren.
- `tools/keyboard_layout.py` — QWERTZ-Mapping generieren/prüfen.
- `tools/pressure_view.py` — Finger-Aufdruck live, `--measure` Kalibrier-Modus
  (Rohwerte + Perzentile, 0.2-mm-Stufen, EMA nur für mm-Anzeige).

## 5. App-Eingabepfade (`ui/`) — detailliert

Innerhalb der commindv2-App gibt es **drei parallele Eingabewege** mit identischer
Semantik — echtes Pad, Pad-Simulator, Kommandozeile. Kein zweiter Verhaltenspfad
(User-Vorgabe 20.09.: "identisches Verhalten, kein zweiter Weg").

### 5.1 Die drei Quellen → ein Handler

```
evdev-Thread (PadBridge)  ─┐
Socket-Thread (inputd)    ─┼→ Qt-Signale → GUI-Thread → handle_stroke(stroke, window)
Pad-Simulator (F10)       ─┘
```

`handle_stroke` (`ui/wacom_pad.py:21-82`) — die Reihenfolge ist Vertrag:
1. **Chord-Aktion** aus `src/pad_actions.json` (via `pad_dispatcher.pad_dispatch`) → ausführen.
2. **Steno-Text** via `ui/steno_layout.translate(stroke)`:
   - Text beginnt mit `/` → Aktion dispatchen (Lapwing user.json kann Tokens zurückgeben).
   - sonst: in den **offenen Editor** tippen (`canvas.type_into_editor`), und wenn keiner
     offen ist, einen **neuen Zettel am letzten Ort** spawnen (`_last_note_id` + Placement).
3. **sonst** Statusmeldung "Chord nicht belegt" (Tweaking-freundlich, nie Crash).

### 5.2 Aktionen (`ui/pad_dispatcher.py`)
- Gemeinsamer Kern `run_action(action, window)` für Pad-Chords **und** physische Buttons.
- Unterstützte Aktionen: `nav:left|right|up|down` (→ `canvas.select_in_direction`,
  `NAV_ANGLE` 0/90/180/270°, Qt-y-Wachstum = 90° ist unten), `bookmark:N`
  (`canvas.bookmark_goto`), `kartei` (`window._on_kartei`), `verwerfen`
  (Tombstone + Placement entfernen + Selektion aufheben), `/steno-role-*` (Rolle auf
  **Selektion**, wie das Dropdown), `/steno-*` (`window._chord_token`).
- Unbelegt oder unbekannt → `False` → no-op. **Fehlklick crasht nie** (Harte Regel fürs
  Hardware-Tweaking).

### 5.3 Chord-Tabellen
- `src/pad_actions.json` — Finger-Chords (Multi-Key = sortierte Keys mit `+`, z.B.
  `"-B+-D"`). **Einzeltasten sind IMMER Steno-Text** (Layout aus `~/.config/plover`),
  App-Aktionen nur auf Chords. 8 belegte Chords: 2 Rollen (question/axiom), 4 nav,
  kartei, verwerfen.
- `src/pad_buttons.json` — physische ExpressKeys BTN_0..8 (+BTN_STYLUS), frei belegbare
  App-Shortcuts (kein Steno). Gleicher Aktion-Vertrag. `BTN_8` bewusst leer (Daemon-Toggle).

### 5.4 Steno-Layout (`ui/steno_layout.py`)
- Liest die **echten** Plover/Lapwing-Dicts: `lapwing-base.json`, `lapwing-commands.json`,
  `user.json` (höchste Priorität, persönliche Add-ons). ⚠️ Der Daemon-Pfad
  (`tools/steno_engine.py`) liest eine andere Priorität (user/main/lapwing-base) — W6.
- `chord_id(stroke)` → kanonische Schreibweise (`{'S-','T-','A'}` → `"STA"`,
  nur rechts → `"-T"`).
- `translate(stroke)` → Dict-Treffer oder Fallback: rohe Chord-ID (fürs Layout-Lernen).
  In der App ist das der Chord→Text-Weg für Text-Eingabe in den Editor/Zettel; die
  systemweite Übersetzung läuft über die Eigen-Engine im Daemon (Standard, Kapitel 4).
- `append_layout_entry(chord, text)` — Chord-Lernmodus ("das war gemeint"), schreibt nach
  `~/.config/plover/user.json`.

### 5.5 Token-Empfang (`ui/chords.py`)
- `COMMAND_TOKENS` — die Atlas-Tabelle aller `/steno-*`-Tokens → Operator-IDs.
- `ChordFilter` (QObject-EventFilter, global installiert): erkennt Tokens in
  Tastatureingaben, ohne normalen Plover-Output zu verschlucken (Editor-Fokus-Gate,
  Token-Streifen nach Dispatch, Resync nach freiem Text).
- `parse_steno_line(raw)` — Kommandozeile: `/steno-link <prädikat> <ziel>` zerlegen.
- `CHORD_TOKENS` in `ui/app.py`: Atlas-Tabelle + `graph.spawn_relation` für `/steno-link`.

### 5.6 Wisch-Geste & Pan (PadBridge-Signale)
- `swipe_signal(dx, dy)` → `_on_swipe`: deterministischer Sprung zum nächsten Kanten-
  Nachbarn in Gewichtrichtung (`next_in_direction`, 45°-Sektor, quadrierte Winkelprüfung
  MIT Vorzeichen); ohne Selektion: nächster Zettel vom Viewport-Zentrum aus; Landung exakt
  mittig, kein Fokuswechsel, kein Editor-Eingriff.
- `pan_signal(dx_mm, dy_mm)` → `_on_pan`: Canvas-Verschiebung = `mm × PX_PER_MM(6) ×
  sensitivity` (aus `input_zones.json`, Default 0.1), Achsen/Invertierung per `x_axis`/
  `y_axis`.
- `zone_signal(msg)` → `_on_zone`: Haltezonen/Mover vom Daemon — **aktuell nur
  Statusmeldung**, die Canvas-Verdrahtung von create/jump/pan folgt noch (offener Punkt).

### 5.7 Zwei Modi des PadBridge
1. **Direkt** (`start`): evdev-Reader-Thread (Finger) + Button-Thread (Pad) greifen exklusiv
   zu. Fallback bei `EBUSY`/`resource busy` → Modus 2.
2. **Socket** (`start_socket`): Daemon hat die Devices, die App liest Strokes/Buttons/Zonen
   vom Socket. "Eine Quelle zur Zeit, kein Umstecken."

## 6. Substrat (`core/store.py`, Schema v6) — detailliert

Das Substrat ist die **einzige Wahrheit**: alles Denken wird als SQLite-Zeilen persistent,
die Canvas ist nur eine Projektion. Aus steno portiert (Verbatim, Header nennt Ausnahme
`paths.py DATA_DIR`), erweitert um Schema v6.

### 6.1 Das Schema — 9 Primitive + Beiwerk

| Tabelle | Zweck | Schlüsselspalten |
|---|---|---|
| `objects` | **Alles ist ein Objekt** — Zettel (kind=`note`), Bild (`image`), Relation-Objekt, Setting, Profil, Bookmark … `kind` ist freier String | `id, workspace, kind, content, created, updated, deleted` |
| `attributes` | Freies Key/Value/Type je Objekt — Rolle (`role`), Größe (`size`/`w`/`h`), Medium (`media`) | `(object_id,key)` PK |
| `relations` | Gerichtete/ungerichtete Kanten `source→predicate→target`, eigenes `deleted` + `cascaded` | `id, workspace, source, predicate, target, deleted, cascaded` |
| `relation_roles` | Rollen in reifizierten Relationen (z.B. "Mittel" in "führt zu") — kaum genutzt | `(relation_id,role,object_id)` |
| `sequences` | Geordnete Kinder `container→member` mit `ord` (float, schiebbar ohne Neuordnen) — Gliederungs-Basis | `(container_id,member_id)` |
| `views` | Benannte Ansichten je Workspace; `config` (JSON) trägt u.a. `last_pose` | `id, workspace, name, config` |
| `placements` | **Position ist Daten, nicht Zustand** — wo ein Objekt in einer View liegt | `(view_id,object_id)` + `x,y,w,h,z,ord` |
| `view_edges` | Kanten-Style pro View (Abweichungen vom Prädikat-Default) | `(view_id,relation_id)` + `style` JSON |
| `events` | Append-only Log jeder Mutation (Audit/Historie/Analyse) | `id, workspace, action, payload, created` |
| `workspaces` | "Räume" — jeder sieht nur seine Objekte | `id, name, created` |
| `type_patterns` | Typisierte Zettel (Feld-Schemata + Constraints) — wenig ausgereizt | `tag, fields, constraints` |
| `search_fts` | FTS5-Volltextindex über `note`-Inhalte (Präfix-Suche) | `content, workspace, object_id` |

### 6.2 Kernmechaniken

- **Tombstones statt Löschen:** `delete_object` setzt `deleted=1` + `updated`; kaskadiert
  auf alle Relationen des Objekts (`cascaded=1`). `restore_object` belebt Objekt **und**
  nur die kaskadierten Relationen zurück (manuell gelöschte bleiben tot). Nichts geht je
  physisch verloren.
- **Paar-Idempotenz** (`add_relation`): je Zettelpaar **maximal eine lebende Kante**,
  Richtung egal. Zweiter Versuch → Prädikat wird **in-place transformiert**, keine zweite
  Zeile (Regression 23.09., Test `test_add_relation_ist_paar_idempotent`).
- **Workspace-Umzug** (`umzug`): Objekt + FTS + Placement wandern; Kanten, deren **beide**
  Enden im Ziel sind, wandern mit; Kanten nach außen bleiben im Quellraum (leben weiter).
- **Events:** jede Mutation erzeugt ein `events`-Zeile + `object.*`-Action; `prune_events`
  begrenzt das Wachstum (Retention, `keep_last`).

### 6.3 Performance-Struktur (gemessen, aus steno)

- **PRAGMAs:** WAL + `synchronous=NORMAL` (kein fsync-Stall pro Commit, ~0.86 ms median),
  `cache_size=-64000` (64 MB Page-Cache), `foreign_keys=ON`.
- **Schema-Versionierung:** `PRAGMA user_version`, `_SCHEMA_VERSION=6`. Aktuelle DB macht
  **kein** DDL-Replay beim Öffnen (Fastpath). Migration v6 remappt Alt-Prädikate → Keeper.
- **Seq-guarded Caches:** `_obj_cache`, `_place_cache`, `_rel_cache`, `_canvas_vid` —
  invalidiert über `(_seq, _ext_seq, total_changes)`, kein manuelles Cache-Management.
- **Bulk-Pfade:** `atomic()`/`batch()` (ein Commit statt N), `create_many`/`place_many`/
  `event_many` (Semantik = N× Einzelaufruf, ein Commit).
- **FTS-Optimierung:** `_fts_may_exist` überspringt teure DELETEs für Nicht-Notiz-Objekte.

## 7. Kernel (`core/kernel.py`) — detailliert

Der Kernel ist der **GUI-freie Geschäftskern**: dieselben Operationen laufen per Tastatur,
Chord, Workflow oder Skript — immer über die Registry. `kernel.call(op_id, …)` ist der
einzige Weg, Zustand zu ändern.

### 7.1 OperatorRegistry
- `Operator` = `{op_id, handler, label, group, token, scope, desc, requires}`.
- `register(op_id, **meta)` als Decorator; `call(op_id, *args, context=…)` prüft
  `requires`-Kontextschlüssel vor dem Aufruf.
- `all()`/`by_group()`/`find()`/`cheatsheet()` — automatisierbar (Cheatsheet-Generierung).

### 7.2 Graph-Operatoren (die gebauten)
| op_id | Wirkung | Token |
|---|---|---|
| `graph.spawn_node` | Zettel + Placement in einem Commit | `/steno-free` |
| `graph.spawn_relation` | Kante (mit EDGE_REMAP-Übersetzung) | `/steno-link` |
| `graph.transform_node_role` | Rolle ändern (in place) | `/steno-role` |
| `graph.transform_edge_predicate` | Prädikat ändern (in place) | `/steno-pred` |
| `graph.delete_placement` | Zettel aus Ansicht nehmen | `/steno-unplace` |
| `graph.tombstone_object` | Zettel verwerfen (Grabstein) | `/steno-scrap` |
| `graph.move_to_workspace` | In anderen Raum verschieben | `/steno-umzug` |

### 7.3 Semantik-Konstanten

**Prädikate: 10 = 9 Keeper + 1 Sonderfall** (commindv2-Stand, Migration v6):
- strukturell: `sys:child` (└), `sys:part_of` (◆), `sys:alternative` (∥), `sys:relates` (—)
- kausal: `sys:causes` (→), `sys:pipeline` (⟹)
- kognitiv: `sys:because` (∵), `sys:example` (ex), `sys:conflicts` (≠), `sys:replaces` (⤳ = Sonderfall)
- `EDGE_REMAP` biegt 8 Alttypen um (so_that→because, if_then→causes, deduces→because,
  trigger→causes, dataflow→pipeline, shared_bus→relates, feedback→pipeline,
  analog_to→alternative). `sys:replaces` hat **kein** Remap (Tombstone, kein Auto-Ziel).

**Rollen: 9** (statement, question, axiom, action, definition, code, **beleg, ziel,
entscheidung**). `comment` ist bewusst draußen (User). Die drei neuen Rollen fangen die
beim Kanten-Rework verlorenen Bedeutungen (so_that/if_then/trigger) als Zettel-Typen ab.

⚠️ steno Original: 18 Prädikate + 7 Rollen (inkl. `comment`). Alt-DBs mit `comment`-
Rollen laufen in commindv2 auf ungültige Rolle → fällt auf `statement` zurück (W4).

### 7.4 Settings, Profile, Bindings
- **Settings:** `define(key, default, min, max, kind, choices, group)` — 17 `motion.*`-
  Werte (duration/easing/reduced/Audio…). Gespeichert als Objekte (`kind=setting`/
  `profile_setting`), nur Abweichungen vom Default existieren. Wertecache für heiße Pfade.
- **Profile:** pro Workspace aktiv, überlagern Settings **und** Bindings. `diff(profil)`
  zeigt Abweichungen. Gedacht für "Maschine" vs. "Steno-Maschine".
- **Bindings:** Token→Operator, drei Ebenen `package < project < personal` mit Präzedenz;
  pro Profil überlagerbar. `winners()` = welche Belegung gewinnt.

## 8. Darstellung (`ui/`) — detailliert

Die Qt-Schicht zeigt den Graphen, nie eigene Daten. Alles wird aus dem Store projiziert.

### 8.1 App-Shell (`ui/app.py`)
- `MainWindow`: Canvas zentral, darunter Cmd-Zeile (`/steno-*`), darunter `WorkspacePanel`,
  Statuszeile. Start-Fokus bleibt auf dem Canvas.
- Verdrahtet: ChordFilter (globaler Event-Filter), WorkflowEngine (`wf_*`-Signale vom
  Canvas), Kartei-Dock (F9, rechts, **kein** Fenster — User-Vorgabe), Suche (Ctrl+F über
  FTS), Bild-Import (Ctrl+Shift+I).
- Teardown-Ordnung (Find-Segfault-Fix): `close_editors()` → Views → Pose speichern →
  ChordFilter entfernen → `store.close()`.
- `ensure_pixmap_cache()`: globaler QPixmapCache 1 GB (gemessen: 512 MB war zu knapp für
  große Arbeitsgebiete).

### 8.2 Canvas (`ui/views/canvas.py`)
- **Frustum-Instanziierung:** ferne Nodes werden **gar nicht** gebaut (kein QGraphicsItem,
  kein RAM) — nur sichtbare + Randzone (`_LAZY_MIN_NODES=1000`, `_LAZY_MARGIN=2500`).
  Placements bleiben in der DB, Pan/Zoom baut nach (kein Pop).
- **Spawn-Pfade:** `spawn_chain_down` (sys:causes, +220 y), `spawn_pipeline_right`
  (sys:pipeline, +320 x), `spawn_branch_child` (sys:child, +60/110), `spawn_free`
  (Mitte). `_free_spot` weicht bei Überlappung entlang der Spawn-Richtung aus
  (Chain/Free; Pipeline/Branch behalten Geometrie).
- **Editor-Sync:** `_on_edited` schreibt in Store **und** den `_db_objs`-Spiegel — sonst
  überschreibt der nächste Zoom den getippten Text aus dem veralteten Spiegel
  (Textverlust-Regression, User-Befund 20.09.).
- **Workflow-Signale:** `wf_node_created/edited/edge_created/selection_changed/
  role_changed/node_moved` werden bei jeder Mutation emittiert.

### 8.3 Nodes (`ui/views/nodes.py`)
- `ZettelNode` (QGraphicsObject): Label (`_StaticLabel`, Layout identisch zum Editor),
  Marker je Rolle, Inline-Editor (`_InlineEditor`, Return=speichern, Ctrl+Return=neue
  Zeile). Anzeige-Deckel 780 px / 25 Zeilen, Breite fix 240. Metrics-Cache für QFont.
- `ImageNode` (Subklasse): Pixmap statt Text, erbt Selektion/Drag/Culling. Eigener LRU
  (120 Einträge), Decode auf Anzeige×2, Deckel 2048 px — **nicht** im globalen QPixmapCache
  (würde Item-Raster verdrängen = FPS-Einsturz, gemessen).

### 8.4 Edges (`ui/views/edges.py`)
- `EdgeItem` (QGraphicsPathItem): 9+1 Formen, Farbe + Vektor-Marker je Keeper
  (`EDGE_STYLES` in `ui/style.py`). **Keine Hitbox, nicht selektierbar** (User: Kanten nie
  im Weg). Bearbeitung läuft über die Endpunkt-Zettel (Ctrl+D auf 2 Selektion).
- Elbow-Override (3 gerade Segmente) pro Kante. Kanten werden **lokal** gemalt
  (±32767-Guard für die GL-Engine). Kurze Kanten gecacht, lange NoCache.

### 8.5 Viewport (`ui/views/viewport.py`)
- Kamera: Pan (Freihand/Drag), Zoom (Anker-zentriert, 0.05–1.5), `fly_to` animiert
  (OutCubic), `_hop` zum nächsten Zettel im Sektor, Pose pro Raum persistiert.
- **LOD + Hysterese:** ≥0.45 Volltext, 0.35–0.45 Silhouette, 0.2–0.35 Farbblöcke,
  <0.2 Blöcke ohne Kanten; Rahmen-Schwelle; Kanten-Hysterese (an 0.35 / aus 0.33).
- **Culling-Grid:** 4000-px-Zellen, Sichtbarkeit pro Kamera-Tick über sichtbare Zellen.
- **Tastatur:** Ctrl+Z Undo-Verwurf (Tombstone zurück), Ctrl+D Kante löschen, Ctrl+K Karte
  anlegen, Entf/Backspace verwerfen, Ctrl+A alles.

### 8.6 Media (`ui/media.py`)
- Bildimport: Datei → `media/<hash>.<ext>` (Inhalt-Hash, gleiche Bilder teilen Datei),
  `import_image` erzeugt `kind=image`-Objekt + Placement. `get_pixmap` dekodiert gedeckelt
  (LRU). Fallback bei fehlender Datei: Farbblock.

## 9. Workflow-Denksystem — detailliert

Das Denksystem von commindv2 besteht aus zwei Ebenen: der **Workflow-Engine** (aktivierbare
Denkmethoden als Code) und der **kognitiven Grundstruktur** (Graph + Kanten + Rollen als
Denkraum). Die Engine ist ein bewusst schlankes Plugin-System — kein Framework, kein DSL,
sondern Python-Klassen mit Hooks.

### 9.1 Architektur

```
Canvas-Events (Qt-Signale)
  → MainWindow._wf_* (Adapter, siehe ui/app.py:206-259)
    → WorkflowEngine.on_* (Dispatch, nur wenn Workflow aktiv)
      → <Workflow>.on_* (Benutzercode in workflows/<name>.py)
        → WorkflowContext (Observe + Act API)
          → Kernel → Store (Graph-Mutationen)
```

**Nur ein Workflow gleichzeitig aktiv.** `WorkflowEngine.deactivate()` räumt auf, der
nächste `activate()` startet frisch. `WorkflowState` ist ein leeres Dict, das der Workflow
selbst füllt — kein persistenter State über Sitzungen hinweg.

### 9.2 WorkflowContext — die API

**Observe** (was der Workflow lesen darf):
- `get_nodes()` → alle `note`-Objekte im Workspace (mit Attributen).
- `get_edges()` → alle lebenden Relationen.
- `get_selection()` → IDs der selektierten Nodes (via Canvas).
- `get_viewport()` → `{zoom, center_x, center_y, frustum}`.
- `get_cursor_pos()` → letzte Szenen-Position oder None.
- `get_node_position(oid)` → `(x, y)` aus Canvas oder Placement-DB.

**Act** (was der Workflow tun darf):
- `spawn_node(x, y, content, role)` → erzeugt Zettel via `graph.spawn_node`, gibt Dict
  mit Attributen zurück.
- `spawn_edge(source, target, predicate)` → erzeugt Kante via `graph.spawn_relation`.
- `set_role(oid, role)` → ändert Zettelrolle.
- `prompt(message, options)` → interaktive Abfrage (Callback oder Fallback: erste Option).
- `highlight_nodes(oids, color)` → selektiert Nodes visuell (kein neuer Render-Pfad).
- `show_annotation(oid, text)` → Text in der Statuszeile.

**Layout-Helfer** (reine Mathematik, kein Qt):
- `layout_arc(center, count, radius, angle_start, angle_end)` → Halbkreis.
- `layout_radial(center, count, radius)` → Vollkreis.
- `layout_grid(origin, count, cols, spacing)` → Gitter.
- `layout_vertical(origin, count, spacing)` → Spalte.
- `layout_horizontal(origin, count, spacing)` → Zeile.

### 9.3 Event-Hooks (nur bei aktivem Workflow)

| Hook | Wann | Typischer Anwendungsfall |
|------|------|--------------------------|
| `on_node_created(node, ctx, state)` | Neuer Zettel | Struktur-Spawns (Ideen-Slots, Prüf-Fragen) |
| `on_node_edited(node, old, new, ctx, state)` | Text geändert | Reaktion auf Inhalte (z.B. "Idee N" → echt) |
| `on_edge_created(edge, ctx, state)` | Kante gezogen | Konflikt-Erkennung, Auflösungs-Spawn |
| `on_selection_changed(old, new, ctx, state)` | Auswahl geändert | Auto-Cluster bei Mehrfachauswahl |
| `on_role_changed(node, old, new, ctx, state)` | Rolle geändert | Reaktivierung (z.B. Frage→Statement) |
| `on_node_moved(node, old, new, ctx, state)` | Verschoben | Layout-Anpassungen |
| `on_keystroke(key, mods, ctx, state)` | Tastendruck | Workflow-eigene Tastenkürzel |
| `on_idle(duration, ctx, state)` | User idle | Timer-basierte Interventionen |

### 9.4 Die drei Module

**Brainstorm** (`workflows/brainstorm.py`):
- `on_node_created`: Rolle `question` → 5 `statement`-Slots im Halbkreis darunter
  (radius 400, ±60°), Kanten `sys:child`.
- `on_selection_changed`: ≥3 selektierte `statement`-Nodes → Auto-Cluster-Parent oben
  (Durchschnittspunkt - 200 y), `sys:child`-Kanten zu allen.
- `on_node_edited`: "Idee N" → echter Text → Zähler `idea_count`.
- State: `idea_count`, `cluster_count`.

**Kritisch** (`workflows/kritisch.py`):
- `on_node_created`: Rolle `statement` → 3 Prüf-Zettel rechts (Frage-Rolle):
  "Beweis?" (`sys:because`), "Gegenargument?" (`sys:conflicts`), "Quelle?" (`sys:relates`).
- `on_edge_created`: Prädikat `sys:conflicts` → "Auflösung?"-Knoten darunter, verbindet
  beide Konflikt-Enden mit `sys:child`.
- `on_role_changed`: Frage→Statement → erneute Prüfung.
- State: `statements_challenged`, `conflicts_spawned`.

**FirstPrinciples** (`workflows/firstprinciples.py`):
- `on_node_created`: Rolle `statement`, Inhalt >20 Zeichen → 3 "Annahme?"-Nodes horizontal
  darunter + 1 "Implikation?"-Node oben, Kanten `sys:causes` von Annahmen zur Implikation.
- `on_node_edited`: Annahme ausgefüllt → Prüfung ob "fundamental" (kein "und"/"oder"/
  Komma = kein weiterer Zerlegungsbedarf).
- `on_selection_changed`: 3 selektierte `definition`-Nodes → "Merge-Kandidat" als Parent.
- State: `decompositions`, `assumptions_total`.

### 9.5 Persistenz

- `core/workflows.py`: `store.workflows.json` neben der DB speichert **nur** den aktiven
  Workflow-Namen (`{"active": "brainstorm", "items": {}}`). Die Module selbst leben als
  Dateien in `workflows/` — Anlegen/Löschen = Datei anlegen/entfernen (kein UI-Editor).
- `WorkflowEngine.load_workflow(name)` → `importlib` lädt `workflows/<name>.py`, erwartet
  Klasse `<Name>Workflow` (Konvention: `brainstorm` → `BrainstormWorkflow`).
- Abwärtskompatibilität: `core/workflows.py` hat noch `create/toggle/delete` für die alte
  JSON-Template-API — wird von der UI nicht mehr benutzt, nur von Tests.

### 9.6 Grenzen (bewusst)

- **Kein DSL, kein YAML, kein visueller Editor.** Workflows sind Python-Code.
- **Keine persistente Workflow-DB.** Der Graph selbst ist der Persistenz-Layer.
- **Keine KI-generierten Workflows** (geplant M7+, siehe `WORKFLOWS.md`).
- **Keine automatische Bedeutungszuweisung.** Workflows spawnen neue Zettel, editieren
  aber nie bestehende Inhalte (Vertrag aus `WORKFLOWS.md`).
- **Nur ein Workflow gleichzeitig.** Parallelität erzeugt Chaos (Spawn-Konflikte).

---

## 10. Lernsystem (Kartei) — detailliert

**Gesamtumfang (User-Entscheid 25.09.): volles Lernsystem, aber gefiltert.** Das bedeutet:
- **Karten sind nicht auf zwei Zettel beschränkt.** Eine Karte kann 2..n Zettel berühren;
  beim Wiederholen deckt man sie **nacheinander** auf (nicht alles auf einen Schlag).
- **Free Recall** (leere Seite gegen den Graphen), **Interleaving**, **Pretest**,
  **Schlaf-Queue** etc. gehören zum System — sie sind vorhanden oder als geerbte Module
  dokumentiert (steno `apps/kartei/`, siehe 10.7/11).
- **Manuell alles:** Membership (welche Zettel in einer Karte), Verdeckte je Zettel,
  Bewertung, Freigabe, Verwerfen — nichts davon automatisch erzwungen.
- **FSRS ist nur ein Teil** des Lernsystems: die Terminierung/Schwierigkeit. Ersetzt nicht
  die Konstruktion der Karten (n Zettel, schrittweises Aufdecken) und nicht die
  Abrufmethoden (Free Recall, Pretest …).

> Code-Stand-Hinweis: commindv2 hat bisher nur den FSRS-Frage-Karten-Kern portiert
> (`add_question_card`, Session mit bool-UI). Der **Systemumfang** ist breiter — jedes
> Bauteil unten trägt `[GEBAUT]` (läuft in commindv2) oder `[GEERBT]` (existiert in steno,
> hier als Teil des Gesamtsystems dokumentiert, noch nicht angebunden).

Das Lernsystem ist die **Konsolidierungsschicht** — es fragt ab, spaced-repetition-t den
Graphen und gibt Reparaturaufträge zurück. Zwei strikt getrennte Datenbanken: der Graph
wird nur gelesen, der Lernstand lebt separat.

### 10.1 Datenmodell (`core/kartei_db.py`)

**Kern des vollen Lernsystems: eine Karte = eine Sicht auf 2..n Zettel, schrittweise
aufdeckbar.** Das Datenmodell trägt das bereits — die UI (Port-Stand) nutzt es bisher nur
für den Zwei-Zettel-Fall.

**`cards`** — eine Karte:
- `kind`: `"frage"` (Frage→Antwort, kanonisch 2 Zettel) **oder** `"region"`
  (Graph-Ausschnitt mit **beliebig vielen** Zetteln) — und im vollen System zusätzlich
  `"kante"` (Rate-Kante) und `"vorwissen"` (Schlaf-Queue, siehe 10.7).
- `question_oid` / `answer_oid`: Object-IDs im Graph (bei `frage`; Kante: Quelle/Ziel).
- `region` (JSON: x/y/w/h) + `form` (`"kontext"`/`"gegend"`): bei `region`-Karten der
  Ausschnitt. Die **Zugehörigkeit** von Zetteln zum Ausschnitt wird live aus dem Store
  aufgelöst (siehe `resolve_membership`), nicht eingefroren.
- `stage`: Fading-Stufe (2=Gegend-Raten, 1=Kontext, 0=Einzelfrage); Erfolg senkt,
  Misserfolg erhöht. Steuert, **wie viel** beim nächsten Mal sichtbar ist.
- `suspended`: Leeche-Flag (ab 3 Resets).
- `deleted`: Tombstone (Karte verschwindet aus Sichten, History bleibt).
- `frage_text`: selbst formulierte Frage (Generation Effect, überschreibt Zettel-Text).

**`card_items`** — die zur Karte gehörenden Zettel:
- Für **Region-/n-Zettel-Karten**: `oid` je Zeile, `hidden=1` = noch verdeckt.
- Das ist der Mechanismus für **nacheinander aufdecken**: pro Item ein `hidden`-Bit,
  nicht ein globales Aufdecken. (Im Port rendert `CardScene.reveal()` alles auf einmal —
  das schrittweise Aufdecken ist Teil des vollen Systems, aber noch nicht im Port.)
- Membership der Ausschnitt-Zettel kommt zur Abfragezeit live aus dem Store.

**`schedule`** — FSRS-Zustand:
- `due` (ISO-Datum), `interval` (Tage), `resets`, `last_review`.
- `stability` / `difficulty` (FSRS DSR-Modell, v2.3.0).

**`history`** — eine Zeile pro Bewertung: `reviewed` (ISO-Datum) + `result` (Grade 1–4).
Wird **nie** gelöscht (Trainingsdaten für FSRS-Optimizer).

**`inbox`** — Merkliste für externes Wissen (Quelle, Datum, Seite); Einbau manuell in der
Workbench.

**`kartei_events`** — Mini-Event-Log analog zum Graph-Substrat.

### 10.2 FSRS-Scheduler (`core/kartei_scheduler.py`)

- **FSRS** (Free Spaced Repetition Scheduler) über das Paket `fsrs` — DSR-Modell
  (Difficulty, Stability, Retrievability).
- **Target Retention:** 0.9 (90 % Abrufwahrscheinlichkeit als Ziel).
- **Grade 1–4:** 1=wieder, 2=knapp, 3=gut, 4=leicht. Bool-Rückwartseingang:
  `False→Again`, `True→Good`.
- **Tagesgranularität:** keine Steps, kein Fuzzing — Fälligkeiten fallen auf ganze Tage.
- **Leech-Erkennung:** ab `LEECH_RESETS=3` Resets → `suspended=1`, Karte wird nicht weiter
  gedrillt, sondern als Reparaturauftrag zurück in den Graphen gegeben.
- **Leech-Heilung:** 3 aufeinanderfolgende Erfolge über ≥2 Tage (`LEECH_RELEARN_N=3`,
  `LEECH_VERJAHR=30`). Ein Reset nach 30 Tagen Ruhe wird verjährt.
- `review_state(stability, difficulty, last_review, today, grade)` → neuer
  `{stability, difficulty, due, interval}`.

### 10.3 Session (`core/kartei_session.py`)

Der Ablauf im **vollen Lernsystem** (User-Entscheid 25.09. — "deck ich nacheinander auf",
"manuell alles"):

1. `start()` → Queue = fällige Karten des Tages (FSRS-Terminierung). Im vollen System
   zusätzlich: Schlaf-Queue voranstellen, Interleaving mischt gebietsnah (10.7).
2. Karte zeigen → **nacheinander aufdecken**: jedes verdeckte Item (Antwort-Zettel,
   verdeckte Zettel eines Ausschnitts) einzeln sichtbar machen — nicht alles auf einen
   Schlag. Jeder Schritt ist ein eigener Abruf-Reiz. (Port-Status: `reveal()` deckt alles
   auf einmal auf — `core/kartei_session.py`/`CardScene.reveal`; schrittweises Aufdecken
   steckt schon im `hidden`-Bit je `card_items`-Zeile, ist aber in der UI noch nicht
   bedienbar.)
3. Zwischen den Schritten: optional **Elaborations-Nudge** ("Warum gilt das?",
   "Was wäre das Gegenbeispiel?" …) — rein mental, Taste = weiter, nie Pflicht.
4. `rate(grade)` → FSRS-Update → nächste Karte. **Grade 1–4** (1=wieder … 4=leicht);
   bool bleibt Rückwartseingang. Die Port-UI bietet nur 2 Buttons, das Modell kann 4.
5. `abort()` → Queue leeren, Rest bleibt fällig.

**Manuelle Steuerung (Pflicht des vollen Systems):**
- Membership: welche Zettel gehören in eine Karte, welche werden verdeckt — per Hand.
- Pro Schritt entscheiden, ob und was aufgedeckt wird.
- Bewertung 1–4, Freigabe, Verwerfen jederzeit.
- Kein Schritt ist automatisch erzwungen; das System bietet an, der User führt aus.

**FSRS = nur Terminierung/Schwierigkeit.** Es ersetzt weder die Kartenkonstruktion
(n Zettel, schrittweises Aufdecken) noch die Abrufmethoden (Free Recall, Pretest).

### 10.3b Abrufmethoden (Teil des vollen Systems)

Neben der klassischen Karten-Wiederholung (cue → recall → rate) gehören zum vollen
Lernsystem weitere Abrufwege — in steno als Module vorhanden (`apps/kartei/`, 10.7/11),
in commindv2 als Gesamtumfang dokumentiert:

- **Free Recall** (`free_recall.py`) `[GEERBT]`: "Schreib alles auf, was du weißt" auf einer
  leeren Seite → token-basierter Diff gegen den echten Graphen → Lückenliste. Stärkster
  Abrufmodus (Karpicke & Blunt 2011). Keine Bewertung, kein Eintrag — Diff als Spiegel.
- **Pretest** (`pretest.py`) `[GEERBT]`: Ausschnitt blind abfragen (als "Gegend"), erst
  rekonstruieren, dann aufdecken — **ohne** Lerneintrag (Vorwissen-Check, Bjork
  Pretesting).
- **Schlaf-Queue** (`schlaf.py`) `[GEERBT]`: gestern erfasste Zettel mit Substanz-Rolle,
  die noch in keiner Karte stecken → als Pre-Test vor dem fälligen Stapel.
- **Kanten-Karte** (`add_kante_card`, M9) `[GEERBT]`: zwei Zettel mit verdeckter Kante,
  Rate-Hypothese als `sys:alternative`, Reveal zeigt die echte.
- **Pfad→Text / vertiefung** (`vertiefung.py`, S5) `[KONZEPT/GEERBT]`: aus Lücken wird ein
  Weg durch den Graphen, daraus ein Dichte-Satz — der Output-Test.

Vertrag aller Abrufmethoden: **Recall passiert im Kopf, eingetippt wird höchstens die
Bewertung.** Keine Punkte, keine Streaks, kein Gamification-Score.

### 10.4 Live-Reader (`core/kartei_reader.py`)

- **Read-Only** auf `store.sqlite3` (URI `mode=ro`, WAL-lesend, `busy_timeout=2000`).
  Schreibversuche scheitern hart (`PRAGMA query_only=1`).
- `resolve_membership(card, reader)` → `{present: [...], gaps: [...]}`:
  - Gelöschtes Element → Lücke (nie Fehler).
  - Neues Element → nur durch explizites Hinzufügen in `card_items`.
- `card_oids(card)` → alle referenzierten Object-IDs (Frage/Antwort + Items).

### 10.5 Karten-Renderer (`core/kartei_renderer.py`)

Drei Darstellungsmodi:
- **VOLL** (Frage): Text, Marker, Rahmen — wie der Canvas.
- **HUELLE** (Kontext): Rahmen + Farbe, kein Text — verdeckte Antwort.
- **BLOCK** (Gegend): nur Farbblock, kein Rahmen — Fernzoom-Optik.

`CardScene` baut echte `EdgeItem`s (keine Neuerfindung), `reveal()` schaltet alles auf VOLL.
`lege_hypothese(predicate, src, tgt)` legt eine `sys:alternative`-Kante (bleibt nach
falscher Rate sichtbar). **Der Port ist fertig, das Kartei-Fenster nutzt ihn aber noch
nicht** (Widerspruch W3-Umfeld).

### 10.6 Karten-Erzeugung heute

- **Ctrl+K auf zwei selektierte Zettel** (`ui/views/viewport.py:1087-1119`):
  erster nach Platzierungsordnung = Frage, optional `frage_text` (Generation Effect).
- **F9** öffnet das Kartei-Dock (`ui/kartei_window.py`): Space = aufdecken, 1 = gewusst,
  0 = nochmal. Nur bool, obwohl Scheduler 4 Grade kann (Widerspruch W3).

### 10.7 Geerbte Lernmodule (steno `apps/kartei/`) — Teil des vollen Systems

Diese 18 Module gehören zum Lernsystem-Gesamtumfang. commindv2 hat bisher nur den Kern
portiert (Kapitel 10.1–10.5); hier die Vollliste mit Rolle im Gesamtsystem:

**Karten-Konstruktion (manuell alles):**
- `overview.py` / `enroll_dialog.py` — **Anlegen**: Raum wählen, Ausschnitt ziehen,
  Zettel anklicken = verdecken, Frage/Anweisung frei formulieren, Karte speichern.
  Membership komplett per Hand. `[GEERBT]`
- `sammlung.py` — **Verwaltung**: Kartenliste (Art, Raum, Fälligkeit, Intervall, Resets),
  Leech-Radar + Freigabe, Inbox-Merkliste für externes Wissen. `[GEERBT]`
- `kartei_db.py` hat im Original zusätzlich `add_region_card`, `add_kante_card`,
  `add_vorwissen_card` (im commindv2-Port fehlen diese drei Create-APIs).

**Abrufmethoden:** `session.py` (volle Session: Schlaf-Queue voran, Interleaving,
Hypothesen-Kanten, Grade-4, Nudges), `free_recall.py`, `pretest.py`, `schlaf.py`
(LIMIT 20, Substanz-Rollen axiom/definition/question), `inkubation.py` (Schläfer 14d,
Denkwärme, Promenade), `abendsweep.py` (offener Rest des Tages), `vertiefung.py`
(Lücken→Pfad), `kalibrierung.py` (R(t,S) vs. real, Fenster 1/3/7/14).

**Terminierung/Ordnung:** `scheduler.py` (FSRS, identisch zum Port), `interleaving.py`
(Jaccard-Cluster über gemeinsame Zettel, SIM_MIN 0.3, Kontrast-Nachbarn, Duplikat-Streuung
statt Blöcke), `renderer.py` (identisch zum Port).

**Bedienung per Akkord:** `chords.py` (9 `/karte-*`-Tokens: weiter/1/2/3/4, anlegen,
fertig, heute, schlaefer), `embed.py` (Drawer/Modal/Canvas-Player-Einbettung).

**Manuelle Prinzipien (gelten fürs ganze Lernsystem):**
- Karte = Sicht, nie Kopie (USER-INPUTS Prinzip 28): gelöschtes Element → Lücke, neues nur
  per explizitem Hinzufügen.
- Recall im Kopf, Bewertung ist der einzige Input.
- Leech ≠ scheitern: Reparaturauftrag in den Graphen (aufspalten, umformulieren, Beispiel),
  kein endloser Drill.
- Vergessen ≠ widerlegt: getrennt loggen.
- Kein JOL, keine Kalibrierungs-Anzeige (nur Scheduler-Diagnose im Log), kein Score.

## 11. stenoQT Original (`~/Projekte/steno`) `[GEERBT]` — detailliert

stenoQT ist die **Grundschicht**: Workbench (v1.4.x) + Kartei (v2.0.x), 685 Tests,
SQLite unter `.steno-data/`. commindv2 ist zu großen Teilen ein Port daraus — daher ist
stenoQT die wichtigste Quelle für "was kann das System eigentlich schon".

### 11.1 Aufbau

```
steno/
  core/    store.py (9 Primitives), kernel.py (Ops/Settings/Profile/Bindings),
           cue.py, wander.py, paths.py, workspace_io.py
  ui/      app.py (MainWindow, Overlays, Cheatsheet, Tutorial, Settings/Types),
           views/canvas.py (~2560 Z., ZettelNode/ImageNode/Kamera/LOD/Culling),
           views/edges.py (~500 Z., 18 Stile), chords.py (86 Tokens + 9 Kartei),
           media.py, style.py, workspace.py, guards.py, theme.py,
           + tutorial_panel, cheatsheet, record, stream_view, presets, types_panel,
             settings_panel, power, bg_test
  apps/kartei/  18 Module (Lernsystem, siehe 10.7)
  tools/   Benchmarks, Migrationen, Cheatsheet-Generator, Live-Messung, Skripte
  docs/    HANDBUCH (602 Z.), CHORDS, CHEATSHEET, plover/ (Dicts), archiv/
  tests/   685 Tests (Workbench + Kartei, offscreen)
```

### 11.2 Was commindv2 übernommen hat (Port)
- **Core komplett:** `store.py` (Verbatim, +Schema v6), `kernel.py` (Verbatim,
  +9+1 Prädikate/9 Rollen), `paths.py` (nur `DATA_DIR` geändert), `workspace_io.py`,
  `cue.py`/`wander.py` (implizit, da Teil des Core-Pakets).
- **UI-Schnitt:** `app.py` (M1-Schnitt), `views/canvas.py` (2560 → M1/M2/M5-Schnitt),
  `views/viewport.py` (2098 → M1), `views/nodes.py`, `views/edges.py` (Verbatim),
  `chords.py` (Verbatim Atlas-Tabelle), `style.py`, `media.py`, `workspace.py`,
  `guards.py`, `theme.py`.
- **Kartei-Schnitt:** `kartei_db.py`, `kartei_reader.py`, `kartei_scheduler.py`,
  `kartei_session.py` (reduziert), `kartei_renderer.py`.
- **Ideen:** Karten-Modell (Karte=Sicht, Live-Referenz), Tombstones, FSRS, Leech-Prinzip,
  LOD/Culling, Frustum-Instanziierung.

### 11.3 Was stenoQT zusätzlich kann (in commindv2 fehlt/ist reduziert)
- **Volles Kartei-App** (18 Module, siehe 10.7): Anlegen-UI, Sammlung, Schlaf-Queue,
  Interleaving, Pretest, Free Recall, Vertiefung, Kalibrierung, Canvas-Player,
  `/karte-*`-Akkorde.
- **18 Prädikate + 7 Rollen** (vor dem commindv2-Rework 9+1/9).
- **Vollständige Token-Oberfläche:** 95 Tokens (86 + 9 Kartei) — commindv2 hat nur einen
  Teil verdrahtet.
- **Overlays:** Liste, Gliederung, Netz, Matrix — getrennte Blicke auf denselben Graphen.
- **Tutorial** (F1, 10 Kapitel, 36 Schritte), **Cheatsheet** (auto-generiert),
  **Types-Panel**, **Settings-Panel**, **Lesezeichen-Panel** (Gruppen, Tasten 1–9).
- **Pfade/Trails** (Navigationslinien mit Stationen), **Umzug-Dialog**, **Telemetrie-Log**
  (`.steno-data/telemetry.log`, JSON alle 2 s).
- **Undo/Redo-System**, **Kanten-Transplantate** (`EDGE/S|H|L` — aufheben/reisen/ablegen),
  **Elbow-Toggle**, **Ideen-Blitz** (`PWE*UTS`), **Kamera-Historie** (50 Orte).
- **Perf-Methodik:** interleaved Median, Telemetrie pms/pmax, A/B-Benchmarks in GUIDE.md,
  Perf-Gates (warm≤130, Zoom≤130, Schwenk≤85, Anlegen≤300 ms, RAM≤1 GB).

### 11.4 Grenzen von stenoQT (bewusst)
- Stationär, Ein-/Aus-gedacht (INSTRUMENT.md): Graph ist Speicher, kein Medium.
- Stift/Skizze (`kind=sketch`) fehlt komplett.
- Kein Output (Text-Generierung) — nur Export-Dump.
- `core/cue.py`: `stagnation`/`hubs` ohne Produktionscaller (nur Tests), nur
  `kontrast_paare` verdrahtet.

## 12. denken (`~/Projekte/denken`) `[GEERBT/KONZEPT]` — detailliert

denken ist die **Methoden-/Konzeptquelle**: Denksprache, kognitive Handles, Prüfmethoden
(Fünf Pfeile, Isomorphie-Check, Interventionen) plus kleine lauffähige Prototypen. Nichts
davon ist in commindv2 als Modul angebunden — es ist die Wissensbasis, aus der die
commind-Konzepte gefiltert wurden.

### 12.1 Dokumente (Methoden-Kanon)
- **`docs/DENKSPRACHE.md`** — Concept Handles (Cowan 4-Chunks: Name = 1 Chunk), TAE-Mini-
  Protokoll (5 Min: vage → Felt-Sense → Kunstwort → definieren), 12 Starter-Handles
  (Inferenzdistanz, Moloch, Double-Crux, Steelmannen, Felt-Sense, TAE-Schritt,
  Requisite Variety, Feedback-Loop, Emergenz, Gestalt-Kipp, Zuhanden/Vorhanden,
  Isomorphie), Notation als Denkzeug (Iverson).
- **`docs/HANDLES-20.md`** — 20 Handles mit Isomorphie-Bezug.
- **`docs/NOTATION-CATEGORY.md`** — Iverson (Notation denkt mit), Kategorie-Mini-Crash
  (Objekt/Morphismus/Funktor/Isomorphie), 5 deutsche Handles (Denkzeugschrift,
  Zuhandenheitskippe, Funktorbrücke, Umkehrgriff, Schleifenblick).
- **`docs/FLUID.md`** — Anti-Klammern-Prinzip: Handles sind Hypothesen mit Verfallsdatum
  (14 Tage ohne 3 Nutzungen → Archiv), max 5 aktiv, wöchentlicher Fluid-Loop (messen,
  killen, kreuzen, ersetzen, Notation prüfen).
- **`docs/TAKT-1..36`** — Zyklus-/Eingriffs-/Drift-Protokolle (Brücken-Score,
  Gegenresultat, Decision-Window, Drift-Regression, Fünf-Pfeile-Check).
- **`docs/SCIENCE-01/02/03`** — quellenbelegte Forschung:
  - 01 Embodied/Extended/Focusing (Varela, Thompson, Lakoff, Barsalou, Jirak, Clark/
    Chalmers, Goldin-Meadow, Gendlin-TAE).
  - 02 Sprache→Gedächtnis (Boroditsky, Winawer, Lupyan, Chen, Miller→Cowan 4,
    Ericsson Deliberate Practice, Gollwitzer Implementation Intentions d=0.65).
  - 03 Systeme/Cybernetics (Ashby Requisite Variety, Wiener, Beer VSM, Meadows Leverage,
    Goodhart/Campbell, Schelling, Ostrom, Moloch).
- **`docs/DENKSPRACHE.md` + `book/`** — 14 Kapitel + BAUPLAN (Buch laut commind als
  `[ARCHIV]` gestrichen), `buch/` (HTML-Builder), `report/` (PDFs).

### 12.2 Lauffähige Prototypen (`src/`, browserbasiert)
- **`concept-graph/`** — `relations.js` (~29 Funktionen) + `index.html`:
  `relationKind`, `decisionWindow`, `bufferCoverage`, `feedbackCoverage`,
  `learningLoopCoverage`, **`isoCheck`** (9 Pflichtfelder: source/target/form/direction/
  bottleneck/feedback/loss/breaks/check), **`bridgeScore`** (0–100),
  `bridgeOutcome`, `bridgeTrialSummary`, `bridgePortfolio`, `bridgePriority`,
  **`interventionPlan`** (5 Felder: form/spot/dose/feedback/stop, Dosis≤15min),
  `interventionOutcome`, `interventionDispatch`, `interventionCycle`,
  **`fiveArrowCheck`** (felt/handle/form/intervention/feedback → `firstBreak`).
- **`five-arrows/`** — interaktiver Fünf-Pfeile-Check.
- **`causal-loop/`** — Causal-Loop-Diagramm-Editor (Nodes/Edges ±, R/B).
- **`iso-board/`** — Isomorphie-Tabelle (Muster/Psyche/Software/Alltag, Umkehrbarkeit).
- **`apl-mini/`** — APL-Minikompressor (+/ , +scan, reshape, reverse, max/min).
- **`tae-timer/`** — TAE-6-Minuten-Timer mit Schritt-Log.

### 12.3 Tests (`tests/`, 32 JS-Dateien)
`five-arrow*.test.js` (Decision/Trial/Board/Drift/Repair/Batch/Cycle/Summary),
`intervention-*.test.js` (Plan/Action/Priority/Dispatch/Outcome/Summary),
`bridge-*.test.js` (Score/Outcome/Portfolio/Priority/Action/Summary),
`iso-check`, `learning-loop`, `dense`, `feedback-edge`, `buffer-edge`,
`decision-window`, `handles`, `relations`. — Alles reine Funktionen mit Unit-Tests.

### 12.4 Bezug zu commindv2
- **Konzeptionell** gefiltert nach commind (`docs/KONZEPTE.md`, `AUSGANGSLAGE.md`).
- **Nichts davon ist im commindv2-App-Code** — Fünf Pfeile, isoCheck, bridgeScore,
  Interventionen leben nur als Methode/Denkmodell. Einziger realer Ankoppelungspunkt wäre
  ein Workflow, der diese Checks einsetzt (Kapitel 9).
- FLUID-Verfallsprinzip, Namen statt Handles, Gegenfall-nur-im-Workflow — sind in den
  commind-Kanon übernommen worden.

## 13. Kognition & Konzepte (aus `../commind/docs/`) `[KONZEPT]` — detailliert

commind hat die kognitive Wissenschaft gefiltert und in Bauteile übersetzt. Diese Ebene
erklärt, **warum** das System so gebaut ist.

### 13.1 Die Grundasymmetrie (`AUSGANGSLAGE.md:9-23`)
Mensch: ~4 aktive Chunks (Cowan), verliert sie in Sekunden. Rechner: verliert nichts, weiß
aber nicht was wichtig ist. **COMMIND arbeitet auf dieser Naht in eine Richtung: der
Computer entlastet das Hirn, das Hirn entscheidet über den Computer.** Nicht "mehr
speichern", sondern Asymmetrie nutzen.

### 13.2 Die 7 Kanäle (`AUSGANGSLAGE.md:26-40`)
| # | Kanal | Hirn-Limit | Computer-Hebel | Gewinn |
|---|---|---|---|---|
| 1 | verbal | 4 Chunks | Capture <2s, Volltextsuche, Tombstones | kein Ideenverlust |
| 2 | räumlich | serieller Engpass | Canvas, LOD, Marker, direkte Bearbeitung | Muster sichtbar |
| 3 | relational | Nähe=Wahrheit | explizite Kanten, 1 Kante=1 Cue | falsifizierbare Netze |
| 4 | motorisch | Vages sagbar | Skizze, Lasso, Form vor Sprache | Gekritzel→Knoten |
| 5 | temporal | Vergessenskurve | FSRS, Pretest, Spacing | Können statt Bekanntheit |
| 6 | metakognitiv | Sicherheitsgefühl lügt | Anki-Grade, Scheduler-Diagnose | verlässliche Prognose |
| 7 | dialogisch | privates Verständnis | Pfad→Text, fremde Domäne | angreifbare Artefakte |

Kanalzahl 7 ist Hypothese; Limits je Quelle belegt.

### 13.3 Die 9 Konzepte (`KONZEPTE.md`) — Bauteil + Beleg + Schaden
1. **Kontrast statt Inhalt** — Rohstoff da (embed/interleaving), Kartenform fehlt. Gut
   belegt (Brunmair & Richter g=0.42).
2. **Vorhersage vor Verbindung** — fehlt (Pretest für Karten da, für Kanten nicht).
   Kalyuga Expertise-Reversal: nur mit Vorwissen.
3. **Begründung = Lernwürdigkeit** — **gebaut** (Rollen steuern Warteschlange). Chi,
   Slamecka.
4. **Zweite Darstellung** — teilweise (LOD, Bild-Zettel); bewusstes Umschalten fehlt.
   Paivio Dual Coding.
5. **Lücke als Objekt** — Liste gebaut (free_recall), Objektstatus fehlt.
6. **Material kommt zurück** — **gebaut** (Scheduler, Schlaf-Queue, Promenade). Spacing.
7. **Grenze mitgeführt** — nur Workflow-Doku, kein Bauteil.
8. **Beerdigung mit Grund** — Substrat gebaut (Tombstones + Events), Protokoll-Form offen.
9. **Gedankenpalast** — Nutzungs-Eigenschaft des Canvas, nicht als Feature gebaut.

Bilanz: 2 gebaut, 3 mit Rohstoff, 3 fehlend, 1 Eigenschaft.

### 13.4 Die 11 Spielzüge (Open World, keine Missionen)
Erfassen · Entlasten · Verknüpfen · Benennen · Workflow-Schritt · Dosieren · Abrufen ·
Schreiben/Entscheiden · Rückschauen · Beerdigen · Pausieren — **keine Reihenfolge, keiner
Pflicht**. Verbotene Züge: Gefühle beweisen, Karten glauben, Personen scoren, bei Gefahr
testen, Metriken vergöttern.

### 13.5 Latenz als Kognition (`INPUT.md:26-29`)
Hover <10 ms · Preview <30 ms · Commit <100 ms · LOD-Gate 130 ms. **>300 ms bricht
Handlungen ab** (Tetris-Lektion: wer beim Ziehen wartet, hört auf zu ziehen).

### 13.6 FAN-Methoden (5, `FAN.md`)
Budget variieren · volle Verteilung + Entropy · JS-Divergenz · Noise Ceiling · kausales
Tagging. Übertragung auf Kanten/Karten als Hypothese.

### 13.7 INSTRUMENT (`INSTRUMENT.md`) — Abacus statt Google
Das Werkzeug soll das Denken **umbauen**, nicht nur assistieren. 5 Bedingungen:
Operation begrifflich+motorisch · Grammatik aus kleinen Einheiten · Raum als Ort ·
kontinuierlich unter der Nachdenkschwelle · eine Dimension komprimieren, eine opfern.
Hoher Lernaufwand erwünscht, wenn dafür eine Form entsteht. Die verlorenen Dimensionen
sind notiert (Halten ohne Ort, Denken ohne Gerät, Übertragbarkeit, Auslagerungsgefahr).

### 13.8 Nordsterne & USER-INPUTS-Kanon
- **5 Nordsterne** (nicht verhandelbar): direktes Erfassen <2s · null Kontextwechsel ·
  lokal/keine KI/keine Auto-Zettel · gemessen statt geraten · diagnostisch nie als Ziel.
- **USER-INPUTS** (`USER-INPUTS.md`) = kanonische User-Vorgaben (wörtliche Inputs 1–37 +
  Prinzipien). Prinzip 28: **Karte = Sicht, FSRS pro Karte**. Prinzip 18: PTH-660 ersetzt
  Steno-Keyboard, Express-Keys abgelehnt (→ W1 irrelevant). Prinzip 25: alle Kanäle
  gleichberechtigt (Akkorde sind nicht der Zwangskanal).

## 14. Daten & Pfade

- `.commind-data/`: `store.sqlite3` (live: 2103 objects, 4115 relations, 9473 events,
  2 views, 2 workspaces), `kartei.sqlite3` (live: 1 Karte, 1 Schedule), `media/`,
  `stress-media/`, `store.workflows.json` (`{"active": null, "items": {}}`).
- Workspaces ("Räume"): `main` + 1 weiterer; letzter Raum in QSettings
  (`commind/commind/last_workspace`); pro Raum eine `canvas`-View + Pose.
- Export/Import: `core/workspace_io.py` (IDs werden neu vergeben).

## 15. Tests & Qualität

- 65 Testdateien in `tests/` — M1*-Canvas/Editor, M2*-Kanten/Navigation/Chords,
  M3-Bookmarks, M4-Kartei (DB/Session/Live-Sync/Renderer/Fenster), M5-Bilder,
  M6-Workflows (Engine/UI/Verwaltung), MVP-Smoke (Ende-zu-Ende + Persistenz + Kaltstart
  <3000 ms), HW (wacom_touch Replay, padmap, wacom_pad, steno_layout), store/kernel/
  batch/edge-priority.
- HW-Tests skippen ohne evdev/Plover-Dicts (CI-tauglich, siehe `tests/test_hw_padmap.py`).
- Perf-Doktrin aus steno übernommen: gemessen statt geraten; Caches in store.py tragen
  Messkommentare.

## 16. Widerspruchsregister & offene Fragen

Sämtliche Fundstellen, die sich widersprechen. **Vor Detail-Kapiteln klären** — je Eintrag
steht die Frage an den User.

| # | Widerspruch | Quelle A | Quelle B | Status |
|---|---|---|---|---|
| W1 | **ExpressKeys** | `USER-INPUTS:41` lehnt sie ab, `HW-TOUCH-PLUGIN.md:14` "Pad ungenutzt" | Code implementiert sie (`pad_buttons.json`, Reader, BTN_8-Toggle) | **GEKLÄRT 25.09.: komplett irrelevant** — keine Feature-Doku, nur Randnotiz (Rohling für Hardware-Tweaking) |
| W2 | **Lernsystem-Umfang** | `core/kartei_session.py` (23.09.: nur FSRS) | `SYSTEM.md:16` + steno `apps/kartei/*` (Free Recall, Interleaving, Pretest, Schlaf-Queue) | **GEKLÄRT 25.09.: VOLLES Lernsystem, gefiltert** — Karten können 2..n Zettel sein (nacheinander aufdecken), Free Recall etc. alles möglich, manuell alles steuerbar, FSRS ist nur ein Teil. Kapitel 10 beschreibt den Gesamtumfang, Code-Stand wird je Bauteil markiert |
| W3 | **Bewertungs-UI:** 2 Buttons vs. 4 Grade | `ui/kartei_window.py` nur Gewusst/Nochmal | Scheduler/Session können Grade 1–4 | folgt aus Lernsystem-Entscheid: volles System = 4 Grade + manuelle Steuerung; aktuelle UI ist Reduktion (Port-Stand) |
| W4 | **Prädikate/Rollen-Stand:** 10/9 vs. 18/7 | commindv2 `core/kernel.py` (9+1 Keeper, 9 Rollen, `comment` raus) | steno `core/kernel.py` (18/7 inkl. `comment`), `SYSTEM.md:133` "7 Rollen" | Migration v6 remapped Prädikate, aber `comment`-Rollen aus Alt-DBs sind in commindv2 ungültig |
| W5 | **Steno-Engine** | `HW-TOUCH-PLUGIN.md:26` "Plover bleibt Engine" | `tools/steno_engine.py` Eigen-Engine | **GEKLÄRT 25.09.: Eigen-Engine = Standard** (inputd + steno_engine, Plover-frei); Plover-Machine-Shim = optionale Alternative. Dict-Format (Plover/Lapwing-JSON) bleibt |
| W6 | **Dict-Pfade divergent** | `ui/steno_layout.py`: lapwing-base + lapwing-commands + user.json | `tools/steno_engine.py:65-69`: user.json + main.json + lapwing-base | unterschiedliche Priorität/Dateien |
| W7 | **Workflow-Vertrag** vs. Implementierung | `WORKFLOWS.md` "spawnt Hilfs-Zettel, editiert NIE bestehende" | `workflows/firstprinciples.py` wertet Edit-Inhalte aus; `brainstorm` clustert automatisch bei Selektion | Grauzone (nur Spawn, aber unerbeten) |
| W8 | **FSRS-Einheit** | `KOGNITION.md:13` + `USER-INPUTS Prinzip 28`: FSRS pro **Karte** | `UNTERTHEMEN.md:56`: "FSRS pro **Kante**" | alte Formulierung in UNTERTHEMEN |
| W9 | **Flächen-Einteilung** | `EINGABE-SPEC.md:17-19` "GENAU EIN Touchpad-Feld … alles andere ohne Wirkung" | `input_zones.json` + `inputd.py`: QWERTZ-Streifen oben + Spacepad-Touchpad + Mover + 3 Haltezonen = mehrere wirksame Flächen | Spec unvollständig oder Daemon außerhalb der Spec |
| W10 | **Zahlen Tokens/Chords** | `steno/docs/CHORDS.md`: 63 Tokens | `steno/GUIDE.md`: 95 (86+9); `commind/docs/STENO.md:7`: 95 verifiziert | vermutlich verschiedene Stände |
| W11 | **Mover-Maße** | `EINGABE-SPEC.md:16` "~1,5 cm Radius" | `input_zones.json` r=16 mm, Deadzone 6 mm | Kalibrierungsdetail |
| W12 | **Stift:** Input-Kanal "ohne Zwang" vs. fehlende Anbindung | `INPUT.md`/`USER-INPUTS` Stift = Kanal 4 | `kind=sketch` + QTabletEvent fehlen komplett (EINGABE-SPEC "Skizzen: später") | als Nicht-Ziel dokumentiert |

## 17. Glossar (Kurzfassung)

- **Zettel** — Informationsblock im Graph (`objects`, kind meist `note`), mit Rolle + Position.
- **Rolle** — Sorte des Zettels (9 Werte), färbt Rahmen/Marker, steuert (im Original) die
  Lernwürdigkeit.
- **Kante** — gerichtete/ungerichtete Relation (`source → predicate → target`), max. eine
  lebende je Zettelpaar.
- **Prädikat/Keeper** — Kantentyp; 9+1 aktive Werte.
- **Karte** — Abfrageeinheit der Kartei (separate DB), Live-Sicht auf den Graphen, nie Kopie.
- **Raum/Workspace** — eigener Graph-Ausschnitt mit eigener Canvas-Projection.
- **Chord** — gleichzeitige Tasten/Multi-Touch → ein Stroke (frozenset Keys).
- **Token** — `/steno-*`-Textbefehl, den `ChordFilter`/`handle_stroke` versteht.
- **Stroke** — ein abgeschlossener Chord (bei Loslassen aller Kontakte).
- **Mover** — Kreis für Richtung+Stärke (CREATE/JUMP/PAN), nie Maus.
- **Workflow** — aktivierbares Python-Modul mit Hooks; nur dann wirksam.
- **Tombstone** — Grabstein statt Löschen; alles wiederherstellbar.
- **Leech** — Karte mit ≥3 Resets → Reparaturauftrag statt Drill.

---

## Detailstatus der Kapitel

- [x] Outline + Beleg-Anker + Widerspruchsregister (Kapitel 0–2, 14–17)
- [x] Kapitel 3–5 (Eingabegerät: Rohschicht, Daemon, App-Pfade) **detailliert**
- [x] Kapitel 6–8 (Substrat, Kernel, Darstellung) **detailliert**
- [x] Kapitel 9 (Denksystem/Workflow-Engine) **detailliert**
- [x] Kapitel 10 (Lernsystem/Kartei, volles System) **detailliert**
- [x] Kapitel 11–13 (stenoQT, denken, Kognition) **detailliert**
- [x] User-Entscheide 25.09. eingearbeitet: Stapel-Modell (W-Schluss), ExpressKeys
  irrelevant (W1), volles Lernsystem gefiltert (W2/W3), Eigen-Engine = Standard (W5)
- [ ] Restliche Widersprüche W4/W6–W12 sind Detail-Kalibrierungen, im Register geführt
