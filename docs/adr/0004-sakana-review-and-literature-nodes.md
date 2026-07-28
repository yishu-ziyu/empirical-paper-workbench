# ADR 0004 — Sakana AI 启发的自动评审节点与文献检索节点

- **Status:** Draft
- **Date:** 2026-07-28
- **Supersedes:** —
- **Superseded by:** —
- **Related:** ADR 0001（title/body chapters split）、ADR 0002（cleaning step protocol）、ADR 0003（Agent Contract / NodeResult 协议）

## 1. Context

### 1.1 Sakana AI Scientist 的核心理念

Sakana AI 在 *The AI Scientist: Towards Fully Automated Open-Ended Scientific Discovery* 中提出"全自动科研闭环"：给定一个粗略研究方向，系统自主完成 **idea generation → literature search → experimentation → paper writing → automated review → iterative refinement**。其中三个要素对本项目直接可借鉴：

1. **自动评审（Automated Review）**：用一个独立 LLM 评审节点对产出论文打分，给出可执行的修改建议，而非一次性生成即定稿。
2. **迭代改进（Iterative Refinement）**：评审不通过时回到写作节点重生成，直至分数达标或达到最大迭代次数，避免单次采样质量不稳定。
3. **文献驱动（Literature-Driven）**：在大纲生成前检索相关文献，把检索结果作为大纲与文献综述章节的素材，降低 LLM 凭空"幻觉引用"的概率。

本 ADR 只把这三要素落地到 econpaper 现有 LangGraph 编排中，不引入 Sakana 的 idea generation / experimentation 模块（与经济学论文生成场景不匹配）。

### 1.2 当前 graph 缺少的质量保障环节

当前 graph 流转（`agent/graph.py`）：

```
START → upload_data → clean_data → generate_title → set_direction
      → generate_outline → generate_chapter（6 章循环）→ translate_code → export_docx → END
```

存在三个质量保障缺口：

| # | 缺口 | 证据 | 后果 |
|---|---|---|---|
| A | 章节生成后无评审，单次 LLM 采样即定稿 | `generate_chapter` 返回 `{"body_chapters": ..., "current_chapter_index": idx+1}`，无质量门 | 章节质量方差大，内生性 / 识别策略等问题无法被发现 |
| B | 大纲生成前无文献检索，文献综述章节完全靠 LLM 凭记忆生成 | `set_direction → generate_outline` 直连，`EconPaperState` 无 `literature_entries` 字段 | 文献综述章节引用失真、年份错乱、作者张冠李戴 |
| C | 无迭代闭环，章节一次性产出后即进入 translate_code | `route_after_chapter` 只看 `current_chapter_index`，无质量分支 | 即使生成了低质量章节也无法回炉 |

### 1.3 与 ADR 0003 NodeResult 协议的关系

ADR 0003 已规划本 ADR（见 0003 §Follow-Up Routes）并明确："不做 Sakana 启发的自动评审节点，该工作另起 ADR 0004"。ADR 0003 引入的 `NodeResult` 协议要求：每个节点定义 `*Output(TypedDict, total=False)`，返回类型注解为该 TypedDict，字段集 ⊆ `EconPaperState.__annotations__`。

**本 ADR 的新节点（`review_chapter`、`search_literature`）必须遵循该协议**：定义 `ReviewOutput`、`LiteratureOutput` TypedDict，新增字段补进 `EconPaperState`。若 ADR 0003 Stage A 尚未合并，本 ADR 的节点先以 `-> dict` 返回，待 0003 Stage A 落地后切换为 `-> ReviewOutput` / `-> LiteratureOutput`，** TypedDict 定义本身不阻塞**。

## 2. Goals And Non-Goals

| Type | Statement | Evidence | Owner |
| --- | --- | --- | --- |
| Goal | `review_chapter` 节点对 `body_chapters` 逐章评审，产出 `review_feedback` + `revision_suggestions` + `review_scores` | 新增 `agent/nodes/review_chapter.py`，返回 `ReviewOutput` | agent owner |
| Goal | `search_literature` 节点基于 `research_direction` 检索文献，产出 `literature_entries`（含 title/authors/year/abstract/doi） | 新增 `agent/nodes/search_literature.py`，返回 `LiteratureOutput` | agent owner |
| Goal | 支持自动迭代：评审不通过时回到 `generate_chapter` 重生成，最多 `max_review_iterations` 次 | `review_chapter` 后加条件边 `route_after_review` | agent owner |
| Goal | 评审标准对齐经济学论文规范（内生性 / 识别策略 / 稳健性 / 贡献度 / 可读性 5 维 rubric） | `ReviewRubric` TypedDict，5 个 float 字段 | agent owner |
| Goal | 评审节点只读 `body_chapters`，不直接修改章节内容（只写 feedback） | `ReviewOutput` 不含 `body_chapters` 键 | agent owner |
| Non-Goal | 不集成真实学术搜索引擎（Semantic Scholar / OpenAlex / Google Scholar）作为初始交付 | Stage 1-3 用 mock 文献库 + mock 评审 LLM；真实 API 留 Stage 4（可选） | — |
| Non-Goal | 不训练专用评审 LLM 模型 | 评审节点复用 `call_llm`，与 `generate_chapter` 同一 LLM 调用通道 | — |
| Non-Goal | 不做 Sakana 的 idea generation / experimentation 模块 | 仅借鉴 review + literature + iteration 三要素 | — |
| Non-Goal | 不替换 `route_after_chapter` 已有的 6 章循环逻辑 | `route_after_review` 在评审通过后委托 `route_after_chapter`，不重写 | — |
| Non-Goal | 不做 HITL 人工评审接入（前端审批 UI） | 评审完全自动；HITL 审批（`approve_chapter` 节点）另立 ticket | — |

