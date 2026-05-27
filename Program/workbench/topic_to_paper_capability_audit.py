from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_OUTPUT_REPORT = "Results/json/topic_to_paper_capability_audit.json"
DEFAULT_OUTPUT_REVIEW = "Reviews/topic_to_paper_capability_audit.md"


def build_topic_to_paper_capability_audit(project_root: Path, topic: str) -> tuple[dict[str, Any], int]:
    formal_summary = load_json(project_root / "state/product/formal_submission_package_summary.json")
    manual_acceptance = load_json(project_root / "state/product/formal_submission_package_manual_acceptance.json")
    paper_quality = load_json(project_root / "Results/json/paper_quality_report.json")
    literature_package = load_json(project_root / "Results/json/literature_package_report.json")
    method_gate = load_json(project_root / "Results/json/method_gate_report.json")
    revision_round = load_json(project_root / "Results/json/paper_revision_round.json")
    research_question = load_json(project_root / "state/product/research_question.json")

    formal_package_ready = formal_summary.get("ready_for_manual_acceptance") is True
    topic_fit = build_topic_fit(topic, research_question, project_root)
    gates = {
        "topic_fit": topic_fit,
        "formal_package": build_formal_package_gate(formal_summary),
        "manual_acceptance": build_manual_acceptance_gate(manual_acceptance),
        "paper_structure_length": build_structure_gate(paper_quality),
        "literature_review": build_literature_gate(literature_package),
        "method_gate": build_method_gate(method_gate),
        "reviewer_revision_loop": build_revision_gate(revision_round),
        "final_artifacts": build_final_artifacts_gate(project_root, formal_summary),
    }
    blocking_reasons = collect_blocking_reasons(formal_summary, gates)
    status, current_reproducibility, general_automation, exit_code = build_overall_status(
        formal_package_ready=formal_package_ready,
        topic_fit=topic_fit,
        blocking_reasons=blocking_reasons,
    )
    report = {
        "schema_version": "p6.topic_to_paper_capability_audit.v1",
        "generated_at": utc_now(),
        "research_topic": topic,
        "status": status,
        "current_topic_reproducibility": current_reproducibility,
        "general_topic_automation": general_automation,
        "gates": gates,
        "blocking_reasons": blocking_reasons,
        "review_targets": build_review_targets(formal_summary),
        "next_tasks": collect_next_tasks(paper_quality, literature_package, method_gate, revision_round, topic_fit),
        "boundary_flags": {
            "this_command_generated_new_paper": False,
            "this_command_modified_formal_package": False,
            "this_command_accepted_package": False,
            "this_command_modified_formal_research_state": False,
        },
    }
    return report, exit_code


def build_topic_fit(topic: str, research_question: dict[str, Any], project_root: Path) -> dict[str, Any]:
    current_question = str(research_question.get("question") or "")
    if not current_question:
        return {"status": "unknown", "current_question": None, "reason": "research_question_missing"}
    topic_tokens = extract_topic_tokens(topic)
    current_tokens = extract_topic_tokens(current_question)
    overlap = sorted(topic_tokens & current_tokens)
    requested_cgss = "cgss" in topic.lower() or "CGSS" in topic
    current_mentions_cgss = "cgss" in current_question.lower() or "CGSS" in current_question
    status = "matched" if overlap and (requested_cgss == current_mentions_cgss) else "new_topic_requires_data_binding"
    return {
        "status": status,
        "current_question": current_question,
        "overlap_tokens": overlap,
        "requested_dataset_hint": "CGSS" if requested_cgss else None,
        "current_question_mentions_requested_dataset": current_mentions_cgss if requested_cgss else None,
        "reason": "topic differs from current formal package" if status != "matched" else "topic overlaps current formal package",
    }


def extract_topic_tokens(text: str) -> set[str]:
    lowered = text.lower()
    tokens = set()
    for token in [
        "cgss",
        "cfps",
        "社会资本",
        "主观幸福感",
        "幸福感",
        "工业机器人",
        "机器人",
        "劳动力",
        "匹配",
        "居民",
    ]:
        if token.lower() in lowered:
            tokens.add(token.lower())
    return tokens


def build_formal_package_gate(summary: dict[str, Any]) -> dict[str, Any]:
    ready = summary.get("ready_for_manual_acceptance") is True
    return {
        "status": "ready" if ready else "blocked",
        "source_status": summary.get("status"),
        "blocking_reasons": summary.get("blocking_reasons") or [],
    }


def build_manual_acceptance_gate(manual_acceptance: dict[str, Any]) -> dict[str, Any]:
    if manual_acceptance.get("accepted") is True:
        status = "accepted"
    elif manual_acceptance.get("decision") == "defer":
        status = "pending_human_review"
    elif manual_acceptance.get("needs_revision") is True:
        status = "needs_revision"
    else:
        status = manual_acceptance.get("status") or "missing"
    return {
        "status": status,
        "decision": manual_acceptance.get("decision"),
        "accepted": manual_acceptance.get("accepted") is True,
        "blocking_reasons": manual_acceptance.get("blocking_reasons") or [],
    }


def build_structure_gate(paper_quality: dict[str, Any]) -> dict[str, Any]:
    verdict = paper_quality.get("verdict") or []
    needs_work_markers = {"too_thin", "missing_sections", "section_length_gate_required", "needs_review_loop"}
    status = "needs_work" if any(marker in verdict for marker in needs_work_markers) else "passed"
    return {
        "status": status,
        "verdict": verdict,
        "word_count": paper_quality.get("word_count") or {},
    }


def build_literature_gate(literature_package: dict[str, Any]) -> dict[str, Any]:
    status = literature_package.get("status") or "missing"
    normalized = "ready" if status in {"ready", "completed", "approved"} else status
    return {
        "status": normalized,
        "counts": literature_package.get("counts") or {},
        "missing_evidence": literature_package.get("missing_evidence") or [],
    }


