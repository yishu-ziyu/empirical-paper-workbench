# Kimi 对接报告：真正有意义的 UI 应如何接入可观察执行层

日期：2026-05-10

读者：Kimi，负责整体交互设计与前端 UI。

目标：把当前 UI 从“展示静态阶段和 mock 卡片”升级为“展示真实研究执行过程，并允许用户在关键节点介入”的 Human-in-the-loop 产品界面。

## 1. 本次 Codex 已完成的后端能力

Codex 已经把 `Program/run_paper.py` 的执行过程改造成可观察执行。

现在一次真实运行会生成：

```text
state/runs/<run_id>/
  run_manifest.json
  run_steps.json
  run_events.jsonl
  gates.json
```

这些文件不是 UI mock，而是由真实执行过程写出来的本地执行证据，统一标记：

```json
{
  "_meta": {
    "evidence_level": "local_execution"
  }
}
```

## 2. 前端应该消费的新 API

### 启动一次项目运行

```http
POST /api/v1/projects/{project_id}/runs
Content-Type: application/json

{
  "mode": "dry-run"
}
```

或真实运行：

```json
{
  "mode": "live"
}
```

返回中会有：

```json
{
  "id": "run_xxx",
  "status": "succeeded",
  "observability": {
    "manifest_path": "state/runs/run_xxx/run_manifest.json",
    "steps_path": "state/runs/run_xxx/run_steps.json",
    "events_path": "state/runs/run_xxx/run_events.jsonl",
    "gates_path": "state/runs/run_xxx/gates.json"
  }
}
```

### 获取完整可观察状态

```http
GET /api/v1/projects/{project_id}/runs/{run_id}/observability
```

返回：

```json
{
  "_meta": { "evidence_level": "local_execution" },
  "run_id": "run_xxx",
  "manifest": {},
  "steps": { "items": [] },
  "events": { "items": [] },
  "gates": { "items": [] }
}
```

### 获取事件流

```http
GET /api/v1/projects/{project_id}/runs/{run_id}/events
```

前端可以 1-3 秒轮询这个端点，用来渲染“Agent 正在做什么”。

### 获取阶段状态

```http
GET /api/v1/projects/{project_id}/runs/{run_id}/steps
```

用于渲染研究旅程条、阶段卡片、Agent 任务行。

### 获取用户介入点

```http
GET /api/v1/projects/{project_id}/runs/{run_id}/gates
```

用于渲染 Human-in-the-loop 面板。

## 3. 当前真实 step 模型

目前后端固定输出 7 个最小阶段：

```text
config_load
dataset_intake
topic_confirmation
analysis_execution
draft_generation
state_index
finalization
```

每个 step 都包含：

```json
{
  "id": "dataset_intake",
  "title": "Inspect analysis dataset",
  "actor": "DataAgent",
  "description": "Check whether the configured analysis dataset is available.",
  "status": "completed",
  "started_at": "2026-05-10T08:55:43.342369+00:00",
  "finished_at": "2026-05-10T08:55:43.342525+00:00",
  "summary": "Configured dataset was inspected.",
  "artifacts": [],
  "metadata": {
    "dataset_path": "Data/Final/analysis_sample.csv",
    "dataset_exists": true,
    "key_variables": {
      "outcome": ["wage"],
      "treatment": ["trained"],
      "controls": ["edu", "experience"],
      "instruments": []
    }
  }
}
```

UI 不应该再写死“Completed 100%”。应该从 `steps.items[*].status`、`started_at`、`finished_at`、`summary` 和 `metadata` 渲染。

## 4. 当前真实 event 模型

事件流是 JSONL，API 会转换为数组。每条事件长这样：

```json
{
  "sequence": 6,
  "timestamp": "2026-05-10T08:55:43.342798+00:00",
  "run_id": "run_observable_live_demo",
  "type": "hitl_gate_opened",
  "step_id": "dataset_intake",
  "actor": "DataAgent",
  "message": "Confirm detected dataset fields",
  "evidence_level": "local_execution",
  "metadata": {
    "gate_id": "gate_dataset_fields",
    "required_by": "analysis_execution",
    "blocking": false
  }
}
```

前端建议按 `sequence` 升序渲染，不要按本地时间重新排序。

推荐 UI 映射：

- `run_started`：创建顶部运行状态。
- `step_started`：对应 Agent 行进入 running。
- `step_completed`：对应 Agent 行进入 completed。
- `step_skipped`：显示为跳过，并展示原因。
- `artifact_written`：在右侧产物栏新增产物链接。
- `hitl_gate_opened`：在 HITL 面板新增待确认项。
- `run_succeeded`：显示运行完成。
- `run_failed`：显示失败横幅和失败 step。

## 5. 当前真实 HITL gate 模型

当前一次 live run 会打开 3 个 gate：

```text
gate_dataset_fields
gate_research_question
gate_identification_boundary
```

