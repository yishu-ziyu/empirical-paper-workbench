# Auto Mode Formal Writeback Execution Preflight Plan

Date: 2026-05-28

## Node Goal

P7-L creates the execution preflight after P7-K. It consumes the formal writeback approval ledger and turns an effective approval into a reviewed execution plan for a later explicit writeback command.

This node still does not execute writeback. It does not modify formal manuscript sources, bibliography, project bibliography, DesignSpec, RunPlan, product state, PDF, DOCX, submission package files, model outputs, or statistical execution artifacts.

## BDD Behaviors

### Behavior 1: Effective approval creates execution preflight plan

Given the P7-K approval ledger is `approved_for_formal_writeback_execution_preflight`
And it has approved manuscript, bibliography, method, statistical, reproducibility, and package-artifact scopes
When Auto Mode builds the execution preflight
Then the status is `ready_for_formal_writeback_execution_review`
And it creates a plan item for each approved scope
And the command still does not execute writeback.

Business rule: 正式写回执行前必须先把将要写什么变成可审阅计划。

### Behavior 2: Block when approval ledger is not effective

Given the current P7-K approval ledger is blocked or deferred
When Auto Mode builds the execution preflight
Then the status is `blocked_by_formal_writeback_approval`
And no execution can be requested.

Business rule: 没有生效审批时，不得进入正式写回执行。

### Behavior 3: Approved ledger without scope blocks execution preflight

Given the approval ledger claims approval
But approved scope is empty
When Auto Mode builds the execution preflight
Then it blocks with a missing-scope reason.

Business rule: 没有明确写回范围的批准不能变成执行计划。

### Behavior 4: Boundary violations block execution preflight

Given the approval ledger already indicates formal state or product state was written
When Auto Mode builds the execution preflight
Then it blocks before any execution request is created.

Business rule: 上游审批账本必须保持只读；发现越界写入时必须停在预检层。

### Behavior 5: Write only execution preflight artifacts

Given an execution preflight is built
When outputs are written
Then JSON and Markdown review files exist
And no formal manuscript, bibliography, project bibliography, DesignSpec, RunPlan, product state, PDF, DOCX, model output, or statistical artifact is written.

Business rule: P7-L 是执行预检，不是正式写回执行器。

### Behavior 6: CLI default reflects current blocked approval

Given the current P7-K approval ledger is blocked by P7-J/P7-I
When the CLI runs with default paths
Then it writes a blocked execution preflight
And reports `formal_writeback_executed=false`.

Business rule: 当前真实状态应该继续停在阻断处，而不是伪造执行准备就绪。

## Boundary Conditions

- Requires `p7.auto_mode_formal_writeback_approval.v1`.
- Requires `status=approved_for_formal_writeback_execution_preflight`.
- Requires `approved=true`, `formal_writeback_allowed=true`, and `can_enter_formal_writeback_execution_preflight=true`.
- Requires non-empty `approved_scope`.
- Rejects any upstream boundary flag indicating formal state, product state, PDF/DOCX, model, or statistical artifact writes.
- No formal writeback.
- No `state/product/*` writeback.
- No PDF/DOCX render or copy.
- No model execution or statistical artifact overwrite.

## Verification

- RED: `python3 -m unittest tests.test_auto_mode_formal_writeback_execution_preflight -v` fails before implementation because `Program.workbench.auto_mode_formal_writeback_execution_preflight` does not exist.
- GREEN: target tests pass after minimal execution preflight implementation.
- Real run writes `Results/json/auto_mode_formal_writeback_execution_preflight.json` and `Reviews/auto_mode_formal_writeback_execution_preflight.md` with current status blocked by the ineffective P7-K approval ledger.
