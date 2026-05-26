from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from workbench.formal_pdf_export_preflight import EVIDENCE_REGISTRY, PLACEHOLDER_MARKERS, resolve_project_path
from workbench.paper_package import relative_or_absolute
from workbench.paper_revision_round import diff_formal_state, snapshot_formal_state


DEFAULT_SOURCE_MAP = "Results/json/formal_manuscript_source_map.json"
DEFAULT_REPORT_PATH = "Results/json/formal_section_source_draft_report.json"
DEFAULT_REVIEW_PATH = "Reviews/formal_section_source_draft.md"


def build_formal_section_source_drafts(
    project_root: Path,
    source_map_path: Path,
    *,
    output_report_path: Path,
    formal_state_before: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    before = formal_state_before or snapshot_formal_state(project_root)
    source_map, source_map_missing = load_optional_json(source_map_path)
    blocking_reasons: list[str] = []

    if source_map_missing:
        blocking_reasons.append("source_map_missing")
        return build_blocked_report(
            project_root,
            source_map_path,
            output_report_path,
            before,
            status="blocked_by_source_map",
            blocking_reasons=blocking_reasons,
        )

    if not source_map.get("can_prepare_pdf_preflight"):
        blocking_reasons.append("source_map_not_ready_for_section_drafting")

    section_sources_path = resolve_project_path(
        project_root,
        str(source_map.get("section_sources_path") or ""),
    )
    if section_sources_path is None or not section_sources_path.exists():
        blocking_reasons.append("section_sources_index_missing")
        return build_blocked_report(
            project_root,
            source_map_path,
            output_report_path,
            before,
            status="blocked_by_source_map",
            blocking_reasons=blocking_reasons,
            source_map=source_map,
        )

    section_sources_index = load_json(section_sources_path)
    sections = list(section_sources_index.get("sections") or [])
    missing_evidence = collect_missing_evidence(project_root, sections)
    if missing_evidence:
        blocking_reasons.append("required_evidence_missing")
        return build_blocked_report(
            project_root,
            source_map_path,
            output_report_path,
            before,
            status="blocked_by_missing_evidence",
            blocking_reasons=blocking_reasons,
            source_map=source_map,
            section_sources_path=section_sources_path,
            missing_evidence=missing_evidence,
        )

    updated_sections = [build_draft_section(project_root, section) for section in sections]
    write_section_draft_files(project_root, source_map_path, updated_sections)

    section_sources_index["generated_at"] = utc_now()
    section_sources_index["draft_layer_only"] = True
    section_sources_index["formal_paper_write_allowed"] = False
    section_sources_index["sections"] = updated_sections
    section_sources_path.write_text(json.dumps(section_sources_index, ensure_ascii=False, indent=2), encoding="utf-8")

    source_map["generated_at"] = utc_now()
    source_map["section_sources"] = update_source_map_sections(source_map.get("section_sources") or [], updated_sections)
    source_map_path.write_text(json.dumps(source_map, ensure_ascii=False, indent=2), encoding="utf-8")

    after = snapshot_formal_state(project_root)
    return build_ready_report(
        project_root,
        source_map_path,
        section_sources_path,
        output_report_path,
        before,
        after,
        updated_sections,
    )


def build_draft_section(project_root: Path, section: dict[str, Any]) -> dict[str, Any]:
    updated = dict(section)
    updated["status"] = "source_draft_ready"
    updated["can_write_final_paper"] = False
    updated["draft_layer_only"] = True
    updated["evidence_bindings"] = build_evidence_bindings(project_root, section.get("evidence_requirements") or [])
    return updated


def build_evidence_bindings(project_root: Path, evidence_requirements: list[str]) -> list[dict[str, Any]]:
    bindings: list[dict[str, Any]] = []
    for evidence_id in evidence_requirements:
        candidate_paths = EVIDENCE_REGISTRY.get(str(evidence_id), [f"Results/json/{evidence_id}.json"])
        existing_paths = [path for path in candidate_paths if (project_root / path).exists()]
        bindings.append(
            {
                "id": str(evidence_id),
                "candidate_paths": candidate_paths,
                "existing_paths": existing_paths,
                "status": "bound" if existing_paths else "missing",
            }
        )
    return bindings


def collect_missing_evidence(project_root: Path, sections: list[dict[str, Any]]) -> list[dict[str, Any]]:
    missing: dict[str, set[str]] = {}
    for section in sections:
        for binding in build_evidence_bindings(project_root, section.get("evidence_requirements") or []):
            if binding["existing_paths"]:
                continue
            missing.setdefault(binding["id"], set()).add(str(section.get("section") or "unknown_section"))
    return [
        {
            "id": evidence_id,
            "candidate_paths": EVIDENCE_REGISTRY.get(evidence_id, [f"Results/json/{evidence_id}.json"]),
            "required_by_sections": sorted(section_names),
        }
        for evidence_id, section_names in sorted(missing.items())
    ]


def write_section_draft_files(project_root: Path, source_map_path: Path, sections: list[dict[str, Any]]) -> None:
    for section in sections:
        path = resolve_project_path(project_root, str(section.get("source_path") or ""))
        if path is None:
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(build_section_draft_markdown(project_root, source_map_path, section), encoding="utf-8")


def build_section_draft_markdown(project_root: Path, source_map_path: Path, section: dict[str, Any]) -> str:
    evidence_lines: list[str] = []
    for binding in section.get("evidence_bindings") or []:
        existing = ", ".join(f"`{path}`" for path in binding.get("existing_paths") or [])
        evidence_lines.append(f"- `{binding['id']}` -> {existing}")

    review_points = build_review_points(section)
    return (
        f"# {section['section']}\n\n"
        "- Status: `source_draft_ready`\n"
        f"- Agent: `{section.get('agent')}`\n"
        f"- Target length: `{section.get('target_length')}`\n"
        f"- Source map: `{relative_or_absolute(source_map_path, project_root)}`\n"
        "- Draft layer: `true`\n"
        "- Final paper write: `false`\n\n"
        "## 本节任务\n\n"
        f"{section.get('purpose') or '围绕已绑定证据整理本节写作素材。'}\n\n"
        "## 已绑定证据\n\n"
        f"{chr(10).join(evidence_lines)}\n\n"
        "## 章节源草案\n\n"
        "本节已经绑定可追溯证据，下一步可以由对应 Agent 按目标长度扩写为候选论文段落。"
        "正式写回前仍保留人工审阅入口。\n\n"
        "## 审阅事项\n\n"
        f"{chr(10).join(review_points)}\n"
    )


def build_review_points(section: dict[str, Any]) -> list[str]:
    section_name = str(section.get("section") or "")
    if section_name == "Abstract":
        return ["- 压缩为目标摘要长度。", "- 只引用已批准 finding 和已验证文献。"]
    if section_name == "References":
        return ["- 只从 verified bibliography 和 citation verification log 生成引用清单。"]
    return [
        "- 检查本节证据是否覆盖写作目标。",
        "- 扩写时保留数据、方法、结果和文献来源的可追溯路径。",
    ]


def update_source_map_sections(source_map_sections: list[dict[str, Any]], updated_sections: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_name = {section.get("section"): section for section in updated_sections}
    merged: list[dict[str, Any]] = []
    for section in source_map_sections:
        updated = dict(section)
        matched = by_name.get(section.get("section"))
        if matched:
            updated["status"] = "source_draft_ready"
            updated["evidence_bindings"] = matched.get("evidence_bindings", [])
            updated["can_write_final_paper"] = False
        merged.append(updated)
    return merged


def build_ready_report(
    project_root: Path,
    source_map_path: Path,
    section_sources_path: Path,
    output_report_path: Path,
    before: dict[str, dict[str, Any]],
    after: dict[str, dict[str, Any]],
    sections: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "schema_version": "p5.formal_section_source_drafts.v1",
        "generated_at": utc_now(),
        "source_map": relative_or_absolute(source_map_path, project_root),
        "section_sources_path": relative_or_absolute(section_sources_path, project_root),
        "output_report": relative_or_absolute(output_report_path, project_root),
        "status": "section_source_drafts_ready",
        "blocking_reasons": [],
        "drafted_sections": len(sections),
        "section_drafts": build_section_draft_summaries(sections),
        "this_command_wrote_formal_state": False,
        "this_command_wrote_final_outputs": False,
        "final_outputs_written": [],
        "formal_state_guard": diff_formal_state(before, after),
        "agent_team_schedule": build_agent_team_schedule(True),
        "next_action": {
            "id": "rerun_formal_pdf_export_preflight",
            "label": "重新运行 PDF 导出预检",
            "description": "章节源草案已经绑定证据，下一步检查是否可以进入 PDF 候选渲染。",
        },
        "write_boundary": "本节点只写章节源草案和对应报告；不写正式层状态，不生成最终 PDF/docx。",
    }


def build_blocked_report(
    project_root: Path,
    source_map_path: Path,
    output_report_path: Path,
    before: dict[str, dict[str, Any]],
    *,
    status: str,
    blocking_reasons: list[str],
    source_map: dict[str, Any] | None = None,
    section_sources_path: Path | None = None,
    missing_evidence: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    after = snapshot_formal_state(project_root)
    return {
        "schema_version": "p5.formal_section_source_drafts.v1",
        "generated_at": utc_now(),
        "source_map": relative_or_absolute(source_map_path, project_root),
        "section_sources_path": (
            relative_or_absolute(section_sources_path, project_root)
            if section_sources_path
            else source_map.get("section_sources_path")
            if source_map
            else None
        ),
        "output_report": relative_or_absolute(output_report_path, project_root),
        "status": status,
        "blocking_reasons": sorted(set(blocking_reasons)),
        "drafted_sections": 0,
        "missing_evidence": missing_evidence or [],
        "section_drafts": [],
        "this_command_wrote_formal_state": False,
        "this_command_wrote_final_outputs": False,
        "final_outputs_written": [],
        "formal_state_guard": diff_formal_state(before, after),
        "agent_team_schedule": build_agent_team_schedule(False),
        "next_action": {
            "id": "resolve_section_source_draft_blockers",
            "label": "补齐章节源草案阻断项",
            "description": "先补齐 source map、section source index 或缺失证据，再生成章节源草案。",
        },
        "write_boundary": "本节点只写章节源草案和对应报告；不写正式层状态，不生成最终 PDF/docx。",
    }


def build_section_draft_summaries(sections: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "section": section.get("section"),
            "source_path": section.get("source_path"),
            "status": section.get("status"),
            "agent": section.get("agent"),
            "target_length": section.get("target_length"),
            "evidence_bindings": section.get("evidence_bindings", []),
        }
        for section in sections
    ]


def build_agent_team_schedule(ready: bool) -> dict[str, Any]:
    return {
        "call_when": "after_evidence_materialization_before_pdf_preflight",
        "called_agents": [
            "ManuscriptAgent",
            "LiteratureAgent",
            "MethodAgent",
            "DataAgent",
            "ExecutionAgent",
            "ReviewerAgent",
            "VerifierAgent",
        ],
        "recall_when": "after_section_source_draft_report_written",
        "next_call_when": "before_pdf_candidate_render",
        "integration_owner": "MainAgent",
        "boundary": "Agent Team 只把证据绑定到章节源草案；正式论文层和最终导出仍由后续人工确认节点处理。",
        "ready": ready,
    }


def write_formal_section_source_draft_outputs(
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
        "# P5-E2d 章节源草案",
        "",
        f"- Status: `{report.get('status')}`",
        f"- Drafted sections: `{report.get('drafted_sections')}`",
        f"- Source map: `{report.get('source_map')}`",
        f"- Section source index: `{report.get('section_sources_path')}`",
        "- 正式层写回：未发生",
        "- 最终 PDF/docx：未生成",
        "",
        "## 阻断原因",
        "",
    ]
    blockers = report.get("blocking_reasons") or []
    lines.extend(f"- `{reason}`" for reason in blockers) if blockers else lines.append("- 无")

    if report.get("missing_evidence"):
        lines.extend(["", "## 缺失证据", ""])
        for evidence in report["missing_evidence"]:
            lines.append(f"- `{evidence.get('id')}`: {', '.join(evidence.get('required_by_sections') or [])}")

    lines.extend(["", "## 章节源草案", ""])
    drafts = report.get("section_drafts") or []
    if drafts:
        for draft in drafts:
            lines.append(f"- `{draft.get('section')}` -> `{draft.get('source_path')}` ({draft.get('agent')})")
    else:
        lines.append("- 未生成章节源草案。")

    lines.extend(
        [
            "",
            "## 下一步",
            "",
            f"- `{report.get('next_action', {}).get('id')}`：{report.get('next_action', {}).get('description')}",
        ]
    )
    return "\n".join(lines) + "\n"


def load_optional_json(path: Path) -> tuple[dict[str, Any], bool]:
    if not path.exists():
        return {}, True
    return load_json(path), False


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
