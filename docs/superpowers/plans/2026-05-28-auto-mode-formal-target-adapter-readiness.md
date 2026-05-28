# Auto Mode Formal Target Adapter Readiness Plan

Date: 2026-05-28

## Node Goal

P7-N consumes the P7-M apply manifest and maps each approved writeback target group to concrete candidate target paths for later formal target adapters.

This node is still a readiness/mapping gate. It does not copy, mutate, render, or write formal manuscript sources, bibliography, project bibliography, DesignSpec, RunPlan, product state, PDFs, DOCX, model outputs, or statistical execution artifacts. It only writes an adapter-readiness report and review Markdown.

## BDD Behaviors

### Behavior 1: Ready apply manifest maps all target groups

Given a valid P7-M apply manifest with six operations
And a package manifest whose source artifacts exist
When Auto Mode builds target adapter readiness
Then the status is `ready_for_formal_target_adapter_review`
And all six writeback target groups are mapped to candidate target paths
And no target adapter is executed.

Business rule: manifest ready 之后仍要先把写回目标显式映射出来，不能让 adapter 隐式猜路径。

### Behavior 2: Missing apply manifest blocks mapping

Given the current repository has no recorded apply manifest
When Auto Mode builds target adapter readiness
Then the status is `blocked_by_apply_manifest`
And no adapter mapping is produced.

Business rule: 没有 P7-M apply manifest 时，P7-N 不能绕过审批链或伪造目标映射。

### Behavior 3: Unknown target group blocks mapping

Given the apply manifest contains an unknown `writeback_target_group`
When target adapter readiness is built
Then it blocks with an unknown target group reason.

Business rule: 未登记的写回目标组必须先补 adapter contract，不能默认写到某个路径。

### Behavior 4: Missing package artifact blocks readiness

Given the apply manifest is valid
But a required package source artifact is missing
When target adapter readiness is built
Then it blocks with a package artifact missing reason.

Business rule: 正式写回候选必须绑定到真实本地产物，不能把不存在的 source 当作可写回证据。

### Behavior 5: Apply manifest boundary violation blocks readiness

Given the apply manifest reports a formal-write boundary flag
When target adapter readiness is built
Then it blocks before mapping.

Business rule: 上游 manifest 只要显示已经越界写入，后续 adapter gate 必须停下。

### Behavior 6: CLI default reflects current blocked state

Given the current default apply manifest path is absent
When the CLI runs with default paths
Then it writes a blocked readiness report and review
And it does not create any candidate target files.

Business rule: 当前真实状态应停在缺少 apply manifest 的阻断处，只留下可审阅证据。

## Boundary Conditions

- Requires `p7.auto_mode_formal_writeback_apply_manifest.v1`.
- Requires `formal_writeback_executed=false` and `formal_target_adapters_executed=false`.
- Requires all apply-manifest boundary flags to be false.
- Requires the package manifest and mapped source artifacts to exist.
- Unknown `writeback_target_group` values block readiness.
- No formal target adapter execution in this node.
- No `state/product/*` writeback.
- No PDF/DOCX render or copy.
- No model execution or statistical artifact overwrite.

## Verification

- RED: `python3 -m unittest tests.test_auto_mode_formal_target_adapter_readiness -v` fails before implementation because `Program.workbench.auto_mode_formal_target_adapter_readiness` does not exist.
- GREEN: target tests pass after minimal readiness/mapping implementation.
- Real run writes `Results/json/auto_mode_formal_target_adapter_readiness.json` and `Reviews/auto_mode_formal_target_adapter_readiness.md` with current status blocked by missing apply manifest.
