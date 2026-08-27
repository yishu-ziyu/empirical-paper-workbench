# ADR 0011: Apodex 深搜旁路——可弃耗材，非依赖

日期：2026-08-27
状态：已接受（实验窗口：Apodex 两周免费 API）

## 背景

`search_literature` 现有源：mock / crossref / semantic_scholar。深研能力
（多路检索、读材料）弱于 Apodex 一类重型求解器。用户提供了 Apodex 两周
免费 API 作为试错耗材。

## 决策

1. **旁路而非替换**：新增 `literature_sources/apodex.py`，OpenAI 兼容端点，
   `APODEX_API_KEY` 存在才启用；无 key、过期、调用失败一律降级
   `mock_degraded`，与 semantic_scholar 同款语义。
2. **不改默认路径**：`llm/router.py` 与 `resolve_literature_source()` 的
   默认链不变（pytest=mock，运行时=crossref）。启用 apodex 必须显式设
   `LITERATURE_SOURCE=apodex`。
3. **证据纪律不让步**：apodex 条目进 state 后走同一套 `citation_indices`
   → 综述引用回溯链（structure_checks 的 invented_citation /
   citation_year_mismatch）。模型说"有这篇论文"不等于允许写进综述；
   编号表之外的一切引用照样拦。
4. **过期即退场**：本 ADR 有效期以免费窗口为限。到期后清理本模块与测试,
   不留死代码。

## 后果

- +1 可选源、+7 契约测试（全部 mock，不打网）。
- 综述回溯两条新规则本周生效（先红后绿）：
  - `citation_year_mismatch`——[N] 邻近的作者-年份必须与编号指向条目的
    年份一致，张冠李戴直接结构失败（分数上限 0.65）。
  - 编号表非空时，作者-年份叙述所在句必须带合法 [N]（`invented_citation`
    家族扩展），无从核对的主张不许出现。

## 拒绝的替代方案

- 用 MiniMax 直接当深搜源：MiniMax 已是生成/评审通道的 LLM 供应商,再让它
  掌管文献事实层会把"生成"和"证据"压在同一供应商身上;违背核对分权。
- 把 FrontierAgent 运行时接进来跑文献:组件太重,且文献检索不需要任务沙盒。
