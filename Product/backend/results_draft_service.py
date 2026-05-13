from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from Product.backend.project_service import utc_now
from Product.backend.registry import get_project_by_id
from Product.backend.run_store import get_run, list_runs


RESULT_ARTIFACT_PATH = "Results/json/analysis_result.json"
DRAFT_ARTIFACT_PATH = "Manuscripts/generated/paper_draft.md"
VALID_REVIEW_ACTIONS = {"approve": "approved", "reject": "rejected", "needs_revision": "needs_revision"}


class FindingNotFoundError(KeyError):
    pass


class InvalidReviewActionError(ValueError):
    pass


def local_execution_meta(service: str) -> dict[str, str]:
    return {
        "evidence_level": "local_execution",
        "service": service,
        "generated_at": utc_now(),
    }


def project_root_for(project: dict[str, Any]) -> Path:
    return Path(project.get("project_root") or project["root"]).resolve()


def get_project_results_draft(product_root: Path, repo_root: Path, project_id: str) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    root = project_root_for(project)
    run = latest_successful_full_run(root)
    if run is None:
        raise FileNotFoundError("successful full run is required before reviewing findings and draft evidence")

    result_path = root / RESULT_ARTIFACT_PATH
    if not result_path.exists():
        raise ValueError(f"missing result artifact: {RESULT_ARTIFACT_PATH}")

    analysis_result = json.loads(result_path.read_text(encoding="utf-8"))
    manifest = load_manifest(root, run["id"])
    plan_binding = run.get("plan_binding") or manifest.get("run_plan_binding") or {}
    method_execution = load_method_execution(root, run, manifest)
    findings = apply_finding_reviews(root, build_findings(run, analysis_result, plan_binding, method_execution))
    return {
        "_meta": local_execution_meta("results_draft_service"),
        "project_id": project_id,
        "latest_run_id": run["id"],
        "run_plan_version": plan_binding.get("run_plan_version"),
        "result_artifact": artifact_reference(root, RESULT_ARTIFACT_PATH, "local_execution"),
        "method_execution": method_execution,
        "draft_artifact": artifact_reference(root, DRAFT_ARTIFACT_PATH, "local_file"),
        "findings": findings,
        "draft_sections": build_draft_sections(root, run, plan_binding),
        "empty_state": None,
    }


def save_project_finding_review(
    product_root: Path,
    repo_root: Path,
    project_id: str,
    finding_id: str,
    action: str,
    note: str,
) -> dict[str, Any]:
    if action not in VALID_REVIEW_ACTIONS:
        raise InvalidReviewActionError(action)

    project = get_project_by_id(product_root, repo_root, project_id)
    root = project_root_for(project)
    results_draft = get_project_results_draft(product_root, repo_root, project_id)
    finding = next((item for item in results_draft.get("findings", []) if item.get("id") == finding_id), None)
    if not finding:
        raise FindingNotFoundError(finding_id)

    review_status = VALID_REVIEW_ACTIONS[action]
    review = {
        "id": f"review_{finding_id}",
        "finding_id": finding_id,
        "review_status": review_status,
        "action": action,
        "actor": "user",
        "note": note,
        "timestamp": utc_now(),
        "evidence_level": "local_file",
        "run_id": finding.get("run_id"),
        "run_plan_version": finding.get("run_plan_version"),
        "artifact_path": finding.get("artifact_path"),
        "result_evidence_level": finding.get("evidence_level"),
        "can_write_to_draft": review_status == "approved",
    }
    state = load_finding_reviews(root)
    state["reviews"][finding_id] = review
    path = finding_review_state_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "_meta": {
            "evidence_level": "local_file",
            "service": "results_draft_service",
            "generated_at": utc_now(),
        },
        "project_id": project_id,
        "review": review,
    }


def latest_successful_full_run(project_root: Path) -> dict[str, Any] | None:
    candidates = [
        item
        for item in list_runs(project_root)
        if item.get("mode") == "full-run" and item.get("status") == "succeeded"
    ]
    if not candidates:
        return None
    candidates.sort(key=lambda item: item.get("finished_at") or item.get("started_at") or "", reverse=True)
    return get_run(project_root, candidates[0]["id"])


def load_manifest(project_root: Path, run_id: str) -> dict[str, Any]:
    path = project_root / "state" / "runs" / run_id / "run_manifest.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def load_method_execution(project_root: Path, run: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any] | None:
    method_execution = run.get("method_execution") or manifest.get("method_execution")
    if not method_execution:
        return None

    artifact_path = method_execution.get("artifact_path")
    if artifact_path:
        path = project_root / artifact_path
        if path.exists():
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload.setdefault("artifact_path", artifact_path)
            payload.setdefault("engine", method_execution.get("engine"))
            payload.setdefault("evidence_level", method_execution.get("evidence_level", "local_execution"))
            payload.setdefault("methods", method_execution.get("methods", []))
            return payload

    return {
        "artifact_path": artifact_path,
        "engine": method_execution.get("engine"),
        "evidence_level": method_execution.get("evidence_level", "local_execution"),
        "methods": method_execution.get("methods", []),
    }


def artifact_reference(project_root: Path, relative_path: str, evidence_level: str) -> dict[str, Any]:
    path = project_root / relative_path
    return {
        "path": relative_path,
        "exists": path.exists(),
        "evidence_level": evidence_level,
    }


