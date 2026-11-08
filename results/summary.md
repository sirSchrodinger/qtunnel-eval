| model | trials/task | pass rate | pass^k (all k trials correct) | tasks always passed | tasks never passed |
|---|---|---|---|---|---|
| claude-haiku-5-5 | 3 | 97% (38/39) | 12/13 tasks | 12 | 0 |
| claude-sonnet-5-5 | 3 | 100% (39/39) | 13/13 tasks | 13 | 0 |
| claude-opus-5-5 | 3 | 100% (39/39) | 13/13 tasks | 13 | 0 |
| claude-fable-5-1 | 3 | 100% (39/39) | 13/13 tasks | 13 | 0 |
| qwen2-5-3b-instruct-q4_K_M-cpu | 3 | 5% (2/39) | 0/13 tasks | 0 | 11 |

Per task (correct trials / trials):

| task | claude-haiku-5-5 | claude-sonnet-5-5 | claude-opus-5-5 | claude-fable-5-1 | qwen2-5-3b-instruct-q4_K_M-cpu |
|---|---|---|---|---|---|
| t1_thin_barrier_exact | 3/3 | 3/3 | 3/3 | 3/3 | 0/3 |
| t2_above_barrier | 3/3 | 3/3 | 3/3 | 3/3 | 1/3 |
| t3_threshold_E_equals_V0 | 3/3 | 3/3 | 3/3 | 3/3 | 1/3 |
| t4_effective_mass_interface | 3/3 | 3/3 | 3/3 | 3/3 | 0/3 |
| t5_resonance_energy | 3/3 | 3/3 | 3/3 | 3/3 | 0/3 |
| t6_asymmetric_resonance_peak | 3/3 | 3/3 | 3/3 | 3/3 | 0/3 |
| t7_thickness_sensitivity_decades | 2/3 | 3/3 | 3/3 | 3/3 | 0/3 |
| t8_stm_barrier_error_factor | 3/3 | 3/3 | 3/3 | 3/3 | 0/3 |
| t9_thick_barrier_validity | 3/3 | 3/3 | 3/3 | 3/3 | 0/3 |
| t10_sloped_barrier | 3/3 | 3/3 | 3/3 | 3/3 | 0/3 |
| t11_resonance_width | 3/3 | 3/3 | 3/3 | 3/3 | 0/3 |
| t12_five_layer_stack | 3/3 | 3/3 | 3/3 | 3/3 | 0/3 |
| t13_triple_barrier_splitting | 3/3 | 3/3 | 3/3 | 3/3 | 0/3 |

Failure labels (task, label: models that produced it):

- t10_sloped_barrier: format: no ANSWER line: qwen2-5-3b-instruct-q4_K_M-cpu
- t10_sloped_barrier: wrong: other: qwen2-5-3b-instruct-q4_K_M-cpu, qwen2-5-3b-instruct-q4_K_M-cpu
- t11_resonance_width: wrong: other: qwen2-5-3b-instruct-q4_K_M-cpu, qwen2-5-3b-instruct-q4_K_M-cpu, qwen2-5-3b-instruct-q4_K_M-cpu
- t12_five_layer_stack: wrong: other: qwen2-5-3b-instruct-q4_K_M-cpu, qwen2-5-3b-instruct-q4_K_M-cpu, qwen2-5-3b-instruct-q4_K_M-cpu
- t13_triple_barrier_splitting: wrong: other: qwen2-5-3b-instruct-q4_K_M-cpu, qwen2-5-3b-instruct-q4_K_M-cpu, qwen2-5-3b-instruct-q4_K_M-cpu
- t1_thin_barrier_exact: wrong method: exp_only_no_prefactor: qwen2-5-3b-instruct-q4_K_M-cpu
- t1_thin_barrier_exact: wrong: other: qwen2-5-3b-instruct-q4_K_M-cpu, qwen2-5-3b-instruct-q4_K_M-cpu
- t2_above_barrier: format: no ANSWER line: qwen2-5-3b-instruct-q4_K_M-cpu
- t2_above_barrier: wrong: other: qwen2-5-3b-instruct-q4_K_M-cpu
- t3_threshold_E_equals_V0: format: no ANSWER line: qwen2-5-3b-instruct-q4_K_M-cpu
- t3_threshold_E_equals_V0: wrong: other: qwen2-5-3b-instruct-q4_K_M-cpu
- t4_effective_mass_interface: wrong: other: qwen2-5-3b-instruct-q4_K_M-cpu, qwen2-5-3b-instruct-q4_K_M-cpu, qwen2-5-3b-instruct-q4_K_M-cpu
- t5_resonance_energy: wrong: other: qwen2-5-3b-instruct-q4_K_M-cpu, qwen2-5-3b-instruct-q4_K_M-cpu, qwen2-5-3b-instruct-q4_K_M-cpu
- t6_asymmetric_resonance_peak: format: no ANSWER line: qwen2-5-3b-instruct-q4_K_M-cpu
- t6_asymmetric_resonance_peak: wrong method: unit_peak_symmetric_rule: qwen2-5-3b-instruct-q4_K_M-cpu
- t6_asymmetric_resonance_peak: wrong: other: qwen2-5-3b-instruct-q4_K_M-cpu
- t7_thickness_sensitivity_decades: format: missing key 'decades': qwen2-5-3b-instruct-q4_K_M-cpu, qwen2-5-3b-instruct-q4_K_M-cpu
- t7_thickness_sensitivity_decades: format: no ANSWER line: qwen2-5-3b-instruct-q4_K_M-cpu
- t7_thickness_sensitivity_decades: wrong method: effective_mass_in_denominator_of_kappa: claude-haiku-5-5
- t8_stm_barrier_error_factor: format: no ANSWER line: qwen2-5-3b-instruct-q4_K_M-cpu
- t8_stm_barrier_error_factor: wrong: other: qwen2-5-3b-instruct-q4_K_M-cpu, qwen2-5-3b-instruct-q4_K_M-cpu
- t9_thick_barrier_validity: wrong: other: qwen2-5-3b-instruct-q4_K_M-cpu, qwen2-5-3b-instruct-q4_K_M-cpu, qwen2-5-3b-instruct-q4_K_M-cpu
