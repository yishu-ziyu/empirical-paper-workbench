# Auto Mode Formal Target Adapter Execution Gate Plan

Date: 2026-05-28

## Node Goal

P7-O consumes the P7-N target adapter readiness report and creates an explicit target-adapter execution gate.

This node separates `dry-run` from confirmed `execute`. The confirmed execution mode only records an execution manifest for a later materialization node; it does not copy package artifacts, create candidate target files, mutate formal manuscript sources, bibliography, project bibliography, DesignSpec, RunPlan, product state, PDFs, DOCX, model outputs, or statistical execution artifacts.

## BDD Behaviors

### Behavior 1: Ready readiness supports dry-run execution planning

Given P7-N target adapter readiness is ready
When Auto Mode runs target adapter execution in `dry-run` mode
Then the status is `target_adapter_execution_dry_run_ready`
And it lists each adapter execution plan item
And no target adapter is executed.

Business rule: readiness ready 后也必须先能审阅即将执行的 adapter 计划。

### Behavior 2: Block when readiness is not ready

Given the current P7-N readiness is blocked
When Auto Mode runs target adapter execution
Then the status is `blocked_by_target_adapter_readiness`
And no execution plan is produced.

Business rule: P7-O 不能绕过 P7-N 的 apply manifest / mapping 阻断。

### Behavior 3: Execute requires explicit confirmation

Given P7-N readiness is ready
When Auto Mode runs in `execute` mode without `--confirm-execution`
Then it blocks with a missing confirmation reason.

Business rule: target adapter execution 需要显式确认，不能由默认参数触发。

### Behavior 4: Execute requires reviewer and note

Given P7-N readiness is ready
And `--confirm-execution` is present
But reviewer or note is missing
When Auto Mode runs in `execute` mode
Then it blocks with execution metadata reasons.

Business rule: 执行层必须留下可追溯的人和说明。

### Behavior 5: Confirmed execute records manifest only

Given P7-N readiness is ready
And `--confirm-execution`, reviewer, and note are present
When outputs are written
Then the execution JSON, review Markdown, and execution manifest are written
And no candidate target files or formal state are written.

Business rule: P7-O 只记录 execution manifest，真实 adapter materialization 必须留给后续节点。

### Behavior 6: Bad adapter mapping blocks execution

Given P7-N readiness contains an adapter mapping that is not ready
When target adapter execution is built
Then it blocks before dry-run or execute.

Business rule: readiness 报告内部 mapping 不是 ready 时，执行门不能继续。

### Behavior 7: CLI default reflects current blocked readiness

Given the current P7-N readiness is blocked
When the CLI runs with default paths
Then it writes a blocked execution gate report
And reports `formal_target_adapters_executed=false`.

Business rule: 当前真实状态应继续停在阻断处，而不是伪造 adapter execution ready。

## Boundary Conditions

- Requires `p7.auto_mode_formal_target_adapter_readiness.v1`.
- Requires `status=ready_for_formal_target_adapter_review` before dry-run ready or execution manifest.
- Requires `mode=execute`, `--confirm-execution`, reviewer, and note before execution manifest can be recorded.
- Requires every adapter mapping to be `ready_for_target_adapter`.
- No target adapter materialization in this node.
- No candidate target file creation.
- No `state/product/*` writeback.
- No PDF/DOCX render or copy.
- No model execution or statistical artifact overwrite.

## Verification

- RED: `python3 -m unittest tests.test_auto_mode_formal_target_adapter_execution -v` fails before implementation because `Program.workbench.auto_mode_formal_target_adapter_execution` does not exist.
- GREEN: target tests pass after minimal execution-gate implementation.
- Real run writes `Results/json/auto_mode_formal_target_adapter_execution.json` and `Reviews/auto_mode_formal_target_adapter_execution.md` with current status blocked by P7-N readiness.
