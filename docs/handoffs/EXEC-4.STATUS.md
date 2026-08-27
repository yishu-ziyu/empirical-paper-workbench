status: done
ran: `cd /Users/mahaoxuan/Desktop/经济学论文/econpaper && ./agent/.venv/bin/python -m pytest agent/tests/test_search_literature.py agent/tests/test_crossref_source.py -q --tb=short` → 30 passed
changed:
- agent/nodes/search_literature.py
- agent/tests/test_search_literature.py
- agent/tests/test_crossref_source.py
- docs/adr/0010-one-product-merge.md
- docs/specs/paper-engine.md
risk: 运行时无网时若有人只看 `literature_source=="crossref"` 当成功，会漏掉 `mock_degraded`；本批失败路径已标降级，但调用方若未读该字段仍可能把 mock 条目当 Crossref。
