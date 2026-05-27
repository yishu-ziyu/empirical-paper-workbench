from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from workbench.paper_package import relative_or_absolute
from workbench.paper_revision_round import diff_formal_state, snapshot_formal_state


def build_manuscript_section_semantic_review(
    project_root: Path,
    draft_expansion_report: dict[str, Any],
    draft_expansion_report_path: Path,
    *,
    target_sections: list[str],
    formal_state_before: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    before = formal_state_before or snapshot_formal_state(project_root)
    expansion_by_section = {
        section.get("section"): section
        for section in draft_expansion_report.get("sections", [])
        if section.get("section")
    }
    sections = [
        review_section(project_root, section_name, expansion_by_section.get(section_name))
        for section_name in target_sections
    ]
    after = snapshot_formal_state(project_root)
    summary = build_summary(sections)
    status = "semantic_review_passed" if summary["passed"] and not summary["needs_revision"] else "semantic_review_needs_revision"
    return {
        "schema_version": "p6.manuscript_section_semantic_review.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "draft_layer_only": True,
        "formal_writeback_allowed": False,
        "source_draft_expansion_report": relative_or_absolute(draft_expansion_report_path, project_root),
        "summary": summary,
        "sections": sections,
        "agent_team_schedule": {
            "call_when": "before_section_semantic_review",
            "called_agents": ["VerifierAgent", "ManuscriptAgent"],
            "recall_when": "after_semantic_review_written",
            "next_call_when": "before_expanding_next_section_or_formal_preflight",
            "boundary": "VerifierAgent 只读核验章节论断；ManuscriptAgent 只在后续修订节点接收反馈。",
        },
        "formal_state_guard": diff_formal_state(before, after),
    }


def review_section(project_root: Path, section_name: str, expansion: dict[str, Any] | None) -> dict[str, Any]:
    if expansion is None:
        return blocked_section(section_name, "draft_expansion_missing")
    if expansion.get("status") != "section_draft_expanded":
        return blocked_section(section_name, "section_not_expanded", expansion.get("path"))

    section_path_value = expansion.get("path")
    section_path = project_root / str(section_path_value) if section_path_value else None
    text = section_path.read_text(encoding="utf-8") if section_path and section_path.exists() else ""
    consumed = expansion.get("consumed_evidence", [])
    checks = [
        check("section_file_exists", bool(section_path and section_path.exists()), "章节草案文件必须存在。"),
        check("section_declares_draft_layer", "Draft layer: `true`" in text, "章节必须显式留在草案层。"),
        check("section_blocks_formal_writeback", "Final paper write: `false`" in text, "章节不得声明可写入正式层。"),
        check_consumed_evidence_declared(text, consumed),
        check_core_claim_grounded(text, consumed),
    ]
    failed = [item for item in checks if item["status"] != "passed"]
    verdict = "needs_revision" if failed else "passed"
    return {
        "section": section_name,
        "path": section_path_value,
        "verdict": verdict,
        "checks": checks,
        "consumed_evidence": consumed,
        "next_action": build_next_action(verdict, failed),
    }


def blocked_section(section_name: str, reason: str, path: str | None = None) -> dict[str, Any]:
    return {
        "section": section_name,
        "path": path,
        "verdict": "needs_revision",
        "checks": [check(reason, False, "章节扩写记录不足，不能进入语义核验。")],
        "consumed_evidence": [],
        "next_action": {"id": "rerun_section_draft_expansion", "reason": reason},
    }


def check(check_id: str, passed: bool, rule: str) -> dict[str, str]:
    return {
        "id": check_id,
        "status": "passed" if passed else "failed",
        "rule": rule,
    }


def check_consumed_evidence_declared(text: str, consumed: list[dict[str, Any]]) -> dict[str, Any]:
    missing = [
        item.get("evidence_id")
        for item in consumed
        if item.get("evidence_id") and str(item.get("evidence_id")) not in text
    ]
    result = check(
        "consumed_evidence_declared",
        bool(consumed) and not missing,
        "每个 consumed evidence id 必须出现在章节的已消费证据区。",
    )
    result["missing_evidence_ids"] = missing
    return result


def check_core_claim_grounded(text: str, consumed: list[dict[str, Any]]) -> dict[str, Any]:
    evidence_ids = {item.get("evidence_id") for item in consumed}
    required = {"main_regression_table", "approved_findings", "coefficient_interpretation"}
    has_required_evidence = required.issubset(evidence_ids)
    has_claim = "机器人暴露提高劳动力市场匹配效率" in text or "approved finding" in text
    result = check(
        "core_claim_grounded",
        has_required_evidence and has_claim,
        "核心结果论断必须同时绑定主表、approved finding 和系数解释。",
    )
    result["required_evidence_ids"] = sorted(required)
    result["claim_detected"] = has_claim
    return result


def build_next_action(verdict: str, failed_checks: list[dict[str, Any]]) -> dict[str, Any]:
    if verdict == "passed":
        return {
            "id": "continue_section_review_or_expand_next_section",
            "owner_agent": "Supervisor",
            "reason": "Main Results 已通过本轮只读语义核验，可以进入下一节扩写或更严格的审稿式复核。",
        }
    return {
        "id": "revise_section_draft",
        "owner_agent": "ManuscriptAgent",
        "reason": "章节草案存在未通过核验项。",
        "failed_checks": [item["id"] for item in failed_checks],
    }


def build_summary(sections: list[dict[str, Any]]) -> dict[str, int]:
    counts = Counter(section.get("verdict") for section in sections)
    return {
        "requested": len(sections),
        "passed": counts.get("passed", 0),
        "needs_revision": counts.get("needs_revision", 0),
    }


def write_manuscript_section_semantic_review(path: Path, report: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def build_manuscript_section_semantic_review_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# 章节语义核验报告",
        "",
        f"- 状态：`{report.get('status')}`",
        f"- 来源：`{report.get('source_draft_expansion_report')}`",
        "- 正式层写回：关闭",
        "",
        "## 章节",
        "",
    ]
    for section in report.get("sections", []):
        lines.extend(
            [
                f"### {section.get('section')}",
                "",
                f"- verdict: `{section.get('verdict')}`",
                f"- path: `{section.get('path')}`",
                "",
            ]
        )
        for item in section.get("checks", []):
            lines.append(f"- `{item.get('id')}`: `{item.get('status')}`")
        lines.extend(["", f"- next_action: `{section.get('next_action', {}).get('id')}`", ""])
    lines.extend(["## 正式层保护", "", f"- changed: `{report.get('formal_state_guard', {}).get('changed')}`"])
    return "\n".join(lines).rstrip() + "\n"


def write_manuscript_section_semantic_review_markdown(path: Path, report: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(build_manuscript_section_semantic_review_markdown(report), encoding="utf-8")
    return path
