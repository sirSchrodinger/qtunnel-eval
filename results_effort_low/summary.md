| model | trials/task | pass rate | pass^k (all k trials correct) | tasks always passed | tasks never passed |
|---|---|---|---|---|---|
| claude-haiku-5-5 | 3 | 95% (37/39) | 11/13 tasks | 11 | 0 |
| claude-sonnet-5-5 | 3 | 100% (39/39) | 13/13 tasks | 13 | 0 |
| claude-opus-5-5 | 3 | 97% (38/39) | 12/13 tasks | 12 | 0 |
| claude-fable-5-1 | 3 | 97% (38/39) | 12/13 tasks | 12 | 0 |

Per task (correct trials / trials):

| task | claude-haiku-5-5 | claude-sonnet-5-5 | claude-opus-5-5 | claude-fable-5-1 |
|---|---|---|---|---|
| t1_thin_barrier_exact | 3/3 | 3/3 | 3/3 | 3/3 |
| t2_above_barrier | 3/3 | 3/3 | 3/3 | 3/3 |
| t3_threshold_E_equals_V0 | 3/3 | 3/3 | 3/3 | 3/3 |
| t4_effective_mass_interface | 3/3 | 3/3 | 3/3 | 3/3 |
| t5_resonance_energy | 2/3 | 3/3 | 3/3 | 3/3 |
| t6_asymmetric_resonance_peak | 3/3 | 3/3 | 3/3 | 3/3 |
| t7_thickness_sensitivity_decades | 3/3 | 3/3 | 3/3 | 3/3 |
| t8_stm_barrier_error_factor | 3/3 | 3/3 | 3/3 | 3/3 |
| t9_thick_barrier_validity | 3/3 | 3/3 | 3/3 | 3/3 |
| t10_sloped_barrier | 3/3 | 3/3 | 3/3 | 3/3 |
| t11_resonance_width | 3/3 | 3/3 | 2/3 | 3/3 |
| t12_five_layer_stack | 3/3 | 3/3 | 3/3 | 3/3 |
| t13_triple_barrier_splitting | 2/3 | 3/3 | 3/3 | 2/3 |

Failure labels (task, label: models that produced it):

- t11_resonance_width: wrong: other: claude-opus-5-5
- t13_triple_barrier_splitting: wrong: other: claude-fable-5-1, claude-haiku-5-5
- t5_resonance_energy: wrong: other: claude-haiku-5-5
