from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from Product.backend.product_control_phase_service import project_summary
from Product.backend.registry import get_project_by_id
from Program.workbench.paper_quality import build_paper_quality_report, write_paper_quality_report


QUALITY_REPORT_PATH = Path("Results/json/course_paper_quality_report.json")
FINAL_PDF_REPORT_PATH = Path("Results/json/parent_education_wage_final_pdf_export.json")
P15_PATH = Path("Results/json/parent_education_wage_p15_draft_export_package.json")


def run_project_product_control_course_paper_quality(
    product_root: Path,
    repo_root: Path,
    project_id: str,
) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    draft = resolve_current_draft(project_root, project)
    report = build_paper_quality_report(project_root, draft, profile="general_working_paper")
    report["review_summary"] = build_review_summary(report)
    write_paper_quality_report(project_root, report, project_root / quality_report_path_for_project(project))
    return attach_product_fields(project, project_root, project_id, report)


def get_project_product_control_course_paper_quality(
    product_root: Path,
    repo_root: Path,
    project_id: str,
) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    report_path = project_root / quality_report_path_for_project(project)
    if report_path.exists():
        report = json.loads(report_path.read_text(encoding="utf-8"))
    else:
        draft = resolve_current_draft(project_root, project)
        report = {
            "schema_version": "p4.paper_quality.v1",
            "status": "course_paper_quality_not_run",
            "draft_path": relative_or_absolute(draft, project_root),
            "verdict": ["review_report_not_run"],
            "recommended_next_tasks": [
                {
                    "id": "run_course_paper_review_report",
                    "agent": "ReviewerAgent",
                    "reason": "PDF 导出不等于课程论文级交付，必须先生成论文审阅报告。",
                    "inputs": [relative_or_absolute(draft, project_root)],
                }
            ],
        }
    return attach_product_fields(project, project_root, project_id, report)


def quality_report_path_for_project(project: dict[str, Any]) -> Path:
    prefix = project.get("artifact_prefix")
    if prefix:
        return Path(f"Results/json/{prefix}_course_paper_quality_report.json")
    return QUALITY_REPORT_PATH


def final_pdf_report_path_for_project(project: dict[str, Any]) -> Path:
    prefix = project.get("artifact_prefix")
    if prefix:
        return Path(f"Results/json/{prefix}_pdf_preflight.json")
    return FINAL_PDF_REPORT_PATH


def draft_package_path_for_project(project: dict[str, Any]) -> Path:
    prefix = project.get("artifact_prefix")
    if prefix:
        return Path(f"Results/json/{prefix}_paper_assembly.json")
    return P15_PATH


def resolve_current_draft(project_root: Path, project: dict[str, Any]) -> Path:
    final_pdf = load_optional_json(project_root / final_pdf_report_path_for_project(project))
    source = final_pdf.get("source_markdown") or final_pdf.get("paper_source")
    if source:
        path = project_root / source
        if path.exists():
            return path

    p15 = load_optional_json(project_root / draft_package_path_for_project(project))
    draft = p15.get("paper_draft_markdown") or p15.get("paper_path")
    if draft:
        path = project_root / draft
        if path.exists():
            return path

    return project_root / "Manuscripts" / "generated" / "paper_draft.md"


def attach_product_fields(
    project: dict[str, Any],
    project_root: Path,
    project_id: str,
    report: dict[str, Any],
) -> dict[str, Any]:
    verdict = report.get("verdict") or []
    review_summary = report.get("review_summary")
    if not isinstance(review_summary, dict):
        review_summary = build_review_summary(report)
    return {
        **report,
        "review_summary": review_summary,
        "status": "course_paper_quality_ready_for_review"
        if verdict == ["ready_for_review"]
        else report.get("status", "course_paper_quality_needs_revision"),
        "project": project_summary(project, project_root),
        "can_claim_course_paper_ready": verdict == ["ready_for_review"],
        "quality_report_path": quality_report_path_for_project(project).as_posix(),
        "refresh_endpoint": f"/api/v1/projects/{project_id}/product-control/course-paper-quality",
        "run_endpoint": f"/api/v1/projects/{project_id}/product-control/course-paper-quality",
    }


