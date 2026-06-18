# Plugin Package Validation

Status: PASS
Generated: 2026-06-17T20:47:38

## Package

- Plugin: `plugins/statspai-empirical-workflow-runtime`
- Manifest: `plugins/statspai-empirical-workflow-runtime/package_manifest.json`
- Install map entries: 6
- Target requirements: 6

## Commands

### `python3 /Users/mahaoxuan/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py /Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/plugins/statspai-empirical-workflow-runtime`

- cwd: `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板`
- exit: 0

stdout:

```text
Plugin validation passed: /Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/plugins/statspai-empirical-workflow-runtime
```

### `python3 scripts/validate_package.py`

- cwd: `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/plugins/statspai-empirical-workflow-runtime`
- exit: 0

stdout:

```text
PASS
```

### `python3 /Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/plugins/statspai-empirical-workflow-runtime/scripts/install_into_project.py --target /var/folders/k6/7c96rbxd1r782myg_bnlqshw0000gn/T/statspai_plugin_target_b1cr7kr8/second-project`

- cwd: `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板`
- exit: 0

stdout:

```text
DRY-RUN target=/private/var/folders/k6/7c96rbxd1r782myg_bnlqshw0000gn/T/statspai_plugin_target_b1cr7kr8/second-project
- would-copy: skills/statspai-empirical-workflow -> .codex/skills/statspai-empirical-workflow
- would-copy: assets/project/.codex/agents -> .codex/agents
- would-copy: assets/project/workflows/skill_subagent_registry.json -> workflows/skill_subagent_registry.json
- would-copy: assets/project/workflows/schemas/skill_subagent_registry.schema.json -> workflows/schemas/skill_subagent_registry.schema.json
- would-copy: assets/project/scripts/31_validate_skill_subagent_registry.py -> scripts/31_validate_skill_subagent_registry.py
- would-copy: assets/project/scripts/32_test_skill_subagent_negative.py -> scripts/32_test_skill_subagent_negative.py
PASS
```

### `python3 /Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/plugins/statspai-empirical-workflow-runtime/scripts/install_into_project.py --target /var/folders/k6/7c96rbxd1r782myg_bnlqshw0000gn/T/statspai_plugin_target_b1cr7kr8/second-project --apply --overwrite`

- cwd: `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板`
- exit: 0

stdout:

```text
APPLY target=/private/var/folders/k6/7c96rbxd1r782myg_bnlqshw0000gn/T/statspai_plugin_target_b1cr7kr8/second-project
- copied: skills/statspai-empirical-workflow -> .codex/skills/statspai-empirical-workflow
- copied: assets/project/.codex/agents -> .codex/agents
- copied: assets/project/workflows/skill_subagent_registry.json -> workflows/skill_subagent_registry.json
- copied: assets/project/workflows/schemas/skill_subagent_registry.schema.json -> workflows/schemas/skill_subagent_registry.schema.json
- copied: assets/project/scripts/31_validate_skill_subagent_registry.py -> scripts/31_validate_skill_subagent_registry.py
- copied: assets/project/scripts/32_test_skill_subagent_negative.py -> scripts/32_test_skill_subagent_negative.py
PASS
```

### `python3 scripts/31_validate_skill_subagent_registry.py`

- cwd: `/var/folders/k6/7c96rbxd1r782myg_bnlqshw0000gn/T/statspai_plugin_target_b1cr7kr8/second-project`
- exit: 0

stdout:

```text
PASS report=artifacts/skill_subagent_validation_report.md
```

### `python3 scripts/32_test_skill_subagent_negative.py`

- cwd: `/var/folders/k6/7c96rbxd1r782myg_bnlqshw0000gn/T/statspai_plugin_target_b1cr7kr8/second-project`
- exit: 0

stdout:

```text
PASS missing 10_defense binding rejected
```

## Checks

- Plugin manifest passed the Codex plugin validator.
- Package manifest sources exist.
- Installer dry-run completed against a temporary second project.
- Installer apply completed against a temporary second project.
- Installed registry validation passed in the temporary second project.
- Installed negative test passed in the temporary second project.
