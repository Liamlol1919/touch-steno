# Scientific Comparator Test 0 Results

**Run status:** completed and frozen synthetic comparator repair  
**Protocol:** `SCIENTIFIC-COMPARATOR-TEST-0`, version 1  
**Manifest:** `synthetic_comparator_manifest.json`  
**Canonical frozen-manifest digest (`FROZEN_MANIFEST_SHA256`):** `922524b495753bd2f4394380b850f4d788c4b38b9af4ea057e57414fe601a25f`  
**Raw file SHA-256:** `eccee106fab4b7aa19a48d0f160c4ea4a933e74b794b996da39a980747aa77c4`  
**Evidence class:** `SYNTHETIC`  
**Decision:** `PASS — evidence boundary validated and comparator freeze complete`

Test 0 validates only the scientific comparator's evidence boundary. It does not implement,
evaluate, or promote Temporal Set-Flow (TSF), and it provides no hardware, human, WPM,
correction, text-accuracy, or product evidence.

## Executed verification

The comparator's 9 integrity tests passed. The full repository suite also passed: **286 tests
run, 1 skipped, 0 failed**. The comparator loads and validates the frozen manifest at runtime
through the read-only `load_frozen_manifest()` API. Any manifest mutation is refused with
`ValueError`, so the canonical manifest digest is an enforced runtime gate. The frozen fixture
manifest declares synthetic-only scope and `hardware_validity=false`.

## Manifest and fixture scope

Each observation contains five frames at an 8 ms frame interval. Every positive has exactly
four unordered contact points. The fixture contains three classes: `alpha`, `beta`, and `gamma`.

| Split | Independent family | Sessions | Positives per class per session | Nulls per session | Total sequences |
|---|---|---:|---:|---:|---:|
| Train | `polygonal_field_translation_A` | 4 | 3 | 2 | 44 |
| Calibration | `diamond_field_pulse_B` | 3 | 2 | 2 | 24 |
| Test | `rectangular_field_twist_C` | 4 | 3 | 2 | 48 |

The train family uses a four-point convex polygon with constant class-axis translation and
bounded scale/translation jitter. The calibration family uses a four-point diamond with an
eased axis-biased pulse and bounded radius, drift, and point jitter. The test family uses a
four-point rectangle with class-directed progress plus alternating twist and bounded start
offset and point jitter. These are separately implemented generator functions; they share no
generation function and copy no prototypes.

## Decision isolation proof

The recognizer receives only `sequence_id`, monotonic frame times, and unordered point
observations with sensor-native `x`, `y`, and `pressure` values. Split, session, class, null
flag, nuisance, expected output, and ground truth are excluded before the decision.

Every decision is first produced from the observation and JSON-serialized with only
`sequence_id`, `candidate`, `confidence`, and `accepted`. Ground truth is joined only after
serialization, solely for scoring. The integrity suite verifies that the serialized decision
contains no class or ground-truth fields and records
`decisions_were_serialized_before_truth_join=true`. Point-order permutation preserved the
semantic decisions and event count exactly:
`point_order_permutation_invariant=true` and
`permutation_semantic_decisions_and_event_count_unchanged=true`.

## Training, calibration, and test separation

The nearest-centroid baseline aggregates every allowed training exemplar, rather than selecting
one prototype per class. It uses 12 positive exemplars for each of `alpha`, `beta`, and
`gamma`, for 36 aggregated positive training exemplars.

Calibration data alone selects the acceptance threshold. The frozen selection is the midpoint
between the minimum positive confidence and maximum null confidence on calibration data. Its
selected value is exactly `0.15827817469940747`; the test examples and labels do not
participate in selection.

The test family remains untouched until calibration has fixed that threshold. Test results
therefore describe the frozen train/calibration/test protocol rather than test-tuned behavior.

## Count matching and integrity controls

Cardinality is matched across classes: every positive in every split has exactly four points.
The count-only recognizer obtains positive accuracy `0.3333333333333333`, equal to the
three-class chance rate, so contact count does not reveal the class.

| Integrity control | Exact positive accuracy | Result |
|---|---:|---|
| Nearest-centroid baseline | `1.0` | Passes fixture accuracy and null gate |
| Always-positive | `0.3333333333333333` | Fails the null gate as required |
| Shuffled-label | `0.2222222222222222` | Below chance `0.3333333333333333` |
| Count-only | `0.3333333333333333` | Chance; no class recovery from count |
| Path-length nuisance-only | `0.3333333333333333` | Chance; path length alone is insufficient |

The always-positive control has null false-commit rate `1.0`, fails the declared null gate,
and exposes all eight null false-commit sequence IDs in its output. This demonstrates that
null rejection is not produced by a label-derived or expected-output-derived forced
abstention.

## Executed baseline metrics

The nearest-centroid baseline's exact Test 0 outputs are:

| Metric | Value |
|---|---:|
| Positive accuracy | `1.0` |
| Chance accuracy | `0.3333333333333333` |
| Null false-commit rate | `0.0` |
| Maximum allowed null false-commit rate | `0.0` |
| Null gate passed | `true` |
| Calibration acceptance threshold | `0.15827817469940747` |
| Session-cluster bootstrap clusters | `4` |
| Session-cluster bootstrap replicates | `256` |
| Positive accuracy 95% session-clustered interval | `[1.0, 1.0]` |
| Decisions serialized before truth join | `true` |
| Point-order permutation invariant | `true` |

The positive-accuracy interval is computed by a deterministic session-cluster bootstrap, not
an event-level interval. All sequences in a sampled session are retained together, so
correlated sequences are not treated as independent session observations.

## Hard limitations and claim boundary

- This is a bounded, deterministic synthetic fixture, not a device, human, or deployment
  evaluation.
- Test 0 validates comparator integrity only. It does not implement TSF or establish that TSF
  is useful, safe, superior, or ready for a synthetic falsifier.
- The successful baseline is a nearest-centroid control on the declared fixture, not a
  TSF result. TSF requires a separate protocol; comparator completion neither advances nor
  promotes TSF.
- The test set has only four session clusters. The 256-replicate bootstrap describes sampling
  variability over those four synthetic sessions; it cannot create broader population
  coverage or hardware-level uncertainty.
- The fixture is small and intentionally controlled. It does not test anatomy, identity,
  segmentation quality, palm contamination, fatigue, learnability, human timing, WPM,
  correction throughput, or text accuracy.
- Passing integrity controls does not establish synthetic or real-world safety, product
  readiness, privacy by retention, or external integration.
- RCI and SOS remain later comparators. At the time of this Test 0 record, TSF was the next unimplemented research branch; its subsequent frozen falsifier failed and it is now held/rejected. No branch is promoted.

The narrow decision from Test 0 was: **the comparator boundary was frozen; TSF was then authorized as a research-only implementation step.** The later TSF falsifier result supersedes that prospective status. No hardware, human, performance, or product claim is made.
