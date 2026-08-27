status: done
ran: cd /Users/mahaoxuan/Desktop/经济学论文/econpaper && ./agent/.venv/bin/python -m pytest agent/tests/test_generate_chapter.py agent/tests/test_generate_chapter_versions.py agent/tests/test_graph_six_chapters.py agent/tests/test_estimate.py -q --tb=short → 44 passed
changed: agent/nodes/generate_chapter.py; agent/tests/test_generate_chapter.py; agent/tests/test_generate_chapter_versions.py。未改 bind / 开写门 / grounding / review_chapter / rollback / prompts / estimate。test_estimate.py 断言未破，未改。
risk: rollback 若再拼一次主表，旧 versions[k] 会叠成两张表（执行 4 的范围）。
