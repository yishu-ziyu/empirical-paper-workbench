"""Codex CoPaper CLI v0.3 (gray-box, modular).

Subcommands:
- run-workbench: 整链路 (orchestrator.run_workbench)
- auto-research: 自动研究 (auto_research_service.run_auto_research)
- run-agent:     单跑某 agent (orchestrator._run_stage + graybox a/e/v/r/s)
- resume:        从 last checkpoint 续跑
- inspect:       列 run / agent / checkpoint / paper
- demo:          一键 tour 某个 run

子模块:
- _common: AGENT_ROLES + helpers (save checkpoint, list runs, list agents, default output files)
- graybox: _prompt_graybox (a/e/v/r/s) + cmd_run_agent
- inspect_mod: cmd_inspect
- resume: cmd_resume
- demo: cmd_demo
- __main__: argparse + main()
"""
