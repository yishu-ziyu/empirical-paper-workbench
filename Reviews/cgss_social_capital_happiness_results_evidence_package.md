# CGSS 社会资本与幸福感结果证据包

- 题目：社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析
- 状态：ready_for_paper_draft_input
- 正式层写回：否

## 来源
- OLS：`Results/json/cgss_social_capital_happiness_minimal_model.json`
- Ordered Logit：`Results/json/cgss_social_capital_happiness_ordered_robustness.json`

## 变量口径
- 因变量：`happiness <- a36`
- 社会资本：`social_capital_index`
- 控制变量：`female`, `age`, `education_level`, `log_income`, `health`, `urban_hukou`, `province fixed effects`

## 主结果

| model | variable | coef | se | p-value | nobs |
| --- | --- | ---: | ---: | ---: | ---: |
| OLS | `social_capital_index` | 0.1658 | 0.0187 | 0.0000 | 5310 |
| Ordered Logit | `social_capital_index` | 0.4050 | 0.0424 | 0.0000 | 5310 |

## 写作种子
在 CGSS2023 样本中，社会资本指数与居民主观幸福感呈正向相关；OLS 系数约为 0.1658，Ordered Logit 系数约为 0.4050。

## 人工确认清单
- `outcome_measurement`
- `social_capital_index_construction`
- `control_variable_set`
- `ordered_model_interpretation`
- `literature_support_for_mechanism`
