# 进度

> 上级：[端点详情](../03-endpoint-details.md)


## GET /sessions/{session_id}/progress

返回 6 章完成进度。

**响应 200**：

```json
{
  "total": 6,
  "completed": 2,
  "current": 3,
  "body_chapters": [
    {"type": "intro", "title": "引言", "status": "approved"},
    {"type": "lit_review", "title": "文献综述", "status": "approved"},
    {"type": "data_desc", "title": "数据描述", "status": "generated"},
    {"type": "methods", "title": "实证方法", "status": null},
    {"type": "results", "title": "实证结果", "status": null},
    {"type": "conclusion", "title": "结论", "status": null}
  ]
}
```

---
