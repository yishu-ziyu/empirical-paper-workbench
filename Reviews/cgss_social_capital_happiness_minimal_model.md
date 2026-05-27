# CGSS 社会资本与幸福感最小模型

- 题目：社会资本对居民主观幸福感的影响研究--基于CGSS数据的实证分析
- 状态：completed_needs_human_review
- 样本量：5310
- 数据：/Users/mahaoxuan/Desktop/论文核心素材库/01_原始数据/实证数据库/A004CGSS中国综合社会调查/中国综合社会调查2023/CGSS2023.dta
- 正式层写回：否

## 主要结果

### baseline_index

| variable | coef | robust se | p-value |
| --- | ---: | ---: | ---: |
| `social_capital_index` | 0.1658 | 0.0187 | 0.0000 |
| `female` | 0.0415 | 0.0231 | 0.0729 |
| `age` | 0.0070 | 0.0008 | 0.0000 |
| `education_level` | 0.0317 | 0.0044 | 0.0000 |
| `log_income` | 0.0022 | 0.0032 | 0.4843 |
| `health` | 0.1832 | 0.0120 | 0.0000 |
| `urban_hukou` | -0.0048 | 0.0274 | 0.8621 |

### trust_only

| variable | coef | robust se | p-value |
| --- | ---: | ---: | ---: |
| `trust` | 0.1290 | 0.0124 | 0.0000 |
| `female` | 0.0511 | 0.0230 | 0.0263 |
| `age` | 0.0057 | 0.0008 | 0.0000 |
| `education_level` | 0.0299 | 0.0044 | 0.0000 |
| `log_income` | 0.0026 | 0.0031 | 0.4134 |
| `health` | 0.1860 | 0.0119 | 0.0000 |
| `urban_hukou` | -0.0004 | 0.0273 | 0.9881 |

### social_dimensions

| variable | coef | robust se | p-value |
| --- | ---: | ---: | ---: |
| `trust` | 0.1254 | 0.0124 | 0.0000 |
| `neighbor_social` | 0.0052 | 0.0061 | 0.3963 |
| `friend_social` | 0.0051 | 0.0073 | 0.4854 |
| `leisure_social` | 0.0415 | 0.0121 | 0.0006 |
| `female` | 0.0438 | 0.0230 | 0.0571 |
| `age` | 0.0059 | 0.0008 | 0.0000 |
| `education_level` | 0.0290 | 0.0044 | 0.0000 |
| `log_income` | 0.0024 | 0.0031 | 0.4482 |
| `health` | 0.1821 | 0.0119 | 0.0000 |
| `urban_hukou` | 0.0021 | 0.0272 | 0.9375 |

## 下一步
- 增加有序 Logit 稳健性。
- 把社会资本拆成信任、社交网络、互助参与三个小节解释。
- 补 CNKI / Scholar 文献综述后再进入完整论文草稿。
