status: done
ran: `cd /Users/mahaoxuan/Desktop/经济学论文/econpaper && ./agent/.venv/bin/python -m pytest agent/tests/test_rollback.py agent/tests/test_results_table_grounding.py -q --tb=short` → 13 passed（rollback 10 绿；联调 3 绿，执行1/2 已落地）
changed:
- agent/tests/test_rollback.py
- agent/tests/test_results_table_grounding.py（新建）
- agent/nodes/rollback.py 未改（已是 content = versions[k]，不再拼 results）
risk: 若以后有人在 rollback 里“补拼”当前 state.results，旧版本会变成 old+当前表；`test_rollback_keeps_old_table_and_does_not_resplice_results` 会红。
