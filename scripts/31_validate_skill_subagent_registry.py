#!/usr/bin/env python3
"""Validate Runtime Gap P4 skill and subagent registration."""

from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path

from jsonschema import ValidationError, validate


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "workflows" / "skill_subagent_registry.json"
SCHEMA_PATH = ROOT / "workflows" / "schemas" / "skill_subagent_registry.schema.json"
WORKFLOW_REGISTRY_PATH = ROOT / "workflows" / "registry.json"
ADAPTER_PATH = ROOT / "workflows" / "tool_adapters.json"
POLICY_PATH = ROOT / "workflows" / "orchestrator_policy.json"
REPORT_PATH = ROOT / "artifacts" / "skill_subagent_validation_report.md"


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def read_json(path: Path, errors: list[str]) -> dict:
    if not path.exists():
        errors.append(f"missing file: {rel(path)}")
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{rel(path)} invalid JSON: {exc}")
        return {}


def path_exists(path_text: str, errors: list[str], label: str) -> Path:
    path = ROOT / path_text
    if not path.exists():
        errors.append(f"missing {label}: {path_text}")
    return path


def parse_skill_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}
    frontmatter = text[4:end].strip().splitlines()
    parsed: dict[str, str] = {}
    for line in frontmatter:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        parsed[key.strip()] = value.strip().strip('"')
    return parsed


def validate_skill_package(package: dict, workflow_ids: set[str], policy_commands: set[str], errors: list[str]) -> None:
    skill_dir = path_exists(package["path"], errors, "skill directory")
    skill_file = path_exists(package["skill_file"], errors, "skill file")
    openai_metadata = path_exists(package["openai_metadata"], errors, "skill openai metadata")
    path_exists(package["safety_policy"], errors, "skill safety policy")
    for reference in package["references"]:
        path_exists(reference, errors, "skill reference")

    unknown_workflows = set(package["covers_workflows"]) - workflow_ids
    if unknown_workflows:
        errors.append(f"skill {package['id']} covers unknown workflows: {', '.join(sorted(unknown_workflows))}")

    safe_entry_commands = {
        "python3 scripts/25_agent_runtime_preflight.py",
        "python3 scripts/28_agent_orchestrator.py --mode dry-run --no-trace",
    }
    for command in package["entry_commands"]:
        if command not in policy_commands and command not in safe_entry_commands:
            errors.append(f"skill {package['id']} entry command is not policy/preflight recognized: {command}")

    if skill_file.exists():
        text = skill_file.read_text(encoding="utf-8")
        if "TODO" in text:
            errors.append(f"{rel(skill_file)} still contains TODO")
        frontmatter = parse_skill_frontmatter(text)
        if frontmatter.get("name") != package["id"]:
            errors.append(f"{rel(skill_file)} frontmatter name does not match registry id")
        if not frontmatter.get("description") or len(frontmatter["description"]) < 80:
            errors.append(f"{rel(skill_file)} description is too short for reliable triggering")
        if str(skill_dir.relative_to(ROOT)) != package["path"]:
            errors.append(f"skill path mismatch for {package['id']}")

    if openai_metadata.exists():
        metadata = openai_metadata.read_text(encoding="utf-8")
        if f"${package['id']}" not in metadata:
            errors.append(f"{rel(openai_metadata)} default_prompt must mention ${package['id']}")
        short_match = re.search(r"short_description:\s*\"([^\"]+)\"", metadata)
        if not short_match:
            errors.append(f"{rel(openai_metadata)} missing quoted short_description")
        elif not 25 <= len(short_match.group(1)) <= 64:
            errors.append(f"{rel(openai_metadata)} short_description must be 25-64 chars")


