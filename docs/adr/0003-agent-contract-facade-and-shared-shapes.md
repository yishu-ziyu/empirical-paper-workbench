# ADR 0003 — Agent Contract, Facade, Test Fixtures, and Shared Shapes

- **Status:** Accepted
- **Date:** 2026-07-28
- **Supersedes:** —
- **Superseded by:** —
- **Related:** ADR 0001 (title/body chapters split), ADR 0002 (cleaning step protocol)

## Context

improve-codebase-architecture 评审识别出 4 个未处理的"浅接缝"深化机会，证据来自 4 份并行只读调研报告：

| # | 问题 | 严重度 | 关键证据 |
|---|---|---|---|
| A | 节点返回 partial state dict 是浅接缝 | 中 | 10 个节点返回类型全部为裸 `dict`；6 处键名不在 `EconPaperState` schema 内（`pdf_path`/`docx_path`/`degraded`/`chapter_index`/`version_index`/`export_template`/`author`/`abstract`/`outliers_cuts`）；pydantic 已在 requirements 但全 agent 代码 0 处使用 |
| B | 端点与节点紧耦合 | 中 | 11/20 端点直接 import 并调用 agent 节点函数；13 次直接节点调用 + 仅 1 次 `graph.invoke`；5 处端点手动复制 graph 编排（outline/chapter/regenerate/doc_export/upload 双重路径）；checkpointer 在直调路径下完全失效 |
| C | 测试 setup 路径黑魔法 | 低 | `EconPaperState` 0 次实例化、77 处 dict 字面量；`mock_llm` 5 份独立实现（签名/返回结构均不一致）；27 个本地 fixture 散落 29 个测试文件；`sys.path.append` 在生产代码 `backend/main.py:12-13`；`generate_title`/`generate_outline` 测试埋在 backend/tests/ 违反命名约定 |
| D | 前后端状态 shape 双份拷贝 | 低 | 后端 state 用 TypedDict 非 Pydantic，FastAPI 无法生成 OpenAPI；0 个 endpoint 声明 `response_model`；前端无 `types/` 目录、无 codegen 工具；5+ 处 shape 漂移（BalanceResult 字段名 `balanced_n` vs `balanced` 导致前端渲染 `undefined`） |

4 个问题相互耦合，构成"链式根因"：A（无类型契约）→ B（端点必须直调节点拿原始 dict）→ D（端点手写 dict 响应，前端各自类型）→ C（测试绕过类型系统用手写 dict）。因此采用统一 ADR，分 4 个 stage 实施。

## Goals And Non-Goals

| Type | Statement | Evidence | Owner |
| --- | --- | --- | --- |
| Goal | 节点返回值有显式类型契约，调用方与被调用方通过 TypedDict 对齐 | 引入 `NodeResult` 协议与 per-node `*Output` TypedDict | agent owner |
| Goal | HTTP 端点与 LangGraph 节点解耦，端点只依赖 Facade 抽象 | `backend/routers/` 0 处直接 import `agent/nodes/` | backend owner |
| Goal | 测试 state 通过共享工厂构造，复用 `EconPaperState` TypedDict | 测试目录 0 处裸 dict 字面量，统一走 `make_state(**overrides)` | test owner |
| Goal | 前后端 shape 单一真相源，codegen 自动同步 | 后端 OpenAPI 含全部 `response_model`；前端 `types/api.ts` 由 `openapi-typescript` 生成 | contract owner |
| Non-Goal | 不重写 LangGraph 编排逻辑或引入新 Agent 框架 | graph.py 节点顺序、边路由、checkpointer 保持不变 | — |
| Non-Goal | 不引入 Pydantic 替换 LangGraph 的 TypedDict state | LangGraph 要求 TypedDict；Pydantic 仅用于 backend response_model | — |
| Non-Goal | 不做前端 UI 重构或新功能 | 仅替换类型定义来源，不动组件结构 | — |
| Non-Goal | 不实现 Sakana 启发的自动评审节点 | 该工作另起 ADR 0004 | — |

