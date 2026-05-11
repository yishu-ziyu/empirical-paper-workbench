# 技术架构文档 v2 —— 研究旅程重塑

日期：2026-05-10
读者：Codex（后端实现）
来源：CoPaper 竞品调研 + 现有产品架构

---

## 1. 架构概览

### 1.1 核心变化

基于 CoPaper 调研，本次重塑将后端服务边界从"技术模块"重新组织为"研究流程阶段"：

| 旧边界 | 新边界 | 说明 |
|--------|--------|------|
| Workflow Service（通用） | workflow_service + execution_adapter + hitl_service | 拆分任务编排、执行适配、人机确认 |
| Project Service（通用） | project_service + dataset_service + design_service | 拆分项目管理、数据管理、设计管理 |
| Agent Cluster（前端 mock） | agent_registry + supervisor + pipeline_agents | 真正的 Agent 治理和编排 |
| Artifacts（通用） | artifact_service + ownership_service + draft_service | 拆分产物管理、归属、草稿 |

### 1.2 7 层架构（更新版）

```
┌─────────────────────────────────────────────────────────────────┐
│ Product UI Layer                                                │
│   研究总览、数据与变量、研究设计、实证执行、论文草稿、产物复现、Agent 控制台 │
├─────────────────────────────────────────────────────────────────┤
│ API and Workflow Layer                                          │
│   FastAPI routes, project_service, dataset_service,             │
│   design_service, workflow_service, execution_adapter,          │
│   draft_service, artifact_service, export_service,              │
│   observability_service, hitl_service                           │
├─────────────────────────────────────────────────────────────────┤
│ Governance Layer                                                │
│   identity_service, permission_service, capability_registry,    │
│   ownership_service, cost_service                               │
├─────────────────────────────────────────────────────────────────┤
│ Agent Orchestration Layer                                       │
│   supervisor, pipeline_agents, dimension_agents,                │
│   task_state_machine, hitl_gate                                 │
├─────────────────────────────────────────────────────────────────┤
│ Skill Registry Layer                                            │
│   skill_registry_adapter, awesome_skills_index,                 │
│   skill_classification                                          │
├─────────────────────────────────────────────────────────────────┤
│ Method Engine Layer                                             │
│   statspai_adapter, local_codex_adapter, stata_adapter,         │
│   r_adapter                                                     │
├─────────────────────────────────────────────────────────────────┤
│ Source Registry Layer                                           │
│   zotero_integration, pdf_library, dataset_registry,            │
│   source_metadata                                               │
├─────────────────────────────────────────────────────────────────┤
│ Workspace and Artifact Layer                                    │
│   Data/, Program/, Results/, Manuscripts/, Submissions/,        │
│   docs/workflows/, Product/state/                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. 新增服务详细设计

### 2.1 dataset_service（数据集管理）

**职责**：
- 数据集上传、存储、版本快照
- Schema 自动识别（CSV/Excel/Stata/JSON/Parquet）
- Sheet 检测（Excel 多 sheet）
- 变量类型推断（数值/分类/日期/文本）

**模块**：
```
Product/backend/dataset_service.py      # 业务逻辑
Product/backend/dataset_schema.py       # Pydantic schemas
Product/backend/dataset_store.py        # JSON 文件存储
```

**状态文件**：
```
Product/state/datasets/
  ├── index.json                        # 数据集索引
  └── {dataset_id}/
      ├── metadata.json                 # 数据集元数据
      ├── schema.json                   # 变量 schema
      ├── snapshot.csv                  # 数据快照（样本）
      └── versions.json                 # 版本历史
```

**核心 Schema**：
```python
class DatasetMetadata(BaseModel):
    id: str
    project_id: str
    name: str
    file_type: Literal["csv", "excel", "stata", "json", "parquet"]
    row_count: int
    column_count: int
    file_size_bytes: int
    sheets: list[str] | None          # Excel 多 sheet
    uploaded_at: datetime
    uploaded_by: str                  # user_id or agent_id
    status: Literal["uploading", "processing", "ready", "error"]

