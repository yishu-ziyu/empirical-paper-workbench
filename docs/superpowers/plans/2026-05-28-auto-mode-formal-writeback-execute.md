# Auto Mode Formal Writeback Execute Plan

Date: 2026-05-28

## Node Goal

P7-M creates the explicit execute gate after P7-L. It consumes the formal writeback execution preflight and separates `dry-run` from `apply`.

This node still does not mutate formal manuscript sources, bibliography, project bibliography, DesignSpec, RunPlan, product state, PDFs, DOCX, model outputs, or statistical execution artifacts. A confirmed `apply` records an apply manifest for later target adapters; it does not write target adapters itself.

## BDD Behaviors

### Behavior 1: Ready preflight supports dry-run planning

Given the P7-L execution preflight is ready
When Auto Mode runs formal writeback execute in `dry-run` mode
Then the status is `formal_writeback_dry_run_ready`
And it lists planned operations
And no formal writeback is executed.

Business rule: dry-run 必须让人看到将要执行什么，但不能改正式层。

### Behavior 2: Block when execution preflight is not ready

Given the current P7-L execution preflight is blocked
When Auto Mode runs formal writeback execute
Then the status is `blocked_by_execution_preflight`
And apply cannot proceed.

Business rule: 未通过执行预检时，不允许靠 execute 命令绕过审批链。

### Behavior 3: Apply requires explicit confirmation

Given the P7-L execution preflight is ready
When Auto Mode runs in `apply` mode without `--confirm-apply`
Then it blocks with a missing confirmation reason.

Business rule: apply 必须有显式确认，不能靠默认参数误触发。

### Behavior 4: Apply requires reviewer and note

Given the P7-L execution preflight is ready
And `--confirm-apply` is present
But reviewer or note is missing
When Auto Mode runs in `apply` mode
Then it blocks with apply metadata reasons.

Business rule: 执行层申请也必须可追溯到具体人和说明。

### Behavior 5: Confirmed apply records manifest only

Given the P7-L execution preflight is ready
And `--confirm-apply`, reviewer, and note are present
When outputs are written
Then the execution JSON, review Markdown, and apply manifest are written
And no formal manuscript, bibliography, project bibliography, DesignSpec, RunPlan, product state, PDF, DOCX, model output, or statistical artifact is written.

Business rule: P7-M 只记录 apply manifest，正式 target adapter 写入必须留给后续节点。

### Behavior 6: CLI default reflects current blocked preflight

Given the current P7-L execution preflight is blocked
When the CLI runs with default paths
Then it writes a blocked dry-run report
And reports `formal_writeback_executed=false`.

Business rule: 当前真实状态应该继续停在阻断处，而不是伪造 dry-run ready 或 apply。

## Boundary Conditions

- Requires `p7.auto_mode_formal_writeback_execution_preflight.v1`.
- Requires `status=ready_for_formal_writeback_execution_review` before dry-run ready or apply manifest.
- Requires `mode=apply`, `--confirm-apply`, reviewer, and note before apply manifest can be recorded.
- No formal writeback target adapter runs in this node.
- No `state/product/*` writeback.
- No PDF/DOCX render or copy.
- No model execution or statistical artifact overwrite.

## Verification

- RED: `python3 -m unittest tests.test_auto_mode_formal_writeback_execute -v` fails before implementation because `Program.workbench.auto_mode_formal_writeback_execute` does not exist.
- GREEN: target tests pass after minimal execute dry-run/apply-manifest implementation.
- Real run writes `Results/json/auto_mode_formal_writeback_execute.json` and `Reviews/auto_mode_formal_writeback_execute.md` with current status blocked by the P7-L execution preflight.
