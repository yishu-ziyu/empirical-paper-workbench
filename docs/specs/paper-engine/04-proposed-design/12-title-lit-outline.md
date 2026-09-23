# 标题、文献查询、大纲

> 上级：[Proposed Design](../04-proposed-design.md)


标题在预写里、估计之后（增强：可以点名符号）。无估计时 `generate_title` 只用方向，不挡预写。

`search_literature` 查询只拼方向四问，不拼 `title_chapter`。

```python
def resolve_literature_source(state) -> str:
    from llm.ssot import in_pytest
    explicit = (state.get("literature_source") or "").strip()
    if explicit:
        return explicit
    if in_pytest() or os.environ.get("ECONPAPER_LLM") == "mock":
        return "mock"
    env = (os.environ.get("LITERATURE_SOURCE") or "").strip()
    if env:
        return env
    return "crossref"  # 文献批次已取代 ADR-0010 默认 mock
```

`test_search_empty_state_defaults` 继续断言 pytest 下 `"mock"`。

`generate_outline` 仍写死六槽 type。每槽写 `bind` 快照（条数、是否有 `treatment_row`）。LLM 只写 `llm_summary`。

---
