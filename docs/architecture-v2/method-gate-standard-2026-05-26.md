# Method Gate Standard

日期：2026-05-26

## 产品目标

方法规范门进入主链路，位置在正式估计之前：

```text
变量角色确认
-> DesignSpec
-> MethodGate
-> RunPlan
-> 执行实验
-> 结果解释
-> 论文草稿
```

方法门不是论文最后的附录检查，而是决定某个识别设计是否可以进入主分析的前置判断。

每个方法门输出：

```json
{
  "method_family": "did | iv | rdd | psm | dml | ols",
  "gate_status": "green | yellow | red",
  "pre_checks": [],
  "diagnostics": [],
  "required_evidence": [],
  "blocking_items": [],
  "recommended_next_tasks": []
}
```

## Gate 语义

- `green`：进入主分析，并把诊断写入论文包。
- `yellow`：可以继续生成草稿，但必须补指定诊断或稳健性。
- `red`：暂停该因果主张，切换方法或回到 DesignSpec。

## DID

### Pre-check

- 处理组、对照组、时间维度明确。
- 处理时间明确，区分一次性处理和交错处理。
- 至少有处理前时期。
- 说明 no anticipation。
- 交错处理不能只依赖传统 TWFE。

### Diagnostics

- 事件研究图。
- 处理前 lead 系数和置信区间。
- 处理时间分组和样本构成。
- 现代 DID 估计器或 TWFE 权重 / 偏误诊断。
- 聚类标准误说明。

### Gate

- `green`：pre-trend 证据、处理时间、估计器和标准误都完整。
- `yellow`：pre-trend 图或现代 DID 诊断缺失，但数据结构支持补做。
- `red`：没有处理前时期、处理时间无法定义、对照组不存在，或 pre-trend 破坏主识别。

## IV

### Pre-check

- 明确内生变量。
- 明确工具变量。
- 写出第一阶段和结构方程。
- 说明相关性、排除限制、独立性。
- 如解释 LATE，说明 monotonicity 和 compliers。

### Diagnostics

- 第一阶段系数。
- partial R2。
- first-stage F / robust F / Kleibergen-Paap。
- reduced form。
- 弱工具稳健推断，如 Anderson-Rubin 或 CLR。
- 如有多个工具，报告 overidentification 相关诊断。

### Gate

- `green`：制度论证、第一阶段、弱工具稳健推断和 reduced form 一致。
- `yellow`：第一阶段弱或弱工具稳健推断缺失，但可补。
- `red`：工具变量缺少排除限制、第一阶段几乎不存在，或 reduced form 与机制冲突。

## RDD

### Pre-check

- 断点和 running variable 明确。
- assignment rule 清楚。
- 区分 sharp / fuzzy。
- 断点附近样本量可用。
- 没有明显同时发生的其他政策断点。

### Diagnostics

- rdplot。
- McCrary / density test。
- 带宽选择和带宽敏感性。
- robust bias-corrected confidence interval。
- 协变量连续性。
- donut / 多项式阶数 / kernel 敏感性。
- fuzzy RDD 时报告第一阶段跳跃。

### Gate

- `green`：密度、协变量、带宽和估计结果都支持断点识别。
- `yellow`：诊断缺失但 running variable 和 cutoff 清楚。
- `red`：running variable 可操纵、断点样本过少、协变量明显跳跃，或带宽敏感性破坏结论。

## PSM

### Pre-check

- 处理变量和处理前协变量明确。
- 说明 selection on observables。
- 只使用处理前变量匹配。
- 明确 ATE / ATT。
- 检查 common support。

### Diagnostics

- 倾向得分重叠图。
- 标准化均值差异。
- 方差比。
- 匹配前后协变量平衡表。
- 被丢弃样本比例。
- caliper / nearest neighbor / weighting 敏感性。

### Gate

- `green`：重叠、平衡、样本保留和敏感性都合理。
- `yellow`：可继续作为辅助设计，但需要补平衡和重叠诊断。
- `red`：common support 很差、关键协变量不平衡，或主要威胁来自不可观测混杂。

## DML

### Pre-check

- 明确 PLR / IRM / PLIV / IIVM。
- 明确 outcome、treatment、controls、instrument if any。
- 使用 Neyman orthogonal score。
- 使用 sample splitting / cross-fitting。
- 明确 nuisance learners。
- 检查 overlap。

### Diagnostics

- folds / repetitions / seeds。
- cross-fit split 记录。
- out-of-fold nuisance performance。
- propensity distribution。
- learner / fold 稳定性。
- estimate / standard error / confidence interval。
- sensitivity bounds，如 RV / RVa。

### Gate

- `green`：orthogonal score、cross-fitting、overlap、稳定性和敏感性完整。
- `yellow`：估计可跑，但缺少 fold 稳定性或 sensitivity。
- `red`：处理变量几乎可被完全预测、overlap 极差、fold 间结果大幅漂移，或 nuisance 表现不可接受。

## OLS / Fixed Effects

OLS 可以作为 baseline，但也需要门禁：

- 样本单位、时期和聚类层级明确。
- outcome、treatment、controls 定义完整。
- 描述统计和缺失值检查存在。
- 结果表包含标准误、样本量、R2 或 FE 信息。
- 不能把 baseline OLS 自动升级为强因果结论；若用户选择因果主张，必须进入 DID / IV / RDD / PSM / DML 或明确理论识别说明。

## 写入位置

项目级：

```text
state/product/method_gate.json
```

Run 级：

```text
workspace/runs/<run_id>/03_design/method_gate_report.json
workspace/runs/<run_id>/04_analysis/method_diagnostics.json
```

论文包：

```text
Results/json/method_gate_report.json
Results/json/method_diagnostics.json
```

## 与 Journal Skill Registry 的关系

Method Gate 是方法级最低标准。

Journal Skill Registry 是期刊或审稿标准增强层，例如 AER-like 会把 DID、IV、RDD 等门槛提高到更严格的版本。

执行顺序：

```text
MethodGate baseline
-> JournalSkill overlay
-> Review & Export verifier
```

第一版如果 AER-like 还处在 proposal 状态，它可以提示和生成 patch proposal；只有进入 canonical 后，才可以阻断 formal export。

