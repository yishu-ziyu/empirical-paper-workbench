# 方法列如何进门

> 上级：[Proposed Design](../04-proposed-design.md)


今天 `DirectionRequest` 丢掉一切额外键。`charls_config` 停在 session，不投影进 `research_direction`。识别在缺列时直接 `star_rating=None`。

**门加宽（同一批实现估计分派）：**

```python
# backend/routers/outline.py
class DirectionRequest(BaseModel):
    question: str
    dv: str
    iv: str
    controls: List[str] = Field(default_factory=list)
    method: str
    template: str = "cn_journal"
    claim: Optional[str] = None
    time_col: Optional[str] = None
    id_col: Optional[str] = None
    first_treat_col: Optional[str] = None
    instrument_col: Optional[str] = None
    instruments: Optional[List[str]] = None
    endogenous_col: Optional[str] = None
    running_var: Optional[str] = None
    cutoff: Optional[float] = None
    unit_col: Optional[str] = None
    treated_unit: Optional[str] = None
    treatment_time: Optional[Any] = None
    cluster: Optional[str] = None
    cluster_levels: List[str] = Field(default_factory=list)
    heterogeneity_groups: List[str] = Field(default_factory=list)
    model_config = {"extra": "allow"}
```

`set_direction` 组装方向时按此优先级填方法列（先出现的赢，不覆盖用户已填）：

1. 本次 `DirectionRequest` 字段  
2. `state.charls_config.variable_mapping` 与确认过的 `waves`（CHARLS：`pid`→`id_col`，`wave`→`time_col`）  
3. `state.panel_id` / `state.time_col`（清洗平衡步留下的）  
4. CSV 列名恰好等于 `year`/`wave`/`id`/`pid`/`state` 时的保守猜测，并写入 `degradations`（`reason="column_guessed"`）

没有猜测到的列保持缺失。识别与估计按缺失降级，不编列。

---
