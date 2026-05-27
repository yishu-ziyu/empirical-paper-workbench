# CGSS DatasetBinding 后变量角色草案

- 题目：社会资本对居民主观幸福感的影响研究--基于CGSS数据的实证分析
- 状态：needs_human_dataset_bound_role_review
- 正式变量角色写回：不写正式变量角色

## 数据绑定
- 推荐数据：CGSS2023 `/Users/mahaoxuan/Desktop/论文核心素材库/01_原始数据/实证数据库/A004CGSS中国综合社会调查/中国综合社会调查2023/CGSS2023.dta`
- 样本量：11326；字段数：439
- 规则：本草案只读取推荐数据集对应年份的字段画像，其他年份只作为后续稳健性或口径对齐候选。

## 因变量
- `happiness` <- `a36`
- 题项：总的来说，您觉得您的生活是否幸福
- 理由：这个题项直接测量居民对自身生活是否幸福的判断，和题目里的主观幸福感概念最贴近；进入正式模型前还要核对编码方向、缺失值和有序等级。

## 核心解释变量
- `social_capital_index_draft`
- 来源题项：`a33`, `a31a`, `a31b`, `a311`
- 理由：社会资本不是单一题项：信任、邻里社交、朋友社交和休闲社交分别覆盖信任与网络互动两个核心维度。先按多维结构进入草案，比直接合成黑箱指数更稳。

## 控制变量
- 来源题项：`a2`, `a3a`, `a7a`, `a7b`, `a15`, `a18`, `a21`, `a8a`, `a8b`, `s41`
- 理由：这些变量覆盖人口学、教育、人力资本、收入、健康、户籍和地区差异，是社会资本与幸福感关系中最容易造成混杂因素的一组基础控制。

## 审阅门禁
- `outcome_coding_and_scale_review`
- `social_capital_index_construction`
- `control_set_completeness`
- `missingness_and_sample_loss_review`
- `literature_support_required`

## 下一步
- 人工确认变量角色后，才允许进入 DesignSpec 草案。
- 未确认前，不写 `state/product/variable_roles.json`。
