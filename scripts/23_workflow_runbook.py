#!/usr/bin/env python3
"""Generate a local runbook from workflow registry and agent specs."""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "workflows" / "registry.json"
AGENT_DIR = ROOT / "workflows" / "agents"
ARTIFACT_REGISTRY_PATH = ROOT / "Tasks" / "artifact-registry.md"
REPORT_PATH = ROOT / "artifacts" / "workflow_runbook_report.md"
STATE_PATH = ROOT / "artifacts" / "workflow_runbook_state.json"
API_CONTRACT_PATH = ROOT / "workflows" / "api_contract.md"

OPEN_STATUSES = {"missing", "partial", "external"}


def clean_cell(cell: str) -> str:
    return cell.strip().replace("`", "").replace("\\*", "*")


def path_exists(path_hint: str) -> bool:
    if "*" in path_hint:
        return bool(list(ROOT.glob(path_hint)))
    return (ROOT / path_hint).exists()


def parse_artifact_registry() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    if not ARTIFACT_REGISTRY_PATH.exists():
        return rows

    for line in ARTIFACT_REGISTRY_PATH.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [clean_cell(cell) for cell in line.strip().strip("|").split("|")]
        if len(cells) != 5:
            continue
        if cells[0] in {"步骤", "---"} or set(cells[0]) == {"-"}:
            continue
        status = cells[3].lower()
        if status not in {"present", "partial", "missing", "external"}:
            continue
        rows.append(
            {
                "step": cells[0],
                "artifact": cells[1],
                "path": cells[2],
                "status": status,
                "note": cells[4],
            }
        )
    return rows


def agent_path(workflow_id: str) -> Path:
    return AGENT_DIR / f"{workflow_id}.agent.md"


def extract_failure_codes(workflow_id: str) -> list[str]:
    path = agent_path(workflow_id)
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    match = re.search(r"## Failure Codes\n(?P<body>.*?)(?:\n## |\Z)", text, flags=re.S)
    if not match:
        return []
    return re.findall(r"`([A-Z][A-Z0-9_]+)`", match.group("body"))


def workflow_issues(workflow: dict, rows: list[dict[str, str]]) -> list[str]:
    issues: list[str] = []
    step_rows = [row for row in rows if row["step"] == workflow["step"]]
    by_artifact = {row["artifact"]: row for row in step_rows}

    for output in workflow["required_outputs"]:
        artifact = output["artifact"]
        path_hint = output["path_hint"]
        matched = by_artifact.get(artifact)
        if matched:
            if matched["status"] in OPEN_STATUSES:
                issues.append(f"{artifact}: {matched['status']} ({matched['path']})")
            continue
        if not path_exists(path_hint):
            issues.append(f"{artifact}: not found at {path_hint}")

    return issues


def gate_summary(workflow: dict) -> str:
    names = []
    for gate in workflow.get("gates", []):
        command = gate.get("command")
        if command:
            names.append(f"{gate['name']}=`{command}`")
        else:
            names.append(gate["name"])
    return "<br>".join(names)


