# Auto Mode Formal Promotion Preflight Plan

Date: 2026-05-28

## Node Goal

P7-J creates the formal-promotion preflight after P7-I. It consumes the Auto Mode final review packet, final review decision, and paper-package manifest, then determines whether the package may ask for a separate formal writeback approval.

This node still does not write formal research state. Even when the P7-I decision is approved, P7-J only creates a preflight ledger and review Markdown. A later explicit approval gate must authorize any formal manuscript, bibliography, project bibliography, DesignSpec, RunPlan, product state, PDF, DOCX, or submission package writeback.

## BDD Behaviors

### Behavior 1: Ready preflight after explicit final-review approval

Given the final review packet is ready
And the final review decision is `approved_for_formal_promotion_preflight`
And the package manifest has no missing targets
When Auto Mode builds the formal-promotion preflight
Then the status is `ready_for_formal_writeback_approval`
And the preflight exposes manuscript, bibliography, method, statistical, reproducibility, and package-artifact scopes.

Business rule: 人工终审通过后，只能进入下一道正式写回审批，不应直接写正式层。

### Behavior 2: Block while final review is deferred

Given the final review decision is `defer`
When Auto Mode builds the preflight
Then the status is `blocked_by_final_review_decision`
And no formal writeback approval can be requested.

Business rule: 没有人类明确 approve 时，不能进入正式推广预检。

### Behavior 3: Approval metadata remains mandatory

Given a decision claims approval but lacks reviewer or note
When Auto Mode builds the preflight
Then it blocks with human approval metadata reasons.

Business rule: 每次进入正式层前都必须可追溯到具体审阅人和说明。

### Behavior 4: Package manifest gaps block preflight

Given final review is approved
But the paper-package manifest has missing targets
When Auto Mode builds the preflight
Then it blocks before formal writeback approval.

Business rule: package 文件不完整时不能靠审批绕过交付缺口。

### Behavior 5: Write only preflight review artifacts

Given the preflight is built
When outputs are written
Then JSON and Markdown review files exist
And no formal manuscript, bibliography, project bibliography, DesignSpec, RunPlan, product state, model output, PDF, DOCX, or submission package is written.

Business rule: P7-J 是预检账本，不是正式写回或导出执行。

### Behavior 6: CLI default reflects the current real defer state

Given the current P7-I decision is `defer`
When the CLI runs with default paths
Then it writes a blocked preflight report
And reports `formal_writeback_allowed=false`.

Business rule: 当前真实状态应该诚实显示“等人工批准”，而不是伪造可交付正式包。

## Boundary Conditions

- Requires `p7.auto_mode_final_review_decision.v1`.
- Requires `decision.status=approved_for_formal_promotion_preflight` before ready status.
- Requires reviewer and note on approved decisions.
- Requires `p7.auto_mode_final_review_packet.v1` with `can_request_final_decision=true`.
- Requires package manifest with no missing targets.
- Ready status only means `can_request_formal_writeback_approval=true`.
- No formal writeback.
- No `state/product/*` writeback.
- No PDF/DOCX render or copy.
- No model execution or statistical artifact overwrite.

## Verification

- RED: `python3 -m unittest tests.test_auto_mode_formal_promotion_preflight -v` fails before implementation because `Program.workbench.auto_mode_formal_promotion_preflight` does not exist.
- GREEN: target tests pass after minimal preflight implementation.
- Real run writes `Results/json/auto_mode_formal_promotion_preflight.json` and `Reviews/auto_mode_formal_promotion_preflight.md` with current status blocked by the deferred final-review decision.
