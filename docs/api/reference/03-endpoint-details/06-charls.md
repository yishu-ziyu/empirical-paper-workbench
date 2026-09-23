# CHARLS 数据集

> 上级：[端点详情](../03-endpoint-details.md)


## GET /sessions/{session_id}/charls/detect

检测上传的数据集是否为 CHARLS 格式。

**响应 200**：

```json
{
  "dataset_type": "CHARLS",
  "charls_config": {
    "variable_mapping": {...},
    "waves": [1, 2, 3, 4, 5],
    "filter_presets": [...]
  }
}
```

非 CHARLS 数据集时 `charls_config` 为 null。

---

## POST /sessions/{session_id}/charls/confirm

确认 CHARLS 向导配置，写入 session state。

**请求体**：

```json
{
  "variable_mapping": {"ID": "id", "wave": "wave"},
  "waves": [1, 2, 3],
  "filter_presets": [{"col": "age", "op": ">=", "val": 50}]
}
```

**响应 200**：

```json
{
  "ok": true,
  "charls_config": {...}
}
```

---
