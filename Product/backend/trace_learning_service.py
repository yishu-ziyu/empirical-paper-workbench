from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from Product.backend.project_service import utc_now
from Product.backend.registry import get_project_by_id


TRACE_LEARNING_BAD_CASES_PATH = Path("state/product/trace_learning_bad_cases.jsonl")
TRACE_LEARNING_REGRESSION_PROPOSALS_PATH = Path("state/product/trace_learning_regression_proposals.jsonl")
TRACE_LEARNING_REGRESSION_PROPOSAL_REVIEWS_PATH = Path(
    "state/product/trace_learning_regression_proposal_reviews.jsonl"
)
TRACE_LEARNING_REGRESSION_TEST_PATCH_PROPOSALS_PATH = Path(
    "state/product/trace_learning_regression_test_patch_proposals.jsonl"
)
ALLOWED_TRACE_LEARNING_FIX_LAYERS = [
    "prompt",
    "skill_playbook",
    "decision_rule",
    "knowledge_base",
    "retrieval",
    "tool_interface",
    "memory",
    "output_format",
    "clarification_flow",
    "product_boundary",
    "eval_set",
]


class TraceLearningProposalBlockedError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def trace_learning_bad_cases_path(project_root: Path) -> Path:
    return project_root / TRACE_LEARNING_BAD_CASES_PATH


def trace_learning_regression_proposals_path(project_root: Path) -> Path:
    return project_root / TRACE_LEARNING_REGRESSION_PROPOSALS_PATH


def trace_learning_regression_proposal_reviews_path(project_root: Path) -> Path:
    return project_root / TRACE_LEARNING_REGRESSION_PROPOSAL_REVIEWS_PATH


def trace_learning_regression_test_patch_proposals_path(project_root: Path) -> Path:
    return project_root / TRACE_LEARNING_REGRESSION_TEST_PATCH_PROPOSALS_PATH


