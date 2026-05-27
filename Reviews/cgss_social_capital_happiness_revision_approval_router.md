# CGSS 修订审批路由记录

- 题目：社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析
- schema：`p6.cgss_revision_approval_router.v1`
- 审批状态：`pending_human_revision_queue_decision`
- 人工决策：`defer`
- 路由状态：`waiting_for_human_revision_queue_decision`
- 下一路由：`wait_for_human_confirmation`
- 草案层：是
- 写入正式论文：否
- 写入 state/product：否
- 生成 Agent 工单：false

## 下一步
- `human_approve_revise_reject_or_defer_cgss_revision_task_queue`

## 路由 JSON
```json
{
  "schema_version": "p6.cgss_revision_approval_router.v1",
  "generated_at": "2026-05-27T11:36:18.424737+00:00",
  "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
  "source_approval": {
    "schema_version": "p6.cgss_revision_queue_approval.v1",
    "status": "pending_human_revision_queue_decision",
    "decision": "defer",
    "approved": false
  },
  "decision": "defer",
  "approved": false,
  "draft_layer_only": true,
  "formal_writeback_allowed": false,
  "can_write_product_state": false,
  "agent_work_orders_generated": false,
  "work_order_manifest": {},
  "next_actions": [
    "human_approve_revise_reject_or_defer_cgss_revision_task_queue"
  ],
  "status": "waiting_for_human_revision_queue_decision",
  "route": "wait_for_human_confirmation",
  "written_work_orders": []
}
```