## 3. Bounded Contexts

| Context | Responsibility | Model/Language | Interfaces | Owned Data |
| --- | --- | --- | --- | --- |
| Agent — Review | 章节评审节点编排（调 LLM、打分、产出 feedback） | TypedDict（`ReviewOutput` / `ReviewRubric`） | `review_chapter(state) -> ReviewOutput`、`route_after_review(state) -> str` | `review_feedback`、`revision_suggestions`、`review_scores`、`review_rubrics`、`review_iteration` |
| Agent — Literature | 文献检索节点编排（构造查询、调检索源、去重） | TypedDict（`LiteratureOutput` / `LiteratureEntry`） | `search_literature(state) -> LiteratureOutput` | `literature_entries`、`literature_query`、`literature_source` |
| Data Source — Mock | Stage 3 mock 文献库 + mock 评审 LLM | Python 字面量 fixture | `mock_literature_corpus()`、`mock_review_llm(chapter, rubric)` | mock 条目池、mock rubric 评分规则 |
| Data Source — Real（Stage 4 可选） | Semantic Scholar API 适配 | REST + JSON | `semantic_scholar_search(query, api_key)` | API key、rate limit |
| Review Standard | 经济学论文评审 rubric | TypedDict（`ReviewRubric`） | 5 维评分 + 加权综合分公式 | rubric 维度定义、权重、阈值 |

| Context | Upstream | Downstream | Translation Surface |
| --- | --- | --- | --- |
| Agent — Review | `generate_chapter`（读 `body_chapters[idx]`） | `route_after_review` 条件边、`generate_chapter`（重生成时读 `revision_suggestions`） | `ReviewOutput` → `EconPaperState` partial |
| Agent — Literature | `set_direction`（读 `research_direction`） | `generate_outline`（消费 `literature_entries`）、`generate_chapter`（lit_review 章节模板渲染） | `LiteratureOutput` → `EconPaperState` partial |
| Data Source — Mock | 测试 / 开发环境 | Agent — Review / Literature | 纯函数，无 IO |
| Data Source — Real | Semantic Scholar API | Agent — Literature | JSON → `LiteratureEntry` |
| Review Standard | Agent — Review（调用方） | — | rubric 维度 → LLM prompt + 加权公式 |

## 4. System Map

新节点的数据流（标注读 / 写字段）：

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          EconPaperState (共享)                          │
└─────────────────────────────────────────────────────────────────────────┘
       ▲                                  ▲                          ▲
       │ 写 literature_entries            │ 写 review_feedback[*]    │
       │ 写 literature_query              │ 写 revision_suggestions  │
       │ 写 literature_source             │ 写 review_scores         │
       │                                  │ 写 review_rubrics        │
       │                                  │ 写 review_iteration      │
       │                                  │ 写 review_chapter_index  │
       │                                  │ （不通过时）写 current_chapter_index（回退）
       │                                  │                          │
┌──────┴──────────────┐         ┌─────────┴──────────┐         ┌─────────┴──────────┐
│ search_literature   │         │ review_chapter     │         │ route_after_review │
│ 读 research_direction│        │ 读 body_chapters[i]│         │ 读 review_scores   │
│ 读 title_chapter    │         │ 读 outline[i]      │         │ 读 review_iteration│
│                     │         │ 读 research_direction│       │ 读 max_review_iter │
│                     │         │ 读 literature_entries│       │ 读 review_enabled  │
└─────────────────────┘         └────────────────────┘         └────────────────────┘
        │                                  │                          │
        │ set_direction 后触发            │ generate_chapter 后触发  │ 条件边路由
        ▼                                  ▼                          ▼
  generate_outline              （不通过）generate_chapter     （通过）route_after_chapter
