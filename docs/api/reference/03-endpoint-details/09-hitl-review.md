# HITL 评审

> 上级：[端点详情](../03-endpoint-details.md)


## GET /sessions/{session_id}/review

获取当前章的评审信息。

**响应 200**：

```json
{
  "chapter_index": 0,
  "feedback": "理论框架清晰，但内生性讨论不足",
  "suggestions": "建议补充工具变量分析",
  "score": 0.65,
  "rubric": {
    "endogeneity": 0.5,
    "identification": 0.7,
    "robustness": 0.6,
    "contribution": 0.7,
    "readability": 0.8
  },
  "review_iteration": 1,
  "max_review_iterations": 2,
  "auto_decision": "fail"
}
```

---

## POST /sessions/{session_id}/review/decision

提交评审决策。合法 decision：`accept` / `reject` / `force_pass`。

**请求体**：

```json
{
  "decision": "accept",
  "reviewer": "user",
  "comment": "章节内容完整，无需修改"
}
```

**响应 200**：

```json
{
  "ok": true,
  "decision": "accept",
  "chapter_index": 0,
  "next_action": "proceed"
}
```

`reject` 时 `next_action` 为 `"regenerate"`，触发重生成。

---
