# Codex Phase A BDD 行为对齐

日期：2026-05-10

范围：Codex 负责的后端/API 工作。本文只定义行为，不包含实现代码。确认后再进入 TDD 测试阶段。

依据：

- `docs/architecture-v2/technical-architecture.md`
- `docs/architecture-v2/api-contract-v2.md`
- 项目级 `AGENTS.md` 中的 BDD + TDD 约束

## 目标

Phase A 的后端目标不是完整替换现有执行系统，而是为 Kimi 的研究旅程 UI 提供稳定、可审计、带 mock 标记的 API 骨架。

所有 mock 数据必须显式包含：

```json
{
  "_meta": {
    "evidence_level": "mock"
  }
}
```

## 行为 1：研究总览 API 返回完整阶段摘要

**Given** 已存在一个项目 `project_id`，且该项目可能已有 workflow、task、artifact 状态  
**When** 前端请求 `GET /api/v1/projects/{project_id}/overview`  
**Then** 后端返回研究总览对象，包含研究问题、总体进度、当前阶段、下一步建议，以及 6 个阶段摘要卡片

业务规则：

研究总览是 v2 产品的入口，不应要求前端自己拼接 project/workflow/artifact 多个接口。后端需要聚合出稳定的 overview response，让 UI 可以直接渲染“从数据到论文”的当前状态。

验收重点：

- 返回结构包含 `_meta.evidence_level`
- 返回 6 个阶段摘要卡片
- 每个阶段至少包含 `stage_id`, `title`, `status`, `progress`, `summary`
- 不存在 project 时返回统一错误格式，而不是空白成功响应

## 行为 2：旅程条 API 返回 9 个研究阶段

**Given** 已存在一个项目 `project_id`  
**When** 前端请求 `GET /api/v1/projects/{project_id}/journey`  
**Then** 后端返回 9 个旅程阶段，每个阶段都有 id、名称、状态、进度和跳转目标

业务规则：

旅程条是 v2 的全局导航锚点，必须由后端提供统一阶段语义，避免 Kimi 前端和 Codex 后端各自硬编码不同阶段。

验收重点：

- `stages` 数量固定为 9
- 每个 stage 必须包含 `id`, `name`, `status`, `progress`, `href`
- `status` 只允许使用约定枚举，例如 `completed`, `in_progress`, `blocked`, `not_started`
- `progress` 在 0 到 1 之间
- 返回结构包含 `_meta.evidence_level`

## 行为 3：数据集列表 API 在 Phase A 可返回空列表但必须可解释

**Given** 项目当前还没有真实上传数据集  
**When** 前端请求 `GET /api/v1/projects/{project_id}/datasets`  
**Then** 后端返回空的 dataset 列表，并提供 mock/meta 信息和下一步提示，而不是返回 404 或让前端自行猜测状态

业务规则：

Phase A 允许 dataset_service 先是 mock/空实现，但 UI 必须能区分“没有数据集”和“接口未实现”。这可以支撑数据与变量页面的空状态。

验收重点：

- 返回 `items: []`
- 返回 `_meta.evidence_level: "mock"`
- 返回可用于 UI 空状态的提示字段，例如 `next_action` 或 `empty_state`
- 项目不存在时仍返回 `project_not_found`

## 行为 4：研究设计 API 返回可渲染的设计状态

**Given** 项目存在，但可能尚未确认研究问题、变量、识别策略或模型设定  
**When** 前端请求 `GET /api/v1/projects/{project_id}/design`  
**Then** 后端返回研究设计状态，至少包含研究问题、变量角色、候选识别策略、模型设定状态和待确认项

业务规则：

研究设计页不能只显示静态文案。即使 Phase A 是 mock，也要建立后续真实 design_service 的响应形状，让用户知道哪些决策已经确认，哪些需要 HITL。

验收重点：

- 返回 `_meta.evidence_level`
- 返回 `research_question`
- 返回 `variables` 或等价变量角色结构
- 返回 `strategies` 或等价策略候选结构
- 返回 `pending_confirmations`，供前端展示待确认项

## 行为 5：草稿列表 API 连接真实 Manuscripts 目录

**Given** 项目目录中可能存在 `Manuscripts/generated/` 下的 Markdown、LaTeX 或其他草稿文件  
**When** 前端请求 `GET /api/v1/projects/{project_id}/drafts`  
**Then** 后端读取真实项目文件并返回草稿章节列表，而不是纯 mock 数据

业务规则：

论文草稿是用户最终能感知的核心产物。Phase A 应优先连接已有文件系统，哪怕只读取清单，也要避免草稿页完全 mock。

验收重点：

- 返回草稿 `items`
- 每个 draft item 至少包含 `chapter_id`, `title`, `path`, `status`
- 不应读取项目根目录以外的文件
- 文件不存在时返回空列表和可解释空状态
- 如果草稿列表混入 mock 补位数据，必须标记 `_meta.evidence_level: "mock"`

