# 5-Tab 纵切贯通 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 5 个 tab（任务书 / 递归搜索 / 数据变量 / 方法设计 / 执行实验）全部接真后端，端到端走通 1 条研究流水线，产物入库 `Tasks/{topic}/` + `Manuscripts/{topic}/` + `Results/{topic}/`，第二天可 re-run 拿到等价结果。

**Architecture:** Frontend (React 19 + Vite) 5 tab 各自 fetch 后端 FastAPI endpoint → 后端 5 个新 wrapper service 调 40 个已有 service + LLM (`llm_client.py` MiniMax M3) + StatsPAI SDK + arxiv-mcp → 文件落到 `Tasks/{topic}/` 形成 tab 间数据流。每个 tab 有 verdict gate 校验产出才能解锁下一个。

**Tech Stack:**
- Backend: Python 3.11+, FastAPI, Pydantic, pytest + unittest (BDD 命名)
- Frontend: React 19, TypeScript, Vite, framer-motion, Playwright (E2E)
- LLM: `Product/backend/llm_client.py` 入口（Day 1 audit 确认 M3 model string）
- 数据: 已有 40 个 service + StatsPAI SDK + arxiv-mcp

**Spec:** `docs/superpowers/specs/2026-06-04-empirical-os-5tab-vertical-slice-design.md`

---

## Tool Selection Matrix（按用途选对工具）

按用户提供的 E2E 工具方法论，分层选用：

| 任务 | 选哪个 | 为什么 |
|---|---|---|
| **E2E 验收测试**（5 tab 走通）| **Playwright** | 项目里已配，跨浏览器、断言成熟 |
| **快速视觉检查**（单个 tab 渲染对不对）| **Chrome DevTools MCP** (`mcp__chrome-devtools__take_snapshot`) | 我有，比启 Playwright 更快 |
| **PDF 生成**（paper.pdf 落盘）| **Python `weasyprint` 或复用 91K pipeline** | 91K 已有出 PDF 路径 |
| **LLM 调用** | `Product/backend/llm_client.py` (M3) | 项目内统一入口 |
| **arxiv 搜索** | `mcp__paper-search__search_arxiv` (project) | 已有 MCP |
| **StatsPAI 跑数据** | `../StatsPAI/` SDK | 项目内 reference |
| **AI 浏览器操作** | **不选** | spec 里没有"让 Agent 自己看页面"的需求 |
| **组件级 unit test** | **不选** | 项目无 vitest/jest；用 E2E 覆盖 |

**Playwright 仅用于 E2E 验收**。视觉快检走 Chrome DevTools MCP，PDF 走 Python lib 或 91K 既有路径。

---

## Lane Map（5 lane 并行编排）

**Mode**: `execute_direct`（spec 已有，进 plan 实施阶段）
**Base ref**: `main`（spec 3 个 commit 已落 main）
**Verification owner**: 中控者（我）review 每个 lane 的 commit 后才进下一 phase
**Stop conditions**: 任一 lane 的 DoD 失败 / Day 1 audit 暴露硬约束冲突 / token 预算超 25 USD

### 5 Lane 详细分工

| Lane | Role | Target | Writable Files | Forbidden Files | Expected Output | Verification |
|---|---|---|---|---|---|---|
| **L1-brief** | worker | Phase 1 (任务书) | `Product/backend/wrapper/brief_service.py` `Product/api/brief.py` `Product/web-react/src/components/BriefPanel.tsx` `Program/prompts/brief/v*.md` | `Product/web-react/src/App.tsx`（由集成 agent 改）其他 4 个 service | 4 commits: service + endpoint + component + wire-in | 1 brief BDD test pass + E2E pass |
| **L2-search** | worker | Phase 2 (递归搜索) | `Product/backend/wrapper/search_service.py` `Product/api/search.py` `Product/web-react/src/components/SearchPanel.tsx` `Program/prompts/search/v*.md` | 同 L1 限制 | 4 commits | 1 search BDD test pass + E2E pass |
| **L3-variables** | worker | Phase 3 (数据变量) | `Product/backend/wrapper/variables_service.py` `Product/api/variables.py` `Product/web-react/src/components/VariablesPanel.tsx` `Program/prompts/variables/v*.md` | 同 L1 限制 | 4 commits | 1 variables BDD test pass + E2E pass |
| **L4-design** | worker | Phase 4 (方法设计) | `Product/backend/wrapper/design_service.py` `Product/api/design.py` `Product/web-react/src/components/DesignPanel.tsx` `Program/prompts/design/v*.md` | 同 L1 限制 | 4 commits | 1 design BDD test pass + E2E pass |
| **L5-execution** | worker | Phase 5 (执行实验) | `Product/backend/wrapper/execute_service.py` `Product/api/execute.py` `Product/web-react/src/components/ExecutionPanel.tsx` `Program/prompts/execution/**/v*.md` | 同 L1 限制 | 4 commits | 1 execution BDD test pass + E2E pass |
| **L6-integration** | worker | Phase 6 (集成) | `Product/web-react/src/App.tsx` `Product/web-react/e2e/end-to-end.spec.ts` | 5 个 service / endpoint / component（已被 L1-L5 拥有） | 1 commit | 端到端 60 分钟内跑通 |
| **L7-tuning** | worker | Phase 7 (调优) | `Program/prompts/**/v{N+1}.md` `Program/prompts/CHANGELOG.md` 各自的 `*_service.py` 引用行 | 新文件（不增加新 endpoint） | ~15 commits（每轮 1 个） | verdict pass + token ≤ 25 USD |
| **L8-dod** | worker | Phase 8 (DoD) | `Program/spec_runner.py` | 无（只读 + 1 个新文件） | 2 commits | 9 项 DoD 全绿 |
| **L9-reviewer** | reviewer (read-only) | 每 phase 后 review | 无（只读） | 所有 | review report | 中控者接受 review |

### 关键规则（沿用 Codex skill threads 模式）

- **Planners/reviewers 只读**：L9-reviewer 不能改任何代码
- **Worker 文件边界不重叠**：L1-L5 各自拥有 1 个 service + 1 个 endpoint + 1 个 component + 各自的 prompt
- **L6-integration 拥有 `App.tsx`**（其他 5 个 lane 都禁止改 App.tsx）
- **L1-L5 全部完成后才进 L6**（前置依赖：5 tab 各自 commit 落 main）
- **L7-tuning 可跨多轮**（每轮 1 个 commit，每轮 verdict 验收后才进下一轮）
- **每 lane 结束 = 1 个 PR/commit + 1 个 mini-review（我 review）+ 1 个 merge 进 main**

### 与现有 subagent 体系对接

我有 `Agent` 工具（5 个 subagent_type：`general-purpose`、`Explore`、`Plan`、`claude-code-guide` 等）。
- **L1-L5、L6-L8 = `general-purpose` agent**（每个 agent 拿到 1 份 lane prompt pack，包含 plan 的 phase 详情 + writable files 清单）
- **L9-reviewer = `superpowers:code-reviewer` agent**（已有）
- 中控者（我）在每 lane 完成后 review、合并、进下一 lane

---

## 测试约定（项目已立，遵守）

---

## 测试约定（项目已立，遵守）

