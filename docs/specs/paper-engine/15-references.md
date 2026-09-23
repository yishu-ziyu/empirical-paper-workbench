# References

> 上级：[econpaper 论文发动机：数字先于正文](../paper-engine.md)


- 本仓：`docs/product/glossary.md`；ADR-0003 / 0004 / 0007 / 0008 / 0009 / **0010（文献默认 mock 由本设计在文献批次取代）**。  
- 代码：`agent/graph.py`，`backend/facade.py`，`backend/routers/outline.py`，`backend/routers/chapter.py`，`agent/nodes/estimate.py`，`identification_verify.py`，`review_chapter.py`，`review_sources/mock_review.py`，`review_sources/structure_checks.py`，`search_literature.py`，`robustness_check.py`，`generate_chapter.py`，`design/spec.py`，`llm/router.py`，`prompts/methods.py`，`prompts/results.py`，`prompts/lit_review.py`。  
- StatsPAI：`statspai.feols`，`statspai.ivreg`（`y ~ (endog ~ z) + exog`），`statspai.rdrobust`，`statspai.synth`，`statspai.callaway_santanna`。不要用 `iv_diag` 当主估计。  
- 书：机制对应见上表「拒绝的模式」；实现说明不再标章号。本地 `chapters/`。  
- 存在条件：`/Users/mahaoxuan/Desktop/coding/wiki/standards/existence-conditions.md`。

---