## 行为 6：Agent 列表同时包含流水线角色和研究维度角色

**Given** v2 架构要求融合 CoPaper 风格 pipeline roles 和现有 10 个 research dimension agents  
**When** 前端请求 `GET /api/v1/agents`  
**Then** 后端返回 Agent 列表，至少包含 `pipeline` 和 `dimension` 两类 `role_type`

业务规则：

Agent 控制台不再只是 10 个并行研究员列表。它需要同时表达“生产流水线角色”和“研究维度专家”，为后续 Supervisor 路由打基础。

验收重点：

- 返回 `_meta.evidence_level`
- 列表中至少有一个 `role_type: "pipeline"` 的 Agent
- 列表中至少有一个 `role_type: "dimension"` 的 Agent
- 现有 10 个研究维度 Agent 不应消失
- 每个 Agent 至少包含 `id`, `name`, `role`, `role_type`, `status`

## 行为 7：Agent 详情 API 展示治理字段

**Given** 前端在 Agent 控制台点击某个 Agent  
**When** 前端请求 `GET /api/v1/agents/{agent_id}/details`  
**Then** 后端返回 Agent 详情，包含身份、权限、能力注册、成本追踪、产物归属和审计日志

业务规则：

这是我们区别于 CoPaper 的关键能力。Agent 不是头像和进度条，而是有身份、权限、能力边界、成本和产物责任的可治理执行主体。

验收重点：

- 返回 `_meta.evidence_level`
- 返回 `identity`
- 返回 `permissions`
- 返回 `capabilities`
- 返回 `cost`
- 返回 `artifacts`
- 返回 `audit_log`
- 未知 Agent 返回 `agent_not_found`

## 行为 8：产物 provenance API 返回可追溯链路

**Given** 一个 artifact 已存在，或 Phase A 需要为 UI 提供 mock provenance  
**When** 前端请求 `GET /api/v1/artifacts/{artifact_id}/provenance`  
**Then** 后端返回该产物的 lineage 数组，每一步包含步骤、类型、描述、执行者和时间

业务规则：

产物不能只是一个文件路径。用户需要知道这个产物来自哪个数据、哪次清洗、哪个 Agent、哪段代码、哪次确认，才能判断它是否可用于正式论文。

验收重点：

- 返回 `_meta.evidence_level`
- 返回 `artifact_id`
- 返回 `lineage`
- 每个 lineage step 至少包含 `step`, `type`, `description`, `actor`
- 未知 artifact 返回 `artifact_not_found`
- mock provenance 不能被 promote 为正式产物

## 需要用户确认的边界条件

1. Phase A 是否只实现 `GET` 端点，不实现上传、PUT、DELETE、pause/resume/provider 切换等写操作？
2. `GET /api/v1/projects/{project_id}/design` 在 API 契约总览中出现，但详细契约没有展开；Phase A 是否允许 Codex 先定义最小响应 schema？
3. `GET /api/v1/datasets/{dataset_id}/schema` 是否纳入 Phase A，还是等真实 dataset upload 后再做？
4. Agent 列表中的 pipeline roles 是否采用 6 个角色：supervisor、preparation、modeling、visualization、writing、review/export？
5. overview 的 6 个阶段摘要是否固定为：数据与变量、研究设计、实证执行、论文草稿、产物与复现、Agent 控制台？
6. 所有 mock response 是否统一只允许 `evidence_level: "mock"`，而真实文件读取 response 使用 `evidence_level: "local_file"`？
7. Phase A 的错误响应是否完全复用现有 `error_response(status_code, code, message)` 格式，不新增复杂 details？

## 确认后进入 TDD 的测试文件建议

确认以上行为后，Codex 再新增或修改测试：

- `tests/test_api_contract_v2.py`
- `tests/backend/test_overview_service.py`
- `tests/backend/test_agent_registry_service.py`
- `tests/backend/test_draft_service.py`

测试必须先失败，失败原因应是端点或服务尚未实现，而不是测试 fixture 错误。

## TDD 执行状态

首次失败测试命令：

```bash
python3 -m unittest tests.test_api_contract_v2 -v
```

首次失败结果：11 条测试运行，其中 8 条 BDD 行为因 v2 GET 端点尚未实现返回 404，3 条错误格式测试因缺少统一 `error` 字段失败。失败原因符合 TDD 预期：功能尚未实现，而不是测试夹具错误。

当前通过测试命令：

```bash
python3 -m unittest tests.test_api_contract_v2 -v
```

当前通过结果：11/11 OK。

### 行为 1 测试状态与 API 样例

测试：`test_bdd_1_overview_returns_six_stage_summaries`

状态：已通过。

Endpoint：`GET /api/v1/projects/{project_id}/overview`

返回样例：