class VariableSchema(BaseModel):
    name: str
    type: Literal["numeric", "categorical", "datetime", "text", "unknown"]
    missing_count: int
    missing_rate: float              # 0-1
    stats: dict                      # 数值: min/max/mean/std；分类: top_values
    sample_values: list              # 前 5 个非空样本值
```

**关键接口**：
```python
class DatasetService:
    def create_dataset(self, project_id: str, file_path: str, uploaded_by: str) -> DatasetMetadata: ...
    def get_schema(self, dataset_id: str) -> list[VariableSchema]: ...
    def inspect_sheets(self, file_path: str) -> list[str]: ...           # Excel 专用
    def get_snapshot(self, dataset_id: str, max_rows: int = 100) -> list[dict]: ...
    def update_variable_type(self, dataset_id: str, variable_name: str, new_type: str) -> VariableSchema: ...
```

**API 端点**：
```
POST   /api/v1/projects/{project_id}/datasets              # 上传数据集
GET    /api/v1/projects/{project_id}/datasets              # 列出数据集
GET    /api/v1/datasets/{dataset_id}                       # 获取数据集元数据
GET    /api/v1/datasets/{dataset_id}/schema                # 获取变量 schema
GET    /api/v1/datasets/{dataset_id}/snapshot              # 获取数据快照
POST   /api/v1/datasets/{dataset_id}/sheets/inspect        # 检测 Excel sheets
PUT    /api/v1/datasets/{dataset_id}/variables/{name}      # 更新变量类型
DELETE /api/v1/datasets/{dataset_id}                       # 删除数据集
```

---

### 2.2 cleaning_service（数据清洗与变量定义）

**职责**：
- 变量角色分配（因变量、自变量、控制变量、工具变量、固定效应）
- Codebook 生成和管理
- 清洗操作日志
- 数据质量报告

**模块**：
```
Product/backend/cleaning_service.py
Product/backend/cleaning_schema.py
```

**状态文件**：
```
Product/state/cleaning/
  └── {project_id}/
      ├── variable_assignments.json       # 变量角色分配
      ├── codebook.json                   # 变量定义手册
      ├── cleaning_log.jsonl              # 清洗操作日志（追加）
      └── quality_report.json             # 数据质量报告
```

**核心 Schema**：
```python
class VariableAssignment(BaseModel):
    dataset_id: str
    variable_name: str
    role: Literal["dependent", "independent", "control", "instrument", "fixed_effect", "unused"]
    definition: str                       # 中文定义
    economic_meaning: str | None          # 计量经济学含义
    assigned_by: str                      # user_id or agent_id
    assigned_at: datetime

class CodebookEntry(BaseModel):
    variable_name: str
    dataset_id: str
    definition: str
    type: str
    role: str
    value_labels: dict | None             # 分类变量的值标签
    notes: str | None

class CleaningLogEntry(BaseModel):
    event_id: str
    project_id: str
    dataset_id: str
    operation: str                        # "remove_outliers", "impute_missing", ...
    parameters: dict                      # 操作参数
    affected_rows: int
    affected_columns: list[str]
    performed_by: str
    performed_at: datetime
    reason: str                           # 为什么做这个操作
```

**关键接口**：
```python
class CleaningService:
    def assign_variable_role(self, project_id: str, assignment: VariableAssignment) -> VariableAssignment: ...
    def get_codebook(self, project_id: str) -> list[CodebookEntry]: ...
    def update_codebook(self, project_id: str, entry: CodebookEntry) -> CodebookEntry: ...
    def log_cleaning_operation(self, entry: CleaningLogEntry) -> None: ...
    def get_cleaning_log(self, project_id: str, dataset_id: str | None = None) -> list[CleaningLogEntry]: ...
    def generate_quality_report(self, project_id: str) -> dict: ...
