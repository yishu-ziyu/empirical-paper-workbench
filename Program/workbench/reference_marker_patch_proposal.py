from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p7.reference_marker_patch_proposal.v1"
DEFAULT_SOURCE_PAPER_PATH = Path("workspace/paper_packages/cgss_social_capital_happiness/paper.md")
DEFAULT_CANDIDATE_PAPER_PATH = Path("Manuscripts/generated/cgss_social_capital_happiness_paper_reference_marked.md")
DEFAULT_REPORT_PATH = Path("Results/json/reference_marker_patch_proposal.json")
DEFAULT_REVIEW_PATH = Path("Reviews/reference_marker_patch_proposal.md")
REFERENCE_MARKER = "（候选，待人工核验）"


def build_reference_marker_patch(paper_text: str, source_path: str = "") -> dict[str, Any]:
    candidate_text, changed_references, section_found = apply_reference_markers(paper_text)
    if not section_found:
        status = "blocked_missing_candidate_references_section"
    elif changed_references:
        status = "needs_human_reference_marker_review"
    else:
        status = "no_reference_marker_patch_needed"

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "source_artifacts": {
            "source_paper": source_path or str(DEFAULT_SOURCE_PAPER_PATH),
        },
        "candidate_paper": str(DEFAULT_CANDIDATE_PAPER_PATH),
        "changed_references": changed_references,
        "candidate_paper_text": candidate_text,
        "boundary_flags": {
            "modified_formal_manuscript": False,
            "modified_formal_bibliography": False,
            "modified_project_bibliography": False,
            "modified_product_state": False,
            "source_paper_overwritten": False,
        },
        "promotion": {
            "allowed": False,
            "required_decision": "human_approve_reference_marker_patch",
            "would_write_if_approved": [
                "workspace/paper_packages/cgss_social_capital_happiness/paper.md",
            ],
        },
    }


def apply_reference_markers(paper_text: str) -> tuple[str, list[dict[str, Any]], bool]:
    lines = paper_text.splitlines(keepends=True)
    section_start = find_candidate_reference_section(lines)
    if section_start is None:
        return paper_text, [], False

    changed: list[dict[str, Any]] = []
    in_section = False
    for index, line in enumerate(lines):
        if index == section_start:
            in_section = True
            continue
        if in_section and line.strip().startswith("#"):
            break
        if not in_section or not is_reference_bullet(line):
            continue
        if has_required_reference_marker(line):
            continue
        updated = append_reference_marker(line)
        lines[index] = updated
        changed.append(
            {
                "line_number": index + 1,
                "before": line.rstrip("\n"),
                "after": updated.rstrip("\n"),
                "marker": REFERENCE_MARKER,
            }
        )
    return "".join(lines), changed, True


def find_candidate_reference_section(lines: list[str]) -> int | None:
    for index, line in enumerate(lines):
        heading = line.strip().lstrip("#").strip().lower()
        if "参考文献候选" in heading or "candidate references" in heading or "candidate bibliography" in heading:
            return index
    return None


def is_reference_bullet(line: str) -> bool:
    stripped = line.lstrip()
    return stripped.startswith("- ") or stripped.startswith("* ")


def has_required_reference_marker(line: str) -> bool:
    lower_line = line.lower()
    has_candidate = "候选" in line or "candidate" in lower_line
    has_human_review = any(marker in line for marker in ["待人工核验", "人工核验", "人工审阅", "人工审查", "needs_human"])
    return has_candidate and has_human_review


def append_reference_marker(line: str) -> str:
    newline = "\n" if line.endswith("\n") else ""
    body = line[:-1] if newline else line
    return f"{body}{REFERENCE_MARKER}{newline}"


def write_outputs(
    project_root: Path,
    patch: dict[str, Any],
    report_path: Path,
    review_path: Path,
    candidate_paper_path: Path,
) -> tuple[Path, Path, Path]:
    absolute_report = project_root / report_path
    absolute_review = project_root / review_path
    absolute_candidate = project_root / candidate_paper_path
    source_path = Path(str(patch.get("source_artifacts", {}).get("source_paper", "")))
    absolute_source = project_root / source_path
    if absolute_candidate.resolve() == absolute_source.resolve():
        raise ValueError("candidate paper path must not overwrite source paper")

    absolute_report.parent.mkdir(parents=True, exist_ok=True)
    absolute_review.parent.mkdir(parents=True, exist_ok=True)
    absolute_candidate.parent.mkdir(parents=True, exist_ok=True)

    patch_for_json = dict(patch)
    patch_for_json.pop("candidate_paper_text", None)
    patch_for_json["candidate_paper"] = str(candidate_paper_path)
    absolute_report.write_text(json.dumps(patch_for_json, ensure_ascii=False, indent=2), encoding="utf-8")
    absolute_review.write_text(render_review(patch_for_json), encoding="utf-8")
    absolute_candidate.write_text(str(patch["candidate_paper_text"]), encoding="utf-8")
    return absolute_report, absolute_review, absolute_candidate


def render_review(patch: dict[str, Any]) -> str:
    lines = [
        "# Reference Marker Patch Proposal",
        "",
        f"- 状态：{patch['status']}",
        f"- 原论文：{patch['source_artifacts']['source_paper']}",
        f"- 候选稿：{patch['candidate_paper']}",
        "- 正式论文写回：否",
        "- 正式 bibliography 写回：否",
        "- project bibliography 写回：否",
        "- product state 写回：否",
        "- 原论文覆盖：否",
        "",
        "## 修改候选",
    ]
    if patch["changed_references"]:
        for item in patch["changed_references"]:
            lines.append(f"- L{item['line_number']}: `{item['before']}` -> `{item['after']}`")
    else:
        lines.append("- 无逐条引用标记修改。")
    lines.extend(
        [
            "",
            "## 人工审阅",
            "- 核对每条候选引用是否确实只应作为候选引用进入草稿层。",
            "- 若批准，可将候选稿提升为下一轮 package paper；未批准则保持原包不变。",
        ]
    )
    return "\n".join(lines) + "\n"