def build_method_gate(method_gate: dict[str, Any]) -> dict[str, Any]:
    red_items = method_gate.get("red_items") or []
    yellow_items = method_gate.get("yellow_items") or []
    blocking_items = method_gate.get("blocking_items") or []
    if red_items or blocking_items:
        status = "blocked"
    elif yellow_items:
        status = "needs_human_review"
    else:
        status = method_gate.get("status") or "missing"
    return {
        "status": status,
        "source_status": method_gate.get("status"),
        "blocking_items": blocking_items,
        "yellow_items": yellow_items,
        "red_items": red_items,
    }


def build_revision_gate(revision_round: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": revision_round.get("status") or "missing",
        "revision_item_count": len(revision_round.get("revision_items") or []),
        "next_action": revision_round.get("next_action") or {},
    }


def build_final_artifacts_gate(project_root: Path, summary: dict[str, Any]) -> dict[str, Any]:
    artifacts = summary.get("artifacts") or {}
    pdf = artifacts.get("paper_pdf") or {}
    docx = artifacts.get("paper_docx") or {}
    pdf_path = project_root / str(pdf.get("path") or "Submissions/formal_package/paper.pdf")
    docx_path = project_root / str(docx.get("path") or "Submissions/formal_package/paper.docx")
    ready = pdf_path.exists() and docx_path.exists()
    return {
        "status": "ready" if ready else "blocked",
        "paper_pdf_exists": pdf_path.exists(),
        "paper_docx_exists": docx_path.exists(),
        "paper_pdf_path": relative_or_absolute(pdf_path, project_root),
        "paper_docx_path": relative_or_absolute(docx_path, project_root),
    }


def collect_blocking_reasons(summary: dict[str, Any], gates: dict[str, dict[str, Any]]) -> list[str]:
    reasons = list(summary.get("blocking_reasons") or [])
    for gate_id, gate in gates.items():
        if gate.get("status") == "blocked":
            reasons.append(f"{gate_id}_blocked")
    return sorted(set(reasons))


def build_overall_status(
    *,
    formal_package_ready: bool,
    topic_fit: dict[str, Any],
    blocking_reasons: list[str],
) -> tuple[str, str, str, int]:
    general_automation = "not_yet_general_auto_paper_generation"
    if not formal_package_ready or blocking_reasons:
        return (
            "blocked_before_paper_package_review",
            "not_reproducible_until_formal_package_ready",
            general_automation,
            2,
        )
    if topic_fit.get("status") == "new_topic_requires_data_binding":
        return (
            "new_topic_requires_data_binding",
            "not_reproducible_until_topic_data_binding",
            general_automation,
            3,
        )
    return (
        "ready_for_human_review_reproduction",
        "reproducible_with_existing_pipeline_and_human_review",
        general_automation,
        0,
    )


def build_review_targets(summary: dict[str, Any]) -> list[str]:
    targets = []
    for target in summary.get("open_targets") or []:
        path = target.get("path")
        if path:
            targets.append(path)
    artifacts = summary.get("artifacts") or {}
    for artifact in [artifacts.get("paper_pdf") or {}, artifacts.get("paper_docx") or {}]:
        path = artifact.get("path")
        if path and path not in targets:
            targets.append(path)
    return targets


def collect_next_tasks(*reports: dict[str, Any]) -> list[str]:
    task_ids: list[str] = []
    for report in reports:
        for task in report.get("recommended_next_tasks") or []:
            if isinstance(task, str):
                task_id = task
            elif isinstance(task, dict):
                task_id = task.get("id")
            else:
                task_id = None
            if task_id and task_id not in task_ids:
                task_ids.append(task_id)
        if report.get("status") == "new_topic_requires_data_binding":
            for task_id in ["bind_topic_to_cgss_dataset", "discover_cgss_social_capital_happiness_variables"]:
                if task_id not in task_ids:
                    task_ids.append(task_id)
    return task_ids


def write_topic_to_paper_capability_audit_outputs(
    report_path: Path,
    review_path: Path,
    report: dict[str, Any],
) -> tuple[Path, Path]:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    review_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    review_path.write_text(render_review(report), encoding="utf-8")
    return report_path, review_path


def render_review(report: dict[str, Any]) -> str:
    lines = [
        "# Topic-to-Paper Capability Audit",
        "",
        f"- 题目：{report.get('research_topic')}",
        f"- 当前状态：{report.get('status')}",
        f"- 当前题目复现能力：{report.get('current_topic_reproducibility')}",
        f"- 任意新题目全自动成文：{'尚未成立' if report.get('general_topic_automation') == 'not_yet_general_auto_paper_generation' else report.get('general_topic_automation')}",
        "",
    ]
    if report.get("status") == "ready_for_human_review_reproduction":
        lines.append("当前题目可以复现到正式包，但仍需要人工审阅。")
    elif report.get("status") == "new_topic_requires_data_binding":
        lines.append("这是新题目，必须先绑定数据和变量，再进入完整论文包生成。")
    else:
        lines.append("当前题目还不能进入论文包审阅，需先解除阻断项。")
    lines.extend(["", "## Gates", ""])
    for gate_id, gate in (report.get("gates") or {}).items():
        lines.append(f"- {gate_id}: {gate.get('status')}")
    lines.extend(["", "## Review Targets", ""])
    for target in report.get("review_targets") or []:
        lines.append(f"- {target}")
    lines.extend(["", "## Next Tasks", ""])
    for task in report.get("next_tasks") or []:
        lines.append(f"- {task}")
    lines.append("")
    return "\n".join(lines)


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def relative_or_absolute(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
