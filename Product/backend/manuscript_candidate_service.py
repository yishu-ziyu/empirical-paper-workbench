from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from Product.backend.project_service import utc_now
from Product.backend.registry import get_project_by_id
from Product.backend.results_draft_service import (
    DRAFT_ARTIFACT_PATH,
    RESULT_ARTIFACT_PATH,
    get_project_results_draft,
    project_root_for,
)


REVIEW_DECISION_PATH = "state/product/finding_reviews.json"
CANDIDATE_REVIEW_PATH = "state/product/manuscript_candidate_reviews.json"
PROMOTION_PATH = "state/product/manuscript_candidate_promotions.json"
EXPORT_PACKAGE_MANIFEST_PATH = "state/product/export_package_manifest.json"
WRITEBACK_PREVIEW_ROOT = "Manuscripts/generated/previews"
VALID_CANDIDATE_REVIEW_ACTIONS = {"approve": "approved", "reject": "rejected", "needs_revision": "needs_revision"}


class ManuscriptCandidateNotFoundError(KeyError):
    pass


class InvalidCandidateReviewActionError(ValueError):
    pass


class CandidateReviewRequiredError(ValueError):
    pass


class CandidatePromotionRequiredError(ValueError):
    pass


def get_project_manuscript_candidates(product_root: Path, repo_root: Path, project_id: str) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = project_root_for(project)
    results_draft = get_project_results_draft(product_root, repo_root, project_id)
    reviews = load_candidate_reviews(project_root).get("reviews", {})
    promotions = load_candidate_promotions(project_root).get("promotions", {})
    exports = load_export_package_manifest(project_root).get("exports", {})
    approved_findings = [
        finding
        for finding in results_draft.get("findings", [])
        if finding.get("can_write_to_draft") is True and finding.get("review_status") == "approved"
    ]
    candidates = [
        apply_candidate_export_preflight(
            apply_candidate_promotion(
                apply_candidate_review(
                    build_manuscript_candidate(finding),
                    reviews.get(f"manuscript_candidate_{finding.get('id', 'finding')}_results"),
                ),
                promotions.get(f"manuscript_candidate_{finding.get('id', 'finding')}_results"),
            ),
            exports.get(f"manuscript_candidate_{finding.get('id', 'finding')}_results"),
        )
        for finding in approved_findings
    ]
    return {
        "_meta": {
            "evidence_level": "local_file",
            "service": "manuscript_candidate_service",
            "generated_at": utc_now(),
        },
        "project_id": project_id,
        "latest_run_id": results_draft.get("latest_run_id"),
        "items": candidates,
        "empty_state": None if candidates else {
            "code": "approved_finding_required",
            "title": "尚无可写入正文的 approved finding",
            "description": "请先在 Results & Draft 中审阅 FindingCard，并将可信论断标记为允许写入正文。",
        },
    }


def get_project_export_package(product_root: Path, repo_root: Path, project_id: str) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = project_root_for(project)
    candidates = get_project_manuscript_candidates(product_root, repo_root, project_id).get("items", [])
    packages = [
        build_export_package(project_root, candidate)
        for candidate in candidates
        if candidate.get("export_status") == "preview_ready"
    ]
    return {
        "_meta": {
            "evidence_level": "local_file",
            "service": "manuscript_candidate_service",
            "generated_at": utc_now(),
        },
        "project_id": project_id,
        "methodology": {
            "reference": "Frontier-Eng",
            "loop": ["proposal", "baseline", "evaluator", "feedback", "next_iteration"],
            "adapted_for": "personal_empirical_research_loop",
        },
        "packages": packages,
        "empty_state": None if packages else {
            "code": "export_preflight_required",
            "title": "尚无 preview_ready 导出包",
            "description": "请先在 Results & Draft 中 approve finding、审阅正文候选，并生成写回预览。",
        },
    }


