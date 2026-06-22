# Workflow API Contract

本文件定义第三层产品工作台读取第二层 workflow 状态的最小接口。

## Endpoint Shape

本地文件等价于未来 API response：

- Source: `artifacts/workflow_runbook_state.json`
- Schema: `workflows/schemas/runbook_state.schema.json`
- Producer: `python3 scripts/23_workflow_runbook.py`
- Validator: `python3 scripts/24_validate_runbook_api.py`

未来产品层可以把它映射为：

```text
GET /api/workflow-state
```

## Response Fields

| Field | Type | Meaning |
|---|---|---|
| `version` | string | runbook state 版本 |
| `layer` | string | 当前固定为 `second` |
| `status` | string | `pass` 或 `partial` |
| `current_route.next_workflow_id` | string/null | 下一步 workflow；无缺口时为 null |
| `artifact_status` | object | present / partial / missing / external 计数 |
| `spec_coverage` | object | 核心 workflow 数和缺失 spec |
| `workflows[]` | array | 十步 workflow 状态 |

## Workflow Object

每个 `workflows[]` 条目必须包含：

- `id`
- `step`
- `name`
- `purpose`
- `agents`
- `inputs`
- `required_outputs`
- `gates`
- `human_checkpoints`
- `stop_conditions`
- `rollback_to`
- `skills`
- `failure_codes`
- `current_issues`
- `spec_path`

## UI Mapping

第三层工作台可直接使用：

- `current_route`: 顶部下一步提示。
- `artifact_status`: 仪表盘统计。
- `workflows[].current_issues`: 每一步红黄灯。
- `workflows[].gates`: 可执行检查按钮。
- `workflows[].failure_codes`: 错误解释和回退建议。
- `workflows[].human_checkpoints`: 人工确认弹窗。

## Boundary

这个 API 只表达状态，不执行任务。

任务执行仍由第一层脚本和第二层 Agent spec 决定；第三层产品不能绕过 human checkpoints 自动改研究结论。
