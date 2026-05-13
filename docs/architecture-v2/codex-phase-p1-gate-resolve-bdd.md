# Codex Phase P1 BDD：HITL Gate Resolve API

日期：2026-05-12

范围：后端最小闭环。P0 已经展示 `gates.json`，P1 先让用户介入动作可以被 API 记录，但前端按钮仍需等后续行为确认后再启用。

## 行为 1：用户确认 gate 后写回 gates.json

**Given** 某次 run 已生成 `gates.json`，其中 gate 状态为 `open`  
**When** 前端调用 `POST /api/v1/projects/{project_id}/runs/{run_id}/gates/{gate_id}/resolve`，payload 为 `{"action": "confirm", "note": "..."}`  
**Then** 对应 gate 状态变为 `resolved`，写入 `resolution.action`、`resolution.note`、`resolved_at`，并保留原始 metadata

业务规则：

用户介入必须成为本地文件证据，不能只在浏览器状态中消失。

## 行为 2：resolve 动作追加审计事件

**Given** 用户确认或驳回了一个 gate  
**When** resolve API 成功返回  
**Then** `run_events.jsonl` 追加 `hitl_gate_resolved` 事件，sequence 必须大于原事件流最后一条，evidence_level 为 `local_execution`

业务规则：

HITL 动作是执行轨迹的一部分，必须进入事件流供审计和复现。

## 行为 3：manifest 更新剩余开放 gate 数量

**Given** run manifest 包含 `human_in_loop.open_gate_count`  
**When** 一个 open gate 被 resolve  
**Then** manifest 中 open gate 数量减少，`human_in_loop.gates_path` 继续指向同一个 `gates.json`

业务规则：

顶部运行头和 HITL 面板应能通过 observability 聚合端点看到最新剩余人工介入数量。

## 行为 4：非法 action 或不存在 gate 返回结构化错误

**Given** 请求中的 action 不属于 `confirm/reject/adjust`，或 gate_id 不存在  
**When** 调用 resolve API  
**Then** 后端返回结构化错误，不改写 gates/events/manifest

业务规则：

P1 允许记录用户选择，但不能接受任意状态字符串污染审计轨迹。

## 当前实现边界

- 本轮只实现后端 API 和文件写回，不启用前端确认/驳回按钮。
- `adjust` 只记录动作和 note，不执行重新规划；重新规划属于后续 Agent orchestration。
- resolve 后不删除 gate，保留完整历史记录。
