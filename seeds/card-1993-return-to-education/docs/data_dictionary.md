# Card (1993) 数据字典

## 数据集信息

| 属性 | 值 |
|------|-----|
| 名称 | card_1995 |
| 来源 | StatsPAI 内置数据集 / NLSY 1976 |
| 样本量 | 3,010 |
| 变量数 | 8 |
| 观测单元 | 个人（男性青年，年龄 24-34 岁） |

## 变量列表

| 变量名 | 类型 | 角色 | 标签 | 取值范围 |
|--------|------|------|------|---------|
| `lwage` | 连续 | outcome | 小时工资对数 | ~4.5 - ~7.5 |
| `educ` | 离散 | treatment | 受教育年限 | 6 - 18 |
| `nearc4` | 二元 | instrument | 附近是否有四年制大学 | 0, 1 |
| `exper` | 连续 | control | 工作经验（年） | 0 - ~25 |
| `expersq` | 连续 | control | 工作经验平方 | 0 - ~625 |
| `black` | 二元 | control | 是否为黑人 | 0, 1 |
| `south` | 二元 | control | 是否居住在南部 | 0, 1 |
| `smsa` | 二元 | control | 是否居住在 SMSA | 0, 1 |

## 描述统计（来自 StatsPAI 内置数据）

```
n = 3010

          mean    std     min     max
lwage     6.26    0.44    4.51    7.78
educ      13.26   2.68    6.00    18.00
nearc4    0.68    0.47    0.00    1.00
exper     11.56   4.38    0.00    24.00
expersq   152.0   113.0   0.00    576.0
black     0.20    0.40    0.00    1.00
south     0.32    0.47    0.00    1.00
smsa      0.66    0.47    0.00    1.00
```

## 关键变量关系

- `educ` 与 `nearc4`: 正相关（第一阶段）
- `educ` 与 `lwage`: 正相关（OLS 基准）
- `exper` 与 `lwage`: 正相关但递减（含 `expersq` 项）

## 数据获取方式

### Python (StatsPAI)
```python
import statspai as sp
df = sp.datasets.card_1995()
```

### Python (raw CSV)
```python
import pandas as pd
url = "https://raw.githubusercontent.com/vincentarelbundock/Rdatasets/master/csv/wooldridge/card.csv"
df = pd.read_csv(url)
```

### R (wooldridge package)
```r
library(wooldridge)
data(card)
```
