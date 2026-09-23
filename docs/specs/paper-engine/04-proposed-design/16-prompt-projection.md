# 投影进 prompt

> 上级：[Proposed Design](../04-proposed-design.md)


```python
# agent/engine/bind.py
def bind_chapter_kwargs(state, chapter_spec) -> dict:
    rd = state.get("research_direction") or {}
    rob = state.get("robustness_results") or {}
    return {
        "research_question": rd.get("question") or state.get("research_question") or "",
        "method": chapter_spec.get("method") or rd.get("method") or "",
        "results": state.get("results") or "",
        "robustness_table": rob.get("summary_table") or "",
        "key_references": format_entries(state.get("literature_entries") or []),
        "citation_indices": state.get("citation_indices") or {},
        "star_rating": state.get("star_rating"),
        "claim": claim_mode(state),
        "identification_report": (state.get("identification_diag") or {}).get("report") or "",
    }
```

覆盖 `_collect_render_kwargs` 同名键。真值只来自节点产物。

---