```

**API 端点**：
```
POST   /api/v1/projects/{project_id}/variables/assign      # 分配变量角色
GET    /api/v1/projects/{project_id}/codebook              # 获取 codebook
PUT    /api/v1/projects/{project_id}/codebook/{var_name}   # 更新 codebook 条目
GET    /api/v1/projects/{project_id}/cleaning-log          # 获取清洗日志
POST   /api/v1/projects/{project_id}/cleaning-log          # 记录清洗操作
GET    /api/v1/projects/{project_id}/quality-report        # 获取质量报告
```

---

### 2.3 design_service（研究设计）

**职责**：
- 研究问题管理
- 识别策略推荐和选择
- DAG（有向无环图）表示
- Paper outline 生成和确认
- 模型设定管理

**模块**：
```
Product/backend/design_service.py
Product/backend/design_schema.py
```

**状态文件**：
```
Product/state/design/
  └── {project_id}/
      ├── research_question.json          # 研究问题
      ├── identification_strategy.json    # 识别策略
      ├── dag.json                        # DAG 表示
      ├── model_specification.json        # 模型设定
      └── outline.json                    # Paper outline
```

**核心 Schema**：
```python
class ResearchQuestion(BaseModel):
    question: str
    hypothesis: str | None
    keywords: list[str]
    updated_by: str
    updated_at: datetime

class IdentificationStrategy(BaseModel):
    method: Literal["ols", "did", "iv", "rd", "psm", "dml", "other"]
    method_name: str                      # 如 "Bartik IV"
    suitability_score: int                # 1-10
    rationale: str                        # 推荐理由
    key_assumptions: list[str]            # 关键假设清单
    assumption_tests: list[dict]          # 假设检验方法
    selected_by: str
    selected_at: datetime
    status: Literal["recommended", "selected", "confirmed"]

class DAGNode(BaseModel):
    id: str
    label: str                            # 变量名
    type: Literal["outcome", "treatment", "control", "unobserved"]
    x: float                              # 布局坐标
    y: float

class DAGEdge(BaseModel):
    from_node: str
    to_node: str
    type: Literal["causal", "confounding", "collider"]

class PaperOutline(BaseModel):
    chapters: list[Chapter]
    confirmed: bool
    generated_by: str
    generated_at: datetime

class Chapter(BaseModel):
    id: str
    number: int
    title: str
    subsections: list[Subsection]
    status: Literal["draft", "confirmed", "modified"]
    confirmed_by: str | None
    confirmed_at: datetime | None

class Subsection(BaseModel):
    id: str
    number: str                           # 如 "1.1"
    title: str
    content_guidance: str | None          # AI 生成的内容指导
```

**关键接口**：
```python
class DesignService:
    def set_research_question(self, project_id: str, question: str, by: str) -> ResearchQuestion: ...
    def recommend_strategies(self, project_id: str) -> list[IdentificationStrategy]: ...
    def select_strategy(self, project_id: str, method: str, by: str) -> IdentificationStrategy: ...
    def confirm_strategy(self, project_id: str, by: str) -> IdentificationStrategy: ...
    def get_dag(self, project_id: str) -> tuple[list[DAGNode], list[DAGEdge]]: ...
    def update_dag(self, project_id: str, nodes: list[DAGNode], edges: list[DAGEdge], by: str) -> None: ...
    def generate_outline(self, project_id: str, by: str) -> PaperOutline: ...
    def confirm_chapter(self, project_id: str, chapter_id: str, by: str) -> Chapter: ...
    def get_model_specification(self, project_id: str) -> dict: ...
    def update_model_specification(self, project_id: str, spec: dict, by: str) -> dict: ...
```

**API 端点**：
```
PUT    /api/v1/projects/{project_id}/research-question     # 设置研究问题
GET    /api/v1/projects/{project_id}/strategies            # 获取推荐策略
POST   /api/v1/projects/{project_id}/strategies/select     # 选择策略
POST   /api/v1/projects/{project_id}/strategies/confirm    # 确认策略
GET    /api/v1/projects/{project_id}/dag                   # 获取 DAG
PUT    /api/v1/projects/{project_id}/dag                   # 更新 DAG
POST   /api/v1/projects/{project_id}/outline/generate      # 生成 outline
GET    /api/v1/projects/{project_id}/outline               # 获取 outline
POST   /api/v1/projects/{project_id}/outline/{ch_id}/confirm # 确认章节
GET    /api/v1/projects/{project_id}/model-spec            # 获取模型设定
PUT    /api/v1/projects/{project_id}/model-spec            # 更新模型设定
```

---

### 2.4 execution_adapter（执行适配器）

**职责**：
- 统一执行入口，路由到不同执行后端
- 管理执行会话
- 收集执行结果和日志
- 错误隔离（失败不整体崩溃）

**模块**：
```
Product/backend/execution_adapter.py
Product/backend/execution_schema.py
Product/backend/adapters/
  ├── codex_adapter.py                  # Local Codex 适配
  ├── statspai_adapter.py               # StatsPAI 适配（已有，扩展）
  ├── stata_adapter.py                  # Stata 适配
  └── r_adapter.py                      # R 适配（预留）
