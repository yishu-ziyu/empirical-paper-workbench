status: done
ran: cd /Users/mahaoxuan/Desktop/经济学论文/econpaper && ./agent/.venv/bin/python -m pytest agent/tests/test_grounding.py -q --tb=short → 9 passed
changed: agent/nodes/review_sources/grounding.py; agent/tests/test_grounding.py; docs/handoffs/B4-EXEC-1.STATUS.md
risk: 处理行写成「年龄」而不是 estimate.treatment / treat / ATT / RD / SCM_gap 时，另造系数不会被 invented_number 抓住