```

**关键数据流契约**：

| 节点 / 边 | 读字段 | 写字段 | 副作用 |
| --- | --- | --- | --- |
| `search_literature` | `research_direction`、`title_chapter.title` | `literature_entries`、`literature_query`、`literature_source` | 无（纯检索） |
| `review_chapter` | `body_chapters`、`outline`、`current_chapter_index`、`research_direction`、`literature_entries`、`review_iteration`、`max_review_iterations` | `review_feedback`、`revision_suggestions`、`review_scores`、`review_rubrics`、`review_iteration`、`review_chapter_index` | 不通过且未达上限时回退 `current_chapter_index`（见 §5） |
| `route_after_review` | `review_enabled`、`review_scores`、`review_iteration`、`max_review_iterations`、`current_chapter_index`、`outline` | — | 纯路由函数，无写入 |
| `generate_chapter`（迭代路径） | 新增读 `review_feedback`、`revision_suggestions`（作为重生成 prompt 上下文） | `body_chapters`、`current_chapter_index` | 既有逻辑不变，仅扩展 prompt 渲染 |

## 5. Interaction Style

| Interaction | Style | Why This Style | Failure Behavior | Backward Compatibility |
| --- | --- | --- | --- | --- |
| `set_direction` → `search_literature` | 同步顺序边 | 文献检索需在 set_direction 后、generate_outline 前执行；检索结果是大纲素材 | 检索失败时 `literature_entries=[]`，`generate_outline` 降级为无文献模式 | `review_enabled=False` 或 `literature_enabled=False` 时跳过该节点，graph 退化为现状 |
| `search_literature` → `generate_outline` | 同步顺序边 | 大纲节点消费 `literature_entries` 渲染 lit_review 章节大纲 | `literature_entries` 缺失时 outline 节点用空列表 | outline 节点对 `literature_entries` 用 `state.get("literature_entries", []) or []` |
| `generate_chapter` → `review_chapter` | 同步顺序边 | 每章生成后立即评审，评审是 6 章循环内的子步骤 | 评审 LLM 失败时返回 `review_scores=[0.0]*n`，触发重生成；若 `review_enabled=False` 则跳过 | `review_enabled=False` 时该边短路到 `route_after_chapter` |
| `review_chapter` → 条件边 `route_after_review` | 条件边（state-driven） | 评审分数 + 迭代次数决定回炉或推进 | 阈值缺失时默认 `0.7`，迭代上限缺失时默认 `2` | 条件边返回值与 `route_after_chapter` 兼容（复用 `"generate_chapter"` / `"translate_code"` 两个目标） |
| `route_after_review` → `generate_chapter`（重生成） | 条件边分支 | 评审不通过回炉当前章 | 回炉前 `review_chapter` 已回退 `current_chapter_index` | 重生成路径复用 `generate_chapter` 既有逻辑，仅 prompt 多渲染 `revision_suggestions` |
| `route_after_review` → `route_after_chapter` 逻辑（推进） | 条件边分支委托 | 评审通过后复用既有 6 章循环路由 | — | 不修改 `route_after_chapter` 函数 |
| `review_enabled` 配置 | `EconPaperState` 字段 + 启动配置 | 用户可关闭自动评审（如调试 / 跑 baseline） | 字段缺失默认 `True` | 关闭后 graph 等价于 ADR 0003 之前的流转 |
| `max_review_iterations` 配置 | `EconPaperState` 字段 | 防止迭代不收敛 | 字段缺失默认 `2`，硬上限 `3` | — |

**自动评审可配置矩阵**：

| 配置位 | 字段 | 默认 | 取值 | 作用 |
| --- | --- | --- | --- | --- |
| 自动评审开关 | `review_enabled` | `True` | `bool` | `False` 时跳过 `review_chapter` 与 `route_after_review`，直连 `route_after_chapter` |
| 最大迭代次数 | `max_review_iterations` | `2` | `int ∈ [0, 3]` | 单章评审不通过时最多重生成次数；`0` 等价于关闭 |
| 通过阈值 | `review_score_threshold`（运行时常量，不入 state） | `0.7` | `float ∈ (0, 1)` | `review_scores[i] >= 阈值` 视为通过 |
| 文献检索开关 | `literature_enabled`（运行时常量） | `True` | `bool` | `False` 时跳过 `search_literature`，`literature_entries=[]` |
| 文献源 | `literature_source` | `"mock"` | `"mock" \| "semantic_scholar"` | Stage 4 前 fixed `"mock"` |

**迭代回退机制（关键）**：`generate_chapter` 完成后会自增 `current_chapter_index`。若 `review_chapter` 判定当前章不通过且 `review_iteration < max_review_iterations`，则 `review_chapter` 在写 `ReviewOutput` 时同步写 `current_chapter_index = review_chapter_index`（即回退到当前评审章），并 `review_iteration += 1`。这样条件边返回 `"generate_chapter"` 时会重生成同一章。通过时 `review_iteration` 重置为 `0`（下一章开始新一轮）。

## 6. Risks

| Risk | Likelihood | Impact | Mitigation | Responsibility Path | Evidence | Decision Record |
| --- | --- | --- | --- | --- | --- | --- |
| 评审 LLM 幻觉导致误判（把合格章节判为不合格，或反之） | 高 | 中 | 1. rubric 5 维分项打分 + 加权综合分，单维度异常时取中位数；2. `max_review_iterations` 硬上限 `3` 兜底；3. mock 评审 LLM 在 Stage 3 提供确定性 baseline | agent owner | Sakana AI Scientist 报告 §3.4 自动评审一致性 < 人类评审 | 本 ADR §8 Decision C |
| 文献检索返回低质量 / 不相关结果 | 中 | 中 | 1. `LiteratureEntry.relevance_score` 字段，`generate_outline` 只消费 `score >= 0.3` 的条目；2. mock 文献库人工筛选经济学顶刊条目；3. Stage 4 真实 API 启用前需通过 relevance 抽检 | agent owner | Semantic Scholar API 噪声 | 本 ADR §8 Decision B |
| 迭代不收敛（评审始终不通过，无限循环） | 中 | 高 | 1. `max_review_iterations` 默认 `2`、硬上限 `3`；2. `route_after_review` 在 `review_iteration >= max` 时强制推进；3. 单元测试覆盖 `iteration == max` 路径 | agent owner | LangGraph 条件边循环无内置上限 | 本 ADR §5 + §7 |
| 评审标准不适配中文论文（rubric 偏英文顶刊语境） | 中 | 中 | 1. rubric 5 维描述中文化；2. mock 评审 LLM prompt 用中文；3. Stage 3 评审样本含中文经济学期刊（如《经济研究》《管理世界》） | agent owner | econpaper 目标产出为中文论文 | 本 ADR §8 Decision C |
| 评审节点误写 `body_chapters`（破坏只读契约） | 低 | 高 | 1. `ReviewOutput` TypedDict 不含 `body_chapters` 键；2. Fitness Function 静态检查 `review_chapter` 返回值不含 `body_chapters`；3. 单元测试断言评审前后 `body_chapters` 内容哈希不变 | agent owner | ADR 0003 NodeResult 协议 | 本 ADR §7 |
| 文献检索增加端到端延迟（每篇论文多一次 API 调用） | 中 | 低 | 1. mock 模式零网络；2. Stage 4 真实 API 启用缓存（query → entries），同一 session 不重复检索；3. `literature_entries` 限长 `<= 20` | agent owner | Semantic Scholar 单次检索 ~2s | 本 ADR §8 Decision B |
| `review_iteration` 在 checkpointer resume 后状态丢失 | 低 | 中 | 1. `review_iteration` 入 `EconPaperState`（持久化）；2. resume 测试覆盖迭代中途断点 | agent owner | LangGraph checkpointer 行为 | 本 ADR §10 |

## 7. Fitness Functions

| Invariant | Metric Or Rule | Threshold | Measurement Source | Cadence | Failure Response | Local Check Path |
| --- | --- | --- | --- | --- | --- | --- |
| `review_chapter` 返回值契约 | `ReviewOutput` 必须含 `review_feedback`、`revision_suggestions`、`review_scores` 三字段 | 100% | `agent/tests/test_review_chapter.py` 断言三字段存在 | 每次 commit | 阻止合并 | `make verify` |
| `search_literature` 返回值契约 | `LiteratureOutput.literature_entries` 每项含 `title`/`authors`/`year`/`abstract`/`doi` 五字段 | 100% | `agent/tests/test_search_literature.py` 遍历断言 | 每次 commit | 阻止合并 | `make verify` |
| 迭代上限 | `review_iteration <= max_review_iterations` 且 `max_review_iterations <= 3` | 100% | `agent/tests/test_route_after_review.py` 覆盖 `iteration == max` 路径 + 静态断言 `max_review_iterations` 赋值 ≤ 3 | 每次 commit | 阻止合并 | `make verify` |
| 评审只读契约 | `review_chapter` 返回值不含 `body_chapters` 键；评审前后 `body_chapters` 内容哈希不变 | 0 命中 / 哈希相等 | `grep -n "body_chapters" agent/nodes/review_chapter.py` 仅命中读路径；单测断言哈希 | 每次 commit | 阻止合并 | `make verify` |
| 评审通过阈值 | `route_after_review` 在 `review_scores[-1] >= 0.7` 时返回推进分支 | 100% | `agent/tests/test_route_after_review.py` 参数化 | 每次 commit | 阻止合并 | `make verify` |
| 文献检索限长 | `len(literature_entries) <= 20` | 100% | `agent/tests/test_search_literature.py` | 每次 commit | 阻止合并 | `make verify` |
| 关闭开关可降级 | `review_enabled=False` 时 graph 退化为无评审流转，端到端跑通 | 100% | `agent/tests/test_graph_review_disabled.py` | 每次 commit | 阻止合并 | `make verify` |
| NodeResult 协议对齐 | `ReviewOutput` / `LiteratureOutput` 字段集 ⊆ `EconPaperState.__annotations__` | 100% | `agent/tests/test_schema_consistency.py`（ADR 0003 Stage A 引入后复用） | 每次 commit | 阻止合并 | `make verify` |

## 8. Decision Table

| Decision | Default | Rejected Alternatives | Exception Conditions |
| --- | --- | --- | --- |
| **A. 自动评审默认开启，`max_review_iterations=2`** | ✅ 采纳 | 1. 默认关闭（违背 Sakana 理念，质量门形同虚设）；2. `max=0`（等价关闭）；3. `max=5`（迭代成本过高，单章最多 6 次 LLM 调用） | 调试 / baseline 模式可经 `review_enabled=False` 关闭；生产环境硬上限 `3` |
| **B. 文献检索默认 mock，配置 API key 后切真实 Semantic Scholar** | ✅ 采纳 | 1. 默认真实 API（开发阶段无 key、rate limit、CI 不稳定）；2. 默认 Google Scholar（无官方 API、反爬严格）；3. 默认 OpenAlex（覆盖面不如 Semantic Scholar 的 CS/Econ 交叉） | Stage 4 落地前 `literature_source` fixed `"mock"`；Stage 4 后 `SEMANTIC_SCHOLAR_API_KEY` 环境变量存在时切换 |
| **C. 评审标准用经济学论文 rubric（内生性 / 识别 / 稳健性 / 贡献度 / 可读性 5 维）** | ✅ 采纳 | 1. 通用论文 rubric（缺内生性 / 识别策略，不适配经济学）；2. 单一综合分（不可解释，无法定位改进点）；3. NeurIPS rubric（Sakana 原版，偏 ML 实验） | lit_review / data_desc 等非实证章节，"内生性"维度权重降为 0，"可读性"权重提升（由 `ReviewRubric` 各维度字段存在性推导） |
| **D. 评审通过阈值 `0.7`** | ✅ 采纳 | 1. `0.5`（过低，质量门失效）；2. `0.9`（过高，迭代频繁、不收敛风险高）；3. 动态阈值（实现复杂，无 baseline 数据） | 阈值为运行时常量（不入 state），Stage 3 mock 调参后再评估是否入配置 |
| **E. 综合分加权公式：`0.3*endogeneity + 0.25*identification + 0.2*robustness + 0.15*contribution + 0.1*readability`** | ✅ 采纳 | 1. 等权平均（内生性识别策略权重不足）；2. 纯 LLM 给综合分（不可解释）；3. 取最低维度分（过于保守） | 非实证章节权重表见 Decision C 异常条件 |
| **F. 迭代回退由 `review_chapter` 节点负责（写 `current_chapter_index`）** | ✅ 采纳 | 1. 由条件边函数回退（条件边应纯路由，无写入副作用，违反 LangGraph 惯例）；2. 引入独立 `rollback_chapter_index` 节点（过度工程） | 通过时 `review_chapter` 不写 `current_chapter_index`，由 `route_after_chapter` 复用既有推进逻辑 |
| **G. `review_chapter` 评审范围 = 当前刚生成的章（`review_chapter_index = current_chapter_index - 1`）** | ✅ 采纳 | 1. 一次性评审全部 6 章（延迟高、反馈粒度粗、迭代无法定位单章）；2. 评审最近 2 章（复杂、状态管理困难） | `review_enabled=False` 时不评审 |

## 9. Stage 切分

### Stage 1 — `review_chapter` 节点 + `ReviewOutput` TypedDict + 条件边
1. 在 `agent/state.py` 新增 `ReviewRubric`、`ReviewOutput` TypedDict，并把字段补进 `EconPaperState`（见 §10）；
2. 新建 `agent/nodes/review_chapter.py`，实现 `review_chapter(state: EconPaperState) -> ReviewOutput`（签名见 §11），评审逻辑暂用 `call_llm` 占位（与 `generate_chapter.call_llm` 同一通道）；
3. 新建 `agent/nodes/route_after_review.py`（或在 `graph.py` 内新增 `route_after_review` 函数），实现条件边路由（见 §11）；
4. 在 `graph.py` 的 `build_graph()` 中：`add_node("review_chapter", review_chapter)`；把 `generate_chapter` 的条件边目标从 `route_after_chapter` 改为 `review_chapter`；`review_chapter` 加条件边 `route_after_review`，分支映射见 §11；
5. `review_enabled=False` 时，`route_after_review` 直接返回 `route_after_chapter(state)`（短路）；
6. 新增 `agent/tests/test_review_chapter.py`：mock LLM，断言返回值含三字段、`body_chapters` 未被修改、`review_iteration` 自增正确；
7. 新增 `agent/tests/test_route_after_review.py`：参数化覆盖 `通过 / 不通过且未达上限 / 不通过且达上限 / review_enabled=False` 四条路径；
8. 跑 `make verify`，全绿。

**Stage 1 验收**：`review_enabled=True`、mock LLM 时，单章评审不通过会触发一次重生成，第二次仍不通过则强制推进；`review_enabled=False` 时 graph 行为与 ADR 0003 完全一致。

### Stage 2 — `search_literature` 节点 + `LiteratureOutput` TypedDict
1. 在 `agent/state.py` 新增 `LiteratureEntry`、`LiteratureOutput` TypedDict，字段补进 `EconPaperState`（见 §10）；
2. 新建 `agent/nodes/search_literature.py`，实现 `search_literature(state: EconPaperState) -> LiteratureOutput`（签名见 §11），检索逻辑暂用本地 mock 函数 `mock_literature_corpus()`（Stage 3 完善）；
3. 在 `graph.py` 的 `build_graph()` 中：`add_node("search_literature", search_literature)`；`set_direction` → `search_literature` → `generate_outline`（替换原 `set_direction` → `generate_outline` 直连边）；
4. `literature_enabled=False` 时，`search_literature` 返回 `{"literature_entries": [], "literature_source": "disabled"}`（不跳过节点，保持 graph 拓扑稳定）；
5. `generate_outline` 节点扩展：从 `state.get("literature_entries", []) or []` 取文献，渲染进 lit_review 章节大纲；
6. `generate_chapter` 的 lit_review prompt 扩展：渲染 `literature_entries` 进 user prompt（作为引用素材）；
7. 新增 `agent/tests/test_search_literature.py`：断言返回值结构、限长 `<= 20`、`literature_enabled=False` 降级；
8. 跑 `make verify`，全绿。

**Stage 2 验收**：`literature_enabled=True` 时 `generate_outline` 产出的 lit_review 章节大纲包含文献条目；`literature_enabled=False` 时大纲退化为现状。

### Stage 3 — mock 文献库 + mock 评审 LLM
1. 新建 `agent/tests/fixtures/mock_literature.py`，定义 `mock_literature_corpus() -> List[LiteratureEntry]`，含 ≥ 30 条经济学顶刊条目（覆盖劳动 / 发展 / 公共 / 计量 / 宏观 5 个子领域，中英文混合）；
2. 新建 `agent/tests/fixtures/mock_review.py`，定义 `mock_review_llm(chapter_content: str, rubric: ReviewRubric) -> ReviewOutput`，按规则评分（如章节内容长度 < 阈值则 `readability` 低分、未提及 IV / DID 则 `identification` 低分）；
3. `search_literature` 在 `literature_source == "mock"` 时调 `mock_literature_corpus()` 并按 `research_direction` 关键词过滤；
4. `review_chapter` 在测试 / 开发环境调 `mock_review_llm`（通过模块级函数 `call_review_llm` 替换，与 `generate_chapter.call_llm` 同一 monkeypatch 模式）；
5. 新增 `agent/tests/test_mock_literature_corpus.py`、`agent/tests/test_mock_review_llm.py`；
6. 跑 `make verify`，全绿。

**Stage 3 验收**：开发环境 `make dev` 跑通完整 graph，`literature_entries` 非空且含中文期刊条目，`review_scores` 为确定性评分（mock 规则可复现）。

### Stage 4 — 真实 Semantic Scholar API 集成（可选）
1. 新建 `agent/nodes/literature_sources/semantic_scholar.py`，实现 `semantic_scholar_search(query: str, api_key: Optional[str]) -> List[LiteratureEntry]`；
2. `search_literature` 节点按 `literature_source` 配置分发：`"mock"` → mock、`"semantic_scholar"` → 真实 API；
3. 新增 `SEMANTIC_SCHOLAR_API_KEY` 到 `backend/.env.example`；后端启动时读环境变量决定 `literature_source`；
4. 新增 `agent/tests/test_semantic_scholar.py`（mock HTTP，不真发请求）；
5. 真实 API 启用前需通过 relevance 抽检：人工标注 20 条检索结果相关性，`relevance_score >= 0.3` 的占比 ≥ 80%；
6. 跑 `make verify`，全绿。

**Stage 4 验收**：`SEMANTIC_SCHOLAR_API_KEY` 存在时 `literature_source == "semantic_scholar"`，检索结果含真实 DOI；key 缺失时自动降级为 `"mock"`。

## 10. 需要补进 EconPaperState 的新字段

在 `agent/state.py` 的 `EconPaperState` 中新增以下字段（遵循 `total=False` 约定，向后兼容）：

```python
# ADR-0004: 文献检索
literature_entries: List[Any]  # [{title, authors, year, abstract, doi}]，详见 LiteratureEntry
literature_query: Optional[str]      # 实际用于检索的查询串（research_direction 派生）
literature_source: Optional[str]     # "mock" | "semantic_scholar" | "disabled"