示例：

```json
{
  "id": "gate_dataset_fields",
  "step_id": "dataset_intake",
  "title": "Confirm detected dataset fields",
  "reason": "The system detected outcome, treatment, and controls from paper.yaml. A user can correct them before trusting downstream analysis.",
  "status": "open",
  "blocking": false,
  "required_by": "analysis_execution",
  "options": [
    "accept_detected_fields",
    "edit_variable_roles",
    "pause_run"
  ],
  "metadata": {
    "dataset_path": "Data/Final/analysis_sample.csv",
    "dataset_exists": true,
    "key_variables": {
      "outcome": ["wage"],
      "treatment": ["trained"],
      "controls": ["edu", "experience"],
      "instruments": []
    }
  }
}
```

注意：本阶段只实现读取和展示，尚未实现 gate resolve API。也就是说，UI 可以先把 gate 显示出来，但“确认 / 修改 / 驳回”的写入动作暂时应设计成 disabled、prototype 或下一阶段 API 需求。

## 6. UI 应该如何重构

### 推荐主界面结构

```text
顶部：Run Header
  - run_id
  - status
  - mode
  - open_gate_count
  - started_at / finished_at

中部左侧：Execution Timeline
  - 用 events.items 渲染真实事件
  - 每条事件展示 actor、step、message、timestamp
  - artifact_written 可以点击跳转到产物

中部中间：Step Board
  - 用 steps.items 渲染 7 个阶段
  - 每个阶段展示 status、actor、summary、metadata 摘要

中部右侧：HITL Gates
  - 用 gates.items 渲染待用户确认点
  - open gate 高亮
  - blocking gate 未来需要置顶

底部：Artifacts / Evidence
  - 从 event.type=artifact_written 和 step.artifacts 聚合
```

### 不建议继续保留的 UI 行为

- 不要用固定的“10/10 agents completed”伪装真实进度。
- 不要在没有真实事件的情况下显示 Agent 正在研究。
- 不要把 mock 的设计候选和真实运行结果混排在同一个视觉层级。
- 不要只显示最终报告按钮，而隐藏执行过程。

### 应保留但改造的 UI 资产

现有 Agent Cluster 的行列表、右侧 drawer、产物面板仍然可用，但数据源要改为：

```text
Agent row        <- steps.items
Agent drawer     <- selected step + related events + related gates
Progress line    <- step status + event timestamps
Artifact drawer  <- artifact_written events
HITL panel       <- gates.items
```

## 7. 和 Codex 后端的下一步接口约定

Kimi 如果要做可交互 UI，请先按只读接入：

1. 启动 run。
2. 保存 `run_id`。
3. 轮询 `/observability` 或 `/events`。
4. 渲染 step、event、gate。
5. gate 操作按钮先做 disabled 状态，文案写清楚“下一阶段支持写回”。

Codex 下一阶段再补写入 API：

```http
POST /api/v1/projects/{project_id}/runs/{run_id}/gates/{gate_id}/resolve
```

计划 payload：

```json
{
  "decision": "accept_detected_fields",
  "comment": "变量解释确认无误",
  "patch": {}
}
```

但这个接口尚未实现，Kimi 不要假设它已经存在。

## 8. 已验证的真实运行样例

Codex 已经执行：

```bash
python3 Program/run_paper.py \
  --project-root artifacts/e2e-runs/2026-05-10-trained-wage/project \
  --run-id run_observable_live_demo
```

真实输出：

```text
[econ-workbench] mode=live
[econ-workbench] run_id=run_observable_live_demo
[econ-workbench] events=state/runs/run_observable_live_demo/run_events.jsonl
[econ-workbench] state=state/project_state.json
[econ-workbench] index=Results/index.json
[econ-workbench] markdown=Manuscripts/generated/paper_draft.md
[econ-workbench] latex=Manuscripts/generated/paper_draft.tex
```

样例文件：

```text
artifacts/e2e-runs/2026-05-10-trained-wage/project/state/runs/run_observable_live_demo/run_manifest.json
artifacts/e2e-runs/2026-05-10-trained-wage/project/state/runs/run_observable_live_demo/run_steps.json
artifacts/e2e-runs/2026-05-10-trained-wage/project/state/runs/run_observable_live_demo/run_events.jsonl
artifacts/e2e-runs/2026-05-10-trained-wage/project/state/runs/run_observable_live_demo/gates.json
```

## 9. 设计原则

这个 UI 的核心不是“好看地展示研究结果”，而是让用户看到系统如何得到结果。

真正有意义的 UI 应该回答：

- 系统现在在哪一步？
- 谁在执行这一步？
- 用了哪个数据或配置？
- 产出了什么文件？
- 哪一步需要我确认？
- 如果我不同意，后续应该在哪里介入？

只要 UI 能回答这些问题，就具备了 Human-in-the-loop 的基础。