def build_state(registry: dict, rows: list[dict[str, str]]) -> dict:
    counts = Counter(row["status"] for row in rows)
    workflows = [workflow for workflow in registry["workflows"] if re.match(r"^[0-9]{2}_", workflow["id"])]
    unresolved: list[tuple[dict, list[str]]] = []
    missing_specs: list[str] = []
    workflow_states: list[dict] = []

    for workflow in workflows:
        spec = agent_path(workflow["id"])
        if not spec.exists():
            missing_specs.append(workflow["id"])
        issues = workflow_issues(workflow, rows)
        if issues:
            unresolved.append((workflow, issues))
        workflow_states.append(
            {
                "id": workflow["id"],
                "step": workflow["step"],
                "name": workflow["name"],
                "purpose": workflow["purpose"],
                "agents": workflow["agents"],
                "inputs": workflow["inputs"],
                "required_outputs": workflow["required_outputs"],
                "gates": workflow["gates"],
                "human_checkpoints": workflow["human_checkpoints"],
                "stop_conditions": workflow["stop_conditions"],
                "rollback_to": workflow["rollback_to"],
                "skills": workflow["skills"],
                "failure_codes": extract_failure_codes(workflow["id"]),
                "current_issues": issues,
                "spec_path": str(spec.relative_to(ROOT)) if spec.exists() else None,
            }
        )

    next_workflow = unresolved[0][0] if unresolved else None
    return {
        "version": "0.4",
        "layer": "second",
        "status": "pass" if not unresolved and not missing_specs else "partial",
        "source_registry": str(REGISTRY_PATH.relative_to(ROOT)),
        "source_artifact_registry": str(ARTIFACT_REGISTRY_PATH.relative_to(ROOT)),
        "api_contract": str(API_CONTRACT_PATH.relative_to(ROOT)),
        "current_route": {
            "next_workflow_id": next_workflow["id"] if next_workflow else None,
            "next_workflow_name": next_workflow["name"] if next_workflow else None,
            "reason": unresolved[0][1] if unresolved else [],
        },
        "artifact_status": {
            "present": counts.get("present", 0),
            "partial": counts.get("partial", 0),
            "missing": counts.get("missing", 0),
            "external": counts.get("external", 0),
        },
        "spec_coverage": {
            "core_workflows": len(workflows),
            "missing_specs": missing_specs,
        },
        "workflows": workflow_states,
    }


def write_json_state(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    rows = parse_artifact_registry()
    state = build_state(registry, rows)
    write_json_state(state)

    lines = [
        "# Workflow Runbook Report",
        "",
        f"Registry: `{REGISTRY_PATH.relative_to(ROOT)}`",
        f"Agent specs: `{AGENT_DIR.relative_to(ROOT)}`",
        f"Artifact registry: `{ARTIFACT_REGISTRY_PATH.relative_to(ROOT)}`",
        f"JSON state: `{STATE_PATH.relative_to(ROOT)}`",
        "",
        "## Current Route",
        "",
    ]

    route = state["current_route"]
    if route["next_workflow_id"]:
        lines.append(f"NEXT `{route['next_workflow_id']}` / {route['next_workflow_name']}")
    else:
        lines.append("NEXT `none`")

    counts = state["artifact_status"]
    lines.extend(
        [
            "",
            "## Artifact Status",
            "",
            f"- present: {counts['present']}",
            f"- partial: {counts['partial']}",
            f"- missing: {counts['missing']}",
            f"- external: {counts['external']}",
            "",
            "## Workflow Table",
            "",
            "| Workflow | Agents | Gates | Failure codes | Current issues |",
            "|---|---|---|---|---|",
        ]
    )

    for workflow in state["workflows"]:
        codes = workflow["failure_codes"]
        issues = workflow["current_issues"]
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{workflow['id']}`",
                    "<br>".join(f"`{agent}`" for agent in workflow["agents"]),
                    gate_summary(workflow),
                    "<br>".join(f"`{code}`" for code in codes) or "missing",
                    "<br>".join(issues) if issues else "none",
                ]
            )
            + " |"
    )

    lines.extend(["", "## Spec Coverage", ""])
    missing_specs = state["spec_coverage"]["missing_specs"]
    if missing_specs:
        lines.extend(f"- missing spec: `{workflow_id}`" for workflow_id in missing_specs)
    else:
        lines.append("- all 10 core workflow specs present")

    lines.extend(["", "## Human Checkpoints", ""])
    for workflow in state["workflows"]:
        checkpoints = workflow.get("human_checkpoints", [])
        lines.append(f"### `{workflow['id']}`")
        lines.extend(f"- {checkpoint}" for checkpoint in checkpoints)
        lines.append("")

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")

    if route["next_workflow_id"]:
        print(f"NEXT {route['next_workflow_id']}: {route['next_workflow_name']}")
    else:
        print("NEXT none")
    print(
        f"workflows={len(state['workflows'])} "
        f"missing_specs={len(missing_specs)} "
        f"report={REPORT_PATH.relative_to(ROOT)} "
        f"json={STATE_PATH.relative_to(ROOT)}"
    )


if __name__ == "__main__":
    main()
