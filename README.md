# QTunnel-Eval: can frontier models do exact quantum-tunnelling physics without a computer?

**Short description.** Domain: quantum transport in nanoelectronics (tunnel oxides, resonant-tunnelling diodes, STM and molecular junctions). I tried to find a limitation of frontier models on *exact* tunnelling calculations that experts normally do with a transfer-matrix code: 13 closed-book numerical tasks, every one graded by code against an exact reference. **Key finding: I did not find the limitation.** Four Claude models (Haiku 5.5, Sonnet 5.5, Opus 5.5, Fable 5.1) answered 307 of 312 trials correctly (3 trials per task, default and low reasoning effort). The 5 misses are one Haiku slip at default effort (effective mass inverted in the decay constant) and four at low effort, three of them an exact calculation silently replaced by an approximation. A 3B open model fails 37 of 39 trials, in ways the grader is built to label. The submission is therefore (1) an honest negative result with full transcripts, (2) a reusable harness whose references are checked by two independent solvers, and (3) a lesson from my own bug: twelve out of twelve trials agreed on an answer that differed from my reference, and the models were right.

**Video walkthrough (5 min max):** https://github.com/sirSchrodinger/qtunnel-eval/blob/main/video/qtunnel_walkthrough.mp4

## Domain and expertise
Physics undergraduate (Bilkent, PHYS 420 Nanoscience term project on tunnelling in single-molecule junctions). The tasks come from the standard 1D envelope-function treatment of tunnelling (BenDaniel-Duke matching, transfer matrices, resonant tunnelling). The solver and the questions about which approximations fail were written with AI assistance, see "AI use".

## What it tests and why it matters
Whether a model gives the *right number* for exact tunnelling problems, including the cases where a textbook approximation is wrong (thin barriers, threshold, above-barrier reflection, position-dependent effective mass, resonance width, asymmetric double barrier). Tunnelling currents change by about a factor of 2 for a 0.3 eV error in barrier height and by a decade per 0.2 nm of oxide, so device and measurement decisions depend on these numbers. The eval is for people deciding whether a model can be trusted as a first-pass calculator in this field, and it is a template for other closed-form-checkable domains.

## Task overview (13 tasks, one instance each)
| id | what the model must do | why it is hard (what the expert knows) | reference |
|---|---|---|---|
| t1 thin barrier | exact T, E=0.40, V0=1.00 eV, a=0.25 nm | kappa a is about 1: the thick-barrier formula is 27% off | 0.4151 |
| t2 above barrier | exact T for E>V0 | T is 0.939, not 1: reflection survives above the barrier | 0.9388 |
| t3 threshold | exact T for E=V0 exactly | kappa to 0, the sinh formula is 0/0; needs the limit | 0.2336 |
| t4 effective-mass interface | GaAs/AlGaAs barrier, BenDaniel-Duke matching | psi' continuity instead of psi'/m* continuity gives 18% error | 0.05801 |
| t5 resonance energy | first peak of a symmetric double barrier | infinite-well estimate 0.2245 eV vs 0.0862 eV | 0.08624 eV |
| t6 asymmetric double barrier | peak T of the first resonance | the "T=1 on resonance" rule holds only for symmetric structures | 0.6953 |
| t7 oxide thickness | decades lost from 1.0 to 1.2 nm (m*=0.42 in the barrier) | the effective mass belongs inside kappa (m*, not 1/m*) | 1.0155 |
| t8 STM barrier error | I_true/I_calc for 0.3 eV error in 4.5 eV | direction of the ratio | 0.4903 |
| t9 validity of thick-barrier formula | smallest width with 10% agreement | needs the exact ratio (1-u)^2+16e(1-e)u, u=exp(-2 kappa a) | 0.1905 nm |
| t10 sloped barrier | exact T for a linearly falling barrier top | Airy-function regime; WKB without prefactor is 3x off | 0.03240 |
| t11 resonance width | FWHM of the first resonance | needs the exact line shape, not just the level | 16.41 meV |
| t12 five-layer stack | exact T, five layers, layer-dependent mass | six interfaces with mass-dependent matching | 0.03686 |
| t13 triple barrier | splitting of the two lowest resonances | coupling of two wells, numerical | 54.47 meV |

