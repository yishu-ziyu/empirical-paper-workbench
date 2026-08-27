status: done
ran: cd /Users/mahaoxuan/Desktop/经济学论文/econpaper && ./agent/.venv/bin/python -m pytest agent/tests/test_estimate.py -q --tb=short → 9 passed
changed: agent/nodes/estimate.py（Bacon 禁 TWFE 且无 first_treat_col 时直接 _error，不再跑 feols 再标 degraded）；agent/tests/test_estimate.py（无队列列 error 夹具 + 有队列列不得回落到 feols）。未改 graph / prewrite / robustness / identification / generate_chapter / 评审。
risk: identification_diag 若把 forbidden_weight_share 写成 40 而不是 0.4，或 Bacon 行的 test 名不是 bacon_decomposition，仍会当成未超阈去跑 TWFE。