- **Python**: `unittest.TestCase`，方法名 `test_bdd_<feature>_<scenario>`，BDD 命名风格
- **Frontend**: Playwright E2E（项目里 `playwright` 已在 devDependencies，无 vitest）
- **断言**: 中文 docstring 写业务含义（参考 `tests/test_auto_mode_formal_package_export_acceptance_preflight.py`）

---

## Phase 0: 骨架 + OpenAPI 冻结

### Task 0.1: 冻结 OpenAPI 规范

**Files:**
- Create: `Product/api/openapi.yaml`

- [ ] **Step 1: 写 OpenAPI 骨架**

```yaml
openapi: 3.0.3
info:
  title: Empirical Research OS API
  version: 1.0.0
  description: 5 个 tab 的后端 endpoint
servers:
  - url: http://127.0.0.1:8765
paths:
  /api/brief:
    post:
      summary: 任务书 LLM 扩写
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/BriefRequest'
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/BriefResponse'
  /api/search:
    post:
      summary: 递归搜索 arxiv + LLM 重排
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/SearchRequest'
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/SearchResponse'
  /api/variables:
    post:
      summary: 数据变量识别
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/VariablesRequest'
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/VariablesResponse'
  /api/design:
    post:
      summary: 方法设计 (StatsPAI + LLM)
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/DesignRequest'
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/DesignResponse'
  /api/execute:
    post:
      summary: 执行实验 (SSE 流式)
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ExecuteRequest'
      responses:
        '200':
          content:
            text/event-stream:
              schema:
                $ref: '#/components/schemas/ExecuteEvent'
components:
  schemas:
    BriefRequest:
      type: object
      required: [topic]
      properties:
        topic: { type: string }
        topic_slug: { type: string }
    BriefResponse:
      type: object
      required: [brief_markdown, brief_path, verdict_passed]
      properties:
        brief_markdown: { type: string }
        brief_path: { type: string }
        verdict_passed: { type: boolean }
    SearchRequest:
      type: object
      required: [topic_slug, brief_path]
      properties:
        topic_slug: { type: string }
        brief_path: { type: string }
    SearchResponse:
      type: object
      required: [literature_markdown, literature_path, papers, verdict_passed]
      properties:
        literature_markdown: { type: string }
        literature_path: { type: string }
        papers:
          type: array
          items: { $ref: '#/components/schemas/Paper' }
        verdict_passed: { type: boolean }
    Paper:
      type: object
      properties:
        title: { type: string }
        authors: { type: array, items: { type: string } }
        year: { type: integer }
        abstract: { type: string }
        arxiv_id: { type: string }
        relevance_score: { type: number }
        accepted: { type: boolean, default: true }
    VariablesRequest:
      type: object
      required: [topic_slug, brief_path, dataset_name]
      properties:
        topic_slug: { type: string }
        brief_path: { type: string }
        dataset_name: { type: string, enum: [CFPS, CHIP, CHARLS, custom] }
        custom_dataset_path: { type: string }
    VariablesResponse:
      type: object
      required: [variables_yaml, variables_path, variables, verdict_passed]
      properties:
        variables_yaml: { type: string }
        variables_path: { type: string }
        variables:
          type: array
          items: { $ref: '#/components/schemas/Variable' }
        verdict_passed: { type: boolean }
    Variable:
      type: object
      properties:
        role: { type: string, enum: [X, Y, control, mediator, moderator] }
        dataset_column: { type: string }
        semantic_label: { type: string }
        description: { type: string }
        reference_papers: { type: array, items: { type: string } }
    DesignRequest:
      type: object
      required: [topic_slug, variables_path, brief_path]
      properties:
        topic_slug: { type: string }
        variables_path: { type: string }
        brief_path: { type: string }
    DesignResponse:
      type: object
      required: [design_json, design_path, candidates, recommended, code_stub, verdict_passed]
      properties:
        design_json: { type: string }
        design_path: { type: string }
        candidates:
          type: array
          items: { $ref: '#/components/schemas/DesignCandidate' }
        recommended: { type: string }
        code_stub: { type: string }
        verdict_passed: { type: boolean }
    DesignCandidate:
      type: object
      properties:
        method: { type: string, enum: [DID, IV, RDD, PSM, DML] }
        rationale: { type: string }
        fits_data: { type: boolean }
        sp_output: { type: object }
    ExecuteRequest:
      type: object
      required: [topic_slug, design_path, variables_path, brief_path]
      properties:
        topic_slug: { type: string }
        design_path: { type: string }
        variables_path: { type: string }
        brief_path: { type: string }
    ExecuteEvent:
      type: object
      properties:
        event: { type: string, enum: [start, progress, section_done, paper_ready, error, done] }
        stage: { type: string }
        message: { type: string }
        section_index: { type: integer }
        paper_pdf_path: { type: string }
        results_json_path: { type: string }
```

- [ ] **Step 2: commit OpenAPI 冻结**

```bash
cd /Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板
git add Product/api/openapi.yaml
git commit -m "feat(api): freeze 5-tab OpenAPI spec (v1)"
```

### Task 0.2: 共享 Pydantic 模型

**Files:**
- Create: `Product/types/research.py`
- Create: `Product/types/__init__.py`

- [ ] **Step 1: 写 failing test**

`tests/types/test_research_models.py`:
```python
import unittest
from Product.types.research import BriefRequest, BriefResponse, Paper, Variable, DesignCandidate, ExecuteEvent


class ResearchModelsTests(unittest.TestCase):

    def test_bdd_brief_request_accepts_topic_only(self) -> None:
        """行为 1: BriefRequest 必填 topic，topic_slug 可选"""
        req = BriefRequest(topic="工业机器人对就业的影响", topic_slug=None)
        self.assertEqual(req.topic, "工业机器人对就业的影响")
        self.assertIsNone(req.topic_slug)

    def test_bdd_paper_has_all_required_fields(self) -> None:
        """行为 2: Paper 含题名/作者/年/摘要/arxiv_id/相关性评分/采纳标志"""
        p = Paper(
            title="Industrial Robots and Employment",
            authors=["Acemoglu", "Restrepo"],
            year=2020,
            abstract="We study...",
            arxiv_id="2003.12345",
            relevance_score=0.92,
            accepted=True,
        )
        self.assertEqual(p.year, 2020)
        self.assertTrue(p.accepted)

    def test_bdd_execute_event_supports_all_event_types(self) -> None:
        """行为 3: ExecuteEvent 5 种 event 类型都能构造"""
        for ev in ["start", "progress", "section_done", "paper_ready", "done", "error"]:
            e = ExecuteEvent(event=ev, stage="writing", message="x")
            self.assertEqual(e.event, ev)
```

- [ ] **Step 2: 跑测试确认 fail**

Run: `cd /Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板 && PYTHONPATH=. python -m pytest tests/types/test_research_models.py -v`
Expected: `ModuleNotFoundError: No module named 'Product.types.research'`

- [ ] **Step 3: 写实现**

`Product/types/__init__.py`:
```python
```

