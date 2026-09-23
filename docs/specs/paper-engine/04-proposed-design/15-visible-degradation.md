# 可见降级（评审假审提前关）

> 上级：[Proposed Design](../04-proposed-design.md)


`call_review_llm` 在 JSON/异常降级时仍可调 `mock_review_llm`，但必须让 `review_chapter` 写出：

```python
review_source = "mock_fallback"  # 或 mock / llm
review_degraded = True
```

并 `state.degradations` 追加 `{node, reason, fallback, visible: True, timestamp}`。

`facade.record_degradation(..., visible: bool = False)`。`GET /sessions/{id}/degradation` 原样返回 `visible`。

`facade.get_review` 与 `ReviewInfoResponse` **同一批**增加：`review_source`, `review_degraded`, `grounding_failures`。`GET /review` 不再把假审显示成真审。

改 `test_review_bad_json_falls_back_to_mock`：仍断言不崩、有 rubric；**加** `review_chapter` 集成断言 `review_source=="mock_fallback"`；`get_review` 投影该字段。不再把“沉默降级”当契约。

这批不依赖 IV 公式或 Crossref。但 **1b 必须测调用**：`POST /generate-chapter`（或 Facade `generate_chapter`）之后 `GET /review` 有分数；不是只测手写进 state 的投影。`backend/tests/test_review.py` 增加这条调用，不是只读。

---
