# 上传 & Session 管理

> 上级：[端点详情](../03-endpoint-details.md)


## POST /upload

上传 CSV 文件，创建 session，运行完整的 LangGraph pipeline。

**请求体**：`multipart/form-data`

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file | File | 是 | CSV / Stata `.dta` / Excel `.xlsx` 文件（最大 50MB），按内容识别格式 |

**响应 200**：

```json
{
  "session_id": "uuid-string",
  "dataset_meta": {
    "columns": ["var1", "var2", ...],
    "rows": 1000,
    "dtypes": {"var1": "int64", "var2": "object"},
    "missing_count": 42,
    "variable_labels": {"a8a": "您个人去年全年的总收入是多少"},
    "value_labels": {"a7a": {"-3": "拒绝回答", "13": "大学本科(正规高等教育)"}}
  }
}
```

Stata `.dta` 按 Stata 的存储方式读入：带值标签的列保留**数值代码**（不转成标签文字，
重复标签也不会拒收），变量标签与值标签放进 `variable_labels` / `value_labels`
（每列最多 40 个值标签）。CSV / Excel 这两个字段为空对象。调查数据里的负数缺失代码
（如 CFPS `-8 不适用`、CGSS `-3 拒绝回答`）原样保留在数据中，需要在清洗时处理。
`GET /sessions/{id}` 的 `dataset` 投影同样带这两个字段。

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