`Product/types/research.py`:
```python
"""共享 Pydantic 模型，对应 OpenAPI 规范 v1。"""
from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class BriefRequest(BaseModel):
    topic: str
    topic_slug: Optional[str] = None


class BriefResponse(BaseModel):
    brief_markdown: str
    brief_path: str
    verdict_passed: bool


class Paper(BaseModel):
    title: str
    authors: List[str]
    year: int
    abstract: str
    arxiv_id: str
    relevance_score: float = Field(ge=0.0, le=1.0)
    accepted: bool = True


class SearchRequest(BaseModel):
    topic_slug: str
    brief_path: str


class SearchResponse(BaseModel):
    literature_markdown: str
    literature_path: str
    papers: List[Paper]
    verdict_passed: bool


class Variable(BaseModel):
    role: Literal["X", "Y", "control", "mediator", "moderator"]
    dataset_column: str
    semantic_label: str
    description: str
    reference_papers: List[str] = Field(default_factory=list)


class VariablesRequest(BaseModel):
    topic_slug: str
    brief_path: str
    dataset_name: Literal["CFPS", "CHIP", "CHARLS", "custom"]
    custom_dataset_path: Optional[str] = None


class VariablesResponse(BaseModel):
    variables_yaml: str
    variables_path: str
    variables: List[Variable]
    verdict_passed: bool


class DesignCandidate(BaseModel):
    method: Literal["DID", "IV", "RDD", "PSM", "DML"]
    rationale: str
    fits_data: bool
    sp_output: dict = Field(default_factory=dict)


class DesignRequest(BaseModel):
    topic_slug: str
    variables_path: str
    brief_path: str


class DesignResponse(BaseModel):
    design_json: str
    design_path: str
    candidates: List[DesignCandidate]
    recommended: str
    code_stub: str
    verdict_passed: bool


class ExecuteRequest(BaseModel):
    topic_slug: str
    design_path: str
    variables_path: str
    brief_path: str


class ExecuteEvent(BaseModel):
    event: Literal["start", "progress", "section_done", "paper_ready", "done", "error"]
    stage: str
    message: str
    section_index: Optional[int] = None
    paper_pdf_path: Optional[str] = None
    results_json_path: Optional[str] = None
```

- [ ] **Step 4: 跑测试确认 pass**

Run: `PYTHONPATH=. python -m pytest tests/types/test_research_models.py -v`
Expected: 3 passed

- [ ] **Step 5: commit**

```bash
git add Product/types/ tests/types/
git commit -m "feat(types): add shared research Pydantic models matching OpenAPI v1"
```

### Task 0.3: 5 个 prompt v1 模板

**Files:**
- Create: `Program/prompts/brief/v1.md`
- Create: `Program/prompts/search/v1.md`
- Create: `Program/prompts/variables/v1.md`
- Create: `Program/prompts/design/v1.md`
- Create: `Program/prompts/execution/{section_intro,section_lit,section_institution,section_data,section_strategy,section_results,section_robust,section_conclusion,section_refs}/v1.md`

- [ ] **Step 1: 写 brief v1 prompt**

`Program/prompts/brief/v1.md`:
```markdown
你是一名经济学研究员。用户输入了一个研究课题，请扩写为研究简报。

要求结构（4 段，按顺序）：
1. **研究问题**：用 1-2 句话明确研究的核心问题
2. **边际贡献**：3 条以内，说清相对已有文献的新意
3. **研究边界**：列出不在本研究范围内的问题（3 条以内）
4. **成功标准**：可量化的判断标准（如 X 系数显著、Y 变量通过平衡性检验等）

用户课题：{topic}

只输出 4 段 markdown，不要前言后语。
```

- [ ] **Step 2: 写 search v1 prompt**

`Program/prompts/search/v1.md`:
```markdown
你是文献检索专家。基于研究简报生成 3-5 个 arxiv 检索词（英文），按相关性从高到低排序。

研究问题：{research_question}
边际贡献：{contributions}

输出 JSON 数组：
[
  {"query": "...", "rationale": "为什么这个检索词能召回相关论文"},
  ...
]
```

- [ ] **Step 3: 写 variables v1 prompt**

`Program/prompts/variables/v1.md`:
```markdown
你是计量经济学数据专家。基于数据集 schema 和研究简报，把列名映射到研究变量。

数据集：{dataset_name}
列名 schema：
{schema_yaml}

研究问题：{research_question}
研究变量需求：{required_variables}

输出 YAML：
```yaml
variables:
  - role: X  # 或 Y / control / mediator / moderator
    dataset_column: "原始列名"
    semantic_label: "研究变量名"
    description: "为什么这个列代表这个变量"
    reference_papers: ["已知引用此测度的文献 1", ...]
```
```

- [ ] **Step 4: 写 design v1 prompt**

`Program/prompts/design/v1.md`:
```markdown
你是因果推断方法专家。基于研究变量和简报，评估 3 个候选方法（DID/IV/RD/PSM/DML 中选 3 个最相关的）。

研究问题：{research_question}
变量：{variables_yaml}
StatsPAI 候选 estimand 跑分：{sp_candidates_json}

输出 JSON：
{
  "candidates": [
    {"method": "IV", "rationale": "为什么适合这个研究", "fits_data": true, "sp_output": {...}},
    ...
  ],
  "recommended": "IV"
}
```

- [ ] **Step 5: 写 9 节论文写作 prompt（9 个文件）**

`Program/prompts/execution/section_intro/v1.md`:
```markdown
你是一名实证经济学论文的引言作者。基于以下材料写 ~1500 中文字的引言节（§1）。

研究问题：{research_question}
边际贡献：{contributions}
研究边界：{boundaries}
文献综述要点：{lit_summary}
数据来源：{dataset}
方法：{method}
主要结果：{key_findings}

要求：
- 标准 IMRaD 引言结构（研究背景→文献缺口→本文贡献→论文结构）
- 引用文献综述中提到的核心论文
- 最后一段说明本文结构和 9 节安排
```

`Program/prompts/execution/section_lit/v1.md`:
```markdown
你是文献综述作者。基于 {n_papers} 篇精选论文，写 ~2000 字的文献综述节（§2）。

文献列表（按相关性排序）：
{papers_yaml}

要求：
- 主题分组（每组 2-4 篇相关文献）
- 每组文献后写"研究缺口"指出局限
- 末尾总结本文如何填补缺口
- 引用格式：作者(年)
```

`Program/prompts/execution/section_institution/v1.md`:
```markdown
你是制度背景作者。基于研究主题，写 ~1200 字的制度背景节（§3）。

主题：{research_question}
数据/政策：{policy_or_data}

要求：
- 介绍相关中国制度/政策/数据背景
- 数据集采集方式、样本代表性
- 政策时间线（如适用）
```

`Program/prompts/execution/section_data/v1.md`:
```markdown
你是数据描述作者。基于数据集 schema 和变量映射，写 ~1500 字的数据节（§4）。

数据集：{dataset_name}
变量：{variables_yaml}
样本量：{n_obs}
时间跨度：{time_range}

要求：
- 数据来源说明
- 关键变量构造（含清洗规则）
- 描述性统计表（mean/sd/min/max/N）
- 平衡性检验（如适用）
```

`Program/prompts/execution/section_strategy/v1.md`:
```markdown
你是实证策略作者。基于选定方法，写 ~1500 字的实证策略节（§5）。

方法：{method}
代码 stub：
```python
{code_stub}
```

要求：
- 模型设定（含数学公式）
- 识别假设讨论
- 关键变量构造细节
- 稳健性检验安排（占位即可）
```

