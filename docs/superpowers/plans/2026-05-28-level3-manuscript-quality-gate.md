# Level 3 Manuscript Quality Gate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a Level 3 paper-package quality gate that checks whether Auto Mode has produced a complete, reviewable empirical paper package rather than disconnected drafts.

**Architecture:** Create a focused workbench module that reads paper Markdown plus optional package manifest and literature seed context, checks required structure, minimum length, candidate-reference review policy, paper-package artifacts, and formal-writeback boundaries, then writes JSON and Markdown review outputs.

**Tech Stack:** Python standard library, `unittest`, CLI wrapper, JSON and Markdown review artifacts.

---

## BDD Behaviors

1. Given a complete paper Markdown, When the Level 3 gate runs, Then it verifies title, abstract, introduction, literature review, data/variables, empirical strategy, main results, robustness/further tests, conclusion, candidate references, and human review checklist.
2. Given a paper body, When length is checked, Then it requires at least 5000 Chinese characters or equivalent reviewable content and reports target/actual length.
3. Given candidate references, When the references section is inspected, Then candidate references must be marked as candidates or pending human verification before they can support paper text.
4. Given a package manifest, When artifact checks run, Then the gate distinguishes real-run evidence, draft-layer artifacts, and human-review-required artifacts.
5. Given the CLI runs, When outputs are written, Then it creates `Results/json/level3_manuscript_quality_gate.json` and `Reviews/level3_manuscript_quality_gate.md`.
6. Given Auto Mode is active, When boundary flags are inspected, Then no formal manuscript, formal bibliography, or product state is written.

## Files

- Create: `Program/workbench/level3_manuscript_quality_gate.py`
- Create: `Program/level3_manuscript_quality_gate.py`
- Create: `tests/test_level3_manuscript_quality_gate.py`
- Create: `docs/superpowers/plans/2026-05-28-level3-manuscript-quality-gate.md`

## Tasks

- [x] Write failing tests for structure, length, citation-review policy, package artifacts, writer output, and boundary flags.
- [x] Confirm RED caused by missing `Program.workbench.level3_manuscript_quality_gate`.
- [x] Implement the smallest gate module and CLI.
- [x] Run target tests and py_compile.
- [x] Run the real CLI on `workspace/paper_packages/cgss_social_capital_happiness/paper.md`.
- [x] Record outputs and verification in `Tasks/todo.md`.
- [x] Commit scoped P7-C files only.

## Execution Record

- Planned output JSON: `Results/json/level3_manuscript_quality_gate.json`.
- Planned output review: `Reviews/level3_manuscript_quality_gate.md`.
- Formal writeback: disabled for manuscript, bibliography, and product state.
- Deliberate gap: this gate evaluates paper-package completeness and review readiness; it does not rewrite the paper or approve finalization.
- Real CLI run: `python3 Program/level3_manuscript_quality_gate.py --project-root . --paper workspace/paper_packages/cgss_social_capital_happiness/paper.md --package-manifest workspace/paper_packages/cgss_social_capital_happiness/manifest.json`.
- Real status: `needs_human_level3_quality_review`.
- Real gate status: `red`.
- Real finding: structure and length pass, but candidate reference entries need explicit human-review markers before Level 3 review readiness.
