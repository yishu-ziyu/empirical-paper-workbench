# CGSS Paper Package Reproducibility README

## Scope
- Topic: 社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析
- Package status: `needs_human_paper_package_review`
- Draft layer only: `true`
- Formal writeback allowed: `false`

## Real Run Artifacts
- `results_evidence_package.json`
- `paper.pdf`

## Draft Layer Artifacts
- `paper.md`
- `literature_review_packet.json`

## Human Review Required
- `method_gate.md`
- `reviewer_report.md`
- `revision_task_queue.md`

## Rebuild Commands
- `python3 Program/cgss_exploratory_paper_assembler.py`
- `python3 Program/cgss_pdf_preflight.py`
- `python3 Program/cgss_method_gate.py --profile aer_like`
- `python3 Program/cgss_reviewer_revision_loop.py`
- `python3 Program/cgss_paper_package_builder.py`

## Boundary
This package is for human acceptance review. It does not promote any content into the formal manuscript, formal bibliography, or product state.