Every prompt states all constants, the matching condition where relevant, the output key and what "exact" means. Prompts are in `tasks/tasks.json`; the reference answers are never sent to a model.

## Grading and how I validated the grader
- Code-based only (`graders/grade.py`): the last line `ANSWER: {"key": number}` is parsed; the number must be within the task tolerance (3% relative for most tasks, 2% for t5, 5% for t10, t11, t12, t13, 0.05 absolute for t7). The outcome is graded, not the method.
- Wrong-method detectors: if an answer misses, it is compared with what common wrong methods give (thick-barrier formula, naive boundary condition, infinite-well level, T=1, inverted ratio, mass inverted) and the failure is labelled.
- `pytest graders` runs 66 tests: the reference passes for every task, answers just inside the tolerance pass, answers just outside fail, every known wrong-method value fails *with the right label*, malformed output fails (no line, wrong key, string, single quotes, NaN), a response that lists every candidate in prose but answers wrongly fails, the last answer line wins.
- References (`reference/solutions.py`) come from a transfer-matrix solver (`qsolver.py`). `reference/independent_check.py` recomputes every reference with a different method (explicit plane-wave amplitudes with a complex linear solve, an analytic resonance condition, closed forms) and all agree to 1e-5 or better (the sliced barrier t10 to 3e-3 with 500 slices).
- No LLM judge is used.

## Setup and run
```
python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
python -m pytest -q graders                       # grader tests
python reference/solutions.py                     # recompute reference answers -> reference/expected.json
python reference/independent_check.py             # independent cross-check of every reference
export ANTHROPIC_API_KEY=...                      # see .env.example
python run_eval.py --backend anthropic --models claude-sonnet-5-5 --trials 3
# OpenAI-compatible endpoints (OpenRouter, Ollama): --backend openai --base-url <url> --models <id>
python regrade.py                                 # re-grade stored raw outputs, rebuild results/summary.md
```
No tools are offered to the model, every trial is an independent single-turn call, the reference is never in the prompt. Runtime and cost of the submitted runs are below. **Not verified:** the `anthropic` and `openai` backends of `run_eval.py` were not run against a live API (no API key was available to me); the results below come from the `claude-cli` backend (Claude Code 2.1.293, `claude -p --tools ""`, clean HOME and empty working directory so no user memory or instructions reach the model (the backend copies your own Claude Code login file into a throwaway HOME for each call and deletes it afterwards), which I checked by asking a model to list its tools: it reported none). The `claude-cli` backend does not expose temperature; the default sampling of each model was used.

## Models tested and results (run date 2026-11-08)
**Main run, default reasoning effort (Claude Code CLI default) plus the open model.** 13 tasks, 3 trials per task, every trial graded by code. pass^k here means all 3 trials of a task are correct. With scores this close to the ceiling I do not claim a ranking between the Claude models.

| model | trials/task | pass rate | pass^k (all k trials correct) | tasks always passed | tasks never passed |
|---|---|---|---|---|---|
| claude-haiku-5-5 | 3 | 97% (38/39) | 12/13 tasks | 12 | 0 |
| claude-sonnet-5-5 | 3 | 100% (39/39) | 13/13 tasks | 13 | 0 |
| claude-opus-5-5 | 3 | 100% (39/39) | 13/13 tasks | 13 | 0 |
| claude-fable-5-1 | 3 | 100% (39/39) | 13/13 tasks | 13 | 0 |
| qwen2.5:3b-instruct-q4_K_M (Ollama, CPU only) | 3 | 5% (2/39) | 0/13 tasks | 0 | 11 |

Per task (correct trials / trials):

| task | claude-haiku-5-5 | claude-sonnet-5-5 | claude-opus-5-5 | claude-fable-5-1 | qwen2.5:3b-instruct-q4_K_M (Ollama, CPU only) |
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

**Low reasoning effort (`--effort low`), same tasks, same grader.**

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

## Failure analysis
**Frontier Claude models: 5 failed trials out of 312** (156 at default effort, 156 at low effort). Every failed trial, with its visible explanation, is in `transcripts/`.

