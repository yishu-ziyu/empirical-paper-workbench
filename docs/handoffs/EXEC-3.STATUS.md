status: done
ran: cd /Users/mahaoxuan/Desktop/经济学论文/econpaper && ./agent/.venv/bin/python -m pytest agent/tests/test_estimate.py agent/tests/test_direction_spec.py agent/tests/test_robustness_check.py agent/tests/test_identification_verify.py agent/tests/test_set_direction.py -q --tb=short → 33 passed
changed: backend/routers/outline.py; agent/design/spec.py; agent/nodes/set_direction.py; agent/nodes/estimate.py; agent/nodes/robustness_check.py; agent/tests/test_estimate.py; agent/tests/test_direction_spec.py; agent/tests/test_robustness_check.py; agent/tests/test_identification_verify.py; agent/.venv 补装 ../StatsPAI（import statspai 原先失败）
risk: DiD 在 Bacon forbidden 超阈且没有 first_treat_col 时仍走 TWFE（status=degraded），交错处理组会把偏误写进主表。