## Bounded Contexts

| Context | Responsibility | Model/Language | Interfaces | Owned Data |
| --- | --- | --- | --- | --- |
| Agent | LangGraph 节点编排与执行 | TypedDict（`EconPaperState` + per-node `*Output`） | `NodeResult` 协议、`agent.graph` | `EconPaperState`、`Chapter`、`DatasetMeta`、`StepReport` |
| Backend | HTTP 边界、session 生命周期、响应序列化 | Pydantic v2（response models） + FastAPI | `AgentFacade`、`backend.routers.*` | `SessionStore`、response DTO |
| Contract | 前后端共享 API schema | OpenAPI 3.1 + TypeScript | `openapi.json` → `types/api.ts` | API shape |
| Test | 测试 state 与 mock 工厂 | Python fixtures + TypedDict 构造器 | `tests/conftest.py`（根级）、`make_state()` | 测试 state 工厂 |

| Context | Upstream | Downstream | Translation Surface |
| --- | --- | --- | --- |
| Agent | backend（HITL config 注入） | backend（NodeResult 返回） | `AgentFacade`：把 NodeResult 的 partial dict 投影成 backend 可消费的 state slice |
| Backend | frontend（HTTP 请求） | frontend（HTTP 响应） | response_model：Pydantic 模型 → OpenAPI → TypeScript |
| Contract | backend（OpenAPI 源） | frontend（types 消费方） | `openapi-typescript` codegen |
| Test | agent + backend | — | 直接复用 `EconPaperState`/`*Output` TypedDict，无翻译 |

## System Map

| Element | Data Flow | Dependency | Trust Boundary | Responsibility |
| --- | --- | --- | --- | --- |
| HTTP Client (Frontend) | → HTTP request | depends on `types/api.ts` | public | 发送请求、渲染响应 |
| FastAPI Router | → AgentFacade.invoke_node / invoke_graph | depends on `AgentFacade` | internal | 参数校验、auth、调用 facade |
| AgentFacade | → graph.invoke / node(state) | depends on `agent.graph` + `agent.nodes` | internal | session 上下文管理、节点调度、NodeResult 聚合 |
| LangGraph | → state mutation | depends on `EconPaperState` schema | internal | 编排节点、条件边、checkpointer |
| Node | → NodeResult (TypedDict) | depends on `agent.state.*` TypedDict | internal | 执行业务逻辑、返回 partial state |
| Pydantic Response Model | ← NodeResult | depends on `agent.state.*` TypedDict | translation | 把 TypedDict 投影成 OpenAPI-friendly shape |
| OpenAPI codegen | ← openapi.json | depends on FastAPI response_model | tooling | 生成 `types/api.ts` |

## Interaction Style

| Interaction | Style | Why This Style | Failure Behavior | Backward Compatibility |
| --- | --- | --- | --- | --- |
| Router → Facade | 同步方法调用 | 进程内调用，无网络开销；Facade 封装 session + graph 调用 | Facade 抛 HTTPException，router 直接透传 | Facade 接口稳定后，节点实现变化不影响 router |
| Facade → Graph/Node | 同步调用（LangGraph 标准） | LangGraph 同步编排，无异步需求 | 节点返回 `{"degraded": True, ...}` 标记降级 | NodeResult 协议保持向后兼容（新字段可选） |
| Backend → Frontend | HTTP JSON + OpenAPI 契约 | 标准 REST，前端 codegen 自动同步 | response_model 校验失败返回 422 | 新增字段不破坏前端（TS optional） |
| Test → State Factory | 同步函数调用 | 测试需要快速构造 state，无 IO | factory 返回 `EconPaperState` 实例，类型错误编译期暴露 | factory 支持任意字段 override，不限定 fixture 数量 |

## Runtime Dependency Adoption