# ADR-0004: 章节评审
review_feedback: List[str]           # 每章的评审反馈（按 chapter_index 对齐）
revision_suggestions: List[str]      # 每章的修改建议
review_scores: List[float]           # 每章的评审综合分 0-1
review_rubrics: List[Any]            # 每章的 5 维 rubric 分项，详见 ReviewRubric
review_iteration: int                # 当前章节的评审迭代次数
review_chapter_index: Optional[int]  # 本轮评审的章节索引（= current_chapter_index - 1）
review_enabled: bool                 # 是否开启自动评审（默认 True）
max_review_iterations: int           # 最大迭代次数（默认 2，硬上限 3）
```

配套 TypedDict 定义（新建于 `agent/state.py` 或 `agent/protocols.py`，遵循 ADR 0003 NodeResult 协议）：

```python
class LiteratureEntry(TypedDict, total=False):
    """单条文献条目（search_literature 写入 literature_entries 列表）。"""
    title: str
    authors: List[str]
    year: int
    abstract: str
    doi: Optional[str]
    source: str              # "mock" | "semantic_scholar"
    relevance_score: float   # 0-1，检索相关性（mock 模式按关键词命中数估算）

class LiteratureOutput(TypedDict, total=False):
    """search_literature 节点返回值（NodeResult 协议）。"""
    literature_entries: List[LiteratureEntry]
    literature_query: str
    literature_source: str

