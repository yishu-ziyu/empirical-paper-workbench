# Card (1993) 教育回报率 — 种子模板

> **来源**: Card, David. "Using Geographic Variation in College Proximity to Estimate the Return to Schooling." *NBER Working Paper* No. 4483, 1993.
>
> **适配**: Empirical OS 种子模板 v0.2.0

## 模板用途

本模板演示如何在实证 OS 框架中复现 Card (1993) 的经典 IV 估计：
- **研究问题**: 教育回报率是否存在能力偏差？
- **识别策略**: 工具变量（地理邻近性）
- **核心方法**: OLS + IV (2SLS)
- **数据**: NLSY 1976 男性青年样本

## 快速开始

### 方式 1：使用 StatsPAI 内置数据

```python
import statspai as sp
df = sp.datasets.card_1995()
```

### 方式 2：从 wooldridge R 包导入

```python
import pandas as pd
df = pd.read_csv("https://raw.githubusercontent.com/vincentarelbundock/Rdatasets/master/csv/wooldridge/card.csv")
```

## 关键变量

| 变量 | 角色 | 说明 |
|------|------|------|
| `lwage` | outcome | 小时工资对数 |
| `educ` | treatment | 受教育年限 |
| `nearc4` | instrument | 附近是否有四年制大学（0/1） |
| `exper` | control | 工作经验 |
| `expersq` | control | 工作经验平方 |
| `black` | control | 是否为黑人 |
| `south` | control | 是否居住在南部 |
| `smsa` | control | 是否居住在 SMSA |

## 预期结果

| 方法 | educ 系数 | 标准误 | 说明 |
|------|----------|--------|------|
| OLS | ~0.073 | ~0.004 | 基准相关 |
| IV (nearc4) | ~0.133-0.145 | ~0.055-0.075 | 因果估计 |

## 文献引用

```bibtex
@techreport{card1993using,
  title={Using Geographic Variation in College Proximity to Estimate the Return to Schooling},
  author={Card, David},
  year={1993},
  institution={National Bureau of Economic Research},
  type={NBER Working Paper},
  number={4483}
}
```

## 扩展阅读

- Angrist, J. D., & Krueger, A. B. (1991). Does compulsory school attendance affect schooling and earnings? *QJE*, 106(4), 979-1014.
- Wooldridge, J. M. (2013). *Introductory Econometrics: A Modern Approach* (5th ed.), Chapter 15.
