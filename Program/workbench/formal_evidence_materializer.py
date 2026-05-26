from __future__ import annotations

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


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