class ReviewRubric(TypedDict, total=False):
    """经济学论文评审 5 维 rubric（每维度 0-1）。"""
    endogeneity: float       # 内生性处理（IV / DID / RD / 自然实验）
    identification: float    # 识别策略清晰度
    robustness: float        # 稳健性（样本 / 设定 / 安慰剂）
    contribution: float      # 贡献度（理论 / 实证 / 政策）
    readability: float       # 可读性（结构 / 逻辑 / 表达）

class ReviewOutput(TypedDict, total=False):
    """review_chapter 节点返回值（NodeResult 协议）。

    注意：不含 body_chapters 字段 —— 评审节点只读章节、只写反馈。
    """
    review_feedback: List[str]
    revision_suggestions: List[str]
    review_scores: List[float]
    review_rubrics: List[ReviewRubric]
    review_iteration: int
    review_chapter_index: int
    current_chapter_index: int  # 仅在判定不通过、需回退时写入（见 §5 回退机制）
```

## 11. 新 graph 流转

### 11.1 流转图

```
START → upload_data → clean_data → generate_title → set_direction
      → search_literature（新增）→ generate_outline → generate_chapter
      → review_chapter（新增）→ 条件边 route_after_review:
          review_enabled == False
            → route_after_chapter（原逻辑，短路）
          review_scores[review_chapter_index] >= 0.7
          或 review_iteration >= max_review_iterations
            → route_after_chapter（原逻辑：idx < 6 回 generate_chapter 下一章；idx >= 6 进 translate_code）
          review_scores[review_chapter_index] < 0.7
          且 review_iteration < max_review_iterations
            → generate_chapter（重生成当前章，review_chapter 已回退 current_chapter_index）
      → translate_code → export_docx → END
