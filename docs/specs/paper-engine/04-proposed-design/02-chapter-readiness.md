# 按章就绪

> 上级：[Proposed Design](../04-proposed-design.md)


```python
# agent/engine/readiness.py

SLOT_REQUIREMENTS = {
    "intro": ("identification",),
    "data_desc": ("identification",),
    "methods": ("identification",),
    "conclusion": ("identification",),
    "results": ("identification", "estimate", "robustness"),
    "lit_review": ("identification", "literature"),
}

TRUTH_KEYS = frozenset({
    "results", "estimate", "robustness_results",
    "identification_diag", "star_rating",
    "literature_entries", "literature_source", "citation_indices",
    "literature_produced_by", "literature_query",
    "citation_graph", "main_specification", "write_blocked",
    "produced_by", "treatment_row", "claim",
})


def paper_ready_to_write(state: dict, chapter_type: str) -> tuple[bool, list[str]]:
    missing: list[str] = []
    if state.get("star_rating") == 0:
        return False, ["star_0"]
    need = SLOT_REQUIREMENTS.get(chapter_type, ("identification",))
    if "identification" in need and not state.get("identification_diag"):
        missing.append("no_identification")
    if "estimate" in need and not _estimate_ran(state):
        missing.append("no_results")
    if "robustness" in need and not _robustness_ran(state):
        missing.append("no_robustness")
    if "literature" in need and not _literature_ran(state):
        missing.append("no_literature")
    return (not missing, missing)


def _estimate_ran(state) -> bool:
    est = state.get("estimate") or {}
    return (
        isinstance(est, dict)
        and est.get("produced_by") == "estimate"
        and est.get("status") in ("ok", "error", "degraded")
        and bool((state.get("results") or "").strip())
        and bool(est.get("treatment_row"))
    )


def _robustness_ran(state) -> bool:
    rob = state.get("robustness_results") or {}
    if not isinstance(rob, dict):
        return False
    if rob.get("produced_by") == "robustness_check":
        return True
    return "diagnostics" in rob


def _literature_ran(state) -> bool:
    """文献节点已跑。

    真：`literature_produced_by == "search_literature"`
    （与 estimate.produced_by 分键，避免抢名）；
    或 `literature_source in {mock_degraded, disabled}`；
    或 `literature_source` 为 mock/crossref/semantic_scholar
    **且** `literature_query` 是 str（可空串）。
    假：source 缺失，或 source 为 mock 但 query 键不存在（节点没跑）。
    """
    if state.get("literature_produced_by") == "search_literature":
        return True
    src = state.get("literature_source")
    if src in {"mock_degraded", "disabled"}:
        return True
    return src in {"mock", "crossref", "semantic_scholar"} and isinstance(
        state.get("literature_query"), str
    )
```

`search_literature` 的 NodeResult 增加 `literature_produced_by: str`，并写入 `EconPaperState`（`test_schema_consistency`）。

`generate_chapter` 开头：解析本章 `type`（见下节）→ `paper_ready_to_write` → 未就绪则返回 `write_blocked=True` 和 `write_blockers`，不写 `body_chapters`。Facade 映射 HTTP 409。

`outline[i].bind` 是 `generate_outline` 按 `SLOT_REQUIREMENTS` 和当时 state 写下的**快照**，给人看。节点开写只认 `SLOT_REQUIREMENTS[type]`，不认客户端改过的 bind（改 bind 不能放宽门）。
