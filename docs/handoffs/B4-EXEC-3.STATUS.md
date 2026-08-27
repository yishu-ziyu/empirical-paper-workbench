status: done
ran: cd /Users/mahaoxuan/Desktop/经济学论文/econpaper && ./agent/.venv/bin/python -m pytest agent/tests/test_review_chapter.py -q --tb=short → 28 passed
changed: agent/nodes/review_chapter.py; agent/tests/test_review_chapter.py（只追加结果章接地用例）
risk: 结果章若再写一张完整 `| 变量 | 系数 | SE | p |` 表头，`invented_table` 会把综合分封顶并回炉。
