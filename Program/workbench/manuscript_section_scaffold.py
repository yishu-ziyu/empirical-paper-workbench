from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from workbench.paper_package import relative_or_absolute
from workbench.paper_revision_round import diff_formal_state, snapshot_formal_state


def build_manuscript_section_scaffold_report(
    project_root: Path,
    revision_round: dict[str, Any],
    revision_round_path: Path,
    *,
    formal_state_before: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    before = formal_state_before or snapshot_formal_state(project_root)
    section_scaffolds = write_manuscript_section_scaffolds(project_root, revision_round, revision_round_path)
    after = snapshot_formal_state(project_root)
    return {
        "schema_version": "p6.manuscript_section_scaffold.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "section_scaffolds_ready",
        "draft_layer_only": True,
        "formal_writeback_allowed": False,
        "source_revision_round": relative_or_absolute(revision_round_path, project_root),
        "section_count": len(section_scaffolds),
        "section_scaffolds": section_scaffolds,
        "agent_team_schedule": {
            "call_when": "after_section_scaffold_manifest_written",
            "called_agents": ["ManuscriptAgent"],
            "recall_when": "after_section_draft_files_written",
            "next_call_when": "before_evidence_bound_section_drafting",
            "boundary": "章节入口已准备；下一步由 ManuscriptAgent 按证据清单扩写草案正文。",
        },
        "formal_state_guard": diff_formal_state(before, after),
    }


def write_manuscript_section_scaffolds(
    project_root: Path,
    revision_round: dict[str, Any],
    revision_round_path: Path,
) -> list[dict[str, Any]]:
    section_scaffolds: list[dict[str, Any]] = []
    for work_order in revision_round.get("manuscript_section_work_orders", []):
        draft_output_path = str(work_order.get("draft_output_path") or "").strip()
        section = str(work_order.get("section") or "").strip()
        if not draft_output_path or not section:
            continue
        path = project_root / draft_output_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            build_manuscript_section_scaffold_markdown(work_order, revision_round_path, project_root),
            encoding="utf-8",
        )
        section_scaffolds.append(
            {
                "section": section,
                "path": relative_or_absolute(path, project_root),
                "status": "section_scaffold_ready",
                "agent": work_order.get("agent", "ManuscriptAgent"),
                "source_work_order": work_order.get("work_order_path"),
                "required_evidence_count": len(work_order.get("required_evidence", [])),
            }
        )
    return section_scaffolds


def build_manuscript_section_scaffold_markdown(
    work_order: dict[str, Any],
    revision_round_path: Path,
    project_root: Path,
) -> str:
    section = work_order.get("section")
    lines = [
        f"# {section}",
        "",
        f"- Status: `section_scaffold_ready`",
        f"- Agent: `{work_order.get('agent', 'ManuscriptAgent')}`",
        f"- Source revision round: `{relative_or_absolute(revision_round_path, project_root)}`",
        f"- Source work order: `{work_order.get('work_order_path')}`",
        f"- Draft layer: `{str(work_order.get('draft_layer_only', True)).lower()}`",
        f"- Final paper write: `{str(work_order.get('formal_writeback_allowed', False)).lower()}`",
        f"- Product state write: `{str(work_order.get('can_write_product_state', False)).lower()}`",
        "",
        "## 本节目标",
        "",
        str(work_order.get("writing_instruction") or "").strip(),
        "",
        "## 证据清单",
        "",
    ]
    for evidence in work_order.get("required_evidence", []):
        lines.append(f"- [ ] {evidence}")
    lines.extend(
        [
            "",
            "## 验收条件",
            "",
        ]
    )
    for item in work_order.get("verification", {}).get("required_before_completion", []):
        lines.append(f"- [ ] {item}")
    lines.extend(
        [
            "",
            "## 草案正文",
            "",
            "<!-- ManuscriptAgent 在这里写入证据绑定后的章节草案。 -->",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def write_manuscript_section_scaffold_report(path: Path, report: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def build_manuscript_section_scaffold_review(report: dict[str, Any]) -> str:
    lines = [
        "# 章节草案入口",
        "",
        f"- 状态：`{report.get('status')}`",
        f"- 来源：`{report.get('source_revision_round')}`",
        f"- 章节数：{report.get('section_count')}",
        "- 正式层写回：关闭",
        "",
        "## Agent Team 调用节奏",
        "",
    ]
    schedule = report.get("agent_team_schedule", {})
    for key in ["call_when", "called_agents", "recall_when", "next_call_when", "boundary"]:
        lines.append(f"- {key}: {schedule.get(key)}")
    lines.extend(["", "## 章节入口", ""])
    for item in report.get("section_scaffolds", []):
        lines.extend(
            [
                f"### {item.get('section')}",
                "",
                f"- 文件：`{item.get('path')}`",
                f"- 状态：`{item.get('status')}`",
                f"- 证据项：{item.get('required_evidence_count')}",
                f"- 工单：`{item.get('source_work_order')}`",
                "",
            ]
        )
    lines.extend(
        [
            "## 正式层保护",
            "",
            f"- changed: `{report.get('formal_state_guard', {}).get('changed')}`",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def write_manuscript_section_scaffold_review(path: Path, report: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(build_manuscript_section_scaffold_review(report), encoding="utf-8")
    return path
