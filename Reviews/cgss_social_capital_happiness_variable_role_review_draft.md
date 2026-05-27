# CGSS 变量角色审阅草案

- 题目：社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析
- 状态：needs_human_role_review
- 正式变量角色写回：否

## 因变量
- `happiness` <- `a36`
- 题项：总的来说，您觉得您的生活是否幸福
- 有序等级：1, 2, 3, 4, 5
- 理由：题项直接询问总体生活幸福感，和题目中的居民主观幸福感概念一致；有序模型已经验证 1-5 等级口径可用。

## 核心解释变量
- `social_capital_index`
- 来源题项：`a33`, `a31a`, `a31b`, `a311`
- 构造：`standardized_mean_index`
- 理由：社会资本先按信任、邻里交往、朋友交往和休闲社交构成综合指数，适合先形成可检验的主结果；后续仍要人工确认是否拆成多维度报告。

## 控制变量
- `female`：控制性别差异。 原始候选：`a2`。
- `age`：控制生命周期差异。 原始候选：`a3a`。
- `education_level`：控制人力资本和社会经济地位差异。 原始候选：`a7a`, `a7b`。
- `log_income`：控制收入水平差异。
- `health`：控制健康对幸福感的直接影响。 原始候选：`a15`。
- `urban_hukou`：控制城乡户籍差异。 原始候选：`a18`, `a21`。
- `province fixed effects`：控制省份层面的地区差异。 原始候选：`s41`。

## 模型证据
- `ols`：`social_capital_index` 系数 0.1658，标准误 0.0187，p 值 7.78e-19，样本量 5310。
- `ordered_logit`：`social_capital_index` 系数 0.4050，标准误 0.0424，p 值 1.25e-21，样本量 5310。
- 一致性检查：样本量一致=True；有序模型门禁=passed；方向=consistent_positive。

## 审阅门禁
- `outcome_measurement`
- `social_capital_index_construction`
- `control_variable_set`
- `ordered_model_interpretation`
- `literature_support_for_mechanism`

## 人工审阅决定
- 因变量：pending
- 核心解释变量：pending
- 控制变量：pending
- 模型证据：pending
