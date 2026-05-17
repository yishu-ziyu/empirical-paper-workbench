from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from Product.backend.manuscript_candidate_service import get_project_export_package
from Product.backend.project_service import utc_now
from Product.backend.registry import get_project_by_id
from Product.backend.results_draft_service import project_root_for


VERIFIER_CHECKS_PATH = "state/product/verifier_checks.json"
RUN_PLAN_PATH = "state/product/run_plan.json"
DEFAULT_METHOD_EXECUTION_PATH = "Results/json/method_execution_result.json"


class ExportCandidateRequiredError(ValueError):
    pass


def verifier_checks_state_path(project_root: Path) -> Path:
    return project_root / VERIFIER_CHECKS_PATH


def get_project_verifier_checks(product_root: Path, repo_root: Path, project_id: str) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = project_root_for(project)
    package = require_export_package(product_root, repo_root, project_id)
    existing = load_verifier_checks(project_root)
    if existing:
        return existing
    return build_verifier_checks(project_root, project_id, package, persist=False)


def run_project_verifier_checks(product_root: Path, repo_root: Path, project_id: str) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = project_root_for(project)
    package = require_export_package(product_root, repo_root, project_id)
    payload = build_verifier_checks(project_root, project_id, package, persist=True)
    path = verifier_checks_state_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def require_export_package(product_root: Path, repo_root: Path, project_id: str) -> dict[str, Any]:
    packages = get_project_export_package(product_root, repo_root, project_id).get("packages", [])
    if not packages:
        raise ExportCandidateRequiredError("export_candidate_required")
    return packages[0]


def load_verifier_checks(project_root: Path) -> dict[str, Any] | None:
    path = verifier_checks_state_path(project_root)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def build_verifier_checks(
    project_root: Path,
    project_id: str,
    package: dict[str, Any],
    persist: bool,
) -> dict[str, Any]:
    checks = [
        build_result_binding_check(project_root, package),
        build_path_check(
            project_root,
            "repro_manifest",
            "复现清单",
            package.get("manifest_path") or "state/product/export_package_manifest.json",
            "local_file",
        ),
        build_path_check(project_root, "run_plan_artifact", "运行计划", RUN_PLAN_PATH, "local_file"),
        build_path_check(
            project_root,
            "analysis_result_artifact",
            "分析结果产物",
            package.get("result_artifact_path") or "Results/json/analysis_result.json",
            "local_execution",
        ),
        build_method_execution_check(project_root, package),
        build_path_check(
            project_root,
            "draft_preview_exists",
            "草稿预览",
            package.get("writeback_preview_path") or "",
            "local_file",
        ),
    ]
    checks.append(build_evidence_levels_check(checks, package))
    checks.append(build_docx_export_preflight_check(project_root, package))
    can_export_docx = all(check.get("status") == "passed" for check in checks)
    return {
        "_meta": {
            "evidence_level": "local_file",
            "service": "verifier_service",
            "generated_at": utc_now(),
        },
        "project_id": project_id,
        "status": "passed" if can_export_docx else "failed",
        "can_export_docx": can_export_docx,
        "candidate_id": package.get("candidate_id"),
        "package_id": package.get("id"),
        "verifier_state_path": VERIFIER_CHECKS_PATH,
        "mode": "persisted" if persist else "preview",
        "checks": checks,
        "docx_export_preflight": checks[-1],
        "next_manual_action": (
            "核验通过后，可由人工执行 docx 导出。"
            if can_export_docx
            else "先处理失败或阻断的 verifier checks，再进入 docx 导出。"
        ),
    }


def build_result_binding_check(project_root: Path, package: dict[str, Any]) -> dict[str, Any]:
    result_path = package.get("result_artifact_path") or "Results/json/analysis_result.json"
    candidate_id = package.get("candidate_id")
    finding_id = package.get("finding_id")
    passed = bool(candidate_id and finding_id and result_path and (project_root / result_path).exists())
    return {
        "id": "result_binding",
        "label": "结果绑定",
        "status": "passed" if passed else "failed",
        "evidence_level": "local_execution",
        "artifact_paths": [result_path],
        "candidate_id": candidate_id,
        "finding_id": finding_id,
        "detail": "正文候选、结果论断卡与结果产物已绑定" if passed else "缺少正文候选、结果论断卡或结果产物",
    }


def build_method_execution_check(project_root: Path, package: dict[str, Any]) -> dict[str, Any]:
    artifact_path = DEFAULT_METHOD_EXECUTION_PATH
    run_id = package.get("run_id")
    if run_id:
        manifest_path = project_root / "state" / "runs" / run_id / "run_manifest.json"
        if manifest_path.exists():
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            artifact_path = ((manifest.get("method_execution") or {}).get("artifact_path")) or artifact_path
    status = "passed" if artifact_path and (project_root / artifact_path).exists() else "failed"
    return {
        "id": "method_execution_artifact",
        "label": "方法执行产物",
        "status": status,
        "evidence_level": "local_execution",
        "artifact_paths": [artifact_path],
        "detail": "方法执行证据存在" if status == "passed" else "缺少方法执行证据",
    }


def build_path_check(
    project_root: Path,
    check_id: str,
    label: str,
    artifact_path: str,
    evidence_level: str,
) -> dict[str, Any]:
    status = "passed" if artifact_path and (project_root / artifact_path).exists() else "failed"
    return {
        "id": check_id,
        "label": label,
        "status": status,
        "evidence_level": evidence_level,
        "artifact_paths": [artifact_path],
    }


def build_evidence_levels_check(checks: list[dict[str, Any]], package: dict[str, Any]) -> dict[str, Any]:
    allowed = {"local_file", "local_execution"}
    levels = [check.get("evidence_level") for check in checks]
    levels.extend([
        package.get("evidence_level"),
        (package.get("writeback_approval") or {}).get("evidence_level"),
        (package.get("docx_preflight") or {}).get("evidence_level"),
    ])
    invalid = [level for level in levels if level and level not in allowed]
    return {
        "id": "evidence_levels_valid",
        "label": "证据等级",
        "status": "failed" if invalid else "passed",
        "evidence_level": "local_file",
        "artifact_paths": [VERIFIER_CHECKS_PATH],
        "detail": "仅允许 local_file / local_execution" if not invalid else f"发现非法证据等级: {', '.join(invalid)}",
    }


def build_docx_export_preflight_check(project_root: Path, package: dict[str, Any]) -> dict[str, Any]:
    preflight = package.get("docx_preflight") or {}
    checks = preflight.get("checks") or []
    preflight_path = preflight.get("path") or "state/product/docx_export_preflight.json"
    ready = preflight.get("status") == "ready" and all(check.get("status") == "passed" for check in checks)
    return {
        "id": "docx_export_preflight",
        "label": "docx 导出预检",
        "status": "passed" if ready and (project_root / preflight_path).exists() else "blocked",
        "evidence_level": "local_file",
        "artifact_paths": [preflight_path],
        "detail": "docx 预检已通过" if ready else "docx 预检尚未通过，最终导出保持禁用",
    }
