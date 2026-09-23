# 客户端不得注入真值

> 上级：[Proposed Design](../04-proposed-design.md)


```python
# facade.generate_chapter
for k, v in (render_kwargs or {}).items():
    if k in TRUTH_KEYS:
        continue
    if k not in state or state.get(k) in (None, ""):
        state[k] = v
```

`render_kwargs` 视为遗留，只允许非真值（如 `data_summary`）。`regenerate_chapter` 不跑 `run_prewrite`，但走同一 `generate_chapter` 节点，因此按章就绪仍然生效；过期方向留下的 `estimate` 若 `produced_by` 仍在，可以重写该章（同一设定）。换方向必须再 `POST /direction`，`run_prewrite` 覆盖 `estimate`。

`test_generate_chapter_merges_render_kwargs` 改为：注入 `results` 被忽略；注入 `data_summary` 仍合并。

---
