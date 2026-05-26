# Paper Package Quality Standard

日期：2026-05-26

## 产品目标

本阶段把 CLI-first 实证工作流从“可执行报告”推进到“working paper 初稿论文包”。

论文包不是单个 PDF。一次完整运行至少应产出：

- 长篇论文草稿：Markdown / Quarto / PDF。
- 复现说明：README 或 reproduce script。
- 数据说明：数据来源、样本构造、变量定义和限制。
- 方法诊断：识别假设、前置条件、主要威胁和已做检查。
- 表图索引：正文引用到真实表图或结果 JSON。
- 审稿记录：method check、evidence check、prose/referee check 和 revision log。
- 导出清单：manifest 记录每个产物路径、证据等级和复现命令。

## 章节结构

第一版 working paper 初稿采用以下结构：

1. Title Page / Metadata
2. Abstract
3. Introduction
4. Literature and Contribution
5. Institutional Background / Theory / Context
6. Data and Measurement
7. Empirical Strategy / Research Design
8. Main Results
9. Robustness / Mechanisms / Heterogeneity
10. Conclusion
11. References
12. Appendix / Reproducibility Notes

## 长度与投稿档位

第一版不把“草稿层”和“正式层”混在一起。系统默认按 `general_working_paper` 检查；用户选择 `aer_like` 或 Supervisor 推荐并获得人工确认后，再启用 AEA/AER 风格硬门。

### general_working_paper

英文 working paper 草稿：

- 主文低于 7,000 words：判定为 `too_thin`。
- 9,000-14,000 words：第一版合理区间。
- 超过 16,000 words：提示压缩结构。

中文 working paper 草稿：

- 主文低于 10,000 字：判定为 `too_thin`。
- 12,000-18,000 字：第一版合理区间。
- 超过 22,000 字：提示压缩结构。

### aer_like

参考 AEA/AER 投稿约束，`aer_like` 目标不是立刻生成终稿，而是让论文包从一开始就按顶刊检查清单组织：

- 正文目标：30-38 页等价篇幅。
- 上限提醒：AER 常规正文、图表、参考文献和文内附录合计不超过 40 页。
- 摘要：必须支持 100 words 以内版本。
- 元数据：JEL codes 2-5 个，keywords 3-6 个。
- 复现材料：必须有 Data Availability Statement、复现 README、软件版本、主运行脚本、预期输出和数据来源说明。

PDF 是否生成成功只说明导出链路可用；论文质量由章节完整性、内容密度、证据绑定、方法诊断、文献闭环和审稿记录共同判断。

## 章节硬门槛

### Abstract

- 默认 100-180 words 或 180-300 中文字。
- 若目标选择 `aer_like`，摘要必须支持 100 words 以内版本。
- 必须包含问题、设计、主结果和贡献。

### Introduction

- 英文建议 1,800-3,000 words，约 4-6 页；中文建议 2,800-5,000 字。
- 必须包含：研究问题、动机、识别思路、主结果、贡献、roadmap。
- 前两段必须让读者知道这篇文章问什么、为什么重要、发现了什么。

### Literature and Contribution

- 英文建议 1,000-1,800 words；中文建议 1,500-3,000 字。
- 不能罗列文献。必须说明最接近文献、差异、数据增量、识别增量或机制增量。
- 每个引用必须能追到文献库、DOI、CNKI 条目或人工确认来源。

### Background / Theory / Context

- 英文建议 800-1,500 words，约 2-4 页；中文建议 1,200-2,500 字。
- 必须解释制度背景、政策环境、市场机制或理论预测。
- 必须说明为什么该背景支持后续识别设计。

### Data and Measurement

- 英文建议 800-1,500 words，约 2-3 页；中文建议 1,200-2,500 字。
- 必须包含：数据名、来源、覆盖期、样本单位、筛选规则、变量定义、缺失情况、描述统计表引用。
- 必须列明 outcome、treatment/key explanatory variable、controls、instrument/running variable if any。

### Empirical Strategy

- 英文建议 1,200-2,000 words，约 3-5 页；中文建议 1,800-3,500 字。
- 必须包含估计方程、变量定义、关键系数、识别假设、比较组、潜在偏误和对应检查。
- DID / IV / RDD / PSM / DML 等方法必须调用方法规范门生成前置检查和诊断清单。

### Main Results

- 英文建议 2,000-3,500 words，约 4-7 页；中文建议 3,000-6,000 字。
- 每个主表必须解释：方向、大小、单位、显著性、经济含义。
- 结论必须绑定真实结果产物，不能只绑定自然语言判断。

### Robustness / Mechanisms / Heterogeneity

- 英文建议 1,500-3,000 words，约 3-6 页；中文建议 2,200-5,000 字。
- 至少覆盖三类：替代变量或指标、替代样本或规格、placebo / pre-trend / sensitivity / falsification 中的一类。
- 机制和异质性必须与研究问题相关，不能为了填充而添加。

### Conclusion

- 英文建议 500-800 words；中文建议 800-1,300 字。
- 只总结已经在正文中出现的证据。
- 必须包含研究边界、政策含义或后续研究方向。

## AEA/AER-like 硬门与提醒

`aer_like` 下列规则进入 hard gate：

- 摘要超过 100 words。
- 缺少 JEL codes。
- 缺少 keywords。
- 缺少 Data Availability Statement。
- 缺少复现 README、主运行脚本、软件版本、预期输出或数据来源说明。
- 数据、表格、图、结论没有对应到 manifest / result json / citation / appendix / human review note。
- DID、IV、RDD、PSM、DML 等方法缺少对应 method gate 报告。

