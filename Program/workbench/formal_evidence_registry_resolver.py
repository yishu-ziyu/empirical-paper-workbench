from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from workbench.formal_pdf_export_preflight import infer_agent_for_evidence
from workbench.paper_package import relative_or_absolute
from workbench.paper_revision_round import diff_formal_state, snapshot_formal_state


DEFAULT_PREFLIGHT_REPORT = "Results/json/formal_pdf_export_preflight.json"
DEFAULT_REPORT_PATH = "Results/json/formal_evidence_registry_resolution.json"
DEFAULT_REVIEW_PATH = "Reviews/formal_evidence_registry_resolution.md"
DEFAULT_PROPOSAL_PATH = "Submissions/formal_package/reproducibility/evidence_registry_patch_proposal.json"

REPAIR_CANDIDATES: dict[str, list[dict[str, str]]] = {
    "approved_findings": [
        {
            "path": "state/product/finding_reviews.json",
            "resolution": "derivable_from_existing_artifact",
            "reason": "approved finding review records can be converted into an approved findings evidence file",
        },
        {
            "path": "state/product/manuscript_candidate_reviews.json",
            "resolution": "derivable_from_existing_artifact",
            "reason": "approved manuscript candidate reviews identify claims already accepted for draft use",
        },
    ],
    "citation_verification_log": [
        {
            "path": "Results/json/literature_package_report.json",
            "resolution": "derivable_from_existing_artifact",
            "reason": "literature package records verification channels and missing citation evidence",
        },
        {
            "path": "Data/literature/processed/verified_bibliography.csv",
            "resolution": "derivable_from_existing_artifact",
            "reason": "verified bibliography can seed a citation verification log",
        },
    ],
    "domain_notes": [
        {
            "path": "Results/json/literature_package_report.json",
            "resolution": "derivable_from_existing_artifact",
            "reason": "literature package contains research context and CNKI/manual queues",
        },
        {
            "path": "state/product/research_question.json",
            "resolution": "derivable_from_existing_artifact",
            "reason": "confirmed research question can seed domain context notes",
        },
    ],
    "figure_manifest": [
        {
            "path": "Submissions/cfps_robot_pdf_export_manifest.json",
            "resolution": "derivable_from_existing_artifact",
            "reason": "PDF export manifest lists rendered manuscript outputs and can seed figure/table references",
        },
        {
            "path": "Submissions/export_manifest.json",
            "resolution": "derivable_from_existing_artifact",
            "reason": "generic export manifest may contain figure and artifact outputs",
        },
    ],
    "limitations_register": [
        {
            "path": "Results/json/reviewer_scorecard_report.json",
            "resolution": "derivable_from_existing_artifact",
            "reason": "reviewer scorecard stores revision tasks and limits that can seed a limitations register",
        },
        {
            "path": "Results/json/method_gate_report.json",
            "resolution": "derivable_from_existing_artifact",
            "reason": "method gate records yellow/red items and identification limitations",
        },
    ],
    "regression_tables": [
        {
            "path": "Results/json/method_execution_result.json",
            "resolution": "derivable_from_existing_artifact",
            "reason": "method execution result stores coefficients, standard errors and model summaries",
        }
    ],
    "robustness_matrix": [
        {
            "path": "Results/json/method_diagnostics_report.json",
            "resolution": "derivable_from_existing_artifact",
            "reason": "method diagnostics report stores robustness and diagnostic checks",
        },
        {
            "path": "Results/json/method_gate_report.json",
            "resolution": "derivable_from_existing_artifact",
            "reason": "method gate lists robustness requirements and unresolved method checks",
        },
    ],
    "sample_profile": [
        {
            "path": "Results/json/method_execution_result.json",
            "resolution": "derivable_from_existing_artifact",
            "reason": "method execution result includes data_preflight rows, sample and formula fields",
        },
        {
            "path": "Results/json/project_snapshot.json",
            "resolution": "derivable_from_existing_artifact",
            "reason": "project snapshot records dataset shape and project data profile",
        },
        {
            "path": "Results/json/cfps_robot_project_snapshot.json",
            "resolution": "derivable_from_existing_artifact",
            "reason": "CFPS robot snapshot records real project data profile",
        },
    ],
    "variable_role_set": [
        {
            "path": "state/product/variable_roles.json",
            "resolution": "direct_alias_available",
            "reason": "current product state stores the approved variable role set under the existing variable_roles file",
        },
        {
            "path": "state/proposals/variable_role_reconciliation.json",
            "resolution": "derivable_from_existing_artifact",
            "reason": "reconciliation proposal records the newer CFPS robot variable role recommendation",
        },
    ],
    "verified_context_sources": [
        {
            "path": "Results/json/literature_package_report.json",
            "resolution": "derivable_from_existing_artifact",
            "reason": "literature package records official-source seeds and manual verification channels",
        },
        {
            "path": "Data/literature/processed/candidate_literature.csv",
            "resolution": "derivable_from_existing_artifact",
            "reason": "candidate literature can seed verified context source review",
        },
    ],
}


