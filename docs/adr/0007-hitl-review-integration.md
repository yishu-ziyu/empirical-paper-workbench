# ADR 0007 — HITL 人工评审接入（前端审批 UI + review_chapter 协同）

- **Status:** Accepted
- **Date:** 2026-07-28
- **Supersedes:** —
- **Superseded by:** —
- **Related:** ADR 0003（Agent Contract / Facade / response_model）、ADR 0004（Sakana 自动评审 + 文献检索节点）

## 1. Context

### 1.1 ADR 0004 的全自动评审闭环

ADR 0004 已实现 `review_chapter` 节点：每章生成后由 LLM 按 5 维 rubric（内生性 / 识别 / 稳健性 / 贡献度 / 可读性）打分，低于 `0.7` 阈值时回退 `current_chapter_index` 触发重生成，达 `max_review_iterations`（默认 2，硬上限 3）则强制推进。该闭环**完全自动**：LLM 既当裁判又当运动员，无人参与。

### 1.2 全自动评审的三个缺口

| # | 缺口 | 证据 | 后果 |
|---|---|---|---|
| A | 自动评审通过，但人工认为质量不够时无法否决 | `route_after_review` 只看 `review_scores` 与 `review_iteration`，无人工覆盖入口 | LLM 自评偏差导致"虚假通过"，低质量章节进入下游 |
| B | 自动评审不通过但达上限（强制推进）时，人工无法叫停或强制接受 | `review_iteration >= max` 时 `route_after_review` 直接委托 `route_after_chapter`，无暂停点 | 达上限的章节往往是质量最差的，却最缺乏人工把关 |
| C | 人工无法查看评审反馈 / rubric 分项 / 修改建议来辅助决策 | `review_feedback` / `review_rubrics` / `revision_suggestions` 只存在 state 里，无 HTTP 端点暴露，前端无渲染组件 | 人工评审若要接入，缺少信息载体与决策入口 |

三个缺口同源：ADR 0004 的评审是**单声道**的（只听 LLM）。本 ADR 在其之上叠加**人工覆盖层**（HITL overlay），不替换自动评审。

### 1.3 与 ADR 0003 / 0004 的关系

- **ADR 0003** 提供 Facade 解耦 + `response_model` + OpenAPI codegen 契约。本 ADR 的新端点遵循该契约：声明 `response_model`，前端类型走 `types/api.ts`。
- **ADR 0004** 提供 `review_chapter` 节点与 `review_feedback` / `review_scores` / `review_rubrics` / `revision_suggestions` state 字段。本 ADR **只读**这些字段（GET 端点），并新增 HITL 决策字段（POST 端点），不修改 `review_chapter` 节点逻辑。
- ADR 0004 §Follow-Up Routes 已规划本 ADR："ADR 0007（待评估）：HITL 人工评审接入 —— 前端审批 UI + approve_chapter 节点与 review_chapter 的协同"。

## 2. Goals And Non-Goals

| Type | Statement | Evidence | Owner |
| --- | --- | --- | --- |
| Goal | 自动评审通过后，人工可在前端否决（拒绝 → 重生成） | `POST /sessions/{id}/review/decision` 接受 `reject` | backend owner |
| Goal | 自动评审不通过但达上限时，人工可强制通过 | `POST /sessions/{id}/review/decision` 接受 `force_pass` | backend owner |
| Goal | 人工可查看评审反馈、5 维 rubric 分项、修改建议、综合分、迭代轮次 | `GET /sessions/{id}/review` 返回完整评审信息；`ReviewPanel` 渲染 | frontend owner |
| Goal | HITL 默认关闭，不影响现有自动流程 | `hitl_review_enabled` 默认 `False`；关闭时 graph 行为等价于 ADR 0004 | agent owner |
| Goal | 人工决策必须写入 state，且 HITL 暂停后 state 不丢失 | `hitl_decision` / `hitl_reviewer` 入 `EconPaperState`；Fitness Function 强制 | agent owner |
| Non-Goal | 不替换 ADR 0004 的自动评审节点 | `review_chapter` 节点逻辑不变；HITL 是叠加层 | — |
| Non-Goal | 不在 Stage 1 实现 LangGraph interrupt 真暂停 | Stage 1 用 state-driven HITL（同 T-04/T-06/T-07 既有模式）；真 interrupt 留 Stage 3 | — |
| Non-Goal | 不做多人协同评审 / 评审工作流（指派 / 通知 / 会签） | 单一 reviewer 字段；无工作流引擎 | — |
| Non-Goal | 不修改 `route_after_review` 条件边逻辑 | HITL 决策通过 facade 写 state，不侵入 graph 路由 | — |

