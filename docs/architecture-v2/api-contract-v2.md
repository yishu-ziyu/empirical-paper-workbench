# API 契约 v2 —— 研究旅程重塑

日期：2026-05-10
读者：Kimi（前端）+ Codex（后端）
来源：现有 `product-api-contract.md` + CoPaper 调研

---

## 1. 原则

- 基于现有 `/api/v1/` 契约扩展，不破环已有端点
- 新增端点遵循相同的资源模型、错误格式、时间格式
- 所有 mock 数据包含 `_meta.evidence_level: "mock"`
- 内容类型：`application/json; charset=utf-8`
- 时间格式：ISO 8601 UTC

---

## 2. 新增端点总览

### 2.1 研究总览

```
GET /api/v1/projects/{project_id}/overview
```

### 2.2 旅程条

```
GET /api/v1/projects/{project_id}/journey
```

### 2.3 数据与变量

```
POST   /api/v1/projects/{project_id}/datasets
GET    /api/v1/projects/{project_id}/datasets
GET    /api/v1/datasets/{dataset_id}
GET    /api/v1/datasets/{dataset_id}/schema
GET    /api/v1/datasets/{dataset_id}/snapshot
POST   /api/v1/datasets/{dataset_id}/sheets/inspect
PUT    /api/v1/datasets/{dataset_id}/variables/{variable_name}
DELETE /api/v1/datasets/{dataset_id}
```

### 2.4 变量与清洗

```
POST /api/v1/projects/{project_id}/variables/assign
GET  /api/v1/projects/{project_id}/codebook
PUT  /api/v1/projects/{project_id}/codebook/{variable_name}
GET  /api/v1/projects/{project_id}/cleaning-log
POST /api/v1/projects/{project_id}/cleaning-log
GET  /api/v1/projects/{project_id}/quality-report
```

### 2.5 研究设计

```
PUT    /api/v1/projects/{project_id}/research-question
GET    /api/v1/projects/{project_id}/strategies
POST   /api/v1/projects/{project_id}/strategies/select
POST   /api/v1/projects/{project_id}/strategies/confirm
GET    /api/v1/projects/{project_id}/dag
PUT    /api/v1/projects/{project_id}/dag
POST   /api/v1/projects/{project_id}/outline/generate
GET    /api/v1/projects/{project_id}/outline
POST   /api/v1/projects/{project_id}/outline/{chapter_id}/confirm
GET    /api/v1/projects/{project_id}/model-spec
PUT    /api/v1/projects/{project_id}/model-spec
```

### 2.6 论文草稿

```
GET  /api/v1/projects/{project_id}/drafts
GET  /api/v1/projects/{project_id}/drafts/{chapter_id}
PUT  /api/v1/projects/{project_id}/drafts/{chapter_id}
POST /api/v1/projects/{project_id}/drafts/{chapter_id}/confirm
POST /api/v1/projects/{project_id}/drafts/{chapter_id}/unlock
```

### 2.7 Agent

```
GET /api/v1/agents
GET /api/v1/agents/{agent_id}/details
POST /api/v1/agents/{agent_id}/pause
POST /api/v1/agents/{agent_id}/resume
PUT /api/v1/agents/{agent_id}/provider
```

### 2.8 HITL

```
GET  /api/v1/workflows/{workflow_id}/hitl-gates
POST /api/v1/hitl/{gate_id}/confirm
POST /api/v1/hitl/{gate_id}/reject
```

### 2.9 产物 Provenance

```
GET /api/v1/artifacts/{artifact_id}/provenance
```

---

## 3. 请求/响应详细契约

### 3.1 GET /api/v1/projects/{project_id}/overview

**用途**：研究总览页数据

**200 OK**

