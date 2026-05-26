from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from workbench.paper_package import relative_or_absolute
from workbench.paper_revision_round import diff_formal_state, snapshot_formal_state


APPROVAL_KEY = "formal_writeback_preflight"
DEFAULT_APPROVAL_REPORT = "Results/json/formal_writeback_approval.json"
DEFAULT_APPROVAL_STATE = "state/product/writeback_approvals.json"
DEFAULT_REPORT_PATH = "Results/json/formal_paper_package_manifest.json"
DEFAULT_REVIEW_PATH = "Reviews/formal_paper_package_manifest.md"
DEFAULT_PACKAGE_ROOT = "Submissions/formal_package"

PACKAGE_SECTION_SPECS = [
    {
        "category": "sections",
        "label": "章节扩写",
        "directory_name": "manuscript",
        "expected_artifacts": ["section_drafts", "section_index"],
    },
    {
        "category": "citations",
        "label": "引用与文献",
        "directory_name": "literature",
        "expected_artifacts": ["verified_bibliography", "contribution_matrix"],
    },
    {
        "category": "method_narrative",
        "label": "方法叙述",
        "directory_name": "methods",
        "expected_artifacts": ["method_gate_report", "method_diagnostics_report"],
    },
    {
        "category": "result_tables",
        "label": "结果表与样本说明",
        "directory_name": "results",
        "expected_artifacts": ["regression_tables", "sample_profile"],
    },
    {
        "category": "reproducibility",
        "label": "复现说明",
        "directory_name": "reproducibility",
        "expected_artifacts": ["replication_readme", "artifact_manifest"],
    },
]


