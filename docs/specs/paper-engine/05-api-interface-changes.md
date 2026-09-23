# API / Interface Changes

> 上级：[econpaper 论文发动机：数字先于正文](../paper-engine.md)


## `DirectionResponse`（预写第一次写出 `results` 的同一批）

```python
class DirectionResponse(BaseModel):
    outline: List[OutlineChapterResponse] = Field(default_factory=list)
    research_direction: Any = None
    star_rating: Optional[int] = None          # int 或 JSON null
    identification_failed: bool = False
    identification_report: Optional[str] = None
    results: Optional[str] = None
    estimate: Optional[Dict[str, Any]] = None  # 含 treatment_row, produced_by, status
    claim: Optional[str] = None
    literature_source: Optional[str] = None
    degradations: List[Dict[str, Any]] = Field(default_factory=list)
    write_blockers: List[str] = Field(default_factory=list)
```

`set_direction_and_outline` 改调 `run_prewrite`，把上列字段填进响应。0 星：`results` 为空，`write_blockers=["star_0"]`，无 outline。

`OutlineChapterResponse` 已 `extra="allow"`，可带 `bind`。

## Facade

- `set_direction_and_outline` → `run_prewrite`  
- `generate_chapter` / `regenerate_chapter`：忽略 `TRUTH_KEYS`；节点 `write_blocked` → 409；**成功写入后调用 `review_chapter`，再 `save_state`**  
- `GenerateChapterResponse` / `RegenerateResponse` 增加：`score`, `auto_decision`（`pass`/`fail`），`review_source`, `review_degraded`, `grounding_failures`。回退 idx 时 `auto_decision="fail"`，仍 200，不是静默通过  
- `get_review`：投影 `review_source` / `review_degraded` / `grounding_failures`  
- `record_degradation(..., visible=False)`  
- 模块级 `review_chapter_node`（与其它节点同一 monkeypatch 接缝）

不新开 MCP。不强制新 `GET /engine-artifacts`：第一读是这次 POST。

## 协议（评审字段）

`ReviewOutput` **必须**增加（否则 `test_schema_consistency` 红）：

```python
class ReviewOutput(TypedDict, total=False):
    review_feedback: List[str]
    revision_suggestions: List[str]
    review_scores: List[float]
    review_rubrics: List[ReviewRubric]
    review_iteration: int
    review_chapter_index: int
    current_chapter_index: int
    review_source: str          # "llm" | "mock" | "mock_fallback"
    review_degraded: bool
    grounding_failures: List[str]
```

三键同步进 `EconPaperState`。`LiteratureOutput` 增加 `literature_produced_by`。

## 旅程（与写出 `results` 同一批）

`_infer_journey`：

- 第 4 站（估计建模）看 `_estimate_ran`，**不要** `body_chapters`  
- 第 5 站看 `_robustness_ran`  
- 第 6 站看 `body_chapters` 或评审字段  

`test_journey.py`：只有估计、没有正文时，currentStage 已过识别。

## 协议

- `EstimateOutput` **已存在**。补文档字段：`estimate` 字典内的 `produced_by` / `treatment_row` / `estimator`。不必新 TypedDict。  
- `GenerateChapterOutput` 增加 `write_blocked: bool`、`write_blockers: list`。`test_schema_consistency.py` 要求这些键 ⊆ `EconPaperState`，故 state 同步加。  
- `ReviewOutput` 增加 `review_source` / `review_degraded` / `grounding_failures`（见上）。  
- 不要只写一个不挂到任何节点 Output 的 `EngineFlags`。

---
