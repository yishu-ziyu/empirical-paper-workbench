# Auto Mode Formal Target Adapter Candidate Verification Plan

Date: 2026-05-28

## Node Goal

P7-R consumes the P7-Q materialization execute report and materialization manifest, then verifies that materialized candidate targets exist and match the manifest.

This node is a verification gate only. It does not create, repair, overwrite, promote, or formalize candidate targets. It does not mutate formal manuscript sources, bibliography, project bibliography, DesignSpec, RunPlan, product state, PDFs, DOCX, model outputs, or statistical execution artifacts.

## BDD Behaviors

### Behavior 1: Completed materialization verifies candidate targets

Given P7-Q materialization execute completed
And the materialization manifest lists existing candidate targets
When Auto Mode verifies materialized targets
Then the status is `candidate_targets_verified_for_review`
And every materialized target has a verification record
And no formal state is written.

Business rule: materialize 后还必须用机器可读证据验证候选目标，不允许直接进入正式推广。

### Behavior 2: Current blocked materialization execute blocks verification

Given the current P7-Q execute report is blocked
When Auto Mode verifies candidate targets
Then the status is `blocked_by_materialization_execute`
And no target verification records are produced.

Business rule: P7-R 不能绕过 P7-Q 的 materialization 阻断。

### Behavior 3: Missing or invalid materialization manifest blocks verification

Given P7-Q execute report says a materialization manifest was recorded
But the manifest is missing or has the wrong schema
When candidate verification runs
Then it blocks with materialization manifest reasons.

Business rule: 验证必须消费真实 manifest，不能只相信 execute report 的布尔字段。

### Behavior 4: Execute report must be completed materialization state

Given the execute report has the right schema
But `candidate_targets_materialized` is false or status is not `adapter_materialization_completed`
When verification runs
Then it blocks before checking targets.

Business rule: 只有 confirmed materialize 完成后才允许验证 candidate targets。

### Behavior 5: Missing target or byte mismatch blocks verification

Given the materialization manifest lists a target
But the target file is missing or its byte size differs from the manifest
When verification runs
Then it blocks with target verification reasons.

Business rule: 候选目标必须是真实存在且与 manifest 一致的本地文件。

### Behavior 6: Boundary violations block verification

Given either the execute report or manifest reports formal/product write flags
When verification runs
Then it blocks before declaring candidate targets verified.

Business rule: 任何上游越界写入都不能被 verification gate 认可。

### Behavior 7: CLI default reflects current blocked state

Given the current repository has blocked P7-Q output and no materialization manifest
When the CLI runs with default paths
Then it writes a blocked candidate verification report and review
And it writes no formal state.

Business rule: 当前真实状态继续停在 P7-Q blocked，不提升候选目标或正式层。

## Boundary Conditions

- Requires `p7.auto_mode_formal_target_adapter_materialization_execute.v1`.
- Requires `status=adapter_materialization_completed`.
- Requires `candidate_targets_materialized=true`.
- Requires `materialization_manifest_recorded=true`.
- Requires `p7.auto_mode_formal_target_adapter_materialization_manifest.v1`.
- Requires every manifest target to exist and match recorded byte size.
- No candidate target creation or repair.
- No `state/product/*` writeback.
- No formal manuscript/bibliography promotion.
- No PDF/DOCX render.
- No model execution or statistical artifact overwrite.

## Verification

- RED: `python3 -m unittest tests.test_auto_mode_formal_target_adapter_candidate_verification -v` fails before implementation because `Program.workbench.auto_mode_formal_target_adapter_candidate_verification` does not exist.
- GREEN: target tests pass after minimal candidate-verification implementation.
- Real run writes `Results/json/auto_mode_formal_target_adapter_candidate_verification.json` and `Reviews/auto_mode_formal_target_adapter_candidate_verification.md` with current status blocked by P7-Q materialization execute state.
