# Auto Mode Acceptance Chain Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Provide one CLI-first acceptance chain that tells whether Auto Mode has produced a reviewable paper package or must run repair tasks first.

**Architecture:** Add a small aggregator that reads Dataset Motherlode Index, Literature Discovery Seed, and Level 3 Manuscript Quality Gate JSON outputs, normalizes their statuses, produces a package readiness status, and writes a repair queue plus human-review checklist.

**Tech Stack:** Python standard library, `unittest`, JSON and Markdown outputs.

---

## BDD Behaviors

1. Given data, literature, and Level 3 gate outputs, When the acceptance chain runs, Then it reports each component status and source path.
2. Given the Level 3 gate is red or not ready, When the chain runs, Then package readiness is `needs_auto_mode_repair` and the repair queue contains gate follow-up tasks.
3. Given the Level 3 gate is yellow and ready for review, When the chain runs, Then package readiness is `needs_human_final_review`.
4. Given artifacts include draft and review layers, When the report is inspected, Then it distinguishes draft-layer output, real-run evidence, and human-review-required items.
5. Given the CLI runs, When outputs are written, Then it creates `Results/json/auto_mode_acceptance_chain.json` and `Reviews/auto_mode_acceptance_chain.md`.
6. Given Auto Mode is active, When boundary flags are inspected, Then no formal manuscript, bibliography, or product state is written.

## Files

- Create: `Program/workbench/auto_mode_acceptance_chain.py`
- Create: `Program/auto_mode_acceptance_chain.py`
- Create: `tests/test_auto_mode_acceptance_chain.py`
- Create: `docs/superpowers/plans/2026-05-28-auto-mode-acceptance-chain.md`

## Tasks

- [x] Write failing tests for readiness aggregation, repair queue, human final review state, output writing, and formal-state boundary.
- [x] Confirm RED caused by missing `Program.workbench.auto_mode_acceptance_chain`.
- [x] Implement aggregator and CLI.
- [x] Run target tests and py_compile.
- [x] Run the real CLI against P7-A/B/C local outputs.
- [x] Record outputs and verification in `Tasks/todo.md`.
- [x] Commit scoped P7-D files only.

## Execution Record

- Planned output JSON: `Results/json/auto_mode_acceptance_chain.json`.
- Planned output review: `Reviews/auto_mode_acceptance_chain.md`.
- Formal writeback: disabled for manuscript, bibliography, project bibliography, and product state.
- Real CLI run: `python3 Program/auto_mode_acceptance_chain.py --project-root . --dataset-index Results/json/dataset_motherlode_index.json --literature-seed Results/json/literature_discovery_seed.json --level3-gate Results/json/level3_manuscript_quality_gate.json`.
- Real status: `needs_auto_mode_repair`.
- Real repair queue: `mark_candidate_references_for_human_review`, `human_review_level3_package_artifacts`.