```json
{
  "_meta": {"evidence_level": "mock", "service": "overview_service"},
  "research_question": "工业机器人如何影响劳动力市场匹配效率？",
  "current_stage": "overview",
  "overall_progress": 0.1,
  "stage_summaries": [
    {"stage_id": "data", "title": "数据与变量", "status": "in_progress", "progress": 0.1, "summary": "等待登记数据源、样本口径和核心变量。"}
  ]
}
```

### 行为 2 测试状态与 API 样例

测试：`test_bdd_2_journey_returns_nine_required_stages`

状态：已通过。

Endpoint：`GET /api/v1/projects/{project_id}/journey`

返回样例：

```json
{
  "_meta": {"evidence_level": "mock", "service": "journey_service"},
  "stages": [
    {"id": "question", "name": "研究问题", "status": "completed", "progress": 1.0, "href": "#view-overview"},
    {"id": "data", "name": "数据准备", "status": "in_progress", "progress": 0.1, "href": "#view-data-variables"}
  ]
}
```

### 行为 3 测试状态与 API 样例

测试：`test_bdd_3_datasets_empty_state_is_explicitly_mocked`

状态：已通过。

Endpoint：`GET /api/v1/projects/{project_id}/datasets`

返回样例：

```json
{
  "_meta": {"evidence_level": "mock", "service": "dataset_service"},
  "items": [],
  "empty_state": {
    "title": "尚未登记数据集",
    "description": "Phase A 只返回可解释空状态；真实上传和 schema 解析留到后续阶段。",
    "next_action": "在数据与变量页登记数据来源、样本口径和变量字典。"
  }
}
```

### 行为 4 测试状态与 API 样例

测试：`test_bdd_4_design_returns_minimum_renderable_state`

状态：已通过。

Endpoint：`GET /api/v1/projects/{project_id}/design`

返回样例：

```json
{
  "_meta": {"evidence_level": "mock", "service": "design_service"},
  "research_question": "工业机器人如何影响劳动力市场匹配效率？",
  "variables": {"outcome": [], "treatment": [], "controls": [], "fixed_effects": []},
  "strategies": [{"id": "baseline_panel", "name": "双向固定效应基准模型", "status": "candidate", "evidence_level": "mock"}],
  "pending_confirmations": ["确认被解释变量的测度口径。"]
}
```

### 行为 5 测试状态与 API 样例

测试：`test_bdd_5_drafts_read_real_manuscripts_as_local_file`

状态：已通过。

Endpoint：`GET /api/v1/projects/{project_id}/drafts`

返回样例：

```json
{
  "_meta": {"evidence_level": "local_file", "service": "draft_service"},
  "source_root": "Manuscripts/generated",
  "items": [
    {"chapter_id": "paper_draft", "title": "工业机器人与劳动力市场匹配效率", "path": "Manuscripts/generated/paper_draft.md", "status": "available", "format": "md"}
  ]
}
```

### 行为 6 测试状态与 API 样例

测试：`test_bdd_6_agents_list_separates_pipeline_and_dimension_roles`

状态：已通过。

Endpoint：`GET /api/v1/agents`

返回样例：

```json
{
  "_meta": {"evidence_level": "mock", "service": "agent_registry_service"},
  "role_types": ["pipeline", "dimension"],
  "items": [
    {"id": "pipeline_overview", "name": "Overview", "role": "研究总览协调", "role_type": "pipeline", "status": "available"},
    {"id": "dimension_01", "name": "墨白", "role": "政策语境研究员", "role_type": "dimension", "status": "available"}
  ]
}
```

### 行为 7 测试状态与 API 样例

测试：`test_bdd_7_agent_details_include_governance_fields`

状态：已通过。

Endpoint：`GET /api/v1/agents/{agent_id}/details`

返回样例：

```json
{
  "_meta": {"evidence_level": "mock", "service": "agent_registry_service"},
  "identity": {"id": "pipeline_supervisor", "name": "Supervisor", "role_type": "pipeline", "provider": "local_codex"},
  "permissions": [{"scope": "read_project_context", "level": "allowed"}],
  "capabilities": [{"id": "summarize_state", "name": "汇总项目状态", "status": "registered"}],
  "cost": {"provider": "local_codex", "estimated_tokens": 0, "estimated_cost_usd": 0, "evidence_level": "mock"},
  "artifacts": [],
  "audit_log": [{"actor": "system", "action": "phase_a_registry_loaded"}]
}
```

### 行为 8 测试状态与 API 样例

测试：`test_bdd_8_artifact_provenance_returns_lineage`

状态：已通过。

Endpoint：`GET /api/v1/artifacts/mock_artifact_baseline/provenance`

返回样例：

```json
{
  "_meta": {"evidence_level": "mock", "service": "provenance_service"},
  "artifact_id": "mock_artifact_baseline",
  "lineage": [
    {"step": 1, "type": "mock_source", "description": "Phase A baseline artifact used for UI provenance rendering.", "actor": "pipeline_artifacts"}
  ],
  "promotion_policy": {"allowed": false, "reason": "mock evidence cannot be promoted as a formal artifact."}
}
```
