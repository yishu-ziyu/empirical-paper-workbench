from __future__ import annotations

import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from workbench.paper_package import relative_or_absolute
from workbench.paper_revision_round import (
    diff_formal_state,
    snapshot_formal_state,
    slugify,
)


ALLOWED_PACKET_STATUSES = ["evidence_packet_ready", "needs_manual_review"]
DEFAULT_GATE_RECOMPUTE_INPUTS = [
    "Results/json/paper_quality_report.json",
    "Results/json/method_gate_report.json",
    "Results/json/reviewer_scorecard_report.json",
    "Submissions/cfps_robot_pdf_export_manifest.json",
]
NAMED_ARTIFACTS = {
    "DesignSpec": ["state/product/design_spec.json"],
    "RunPlan": ["state/product/run_plan.json"],
    "paper_quality_report": ["Results/json/paper_quality_report.json"],
    "paper_draft": [
        "Manuscripts/generated/paper_package_draft.md",
        "Manuscripts/generated/paper_draft.md",
    ],
    "verified_bibliography.csv": [
        "Data/literature/processed/verified_bibliography.csv",
    ],
    "contribution_matrix.md": [
        "Data/literature/processed/contribution_matrix.md",
    ],
}
TASK_ARTIFACTS = {
    "build_literature_package": ["Results/json/literature_package_report.json"],
    "run_method_gate": ["Results/json/method_gate_report.json"],
    "run_reviewer_revision_loop": [
        "Results/json/reviewer_scorecard_report.json",
        "Results/json/paper_quality_report.json",
    ],
    "add_weak_iv_robust_interval_or_caveat": [
        "Results/json/method_diagnostics_report.json",
        "Results/json/method_gate_report.json",
        "Results/json/reviewer_scorecard_report.json",
    ],
    "recover_bartik_share_shock_components": [
        "Results/json/method_execution_result.json",
        "Results/json/method_diagnostics_report.json",
    ],
    "add_rotemberg_weights_review": [
        "Results/json/method_diagnostics_report.json",
        "Results/json/method_gate_report.json",
    ],
    "add_leave_one_out_or_alternative_shock_check": [
        "Results/json/method_diagnostics_report.json",
        "Results/json/method_gate_report.json",
    ],
    "write_exclusion_and_shock_exogeneity_review": [
        "Results/json/method_diagnostics_report.json",
        "Results/json/method_gate_report.json",
    ],
    "explain_missing_drop_and_analysis_sample": [
        "Results/json/method_execution_result.json",
        "Results/json/method_diagnostics_report.json",
    ],
    "expand_working_paper_sections": [
        "Manuscripts/generated/paper_package_draft.md",
        "Results/json/paper_quality_report.json",
    ],
    "fix_submission_metadata": [
        "Manuscripts/generated/paper_package_draft.md",
        "Results/json/paper_quality_report.json",
    ],
}


