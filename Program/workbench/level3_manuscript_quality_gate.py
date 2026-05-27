from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p7.level3_manuscript_quality_gate.v1"
DEFAULT_PAPER_PATH = Path("workspace/paper_packages/cgss_social_capital_happiness/paper.md")
DEFAULT_MANIFEST_PATH = Path("workspace/paper_packages/cgss_social_capital_happiness/manifest.json")
DEFAULT_REPORT_PATH = Path("Results/json/level3_manuscript_quality_gate.json")
DEFAULT_REVIEW_PATH = Path("Reviews/level3_manuscript_quality_gate.md")

REQUIRED_SECTIONS = {
    "title": ["# "],
    "abstract": ["摘要", "abstract"],
    "introduction": ["引言", "introduction"],
    "literature_review": ["文献", "研究贡献", "literature", "contribution"],
    "data_and_variables": ["数据", "变量", "data", "measurement"],
    "empirical_strategy": ["实证策略", "识别", "empirical strategy", "research design"],
    "main_results": ["主要实证结果", "主结果", "结果", "main results"],
    "robustness_and_further_tests": ["稳健", "进一步检验", "机制", "异质", "robustness", "mechanism"],
    "conclusion": ["结论", "conclusion"],
    "candidate_references": ["参考文献候选", "candidate references", "candidate bibliography"],
    "human_review_checklist": ["人工审阅清单", "human review checklist"],
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_level3_quality_gate(
    paper_text: str,
    package_manifest: dict[str, Any] | None = None,
    source_paths: dict[str, str] | None = None,
) -> dict[str, Any]:
    package_manifest = package_manifest or {}
    source_paths = source_paths or {}
    structure_check = build_structure_check(paper_text)
    length_check = build_length_check(paper_text)
    citation_policy_check = build_citation_policy_check(paper_text, structure_check)
    artifact_check = build_artifact_check(package_manifest)
    boundary_flags = {
        "modified_formal_manuscript": False,
        "modified_formal_bibliography": False,
        "modified_project_bibliography": False,
        "modified_product_state": False,
    }
    required_followup_tasks = build_required_followup_tasks(
        structure_check,
        length_check,
        citation_policy_check,
        artifact_check,
    )
    ready = (
        not structure_check["missing_sections"]
        and length_check["status"] == "passed_minimum"
        and citation_policy_check["status"] == "passed_candidate_review_markers"
    )
    gate_status = "red"
    if ready:
        gate_status = "yellow" if artifact_check["status"] == "needs_human_review" else "green"

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "needs_human_level3_quality_review",
        "gate_status": gate_status,
        "ready_for_level3_review": ready,
        "source_artifacts": {
            "paper": source_paths.get("paper", str(DEFAULT_PAPER_PATH)),
            "package_manifest": source_paths.get("package_manifest", str(DEFAULT_MANIFEST_PATH)),
        },
        "quality_target": {
            "level": "Level 3",
            "minimum_chinese_characters": 5000,
            "target_chinese_characters": "10000+",
            "finalization": "human_review_required",
        },
        "structure_check": structure_check,
        "length_check": length_check,
        "citation_policy_check": citation_policy_check,
        "artifact_check": artifact_check,
        "required_followup_tasks": required_followup_tasks,
        "boundary_flags": boundary_flags,
    }


def build_structure_check(paper_text: str) -> dict[str, Any]:
    headings = extract_headings(paper_text)
    present: list[str] = []
    missing: list[str] = []
    for section, aliases in REQUIRED_SECTIONS.items():
        if section == "title":
            found = any(line.startswith("# ") and not line.startswith("## ") for line in paper_text.splitlines())
        else:
            found = any(any(alias.lower() in heading.lower() for alias in aliases) for heading in headings)
        if found:
            present.append(section)
        else:
            missing.append(section)
    return {
        "required_sections": list(REQUIRED_SECTIONS),
        "present_sections": present,
        "missing_sections": missing,
        "detected_headings": headings,
        "status": "passed" if not missing else "missing_required_sections",
    }


def extract_headings(paper_text: str) -> list[str]:
    headings = []
    for line in paper_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            headings.append(stripped.lstrip("#").strip())
    return headings


def build_length_check(paper_text: str) -> dict[str, Any]:
    chinese_characters = len(re.findall(r"[\u4e00-\u9fff]", paper_text))
    english_words = len(re.findall(r"[A-Za-z][A-Za-z0-9_'-]*", paper_text))
    status = "passed_minimum" if chinese_characters >= 5000 or english_words >= 3500 else "too_short"
    return {
        "status": status,
        "chinese_characters": chinese_characters,
        "english_words": english_words,
        "minimum_chinese_characters": 5000,
        "target_chinese_characters": 10000,
    }