```json
{
  "_meta": {
    "evidence_level": "mock",
    "generated_at": "2026-05-10T12:00:00Z"
  },
  "project_id": "proj_robot_labor_match",
  "research_question": {
    "question": "工业机器人应用对劳动力市场匹配效率的影响",
    "hypothesis": "机器人密度提升会提高工资但降低职业流动性",
    "keywords": ["工业机器人", "劳动力市场", "匹配效率", "Bartik IV"]
  },
  "journey_status": {
    "current_stage": "modeling",
    "overall_progress": 0.42,
    "stages": [
      {
        "id": "data",
        "name": "数据",
        "status": "completed",
        "progress": 1.0
      },
      {
        "id": "variables",
        "name": "变量",
        "status": "completed",
        "progress": 1.0
      },
      {
        "id": "identification",
        "name": "识别",
        "status": "completed",
        "progress": 1.0
      },
      {
        "id": "modeling",
        "name": "模型",
        "status": "in_progress",
        "progress": 0.65
      },
      {
        "id": "robustness",
        "name": "稳健性",
        "status": "not_started",
        "progress": 0.0
      },
      {
        "id": "figures",
        "name": "图表",
        "status": "not_started",
        "progress": 0.0
      },
      {
        "id": "manuscript",
        "name": "正文",
        "status": "not_started",
        "progress": 0.0
      },
      {
        "id": "review",
        "name": "审阅",
        "status": "not_started",
        "progress": 0.0
      },
      {
        "id": "export",
        "name": "导出",
        "status": "not_started",
        "progress": 0.0
      }
    ]
  },
  "stage_summaries": [
    {
      "stage_id": "data",
      "stage_name": "数据与变量",
      "status": "completed",
      "metrics": [
        { "label": "数据集", "value": "3" },
        { "label": "变量数", "value": "47" },
        { "label": "样本量", "value": "15,230" }
      ],
      "next_step_hint": "数据准备完成，进入研究设计",
      "has_pending_action": false
    },
    {
      "stage_id": "design",
      "stage_name": "研究设计",
      "status": "completed",
      "metrics": [
        { "label": "识别策略", "value": "Bartik IV" },
        { "label": "因变量", "value": "ln_wage" },
        { "label": "控制变量", "value": "12" }
      ],
      "next_step_hint": "研究设计已确认，开始实证执行",
      "has_pending_action": false
    },
    {
      "stage_id": "execution",
      "stage_name": "实证执行",
      "status": "in_progress",
      "metrics": [
        { "label": "已完成", "value": "12/18" },
        { "label": "运行中", "value": "2" },
        { "label": "核心系数", "value": "0.1995**" }
      ],
      "next_step_hint": "Baseline 模型运行中",
      "has_pending_action": false
    },
    {
      "stage_id": "draft",
      "stage_name": "论文草稿",
      "status": "not_started",
      "metrics": [
        { "label": "章节", "value": "0/7" },
        { "label": "字数", "value": "0" }
      ],
      "next_step_hint": "等待实证执行完成后生成",
      "has_pending_action": false
    },
    {
      "stage_id": "artifacts",
      "stage_name": "产物与复现",
      "status": "not_started",
      "metrics": [
        { "label": "产物数", "value": "0" },
        { "label": "已审核", "value": "0" }
      ],
      "next_step_hint": "暂无产物",
      "has_pending_action": false
    },
    {
      "stage_id": "agents",
      "stage_name": "Agent 活动",
      "status": "in_progress",
      "metrics": [
        { "label": "活跃 Agent", "value": "3" },
        { "label": "最近事件", "value": "2分钟前" }
      ],
      "next_step_hint": "modeling_agent 正在执行 OLS baseline",
      "has_pending_action": false
    }
  ],
  "risks": [
    {
      "id": "risk_01",
      "level": "warning",
      "description": "弱工具变量风险：第一阶段 F 统计量需大于 10",
      "stage": "identification",
      "action_link": "/projects/{id}/design"
    }
  ],
  "next_steps": [
    {
      "id": "step_01",
      "priority": 1,
      "description": "确认 Baseline OLS 结果",
      "action": "确认模型结果",
      "action_link": "/projects/{id}/execution"
    }
  ],
  "recent_events": [
    {
      "id": "evt_01",
      "timestamp": "2026-05-10T11:58:00Z",
      "agent_name": "modeling_agent",
      "agent_role": "建模 Agent",
      "action": "完成 OLS baseline 估计",
      "result": "success",
      "duration_seconds": 45
    }
  ]
}
```

### 3.2 GET /api/v1/projects/{project_id}/journey

**用途**：旅程条专用（轻量，可被频繁调用）

**200 OK**

```json
{
  "_meta": {
    "evidence_level": "mock",
    "generated_at": "2026-05-10T12:00:00Z"
  },
  "project_id": "proj_robot_labor_match",
  "current_stage": "modeling",
  "overall_progress": 0.42,
  "stages": [
    { "id": "data", "name": "数据", "status": "completed", "progress": 1.0, "href": "#view-data-variables" },
    { "id": "variables", "name": "变量", "status": "completed", "progress": 1.0, "href": "#view-data-variables" },
    { "id": "identification", "name": "识别", "status": "completed", "progress": 1.0, "href": "#view-research-design" },
    { "id": "modeling", "name": "模型", "status": "in_progress", "progress": 0.65, "href": "#view-empirical-execution" },
    { "id": "robustness", "name": "稳健性", "status": "not_started", "progress": 0.0, "href": "#view-empirical-execution" },
    { "id": "figures", "name": "图表", "status": "not_started", "progress": 0.0, "href": "#view-paper-draft" },
    { "id": "manuscript", "name": "正文", "status": "not_started", "progress": 0.0, "href": "#view-paper-draft" },
    { "id": "review", "name": "审阅", "status": "not_started", "progress": 0.0, "href": "#view-paper-draft" },
    { "id": "export", "name": "导出", "status": "not_started", "progress": 0.0, "href": "#view-artifacts-replication" }
  ]
}
```

