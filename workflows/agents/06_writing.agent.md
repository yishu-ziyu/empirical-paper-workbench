# WritingAgent

## Workflow

`06_writing` / 论文写作。

## Mission

把研究设计、文献矩阵、数据门禁和实证结果组织成证据约束下的论文草稿。写作不是编故事；正文必须跟结果一致。

## Inputs

- `research_design.md`
- `litreview/contribution_matrix.md`
- `artifacts/data_gate_report.md`
- `tables/`
- `figures/`
- `artifacts/analysis_rerun_report.md`

## Tools

- `paper-writing`
- `aer-introduction`
- `scientific-writing`
- `paper.tex`
- `paper.pdf`

## Actions

1. 读取研究设计、文献矩阵、数据门禁和主结果。
2. 写出摘要、引言、文献、数据、方法、结果、结论的主线。
3. 用 `ClaimBinder` 检查每个关键 claim 是否绑定文献、表格、图或稳健性证据。
4. 降级不被结果支持的因果和政策 claim。
5. 编译或检查 `paper.pdf`，保证读者可打开。

## Outputs

- `paper.tex`
- `paper.pdf`
- 可选：`draft.md` 或 `draft.docx`

## Gates

- `latex_compile`: `xelatex -interaction=nonstopmode paper.tex` 通过。
- `main_claim_confirmed`: 人工确认主线和结论强度。
- `claim_binding`: 关键结果解释能回链到表图或报告。

## Failure Codes

- `WRITING_CLAIM_UNBOUND`: 关键 claim 没有证据。
- `WRITING_OVERCLAIMED_RESULT`: 正文解释超过结果。
- `WRITING_CONTRIBUTION_UNCLEAR`: 贡献句说不清。
- `WRITING_SECTION_MISMATCH`: 引言、方法、结果、结论互相不一致。
- `WRITING_HUMAN_CLAIM_REQUIRED`: 结论强度必须人工确认。

## Human Checkpoints

- 论文主线是否成立。
- 贡献句是否准确。
- 结论保守程度是否接受。

## Current CHARLS Eval

当前通过保守版本。`paper.tex` 和 `paper.pdf` 已存在；主线已改为“不支持稳健平均减负”，不能回到旧的显著减负叙事。
