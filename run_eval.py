#!/usr/bin/env python3
"""Run the tunnelling eval against one or more models and write raw transcripts + a summary.

  python run_eval.py --backend anthropic --models claude-sonnet-5-5 --trials 3            # needs ANTHROPIC_API_KEY
  python run_eval.py --backend openai --base-url https://openrouter.ai/api/v1 --models <id>  # needs OPENAI_API_KEY
  python run_eval.py --backend claude-cli --models claude-haiku-5-5                         # Claude Code CLI (what the
                                                                                              submitted run used)
Every trial is an independent single-turn call with no shared history. No tools are offered to the model.
Reference answers are never sent. Raw outputs go to results/raw/<model>/<task>__<trial>.json.
"""
import argparse, concurrent.futures as cf, json, os, shutil, subprocess, sys, tempfile, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "graders"))
import grade  # noqa: E402

PREAMBLE = ("This is a closed-book numerical physics problem. No code execution or other tools are available: use your own "
            "reasoning and arithmetic. Use hbar^2/(2 m0) = 0.0380998 eV nm^2, where m0 is the free-electron mass. Electron "
            "energies are measured from the band edge of the contacts, where the potential is 0 unless stated otherwise.\n\n")
POSTAMBLE = ('\n\nReply with brief reasoning, then finish with one final line of exactly this form (JSON, a plain number, '
             'no units inside the braces): ANSWER: {"<key>": <number>}')
SYSTEM = "You are an expert physicist. Answer the problem you are given."


def build_prompt(task):
    return PREAMBLE + task["prompt"] + POSTAMBLE


def call_anthropic(model, prompt, temperature):
    body = {"model": model, "max_tokens": 8000, "system": SYSTEM, "messages": [{"role": "user", "content": prompt}]}
    if temperature is not None:
        body["temperature"] = temperature
    req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=json.dumps(body).encode(), headers={
        "x-api-key": os.environ["ANTHROPIC_API_KEY"], "anthropic-version": "2023-06-01", "content-type": "application/json"})
    r = json.load(urllib.request.urlopen(req, timeout=600))
    return "".join(b.get("text", "") for b in r["content"] if b["type"] == "text"), r.get("usage", {})


def call_openai(model, prompt, temperature, base_url):
    body = {"model": model, "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt}],
            "max_tokens": 8000}
    if temperature is not None:
        body["temperature"] = temperature
    req = urllib.request.Request(base_url.rstrip("/") + "/chat/completions", data=json.dumps(body).encode(), headers={
        "Authorization": "Bearer " + os.environ["OPENAI_API_KEY"], "content-type": "application/json"})
    r = json.load(urllib.request.urlopen(req, timeout=600))
    return r["choices"][0]["message"]["content"], r.get("usage", {})


def call_claude_cli(model, prompt, _temperature, effort=None):
    """Clean HOME + empty cwd so no user memory/CLAUDE.md/settings reach the model; tools disabled."""
    home = tempfile.mkdtemp(prefix="evalhome.")
    try:
        os.makedirs(home + "/.claude"); os.makedirs(home + "/work")
        src = os.path.expanduser("~/.claude/.credentials.json")
        if os.path.exists(src):
            shutil.copy(src, home + "/.claude/.credentials.json")
        env = dict(os.environ, HOME=home)
        cmd = ["claude", "-p", "--model", model, "--tools", "", "--no-session-persistence", "--output-format", "json",
               "--system-prompt", SYSTEM] + (["--effort", effort] if effort else []) + [prompt]
        p = subprocess.run(cmd,
                           capture_output=True, text=True, cwd=home + "/work", env=env, timeout=900)
        j = json.loads(p.stdout)
        return j.get("result", ""), {**j.get("usage", {}), "cost_usd": j.get("total_cost_usd")}
    finally:
        shutil.rmtree(home, ignore_errors=True)


