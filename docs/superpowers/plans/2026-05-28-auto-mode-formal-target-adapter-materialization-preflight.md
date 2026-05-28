# Auto Mode Formal Target Adapter Materialization Preflight Plan

Date: 2026-05-28

## Node Goal

P7-P consumes the P7-O target adapter execution report and execution manifest, then creates a materialization preflight for candidate target files.

This node still does not materialize candidate targets. It only checks whether a later, explicitly confirmed materialization command can be requested. It does not copy package artifacts, create candidate target files, mutate formal manuscript sources, bibliography, project bibliography, DesignSpec, RunPlan, product state, PDFs, DOCX, model outputs, or statistical execution artifacts.

## BDD Behaviors

### Behavior 1: Recorded execution manifest supports materialization preflight

Given P7-O has recorded an execution manifest
And the manifest contains adapter execution plan items
When Auto Mode builds materialization preflight
Then the status is `ready_for_adapter_materialization_review`
And each adapter execution plan item is converted into a materialization plan item
And no candidate target is created.

Business rule: execution manifest ready 后仍要先做 materialization 预检，不能直接把目标文件写出来。

### Behavior 2: Current blocked execution report blocks preflight

Given the current P7-O execution report is blocked
When Auto Mode builds materialization preflight
Then the status is `blocked_by_target_adapter_execution`
And no materialization plan is produced.

Business rule: P7-P 不能绕过 P7-O 的 readiness 阻断或伪造 manifest。

### Behavior 3: Missing or invalid execution manifest blocks preflight

Given the P7-O execution report says a manifest was recorded
But the execution manifest is missing or has the wrong schema
When Auto Mode builds materialization preflight
Then it blocks with execution manifest reasons.

Business rule: materialization 必须消费真实 manifest，而不是只相信 execution report 的路径字段。

### Behavior 4: Execution report must be a recorded-manifest state

Given the execution report has the right schema
But `execution_manifest_recorded` is false or status is not `target_adapter_execution_manifest_recorded`
When materialization preflight is built
Then it blocks before reading a materialization plan.

Business rule: 只有 P7-O confirmed execute 记录 manifest 后，才允许进入 materialization preflight。

### Behavior 5: Bad adapter execution plan blocks materialization

Given an execution manifest contains a plan item without candidate targets or without `requires_materialization_node=true`
When materialization preflight is built
Then it blocks with materialization contract reasons.

Business rule: adapter plan 不完整时，不能把目标路径猜出来。

### Behavior 6: CLI default reflects current blocked execution state

Given the current repository has a blocked P7-O execution report and no execution manifest
When the CLI runs with default paths
Then it writes a blocked materialization preflight report and review
And it creates no candidate target files.

Business rule: 当前真实状态继续停在 P7-O blocked，不产生任何正式层或候选目标副作用。

## Boundary Conditions

- Requires `p7.auto_mode_formal_target_adapter_execution.v1`.
- Requires `status=target_adapter_execution_manifest_recorded`.
- Requires `execution_manifest_recorded=true`.
- Requires `p7.auto_mode_formal_target_adapter_execution_manifest.v1`.
- Requires manifest `candidate_targets_created=false`.
- Requires every adapter plan item to have candidate targets and `requires_materialization_node=true`.
- No candidate target materialization in this node.
- No formal target adapter execution in this node.
- No `state/product/*` writeback.
- No PDF/DOCX render or copy.
- No model execution or statistical artifact overwrite.

## Verification

- RED: `python3 -m unittest tests.test_auto_mode_formal_target_adapter_materialization_preflight -v` fails before implementation because `Program.workbench.auto_mode_formal_target_adapter_materialization_preflight` does not exist.
- GREEN: target tests pass after minimal materialization-preflight implementation.
- Real run writes `Results/json/auto_mode_formal_target_adapter_materialization_preflight.json` and `Reviews/auto_mode_formal_target_adapter_materialization_preflight.md` with current status blocked by P7-O execution state.
