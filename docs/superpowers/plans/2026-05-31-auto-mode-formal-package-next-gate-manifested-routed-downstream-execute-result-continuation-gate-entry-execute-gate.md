# P7-BM Manifested Routed Downstream Execute Result Continuation Gate Entry Execute Gate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build P7-BM as the explicit execute gate after P7-BL downstream execute result continuation gate entry.

**Architecture:** P7-BM consumes only the P7-BL gate-entry JSON. In dry-run it previews the next continuation. In execute mode, export branches can enter the existing route-specific artifact executor entry dry-run, while manual terminal branches only record product-review packet preparation. It must not export artifacts, accept the package, render PDF/DOCX, or write `state/product/*`.

**Tech Stack:** Python stdlib, unittest, existing CLI-first Auto Mode JSON/Markdown pattern.

---

## BDD 行为

1. Given P7-BL is export-ready with one accepted continuation input record, When P7-BM runs in dry-run mode, Then it previews the route-specific artifact executor entry command without running it.
   - 业务规则：export 分支必须先把“将进入哪个执行入口”展示出来，不能默认执行。

2. Given P7-BL is manual-terminal-ready with one accepted product-review packet continuation record, When P7-BM runs in dry-run mode, Then it previews product-review packet preparation without any external command.
   - 业务规则：manual terminal 分支不是导出命令，只能准备产品审阅包记录。

3. Given the current real P7-BL is blocked, When P7-BM runs with default inputs, Then it remains blocked and writes no continuation execution.
   - 业务规则：上游未放行时，P7-BM 不能猜测下一步。

4. Given P7-BL is missing, has the wrong schema, is not ready, cannot continue, or has blockers, When P7-BM reviews it, Then it blocks on the source gate entry.
   - 业务规则：P7-BM 只接受完整、明确放行的 P7-BL。

5. Given a ready P7-BL has missing, duplicated, mismatched, unaccepted, or non-continuable continuation input records, When P7-BM reviews it, Then it blocks on the continuation execute contract.
   - 业务规则：执行闸门只能消费一个干净、已接受、可继续的 continuation input record。

6. Given P7-BM runs in execute mode without confirmation, reviewer, or note, When it validates the request, Then it blocks before any continuation action.
   - 业务规则：真正进入下一段必须有明确人工确认和审阅元数据。

7. Given a manual terminal P7-BL is ready and execute mode is confirmed, When P7-BM runs, Then it records product-review packet preparation only and runs no external command.
   - 业务规则：manual terminal 的完成态只进入产品审阅准备记录，不触发导出或正式写回。

8. Given an export P7-BL is ready and execute mode is confirmed, When P7-BM runs with matching selected-route execution inputs, Then it enters the route-specific artifact executor entry dry-run and still produces no formal package artifact.
   - 业务规则：export 分支的显式执行只进入下一层 dry-run 入口，不直接生成 PDF/DOCX/manifest 或验收结果。

## 边界条件

- 当前真实仓库默认应因 P7-BL blocked 而 blocked。
- P7-BM 不直接导出 PDF/DOCX，不生成 formal package manifest，不执行人工验收，不写 `state/product/*`。
- Export 分支 execute 只允许进入已有 route-specific artifact executor entry 的 dry-run。
- Manual terminal 分支 execute 不调用外部命令，只记录 product-review packet preparation。
- 下一节点 P7-BN 应只消费 P7-BM 输出。

## 验证步骤

1. 写 `tests/test_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_gate_entry_execute_gate.py` 并先运行 RED。
2. 新增 workbench 与 CLI。
3. 运行目标测试、真实 CLI、`py_compile`、Auto Mode 回归和 diff 检查。
4. 把阶段效果写入 `Tasks/todo.md` 和 session log。
