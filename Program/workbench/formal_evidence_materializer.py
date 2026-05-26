from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from workbench.paper_package import relative_or_absolute
from workbench.paper_revision_round import diff_formal_state, snapshot_formal_state


DEFAULT_PROPOSAL_PATH = "Submissions/formal_package/reproducibility/evidence_registry_patch_proposal.json"
DEFAULT_REPORT_PATH = "Results/json/formal_evidence_materialization_report.json"
DEFAULT_REVIEW_PATH = "Reviews/formal_evidence_materialization.md"
DEFAULT_EVIDENCE_IDS = ["variable_role_set", "sample_profile", "regression_tables"]

TARGET_PATHS = {
    "variable_role_set": "Submissions/formal_package/evidence/variable_role_set.json",
    "sample_profile": "Results/json/sample_profile.json",
    "regression_tables": "Results/json/regression_tables.json",
    "figure_manifest": "Results/json/figure_manifest.json",
    "robustness_matrix": "Results/json/robustness_matrix.json",
    "limitations_register": "Results/json/limitations_register.json",
    "approved_findings": "Results/json/approved_findings.json",
    "citation_verification_log": "Results/json/citation_verification_log.json",
    "domain_notes": "Results/json/domain_notes.json",
    "verified_context_sources": "Results/json/verified_context_sources.json",
}