```

### 11.2 节点与路由函数签名

```python
# agent/nodes/search_literature.py
def search_literature(state: EconPaperState) -> LiteratureOutput:
    """基于 research_direction 检索文献，写 literature_entries。

    1. 从 state['research_direction'] + state['title_chapter'].title 派生 literature_query；
    2. 按 literature_source 配置分发（mock / semantic_scholar）；
    3. 去重（按 doi 或 title 规范化）；
    4. 限长 <= 20；
    5. 返回 LiteratureOutput（不含 outline / body_chapters）。
    """

# agent/nodes/review_chapter.py
def call_review_llm(chapter_content: str, rubric_template: ReviewRubric,
                    research_direction: str, literature_entries: List[Any]) -> ReviewOutput:
    """模块级 LLM 调用函数（与 generate_chapter.call_llm 同一 monkeypatch 模式）。

    生产环境接 langchain-anthropic；开发 / 测试通过 monkeypatch 替换为 mock_review_llm。
    """

def review_chapter(state: EconPaperState) -> ReviewOutput:
    """对当前刚生成的章节（review_chapter_index = current_chapter_index - 1）评审。

    1. 计算待评审章索引：idx = current_chapter_index - 1（generate_chapter 已自增）；
    2. 读 body_chapters[idx].content / outline[idx] / research_direction / literature_entries；
    3. 调 call_review_llm 得 5 维 rubric + feedback + suggestions；
    4. 加权算综合分：0.3*endo + 0.25*ident + 0.2*robust + 0.15*contrib + 0.1*read；
    5. 写 review_feedback[idx] / revision_suggestions[idx] / review_scores[idx] / review_rubrics[idx]；
    6. 若综合分 < threshold 且 review_iteration < max_review_iterations：
         - 写 current_chapter_index = idx（回退，使条件边回 generate_chapter 重生成）
         - 写 review_iteration += 1
       否则：
         - 写 review_iteration = 0（下一章重置）
    7. 写 review_chapter_index = idx；
    8. 返回 ReviewOutput（不含 body_chapters）。

    review_enabled == False 时返回 {} （no-op，由条件边短路）。
    """