def build_review_summary(report: dict[str, Any]) -> dict[str, Any]:
    verdict = report.get("verdict") or []
    word_count = report.get("word_count") if isinstance(report.get("word_count"), dict) else {}
    thresholds = word_count.get("thresholds") if isinstance(word_count.get("thresholds"), dict) else {}
    current_chinese_chars = int(word_count.get("main_text_chinese_chars") or 0)
    current_english_words = int(word_count.get("main_text_words") or 0)
    target_chinese_chars = str(thresholds.get("chinese_target_chars") or "12000-18000")
    min_chinese_chars = int(thresholds.get("chinese_min_chars") or 10000)

    section_gaps = build_section_gaps(report)
    evidence_issues = build_evidence_issues(report)
    top_priorities = build_top_priorities(report, section_gaps, evidence_issues)
    decision = "ready_for_review" if verdict == ["ready_for_review"] else "needs_revision"
    headline = (
        "论文已形成可审阅版本，下一步进入人工终审。"
        if decision == "ready_for_review"
        else f"当前稿约 {current_chinese_chars} 个中文字符，距离最低完整稿标准还差约 {max(min_chinese_chars - current_chinese_chars, 0)} 个字符。"
    )
    return {
        "decision": decision,
        "headline": headline,
        "current_chinese_chars": current_chinese_chars,
        "current_english_words": current_english_words,
        "target_chinese_chars": target_chinese_chars,
        "top_priorities": top_priorities,
        "section_gaps": section_gaps,
        "evidence_issues": evidence_issues,
        "source_paths": {
            "draft": report.get("draft_path"),
            "results": (report.get("evidence_integrity_checks") or {}).get("results_path")
            if isinstance(report.get("evidence_integrity_checks"), dict)
            else None,
            "method": (report.get("method_gate_checks") or {}).get("path")
            if isinstance(report.get("method_gate_checks"), dict)
            else None,
        },
    }


def build_section_gaps(report: dict[str, Any]) -> list[dict[str, Any]]:
    checks = report.get("section_length_checks") if isinstance(report.get("section_length_checks"), dict) else {}
    sections = checks.get("sections") if isinstance(checks.get("sections"), dict) else {}
    gaps: list[dict[str, Any]] = []
    for section, payload in sections.items():
        if not isinstance(payload, dict):
            continue
        status = payload.get("status")
        if status not in {"missing", "too_short", "too_long"}:
            continue
        gaps.append(
            {
                "section": section,
                "status": status,
                "current_chinese_chars": int(payload.get("chinese_char_count") or 0),
                "current_english_words": int(payload.get("english_word_count") or 0),
                "target_chinese_chars": payload.get("target_chinese_chars"),
                "target_english_words": payload.get("target_english_words"),
            }
        )
    return gaps


def build_evidence_issues(report: dict[str, Any]) -> list[dict[str, Any]]:
    checks = report.get("evidence_integrity_checks") if isinstance(report.get("evidence_integrity_checks"), dict) else {}
    issues = checks.get("issues") if isinstance(checks.get("issues"), list) else []
    return [
        {
            "id": str(issue.get("rule_id") or "evidence_issue"),
            "severity": str(issue.get("severity") or "Major"),
            "message": str(issue.get("message") or ""),
            "fix": str(issue.get("fix") or ""),
        }
        for issue in issues
        if isinstance(issue, dict)
    ]


def build_top_priorities(
    report: dict[str, Any],
    section_gaps: list[dict[str, Any]],
    evidence_issues: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    priorities: list[dict[str, Any]] = []
    verdict = report.get("verdict") or []
    if "too_thin" in verdict or "missing_sections" in verdict or section_gaps:
        priorities.append(
            {
                "id": "expand_core_sections",
                "title": "扩写核心章节",
                "detail": f"当前有 {len(section_gaps)} 个章节缺失、过短或过长，先补引言、文献、数据、方法、主结果和稳健性段落。",
                "owner": "ManuscriptAgent",
            }
        )
    if evidence_issues:
        priorities.append(
            {
                "id": "repair_evidence_chain",
                "title": "修复证据链",
                "detail": "把正文中的结论逐条绑定到结果包、方法文件和可复现输出。",
                "owner": "VerifierAgent",
            }
        )
    citation_checks = report.get("citation_checks") if isinstance(report.get("citation_checks"), dict) else {}
    if citation_checks.get("status") != "passed":
        priorities.append(
            {
                "id": "complete_literature_package",
                "title": "补齐文献与贡献矩阵",
                "detail": "需要足够的核验文献、相邻研究和贡献定位，否则文章只能算草稿。",
                "owner": "LiteratureAgent",
            }
        )
    revision_checks = report.get("revision_checks") if isinstance(report.get("revision_checks"), dict) else {}
    if revision_checks.get("status") != "passed":
        priorities.append(
            {
                "id": "record_review_loop",
                "title": "形成修订记录",
                "detail": "保留审稿意见、修改记录和下一轮生成依据，避免只产出一次性 PDF。",
                "owner": "ReviewerAgent",
            }
        )
    return priorities


def load_optional_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def relative_or_absolute(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path)
