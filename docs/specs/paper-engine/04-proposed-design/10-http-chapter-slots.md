# HTTP 章节槽

> 上级：[Proposed Design](../04-proposed-design.md)


节点必须认操作台点的那一章。`POST /generate-chapter` 已校验 `chapter.type` 并写入 `state["current_chapter"]`。今天节点丢掉它。

```python
def _resolve_slot(state) -> tuple[int, dict]:
    outline = state.get("outline") or []
    requested = state.get("current_chapter") or {}
    want = requested.get("type") if isinstance(requested, dict) else None
    if want:
        for i, spec in enumerate(outline):
            if isinstance(spec, dict) and spec.get("type") == want:
                return i, spec
        raise ValueError(f"chapter.type {want!r} not in outline")
    idx = state.get("current_chapter_index")
    if idx is None or not outline or idx >= len(outline):
        return -1, {}
    return idx, dict(outline[idx])
```

图侧测试不设 `current_chapter`，仍按下标走。操作台以 `chapter.type` 为准。写完后 `current_chapter_index = idx + 1`（与现语义一致）。章节 HTTP 单测**不要**走 `POST /direction` 灌就绪态。`_seed_session_state` 今天会 `iv=education`，样本 CSV 只有 `income,age,city`，预写后 `estimate.status=error`，结果章 409。改为 `facade.seed_state(sid, make_write_ready_state())`。方向端到端另测：`iv=age`（列存在），或给样本 CSV 加 `education`。

---
