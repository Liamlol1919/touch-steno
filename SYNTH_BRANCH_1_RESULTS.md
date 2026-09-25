# SYNTH-BRANCH-1 Frozen Results

**Run status:** completed frozen synthetic comparison  
**Protocol:** `SYNTH-BRANCH-1`, version 1  
**Manifest SHA-256:** `5793c2af9ee532cbda69ff7791d23c88f6d4f0575d0760e4788ef4847bea35e8`  
**Evidence class:** `SYNTHETIC`  
**Validity boundary:** offline synthetic comparison only; no hardware, human, WPM, correction, or text-accuracy evidence

## Decision summary

- **Contact Field:** rejected as the current primary representation. Its discriminability result is above chance, but the frozen run fails the wrong-commit/accepted-event safety and nuisance-retention requirements. This is a rejection of the current representation, not a claim that every possible Contact Field redesign is impossible.
- **Elastic Word:** passes the frozen synthetic recognition comparator, but remains a **synthetic control/fallback**, not a product branch. It still lacks anonymous-contact segmentation and end-to-end event construction.
- **FCPT:** arithmetic-only and primitive-rejected. The run contains 27 modeled-cost parameter settings and no recognition metrics; modeled cost is not accuracy.
- **No branch is promoted to product.** The next action is Contact Field redesign/hold, not claim inflation or more comparator tuning.

## Frozen manifest and run envelope

The run used the frozen manifest above, seed `1729`, disjoint train/calibration/test generator families, 20/5/20 sessions, 10 instances per class per session, 10 null instances per session, and nuisance levels `clean`, `mild`, `moderate`, and `severe`. The run reports 1,800 test events for each recognition arm: 1,600 positive events and 200 null events. FCPT has 27 modeled-cost settings and 27 layout-comparison rows; it has no recognizer and therefore no recognition event accuracy.

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

- **Contact Field (`SYNTH-CF-1`): FAIL / representation rejected.** Recall and its lower bound clear the discriminability threshold (`0.585` and `0.5646117205785063`), and coverage is exactly `0.8`. However, conditional accepted-event error is `0.35` versus the `0.025` maximum, wrong-commit rate is `0.28`, and nuisance retention fails: mild is below 80% of clean and moderate/severe collapse. The reported null upper bound is `0.013347160654775625`, also above the nominal `0.01` safety ceiling. The run does not report a usable full-descriptor-versus-nuisance-only control margin, so that portion cannot be credited as a pass. The failed safety and nuisance gates are decisive for rejecting the current representation; no hold label can override them.
- **Elastic Word (`SYNTH-EW-1`): PASS as the frozen synthetic comparator, with limitations.** Macro recall is `1.0` with lower bound `0.9983118898757506`, coverage is `0.8888888888888888`, accepted-event error and wrong commits are `0.0`, and every nuisance stratum is `1.0`. The exact machine-readable null false-commit upper95 is `0.013347160654775625`; this is retained as a limitation against a literal `0.01` safety ceiling and is not hidden or inflated. The comparator result still supplies no anonymous-contact segmentation, recorder integration, end-to-end event construction, or repair evidence, so Elastic remains control/fallback and is not product-promoted.
- **FCPT (`SYNTH-FCPT-1`): not a recognition gate.** There are 27 modeled-cost settings only, `recognition_metrics=null`, and the result explicitly states that modeled layout cost is not recognition accuracy. The current selected-thumb primitive remains rejected. Any arithmetic result cannot revive that primitive or support hardware, human, WPM, correction, or text-accuracy claims.

## Limitations and interpretation

This is a deterministic offline comparator over generated raw geometry/control paths. It does not observe a device, validate anatomy or reach, establish contact segmentation, measure real event timing, test human fatigue or learnability, validate English steno decoding, measure WPM, measure correction throughput, or measure text accuracy. The frozen generator and split are useful for falsifying a representation against nuisance and safety conditions, but they do not establish product behavior.

The result therefore changes research prioritization rather than product evidence: Contact Field is rejected pending redesign or a held decision; Elastic Word is retained as a synthetic control/fallback only; FCPT remains arithmetic-only with its selectable-thumb primitive rejected. No branch is promoted to product on these results.