### 3.3 GET /api/v1/agents

**用途**：Agent 控制台 — Agent 列表

**200 OK**

```json
{
  "_meta": {
    "evidence_level": "mock",
    "generated_at": "2026-05-10T12:00:00Z"
  },
  "items": [
    {
      "id": "agent_preparation_01",
      "display_name": "准备 Agent",
      "role": "preparation_agent",
      "role_type": "pipeline",
      "status": "idle",
      "avatar": { "initial": "准", "color": "#1e6f62" },
      "capabilities": ["data_inspection", "variable_profiling", "codebook_generation"],
      "current_task": null,
      "total_cost": { "wall_seconds": 0, "invocation_count": 0 }
    },
    {
      "id": "agent_modeling_01",
      "display_name": "建模 Agent",
      "role": "modeling_agent",
      "role_type": "pipeline",
      "status": "active",
      "avatar": { "initial": "建", "color": "#a14a18" },
      "capabilities": ["ols_estimation", "iv_regression", "fixed_effects", "clustered_se"],
      "current_task": "OLS baseline 估计",
      "total_cost": { "wall_seconds": 320, "invocation_count": 8 }
    },
    {
      "id": "agent_literature_01",
      "display_name": "文献 Agent",
      "role": "literature_agent",
      "role_type": "dimension",
      "status": "idle",
      "avatar": { "initial": "文", "color": "#6b5b45" },
      "capabilities": ["zotero_search", "pdf_parsing", "citation_network"],
      "current_task": null,
      "total_cost": { "wall_seconds": 180, "invocation_count": 5 }
    }
  ]
}
```

### 3.4 GET /api/v1/agents/{agent_id}/details

**用途**：Agent 控制台 — Agent 详情

**200 OK**

```json
{
  "_meta": {
    "evidence_level": "mock",
    "generated_at": "2026-05-10T12:00:00Z"
  },
  "id": "agent_modeling_01",
  "display_name": "建模 Agent",
  "role": "modeling_agent",
  "role_type": "pipeline",
  "status": "active",
  "avatar": { "initial": "建", "color": "#a14a18" },
  "identity": {
    "id": "agent_modeling_01",
    "kind": "agent",
    "created_by": "user_owner_01",
    "created_at": "2026-05-08T00:00:00Z",
    "status": "active"
  },
  "permissions": {
    "allow": [
      "artifact.read",
      "artifact.write",
      "method.execute",
      "dataset.read"
    ],
    "deny": [
      "source.promote",
      "export.docx",
      "workflow.cancel"
    ]
  },
  "capabilities": [
    {
      "id": "cap_ols_estimation",
      "name": "OLS 估计",
      "source": "StatsPAI",
      "risk_level": "low",
      "cost_model": "local_cpu_time"
    },
    {
      "id": "cap_iv_regression",
      "name": "IV 回归",
      "source": "StatsPAI",
      "risk_level": "medium",
      "cost_model": "local_cpu_time"
    }
  ],
  "artifacts": [
    {
      "id": "artifact_baseline_001",
      "title": "Baseline OLS 结果",
      "kind": "markdown",
      "path": "docs/workflows/wf_001/baseline_ols.md",
      "created_at": "2026-05-10T11:00:00Z",
      "status": "draft"
    }
  ],
  "cost_summary": {
    "total_wall_seconds": 320,
    "total_invocations": 8,
    "by_capability": [
      { "capability_id": "cap_ols_estimation", "wall_seconds": 120, "invocations": 3 },
      { "capability_id": "cap_iv_regression", "wall_seconds": 200, "invocations": 5 }
    ]
  },
  "audit_log": [
    {
      "event_id": "evt_001",
      "timestamp": "2026-05-10T11:58:00Z",
      "action": "execute_capability",
      "capability_id": "cap_ols_estimation",
      "task_id": "task_001",
      "result": "success",
      "duration_seconds": 45
    }
  ]
}
```

### 3.5 GET /api/v1/artifacts/{artifact_id}/provenance

**用途**：产物溯源链

**200 OK**

