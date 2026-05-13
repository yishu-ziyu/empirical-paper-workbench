# Codex Phase P0 BDD：真实执行可观察 UI

日期：2026-05-12

范围：前端最小产品闭环。基于已存在的后端 run observability API，把真实执行轨迹渲染到 `实证执行` 页面。

## 行为 1：实证执行页展示真实 run 选择与运行头

**Given** 项目已存在至少一次 run，且 `/api/v1/projects/{project_id}/runs` 返回 run 列表  
**When** 用户打开“实证执行”页面  
**Then** 页面默认选择最新 run，并展示 run_id、mode、status、started_at、finished_at、artifact_count 和证据等级

业务规则：

用户首先需要确认自己看的到底是哪一次运行，不能只看到抽象的“执行状态”。

## 行为 2：实证执行页读取完整 observability

**Given** 用户选中了一个 run_id  
**When** 前端请求 `/api/v1/projects/{project_id}/runs/{run_id}/observability`  
**Then** 页面把 manifest、steps、events、gates 都存入状态并触发渲染

业务规则：

前端应消费完整 observability 聚合端点，而不是让每个组件各自拼 API。

## 行为 3：Step Board 渲染真实执行阶段

**Given** observability 返回 `steps.items`  
**When** 页面渲染 Step Board  
**Then** 每个 step 显示 id/title/status/actor/summary、时间和 metadata 摘要

业务规则：

阶段卡片必须来自真实 `run_steps.json`，不能再写死“Phase A 骨架”或“Completed 100%”。

## 行为 4：Event Stream 按 sequence 渲染事件流

**Given** observability 返回 `events.items`  
**When** 页面渲染事件流  
**Then** 事件按 `sequence` 升序展示，并显示 type、actor、step_id、message、timestamp 和 evidence_level

业务规则：

事件顺序由执行器写入的 sequence 决定，不应按浏览器本地时间重排。

## 行为 5：HITL Gates 显示人工介入点但禁用写入动作

**Given** observability 返回 `gates.items`  
**When** 页面渲染 HITL 面板  
**Then** 每个 gate 显示 title、reason、status、blocking、required_by、options 和 metadata；确认/驳回按钮标记为 P1 disabled

业务规则：

P0 只能展示 gate，不能让 UI 暗示已经支持确认/驳回写入。

## 行为 6：Artifact / Evidence 面板聚合产物和证据等级

**Given** events 中存在 `artifact_written`，steps 中也可能包含 artifacts  
**When** 页面渲染产物面板  
**Then** 页面聚合产物路径、来源 step、actor、evidence_level，并显示顶层 `_meta.evidence_level`

业务规则：

产物必须可追溯到真实运行轨迹；mock、本地文件、真实执行不能混在一起。

## 行为 7：历史 run 缺少观测文件时显示可恢复状态

**Given** run 列表中存在旧 run，但该 run 没有 `state/runs/{run_id}/run_manifest.json`、`run_steps.json`、`run_events.jsonl` 或 `gates.json`  
**When** 用户选中该 run，且 observability endpoint 返回 404  
**Then** 页面保留 run 选择器和运行头，显示“缺少可观察执行轨迹”，并提示用户点击“启动试运行”生成新的可观察 run

业务规则：

历史 run 不能让整个“实证执行”页面进入不可恢复错误态；用户必须能从旧状态继续生成新 run。

## 需要后续确认的边界

1. P1 gate resolve API 是否沿用 `/api/v1/hitl/{gate_id}/confirm|reject`，还是改成 project/run 作用域？
2. 从本地数据集启动真实 run 时，是否复用 `/api/v1/projects/{project_id}/runs`，还是新增 dataset-bound run endpoint？
3. StatsPAI adapter 的真实方法调用是否应先接 `Program/run_paper.py`，还是先接 workbench run 编排路径？
