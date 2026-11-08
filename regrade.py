#!/usr/bin/env python3
"""Re-grade the stored raw outputs with the current reference answers (no model calls) and rebuild the summary.
The grade stored at run time is kept under `grade_firstpass` the first time a record is re-graded."""
import argparse, glob, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "graders"))
import grade, run_eval  # noqa: E402

ap = argparse.ArgumentParser(); ap.add_argument("--out", default=os.path.join(HERE, "results")); a = ap.parse_args()
recs, changed = [], 0
for f in sorted(glob.glob(os.path.join(a.out, "raw", "*", "*.json"))):
    r = json.load(open(f))
    new = grade.grade(r["task"], r["output"])
    if new != r["grade"]:
        r.setdefault("grade_firstpass", r["grade"]); r["grade"] = new; changed += 1
        json.dump(r, open(f, "w"), ensure_ascii=False, indent=1)
    recs.append(r)
models = sorted({r["model"] for r in recs}, key=lambda m: ["claude-haiku-5-5", "claude-sonnet-5-5", "claude-opus-5-5", "claude-fable-5-1"].index(m) if m in ["claude-haiku-5-5", "claude-sonnet-5-5", "claude-opus-5-5", "claude-fable-5-1"] else 9)
trials = max(r["trial"] for r in recs)
ns = argparse.Namespace(models=models, trials=trials, out=a.out)
print(f"re-graded {len(recs)} records, {changed} grades changed\n")
run_eval.summarize(ns, recs)
