# P7-S Auto Mode Formal Target Adapter Candidate Promotion Preflight

## Goal

P7-S consumes the P7-R verified candidate target report and builds a preflight plan for later candidate promotion. It must not promote candidate targets, copy files, overwrite formal package files, write `state/product/*`, render documents, or rerun models.

## BDD Behaviors

### Behavior 1: Verified candidates create a promotion preflight plan

Given P7-R reports `candidate_targets_verified_for_review`
When Auto Mode builds the candidate promotion preflight
Then it produces one promotion plan item per verified target and marks the preflight ready for a later approval/execute node.

Business rule: 已验证候选目标只能进入“可审阅的正式提升预检”，不能在本节点直接提升。

### Behavior 2: Current blocked verification blocks promotion preflight

Given the current P7-R report is blocked
When Auto Mode builds the candidate promotion preflight
Then it blocks and carries the upstream reasons forward.

Business rule: 不能绕过 P7-R 的 materialization/verification 阻断。

### Behavior 3: Missing or invalid verification schema blocks promotion preflight

Given the verification report is missing or has an unexpected schema
When Auto Mode builds the candidate promotion preflight
Then it blocks without creating a promotion plan.

Business rule: 正式提升链路必须依赖明确版本的上游证据。

### Behavior 4: Verification records must all be verified

Given P7-R is nominally ready but one record is missing, unverified, outside `Submissions/auto_mode`, or lacks a SHA256
When Auto Mode builds the candidate promotion preflight
Then it blocks and names the faulty candidate target.

Business rule: 每个候选文件必须有可审计的验证记录，不能用整体 ready 状态替代逐项证据。

### Behavior 5: Boundary violations block promotion preflight

Given P7-R or its boundary flags indicate formal state, product state, adapter execution, or candidate repair side effects
When Auto Mode builds the candidate promotion preflight
Then it blocks before building any promotion plan.

Business rule: 候选提升预检不能消费已经越界的证据。

### Behavior 6: CLI defaults to the current blocked state

Given the repository's current P7-R output is blocked
When the CLI runs with defaults
Then it writes a blocked report/review and does not promote any candidate.

Business rule: 默认命令必须保持安全，只暴露当前真实阻断。

### Behavior 7: Outputs are report/review only

Given verified candidates are ready
When P7-S writes outputs
Then it writes only JSON and Markdown review artifacts, leaving candidate targets and formal state unchanged.

Business rule: 本节点是预检，不是提升执行器。

## Boundary Conditions

- Formal destination path mapping remains advisory in this node.
- Any real copy/overwrite must be handled by a later explicit promotion execution node.
- Current repository state is expected to remain blocked because P7-R is blocked.
