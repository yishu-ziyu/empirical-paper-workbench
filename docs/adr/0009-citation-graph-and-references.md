# ADR 0009 — 文献引用图谱构建与参考文献列表自动生成

- **Status:** Draft
- **Date:** 2026-07-28
- **Supersedes:** —
- **Superseded by:** —
- **Related:** ADR 0003（Agent Contract / NodeResult 协议）、ADR 0004（search_literature / review_chapter 节点）

## 1. Context

### 1.1 ADR 0004 的扁平文献列表缺口

ADR 0004 落地 `search_literature` 节点后，`EconPaperState.literature_entries` 是一个扁平 `List[LiteratureEntry]`，每个条目含 `title / authors / year / abstract / doi / source / relevance_score`。这带来三个未解问题（ADR 0004 §Follow-Up Routes 已记录为 ADR 0009 候选）：

1. **无引用关系**：条目之间互不关联，无法回答"X 文献引用了哪些 Y 文献"。
2. **无参考文献章节**：`export_docx` 节点不生成 References 章节，论文末尾缺少学术规范的引用列表。
3. **无引用编号**：`generate_chapter` 的 `lit_review` 章节正文没有 `[1][2]` 引用标记，读者无法把叙述对应到 References。

### 1.2 当前 graph 流转的引用缺口

```
START → upload_data → clean_data → generate_title → set_direction
      → search_literature → generate_outline → generate_chapter（6 章循环 + review）
      → translate_code → export_docx → END
```

| # | 缺口 | 证据 | 后果 |
|---|---|---|---|
| A | `literature_entries` 无引用编号 | `EconPaperState` 无 `citation_indices` 字段 | 正文无法引用 `[1][2]`，参考文献无序号 |
| B | `export_docx` 不渲染 References 章节 | `agent/nodes/export_docx.py` 只渲染 `chapters`，无 bibliography 环境 | 论文末尾无参考文献列表 |
| C | 文献条目无引用关系图 | `EconPaperState` 无 `citation_graph` 字段 | 无法做引用追踪 / 影响力分析（Stage 2 留接口） |

### 1.3 与 ADR 0003 NodeResult 协议的关系

本 ADR 新增的两个节点（`build_citation_graph`、`generate_references`）必须遵循 ADR 0003 NodeResult 协议：定义 `CitationGraphOutput`、`ReferencesOutput` TypedDict，返回类型注解为对应 TypedDict，字段集 ⊆ `EconPaperState.__annotations__`。`tests/test_schema_consistency.py` 的 `NODES` 列表需追加这两个节点。

## 2. Goals And Non-Goals

| Type | Statement | Evidence | Owner |
| --- | --- | --- | --- |
| Goal | `build_citation_graph` 节点在 `search_literature` 后构建引用图谱，为每条文献分配引用编号 `[1], [2], ...`（按 `(year, title)` 升序） | 新增 `agent/nodes/citation_graph.py`，返回 `CitationGraphOutput` | agent owner |
| Goal | `generate_references` 节点在 `export_docx` 前生成 References 列表（APA 格式，作者 > 3 用 et al.，DOI 可追溯） | 新增 `agent/nodes/generate_references.py`，返回 `ReferencesOutput` | agent owner |
| Goal | `export_docx` 节点把 `references_list` 渲染为 `\begin{thebibliography}` 环境，追加在 `latex_source` 末尾 | 修改 `agent/nodes/export_docx.py` | agent owner |
| Goal | 引用图谱数据结构支持 Stage 2 扩展（`edges` 字段预留引用关系边） | `citation_graph` 含 `entries / edges / indices` 三键 | agent owner |
| Non-Goal | 不接入 Semantic Scholar citations API 构建真实引用关系 | Stage 1 `edges` 为空列表；Stage 2 follow-up | — |
| Non-Goal | 不修改 `generate_chapter` 的 `lit_review` prompt（引用标记 `[1][2]` 自动插入留 follow-up） | 本 ADR 只做图谱 + 参考文献列表 | — |
| Non-Goal | 不替换 `search_literature` 的检索逻辑 | `build_citation_graph` 只消费 `literature_entries`，不重新检索 | — |
| Non-Goal | 不做参考文献样式切换（GB/T 7714 / Chicago 等） | Stage 1 固定 APA 风格；样式抽象留 follow-up | — |

## 3. Bounded Contexts

