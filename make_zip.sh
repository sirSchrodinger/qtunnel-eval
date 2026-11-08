#!/bin/bash
# Build the submission ZIP (code, tasks, reference, graders, raw results, transcripts; no venv, no videos, no keys).
set -e
cd "$(dirname "$0")"
OUT=${1:-../tunnel-eval-submission.zip}
rm -f "$OUT"
zip -qr "$OUT" README.md requirements.txt .env.example run_eval.py regrade.py make_transcripts.py qsolver.py tasks reference graders results results_effort_low transcripts video/slides.md \
  -x "*/__pycache__/*" "*.pyc" "*/.pytest_cache/*"
unzip -l "$OUT" | tail -1
