# Skill / Subagent Registry Validation

Status: PASS

- Registry: `workflows/skill_subagent_registry.json`
- Schema: `workflows/schemas/skill_subagent_registry.schema.json`
- Skills: 1
- Native subagents: 6
- Workflow bindings: 11
- Core workflow coverage: 10/10

## Checks

- Registry matches JSON schema.
- Skill package files and references exist.
- Skill frontmatter and UI metadata are triggerable.
- Native subagent TOML files parse and match registry ids.
- Ten core workflows have skill/subagent bindings.
- Bound adapters exist and allowed adapters respect orchestrator policy.