def capture_project_trace_learning_bad_case(
    product_root: Path,
    repo_root: Path,
    project_id: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    path = trace_learning_bad_cases_path(project_root)
    existing_cases = load_trace_learning_bad_cases(path)
    timestamp = utc_now()
    fix_layer = normalize_fix_layer(payload.get("fix_layer"))
    record: dict[str, Any] = {
        "id": build_bad_case_id(existing_cases, payload.get("stage")),
        "trace_learning_version": 1,
        "status": "captured",
        "created_at": timestamp,
        "project_id": project["id"],
        "stage": str(payload.get("stage") or "unknown"),
        "surface": str(payload.get("surface") or "unknown"),
        "page_url": str(payload.get("page_url") or ""),
        "target_text": str(payload.get("target_text") or ""),
        "agent_output": str(payload.get("agent_output") or ""),
        "user_feedback": str(payload.get("user_feedback") or "").strip(),
        "expected_behavior": str(payload.get("expected_behavior") or ""),
        "fix_layer": fix_layer,
        "severity": str(payload.get("severity") or "medium"),
        "related_files": normalize_string_list(payload.get("related_files")),
        "writes_formal_layer": False,
        "next_action": "turn_into_regression_test",
        "regression_target": {
            "kind": "contract_test",
            "status": "pending",
            "suggested_test_name": f"test_trace_learning_bad_case_{slugify(payload.get('stage') or 'unknown')}",
        },
    }
    original_fix_layer = str(payload.get("fix_layer") or "")
    if original_fix_layer and original_fix_layer != fix_layer:
        record["original_fix_layer"] = original_fix_layer

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

    return {
        "project_id": project["id"],
        "bad_case": record,
        "trace_learning": build_trace_learning_summary(path, len(existing_cases) + 1),
    }


def get_project_trace_learning_bad_cases(product_root: Path, repo_root: Path, project_id: str) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    path = trace_learning_bad_cases_path(project_root)
    cases = load_trace_learning_bad_cases(path)
    summary = build_trace_learning_summary(path, len(cases))
    summary["bad_cases"] = cases
    return {"project_id": project["id"], "trace_learning": summary}


def generate_project_trace_learning_regression_proposal(
    product_root: Path,
    repo_root: Path,
    project_id: str,
) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    bad_cases_path = trace_learning_bad_cases_path(project_root)
    proposals_path = trace_learning_regression_proposals_path(project_root)
    bad_cases = load_trace_learning_bad_cases(bad_cases_path)
    if not bad_cases:
        raise TraceLearningProposalBlockedError(
            "no_captured_trace_learning_bad_cases",
            "No captured Trace Learning bad cases exist for this project.",
        )

    existing_proposals = load_trace_learning_regression_proposals(proposals_path)
    proposed_case_ids = {
        case_id
        for proposal in existing_proposals
        for case_id in proposal.get("source_bad_case_ids", [])
    }
    source_cases = [case for case in bad_cases if case.get("id") not in proposed_case_ids]
    if not source_cases:
        raise TraceLearningProposalBlockedError(
            "no_new_trace_learning_bad_cases",
            "All captured Trace Learning bad cases already have regression proposals.",
        )

    first_case = source_cases[0]
    patch_layer = normalize_fix_layer(first_case.get("fix_layer"))
    proposal = {
        "id": build_regression_proposal_id(existing_proposals, patch_layer),
        "trace_learning_version": 1,
        "status": "needs_review",
        "created_at": utc_now(),
        "project_id": project["id"],
        "source_bad_case_ids": [str(case.get("id")) for case in source_cases],
        "patch_layer": patch_layer,
        "suggested_tests": [build_suggested_regression_test(case) for case in source_cases],
        "writes_formal_layer": False,
        "requires_human_review": True,
        "artifact_path": TRACE_LEARNING_REGRESSION_PROPOSALS_PATH.as_posix(),
        "next_action": "human_review_regression_proposal",
        "canonical_rule_write_allowed": False,
    }

    proposals_path.parent.mkdir(parents=True, exist_ok=True)
    with proposals_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(proposal, ensure_ascii=False, sort_keys=True) + "\n")

    reviews_path = trace_learning_regression_proposal_reviews_path(project_root)
    existing_reviews = load_trace_learning_regression_proposal_reviews(reviews_path)
    latest_proposal = enrich_regression_proposals_with_review_status([proposal], existing_reviews)[0]
    summary = build_trace_learning_regression_proposal_summary(
        proposals_path,
        len(existing_proposals) + 1,
        existing_reviews,
    )
    summary["latest_proposal"] = latest_proposal
    return {
        "project_id": project["id"],
        "regression_proposal": latest_proposal,
        "trace_learning": summary,
    }


def get_project_trace_learning_regression_proposals(product_root: Path, repo_root: Path, project_id: str) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    path = trace_learning_regression_proposals_path(project_root)
    reviews_path = trace_learning_regression_proposal_reviews_path(project_root)
    proposals = load_trace_learning_regression_proposals(path)
    reviews = load_trace_learning_regression_proposal_reviews(reviews_path)
    proposal_ids = {str(proposal.get("id")) for proposal in proposals}
    proposal_reviews = [review for review in reviews if str(review.get("proposal_id")) in proposal_ids]
    summary = build_trace_learning_regression_proposal_summary(path, len(proposals), proposal_reviews)
    summary["regression_proposals"] = enrich_regression_proposals_with_review_status(proposals, proposal_reviews)
    summary["proposal_reviews"] = proposal_reviews
    return {"project_id": project["id"], "trace_learning": summary}