Default effort (1 failure):
- `claude-haiku-5-5`, t7, trial 2: answered 2.418 (reference 1.0155), label: wrong method: effective_mass_in_denominator_of_kappa
  - Why: the model put the effective mass in the *denominator* of kappa (kappa^2 = (V0-E)/[(hbar^2/2m0)(0.42)] instead of multiplying), so kappa came out 13.9 per nm instead of 5.85. A heavier electron must tunnel *less*; a dimension-and-limit check would have caught it.

Low effort (4 failures):
- `claude-fable-5-1`, t13, trial 2: answered 59.0 (reference 54.469), label: wrong: other
- `claude-haiku-5-5`, t13, trial 1: answered 69.0 (reference 54.469), label: wrong: other
- `claude-haiku-5-5`, t5, trial 2: answered 0.169 (reference 0.086238), label: wrong: other
- `claude-opus-5-5`, t11, trial 1: answered 0.0142 (reference 0.016406), label: wrong: other
  - Opus, t11: replaced the exact condition T(E)=0.5 by a Lorentzian escape-rate estimate, and wrote "this is a Lorentzian approximation, not an exact evaluation" in the answer.
  - Haiku, t13: replaced the exact transfer matrix by the Herring double-well formula, and wrote "this is an estimate rather than an exact transfer-matrix result".
  - Fable, t13: quantised the double well while "treating the outer barriers as thick" (8% off), and did not say how large the neglected shift was.
  - Haiku, t5: derived a resonance condition by hand and slipped in the algebra; it picked a wrong root (0.169 eV; the infinite-well estimate of 0.224 eV was used as a sanity check, and 0.169 passed it).

Where models came close: t13 (Fable, 59 vs 54.5 meV, 8% off) and t11 (Opus, 13% off) are within the range an engineer might accept in a first pass, which is exactly the problem: the prompt asked for the exact value and the answer line contains no hint of the approximation.

**Open 3B model (qwen2.5:3b):** {len(fq)} of {len(qwen)} trials failed. {lab['format']} of those are format failures (no ANSWER line or the wrong key), {lab['wrong method']} match a known wrong method (T=1 for an asymmetric double barrier; exp(-2 kappa a) without the prefactor), the other {lab['other wrong']} are wrong numbers with no recognisable method (for example T of about 0.9 for the GaAs barrier). The two passes are t2 and t3, the simplest closed forms. So the eval does separate a small model from the frontier models, and the frontier models fail only where the arithmetic or the exactness is heaviest.

**Validity checks from the guide.** (a) Not 0% everywhere: yes, the frontier models are near 100%, so the tasks are solvable and the grader accepts correct answers. (b) More capability or effort should do better: the low-effort run has 4 failures against 1 at default effort, all in the numerically heaviest tasks (t5, t11, t13) plus the slip at default effort; with 4 and 1 events this is directional only. (c) Headroom: there is almost none for the frontier models, so this eval no longer shows a limitation for them.

## Integrity notes (what I got wrong, and how it was found)
1. **My first reference for t5 and t6 was wrong.** The helper that computes the double-barrier reference gave the *contacts* the free-electron mass instead of 0.067 m0, although the prompt puts 0.067 m0 in every region. After the first run, the first-pass grading said 0 of 12 trials passed t5. The models gave 0.0862 eV in 11 of 12 trials (0.0850 once), my reference said 0.0818 eV. The guide says a 0% pass rate everywhere is a warning sign, so I checked the reference with an independent analytic resonance condition: the models were right, I was wrong. The fix (mass of the contacts), the new references and the independent checks are in the repo; the stored raw outputs were re-graded without any model call (`regrade.py`), the grade given at run time is kept in each raw file under `grade_firstpass`. t6 also changed (0.6819 to 0.6953), the models were within tolerance of both.
2. Two tasks (t10, t11) and two more (t12, t13) were added after the first 9 tasks showed no failures, because the first set had no headroom. They were added for an a-priori reason (numerical regimes where an expert reaches for a code, not because a model failed them) and they are in the results as run; none of the four Claude models fails them either.
3. The author of the tasks, solver and harness is the same model family as the frontier row (Claude). This is a possible bias in what I considered hard; the open-model row and the wrong-method labels are the only evidence here from outside that family.

