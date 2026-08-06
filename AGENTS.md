# Empirical Paper Workbench — Project Instructions

本文件约束 `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板`（empirical-paper-workbench）及其子目录。

## Product identity（先读）

- 产品：`docs/PRODUCT.md` — **Continuous Empirical Loop**（全自动：设计→估计→成文→复现→修订）
- Agent 身份：`SOUL.md`
- 人入口：`README.md`
- 状态：`WORKFLOW_STATUS.md`（只记现在，无 P 朝代）
- 编排 SSOT：`runtime/continuous_loop.py`（内环 `runtime/full_pipeline.py`）
- **默认 LLM：Grok 4.5**（`provider_id=grok` · `docs/SETUP_GROK.md`）。开发/测试真实调用一律 Grok 4.5，禁止默默退回 MiniMax。

**禁止**把已删除的 product-control / P0–P18 /「半成品+红标品牌」叙事当产品定义。  
审计与质量门是 loop 内刹车，不是首页哲学。

## 默认工作方式：BDD + TDD

在本项目中，凡是新增功能、修复行为缺陷、调整产品流程、改变 API 契约或修改用户可见交互，默认采用 BDD + TDD。不要一上来写实现代码。

### 第一阶段：BDD 行为对齐

- 先不要写实现代码。
- 先把需求拆成 3-8 条可审查的 BDD 行为用例。
- 每条用例必须使用 Given / When / Then。
- 每条用例必须用中文说明它验证的业务规则。
- 同时列出需要用户确认的边界条件。
- 如果需求有歧义，先问问题，不要自行补设定。

### 第二阶段：TDD 测试

- 等用户确认 BDD 后，再写测试代码。
- 每条测试都必须能对应到某条 BDD 行为。
- 测试名或注释必须说明业务含义。
- 写完测试后先运行，确认测试失败。
- 失败原因必须是功能尚未实现，而不是测试写错、环境错误或 fixture 错误。

### 第三阶段：实现

- 测试确认后，再写生产代码。
- 不要修改已确认的测试，除非用户明确同意。
- 只写让测试通过的最小实现。
- 不要为了通过测试而削弱测试。
- 不要顺手重构无关代码。
- 每次修改后运行相关测试。
- 如果测试失败，优先修实现，不要削弱测试。

### 第四阶段：验收

交付时必须说明：

- 实现了哪些 BDD 行为。
- 哪些测试覆盖了这些行为。
- 运行过哪些测试命令。
- 哪些边界还没有覆盖。
- 用户可以怎样手动验收。

最终交付格式：

```text
## 行为覆盖
- [x] 行为 1：...
- [x] 行为 2：...
- [ ] 未覆盖行为：...

## 测试覆盖
- 测试文件：...
- 运行命令：...
- 结果：...

## 实现范围
- 修改了哪些文件。
- 每个文件为什么需要改。

## 手动验收
1. ...
2. ...
3. ...

## 剩余风险
- ...
```

### 例外

- 纯只读检查、项目状态汇报、命令输出解释、简单文案整理、无行为变化的文档记录，可以不进入完整 BDD/TDD。
- 紧急恢复或阻断性故障可先做最小止血，但必须在最终说明中标记跳过了哪些 BDD/TDD 阶段以及原因。

## Agent skills

Matt Pocock 的工程 skills（vendored at `~/.trae-cn/vendor/mattpocock-skills/`）在本仓库按下列配置生效。首次使用 `/to-tickets`、`/to-spec`、`/wayfinder`、`/triage`、`/implement` 等 skill 前需先读完此区块指向的 docs。

### Issue tracker

Local markdown tracker — issues/specs 作为 markdown 文件存放在 `.scratch/<feature-slug>/`，不使用 `gh`/`glab`。wayfinder 用 `.scratch/<effort>/map.md` + 子 ticket 文件。See `docs/agents/issue-tracker.md`.

### Domain docs

Single-context layout — 一个根 `CONTEXT.md` + `docs/adr/`。`CONTEXT-MAP.md` 不存在；如未来出现 monorepo 信号再切 multi-context。See `docs/agents/domain.md`.

## Lessons

- **Manuscript body is human academic prose only (2026-08-06):** Never put repo paths, `(证据：tables/...)`, claim register IDs, Continuous Loop / integrity / package jargon, or JSON/CSV filenames in the paper body or PDF front matter. Evidence binding lives only in claim register, Results JSON, and replication. Prefer `course_paper_builder` as primary writer; reject LLM polish that reintroduces path leaks.
- **Literature must be DOI-verified before author-year cites (2026-08-06):** Use `runtime/literature_pack.py` (Crossref) → `references.bib` + verified CSV + contribution matrix. Writing may cite only verified entries. Never paste placeholder seeds or invent author/year/journal. `verified_count=0` means no formal bibliography claims in the body. Style failures are hard reds, not "extra craft points".
