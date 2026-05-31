# P7-BD Auto Mode Formal Package Next Gate Manifested Routed Next Gate Command Execute Gate Entry Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a P7-BD gate that consumes P7-BC run preflight and only delegates to the existing manifested routed next-gate command execute component after explicit confirmation.

**Architecture:** P7-BD is a narrow wrapper. It validates the P7-BC schema/status/input record, checks command execution metadata, converts the P7-BC command plan to the older manifested command preflight shape, then delegates to the existing P7-AI execute component only when confirmed.

**Tech Stack:** Python CLI/workbench modules, unittest, JSON reports, Markdown reviews.

---

## BDD Behaviors

1. Given P7-BC is ready and command execution is explicitly confirmed, When P7-BD runs, Then it delegates to the existing manifested command execute component and records the delegated result.
   - Business rule: P7-BD is the execution gate for the run plan produced by P7-BC.
2. Given the current P7-BC report is blocked or missing, When P7-BD runs, Then it blocks without a delegated command.
   - Business rule: the main chain cannot skip P7-BC.
3. Given P7-BC has the wrong schema, is not ready, or cannot request command execution, When P7-BD runs, Then it blocks on the P7-BC run preflight.
   - Business rule: only a ready P7-BC preflight can unlock command execution.
4. Given P7-BC has missing, duplicated, or mismatched run input records, When P7-BD runs, Then it blocks on the input contract.
   - Business rule: the execute gate needs exactly one clean P7-BC input record tied to the command plan.
5. Given P7-BC is ready but confirmation is missing, When P7-BD runs, Then it blocks before delegating.
   - Business rule: running the next gate command is never implicit.
6. Given P7-BC is ready and confirmed but reviewer or note is missing, When P7-BD runs, Then it blocks before delegating.
   - Business rule: command execution must have accountable metadata.
7. Given P7-BC already signals command execution, next gate entry, export/acceptance, writeback, or boundary violations, When P7-BD runs, Then it blocks.
   - Business rule: P7-BD can only consume a clean pre-execution preflight.
8. Given the CLI reads the current blocked repo state, When P7-BD runs with defaults, Then it writes blocked report/review only and does not run the next command.
   - Business rule: the current product effect is visible and non-destructive.

## Files

- Create `Program/workbench/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry.py`
- Create `Program/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry.py`
- Create `tests/test_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry.py`
- Create `Reviews/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry.md`
- Update `Tasks/todo.md`
- Create `notes/session-logs/2026-05-31-p7-bd-manifested-routed-next-gate-command-execute-gate-entry.md`

## Verification

- Target test must fail first because the P7-BD module does not exist.
- Target test must pass after implementation.
- Real CLI should write a blocked report in the current repo state.
- Auto Mode formal-package test family should pass.
- Staged diff whitespace check should pass before commit.