def save_project_manuscript_candidate_review(
    product_root: Path,
    repo_root: Path,
    project_id: str,
    candidate_id: str,
    action: str,
    note: str,
) -> dict[str, Any]:
    if action not in VALID_CANDIDATE_REVIEW_ACTIONS:
        raise InvalidCandidateReviewActionError(action)

    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = project_root_for(project)
    candidates = get_project_manuscript_candidates(product_root, repo_root, project_id).get("items", [])
    candidate = next((item for item in candidates if item.get("id") == candidate_id), None)
    if not candidate:
        raise ManuscriptCandidateNotFoundError(candidate_id)

    review_status = VALID_CANDIDATE_REVIEW_ACTIONS[action]
    review = {
        "id": f"review_{candidate_id}",
        "candidate_id": candidate_id,
        "finding_id": candidate.get("finding_id"),
        "review_status": review_status,
        "action": action,
        "actor": "user",
        "note": note,
        "timestamp": utc_now(),
        "evidence_level": "local_file",
        "run_id": candidate.get("run_id"),
        "run_plan_version": candidate.get("run_plan_version"),
        "source_draft_path": DRAFT_ARTIFACT_PATH,
        "result_artifact_path": RESULT_ARTIFACT_PATH,
        "can_promote": review_status == "approved",
    }
    state = load_candidate_reviews(project_root)
    state["reviews"][candidate_id] = review
    path = candidate_review_state_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "_meta": {
            "evidence_level": "local_file",
            "service": "manuscript_candidate_service",
            "generated_at": utc_now(),
        },
        "project_id": project_id,
        "candidate_id": candidate_id,
        "review_status": review_status,
        "evidence_level": "local_file",
        "can_promote": review_status == "approved",
        "review": review,
    }


def save_project_manuscript_candidate_promotion(
    product_root: Path,
    repo_root: Path,
    project_id: str,
    candidate_id: str,
    note: str,
) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = project_root_for(project)
    candidates = get_project_manuscript_candidates(product_root, repo_root, project_id).get("items", [])
    candidate = next((item for item in candidates if item.get("id") == candidate_id), None)
    if not candidate:
        raise ManuscriptCandidateNotFoundError(candidate_id)
    if candidate.get("review_status") != "approved" or candidate.get("can_promote") is not True:
        raise CandidateReviewRequiredError(candidate_id)

    promotion = {
        "id": f"promotion_{candidate_id}",
        "candidate_id": candidate_id,
        "finding_id": candidate.get("finding_id"),
        "promotion_status": "ready_for_export",
        "actor": "user",
        "note": note,
        "timestamp": utc_now(),
        "evidence_level": "local_file",
        "run_id": candidate.get("run_id"),
        "run_plan_version": candidate.get("run_plan_version"),
        "target_section": candidate.get("section"),
        "source_draft_path": DRAFT_ARTIFACT_PATH,
        "result_artifact_path": RESULT_ARTIFACT_PATH,
        "candidate_review_path": CANDIDATE_REVIEW_PATH,
        "promotion_path": PROMOTION_PATH,
        "can_export": True,
        "can_write_back": False,
    }
    state = load_candidate_promotions(project_root)
    state["promotions"][candidate_id] = promotion
    path = candidate_promotion_state_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "_meta": {
            "evidence_level": "local_file",
            "service": "manuscript_candidate_service",
            "generated_at": utc_now(),
        },
        "project_id": project_id,
        "candidate_id": candidate_id,
        "promotion_status": "ready_for_export",
        "evidence_level": "local_file",
        "can_export": True,
        "can_write_back": False,
        "promotion": promotion,
    }


def save_project_manuscript_candidate_export_preflight(
    product_root: Path,
    repo_root: Path,
    project_id: str,
    candidate_id: str,
    note: str,
) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = project_root_for(project)
    candidates = get_project_manuscript_candidates(product_root, repo_root, project_id).get("items", [])
    candidate = next((item for item in candidates if item.get("id") == candidate_id), None)
    if not candidate:
        raise ManuscriptCandidateNotFoundError(candidate_id)
    if candidate.get("promotion_status") != "ready_for_export" or candidate.get("can_export") is not True:
        raise CandidatePromotionRequiredError(candidate_id)

    preview_path = f"{WRITEBACK_PREVIEW_ROOT}/{candidate_id}.md"
    preview_file = project_root / preview_path
    preview_file.parent.mkdir(parents=True, exist_ok=True)
    source_draft = project_root / DRAFT_ARTIFACT_PATH
    original_draft = source_draft.read_text(encoding="utf-8") if source_draft.exists() else ""
    preview_file.write_text(build_writeback_preview(candidate, original_draft), encoding="utf-8")

    export_entry = {
        "id": f"export_preflight_{candidate_id}",
        "candidate_id": candidate_id,
        "finding_id": candidate.get("finding_id"),
        "export_status": "preview_ready",
        "actor": "user",
        "note": note,
        "timestamp": utc_now(),
        "evidence_level": "local_file",
        "run_id": candidate.get("run_id"),
        "run_plan_version": candidate.get("run_plan_version"),
        "source_draft_path": DRAFT_ARTIFACT_PATH,
        "writeback_preview_path": preview_path,
        "manifest_path": EXPORT_PACKAGE_MANIFEST_PATH,
        "candidate_promotion_path": PROMOTION_PATH,
        "result_artifact_path": RESULT_ARTIFACT_PATH,
        "can_write_back": False,
    }
    manifest = load_export_package_manifest(project_root)
    manifest["exports"][candidate_id] = export_entry
    path = export_package_manifest_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "_meta": {
            "evidence_level": "local_file",
            "service": "manuscript_candidate_service",
            "generated_at": utc_now(),
        },
        "project_id": project_id,
        "candidate_id": candidate_id,
        "export_status": "preview_ready",
        "evidence_level": "local_file",
        "preview_path": preview_path,
        "manifest_path": EXPORT_PACKAGE_MANIFEST_PATH,
        "can_write_back": False,
        "export": export_entry,
    }