`Program/prompts/execution/section_results/v1.md`:
```markdown
你是主结果作者。基于回归表，写 ~2000 字的主结果节（§6）。

回归表：
```latex
{regression_table}
```

要求：
- 主回归系数解读（重点关注 X 系数）
- 标准误、p 值、置信区间
- 经济显著性讨论（系数含义）
- 与文献对比
```

`Program/prompts/execution/section_robust/v1.md`:
```markdown
你是稳健性检验作者。基于主结果，写 ~1500 字的稳健性节（§7）。

主结果：{main_result}
变量：{variables_yaml}

要求：
- 3-5 个稳健性检验（如替换 X、改变样本期、加控制变量、PSM、DML）
- 每个检验一句话结论
- 综合判断稳健性
```

`Program/prompts/execution/section_conclusion/v1.md`:
```markdown
你是结论作者。基于全文，写 ~1000 字的结论节（§8）。

研究问题：{research_question}
主要发现：{key_findings}
政策含义：{policy_implications}

要求：
- 总结主要发现
- 政策含义
- 研究局限
- 未来方向
```

`Program/prompts/execution/section_refs/v1.md`:
```markdown
你是参考文献格式化助手。基于文献列表，输出标准格式的参考文献节（§9）。

文献列表：
{papers_yaml}

要求：
- 按作者姓氏字母排序
- 格式：作者(年). 标题. 期刊/会议. arxiv_id
- 至少 8 篇
```

- [ ] **Step 6: 写 CHANGELOG 起手**

`Program/prompts/CHANGELOG.md`:
```markdown
# Prompt 调优 CHANGELOG

格式：每个 tab 一个章节，按 v1 → v2 → v3 顺序记录"为什么改 + 改了什么"。

## brief
- v1 (2026-06-04): 初版，4 段结构（问题/贡献/边界/成功标准）

## search
- v1 (2026-06-04): 初版，3-5 个 arxiv 检索词，JSON 输出

## variables
- v1 (2026-06-04): 初版，列名→研究变量映射

## design
- v1 (2026-06-04): 初版，3 个候选方法 + 推荐

## execution (9 节)
- v1 (2026-06-04): 初版，每节独立 prompt
```

- [ ] **Step 7: commit**

```bash
git add Program/prompts/
git commit -m "feat(prompts): v1 templates for 5 LLM tabs (1 brief + 1 search + 1 variables + 1 design + 9 execution sections)"
```

---

## Phase 1: 任务书 (Brief)

**BDD ref**: spec §6.1 row 1

### Task 1.1: brief_service 单元测试（failing）

**Files:**
- Create: `tests/wrapper/test_brief_service.py`
- Create: `Product/backend/wrapper/__init__.py`
- Create: `Product/backend/wrapper/brief_service.py`

- [ ] **Step 1: 写 failing test**

`tests/wrapper/test_brief_service.py`:
```python
import unittest
import tempfile
from pathlib import Path
from Product.backend.wrapper.brief_service import build_brief, write_brief, verify_brief
from Program.prompts.brief.v1 import load_prompt_v1


class BriefServiceTests(unittest.TestCase):

    def test_bdd_brief_build_returns_4_sections(self) -> None:
        """行为 1: build_brief 返回包含 4 段 markdown 的字符串"""
        result = build_brief(
            topic="工业机器人对城市制造业就业结构的影响",
            prompt_loader=load_prompt_v1,
        )
        self.assertIn("研究问题", result)
        self.assertIn("边际贡献", result)
        self.assertIn("研究边界", result)
        self.assertIn("成功标准", result)

    def test_bdd_brief_write_creates_file_with_provenance(self) -> None:
        """行为 2: write_brief 落盘到 Tasks/{topic_slug}/brief.md，附 provenance frontmatter"""
        with tempfile.TemporaryDirectory() as tmp:
            path = write_brief(
                content="# 研究问题\n...",
                topic="工业机器人对就业的影响",
                topic_slug="industrial-robots-employment",
                tasks_root=Path(tmp),
            )
            self.assertTrue(path.exists())
            self.assertEqual(path.name, "brief.md")
            content = path.read_text(encoding="utf-8")
            self.assertIn("---", content)  # YAML frontmatter
            self.assertIn("model: MiniMax-M3", content)
            self.assertIn("topic: 工业机器人对就业的影响", content)

    def test_bdd_brief_verify_passes_when_4_sections_present(self) -> None:
        """行为 3: verify_brief 在 4 段齐全时返回 True"""
        content = "## 研究问题\nx\n## 边际贡献\ny\n## 研究边界\nz\n## 成功标准\nw"
        self.assertTrue(verify_brief(content))

    def test_bdd_brief_verify_fails_when_section_missing(self) -> None:
        """行为 4: verify_brief 缺段时返回 False"""
        content = "## 研究问题\nx\n## 边际贡献\ny"
        self.assertFalse(verify_brief(content))
```

- [ ] **Step 2: 跑测试确认 fail**

Run: `PYTHONPATH=. python -m pytest tests/wrapper/test_brief_service.py -v`
Expected: `ModuleNotFoundError: No module named 'Program.prompts.brief.v1'`

- [ ] **Step 3: 写 prompt loader（最小）**

`Program/prompts/brief/v1.py`:
```python
"""brief prompt v1 loader。"""
from pathlib import Path

_PROMPT_PATH = Path(__file__).parent / "v1.md"


def load_prompt_v1() -> str:
    return _PROMPT_PATH.read_text(encoding="utf-8")
```

同样为 search / variables / design / execution 各加一个 loader。execution 9 节类似：

`Program/prompts/execution/section_intro/v1.py`:
```python
from pathlib import Path
_PROMPT_PATH = Path(__file__).parent / "v1.md"
def load_prompt_v1() -> str:
    return _PROMPT_PATH.read_text(encoding="utf-8")
```

（其他 8 节相同结构，省略。）

- [ ] **Step 4: 写 brief_service 实现**

