# touch-steno — Kern

## Was wir erreichen wollen

Eine **Laut→Zonen-Zuweisung** für ein 4-Finger-Touch-Stenografiebrett, die zwei Dinge
gleichzeitig erfüllt:

1. **physisch billig** — jede Bewegung des Fingers kostet so wenig Zeit wie möglich,
2. **logisch symmetrisch** — die Zuweisung ist so regelmäßig, dass die Lernkurve
   steil abfällt, statt 39 Einzellauten auswendig zu lernen.

Der Kern ist ein Optimierer, kein Dokumentenschatten. Alles, was früher im Repo lag,
ist entfernt; die Historie auf GitHub bleibt als Archiv erhalten.

## Topologie

40 Zonen auf einem 224 × 148 mm Pad (Ursprung unten links, y nach oben):

| Finger | Zonen | Anordnung |
|---|---:|---|
| linker Daumen | 16 | Polarfächer, 4 Ringe × 4 Sektoren |
| rechter Daumen | 16 | Polarfächer, 4 Ringe × 4 Sektoren |
| linker Zeigefinger | 4 | 2 × 2 Block |
| rechter Zeigefinger | 4 | 2 × 2 Block |

Die linke Hälfte ist das **exakte Spiegelbild** der rechten — deshalb ist der
Symmetrie-Begriff der Zielfunktion überhaupt wohldefiniert: jede Lautklasse sitzt
beidseits spiegelbildlich, also lernt man die Hand einmal.

39 ARPAbet-Laute (CMUdict) + `SPACE` = 40 Symbole, bijektiv auf die 40 Zonen.

## Die zwei Programme

### `layout_optimizer.py` — die Zuweisung finden

Korpora: die 20 000 häufigsten englischen Wörter (Norvig, Google-Web-1T) gejoint mit
CMUdict-Aussprachen → 18 015 Wörter, 97,8 % der Token-Masse, 1,652 Silben/Token.

Ziel, vier normalisierte Komponenten (1,0 = Zufallslayout):

| Komponente | Gewicht | Inhalt |
|---|---:|---|
| `time` | 0,40 | Fitts-Bewegung auf dem **kinematischen** Pfad + Finger-/Handwechsel + Rückkehr zur Ruhelage |
| `error` | 0,20 | korpus-abgeleitete Verwechslbarkeit × räumliche Nähe |
| `learn` | 0,25 | artikulatorische Nähe × Zonendistanz |
| `sym` | 0,15 | 1 − Spiegel-Score der Lautklassen |

Gesucht mit **Simulated Annealing** (Swap-Nachbarschaft, geometrische Abkühlung,
Temperatur skalenfrei aus dem Startzustand, 4 Restarts, Best-Improvement-Polish,
deterministisch per Seed). Δ-Auswertung O(n) pro Zug, verifiziert gegen die
Vollberechnung auf 1e-15.

**Wichtig:** die Kinematik ist pro Finger ein eigenes Polarsystem. Der Daumen
zirkumduziert um das CMC, der Zeigefinger flektiert um das MCP; eine Bewegung kostet
den tatsächlich zurückgelegten Weg, nicht die Luftlinie. Der tangentiale Anteil wird
mit dem *gemessenen* Tangential-Aufschlag bepreist.

```bash
python3 layout_optimizer.py --self-test                  # 20 Invarianten, kein Netz nötig
python3 layout_optimizer.py --out layout.json            # voller Lauf, ~25 s
python3 layout_optimizer.py --hand-profile messung/rom/hand_profile.json
python3 layout_optimizer.py --write-profile-template profil.json
```

### `rom_capture.py` — die Geometrie messen

Das Optimierer-Modell braucht vier Dinge, die man nicht raten kann: Wo der Daumen in
Ruhe liegt, wie weit er **bequem** reicht (nicht maximal), wie der Fächer läuft und wie
viel langsamer ein seitlicher Sweep ist als eine radiale Extension.

Das Programm führt eine angeleitete Sequenz mit der rechten Hand durch und schreibt
`hand_profile.json` im Format, das `--hand-profile` liest. Jeder Sweep läuft **zwei
Mal**: einmal „so weit wie du bequem willst", einmal „so weit wie physisch möglich".
Die Lücke dazwischen entscheidet, ob 16 Zonen pro Daumen überhaupt baubar sind.

```bash
python3 rom_capture.py --device /dev/input/event19 --out-dir messung/rom
python3 rom_capture.py --manual --out-dir messung/rom      # ohne Tablet
python3 rom_capture.py --sheet pad.svg                      # Druckbogen zum Messen
python3 rom_capture.py --self-test                          # synthetische Events
```

Anleitung pro Schritt: Ferse der Hand **vom** Pad, nur der zu testende Finger
berührt. Kalibrierung über die drei Pad-Ecken, Kontaktspanne > 30 mm wird als Handfläche
verworfen.

## Ehrliche Grenzen

- **Keine Messung aus diesem Repo wird verwendet.** Alle Kostenkonstanten sind
  deklarierte Modellparameter mit Herkunftsetikett (`PROVENANCE` im Code). Fitts'
  Koeffizienten sind die publizierten Shannon-Werte, alles andere ist Annahme.
- Die WPM-Zahl ist ein **Modelloutput**, keine Messung. Bei einem Strich pro Laut
  (4,24 Laute/Wort) begrenzt allein die Strichzahl auf ~175 WPM, auch wenn jede
  Bewegung gratis wäre.
- Was **nicht** modelliert ist: 3D-Daumenrotation, Handgelenkabweichung,
  Kontaktpatch-Dynamik, individuelle Handgröße, Ermüdung, bimanuales Parallelisieren
  (die Zeitrechnung ist strikt sequenziell).
- `rom_capture.py` misst Geometrie und Komfort, **keine** Dauerleistung. Ein
  Bewegungsprotokoll über Sitzungen ist nicht Teil des Ziels.
- Getestet: beide Programme laufen, die Selbsttests sind grün, der
  Live-Evdev-Pfad ist **nicht** ausgeführt worden (kein Tablet angeschlossen) —
  Tracker, Kalibrierung, Aufnahmeschleife und Auswertung sind mit synthetischen
  Events getestet.

## Werkzeuge, nicht Ergebnisse

`--self-test` prüft Invarianten, keine Zahlen auf Plausibilität. Der Optimierer
vergleicht gegen vier Baselines (Inventarordnung, umgekehrt, frequenzgreedy, zufällig)
und verliert gegen keine davon. Fehlerhafte Geometrie wird im Hauptpfad **nicht**
stillschweigend akzeptiert, sondern vor dem Lauf als Bruchliste ausgegeben.
