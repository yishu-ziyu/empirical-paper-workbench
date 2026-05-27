# Reference Marker Patch Proposal Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Repair the Level 3 citation-marker gap as a reviewable draft-layer proposal, without overwriting the paper package source, formal manuscript, formal bibliography, or product state.

**Architecture:** Add a small LiteratureAgent repair CLI that reads a paper Markdown file, locates `## 参考文献候选`, appends `（候选，待人工核验）` to unmarked bullet items, writes a candidate paper copy, and records machine-readable plus Markdown review outputs.

**Tech Stack:** Python standard library, `unittest`, JSON and Markdown outputs.

---

## BDD Behaviors

1. Given a paper with `## 参考文献候选` and unmarked bullet references, When the reference marker proposal runs, Then it writes a candidate paper where each reference bullet is marked `（候选，待人工核验）`.
   - 业务规则：候选引用不能以未核验形式进入 Level 3 人工审阅。
2. Given a paper whose candidate references are already marked, When the proposal runs, Then it reports `no_reference_marker_patch_needed` and does not change paper content.
   - 业务规则：修复器必须幂等，不能重复追加标记。
3. Given the proposal writes artifacts, When outputs are inspected, Then it creates JSON, Markdown review, and a draft-layer candidate paper path.
   - 业务规则：Auto Mode 只能生成可审阅候选产物，不能静默改正式包。
4. Given boundary flags are inspected, When the proposal completes, Then formal manuscript, bibliography, project bibliography, product state, and source paper overwrite are all false.
   - 业务规则：本节点是 patch proposal，不是正式写回。
5. Given the paper has no candidate reference section, When the proposal runs, Then it reports `blocked_missing_candidate_references_section`.
   - 业务规则：缺少引用候选节时不能猜测要改哪里。

## Files

- Create: `Program/workbench/reference_marker_patch_proposal.py`
- Create: `Program/reference_marker_patch_proposal.py`
- Create: `tests/test_reference_marker_patch_proposal.py`
- Create: `docs/superpowers/plans/2026-05-28-reference-marker-patch-proposal.md`

## Tasks

- [x] Write failing tests for marker insertion, idempotence, output writing, boundary flags, and missing section blocking.
- [x] Confirm RED caused by missing `Program.workbench.reference_marker_patch_proposal`.
- [x] Implement proposal builder and CLI.
- [x] Run target tests and py_compile.
- [x] Run the real CLI against `workspace/paper_packages/cgss_social_capital_happiness/paper.md`.
- [x] Re-run Level 3 gate and Auto Mode acceptance chain on the candidate paper.
- [x] Record outputs and verification in `Tasks/todo.md`.
- [x] Commit scoped P7-E files only.

## Execution Record

- Planned candidate paper: `Manuscripts/generated/cgss_social_capital_happiness_paper_reference_marked.md`.
- Planned output JSON: `Results/json/reference_marker_patch_proposal.json`.
- Planned output review: `Reviews/reference_marker_patch_proposal.md`.
- Formal writeback: disabled for manuscript, bibliography, project bibliography, product state, and source paper overwrite.
- RED test: `python3 -m unittest tests.test_reference_marker_patch_proposal -v` failed with missing `Program.workbench.reference_marker_patch_proposal`.
- Real CLI run: `python3 Program/reference_marker_patch_proposal.py --project-root . --source-paper workspace/paper_packages/cgss_social_capital_happiness/paper.md --candidate-paper Manuscripts/generated/cgss_social_capital_happiness_paper_reference_marked.md --output-report Results/json/reference_marker_patch_proposal.json --output-review Reviews/reference_marker_patch_proposal.md`.
- Real status: `needs_human_reference_marker_review`; changed references: 8.
- Candidate Level 3 gate: `gate_status=yellow`, `ready_for_level3_review=true`, citation policy passed.
- Candidate Auto Mode acceptance: `package_readiness=needs_human_final_review`, repair queue empty.