def one(args, model, task, trial):
    out = os.path.join(args.out, "raw", model, f"{task['id']}__{trial}.json")
    if os.path.exists(out) and not args.force:
        return json.load(open(out))
    prompt = build_prompt(task)
    t0 = time.time()
    for attempt in range(3):
        try:
            if args.backend == "anthropic":
                text, usage = call_anthropic(model, prompt, args.temperature)
            elif args.backend == "openai":
                text, usage = call_openai(model, prompt, args.temperature, args.base_url)
            else:
                text, usage = call_claude_cli(model, prompt, args.temperature, args.effort)
            break
        except Exception as e:  # network / rate limit: retry, then record the error as a failed trial
            text, usage = "", {"error": str(e)[:300]}
            time.sleep(5 * (attempt + 1))
    rec = {"model": model, "task": task["id"], "trial": trial, "backend": args.backend, "effort": args.effort,
           "date": time.strftime("%Y-%m-%d %H:%M:%S"), "seconds": round(time.time() - t0, 1),
           "prompt": prompt, "output": text, "usage": usage, "grade": grade.grade(task["id"], text)}
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump(rec, open(out, "w"), ensure_ascii=False, indent=1)
    return rec


def summarize(args, recs):
    lines = ["| model | trials/task | pass rate | pass^k (all k trials correct) | tasks always passed | tasks never passed |",
             "|---|---|---|---|---|---|"]
    per_task = {}
    for m in args.models:
        rs = [r for r in recs if r["model"] == m]
        by = {}
        for r in rs:
            by.setdefault(r["task"], []).append(r["grade"]["ok"])
        n_ok = sum(sum(v) for v in by.values()); n = sum(len(v) for v in by.values())
        allk = sum(all(v) for v in by.values()); never = sum(not any(v) for v in by.values())
        lines.append(f"| {m} | {args.trials} | {100*n_ok/max(n,1):.0f}% ({n_ok}/{n}) | {allk}/{len(by)} tasks | {allk} | {never} |")
        for t, v in by.items():
            per_task.setdefault(t, {})[m] = f"{sum(v)}/{len(v)}"
    lines += ["", "Per task (correct trials / trials):", "", "| task | " + " | ".join(args.models) + " |",
              "|---|" + "---|" * len(args.models)]
    for t in grade.TASKS:
        lines.append(f"| {t} | " + " | ".join(per_task.get(t, {}).get(m, "-") for m in args.models) + " |")
    labels = {}
    for r in recs:
        if not r["grade"]["ok"]:
            labels.setdefault((r["task"], r["grade"]["label"]), []).append(r["model"])
    lines += ["", "Failure labels (task, label: models that produced it):", ""]
    for (t, l), ms in sorted(labels.items()):
        lines.append(f"- {t}: {l}: " + ", ".join(sorted(ms)))
    open(os.path.join(args.out, "summary.md"), "w").write("\n".join(lines) + "\n")
    with open(os.path.join(args.out, "all_trials.csv"), "w") as f:
        f.write("model,task,trial,ok,value,label,seconds\n")
        for r in recs:
            g = r["grade"]
            f.write(f'{r["model"]},{r["task"]},{r["trial"]},{int(g["ok"])},{g["value"]},"{g["label"]}",{r["seconds"]}\n')
    print("\n".join(lines))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", choices=["anthropic", "openai", "claude-cli"], default="anthropic")
    ap.add_argument("--models", nargs="+", required=True)
    ap.add_argument("--trials", type=int, default=3)
    ap.add_argument("--tasks", nargs="*", default=None)
    ap.add_argument("--temperature", type=float, default=None, help="omit to use the provider default")
    ap.add_argument("--base-url", default="https://openrouter.ai/api/v1")
    ap.add_argument("--effort", default=None, help="claude-cli backend only: reasoning effort level (e.g. low)")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--out", default=os.path.join(HERE, "results"))
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    tasks = [t for t in grade.TASKS.values() if not args.tasks or t["id"] in args.tasks]
    jobs = [(m, t, k) for m in args.models for t in tasks for k in range(1, args.trials + 1)]
    with cf.ThreadPoolExecutor(args.jobs) as ex:
        recs = list(ex.map(lambda j: one(args, *j), jobs))
    summarize(args, recs)


if __name__ == "__main__":
    main()
