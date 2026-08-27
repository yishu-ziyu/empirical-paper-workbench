status: done
ran: cd /Users/mahaoxuan/Desktop/经济学论文/econpaper && ./agent/.venv/bin/python -m pytest agent/tests/test_review_chapter.py agent/tests/test_review_weights_and_channel.py agent/tests/test_schema_consistency.py -q --tb=short → 33 passed; ./backend/.venv/bin/python -m pytest backend/tests/test_review.py -q --tb=short → 18 passed
changed: agent/nodes/review_chapter.py; agent/protocols.py; agent/state.py; backend/facade.py; backend/schemas/review.py; backend/schemas/responses.py; backend/routers/chapter.py; backend/routers/review.py; agent/tests/test_review_chapter.py; agent/tests/test_review_weights_and_channel.py; backend/tests/test_review.py; docs/handoffs/EXEC-1.STATUS.md
risk: 真 LLM 若返回缺 rubric 键的合法 JSON，会当成功真审（review_source=llm），不会走 mock_fallback
