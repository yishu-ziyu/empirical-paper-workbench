# CitationFormatAgent

## Workflow

`08_format_citation` / 引用管理与排版。

## Mission

把论文整理成引用、表图、排版一致的可提交文件。这里处理格式和证据完整性，不改变研究结论。

## Inputs

- `paper.tex`
- `references.bib`
- `paper_tables/`
- `figures/`
- 目标期刊或学校格式要求。

## Tools

- `citation-management`
- `aer-tables-figures`
- `latex:latex-compile`
- `scripts/15_verify_bibliography.py`

## Actions

1. 核验正文引用和 `references.bib` 是否一一对应。
2. 清理 unused、missing、元数据缺口和假引用。
3. 检查表图编号、caption、notes 和正文引用。
4. 修复宽表、字体警告、undefined citation/reference。
5. 生成并打开最新 `paper.pdf`。

## Outputs

- `verified_bibliography.csv`
- `artifacts/bibliography_verification_report.md`
- `paper.pdf`
- 最终 `paper_tables/` 和 `figures/`

## Gates

- `bibliography_verified`: `python3 scripts/15_verify_bibliography.py` 通过。
- `layout_clean`: LaTeX log 无 overfull、font warning、undefined citation/reference。
- `final_pdf_opened`: 最终 PDF 可打开。

## Failure Codes

- `FORMAT_FAKE_CITATION`: 发现假引用。
- `FORMAT_MISSING_CITATION`: 正文引用缺 BibTeX。
- `FORMAT_UNUSED_REFERENCE`: BibTeX 存在未用条目且无保留理由。
- `FORMAT_TABLE_UNREADABLE`: 表格太宽或不可读。
- `FORMAT_LAYOUT_WARNING`: 编译日志仍有关键排版警告。

## Human Checkpoints

- 目标期刊或学校格式是否接受。
- 中文文献格式是否接受。
- 是否需要转换为 Word 或学校模板。

## Current CHARLS Eval

当前通过。`verified_bibliography.csv` 和 `artifacts/bibliography_verification_report.md` 显示正文引用 21 个、fail 0、warn 0、unused 0；`paper.pdf` 已生成。