```

**核心 Schema**：
```python
class ExecutionRequest(BaseModel):
    task_id: str
    workflow_id: str
    project_id: str
    capability_id: str
    provider: Literal["local-codex", "statspai", "stata", "r"]
    code: str | None                      # 直接传入代码
    data_path: str | None                 # 数据路径
    parameters: dict                      # 执行参数
    timeout_seconds: int = 300

class ExecutionResult(BaseModel):
    task_id: str
    status: Literal["succeeded", "failed", "timeout", "cancelled"]
    stdout: str
    stderr: str
    exit_code: int | None
    artifacts: list[str]                  # 生成的文件路径
    result_object: dict | None            # 结构化结果（如回归表 JSON）
    wall_time_seconds: float
    error_note: str | None                # 失败时的恢复建议

class ExecutionLog(BaseModel):
    event_id: str
    task_id: str
    timestamp: datetime
    level: Literal["info", "warning", "error"]
    message: str
    code_snippet: str | None
```

**关键接口**：
```python
class ExecutionAdapter:
    def execute(self, request: ExecutionRequest) -> ExecutionResult: ...
    def cancel(self, task_id: str) -> bool: ...
    def get_log(self, task_id: str) -> list[ExecutionLog]: ...
    def get_result(self, task_id: str) -> ExecutionResult | None: ...
```

**适配器注册**：
```python
ADAPTERS: dict[str, Callable] = {
    "local-codex": CodexAdapter(),
    "statspai": StatsPAIAdapter(),
    "stata": StataAdapter(),
    "r": RAdapter(),
}
```

**API 端点**：
```
POST   /api/v1/workflows/{wf_id}/tasks/{task_id}/execute   # 执行任务
POST   /api/v1/workflows/{wf_id}/tasks/{task_id}/cancel    # 取消任务
GET    /api/v1/workflows/{wf_id}/tasks/{task_id}/log       # 获取执行日志
GET    /api/v1/workflows/{wf_id}/tasks/{task_id}/result    # 获取执行结果
```

---

### 2.5 draft_service（论文草稿）

**职责**：
- 章节管理（CRUD）
- Markdown 内容存储和版本
- 章节确认/解锁
- 引用管理

**模块**：
```
Product/backend/draft_service.py
Product/backend/draft_schema.py
```

**状态文件**：
```
Product/state/drafts/
  └── {project_id}/
      ├── manifest.json                   # 章节清单
      └── chapters/
          ├── {chapter_id}.md             # 章节内容
          └── {chapter_id}.versions.json  # 版本历史
```

**核心 Schema**：
```python
class DraftChapter(BaseModel):
    id: str
    number: int
    title: str
    status: Literal["draft", "confirmed", "modified"]
    word_count: int
    content: str                          # Markdown
    confirmed_by: str | None
    confirmed_at: datetime | None
    modified_at: datetime
    modified_by: str

class DraftManifest(BaseModel):
    project_id: str
    chapters: list[DraftChapter]
    total_word_count: int
    confirmed_chapters: int
```

**API 端点**：
```
GET    /api/v1/projects/{project_id}/drafts                # 获取草稿清单
GET    /api/v1/projects/{project_id}/drafts/{ch_id}        # 获取章节内容
PUT    /api/v1/projects/{project_id}/drafts/{ch_id}        # 更新章节内容
POST   /api/v1/projects/{project_id}/drafts/{ch_id}/confirm # 确认章节
POST   /api/v1/projects/{project_id}/drafts/{ch_id}/unlock  # 解锁章节
```

---

### 2.6 hitl_service（人机确认门）

**职责**：
- 管理 HITL gate 的生命周期
- 暂停/恢复 workflow
- 记录用户决策
- 超时处理

**模块**：
```
Product/backend/hitl_service.py
Product/backend/hitl_schema.py
```

**状态文件**：
```
Product/state/hitl/
  └── gates.json                        # 当前活跃的 gates
  └── history.jsonl                     # 历史决策记录
