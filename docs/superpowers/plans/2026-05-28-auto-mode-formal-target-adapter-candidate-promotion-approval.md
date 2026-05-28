# P7-T Auto Mode Formal Target Adapter Candidate Promotion Approval

## Goal

P7-T consumes the P7-S verified candidate promotion preflight and records a human decision for candidate promotion. It must not promote candidate targets, copy files, overwrite formal package files, write `state/product/*`, render documents, or rerun models.

## BDD Behaviors

### Behavior 1: Approve a ready preflight without promoting candidates

Given P7-S is `ready_for_verified_candidate_promotion_review`
When a human records `approve` with reviewer and note
Then P7-T records an effective approval ledger for the next explicit promotion execution preflight, while `candidate_targets_promoted=false`.

Business rule: 人工批准只能开启下一道执行预检，不能在审批节点直接提升候选文件。

### Behavior 2: Defer waits without enabling promotion

Given P7-S is ready
When the decision is `defer`
Then P7-T records a waiting state and does not approve candidate promotion.

Business rule: 默认安全状态是等待，不应误认为批准。

### Behavior 3: Block when P7-S is not ready

Given P7-S is blocked
When the decision is `approve`
Then P7-T remains blocked and carries the upstream preflight reasons.

Business rule: 不能绕过候选验证/提升预检阻断。

### Behavior 4: Approve requires reviewer and note

Given P7-S is ready
When the decision is `approve` without reviewer or note
Then P7-T blocks on approval metadata.

Business rule: 有效审批必须可追溯。

### Behavior 5: Revise and reject do not approve promotion

Given P7-S is ready
When the decision is `revise` or `reject`
Then P7-T records the route but leaves promotion disabled.

Business rule: 返修/拒绝只能改变后续路线，不能开启提升。

### Behavior 6: CLI defaults to current blocked preflight

Given the repository's current P7-S output is blocked
When the CLI runs with defaults
Then it writes a blocked approval report/review and does not promote any candidate.

Business rule: 默认命令必须忠实呈现当前真实阻断。

### Behavior 7: Outputs are report/review only

Given approval is effective
When P7-T writes outputs
Then it writes only JSON and Markdown review artifacts, leaving candidate and formal state unchanged.

Business rule: 审批账本不是执行器。

## Boundary Conditions

- P7-T does not copy candidate files into `Submissions/formal_package`.
- P7-T does not write any `state/product/*` artifact.
- A later P7-U node must handle explicit promotion execution preflight.
