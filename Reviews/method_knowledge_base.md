# Method Knowledge Base

- 状态：needs_human_method_kb_review
- profile：aer_like
- query：CGSS 主观幸福感 社会资本 OLS Ordered Logit 横截面 AER-like
- proposal 来源数：1
- canonical 规则数：0
- reviewed canonical blocking 规则数：0
- proposal 规则阻断正式导出：否
- 正式论文写回：否
- 正式 bibliography 写回：否
- DesignSpec/RunPlan 写回：否
- product state 写回：否
- canonical 规则写回：否

## 推荐方法检查
- `ordered_outcome_model_fit`：主观幸福感等有序因变量需要 Ordered Logit/Ordered Probit 稳健性或解释边界。
- `ols_association_boundary`：横截面 OLS 只能支持条件相关，不能自动升级为强因果。
- `endogeneity_risk_statement`：需要说明反向因果、遗漏变量和样本选择风险。
- `baseline_controls`：控制变量应覆盖基本人口学、经济条件、健康、户籍或地区差异。
- `robustness_heterogeneity_mechanism_plan`：需要进入下一轮稳健性、异质性和机制检验计划或真实结果。
- `candidate_citation_verification`：候选引用不能支撑正式方法或理论主张，必须进入人工核验。

## 人工审阅
- 核对 proposal 来源是否可以进入 canonical review。
- 核对 recommended checks 是否适用于当前研究设计。
- 只有人工 review 后的 canonical blocking 规则才能接入正式导出门禁。