| Dependency | Capability | Alternative | Failure Mode | Timeout/Retry/Fallback | Adoption Criteria |
| --- | --- | --- | --- | --- | --- |
| `openapi-typescript` | OpenAPI → TypeScript codegen | `swagger-typescript-api`、`orval`、`@hey-api/openapi-ts` | codegen 失败导致 types 不更新 | 手动 `make gen-api` 触发，CI 检查 types 是否 fresh | 选 `openapi-typescript` 因其最小依赖、零配置、输出纯净 |
| Pydantic v2 response_model | runtime 校验 + OpenAPI 生成 | 手写 serializer、TypedDict + 手写 OpenAPI | 校验失败抛 ValidationError | FastAPI 自动捕获转 422 | 已在 requirements，零新增依赖 |
| `AgentFacade`（自研） | 端点 → agent 解耦 | 直接调用、Service 层 | Facade 方法抛 HTTPException | — | 自研，无第三方依赖 |

## Risks

| Risk | Likelihood | Impact | Mitigation | Responsibility Path | Evidence | Decision Record |
| --- | --- | --- | --- | --- | --- | --- |
| 重构破坏现有 e2e（make dev smoke） | 中 | 高 | 分 stage 提交，每个 stage 后跑 `make verify` + smoke | agent owner → test owner | 174 测试基线 | 本 ADR §Stage 切分 |
| NodeResult 协议过严，导致节点无法返回降级字段 | 低 | 中 | `NodeResult` 用 `total=False` TypedDict，所有字段可选 | agent owner | `agent/protocols.py` | 本 ADR §Decision A |
| codegen 引入构建复杂度 | 中 | 低 | `make gen-api` 一键命令，package.json script 同步 | frontend owner | `Makefile` | 本 ADR §Stage 4 |
| Pydantic response_model 与 TypedDict 双份定义 | 中 | 中 | response_model 通过 `model_validate` 从 TypedDict 构造，不手写字段 | backend owner | `backend/schemas/` | 本 ADR §Decision D |
| Facade 成为 god object | 中 | 中 | Facade 只做调度，不做业务；每个节点一个 facade 方法，方法体 ≤ 5 行 | backend owner | `backend/facade.py` | 本 ADR §Decision B |

## Fitness Functions

| Invariant | Metric Or Rule | Threshold | Measurement Source | Cadence | Failure Response | Local Check Path |
| --- | --- | --- | --- | --- | --- | --- |
| 节点返回值类型化 | 节点函数返回类型为 `NodeResult` 子类，非裸 `dict` | 100% | `grep -rn "def .*state.*-> dict:" agent/nodes/` 命中 0 | 每次 commit | 阻止合并 | `make verify` |
| Router 不直调节点 | `backend/routers/` 下 `from nodes` / `from graph` 命中 0 | 0 命中 | `grep -rn "from nodes\|from graph\|from cleaning" backend/routers/` | 每次 commit | 阻止合并 | `make verify` |
| 测试 state 走工厂 | 测试目录 `state = {` 字面量数 ≤ 5（允许少量 fixture 内部使用） | ≤ 5 | `grep -rn "state = {" agent/tests/ backend/tests/` | 每次 commit | 阻止合并 | `make verify` |
| 后端 response_model 覆盖 | 返回 JSON 的 endpoint 100% 声明 `response_model` | 100% | `grep -L "response_model" backend/routers/*.py` | 每次 commit | 阻止合并 | `make verify` |
| 前端类型单一来源 | `frontend/src/types/api.ts` 由 codegen 生成，组件内 0 处手写 API 响应 interface | 0 处 | `grep -rn "interface.*Result\|interface.*Response" frontend/src/components/` | 每次 commit | 阻止合并 | `make verify` |
| shape 漂移检测 | 前端 `tsc --noEmit` 通过 + `make gen-api` 后 `git diff --exit-code types/` | 0 diff | `make gen-api && git diff --exit-code` | CI | 阻止合并 | `make check-api-drift` |

## Decision Table