```

**核心 Schema**：
```python
class HITLGate(BaseModel):
    id: str
    workflow_id: str
    task_id: str
    stage: str                            # 哪个阶段暂停
    reason: str                           # 暂停原因
    details: str                          # 详细说明
    suggested_action: str | None
    status: Literal["pending", "confirmed", "rejected", "timeout"]
    created_at: datetime
    timeout_at: datetime
    resolved_at: datetime | None
    resolved_by: str | None
    resolution_note: str | None

class HITLDecision(BaseModel):
    gate_id: str
    decision: Literal["confirm", "reject"]
    note: str | None                      # 拒绝时的修改建议
    made_by: str
    made_at: datetime
```

**API 端点**：
```
GET    /api/v1/workflows/{wf_id}/hitl-gates                # 获取当前 gates
POST   /api/v1/hitl/{gate_id}/confirm                      # 确认继续
POST   /api/v1/hitl/{gate_id}/reject                       # 拒绝并修改
```

---

### 2.7 observability_service（可观测性）

**职责**：
- 错误收集和聚类
- 日志查询
- 质量门禁
- 指标聚合

**模块**：
```
Product/backend/observability_service.py
Product/backend/observability_schema.py
```

**API 端点**：
```
GET    /api/v1/errors                                      # 错误列表
GET    /api/v1/errors/{error_id}                           # 错误详情
POST   /api/v1/errors/{error_id}/resolve                   # 解决错误
GET    /api/v1/observability/metrics                       # 系统指标
GET    /api/v1/observability/logs                          # 日志查询
```

---

## 3. 数据模型关系图

```
Project (1)
├── Dataset (N)
│   ├── VariableSchema (N)
│   └── CleaningLogEntry (N)
├── VariableAssignment (N)
├── CodebookEntry (N)
├── ResearchQuestion (1)
├── IdentificationStrategy (1)
├── DAG: Node(N) + Edge(N)
├── ModelSpecification (1)
├── PaperOutline: Chapter(N) + Subsection(N)
├── DraftChapter (N)
├── Workflow (N)
│   ├── Task (N)
│   │   ├── ExecutionResult (1)
│   │   ├── ExecutionLog (N)
│   │   └── HITLGate (0-1)
│   └── Artifact (N)
│       └── OwnershipRecord (1)
├── AgentIdentity (N)
│   ├── PermissionPolicy (1)
│   ├── CapabilityAssignment (N)
│   └── CostEvent (N)
└── CostSummary (1)
```

---

## 4. Agent 编排架构

### 4.1 Supervisor

**职责**：
- 接收用户研究目标
- 制定执行计划（plan）
- 分配任务给 Pipeline Roles 和 Dimension Agents
- 监控任务状态
- 触发 HITL gate
- 处理失败恢复

**状态机**：
```
planning → dispatching → running → hitl_pending → reviewing → completed
    ↓           ↓           ↓           ↓            ↓
  failed      failed      failed      timeout      failed