def build_formal_evidence_registry_resolution(
    project_root: Path,
    preflight_report_path: Path,
    *,
    output_report_path: Path,
    formal_state_before: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    before = formal_state_before or snapshot_formal_state(project_root)
    if not preflight_report_path.exists():
        return build_blocked_report(
            project_root,
            preflight_report_path,
            output_report_path,
            before,
            ["preflight_report_missing"],
        )

    preflight = json.loads(preflight_report_path.read_text(encoding="utf-8"))
    missing_checks = [
        check
        for check in preflight.get("evidence_checks") or []
        if check.get("status") == "failed" or "required_evidence_missing" in (check.get("issues") or [])
    ]

    resolutions = [resolve_evidence_id(project_root, check) for check in missing_checks]
    patch_items = [build_patch_item(item, output_report_path, project_root) for item in resolutions if item["selected_paths"]]
    status = "no_missing_evidence" if not missing_checks else "evidence_registry_patch_proposed"
    if missing_checks and not patch_items:
        status = "no_existing_artifacts_found"

    after = snapshot_formal_state(project_root)
    return {
        "schema_version": "p5.formal_evidence_registry_resolution.v1",
        "generated_at": utc_now(),
        "source_preflight_report": relative_or_absolute(preflight_report_path, project_root),
        "resolution_report": relative_or_absolute(output_report_path, project_root),
        "status": status,
        "blocking_reasons": [],
        "preflight_status": preflight.get("status"),
        "missing_evidence_count": len(missing_checks),
        "evidence_resolutions": resolutions,
        "patch_summary": summarize_patch_items(patch_items),
        "this_command_mutated_preflight": False,
        "this_command_wrote_formal_state": False,
        "formal_state_guard": diff_formal_state(before, after),
        "agent_team_schedule": build_agent_team_schedule(resolutions),
        "next_action": build_next_action(resolutions),
        "write_boundary": (
            "本节点只生成 evidence registry patch proposal；不改 PDF 预检报告、不改章节源、"
            "不改 state/product 正式研究状态，也不写 canonical 规则库。"
        ),
    }


def build_blocked_report(
    project_root: Path,
    preflight_report_path: Path,
    output_report_path: Path,
    before: dict[str, dict[str, Any]],
    blocking_reasons: list[str],
) -> dict[str, Any]:
    after = snapshot_formal_state(project_root)
    return {
        "schema_version": "p5.formal_evidence_registry_resolution.v1",
        "generated_at": utc_now(),
        "source_preflight_report": relative_or_absolute(preflight_report_path, project_root),
        "resolution_report": relative_or_absolute(output_report_path, project_root),
        "status": "blocked_by_preflight_report",
        "blocking_reasons": blocking_reasons,
        "preflight_status": None,
        "missing_evidence_count": 0,
        "evidence_resolutions": [],
        "patch_summary": {"total": 0, "by_resolution": {}, "requires_human_confirmation": 0},
        "this_command_mutated_preflight": False,
        "this_command_wrote_formal_state": False,
        "formal_state_guard": diff_formal_state(before, after),
        "agent_team_schedule": build_agent_team_schedule([]),
        "next_action": {
            "id": "rerun_formal_pdf_export_preflight",
            "label": "重新运行 PDF 预检",
            "description": "先生成 formal_pdf_export_preflight.json，再解析 evidence registry 缺口。",
        },
        "write_boundary": (
            "本节点只生成 evidence registry patch proposal；不改 PDF 预检报告、不改章节源、"
            "不改 state/product 正式研究状态，也不写 canonical 规则库。"
        ),
    }


def resolve_evidence_id(project_root: Path, check: dict[str, Any]) -> dict[str, Any]:
    evidence_id = str(check.get("id") or "")
    configured = [
        {
            "path": path,
            "resolution": "direct_alias_available",
            "reason": "preflight candidate path already exists",
        }
        for path in check.get("candidate_paths") or []
    ]
    candidates = configured + REPAIR_CANDIDATES.get(evidence_id, [])
    selected: list[dict[str, str]] = []
    for candidate in candidates:
        path = candidate["path"]
        if (project_root / path).exists():
            selected.append(candidate)

    if selected:
        resolution = selected[0]["resolution"]
        selected_paths = [candidate["path"] for candidate in selected]
    else:
        resolution = "missing_after_scan"
        selected_paths = []

    return {
        "id": evidence_id,
        "resolution": resolution,
        "selected_paths": selected_paths,
        "candidate_paths_checked": [candidate["path"] for candidate in candidates],
        "required_by_sections": check.get("required_by_sections") or [],
        "agent": infer_agent_for_evidence(evidence_id),
        "requires_human_confirmation": True,
        "action": build_resolution_action(evidence_id, resolution),
        "reason": selected[0]["reason"] if selected else "no known local artifact matched this evidence id",
    }


def build_patch_item(item: dict[str, Any], output_report_path: Path, project_root: Path) -> dict[str, Any]:
    return {
        "id": item["id"],
        "resolution": item["resolution"],
        "suggested_registry_paths": item["selected_paths"],
        "source_resolution_report": relative_or_absolute(output_report_path, project_root),
        "agent": item["agent"],
        "requires_human_confirmation": True,
        "action": item["action"],
        "reason": item["reason"],
    }


def build_resolution_action(evidence_id: str, resolution: str) -> str:
    if resolution == "direct_alias_available":
        return f"把 `{evidence_id}` 的 existing path 作为可审查 alias 加入 evidence registry patch proposal。"
    if resolution == "derivable_from_existing_artifact":
        return f"由现有结构化产物派生 `{evidence_id}`，生成目标 evidence file 后再重跑 PDF 预检。"
    return f"未找到 `{evidence_id}` 的可复用产物；保留给对应 Agent 新建证据。"


def summarize_patch_items(patch_items: list[dict[str, Any]]) -> dict[str, Any]:
    by_resolution = Counter(item["resolution"] for item in patch_items)
    return {
        "total": len(patch_items),
        "by_resolution": dict(sorted(by_resolution.items())),
        "requires_human_confirmation": sum(1 for item in patch_items if item.get("requires_human_confirmation")),
    }


def build_patch_proposal(report: dict[str, Any]) -> dict[str, Any]:
    patch_items = [
        {
            "id": item["id"],
            "resolution": item["resolution"],
            "suggested_registry_paths": item["selected_paths"],
            "agent": item["agent"],
            "requires_human_confirmation": item["requires_human_confirmation"],
            "action": item["action"],
            "reason": item["reason"],
        }
        for item in report.get("evidence_resolutions") or []
        if item.get("selected_paths")
    ]
    return {
        "schema_version": "p5.evidence_registry_patch_proposal.v1",
        "generated_at": utc_now(),
        "source_resolution_report": report.get("resolution_report"),
        "source_preflight_report": report.get("source_preflight_report"),
        "can_apply_without_human_review": False,
        "patch_items": patch_items,
        "missing_after_scan": [
            item
            for item in report.get("evidence_resolutions") or []
            if item.get("resolution") == "missing_after_scan"
        ],
        "write_boundary": "这是审查提案，不自动修改 canonical registry 或正式层状态。",
    }


def write_formal_evidence_registry_resolution_outputs(
    report_path: Path,
    review_path: Path,
    proposal_path: Path,
    report: dict[str, Any],
) -> tuple[Path, Path, Path]:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    review_path.parent.mkdir(parents=True, exist_ok=True)
    review_path.write_text(build_review_markdown(report), encoding="utf-8")

    proposal_path.parent.mkdir(parents=True, exist_ok=True)
    proposal_path.write_text(json.dumps(build_patch_proposal(report), ensure_ascii=False, indent=2), encoding="utf-8")
    return report_path, review_path, proposal_path


def build_review_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# P5-E1 证据注册表解析",
        "",
        f"- Status: `{report.get('status')}`",
        f"- Source preflight: `{report.get('source_preflight_report')}`",
        f"- Missing evidence count: `{report.get('missing_evidence_count')}`",
        "- 正式层写回：未发生",
        "- PDF 预检报告写回：未发生",
        "",
        "## 解析结果",
        "",
    ]
    resolutions = report.get("evidence_resolutions") or []
    if resolutions:
        for item in resolutions:
            paths = ", ".join(f"`{path}`" for path in item.get("selected_paths") or []) or "无"
            lines.append(f"- `{item.get('id')}`: `{item.get('resolution')}` / {paths}")
    else:
        lines.append("- 无缺失证据需要解析。")

    lines.extend(["", "## Patch proposal 摘要", ""])
    patch_summary = report.get("patch_summary") or {}
    lines.append(f"- Total: `{patch_summary.get('total', 0)}`")
    for resolution, count in (patch_summary.get("by_resolution") or {}).items():
        lines.append(f"- `{resolution}`: `{count}`")

    lines.extend(
        [
            "",
            "## 下一步",
            "",
            f"- `{report.get('next_action', {}).get('id')}`：{report.get('next_action', {}).get('description')}",
        ]
    )
    return "\n".join(lines) + "\n"


