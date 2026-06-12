# API 地图

本文档记录当前后端已经存在的主要入口、处理文件和状态触点。目标是让后续接入 SupervisorPlan、Agent Task Queue、真实执行、Verifier 和导出时，不再靠前端猜接口。

## 1. 总入口

主应用入口是 `Product/app.py`。它同时承担静态产品壳、React 构建产物、核心 `/api/v1` 接口和部分 legacy alias。当前开发时必须先确认真正运行的是 `Product/app.py`，而不是旧的静态服务或其他端口。`demo_server.py` 只是启动器。

## 2. `/api` wrapper flow

`/api/*` 主要服务 React 阶段面板，适合快速完成“题目 -> brief -> search -> variables -> design -> execute -> audit”的本地工作流。它不是完整产品状态层。

| Method | Exact path | Handler | File | State touched |
| --- | --- | --- | --- | --- |
| POST | `POST /api/brief` | `post_brief` | `Product/api/brief.py` | `Tasks/{topic_slug}/brief.md` |
| POST | `POST /api/brief/stream` | `post_brief_stream` | `Product/api/brief_stream.py` | streamed brief payload |
| POST | `POST /api/brief/stream/resume` | `post_brief_stream_resume` | `Product/api/brief_stream.py` | resumed brief stream |
| POST | `POST /api/supervisor/plan` | `post_supervisor_plan` | `Product/api/supervisor.py` | brief-tab supervisor preview |
| POST | `POST /api/search` | `post_search` | `Product/api/search.py` | `Tasks/{topic_slug}/literature.md` |
| POST | `POST /api/variables` | `post_variables` | `Product/api/variables.py` | `Tasks/{topic_slug}/variables.yaml` |
| POST | `POST /api/design` | `post_design` | `Product/api/design.py` | `Tasks/{topic_slug}/design.json` |
| POST | `POST /api/execute` | `post_execute` | `Product/api/execute.py` | `Manuscripts/{topic_slug}/sections/section_*.md`, `Manuscripts/{topic_slug}/paper.pdf`, `Results/{topic_slug}/results.json` |
| POST | `POST /api/identification/audit` | `post_identification_audit` | `Product/api/identification.py` | design/results audit output |
| GET | `GET /api/capabilities/methods` | `get_capabilities_methods` | `Product/api/capabilities.py` | capability list |
| POST | `POST /api/system/status` | `post_system_status` | `Product/api/system.py` | state/product, runs, cost, capability, artifact aggregate |
| POST | `POST /api/auto-research/start` | `post_auto_research_start` | `Product/api/auto_research.py` | exploratory research run artifacts |

## 3. `/api/v1` product-state flow

`/api/v1/*` 是产品状态层接口，围绕项目、canonical state、runs、Agent Task Queue、导出、权限和成本展开。后续正式产品功能优先挂到这里。

