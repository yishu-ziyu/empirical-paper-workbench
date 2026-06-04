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
- section_data v2 (2026-06-04): 4 段（来源/构造/描述统计/平衡性），加缺失变量 fallback 句。
- section_strategy v2 (2026-06-04): 4 段（设定/假设/构造细节/稳健性安排），加"假设不满足会怎样"。
- section_lit v2 (2026-06-04): 4 段（背景/分组/缺口/衔接），强制"衔接到 §1"。
- section_institution v2 (2026-06-04): 3 段（制度/采集/时间线），简化为聚焦数据集背景。
- section_conclusion v2 (2026-06-04): 4 段（发现/政策/局限/未来），加"与 §1 引言一一对应"硬约束。
- v3 (2026-06-04): 关键 4 节 (intro/results/robust/strategy) 加 evidence binding 硬约束。
  每节 prompt 末尾追加「必须显式引用 results_evidence_package.json 里的 evidence_id (≥1 处)」，
  避免模型用 placeholder 数字 (Phase 7 P3 痛点：回归系数凭空写)。
  旧 v1/v2 仍可访问 (向后兼容未升级的节)。
- v4 (2026-06-04): 关键 4 节 (intro/results/robust/strategy) 加 identification-audit 联动 (D3 6th tab)。
  - intro: 末尾"研究设计"段必须点名 identification strategy (DID/IV/RDD/PSM) + 写明一句话
    识别假设 (e.g. "平行趋势假设", "排他性约束")
  - results: 异质性段后追加一段"对识别假设的回应证据" (e.g. "pre-trend p 值 0.42 > 0.1，支持平行趋势")
  - robust: 第 1 段后追加"identification falsification list" — 至少 2 个直接针对识别假设的反事实检验
    (e.g. placebo / leave-one-out / 弱 IV 的 Anderson-Rubin CI)
  - strategy: 第 4 段"稳健性安排"后追加"识别假设的 refutability" — 一句话讲该假设可被哪种证据推翻
- section_refs: 暂不升级 (v1 输出格式已稳定，再调 ROI 低)。
- execute_service: loader 链: v4 → v3 → v2 → v1 (向后兼容未升级的节)。
