# P1-K Manuscript Consumption BDD

日期：2026-05-13

## 背景

P1-J 已经把 FindingCard 从“执行结果展示”推进到“可审阅论文论断”。`finding_trained_effect` 当前可通过 claim review 变成 `review_status=approved`、`can_write_to_draft=true`。

下一步是 Manuscript consumption：论文正文不能直接从 full-run 或 Markdown 草稿自动覆盖生成，而应只消费已经 approved 的 FindingCard，生成可审阅的正文段落候选。

本阶段不实现完整 Markdown 编辑器，也不覆盖 `Manuscripts/generated/paper_draft.md`。

## 行为 1：没有 approved FindingCard 时不得生成正文候选

Given 项目已有 successful full-run  
And FindingCard 仍是 `needs_review`、`rejected` 或 `needs_revision`  
When 前端或 API 请求 manuscript candidates  
Then 返回空 candidates  
And 返回 empty_state code `approved_finding_required`  
And 不修改 `Manuscripts/generated/paper_draft.md`

业务规则：只有用户批准过的论断才能进入正文候选层。

## 行为 2：approved FindingCard 生成正文段落候选

Given FindingCard `can_write_to_draft=true`  
When 请求 manuscript candidates  
Then 返回至少一个 candidate  
And candidate 绑定 `finding_id`、`run_id`、`run_plan_version`  
And candidate 的正文包含 treatment、outcome、estimate、standard error、p value、sample size  
And candidate 状态为 `draft`

业务规则：candidate 是正文候选，不是最终正文；必须可审阅。

## 行为 3：candidate 必须绑定三类 provenance

Given approved FindingCard 生成了 candidate  
When 读取 candidate provenance  
Then provenance 包含 source draft `Manuscripts/generated/paper_draft.md`，证据等级 `local_file`  
And 包含 result artifact `Results/json/analysis_result.json`，证据等级 `local_execution`  
And 包含 review decision `state/product/finding_reviews.json`，证据等级 `local_file`

业务规则：正文候选必须能解释“从哪个草稿、哪个结果文件、哪个人工审阅决定”来的。

## 行为 4：前端 Manuscript candidates 只显示 approved 输入

Given Results & Draft 页面加载 manuscript candidates  
When API 返回 candidates  
Then 页面显示 candidate body、status、finding_id、provenance paths  
And 页面保留 empty state，说明没有 approved finding 时不能生成正文候选  
And 不提供“覆盖正文”按钮

业务规则：当前阶段只做候选生成和审阅准备，不允许直接覆盖源草稿。

## 边界条件

- 本阶段只生成 deterministic candidate，不调用 LLM 改写。
- 本阶段不创建最终 Word / PDF / replication package。
- 本阶段不把 rejected / needs_revision finding 写入候选。
- Feynman 继续作为 external callable research engine provenance 方向，不嵌入源码。
