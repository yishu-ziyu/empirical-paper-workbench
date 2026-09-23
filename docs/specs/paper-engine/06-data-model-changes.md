# Data Model Changes

> 上级：[econpaper 论文发动机：数字先于正文](../paper-engine.md)


无独立库迁移。

| 字段 | 谁写 | 备注 |
| --- | --- | --- |
| `estimate.produced_by` / `treatment_row` / `estimator` | `estimate` | 开写与接地的针 |
| `robustness_results.produced_by` / `diagnostics` / `degraded` / `reason` | `robustness_check` | 占位 summary 不算已跑 |
| `degradations` | 各节点 | 含 `visible` |
| `write_blocked` / `write_blockers` | `generate_chapter` | 挂在 GenerateChapterOutput |
| `review_degraded` / `review_source` / `grounding_failures` | `review_chapter`（挂 `ReviewOutput`） | Facade 写章后调用；GET 投影 |
| `literature_produced_by` | `search_literature` | `_literature_ran` 优先看它 |
| `outline[i].bind` | `generate_outline` | 快照 |
| `main_specification` 方法键 | `set_direction` | 见上表 |
| `research_direction` 方法列 | 门 + 投影 | extra=allow |

旧会话缺 `produced_by`：结果/综述 409，人再点方向。

本设计**已取代** ADR-0010「文献默认仍 mock」：`resolve_literature_source` 运行时最后一档为 `crossref`。pytest / `ECONPAPER_LLM=mock` 仍 mock。无网则 `mock_degraded`。

---
