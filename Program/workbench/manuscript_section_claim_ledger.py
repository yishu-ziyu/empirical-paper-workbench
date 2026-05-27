from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from workbench.paper_package import relative_or_absolute
from workbench.paper_revision_round import diff_formal_state, snapshot_formal_state


def build_manuscript_section_claim_ledger(
    project_root: Path,
    semantic_review: dict[str, Any],
    semantic_review_path: Path,
    *,
    target_sections: list[str],
    formal_state_before: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    before = formal_state_before or snapshot_formal_state(project_root)
    review_by_section = {
        section.get("section"): section
        for section in semantic_review.get("sections", [])
        if section.get("section")
    }
    approved_findings = load_approved_findings(project_root)
    sections = [
        build_section_claims(project_root, section_name, review_by_section.get(section_name), approved_findings)
        for section_name in target_sections
    ]
    after = snapshot_formal_state(project_root)
    summary = build_summary(sections)
    return {
        "schema_version": "p6.manuscript_section_claim_ledger.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "claim_ledger_ready" if summary["claims"] and not summary["needs_revision"] else "claim_ledger_needs_revision",
        "draft_layer_only": True,
        "formal_writeback_allowed": False,
        "source_semantic_review": relative_or_absolute(semantic_review_path, project_root),
        "summary": summary,
        "sections": sections,
        "agent_team_schedule": {
            "call_when": "after_section_semantic_review_passed",
            "called_agents": ["VerifierAgent", "ManuscriptAgent"],
            "recall_when": "before_next_section_expansion_or_pdf_preflight",
            "boundary": "VerifierAgent 复核 claim ledger；ManuscriptAgent 后续只消费 ready_for_next_review 的草案论断。",
        },
        "formal_state_guard": diff_formal_state(before, after),
    }


def build_section_claims(
    project_root: Path,
    section_name: str,
    section_review: dict[str, Any] | None,
    approved_findings: list[dict[str, Any]],
) -> dict[str, Any]:
    if section_review is None:
        return blocked_section(section_name, "semantic_review_missing")
    if section_review.get("verdict") != "passed":
        return blocked_section(section_name, "semantic_review_not_passed", section_review.get("path"))

    path_value = section_review.get("path")
    section_path = project_root / str(path_value) if path_value else None
    section_text = section_path.read_text(encoding="utf-8") if section_path and section_path.exists() else ""
    evidence_ids = sorted(
        {
            str(item.get("evidence_id"))
            for item in section_review.get("consumed_evidence", [])
            if item.get("evidence_id")
        }
    )
    claims = [
        build_claim_record(section_name, finding, evidence_ids)
        for finding in approved_findings
        if finding_claim(finding) and finding_claim(finding) in section_text
    ]
    missing_reasons = [] if claims else ["no_approved_finding_claim_detected_in_section"]
    return {
        "section": section_name,
        "path": path_value,
        "status": "claim_ledger_ready" if claims else "needs_revision",
        "claims": claims,
        "missing_reasons": missing_reasons,
    }


def blocked_section(section_name: str, reason: str, path: str | None = None) -> dict[str, Any]:
    return {
        "section": section_name,
        "path": path,
        "status": "needs_revision",
        "claims": [],
        "missing_reasons": [reason],
    }


def build_claim_record(section_name: str, finding: dict[str, Any], evidence_ids: list[str]) -> dict[str, Any]:
    return {
        "claim_id": f"{section_slug(section_name)}::{finding_id(finding)}",
        "section": section_name,
        "claim_text": finding_claim(finding),
        "source_finding_id": finding_id(finding),
        "source_finding_status": finding.get("status") or finding.get("review_status"),
        "source_evidence_level": finding.get("evidence_level"),
        "bound_evidence_ids": evidence_ids,
        "review_status": "ready_for_next_review",
        "next_action": {
            "id": "keep_claim_in_draft_review_queue",
            "owner_agent": "VerifierAgent",
            "reason": "论断已在章节草案中出现，并绑定到已消费证据；下一步进入更严格审稿或相邻章节一致性检查。",
        },
    }


def load_approved_findings(project_root: Path) -> list[dict[str, Any]]:
    path = project_root / "Results" / "json" / "approved_findings.json"
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    findings = payload.get("findings") if isinstance(payload, dict) else []
    return [
        item
        for item in findings
        if isinstance(item, dict) and (item.get("status") == "approved" or item.get("review_status") == "approved")
    ]


def finding_claim(finding: dict[str, Any]) -> str:
    return str(finding.get("claim") or finding.get("claim_text") or "").strip()


def finding_id(finding: dict[str, Any]) -> str:
    return str(finding.get("id") or finding.get("finding_id") or "approved_finding")


def section_slug(value: str) -> str:
    return "-".join(value.lower().split())


def build_summary(sections: list[dict[str, Any]]) -> dict[str, int]:
    counts = Counter(section.get("status") for section in sections)
    return {
        "sections": len(sections),
        "claims": sum(len(section.get("claims", [])) for section in sections),
        "needs_revision": counts.get("needs_revision", 0),
    }


def write_manuscript_section_claim_ledger(path: Path, report: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def build_manuscript_section_claim_ledger_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# 章节论断账本",
        "",
        f"- 状态：`{report.get('status')}`",
        f"- 来源：`{report.get('source_semantic_review')}`",
        "- 正式层写回：关闭",
        "",
    ]
    for section in report.get("sections", []):
        lines.extend([f"## {section.get('section')}", "", f"- 状态：`{section.get('status')}`"])
        for claim in section.get("claims", []):
            lines.extend(
                [
                    "",
                    f"### {claim.get('claim_id')}",
                    "",
                    f"- 论断：{claim.get('claim_text')}",
                    f"- 来源 finding：`{claim.get('source_finding_id')}`",
                    f"- 证据：`{', '.join(claim.get('bound_evidence_ids', []))}`",
                    f"- 下一步：`{claim.get('next_action', {}).get('id')}`",
                ]
            )
        for reason in section.get("missing_reasons", []):
            lines.append(f"- 缺口：`{reason}`")
        lines.append("")
    lines.extend(["## 正式层保护", "", f"- changed: `{report.get('formal_state_guard', {}).get('changed')}`"])
    return "\n".join(lines).rstrip() + "\n"


def write_manuscript_section_claim_ledger_markdown(path: Path, report: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(build_manuscript_section_claim_ledger_markdown(report), encoding="utf-8")
    return path