# agent/graph.py（新增路由函数）
def route_after_review(state: EconPaperState) -> str:
    """review_chapter 后的条件边路由。

    返回值与 route_after_chapter 兼容（"generate_chapter" / "translate_code"）。

    - review_enabled == False → 委托 route_after_chapter(state)
    - review_scores[review_chapter_index] >= threshold
      或 review_iteration >= max_review_iterations → 委托 route_after_chapter(state)
    - 否则 → "generate_chapter"（重生成当前章，review_chapter 已回退 idx）
    """
```

### 11.3 `build_graph()` 改动点

```python
# 新增节点
builder.add_node("search_literature", search_literature)
builder.add_node("review_chapter", review_chapter)

# 边改动（伪代码，非实现）
# 原：builder.add_edge("set_direction", "generate_outline")
# 新：
builder.add_edge("set_direction", "search_literature")
builder.add_edge("search_literature", "generate_outline")

# 原：builder.add_conditional_edges("generate_chapter", route_after_chapter, {...})
# 新：
builder.add_edge("generate_chapter", "review_chapter")
builder.add_conditional_edges(
    "review_chapter",
    route_after_review,
    {
        "generate_chapter": "generate_chapter",  # 重生成当前章
        "translate_code": "translate_code",      # 6 章全部完成
    },
)
# 注意：route_after_review 委托 route_after_chapter 时，"generate_chapter" 分支
# 也覆盖"评审通过、进入下一章"的语义（route_after_chapter 在 idx < 6 时返回该值）。
```

## Exceptions

- **`review_enabled=False`**：`review_chapter` 返回 `{}`，`route_after_review` 直接委托 `route_after_chapter`，graph 行为等价于 ADR 0003 之前的流转。这是降级 / 调试 / baseline 模式。
- **`literature_enabled=False`**：`search_literature` 返回 `{"literature_entries": [], "literature_source": "disabled"}`，节点不跳过（保持 graph 拓扑稳定），`generate_outline` 降级为无文献模式。
- **`review_chapter_index` 缺失 / `current_chapter_index == 0`**：`review_chapter` 返回 `{}`（no-op），避免首章前误触发评审。
- **`body_chapters[idx]` 为空 dict 或 `content` 缺失**：`review_chapter` 跳过该章，`review_scores[idx] = 0.0`，`review_feedback[idx] = "章节内容为空，跳过评审"`，不触发回退（避免空章节无限重生成）。
- **`SEMANTIC_SCHOLAR_API_KEY` 缺失但 `literature_source == "semantic_scholar"`**：`search_literature` 自动降级为 `"mock"` 并在 `literature_source` 字段写 `"mock_degraded"`，记录 warning。

## Follow-Up Routes

- **ADR 0005**（待评估）：agent 扁平 import → 包式 import 迁移，删除 `backend/main.py` 的 `sys.path.append` 黑魔法（继承自 ADR 0003 follow-up）。
- **ADR 0006**（待评估）：session store 从内存 dict 迁移到 SQLite/Redis，支持持久化与多 worker（继承自 ADR 0003 follow-up）。
- **ADR 0007**（待评估）：HITL 人工评审接入 —— 前端审批 UI + `approve_chapter` 节点与 `review_chapter` 的协同（自动评审通过后是否仍需人工确认）。
- **ADR 0008**（待评估）：多 LLM 路由 —— 评审 LLM 与生成 LLM 使用不同模型（如生成用 Claude、评审用 GPT-4），降低同模型自评偏差。
- **ADR 0009**（待评估）：文献检索结果去重 / 引用图谱构建 —— 把 `literature_entries` 升级为引用关系图，支持 `generate_chapter` 自动生成参考文献列表。