def build_citation_policy_check(paper_text: str, structure_check: dict[str, Any]) -> dict[str, Any]:
    if "candidate_references" in structure_check["missing_sections"]:
        return {
            "status": "missing_candidate_references_section",
            "candidate_references_can_support_claims": False,
            "required_marker_found": False,
        }
    references_body = extract_candidate_reference_body(paper_text)
    has_candidate_marker = "候选" in references_body or "candidate" in references_body.lower()
    has_review_marker = any(marker in references_body for marker in ["待人工核验", "人工核验", "人工审阅", "needs_human"])
    status = "passed_candidate_review_markers" if has_candidate_marker and has_review_marker else "needs_human_review_markers"
    return {
        "status": status,
        "candidate_references_can_support_claims": False,
        "required_marker_found": status == "passed_candidate_review_markers",
    }


def extract_candidate_reference_body(paper_text: str) -> str:
    lines = paper_text.splitlines()
    start: int | None = None
    for index, line in enumerate(lines):
        heading = line.strip().lstrip("#").strip().lower()
        if "参考文献候选" in heading or "candidate references" in heading or "candidate bibliography" in heading:
            start = index + 1
            break
    if start is None:
        return ""
    body = []
    for line in lines[start:]:
        if line.strip().startswith("#"):
            break
        body.append(line)
    return "\n".join(body)


def build_artifact_check(package_manifest: dict[str, Any]) -> dict[str, Any]:
    real_run = package_manifest.get("real_run_artifacts", [])
    draft_layer = package_manifest.get("draft_layer_artifacts", [])
    human_review = package_manifest.get("human_review_required", [])
    if not package_manifest:
        status = "missing_manifest"
    elif human_review:
        status = "needs_human_review"
    else:
        status = "passed"
    return {
        "status": status,
        "package_status": package_manifest.get("status", "not_provided"),
        "real_run_artifacts": real_run,
        "draft_layer_artifacts": draft_layer,
        "human_review_required": human_review,
        "formal_writeback_allowed": bool(package_manifest.get("formal_writeback_allowed", False)),
    }


def build_required_followup_tasks(
    structure_check: dict[str, Any],
    length_check: dict[str, Any],
    citation_policy_check: dict[str, Any],
    artifact_check: dict[str, Any],
) -> list[str]:
    tasks: list[str] = []
    if structure_check["missing_sections"]:
        tasks.append("complete_missing_level3_sections")
    if length_check["status"] == "too_short":
        tasks.append("expand_paper_to_level3_minimum_length")
    if citation_policy_check["status"] == "needs_human_review_markers":
        tasks.append("mark_candidate_references_for_human_review")
    if citation_policy_check["status"] == "missing_candidate_references_section":
        tasks.append("add_candidate_references_section")
    if artifact_check["status"] == "missing_manifest":
        tasks.append("build_paper_package_manifest")
    if artifact_check["status"] == "needs_human_review":
        tasks.append("human_review_level3_package_artifacts")
    return tasks


def write_report(project_root: Path, report: dict[str, Any], report_path: Path, review_path: Path) -> tuple[Path, Path]:
    absolute_report = project_root / report_path
    absolute_review = project_root / review_path
    absolute_report.parent.mkdir(parents=True, exist_ok=True)
    absolute_review.parent.mkdir(parents=True, exist_ok=True)
    absolute_report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    absolute_review.write_text(render_review(report), encoding="utf-8")
    return absolute_report, absolute_review


def render_review(report: dict[str, Any]) -> str:
    lines = [
        "# Level 3 Manuscript Quality Gate",
        "",
        f"- 状态：{report['status']}",
        f"- 门禁：{report['gate_status']}",
        f"- 可进入 Level 3 人工审阅：{report['ready_for_level3_review']}",
        "- 正式论文写回：否",
        "- 正式 bibliography 写回：否",
        "",
        "## 结构检查",
        f"- 缺失章节：{', '.join(report['structure_check']['missing_sections']) or '无'}",
        "",
        "## 长度检查",
        f"- 中文字符：{report['length_check']['chinese_characters']}",
        f"- 状态：{report['length_check']['status']}",
        "",
        "## 引用策略",
        f"- 状态：{report['citation_policy_check']['status']}",
        f"- 候选引用可直接支撑强结论：{report['citation_policy_check']['candidate_references_can_support_claims']}",
        "",
        "## 产物信任层",
        f"- 真实运行产物：{', '.join(report['artifact_check']['real_run_artifacts']) or '无'}",
        f"- 草稿层产物：{', '.join(report['artifact_check']['draft_layer_artifacts']) or '无'}",
        f"- 需要人工审阅：{', '.join(report['artifact_check']['human_review_required']) or '无'}",
        "",
        "## 后续任务",
    ]
    for task in report["required_followup_tasks"]:
        lines.append(f"- `{task}`")
    if not report["required_followup_tasks"]:
        lines.append("- 无新增自动修复任务；等待人工 Level 3 审阅。")
    return "\n".join(lines) + "\n"
