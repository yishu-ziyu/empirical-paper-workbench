status: done
ran: `cd /Users/mahaoxuan/Desktop/经济学论文/econpaper && ./agent/.venv/bin/python -m pytest agent/tests/test_structure_checks.py -q --tb=short` → 14 passed
changed:
- agent/nodes/review_sources/structure_checks.py
- agent/tests/test_structure_checks.py
risk: 空表时只认 Name (YYYY) / Name and Name (YYYY) / (Author, YYYY) / （张三, YYYY）。`et al.`、`smith (2020)` 小写、`Smith (2020a)` 不会报 invented_citation。
