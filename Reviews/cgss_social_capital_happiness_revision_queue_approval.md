# CGSS 修订任务队列人工决策记录

- 题目：社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析
- schema：`p6.cgss_revision_queue_approval.v1`
- 状态：`pending_human_revision_queue_decision`
- 决策：`defer`
- 审阅人：未记录
- 草案层：是
- 写入正式论文：否
- 写入 state/product：否

## 当前阻断
- `human_approve_cgss_revision_task_queue`

## 决策 JSON
```json
{
  "schema_version": "p6.cgss_revision_queue_approval.v1",
  "generated_at": "2026-05-27T11:21:45.438433+00:00",
  "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
  "decision": "defer",
  "reviewer": "",
  "note": "",
  "approved": false,
  "draft_layer_only": true,
  "formal_writeback_allowed": false,
  "can_write_product_state": false,
  "source_queue": {
    "schema_version": "p6.cgss_revision_task_queue.v1",
    "status": "needs_human_revision_queue_approval",
    "task_count": 8,
    "required_decision": "human_approve_cgss_revision_task_queue"
  },
  "approved_queue": {},
  "status": "pending_human_revision_queue_decision",
  "blocking_reasons": [
    "human_approve_cgss_revision_task_queue"
  ],
  "promotion": {
    "allowed": false,
    "required_decision": "human_approve_cgss_revision_task_queue"
  }
}
```
