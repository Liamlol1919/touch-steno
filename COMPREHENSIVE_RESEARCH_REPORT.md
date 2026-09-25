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
- Ein leeres oder historisches Repository nicht als Beleg für eine aktuelle Implementierung zitieren.
