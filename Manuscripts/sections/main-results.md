# Main Results

- Status: `section_draft_expanded`
- Agent: `ManuscriptAgent`
- Draft layer: `true`
- Final paper write: `false`

## 已消费证据

- `main_regression_table` -> `Results/json/regression_tables.json`; sha256=`34df595330fa9280af2ed85ded2f198a91c1c2a006fb39a3c52c2102071f4ecb`
- `approved_findings` -> `Results/json/approved_findings.json`; sha256=`417f8c5c1327ed61c952a20d06f6cd1e276a39e9125bdaf7884f8512ba5361f4`
- `coefficient_interpretation` -> `Results/json/approved_findings.json`; sha256=`417f8c5c1327ed61c952a20d06f6cd1e276a39e9125bdaf7884f8512ba5361f4`

## 草案正文

本节围绕主回归表、已审批 finding 和系数解释证据组织结果叙述。主表提供估计方向、标准误和显著性信息；approved findings 提供可以进入正文候选的研究论断；method execution result 则把系数解释绑定回本地执行产物。
主表证据摘要：table_id=regression_table_1, dependent_var=ln_wage, treatment=ln_robot, nobs=34315, coefficient=0.199384322747, standard_error=0.0793435494782, p_value=0.0119807291718；table_id=regression_table_2, dependent_var=ln_wage, treatment=ln_robot, nobs=15697, coefficient=0.1039074473, standard_error=0.0058946931, p_value=1.5209199652e-69；table_id=regression_table_3, dependent_var=ln_wage, treatment=ln_robot, nobs=34315, coefficient=0.0798431464061, standard_error=0.0222977162482, p_value=0.000343336034355
已审批 finding 摘要：草案提案：在 iv 规格中，ln_robot 对 ln_wage 的估计系数为 0.199384322747（SE=0.0793435494782, p=0.0119807291718, N=34315）。
系数解释证据摘要：task_id=robot_wage_iv_baseline, method_id=iv, estimator=iv, dependent_var=ln_wage, treatment=ln_robot, nobs=34315, coefficient=0.199384322747, standard_error=0.0793435494782, p_value=0.0119807291718；task_id=robot_wage_ols_comparison, method_id=ols, estimator=ols, dependent_var=ln_wage, treatment=ln_robot, nobs=15697, coefficient=0.1039074473, standard_error=0.0058946931, p_value=1.5209199652e-69；task_id=robot_manu_iv, method_id=iv, estimator=iv, dependent_var=ln_wage, treatment=ln_robot, nobs=34315, coefficient=0.0798431464061, standard_error=0.0222977162482, p_value=0.000343336034355
写作上，Main Results 应先说明核心估计量和经济含义，再解释该结果如何回答研究问题，最后交代后续稳健性、机制或异质性检验需要继续支撑的部分。

## 审阅事项

- VerifierAgent 需要逐条反查本节论断是否能回到 consumed evidence。
- 人工确认前，本节仍停留在草案层，不进入正式论文。