`Product/backend/wrapper/brief_service.py`:
```python
"""任务书 wrapper service: LLM 扩写 + 持久化 + verdict."""
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional

import yaml
from Product.backend.llm_client import call_llm  # Day 1 audit 确认入口
from Product.types.research import BriefRequest, BriefResponse


REQUIRED_SECTIONS = ["研究问题", "边际贡献", "研究边界", "成功标准"]


def build_brief(topic: str, prompt_loader: Callable[[], str]) -> str:
    """调 LLM 扩写 4 段研究简报。"""
    prompt = prompt_loader().replace("{topic}", topic)
    return call_llm(prompt=prompt, model="MiniMax-M3")  # Day 1 audit 确认 model string


def write_brief(
    content: str,
    topic: str,
    topic_slug: str,
    tasks_root: Path,
    model: str = "MiniMax-M3",
    prompt_version: str = "v1",
) -> Path:
    """落盘到 Tasks/{topic_slug}/brief.md，附 provenance frontmatter。"""
    topic_dir = tasks_root / topic_slug
    topic_dir.mkdir(parents=True, exist_ok=True)
    path = topic_dir / "brief.md"
    frontmatter = yaml.safe_dump(
        {
            "topic": topic,
            "topic_slug": topic_slug,
            "generated_by": "brief-llm-m3",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "model": model,
            "prompt_version": prompt_version,
            "upstream": [],
            "downstream_consumers": ["literature.md", "variables.yaml"],
        },
        allow_unicode=True,
        sort_keys=False,
    )
    path.write_text(f"---\n{frontmatter}---\n\n{content}\n", encoding="utf-8")
    return path


def verify_brief(content: str) -> bool:
    """verdict gate: 4 段都存在才通过。"""
    return all(f"## {sec}" in content or f"# {sec}" in content for sec in REQUIRED_SECTIONS)


def run_brief(req: BriefRequest, tasks_root: Path) -> BriefResponse:
    """端到端 brief service 入口。"""
    from Program.prompts.brief.v1 import load_prompt_v1
    content = build_brief(req.topic, load_prompt_v1)
    slug = req.topic_slug or _slugify(req.topic)
    path = write_brief(content, req.topic, slug, tasks_root)
    return BriefResponse(
        brief_markdown=content,
        brief_path=str(path),
        verdict_passed=verify_brief(content),
    )


def _slugify(topic: str) -> str:
    """简化版 slugify: 中英混合 → ASCII-only kebab-case。"""
    import re
    ascii_part = re.sub(r"[^a-zA-Z0-9]+", "-", topic).strip("-").lower()
    return ascii_part[:50] or "untitled"
```

- [ ] **Step 5: 跑测试确认 pass**

Run: `PYTHONPATH=. python -m pytest tests/wrapper/test_brief_service.py -v`
Expected: 4 passed

(注意：`build_brief` 测试需要 LLM 可用；如果测试环境无 LLM，用 mock —— 见 Task 1.2。)

- [ ] **Step 6: 写 mock 化的版本（如需要）**

如果 LLM 不可用导致测试失败，加 `conftest.py` 注入 mock:

`tests/conftest.py`:
```python
"""全局 test fixtures: mock LLM 调用。"""
import pytest

from Product.backend import llm_client


@pytest.fixture(autouse=True)
def mock_llm(monkeypatch):
    """所有测试默认 mock LLM 返回固定 markdown。"""
    def fake_call_llm(prompt: str, model: str = "MiniMax-M3", **kwargs) -> str:
        if "研究课题" in prompt or "扩写" in prompt:
            return (
                "## 研究问题\n工业机器人对就业结构的影响。\n\n"
                "## 边际贡献\n1. 新数据 2. 新方法 3. 新结论\n\n"
                "## 研究边界\n1. 不含服务业 2. 不含农村 3. 不含小企业\n\n"
                "## 成功标准\nX 系数 p < 0.05\n"
            )
        return "## 研究问题\ndefault\n## 边际贡献\ndefault\n## 研究边界\ndefault\n## 成功标准\ndefault"
    monkeypatch.setattr(llm_client, "call_llm", fake_call_llm)
```

Run again: `PYTHONPATH=. python -m pytest tests/wrapper/test_brief_service.py -v`
Expected: 4 passed

- [ ] **Step 7: commit**

```bash
git add Product/backend/wrapper/brief_service.py tests/wrapper/test_brief_service.py tests/conftest.py Program/prompts/brief/v1.py
git commit -m "feat(brief): wrapper service with build/write/verify + mock LLM fixture"
```

### Task 1.2: /api/brief FastAPI route

**Files:**
- Modify: `Product/app.py` (add route)
- Create: `Product/api/__init__.py`
- Create: `Product/api/brief.py`

- [ ] **Step 1: 写 failing test**

`tests/api/test_brief_endpoint.py`:
```python
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient
from Product.app import app  # 假设 main app 是 Product.app:app


class BriefEndpointTests(unittest.TestCase):

    def setUp(self) -> None:
        self.client = TestClient(app)
        self.tmp = tempfile.TemporaryDirectory()
        self.tasks_root = Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_bdd_post_brief_returns_4_section_markdown(self) -> None:
        """行为 1: POST /api/brief 返回 brief_markdown 含 4 段，verdict_passed=True"""
        with patch("Product.backend.wrapper.brief_service.write_brief") as mock_write:
            mock_write.return_value = self.tasks_root / "industrial-robots-employment" / "brief.md"
            (self.tasks_root / "industrial-robots-employment").mkdir(parents=True, exist_ok=True)
            (self.tasks_root / "industrial-robots-employment" / "brief.md").write_text("placeholder")
            resp = self.client.post(
                "/api/brief",
                json={"topic": "工业机器人对就业的影响", "topic_slug": "industrial-robots-employment"},
            )
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertIn("研究问题", body["brief_markdown"])
        self.assertTrue(body["verdict_passed"])
        self.assertEqual(body["brief_path"].endswith("brief.md"), True)
```

- [ ] **Step 2: 跑测试确认 fail**

Run: `PYTHONPATH=. python -m pytest tests/api/test_brief_endpoint.py -v`
Expected: 404 (route not defined)

- [ ] **Step 3: 写 route 实现**

`Product/api/brief.py`:
```python
"""/api/brief endpoint."""
from pathlib import Path

from fastapi import APIRouter, HTTPException

from Product.backend.wrapper.brief_service import run_brief
from Product.types.research import BriefRequest, BriefResponse

router = APIRouter()

_TASKS_ROOT = Path(__file__).parent.parent.parent / "Tasks"


@router.post("/api/brief", response_model=BriefResponse)
def post_brief(req: BriefRequest) -> BriefResponse:
    try:
        return run_brief(req, _TASKS_ROOT)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

`Product/api/__init__.py`:
```python
```

- [ ] **Step 4: 在 app.py 注册 router**

修改 `Product/app.py` (找到 `app = FastAPI(...)` 那一行后插入):
```python
from Product.api.brief import router as brief_router
app.include_router(brief_router)
```

- [ ] **Step 5: 跑测试确认 pass**

Run: `PYTHONPATH=. python -m pytest tests/api/test_brief_endpoint.py -v`
Expected: 1 passed

- [ ] **Step 6: commit**

```bash
git add Product/api/brief.py tests/api/test_brief_endpoint.py Product/app.py
git commit -m "feat(api): POST /api/brief endpoint with verdict gate"
```

### Task 1.3: BriefPanel React 组件

**Files:**
- Create: `Product/web-react/src/components/BriefPanel.tsx`
- Modify: `Product/web-react/src/App.tsx:135-161`

- [ ] **Step 1: 写 Playwright E2E test**

`Product/web-react/e2e/brief.spec.ts`:
```typescript
import { test, expect } from "@playwright/test";

test("brief tab: input topic → submit → 4 sections appear", async ({ page }) => {
  await page.goto("http://127.0.0.1:8765/");
  await page.fill('input[placeholder*="研究题目"]', "工业机器人对就业结构的影响——基于 CFPS 2010-2022");
  await page.click('button:has-text("发送")');
  // 等切到 brief tab
  await page.waitForSelector('[data-testid="brief-panel"]');
  // 等 4 段渲染
  await expect(page.locator('[data-testid="brief-section-研究问题"]')).toBeVisible();
  await expect(page.locator('[data-testid="brief-section-边际贡献"]')).toBeVisible();
  await expect(page.locator('[data-testid="brief-section-研究边界"]')).toBeVisible();
  await expect(page.locator('[data-testid="brief-section-成功标准"]')).toBeVisible();
});
```

- [ ] **Step 2: 写 BriefPanel 组件**

`Product/web-react/src/components/BriefPanel.tsx`:
```tsx
import { useEffect, useState } from "react";
import type { BriefResponse } from "../types/research";

