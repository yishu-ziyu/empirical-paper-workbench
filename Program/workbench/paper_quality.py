from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REQUIRED_SECTIONS = [
    "Abstract",
    "Introduction",
    "Literature and Contribution",
    "Institutional Background / Theory / Context",
    "Data and Measurement",
    "Empirical Strategy",
    "Main Results",
    "Robustness / Mechanisms / Heterogeneity",
    "Conclusion",
    "References",
]


SECTION_ALIASES = {
    "Abstract": ["abstract", "摘要"],
    "Introduction": ["introduction", "引言", "介绍"],
    "Literature and Contribution": ["literature", "contribution", "文献", "贡献"],
    "Institutional Background / Theory / Context": ["background", "theory", "context", "背景", "理论", "制度"],
    "Data and Measurement": ["data", "measurement", "变量", "数据"],
    "Empirical Strategy": ["empirical strategy", "identification", "research design", "识别", "实证策略", "研究设计"],
    "Main Results": ["results", "main results", "结果", "主结果"],
    "Robustness / Mechanisms / Heterogeneity": ["robustness", "mechanism", "heterogeneity", "稳健", "机制", "异质"],
    "Conclusion": ["conclusion", "结论"],
    "References": ["references", "参考文献", "bibliography"],
}


SECTION_LENGTH_STANDARDS = {
    "Abstract": {
        "min_english_words": 100,
        "max_english_words": 180,
        "min_chinese_chars": 180,
        "max_chinese_chars": 300,
    },
    "Introduction": {
        "min_english_words": 1800,
        "max_english_words": 3000,
        "min_chinese_chars": 2800,
        "max_chinese_chars": 5000,
    },
    "Literature and Contribution": {
        "min_english_words": 1000,
        "max_english_words": 1800,
        "min_chinese_chars": 1500,
        "max_chinese_chars": 3000,
    },
    "Institutional Background / Theory / Context": {
        "min_english_words": 800,
        "max_english_words": 1500,
        "min_chinese_chars": 1200,
        "max_chinese_chars": 2500,
    },
    "Data and Measurement": {
        "min_english_words": 800,
        "max_english_words": 1500,
        "min_chinese_chars": 1200,
        "max_chinese_chars": 2500,
    },
    "Empirical Strategy": {
        "min_english_words": 1200,
        "max_english_words": 2000,
        "min_chinese_chars": 1800,
        "max_chinese_chars": 3500,
    },
    "Main Results": {
        "min_english_words": 2000,
        "max_english_words": 3500,
        "min_chinese_chars": 3000,
        "max_chinese_chars": 6000,
    },
    "Robustness / Mechanisms / Heterogeneity": {
        "min_english_words": 1500,
        "max_english_words": 3000,
        "min_chinese_chars": 2200,
        "max_chinese_chars": 5000,
    },
    "Conclusion": {
        "min_english_words": 500,
        "max_english_words": 800,
        "min_chinese_chars": 800,
        "max_chinese_chars": 1300,
    },
}


@dataclass(frozen=True)
class LiteraturePackage:
    verified_bibliography: Path | None
    contribution_matrix: Path | None
    verified_count: int
    closest_or_method_count: int


def build_paper_quality_report(
    project_root: Path,
    draft_path: Path | None = None,
    profile: str = "general_working_paper",
) -> dict[str, Any]:
    draft = resolve_draft_path(project_root, draft_path)
    draft_text = draft.read_text(encoding="utf-8") if draft.exists() else ""
    word_count = count_words(draft_text)
    format_checks = build_format_checks(draft_text, profile)
    section_checks = build_section_checks(draft_text)
    section_length_checks = build_section_length_checks(draft_text, profile)
    literature = find_literature_package(project_root)
    citation_checks = build_citation_checks(literature)
    method_gate_checks = build_method_gate_checks(project_root)
    revision_checks = build_revision_checks(project_root)
    verdict = build_verdict(
        word_count,
        format_checks,
        section_checks,
        section_length_checks,
        citation_checks,
        method_gate_checks,
        revision_checks,
    )
    recommended_next_tasks = build_recommended_next_tasks(
        verdict,
        format_checks,
        section_checks,
        section_length_checks,
        citation_checks,
        method_gate_checks,
        revision_checks,
    )

    return {
        "schema_version": "p4.paper_quality.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "profile": profile,
        "draft_path": relative_or_absolute(draft, project_root),
        "word_count": word_count,
        "format_checks": format_checks,
        "section_checks": section_checks,
        "section_length_checks": section_length_checks,
        "citation_checks": citation_checks,
        "method_gate_checks": method_gate_checks,
        "revision_checks": revision_checks,
        "verdict": verdict,
        "recommended_next_tasks": recommended_next_tasks,
    }


