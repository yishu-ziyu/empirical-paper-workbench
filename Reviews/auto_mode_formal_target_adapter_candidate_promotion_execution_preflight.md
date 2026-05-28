# Auto Mode Formal Target Adapter Candidate Promotion Execution Preflight

- 题目：社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析
- 状态：`blocked_by_candidate_promotion_approval`
- 可请求 candidate promotion execute：false
- 需要显式 promotion execute 命令：false
- 已提升 candidate targets：false
- 已执行正式写回：false
- 本命令写入正式层：false
- 写入 state/product：false

## Blocking Reasons
- `candidate_promotion_approval_not_effective`
- `candidate_promotion_not_approved`
- `verified_candidate_promotion_not_allowed`
- `candidate_promotion_approval_cannot_enter_execution_preflight`
- `candidate_promotion_approval_has_blocking_reasons`
- `candidate_promotion_approval_decision_not_approve`
- `candidate_promotion_approval_metadata_incomplete`

## Promotion Execution Plan
- 无；等待生效审批或修复 approved promotion plan。

## Next Action
- `obtain_effective_candidate_promotion_approval`: The execution preflight cannot proceed until P7-T approval is effective.
