from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from workbench.paper_package import relative_or_absolute
from workbench.paper_revision_round import diff_formal_state, snapshot_formal_state


ALLOWED_GATE_RECOMPUTE_STATUSES = ["cleared", "still_blocking", "manual_review_required"]
DEFAULT_GATE_SOURCE_PATHS = {
    "paper_quality_report": "Results/json/paper_quality_report.json",
    "method_gate_report": "Results/json/method_gate_report.json",
    "reviewer_scorecard_report": "Results/json/reviewer_scorecard_report.json",
    "pdf_export_manifest": "Submissions/cfps_robot_pdf_export_manifest.json",
}


def build_revision_gate_recompute(
    project_root: Path,
    evidence_manifest: dict[str, Any],
    evidence_manifest_path: Path,
    *,
    formal_state_before: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    before = formal_state_before or snapshot_formal_state(project_root)
    gate_sources = load_gate_sources(project_root)
    task_results = [
        classify_task_against_gates(project_root, task, gate_sources)
        for task in evidence_manifest.get("task_results", [])
    ]
    status_counts = Counter(record["status"] for record in task_results)
    after = snapshot_formal_state(project_root)
    has_open_items = any(record["status"] != "cleared" for record in task_results)

    return {
        "schema_version": "p4.paper_revision_gate_recompute.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_evidence_manifest": relative_or_absolute(evidence_manifest_path, project_root),
        "status": "needs_revision_work" if has_open_items else "ready_for_formal_writeback_preflight",
        "draft_layer_only": True,
        "formal_writeback_allowed": False,
        "allowed_statuses": ALLOWED_GATE_RECOMPUTE_STATUSES,
        "status_counts": {
            status: status_counts.get(status, 0)
            for status in ALLOWED_GATE_RECOMPUTE_STATUSES
        },
        "task_results": task_results,
        "gate_sources": summarize_gate_sources(project_root, gate_sources),
        "agent_team_schedule": build_agent_team_schedule(task_results),
        "formal_state_guard": diff_formal_state(before, after),
        "next_action": build_next_action(task_results),
    }


def load_gate_sources(project_root: Path) -> dict[str, dict[str, Any]]:
    sources: dict[str, dict[str, Any]] = {}
    for name, relative_path in DEFAULT_GATE_SOURCE_PATHS.items():
        path = project_root / relative_path
        if not path.exists():
            sources[name] = {"path": relative_path, "exists": False, "data": None}
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            sources[name] = {
                "path": relative_path,
                "exists": True,
                "parse_status": "json_parse_failed",
                "error": str(exc),
                "data": None,
            }
            continue
        sources[name] = {
            "path": relative_path,
            "exists": True,
            "parse_status": "parsed",
            "schema_version": data.get("schema_version") if isinstance(data, dict) else None,
            "data": data,
        }
    return sources


def summarize_gate_sources(project_root: Path, gate_sources: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    summary = []
    for name, source in gate_sources.items():
        path = project_root / source["path"]
        summary.append(
            {
                "name": name,
                "path": relative_or_absolute(path, project_root),
                "exists": source.get("exists", False),
                "parse_status": source.get("parse_status") if source.get("exists") else None,
                "schema_version": source.get("schema_version"),
            }
        )
    return summary


def classify_task_against_gates(
    project_root: Path,
    task: dict[str, Any],
    gate_sources: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    task_id = str(task.get("task_id") or "")
    missing_evidence = task.get("missing_evidence") or []
    missing_gate_inputs = find_missing_gate_inputs(project_root, task)

    base = {
        "task_id": task_id,
        "agent": task.get("agent"),
        "previous_status": task.get("status"),
        "evidence_packet_path": task.get("evidence_packet_path"),
        "missing_evidence": missing_evidence,
        "gate_recompute_inputs": task.get("gate_recompute_inputs", []),
        "missing_gate_inputs": missing_gate_inputs,
        "blocking_sources": [],
        "gate_matches": [],
        "requires_human_confirmation": True,
        "can_write_product_state": False,
    }

    if task.get("status") == "needs_manual_review" or missing_evidence:
        return {
            **base,
            "status": "manual_review_required",
            "reason": "Evidence packet still requires human or external-source review.",
        }

    if missing_gate_inputs:
        return {
            **base,
            "status": "still_blocking",
            "blocking_sources": ["missing_gate_input"],
            "reason": "One or more gate recompute inputs are missing.",
        }

    matches = find_task_gate_matches(task_id, gate_sources)
    blocking_sources = sorted({match["source"] for match in matches})
    if matches:
        return {
            **base,
            "status": "still_blocking",
            "blocking_sources": blocking_sources,
            "gate_matches": matches,
            "reason": "Current gate artifacts still reference this revision task.",
        }

    return {
        **base,
        "status": "cleared",
        "reason": "Evidence is ready and current gate artifacts no longer carry this task as a blocker.",
    }


def find_missing_gate_inputs(project_root: Path, task: dict[str, Any]) -> list[str]:
    missing: list[str] = []
    for value in task.get("gate_recompute_inputs", []):
        if not isinstance(value, str) or not value:
            continue
        path = Path(value)
        resolved = path if path.is_absolute() else project_root / path
        if not resolved.exists():
            missing.append(value)
    return missing


def find_task_gate_matches(task_id: str, gate_sources: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    if not task_id:
        return []
    matches: list[dict[str, Any]] = []
    for source_name, source in gate_sources.items():
        data = source.get("data")
        if data is None:
            continue
        matches.extend(find_matches_in_value(task_id, data, source_name, "/"))
    return matches


def find_matches_in_value(task_id: str, value: Any, source_name: str, pointer: str) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    if isinstance(value, dict):
        if value.get("id") == task_id or value.get("task_id") == task_id:
            matches.append({"source": source_name, "json_pointer": pointer, "match_type": "task_id"})
        for key, nested in value.items():
            nested_pointer = f"{pointer.rstrip('/')}/{escape_json_pointer(str(key))}"
            matches.extend(find_matches_in_value(task_id, nested, source_name, nested_pointer))
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            nested_pointer = f"{pointer.rstrip('/')}/{index}"
            matches.extend(find_matches_in_value(task_id, nested, source_name, nested_pointer))
    elif isinstance(value, str) and task_id in value:
        matches.append({"source": source_name, "json_pointer": pointer, "match_type": "string_contains_task_id"})
    return matches


def escape_json_pointer(value: str) -> str:
    return value.replace("~", "~0").replace("/", "~1")


def build_agent_team_schedule(task_results: list[dict[str, Any]]) -> dict[str, Any]:
    task_agents = sorted({str(record.get("agent")) for record in task_results if record.get("agent")})
    called_agents = list(task_agents)
    for agent in ["ReviewerAgent", "VerifierAgent"]:
        if agent not in called_agents:
            called_agents.append(agent)
    return {
        "call_when": "before_revision_gate_recompute",
        "called_agents": called_agents,
        "recall_when": "after_revision_gate_recompute_written",
        "next_call_when": "before_formal_writeback_preflight",
        "integration_owner": "MainAgent",
        "boundary": (
            "P4-I1 只把 P4-H evidence packet 与当前质量门、方法门、审稿门、导出门产物对齐；"
            "各 Agent 的修复任务、外部文献补证和正式层写回放到后续节点。"
        ),
    }


def build_next_action(task_results: list[dict[str, Any]]) -> dict[str, Any]:
    manual = [record["task_id"] for record in task_results if record["status"] == "manual_review_required"]
    blocking = [record["task_id"] for record in task_results if record["status"] == "still_blocking"]
    if manual:
        return {
            "id": "collect_manual_evidence",
            "label": "补齐人工证据",
            "task_ids": manual,
            "description": "先补齐外部文献、人工识别叙事或缺失本地产物，再重新进入 gate recompute。",
        }
    if blocking:
        return {
            "id": "rerun_blocking_gates",
            "label": "重跑仍阻塞的 gate",
            "task_ids": blocking,
            "description": "针对仍被质量门、审稿门或导出门引用的任务重新执行对应检查。",
        }
    return {
        "id": "formal_writeback_preflight",
        "label": "进入正式层写回预检",
        "task_ids": [],
        "description": "全部证据包已通过复核，可以进入独立的正式层写回预检节点。",
    }


def write_revision_gate_recompute_outputs(
    report_path: Path,
    review_path: Path,
    report: dict[str, Any],
) -> tuple[Path, Path]:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    review_path.parent.mkdir(parents=True, exist_ok=True)
    review_path.write_text(build_review_markdown(report), encoding="utf-8")
    return report_path, review_path


def build_review_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# P4-I 质量门复核账本",
        "",
        f"- Source evidence manifest: `{report.get('source_evidence_manifest')}`",
        f"- Status: `{report.get('status')}`",
        "- 正式层写回：关闭",
        "",
        "## 状态计数",
        "",
    ]
    for status, count in report.get("status_counts", {}).items():
        lines.append(f"- {status}: {count}")

    lines.extend(["", "## Task Results", ""])
    for record in report.get("task_results", []):
        lines.extend(
            [
                f"### {record.get('task_id')}",
                "",
                f"- Agent: `{record.get('agent')}`",
                f"- Previous status: `{record.get('previous_status')}`",
                f"- Recompute status: `{record.get('status')}`",
                f"- Reason: {record.get('reason')}",
                f"- Blocking sources: {', '.join(record.get('blocking_sources', [])) or 'none'}",
                f"- Missing gate inputs: {', '.join(record.get('missing_gate_inputs', [])) or 'none'}",
                f"- Missing evidence: {len(record.get('missing_evidence', []))}",
                "",
            ]
        )

    lines.extend(["## Agent Team 调用节奏", ""])
    schedule = report.get("agent_team_schedule", {})
    for key in ["call_when", "called_agents", "recall_when", "next_call_when", "boundary"]:
        lines.append(f"- {key}: {schedule.get(key)}")

    lines.extend(
        [
            "",
            "## 正式层保护",
            "",
            f"- changed: `{report.get('formal_state_guard', {}).get('changed')}`",
            "- protected paths:",
        ]
    )
    for path in report.get("formal_state_guard", {}).get("protected_paths", []):
        lines.append(f"  - `{path}`")
    return "\n".join(lines).rstrip() + "\n"