```json
{
  "_meta": {
    "evidence_level": "mock",
    "generated_at": "2026-05-10T12:00:00Z"
  },
  "artifact_id": "artifact_baseline_001",
  "title": "Baseline OLS 结果",
  "lineage": [
    {
      "step": 1,
      "type": "data_source",
      "description": "原始数据集：CFPS 2010-2020",
      "source": "Data/Raw/cfps_panel.csv",
      "timestamp": "2026-05-08T00:00:00Z",
      "actor": "user_owner_01"
    },
    {
      "step": 2,
      "type": "cleaning",
      "description": "缺失值处理、异常值剔除",
      "source": "cleaning_log.jsonl",
      "timestamp": "2026-05-08T01:00:00Z",
      "actor": "agent_preparation_01"
    },
    {
      "step": 3,
      "type": "code_execution",
      "description": "OLS baseline 估计：ln_wage ~ robot_density + controls",
      "source": "Program/Analysis/baseline_ols.py",
      "timestamp": "2026-05-10T11:58:00Z",
      "actor": "agent_modeling_01",
      "capability_id": "cap_ols_estimation"
    },
    {
      "step": 4,
      "type": "output",
      "description": "回归结果 markdown 报告",
      "source": "docs/workflows/wf_001/baseline_ols.md",
      "timestamp": "2026-05-10T11:59:00Z",
      "actor": "agent_modeling_01"
    }
  ],
  "cost": {
    "wall_seconds": 45,
    "capability_id": "cap_ols_estimation",
    "actor": "agent_modeling_01"
  }
}
```

---

## 4. 错误码扩展

在现有错误码基础上新增：

| 错误码 | 说明 | HTTP 状态 |
|--------|------|----------|
| `dataset_not_found` | 数据集不存在 | 404 |
| `dataset_processing` | 数据集正在处理中 | 409 |
| `invalid_file_type` | 不支持的文件类型 | 400 |
| `strategy_not_found` | 识别策略不存在 | 404 |
| `dag_invalid` | DAG 结构无效 | 400 |
| `chapter_not_found` | 章节不存在 | 404 |
| `chapter_already_confirmed` | 章节已确认 | 409 |
| `agent_not_found` | Agent 不存在 | 404 |
| `hitl_gate_not_found` | HITL gate 不存在 | 404 |
| `hitl_gate_already_resolved` | HITL gate 已解决 | 409 |
| `provenance_not_available` | 溯源信息不可用 | 404 |

---

## 5. 与现有端点的关系

### 5.1 保留的现有端点

以下端点保持不变，继续工作：

```
GET    /api/v1/health
GET    /api/v1/projects
POST   /api/v1/projects
GET    /api/v1/projects/{project_id}
POST   /api/v1/projects/{project_id}/runs
GET    /api/v1/projects/{project_id}/runs
GET    /api/v1/projects/{project_id}/runs/{run_id}
POST   /api/v1/projects/{project_id}/export
POST   /api/v1/projects/{project_id}/orchestrate
```

### 5.2 扩展的现有端点

```
# Workflow 端点（已有，增加 HITL 相关数据）
GET /api/v1/workflows/{workflow_id}
# 响应增加：hitl_gates 字段

# Artifact 端点（已有，增加 provenance）
GET /api/v1/artifacts/{artifact_id}
# 响应增加：provenance 字段
```

### 5.3 废弃计划

以下旧版端点标记为 deprecated，但继续保留：

```
GET  /api/status           → 使用 /api/v1/health
GET  /api/projects         → 使用 /api/v1/projects
POST /api/projects/{slug}/run → 使用 /api/v1/projects/{id}/runs
```

---

## 6. 测试契约

### 6.1 必须验证的契约

```python
class TestAPIContractV2(unittest.TestCase):
    def test_overview_returns_all_stage_summaries(self):
        """overview 必须返回 6 个阶段摘要卡片"""
        pass

    def test_overview_journey_has_9_stages(self):
        """journey_status.stages 必须有 9 个阶段"""
        pass

    def test_journey_stages_have_required_fields(self):
        """每个阶段必须有 id, name, status, progress, href"""
        pass

    def test_agents_list_has_pipeline_and_dimension(self):
        """agents 列表必须包含 pipeline 和 dimension 两种 role_type"""
        pass

    def test_agent_details_has_identity_permissions_capabilities(self):
        """agent details 必须包含 identity, permissions, capabilities, artifacts, cost, audit_log"""
        pass

    def test_artifact_provenance_has_lineage(self):
        """provenance 必须有 lineage 数组，每步有 step, type, description, actor"""
        pass

    def test_all_mock_responses_have_meta(self):
        """所有 mock 数据必须有 _meta.evidence_level = 'mock'"""
        pass
```
