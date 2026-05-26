#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../../.."

python3 Program/formal_pdf_candidate.py \
  --project-root . \
  --preflight-report Results/json/formal_pdf_export_preflight.json \
  --source-map Results/json/formal_manuscript_source_map.json \
  --output-report Results/json/formal_pdf_candidate_report.json \
  --output-review Reviews/formal_pdf_candidate.md \
  --output-qmd Submissions/formal_package/manuscript/paper_candidate.qmd \
  --output-pdf Submissions/formal_package/paper_candidate.pdf \
  --reproduce-script Submissions/formal_package/reproducibility/render_pdf_candidate.sh \
  --render-mode auto
