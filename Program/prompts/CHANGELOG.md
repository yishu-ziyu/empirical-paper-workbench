# Prompt 调优 CHANGELOG

格式：每个 tab 一个章节，按 v1 → v2 → v3 顺序记录"为什么改 + 改了什么"。
verdict gate 红色 + 用户反馈驱动调优（spec §4.6）。

## brief
- v1 (2026-06-04): 初版，4 段结构（问题/贡献/边界/成功标准）

## search
- v1 (2026-06-04): 初版，3-5 个 arxiv 检索词，JSON 输出

## variables
- v1 (2026-06-04): 初版，列名→研究变量映射

## design
- v1 (2026-06-04): 初版，3 个候选方法 + 推荐

## execution (9 节)
- v1 (2026-06-04): 初版，每节独立 prompt
  - section_intro: IMRaD 引言，~1500 字
  - section_lit: 主题分组 + 研究缺口，~2000 字
  - section_institution: 制度/政策背景，~1200 字
  - section_data: 数据描述 + 描述性统计，~1500 字
  - section_strategy: 模型设定 + 识别假设，~1500 字
  - section_results: 主回归解读，~2000 字
  - section_robust: 3-5 个稳健性检验，~1500 字
  - section_conclusion: 结论 + 政策含义，~1000 字
  - section_refs: 参考文献格式化，≥8 篇