def build_revision_evidence_packets(
    project_root: Path,
    revision_round: dict[str, Any],
    revision_round_path: Path,
    *,
    formal_state_before: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    before = formal_state_before or snapshot_formal_state(project_root)
    tasks = flatten_revision_tasks(revision_round)
    task_results = [build_task_result(project_root, task) for task in tasks]
    after = snapshot_formal_state(project_root)
    status_counts = Counter(record["status"] for record in task_results)

    return {
        "schema_version": "p4.paper_revision_evidence_packets.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_revision_round": relative_or_absolute(revision_round_path, project_root),
        "source_round_id": revision_round.get("round_id"),
        "status": "ready_for_gate_recompute",
        "draft_layer_only": True,
        "formal_writeback_allowed": False,
        "write_boundary": (
            "P4-H 只写草案层 evidence packet、manifest 和 review doc；"
            "正式层 state/product、正式论文和 canonical 方法库必须人工确认后写回。"
        ),
        "allowed_statuses": ALLOWED_PACKET_STATUSES,
        "status_counts": {status: status_counts.get(status, 0) for status in ALLOWED_PACKET_STATUSES},
        "task_results": task_results,
        "agent_team_schedule": build_agent_team_schedule(task_results),
        "formal_state_guard": diff_formal_state(before, after),
        "next_action": {
            "id": "recompute_quality_gates",
            "label": "重跑质量门、方法门和审稿门",
            "description": "使用 P4-H evidence packet manifest 判断每条 P4-G 修订任务是 cleared、still_blocking 还是 manual_review_required。",
        },
    }


def flatten_revision_tasks(revision_round: dict[str, Any]) -> list[dict[str, Any]]:
    tasks: list[dict[str, Any]] = []
    for packet in revision_round.get("agent_packets", []):
        packet_agent = packet.get("agent")
        for task in packet.get("tasks", []):
            normalized = dict(task)
            normalized.setdefault("agent", packet_agent)
            tasks.append(normalized)
    return sorted(tasks, key=lambda item: (int(item.get("order") or 0), str(item.get("id") or "")))


def build_task_result(project_root: Path, task: dict[str, Any]) -> dict[str, Any]:
    evidence_items, missing_evidence = collect_task_evidence(project_root, task)
    status = "evidence_packet_ready" if evidence_items and not missing_evidence else "needs_manual_review"
    task_id = str(task.get("id") or "revision_task")
    agent = str(task.get("agent") or "ManuscriptAgent")
    evidence_packet_path = task.get("draft_output_path") or build_draft_output_path(agent, task_id)
    gate_inputs = build_gate_recompute_inputs(task, evidence_items)

    return {
        "task_id": task_id,
        "agent": agent,
        "status": status,
        "artifact_type": "draft_evidence_packet",
        "source": task.get("source"),
        "source_artifact": task.get("source_artifact"),
        "action_item": task.get("action_item"),
        "reason": task.get("reason"),
        "review_context": build_review_context(task),
        "evidence_packet_path": evidence_packet_path,
        "evidence_items": evidence_items,
        "missing_evidence": missing_evidence,
        "verification_evidence_required": task.get("verification_evidence_required", []),
        "gate_recompute_inputs": gate_inputs,
        "requires_human_confirmation": True,
        "can_write_product_state": False,
    }


def collect_task_evidence(project_root: Path, task: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    candidates = evidence_candidates(task)
    evidence_items = []
    missing_evidence = []
    seen: set[str] = set()
    for candidate in candidates:
        if not candidate:
            continue
        display_path, resolved_path = resolve_candidate_path(project_root, candidate)
        if display_path in seen:
            continue
        seen.add(display_path)
        if resolved_path.exists() and resolved_path.is_file():
            evidence_items.append(build_evidence_item(project_root, display_path, resolved_path))
        else:
            missing_evidence.append(
                {
                    "path": display_path,
                    "exists": False,
                    "review_reason": "required local artifact was not found",
                    "evidence_level": "missing_local_artifact",
                }
            )
    return evidence_items, missing_evidence


def evidence_candidates(task: dict[str, Any]) -> list[str]:
    task_id = str(task.get("id") or "")
    candidates: list[str] = list(TASK_ARTIFACTS.get(task_id, []))
    source_artifact = task.get("source_artifact")
    if isinstance(source_artifact, str) and is_artifact_reference(source_artifact):
        candidates.append(source_artifact)
    for value in task.get("inputs", []):
        if not isinstance(value, str):
            continue
        if value in NAMED_ARTIFACTS:
            candidates.extend(NAMED_ARTIFACTS[value])
        elif is_artifact_reference(value):
            candidates.append(value)
    return candidates


def is_artifact_reference(value: str) -> bool:
    if value in NAMED_ARTIFACTS:
        return True
    path = Path(value)
    if path.suffix:
        return True
    return value.startswith(("Results/", "Submissions/", "Manuscripts/", "workspace/", "state/"))


def resolve_candidate_path(project_root: Path, value: str) -> tuple[str, Path]:
    path = Path(value)
    resolved = path if path.is_absolute() else project_root / path
    if not resolved.exists() and not path.is_absolute() and len(path.parts) == 1:
        discovered = discover_named_artifact(project_root, value)
        if discovered is not None:
            resolved = discovered
    try:
        display = relative_or_absolute(resolved, project_root)
    except ValueError:
        display = str(path)
    return display, resolved


def discover_named_artifact(project_root: Path, filename: str) -> Path | None:
    for root in [
        project_root / "Data" / "literature" / "processed",
        project_root / "workspace" / "runs",
        project_root / "Results",
        project_root / "Manuscripts",
        project_root / "Submissions",
    ]:
        if not root.exists():
            continue
        matches = sorted(root.rglob(filename))
        if matches:
            return matches[0]
    return None


def build_evidence_item(project_root: Path, display_path: str, resolved_path: Path) -> dict[str, Any]:
    content = resolved_path.read_bytes()
    item = {
        "path": display_path,
        "exists": True,
        "bytes": len(content),
        "sha256": hashlib.sha256(content).hexdigest(),
        "evidence_level": "structured_local_artifact" if resolved_path.suffix == ".json" else "local_artifact",
    }
    if resolved_path.suffix == ".json":
        json_metadata = inspect_json_artifact(resolved_path)
        item.update(json_metadata)
    return item


def inspect_json_artifact(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {"parse_status": "json_parse_failed"}
    if isinstance(data, dict):
        return {
            "parse_status": "parsed",
            "schema_version": data.get("schema_version"),
            "json_pointer": "/",
            "field_refs": sorted(str(key) for key in data.keys())[:20],
        }
    return {
        "parse_status": "parsed",
        "schema_version": None,
        "json_pointer": "/",
        "field_refs": [],
    }


def build_gate_recompute_inputs(task: dict[str, Any], evidence_items: list[dict[str, Any]]) -> list[str]:
    inputs = {str(item.get("path")) for item in evidence_items if item.get("path")}
    inputs.update(DEFAULT_GATE_RECOMPUTE_INPUTS)
    for required in task.get("verification_evidence_required", []):
        if isinstance(required, str) and required.endswith(".json"):
            inputs.add(required)
    return sorted(inputs)


def build_review_context(task: dict[str, Any]) -> dict[str, Any]:
    return {
        "reason": task.get("reason"),
        "action_item": task.get("action_item"),
        "verification_evidence_required": task.get("verification_evidence_required", []),
        "source": task.get("source"),
    }


def build_agent_team_schedule(task_results: list[dict[str, Any]]) -> dict[str, Any]:
    called_agents = sorted({str(record["agent"]) for record in task_results if record.get("agent")})
    called_agents.extend(agent for agent in ["ReviewerAgent", "VerifierAgent"] if agent not in called_agents)
    return {
        "call_when": "before_revision_evidence_execution",
        "called_agents": called_agents,
        "recall_when": "after_revision_evidence_packets_written",
        "next_call_when": "before_quality_gate_recompute_or_formal_writeback",
        "integration_owner": "MainAgent",
        "boundary": (
            "按 revision round 的 Agent packet 并行生成 evidence packet；"
            "每个 Agent 只写自己的草案层证据包；MainAgent 收回后合并 manifest，"
            "进入质量门重跑或正式层写回前再调用 ReviewerAgent / VerifierAgent 复核。"
        ),
    }


def build_draft_output_path(agent: str, task_id: str) -> str:
    return f"Reviews/agent_packets/{slugify(agent)}/{slugify(task_id)}.md"


def write_revision_evidence_outputs(
    project_root: Path,
    manifest_path: Path,
    review_path: Path,
    manifest: dict[str, Any],
) -> tuple[Path, Path]:
    write_packet_files(project_root, manifest)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    review_path.parent.mkdir(parents=True, exist_ok=True)
    review_path.write_text(build_review_markdown(manifest), encoding="utf-8")
    return manifest_path, review_path


def write_packet_files(project_root: Path, manifest: dict[str, Any]) -> None:
    for record in manifest.get("task_results", []):
        path = project_root / record["evidence_packet_path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(build_packet_markdown(record), encoding="utf-8")


def build_packet_markdown(record: dict[str, Any]) -> str:
    lines = [
        f"# Evidence Packet: {record['task_id']}",
        "",
        f"- Agent: `{record['agent']}`",
        f"- Status: `{record['status']}`",
        "- Formal writeback: `disabled`",
        "- Human review: `required`",
        "",
        "## Task",
        "",
        f"- Source: `{record.get('source')}`",
        f"- Source artifact: `{record.get('source_artifact')}`",
        f"- Action: {record.get('action_item')}",
        f"- Reason: {record.get('reason')}",
        "",
        "## Source Evidence",
        "",
    ]
    if record.get("evidence_items"):
        for item in record["evidence_items"]:
            lines.extend(
                [
                    f"- `{item['path']}`",
                    f"  - sha256: `{item['sha256']}`",
                    f"  - evidence_level: `{item['evidence_level']}`",
                    f"  - schema_version: `{item.get('schema_version')}`",
                ]
            )
    else:
        lines.append("- 暂无可绑定的本地结构化证据。")
    if record.get("missing_evidence"):
        lines.append("")
        lines.append("### Missing Evidence")
        for item in record["missing_evidence"]:
            lines.append(f"- `{item['path']}`: {item['review_reason']}")

    lines.extend(
        [
            "",
            "## Draft Output",
            "",
            f"- Draft packet path: `{record['evidence_packet_path']}`",
            "- This packet is a draft-layer evidence artifact for human review.",
            "",
            "## Verification Evidence",
            "",
        ]
    )
    for evidence in record.get("verification_evidence_required", []):
        lines.append(f"- {evidence}")
    lines.extend(["", "## Gate Recompute Inputs", ""])
    for gate_input in record.get("gate_recompute_inputs", []):
        lines.append(f"- `{gate_input}`")
    lines.extend(
        [
            "",
            "## Human Review",
            "",
            "- decision: `pending`",
            "- can_write_product_state: `false`",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def build_review_markdown(manifest: dict[str, Any]) -> str:
    lines = [
        "# P4-H 证据包汇总",
        "",
        f"- Source revision round: `{manifest.get('source_revision_round')}`",
        f"- Status: `{manifest.get('status')}`",
        "- 正式层写回：关闭",
        "",
        "## 状态计数",
        "",
    ]
    for status, count in manifest.get("status_counts", {}).items():
        lines.append(f"- {status}: {count}")
    lines.extend(["", "## Agent Team 调用节奏", ""])
    schedule = manifest.get("agent_team_schedule", {})
    for key in ["call_when", "called_agents", "recall_when", "next_call_when", "boundary"]:
        lines.append(f"- {key}: {schedule.get(key)}")
    lines.extend(["", "## Task Results", ""])
    for record in manifest.get("task_results", []):
        lines.extend(
            [
                f"### {record['task_id']}",
                "",
                f"- Agent: `{record['agent']}`",
                f"- Status: `{record['status']}`",
                f"- Evidence packet: `{record['evidence_packet_path']}`",
                f"- Evidence items: {len(record.get('evidence_items', []))}",
                f"- Missing evidence: {len(record.get('missing_evidence', []))}",
                "",
            ]
        )
    lines.extend(
        [
            "## 正式层保护",
            "",
            f"- changed: `{manifest.get('formal_state_guard', {}).get('changed')}`",
            "- protected paths:",
        ]
    )
    for path in manifest.get("formal_state_guard", {}).get("protected_paths", []):
        lines.append(f"  - `{path}`")
    return "\n".join(lines).rstrip() + "\n"
