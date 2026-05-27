# CGSS 研究设计草案

- 题目：社会资本对居民主观幸福感的影响研究--基于CGSS数据的实证分析
- 状态：`needs_human_design_spec_review`
- 写入正式 DesignSpec：不写正式 DesignSpec
- 写入 RunPlan：否

## 数据与变量
- 数据：CGSS2023 `/Users/mahaoxuan/Desktop/论文核心素材库/01_原始数据/实证数据库/A004CGSS中国综合社会调查/中国综合社会调查2023/CGSS2023.dta`
- 因变量：`happiness` <- `a36`
- 核心解释变量：`social_capital_index_draft` <- `a33, a31a, a31b, a311`
- 控制变量：`a2, a3a, a7a, a7b, a15, a18, a21, a8a, a8b, s41`

## 识别边界
- 当前 CGSS2023 是横截面数据，本阶段先估计社会资本与主观幸福感之间的条件相关关系。
- 结论边界：可以写社会资本与幸福感存在正向或负向条件相关；暂不写社会资本严格导致幸福感变化。

## 模型候选
- OLS 基准模型（ols）：`happiness ~ social_capital_index_draft + a2 + a3a + a7a + a7b + a15 + a18 + a21 + a8a + a8b + s41`；给出最直观的基准相关关系，便于解释方向、数量级和控制变量变化。
- Ordered Logit 有序模型（ordered_logit）：`happiness ~ social_capital_index_draft + a2 + a3a + a7a + a7b + a15 + a18 + a21 + a8a + a8b + s41`；把幸福感作为有序结果处理，用于检验 OLS 方向是否稳定。

## 暂不进入的计量方法
- DID：当前题目没有明确政策冲击、处理组/对照组、处理时间和处理前趋势。
- IV：当前没有经过文献和数据共同支持的工具变量，也没有排除性约束说明。
- RDD：当前没有断点、运行变量、阈值规则和带宽诊断条件。
- PSM：当前社会资本是连续/多维构造草案，还没有二元处理定义和平衡性诊断。
- DML：当前目标是建立可解释基准模型，还没有因果处理设定、交叉拟合方案和 nuisance 模型诊断。

## 审阅门禁
- `outcome_order_and_coding_review`
- `social_capital_index_construction_review`
- `control_set_and_missingness_review`
- `cross_section_identification_boundary_review`
- `literature_support_required`

## 下一步
- `human_review_cgss_design_spec_draft`
- `after_approval_build_RunPlan_draft`
- `prepare_cgss_minimal_model_execution`
