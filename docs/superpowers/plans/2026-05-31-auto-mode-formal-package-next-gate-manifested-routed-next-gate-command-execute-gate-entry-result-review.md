# P7-BE Auto Mode Formal Package Next Gate Manifested Routed Next Gate Command Execute Gate Entry Result Review Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a P7-BE result review node that consumes the P7-BD gate entry result and decides whether the delegated next-gate execution can continue.

**Architecture:** P7-BE is a one-input review wrapper. It validates the P7-BD result schema/status, delegated execution outcome, delegated result contract, and side-effect boundaries, then emits a continuation record without running commands or writing product state.

**Tech Stack:** Python CLI/workbench modules, unittest, JSON reports, Markdown reviews.

---

## BDD Behaviors

1. Given P7-BD executed successfully and recorded a delegated success, When P7-BE runs, Then it returns `manifested_routed_next_gate_command_execute_gate_entry_result_review_ready` with one delegated result record.
   - Business rule: P7-BE turns a completed command execution into an auditable continuation record.
2. Given the current P7-BD result is blocked or missing, When P7-BE runs, Then it blocks without continuation records.
   - Business rule: the main chain cannot skip the execute gate entry.
3. Given P7-BD has wrong schema, is not executed, or has blockers, When P7-BE runs, Then it blocks on the P7-BD gate entry.
   - Business rule: only a completed P7-BD result can be reviewed.
4. Given delegated return code, status, report path, or review path is missing or mismatched, When P7-BE runs, Then it blocks on delegated result contract.
   - Business rule: continuation must be tied to the exact delegated result reported by P7-BD.
5. Given delegated result summary is missing, invalid, blocked, or non-success, When P7-BE runs, Then it blocks on delegated next-gate result.
   - Business rule: a command run is not enough; its delegated result must be acceptable.
6. Given P7-BD signals product-state writes, formal writeback, export/acceptance execution by this review node, or boundary violations, When P7-BE runs, Then it blocks.
   - Business rule: result review is read-only and cannot continue from unsafe boundary signals.
7. Given P7-BE writes outputs, When it runs, Then it writes only its result review report/review.
   - Business rule: P7-BE does not run commands or write `state/product/*`.
8. Given the CLI reads the current blocked repo state, When P7-BE runs with defaults, Then it writes blocked report/review only.
   - Business rule: the current product effect remains visible and non-destructive.

## Files

- Create `Program/workbench/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry_result_review.py`
- Create `Program/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry_result_review.py`
- Create `tests/test_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry_result_review.py`
- Create `Reviews/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry_result_review.md`
- Update `Tasks/todo.md`
- Create `notes/session-logs/2026-05-31-p7-be-manifested-routed-next-gate-command-execute-gate-entry-result-review.md`

## Verification

- Target test must fail first because the P7-BE module does not exist.
- Target test must pass after implementation.
- Real CLI should write a blocked report in the current repo state.
- Auto Mode formal-package test family should pass.
- Staged diff whitespace check should pass before commit.