def finding_review_state_path(project_root: Path) -> Path:
    return project_root / "state" / "product" / "finding_reviews.json"


def load_finding_reviews(project_root: Path) -> dict[str, Any]:
    path = finding_review_state_path(project_root)
    if not path.exists():
        return {
            "_meta": {
                "evidence_level": "local_file",
                "service": "results_draft_service",
            },
            "reviews": {},
        }
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload.setdefault("reviews", {})
    return payload


def apply_finding_reviews(project_root: Path, findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    reviews = load_finding_reviews(project_root).get("reviews", {})
    reviewed_findings: list[dict[str, Any]] = []
    for finding in findings:
        review = matching_review(finding, reviews.get(finding.get("id")))
        status = review.get("review_status") if review else "needs_review"
        item = {
            **finding,
            "review_status": status,
            "can_write_to_draft": status == "approved",
            "review": review,
        }
        reviewed_findings.append(item)
    return reviewed_findings


def matching_review(finding: dict[str, Any], review: dict[str, Any] | None) -> dict[str, Any] | None:
    if not review:
        return None
    if review.get("run_id") != finding.get("run_id"):
        return None
    if review.get("artifact_path") != finding.get("artifact_path"):
        return None
    return review


def build_findings(
    run: dict[str, Any],
    analysis_result: dict[str, Any],
    plan_binding: dict[str, Any],
    method_execution: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    result_payload = analysis_result.get("result_payload") or {}
    coefficients = result_payload.get("coefficients") or {}
    treatment = (
        ((analysis_result.get("draft") or {}).get("parsed_hints") or {}).get("treatment")
        or first_treatment_name(coefficients)
    )
    coefficient = coefficients.get(treatment or "")
    if not treatment or not coefficient:
        return []
    dependent_var = result_payload.get("dependent_var") or ((analysis_result.get("draft") or {}).get("parsed_hints") or {}).get("y")
    return [
        {
            "id": f"finding_{slugify(treatment)}_effect",
            "title": f"{treatment} effect on {dependent_var or 'outcome'}",
            "run_id": run["id"],
            "run_plan_version": plan_binding.get("run_plan_version"),
            "artifact_path": RESULT_ARTIFACT_PATH,
            "evidence_level": "local_execution",
            "treatment": treatment,
            "dependent_var": dependent_var,
            "model_type": result_payload.get("model_type") or result_payload.get("method"),
            "sample_size": result_payload.get("n_obs"),
            "estimate": coefficient.get("estimate"),
            "std_error": coefficient.get("std_error"),
            "p_value": coefficient.get("p_value"),
            "conf_low": coefficient.get("conf_low"),
            "conf_high": coefficient.get("conf_high"),
            "method_evidence": build_method_evidence(treatment, method_execution),
        }
    ]


def build_method_evidence(treatment: str, method_execution: dict[str, Any] | None) -> dict[str, Any] | None:
    if not method_execution:
        return None

    methods = method_execution.get("methods") or []
    method = next(
        (
            item
            for item in methods
            if item.get("treatment") == treatment or treatment in (item.get("coefficients") or {})
        ),
        methods[0] if methods else None,
    )
    if not method:
        return None

    return {
        "artifact_path": method_execution.get("artifact_path"),
        "engine": method_execution.get("engine"),
        "evidence_level": method.get("evidence_level") or method_execution.get("evidence_level", "local_execution"),
        "method_id": method.get("method_id") or method.get("estimator"),
        "formula": method.get("formula"),
        "dataset_path": method.get("dataset_path"),
        "run_plan_version": method.get("run_plan_version"),
        "nobs": method.get("nobs"),
        "treatment": method.get("treatment") or treatment,
        "treatment_coefficient": method.get("treatment_coefficient"),
    }


def first_treatment_name(coefficients: dict[str, Any]) -> str | None:
    for name in coefficients:
        if name.lower() != "intercept":
            return name
    return None


def build_draft_sections(project_root: Path, run: dict[str, Any], plan_binding: dict[str, Any]) -> list[dict[str, Any]]:
    draft_path = project_root / DRAFT_ARTIFACT_PATH
    if not draft_path.exists():
        return []
    sections = parse_markdown_sections(draft_path.read_text(encoding="utf-8"))
    return [
        {
            "id": f"draft_section_{slugify(title)}",
            "title": title,
            "content": content.strip(),
            "source_path": DRAFT_ARTIFACT_PATH,
            "source_evidence_level": "local_file",
            "evidence_binding": {
                "run_id": run["id"],
                "run_plan_version": plan_binding.get("run_plan_version"),
                "artifact_path": RESULT_ARTIFACT_PATH,
                "claim_evidence_level": "local_execution",
            },
        }
        for title, content in sections
    ]


def parse_markdown_sections(markdown: str) -> list[tuple[str, str]]:
    matches = list(re.finditer(r"^##\s+(.+?)\s*$", markdown, flags=re.MULTILINE))
    if not matches:
        return [("Draft", markdown)]
    sections: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        title = match.group(1).strip()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
        sections.append((title, markdown[start:end].strip()))
    return sections


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip()).strip("_").lower()
    return slug or "item"