def write_paper_quality_report(project_root: Path, report: dict[str, Any], output_path: Path | None = None) -> Path:
    output = output_path or (project_root / "Results" / "json" / "paper_quality_report.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return output


def resolve_draft_path(project_root: Path, draft_path: Path | None) -> Path:
    if draft_path is not None:
        return draft_path if draft_path.is_absolute() else project_root / draft_path
    candidates = [
        project_root / "Manuscripts" / "generated" / "cfps_robot_paper_draft.md",
        project_root / "Manuscripts" / "generated" / "paper_draft.md",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[-1]


def count_words(text: str) -> dict[str, Any]:
    units = count_text_units(text)
    return {
        "main_text_words": units["english_word_count"],
        "main_text_chinese_chars": units["chinese_char_count"],
        "approx_total_units": units["english_word_count"] + units["chinese_char_count"],
        "thresholds": {
            "english_min_words": 7000,
            "english_target_words": "9000-14000",
            "aer_like_target_pages": "30-38",
            "aer_like_upper_pages": 40,
            "chinese_min_chars": 10000,
            "chinese_target_chars": "12000-18000",
        },
    }


def count_text_units(text: str) -> dict[str, int]:
    chinese_chars = re.findall(r"[\u4e00-\u9fff]", text)
    latin_words = re.findall(r"[A-Za-z][A-Za-z0-9_'-]*", text)
    return {"english_word_count": len(latin_words), "chinese_char_count": len(chinese_chars)}


def build_format_checks(text: str, profile: str) -> dict[str, Any]:
    abstract_text = extract_section_body(text, "Abstract")
    abstract_words = len(re.findall(r"[A-Za-z][A-Za-z0-9_'-]*", abstract_text))
    abstract_chinese_chars = len(re.findall(r"[\u4e00-\u9fff]", abstract_text))
    has_jel = bool(re.search(r"(?im)^\s*(jel|jel codes?|jel classification)\s*[:：]", text))
    has_keywords = bool(re.search(r"(?im)^\s*(keywords?|关键词)\s*[:：]", text))
    has_data_availability = bool(
        re.search(r"(?im)^\s*#*\s*(data availability|data and code availability|数据可得性|数据和代码可得性)", text)
    )

    warnings: list[str] = []
    hard_errors: list[str] = []
    if abstract_words == 0 and abstract_chinese_chars == 0:
        warnings.append("missing_abstract_body")
    if not has_jel:
        warnings.append("missing_jel")
    if not has_keywords:
        warnings.append("missing_keywords")
    if not has_data_availability:
        warnings.append("missing_data_availability_statement")

    if profile == "aer_like":
        if abstract_words > 100:
            hard_errors.append("abstract_over_100_words")
        if not has_jel:
            hard_errors.append("missing_jel")
        if not has_keywords:
            hard_errors.append("missing_keywords")
        if not has_data_availability:
            hard_errors.append("missing_data_availability_statement")

    return {
        "profile": profile,
        "abstract": {
            "english_word_count": abstract_words,
            "chinese_char_count": abstract_chinese_chars,
            "aer_like_limit_words": 100,
            "status": "too_long" if profile == "aer_like" and abstract_words > 100 else "passed",
        },
        "metadata": {
            "jel": "found" if has_jel else "missing",
            "keywords": "found" if has_keywords else "missing",
            "data_availability_statement": "found" if has_data_availability else "missing",
        },
        "warnings": warnings,
        "hard_errors": hard_errors,
        "status": "blocked" if hard_errors else "passed",
    }


def extract_section_body(text: str, section: str) -> str:
    aliases = SECTION_ALIASES[section]
    lines = text.splitlines()
    start: int | None = None
    for index, line in enumerate(lines):
        stripped = line.strip()
        if not stripped.startswith("#"):
            continue
        heading = stripped.lstrip("#").strip().lower()
        if any(alias in heading for alias in aliases):
            start = index + 1
            break
    if start is None:
        return ""
    body: list[str] = []
    for line in lines[start:]:
        if line.strip().startswith("#"):
            break
        body.append(line)
    return "\n".join(body).strip()


def build_section_checks(text: str) -> dict[str, Any]:
    headings = extract_headings(text)
    present: list[str] = []
    missing: list[str] = []
    for section in REQUIRED_SECTIONS:
        if section_present(section, headings):
            present.append(section)
        else:
            missing.append(section)
    return {
        "required_sections": REQUIRED_SECTIONS,
        "present_sections": present,
        "missing_sections": missing,
        "detected_headings": headings,
        "status": "passed" if not missing else "needs_expansion",
    }


def build_section_length_checks(text: str, profile: str) -> dict[str, Any]:
    sections: dict[str, Any] = {}
    too_short_sections: list[str] = []
    too_long_sections: list[str] = []
    missing_sections: list[str] = []
    for section in REQUIRED_SECTIONS:
        if section == "References":
            sections[section] = {
                "status": "not_applicable",
                "reason": "references_are_checked_by_citation_package",
            }
            continue
        standard = section_length_standard(section, profile)
        body = extract_section_body(text, section)
        units = count_text_units(body)
        if not body:
            status = "missing"
            missing_sections.append(section)
        elif units["english_word_count"] < standard["min_english_words"] and (
            units["chinese_char_count"] < standard["min_chinese_chars"]
        ):
            status = "too_short"
            too_short_sections.append(section)
        elif units["english_word_count"] > standard["max_english_words"] or (
            units["chinese_char_count"] > standard["max_chinese_chars"]
        ):
            status = "too_long"
            too_long_sections.append(section)
        else:
            status = "passed"
        sections[section] = {
            **units,
            **standard,
            "status": status,
            "target_english_words": f"{standard['min_english_words']}-{standard['max_english_words']}",
            "target_chinese_chars": f"{standard['min_chinese_chars']}-{standard['max_chinese_chars']}",
        }

    if missing_sections or too_short_sections:
        status = "needs_expansion"
    elif too_long_sections:
        status = "needs_compression"
    else:
        status = "passed"
    return {
        "profile": profile,
        "sections": sections,
        "summary": {
            "missing_sections": missing_sections,
            "too_short_sections": too_short_sections,
            "too_long_sections": too_long_sections,
        },
        "status": status,
    }


def section_length_standard(section: str, profile: str) -> dict[str, int]:
    standard = dict(SECTION_LENGTH_STANDARDS[section])
    if profile == "aer_like" and section == "Abstract":
        standard["max_english_words"] = 100
    return standard


def extract_headings(text: str) -> list[str]:
    headings: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            heading = stripped.lstrip("#").strip()
            if heading:
                headings.append(heading)
    return headings


def section_present(section: str, headings: list[str]) -> bool:
    aliases = SECTION_ALIASES[section]
    normalized_headings = [heading.lower() for heading in headings]
    return any(any(alias in heading for alias in aliases) for heading in normalized_headings)


def find_literature_package(project_root: Path) -> LiteraturePackage:
    candidates = sorted((project_root / "workspace" / "runs").glob("*/02_literature/verified_bibliography.csv"))
    project_candidates = [
        project_root / "Data" / "literature" / "processed" / "verified_bibliography.csv",
        project_root / "state" / "product" / "verified_bibliography.csv",
    ]
    verified = next((path for path in project_candidates + candidates if path.exists()), None)
    contribution_candidates = []
    if verified is not None:
        contribution_candidates.append(verified.parent / "contribution_matrix.md")
    contribution_candidates.extend(
        [
            project_root / "Data" / "literature" / "processed" / "contribution_matrix.md",
            project_root / "state" / "product" / "contribution_matrix.md",
        ]
    )
    contribution = next((path for path in contribution_candidates if path.exists()), None)
    verified_count, closest_or_method_count = count_verified_literature(verified) if verified else (0, 0)
    return LiteraturePackage(verified, contribution, verified_count, closest_or_method_count)


def count_verified_literature(path: Path) -> tuple[int, int]:
    try:
        with path.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
    except (OSError, csv.Error):
        return 0, 0
    verified_rows = [
        row for row in rows if (row.get("verification_status") or "").strip() not in {"", "needs_manual_review"}
    ]
    contribution_rows = [
        row
        for row in verified_rows
        if (row.get("contribution_role") or "").strip() in {"closest_paper", "method_reference"}
    ]
    return len(verified_rows), len(contribution_rows)


def build_citation_checks(literature: LiteraturePackage) -> dict[str, Any]:
    return {
        "verified_bibliography": {
            "status": "found" if literature.verified_bibliography else "missing",
            "path": str(literature.verified_bibliography) if literature.verified_bibliography else None,
            "verified_count": literature.verified_count,
            "closest_or_method_count": literature.closest_or_method_count,
        },
        "contribution_matrix": {
            "status": "found" if literature.contribution_matrix else "missing",
            "path": str(literature.contribution_matrix) if literature.contribution_matrix else None,
        },
        "status": (
            "passed"
            if literature.verified_bibliography and literature.contribution_matrix and literature.verified_count >= 5
            else "needs_literature_review"
        ),
    }


def build_method_gate_checks(project_root: Path) -> dict[str, Any]:
    candidates = [
        project_root / "Results" / "json" / "method_gate_report.json",
        project_root / "state" / "product" / "method_gate.json",
    ]
    candidates.extend(sorted((project_root / "workspace" / "runs").glob("*/03_design/method_gate_report.json")))
    report_path = next((path for path in candidates if path.exists()), None)
    if report_path is None:
        return {
            "status": "missing",
            "path": None,
            "gate_status": None,
            "method_family": None,
            "required_evidence": [],
        }
    try:
        payload = json.loads(report_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {
            "status": "invalid",
            "path": str(report_path),
            "gate_status": "red",
            "method_family": None,
            "required_evidence": [],
        }
    return {
        "status": "found",
        "path": str(report_path),
        "gate_status": payload.get("gate_status"),
        "method_family": payload.get("method_family"),
        "required_evidence": payload.get("required_evidence", []),
        "blocking_items": payload.get("blocking_items", []),
    }


def build_revision_checks(project_root: Path) -> dict[str, Any]:
    reviewer_scorecard_candidates = [
        project_root / "Results" / "json" / "reviewer_scorecard_report.json",
        project_root / "state" / "product" / "reviewer_scorecard.json",
    ]
    reviewer_scorecard = next((path for path in reviewer_scorecard_candidates if path.exists()), None)
    reviewer_payload = load_optional_json(reviewer_scorecard) if reviewer_scorecard else {}
    revision_log_candidates = [
        project_root / "state" / "product" / "revision_log.jsonl",
        project_root / "Submissions" / "pdf_first_review.md",
    ]
    writeback_preflight = project_root / "state" / "product" / "manuscript_export_package.json"
    revision_log = next((path for path in revision_log_candidates if path.exists()), None)
    return {
        "reviewer_scorecard": {
            "status": "found" if reviewer_scorecard else "missing",
            "path": relative_or_absolute(reviewer_scorecard, project_root) if reviewer_scorecard else None,
            "overall_verdict": reviewer_payload.get("overall_verdict"),
            "blocks_export_or_formal_claims": reviewer_payload.get("blocks_export_or_formal_claims"),
        },
        "revision_log": {
            "status": "found" if revision_log else "missing",
            "path": str(revision_log) if revision_log else None,
        },
        "writeback_preflight": {
            "status": "found" if writeback_preflight.exists() else "missing",
            "path": str(writeback_preflight) if writeback_preflight.exists() else None,
        },
        "status": "passed" if reviewer_scorecard and revision_log else "needs_review_loop",
    }


def load_optional_json(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def build_verdict(
    word_count: dict[str, Any],
    format_checks: dict[str, Any],
    section_checks: dict[str, Any],
    section_length_checks: dict[str, Any],
    citation_checks: dict[str, Any],
    method_gate_checks: dict[str, Any],
    revision_checks: dict[str, Any],
) -> list[str]:
    verdict: list[str] = []
    if word_count["main_text_words"] < 7000 and word_count["main_text_chinese_chars"] < 10000:
        verdict.append("too_thin")
    if format_checks["status"] != "passed":
        verdict.append("format_gate_required")
    if section_checks["status"] != "passed":
        verdict.append("missing_sections")
    if section_length_checks["status"] != "passed":
        verdict.append("section_length_gate_required")
    if citation_checks["status"] != "passed":
        verdict.append("needs_literature_review")
    if method_gate_checks["status"] != "found":
        verdict.append("method_gate_required")
    if revision_checks["status"] != "passed":
        verdict.append("needs_review_loop")
    return verdict or ["ready_for_review"]


def build_recommended_next_tasks(
    verdict: list[str],
    format_checks: dict[str, Any],
    section_checks: dict[str, Any],
    section_length_checks: dict[str, Any],
    citation_checks: dict[str, Any],
    method_gate_checks: dict[str, Any],
    revision_checks: dict[str, Any],
) -> list[dict[str, Any]]:
    tasks: list[dict[str, Any]] = []
    if "too_thin" in verdict or "missing_sections" in verdict:
        tasks.append(
            {
                "id": "expand_working_paper_sections",
                "agent": "ManuscriptAgent",
                "reason": "正文结构或篇幅还没有达到 working paper 初稿区间。",
                "inputs": section_checks.get("missing_sections", []),
            }
        )
    if "section_length_gate_required" in verdict:
        thin_sections = build_underdeveloped_section_inputs(section_length_checks)
        if thin_sections:
            tasks.append(
                {
                    "id": "expand_underdeveloped_sections",
                    "agent": "ManuscriptAgent",
                    "reason": "核心章节已存在，但篇幅没有达到 working paper 可审阅的最低厚度。",
                    "inputs": thin_sections,
                    "section_expansion_packet": build_section_expansion_packet(thin_sections),
                    "verification": {
                        "required_before_completion": [
                            "section_length_checks.status=passed",
                            "updated_section_drafts",
                        ]
                    },
                }
            )
    if "format_gate_required" in verdict:
        tasks.append(
            {
                "id": "fix_submission_metadata",
                "agent": "ManuscriptAgent",
                "reason": "补齐摘要、JEL、关键词和数据可得性说明，使草稿进入目标投稿规范。",
                "inputs": format_checks.get("hard_errors", []),
            }
        )
    if citation_checks["status"] != "passed":
        tasks.append(
            {
                "id": "build_literature_package",
                "agent": "LiteratureAgent",
                "reason": "补齐 Zotero/CNKI/DOI 证据和贡献矩阵。",
                "inputs": ["verified_bibliography.csv", "contribution_matrix.md"],
            }
        )
    if method_gate_checks["status"] != "found":
        tasks.append(
            {
                "id": "run_method_gate",
                "agent": "MethodAgent",
                "reason": "在正式估计和论文导出前生成方法规范门报告。",
                "inputs": ["DesignSpec", "RunPlan", "method_family"],
            }
        )
    if revision_checks["status"] != "passed":
        tasks.append(
            {
                "id": "run_reviewer_revision_loop",
                "agent": "ReviewerAgent",
                "reason": "形成审稿意见、修订记录和再次生成路径。",
                "inputs": ["paper_draft", "paper_quality_report"],
            }
        )
    return tasks


def build_underdeveloped_section_inputs(section_length_checks: dict[str, Any]) -> list[dict[str, Any]]:
    sections = section_length_checks.get("sections", {})
    summary = section_length_checks.get("summary", {})
    section_names = [
        *summary.get("missing_sections", []),
        *summary.get("too_short_sections", []),
    ]
    inputs: list[dict[str, Any]] = []
    seen: set[str] = set()
    for section in section_names:
        if section in seen:
            continue
        seen.add(section)
        check = sections.get(section, {})
        inputs.append(
            {
                "section": section,
                "status": check.get("status"),
                "english_word_count": check.get("english_word_count", 0),
                "chinese_char_count": check.get("chinese_char_count", 0),
                "target_english_words": check.get("target_english_words"),
                "target_chinese_chars": check.get("target_chinese_chars"),
            }
        )
    return inputs


def build_section_expansion_packet(section_inputs: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "source": "section_length_checks",
        "source_quality_report": "Results/json/paper_quality_report.json",
        "owner_agent": "ManuscriptAgent",
        "draft_layer_only": True,
        "formal_writeback_allowed": False,
        "sections": [build_section_expansion_item(section_input) for section_input in section_inputs],
        "verification": {
            "required_before_completion": [
                "section_length_checks.status=passed",
                "updated_section_drafts",
                "human_review_before_formal_writeback",
                "no_state_product_writeback",
            ]
        },
    }


def build_section_expansion_item(section_input: dict[str, Any]) -> dict[str, Any]:
    section = str(section_input.get("section") or "")
    return {
        "section": section,
        "status": section_input.get("status"),
        "current_units": {
            "english_word_count": section_input.get("english_word_count", 0),
            "chinese_char_count": section_input.get("chinese_char_count", 0),
        },
        "target_units": {
            "english_words": section_input.get("target_english_words"),
            "chinese_chars": section_input.get("target_chinese_chars"),
        },
        "required_evidence": section_evidence_requirements(section),
        "writing_instruction": section_writing_instruction(section),
        "output_path": f"Manuscripts/sections/{slugify_section(section)}.md",
    }


def section_evidence_requirements(section: str) -> list[str]:
    requirements = {
        "Abstract": ["approved_findings", "method_gate_report", "verified_bibliography.csv"],
        "Introduction": ["research_question", "contribution_matrix.md", "approved_findings"],
        "Literature and Contribution": ["verified_bibliography.csv", "contribution_matrix.md", "closest_papers"],
        "Institutional Background / Theory / Context": ["domain_notes", "mechanism_hypotheses", "literature_context"],
        "Data and Measurement": ["dataset_profile", "variable_dictionary", "sample_construction_log"],
        "Empirical Strategy": ["design_spec", "run_plan", "method_gate_report"],
        "Main Results": ["main_regression_table", "approved_findings", "coefficient_interpretation"],
        "Robustness / Mechanisms / Heterogeneity": [
            "robustness_matrix",
            "mechanism_or_heterogeneity_results",
            "method_gate_report",
        ],
        "Conclusion": ["approved_findings", "limitations_register", "reviewer_scorecard_report"],
    }
    return requirements.get(section, ["section_source_notes", "verified_evidence"])


def section_writing_instruction(section: str) -> str:
    instructions = {
        "Literature and Contribution": "先按相邻问题、识别方法和本文增量组织文献，再把每一类贡献绑定到已核验来源。",
        "Data and Measurement": "补齐数据来源、样本筛选、变量定义、缺失处理和描述统计，不把未校验字段写成正式事实。",
        "Empirical Strategy": "写清估计方程、识别假设、标准误、方法门状态和仍需人工判断的边界。",
        "Main Results": "围绕主表和主图解释系数方向、量级、显著性、经济含义和与研究问题的关系。",
        "Robustness / Mechanisms / Heterogeneity": "把稳健性、机制、异质性和敏感性结果按证据强度分层组织。",
    }
    return instructions.get(section, "补齐本节论证链、证据来源和与全文主问题的连接。")


def slugify_section(section: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", section.lower()).strip("-")
    return slug or "section"


def relative_or_absolute(path: Path, project_root: Path) -> str:
    try:
        return str(path.relative_to(project_root))
    except ValueError:
        return str(path)
