from __future__ import annotations

import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from workbench.paper_package import relative_or_absolute
from workbench.paper_revision_round import diff_formal_state, snapshot_formal_state


EVIDENCE_CANDIDATES = {
    "approved_findings": ["Results/json/approved_findings.json"],
    "method_gate_report": ["Results/json/method_gate_report.json"],
    "verified_bibliography.csv": [
        "Data/literature/processed/verified_bibliography.csv",
        "workspace/runs/*/02_literature/verified_bibliography.csv",
    ],
    "contribution_matrix.md": [
        "Data/literature/processed/contribution_matrix.md",
        "workspace/runs/*/02_literature/contribution_matrix.md",
    ],
    "closest_papers": [
        "Data/literature/processed/contribution_matrix.md",
        "Results/json/literature_package_report.json",
    ],
    "research_question": [
        "state/product/research_question.json",
        "Results/json/paper_supervisor_context.json",
        "Results/json/paper_expansion_plan.json",
    ],
    "domain_notes": ["Results/json/domain_notes.json"],
    "mechanism_hypotheses": ["Results/json/domain_notes.json", "Results/json/literature_package_report.json"],
    "literature_context": ["Results/json/literature_package_report.json"],
    "dataset_profile": ["Results/json/sample_profile.json", "Results/json/project_snapshot.json"],
    "variable_dictionary": [
        "Results/json/variable_role_reconciliation_report.json",
        "Submissions/formal_package/evidence/variable_role_set.json",
    ],
    "sample_construction_log": ["Results/json/sample_profile.json", "Results/json/method_execution_result.json"],
    "design_spec": ["state/product/design_spec.json"],
    "run_plan": ["state/product/run_plan.json"],
    "main_regression_table": ["Results/json/regression_tables.json", "Results/json/method_execution_result.json"],
    "coefficient_interpretation": ["Results/json/approved_findings.json", "Results/json/method_execution_result.json"],
    "robustness_matrix": ["Results/json/robustness_matrix.json"],
    "mechanism_or_heterogeneity_results": [
        "Results/json/robustness_matrix.json",
        "Results/json/method_execution_result.json",
    ],
    "limitations_register": ["Results/json/limitations_register.json"],
    "reviewer_scorecard_report": ["Results/json/reviewer_scorecard_report.json"],
}


