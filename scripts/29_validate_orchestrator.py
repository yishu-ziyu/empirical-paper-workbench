#!/usr/bin/env python3
"""Validate Runtime Gap P3 orchestrator artifacts and safety policy."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import ValidationError, validate


ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "workflows" / "orchestrator_policy.json"
POLICY_SCHEMA_PATH = ROOT / "workflows" / "schemas" / "orchestrator_policy.schema.json"
RUN_STATE_SCHEMA_PATH = ROOT / "workflows" / "schemas" / "orchestrator_run_state.schema.json"
ADAPTER_PATH = ROOT / "workflows" / "tool_adapters.json"
RUN_STATE_PATH = ROOT / "artifacts" / "orchestrator_run_state.json"
REPORT_PATH = ROOT / "artifacts" / "orchestrator_validation_report.md"
ORCHESTRATOR_SCRIPT = ROOT / "scripts" / "28_agent_orchestrator.py"


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


def main() -> None:
    errors: list[str] = []

    policy = read_json(POLICY_PATH, errors)
    policy_schema = read_json(POLICY_SCHEMA_PATH, errors)
    run_state_schema = read_json(RUN_STATE_SCHEMA_PATH, errors)
    adapters = read_json(ADAPTER_PATH, errors)
    run_state = read_json(RUN_STATE_PATH, errors)

    if not ORCHESTRATOR_SCRIPT.exists():
        errors.append(f"missing file: {rel(ORCHESTRATOR_SCRIPT)}")
    if policy_schema and policy_schema.get("title") != "StatspAI Orchestrator Policy":
        errors.append(f"{rel(POLICY_SCHEMA_PATH)} has unexpected title")
    if run_state_schema and run_state_schema.get("title") != "StatspAI Orchestrator Run State":
        errors.append(f"{rel(RUN_STATE_SCHEMA_PATH)} has unexpected title")

    for label, instance, schema, schema_path in [
        ("orchestrator policy", policy, policy_schema, POLICY_SCHEMA_PATH),
        ("orchestrator run state", run_state, run_state_schema, RUN_STATE_SCHEMA_PATH),
    ]:
        if instance and schema:
            try:
                validate(instance=instance, schema=schema)
            except ValidationError as exc:
                errors.append(f"{label} schema validation failed via {rel(schema_path)}: {exc.message}")

    adapter_map = {adapter["id"]: adapter for adapter in adapters.get("adapters", [])} if adapters else {}

    if policy:
        if policy.get("default_mode") != "dry-run":
            errors.append("orchestrator default_mode must be dry-run")
        for field in ["allow_network", "allow_human_auth", "allow_placeholder_commands", "allow_recursive_preflight"]:
            if policy.get(field) is not False:
                errors.append(f"{field} must be false")

        allow_execute = set(policy.get("allow_execute_adapters", []))
        blocked = set(policy.get("blocked_adapters", []))
        dry_run_only = set(policy.get("dry_run_only_adapters", []))
        overlap = allow_execute & blocked
        if overlap:
            errors.append(f"adapter cannot be both executable and blocked: {', '.join(sorted(overlap))}")
        overlap = allow_execute & dry_run_only
        if overlap:
            errors.append(f"adapter cannot be both executable and dry-run-only: {', '.join(sorted(overlap))}")

        if "workflow_preflight" not in dry_run_only:
            errors.append("workflow_preflight must be dry-run-only to avoid recursion")

        for adapter_id in allow_execute:
            adapter = adapter_map.get(adapter_id)
            if not adapter:
                errors.append(f"allow_execute_adapters references unknown adapter: {adapter_id}")
                continue
            if adapter["network_required"]:
                errors.append(f"{adapter_id} requires network and cannot be executable")
            if adapter["human_auth_required"]:
                errors.append(f"{adapter_id} requires human auth and cannot be executable")
            if adapter["side_effect_level"] not in policy.get("allowed_side_effect_levels", []):
                errors.append(f"{adapter_id} side effect not allowed: {adapter['side_effect_level']}")
            for command in adapter["commands"]:
                if command not in policy.get("command_allowlist", []):
                    errors.append(f"{adapter_id} command not allowlisted: {command}")

        for adapter_id in blocked:
            if adapter_id not in adapter_map:
                errors.append(f"blocked_adapters references unknown adapter: {adapter_id}")

    if run_state:
        if run_state.get("mode") not in {"dry-run", "execute"}:
            errors.append("run state mode invalid")
        if not run_state.get("events"):
            errors.append("run state must contain events")
        required_event_fields = {
            "adapter_id",
            "decision",
            "status",
            "reason",
            "failure_code",
            "commands",
            "command_results",
            "inputs",
            "outputs",
            "verification",
        }
        for event in run_state.get("events", []):
            missing_fields = required_event_fields - set(event)
            if missing_fields:
                errors.append(f"run state event missing fields for {event.get('adapter_id', 'unknown')}: {', '.join(sorted(missing_fields))}")
                continue
            adapter_id = event.get("adapter_id")
            if adapter_id not in adapter_map:
                errors.append(f"run state references unknown adapter: {adapter_id}")
            if event.get("decision") not in {"planned", "executed", "blocked", "failed"}:
                errors.append(f"run state event decision invalid for {adapter_id}")
            if event.get("status") not in {"planned", "pass", "fail", "blocked"}:
                errors.append(f"run state event status invalid for {adapter_id}")
            for field in ["reason", "commands", "command_results", "inputs", "outputs", "verification"]:
                if not isinstance(event.get(field), list):
                    errors.append(f"run state event {field} must be a list for {adapter_id}")

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    status = "FAIL" if errors else "PASS"
    lines = [
        "# Orchestrator Validation",
        "",
        f"Status: {status}",
        "",
        f"- Policy: `{rel(POLICY_PATH)}`",
        f"- Policy schema: `{rel(POLICY_SCHEMA_PATH)}`",
        f"- Run state schema: `{rel(RUN_STATE_SCHEMA_PATH)}`",
        f"- Run state: `{rel(RUN_STATE_PATH)}`",
        f"- Script: `{rel(ORCHESTRATOR_SCRIPT)}`",
        f"- Executable adapters: {', '.join(policy.get('allow_execute_adapters', [])) if policy else 'unknown'}",
        "",
    ]

    if errors:
        lines.extend(["## Errors", "", *[f"- {error}" for error in errors], ""])
    else:
        lines.extend(
            [
                "## Checks",
                "",
                "- Default mode is dry-run.",
                "- Network, auth, placeholder commands, and recursive preflight are blocked.",
                "- Executable adapters are registered, allowlisted, local, and low side-effect.",
                "- Latest run state references known adapters.",
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