| Method | Exact path | Handler | State touched |
| --- | --- | --- | --- |
| GET | `GET /api/status` | `api_status` | app status |
| GET | `GET /api/v1/health` | `api_v1_health` | health status |
| GET | `GET /api/v1/providers/local-codex` | `api_v1_local_codex_provider` | local provider status |
| GET | `GET /api/v1/providers/llm-supervisor` | `api_v1_llm_supervisor_provider` | LLM Supervisor provider status |
| POST | `POST /api/v1/providers/llm-supervisor/probe` | `api_v1_llm_supervisor_probe` | provider probe result |
| POST | `POST /api/v1/topic-intake/supervisor-plan` | `api_v1_topic_intake_supervisor_plan` | `state/product/research_question.json`, `state/product/supervisor_plan.json` |
| POST | `POST /api/v1/topic-intake/supervisor-plan/preview` | `api_v1_topic_intake_preview_supervisor_plan` | preview plan payload |
| GET | `GET /api/v1/projects/{project_id}/overview` | project overview handler in `Product/app.py` | project overview |
| GET | `GET /api/v1/projects/{project_id}/journey` | project journey handler in `Product/app.py` | project journey |
| GET|PUT | `GET|PUT /api/v1/projects/{project_id}/research-question/current` | current question handlers in `Product/app.py` | `state/product/research_question.json` |
| GET|PUT | `GET|PUT /api/v1/projects/{project_id}/variable-roles` | variable role handlers in `Product/app.py` | `state/product/variable_roles.json` |
| GET|PUT | `GET|PUT /api/v1/projects/{project_id}/design-spec` | design spec handlers in `Product/app.py` | `state/product/design_spec.json` |
| GET|PUT | `GET|PUT /api/v1/projects/{project_id}/run-plan` | run plan handlers in `Product/app.py` | `state/product/run_plan.json` |
| GET|POST|PUT | supervisor plan endpoints under `/api/v1/projects/{project_id}/supervisor-plan` | supervisor plan handlers in `Product/app.py` | `state/product/supervisor_plan.json`, `state/product/supervisor_plan.raw.md` |
| GET|POST | `GET|POST /api/v1/projects/{project_id}/agent-task-queue` | agent queue handlers in `Product/app.py` | `state/product/agent_task_queue.json` |
| POST | agent task action endpoints under `/api/v1/projects/{project_id}/agent-task-queue/tasks/{task_id}/...` | task action handlers in `Product/app.py` | dispatch review, skill packet, citation verification, section drafts, formal export, pdf candidate, writeback, backend selection |
| POST | `POST /api/v1/projects/{project_id}/runs` | `api_v1_create_run` | `state/runs/index.json`, run manifest/events |
| POST | `POST /api/v1/projects/{project_id}/runs/full` | `api_v1_create_full_run` | `state/runs/{run_id}/run_manifest.json`, `run_steps.json`, `run_events.jsonl`, `gates.json` |

## 4. 状态触点

API 不能只返回漂亮文本，必须读写可审计状态。当前主要状态路径如下：

- `Product/state`：项目和 workflow registry，如 `projects.json`、`workflows/{workflow_id}/workflow.json`、`tasks.json`、`artifacts.json`。
- `state/product`：产品级 canonical 状态，如 `research_question.json`、`variable_roles.json`、`design_spec.json`、`run_plan.json`、`supervisor_plan.json`、`supervisor_plan.raw.md`、`agent_task_queue.json`、`capabilities.json`、`export_package_manifest.json`、`verifier_checks.json`、`writeback_approvals.json`。
- `state/runs`：运行索引和每次 run 的 manifest、steps、events、gates。这里是可观察执行的核心。
- `Results/json`：方法执行结果、回归表、稳健性矩阵、样本画像、approved findings、verified literature、formal writeback、StatsPAI 执行结果等。
- `Manuscripts/generated`：草稿层论文、TeX、预览稿和生成文本。
- `Submissions`：正式导出 manifest、PDF、DOCX、复现包和提交材料。

后续任何 API 若产生用户可见结果，应至少写入一个状态对象，并返回该对象的路径或 id。否则前端会出现“看起来完成，但无法追溯”的状态。

## 5. 前端对接建议

前端应按页面读取最小必要接口：

- 工作台首页：读取项目列表、最近 Next Action、当前研究问题和服务状态。
- 任务书：调用 brief 与 supervisor plan 相关入口，写入 `state/product/research_question.json` 和 `state/product/supervisor_plan.json`。
- 数据与设计：读取 datasets、variable roles、design spec、run plan。
- 实证执行：读取 runs、observability、run_steps.json、run_events.jsonl、gates.json。
- 结果与草稿：读取 MethodExecutionResult、approved findings、drafts、manuscript candidates。
- 审阅与导出：读取 Verifier、writeback approvals、docx/pdf preflight、export package。

## 6. 接口开发约束

新增 API 必须说明：

1. 处理文件在哪，例如 `Product/app.py` 或 `Product/api/supervisor.py`。
2. URL 是否属于 `/api/v1`。
3. 读写哪个 `Product/state`、`state/product`、`state/runs` 或 `Results/json` 文件。
4. 返回值是否包含 evidence_level、status、next_action 和 audit/provenance 信息。
5. 是否允许进入正式层。默认不允许，除非已有 gate 和 writeback approval。
