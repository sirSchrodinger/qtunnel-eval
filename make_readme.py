#!/usr/bin/env python3
"""Fill README.template.md from the result files (tables, counts, cost). Usage: python make_readme.py <video_url>"""
import collections, glob, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "graders"))
import grade
video = sys.argv[1] if len(sys.argv) > 1 else "(link added at submission)"

def load(d):
    return [json.load(open(f)) for f in sorted(glob.glob(os.path.join(HERE, d, "raw", "*", "*.json")))]
main_r, low_r = load("results"), load("results_effort_low")
claude_main = [r for r in main_r if r["model"].startswith("claude")]
qwen = [r for r in main_r if r["model"].startswith("qwen")]
def summ(d):
    t = open(os.path.join(HERE, d, "summary.md")).read()
    t = t.split("\nFailure labels")[0].strip()
    return t.replace("qwen2-5-3b-instruct-q4_K_M-cpu", "qwen2.5:3b-instruct-q4_K_M (Ollama, CPU only)")

tables = ("**Main run, default reasoning effort (Claude Code CLI default) plus the open model.** 13 tasks, 3 trials per task, every trial graded by code. "
          "pass^k here means all 3 trials of a task are correct. With scores this close to the ceiling I do not claim a ranking between the Claude models.\n\n"
          + summ("results") + "\n\n**Low reasoning effort (`--effort low`), same tasks, same grader.**\n\n" + summ("results_effort_low"))

def fails(rs): return [r for r in rs if not r["grade"]["ok"]]
fc, fl, fq = fails(claude_main), fails(low_r), fails(qwen)
ref = lambda t: grade.EXPECTED[t]["ref"]
def line(r):
    th = (r["usage"].get("output_tokens_details") or {}).get("thinking_tokens")
    return f'`{r["model"]}`, {r["task"].split("_")[0]}, trial {r["trial"]}: answered {r["grade"]["value"]} (reference {ref(r["task"]):.5g}), label: {r["grade"]["label"]}'
n_claude = len(claude_main) + len(low_r)
lab = collections.Counter("format" if r["grade"]["label"].startswith("format") else ("wrong method" if r["grade"]["label"].startswith("wrong method") else "other wrong") for r in fq)
failures = f"""**Frontier Claude models: {len(fc) + len(fl)} failed trials out of {n_claude}** ({len(claude_main)} at default effort, {len(low_r)} at low effort). Every failed trial, with its visible explanation, is in `transcripts/`.

Default effort ({len(fc)} failure):
""" + "\n".join("- " + line(r) for r in fc) + f"""
  - Why: the model put the effective mass in the *denominator* of kappa (kappa^2 = (V0-E)/[(hbar^2/2m0)(0.42)] instead of multiplying), so kappa came out 13.9 per nm instead of 5.85. A heavier electron must tunnel *less*; a dimension-and-limit check would have caught it.

Low effort ({len(fl)} failures):
""" + "\n".join("- " + line(r) for r in fl) + """
  - Opus, t11: replaced the exact condition T(E)=0.5 by a Lorentzian escape-rate estimate, and wrote "this is a Lorentzian approximation, not an exact evaluation" in the answer.
  - Haiku, t13: replaced the exact transfer matrix by the Herring double-well formula, and wrote "this is an estimate rather than an exact transfer-matrix result".
  - Fable, t13: quantised the double well while "treating the outer barriers as thick" (8% off), and did not say how large the neglected shift was.
  - Haiku, t5: derived a resonance condition by hand and slipped in the algebra; it picked a wrong root (0.169 eV; the infinite-well estimate of 0.224 eV was used as a sanity check, and 0.169 passed it).

Where models came close: t13 (Fable, 59 vs 54.5 meV, 8% off) and t11 (Opus, 13% off) are within the range an engineer might accept in a first pass, which is exactly the problem: the prompt asked for the exact value and the answer line contains no hint of the approximation.

**Open 3B model (qwen2.5:3b):** {len(fq)} of {len(qwen)} trials failed. {lab['format']} of those are format failures (no ANSWER line or the wrong key), {lab['wrong method']} match a known wrong method (T=1 for an asymmetric double barrier; exp(-2 kappa a) without the prefactor), the other {lab['other wrong']} are wrong numbers with no recognisable method (for example T of about 0.9 for the GaAs barrier). The two passes are t2 and t3, the simplest closed forms. So the eval does separate a small model from the frontier models, and the frontier models fail only where the arithmetic or the exactness is heaviest.

**Validity checks from the guide.** (a) Not 0% everywhere: yes, the frontier models are near 100%, so the tasks are solvable and the grader accepts correct answers. (b) More capability or effort should do better: the low-effort run has 4 failures against 1 at default effort, all in the numerically heaviest tasks (t5, t11, t13) plus the slip at default effort; with 4 and 1 events this is directional only. (c) Headroom: there is almost none for the frontier models, so this eval no longer shows a limitation for them."""

