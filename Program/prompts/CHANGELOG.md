# Prompt 调优 CHANGELOG

格式：每个 tab 一个章节，按 v1 → v2 → v3 顺序记录"为什么改 + 改了什么"。
verdict gate 红色 + 用户反馈驱动调优（spec §4.6）。

## brief
- v1 (2026-06-04): 初版，4 段结构（问题/贡献/边界/成功标准）
- v2 (2026-06-04): 紧凑化。每段强制 1 行 bullet；删「要求结构/解释」前言；token 估降 ~35%，用户痛点=跑数据慢。

## search
- v1 (2026-06-04): 初版，3-5 个 arxiv 检索词，JSON 输出
- v2 (2026-06-04): 加相关性评分 rubric（0.2-1.0 四档），让 LLM 拒收弱相关，缩短重排时间。

## variables
- v1 (2026-06-04): 初版，列名→研究变量映射
- v2 (2026-06-04): 加 5 条硬约束（角色枚举/X+Y 必填/列名严格匹配/语义术语/引用文献），减少 LLM 乱填导致的返工。
- v3 (2026-06-04): 加 "一次性输出" + "不要解释 schema" 指令，减少 LLM 前言后语，加快单次完成时间。

## design
- v1 (2026-06-04): 初版，3 个候选方法 + 推荐
- v2 (2026-06-04): 加 4 项评估标准（内生性/假设/数据/计算成本），"30 分钟内能跑"作为硬门槛。
- v3 (2026-06-04): 加 JSON schema 硬约束（candidates.length=3, method 大写, recommended.method ∈ candidates），减少 LLM 输出解析失败导致重跑。

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
- section_intro v2 (2026-06-04): 显式分 4 段（背景/缺口/贡献/数据+方法+结果摘要），让 LLM 输出与摘要表一一对应。
- section_results v2 (2026-06-04): 4 段（系数/经济显著性/异质/文献对比），强制经济显著性讨论。
- section_robust v2 (2026-06-04): 4 段（设计/5 个具体检验/弱 IV 诊断/综合判断），加弱 IV 诊断。
- execute_service: 优先 v2 loader，fallback v1（向后兼容未升级的节）。