def build_manuscript_candidate(finding: dict[str, Any]) -> dict[str, Any]:
    finding_id = finding.get("id", "finding")
    return {
        "id": f"manuscript_candidate_{finding_id}_results",
        "type": "manuscript_section_candidate",
        "status": "draft",
        "section": "Results",
        "title": finding.get("title") or "Result finding",
        "finding_id": finding_id,
        "run_id": finding.get("run_id"),
        "run_plan_version": finding.get("run_plan_version"),
        "body": build_results_paragraph(finding),
        "provenance": {
            "source_draft": {
                "path": DRAFT_ARTIFACT_PATH,
                "evidence_level": "local_file",
            },
            "result_artifact": {
                "path": RESULT_ARTIFACT_PATH,
                "evidence_level": "local_execution",
            },
            "review_decision": {
                "path": REVIEW_DECISION_PATH,
                "evidence_level": "local_file",
                "review_status": finding.get("review_status"),
            },
        },
    }


def apply_candidate_review(candidate: dict[str, Any], review: dict[str, Any] | None) -> dict[str, Any]:
    matched_review = matching_candidate_review(candidate, review)
    review_status = matched_review.get("review_status") if matched_review else "needs_review"
    provenance = dict(candidate.get("provenance") or {})
    if matched_review:
        provenance["candidate_review"] = {
            "path": CANDIDATE_REVIEW_PATH,
            "evidence_level": "local_file",
            "review_status": review_status,
        }
    return {
        **candidate,
        "review_status": review_status,
        "can_promote": review_status == "approved",
        "review": matched_review,
        "provenance": provenance,
    }


def apply_candidate_promotion(candidate: dict[str, Any], promotion: dict[str, Any] | None) -> dict[str, Any]:
    matched_promotion = matching_candidate_promotion(candidate, promotion)
    provenance = dict(candidate.get("provenance") or {})
    if matched_promotion:
        provenance["promotion_state"] = {
            "path": PROMOTION_PATH,
            "evidence_level": "local_file",
            "promotion_status": matched_promotion.get("promotion_status"),
        }
    return {
        **candidate,
        "promotion_status": matched_promotion.get("promotion_status") if matched_promotion else "not_promoted",
        "can_export": matched_promotion.get("can_export") is True if matched_promotion else False,
        "can_write_back": False,
        "promotion": matched_promotion,
        "provenance": provenance,
    }


def apply_candidate_export_preflight(candidate: dict[str, Any], export_entry: dict[str, Any] | None) -> dict[str, Any]:
    matched_export = matching_candidate_export(candidate, export_entry)
    provenance = dict(candidate.get("provenance") or {})
    if matched_export:
        provenance["export_package"] = {
            "path": EXPORT_PACKAGE_MANIFEST_PATH,
            "evidence_level": "local_file",
            "export_status": matched_export.get("export_status"),
        }
    return {
        **candidate,
        "export_status": matched_export.get("export_status") if matched_export else "not_started",
        "writeback_preview_path": matched_export.get("writeback_preview_path") if matched_export else None,
        "export_manifest_path": EXPORT_PACKAGE_MANIFEST_PATH if matched_export else None,
        "export": matched_export,
        "provenance": provenance,
    }


def matching_candidate_review(candidate: dict[str, Any], review: dict[str, Any] | None) -> dict[str, Any] | None:
    if not review:
        return None
    if review.get("candidate_id") != candidate.get("id"):
        return None
    if review.get("finding_id") != candidate.get("finding_id"):
        return None
    if review.get("run_id") != candidate.get("run_id"):
        return None
    return review