def build_formal_paper_package_manifest(
    project_root: Path,
    approval_report: dict[str, Any],
    approval_report_path: Path,
    approval_state: dict[str, Any],
    approval_state_path: Path,
    package_root: Path,
    *,
    formal_state_before: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    before = formal_state_before or snapshot_formal_state(project_root)
    blocking_reasons = build_blocking_reasons(approval_report, approval_state)
    ready = not blocking_reasons

    if ready:
        create_package_skeleton(project_root, package_root, approval_report)

    after = snapshot_formal_state(project_root)
    package_sections = build_package_sections(project_root, package_root, approval_report) if ready else []
    return {
        "schema_version": "p5.formal_paper_package_manifest.v1",
        "generated_at": utc_now(),
        "source_approval": relative_or_absolute(approval_report_path, project_root),
        "approval_state_path": relative_or_absolute(approval_state_path, project_root),
        "package_root": relative_or_absolute(package_root, project_root),
        "status": "formal_package_manifest_ready" if ready else "blocked_by_approval",
        "blocking_reasons": blocking_reasons,
        "can_build_package": ready,
        "this_command_wrote_formal_state": False,
        "this_command_wrote_final_outputs": False,
        "final_outputs_written": [],
        "package_sections": package_sections,
        "formal_state_guard": diff_formal_state(before, after),
        "agent_team_schedule": build_agent_team_schedule(ready),
        "next_action": build_next_action(ready),
    }


def build_blocking_reasons(approval_report: dict[str, Any], approval_state: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    if approval_report.get("status") != "approved_for_p5" or not approval_report.get("can_enter_p5"):
        reasons.append("approval_report_not_approved_for_p5")
    if approval_report.get("this_command_wrote_formal_state"):
        reasons.append("approval_report_claims_formal_state_write")
    if approval_report.get("formal_state_guard", {}).get("changed"):
        reasons.append("approval_report_formal_state_changed")

    entry = (approval_state.get("formal_preflight_approvals") or {}).get(APPROVAL_KEY)
    if not entry:
        reasons.append("approval_state_missing_formal_entry")
    elif entry.get("status") != "approved" or not entry.get("can_enter_p5"):
        reasons.append("approval_state_formal_entry_not_approved")
    return reasons


def build_package_sections(
    project_root: Path,
    package_root: Path,
    approval_report: dict[str, Any],
) -> list[dict[str, Any]]:
    approved_categories = set(approval_report.get("writeback_scope_categories") or [])
    sections: list[dict[str, Any]] = []
    for order, spec in enumerate(PACKAGE_SECTION_SPECS, start=1):
        category = spec["category"]
        section_dir = package_root / spec["directory_name"]
        sections.append(
            {
                "order": order,
                "category": category,
                "label": spec["label"],
                "directory": relative_or_absolute(section_dir, project_root),
                "approved_by_p5a": category in approved_categories,
                "write_status": "skeleton_only",
                "evidence_level": "local_file" if section_dir.exists() else "planned_artifact",
                "expected_artifacts": spec["expected_artifacts"],
            }
        )
    return sections


def create_package_skeleton(project_root: Path, package_root: Path, approval_report: dict[str, Any]) -> None:
    package_root.mkdir(parents=True, exist_ok=True)
    for spec in PACKAGE_SECTION_SPECS:
        (package_root / spec["directory_name"]).mkdir(parents=True, exist_ok=True)
    (package_root / "README.md").write_text(build_package_readme(project_root, package_root, approval_report), encoding="utf-8")


def build_package_readme(project_root: Path, package_root: Path, approval_report: dict[str, Any]) -> str:
    lines = [
        "# P5-B 正式论文包骨架",
        "",
        "本目录是正式 paper package 的结构入口。本节点只创建目录和 manifest，不生成最终 PDF、docx 或正式正文。",
        "",
        f"- Source approval: `{approval_report.get('source_preflight')}`",
        f"- Package root: `{relative_or_absolute(package_root, project_root)}`",
        "- Formal state write: `false`",
        "- Final output write: `false`",
        "",
        "## 目录",
        "",
    ]
    for spec in PACKAGE_SECTION_SPECS:
        lines.append(f"- `{spec['directory_name']}/`：{spec['label']}")
    return "\n".join(lines) + "\n"


def write_formal_paper_package_manifest_outputs(
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
        "# P5-B 正式 paper package manifest",
        "",
        f"- Status: `{report.get('status')}`",
        f"- Can build package: `{str(report.get('can_build_package')).lower()}`",
        f"- Package root: `{report.get('package_root')}`",
        "- 本命令写正式层：否",
        "- 本命令生成最终 PDF/docx/正文：否",
        "",
        "## 包结构",
        "",
    ]
    sections = report.get("package_sections") or []
    if sections:
        for section in sections:
            lines.append(f"- `{section['category']}` -> `{section['directory']}`：{section['label']}")
    else:
        lines.append("- 未生成包结构。")
    blockers = report.get("blocking_reasons") or []
    if blockers:
        lines.extend(["", "## 阻断原因", ""])
        lines.extend(f"- `{reason}`" for reason in blockers)
    lines.extend(
        [
            "",
            "## 下一步",
            "",
            f"- `{report.get('next_action', {}).get('id')}`：{report.get('next_action', {}).get('description')}",
        ]
    )
    return "\n".join(lines) + "\n"


def build_agent_team_schedule(ready: bool) -> dict[str, Any]:
    return {
        "call_when": "after_p5a_human_approval_before_package_build",
        "called_agents": ["ManuscriptAgent", "LiteratureAgent", "MethodAgent", "ExecutionAgent", "VerifierAgent"],
        "recall_when": "after_formal_package_manifest_written",
        "next_call_when": "before_pdf_or_docx_export_preflight",
        "integration_owner": "MainAgent",
        "boundary": (
            "本节点只组织正式包骨架；各 Agent 后续补齐章节、文献、方法、结果和复现材料，"
            "最终 PDF/docx 由独立导出节点处理。"
        ),
        "ready": ready,
    }


def build_next_action(ready: bool) -> dict[str, str]:
    if ready:
        return {
            "id": "assemble_formal_manuscript_sources",
            "label": "装配正式论文源文件",
            "description": "读取正式包 manifest，开始把已批准的章节、文献、方法、结果和复现说明装配为正式源文件。",
        }
    return {
        "id": "fix_p5a_approval",
        "label": "修复 P5-A 批准账本",
        "description": "先让批准报告和 state/product/writeback_approvals.json 中的正式批准记录一致，再生成包骨架。",
    }


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
