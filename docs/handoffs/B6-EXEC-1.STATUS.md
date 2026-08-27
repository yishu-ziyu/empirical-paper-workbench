status: done
ran: cd /Users/mahaoxuan/Desktop/经济学论文/econpaper && ./agent/.venv/bin/python -m pytest agent/tests/test_graph_fanin.py agent/tests/test_graph_six_chapters.py -q --tb=short → 14 passed; ./backend/.venv/bin/python -m pytest backend/tests/test_graph.py → collect error（backend venv 无 psycopg，import graph 失败）；agent venv 跑 backend/tests/test_graph.py 则 backend/tests/conftest.py 要 fastapi。路由断言已在 agent/tests/test_graph_six_chapters.py 同步改绿。未改 run_prewrite。
changed: agent/graph.py; agent/tests/test_graph_fanin.py; agent/tests/test_graph_six_chapters.py; backend/tests/test_graph.py; docs/handoffs/B6-EXEC-1.STATUS.md
risk: 两条独立边（不是 add_edge([robustness, cite], title)）会让 generate_title 跑两次；以后改边若拆开 waiting_edges 会再双触发
