# Fünf Stunden, zwei Agenten — was wirklich passiert ist

**Zeitraum:** 2026-09-25, ca. 06:00–10:00 MESZ
**Beteiligt:** Agent 1 (Haupt-Baupfad), Agent 2 (Forschung/Modell/Auswertung), Nutzer als Messperson
**Stand:** 86 Commits, 24 Issues, 125+ Tests grün

---

## 1. Das Urteil zuerst

**Es wurde kein Eingabesystem gebaut.** Kein Steno-Dekoder, der einen echten Strich in
Text übersetzt, existiert. Das war die ursprüngliche Frage. Sie ist offen.

Was entstanden ist, ist eine **belastbare Neuausrichtung des Problems plus ein
Messgerät**. Das ist kein Produkt, und fünf Stunden sind dafür viel.

---

## 2. Die eine Sache, die zählt: echte Handdaten

Der Nutzer hat rund eine Stunde echte Messungen geliefert. Das war die wertvollste
Rohstoffzufuhr der ganzen Zeit — und sie hat eine zentrale Annahme des Projekts gekippt.

| Messung | Wert | Konsequenz |
|---|---|---|
| Sektor-Genauigkeit, 12 mm, rechter Daumen | **47,6 %** | Modell nahm 58–68 % an — Annahme unbestätigt |
| Ruhe-Streuung ruhender Finger, 9007 Samples | **0,4 mm** (Median) | Sensor arbeitet sauber |
| Signal bei 12 mm Auslenkung | **~30 : 1** | **Der Sensor ist als Fehlerquelle ausgeschlossen** |
| 20-mm-Arm | 0 Events | 31 Blöcke unter dem 88-ms-Detektorfenster |
| Natürliche Daumenhülle | 24,6 × 18,2 mm | größer als die 12-mm-Armannahme |

**Die Fehler liegen in der Hand, nicht im Gerät.** Vorher wusste das niemand; die
Projektmodelle nahmen einen Richtungsfehler als gegeben an und optimierten darunter.

Die Fehlerstruktur ist dabei **kein Rauschen, sondern ein Muster**: jeder Fehler fällt auf
das exakte 180°-Gegenüber (NE↔SW, NW↔SE, S↔N, W↔E). Das ist lösbar, aber noch nicht gelöst.

---

## 3. Die Korrektur, die Agent 2 selbst durchgesetzt hat

Agent 2 veröffentlichte die Kernbehauptung des Zyklus:

> „Die Sprachschicht hebt 6,8 % auf 88,8 % Wortgenauigkeit."

und zog sie **am selben Morgen** zurück. Grund: der Kandidatensatz wurde aus der Zeile des
*beabsichtigten* Sektors gebaut — der Sprachmodell bekam die Antwort vorgegeben. Korrigiert
auf P(wahr | beobachtet) fällt der Gewinn auf ~0. Mit **Oracle-Präfix** (wahre Kontextbuchstaben
vorgegeben) bleibt er bei ~0: es liegt weder an Modellqualität noch an Fehlerfortpflanzung.

Mitgezogen wurden: die Rückzugs-Politik, die Korrekturlast (1,87 → 0,92 Aktionen/Wort) und
**sämtliche WPM-Zahlen**. Alles war stromabwärts vom selben Fehler.

