# Comprehensive Research Report

**Arbeitsstand:** 25.09.2026, erste Rechercheiteration (Agent 1)
**Arbeitsverzeichnis:** `/home/lilatg3/Projekte/chordtouch-research`
**Status:** living draft; alle WPM-/Fehlerquoten müssen vor einer finalen Veröffentlichung gegen den jeweiligen Original-Paper geprüft werden.

## 0. Executive summary

Eine kontinuierliche Touch-Fläche mit 0G-Fingerkontakt ist kein Ersatz für eine Tastatur. Die zentrale technische Aufgabe ist nicht „Buchstaben erkennen“, sondern **intent separation**: aus einer kontinuierlichen Menge von Kontakten, Kontaktflächen und Bewegungen eine kleine Menge diskreter Tastenereignisse mit geringer Latenz und korrigierbarer Fehlwahrscheinlichkeit zu gewinnen.

Die wichtigste Folgerung aus der bisherigen Sichtung:

1. **150–250 WPM sind auf einer reinen, unsichtbaren 0G-Fläche nicht als evidenzbasierte Standardprognose zulässig.** 150–250 WPM sind mit trainierterQWERTY-Tastatur für erfahrene Tipper möglich; die hier gefundenen Surface-/Wearable-Systeme berichten meist 23–45 WPM, mit Lern-/Korrekturaufwand und engerem Textkorpus. Eine 150-WPM-Version ist als Forschungsziel, nicht als bestätigte Eigenschaft.
2. Die aussichtsreichste Architektur ist eine **mehrstufige Zustandsmaschine**: Palm-/Kontaktregion → stabile Ruhepositionen → kurze Tap- oder Drift-Impulse → Chord/Silben-/Wortdecoder →Sprachmodell → Korrektur.
3. Ein **expliziter Ruhezustand oder Pausen-/Kontakt-Timeout** ist unvermeidbar, wenn 0G-Ruhekontakte vermieden werden sollen. Software allein kann echte haptische Orientierung nicht vollständig ersetzen.
4. **Dekodierung sollte probabilistisch sein**, aber niemals versteckte Großfehler produzieren. Rohsignal, Konfidenz, Kandidat und Korrektur müssen geloggt werden; ein Sprachmodell darf niemals eine Eingabe als „sicher“ ausgeben, wenn die Sensorik nur einen Kontakt sieht.
5. Für Linux ist zunächst ein **libinput/uinput-Prototyp** sinnvoll. Die Wacom-Feel-API liefert mehr Fingersensorik (u.a. Palm Detection, Confidence, Blob/Raw-Daten), ist aber primär Windows/macOS-orientiert; der Linux-Treiberweg muss mit der tatsächlichen PTH-660-Konfiguration verifiziert werden.

## 1. Scope, Terminologie und Evidenzstufen

- **WPM:** Wörter pro Minute; pro Studie definition beachten (Standardwortlänge, Korrektur, Pause, Fehlerkorrektur).
- **Oberfläche:** PTH-660 ist ein drucksensibles/berührungsfähiges Grafiktablett; je nach Treiber können Touch- und Pen-Events separat oder arbitrariert ankommen.
- **Enslavement:** anatomische Kopplung, insbesondere Mitbewegung des Ringfingers bei Bewegungen des Mittelfingers.
- **0G:** kontinuierliche kapazitive Berührung ohne Tastendruck; die Kontaktfläche ist der wichtigste beobachtbare Ersatz für Betätigungskraft, aber kein zuverlässiger Tastendruck.

Evidenzstufen in diesem Dokument:

- **A:** Originalpaper/Originalprojekt oder explizit gemessenes Ergebnis.
- **B:** Peer-reviewed related work bzw. technische Dokumentation.
- **C:** plausible Übertragung/Entwurfshypothese, experimentell zu validieren.
- **D:** Marketing-/Sekundärangabe; nicht als Leistungsnachweis verwenden.

## 2. Track 1 — Akademischer Stand

### 2.1 Relevante Arbeiten und übertragbare Befunde

