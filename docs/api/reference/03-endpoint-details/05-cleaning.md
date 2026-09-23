# 数据清洗（样本构造）

> 上级：[端点详情](../03-endpoint-details.md)


## POST /sessions/{session_id}/transform

变量重编码与构造（sub-step 5）。支持类型：`log_transform` / `onehot` / `label` / `bin` / `interaction` / `policy_dummy`。

**请求体示例（log_transform）**：

```json
{
  "type": "log_transform",
  "column": "income"
}
```

**请求体示例（interaction）**：

```json
{
  "type": "interaction",
  "column": "education",
  "other_column": "experience"
}
```

**响应 200**：

```json
{
  "constructed_vars": ["log_income"]
}
```

---

## POST /sessions/{session_id}/filter

样本筛选（sub-step 6）。

**请求体**：

```json
{
  "conditions": [
    {"col": "age", "op": ">=", "val": 18},
    {"col": "income", "op": ">", "val": 0}
  ]
}
```

**响应 200**：

```json
{
  "n_before": 1000,
  "n_after": 950,
  "conditions": [...]
}
```

---

## POST /sessions/{session_id}/balance

面板平衡性检查（sub-step 7）。

**请求体**：

```json
{
  "panel_id": "id",
  "time_col": "year"
}
```

**响应 200**：

```json
{
  "balanced": 500,
  "unbalanced": 50,
  "n_periods": 5,
  "attrition_rate": 0.1
}
```

**错误码**：400（panel_id 或 time_col 缺失）

---
