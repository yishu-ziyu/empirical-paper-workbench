# CGSS 文献综述种子包

- 题目：社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析
- 状态：needs_human_literature_review
- 正式参考文献写回：否
- 正式论文写回：否

## 覆盖范围
- `social_capital_theory`
- `subjective_wellbeing_measurement`
- `cgss_empirical_context`
- `ordinal_outcome_method`
- `chinese_literature_queue`

## 种子文献
### S01 CGSS 项目概况
- 类型：`official_data`
- 作者/机构：中国人民大学中国调查与数据中心
- 年份：
- 链接：https://cgss.ruc.edu.cn/xmjs/xmgk.htm
- 证据角色：`cgss_empirical_context`, `data_source_description`
- 可用于：说明 CGSS 的项目来源、全国综合社会调查定位和数据使用边界。
- 不应直接写成：不能仅凭数据来源说明把本文结果写成严格因果效应。

### S02 Social Capital in the Creation of Human Capital
- 类型：`classic_theory`
- 作者/机构：James S. Coleman
- 年份：1988
- 链接：https://www.journals.uchicago.edu/doi/10.1086/228943
- 证据角色：`social_capital_theory`, `mechanism`
- 可用于：支撑社会资本通过义务、期望、信息渠道和社会规范影响个体福利的理论机制。
- 不应直接写成：不能直接证明 CGSS 中某个题项就是完整社会资本。

### S03 Bowling Alone: The Collapse and Revival of American Community
- 类型：`classic_theory`
- 作者/机构：Robert D. Putnam
- 年份：2000
- 链接：https://www.simonandschuster.com/books/Bowling-Alone-Revised-and-Updated/Robert-D-Putnam/9781982130848
- 证据角色：`social_capital_theory`, `trust_norms_networks`
- 可用于：用于组织信任、规范和网络三类社会资本维度。
- 不应直接写成：不能把美国社区衰退叙事直接套用到中国居民幸福感。

### S04 The Forms of Capital
- 类型：`classic_theory`
- 作者/机构：Pierre Bourdieu
- 年份：1986
- 链接：https://web.stanford.edu/~eckert/PDF/Bourdieu1986.pdf
- 证据角色：`social_capital_theory`, `resource_network`
- 可用于：补充社会资本作为可动员关系资源的解释。
- 不应直接写成：不能把阶层再生产理论直接写成本文实证结论。

### S05 Subjective Well-Being
- 类型：`measurement_standard`
- 作者/机构：Ed Diener
- 年份：1984
- 链接：https://doi.org/10.1037/0033-2909.95.3.542
- 证据角色：`subjective_wellbeing_measurement`
- 可用于：界定主观幸福感和生活评价的概念边界。
- 不应直接写成：CGSS 单题幸福感只是代理变量，不能覆盖多维 SWB。

### S06 OECD Guidelines on Measuring Subjective Well-being
- 类型：`measurement_standard`
- 作者/机构：OECD
- 年份：2025
- 链接：https://www.oecd.org/en/publications/oecd-guidelines-on-measuring-subjective-well-being-2025-update_9203632a-en/full-report/measuring-subjective-well-being_b4b53f27.html
- 证据角色：`subjective_wellbeing_measurement`, `measurement_limits`
- 可用于：说明主观幸福感测量应区分生活评价、情感体验和其他福利指标。
- 不应直接写成：不能把幸福感自评当作客观福利水平。

### S07 Measuring Social Capital: An Integrated Questionnaire
- 类型：`measurement_standard`
- 作者/机构：World Bank
- 年份：2004
- 链接：https://openknowledge.worldbank.org/entities/publication/634c867c-cbc8-536a-8446-a2703177bc7c
- 证据角色：`social_capital_measurement`, `variable_operationalization`
- 可用于：为信任、网络、集体行动、信息沟通等社会资本维度提供测量参照。
- 不应直接写成：CGSS 不是完整 SC-IQ，不能声称完全复刻该量表。

### S08 Social trust, social capital, and subjective well-being of rural residents
- 类型：`cgss_empirical_study`
- 作者/机构：Xu, Zhang, Huang
- 年份：2023
- 链接：https://www.nature.com/articles/s41599-023-01532-1
- 证据角色：`cgss_empirical_context`, `mechanism`, `variable_operationalization`
- 可用于：提供 CGSS 语境下社会信任、社会资本与主观幸福感的实证参照。
- 不应直接写成：该文样本和波次不同，不能直接外推到本文 CGSS2023 全样本。

### S09 机会不均等、社会资本与农民主观幸福感
- 类型：`chinese_literature_seed`
- 作者/机构：张彤进, 万广华
- 年份：2020
- 链接：https://qks.shufe.edu.cn/J/ArticleQuery/f824063e-2826-4256-90f5-e5ff8aa79e7a/CN
- 证据角色：`cnki_manual_queue`, `chinese_empirical_context`
- 可用于：作为中文 CGSS 幸福感研究和社会资本机制的候选中文文献。
- 不应直接写成：其农民样本和机会不均等框架不能直接替代本文居民样本框架。

### S10 How Important is Methodology for the estimates of the determinants of Happiness?
- 类型：`method_reference`
- 作者/机构：Ferrer-i-Carbonell, Frijters
- 年份：2004
- 链接：https://doi.org/10.1111/j.1468-0297.2004.00235.x
- 证据角色：`ordinal_outcome_method`, `subjective_wellbeing_method`
- 可用于：支撑幸福感有序变量建模和 OLS/有序模型稳健性讨论。
- 不应直接写成：方法选择仍需结合 CGSS 量表和本文诊断结果说明。

## 变量支持
- 因变量 `happiness`：`a36`；CGSS a36 是单题总体幸福感代理变量。
- 核心解释变量 `social_capital_index`：`a33`, `a31a`, `a31b`, `a311`；综合指数需要人工确认维度权重和缺失值处理。
- 控制变量：`female`, `age`, `education_level`, `log_income`, `health`, `urban_hukou`, `province fixed effects`

## 机制地图
- `social_trust_mechanism`：社会信任降低互动不确定性，增强安全感和社会支持预期。 需要来源：Coleman 1988, Putnam 2000, Xu et al. 2023。
- `social_participation_mechanism`：社会交往和参与网络可能通过情感支持、信息交换和资源获得影响幸福感。 需要来源：Putnam 2000, World Bank SC-IQ, Chinese CGSS literature。
- `health_income_confounding`：健康、收入和教育同时影响社会资本积累和幸福感评价，需要作为控制变量处理。 需要来源：subjective well-being empirical literature。

## 方法支持
- `ordered_logit`：CGSS a36 是 1-5 有序幸福感量表，Ordered Logit 应进入主模型或核心稳健性。 待检查：报告边际效应, 检查比例优势假设或说明局限。
- `ols_baseline`：OLS 便于解释系数方向和大小，可作为可读性基准。 待检查：说明有序变量被连续化处理的限制。

## CNKI 人工检索队列
- `社会资本 主观幸福感 CGSS`：确认中文核心文献中社会资本与幸福感的变量定义和常用控制变量。 状态：`manual_search_required`。
- `社会信任 居民幸福感 CGSS 有序Logit`：核验 CGSS 幸福感题项、社会信任题项和有序 Logit 写法。 状态：`manual_search_required`。
- `社会参与 社会网络 主观幸福感 中国综合社会调查`：补充分维度社会资本机制，避免只使用社会信任解释所有结果。 状态：`manual_search_required`。

## 下一步
- `run_cnki_manual_search`
- `verify_scholar_zotero_sources`
- `bind_literature_to_variable_roles`
- `draft_literature_review_section`