```

### 4.2 Pipeline Roles（流水线角色）

| 角色 | 职责 | 对应页面阶段 |
|------|------|-------------|
| preparation_agent | 数据准备、变量定义、codebook | 数据与变量 |
| modeling_agent | baseline、robustness、mechanism | 实证执行 |
| visualization_agent | 图表、回归表、描述统计 | 实证执行 / 论文草稿 |
| writing_agent | 论文正文、引用、格式 | 论文草稿 |
| review_agent | 审阅、批注、修改建议 | 论文草稿 / 审阅 |
| export_agent | DOCX、LaTeX、复现包 | 产物与复现 |

### 4.3 Research Dimension Agents（研究维度代理）

保持现有 10 个 Agent 不变，但明确它们在 pipeline 中的调用时机：

| Agent | 调用时机 | 产出 |
|-------|---------|------|
| literature_agent | preparation 阶段 | 文献综述笔记 |
| data_agent | preparation 阶段 | 数据质量报告 |
| variable_agent | preparation 阶段 | 变量关系分析 |
| identification_agent | modeling 阶段 | 识别策略设计 |
| robustness_agent | modeling 阶段 | 稳健性检验方案 |
| mechanism_agent | modeling 阶段 | 机制分析结果 |
| heterogeneity_agent | modeling 阶段 | 异质性分析结果 |
| figure_agent | visualization 阶段 | 图表产物 |
| manuscript_agent | writing 阶段 | 章节草稿 |
| reviewer_agent | review 阶段 | 审阅批注 |

### 4.4 任务路由规则

```python
ROUTING_RULES = {
    "data_preparation": ["preparation_agent", "literature_agent", "data_agent", "variable_agent"],
    "modeling": ["modeling_agent", "identification_agent", "robustness_agent", "mechanism_agent", "heterogeneity_agent"],
    "visualization": ["visualization_agent", "figure_agent"],
    "writing": ["writing_agent", "manuscript_agent"],
    "review": ["review_agent", "reviewer_agent"],
    "export": ["export_agent"],
}
```

---

## 5. 与现有系统的集成

### 5.1 保持不变的模块

| 模块 | 说明 |
|------|------|
| `Product/app.py` 现有路由 | 全部保留，新增路由通过 `/api/v2/` 或扩展 `/api/v1/` |
| `Product/backend/project_service.py` | 保留，project 概念不变 |
| `Product/backend/run_store.py` | 保留，run 概念映射到 workflow |
| `Program/run_paper.py` | 保留，作为 execution_adapter 的 local-codex 后端 |
| `Program/export_docx.py` | 保留，作为 export_service 的后端 |
| `paper.yaml` | 保留，项目定义不变 |

### 5.2 扩展现有的模块

| 现有模块 | 扩展内容 |
|---------|---------|
| `workflow_service.py` | 增加 HITL gate 集成、task 路由逻辑 |
| `artifact_service.py` | 增加 provenance 溯源链、draft 类型产物 |
| `orchestrator.py` | 重构为 supervisor，增加 plan/dispatch 逻辑 |
| `statspai_runner.py` | 包装为 statspai_adapter |

### 5.3 数据兼容策略

- 新增状态目录 `Product/state/datasets/`, `Product/state/cleaning/`, `Product/state/design/`, `Product/state/drafts/`, `Product/state/hitl/`
- 现有 `Product/state/workflows/` 保持不变，新增字段可选
- 现有 `state/project_state.json` 继续由 `run_paper.py` 写入
- 新增服务读取 `project_state.json` 作为 fallback 数据源

---

## 6. Phase A 实现范围（信息架构重塑）

### 6.1 目标

先不大改后端逻辑，新增支持前端新页面的 API 端点和 mock 数据。

### 6.2 新增端点（Phase A）

| 端点 | 用途 | 实现方式 |
|------|------|---------|
| `GET /api/v1/projects/{id}/overview` | 研究总览数据 | 聚合 project + workflow + artifact 状态 |
| `GET /api/v1/projects/{id}/journey` | 旅程条状态 | 从 workflow 状态推导 |
| `GET /api/v1/projects/{id}/datasets` | 数据集列表 | Mock（空列表 + schema） |
| `GET /api/v1/datasets/{id}/schema` | 变量 schema | Mock |
| `GET /api/v1/projects/{id}/design` | 研究设计状态 | Mock |
| `GET /api/v1/projects/{id}/drafts` | 草稿清单 | 读取 Manuscripts/generated/ |
| `GET /api/v1/agents` | Agent 列表 | Mock（10 个 dimension agents + 6 pipeline agents） |
| `GET /api/v1/agents/{id}/details` | Agent 详情 | Mock（身份、权限、能力、成本、产物、日志） |

### 6.3 Mock 数据规范

所有 mock 数据必须包含：
```json
{
  "_meta": {
    "evidence_level": "mock",
    "generated_at": "2026-05-10T00:00:00+08:00",
    "note": "This is mock data for UI development"
  }
}
```

### 6.4 新增后端文件（Phase A）

```
Product/backend/
  ├── overview_service.py           # 研究总览数据聚合
  ├── overview_schema.py            # 总览相关 schema
  ├── mock_data_generator.py        # Mock 数据生成器
  └── dataset_service.py            # 数据集服务（mock 实现）
