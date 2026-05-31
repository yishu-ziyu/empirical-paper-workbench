# 数据与变量

- Status: `section_draft_ready_for_review`
- Draft layer: `true`
- Formal writeback: `false`

## 草案正文

本文使用 CGSS2023 数据，原始文件为 CGSS2023.dta。当前证据包记录的数据路径为 /Users/mahaoxuan/Desktop/论文核心素材库/01_原始数据/实证数据库/A004CGSS中国综合社会调查/中国综合社会调查2023/CGSS2023.dta，说明本轮分析来自本机真实数据资产，而不是页面模拟数据。被解释变量为居民主观幸福感，口径写作 happiness <- a36；该变量以有序等级记录，因此后续模型既保留线性基准，也需要有序响应模型作为稳健性参照。核心解释变量为 social_capital_index，由 a33 trust、a31a neighbor_social、a31b friend_social、a311 leisure_social 等题项构造。这组题项覆盖社会信任、邻里交往、朋友交往与休闲社会参与，能够形成一个围绕社会连接和关系资源的操作化指标。控制变量包括 female、age、education_level、log_income、health、urban_hukou、province fixed effects。这些控制项用于吸收性别、年龄、教育、收入、健康、户籍和地区差异等可能同时影响社会资本与幸福感的因素。本节后续人工审阅的重点，是确认幸福感题项是否需要反向处理、社会资本指数是否需要标准化或分维度展示、收入和健康变量的缺失处理是否需要更详细说明。从论文写作角度看，数据与变量部分不能只罗列变量名，还需要解释每个变量为什么进入模型。幸福感变量承担研究问题的结果端，社会资本指数承担解释端，控制变量则用于减少可观察混杂因素带来的解释偏差。由于本轮样本来自单期 CGSS2023 横截面数据，正文需要明确样本时点和数据结构，避免读者误以为当前模型已经利用了面板变化。社会资本指数的构造也应当在正式稿中展示题项来源、处理方向和合成方式；如果后续发现某些题项缺失率过高或含义不一致，系统应当派发新的变量审阅任务，而不是直接把当前指数推进到正式层。这部分内容为后续结果解释提供边界：本文现在解释的是可观察社会连接与幸福感之间的稳定关联，而不是完整社会资本量表的全部效应。

## 证据绑定
- `cgss_results_evidence_package`
- `cgss_minimal_model`
- `cgss_ordered_robustness`

## 引用占位
- `cgss_official_source_placeholder`

## 人工审阅问题
- CGSS2023 官方说明是否已经记录访问日期？
- 社会资本指数是否需要分项信度检查或标准化说明？
- 控制变量集合是否遗漏婚姻、就业或地区经济环境变量？

## 审阅备注
- outcome_measurement
- social_capital_index_construction
- control_variable_set
- ordered_model_interpretation
- literature_support_for_mechanism