| Arbeit | Methode / Ergebnis | Relevanz für dieses Projekt | Evidenz |
|---|---|---|---|
| Findlater, Wobbrock, Wigdor, **Typing on Flat Glass: Examining Ten-finger Expert Typing Patterns on Touch Surfaces**, CHI 2011, DOI [10.1145/2048064.2048080](https://doi.org/10.1145/2048064.2048080) | Zehn-Finger-Expertenmuster auf Touchflächen; positionsbasierte Klassifikation, große Kontaktflächen und persönliche Modelle sind relevant. | Belegt, dass Touchfläche nicht nur als Punkt behandelt werden darf und dass persönliche Geometrie wichtig ist. | A/B |
| Findlater & Wobbrock, **Bayesian Touch**,CHI 2012, [ACM](https://dl.acm.org/doi/10.1145/2382193.2382252) | Statistische Zielauswahl mit Nutzer-/Touchmodell. | Grundbaustein für ein probabilistisches Touchmodell; auf PTH-660 zusätzlich mit Ruheprior kombinierbar. | A |
| Azenkot & Zhai, **Two-Thumb Asymmetric Typing on a Small Handheld Device**, MobileHCI 2010, [ACM](https://dl.acm.org/doi/10.1145/1857993.1858037) | Asymmetrische Bewertung des gesamten Kontaktbereichs, nicht nur des Schwerpunkts. | Kontaktfläche, Ellipse und Drift müssen als Merkmale gespeichert werden. | A |
| **Hand Posture’s Effect on Touch Screen Text Input Behaviors: A Touch Area Based Study**, arXiv:1504.02134, [PDF](https://arxiv.org/pdf/1504.02134) | Kontaktflächenbasierte Analyse; Indexfinger versus ein/zwei Daumen. Zwei Daumen zeigten in der Studie die niedrigsten Fehlerquoten. | Warnung vor zu großer Indexfingerbewegung und Kontamination durch Handversatz. | A/B |
| Zhai, Kristensson & Buxton, **Write黄金: Eyes-free text entry on a touchscreen phone**, CHI 2003, [ACM search/reference](https://dl.acm.org/doi/10.1145/958432.958441) | Shorthand-Gesten ohne sichtbare Tastatur. | Zeigt, dass eine reduzierte Gestenmenge lernbar sein kann, aber kein Beleg für 150 WPM ist. | A |
| Bonner et al., **No-Look Notes: Accessible Eyes-Free Multi-touch Text Entry**, Pervasive 2010 | Multi-Touch-Pie-/Segmenttext, eyes-free. | Nützlich für robuste Modus-/Navigationsgesten; niedrige Frequenz und Trainingsabhängigkeit. | A |
| **TOAST** (in TypeAnywhere referenziert), CHI/Journal paper context | Markov-Bayesian räumliche Dekodierung auf großen Touchscreens; berichteter Mittelwert 44,6 WPM. | Gutes Benchmark für probabilistische Oberflächen-Dekodierung; große Touchscreen-Geometrie ist nicht direkt PTH-660. | A/B |
| Streli et al., **TapType: Ten-finger text entry on everyday surfaces via Bayesian inference**, CHI 2022, DOI [10.1145/3491102.3501878](https://doi.org/10.1145/3491102.3501878), [arXiv PDF](https://arxiv.org/pdf/2410.06001) | Inertiale Sensoren am Handgelenk; zehnfingerige QWERTY-ähnliche Eingabe auf passiven Flächen, Bayes-Decoder. | Stärkstes Argument für sensorische Taps statt Oberflächenposition; PTH-660 hat jedoch nicht dieselbe Sensorik. | A |
| Banerjee et al., **TypeAnywhere: A QWERTY-Based Text Entry Solution for Ubiquitous Computing**, CHI 2022, DOI [10.1145/3491102.3517686](https://doi.org/10.1145/3491102.3517686), [Full HTML](https://dl.acm.org/doi/fullHtml/10.1145/3491102.3517686) | Finger-Tap-Sequenzen statt Positionen; Mapping persönlicher Finger-zu-Tasten; LM-Decoder. | Sehr passend als Referenzarchitektur: Tap-Identität plus Sequenz/LM, nicht absolute Key-Ziele. | A |
| **Typing on an Invisible Keyboard**, CHI 2018, DOI [10.1145/3173574.3174013](https://doi.org/10.1145/3173574.3174013) | Erhöhte Geschwindigkeit von 31,3 auf 37,9 WPM nach kurzen Übungssitzungen; 41,6 WPM als sichtbare Tastaturvergleich. | Nützliche Lernkurven-Realität: 20–25 min pro Tag über drei Tage brachte nur moderate Verbesserung. | A |
| Xu et al., **BiTipText: Bimanual Eyes-Free Text Entry on a Fingertip Keyboard**, CHI 2020, DOI [10.1145/3313831.3376306](https://doi.org/10.1145/3313831.3376306) | Fingertip-Tastatur, Daumen tippt auf Indexfinger; 23,4 WPM gemeldet. | Ebenfalls starke Lern-/Akzeptanzwarnung; nicht direkt auf kontinuierliche Glasfläche übertragbar. | A |
| Li et al., **FineType: Fine-grained Tapping Gesture Recognition for Text Entry**, CHI 2025, DOI [10.1145/3706598.3714278](https://doi.org/10.1145/3706598.3714278) | Einhändige Tapping-Gesten mit Fingerkombinationen/Posturen; 35,1 WPM und 5,1 % Zeichenfehler berichtet. | Aktueller relevanter Benchmark für flache Oberflächen; nutzt zusätzliche Wearable-Sensorik. | A |
| **Surface Haptics review**, arXiv:2004.13864, [PDF](https://arxiv.org/pdf/2004.13864) | Vibro-, elektrostatische und ultraschallbasierte Oberflächenhaptik. | Relevant, weil PTH-660 selbst keine haptische Rückmeldung liefert; Hardware-Augmentation ist separat zu bewerten. | A/B |
| Wacom Feel Multi-Touch Developer Docs, [Overview](https://developer-docs.wacom.com/docs/icbt/macos/multi-touch/multitouch-framework-overview), [Basics](https://developer-docs.wacom.com/docs/icbt/windows/wacom-feel-multi-touch/wfmt-basics) | API mit per-contact Daten, Palm Detection/Rejection, Confidence; Consumer/Observer mode. | Direkte technische Integrationsmöglichkeit, wenn Windows/macOS-Treiber genutzt wird. | A |
| Linux Wacom Project, [input-wacom](https://github.com/linuxwacom/input-wacom), [libwacom](https://github.com/linuxwacom/libwacom), [libinput tablet support](https://wayland.freedesktop.org/libinput/doc/1.19.0/tablet-support.html) | Linux-Treiber liefert touch arbitration; die sehr niedrige Schwellenempfindlichkeit kann Phantom-Touch erzeugen. | Muss mit `/dev/input/event*` und `libinput debug-events` gegen PTH-660 verifiziert werden. | A/B |

### 2.2 Was die Literatur für die Nullkraft-Erkennung tatsächlich liefert

Die Papers liefern **keine universelle Schwelle** wie „3 mm = Tastendruck“. Sie liefern组合 aus:

- **Ruhe-/Vorlaufmodell:** Kontakt über eine Zeitdauer stabil und langsam; erst nach Timeout oder Pausengeste wird eine Auswahl zugelassen.
- **Kontaktgeometrie:** Schwerpunkt, Ellipse, Fläche, Orientierung und Änderung dieser Größen. Kontaktfläche ist kein Tastendruck, aber ein gutes Diskriminierungsmerkmal.
- **Dynamik:** Peak-Geschwindigkeit, kinetische Energie, Beschleunigung, Richtungsänderung und Dauer. Ein kurzer Impuls ist robuster als absolute Position.
- **Identität:** Tracking-ID bzw. stabile Zuordnung zum anatomischen Finger; bei 0G ist das schwieriger als bei einem physischen Tastendruck.
- **Kontext/Grammar:** QWERTY-Prior, persönliche Belegung, n-Gramm/LM und chordale Zustandsmaschine reduzieren die Klassenmenge.
- **Kalibrierung:** individuelle Ruhepositionen und Kontaktmodelle statt fixer absoluter Schwellwerte.

Eine robuste Entscheidungsschwelle kann als Likelihood-Ratio formuliert werden:

\[
\Lambda_t = \frac{p(\mathbf{x}_t \mid H_\text{tap})}{p(\mathbf{x}_t \mid H_\text{rest})}
\]

mit Featurevektor \(\mathbf{x}_t\) aus Position, Geschwindigkeit, Kontaktfläche, Orientierung, Identität, Dauer und Kontext. Eine Eingabe wird nur akzeptiert, wenn zusätzlich ein Hysterese-/Mindesthaltungszustand und eine grammatische Mindestkonfidenz erfüllt sind. Das reduziert die Fehlalarmwahrscheinlichkeit, kann aber Reaktionszeit erhöhen.

Für ein Velocity-Peak-Modell ist eine einfache Kandidatenmenge:

\[
I = \{(f,d,\Delta t): f\in F_\text{active}, d\in D, \|\Delta p_d\|\ge v_\min, \|\Delta p_d\|\le v_\max, \tau_\min\le \Delta t\le \tau_\max\}
\]

Danach wird der beste Kandidat nicht nur über die maximale Geschwindigkeit gewählt, sondern über Kosten:

\[
C = w_v E_v + w_a E_a + w_o E_o + w_g E_\text{grammar} + w_h E_\text{history} + \lambda C_\text{latency}.
\]

**Wichtig:** Schwellen wie 3–8 mm/s oder 10–30 ms sind Startwerte für Messung, keine aus der Literatur abgeleiteten universellen Werte. Die PTH-660-Abtastrate, Sensorik, Handgröße, Kontaktmedium und Auswertungskette müssen eine eigene ROC-/PR-Messung liefern.

### 2.3 Palm rejection, Finger confidence und Enslavement

Palm rejection ist nicht dasselbe wie Finger-ID. Ein robustes System braucht:

1. **Geometrische Palm-Klasse:** große, langlebige Blobflächen, niedriger Dichte-Änderung, begrenzte Anzahl verletzbarer Kontakte.
2. **Anatomische Konsistenz:** Handballen darf liegen bleiben, während sich Zeige-/Mittelfinger bewegen; Ringfinger wird als *dependent* markiert, nicht automatisch gelöscht.
3. **Enslavement-Modell:** \(\mathbf{p}_r\) wird bei einer erwarteten Bewegung von \(\mathbf{p}_m\) mitgeführt. Eine Pause von \(r\) ist weniger wahrscheinlich, wenn \(\Delta \mathbf{p}_r \approx \boldsymbol{\beta}\Delta \mathbf{p}_m\) und beide Bewegungen zeitgleich sind. Ein schwellenbasierter Ansatz kann Ringfingerkontakte als **suppressed** statt als separate Tasten klassifizieren.
4. **Bestätigung:** Ein bewusstes Zeichen muss eine eigene Peak-/Driftphase oder eine explizite Chord-Sequenz besitzen; „nur mitgezogen“ genügt nicht.

Formalisierung:

\[
E_\text{move} = \left\|\Delta \mathbf p_f - \boldsymbol{\beta}_{r\leftarrow m}\Delta \mathbf p_m\right\| < \epsilon
\Rightarrow P(\text{intent}_r \mid \text{move}) \downarrow
\]

Das ist ein Bayes-Update, kein Ersatz für Kalibrierung. Es ist insbesondere zu prüfen, ob die PTH-660-API separate Kontakte überhaupt zuverlässig liefert und ob Kontakt-IDs beim Heben/Aufsetzen wiederverwendet werden.

## 3. Track 2 — Eingabe-Paradigmen

### 3.1 Grobe Systemklassen

- **Stenografie/Chording:** eine oder wenige Silben werden pro Stroke oder Tastenfolge codiert; Plover ist die stärkste Open-Source-Ausgangsbasis, aber die Standard-Stenokeys sind für 0G-Tracking nicht unverändert geeignet.
- **Directional/Chording:** kleine Zahl von Tasten plus Richtung/Posture; gut für reduzierte Fingerzahl, aber Lernlast.
- **Word/gesture:** ganze Wörter über Pfade/Sektoren; sehr schnell nach Lernen, aber stark abhängig von LM, Korrektur und stabiler Geometrie.
- **Tap-sequence/LM:** Fingeridentität oder Kontakt-Timing statt absoluter Position; adaptierbar an 0G, wenn Kontaktstart zuverlässig erkannt wird.
- **QWERTY-Prior/virtual layout:** aus Nutzerfehlern lernen; nicht mit einer fixen Pixel-Tastatur verwechseln.

### 3.2 Paradoxon der Zielgeschwindigkeit

Bei 150 WPM entspricht ein durchschnittliches Wort ungefähr 0,4 s. Selbst bei fünf Wörtern pro Sekunde muss ein Decoder mehrere Korrektur- und LM-Entscheidungen in dieser Zeit verarbeiten. Bei 250 WPM bleiben ca. 0,24 s/Wort. Ein Einzelkontakt-Stream mit Pausen, Drift und Identitätsunsicherheit hat diese Latenz möglicherweise nicht. Ein 150–250-WPM-Ziel sollte daher operationell definiert werden:

- Rohereignisrate ≥ Zielrate,
- Character/Silhouette-error nach Korrektur < definierter Wert,
- keine blockierende Bestätigungs-Pause,
- subjektive Belastung und Fehltrigger getrennt berichten.

### 3.3 Empfohlene Lernkurven- und Testmetriken

- ungewichtete WPM (kein Korrektur-Discount),
- KSPC: Keystrokes per Correct Character,
- raw und corrected WPM,
- false activations per minute,
- idle false-trigger rate,
- latency P50/P95,
- correction/backspace rate,
- contact-ID switches,
- thermal comfort/Selbstbewertung nach 30/60 Minuten.

## 4. Track 4 — Null-Kraft-Strategien

| Strategie | Vorteil | Risiko / Gegenmaßnahme |
|---|---|---|
| Velocity-Peak | Passive Hände erzeugen meist weniger scharfe Peaks; direkt aus Multitouch ableitbar. | Ungewöhnliche schnelle Nebenbewegungen; Peak-basierte Latenz und individuelle Schwelle. |
| Fläche/Blob | Palm ist meist größer und langlebiger als Fingerkontakt. | Wacom-Auflösung, Fingerdruck und Ausrichtung ändern Fläche stark. |
| Drift statt absoluter Position | Kleine Bewegungen werden als Zeichen genutzt; Handversatz wird teilweise toleriert. | Drift kann mit Zittern/Palm-Reibung verwechselt werden. |
| Deadband/Hysterese | Verhindert Flattern an der Schwelle. | Zu großes Deadband verliert schnelle Eingaben. |
| Aufenthaltswahrscheinlichkeit | Ruhepositionen werden gelernt; Ausgabe nur bei Abweichung. | Benutzer muss Position halten; ergonomisches Risiko. |
| Chord/Posture | Mehr Bits pro Ereignis; zusätzliche Identitätsinformation. | Enslavement und anatomische Belastung. |
| Sprache/LM | Korrigiert einzelne Sensorfehler und verkürzt Zielbewegungen. | Halluzination/Autokorrektur; unsichtbare Fehler gefährlich. |
| Passives Overlay |Referenzkanten, Vertiefungen und Druckpunkte ohne Elektronik. | Aufsetzen/Abreiben, Reinigung, Wacom-Kalibrierung. |
| Handballenauflage | Kann Kontaktfläche und Druckvorbelastung verändern. | Kann Fehltrigger vergrößern; nicht ungeprüft verwenden. |
| Aktive Haptik | echte taktile Orientierung. | PTH-660 hat keine integrierte Haptik; externe Hardware nötig. |

**Urteil:** Die beste Nullkraft-Lösung ist nicht „dicker Deadband“, sondern ein **mehrschichtiges Intent-Modell mit bewusstem Ruhe-/Aktivierungston**. Ein rein passiver Stickmodus ist nur plausibel, wenn der Nutzer eine nichtelektrische Referenzstruktur akzeptiert oder bereit ist, die Hand aktiv in einer Pose zu halten.

## 5. Software-Architektur-Skizze

```text
 PTH-660 / Linux event stream
            |
            v
 raw contacts: id, x, y, area, pressure/tool, time
            |
            v
 tracker + palm gate + anatomical assignment
            |
            +--> rest-state model (per-user Gaussian / HMM)
            +--> velocity/area/drift feature stream
            +--> enslavement estimator
            |
            v
 candidate event generator (tap / micro-drift / chord)
            |
            v
 temporal decoder (HMM + weighted finite-state grammar + LM)
            |
            v
 candidate UI + confidence + undo + audio/visual feedback
            |
            v
 uinput keyboard or application protocol
```

Wichtig: Die UI muss jederzeit anzeigen, ob der Decoder **idle**, **armed**, **tentative** oder **committed** ist. Eine commit-Entscheidung ist reversibel; niemals ein Zeichen aus einem einzelnen unkontrollierten Kontakt emittieren.

## 6. Quellen- und Prüfprotokoll

Die Links in diesem ersten Stand stammen aus ACM DL, arXiv, Wacom Developer Docs, Linux Wacom und Suchergebnissen. Vor `FINAL` werden folgende Prüfungen durchgeführt:

- [ ] Original-PDF für jede WPM-/Fehlerangabe öffnen.
- [ ] Prüfen, ob WPM corrected oder uncorrected ist.
- [ ] Prüfen, ob Studienteilnehmer trainierte QWERTY-Nutzer waren.
- [ ] Prüfen, ob Palm rejection vom Gerät selbst oder vom Experiment bereitgestellt wurde.
- [ ] GitHub-Repos mit festem Commit SHA dokumentieren.
- [ ] Lizenz- und Patentstatus der Layouts prüfen.
- [ ] PTH-660-Eventdaten auf dem Ziel-Linux-System messen.
- [ ] Aussagen mit „nicht belegt“ markieren, statt Schätzwerte als Fakten auszugeben.

## 7. Praktische Code-Integration (verifizierte Upstream-Bausteine)

### Plover als Backend

Die Open-Source-Engine `opensteno/plover` trennt sinnvoll in:

- `plover/steno.py` (`Stroke`, RTFCRE-Normalisierung),
- `plover/steno_dictionary.py` (`StenoDictionaryCollection`),
- `plover/translation.py` (`Translator.translate_stroke()`),
- `plover/formatting.py` (Formatter und Metas),
- `plover/machine/keyboard.py` (Chord-/Arpeggiate-Muster).

Für dieses Projekt ist der stabilste Integrationsschnitt eine **eigene Touch-Machine/Source**, die plausible `down/up/hold`-Events erzeugt und an Plover übergibt. Nicht der gesamte Plover-Kern muss in eine proprietäre Anwendung kopiert werden. Plover ist GPL-2.0+; Lizenz- und Prozessgrenzen sind vor einer Veröffentlichung zu prüfen.

### Linux-Eingabe

Für Linux ist der rohe Weg:

```text
/dev/input/eventN
  -> EVDEV multi-touch slots
  -> palm/rest/intent layer
  -> Plover stroke or gesture decoder
  -> uinput virtual keyboard
```

Kernel MT-Slots verwenden `ABS_MT_SLOT`, `ABS_MT_TRACKING_ID`, `ABS_MT_POSITION_X/Y`, optional `ABS_MT_PRESSURE`/`ABS_MT_TOUCH_MAJOR` und `EV_SYN/SYN_REPORT`. `libinput` kann die Geräte- und Palm-Arbitration vereinfachen, ist aber **kein** Textdecoder. Unter Wayland ist ein eigener `uinput`-Sink robuster als X11-spezifische XTest-Injektion. `python-evdev` und `libevdev` sind geeignete Referenzen für die Ereignis-/Umsetzungsschicht.

### DasherCore und 8VIM

`DasherCore/src/dasher.h` ist als moderne C-API mit screen/mouse/key/frame/output callbacks und WPM/CPS-Zugriff ein brauchbarer Baustein für einen kontinuierlichen Fallback. `8VIM/8VIM` demonstriert eine 8-Sektor-/Zentrum-State-Machine mit Editor-Integration; der Code ist Android-spezifisch und daher eher Layout-/Erkennungsreferenz als Linux-Bibliothek.

## 8. Replikations- und Sicherheitsregeln

- Rohereignisse nur mit Einwilligung speichern; keineunnötigen Geräte-/Personenidentifikatoren.
- Testdaten mit Treiber- und Kernelversion versehen.
- Falschauslöser und Korrekturen getrennt von Korrektur-WPM berichten.
- Layouts, Wörterbücher und Code nicht ungeprüft unter einer Lizenz zusammenführen.

### Palm rejection: konkrete Evidenz

- **Probabilistic Palm Rejection Using Spatiotemporal Touch Filtering**, ACM IMWUT/TOC 2014, DOI [10.1145/2556288.2557056](https://doi.org/10.1145/2556288.2557056): probabilistische, räumlich-zeitliche Filterung; berichtet 0,016 unfreiwillige Palm-Eingaben pro Pen-Stroke bei 98 % korrekt durchgelassenen Stylus-Eingaben. Das ist ein Stift-System, aber die Modellidee (Blob-/Kontakt-Historie statt fester Fläche) ist übertragbar.
- **PalmTouch**, 2018, [PDF](https://www.mmi.ifi.lmu.de/pubdb/publications/pub/le2018palmtouchusing/le2018palmtouchusing.pdf): Palm wird nicht nur verworfen, sondern als eigene Modalität modelliert; berichtet 99,53 % Genauigkeit in realistischen Szenarien. Für dieses Projekt relevant, weil ein Handballen-Auflage-basiertes Kommando den 0G-Ruhezustand explizit nutzen kann.
- **SpeciFingers: Finger Identification and Error Correction on Capacitive Touchscreens**, IMWUT 2024, DOI [10.1145/3643559](https://doi.org/10.1145/3643559): Identifiziert Finger aus kapazitiven Rohdaten und nutzt Fingerkategorien als zusätzliche Interaktionsmerkmale. Das ist näher an der Kernfrage als reine XY-Punkte; die Verfügbarkeit auf PTH-660 ist offen.
- **CapContact: Super-resolution Contact Areas from Capacitive Touchscreens**, CHI 2021, [ETH project page](https://inf.ethz.ch/news-and-events/spotlights/infk-news-channel/2021/05/christian-holz-capcontact.html): schätzt hochauflösende Kontaktbereiche und berichtet, dass etwa ein Drittel der Lokalisierungsfehler moderner Touchscreens auf die niedrige Sensorauflösung zurückgeht. Ein PTH-660-Prototyp sollte daher Blob-/Kontaktgeometrie speichern, auch wenn ein Modell später trainiert wird.
- **Transferable Microgestures Across Hand Posture and Location**, CHI 2023, DOI [10.1145/3586183.3606713](https://doi.org/10.1145/3586183.3606713): Mikrogesten mit Mittel-, Ring- und kleinem Finger; relevant für Robustheit, weil die Hand nicht in einer starren Einzelpose verharren muss.

### Korrigierte Benchmarkwerte

Die aktuelle Quellenprüfung liefert wichtige Korrekturen:

- **TapType**: Der arXiv-Abstract nennt online 19 WPM nach 30 Minuten Training und 0,6 % CER; Experten lagen bei >25 WPM. Das ist kein Beleg für 150 WPM.
- **TypeAnywhere** zitiert Twiddler mit durchschnittlich 26 WPM nach 400 Minuten (6,67 Stunden) Training. Das ist ein wichtiger Realitätscheck gegen Marketing-Claims.
- **TOAST**: 44,6 WPM wird in TypeAnywhere als TOAST-Resultat genannt; es darf nicht TypeAnywhere zugeschrieben werden.
- **FineType**: 35,1 WPM und 5,1 % Character Error werden aktuell als Paper-Abstract-Werte geführt; spätere Original-PDF-Prüfung bleibt nötig.

## 9. Neue Hypothese: Kontaktfläche statt Druckproxy

Da PTH-660 auf einer kontinuierlichen Oberfläche keinen diskreten Tastendruck liefert, ist der **plötzliche Anstieg der effektiven Kontaktfläche** ein plausibler Ersatz für die Key-down-Phase:

\[
u_t = A_t - \min_{k \in [t-\tau,t]} A_k
\]

Ein Tap-Kandidat benötigt dann eine kurze Anstiegsflanke \(u_t > u_\text{min}\), eine Mindestbewegungsenergie und einen stabilen Vorabschnitt. Das ist robuster als ein fixer Druckwert, weil Druck bei kapazitiven Tablets je nach Treiber semantisch unzuverlässig oder gar nicht exponiert sein kann. Die Hypothese muss gegen bloßes Aufsetzen, Handrutsch und Korrektur verglichen werden.

## 11. Vertiefte HCI-Evidenz: Lernkurven, Mikrogesten und Enslavement

### Twiddler und Chording-Lernkurven

- **Lyons et al., Twiddler Typing, CHI 2004**, DOI [10.1145/985692.985777](https://doi.org/10.1145/985692.985777): Chording hat eine steilere Lernkurve als Multi-Tap; genaue Novizen-WPM im Abstract nicht extrahiert.
- **Lyons, Plaisted, Starner, Expert Chording Text Entry on the Twiddler, ISWC 2004**, [IEEE](https://ieeexplore.ieee.org/document/1364695): n=5 Experten, Mittel 47 WPM nach ungefähr 25 Stunden Übung. Das ist ein belastbarer Realitätscheck: selbst spezialisiertes Chording ist nicht bei 150 WPM.
- **Lyons et al., Experimental Evaluations of the Twiddler, HCI 2006**, DOI [10.1207/s15327051hci2104_1](https://doi.org/10.1207/s15327051hci2104_1): Longitudinalstudie zu Novize→Experte, Software T-CAT/Twidor und Soukoreff/MacKenzie-Phrasenset; vollständige Block-/Fehlerraten noch zu prüfen.
- **Clarkson et al., Typing Rates on mini-QWERTY Keyboards, CHI 2005**, [PDF](https://sites.cc.gatech.edu/home/thad/p/030_10_MTE/mini-qwerty-chi05.pdf): 20×20-Minuten-Sitzungen, Session 1 31,72 WPM, Session 20 60,03 WPM. Das ist eine nützliche Lernkurven-Referenz für Soft-/Touch-Keyboards, aber kein 0G-Nachweis.
- **Clawson et al., Impacts of Limited Visual Feedback, ISWC 2005**, [paper information](https://dl.acm.org/doi/10.1145/1099802.1099803): fehlendes visuelles Feedback beeinträchtigt Experten-Chording nicht grundsätzlich; eyes-free ist also prinzipiell möglich, aber nicht automatisch schnell.

### Flat-glass und unsichtbare Tastatur

- **Typing on an Invisible Keyboard, CHI 2018**, DOI [10.1145/3173574.3174013](https://doi.org/10.1145/3173574.3174013): 31,3 → 37,9 WPM nach 3×20–25 Minuten; sichtbare Kontrolle 41,6 WPM; WER etwa 2,4–2,5 %. Adaptierte räumliche Modelle und ein LM waren entscheidend.
- **Typing on Flat Glass, CHI 2011**, [ACM DOI](https://doi.org/10.1145/2048064.2048080): zehnfingerige Expertenmuster auf Glas; die Arbeit begründet persönliche Drift-/Zielmodelle. Die exakten Zahlen müssen im Volltext geprüft werden.
- **Personalized Input, CHI 2012**, DOI [10.1145/2207676.2208520](https://doi.org/10.1145/2207676.2208520): automatische Anpassung an Nutzer, Tasten und Handhaltung verbessert Touch-Typing; quantitativer Gain im Volltext zu prüfen.
- **Tinwala & MacKenzie, Eyes-Free Text Entry with Error Correction, NordiCHI 2010**, DOI [10.1145/1868914.1868972](https://doi.org/10.1145/1868914.1868972): Graffiti-Strokes plus auditive Korrektur; Mittel 10,0 WPM, maximal 21,5 WPM, Accuracy 95,7 %. Verzögerte Rückmeldung erhöhte die Rate gegenüber unmittelbarer Rückmeldung.

### Palm rejection, Kontaktgröße und Vorberührung

- **PalmTouch, CHI 2018**, DOI [10.1145/3173574.3173934](https://doi.org/10.1145/3173574.3173934): kapazitive Rohbilder + ML; 99,53 % mittlere Genauigkeit und 0,09 % False-Positive-Rate in realistischen Szenarien. Die Daten benötigen OEM-Rohzugang, nicht die Standard-API.
- **Probabilistic Palm Rejection, CHI 2014**, DOI [10.1145/2556288.2557056](https://doi.org/10.1145/2556288.2557056): Features Radius-Mittelwert/-Varianz/Min/Max, Abstand zu anderen Touches, Geschwindigkeit/Beschleunigung; iterative Vorwärts-/Rückwärtsfilterung ±100 ms; 0,016 Palm-Fehltrigger pro Pen-Stroke bei 98 % korrekt akzeptierten Stylus-Eingaben.
- **Pre-Touch Sensing, CHI 2016**, DOI [10.1145/2858036.2858582](https://doi.org/10.1145/2858036.2858582): Self-Capacitance-Sensorik erkennt Finger über der Oberfläche und Griffe um Kanten; Hover liefert Kontext/Antizipation, aber keine zuverlässige Textposition.
- Consumer-Touch-APIs liefern normalerweise keinen Hover-State. Ein PTH-660-Prototyp darf daher nicht auf eine nicht vorhandene Hover-Funktion bauen, außer der konkrete Treiber dokumentiert sie.

### Mikrogesten

- **User Elicitation on Single-Hand Microgestures, CHI 2016**, DOI [10.1145/2858036.2858589](https://doi.org/10.1145/2858036.2858589): Finger-Dexterität und Mikrogesten sind stark fingerabhängig; Ring-/Kleinfinger sollten nicht als äquivalent zu Daumen/Index angenommen werden.
- **Grasping Microgestures, CHI 2019**, DOI [10.1145/3290605.3300632](https://doi.org/10.1145/3290605.3300632): Cluster von Hook/Palmar/Cylindrical/Tip/Lateral-Gesten; ruhende Finger werden je nach Grasp unterschiedlich rekrutiert.
- **SoloFinger, CHI 2021**, DOI [10.1145/3411764.3445197](https://doi.org/10.1145/3411764.3445197): eine einzelne bewegte Fingerbewegung gegen statische Restfinger ist ein gutes Signal gegen Alltags-Hintergrundbewegung.
- **EFRing, IMWUT 2023**, DOI [10.1145/3569478](https://doi.org/10.1145/3569478): 9 Daumen-zu-Index-Gesten mit 89,5 % within-user und 85,2 % cross-user accuracy; kontinuierliches 1D-Tracking MSE 3,5 % generisch bzw. 2,3 % personalisiert. Das ist ein starker Beleg, dass zusätzliche Ring-/Armsensorik die Identität lösen kann, aber keine direkte PTH-660-Lösung.

### Enslavement: belastbare Grenzen für das Layout

Finger-Enslavement ist ein physiologisches Multi-Finger-Kraftproblem; die relevanten Befunde stammen ursprünglich aus Kraft-/Bewegungsstudien, nicht aus kapazitivem Multi-Touch:

- **Kapur, Friedman, Zatsiorsky, Latash, Finger Interaction in 3D Pressing Task, Exp Brain Res 2010**, DOI [10.1007/s00221-010-2213-7](https://doi.org/10.1007/s00221-010-2213-7): Index erzeugt die kleinsten ungewollten Kräfte; der Fähigkeitsrang zum Enslaven ist etwa Index < Middle < Ring/Little. Ringfinger ist der problematischste Nebenfinger.
- Reviews der Zatsiorsky/Latash-Linie dokumentieren Force Sharing, Force Deficit, Enslaving und Occlusion. Daraus folgt für HCI eine **Designregel**, nicht eine direkt gemessene Touch-Decoder-Genauigkeit: Ring-/Kleinfinger nicht als unabhängige, zeitkritische Tasten behandeln.
- **BiTipText, CHI 2020**, DOI [10.1145/3313831.3376306](https://doi.org/10.1145/3313831.3376306): 23,4 WPM, 0,03 % UER; Layoutoptimierung über 67.108.864 Kandidaten und Handedness-Sequenzen reduzierte Mehrdeutigkeit.
- **TapType, CHI 2022 / arXiv 2410.06001**, [arXiv](https://arxiv.org/abs/2410.06001): 19,2 WPM online nach 30 Minuten, CER 0,6 %, >25 WPM für Experten, OOV ca. 9 WPM. Wrist-IMU-Fingerwahrscheinlichkeiten werden mit n-Gram-Prior fusioniert.

Für die Touch-Oberfläche bedeutet das: Die Matrix eines kapazitiven Decoders sollte zunächst **Index/Middle plus Daumen** priorisieren, Ringfinger-Kontakte als „dependent“ unterdrücken und eine aktive Bewegung des Nutzers als Evidence-Höhung verwenden. Individuelle Enslavement-Matrizen aus Kontaktflächen zu schätzen ist derzeit eine **Hypothese**, kein evidenzbasierter Algorithmus.

## 12. Realistische Zielhierarchie

| Ziel | Status | Bedingung |
|---:|---|---|
| 19–25 WPM | gut gestützt | zehnfingerige passive Tap-Erkennung mit 30 Minuten Training und LM |
| 31–40 WPM | gut gestützt | unsichtbares 1–2-Finger-QWERTY-Modell, nach Stunden Training |
| 45–60 WPM | als langfristiges Expertenziel | etwa 25 Stunden Twiddler-Chording oder starker sequenzieller Decoder |
| 70+ WPM | experimentell möglich | TypeAnywhere-ähnliche Tap-Sequenz + starkes LM; OOV separat prüfen |
| 150–250 WPM | derzeit nicht evidenzbelegt | kein gefundener direkter 0G-/PTH-660-Benchmark; Forschungsziel, nicht Prognose |


1. Kann die PTH-660-Ausgabe zwischen Kontaktfläche, Kontakt-ID und anatomischer Fingerklasse überhaupt unterscheiden?
2. Wie groß ist der Ringfinger-„enslavement gain“ \(\beta_{r\leftarrow m}\) bei verschiedenen Griffweisen?
3. Ist ein **expliziter Armierungsmodus** schneller und ermüdungsärmer als dauerhaftes Ruhe-Tracking?
4. Welche Overlay-Geometrie erzeugt echte propriozeptive Orientierung, ohne zusätzliche Sensorik?
5. Wie viele Korrekturen darf ein LM verdecken, bevor eine Eingabe als „committed“ gilt?
6. Ist QWERTY-Finger-Identität auf einer 0G-Fläche stabiler als absolute QWERTY-Zielposition?
7. Welche Plover-Stroke-Variante maximiert WPM bei gleichzeitig minimierender Mehrdeutigkeit?