def build_manuscript_section_evidence_bindings_report(
    project_root: Path,
    revision_round: dict[str, Any],
    revision_round_path: Path,
    scaffold_report: dict[str, Any],
    scaffold_report_path: Path,
    *,
    formal_state_before: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    before = formal_state_before or snapshot_formal_state(project_root)
    scaffold_paths = {
        item.get("section"): item.get("path")
        for item in scaffold_report.get("section_scaffolds", [])
        if item.get("section") and item.get("path")
    }
    sections = [
        build_section_binding(project_root, work_order, scaffold_paths.get(work_order.get("section")))
        for work_order in revision_round.get("manuscript_section_work_orders", [])
        if work_order.get("section")
    ]
    after = snapshot_formal_state(project_root)
    summary = build_summary(sections)
    status = "section_evidence_bindings_ready" if summary["missing"] == 0 else "section_evidence_bindings_with_gaps"
    return {
        "schema_version": "p6.manuscript_section_evidence_bindings.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "draft_layer_only": True,
        "formal_writeback_allowed": False,
        "source_revision_round": relative_or_absolute(revision_round_path, project_root),
        "source_scaffold_report": relative_or_absolute(scaffold_report_path, project_root),
        "summary": summary,
        "sections": sections,
        "agent_team_schedule": {
            "call_when": "after_evidence_binding_report_written",
            "called_agents": ["ManuscriptAgent", "VerifierAgent"],
            "recall_when": "after_section_evidence_gaps_reviewed",
            "next_call_when": "before_section_draft_expansion",
            "boundary": "证据索引已准备；下一步只允许基于 bound evidence 扩写草案，对 missing evidence 先补证或人工确认。",
        },
        "formal_state_guard": diff_formal_state(before, after),
    }


def build_section_binding(project_root: Path, work_order: dict[str, Any], scaffold_path: str | None) -> dict[str, Any]:
    bindings = [bind_evidence(project_root, evidence_id) for evidence_id in work_order.get("required_evidence", [])]
    missing = [item for item in bindings if item["status"] == "missing"]
    return {
        "section": work_order.get("section"),
        "status": "evidence_bound" if not missing else "evidence_gaps_remaining",
        "section_file": scaffold_path or work_order.get("draft_output_path"),
        "source_work_order": work_order.get("work_order_path"),
        "bindings": bindings,
        "missing_evidence": [
            {
                "evidence_id": item["evidence_id"],
                "candidate_paths": item["candidate_paths"],
                "review_reason": "required artifact was not found in the local project",
            }
            for item in missing
        ],
    }


def bind_evidence(project_root: Path, evidence_id: str) -> dict[str, Any]:
    candidates = EVIDENCE_CANDIDATES.get(evidence_id, [evidence_id])
    resolved_paths = resolve_candidates(project_root, candidates)
    if not resolved_paths:
        return {
            "evidence_id": evidence_id,
            "status": "missing",
            "evidence_level": "missing_local_artifact",
            "primary_path": None,
            "paths": [],
            "candidate_paths": candidates,
        }

    primary = resolved_paths[0]
    return {
        "evidence_id": evidence_id,
        "status": "bound",
        "evidence_level": "local_artifact",
        "primary_path": relative_or_absolute(primary, project_root),
        "paths": [relative_or_absolute(path, project_root) for path in resolved_paths],
        "candidate_paths": candidates,
        "bytes": primary.stat().st_size,
        "sha256": hashlib.sha256(primary.read_bytes()).hexdigest(),
    }


def resolve_candidates(project_root: Path, candidates: list[str]) -> list[Path]:
    paths: list[Path] = []
    seen: set[Path] = set()
    for candidate in candidates:
        matches = sorted(project_root.glob(candidate)) if any(char in candidate for char in "*?[]") else [project_root / candidate]
        for path in matches:
            if path.exists() and path.is_file() and path not in seen:
                seen.add(path)
                paths.append(path)
    return paths


def build_summary(sections: list[dict[str, Any]]) -> dict[str, Any]:
    counter = Counter(binding["status"] for section in sections for binding in section.get("bindings", []))
    missing = [
        {"section": section["section"], **item}
        for section in sections
        for item in section.get("missing_evidence", [])
    ]
    return {
        "sections": len(sections),
        "bound": counter.get("bound", 0),
        "missing": counter.get("missing", 0),
        "missing_evidence": missing,
    }


def write_manuscript_section_evidence_bindings_report(path: Path, report: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def build_manuscript_section_evidence_bindings_review(report: dict[str, Any]) -> str:
    lines = [
        "# 章节证据绑定索引",
        "",
        f"- 状态：`{report.get('status')}`",
        f"- 来源 round：`{report.get('source_revision_round')}`",
        f"- 来源 scaffold：`{report.get('source_scaffold_report')}`",
        "- 正式层写回：关闭",
        "",
        "## 汇总",
        "",
    ]
    summary = report.get("summary", {})
    lines.extend(
        [
            f"- 章节数：{summary.get('sections')}",
            f"- 已绑定证据：{summary.get('bound')}",
            f"- 缺失证据：{summary.get('missing')}",
            "",
            "## Agent Team 调用节奏",
            "",
        ]
    )
    schedule = report.get("agent_team_schedule", {})
    for key in ["call_when", "called_agents", "recall_when", "next_call_when", "boundary"]:
        lines.append(f"- {key}: {schedule.get(key)}")
    lines.extend(["", "## 章节", ""])
    for section in report.get("sections", []):
        lines.extend([f"### {section.get('section')}", "", f"- 状态：`{section.get('status')}`"])
        for binding in section.get("bindings", []):
            path = binding.get("primary_path") or "missing"
            lines.append(f"- `{binding.get('evidence_id')}`: `{binding.get('status')}` -> `{path}`")
        lines.append("")
    lines.extend(["## 正式层保护", "", f"- changed: `{report.get('formal_state_guard', {}).get('changed')}`"])
    return "\n".join(lines).rstrip() + "\n"


def write_manuscript_section_evidence_bindings_review(path: Path, report: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(build_manuscript_section_evidence_bindings_review(report), encoding="utf-8")
    return path