def build_agent_team_schedule(resolutions: list[dict[str, Any]]) -> dict[str, Any]:
    agents = {"VerifierAgent"}
    agents.update(str(item.get("agent")) for item in resolutions if item.get("agent"))
    return {
        "call_when": "after_formal_pdf_preflight_blocks_on_evidence",
        "called_agents": sorted(agents),
        "recall_when": "after_evidence_registry_resolution_written",
        "next_call_when": "before_deriving_missing_evidence_files_or_applying_registry_patch",
        "integration_owner": "MainAgent",
        "boundary": "Agent Team 只提出证据绑定/派生建议；canonical registry 和正式层写回必须人工确认。",
    }


def build_next_action(resolutions: list[dict[str, Any]]) -> dict[str, str]:
    if not resolutions:
        return {
            "id": "return_to_pdf_preflight",
            "label": "回到 PDF 预检",
            "description": "没有缺失证据需要解析；继续处理章节源或进入 PDF 候选渲染。",
        }
    if any(item.get("selected_paths") for item in resolutions):
        return {
            "id": "review_evidence_registry_patch_proposal",
            "label": "审阅证据注册表修复提案",
            "description": "先确认可绑定或可派生的本地产物，再生成目标 evidence files 并重跑 PDF 预检。",
        }
    return {
        "id": "dispatch_agents_for_missing_evidence",
        "label": "派发缺失证据任务",
        "description": "当前仓库没有可复用产物；按 evidence id 派发 Data/Method/Literature/Execution/Reviewer Agent 新建证据。",
    }


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
