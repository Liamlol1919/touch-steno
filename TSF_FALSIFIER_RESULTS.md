# TSF Synthetic Falsifier Results

**Run status:** completed; falsifier failed  
**Protocol:** `TSF-SYNTHETIC-FALSIFIER`, version 1  
**Manifest:** `tsf_falsifier_manifest.json`  
**Canonical frozen-manifest digest:** `a95f0d18832362b314417c557d615be4802cc869010617113fb75100090ffe7e`  
**Evidence class:** `SYNTHETIC`  
**Decision:** `HOLD / REJECT — no TSF advancement or claim`  
**Recorded claim:** `none`

The bounded TSF prototype was identity-free and passed its structural tests, but the frozen
synthetic falsifier did not show a positive temporal-information margin. The current research
implementation is therefore held/rejected. It is not promoted to a product or hardware branch,
and it must not be retuned to erase the failed margin.

## Executed verification

`run_falsifier()` was executed against the frozen manifest. All **11 TSF tests passed**. The
prototype's structural behavior does not override the failed recognition and comparative gates.

The train, calibration, and test families were `triangles_orthogonal_pulse_A`,
`diamonds_alternating_shear_B`, and `asymmetric_hexagons_local_pinch_C`, respectively. The
synthetic test set contained **12 examples** in **3 session clusters**. Calibration selected
only the acceptance threshold; `test_used_for_selection=false`. Every recognizer serialized
its decisions before truth join.

## Exact TSF metrics

| Metric | Exact result |
|---|---:|
| Positive accuracy | `0.0` |
| Positive-accuracy session-cluster bootstrap | 3 clusters, 256 replicates |
| Positive-accuracy 95% interval | `[0.0, 0.0]` |
| Null false-commit rate | `0.0` |
| Null-rate session-cluster bootstrap | 3 clusters, 256 replicates |
| Null-rate 95% interval | `[0.0, 0.0]` |
| Calibration acceptance threshold | `0.0834054855946207` |
| Test used for threshold selection | `false` |
| Decisions serialized before truth join | `true` |

The confidence intervals use a deterministic session-cluster bootstrap. They describe only
variability over the three synthetic test sessions.

## Exact controls

| Recognizer | Positive accuracy | Null false-commit rate |
|---|---:|---:|
| `tsf` | `0.0` | `0.0` |
| `count_only` | `0.3333333333333333` | `0.6666666666666666` |
| `centroid_spread_only` | `0.3333333333333333` | `0.3333333333333333` |
| `instantaneous_shape` | `0.0` | `0.0` |
| `current_contact_field` | `0.0` | `0.0` |
| `rigid_motion` | `0.3333333333333333` | `0.3333333333333333` |

The best control was `rigid_motion`, with positive accuracy
`0.3333333333333333`. The observed TSF-versus-best-control margin was
`-0.3333333333333333`. Its paired session-cluster bootstrap used 3 clusters and 256
replicates, with a 95% interval of `[-0.6666666666666666, 0.0]`.

## Frozen gates and outcomes

All frozen gates were required; none compensated for another.

| Frozen gate | Requirement | Exact outcome | Result |
|---|---|---|---|
| Positive accuracy | At least `0.8` | `0.0` | **FAIL** |
| Null false-commit rate | At most `0.0` | `0.0` | **PASS** |
| TSF margin over best control | At least `0.1` | `-0.3333333333333333` | **FAIL** |
| Paired margin lower 95% bound | Greater than `0.0` | `-0.6666666666666666` | **FAIL** |

The overall `kill_gate_passed` result was `false`. Under the frozen manifest, failure of any
gate requires `claim=none`; that requirement was met.

## Interpretation and limitations

The result is a falsification of the current bounded TSF research implementation under this
frozen synthetic protocol. It does not show that temporal deformation is useful, that TSF is
safe in deployment, or that every possible TSF redesign is impossible. It does show that this
prototype did not meet its positive-accuracy or temporal-information-margin gates.

This is synthetic-only evidence from a small controlled fixture with three test session
clusters. It is not hardware, human, anatomy, fatigue, privacy-by-retention, WPM, correction,
text-accuracy, Plover, network, product, or external-repository evidence. Passing structural
tests establishes implementation properties only; it cannot replace the failed falsifier.

The next executable action is a fresh post-failure branch decision, not TSF threshold or
parameter tuning. RCI and SOS remain unimplemented later comparators and receive no automatic
promotion or authorization from this failed run. Any later branch requires its own frozen
hypothesis, comparator, and falsifier decision.
