#!/usr/bin/env python3
"""Validate the second-layer workflow registry."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "workflows" / "registry.json"
REPORT_PATH = ROOT / "artifacts" / "workflow_contract_validation.md"

REQUIRED_WORKFLOW_FIELDS = {
    "id",
    "step",
    "name",
    "purpose",
    "agents",
    "inputs",
    "required_outputs",
    "gates",
    "human_checkpoints",
    "stop_conditions",
    "rollback_to",
    "skills",
}

REQUIRED_OUTPUT_FIELDS = {"artifact", "path_hint"}
REQUIRED_GATE_FIELDS = {"name", "type"}
VALID_GATE_TYPES = {"automated", "human"}


def fail(errors: list[str]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        "# Workflow Contract Validation\n\n"
        "Status: FAIL\n\n"
        + "\n".join(f"- {error}" for error in errors)
        + "\n",
        encoding="utf-8",
    )
    raise SystemExit(1)


def main() -> None:
    errors: list[str] = []

    if not REGISTRY_PATH.exists():
        fail([f"missing registry: {REGISTRY_PATH.relative_to(ROOT)}"])

    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    workflows = registry.get("workflows")
    if not isinstance(workflows, list) or not workflows:
        fail(["registry.workflows must be a non-empty list"])

    ids: set[str] = set()
    steps: set[str] = set()
    output_paths: dict[str, set[str]] = {}

    for index, workflow in enumerate(workflows, start=1):
        prefix = f"workflow[{index}]"
        missing = REQUIRED_WORKFLOW_FIELDS - set(workflow)
        if missing:
            errors.append(f"{prefix} missing fields: {', '.join(sorted(missing))}")
            continue

        workflow_id = workflow["id"]
        step = workflow["step"]
        if workflow_id in ids:
            errors.append(f"duplicate workflow id: {workflow_id}")
        ids.add(workflow_id)
        steps.add(step)

        for field in ("agents", "inputs", "required_outputs", "gates", "human_checkpoints", "stop_conditions", "skills"):
            if not isinstance(workflow[field], list) or not workflow[field]:
                errors.append(f"{workflow_id}.{field} must be a non-empty list")

        for output in workflow.get("required_outputs", []):
            missing_output = REQUIRED_OUTPUT_FIELDS - set(output)
            if missing_output:
                errors.append(f"{workflow_id}.required_outputs missing fields: {', '.join(sorted(missing_output))}")
                continue
            path_hint = output["path_hint"]
            output_paths.setdefault(path_hint, set()).add(workflow_id)

        for gate in workflow.get("gates", []):
            missing_gate = REQUIRED_GATE_FIELDS - set(gate)
            if missing_gate:
                errors.append(f"{workflow_id}.gates missing fields: {', '.join(sorted(missing_gate))}")
                continue
            if gate["type"] not in VALID_GATE_TYPES:
                errors.append(f"{workflow_id}.gate {gate['name']} has invalid type: {gate['type']}")
            if gate["type"] == "automated" and gate.get("command") is not None and not isinstance(gate["command"], str):
                errors.append(f"{workflow_id}.gate {gate['name']} command must be a string")

    expected_steps = {f"{i:02d}" for i in range(1, 11)}
    missing_steps = expected_steps - steps
    if missing_steps:
        errors.append(f"registry does not cover steps: {', '.join(sorted(missing_steps))}")

    if errors:
        fail(errors)

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    report = [
        "# Workflow Contract Validation",
        "",
        "Status: PASS",
        "",
        f"- Registry: `{REGISTRY_PATH.relative_to(ROOT)}`",
        f"- Workflows: {len(workflows)}",
        f"- Core steps covered: {', '.join(sorted(expected_steps))}",
        f"- Unique output path hints: {len(output_paths)}",
        "",
    ]
    REPORT_PATH.write_text("\n".join(report), encoding="utf-8")
    print(f"PASS workflows={len(workflows)} report={REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
