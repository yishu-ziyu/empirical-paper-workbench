# CGSS RunPlan seed

- 题目：社会资本对居民主观幸福感的影响研究--基于CGSS数据的实证分析
- 状态：`needs_human_run_plan_seed_review`
- 写入正式 RunPlan：不写正式 RunPlan
- 执行模型：否，仅生成可审阅计划

## 执行前预检
- 数据：`/Users/mahaoxuan/Desktop/论文核心素材库/01_原始数据/实证数据库/A004CGSS中国综合社会调查/中国综合社会调查2023/CGSS2023.dta`
- 必需原始字段：`a36, a33, a31a, a31b, a311, a2, a3a, a7a, a8a, a15, a18, s41`
- 执行变量：`happiness, social_capital_index, female, age, education_level, log_income, health, urban_hukou, province`
- 暂缓控制字段：`a7b, a21, a8b`

## 任务
- CGSS 数据读取和字段预检：`cgss_data_preflight` / `data_preflight`
- 构造 CGSS 分析样本和社会资本指数：`build_cgss_analysis_frame` / `feature_engineering`
- OLS 基准模型：`run_ols_baseline` / `ols`
  - 命令：`python3 Program/cgss_minimal_model.py --project-root . --dataset '/Users/mahaoxuan/Desktop/论文核心素材库/01_原始数据/实证数据库/A004CGSS中国综合社会调查/中国综合社会调查2023/CGSS2023.dta' --topic '社会资本对居民主观幸福感的影响研究--基于CGSS数据的实证分析'`
  - 产物：`Results/json/cgss_social_capital_happiness_minimal_model.json, Reviews/cgss_social_capital_happiness_minimal_model.md`
- Ordered Logit 有序模型：`run_ordered_logit_robustness` / `ordered_logit`
  - 命令：`python3 Program/cgss_ordered_robustness.py --project-root . --dataset '/Users/mahaoxuan/Desktop/论文核心素材库/01_原始数据/实证数据库/A004CGSS中国综合社会调查/中国综合社会调查2023/CGSS2023.dta' --topic '社会资本对居民主观幸福感的影响研究--基于CGSS数据的实证分析'`
  - 产物：`Results/json/cgss_social_capital_happiness_ordered_robustness.json, Reviews/cgss_social_capital_happiness_ordered_robustness.md`

## 失败时先看
- `dataset_missing_or_unreadable`
- `required_source_columns_missing`
- `too_few_complete_rows_after_missingness_filter`
- `outcome_has_too_few_ordered_levels_for_ordered_logit`
- `social_capital_index_has_no_variation`

## 下一步
- `human_review_cgss_run_plan_seed`
- `after_approval_execute_cgss_ols_and_ordered_logit`
- `combine_cgss_results_evidence_package`