## Cost and runtime
| run | model | trials | mean output tokens / trial | mean seconds / trial | cost at list price (39 trials) |
|---|---|---|---|---|---|
| default effort | claude-haiku-5-5 | 39 | 17566 | 75 | $0.37 |
| default effort | claude-sonnet-5-5 | 39 | 3517 | 29 | $1.47 |
| default effort | claude-opus-5-5 | 39 | 3922 | 39 | $3.24 |
| default effort | claude-fable-5-1 | 39 | 5108 | 59 | $10.48 |
| low effort | claude-haiku-5-5 | 39 | 13151 | 58 | $0.27 |
| low effort | claude-sonnet-5-5 | 39 | 2575 | 22 | $1.07 |
| low effort | claude-opus-5-5 | 39 | 1871 | 20 | $1.58 |
| low effort | claude-fable-5-1 | 39 | 2060 | 27 | $4.31 |

The Claude costs are the list-price figures reported by Claude Code (`total_cost_usd`); the runs were paid by a subscription, not per token. The whole Claude part (4 models, 2 effort levels, 312 trials) took about 40 minutes of wall-clock time with 4 parallel calls. The open model ran on a CPU-only, heavily loaded 24-thread machine at about 13 tokens per second, about 50 minutes for 39 trials. A rerun of one Claude model with the API backend should cost a few dollars and take 10 to 20 minutes (Haiku writes about 5 times more output tokens per task than Sonnet at default effort).

## Prior work and sources
- Existed before the hackathon (opened 30 Oct 2026): the transfer-matrix solver `qsolver.py`, written 19-23 Oct 2026 for my PHYS 420 term-project code (`tm.py` there). Nothing else in this repository existed before 8 Nov 2026.
- Built during the hackathon: tasks, reference solutions, independent checks, grader and its tests, harness, results, transcripts, this README and the video.
- No external benchmark or dataset is used. Physical constant: hbar^2/(2 m0) = 0.0380998 eV nm^2 (given in every prompt). The effective masses are the usual GaAs/AlGaAs textbook values; the Si/SiO2-like oxide numbers are typical values, not taken from a specific paper.

## AI use
Claude (Anthropic) drafted the tasks, the references, the independent checks, the grader, its tests, the harness, the video script and this README, and ran the experiments, on my instruction, overnight. **I have not yet reviewed every task, reference answer and grading rule myself**; what stands in for that review is: two independent solvers for every reference, 66 grader tests including deliberately wrong answers, the model-consensus check that exposed the t5 reference bug, and raw outputs of every trial. If the judges find an error in a reference, please check `reference/independent_check.py` first. Hidden reasoning of the models is not stored (the CLI returns only the visible answer and token counts).

## Main failure mode and hot take
When pushed, the models do not fail by lack of knowledge, they fail by **commitment to exactness**: in 3 of the 4 low-effort failures they replaced the exact calculation the prompt asked for with a named approximation, said so in a caveat, and still put a single number on the answer line. A parser, a downstream script or a tired engineer reads only the number, and a grader that reads only the final number cannot see the caveat either. Eval authors should score "declared approximation" as its own outcome, and users should not treat a bare number from a model as exact.

Hot take 1: closed-book, textbook-level quantum mechanics is no longer where frontier models fail; they solved Airy-function and five-layer transfer-matrix problems to under 1% with no tools (one Haiku trial used 37,000 hidden reasoning tokens to sum Airy power series by hand). The limitation is cost, latency and the exactness commitment above, not physics knowledge. Hot take 2: in this domain a bug in the *reference* is now more likely than a mistake by the model. My own reference for t5 was wrong and 11 of 12 trials disagreed with it, correctly. Eval authors need an independent second solver before they believe a 0% pass rate.

## Files
`tasks/` prompts, `reference/` reference solutions and independent checks, `graders/` grader and tests, `run_eval.py` harness, `regrade.py`, `qsolver.py`, `results/` raw outputs and summary for the default-effort runs (and the open model), `results_effort_low/` the low-effort runs, `transcripts/` selected transcripts (every failure, plus trial 1 of t4 and t10 for every model), `video/slides.md` the video script. The video itself is hosted at the link above, not in the ZIP.