def matching_candidate_promotion(candidate: dict[str, Any], promotion: dict[str, Any] | None) -> dict[str, Any] | None:
    if not promotion:
        return None
    if promotion.get("candidate_id") != candidate.get("id"):
        return None
    if promotion.get("finding_id") != candidate.get("finding_id"):
        return None
    if promotion.get("run_id") != candidate.get("run_id"):
        return None
    return promotion


def matching_candidate_export(candidate: dict[str, Any], export_entry: dict[str, Any] | None) -> dict[str, Any] | None:
    if not export_entry:
        return None
    if export_entry.get("candidate_id") != candidate.get("id"):
        return None
    if export_entry.get("finding_id") != candidate.get("finding_id"):
        return None
    if export_entry.get("run_id") != candidate.get("run_id"):
        return None
    return export_entry


def candidate_review_state_path(project_root: Path) -> Path:
    return project_root / CANDIDATE_REVIEW_PATH


def candidate_promotion_state_path(project_root: Path) -> Path:
    return project_root / PROMOTION_PATH


def export_package_manifest_path(project_root: Path) -> Path:
    return project_root / EXPORT_PACKAGE_MANIFEST_PATH


def load_candidate_reviews(project_root: Path) -> dict[str, Any]:
    path = candidate_review_state_path(project_root)
    if not path.exists():
        return {
            "_meta": {
                "evidence_level": "local_file",
                "service": "manuscript_candidate_service",
            },
            "reviews": {},
        }
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload.setdefault("reviews", {})
    return payload


def load_candidate_promotions(project_root: Path) -> dict[str, Any]:
    path = candidate_promotion_state_path(project_root)
    if not path.exists():
        return {
            "_meta": {
                "evidence_level": "local_file",
                "service": "manuscript_candidate_service",
            },
            "promotions": {},
        }
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload.setdefault("promotions", {})
    return payload


def load_export_package_manifest(project_root: Path) -> dict[str, Any]:
    path = export_package_manifest_path(project_root)
    if not path.exists():
        return {
            "_meta": {
                "evidence_level": "local_file",
                "service": "manuscript_candidate_service",
            },
            "exports": {},
        }
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload.setdefault("exports", {})
    return payload


def build_export_package(project_root: Path, candidate: dict[str, Any]) -> dict[str, Any]:
    export_entry = candidate.get("export") or {}
    checks = build_export_evaluator_checks(project_root, candidate)
    evaluator_status = "passed" if all(check.get("status") == "passed" for check in checks) else "failed"
    return {
        "id": f"export_package_{candidate.get('id')}",
        "candidate_id": candidate.get("id"),
        "finding_id": candidate.get("finding_id"),
        "run_id": candidate.get("run_id"),
        "run_plan_version": candidate.get("run_plan_version"),
        "section": candidate.get("section"),
        "title": candidate.get("title"),
        "export_status": candidate.get("export_status"),
        "evidence_level": export_entry.get("evidence_level") or "local_file",
        "writeback_preview_path": candidate.get("writeback_preview_path"),
        "manifest_path": candidate.get("export_manifest_path") or EXPORT_PACKAGE_MANIFEST_PATH,
        "source_draft_path": export_entry.get("source_draft_path") or DRAFT_ARTIFACT_PATH,
        "result_artifact_path": export_entry.get("result_artifact_path") or RESULT_ARTIFACT_PATH,
        "can_write_back": candidate.get("can_write_back") is True,
        "evaluator_status": evaluator_status,
        "evaluator_checks": checks,
        "frontier_loop": {
            "reference": "Frontier-Eng",
            "objective": "让 approved finding 进入可人工验收的正文导出包。",
            "baseline": f"source_draft={DRAFT_ARTIFACT_PATH}",
            "evaluator": "preview_exists + manifest_exists + result_bound + promotion_decision + no_writeback",
            "feedback": f"evaluator_status={evaluator_status}",
        },
        "frontier_iteration_log": build_frontier_iteration_log(candidate, evaluator_status),
        "next_manual_action": "人工确认预览段落和 evaluator checks 后，再进入显式写回或 docx 导出。",
    }


