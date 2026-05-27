# CGSS RunPlan seed 审阅决策

- 题目：社会资本对居民主观幸福感的影响研究--基于CGSS数据的实证分析
- schema：`p6.cgss_run_plan_seed_approval.v1`
- 状态：`pending_human_run_plan_seed_decision`
- 决策：`defer`
- 审阅人：未记录
- 草案层：是
- 写入正式 RunPlan：否
- 写入 state/product：否
- 执行模型：否，本节点只记录审阅决策

## 当前阻断
- `human_approve_cgss_run_plan_seed`

## 决策 JSON
```json
{
  "schema_version": "p6.cgss_run_plan_seed_approval.v1",
  "generated_at": "2026-05-27T12:58:41.673278+00:00",
  "topic": "社会资本对居民主观幸福感的影响研究--基于CGSS数据的实证分析",
  "decision": "defer",
  "reviewer": "",
  "note": "",
  "approved": false,
  "draft_layer_only": true,
  "formal_writeback_allowed": false,
  "can_write_product_state": false,
  "source_run_plan_seed": {
    "schema_version": "p6.cgss_run_plan_seed.v1",
    "status": "needs_human_run_plan_seed_review",
    "task_count": 4,
    "required_decision": "human_approve_cgss_run_plan_seed"
  },
  "approved_run_plan_seed": {},
  "status": "pending_human_run_plan_seed_decision",
  "blocking_reasons": [
    "human_approve_cgss_run_plan_seed"
  ],
  "promotion": {
    "allowed": false,
    "required_decision": "human_approve_cgss_run_plan_seed"
  }
}
```
