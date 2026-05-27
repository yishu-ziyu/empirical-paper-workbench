# CGSS AER-like 方法规范门

- 题目：社会资本对居民主观幸福感的影响研究--基于CGSS数据的实证分析
- 状态：`needs_human_method_gate_review`
- profile：`aer_like`
- gate_status：`yellow`
- 强制启用：`true`
- 正式层写回：`false`

## 方法检查
- `variable_definitions`：变量定义是否充分 -> `passed`
  - 审阅说明：正式稿仍需把题项方向、量表含义和缺失处理写入变量表。
- `ordered_outcome_model_fit`：主观幸福感因变量是否适合 OLS + Ordered Logit -> `passed`
  - 审阅说明：OLS 可作可解释基准，Ordered Logit 用于有序因变量稳健性。
- `social_capital_theory_literature`：社会资本核心解释变量是否有理论和文献依据 -> `needs_human_verification`
  - 审阅说明：候选引用存在，但正式 bibliography 和中文文献仍需人工核验。
- `baseline_controls`：控制变量是否覆盖基本人口学和经济变量 -> `passed`
  - 审阅说明：已覆盖性别、年龄、教育、收入、健康和户籍；可继续补地区与家庭结构。
- `robustness_heterogeneity_mechanism_plan`：是否需要进一步稳健性、异质性、机制检验 -> `needs_followup`
  - 审阅说明：当前完整稿已有计划段落，但尚未真实执行分项指数、异质性和机制检验。
- `reverse_causality_and_omitted_variable_risk`：是否存在反向因果和遗漏变量风险 -> `risk_flagged`
  - 审阅说明：横截面结果只能支持条件相关；幸福感也可能影响社会参与，遗漏人格、社区质量等变量。

## 结果数字绑定
- 来源：`cgss_results_evidence_package`
- OLS：coef=0.1658，n=5310
- Ordered Logit：coef=0.405，n=5310

## 风险登记
- `reverse_causality`：反向因果
- `omitted_variables`：遗漏变量

## 下一步
- `human_review_cgss_method_gate`
- `add_variable_definition_detail`
- `plan_robustness_heterogeneity_mechanism_tests`
- `address_endogeneity_risk_in_reviewer_loop`
