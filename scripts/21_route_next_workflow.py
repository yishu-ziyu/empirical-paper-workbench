#!/usr/bin/env python3
"""Route the next workflow from the current artifact registry."""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "workflows" / "registry.json"
ARTIFACT_REGISTRY_PATH = ROOT / "Tasks" / "artifact-registry.md"
REPORT_PATH = ROOT / "artifacts" / "workflow_router_report.md"

OPEN_STATUSES = {"missing", "partial", "external"}


def clean_cell(cell: str) -> str:
    return cell.strip().replace("`", "").replace("\\*", "*")


def parse_artifact_registry() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
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


def path_exists(path_hint: str) -> bool:
    if "*" in path_hint:
        return bool(list(ROOT.glob(path_hint)))
    return (ROOT / path_hint).exists()


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


def current_policy_rollout_gap() -> list[str]:
    feasibility = ROOT / "artifacts" / "policy_rollout_feasibility.md"
    sources = ROOT / "data" / "policy" / "urbmi_ncms_rollout_sources.csv"
    clean = ROOT / "data" / "policy" / "policy_rollout_clean.csv"
    gaps: list[str] = []
    if feasibility.exists() and not sources.exists():
        gaps.append("urbmi_ncms_rollout_sources.csv: missing")
    if feasibility.exists() and not clean.exists():
        gaps.append("policy_rollout_clean.csv: missing")
    return gaps


def main() -> None:
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    workflows = registry["workflows"]
    rows = parse_artifact_registry()
    counts = Counter(row["status"] for row in rows)

    unresolved: list[tuple[str, str, list[str]]] = []
    for workflow in workflows:
        issues = workflow_issues(workflow, rows)
        if workflow["id"] == "05x_policy_rollout_data_layer":
            existing = "\n".join(issues)
            for gap in current_policy_rollout_gap():
                if gap.split(":")[0] not in existing:
                    issues.append(gap)
        if issues:
            unresolved.append((workflow["id"], workflow["name"], issues))

    recommended = unresolved[0] if unresolved else None

    report_lines = [
        "# Workflow Router Report",
        "",
        f"Registry: `{REGISTRY_PATH.relative_to(ROOT)}`",
        f"Artifact registry: `{ARTIFACT_REGISTRY_PATH.relative_to(ROOT)}`",
        "",
        "## Artifact Status",
        "",
        f"- present: {counts.get('present', 0)}",
        f"- partial: {counts.get('partial', 0)}",
        f"- missing: {counts.get('missing', 0)}",
        f"- external: {counts.get('external', 0)}",
        "",
        "## Recommendation",
        "",
    ]

    if recommended:
        workflow_id, name, issues = recommended
        report_lines.extend(
            [
                f"Next workflow: `{workflow_id}` / {name}",
                "",
                "Reason:",
                *[f"- {issue}" for issue in issues],
                "",
            ]
        )
    else:
        report_lines.extend(["No unresolved workflow outputs detected.", ""])

    report_lines.extend(["## Open Workflow Issues", ""])
    for workflow_id, name, issues in unresolved:
        safe_name = re.sub(r"\s+", " ", name)
        report_lines.append(f"### `{workflow_id}` / {safe_name}")
        report_lines.extend(f"- {issue}" for issue in issues)
        report_lines.append("")

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(report_lines), encoding="utf-8")

    if recommended:
        print(f"NEXT {recommended[0]}: {recommended[1]}")
        for issue in recommended[2]:
            print(f"- {issue}")
    else:
        print("NEXT none")
    print(f"report={REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
