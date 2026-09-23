# 上传 & Session 管理

> 上级：[端点详情](../03-endpoint-details.md)


## POST /upload

上传 CSV 文件，创建 session，运行完整的 LangGraph pipeline。

**请求体**：`multipart/form-data`

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file | File | 是 | CSV 文件（最大 50MB） |

**响应 200**：

```json
{
  "session_id": "uuid-string",
  "dataset_meta": {
    "columns": ["var1", "var2", ...],
    "rows": 1000,
    "dtypes": {"var1": "int64", "var2": "object"},
    "missing_count": 42
  }
}
```

**错误码**：400（非 CSV 文件）、413（超过大小限制）、422（解析失败）

---

## POST /sessions

创建空 session（不上传文件）。

**响应 200**：

```json
{
  "session_id": "uuid-string"
}
```

---

## GET /sessions/{session_id}

查询 session 是否存在及是否包含数据集。用于前端 localStorage 恢复校验。

**响应 200**：

```json
{
  "session_id": "uuid-string",
  "exists": true,
  "has_dataset": true
}
```

**错误码**：404（session 不存在）

---