```

---

## 7. 安全与治理

### 7.1 权限检查点

每个新增端点必须检查：
```python
async def endpoint(project_id: str, request: Request):
    # 1. 身份验证（Phase A 可跳过）
    # user = await authenticate(request)
    
    # 2. 权限检查（Phase A 可跳过）
    # if not check_permission(user.id, f"project.{project_id}.read"):
    #     raise PermissionDenied()
    
    # 3. 项目存在性检查
    project = project_service.get(project_id)
    if not project:
        raise ProjectNotFound()
    
    # 4. 执行操作
    ...
```

### 7.2 输入验证

- 所有请求体使用 Pydantic schema 验证
- 文件路径参数必须校验在白名单内
- 字符串长度限制（防止 DoS）

### 7.3 错误处理

统一错误格式（与现有 API 契约一致）：
```json
{
  "error": {
    "code": "dataset_not_found",
    "message": "Dataset ds_xxx does not exist.",
    "details": {}
  }
}
```

---

## 8. 测试策略

### 8.1 单元测试

每个 service 模块配套测试：
```
tests/backend/test_overview_service.py
tests/backend/test_dataset_service.py
tests/backend/test_design_service.py
...
```

### 8.2 集成测试

扩展现有 `tests/test_product_api_integration.py`：
```python
class TestNewEndpoints(unittest.TestCase):
    def test_overview_returns_journey_stages(self): ...
    def test_agents_list_returns_mock_data(self): ...
    def test_datasets_list_returns_empty_with_meta(self): ...
```

### 8.3 契约测试

验证前端期望的数据结构：
```python
class TestAPIContracts(unittest.TestCase):
    def test_overview_response_has_all_stage_summaries(self): ...
    def test_agent_details_has_required_fields(self): ...
```

---

## 9. 文件清单

### 新建文件

| 文件 | 说明 | 优先级 |
|------|------|--------|
| `Product/backend/overview_service.py` | 研究总览数据聚合 | P0 |
| `Product/backend/overview_schema.py` | 总览 schema | P0 |
| `Product/backend/mock_data_generator.py` | Mock 数据生成 | P0 |
| `Product/backend/dataset_service.py` | 数据集服务 | P1 |
| `Product/backend/dataset_schema.py` | 数据集 schema | P1 |
| `Product/backend/cleaning_service.py` | 清洗服务 | P2 |
| `Product/backend/design_service.py` | 设计服务 | P2 |
| `Product/backend/draft_service.py` | 草稿服务 | P2 |
| `Product/backend/hitl_service.py` | HITL 服务 | P2 |
| `Product/backend/execution_adapter.py` | 执行适配 | P3 |

### 修改文件

| 文件 | 修改内容 | 优先级 |
|------|---------|--------|
| `Product/app.py` | 注册新路由 | P0 |
| `Product/backend/workflow_service.py` | 增加 HITL 集成 | P2 |
| `Product/backend/artifact_service.py` | 增加 provenance | P2 |

---

## 10. 实现顺序建议

### Week 1：Phase A 骨架
1. `mock_data_generator.py` — 生成一致的 mock 数据
2. `overview_service.py` + `overview_schema.py` — 研究总览 API
3. `app.py` — 注册新路由
4. 集成测试 — 验证契约

### Week 2：服务填充
5. `dataset_service.py` — 数据集管理（mock）
6. `design_service.py` — 研究设计（mock）
7. `draft_service.py` — 论文草稿（连接真实文件）

### Week 3：Agent 治理
8. Agent 注册表 + mock Agent 数据
9. `hitl_service.py` — 人机确认门

### Week 4：执行接入
10. `execution_adapter.py` — 连接真实执行后端
11. 与 `run_paper.py` 集成测试
