from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from workbench.paper_package import relative_or_absolute
from workbench.paper_revision_round import diff_formal_state, snapshot_formal_state


def build_manuscript_section_draft_expansion_report(
    project_root: Path,
    evidence_bindings: dict[str, Any],
    evidence_bindings_path: Path,
    *,
    target_sections: list[str],
    formal_state_before: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    before = formal_state_before or snapshot_formal_state(project_root)
    binding_by_section = {
        section.get("section"): section
        for section in evidence_bindings.get("sections", [])
        if section.get("section")
    }
    sections = [
        build_section_expansion(project_root, section_name, binding_by_section.get(section_name))
        for section_name in target_sections
    ]
    after = snapshot_formal_state(project_root)
    summary = build_summary(sections)
    status = "section_drafts_expanded" if summary["expanded"] and not summary["blocked"] else "section_drafts_blocked"
    return {
        "schema_version": "p6.manuscript_section_draft_expansion.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "draft_layer_only": True,
        "formal_writeback_allowed": False,
        "source_evidence_bindings": relative_or_absolute(evidence_bindings_path, project_root),
        "summary": summary,
        "sections": sections,
        "agent_team_schedule": {
            "call_when": "after_bound_evidence_selected",
            "called_agents": ["ManuscriptAgent", "VerifierAgent"],
            "recall_when": "after_target_section_draft_expanded",
            "next_call_when": "before_section_semantic_review",
            "boundary": "ManuscriptAgent 只扩写草案层；VerifierAgent 随后反查 consumed evidence 与章节论断。",
        },
        "formal_state_guard": diff_formal_state(before, after),
    }


def build_section_expansion(
    project_root: Path,
    section_name: str,
    section_binding: dict[str, Any] | None,
) -> dict[str, Any]:
    if section_binding is None:
        return {
            "section": section_name,
            "status": "blocked_by_missing_section_binding",
            "path": None,
            "blocking_reasons": ["section_binding_missing"],
            "consumed_evidence": [],
        }
    if section_binding.get("status") != "evidence_bound":
        return {
            "section": section_name,
            "status": "blocked_by_missing_evidence",
            "path": section_binding.get("section_file"),
            "blocking_reasons": ["missing_evidence_remaining"],
            "missing_evidence": section_binding.get("missing_evidence", []),
            "consumed_evidence": [],
        }

    consumed = [
        {
            "evidence_id": binding.get("evidence_id"),
            "path": binding.get("primary_path"),
            "sha256": binding.get("sha256"),
            "evidence_level": binding.get("evidence_level"),
        }
        for binding in section_binding.get("bindings", [])
        if binding.get("status") == "bound"
    ]
    section_path = project_root / str(section_binding.get("section_file"))
    section_path.parent.mkdir(parents=True, exist_ok=True)
    section_path.write_text(build_section_draft_markdown(project_root, section_name, consumed), encoding="utf-8")
    return {
        "section": section_name,
        "status": "section_draft_expanded",
        "path": relative_or_absolute(section_path, project_root),
        "blocking_reasons": [],
        "consumed_evidence": consumed,
    }


def build_section_draft_markdown(project_root: Path, section_name: str, consumed: list[dict[str, Any]]) -> str:
    evidence_lines = [
        f"- `{item['evidence_id']}` -> `{item['path']}`; sha256=`{item['sha256']}`"
        for item in consumed
    ]
    evidence_ids = {item["evidence_id"] for item in consumed}
    paragraphs = build_section_paragraphs(project_root, evidence_ids)
    return (
        f"# {section_name}\n\n"
        "- Status: `section_draft_expanded`\n"
        "- Agent: `ManuscriptAgent`\n"
        "- Draft layer: `true`\n"
        "- Final paper write: `false`\n\n"
        "## 已消费证据\n\n"
        f"{chr(10).join(evidence_lines)}\n\n"
        "## 草案正文\n\n"
        f"{chr(10).join(paragraphs)}\n\n"
        "## 审阅事项\n\n"
        "- VerifierAgent 需要逐条反查本节论断是否能回到 consumed evidence。\n"
        "- 人工确认前，本节仍停留在草案层，不进入正式论文。\n"
    )


def build_section_paragraphs(project_root: Path, evidence_ids: set[str]) -> list[str]:
    if {"main_regression_table", "approved_findings", "coefficient_interpretation"}.issubset(evidence_ids):
        table_summary = summarize_json(project_root / "Results" / "json" / "regression_tables.json", project_root)
        finding_summary = summarize_json(project_root / "Results" / "json" / "approved_findings.json", project_root)
        coefficient_summary = summarize_json(project_root / "Results" / "json" / "method_execution_result.json", project_root)
        return [
            "本节围绕主回归表、已审批 finding 和系数解释证据组织结果叙述。主表提供估计方向、标准误和显著性信息；approved findings 提供可以进入正文候选的研究论断；method execution result 则把系数解释绑定回本地执行产物。",
            f"主表证据摘要：{table_summary}",
            f"已审批 finding 摘要：{finding_summary}",
            f"系数解释证据摘要：{coefficient_summary}",
            "写作上，Main Results 应先说明核心估计量和经济含义，再解释该结果如何回答研究问题，最后交代后续稳健性、机制或异质性检验需要继续支撑的部分。",
        ]
    return [
        "本节已经绑定本地证据，草案正文按 consumed evidence 组织。后续扩写应继续保持每个关键论断都有可追溯路径。",
    ]


def summarize_json(path: Path, project_root: Path | None = None) -> str:
    if not path.exists():
        root = project_root or path.parent
        return f"{relative_or_absolute(path, root)} missing"
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and data.get("findings"):
        claims = []
        for item in data["findings"][:3]:
            claim = item.get("claim")
            if claim:
                claims.append(str(claim))
            else:
                claims.append(
                    ", ".join(
                        f"{key}={item.get(key)}"
                        for key in ["finding_id", "run_id", "review_status", "evidence_level"]
                        if item.get(key) is not None
                    )
                )
        return "；".join(part for part in claims if part) or "findings present"
    if isinstance(data, dict) and data.get("tables"):
        rows = []
        for table in data["tables"][:3]:
            row_parts = []
            for key in ["id", "table_id", "dependent_variable", "dependent_var", "key_regressor", "treatment", "nobs"]:
                if table.get(key) is not None:
                    row_parts.append(f"{key}={table.get(key)}")
            treatment = table.get("treatment") or table.get("key_regressor")
            coefficient_rows = table.get("coefficient_rows", [])
            treatment_row = next((row for row in coefficient_rows if row.get("term") == treatment), None)
            if treatment_row:
                for key in ["coefficient", "standard_error", "p_value"]:
                    if treatment_row.get(key) is not None:
                        row_parts.append(f"{key}={treatment_row.get(key)}")
            else:
                for key in ["coefficient", "standard_error", "p_value"]:
                    if table.get(key) is not None:
                        row_parts.append(f"{key}={table.get(key)}")
            rows.append(", ".join(row_parts))
        return "；".join(rows) or "tables present"
    if isinstance(data, dict) and data.get("coefficients"):
        rows = []
        for coefficient in data["coefficients"][:3]:
            rows.append(
                ", ".join(
                    f"{key}={value}"
                    for key, value in coefficient.items()
                    if key in {"term", "estimate", "standard_error", "p_value"}
                )
            )
        return "；".join(rows) or "coefficients present"
    if isinstance(data, dict) and data.get("methods"):
        rows = []
        for method in data["methods"][:3]:
            row_parts = []
            for key in ["task_id", "method_id", "estimator", "dependent_var", "treatment", "nobs"]:
                if method.get(key) is not None:
                    row_parts.append(f"{key}={method.get(key)}")
            treatment = method.get("treatment")
            if treatment:
                coefficient = method.get("treatment_coefficient") or method.get("coefficients", {}).get(treatment)
                standard_error = method.get("standard_errors", {}).get(treatment)
                p_value = method.get("p_values", {}).get(treatment)
                if coefficient is not None:
                    row_parts.append(f"coefficient={coefficient}")
                if standard_error is not None:
                    row_parts.append(f"standard_error={standard_error}")
                if p_value is not None:
                    row_parts.append(f"p_value={p_value}")
            rows.append(", ".join(row_parts))
        return "；".join(rows) or "methods present"
    return json.dumps(data, ensure_ascii=False)[:320]


def build_summary(sections: list[dict[str, Any]]) -> dict[str, Any]:
    counts = Counter(section.get("status") for section in sections)
    return {
        "requested": len(sections),
        "expanded": counts.get("section_draft_expanded", 0),
        "blocked": sum(count for status, count in counts.items() if status != "section_draft_expanded"),
    }


def write_manuscript_section_draft_expansion_report(path: Path, report: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def build_manuscript_section_draft_expansion_review(report: dict[str, Any]) -> str:
    lines = [
        "# 章节草案扩写报告",
        "",
        f"- 状态：`{report.get('status')}`",
        f"- 来源：`{report.get('source_evidence_bindings')}`",
        "- 正式层写回：关闭",
        "",
        "## 汇总",
        "",
    ]
    summary = report.get("summary", {})
    lines.extend(
        [
            f"- requested: {summary.get('requested')}",
            f"- expanded: {summary.get('expanded')}",
            f"- blocked: {summary.get('blocked')}",
            "",
            "## 章节",
            "",
        ]
    )
    for section in report.get("sections", []):
        lines.extend([f"### {section.get('section')}", "", f"- 状态：`{section.get('status')}`"])
        if section.get("path"):
            lines.append(f"- 文件：`{section.get('path')}`")
        for evidence in section.get("consumed_evidence", []):
            lines.append(f"- `{evidence.get('evidence_id')}` -> `{evidence.get('path')}`")
        for reason in section.get("blocking_reasons", []):
            lines.append(f"- 阻断：`{reason}`")
        lines.append("")
    lines.extend(["## 正式层保护", "", f"- changed: `{report.get('formal_state_guard', {}).get('changed')}`"])
    return "\n".join(lines).rstrip() + "\n"


def write_manuscript_section_draft_expansion_review(path: Path, report: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(build_manuscript_section_draft_expansion_review(report), encoding="utf-8")
    return path
