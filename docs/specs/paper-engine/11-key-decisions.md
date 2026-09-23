# Key Decisions

> 上级：[econpaper 论文发动机：数字先于正文](../paper-engine.md)


1. 保持一张 LangGraph。不换规划器，不拆蜂群，不做 MCP/A2A 产品。  
2. 第一批图是线性预写到大纲后 `END`。章节只走 Facade。不发明 `wait_*`。  
3. `run_prewrite` 是图与 Facade 唯一预写入口。顺序：识别 → **估计** → 稳健性 → 文献 → 标题 → 大纲。  
4. 开写检查在 `generate_chapter`，且按 `chapter.type` 分槽。  
5. HTTP `chapter.type` 选槽；与下标冲突时 type 赢。  
6. `render_kwargs` 不得写入 `TRUTH_KEYS`。  
7. `MainSpecification` 按方法写清 StatsPAI 调用。IV 主表是 `ivreg`，不是 `iv_diag.beta_2sls`。稳健性同一张表。  
8. 门 `extra="allow"` + 显式方法字段，并投影 `charls_config` / 面板列。  
9. `treatment_row` 是表同一的针。`versions[0] = prose + results`。结果章 prompt 禁止再画表。  
10. 关联主张在结构检查、mock 评审、权重、prompt、rubric 前检查五处一起关。  
11. 评审 JSON 失败在早期批次就对 `GET /review` 可见。  
12. `star_rating is None` + `claim_mode==association` 是 OLS 成功，不是硬条失败。  
13. `claim_mode` 只降不升。  
14. 上传后权威状态是 Facade 内存。  
15. 文献缺省改 Crossref **已取代** ADR-0010 的 mock 默认；pytest / `ECONPAPER_LLM=mock` 仍 mock。  
16. `EstimateOutput` 已存在；`write_blocked` 必须挂在 `GenerateChapterOutput`。  
17. 图缩小后，Facade 写章必须调用 `review_chapter`。回退不当通过。  
18. association mock 分数钉死为 0.7/0.7/0.7/0.7 + 长文可读 0.8，保证综合分 ≥ 0.7。  
19. `invented_number` 只打处理标签行。  
20. `CausalResult` 用 `result.estimate`，不用 `float(result)`。

---
