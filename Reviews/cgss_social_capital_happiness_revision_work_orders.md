# CGSS Agent 草案工单门禁

- 题目：社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析
- schema：`p6.cgss_revision_work_orders.v1`
- 状态：`blocked_revision_queue_not_approved`
- 草案层：是
- 写入正式论文：否
- 写入 state/product：否

## 当前阻断
- `human_approve_cgss_revision_task_queue`

## 工单 Manifest
```json
{
  "schema_version": "p6.cgss_revision_work_orders.v1",
  "generated_at": "2026-05-27T11:13:55.929447+00:00",
  "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
  "draft_layer_only": true,
  "formal_writeback_allowed": false,
  "can_write_product_state": false,
  "source_queue": {
    "schema_version": "p6.cgss_revision_task_queue.v1",
    "status": "needs_human_revision_queue_approval",
    "required_decision": "human_approve_cgss_revision_task_queue"
  },
  "status": "blocked_revision_queue_not_approved",
  "blocking_reasons": [
    "human_approve_cgss_revision_task_queue"
  ],
  "work_orders": [],
  "written_work_orders": [],
  "promotion": {
    "allowed": false,
    "required_decision": "human_approve_cgss_revision_task_queue"
  }
}
```
