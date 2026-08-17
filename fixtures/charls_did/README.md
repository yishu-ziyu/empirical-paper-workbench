# CHARLS DID proof case

这不是产品，是第一阶段跑通「数据 → 设计 → 估计」的样例夹具。

完整论文仓（含脚本、表图、TeX）仍在：

`/Users/mahaoxuan/Desktop/经济学论文/papers/StatspAI_跑通一次_CHARLS_DID/`

本目录只收设计叙事，方便产品主路径对照。原始微观数据不入库。

## 当前合格表述

M5 `treat_post = +0.081`, SE `0.053`，不显著。

不能写「城乡医保整合稳健降低住院自付」。简单规格为负，首选规格和保守推断不支持稳健平均减负；证据更像利用和支出结构调整。

## 文件

- `causal_question.yaml` — 问题、处理、对照、主结果
- `research_design.md` — 估计对象与禁止写法
- `design_risk.md` — 风险登记

换题目时改研究方向，不要另开一个产品仓。