下列规则进入 warning：

- Introduction 没有明确 punchline。
- Literature 只是罗列文献，没有 closest paper 和 contribution matrix。
- Robustness 只是堆规格，没有对应识别威胁。
- 主文过度依赖补充附录。
- 结论加入正文没有展示的新估计。

## 文献闭环

文献综述不直接从模型记忆生成，必须经过四层证据：

1. `discover`：OpenAlex / Semantic Scholar / Google Scholar / CNKI / 本地 PDF / Zotero 找候选。
2. `normalize`：DOI、CNKI ID、标题、作者、年份、期刊统一。
3. `verify`：Crossref、Zotero、CNKI 导出或人工截图确认。
4. `bind`：写入 `verified_bibliography.csv` 和 `contribution_matrix.md`，再进入论文草稿。

CNKI 第一版定位为中文文献和中文期刊规范的人工辅助检索来源。可以记录检索词、筛选条件、截图、导出 RIS/TXT、人工确认笔记；不把不稳定网页抓取作为默认主路径。

## 内容密度门槛

每个章节必须包含本研究专属实体，而不是模板句：

- 数据集名。
- 国家、地区、行业、时期或政策事件。
- 变量名。
- 估计方法。
- 表、图、方程、文献或附录引用。

每个核心 claim 必须绑定至少一个证据位置：

- table
- figure
- equation
- result json
- citation
- appendix
- human review note

## LLM Supervisor 与执行器分工

本项目不是纯 Python 写论文，也不是把自然语言直接丢给模型自由发挥。正确主链路是：

```text
研究题目 / 已有状态 / 真实数据
-> Python 质量门和上下文打包
-> LLM Supervisor 制定研究路线和 Agent Task Queue
-> LiteratureAgent / DataAgent / MethodAgent / ExecutionAgent / ManuscriptAgent / ReviewerAgent 分工执行
-> StatsPAI / Python / StataMCP 等后端产出可复现结果
-> 质量门、方法门、文献门、审稿门再次检查
-> 人工确认后进入正式层和最终 PDF
```

各层职责如下：

- `local_codex` / LLM Supervisor：研究中控。负责解释题目、选择路线、拆任务、派子 Agent、提出变量和方法候选、规划递归搜索、生成章节草稿、组织审稿式修订。它写入的是草案层和 proposal 层。
- `StatsPAI`：Agent-native 计量和因果推断执行器。负责根据结构化 schema 调用 OLS、IV、DID、RDD、PSM、DML 等方法，返回机器可读结果、诊断、图表和发表级表格。
- `StataMCP` / `stata-code`：Stata 生态执行器。负责需要 Stata 命令、do-file 复现或 Stata 兼容结果时的运行和日志保存。
- `Python`：确定性本地执行层。负责数据画像、文件索引、质量报告、manifest、PDF 预检、轻量统计、测试和可复现脚本。
- `Journal / Method Skill Registry`：专家规则库。AER-Skills、方法规范和期刊检查清单先进入 proposal；canonical 规则只能人工 review 后合并。

这意味着 `Program/paper_quality.py` 和 `Program/paper_package.py` 的作用不是“自己写完论文”，而是把当前论文包差距变成可执行上下文。它们必须输出：

- `Results/json/paper_quality_report.json`：当前论文包质量门。
- `Results/json/paper_expansion_plan.json`：章节扩写和证据补齐计划。
- `Results/json/paper_supervisor_context.json`：交给 LLM Supervisor 的上下文包。
- `Manuscripts/generated/*paper_package_draft.md`：结构化草稿层，不覆盖正式稿。

## CLI 验收规则

`paper-package` 或后续同类命令必须输出一个 quality report：

```json
{
    "word_count": 0,
    "format_checks": {},
    "section_checks": {},
    "evidence_bindings": {},
  "citation_checks": {},
  "method_gate_checks": {},
  "revision_checks": {},
  "verdict": "ready_for_review | too_thin | format_gate_required | missing_evidence | method_gate_required"
}
```

MVP 不追求一次生成终稿，但必须让用户看到：

```text
哪里已经像论文
哪里还需要补文献
哪里还需要补方法诊断
哪里还需要补结果或稳健性
下一轮自动任务应该做什么
```

## 下一步接入点

1. `Program/workbench/drafts.py` 增加长篇章节生成和 quality report。
2. `Program/export_pdf.py` 的 manifest 增加 paper package 字段。
3. `Program/methodology/` 提供 journal/method rules。
4. `Product/backend/*manuscript*` 与 CLI 共享同一套 quality report。
5. Review & Export 使用 quality report 决定是否进入人工审阅和最终导出。

## 参考来源

- AER Submission Guidelines: https://www.aeaweb.org/journals/aer/submissions
- AER Style Guide: https://www.aeaweb.org/journals/aer/style-guide
- AEA Data and Code Availability Policy: https://www.aeaweb.org/journals/data/data-code-policy
- AEA Data Editor preparing files: https://aeadataeditor.github.io/aea-de-guidance/preparing-for-data-deposit.html
- Social Science Data Editors README template: https://social-science-data-editors.github.io/template_README/template-README.html
- NBER Working Papers: https://www.nber.org/working-papers
- IZA Discussion Papers: https://www.iza.org/publications/dp