| Context | Responsibility | Model/Language | Interfaces | Owned Data |
| --- | --- | --- | --- | --- |
| Agent — Citation Graph | 引用图谱构建（编号分配、关系边预留） | TypedDict（`CitationGraphOutput` / `CitationEntry`） | `build_citation_graph(state) -> CitationGraphOutput` | `citation_graph`、`citation_indices` |
| Agent — References | 参考文献列表生成（APA 格式化） | TypedDict（`ReferencesOutput`） | `generate_references(state) -> ReferencesOutput` | `references_list` |
| Agent — Export | LaTeX bibliography 渲染 | Jinja2 + LaTeX | `export_docx` 内追加 `\begin{thebibliography}` | `latex_source`（既有字段） |

| Context | Upstream | Downstream | Translation Surface |
| --- | --- | --- | --- |
| Agent — Citation Graph | `search_literature`（读 `literature_entries`） | `generate_references`（消费 `citation_graph.entries`）、`generate_chapter`（未来消费 `citation_indices`） | `CitationGraphOutput` → `EconPaperState` partial |
| Agent — References | `build_citation_graph`（读 `citation_graph`） | `export_docx`（消费 `references_list`） | `ReferencesOutput` → `EconPaperState` partial |
| Agent — Export | `generate_references`（读 `references_list`） | PDF / docx 产物 | `references_list` → `\begin{thebibliography}` |

## 4. System Map

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          EconPaperState (共享)                          │
└─────────────────────────────────────────────────────────────────────────┘
       ▲                                  ▲                          ▲
       │ 写 citation_graph                │ 写 references_list       │ 写 latex_source
       │ 写 citation_indices              │                          │ （追加 thebibliography）
       │                                  │                          │
┌──────┴──────────────┐         ┌─────────┴──────────┐         ┌─────────┴──────────┐
│ build_citation_graph │         │ generate_references │         │ export_docx        │
│ 读 literature_entries│        │ 读 citation_graph   │         │ 读 references_list │
└─────────────────────┘         └────────────────────┘         └────────────────────┘
        │                                  │                          │
        │ search_literature 后触发        │ export_docx 前触发       │ 末尾渲染
        ▼                                  ▼                          ▼
  generate_outline              （原）translate_code           PDF + docx
```

**关键数据流契约**：

| 节点 | 读字段 | 写字段 | 副作用 |
| --- | --- | --- | --- |
| `build_citation_graph` | `literature_entries` | `citation_graph`、`citation_indices` | 无（纯函数） |
| `generate_references` | `citation_graph` | `references_list` | 无（纯函数） |
| `export_docx`（扩展） | 既有 + `references_list` | `latex_source`（追加 bibliography） | 既有编译逻辑不变 |

## 5. Interaction Style

| Interaction | Style | Why This Style | Failure Behavior | Backward Compatibility |
| --- | --- | --- | --- | --- |
| `search_literature` → `build_citation_graph` | 同步顺序边 | 编号分配需在检索后、大纲前完成（`generate_outline` 可选消费 `citation_indices`） | `literature_entries` 缺失时返回空图谱 | `literature_entries=[]` 时图谱为空，下游降级 |
| `build_citation_graph` → `generate_outline` | 同步顺序边 | 大纲节点可读 `citation_indices`（未来用于 lit_review 章节编号渲染） | `citation_indices` 缺失时大纲节点用空 dict | 不修改 `generate_outline` 既有逻辑 |
| `translate_code` → `generate_references` | 同步顺序边 | 参考文献列表需在 export 前就绪 | `citation_graph` 缺失时返回空列表 | `references_list=[]` 时 `export_docx` 不追加 bibliography |
| `generate_references` → `export_docx` | 同步顺序边 | export 节点消费 `references_list` 渲染 thebibliography | `references_list` 为空时不渲染 bibliography 环境 | 既有模板渲染逻辑不变 |

**编号分配规则**（关键）：

1. 按 `(year, title)` 升序排序（年份升序，同年按 title 字母序）；
2. 从 `[1]` 起递增分配编号；
3. 编号 key 优先用 `doi`，DOI 缺失时 fallback 到 `title`；
4. 编号映射写入 `citation_indices: Dict[str, int]`（key = doi 或 title）。

## 6. Risks

| Risk | Likelihood | Impact | Mitigation | Responsibility Path | Evidence | Decision Record |
| --- | --- | --- | --- | --- | --- | --- |
| 引用编号与正文 `[1][2]` 标记不一致（正文未自动插入） | 高 | 中 | 本 ADR 不做正文标记插入（follow-up）；Stage 1 只保证 References 列表编号连续 | agent owner | lit_review prompt 未改 | 本 ADR §2 Non-Goal + §Follow-Up |
| DOI 缺失导致编号 key 冲突（多条无 DOI 同 title 文献） | 低 | 中 | `build_citation_graph` 用 `doi or title` 作 key；`search_literature` 已按 doi/title 去重 | agent owner | ADR 0004 去重逻辑 | 本 ADR §5 编号规则 |
| APA 格式不适配中文文献（作者列表、标点） | 中 | 低 | Stage 1 用简化 APA（作者 > 3 用 et al.，DOI 拼 `https://doi.org/...`）；中文作者原样输出 | agent owner | econpaper 目标为中英文混合 | 本 ADR §2 Non-Goal |
| `export_docx` 渲染 thebibliography 破坏既有 LaTeX 编译 | 低 | 中 | thebibliography 在 `\end{document}` 前追加；空列表时不渲染；测试覆盖编译路径 | agent owner | LaTeX 标准环境 | 本 ADR §7 |
| Stage 2 接 Semantic Scholar citations API 时 `edges` schema 变化 | 中 | 低 | `edges` 当前为 `List[Dict]`，预留 `{from, to}` 形态；Stage 2 可扩展不破坏 Stage 1 | agent owner | 图谱 schema 设计 | 本 ADR §8 Decision B |

