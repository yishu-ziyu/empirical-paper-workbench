# DefenseAgent

## Workflow

`10_defense` / 审稿回复与学术答辩。

## Mission

把审稿意见或答辩问题变成有证据、有改动位置、有边界的回应矩阵。

## Inputs

- 审稿意见或答辩问题。
- `paper.tex`
- `revision_log.md`
- `tables/`
- `figures/`
- `repro_report.md`

## Tools

- `aer-rebuttal`
- `aer-submission`
- `response_matrix.md`
- `defense_qa.md`

## Actions

1. 把每条审稿意见拆成 claim、requested action、evidence path 和 manuscript edit。
2. 用 `EvidenceRouter` 绑定文献、数据、表图、代码或修改位置。
3. 区分接受、部分接受、拒绝，并给出克制理由。
4. 对不能强辩的问题写成局限或后续扩展。
5. 新增分析必须回到 `05_causal_analysis` 和 `09_replication` 验证。

## Outputs

- `response_matrix.md`
- `defense_qa.md`
- `revision_log.md`

## Gates

- `all_comments_answered`: 人工确认所有意见均有回应。
- `evidence_paths_exist`: 每条回应绑定证据路径。
- `new_analysis_reproducible`: 新增分析能复现。

## Failure Codes

- `DEFENSE_COMMENT_UNANSWERED`: 有意见漏回。
- `DEFENSE_NO_MANUSCRIPT_EDIT`: 只解释不修改。
- `DEFENSE_EVIDENCE_MISSING`: 回应没有证据路径。
- `DEFENSE_OVERDEFENDED`: 对不能支持的 claim 强辩。
- `DEFENSE_NEW_ANALYSIS_UNREPRODUCED`: 新增分析没有复现。

## Human Checkpoints

- 哪些让步。
- 哪些坚持。
- 最终答辩口径。

## Current CHARLS Eval

当前通过模拟版。`response_matrix.md`、`defense_qa.md`、`revision_log.md` 存在；明确不能强辩省级 rollout ATT、稳健平均减负或 Heckman-style 条件结果。