def stats(rs):
    a = collections.defaultdict(lambda: [0, 0.0, 0.0, 0.0])
    for r in rs:
        x = a[r["model"]]; x[0] += 1; x[1] += r["usage"].get("output_tokens", 0) or 0; x[2] += r["usage"].get("cost_usd") or 0; x[3] += r["seconds"]
    return a
rows = ["| run | model | trials | mean output tokens / trial | mean seconds / trial | cost at list price (39 trials) |", "|---|---|---|---|---|---|"]
for tag, rs in (("default effort", claude_main), ("low effort", low_r)):
    for m, x in sorted(stats(rs).items(), key=lambda kv: kv[1][2]):
        rows.append(f"| {tag} | {m} | {x[0]} | {x[1]/x[0]:.0f} | {x[3]/x[0]:.0f} | ${x[2]:.2f} |")
cost = "\n".join(rows) + """

The Claude costs are the list-price figures reported by Claude Code (`total_cost_usd`); the runs were paid by a subscription, not per token. The whole Claude part (4 models, 2 effort levels, 312 trials) took about 40 minutes of wall-clock time with 4 parallel calls. The open model ran on a CPU-only, heavily loaded 24-thread machine at about 13 tokens per second, about 50 minutes for 39 trials. A rerun of one Claude model with the API backend should cost a few dollars and take 10 to 20 minutes (Haiku writes about 5 times more output tokens per task than Sonnet at default effort)."""

hot = """When pushed, the models do not fail by lack of knowledge, they fail by **commitment to exactness**: in 3 of the 4 low-effort failures they replaced the exact calculation the prompt asked for with a named approximation, said so in a caveat, and still put a single number on the answer line. A parser, a downstream script or a tired engineer reads only the number, and a grader that reads only the final number cannot see the caveat either. Eval authors should score "declared approximation" as its own outcome, and users should not treat a bare number from a model as exact.

Hot take 1: closed-book, textbook-level quantum mechanics is no longer where frontier models fail; they solved Airy-function and five-layer transfer-matrix problems to under 1% with no tools (one Haiku trial used 37,000 hidden reasoning tokens to sum Airy power series by hand). The limitation is cost, latency and the exactness commitment above, not physics knowledge. Hot take 2: in this domain a bug in the *reference* is now more likely than a mistake by the model. My own reference for t5 was wrong and 11 of 12 trials disagreed with it, correctly. Eval authors need an independent second solver before they believe a 0% pass rate."""

t = open(os.path.join(HERE, "README.template.md")).read()
for k, v in {"@VIDEO_URL@": video, "@TABLES@": tables, "@FAILURES@": failures, "@COST@": cost, "@HOTTAKE@": hot}.items():
    t = t.replace(k, v)
open(os.path.join(HERE, "README.md"), "w").write(t)
print("README.md written,", len(t), "chars")