## 7. Fitness Functions

| Invariant | Metric Or Rule | Threshold | Measurement Source | Cadence | Failure Response | Local Check Path |
| --- | --- | --- | --- | --- | --- | --- |
| 参考文献按字母序（年份升序） | `references_list` 按 `(year, title)` 升序，编号连续 `[1..N]` | 100% | `agent/tests/test_citation_graph.py` + `agent/tests/test_generate_references.py` | 每次 commit | 阻止合并 | `make verify` |
| 引用编号连续 | `citation_indices.values()` 为 `{1, 2, ..., N}` 无间断 | 100% | `agent/tests/test_citation_graph.py` 断言编号集合 | 每次 commit | 阻止合并 | `make verify` |
| DOI 可追溯 | `references_list` 每项含 `doi` 字段（可为 None）；有 DOI 时 APA 文本含 `https://doi.org/...` | 100% | `agent/tests/test_generate_references.py` 遍历断言 | 每次 commit | 阻止合并 | `make verify` |
| 空图谱降级 | `literature_entries=[]` 时 `citation_graph.entries=[]`、`references_list=[]`、`export_docx` 不渲染 thebibliography | 100% | `agent/tests/test_citation_graph.py` + `test_export_docx.py` | 每次 commit | 阻止合并 | `make verify` |
| NodeResult 协议对齐 | `CitationGraphOutput` / `ReferencesOutput` 字段集 ⊆ `EconPaperState.__annotations__` | 100% | `agent/tests/test_schema_consistency.py` 追加两节点 | 每次 commit | 阻止合并 | `make verify` |
| thebibliography 渲染 | `references_list` 非空时 `latex_source` 含 `\begin{thebibliography}` + `\bibitem` | 100% | `agent/tests/test_export_docx.py` 新增用例 | 每次 commit | 阻止合并 | `make verify` |

## 8. Decision Table