def build_export_evaluator_checks(project_root: Path, candidate: dict[str, Any]) -> list[dict[str, Any]]:
    preview_path = candidate.get("writeback_preview_path") or ""
    manifest_path = candidate.get("export_manifest_path") or EXPORT_PACKAGE_MANIFEST_PATH
    promotion_path = candidate.get("promotion", {}).get("promotion_path") or PROMOTION_PATH
    result_artifact_path = candidate.get("export", {}).get("result_artifact_path") or RESULT_ARTIFACT_PATH
    return [
        {
            "id": "writeback_preview_exists",
            "label": "写回预览文件存在",
            "status": "passed" if preview_path and (project_root / preview_path).exists() else "failed",
            "evidence_level": "local_file",
            "path": preview_path,
        },
        {
            "id": "export_manifest_exists",
            "label": "export manifest 存在",
            "status": "passed" if (project_root / manifest_path).exists() else "failed",
            "evidence_level": "local_file",
            "path": manifest_path,
        },
        {
            "id": "result_artifact_bound",
            "label": "结果产物已绑定",
            "status": "passed" if (project_root / result_artifact_path).exists() else "failed",
            "evidence_level": "local_execution",
            "path": result_artifact_path,
        },
        {
            "id": "promotion_decision_present",
            "label": "人工 promote 决策存在",
            "status": "passed" if (project_root / promotion_path).exists() else "failed",
            "evidence_level": "local_file",
            "path": promotion_path,
        },
        {
            "id": "source_draft_not_overwritten",
            "label": "源草稿未被自动覆盖",
            "status": "passed" if candidate.get("can_write_back") is not True else "failed",
            "evidence_level": "local_file",
            "path": DRAFT_ARTIFACT_PATH,
            "detail": "can_write_back=false" if candidate.get("can_write_back") is not True else "can_write_back=true",
        },
    ]


def build_frontier_iteration_log(candidate: dict[str, Any], evaluator_status: str) -> list[dict[str, Any]]:
    timestamp = utc_now()
    run_id = candidate.get("run_id")
    candidate_id = candidate.get("id")
    return [
        {
            "phase": "objective",
            "title": "目标",
            "description": "把已审阅 FindingCard 转成可人工验收的论文结果段落导出包。",
            "candidate_id": candidate_id,
            "run_id": run_id,
            "timestamp": timestamp,
        },
        {
            "phase": "baseline",
            "title": "Baseline",
            "description": f"以当前草稿 {DRAFT_ARTIFACT_PATH} 和 full-run 结果作为最小可运行版本。",
            "candidate_id": candidate_id,
            "run_id": run_id,
            "timestamp": timestamp,
        },
        {
            "phase": "evaluator",
            "title": "Evaluator",
            "description": "检查 preview、manifest、result artifact、promotion decision 和 no-writeback 保护。",
            "candidate_id": candidate_id,
            "run_id": run_id,
            "timestamp": timestamp,
        },
        {
            "phase": "feedback",
            "title": "反馈",
            "description": f"本轮 evaluator_status={evaluator_status}。",
            "candidate_id": candidate_id,
            "run_id": run_id,
            "timestamp": timestamp,
        },
        {
            "phase": "next_iteration",
            "title": "下一轮",
            "description": "人工确认后进入显式写回、docx 导出或继续修改 candidate。",
            "candidate_id": candidate_id,
            "run_id": run_id,
            "timestamp": timestamp,
        },
    ]


def build_results_paragraph(finding: dict[str, Any]) -> str:
    treatment = finding.get("treatment") or "treatment"
    outcome = finding.get("dependent_var") or "outcome"
    estimate = format_number(finding.get("estimate"))
    std_error = format_number(finding.get("std_error"))
    p_value = format_number(finding.get("p_value"))
    sample_size = finding.get("sample_size") or "-"
    model_type = finding.get("model_type") or "model"
    return (
        f"在 {model_type} 设定下，{treatment} 对 {outcome} 的估计系数为 {estimate}，"
        f"标准误为 {std_error}，p 值为 {p_value}，样本量为 {sample_size}。"
        "该段落候选来自已审阅的 FindingCard，进入正文前仍需人工检查表述、识别假设和稳健性上下文。"
    )


def build_writeback_preview(candidate: dict[str, Any], original_draft: str) -> str:
    return (
        f"{original_draft.rstrip()}\n\n"
        "<!-- writeback_preview: do not overwrite source draft automatically -->\n"
        f"source_draft: {DRAFT_ARTIFACT_PATH}\n"
        f"candidate_id: {candidate.get('id')}\n"
        f"run_id: {candidate.get('run_id')}\n"
        f"run_plan_version: {candidate.get('run_plan_version')}\n\n"
        "### Proposed Results paragraph\n\n"
        f"{candidate.get('body', '')}\n"
    )


def format_number(value: Any) -> str:
    if value is None or value == "":
        return "-"
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    if number != 0 and abs(number) < 0.001:
        return f"{number:.2e}"
    return f"{number:.4f}".rstrip("0").rstrip(".")
