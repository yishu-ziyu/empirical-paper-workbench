# PaperReadingAgent

## Workflow

`03_paper_reading` / 论文阅读与拆解。

## Mission

把核心文献读到方法、表格、结论、局限和可引用证据位置。只读摘要不算通过。

## Inputs

- `litreview/literature_candidates.csv`
- PDF、HTML 或政策原文。
- 已确认的 closest papers。

## Tools

- `pdf`
- `paper-lookup`
- `literature-review`
- 慢读协议：outline -> paragraph_id -> source spans -> compressed notes -> reading state。

## Actions

1. 为每篇核心文献建立全文来源。
2. 抽取研究问题、数据、识别策略、主要结果、机制、局限。
3. 把关键 claim 绑定到页码、表号、行号或 paragraph_id。
4. 更新 compressed notes 和 reading state。
5. 让 `EvidenceAuditor` 检查正文可引用 claim 是否有来源位置。

## Outputs

- `litreview/notes/compressed/`
- `litreview/notes/span_index.json`
- `litreview/notes/reading_state.md`

## Gates

- `source_spans_bound`: 核心 claim 有来源位置。
- `literature_role_confirmed`: 人工确认每篇文献在本文中的角色。

## Failure Codes

- `READING_FULLTEXT_MISSING`: 核心文献没有全文。
- `READING_ABSTRACT_ONLY`: 只有摘要级笔记。
- `READING_SPAN_MISSING`: 关键 claim 没有证据位置。
- `READING_CLAIM_UNBOUND`: 正文 claim 和文献证据未绑定。

## Human Checkpoints

- 文献角色：支持、对比、反证、方法参考、背景。
- 该文献是否能进入正文强引用。

## Current CHARLS Eval

当前通过。证据：核心中文文献、政策文件和方法文献已有 compressed notes；`litreview/notes/reading_state.md` 存在。页码级精修仍可继续提高质量，但不阻塞 P1。