| Decision | Default | Rejected Alternatives | Exception Conditions |
| --- | --- | --- | --- |
| **A. 引用编号按 `(year, title)` 升序分配** | ✅ 采纳 | 1. 按检索顺序（不稳定，依赖 mock 顺序）；2. 按字母序（缺年份维度，不符学术规范）；3. 按 relevance_score（relevance 是 mock 估算，不可靠） | DOI 缺失时 fallback 到 title 作 key |
| **B. `citation_graph` schema：`{entries, edges, indices}`** | ✅ 采纳 | 1. 用 networkx Graph 对象（不可序列化，LangGraph state 需 JSON-friendly）；2. 只存 entries + indices（无 edges 预留，Stage 2 需改 schema） | Stage 2 `edges` 元素 schema 可扩展，但顶层三键不变 |
| **C. APA 格式简化版（作者 > 3 用 et al.，DOI 拼 URL）** | ✅ 采纳 | 1. 完整 APA 7th（实现复杂，需处理期刊名/卷期/页码，Stage 1 缺数据）；2. GB/T 7714（中文规范，但英文文献适配差）；3. Chicago（与经济学主流 APA 不符） | 中文作者原样输出（不做"姓-名"反转） |
| **D. `build_citation_graph` 插在 `search_literature` 后、`generate_outline` 前** | ✅ 采纳 | 1. 插在 `generate_outline` 后（大纲节点无法消费编号）；2. 插在 `export_docx` 前（来不及供 generate_chapter 用） | `literature_entries=[]` 时返回空图谱，下游降级 |
| **E. `generate_references` 插在 `translate_code` 后、`export_docx` 前** | ✅ 采纳 | 1. 插在 `export_docx` 内（节点职责单一原则）；2. 插在 `build_citation_graph` 后（太早，references 可能随章节内容变化——Stage 1 不涉及，但预留位置） | `citation_graph` 缺失时返回空列表 |
| **F. thebibliography 追加在 `\end{document}` 前** | ✅ 采纳 | 1. 用 BibTeX + `.bib` 文件（需额外编译步骤，latexmk 已支持但复杂度高）；2. 在每章节末尾插入引用（不符学术规范） | `references_list=[]` 时不渲染 thebibliography 环境 |

## 9. Stage 切分

### Stage 1 — 图谱构建 + 参考文献列表 + LaTeX 渲染（本 ADR 范围）

1. 在 `agent/state.py` 的 `EconPaperState` 新增 `citation_graph`、`references_list`、`citation_indices` 字段（见 §10）；
2. 在 `agent/protocols.py` 新增 `CitationEntry`、`CitationGraphOutput`、`ReferencesOutput` TypedDict（见 §10）；
3. 新建 `agent/nodes/citation_graph.py`，实现 `build_citation_graph(state) -> CitationGraphOutput`（签名见 §11）；
4. 新建 `agent/nodes/generate_references.py`，实现 `generate_references(state) -> ReferencesOutput` + 模块级 `_format_apa(entry) -> str`；
5. 在 `graph.py` 的 `build_graph()` 中：`add_node("build_citation_graph", build_citation_graph)`、`add_node("generate_references", generate_references)`；边改动见 §11.3；
6. 修改 `agent/nodes/export_docx.py`：渲染 `references_list` 为 `\begin{thebibliography}{N} \bibitem{[i]} ... \end{thebibliography}`，追加在 `latex_source` 末尾（`\end{document}` 前）；
7. 新增 `agent/tests/test_citation_graph.py`：空图谱、排序、DOI fallback；
8. 新增 `agent/tests/test_generate_references.py`：空列表、APA 格式、et al.、排序；
9. 更新 `agent/tests/test_schema_consistency.py`：`NODES` 追加两节点；
10. 跑 `make verify`，全绿。

**Stage 1 验收**：`literature_entries` 非空时 `export_docx` 产出的 `latex_source` 含 `\begin{thebibliography}` 且每个 `\bibitem` 编号连续；空列表时不渲染 bibliography 环境。

### Stage 2 — 引用关系边 + Semantic Scholar citations API（follow-up）

1. `build_citation_graph` 扩展：调 Semantic Scholar citations API 填充 `edges`（`{from: doi, to: doi}`）；
2. `edges` 用于 `generate_chapter` 的 lit_review prompt（按引用关系组织叙述）；
3. 新增 `agent/tests/test_citation_edges.py`：mock API，断言 edges 结构；
4. 跑 `make verify`，全绿。

### Stage 3 — 正文引用标记 `[1][2]` 自动插入（follow-up）

1. 修改 `agent/prompts/lit_review.py`：渲染 `citation_indices` 进 prompt，要求 LLM 在叙述中插入 `[1][2]` 标记；
2. `generate_chapter` 的 lit_review 模板扩展：把 `citation_indices` 作为 render kwargs 传入；
3. 新增 `agent/tests/test_citation_markers.py`：断言正文含 `[1]` 等标记；
4. 跑 `make verify`，全绿。

## 10. 需要补进 EconPaperState 的新字段

在 `agent/state.py` 的 `EconPaperState` 中新增（遵循 `total=False` 约定）：

```python
# ADR-0009: 引用图谱
citation_graph: Optional[Any]  # {entries: [...], edges: [{from, to}], indices: {doi: int}}
references_list: List[Any]  # 最终参考文献列表 [{index, text, doi, entry}]
citation_indices: Dict[str, int]  # doi → 引用编号 [1] [2] ...
```

