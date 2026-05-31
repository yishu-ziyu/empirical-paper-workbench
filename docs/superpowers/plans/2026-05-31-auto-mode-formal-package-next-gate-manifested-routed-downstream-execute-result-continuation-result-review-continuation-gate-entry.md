# Auto Mode Formal Package Manifested Routed Downstream Execute Result Continuation Result Review Continuation Gate Entry Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:test-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add P7-BO as the continuation gate entry after P7-BN result review.

**Architecture:** P7-BO consumes only P7-BN result review JSON. It records a continuation entry for either route-specific artifact execution or product-review packet preparation, while preserving the no-execution/no-product-state boundary.

**Tech Stack:** Python stdlib CLI/workbench, unittest, JSON/Markdown reports.

---

## BDD 行为

1. Given P7-BN export result review is ready with one clean route-specific artifact execution record, When P7-BO builds the gate entry, Then it records one route-specific artifact execution continuation input and requires an explicit continuation command.
   - 业务规则：export 分支只能从已审阅通过的 artifact execution record 进入下一步。

2. Given P7-BN manual result review is ready with one clean product-review packet input record, When P7-BO builds the gate entry, Then it records one product-review packet continuation input without running a command.
   - 业务规则：manual terminal 分支进入产品审阅包，不再回到导出执行链。

3. Given the current repository P7-BN output is blocked, When P7-BO runs, Then it remains blocked and emits no continuation input.
   - 业务规则：blocked 上游不能被当作可继续状态。

4. Given P7-BN is missing, has a wrong schema, is not ready, cannot continue, or has blockers, When P7-BO validates the source, Then it blocks at the source contract.
   - 业务规则：P7-BO 只信任 P7-BN 的 ready result review。

5. Given export-ready P7-BN has missing, duplicated, mismatched, or unaccepted artifact execution records, When P7-BO validates records, Then it blocks at the continuation contract.
   - 业务规则：export continuation 必须只有一条干净的 artifact execution record。

6. Given manual-ready P7-BN has missing, duplicated, mismatched, or unaccepted product-review packet input records, When P7-BO validates records, Then it blocks at the continuation contract.
   - 业务规则：manual continuation 必须只有一条干净的 product-review packet input record。

7. Given P7-BN carries execution, export, formal writeback, product-state, or boundary violation signals, When P7-BO validates boundaries, Then it blocks and does not generate continuation input.
   - 业务规则：result-review continuation entry 仍是入口记录节点，不允许夹带正式层副作用。

8. Given P7-BO writes outputs, When the CLI runs with the current default blocked input, Then it writes only P7-BO JSON/Markdown and does not write `state/product/*`.
   - 业务规则：本节点只产出审阅入口，不执行下游。

## 边界条件

- 本阶段不执行 route-specific artifact execution。
- 本阶段不生成 product-review packet 正式产物。
- 本阶段不导出 PDF/DOCX、不生成 package manifest、不执行人工验收。
- 本阶段不写 `state/product/*`。

## TDD 步骤

- [x] 写 P7-BO 失败测试。
- [x] 运行目标测试确认 RED。
- [x] 实现 P7-BO workbench。
- [x] 实现 P7-BO CLI。
- [x] 运行目标测试、真实 CLI、Auto Mode 回归、编译和 diff 检查。
- [x] 更新 `Tasks/todo.md` 和 session log。
