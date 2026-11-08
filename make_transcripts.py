#!/usr/bin/env python3
"""Select representative transcripts into transcripts/: every failed trial, plus trial 1 of tasks t4 and t10 for every model
(successful examples of the two hardest-to-fake tasks). Raw outputs of ALL trials are in results*/raw/."""
import glob, json, os, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "transcripts")
shutil.rmtree(OUT, ignore_errors=True); os.makedirs(OUT)
n = 0
for d, tag in (("results", "default-effort"), ("results_effort_low", "low-effort")):
    for f in sorted(glob.glob(os.path.join(HERE, d, "raw", "*", "*.json"))):
        r = json.load(open(f))
        keep = (not r["grade"]["ok"]) or (r["task"] in ("t4_effective_mass_interface", "t10_sloped_barrier") and r["trial"] == 1)
        if not keep:
            continue
        name = f'{tag}__{r["model"]}__{r["task"]}__trial{r["trial"]}__{"PASS" if r["grade"]["ok"] else "FAIL"}.md'
        with open(os.path.join(OUT, name), "w") as fh:
            fh.write(f'# {r["model"]} | {r["task"]} | trial {r["trial"]} | {tag}\n\n'
                     f'- grade: **{"pass" if r["grade"]["ok"] else "fail"}** ({r["grade"]["label"]}), parsed value: {r["grade"]["value"]}\n'
                     f'- run date: {r["date"]}, seconds: {r["seconds"]}, usage: output_tokens={r["usage"].get("output_tokens")}\n\n'
                     f'## Prompt sent\n\n```\n{r["prompt"]}\n```\n\n## Model output (visible text; hidden reasoning is not stored)\n\n{r["output"]}\n')
        n += 1
print(n, "transcripts written to", OUT)