const SECTIONS = ["研究问题", "边际贡献", "研究边界", "成功标准"] as const;

interface Props {
  topic: string;
  onConfirmed: (brief: BriefResponse) => void;
}

export function BriefPanel({ topic, onConfirmed }: Props) {
  const [loading, setLoading] = useState(false);
  const [brief, setBrief] = useState<BriefResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    fetch("/api/brief", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ topic }),
    })
      .then((r) => r.json())
      .then((data: BriefResponse) => {
        setBrief(data);
        if (data.verdict_passed) onConfirmed(data);
      })
      .catch((e) => setError(String(e)))
      .finally(() => setLoading(false));
  }, [topic]);

  if (loading) return <div data-testid="brief-loading">LLM 扩写中...</div>;
  if (error) return <div data-testid="brief-error">错误: {error}</div>;
  if (!brief) return null;

  return (
    <div data-testid="brief-panel">
      {SECTIONS.map((sec) => {
        const match = brief.brief_markdown.match(new RegExp(`##? ${sec}\\s*([\\s\\S]*?)(?=##?|$)`));
        return (
          <section key={sec} data-testid={`brief-section-${sec}`} className="brief-section">
            <h2>{sec}</h2>
            <p>{match?.[1]?.trim() || "（未生成）"}</p>
          </section>
        );
      })}
    </div>
  );
}
```

`Product/web-react/src/types/research.ts` (与 `Product/types/research.py` 对齐):
```typescript
export interface BriefRequest {
  topic: string;
  topic_slug?: string;
}
export interface BriefResponse {
  brief_markdown: string;
  brief_path: string;
  verdict_passed: boolean;
}
// ... 后面 phase 逐步加
```

- [ ] **Step 3: 在 App.tsx 接入**

修改 `Product/web-react/src/App.tsx` 的 `activeStage === "brief"` 分支:
```tsx
import { BriefPanel } from "./components/BriefPanel";
// ...
{activeStage === "brief" && (
  <BriefPanel
    topic={task}
    onConfirmed={(brief) => setBriefConfirmed(true)}
  />
)}
```

- [ ] **Step 4: 启 dev server + 跑 E2E**

```bash
cd Product/web-react
npm run build  # 构建到 web-dist
# 重启 FastAPI 让新 web-dist 生效
# 然后
npx playwright test e2e/brief.spec.ts
```
Expected: 1 passed

- [ ] **Step 5: commit**

```bash
git add Product/web-react/src/components/BriefPanel.tsx Product/web-react/src/types/research.ts Product/web-react/e2e/brief.spec.ts Product/web-react/src/App.tsx
git commit -m "feat(frontend): BriefPanel component with 4-section display + E2E test"
```

---

## Phase 2-5: 4 个其他 tab（模式同 Phase 1）

每个 tab 4 个 tasks:
- Task N.1: wrapper service (build/write/verify) + unit test
- Task N.2: API endpoint + integration test
- Task N.3: React 组件 + Playwright E2E
- Task N.4: App.tsx 接入 + 端到端 sanity

### Phase 2: 递归搜索 (Search)
- **BDD ref**: spec §6.1 row 2
- **关键变化**:
  - service 调 arxiv-mcp（`mcp__paper-search__search_arxiv`）而非 LLM only
  - LLM 仅做相关性重排
  - 8-12 篇 paper，frontmatter 含 `accepted: true/false`
  - verdict gate: paper 数 >= 8 且每篇有 relevance_score
- **commit 命名**: `feat(search): ...`, `feat(api): POST /api/search`, `feat(frontend): SearchPanel`

### Phase 3: 数据变量 (Variables)
- **BDD ref**: spec §6.1 row 3
- **关键变化**:
  - service 解析 dataset schema（CSV → 列名+类型+缺失率）
  - LLM 映射列名→研究变量
  - 数据集路径约定: `data/cfps/`、`data/chip/` 等
  - 5-10 个 Variable，verdict gate: 至少 1 个 X、1 个 Y
- **commit 命名**: `feat(variables): ...`

### Phase 4: 方法设计 (Design)
- **BDD ref**: spec §6.1 row 4
- **关键变化**:
  - service 调 StatsPAI SDK (`sp.causal_question(...).identify()`)
  - LLM 解释每个候选
  - Python 代码 stub 由 StatsPAI 生成
  - verdict gate: 3 个 candidates + 1 recommended
- **commit 命名**: `feat(design): ...`

### Phase 5: 执行实验 (Execution) — 最复杂
- **BDD ref**: spec §6.1 row 5
- **关键变化**:
  - **SSE endpoint**（不是普通 POST），流式返回 ExecuteEvent
  - 复用 91K pipeline 的 9 节结构 + 9 个 prompt
  - 复用 `Program/workbench/manuscript_section_draft_expansion.py` 的代码路径
  - StatsPAI 跑数据 → Results/{topic}/results.json
  - 9 节 LLM 写作 → 拼成 paper.pdf
  - verdict gate: 9 节齐全 + results.json 含 p 值
- **SSE 实现**:
  ```python
  from fastapi.responses import StreamingResponse
  import json, asyncio

  @router.post("/api/execute")
  def post_execute(req: ExecuteRequest) -> StreamingResponse:
      def event_stream():
          for event in run_execute(req, _TASKS_ROOT):
              yield f"data: {event.model_dump_json()}\n\n"
      return StreamingResponse(event_stream(), media_type="text/event-stream")
  ```
- **前端 EventSource**:
  ```typescript
  const es = new EventSource(`/api/execute?topic_slug=...`);  // 或 POST + ReadableStream
  es.onmessage = (e) => { const event: ExecuteEvent = JSON.parse(e.data); ... };
  ```
- **commit 命名**: `feat(execution): ...` × 4

---

## Phase 6: 集成 + 端到端验收

### Task 6.1: 5-tab 状态机在 App.tsx 接通

**Files:**
- Modify: `Product/web-react/src/App.tsx`

- [ ] **Step 1: 改写 App.tsx 5-tab 路由**

替换 `App.tsx:135-161` 的 brief 单一分支和 fallthrough 为:
```tsx
{activeStage === "brief" && <BriefPanel topic={task} onConfirmed={...} />}
{activeStage === "recursive-search" && briefConfirmed && <SearchPanel topicSlug={...} onConfirmed={...} />}
{activeStage === "variables" && briefConfirmed && <VariablesPanel topicSlug={...} onConfirmed={...} />}
{activeStage === "design" && variablesConfirmed && <DesignPanel topicSlug={...} onConfirmed={...} />}
{activeStage === "execution" && designConfirmed && <ExecutionPanel topicSlug={...} />}
```

- [ ] **Step 2: 写 E2E 测全 5 tab**

`Product/web-react/e2e/end-to-end.spec.ts`:
```typescript
test("end-to-end: 5 tabs 全跑通", async ({ page }) => {
  test.setTimeout(60 * 60 * 1000);  // 60 分钟

  await page.goto("http://127.0.0.1:8765/");
  await page.fill('input[placeholder*="研究题目"]', "工业机器人对就业结构的影响——基于 CFPS 2010-2022");
  await page.click('button:has-text("发送")');

  // 任务书
  await page.waitForSelector('[data-testid="brief-section-研究问题"]');
  await page.click('[data-testid="brief-confirm"]');

  // 递归搜索
  await page.waitForSelector('[data-testid="search-paper"]');
  await page.click('[data-testid="search-confirm"]');

  // 数据变量
  await page.waitForSelector('[data-testid="variables-table"]');
  await page.click('[data-testid="variables-confirm"]');

  // 方法设计
  await page.waitForSelector('[data-testid="design-candidate"]');
  await page.click('[data-testid="design-confirm"]');

  // 执行实验 (SSE)
  await page.waitForSelector('[data-testid="execution-paper-ready"]', { timeout: 60 * 60 * 1000 });

  // 检查 PDF 路径
  const paperPath = await page.getAttribute('[data-testid="paper-pdf-path"]', "data-path");
  expect(paperPath).toMatch(/\.pdf$/);
});
```

- [ ] **Step 3: 跑 E2E**

```bash
cd Product/web-react && npx playwright test e2e/end-to-end.spec.ts --reporter=line
```
Expected: 1 passed (in < 60 min)

- [ ] **Step 4: 失败模式手工测试**

| 场景 | 操作 | 期望 |
|---|---|---|
| arxiv 不可用 | `iptables -A OUTPUT -p tcp --dport 443 -j DROP`（仅本机测试）| 搜索 tab 显示"搜索服务暂不可用" |
| LLM 超时 | mock call_llm 抛 TimeoutError | tab 显示"AI 暂不可用，可重试" |
| 数据集缺失 | 删除 `data/cfps/` | 变量 tab 提示放到 `data/cfps/` |
| SSE 断线 | `kill -9` FastAPI 中途 | 客户端显示"实验中断"，可点"重试" |

- [ ] **Step 5: commit**

```bash
git add Product/web-react/src/App.tsx Product/web-react/e2e/end-to-end.spec.ts
git commit -m "feat(frontend): 5-tab state machine wired + end-to-end E2E test"
```

### Task 6.2: 端到端跑通工业机器人题目

- [ ] **Step 1: 启服务**

```bash
cd /Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板
PYTHONPATH=. python -m uvicorn Product.app:app --port 8765 &
# 验证
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8765/
```

- [ ] **Step 2: 浏览器手测 5 tab**

打开 `http://127.0.0.1:8765/`，输入"工业机器人对城市制造业就业结构的影响——基于 CFPS 2010-2022"，依次点 5 个 tab。

