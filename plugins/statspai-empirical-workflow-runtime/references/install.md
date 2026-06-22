# StatspAI Empirical Workflow Runtime Plugin

用途：把 P4 注册层迁移到第二个项目。

## 包含什么

- Codex plugin manifest: `.codex-plugin/plugin.json`
- Skill: `skills/statspai-empirical-workflow/`
- Native subagent specs: `assets/project/.codex/agents/statspai-*.toml`
- Registry: `assets/project/workflows/skill_subagent_registry.json`
- Schema: `assets/project/workflows/schemas/skill_subagent_registry.schema.json`
- Validators: `assets/project/scripts/31_validate_skill_subagent_registry.py` and `32_test_skill_subagent_negative.py`

## 安装到第二项目

```bash
python3 plugins/statspai-empirical-workflow-runtime/scripts/install_into_project.py --target /path/to/second-project --apply
```

默认是 dry-run，不写文件：

```bash
python3 plugins/statspai-empirical-workflow-runtime/scripts/install_into_project.py --target /path/to/second-project
```

## 目标项目必须已有

- `workflows/registry.json`
- `workflows/tool_adapters.json`
- `workflows/orchestrator_policy.json`
- `scripts/23_workflow_runbook.py`
- `scripts/24_validate_runbook_api.py`
- `scripts/25_agent_runtime_preflight.py`

这些是 P0-P3 runtime 层。这个包只负责 P4 注册层。

## 安装后验证

```bash
python3 scripts/31_validate_skill_subagent_registry.py
python3 scripts/32_test_skill_subagent_negative.py
```