Das ist wertvoll, weil die Korrektur öffentlich und im Repo dokumentiert wurde
(`LM_RECOVERY.md`, Issue #20) — statt die Zahl stillschweigend zu ersetzen.

**Agent 1 hat den Fehler danach behoben**, nicht wiederholt: `lexicon_recovery.py`
erzeugt Kandidaten aus der *beobachteten* Sektor-Spalte und gibt das Zielfort erst danach
zur Bewertung frei (`conditioning: observed-sector-column`).

---

## 4. Die belastbare Modellaussage (synthetischer Kanal, korrekt konditioniert)

`lexicon_recovery.py`, 2000 Versuche je Radius, 20k-Lexikon:

| Radius | Top-1 Wort | richtiges Symbol in Top-3 | Wort im Lexikon erreichbar | **Dekoder wählt korrekt** | unerreichbar | Korrekturen/Wort |
|---|---|---|---|---|---|---|
| 12 mm | 6,8 % | 96,3 % | 80,7 % | **73,6 %** | 14,5 % | 0,264 |
| 15 mm | 15,5 % | 99,1 % | 94,9 % | **89,2 %** | 3,0 % | 0,108 |
| 20 mm | 38,5 % | 99,9 % | 99,5 % | **96,3 %** | ~0 % | 0,038 |

**Das ist die zentrale Erkenntnis des Projekts:** der Sensor liefert die richtige Information
zu 96 % unter den Top-3. Der naive Dekoder nimmt Top-1 und wirft 80 % weg. Eine
wortweise Lexikonsuche holt sie zurück.

**Einschränkung, die in jeder Datei steht:** der Kanal ist synthetisch, kalibriert über
`layout_assignment.py`. Das sind **keine** PTH-660-Messungen. Und die 47,6 % aus der echten
Hand liegen **unter** der 12-mm-Modellannahme — die Kurve beschreibt also einen Kanal, dessen
Fehlerrate real nicht validiert ist.

---

## 5. Was baulich entstanden ist

| Artefakt | Umfang | Zweck |
|---|---|---|
| `guided_calibration.py` | ~370 Zeilen | geführte Messung, Radius-Arm, selbstgetakteter Modus |
| `session_runner.py` | 223 Zeilen | ganze Sitzung in einem Befehl |
| `lexicon_decoder.py` | 188 Zeilen | wortweiser Lexikon-Dekoder |
| `lexicon_recovery.py` | 152 Zeilen | korrekt konditionierte Benchmark |
| `layout_assignment.py` | 237 Zeilen | Sektor-Layout gegen Confusion-Matrix |
| `correction_timing.py` | — | Stoppuhr-Protokoll, tabletfrei |
| `plot_models.py` + `models/*.png` | 3 Abbildungen | Layout, gemessene Confusion, Decoder-Decke |
| Messgeräte | 6 Tasks | noise, palm, sectors, tempo, correction, chord, identity |

Belege im Repo: 3 Abbildungen, 8 Markdown-Dokumente, 24 Issues (20 geschlossen),
125+ grüne Tests.

---

## 6. Was nicht existiert

- **Kein Steno-Dekoder.** Kein Modul übersetzt reale Striche in Steno-Symbole oder Text.
  `stroke_decoder.py` liefert Richtungsvektoren, kein Wort.
- **Kein End-to-End-Textausgang.** Es gibt keine Demo, in der eine Bewegung zu Text wird.
- **Keine brauchbare WPM-Zahl.** Sämtliche Extrapolationen wurden zurückgezogen und nicht
  ersetzt. Sekunden-pro-Korrektur ist in der Literatur **nicht** vorhanden (Agent 2 hat
  das verifiziert) und mit dem Nutzer nicht gemessen worden.
- **Keine Freiheitsgrad-Vermessung.** Die behaupteten 68 % Mitbewegung stammen aus
  Modellannahmen, nicht aus Messung.
- **Kein 20-mm-Datenarm.** Der Lauf scheiterte an der 88-ms-Schwelle, nicht am Nutzer.

---

## 7. Wo die Zeit verloren ging

Der Nutzer verlor rund eine Stunde an **Fehlern, die Agent 2 selbst eingebaut hatte**:

1. **Vier falsche Befehlszeilen** in einem fremd erstellten Session-Plan (Flags, die es
   nicht gab). Hätte beim ersten Schritt abgebrochen.
2. **`--task sectors` hatte keinen Radius-Parameter** — die 12-vs-20-mm-Frage, die als
   entscheidend galt, war nicht messbar. Nachträglich ergänzt.
3. **Kein `--force`**, vorhandene Dateien blockierten jeden zweiten Lauf.
4. **Ein Ausgabepuffer im Runner**, der sämtliche Live-Anweisungen verschluckte.
5. **Ein Countdown mit 1,5 s pro Sektor** — in dieser Zeit weder lesen noch ausführen.
6. **`\r`-basierte Neuanzeige**, die auf dem Terminal des Nutzers zu Dutzenden
   identischen Zeilen führte.

Punkt 1–3 fielen auf, weil die Befehle **nie vorher ausgeführt** worden waren — nur
gegen `--help` und statisch geprüft. Das ist der eigentliche Fehler: Prüfung, die die
Fehlerart nicht abdeckt, auf die es ankam.

---

## 8. Ehrliche Bilanz

| Frage | Antwort |
|---|---|
| Wird das Projekt durch die Messung besser? | **Ja.** Fehlerquelle eingegrenzt, Muster erkannt, Fehlannahme entkräftet |
| Ist die zentrale Hypothese belegt? | **Teilweise.** Synthetisch kalibriert, gegen echte Hand nicht validiert |
| Gibt es ein benutzbares System? | **Nein** |
| War die ursprüngliche Frage beantwortet? | **Nein.** „Wo ist das optimierte Steno-Modell" — es existiert nicht |
| Ist die investierte Zeit verschwendet? | **Der Forschungsanteil nicht. Die Build- und Dokumentationsmenge ja.** |

**Die Reihenfolge war verkehrt.** Zuerst 30 Issues, Messgeräte und Hypothesen, dann nie
das Dekodieren. Die Frage „wo ist das Steno-Modell" hätte am ersten Tag stehen müssen,
nicht am fünften.

---

## 9. Was als Nächstes gebaut werden muss

Ein Steno-Dekoder: Plover-Steno-Tabelle über die Sektorvektoren, lauffähig gegen die
gemessenen 63 Striche. Kein weiterer Messaufwand, kein Tablet. Der Ausgang wird bei 47,6 %
fehlerhaft sein — sichtbar wird aber, ob das Prinzip trägt, und das ist heute unbekannt.

Erst wenn daraus Text wird, sind Genauigkeit, Undo und Tempo sinnvoll zu optimieren.

---

## Anhang: Zustand des Arbeitsverzeichnisses

Das lokale Arbeitsverzeichnis ist **5 Commits hinter `origin/main`** und trägt
uncommittete Änderungen an `scripts/guided_calibration.py` — dieselbe Datei, an der
beide Agenten gearbeitet haben. Beide Agenten arbeiten im selben Verzeichnis; das ist
die Ursache der fehlgeschlagenen Pulls und der doppelten Arbeit.

**Vor weiterer Arbeit:** Änderungen committen oder stashen, dann `git pull --rebase`,
dann `scripts/guided_calibration.py` von Hand zusammenführen.
