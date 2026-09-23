# econpaper 论文发动机：数字先于正文

| 字段 | 值 |
| --- | --- |
| 文档 | Paper Engine Design |
| 作者 | Grok Build（占位） |
| 日期 | 2026-08-16 |
| 修订 | 2026-08-16 r4（`literature_produced_by` / `literature_query` 列入 `TRUTH_KEYS`） |
| 状态 | Draft |
| 产品 | `econpaper/` |
| 范围 | `agent/` + `../dependencies/StatsPAI/` + 产品内置代码导出；FastAPI 只是门；操作台只展示发动机产物 |
| 权威 | `docs/product/glossary.md`、`docs/adr/*`、`agent/graph.py`、`backend/facade.py` |
| 机制目录 | Antonio Gulli《Agentic Design Patterns》中译（本地 `chapters/`）。书是机制清单，不是产品名。 |

**一句话：** 人坐着写一篇实证论文。发动机必须先交出可引用的数字和文献条目，再让模型填六章；OLS 禁止写成因果。

---

## 目录

1. [Overview](paper-engine/01-overview.md)
2. [Background & Motivation](paper-engine/02-background-motivation.md)
3. [Goals & Non-Goals](paper-engine/03-goals-non-goals.md)
4. [Proposed Design](paper-engine/04-proposed-design.md)
5. [API / Interface Changes](paper-engine/05-api-interface-changes.md)
6. [Data Model Changes](paper-engine/06-data-model-changes.md)
7. [Alternatives Considered](paper-engine/07-alternatives-considered.md)
8. [Security & Privacy Considerations](paper-engine/08-security-privacy-considerations.md)
9. [Observability](paper-engine/09-observability.md)
10. [Rollout Plan](paper-engine/10-rollout-plan.md)
11. [Key Decisions](paper-engine/11-key-decisions.md)
12. [Open Questions](paper-engine/12-open-questions.md)
13. [Hard bars（可测试）](paper-engine/13-hard-bars.md)
14. [拒绝的模式](paper-engine/14-rejected-patterns.md)
15. [References](paper-engine/15-references.md)
16. [PR Plan](paper-engine/16-pr-plan.md)
