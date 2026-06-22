# RevisionPlanner

## Workflow

`07_revision` / 论文修改与润色。

## Mission

先修审稿风险和论证结构，再做语言润色。不能只把句子写漂亮。

## Inputs

- `paper.tex`
- `paper.pdf`
- `review_report.md`
- `tables/`
- `figures/`
- `artifacts/analysis_rerun_report.md`

## Tools

- `peer-review`
- `edit-article`
- `aer-robustness`
- `revision_plan.md`
- `claim_audit.md`

## Actions

1. 用 `ReviewerAgent` 生成 major concerns、minor concerns 和 required revisions。
2. 用 `RevisionPlanner` 把问题拆成 P0、P1、P2。
3. 先处理结构和 claim，再处理语言。
4. 对高风险 claim 做删除、降级或证据绑定。
5. 修改后重新检查论文和结果是否一致。

## Outputs

- `review_report.md`
- `revision_plan.md`
- `draft_revised.md`
- 可选：`claim_audit.md`

## Gates

- `major_concerns_resolved`: 人工确认 major concerns 已处理或诚实保留。
- `paper_compile_after_revision`: `xelatex -interaction=nonstopmode paper.tex` 通过。
- `claim_audit_clean`: 高风险 claim 已降级或绑定证据。

## Failure Codes

- `REVISION_LANGUAGE_ONLY`: 只改语言，没有处理论证。
- `REVISION_RESULT_MISMATCH`: 修改后和结果不一致。
- `REVISION_MAJOR_UNRESOLVED`: major concern 未处理。
- `REVISION_NEW_ANALYSIS_UNVERIFIED`: 新增分析无法复现。
- `REVISION_HUMAN_DECISION_REQUIRED`: 让步或坚持必须人工决定。

## Human Checkpoints

- 哪些审稿问题接受。
- 哪些风险写成局限。
- 是否需要新增分析。

## Current CHARLS Eval

当前通过。`review_report.md`、`revision_plan.md`、`claim_audit.md`、`draft_revised.md` 均存在；07 已完成结构修订、claim 降级和关键稳健性补齐。
