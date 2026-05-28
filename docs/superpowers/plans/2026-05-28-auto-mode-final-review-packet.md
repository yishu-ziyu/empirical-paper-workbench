# Auto Mode Final Review Packet Plan

Date: 2026-05-28

## Node Goal

P7-I turns the P7-H `needs_human_final_review` acceptance chain into a reviewable final packet and a decision router. The packet must collect the five-component readiness evidence plus the paper-package manifest so a human can decide whether to defer, approve for the next preflight, request revision, or reject/rebuild.

This node is not formal promotion. It records review evidence and the human decision route only. Even an `approve` decision can only enable a later formal-promotion preflight; it cannot write formal manuscript, bibliography, project bibliography, DesignSpec, RunPlan, product state, or model outputs.

## BDD Behaviors

### Behavior 1: Build a final review packet from a ready acceptance chain

Given Auto Mode acceptance is `needs_human_final_review`
And the paper package manifest has no missing targets
When P7-I builds the final review packet
Then the packet includes five component statuses, method readiness, statistical readiness, package artifacts, and required review items
And it is marked `awaiting_human_final_review`.

Business rule: 人工终审必须知道自己正在审哪些证据，而不是只看到一个 ready 状态。

### Behavior 2: Block packet creation when upstream readiness is not final-review ready

Given the acceptance chain has missing inputs, repair tasks, or a non-final readiness
When P7-I builds the packet
Then the packet is `blocked_final_review_packet_inputs`
And final decision is not requestable.

Business rule: 有修复队列时不能绕过 Auto Mode repair 直接进入终审。

### Behavior 3: Default decision is defer without formal writeback

Given a review-ready final packet
When the decision router runs with `defer`
Then it waits for a human final review decision
And it writes only packet/router JSON and Markdown review artifacts.

Business rule: 默认动作必须保守，不因为生成了 packet 就自动批准。

### Behavior 4: Approval requires reviewer and note

Given a review-ready final packet
When the decision is `approve` without reviewer or note
Then the router blocks with missing human approval metadata.

Business rule: 人工批准必须可追溯，不能用空审批进入下一门。

### Behavior 5: Approval routes only to formal-promotion preflight

Given a review-ready final packet
And a human reviewer approves with a note
When the decision router runs
Then the status becomes `approved_for_formal_promotion_preflight`
And formal writeback and product-state writeback remain false.

Business rule: P7-I 的 approve 只允许进入下一道预检，不能直接写正式层。

### Behavior 6: Revise and reject route without promotion

Given a review-ready final packet
When the decision is `revise` or `reject`
Then the router records the corresponding repair or rebuild route
And no promotion or writeback is allowed.

Business rule: 人工终审可以要求返修或停止，不应生成任何正式层产物。

## Boundary Conditions

- Requires `p7.auto_mode_acceptance_chain.v1` with `package_readiness=needs_human_final_review`.
- Requires a paper-package manifest with no missing targets.
- Default decision is `defer`.
- `approve`, `revise`, and `reject` require reviewer and note.
- `approve` only enables a later formal-promotion preflight.
- No formal manuscript writeback.
- No formal bibliography or project bibliography writeback.
- No DesignSpec or RunPlan writeback.
- No `state/product/*` writeback.
- No model execution or statistical artifact overwrite.

## Verification

- RED: `python3 -m unittest tests.test_auto_mode_final_review_packet -v` fails before implementation because `Program.workbench.auto_mode_final_review_packet` does not exist.
- GREEN: target tests pass after minimal packet/router implementation.
- Real run writes `Results/json/auto_mode_final_review_packet.json`, `Reviews/auto_mode_final_review_packet.md`, `Results/json/auto_mode_final_review_decision.json`, and `Reviews/auto_mode_final_review_decision.md`.
