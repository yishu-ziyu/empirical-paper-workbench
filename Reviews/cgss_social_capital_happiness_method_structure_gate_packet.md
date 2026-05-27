# CGSS 方法规范与论文结构门禁

- 题目：社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析
- 状态：`needs_human_method_structure_approval`
- 写入正式论文：否
- 写入 DesignSpec / RunPlan：否

## 当前需要处理
- `method_structure_gate_needs_human_approval`

## 论文长度标准
- 目标总长度：22000 中文字符左右
- 最低总长度：16000 中文字符
- 建议上限：32000 中文字符
- 写作规则：先按 section 写足证据、变量、方法和结果，再由审稿式修订循环压缩重复内容。

## 方法门禁
- 样本量：5310
- OLS：系数 0.1658，稳健标准误 0.0187
- Ordered Logit：系数 0.405，标准误 0.0424
- 当前主结论边界：`positive_conditional_association`

### 当前可以写的说法
- `conditional_association`：社会资本指数与居民主观幸福感呈正向相关。
- `ordered_outcome_robustness`：在有序响应模型下，正向关系保持稳定。

### 当前暂不进入的计量方法
- DID：当前没有政策冲击、处理组、对照组和处理时间。
- IV：当前没有通过相关性与排除性讨论的工具变量。
- RDD：当前没有明确断点、运行变量和带宽诊断。
- PSM：当前没有已定义处理状态和匹配前平衡诊断。
- DML：当前没有因果处理设定、交叉拟合计划和 nuisance 模型诊断。

## 章节长度和证据要求
- Abstract：180-300 中文字符；证据：section_specific_evidence
- Introduction：2800-5000 中文字符；证据：section_specific_evidence
- Literature and Contribution：1500-3000 中文字符；证据：verified_bibliography_candidates, citation_bindings, contribution_position
- Institutional Background / Theory / Context：1200-2500 中文字符；证据：section_specific_evidence
- Data and Measurement：1200-2500 中文字符；证据：CGSS2023_path, variable_role_review_draft, sample_construction
- Empirical Strategy：1800-3500 中文字符；证据：model_formula, claim_boundary, method_gate
- Main Results：3000-6000 中文字符；证据：OLS_result, Ordered_Logit_result, main_table
- Robustness / Mechanisms / Heterogeneity：2200-5000 中文字符；证据：ordered_outcome_robustness, future_robustness_matrix
- Conclusion：800-1300 中文字符；证据：section_specific_evidence
- References：按内容需要；证据：human_approved_verified_bibliography

## 人工批准后才会写入
- `Results/json/cgss_social_capital_happiness_design_spec_review.json`
- `Manuscripts/sections/empirical-strategy.md`
- `Manuscripts/sections/main-results.md`

## 下一步
- `human_review_method_structure_gate`
- `decide_primary_model_ols_or_ordered_logit`
- `draft_empirical_strategy_after_approval`
- `draft_main_results_after_approval`
