# CGSS RunPlan seed 执行记录

- 题目：社会资本对居民主观幸福感的影响研究--基于CGSS数据的实证分析
- schema：`p6.cgss_run_plan_seed_execution.v1`
- 状态：`completed_needs_human_result_review`
- 已执行模型：是
- 草案层：是
- 写入正式 RunPlan：否
- 写入 state/product：否

## 执行任务
- `run_ols_baseline`
- `run_ordered_logit_robustness`

## 产物
- minimal_model：`Results/json/cgss_social_capital_happiness_minimal_model.json`，状态 `completed_needs_human_review`
- ordered_robustness：`Results/json/cgss_social_capital_happiness_ordered_robustness.json`，状态 `completed_needs_human_review`
- evidence_package：`Results/json/cgss_social_capital_happiness_results_evidence_package.json`，状态 `ready_for_paper_draft_input`

## 写作种子
在 CGSS2023 样本中，社会资本指数与居民主观幸福感呈正向相关；OLS 系数约为 0.1658，Ordered Logit 系数约为 0.4050。

## 下一步
- `human_review_cgss_results_evidence_package`
- `route_cgss_evidence_into_manuscript_draft`
