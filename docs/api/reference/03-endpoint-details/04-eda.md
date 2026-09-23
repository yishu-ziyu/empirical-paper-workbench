# 探索性数据分析 (EDA)

> 上级：[端点详情](../03-endpoint-details.md)


## POST /sessions/{session_id}/eda

运行 EDA 动作。合法 action：`describe` / `corr` / `missing` / `plot` / `scatter` / `regression`。

**请求体**：

```json
{
  "action": "describe"
}
```

**describe 响应 200**：

```json
{
  "action": "describe",
  "result": {
    "columns": ["variable", "count", "mean", "std", "min", "max", "missing"],
    "rows": [
      {"variable": "age", "count": 1000, "mean": 45.2, "std": 12.3, "min": 18, "max": 80, "missing": 5},
      ...
    ]
  }
}
```

**corr 响应 200**：

```json
{
  "action": "corr",
  "result": {
    "variables": ["age", "income", "education"],
    "matrix": [[1.0, 0.3, 0.5], [0.3, 1.0, 0.2], [0.5, 0.2, 1.0]]
  }
}
```

**missing 响应 200**：

```json
{
  "action": "missing",
  "result": {
    "columns": ["variable", "missing_count", "missing_pct"],
    "rows": [
      {"variable": "income", "missing_count": 15, "missing_pct": 0.015},
      ...
    ]
  }
}
```

**错误码**：400（无效 action）

---