| Decision | Default | Rejected Alternatives | Exception Conditions |
| --- | --- | --- | --- |
| **A. NodeResult 协议**：每个节点定义 `*Output(TypedDict, total=False)`，返回类型注解为该 TypedDict；引入 `NodeResult` 协议类型作为类型别名 | ✅ 采纳 | 1. Pydantic BaseModel（LangGraph 不支持）；2. 保持裸 dict + 靠 mypy 推断（mypy 对 dict 字面量推断弱）；3. dataclass（与 LangGraph reducer 不兼容） | translate_code/export_docx 等返回大量字段的节点允许 TypedDict 字段较多 |
| **B. AgentFacade 门面**：新建 `backend/facade.py`，封装 session 上下文 + graph.invoke + 单节点直调；router 只调 facade | ✅ 采纳 | 1. router 直接调 graph（重复编排问题未解）；2. 引入 Service 层（过度工程，无业务逻辑）；3. 把 graph 暴露成全局变量（违反依赖注入） | /upload 保持走完整 graph.invoke；其他端点走 facade.invoke_node |
| **C. 共享测试工厂**：根目录 `conftest.py` 定义 `make_state(**overrides)` 工厂 + `mock_llm_factory(node_name)`；删除 5 份 mock_llm 重复 | ✅ 采纳 | 1. 每 test 文件各自维护（现状，已证明漂移）；2. factory_boy（过重）；3. 全用 fixture（参数化困难） | 节点特定测试允许在文件内追加局部 fixture，但必须继承共享工厂 |
| **D. Pydantic response_model + OpenAPI codegen**：backend 新建 `backend/schemas/responses.py`，全部 JSON endpoint 声明 `response_model`；前端引入 `openapi-typescript` 生成 `types/api.ts` | ✅ 采纳 | 1. 手写 TS interface（已证明漂移）；2. gRPC / tRPC（技术栈切换过激）；3. Zod runtime 校验（runtime 校验非 shape 单一来源） | PlainTextResponse / FileResponse 端点（doc_export/code_export）豁免 |

## Synthesized Default

四个决策构成单向依赖链：**A（NodeResult）→ B（Facade）→ D（response_model）→ C（test factory）**。

- A 为 B 提供"节点返回值有类型"的基础，Facade 可以把 `NodeResult` 投影成 response_model；
- B 为 D 提供"端点只依赖 Facade"的解耦基础，response_model 不再需要手写 dict；
- D 为 C 提供"测试断言 response_model 而非裸 dict"的类型基础，工厂构造的 state 通过 response_model 序列化后与前端契约一致；
- C 反过来为 A/B/D 提供"测试侧类型化"的基础，避免测试绕过类型系统让生产代码 schema 演进失同步。

实施分 4 个 stage，每个 stage 独立可验证，按依赖顺序推进。允许在 stage 边界提交并跑全量测试。

## Stage 切分

### Stage A — NodeResult 协议（问题 A）
1. 新建 `agent/protocols.py`，定义 `NodeResult = TypeVar("NodeResult", bound=Mapping[str, Any])` 协议类型；
2. 为每个节点定义 `*Output` TypedDict（如 `UploadDataOutput`、`CleanDataOutput` ... `ExportDocxOutput`），字段从调研报告 §1.1 抽取；
3. 把 10 个节点函数的返回类型从 `dict` 改为对应的 `*Output`；
4. 把调研发现的 6 处 schema 外键（`pdf_path`/`docx_path`/`degraded`/`chapter_index`/`version_index`/`export_template`/`author`/`abstract`/`outliers_cuts`）补进 `EconPaperState` 或对应 `*Output`；
5. 新增 `agent/tests/test_schema_consistency.py`：遍历所有 `*Output` TypedDict，断言其字段集 ⊆ `EconPaperState.__annotations__`；
6. 跑 `make verify`，全绿。