def validate_subagent(agent: dict, workflow_ids: set[str], adapter_ids: set[str], policy: dict, errors: list[str]) -> None:
    path = path_exists(agent["path"], errors, "native subagent")
    covers = set(agent["covers_workflows"])
    unknown_workflows = covers - workflow_ids - {"all"}
    if unknown_workflows:
        errors.append(f"subagent {agent['id']} covers unknown workflows: {', '.join(sorted(unknown_workflows))}")

    unknown_adapters = set(agent["allowed_adapters"] + agent["blocked_adapters"]) - adapter_ids
    if unknown_adapters:
        errors.append(f"subagent {agent['id']} references unknown adapters: {', '.join(sorted(unknown_adapters))}")

    allowed_by_policy = set(policy.get("allow_execute_adapters", []))
    unsafe_allowed = set(agent["allowed_adapters"]) - allowed_by_policy
    if unsafe_allowed:
        errors.append(f"subagent {agent['id']} allows adapters not executable by policy: {', '.join(sorted(unsafe_allowed))}")

    if path.exists():
        try:
            parsed = tomllib.loads(path.read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError as exc:
            errors.append(f"{rel(path)} invalid TOML: {exc}")
            return
        for field in ["name", "description", "developer_instructions"]:
            if not parsed.get(field):
                errors.append(f"{rel(path)} missing {field}")
        if parsed.get("name") != agent["id"]:
            errors.append(f"{rel(path)} name does not match registry id")
        instructions = parsed.get("developer_instructions", "")
        if "TODO" in instructions:
            errors.append(f"{rel(path)} still contains TODO")
        if "Scope:" not in instructions or "Rules:" not in instructions:
            errors.append(f"{rel(path)} must contain Scope and Rules sections")


def main() -> None:
    errors: list[str] = []
    registry = read_json(REGISTRY_PATH, errors)
    schema = read_json(SCHEMA_PATH, errors)
    workflow_registry = read_json(WORKFLOW_REGISTRY_PATH, errors)
    adapters = read_json(ADAPTER_PATH, errors)
    policy = read_json(POLICY_PATH, errors)

    if registry and schema:
        try:
            validate(instance=registry, schema=schema)
        except ValidationError as exc:
            errors.append(f"registry schema validation failed via {rel(SCHEMA_PATH)}: {exc.message}")

    workflow_ids = {workflow["id"] for workflow in workflow_registry.get("workflows", [])}
    core_workflow_ids = {workflow["id"] for workflow in workflow_registry.get("workflows", []) if re.match(r"^(0[1-9]|10)_", workflow["id"])}
    adapter_ids = {adapter["id"] for adapter in adapters.get("adapters", [])}
    policy_commands = set(policy.get("command_allowlist", []))

    skill_ids = {package["id"] for package in registry.get("skill_packages", [])}
    subagent_ids = {agent["id"] for agent in registry.get("native_subagents", [])}

    for package in registry.get("skill_packages", []):
        validate_skill_package(package, workflow_ids, policy_commands, errors)

    for agent in registry.get("native_subagents", []):
        validate_subagent(agent, workflow_ids, adapter_ids, policy, errors)

    bindings = registry.get("workflow_bindings", [])
    bound_core_workflows = {binding["workflow_id"] for binding in bindings if binding["workflow_id"] in core_workflow_ids}
    missing_core = core_workflow_ids - bound_core_workflows
    extra_workflows = {binding["workflow_id"] for binding in bindings} - workflow_ids
    if missing_core:
        errors.append(f"missing core workflow bindings: {', '.join(sorted(missing_core))}")
    if extra_workflows:
        errors.append(f"bindings reference unknown workflows: {', '.join(sorted(extra_workflows))}")

    for binding in bindings:
        if binding["skill"] not in skill_ids:
            errors.append(f"binding {binding['workflow_id']} references unknown skill: {binding['skill']}")
        missing_subagents = set(binding["subagents"]) - subagent_ids
        if missing_subagents:
            errors.append(f"binding {binding['workflow_id']} references unknown subagents: {', '.join(sorted(missing_subagents))}")
        missing_adapters = set(binding["default_adapters"]) - adapter_ids
        if missing_adapters:
            errors.append(f"binding {binding['workflow_id']} references unknown adapters: {', '.join(sorted(missing_adapters))}")

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    status = "FAIL" if errors else "PASS"
    lines = [
        "# Skill / Subagent Registry Validation",
        "",
        f"Status: {status}",
        "",
        f"- Registry: `{rel(REGISTRY_PATH)}`",
        f"- Schema: `{rel(SCHEMA_PATH)}`",
        f"- Skills: {len(skill_ids)}",
        f"- Native subagents: {len(subagent_ids)}",
        f"- Workflow bindings: {len(bindings)}",
        f"- Core workflow coverage: {len(bound_core_workflows)}/{len(core_workflow_ids)}",
        "",
    ]
    if errors:
        lines.extend(["## Errors", "", *[f"- {error}" for error in errors], ""])
    else:
        lines.extend(
            [
                "## Checks",
                "",
                "- Registry matches JSON schema.",
                "- Skill package files and references exist.",
                "- Skill frontmatter and UI metadata are triggerable.",
                "- Native subagent TOML files parse and match registry ids.",
                "- Ten core workflows have skill/subagent bindings.",
                "- Bound adapters exist and allowed adapters respect orchestrator policy.",
                "",
            ]
        )

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    if errors:
        print(f"FAIL report={rel(REPORT_PATH)}")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)
    print(f"PASS report={rel(REPORT_PATH)}")


if __name__ == "__main__":
    main()
