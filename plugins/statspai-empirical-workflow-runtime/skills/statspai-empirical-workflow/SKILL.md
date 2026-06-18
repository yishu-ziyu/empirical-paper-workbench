---
name: statspai-empirical-workflow
description: Run and inspect the project-level ten-step empirical paper workflow. Use when Codex needs to route the next CHARLS or StatsPAI-style empirical paper step, check gates, use the policy-gated orchestrator, validate workflow artifacts, or hand work to project subagents without changing the research claim boundary.
---

# StatspAI Empirical Workflow

Use this skill as the project entrypoint for the second-layer workflow runtime.

## Start Here

1. Read `AGENTS.md`, `tasks/agent-loop.md`, and `tasks/todo.md`.
2. Generate or refresh workflow state:
   ```bash
   python3 scripts/23_workflow_runbook.py
   python3 scripts/24_validate_runbook_api.py
   ```
3. If only checking readiness, run:
   ```bash
   python3 scripts/25_agent_runtime_preflight.py
   ```
4. If planning execution, dry-run first:
   ```bash
   python3 scripts/28_agent_orchestrator.py --mode dry-run --no-trace
   ```
5. Execute only policy-allowed adapters:
   ```bash
   python3 scripts/28_agent_orchestrator.py --mode execute --adapter reproduction_verify
   ```

## Boundaries

- Do not claim robust average OOP reduction unless new verified results support it.
- Do not auto-run credentialed, network, browser-download, high-side-effect, or result-rewriting adapters.
- Treat `workflows/orchestrator_policy.json` as the execution boundary.
- Use Chrome preview only after generating a user-facing artifact.
- Record durable changes in `tasks/todo.md`.

## Registration Layer

- Skill registry: `workflows/skill_subagent_registry.json`
- Native subagent specs: `.codex/agents/*.toml`
- Tool adapters: `workflows/tool_adapters.json`
- Orchestrator policy: `workflows/orchestrator_policy.json`
- Trace log: `artifacts/agent_trace_log.jsonl`

## References

- For the ten-step workflow map, read `references/workflow-map.md`.
- For orchestration and safety policy, read `references/orchestrator-policy.md`.