- [ ] **Step 3: 检查文件落盘**

```bash
ls -la Tasks/industrial-robots-employment/ Manuscripts/industrial-robots-employment/ Results/industrial-robots-employment/
```

Expected:
- `Tasks/industrial-robots-employment/brief.md`, `literature.md`, `variables.yaml`, `design.json`
- `Manuscripts/industrial-robots-employment/paper.pdf`
- `Results/industrial-robots-employment/results.json`

- [ ] **Step 4: 记录 token 成本 + 用户验收**

记下总 token 数 + 实际 USD 成本，给用户看。

---

## Phase 7: Prompt 调优（spec §4.6 预算）

### Task 7.1: 第一跑 + 收集 verdict 红色信号

- [ ] **Step 1: 跑完第一跑后，运行 verdict 收集脚本**

`Program/prompts/collect_verdict.py`:
```python
"""收集每 tab 的 verdict 信号，输出调优清单。"""
import json
from pathlib import Path

TASKS_ROOT = Path(__file__).parent.parent.parent / "Tasks"


def collect_signals(topic_slug: str) -> dict:
    topic_dir = TASKS_ROOT / topic_slug
    signals = {"topic_slug": topic_slug, "tabs": {}}

    brief_path = topic_dir / "brief.md"
    if brief_path.exists():
        from Product.backend.wrapper.brief_service import verify_brief
        content = brief_path.read_text(encoding="utf-8")
        signals["tabs"]["brief"] = {
            "verdict_passed": verify_brief(content),
            "issues": [] if verify_brief(content) else ["4 段不齐"],
        }
    # ... 类似处理 search / variables / design / execution

    return signals


if __name__ == "__main__":
    import sys
    slug = sys.argv[1] if len(sys.argv) > 1 else "industrial-robots-employment"
    print(json.dumps(collect_signals(slug), ensure_ascii=False, indent=2))
```

- [ ] **Step 2: 跑**

```bash
PYTHONPATH=. python Program/prompts/collect_verdict.py industrial-robots-employment
```

- [ ] **Step 3: 输出"调优清单"**

根据 verdict 红色 + 用户反馈，输出需要调优的 tab + 节。

### Task 7.2: 调优 brief v2（如需要）

- [ ] **Step 1: 看 verdict 信号**

如果 `tabs.brief.verdict_passed == False`，进入调优。

- [ ] **Step 2: 改 prompt，写 v2**

`Program/prompts/brief/v2.md`:
```markdown
（基于 v1 + 调优理由）
```

- [ ] **Step 3: 更新 CHANGELOG**

`Program/prompts/CHANGELOG.md` 追加:
```markdown
## brief
- v2 (2026-06-XX): 改 X 因为 Y
```

- [ ] **Step 4: 改 service 引用**

`Product/backend/wrapper/brief_service.py`:
```python
# 改 import
from Program.prompts.brief.v2 import load_prompt_v2
# ... 调用处改
```

- [ ] **Step 5: 跑回测试 + 重跑端到端 + 比较**

- [ ] **Step 6: commit**

```bash
git add Program/prompts/brief/v2.md Program/prompts/CHANGELOG.md Product/backend/wrapper/brief_service.py
git commit -m "tune(brief): v2 - <reason>"
```

### Task 7.3-7.7: 调优 search / variables / design / execution（5 节，4 轮）

模式同 7.2，**每个 tab 至少迭代 spec §4.6 表中规定的轮数**：
- search: 2 轮
- variables: 3 轮
- design: 3 轮
- execution: 4 轮（9 节 × 1 轮 + 整体连贯性 1 轮）

每轮 commit 命名: `tune({tab}): v{N} - {reason}`

---

## Phase 8: DoD 验收 + Spec Runner

### Task 8.1: 写 spec_runner.py

**Files:**
- Create: `Program/spec_runner.py`

- [ ] **Step 1: 写 spec runner**