配套 TypedDict（新建于 `agent/protocols.py`）：

```python
class CitationEntry(TypedDict, total=False):
    """参考文献条目（含引用编号）。"""
    entry: LiteratureEntry  # 原文献
    citation_index: int  # [1] [2] ...
    cited_in_chapters: List[int]  # 在哪些章节被引用


class CitationGraphOutput(TypedDict, total=False):
    """build_citation_graph 节点返回值。"""
    citation_graph: Any
    citation_indices: Dict[str, int]


class ReferencesOutput(TypedDict, total=False):
    """generate_references 节点返回值。"""
    references_list: List[Any]
```

## 11. 新 graph 流转

### 11.1 流转图

```
START → upload_data → clean_data → generate_title → set_direction
      → search_literature → build_citation_graph（新增）→ generate_outline
      → generate_chapter（6 章循环 + review）
      → translate_code → generate_references（新增）→ export_docx → END
```

### 11.2 节点函数签名

```python
# agent/nodes/citation_graph.py
def build_citation_graph(state: EconPaperState) -> CitationGraphOutput:
    """构建引用图谱。

    1. 读 literature_entries；
    2. 按 (year, title) 升序排序，分配 [1], [2], ...；
    3. 编号 key 优先 doi，缺失时 fallback title；
    4. edges 当前为空（Stage 2 接 Semantic Scholar citations API）；
    5. 返回 citation_graph + citation_indices。
    """


# agent/nodes/generate_references.py
def _format_apa(entry: Any) -> str:
    """APA 格式化单条参考文献。

    - 作者 > 3 用 et al.；
    - DOI 拼成 https://doi.org/{doi}；
    - 中文作者原样输出。
    """

def generate_references(state: EconPaperState) -> ReferencesOutput:
    """生成参考文献列表。

    1. 读 citation_graph（build_citation_graph 产出）；
    2. 按引用编号顺序格式化；
    3. 返回 references_list。
    """
```

### 11.3 `build_graph()` 改动点

```python
# 新增节点
builder.add_node("build_citation_graph", build_citation_graph)
builder.add_node("generate_references", generate_references)

# 边改动
# 原：builder.add_edge("search_literature", "generate_outline")
# 新：
builder.add_edge("search_literature", "build_citation_graph")
builder.add_edge("build_citation_graph", "generate_outline")

# 原：builder.add_edge("translate_code", "export_docx")
# 新：
builder.add_edge("translate_code", "generate_references")
builder.add_edge("generate_references", "export_docx")
```

### 11.4 `export_docx` LaTeX 渲染改动

在 `export_docx` 节点渲染完模板后，若 `state["references_list"]` 非空，则在 `latex_source` 的 `\end{document}` 前插入：

```latex
\begin{thebibliography}{99}
\bibitem{[1]} Smith (2023). Test. https://doi.org/10.1/x
\bibitem{[2]} ...
\end{thebibliography}
```

空列表时不插入（保持既有 LaTeX 源码不变）。

## Exceptions

- **`literature_entries` 缺失或为空**：`build_citation_graph` 返回 `{"citation_graph": {"entries": [], "edges": [], "indices": {}}, "citation_indices": {}}`，下游 `generate_references` 返回 `{"references_list": []}`，`export_docx` 不渲染 thebibliography。
- **`citation_graph` 缺失**：`generate_references` 返回 `{"references_list": []}`，`export_docx` 不渲染 thebibliography。
- **DOI 缺失**：`build_citation_graph` 用 `title` 作 `citation_indices` 的 key；`_format_apa` 不输出 `https://doi.org/...` 后缀。
- **作者列表缺失**：`_format_apa` 输出 `Unknown` 作为作者占位。
- **`references_list` 为空**：`export_docx` 不追加 thebibliography 环境，`latex_source` 与既有行为一致。

## Follow-Up Routes

- **Stage 2 — Semantic Scholar citations API**：填充 `citation_graph.edges`，支持引用关系追踪。
- **Stage 3 — 正文引用标记 `[1][2]` 自动插入**：修改 `generate_chapter` 的 `lit_review` prompt，消费 `citation_indices`。
- **ADR 0010**（待评估）：参考文献样式抽象（GB/T 7714 / Chicago / APA 切换）。
- **ADR 0011**（待评估）：BibTeX 导出（`.bib` 文件生成，支持 LaTeX 标准引用工作流）。
