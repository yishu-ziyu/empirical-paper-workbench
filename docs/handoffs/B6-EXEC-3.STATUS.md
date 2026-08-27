status: done
ran: cd /Users/mahaoxuan/Desktop/经济学论文/econpaper && ./agent/.venv/bin/python -m pytest agent/tests/test_robustness_check.py -q --tb=short → 8 passed
changed: agent/nodes/robustness_check.py; agent/tests/test_robustness_check.py
risk: 判断 CS 只认 estimate.estimator==statspai.callaway_santanna；主估计已是 CS 但没写下这个字段时，稳健性仍会走 TWFE 的 y ~ treat 套餐。