## 3. Bounded Contexts

| Context | Responsibility | Model/Language | Interfaces | Owned Data |
| --- | --- | --- | --- | --- |
| Agent — Review（继承 ADR 0004） | 自动评审节点编排 | TypedDict（`ReviewOutput` / `ReviewRubric`） | `review_chapter(state) -> ReviewOutput`（不改） | `review_feedback`、`revision_suggestions`、`review_scores`、`review_rubrics`、`review_iteration`、`review_chapter_index` |
| Agent — HITL（新增） | 人工评审决策的 state 载体 | TypedDict（`EconPaperState` 新增字段） | state 字段读写 | `hitl_review_enabled`、`hitl_decision`、`hitl_reviewer`、`hitl_comment` |
| Backend — Review Router（新增） | HTTP 端点：读评审结果 / 写人工决策 | Pydantic v2（`ReviewInfoResponse` / `ReviewDecisionResponse`） | `GET /sessions/{id}/review`、`POST /sessions/{id}/review/decision` | HTTP 请求 / 响应 DTO |
| Backend — Facade（扩展） | 端点 → agent 解耦；读 state 评审 slice / 写决策 / 触发重生成 | Python 方法 | `facade.get_review(session_id)`、`facade.submit_review_decision(session_id, decision, reviewer, comment)` | session state 读写 |
| Frontend — ReviewPanel（新增） | 评审信息渲染 + 决策按钮交互 | React + TypeScript（`types/api.ts` codegen） | `ReviewPanel` 组件 | 组件本地态（决策中 loading） |

| Context | Upstream | Downstream | Translation Surface |
| --- | --- | --- | --- |
| Agent — Review | `generate_chapter`（读 `body_chapters`） | Backend — Facade（读 `review_*` 字段） | `ReviewOutput` → `EconPaperState` partial（不变） |
| Agent — HITL | Backend — Facade（写 `hitl_*` 字段） | `route_after_review`（Stage 3 读 `hitl_decision`） | `hitl_decision` 是 string 枚举，无翻译 |
| Backend — Review Router | Frontend（HTTP 请求） | Frontend（HTTP 响应） | `response_model`：Pydantic → OpenAPI → TypeScript |
| Backend — Facade | Review Router（方法调用） | Agent state（读写） | `get_review` 把 state 的 `review_*` 列表投影成单章 `ReviewInfoResponse` |
| Frontend — ReviewPanel | `types/api.ts`（类型） | — | codegen 类型 → 组件 props |

## 4. System Map

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          EconPaperState (共享)                          │
│  ┌─────────────────────────────┐  ┌──────────────────────────────────┐  │
│  │ ADR-0004 自动评审字段（只读）│  │ ADR-0007 HITL 字段（新增，读写） │  │
│  │ review_feedback[]           │  │ hitl_review_enabled (默认 False) │  │
│  │ revision_suggestions[]      │  │ hitl_decision ("accept"|"reject" │  │
│  │ review_scores[]             │  │   |"force_pass")                  │  │
│  │ review_rubrics[]            │  │ hitl_reviewer (str)              │  │
│  │ review_iteration            │  │ hitl_comment (str)               │  │
│  │ review_chapter_index        │  └──────────────────────────────────┘  │
│  │ max_review_iterations       │                                        │
│  └─────────────────────────────┘                                        │
└─────────────────────────────────────────────────────────────────────────┘
       ▲ 读 review_*                ▲ 写 hitl_*                     ▲
       │                            │                               │