def review_project_trace_learning_regression_proposal(
    product_root: Path,
    repo_root: Path,
    project_id: str,
    proposal_id: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    proposals_path = trace_learning_regression_proposals_path(project_root)
    reviews_path = trace_learning_regression_proposal_reviews_path(project_root)
    proposals = load_trace_learning_regression_proposals(proposals_path)
    proposal = next((item for item in proposals if str(item.get("id")) == proposal_id), None)
    if proposal is None:
        raise TraceLearningProposalBlockedError(
            "trace_learning_proposal_not_found",
            f"Trace Learning regression proposal {proposal_id} does not exist.",
        )

    existing_reviews = load_trace_learning_regression_proposal_reviews(reviews_path)
    decision = normalize_review_decision(payload.get("decision"))
    review = {
        "id": build_regression_proposal_review_id(existing_reviews, proposal_id),
        "trace_learning_version": 1,
        "status": status_for_review_decision(decision),
        "created_at": utc_now(),
        "project_id": project["id"],
        "proposal_id": proposal_id,
        "decision": decision,
        "reviewer": str(payload.get("reviewer") or "human"),
        "note": str(payload.get("note") or ""),
        "writes_formal_layer": False,
        "canonical_rule_write_allowed": False,
        "test_file_write_allowed": False,
        "artifact_path": TRACE_LEARNING_REGRESSION_PROPOSAL_REVIEWS_PATH.as_posix(),
        "next_action": next_action_for_review_decision(decision),
    }

    reviews_path.parent.mkdir(parents=True, exist_ok=True)
    with reviews_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(review, ensure_ascii=False, sort_keys=True) + "\n")

    proposal_reviews = existing_reviews + [review]
    summary = build_trace_learning_regression_proposal_summary(
        proposals_path,
        len(proposals),
        proposal_reviews,
    )
    enriched_proposals = enrich_regression_proposals_with_review_status(proposals, proposal_reviews)
    enriched_proposal = next((item for item in enriched_proposals if str(item.get("id")) == proposal_id), proposal)
    summary["regression_proposals"] = enriched_proposals
    summary["proposal_reviews"] = proposal_reviews
    return {
        "project_id": project["id"],
        "regression_proposal": enriched_proposal,
        "regression_proposal_review": review,
        "trace_learning": summary,
    }


def generate_project_trace_learning_regression_test_patch_proposal(
    product_root: Path,
    repo_root: Path,
    project_id: str,
    proposal_id: str,
) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    proposals_path = trace_learning_regression_proposals_path(project_root)
    reviews_path = trace_learning_regression_proposal_reviews_path(project_root)
    patch_proposals_path = trace_learning_regression_test_patch_proposals_path(project_root)
    proposals = load_trace_learning_regression_proposals(proposals_path)
    proposal = next((item for item in proposals if str(item.get("id")) == proposal_id), None)
    if proposal is None:
        raise TraceLearningProposalBlockedError(
            "trace_learning_proposal_not_found",
            f"Trace Learning regression proposal {proposal_id} does not exist.",
        )

    reviews = load_trace_learning_regression_proposal_reviews(reviews_path)
    latest_review = latest_review_by_proposal_id(reviews).get(proposal_id)
    if latest_review is None or latest_review.get("status") != "approved":
        raise TraceLearningProposalBlockedError(
            "trace_learning_regression_proposal_approval_required",
            "Trace Learning regression proposal must be approved before preparing a test patch proposal.",
        )

    existing_patch_proposals = load_trace_learning_regression_test_patch_proposals(patch_proposals_path)
    existing_for_proposal = [
        item for item in existing_patch_proposals if str(item.get("proposal_id") or "") == proposal_id
    ]
    if existing_for_proposal:
        patch_proposal = existing_for_proposal[-1]
        summary = build_trace_learning_regression_test_patch_proposal_summary(
            patch_proposals_path,
            len(existing_patch_proposals),
        )
        summary["latest_patch_proposal"] = patch_proposal
        return {
            "project_id": project["id"],
            "regression_test_patch_proposal": patch_proposal,
            "trace_learning": summary,
        }

    patch_layer = normalize_fix_layer(proposal.get("patch_layer"))
    suggested_tests = proposal.get("suggested_tests") if isinstance(proposal.get("suggested_tests"), list) else []
    patch_proposal = {
        "id": build_regression_test_patch_proposal_id(existing_patch_proposals, proposal_id),
        "trace_learning_version": 1,
        "status": "needs_review",
        "created_at": utc_now(),
        "project_id": project["id"],
        "proposal_id": proposal_id,
        "source_bad_case_ids": normalize_string_list(proposal.get("source_bad_case_ids")),
        "patch_layer": patch_layer,
        "approved_review_id": latest_review.get("id"),
        "proposed_test_cases": [
            build_regression_test_patch_case(suggested_test) for suggested_test in suggested_tests
        ],
        "writes_formal_layer": False,
        "test_file_write_allowed": False,
        "canonical_rule_write_allowed": False,
        "requires_human_review": True,
        "artifact_path": TRACE_LEARNING_REGRESSION_TEST_PATCH_PROPOSALS_PATH.as_posix(),
        "next_action": "human_review_regression_test_patch",
    }

    patch_proposals_path.parent.mkdir(parents=True, exist_ok=True)
    with patch_proposals_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(patch_proposal, ensure_ascii=False, sort_keys=True) + "\n")

    summary = build_trace_learning_regression_test_patch_proposal_summary(
        patch_proposals_path,
        len(existing_patch_proposals) + 1,
    )
    summary["latest_patch_proposal"] = patch_proposal
    return {
        "project_id": project["id"],
        "regression_test_patch_proposal": patch_proposal,
        "trace_learning": summary,
    }


