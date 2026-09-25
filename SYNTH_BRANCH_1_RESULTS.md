# SYNTH-BRANCH-1 Frozen Results

**Run status:** completed frozen synthetic comparison  
**Protocol:** `SYNTH-BRANCH-1`, version 1  
**Manifest SHA-256:** `5793c2af9ee532cbda69ff7791d23c88f6d4f0575d0760e4788ef4847bea35e8`  
**Evidence class:** `SYNTHETIC`  
**Validity boundary:** offline synthetic comparison only; no hardware, human, WPM, correction, or text-accuracy evidence

**Promotion status:** `NON-PROMOTIONAL — STRUCTURALLY AUDITED`
**Post-failure decision:** `POST_FAILURE_BRANCH_DECISION.md`

## Decision summary

- **Contact Field:** rejected as the current implementation. Its exact generated-positive metrics are preserved, but the favorable null result is not credited because the harness forced null abstention and its class-count parity leaked labels. The current implementation remains rejected; the audit does not prove every redesign impossible.
- **Elastic Word:** remains a **synthetic control/fallback**, not a product branch. Its exact perfect generated score is preserved but is not promotion, safety, generalization, or severe-nuisance evidence: the severe transform was a near-duplicate, calibration was unused, splits shared generators, and training used one exemplar per class.
- **FCPT:** arithmetic-only and primitive-rejected. The run contains 27 modeled-cost parameter settings and no recognition metrics; modeled cost is not accuracy.
- **No branch is promoted.** This historical run is followed by the repaired Test 0 comparator and the failed TSF synthetic falsifier; the current state requires a fresh post-failure branch decision.

## Frozen manifest and run envelope

The manifest declared seed `1729`, 20/5/20 sessions, 10 instances per class per session, 10 null instances per session, and nuisance levels `clean`, `mild`, `moderate`, and `severe`. The run reports 1,800 test events for each recognition arm: 1,600 positive events and 200 null events. **Post-failure audit correction:** the splits were not independent generator families; they called shared generator functions, calibration was generated but unused, and one training exemplar was selected per class. FCPT has 27 modeled-cost settings and 27 layout-comparison rows; it has no recognizer and therefore no recognition event accuracy.

All times, where present in the machine-readable result, are offline implementation cost only. They are not human latency or throughput.

## Exact recognition metrics

| Metric | Contact Field | Elastic Word |
|---|---:|---:|
| Macro top-1 recall | `0.585` | `1.0` |
| Balanced accuracy | `0.585` | `1.0` |
| Chance macro recall | `0.125` | `0.125` |
| One-sided 95% lower bound | `0.5646117205785063` | `0.9983118898757506` |
| Coverage | `0.8` | `0.8888888888888888` |
| Abstention rate | `0.19999999999999996` | `0.11111111111111116` |
| Wrong-commit rate | `0.28` | `0.0` |
| Conditional accepted-event error | `0.35` | `0.0` |
| Null false-commit rate | `0.0` | `0.0` |
| One-sided 95% null false-commit upper bound | `0.013347160654775625` | `0.013347160654775625` |

Contact Field class-wise recalls were: `cf0=0.47`, `cf1=0.455`, `cf2=0.645`, `cf3=0.575`, `cf4=0.615`, `cf5=0.645`, `cf6=0.685`, `cf7=0.59`. Elastic Word class-wise recall was `1.0` for every class `ew0` through `ew7`.

### Nuisance-stratum recall

| Nuisance | Contact Field recall | Contact Field count | Elastic Word recall | Elastic Word count |
|---|---:|---:|---:|---:|
| Clean | `0.9625` | `480` | `1.0` | `480` |
| Mild | `0.7625` | `480` | `1.0` | `480` |
| Moderate | `0.3375` | `320` | `1.0` | `320` |
| Severe | `0.0` | `320` | `1.0` | `320` |

## Gate evaluation

The frozen recognition thresholds require macro recall at least `0.25`, a one-sided lower bound above chance `0.125`, coverage at least `0.80`, conditional accepted-event error at most `0.025`, and nuisance retention of at least 80% of clean recall (with nuisance recall above chance). The Contact Field gate additionally requires a full-descriptor control margin of at least `0.10` with a positive lower bound.

- **Contact Field (`SYNTH-CF-1`): FAIL / current implementation rejected.** Its exact macro recall `0.585`, lower bound `0.5646117205785063`, coverage `0.8`, wrong-commit rate `0.28`, conditional accepted-event error `0.35`, null rate `0.0`, null upper bound `0.013347160654775625`, and nuisance recalls `0.9625/0.7625/0.3375/0.0` remain valid as frozen outputs. Wrong-commit/accepted-error and nuisance failure still reject the implementation. The null rate/bound is not credited as recognizer safety because the harness used `expected_output is None` to force abstention; the null upper bound also exceeds the nominal `0.01` ceiling. Count parity leaked labels, so the descriptor is not credited as a clean representation result.
- **Elastic Word (`SYNTH-EW-1`): exact comparator output preserved; `PASS` claim withdrawn as promotion evidence.** Its exact macro recall/balanced accuracy `1.0`, lower bound `0.9983118898757506`, coverage `0.8888888888888888`, error rates `0.0`, null upper bound `0.013347160654775625`, and all-stratum recall `1.0` remain recorded. The score is not credible safety, generalization, or severe-nuisance evidence because nulls were forced to abstain, splits shared generators, calibration was unused, training used one exemplar, and the severe insertion was only `0.0001` coordinate units from a neighbor. Elastic remains control/fallback only.
- **FCPT (`SYNTH-FCPT-1`): not a recognition gate.** There are 27 modeled-cost settings only, `recognition_metrics=null`, and the result explicitly states that modeled layout cost is not recognition accuracy. The current selected-thumb primitive remains rejected. Any arithmetic result cannot revive that primitive or support hardware, human, WPM, correction, or text-accuracy claims.

## Limitations and interpretation

This is a deterministic offline comparator over generated raw geometry/control paths. It does not observe a device, validate anatomy or reach, establish contact segmentation, measure real event timing, test human fatigue or learnability, validate English steno decoding, measure WPM, measure correction throughput, or measure text accuracy. The post-failure audit further finds that null abstention, shared split generators, unused calibration, one-exemplar training, Contact Field count leakage, and a near-duplicate Elastic severe nuisance prevent favorable null/safety and perfect-Elastic claims from serving as promotion evidence.

The exact metrics remain historical facts. The valid decision is narrow: the current Contact Field implementation is rejected; Elastic remains a control/fallback; FCPT remains arithmetic-only with its selectable-thumb primitive rejected. `POST_FAILURE_BRANCH_DECISION.md` freezes TSF as the single next research-only branch after Test 0 comparator repair. RCI and SOS are later comparators; dwell, topology, and raw-field work remain hold/prerequisite. No branch or hardware claim is promoted.