┌──────┴──────────────┐    ┌────────┴─────────────┐    ┌────────────┴──────────┐
│ GET /review         │    │ POST /review/decision│    │ ReviewPanel.tsx       │
│ facade.get_review() │    │ facade.submit_       │    │ 渲染 feedback/rubric  │
│ 读 review_* 列表    │    │   review_decision()  │    │ 三按钮：接受/拒绝/    │
│ 投影成单章信息      │    │ 写 hitl_decision     │    │   强制通过            │
│                     │    │ reject → 重生成章节  │    │ 调 POST /review/      │
│                     │    │ accept/force_pass →  │    │   decision            │
│                     │    │   proceed            │    │                       │
└─────────────────────┘    └──────────────────────┘    └───────────────────────┘
```

**关键数据流契约**：

| 端点 / 组件 | 读字段 | 写字段 | 副作用 |
| --- | --- | --- | --- |
| `GET /sessions/{id}/review` | `review_feedback`、`revision_suggestions`、`review_scores`、`review_rubrics`、`review_chapter_index`、`review_iteration`、`max_review_iterations` | — | 无（纯读） |
| `POST /sessions/{id}/review/decision` | `review_chapter_index`（确定操作章） | `hitl_decision`、`hitl_reviewer`、`hitl_comment` | `decision=="reject"` 时调 `facade.regenerate_chapter` 重生成该章 |
| `ReviewPanel` | `ReviewInfoResponse`（props 或 fetch） | — | 调 `POST /review/decision`；按 `next_action` 决定后续 UI |

## 5. Interaction Style

| Interaction | Style | Why This Style | Failure Behavior | Backward Compatibility |
| --- | --- | --- | --- | --- |
| Frontend → `GET /review` | 同步 HTTP GET | 评审信息是 state 的只读投影，无副作用，适合同步拉取 | session 不存在 → 404；无评审数据 → 200 + 空字段 | 新增端点，不影响现有 |
| Frontend → `POST /review/decision` | 同步 HTTP POST | 决策需立即生效并返回 `next_action` | 非法 decision → 422；session 不存在 → 404 | 新增端点，不影响现有 |
| Facade → state（读评审） | 同步方法调用 | 进程内，无 IO | state 缺 `review_*` 字段时返回空默认值 | `hitl_review_enabled=False` 时 GET 仍可返回自动评审结果 |
| Facade → state（写决策） | 同步方法调用 | 写 `hitl_*` 字段 + 可能触发重生成 | `regenerate_chapter` 失败 → 400 | 不写 `review_*` 字段（只读 ADR 0004 数据） |
| Facade → `regenerate_chapter`（reject 路径） | 同步节点调用 | 复用 ADR 0003 既有 facade 方法 | 节点不可用 → 503 | 重生成后 `review_chapter` 会再次评审（自动闭环继续） |
| Stage 3：LangGraph interrupt 暂停 | interrupt + resume | 真暂停 graph 执行等待人工 | interrupt 后 state 由 checkpointer 持久化 | Stage 1 state-driven 模式不依赖 interrupt；Stage 3 替换为 interrupt 时不改端点契约 |

**HITL 协同矩阵（自动评审 × 人工决策）**：

| 自动评审结果（`auto_decision`） | 人工决策（`hitl_decision`） | 最终行为 | `next_action` |
| --- | --- | --- | --- |
| `pass`（score >= 0.7） | `accept` | 推进下一章 | `proceed` |
| `pass` | `reject` | 否决自动通过，重生成当前章 | `regenerate` |
| `pass` | （未决策，HITL 关闭） | 推进（等价 ADR 0004） | — |
| `fail`（score < 0.7，未达上限） | `force_pass` | 人工强制通过，推进 | `proceed` |
| `fail`（达上限，强制推进） | `force_pass` | 人工确认强制通过 | `proceed` |
| `fail` | `accept` | 接受失败判定，重生成（等价自动回退） | `regenerate` |
| `fail` | （未决策，HITL 关闭） | 自动回退或强制推进（等价 ADR 0004） | — |

## 6. Risks

| Risk | Likelihood | Impact | Mitigation | Responsibility Path | Evidence | Decision Record |
| --- | --- | --- | --- | --- | --- | --- |
| HITL 暂停后 state 丢失（Stage 3 interrupt） | 中 | 高 | 1. `hitl_*` 字段入 `EconPaperState`（TypedDict 持久化）；2. checkpointer resume 测试覆盖中断点；3. Stage 1 state-driven 模式无此风险（state 在 facade 内存） | agent owner | LangGraph interrupt 行为 | 本 ADR §10 + §9 Stage 3 |
| 人工决策未写入 state（前端发了请求但 facade 没持久化） | 低 | 高 | 1. `submit_review_decision` 必须调 `save_state`；2. Fitness Function 断言 POST 后 state 含 `hitl_decision`；3. 端点返回 `ok=True` 前确认 state 已写 | backend owner | facade.update_state 契约 | 本 ADR §7 |
| `reject` 触发重生成后自动评审又判 fail，无限循环 | 中 | 中 | 1. 复用 ADR 0004 `max_review_iterations` 硬上限 3；2. 重生成后 `review_iteration` 自增（ADR 0004 既有逻辑）；3. 达上限后自动强制推进，人工可 `force_pass` | agent owner | ADR 0004 §5 迭代回退机制 | 本 ADR §5 协同矩阵 |
| 前端 ReviewPanel 显示不完整（缺 rubric 分项 / suggestions） | 中 | 中 | 1. `ReviewInfoResponse` schema 强制 5 维 rubric + suggestions 字段；2. ReviewPanel 测试断言 5 维渲染；3. codegen 保证前后端类型一致 | frontend owner | ADR 0003 codegen 契约 | 本 ADR §7 + §9 Stage 2 |
| HITL 默认开启破坏现有自动流程 | 低 | 高 | 1. `hitl_review_enabled` 默认 `False`；2. Fitness Function 断言默认值；3. 关闭时端点仍可用（只读评审结果）但无暂停 | agent owner | state.py 默认值 | 本 ADR §8 Decision A |
| Stage 1 state-driven 与 Stage 3 interrupt 切换时端点契约变化 | 低 | 中 | 1. 端点 `response_model` 在两阶段保持一致；2. Stage 3 只改 facade 内部实现（interrupt vs 直调），不改 HTTP 契约；3. `next_action` 语义不变 | backend owner | ADR 0003 response_model 契约 | 本 ADR §9 Stage 3 |

## 7. Fitness Functions

| Invariant | Metric Or Rule | Threshold | Measurement Source | Cadence | Failure Response | Local Check Path |
| --- | --- | --- | --- | --- | --- | --- |
| HITL 暂停后 state 不丢失 | `hitl_decision` / `hitl_reviewer` 在 POST 后存在于 state | 100% | `backend/tests/test_review.py` 断言 POST 后 `facade.get_state(sid)["hitl_decision"]` 非空 | 每次 commit | 阻止合并 | `make verify` |
| 人工决策必须写入 state | `submit_review_decision` 调用 `save_state`；返回 `ok=True` 时 state 已持久化 | 100% | `backend/tests/test_review.py` 断言 | 每次 commit | 阻止合并 | `make verify` |
| UI 显示完整评审信息 | `ReviewInfoResponse` 含 feedback / suggestions / score / rubric(5 维) / iteration / max / auto_decision | 100% | `backend/schemas/review.py` 字段定义 + `frontend ReviewPanel.test.tsx` 断言 5 维渲染 | 每次 commit | 阻止合并 | `make verify` |
| HITL 默认关闭 | `hitl_review_enabled` 默认 `False`；关闭时 graph 行为等价 ADR 0004 | 100% | `agent/state.py` 注释 + `backend/tests/test_review.py` 断言 GET 在关闭时仍返回评审数据 | 每次 commit | 阻止合并 | `make verify` |
| Router 不直调节点 | `backend/routers/review.py` 无 `from nodes` / `from graph` import | 0 命中 | `grep -rn "from nodes\|from graph" backend/routers/review.py` | 每次 commit | 阻止合并 | `make verify` |
| response_model 覆盖 | review router 的 JSON endpoint 100% 声明 `response_model` | 100% | `grep -L "response_model" backend/routers/review.py` | 每次 commit | 阻止合并 | `make verify` |
| 前端类型单一来源 | ReviewPanel 不手写 API 响应 interface，import `types/api.ts` | 0 处手写 | `grep -rn "interface.*Review" frontend/src/components/ReviewPanel.tsx` | 每次 commit | 阻止合并 | `make verify` |
| HITL 不写 ADR 0004 评审字段 | `submit_review_decision` 不写 `review_feedback` / `review_scores` / `review_rubrics` | 0 命中 | `backend/tests/test_review.py` 断言 POST 后 `review_*` 字段不变 | 每次 commit | 阻止合并 | `make verify` |

## 8. Decision Table

| Decision | Default | Rejected Alternatives | Exception Conditions |
| --- | --- | --- | --- |
| **A. HITL 默认关闭（`hitl_review_enabled=False`）** | ✅ 采纳 | 1. 默认开启（破坏现有自动流程，违背"叠加层"定位）；2. 全局配置文件控制（与 state-driven 模式不一致）；3. 每章独立开关（Stage 1 过度复杂） | 用户可通过 state 注入 `hitl_review_enabled=True` 启用；Stage 3 interrupt 集成后可由 graph 配置注入 |
| **B. Stage 1 用 state-driven HITL（非 LangGraph interrupt）** | ✅ 采纳 | 1. Stage 1 直接上 interrupt（需改 graph 编译 + checkpointer 配置，风险高）；2. 用 WebSocket 推送暂停状态（过度工程，HTTP 轮询足够）；3. 用独立审批队列（引入新基础设施） | 与 T-04/T-06/T-07 既有 state-driven HITL 模式一致；Stage 3 替换为 interrupt 时不改端点契约 |
| **C. `reject` 触发 `facade.regenerate_chapter` 重生成** | ✅ 采纳 | 1. 只写 decision 不触发重生成（前端需二次调 /regenerate，多一次往返）；2. 直接调 `generate_chapter` 节点（绕过 facade 解耦）；3. 写回 `current_chapter_index` 让 graph 自动重生成（Stage 1 无 interrupt，graph 不会自动跑） | `regenerate_chapter` 不可用时返回 503，不阻塞 decision 写入 |
| **D. 人工决策用 3 值枚举（accept / reject / force_pass）** | ✅ 采纳 | 1. 2 值（accept / reject）（无法表达"自动 fail 但人工强制通过"）；2. 5 值（加 "defer" / "escalate"）（Stage 1 无工作流引擎）；3. 自由文本（不可枚举，无法自动化） | 非法值由 Pydantic 422 拦截 |
| **E. GET /review 返回单章评审（非全 6 章）** | ✅ 采纳 | 1. 返回全部 6 章评审（信息过载，前端一次只评审一章）；2. 返回全量 + 当前章高亮（冗余，前端可按需调）；3. 分页（6 章无需分页） | 无评审数据时返回 200 + 空字段（非 404），让前端渲染空态 |
| **F. `auto_decision` 由后端计算（非 state 存储）** | ✅ 采纳 | 1. 存入 state（与 ADR 0004 的 `review_scores` 冗余，且自动决策可由 score 推导）；2. 前端计算（重复逻辑，前后端漂移）；3. LLM 直接输出（不可解释） | 阈值 `0.7` 与 `review_chapter.REVIEW_SCORE_THRESHOLD` 保持一致 |

## 9. Stage 切分

### Stage 1 — 后端 endpoint + facade + schema（本 ADR 实施）
1. 在 `agent/state.py` 新增 HITL 字段（见 §10）；
2. 新建 `backend/schemas/review.py`，定义 `ReviewRubricResponse` / `ReviewInfoResponse` / `ReviewDecisionRequest` / `ReviewDecisionResponse`；
3. 在 `backend/facade.py` 新增 `get_review(session_id) -> dict` 与 `submit_review_decision(session_id, decision, reviewer, comment) -> dict`；
4. 新建 `backend/routers/review.py`，实现 `GET /sessions/{id}/review` 与 `POST /sessions/{id}/review/decision`，声明 `response_model`；
5. 在 `backend/main.py` 注册 review router；
6. 新增 `backend/tests/test_review.py`：测试 GET / POST 端点契约、state 持久化、reject 触发重生成、HITL 不写 review_* 字段；
7. 跑 `make gen-api` 更新 `frontend/src/types/api.ts`；
8. 跑 `make verify`，全绿。

**Stage 1 验收**：`GET /sessions/{id}/review` 返回当前章评审信息（feedback / 5 维 rubric / score / suggestions / iteration / auto_decision）；`POST /sessions/{id}/review/decision` 写入 `hitl_decision` / `hitl_reviewer` 到 state，`reject` 触发重生成并返回 `next_action="regenerate"`；`hitl_review_enabled=False` 时端点仍可读评审结果。

### Stage 2 — 前端 ReviewPanel 组件（本 ADR 实施）
1. 新建 `frontend/src/components/ReviewPanel.tsx`；
2. 接收 `ReviewInfoResponse` props（或内部 fetch），渲染 feedback / 5 维 rubric 条形图 / suggestions / score / iteration；
3. 三个按钮：接受（accept）、拒绝重生成（reject）、强制通过（force_pass）；
4. 按钮调 `POST /sessions/{id}/review/decision`，按 `next_action` 回调通知父组件；
5. 类型从 `types/api.ts` import（遵循 ADR 0003 codegen 规范）；
6. 新建 `frontend/src/components/__tests__/ReviewPanel.test.tsx`：断言 5 维渲染、按钮触发回调、auto_decision 影响按钮可用性；
7. 跑 `npx vitest run`，全绿。

**Stage 2 验收**：ReviewPanel 渲染完整评审信息；三个决策按钮可点击并调 POST 端点；`auto_decision="pass"` 时"强制通过"按钮禁用（无意义）；`auto_decision="fail"` 时"接受"按钮语义为"接受重生成"。

### Stage 3 — LangGraph interrupt 集成（后续 ticket）
1. 在 `agent/graph.py` 的 `review_chapter` 节点后加 `interrupt()`（当 `hitl_review_enabled=True`）；
2. `route_after_review` 读 `hitl_decision`：未决策时暂停（interrupt），决策后按 `accept`/`reject`/`force_pass` 路由；
3. `backend/facade.py` 的 `submit_review_decision` 改为 `graph.update_state` + `graph.invoke(None, config)`（resume）；
4. checkpointer 从 `InMemorySaver` 迁移到持久化存储（关联 ADR 0006）；
5. 新增 interrupt resume 测试：模拟暂停 → 写 decision → resume → 验证 state 完整；
6. 跑 `make verify`，全绿。

**Stage 3 验收**：`hitl_review_enabled=True` 时 graph 在 `review_chapter` 后暂停；前端 GET /review 获得暂停状态；POST /review/decision resume graph；resume 后 state 含完整 `review_*` + `hitl_*` 字段。端点 HTTP 契约与 Stage 1 一致。

## 10. 需要补进 EconPaperState 的新字段

在 `agent/state.py` 的 `EconPaperState` 中新增以下字段（遵循 `total=False` 约定，向后兼容）：

```python
# ADR-0007: HITL 人工评审
hitl_review_enabled: bool           # 是否启用人工评审暂停点（默认 False）
hitl_decision: Optional[str]        # 人工决策："accept" | "reject" | "force_pass"
hitl_reviewer: Optional[str]        # 评审人标识（用户名 / open_id）
hitl_comment: Optional[str]         # 评审人备注（可选）
```

这些字段与 ADR 0004 的 `review_*` 字段正交：HITL 字段只由 `POST /review/decision` 写入，`review_*` 字段只由 `review_chapter` 节点写入。Fitness Function 强制两者不交叉写入。

## 11. Exceptions

- **`hitl_review_enabled=False`（默认）**：HITL 叠加层不激活。`GET /review` 仍返回自动评审结果（只读），`POST /review/decision` 仍可调用（写 state + 可能重生成），但 graph 不暂停。等价于"人工可看可决策但不阻塞自动流程"。
- **无评审数据（`review_chapter` 未跑过）**：`GET /review` 返回 200 + 空字段（`feedback=""`, `score=0.0`, `rubric={}` 全 None, `auto_decision="fail"`），让前端渲染空态而非报错。
- **`review_chapter_index` 缺失**：`GET /review` 回退用 `current_chapter_index - 1`；`POST /review/decision` 的 `reject` 回退用 `current_chapter_index - 1` 触发重生成。
- **`reject` 时 `regenerate_chapter` 不可用（agent 模块缺失）**：`submit_review_decision` 仍写入 `hitl_decision`，但返回 `next_action="regenerate"` + `ok=True`，由前端调既有 `/regenerate` 端点完成重生成（降级：decision 已记录，重生成延后）。
- **非法 `decision` 值**：Pydantic `ReviewDecisionRequest` 不做枚举校验（保持 string），由 facade 运行时校验，非法值返回 400。这样未来加新 decision 值不需改 schema。
- **Stage 3 interrupt 后 checkpointer 失效**：降级为 Stage 1 state-driven 模式（facade 直调节点），记录 warning。

## Follow-Up Routes

- **ADR 0008**（待评估）：多 LLM 路由 —— 评审 LLM 与生成 LLM 使用不同模型，降低同模型自评偏差（继承自 ADR 0004 follow-up）。
- **ADR 0009**（待评估）：文献检索结果去重 / 引用图谱构建（继承自 ADR 0004 follow-up）。
- **ADR 0010**（待评估）：HITL 审批工作流 —— 多人会签 / 指派 / 通知，把单 reviewer 升级为工作流引擎（基于本 ADR 的 `hitl_decision` 扩展）。
- **Stage 3 ticket**：LangGraph interrupt 集成（本 ADR §9 Stage 3），关联 ADR 0006（session store 持久化）。
