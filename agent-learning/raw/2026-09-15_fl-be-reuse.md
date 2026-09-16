# econpaper Codex Run Record

- Date: 2026-09-15
- Task ID / state file: FM-E-BUILD-BRYCE-1 / FL-BE-reuse · `runtime/tasks/20260915-fl-be-reuse.md`
- Commit / Git context: `feat/fm-e-build-fl-be-reuse-1` from `fix/fm-e-build-data-rigor-1` @ `4546e4de`
- Model and tool environment: Cursor cloud agent
- Dataset class / research method（不含原始数据）: literature search wrap (OpenAlex / Crossref / S2)
- Task: Thin-wrap `fetch_papers.py` into existing `find_lit`; checkbox before write; no parallel lit pipeline; no synthetic as found
- Result: pass
- Session / run ID:
- Verification commands: pytest agent/tests/test_find_lit.py agent/tests/test_fetch_papers.py agent/tests/test_openalex_source.py agent/tests/test_search_literature.py agent/tests/test_generate_chapter.py agent/tests/test_semantic_scholar.py agent/tests/test_crossref_source.py agent/tests/test_readiness.py — 123 passed. Full `agent/tests` — 898 passed, 2 skipped. `make verify` not run (services down).
- Output evidence locations:

## 成功动作

- Extracted OpenAlex+Crossref+S2 fetch + DOI dedupe into `agent/find_lit/fetch_papers.py`. `search_find_lit` still owns confirmed-design, cards, checkbox, bib/CSL.
- Unconfirmed design does not call `fetch_papers`. Source failure degrades that source; does not fill mock corpus.
- Mock / synthetic / gold sources dropped as not-found (DATA-RIGOR analog). V1 sources remain the FL three.

## 失败动作与根因

- Injected Crossref DOI URLs were stored un-normalized; card path already normalized. Fixed by `_prepare_hit` before dedupe.

## 可复现条件

- Confirmed design + mocked three-source searchers with overlapping DOI URL forms; injected `source=mock|synthetic`.

## 候选模式

- Bryce lit-review is a named fetch helper inside `find_lit`, not a second product object. HTTP stays in `literature_sources`.
