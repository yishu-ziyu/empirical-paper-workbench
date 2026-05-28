# Auto Mode Formal Writeback Approval Plan

Date: 2026-05-28

## Node Goal

P7-K records the separate human approval required after P7-J formal promotion preflight. It consumes the P7-J preflight ledger and an explicit human decision, then determines whether a later node may enter formal writeback execution preflight.

This node still does not write formal research state. An `approve` decision records approval and enables the next gate, but this command does not modify formal manuscript sources, bibliography, project bibliography, DesignSpec, RunPlan, product state, PDF, DOCX, submission package files, model outputs, or statistical execution artifacts.

## BDD Behaviors

### Behavior 1: Approve ready preflight records approval without writeback

Given the P7-J preflight is `ready_for_formal_writeback_approval`
And a human decision is `approve`
And reviewer and note are present
When Auto Mode builds the formal writeback approval ledger
Then the status is `approved_for_formal_writeback_execution_preflight`
And a later formal writeback execution preflight may be requested
And this command still writes no formal state.

Business rule: 正式写回审批通过只授权下一道执行预检，本节点不能直接改正式论文包。

### Behavior 2: Defer waits without approving writeback

Given the P7-J preflight is ready
When the human decision is `defer`
Then the status is `waiting_for_human_formal_writeback_approval`
And formal writeback remains disallowed.

Business rule: 没有人类明确 approve 时，不能进入实际写回预检。

### Behavior 3: Block when P7-J preflight is not ready

Given the P7-J preflight is blocked
When the human decision is `approve`
Then the status is `blocked_by_formal_promotion_preflight`
And the approval is not recorded as effective.

Business rule: 不能绕过前置 formal promotion preflight 的阻断原因。

### Behavior 4: Approval metadata remains mandatory

Given the P7-J preflight is ready
And a decision claims `approve`
But reviewer or note is missing
When Auto Mode builds the approval ledger
Then it blocks with approval metadata reasons.

Business rule: 正式写回审批必须能追溯到具体人和具体说明。

### Behavior 5: Revise and reject do not enable writeback

Given the P7-J preflight is ready
When the decision is `revise` or `reject`
Then the ledger records that route
And no formal writeback execution preflight can be requested.

Business rule: 返修或拒绝只能记录路线，不能变成隐式批准。

### Behavior 6: Write only approval ledger artifacts

Given an approval ledger is built
When outputs are written
Then only JSON and Markdown review files are written
And no formal manuscript, bibliography, project bibliography, DesignSpec, RunPlan, product state, PDF, DOCX, model output, or statistical artifact is written.

Business rule: P7-K 是审批账本，不是正式写回执行器。

### Behavior 7: CLI default reflects current blocked preflight

Given the current P7-J preflight is blocked by the P7-I defer decision
When the CLI runs with default paths
Then it writes a blocked approval ledger
And reports `formal_writeback_allowed=false`.

Business rule: 当前真实状态应该继续显示等待人工批准，而不是伪造已允许写回。

## Boundary Conditions

- Requires `p7.auto_mode_formal_promotion_preflight.v1`.
- Requires `status=ready_for_formal_writeback_approval` before approval can be effective.
- Requires `can_request_formal_writeback_approval=true`.
- Requires decision `approve` plus reviewer and note before the next formal writeback execution preflight can be requested.
- `defer`, `revise`, and `reject` never enable writeback.
- No formal writeback.
- No `state/product/*` writeback.
- No PDF/DOCX render or copy.
- No model execution or statistical artifact overwrite.

## Verification

- RED: `python3 -m unittest tests.test_auto_mode_formal_writeback_approval -v` fails before implementation because `Program.workbench.auto_mode_formal_writeback_approval` does not exist.
- GREEN: target tests pass after minimal approval ledger implementation.
- Real run writes `Results/json/auto_mode_formal_writeback_approval.json` and `Reviews/auto_mode_formal_writeback_approval.md` with current status blocked by the P7-J preflight.