def build_formal_evidence_materialization(
    project_root: Path,
    proposal_path: Path,
    evidence_ids: list[str],
    *,
    output_report_path: Path,
    formal_state_before: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    before = formal_state_before or snapshot_formal_state(project_root)
    requested = normalize_evidence_ids(evidence_ids)
    if not proposal_path.exists():
        return build_blocked_report(
            project_root,
            proposal_path,
            output_report_path,
            before,
            requested,
            ["patch_proposal_missing"],
        )

    proposal = load_json(proposal_path)
    allowed_ids = {
        str(item.get("id"))
        for item in proposal.get("patch_items") or []
        if item.get("id")
    }

    materialized: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    warnings: list[str] = []
    for evidence_id in requested:
        if evidence_id not in TARGET_PATHS:
            skipped.append({"id": evidence_id, "reason": "unsupported_evidence_id"})
            continue
        if evidence_id not in allowed_ids:
            skipped.append({"id": evidence_id, "reason": "not_present_in_patch_proposal"})
            continue

        payload, item_warnings = build_evidence_payload(project_root, evidence_id)
        warnings.extend(item_warnings)
        target_path = project_root / TARGET_PATHS[evidence_id]
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        materialized.append(
            {
                "id": evidence_id,
                "target_path": relative_or_absolute(target_path, project_root),
                "source_paths": payload.get("source_paths") or [],
                "warnings": item_warnings,
            }
        )

    after = snapshot_formal_state(project_root)
    status = "evidence_materialized" if materialized else "no_requested_evidence_materialized"
    return {
        "schema_version": "p5.formal_evidence_materialization.v1",
        "generated_at": utc_now(),
        "source_patch_proposal": relative_or_absolute(proposal_path, project_root),
        "materialization_report": relative_or_absolute(output_report_path, project_root),
        "status": status,
        "blocking_reasons": [],
        "requested_evidence_ids": requested,
        "materialized": materialized,
        "skipped": skipped,
        "warnings": sorted(set(warnings)),
        "this_command_wrote_formal_state": False,
        "this_command_wrote_final_outputs": False,
        "formal_state_guard": diff_formal_state(before, after),
        "agent_team_schedule": build_agent_team_schedule(materialized, skipped),
        "next_action": build_next_action(bool(materialized)),
        "write_boundary": (
            "本节点只从现有本地产物派生正式包证据文件；不写 state/product 正式状态，"
            "不生成最终 PDF/docx，也不修改 canonical evidence registry。"
        ),
    }


def build_blocked_report(
    project_root: Path,
    proposal_path: Path,
    output_report_path: Path,
    before: dict[str, dict[str, Any]],
    requested: list[str],
    blocking_reasons: list[str],
) -> dict[str, Any]:
    after = snapshot_formal_state(project_root)
    return {
        "schema_version": "p5.formal_evidence_materialization.v1",
        "generated_at": utc_now(),
        "source_patch_proposal": relative_or_absolute(proposal_path, project_root),
        "materialization_report": relative_or_absolute(output_report_path, project_root),
        "status": "blocked_by_patch_proposal",
        "blocking_reasons": blocking_reasons,
        "requested_evidence_ids": requested,
        "materialized": [],
        "skipped": [],
        "warnings": [],
        "this_command_wrote_formal_state": False,
        "this_command_wrote_final_outputs": False,
        "formal_state_guard": diff_formal_state(before, after),
        "agent_team_schedule": build_agent_team_schedule([], []),
        "next_action": {
            "id": "rerun_formal_evidence_registry_resolver",
            "label": "重新生成证据注册表修复提案",
            "description": "先生成 evidence_registry_patch_proposal.json，再材料化正式包证据。",
        },
        "write_boundary": (
            "本节点只从现有本地产物派生正式包证据文件；不写 state/product 正式状态，"
            "不生成最终 PDF/docx，也不修改 canonical evidence registry。"
        ),
    }


def build_evidence_payload(project_root: Path, evidence_id: str) -> tuple[dict[str, Any], list[str]]:
    if evidence_id == "variable_role_set":
        return build_variable_role_set_evidence(project_root)
    if evidence_id == "sample_profile":
        return build_sample_profile(project_root)
    if evidence_id == "regression_tables":
        return build_regression_tables(project_root)
    if evidence_id == "figure_manifest":
        return build_figure_manifest(project_root)
    if evidence_id == "robustness_matrix":
        return build_robustness_matrix(project_root)
    if evidence_id == "limitations_register":
        return build_limitations_register(project_root)
    if evidence_id == "approved_findings":
        return build_approved_findings(project_root)
    if evidence_id == "citation_verification_log":
        return build_citation_verification_log(project_root)
    if evidence_id == "domain_notes":
        return build_domain_notes(project_root)
    if evidence_id == "verified_context_sources":
        return build_verified_context_sources(project_root)
    raise ValueError(f"unsupported evidence id: {evidence_id}")


def build_variable_role_set_evidence(project_root: Path) -> tuple[dict[str, Any], list[str]]:
    variable_roles_path = project_root / "state" / "product" / "variable_roles.json"
    method_result_path = project_root / "Results" / "json" / "method_execution_result.json"
    source_roles = load_json(variable_roles_path) if variable_roles_path.exists() else {}
    method_result = load_json(method_result_path) if method_result_path.exists() else {}
    method = first_method(method_result)
    method_dataset = method.get("dataset_path") or (method.get("data_preflight") or {}).get("dataset_path")
    role_dataset = source_roles.get("dataset_path")

    warnings: list[str] = []
    if role_dataset and method_dataset and role_dataset != method_dataset:
        warnings.append("variable_role_dataset_mismatch")

    source_paths = []
    if variable_roles_path.exists():
        source_paths.append("state/product/variable_roles.json")
    if method_result_path.exists():
        source_paths.append("Results/json/method_execution_result.json")

    return (
        {
            "schema_version": "p5.variable_role_set_evidence.v1",
            "evidence_id": "variable_role_set",
            "generated_at": utc_now(),
            "source_paths": source_paths,
            "review_status": "needs_human_review" if warnings else "ready_for_review",
            "canonical_write_allowed": False,
            "source_variable_roles": source_roles,
            "source_variable_roles_dataset_path": role_dataset,
            "method_execution_dataset_path": method_dataset,
            "method_execution_variables": {
                "dependent_var": method.get("dependent_var"),
                "treatment": method.get("treatment"),
                "formula": method.get("formula"),
            },
            "warnings": warnings,
            "next_action": "人工确认变量角色是否应提升为当前 CFPS robot 研究的正式 VariableRoleSet。",
        },
        warnings,
    )


def build_sample_profile(project_root: Path) -> tuple[dict[str, Any], list[str]]:
    method_result_path = project_root / "Results" / "json" / "method_execution_result.json"
    method_result = load_json(method_result_path)
    method = first_method(method_result)
    data_preflight = method.get("data_preflight") or {}
    return (
        {
            "schema_version": "p5.sample_profile.v1",
            "evidence_id": "sample_profile",
            "generated_at": utc_now(),
            "source_paths": ["Results/json/method_execution_result.json"],
            "review_status": "ready_for_review",
            "dataset_path": data_preflight.get("dataset_path") or method.get("dataset_path"),
            "nobs": method.get("nobs"),
            "rows_read": data_preflight.get("rows_read"),
            "usable_numeric_rows": data_preflight.get("usable_numeric_rows"),
            "dropped_rows": data_preflight.get("dropped_rows"),
            "required_fields": data_preflight.get("required_fields") or [],
            "checks": data_preflight.get("checks") or [],
            "method_task_id": method.get("task_id"),
            "run_id": method.get("run_id"),
        },
        [],
    )


def build_regression_tables(project_root: Path) -> tuple[dict[str, Any], list[str]]:
    method_result_path = project_root / "Results" / "json" / "method_execution_result.json"
    method_result = load_json(method_result_path)
    tables = []
    for index, method in enumerate(method_result.get("methods") or [], start=1):
        coefficients = method.get("coefficients") or {}
        standard_errors = method.get("standard_errors") or {}
        t_statistics = method.get("t_statistics") or {}
        p_values = method.get("p_values") or {}
        rows = []
        for term in coefficients:
            rows.append(
                {
                    "term": term,
                    "coefficient": coefficients.get(term),
                    "standard_error": standard_errors.get(term),
                    "t_statistic": t_statistics.get(term),
                    "p_value": p_values.get(term),
                }
            )
        tables.append(
            {
                "table_id": f"regression_table_{index}",
                "run_id": method.get("run_id"),
                "task_id": method.get("task_id"),
                "method_id": method.get("method_id"),
                "estimator": method.get("estimator"),
                "formula": method.get("formula"),
                "nobs": method.get("nobs"),
                "dependent_var": method.get("dependent_var"),
                "treatment": method.get("treatment"),
                "coefficient_rows": rows,
                "diagnostics": method.get("diagnostics") or {},
                "summary_text": method.get("summary_text"),
            }
        )
    return (
        {
            "schema_version": "p5.regression_tables.v1",
            "evidence_id": "regression_tables",
            "generated_at": utc_now(),
            "source_paths": ["Results/json/method_execution_result.json"],
            "review_status": "ready_for_review",
            "tables": tables,
        },
        [],
    )


def build_figure_manifest(project_root: Path) -> tuple[dict[str, Any], list[str]]:
    figure_dirs = [
        project_root / "Results" / "fig",
        project_root / "Results" / "figures",
        project_root / "Submissions" / "formal_package" / "figures",
    ]
    manifest_candidates = [
        project_root / "Submissions" / "cfps_robot_pdf_export_manifest.json",
        project_root / "Submissions" / "export_manifest.json",
        project_root / "Results" / "fig" / "README.md",
    ]
    figure_suffixes = {".png", ".jpg", ".jpeg", ".svg", ".pdf"}
    figures: list[dict[str, Any]] = []
    for directory in figure_dirs:
        if not directory.exists():
            continue
        for path in sorted(directory.rglob("*")):
            if path.is_file() and path.suffix.lower() in figure_suffixes:
                figures.append(
                    {
                        "id": path.stem,
                        "path": relative_or_absolute(path, project_root),
                        "format": path.suffix.lower().lstrip("."),
                        "status": "registered",
                    }
                )

    source_paths = [
        relative_or_absolute(path, project_root)
        for path in manifest_candidates
        if path.exists()
    ]
    if not source_paths:
        source_paths = [
            relative_or_absolute(directory, project_root)
            for directory in figure_dirs
            if directory.exists()
        ]

    warnings: list[str] = []
    status = "registered"
    review_status = "ready_for_review"
    next_action = "核对图表编号、caption、正文引用和导出格式。"
    if not figures:
        status = "no_rendered_figures_registered"
        review_status = "needs_human_review"
        warnings.append("no_rendered_figures_registered")
        next_action = "先渲染或登记真实图表，再进入最终 PDF 导出。"

    return (
        {
            "schema_version": "p5.figure_manifest.v1",
            "evidence_id": "figure_manifest",
            "generated_at": utc_now(),
            "source_paths": source_paths,
            "status": status,
            "review_status": review_status,
            "figures": figures,
            "tables_referenced_elsewhere": ["Results/json/regression_tables.json"],
            "canonical_write_allowed": False,
            "next_action": next_action,
        },
        warnings,
    )


def build_robustness_matrix(project_root: Path) -> tuple[dict[str, Any], list[str]]:
    diagnostics_path = project_root / "Results" / "json" / "method_diagnostics_report.json"
    gate_path = project_root / "Results" / "json" / "method_gate_report.json"
    analysis_path = project_root / "Results" / "json" / "cfps_robot_analysis_result.json"
    diagnostics_report = load_json_if_exists(diagnostics_path)
    gate_report = load_json_if_exists(gate_path)
    analysis_result = load_json_if_exists(analysis_path)

    checks: list[dict[str, Any]] = []
    for diagnostic in diagnostics_report.get("diagnostics") or []:
        status = diagnostic.get("status")
        checks.append(
            {
                "id": diagnostic.get("id"),
                "status": status,
                "scope": diagnostic.get("scope"),
                "source": "method_diagnostics_report",
                "outputs": diagnostic.get("outputs") or {},
                "review_items": diagnostic.get("review_items") or [],
                "requires_human_review": status in {"yellow", "needs_manual_review", "red"},
            }
        )

    existing_ids = {item.get("id") for item in checks}
    for diagnostic in gate_report.get("diagnostics") or []:
        diagnostic_id = diagnostic.get("id")
        if diagnostic_id in existing_ids:
            continue
        status = diagnostic.get("status")
        checks.append(
            {
                "id": diagnostic_id,
                "status": status,
                "source": "method_gate_report",
                "observed": diagnostic.get("observed"),
                "review_items": [],
                "requires_human_review": status in {"yellow", "needs_manual_review", "failed", "red"},
            }
        )

    robustness_findings = []
    for finding in (analysis_result.get("robustness_findings") or {}).get("_findings") or []:
        robustness_findings.append(
            {
                "id": finding.get("name"),
                "label": finding.get("label"),
                "status": finding.get("severity"),
                "value": finding.get("value"),
                "interpretation": finding.get("interpretation"),
                "source": "cfps_robot_analysis_result",
            }
        )

    warnings: list[str] = []
    needs_review = any(item.get("requires_human_review") for item in checks)
    if needs_review:
        warnings.append("robustness_items_need_review")

    source_paths = [
        relative_or_absolute(path, project_root)
        for path in [diagnostics_path, gate_path, analysis_path]
        if path.exists()
    ]
    return (
        {
            "schema_version": "p5.robustness_matrix.v1",
            "evidence_id": "robustness_matrix",
            "generated_at": utc_now(),
            "source_paths": source_paths,
            "method_family": diagnostics_report.get("method_family") or gate_report.get("method_family"),
            "method_subtype": diagnostics_report.get("method_subtype") or gate_report.get("method_subtype"),
            "status": "completed_with_review_items" if needs_review else "ready_for_review",
            "review_status": "needs_human_review" if needs_review else "ready_for_review",
            "checks": checks,
            "supplemental_robustness_findings": robustness_findings,
            "gate_status": gate_report.get("gate_status"),
            "required_evidence": gate_report.get("required_evidence") or [],
            "yellow_items": gate_report.get("yellow_items") or [],
            "red_items": gate_report.get("red_items") or [],
            "blocking_items": gate_report.get("blocking_items") or [],
            "recommended_next_tasks": gate_report.get("recommended_next_tasks") or [],
            "canonical_write_allowed": False,
            "interpretation_boundary": "该矩阵支持草案中的稳健性讨论和下一轮任务拆解；正式强因果表述仍取决于黄灯和人工审阅项是否关闭。",
        },
        warnings,
    )


def build_limitations_register(project_root: Path) -> tuple[dict[str, Any], list[str]]:
    scorecard_path = project_root / "Results" / "json" / "reviewer_scorecard_report.json"
    gate_path = project_root / "Results" / "json" / "method_gate_report.json"
    diagnostics_path = project_root / "Results" / "json" / "method_diagnostics_report.json"
    scorecard = load_json_if_exists(scorecard_path)
    gate_report = load_json_if_exists(gate_path)
    diagnostics_report = load_json_if_exists(diagnostics_path)

    limitations: list[dict[str, Any]] = []
    for task in scorecard.get("revision_tasks") or []:
        limitations.append(
            {
                "id": task.get("id"),
                "source": "reviewer_scorecard_report.revision_tasks",
                "severity": task.get("severity"),
                "agent": task.get("agent"),
                "blocking_scope": task.get("blocking_scope"),
                "evidence_source": task.get("evidence_source"),
                "recommended_action": task.get("recommended_action"),
                "requires_human_acceptance": bool(task.get("requires_human_acceptance")),
                "status": task.get("status"),
            }
        )

    for item in gate_report.get("yellow_items") or []:
        limitations.append(
            {
                "id": f"yellow_item:{item}",
                "source": "method_gate_report.yellow_items",
                "severity": "major",
                "blocking_scope": "formal_claims",
                "evidence_source": item,
                "recommended_action": "关闭该方法门黄灯项，或在正文中保留明确局限说明。",
                "requires_human_acceptance": True,
                "status": "open",
            }
        )

    for item in gate_report.get("blocking_items") or []:
        limitations.append(
            {
                "id": f"blocking_item:{item}",
                "source": "method_gate_report.blocking_items",
                "severity": "blocking",
                "blocking_scope": "export",
                "evidence_source": item,
                "recommended_action": "补齐阻断证据后再进入导出。",
                "requires_human_acceptance": True,
                "status": "open",
            }
        )

    blocks_export = bool(scorecard.get("blocks_export_or_formal_claims") or gate_report.get("blocking_items"))
    warnings: list[str] = []
    if limitations or blocks_export:
        warnings.append("limitations_need_human_review")

    source_paths = [
        relative_or_absolute(path, project_root)
        for path in [scorecard_path, gate_path, diagnostics_path]
        if path.exists()
    ]
    return (
        {
            "schema_version": "p5.limitations_register.v1",
            "evidence_id": "limitations_register",
            "generated_at": utc_now(),
            "source_paths": source_paths,
            "status": "needs_human_review" if limitations or blocks_export else "ready_for_review",
            "review_status": "needs_human_review" if limitations or blocks_export else "ready_for_review",
            "method_family": scorecard.get("method_family") or gate_report.get("method_family") or diagnostics_report.get("method_family"),
            "method_subtype": scorecard.get("method_subtype") or gate_report.get("method_subtype") or diagnostics_report.get("method_subtype"),
            "overall_score": scorecard.get("overall_score"),
            "overall_verdict": scorecard.get("overall_verdict"),
            "blocks_export_or_formal_claims": blocks_export,
            "limitations": limitations,
            "gate_status": gate_report.get("gate_status"),
            "canonical_write_allowed": False,
            "claim_boundary": "局限登记表用于写作和导出前审阅；正式结论强度必须由人工基于这些条目确认。",
        },
        warnings,
    )


def build_approved_findings(project_root: Path) -> tuple[dict[str, Any], list[str]]:
    finding_reviews_path = project_root / "state" / "product" / "finding_reviews.json"
    candidate_reviews_path = project_root / "state" / "product" / "manuscript_candidate_reviews.json"
    finding_reviews = load_json_if_exists(finding_reviews_path)
    candidate_reviews = load_json_if_exists(candidate_reviews_path)

    raw_reviews = list(as_record_list(finding_reviews.get("reviews") or finding_reviews.get("items") or []))
    raw_reviews.extend(as_record_list(candidate_reviews.get("reviews") or candidate_reviews.get("items") or []))

    findings: list[dict[str, Any]] = []
    warnings: list[str] = []
    for review in raw_reviews:
        if review.get("review_status") != "approved" or not review.get("can_write_to_draft"):
            continue
        artifact_path = str(review.get("artifact_path") or "")
        artifact_exists = bool(artifact_path and (project_root / artifact_path).exists())
        if artifact_path and not artifact_exists:
            warnings.append("approved_finding_artifact_missing")
        findings.append(
            {
                "review_id": review.get("id"),
                "finding_id": review.get("finding_id"),
                "claim": review.get("claim"),
                "run_id": review.get("run_id"),
                "artifact_path": artifact_path,
                "artifact_exists": artifact_exists,
                "evidence_level": review.get("evidence_level"),
                "review_status": review.get("review_status"),
                "source": "finding_reviews",
            }
        )

    if not findings:
        warnings.append("approved_findings_empty")

    source_paths = [
        relative_or_absolute(path, project_root)
        for path in [finding_reviews_path, candidate_reviews_path]
        if path.exists()
    ]
    needs_review = bool(warnings)
    return (
        {
            "schema_version": "p5.approved_findings.v1",
            "evidence_id": "approved_findings",
            "generated_at": utc_now(),
            "source_paths": source_paths,
            "status": "needs_human_review" if needs_review else "ready_for_review",
            "review_status": "needs_human_review" if needs_review else "ready_for_review",
            "approved_count": len(findings),
            "findings": findings,
            "canonical_write_allowed": False,
            "warnings": sorted(set(warnings)),
            "next_action": "人工复核 approved finding 是否与当前正式稿章节和最新执行结果一致。",
        },
        sorted(set(warnings)),
    )


def build_citation_verification_log(project_root: Path) -> tuple[dict[str, Any], list[str]]:
    literature_report_path = project_root / "Results" / "json" / "literature_package_report.json"
    verified_bibliography_path = project_root / "Data" / "literature" / "processed" / "verified_bibliography.csv"
    literature_report = load_json_if_exists(literature_report_path)
    rows = read_csv_rows(verified_bibliography_path)

    citations = []
    missing_doi = False
    unverified = False
    for row in rows:
        doi = row.get("doi") or ""
        verification_status = row.get("verification_status") or ""
        if not doi:
            missing_doi = True
        if verification_status not in {"doi_verified", "verified"}:
            unverified = True
        citations.append(
            {
                "source_id": row.get("source_id"),
                "citation_key": row.get("citation_key"),
                "title": row.get("title"),
                "authors": row.get("authors"),
                "year": row.get("year"),
                "venue": row.get("venue"),
                "doi": doi,
                "verification_status": verification_status,
                "used_in_section": row.get("used_in_section"),
                "url": row.get("url"),
            }
        )

    warnings: list[str] = []
    if literature_report.get("status") != "approved":
        warnings.append("citation_log_needs_manual_review")
    if missing_doi:
        warnings.append("citation_entries_missing_doi")
    if unverified:
        warnings.append("citation_entries_not_fully_verified")

    source_paths = [
        relative_or_absolute(path, project_root)
        for path in [literature_report_path, verified_bibliography_path]
        if path.exists()
    ]
    needs_review = bool(warnings)
    return (
        {
            "schema_version": "p5.citation_verification_log.v1",
            "evidence_id": "citation_verification_log",
            "generated_at": utc_now(),
            "source_paths": source_paths,
            "status": "needs_human_review" if needs_review else "ready_for_review",
            "review_status": "needs_human_review" if needs_review else "ready_for_review",
            "literature_package_status": literature_report.get("status"),
            "verification_channels": literature_report.get("verification_channels") or [],
            "verified_count": len([item for item in citations if item.get("verification_status") in {"doi_verified", "verified"}]),
            "citations": citations,
            "cnki_manual_queue": literature_report.get("cnki_manual_queue") or [],
            "canonical_write_allowed": False,
            "warnings": sorted(set(warnings)),
            "next_action": "人工复核 DOI、CNKI 队列和正文引用绑定后，再允许进入正式引用层。",
        },
        sorted(set(warnings)),
    )


def build_domain_notes(project_root: Path) -> tuple[dict[str, Any], list[str]]:
    literature_report_path = project_root / "Results" / "json" / "literature_package_report.json"
    research_question_path = project_root / "state" / "product" / "research_question.json"
    design_spec_path = project_root / "state" / "product" / "design_spec.json"
    literature_report = load_json_if_exists(literature_report_path)
    research_question = load_json_if_exists(research_question_path)
    design_spec = load_json_if_exists(design_spec_path)
    inputs = literature_report.get("formal_state_inputs") or {}
    design_context = inputs.get("design_spec") or design_spec
    run_context = inputs.get("run_plan") or {}

    warnings = ["domain_notes_need_human_review"]
    source_paths = [
        relative_or_absolute(path, project_root)
        for path in [literature_report_path, research_question_path, design_spec_path]
        if path.exists()
    ]
    return (
        {
            "schema_version": "p5.domain_notes.v1",
            "evidence_id": "domain_notes",
            "generated_at": utc_now(),
            "source_paths": source_paths,
            "status": "needs_human_review",
            "review_status": "needs_human_review",
            "research_question": {
                "title": research_question.get("title") or (inputs.get("research_question") or {}).get("title"),
                "status": research_question.get("status"),
                "dataset_hint": research_question.get("dataset_hint"),
            },
            "data_context": {
                "dataset_path": run_context.get("dataset_path"),
                "unit": run_context.get("unit"),
            },
            "method_context": {
                "method_family": design_context.get("method_family"),
                "method_subtype": design_context.get("method_subtype"),
            },
            "literature_context": {
                "package_status": literature_report.get("status"),
                "evidence_level": literature_report.get("evidence_level"),
                "verification_channels": literature_report.get("verification_channels") or [],
                "missing_evidence": literature_report.get("missing_evidence") or [],
            },
            "cnki_manual_queue": literature_report.get("cnki_manual_queue") or [],
            "canonical_write_allowed": False,
            "warnings": warnings,
            "next_action": "人工复核领域语境是否足够支撑正式引言、文献综述和方法选择说明。",
        },
        warnings,
    )


def build_verified_context_sources(project_root: Path) -> tuple[dict[str, Any], list[str]]:
    source_registry_path = project_root / "state" / "source_registry.json"
    orchestration_source_registry_path = project_root / "state" / "orchestration" / "source_registry.json"
    literature_report_path = project_root / "Results" / "json" / "literature_package_report.json"
    verified_bibliography_path = project_root / "Data" / "literature" / "processed" / "verified_bibliography.csv"
    candidate_literature_path = project_root / "Data" / "literature" / "processed" / "candidate_literature.csv"

    source_registry = load_json_if_exists(source_registry_path)
    if not source_registry:
        source_registry = load_json_if_exists(orchestration_source_registry_path)
    literature_report = load_json_if_exists(literature_report_path)
    verified_rows = read_csv_rows(verified_bibliography_path)
    candidate_rows = read_csv_rows(candidate_literature_path)

    warnings = ["verified_context_sources_need_review"]
    source_paths = [
        relative_or_absolute(path, project_root)
        for path in [
            source_registry_path,
            orchestration_source_registry_path,
            literature_report_path,
            verified_bibliography_path,
            candidate_literature_path,
        ]
        if path.exists()
    ]
    return (
        {
            "schema_version": "p5.verified_context_sources.v1",
            "evidence_id": "verified_context_sources",
            "generated_at": utc_now(),
            "source_paths": source_paths,
            "status": "needs_human_review",
            "review_status": "needs_human_review",
            "source_registry": source_registry,
            "literature_source_summary": {
                "verified_bibliography_rows": len(verified_rows),
                "candidate_literature_rows": len(candidate_rows),
                "verification_channels": literature_report.get("verification_channels") or [],
                "cnki_manual_queue_count": len(literature_report.get("cnki_manual_queue") or []),
                "missing_evidence": literature_report.get("missing_evidence") or [],
            },
            "canonical_write_allowed": False,
            "warnings": warnings,
            "next_action": "人工复核本地数据、Zotero/PDF、CNKI 和候选文献来源后，再允许正式引用和上下文写回。",
        },
        warnings,
    )


def write_formal_evidence_materialization_outputs(
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
        "# P5-E2a 正式包证据材料化",
        "",
        f"- Status: `{report.get('status')}`",
        f"- Patch proposal: `{report.get('source_patch_proposal')}`",
        "- 正式层写回：未发生",
        "- 最终 PDF/docx：未生成",
        "",
        "## 已材料化证据",
        "",
    ]
    materialized = report.get("materialized") or []
    if materialized:
        for item in materialized:
            warnings = ", ".join(item.get("warnings") or ["none"])
            lines.append(f"- `{item.get('id')}` -> `{item.get('target_path')}` ({warnings})")
    else:
        lines.append("- 无。")

    lines.extend(["", "## 跳过项", ""])
    skipped = report.get("skipped") or []
    if skipped:
        for item in skipped:
            lines.append(f"- `{item.get('id')}`: `{item.get('reason')}`")
    else:
        lines.append("- 无。")

    lines.extend(["", "## Warnings", ""])
    warnings = report.get("warnings") or []
    if warnings:
        lines.extend(f"- `{warning}`" for warning in warnings)
    else:
        lines.append("- 无。")

    lines.extend(
        [
            "",
            "## 下一步",
            "",
            f"- `{report.get('next_action', {}).get('id')}`：{report.get('next_action', {}).get('description')}",
        ]
    )
    return "\n".join(lines) + "\n"


def build_agent_team_schedule(
    materialized: list[dict[str, Any]],
    skipped: list[dict[str, Any]],
) -> dict[str, Any]:
    agents = {"VerifierAgent"}
    for item in materialized + skipped:
        evidence_id = item.get("id")
        if evidence_id == "variable_role_set":
            agents.add("DataAgent")
        elif evidence_id == "regression_tables":
            agents.add("ExecutionAgent")
        elif evidence_id == "sample_profile":
            agents.add("DataAgent")
        elif evidence_id == "figure_manifest":
            agents.add("ExecutionAgent")
        elif evidence_id == "robustness_matrix":
            agents.add("MethodAgent")
        elif evidence_id == "limitations_register":
            agents.add("ReviewerAgent")
        elif evidence_id == "approved_findings":
            agents.add("ReviewerAgent")
        elif evidence_id == "citation_verification_log":
            agents.add("LiteratureAgent")
        elif evidence_id == "domain_notes":
            agents.add("DomainAgent")
        elif evidence_id == "verified_context_sources":
            agents.add("LiteratureAgent")
            agents.add("DataAgent")
    return {
        "call_when": "before_high_confidence_evidence_materialization",
        "called_agents": sorted(agents),
        "recall_when": "after_evidence_files_written",
        "next_call_when": "before_rerunning_pdf_preflight_or_promoting_formal_state",
        "integration_owner": "MainAgent",
        "boundary": "Agent Team 只复核 evidence file 是否可被预检消费；正式状态提升仍需人工确认。",
    }


def build_next_action(wrote_anything: bool) -> dict[str, str]:
    if wrote_anything:
        return {
            "id": "rerun_formal_pdf_export_preflight",
            "label": "重跑 PDF 导出预检",
            "description": "让 P5-D 读取新材料化的证据文件，确认哪些缺口已经消除。",
        }
    return {
        "id": "review_patch_proposal_scope",
        "label": "检查修复提案范围",
        "description": "当前请求的 evidence id 没有被材料化；检查 patch proposal 或拆成新的证据节点。",
    }


def normalize_evidence_ids(evidence_ids: list[str]) -> list[str]:
    normalized: list[str] = []
    for value in evidence_ids:
        for part in value.split(","):
            candidate = part.strip()
            if candidate and candidate not in normalized:
                normalized.append(candidate)
    return normalized


def first_method(method_result: dict[str, Any]) -> dict[str, Any]:
    methods = method_result.get("methods") or []
    return methods[0] if methods else {}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_json_if_exists(path: Path) -> dict[str, Any]:
    return load_json(path) if path.exists() else {}


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as file:
        return [dict(row) for row in csv.DictReader(file)]


def as_record_list(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    if isinstance(value, dict):
        return [item for item in value.values() if isinstance(item, dict)]
    return []


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
