# 通用错误格式

> 上级：[econpaper API 文档](../README.md)


```json
{
  "error": "Internal server error",
  "detail": "错误详情（DEBUG 模式）",
  "request_id": "uuid",
  "degraded": true
}
```

| 字段 | 说明 |
|------|------|
| `error` | 错误类型 |
| `detail` | 错误详情（生产环境仅 500 时隐藏） |
| `request_id` | 请求追踪 ID |
| `degraded` | 是否降级（>= 500 时为 true） |