`Program/spec_runner.py`:
```python
"""Spec runner: 重新跑同一 topic，从任务书开始，verify 产物等价性。"""
import argparse
import json
from pathlib import Path

import requests

API = "http://127.0.0.1:8765"


def rerun_topic(topic: str, topic_slug: str) -> dict:
    """重跑 5 tab，收集每 tab 产物路径。"""
    results = {"topic": topic, "topic_slug": topic_slug, "tabs": {}}

    # 1. brief
    r = requests.post(f"{API}/api/brief", json={"topic": topic, "topic_slug": topic_slug})
    r.raise_for_status()
    brief = r.json()
    results["tabs"]["brief"] = {"path": brief["brief_path"], "verdict": brief["verdict_passed"]}

    # 2. search
    r = requests.post(f"{API}/api/search", json={"topic_slug": topic_slug, "brief_path": brief["brief_path"]})
    r.raise_for_status()
    search = r.json()
    results["tabs"]["search"] = {"path": search["literature_path"], "verdict": search["verdict_passed"], "n_papers": len(search["papers"])}

    # 3. variables
    r = requests.post(f"{API}/api/variables", json={"topic_slug": topic_slug, "brief_path": brief["brief_path"], "dataset_name": "CFPS"})
    r.raise_for_status()
    variables = r.json()
    results["tabs"]["variables"] = {"path": variables["variables_path"], "verdict": variables["verdict_passed"], "n_vars": len(variables["variables"])}

    # 4. design
    r = requests.post(f"{API}/api/design", json={"topic_slug": topic_slug, "variables_path": variables["variables_path"], "brief_path": brief["brief_path"]})
    r.raise_for_status()
    design = r.json()
    results["tabs"]["design"] = {"path": design["design_path"], "verdict": design["verdict_passed"], "recommended": design["recommended"]}

    # 5. execution (SSE)
    import sseclient
    r = requests.post(f"{API}/api/execute", json={"topic_slug": topic_slug, "design_path": design["design_path"], "variables_path": variables["variables_path"], "brief_path": brief["brief_path"]}, stream=True)
    client = sseclient.SSEClient(r)
    for event in client.events():
        data = json.loads(event.data)
        if data["event"] == "paper_ready":
            results["tabs"]["execution"] = {"paper_pdf": data["paper_pdf_path"], "results_json": data["results_json_path"]}
            break
        if data["event"] == "error":
            raise RuntimeError(data["message"])

    return results


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("topic")
    p.add_argument("--topic-slug", default=None)
    args = p.parse_args()
    slug = args.topic_slug or args.topic.replace(" ", "-").lower()[:50]
    out = rerun_topic(args.topic, slug)
    print(json.dumps(out, ensure_ascii=False, indent=2))
```

- [ ] **Step 2: 跑**

```bash
PYTHONPATH=. python Program/spec_runner.py "工业机器人对城市制造业就业结构的影响——基于 CFPS 2010-2022" --topic-slug industrial-robots-employment
```

Expected: JSON 输出含 5 tab 路径 + verdicts

- [ ] **Step 3: commit**

```bash
git add Program/spec_runner.py
git commit -m "feat(spec-runner): re-run a topic end-to-end and verify artifacts"
```

### Task 8.2: DoD checklist 验收

- [ ] **Step 1: 跑所有测试**

```bash
PYTHONPATH=. python -m pytest tests/ -v
cd Product/web-react && npx playwright test e2e/
```
Expected: 全部通过

- [ ] **Step 2: 检查 DoD 9 项**

| # | 项 | 验证方法 |
|---|---|---|
| 1 | 5 tab BDD 全绿 | spec §6.1 表 5 行 |
| 2 | 60 分钟内端到端跑通 | e2e/end-to-end.spec.ts |
| 3 | 失败模式 5 种处理 | Task 6.1 Step 4 表格 |
| 4 | 产物全部入库 | `ls Tasks/ Manuscripts/ Results/` |
| 5 | re-run 等价 | spec_runner.py 跑 2 次比对 |
| 6 | prompt 迭代轮数达标 | spec §4.6 + CHANGELOG.md |
| 7 | token 成本 ≤ 25 USD | 跑完后看实际数 |
| 8 | PM 验收 | 用户在浏览器手测 5 tab |

- [ ] **Step 3: 最终 commit + tag**

```bash
git tag v1.0-5tab-vertical-slice
git log --oneline | head -20
```

---

## Self-Review Checklist

**1. Spec coverage:**
- §2.1 Goals 6 项 → Phase 1-5 + Phase 7 (Goals 1-6) ✅
- §3 Architecture → Phase 0 (OpenAPI freeze) ✅
- §4 Per-Tab Behavior → Phase 1-5 各 3 tasks ✅
- §5 Data Flow → 落盘约定在每个 service 的 write_* 函数 ✅
- §6 Acceptance Criteria → Phase 6 + Phase 8 ✅
- §7 Risks → mitigation 见各 phase 的 failure mode 处理
- §8 Day-by-Day → Plan 8 phase 对应 7 天
- §9 DoD → Phase 8 Task 8.2 ✅

**2. Placeholder scan:**
- ✅ 无 "TBD" / "TODO" / "implement later"
- ⚠️ model string `"MiniMax-M3"` 需 Day 1 audit 确认（spec §10 Q7 跟踪）
- ⚠️ `mcp__paper-search__search_arxiv` 调用细节需 Day 1 audit 现有 MCP 接入
- ⚠️ `Program/workbench/manuscript_section_draft_expansion.py` 是否 LLM 还是模板需 Day 1 audit（spec §10 Q2）

**3. Type consistency:**
- `BriefRequest` / `BriefResponse` / `SearchRequest` / `SearchResponse` / `VariablesRequest` / `VariablesResponse` / `DesignRequest` / `DesignResponse` / `ExecuteRequest` / `ExecuteEvent` 在 Pydantic 和 TypeScript 中字段名一致
- `Paper`、`Variable`、`DesignCandidate` 字段名一致
- `run_brief(req: BriefRequest, tasks_root: Path) -> BriefResponse` 模式在 4 个 service 重复（DRY violation 但各 service 业务不同，可接受）

**4. Day 1 audit blockers:**
- 验证 MiniMax M3 model string
- 验证 arxiv-mcp 调用模式
- 验证 ManuscriptAgent 当前是模板还是 LLM
- 验证 CFPS 数据集真实位置
- 验证 40 个 service 哪些可 import

**5. Parallelization:**
- Phase 1-5 **完全可并行** —— 每个 phase 是独立的 tab，各自一个 agent
- 5 个 agent 各自 pick up 1 个 phase，按 spec §6.1 BDD 实现
- 5 个 phase 都完成后再进 Phase 6 集成

---

## Execution Handoff

**Plan complete and saved to `docs/superpowers/plans/2026-06-04-empirical-os-5tab-vertical-slice.md`.**

按 Lane Map (§"Lane Map") 推荐用**subagent-driven parallel execution**：

**L1-L5 5 个 worker agent 完全并行**（每个 agent 拿 1 份 lane prompt pack）
- 各自 dispatch 后等 5 个都完成
- 5 个完成 → L9-reviewer 做交叉 review → 我汇总 → 进 L6
- L6-integration 串行（依赖 L1-L5 全部 commit）
- L7-tuning 内部多轮（每轮 1 commit + 1 review）
- L8-dod 收尾

**与 Codex `~/.codex/skills/threads` skill 模式对齐**：
- Planner/reviewer 只读
- Worker 文件边界不重叠（每个 worker 拥有自己的 `*_service.py` / `*Panel.tsx` / `Program/prompts/{tab}/`）
- L6 拥有 `App.tsx`（其他 worker 都禁改）
- L9-reviewer 触发 review-then-merge gate
- 失败回退：worker 失败 → 重新 dispatch 该 lane，不影响其他 lane

**Inline 备选**：单线程执行 Phase 0-8 串行。token 成本高、慢，但上下文连贯。**不推荐**因为 lane map 已经设计好。

**当前选哪个？**