def load_trace_learning_bad_cases(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    cases: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            cases.append(json.loads(line))
    return cases


def load_trace_learning_regression_proposals(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    proposals: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            proposals.append(json.loads(line))
    return proposals


def load_trace_learning_regression_proposal_reviews(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    reviews: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            reviews.append(json.loads(line))
    return reviews


def load_trace_learning_regression_test_patch_proposals(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    patch_proposals: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            patch_proposals.append(json.loads(line))
    return patch_proposals


def build_trace_learning_summary(path: Path, case_count: int) -> dict[str, Any]:
    return {
        "path": TRACE_LEARNING_BAD_CASES_PATH.as_posix(),
        "case_count": case_count,
        "absolute_path": str(path),
        "allowed_fix_layers": ALLOWED_TRACE_LEARNING_FIX_LAYERS,
    }


def build_trace_learning_regression_proposal_summary(
    path: Path,
    proposal_count: int,
    reviews: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    review_records = reviews or []
    return {
        "path": TRACE_LEARNING_REGRESSION_PROPOSALS_PATH.as_posix(),
        "proposal_count": proposal_count,
        "absolute_path": str(path),
        "proposal_status": "needs_review",
        "review_path": TRACE_LEARNING_REGRESSION_PROPOSAL_REVIEWS_PATH.as_posix(),
        "review_count": len(review_records),
        "review_status_by_proposal_id": latest_review_status_by_proposal_id(review_records),
    }


def build_trace_learning_regression_test_patch_proposal_summary(
    path: Path,
    patch_proposal_count: int,
) -> dict[str, Any]:
    return {
        "path": TRACE_LEARNING_REGRESSION_TEST_PATCH_PROPOSALS_PATH.as_posix(),
        "patch_proposal_count": patch_proposal_count,
        "absolute_path": str(path),
        "proposal_status": "needs_review",
    }


def enrich_regression_proposals_with_review_status(
    proposals: list[dict[str, Any]],
    reviews: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    latest_reviews = latest_review_by_proposal_id(reviews)
    enriched: list[dict[str, Any]] = []
    for proposal in proposals:
        proposal_id = str(proposal.get("id") or "")
        latest_review = latest_reviews.get(proposal_id)
        item = dict(proposal)
        current_review_status = latest_review.get("status") if latest_review else proposal.get("status")
        item["current_review_status"] = str(current_review_status or "needs_review")
        item["latest_review_id"] = latest_review.get("id") if latest_review else None
        enriched.append(item)
    return enriched


def build_suggested_regression_test(bad_case: dict[str, Any]) -> dict[str, Any]:
    source_bad_case_id = str(bad_case.get("id") or "unknown")
    stage = str(bad_case.get("stage") or "unknown")
    surface = str(bad_case.get("surface") or "unknown")
    feedback = str(bad_case.get("user_feedback") or "同类问题")
    expected_behavior = str(bad_case.get("expected_behavior") or "系统应避免重复该坏案例。")
    return {
        "id": f"test_{source_bad_case_id}",
        "source_bad_case_id": source_bad_case_id,
        "target_kind": "contract_test",
        "target_stage": stage,
        "bdd": (
            f"Given 用户在 {surface} 的 {stage} 阶段指出坏案例；"
            f"When 系统再次处理相似输入或相同页面反馈；"
            f"Then 不得重复出现：{feedback}，并且应满足：{expected_behavior}"
        ),
        "suggested_test_name": f"test_trace_learning_regression_{slugify(stage)}",
    }


def build_regression_test_patch_case(suggested_test: dict[str, Any]) -> dict[str, Any]:
    source_bad_case_id = str(suggested_test.get("source_bad_case_id") or "unknown")
    target_stage = str(suggested_test.get("target_stage") or "unknown")
    suggested_test_name = str(
        suggested_test.get("suggested_test_name")
        or f"test_trace_learning_regression_{slugify(target_stage)}"
    )
    bdd = str(
        suggested_test.get("bdd")
        or "Given 已确认坏案例；When 添加回归测试；Then 系统不应重复该问题。"
    )
    return {
        "id": f"test_patch_case_{slugify(suggested_test.get('id') or source_bad_case_id)}",
        "source_bad_case_id": source_bad_case_id,
        "target_file": "tests/test_trace_learning.py",
        "target_kind": str(suggested_test.get("target_kind") or "contract_test"),
        "target_stage": target_stage,
        "suggested_test_name": suggested_test_name,
        "bdd": bdd,
        "patch_intent": "Add a failing regression test before changing production behavior.",
        "expected_assertion": "The same bad case is preserved as an executable contract test.",
    }


def normalize_fix_layer(value: Any) -> str:
    fix_layer = str(value or "").strip()
    if fix_layer in ALLOWED_TRACE_LEARNING_FIX_LAYERS:
        return fix_layer
    return "eval_set"


def normalize_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if str(item).strip()]


def normalize_review_decision(value: Any) -> str:
    decision = str(value or "").strip()
    if decision in {"approve", "request_revision", "reject"}:
        return decision
    raise TraceLearningProposalBlockedError(
        "invalid_trace_learning_review_decision",
        "Trace Learning regression proposal review decision must be approve, request_revision, or reject.",
    )


def status_for_review_decision(decision: str) -> str:
    return {
        "approve": "approved",
        "request_revision": "needs_revision",
        "reject": "rejected",
    }[decision]


def next_action_for_review_decision(decision: str) -> str:
    return {
        "approve": "prepare_regression_test_patch",
        "request_revision": "revise_regression_proposal",
        "reject": "close_regression_proposal",
    }[decision]


def latest_review_status_by_proposal_id(reviews: list[dict[str, Any]]) -> dict[str, str]:
    return {
        proposal_id: str(review.get("status") or "unknown")
        for proposal_id, review in latest_review_by_proposal_id(reviews).items()
    }


def latest_review_by_proposal_id(reviews: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    for review in reviews:
        proposal_id = str(review.get("proposal_id") or "")
        if proposal_id:
            latest[proposal_id] = review
    return latest


def build_bad_case_id(existing_cases: list[dict[str, Any]], stage: Any) -> str:
    return f"bad_case_{len(existing_cases) + 1:04d}_{slugify(stage or 'unknown')}"


def build_regression_proposal_id(existing_proposals: list[dict[str, Any]], patch_layer: Any) -> str:
    return f"regression_proposal_{len(existing_proposals) + 1:04d}_{slugify(patch_layer or 'unknown')}"


def build_regression_proposal_review_id(existing_reviews: list[dict[str, Any]], proposal_id: Any) -> str:
    return f"regression_proposal_review_{len(existing_reviews) + 1:04d}_{slugify(proposal_id or 'unknown')}"


def build_regression_test_patch_proposal_id(existing_patch_proposals: list[dict[str, Any]], proposal_id: Any) -> str:
    return f"regression_test_patch_proposal_{len(existing_patch_proposals) + 1:04d}_{slugify(proposal_id or 'unknown')}"


def slugify(value: Any) -> str:
    text = str(value).strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_") or "unknown"
