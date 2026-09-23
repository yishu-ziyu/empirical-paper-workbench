# Rollout Plan

> 上级：[econpaper 论文发动机：数字先于正文](../paper-engine.md)


本地单用户。

| 变量 | pytest | 运行时（文献批次前） | 文献批次后 |
| --- | --- | --- | --- |
| `ECONPAPER_LLM` / `in_pytest` | mock | MiniMax | 同左 |
| `LITERATURE_SOURCE` / resolver 最后一档 | mock | mock | `crossref`（已落地） |

回退：还原该批文件。旧会话再 `POST /direction`。

| 风险 | 严重度 | 缓解 |
| --- | --- | --- |
| 开写检查让未灌就绪字段的章节单测变 no-op | 高 | `make_write_ready_state`；下列文件全部改种子 |
| Facade 与图分叉 | 高 | 只许 `run_prewrite` 一条预写 |
| 扇入双触发 `generate_title` | 中 | 第一批线性；并行单测「title 一次」 |
| Crossref 挡主表 | 中 | 估计在文献前；第一批 mock |
| `test_generate_chapter_all_six_types` 靠假 `results` | 高 | 改种子，禁止真值 render_kwargs |

必须改种子或断言的、直接调用 `generate_chapter(` 的测试文件：

- `agent/tests/test_generate_chapter.py`
- `agent/tests/test_generate_chapter_versions.py`
- `agent/tests/test_graph_six_chapters.py`（`_loop_state`；此文件**没有**稳健性节点，是迷你章节环，不是“六章后才稳健性”）
- `agent/tests/test_citation_markers.py`
- `agent/tests/test_threat_cards.py`
- `agent/tests/test_revision_loop.py`
- `agent/tests/test_estimate.py`（`test_results_chapter_user_prompt_contains_estimate`）
- `backend/tests/test_chapter.py`（含 `render_kwargs.results="R"`）
- `backend/tests/test_regenerate.py`（若走真节点）
- `backend/tests/test_facade.py`（`test_set_direction_and_outline_calls_both_nodes` 的调用序；`test_generate_chapter_merges_render_kwargs`）
- `backend/tests/test_graph.py`（`test_graph_has_three_nodes` 不得再 invoke 出标题）
- `backend/tests/test_journey.py`

`conftest.py` 增加完整状态字典（不是 POST 封装）：

```python
def make_write_ready_state(**overrides) -> dict:
    treatment_row = "| age | 0.1234 | 0.0456 | 0.0078 |"
    base = make_state(
        research_direction={
            "question": "年龄与收入",
            "dv": "income",
            "iv": "age",
            "method": "ols",
            "claim": "association",
        },
        identification_diag={
            "strategy": None,
            "diagnostics": [],
            "passed": True,
            "report": "OLS 无识别套餐，按相关表述。",
            "star_rating": None,
        },
        star_rating=None,
        estimate={
            "status": "ok",
            "produced_by": "estimate",
            "method": "ols",
            "estimator": "statspai.feols",
            "treatment": "age",
            "coef": 0.1234,
            "se": 0.0456,
            "p": 0.0078,
            "n": 5,
            "treatment_row": treatment_row,
            "formula": "income ~ age",
        },
        results=(
            "# 主结果\n\n| 变量 | 系数 | SE | p |\n"
            "|------|------|----|---|\n" + treatment_row
        ),
        robustness_results={
            "produced_by": "robustness_check",
            "diagnostics": [],
            "degraded": True,
            "reason": "no_cluster_or_groups",
            "summary_table": "# 稳健性",
        },
        literature_source="mock",
        literature_query="q",
        literature_produced_by="search_literature",
        literature_entries=[
            {"title": "T", "authors": ["A"], "year": 2020, "doi": "10.1/x", "source": "mock"}
        ],
        citation_indices={"10.1/x": 1},
        outline=make_six_chapter_outline(),
        current_chapter_index=0,
    )
    base.update(overrides)
    return base
```

章节 HTTP 单测：`facade.seed_state(sid, make_write_ready_state())`，**不要**经 `_seed_session_state` → `POST /direction`。方向端到端：`iv=age`，或给 `backend/tests` 样本 CSV 加上 `education`。`make_state()` 保持最小。

---