### Stage B — AgentFacade 门面（问题 B）
1. 新建 `backend/facade.py`，定义 `AgentFacade` 类，封装 `session_id` + state store + graph 调用；
2. 每个 router 调用的节点方法对应一个 facade 方法（如 `facade.set_direction_and_outline(state, rd)`、`facade.generate_chapter(state, chapter, kwargs)`）；
3. facade 内部统一用 `graph.invoke` 或显式节点调用，但 router 不感知；
4. 把 11 个直调节点的端点改为调 facade；
5. 删除 `backend/routers/` 下所有 `from nodes` / `from graph` / `from cleaning` import；
6. 新增 `backend/tests/test_facade.py`：mock graph，验证 facade 调用顺序；
7. 跑 `make verify`，全绿。

### Stage D — Pydantic response_model + OpenAPI codegen（问题 D）
1. 新建 `backend/schemas/__init__.py` + `backend/schemas/responses.py`，定义每个 endpoint 的 response Pydantic 模型；
2. 修复 BalanceResult 字段名漂移（统一为后端 step report 的 `balanced` / `n_periods` / `attrition_rate` + 补 `unbalanced_n`）；
3. 修复 OutlierReport 结构漂移（统一为 list 结构，与 step report 一致）；
4. 修复 Profile 字段缺失（补 `dataset_type` / `charls_config`）；
5. 修复 Chapter status 枚举不对齐（前端补 `approved`/`edited`/`rolled_back`）；
6. 每个 endpoint 加 `response_model=...`；
7. 前端 `package.json` 加 `openapi-typescript` devDependency；
8. 新增 `Makefile` target `gen-api`：`cd frontend && npx openapi-typescript http://localhost:8000/openapi.json -o src/types/api.ts`；
9. 前端组件删除手写 interface，改 import `types/api.ts`；
10. 新增 `Makefile` target `check-api-drift`：`make gen-api && git diff --exit-code frontend/src/types/api.ts`；
11. 跑 `make verify` + `make check-api-drift`，全绿。

### Stage C — 共享测试工厂（问题 C）
1. 新建根目录 `conftest.py`，定义 `make_state(**overrides) -> EconPaperState` 工厂；
2. 定义 `mock_llm_for(node_name)` 工厂，支持 `generate_title` / `generate_outline` / `generate_chapter` 三种签名；
3. 定义 `make_body_chapters(n=6)`、`make_six_chapter_outline()`、`make_cleaning_report()` 等公共 fixture；
4. 删除 14 个文件中的 27 个重复 fixture，改为从根 conftest import；
5. 删除 5 份 `mock_llm` 重复实现，统一用 `mock_llm_for`；
6. 把 `backend/tests/test_outline.py` 移到 `agent/tests/test_generate_outline.py`（遵守命名约定）；
7. 把 `generate_title` 的测试从 `backend/tests/test_graph.py` 抽出，新建 `agent/tests/test_generate_title.py`；
8. 跑 `make verify`，全绿。

## Exceptions

- **PlainTextResponse / FileResponse 端点**（doc_export、code_export）豁免 response_model 要求，因为它们不返回 JSON。
- **WebSocket 端点**（ws.py）豁免 response_model，但 WSMessage 的 shape 仍需在前端 `types/api.ts` 中定义（通过 `components.schemas` 而非 `responses`）。
- **生产代码 `sys.path.append`**（`backend/main.py:12-13`）暂保留，因为 agent 扁平 import 风格是 LangGraph 生态惯例；长期解决方案是改为 `from agent.state import ...` 包式 import，但需同时改 agent 所有文件，超出本 ADR 范围。记录为 follow-up。

## Follow-Up Routes

- **ADR 0004**：Sakana 启发的自动评审节点 + 文献检索（本 ADR 完成后启动）
- **ADR 0005**（待评估）：agent 扁平 import → 包式 import 迁移，删除 `sys.path.append` 黑魔法
- **ADR 0006**（待评估）：session store 从内存 dict 迁移到 SQLite/Redis，支持持久化与多 worker
