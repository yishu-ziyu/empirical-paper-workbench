#!/usr/bin/env python3
"""Validate the machine-readable workflow runbook state."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "artifacts" / "workflow_runbook_state.json"
SCHEMA_PATH = ROOT / "workflows" / "schemas" / "runbook_state.schema.json"
API_CONTRACT_PATH = ROOT / "workflows" / "api_contract.md"
REPORT_PATH = ROOT / "artifacts" / "workflow_api_validation_report.md"


def relative(path: Path) -> str:
    return str(path.relative_to(ROOT))


def main() -> None:
    errors: list[str] = []

    for path in [STATE_PATH, SCHEMA_PATH, API_CONTRACT_PATH]:
        if not path.exists():
            errors.append(f"missing file: {relative(path)}")

    state = {}
    schema = {}
    if STATE_PATH.exists():
        try:
            state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{relative(STATE_PATH)} invalid JSON: {exc}")

    if SCHEMA_PATH.exists():
        try:
            schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{relative(SCHEMA_PATH)} invalid JSON: {exc}")

    required_state = {
        "version",
        "layer",
        "status",
        "source_registry",
        "source_artifact_registry",
        "api_contract",
        "current_route",
        "artifact_status",
        "spec_coverage",
        "workflows",
    }
    if state:
        missing = required_state - set(state)
        if missing:
            errors.append(f"{relative(STATE_PATH)} missing keys: {', '.join(sorted(missing))}")

        workflows = state.get("workflows")
        if not isinstance(workflows, list) or len(workflows) != 10:
            errors.append(f"{relative(STATE_PATH)} workflows must contain 10 core workflows")
        else:
            for workflow in workflows:
                workflow_id = workflow.get("id", "unknown")
                if not workflow.get("failure_codes"):
                    errors.append(f"{workflow_id} missing failure_codes")
                if not workflow.get("spec_path"):
                    errors.append(f"{workflow_id} missing spec_path")
                if not workflow.get("gates"):
                    errors.append(f"{workflow_id} missing gates")

        coverage = state.get("spec_coverage", {})
        if coverage.get("missing_specs"):
            errors.append(f"missing specs: {', '.join(coverage['missing_specs'])}")

    if schema and schema.get("title") != "StatspAI Workflow Runbook State":
        errors.append(f"{relative(SCHEMA_PATH)} has unexpected title")

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    if errors:
        lines = ["# Workflow API Validation", "", "Status: FAIL", "", *[f"- {error}" for error in errors], ""]
        REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
        raise SystemExit(1)

    lines = [
        "# Workflow API Validation",
        "",
        "Status: PASS",
        "",
        f"- State: `{relative(STATE_PATH)}`",
        f"- Schema: `{relative(SCHEMA_PATH)}`",
        f"- Contract: `{relative(API_CONTRACT_PATH)}`",
        f"- Workflows: {len(state['workflows'])}",
        f"- Current route: `{state['current_route']['next_workflow_id'] or 'none'}`",
        "",
    ]
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"PASS workflows={len(state['workflows'])} report={relative(REPORT_PATH)}")


if __name__ == "__main__":
    main()
