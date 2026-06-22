#!/usr/bin/env python3
"""Validate tool adapter registry and trace log for Runtime Gap P2."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ADAPTER_PATH = ROOT / "workflows" / "tool_adapters.json"
ADAPTER_SCHEMA_PATH = ROOT / "workflows" / "schemas" / "tool_adapters.schema.json"
TRACE_SCHEMA_PATH = ROOT / "workflows" / "schemas" / "agent_trace.schema.json"
TRACE_PATH = ROOT / "artifacts" / "agent_trace_log.jsonl"
REPORT_PATH = ROOT / "artifacts" / "tool_adapter_validation_report.md"

REQUIRED_ADAPTER_FIELDS = {
    "id",
    "category",
    "description",
    "workflows",
    "owner_agents",
    "commands",
    "inputs",
    "outputs",
    "network_required",
    "human_auth_required",
    "side_effect_level",
    "allowed_in_orchestrator",
    "risks",
    "verification",
    "trace_required",
}

REQUIRED_TRACE_FIELDS = {
    "run_id",
    "event_id",
    "timestamp",
    "mode",
    "actor",
    "workflow_id",
    "adapter_id",
    "decision",
    "action",
    "status",
    "reason",
    "failure_code",
    "commands",
    "command_results",
    "inputs",
    "outputs",
    "verification",
    "evidence",
}

REQUIRED_CATEGORIES = {
    "workflow_validation",
    "workflow_state",
    "literature",
    "literature_fetch",
    "data",
    "statistics",
    "document_build",
    "replication",
    "human_review",
}

REQUIRED_ADAPTERS = {
    "workflow_preflight",
    "workflow_runbook",
    "literature_metadata_verifier",
    "pdf_fetch_scansci",
    "cnki_browser_hqu",
    "data_gate_runner",
    "causal_analysis_runner",
    "latex_compile",
    "reproduction_verify",
    "browser_preview",
}

VALID_STATUSES = {"pass", "fail", "blocked", "recorded"}
VALID_TRACE_MODES = {"dry-run", "execute", "record"}
VALID_TRACE_DECISIONS = {"planned", "executed", "blocked", "failed", "recorded"}
NETWORK_ORCHESTRATOR_ALLOWLIST: set[str] = set()


def relative(path: Path) -> str:
    return str(path.relative_to(ROOT))


def read_json(path: Path, errors: list[str]) -> dict:
    if not path.exists():
        errors.append(f"missing file: {relative(path)}")
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{relative(path)} invalid JSON: {exc}")
        return {}


def validate_non_empty_string_list(value: object, label: str, errors: list[str]) -> None:
    if not isinstance(value, list) or not value or not all(isinstance(item, str) and item for item in value):
        errors.append(f"{label} must be a non-empty string list")


def validate_string_list(value: object, label: str, errors: list[str]) -> None:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        errors.append(f"{label} must be a string list")


def load_trace_events(errors: list[str]) -> list[dict]:
    if not TRACE_PATH.exists():
        errors.append(f"missing file: {relative(TRACE_PATH)}")
        return []

    events: list[dict] = []
    for line_number, line in enumerate(TRACE_PATH.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"{relative(TRACE_PATH)} line {line_number} invalid JSON: {exc}")
            continue
        events.append(event)
    return events


def main() -> None:
    errors: list[str] = []

    adapter_registry = read_json(ADAPTER_PATH, errors)
    adapter_schema = read_json(ADAPTER_SCHEMA_PATH, errors)
    trace_schema = read_json(TRACE_SCHEMA_PATH, errors)

    if adapter_schema and adapter_schema.get("title") != "StatspAI Tool Adapter Registry":
        errors.append(f"{relative(ADAPTER_SCHEMA_PATH)} has unexpected title")
    if trace_schema and trace_schema.get("title") != "StatspAI Agent Trace Event":
        errors.append(f"{relative(TRACE_SCHEMA_PATH)} has unexpected title")

    adapter_ids: set[str] = set()
    categories: set[str] = set()
    network_or_auth_blocked: list[str] = []

    if adapter_registry:
        if adapter_registry.get("layer") != "second":
            errors.append(f"{relative(ADAPTER_PATH)} layer must be second")

        adapters = adapter_registry.get("adapters")
        if not isinstance(adapters, list) or len(adapters) < 8:
            errors.append("tool adapter registry must contain at least 8 adapters")
            adapters = []

        for index, adapter in enumerate(adapters, start=1):
            prefix = f"adapter[{index}]"
            missing = REQUIRED_ADAPTER_FIELDS - set(adapter)
            if missing:
                errors.append(f"{prefix} missing fields: {', '.join(sorted(missing))}")
                continue

            adapter_id = adapter["id"]
            if adapter_id in adapter_ids:
                errors.append(f"duplicate adapter id: {adapter_id}")
            adapter_ids.add(adapter_id)
            categories.add(adapter["category"])

            for field in ["workflows", "owner_agents", "commands", "inputs", "outputs", "risks", "verification"]:
                validate_non_empty_string_list(adapter[field], f"{adapter_id}.{field}", errors)

            for field in ["network_required", "human_auth_required", "allowed_in_orchestrator", "trace_required"]:
                if not isinstance(adapter[field], bool):
                    errors.append(f"{adapter_id}.{field} must be boolean")

            if adapter["trace_required"] is not True:
                errors.append(f"{adapter_id}.trace_required must be true")

            if adapter["human_auth_required"] and adapter["allowed_in_orchestrator"]:
                errors.append(f"{adapter_id} requires human auth and cannot be orchestrator-allowed")
            if (
                adapter["network_required"]
                and adapter["allowed_in_orchestrator"]
                and adapter_id not in NETWORK_ORCHESTRATOR_ALLOWLIST
            ):
                errors.append(f"{adapter_id} requires network access and is not in the orchestrator allowlist")

            if adapter["network_required"] or adapter["human_auth_required"]:
                network_or_auth_blocked.append(adapter_id)

        missing_adapters = REQUIRED_ADAPTERS - adapter_ids
        if missing_adapters:
            errors.append(f"missing required adapters: {', '.join(sorted(missing_adapters))}")

        missing_categories = REQUIRED_CATEGORIES - categories
        if missing_categories:
            errors.append(f"missing required categories: {', '.join(sorted(missing_categories))}")

    events = load_trace_events(errors)
    traced_adapter_ids: set[str] = set()
    event_ids: set[str] = set()
    for index, event in enumerate(events, start=1):
        prefix = f"trace[{index}]"
        missing = REQUIRED_TRACE_FIELDS - set(event)
        if missing:
            errors.append(f"{prefix} missing fields: {', '.join(sorted(missing))}")
            continue

        event_id = event["event_id"]
        if event_id in event_ids:
            errors.append(f"duplicate trace event id: {event_id}")
        event_ids.add(event_id)

        adapter_id = event["adapter_id"]
        traced_adapter_ids.add(adapter_id)
        if adapter_ids and adapter_id not in adapter_ids:
            errors.append(f"{prefix} references unknown adapter: {adapter_id}")
        if event["status"] not in VALID_STATUSES:
            errors.append(f"{prefix}.status invalid: {event['status']}")
        if event["mode"] not in VALID_TRACE_MODES:
            errors.append(f"{prefix}.mode invalid: {event['mode']}")
        if event["decision"] not in VALID_TRACE_DECISIONS:
            errors.append(f"{prefix}.decision invalid: {event['decision']}")
        if event["failure_code"] is not None and not isinstance(event["failure_code"], str):
            errors.append(f"{prefix}.failure_code must be string or null")

        for field in ["inputs", "outputs", "verification", "evidence"]:
            validate_non_empty_string_list(event[field], f"{prefix}.{field}", errors)
        for field in ["reason", "commands"]:
            validate_string_list(event[field], f"{prefix}.{field}", errors)
        if not isinstance(event["command_results"], list):
            errors.append(f"{prefix}.command_results must be a list")
        else:
            for result_index, result in enumerate(event["command_results"], start=1):
                result_prefix = f"{prefix}.command_results[{result_index}]"
                required_result_fields = {
                    "command",
                    "argv",
                    "returncode",
                    "started_at",
                    "ended_at",
                    "stdout_summary",
                    "stderr_summary",
                }
                if not isinstance(result, dict):
                    errors.append(f"{result_prefix} must be an object")
                    continue
                missing_result = required_result_fields - set(result)
                if missing_result:
                    errors.append(f"{result_prefix} missing fields: {', '.join(sorted(missing_result))}")
                    continue
                if not isinstance(result["argv"], list) or not all(isinstance(item, str) for item in result["argv"]):
                    errors.append(f"{result_prefix}.argv must be a string list")
                if not isinstance(result["returncode"], int):
                    errors.append(f"{result_prefix}.returncode must be integer")

    for adapter_id in ["workflow_runbook", "workflow_preflight", "reproduction_verify"]:
        if adapter_id not in traced_adapter_ids:
            errors.append(f"trace log must include adapter {adapter_id}")

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    status = "FAIL" if errors else "PASS"
    lines = [
        "# Tool Adapter Validation",
        "",
        f"Status: {status}",
        "",
        f"- Adapter registry: `{relative(ADAPTER_PATH)}`",
        f"- Adapter schema: `{relative(ADAPTER_SCHEMA_PATH)}`",
        f"- Trace schema: `{relative(TRACE_SCHEMA_PATH)}`",
        f"- Trace log: `{relative(TRACE_PATH)}`",
        f"- Adapters: {len(adapter_ids)}",
        f"- Categories: {len(categories)}",
        f"- Trace events: {len(events)}",
        f"- Network/auth-gated adapters: {', '.join(network_or_auth_blocked) if network_or_auth_blocked else 'none'}",
        "",
    ]

    if errors:
        lines.extend(["## Errors", "", *[f"- {error}" for error in errors], ""])
    else:
        lines.extend(
            [
                "## Checks",
                "",
                "- Required adapter categories are covered.",
                "- Credential-gated or network-gated adapters are not allowed for automatic orchestrator execution unless allowlisted.",
                "- Trace events reference known adapters.",
                "- Runbook, preflight, and reproduction checks are represented in trace.",
                "",
            ]
        )

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    if errors:
        raise SystemExit(1)
    print(f"PASS adapters={len(adapter_ids)} trace_events={len(events)} report={relative(REPORT_PATH)}")


if __name__ == "__main__":
    main()
