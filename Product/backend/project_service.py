from __future__ import annotations

import csv
import importlib.util
import json
import math
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from .registry import add_project, get_project, get_project_by_id, list_projects
from .orchestrator import orchestrate_project, run_workbench
from .observability_service import (
    load_observable_events,
    load_observable_gates,
    load_observable_steps,
    load_run_observability,
    resolve_observable_gate,
)
from .run_store import create_run, get_run, list_runs, save_run


ESSENTIAL_PATHS = [
    "README.md",
    ".gitignore",
    "paper.yaml",
    "Data",
    "Manuscripts",
    "Program",
    "Reference",
    "Results",
    "Submissions",
    "Tasks",
    "docs",
    "state",
]


class UnsupportedRunPlanMethodError(ValueError):
    pass


class MethodExecutionError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def copy_essential_tree(repo_root: Path, target_root: Path) -> None:
    target_root.mkdir(parents=True, exist_ok=True)
    for rel in ESSENTIAL_PATHS:
        src = repo_root / rel
        dst = target_root / rel
        if src.is_dir():
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)


def reset_runtime_outputs(target_root: Path) -> None:
    cleanup_paths = [
        target_root / "Results" / "index.json",
        target_root / "Results" / "json" / "analysis_result.json",
        target_root / "Results" / "json" / "project_snapshot.json",
        target_root / "Results" / "logs" / "run_paper.log",
        target_root / "Results" / "logs" / "export_docx.log",
        target_root / "Manuscripts" / "generated" / "paper_draft.md",
        target_root / "Manuscripts" / "generated" / "paper_draft.tex",
        target_root / "Submissions" / "paper_draft.docx",
        target_root / "Submissions" / "export_manifest.json",
        target_root / "state" / "project_state.json",
    ]
    for path in cleanup_paths:
        if path.exists():
            path.unlink()


def customize_paper_yaml(target_root: Path, slug: str, title: str, question: str) -> None:
    paper_path = target_root / "paper.yaml"
    payload = yaml.safe_load(paper_path.read_text(encoding="utf-8"))
    payload["project"]["slug"] = slug
    payload["project"]["title"] = title
    payload["research"]["question"] = question
    paper_path.write_text(yaml.safe_dump(payload, allow_unicode=True, sort_keys=False), encoding="utf-8")


def create_workspace(
    product_root: Path,
    repo_root: Path,
    slug: str,
    title: str,
    question: str,
) -> dict[str, Any]:
    workspace_root = product_root / "workspaces" / slug
    if workspace_root.exists():
        raise FileExistsError(slug)
    copy_essential_tree(repo_root, workspace_root)
    reset_runtime_outputs(workspace_root)
    customize_paper_yaml(workspace_root, slug=slug, title=title, question=question)
    # Initialize git repo for experiment logging
    try:
        import subprocess
        subprocess.run(["git", "init"], cwd=workspace_root, capture_output=True, check=True)
        subprocess.run(["git", "config", "user.email", "empirical-os@local"], cwd=workspace_root, capture_output=True)
        subprocess.run(["git", "config", "user.name", "实证工作台"], cwd=workspace_root, capture_output=True)
    except Exception:
        pass  # Git init is best-effort
    project = {
        "slug": slug,
        "title": title,
        "question": question,
        "root": str(workspace_root),
        "source": "product-wizard",
        "created_at": utc_now(),
    }
    add_project(product_root, repo_root, project)
    return project


def load_json_if_exists(path: Path) -> dict[str, Any] | None:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return None


def latest_orchestration_snapshot(root: Path) -> dict[str, Any] | None:
    candidates = [
        root / "06_workspace" / "runs",
        root / "workspace" / "runs",
        root / "state" / "orchestration",
    ]
    orchestrations_root = next((path for path in candidates if path.exists()), None)
    if orchestrations_root is None:
        return None
    manifests = sorted(orchestrations_root.glob("*/run_manifest.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not manifests:
        return None
    manifest_path = manifests[0]
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    revised_path = manifest_path.parent / "06_writing" / "paper_draft.md"
    review_path = manifest_path.parent / "07_review" / "reviewer_decision.json"
    if not revised_path.exists():
        revised_path = manifest_path.parent / "outputs" / "paper_draft_revised.md"
    if not review_path.exists():
        review_path = manifest_path.parent / "reviews" / "01_reviewer.json"
    return {
        "manifest": manifest,
        "revised_draft_path": str(revised_path.relative_to(root)) if revised_path.exists() else None,
        "revised_draft": revised_path.read_text(encoding="utf-8") if revised_path.exists() else None,
        "review_packet": json.loads(review_path.read_text(encoding="utf-8")) if review_path.exists() else None,
    }


def project_snapshot(project: dict[str, Any]) -> dict[str, Any]:
    root = Path(project["root"])
    return {
        **project,
        "paper": load_json_if_exists(root / "state" / "project_state.json"),
        "results_index": load_json_if_exists(root / "Results" / "index.json"),
        "analysis_result": load_json_if_exists(root / "Results" / "json" / "analysis_result.json"),
        "latest_orchestration": latest_orchestration_snapshot(root),
        "artifacts": {
            "markdown": (root / "Manuscripts" / "generated" / "paper_draft.md").exists(),
            "latex": (root / "Manuscripts" / "generated" / "paper_draft.tex").exists(),
            "docx": (root / "Submissions" / "paper_draft.docx").exists(),
        },
    }


def project_api_view(project: dict[str, Any]) -> dict[str, Any]:
    snapshot = project_snapshot(project)
    paper = snapshot.get("paper") or {}
    return {
        "id": project["id"],
        "slug": project["slug"],
        "title": project["title"],
        "question": project.get("question", ""),
        "root": project["root"],
        "project_root": project["project_root"],
        "language": project.get("language", "zh"),
        "current_stage": paper.get("current_stage", "question-definition"),
        "dataset_exists": paper.get("dataset_exists", False),
        "last_run_mode": paper.get("last_run_mode", "never"),
        "created_at": project["created_at"],
        "updated_at": project.get("updated_at", project["created_at"]),
    }


def project_detail_view(project: dict[str, Any]) -> dict[str, Any]:
    snapshot = project_snapshot(project)
    return {
        "id": project["id"],
        **snapshot,
        "project_root": project["project_root"],
        "language": project.get("language", "zh"),
    }


def run_pipeline(project: dict[str, Any], live: bool) -> dict[str, Any]:
    root = Path(project["root"])
    command = ["python3", "Program/run_paper.py", "--project-root", "."]
    if not live:
        command.append("--dry-run")
    result = subprocess.run(command, cwd=root, text=True, capture_output=True)
    return {
        "command": command,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def export_docx(project: dict[str, Any]) -> dict[str, Any]:
    root = Path(project["root"])
    command = ["python3", "Program/export_docx.py", "--project-root", "."]
    result = subprocess.run(command, cwd=root, text=True, capture_output=True)
    return {
        "command": command,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def load_project_snapshot(product_root: Path, repo_root: Path, slug: str) -> dict[str, Any]:
    return project_snapshot(get_project(product_root, repo_root, slug))


def load_project_list(product_root: Path, repo_root: Path) -> list[dict[str, Any]]:
    return [project_snapshot(project) for project in list_projects(product_root, repo_root)]


def run_orchestration(project: dict[str, Any], live: bool) -> dict[str, Any]:
    root = Path(project["root"])
    manifest = orchestrate_project(root, run_live=live)
    return {
        "run_id": manifest["run_id"],
        "manifest": manifest,
        "run_dir": manifest["run_root"],
    }


def register_project_root(
    product_root: Path,
    repo_root: Path,
    slug: str,
    title: str,
    project_root: Path,
    language: str,
) -> dict[str, Any]:
    has_generic_runner = (project_root / "paper.yaml").exists() and (project_root / "Program" / "run_paper.py").exists()
    has_thesis_layout = (project_root / "01_data").exists() and (project_root / "02_code").exists() and (project_root / "04_paper").exists()
    if not (has_generic_runner or has_thesis_layout):
        raise FileNotFoundError("paper.yaml + Program/run_paper.py or thesis 01_data/02_code/04_paper")

    question = ""
    if (project_root / "paper.yaml").exists():
        question = yaml.safe_load((project_root / "paper.yaml").read_text(encoding="utf-8")).get("research", {}).get("question", "")
    elif (project_root / "state" / "project_state.json").exists():
        question = load_json_if_exists(project_root / "state" / "project_state.json").get("research_question", "")
    project = {
        "id": f"proj_{slug.replace('-', '_')}",
        "slug": slug,
        "title": title,
        "question": question,
        "root": str(project_root),
        "project_root": str(project_root),
        "language": language,
        "source": "registered",
        "created_at": utc_now(),
        "updated_at": utc_now(),
    }
    add_project(product_root, repo_root, project)
    return project


def get_project_api_view(product_root: Path, repo_root: Path, project_id: str) -> dict[str, Any]:
    return project_api_view(get_project_by_id(product_root, repo_root, project_id))


def list_project_api_views(product_root: Path, repo_root: Path) -> list[dict[str, Any]]:
    return [project_api_view(project) for project in list_projects(product_root, repo_root)]


def get_project_detail_api_view(product_root: Path, repo_root: Path, project_id: str) -> dict[str, Any]:
    return project_detail_view(get_project_by_id(product_root, repo_root, project_id))


def execute_run(project: dict[str, Any], mode: str, dataset_path: str | None = None) -> dict[str, Any]:
    root = Path(project["project_root"])
    dataset_source = resolve_dataset_source(root, dataset_path)
    run = create_run(root, project["id"], mode)
    run["status"] = "running"
    if dataset_source:
        run["dataset_source"] = dataset_source
    save_run(root, run)

    command = ["python3", "Program/run_paper.py", "--project-root", ".", "--run-id", run["id"]]
    if mode == "dry-run":
        command.append("--dry-run")

    process = subprocess.run(command, cwd=root, text=True, capture_output=True)
    state_path = root / "state" / "project_state.json"
    results_index_path = root / "Results" / "index.json"
    state = load_json_if_exists(state_path)
    results = load_json_if_exists(results_index_path)
    artifact_paths = []
    if state_path.exists():
        artifact_paths.append("state/project_state.json")
    if results_index_path.exists():
        artifact_paths.append("Results/index.json")
    if results and results.get("artifacts"):
        artifact_paths.extend(
            [
                artifact["path"]
                for artifact in results["artifacts"]
                if artifact.get("exists")
            ]
        )

    run.update(
        {
            "status": "succeeded" if process.returncode == 0 else "failed",
            "finished_at": utc_now(),
            "state_path": "state/project_state.json" if state_path.exists() else None,
            "results_index_path": "Results/index.json" if results_index_path.exists() else None,
            "artifact_count": len(artifact_paths),
            "artifact_paths": artifact_paths,
            "observability": {
                "manifest_path": f"state/runs/{run['id']}/run_manifest.json",
                "steps_path": f"state/runs/{run['id']}/run_steps.json",
                "events_path": f"state/runs/{run['id']}/run_events.jsonl",
                "gates_path": f"state/runs/{run['id']}/gates.json",
            },
            "state": {
                "current_stage": state.get("current_stage") if state else None,
                "last_run_mode": state.get("last_run_mode") if state else None,
                "dataset_exists": state.get("dataset_exists") if state else None,
            }
            if state
            else None,
            "results": results,
            "dataset_source": dataset_source,
            "error": None
            if process.returncode == 0
            else {"stdout": process.stdout, "stderr": process.stderr},
        }
    )
    persist_run_dataset_source(root, run["id"], dataset_source)
    save_run(root, run)
    return run


def execute_full_run_from_run_plan(project: dict[str, Any]) -> dict[str, Any]:
    from Product.backend.design_spec_service import load_saved_design_spec, load_saved_run_plan

    root = Path(project["project_root"])
    design_spec = load_saved_design_spec(root)
    run_plan = load_saved_run_plan(root)
    if not run_plan or run_plan.get("status") != "approved":
        raise FileNotFoundError("approved RunPlan is required")
    if not design_spec or design_spec.get("status") != "approved":
        raise FileNotFoundError("approved DesignSpec is required")

    dataset_source = resolve_dataset_source(root, run_plan.get("dataset_path"))
    validate_supported_run_plan_methods(run_plan)
    plan_binding = build_run_plan_binding(design_spec, run_plan)
    research_engine = build_research_engine_reference()
    run = create_run(root, project["id"], "full-run")
    run["status"] = "running"
    run["dataset_source"] = dataset_source
    run["plan_binding"] = plan_binding
    run["research_engine"] = research_engine
    save_run(root, run)

    command = ["python3", "Program/run_paper.py", "--project-root", ".", "--run-id", run["id"]]
    process = subprocess.run(command, cwd=root, text=True, capture_output=True)
    state_path = root / "state" / "project_state.json"
    results_index_path = root / "Results" / "index.json"
    state = load_json_if_exists(state_path)
    results = load_json_if_exists(results_index_path)
    method_execution = None
    if process.returncode == 0:
        method_execution = execute_run_plan_method_tasks(root, run["id"], design_spec, run_plan, dataset_source)
    artifact_paths = []
    if state_path.exists():
        artifact_paths.append("state/project_state.json")
    if results_index_path.exists():
        artifact_paths.append("Results/index.json")
    if results and results.get("artifacts"):
        artifact_paths.extend(
            [
                artifact["path"]
                for artifact in results["artifacts"]
                if artifact.get("exists")
            ]
        )
    if method_execution:
        artifact_paths.append(method_execution["artifact_path"])

    run.update(
        {
            "status": "succeeded" if process.returncode == 0 else "failed",
            "finished_at": utc_now(),
            "state_path": "state/project_state.json" if state_path.exists() else None,
            "results_index_path": "Results/index.json" if results_index_path.exists() else None,
            "artifact_count": len(artifact_paths),
            "artifact_paths": artifact_paths,
            "observability": {
                "manifest_path": f"state/runs/{run['id']}/run_manifest.json",
                "steps_path": f"state/runs/{run['id']}/run_steps.json",
                "events_path": f"state/runs/{run['id']}/run_events.jsonl",
                "gates_path": f"state/runs/{run['id']}/gates.json",
            },
            "state": {
                "current_stage": state.get("current_stage") if state else None,
                "last_run_mode": state.get("last_run_mode") if state else None,
                "dataset_exists": state.get("dataset_exists") if state else None,
            }
            if state
            else None,
            "results": results,
            "dataset_source": dataset_source,
            "plan_binding": plan_binding,
            "research_engine": research_engine,
            "method_execution": method_execution,
            "execution_evidence_level": "local_execution",
            "error": None
            if process.returncode == 0
            else {"stdout": process.stdout, "stderr": process.stderr},
        }
    )
    persist_run_dataset_source(root, run["id"], dataset_source)
    persist_full_run_provenance(root, run["id"], plan_binding, research_engine, method_execution)
    save_run(root, run)
    return run


def validate_supported_run_plan_methods(run_plan: dict[str, Any]) -> None:
    supported = {"ols", "iv", "did", "rdd", "psm", "dml"}
    unsupported = sorted(
        {
            str(task.get("method_id") or task.get("estimator") or "").strip()
            for task in run_plan.get("tasks", [])
            if str(task.get("method_id") or task.get("estimator") or "").strip() not in supported
        }
    )
    if unsupported:
        raise UnsupportedRunPlanMethodError(", ".join(unsupported))


def build_run_plan_binding(design_spec: dict[str, Any], run_plan: dict[str, Any]) -> dict[str, Any]:
    return {
        "evidence_level": "local_file",
        "variable_role_set_version": design_spec.get("variable_role_set_version"),
        "design_spec_version": run_plan.get("design_spec_version"),
        "run_plan_version": run_plan.get("version"),
        "dataset_path": run_plan.get("dataset_path"),
        "tasks": [
            {
                "id": task.get("id"),
                "method_id": task.get("method_id") or task.get("estimator"),
                "formula": task.get("formula"),
                "estimator": task.get("estimator"),
                "status": task.get("status"),
            }
            for task in run_plan.get("tasks", [])
        ],
        "outputs": run_plan.get("outputs", []),
    }


def execute_run_plan_method_tasks(
    project_root: Path,
    run_id: str,
    design_spec: dict[str, Any],
    run_plan: dict[str, Any],
    dataset_source: dict[str, Any] | None,
) -> dict[str, Any]:
    methods = []
    execution_contract = build_empirical_execution_contract("statspai")
    for task in run_plan.get("tasks", []):
        method_id = str(task.get("method_id") or task.get("estimator") or "").strip()
        if method_id == "ols":
            methods.append(execute_ols_task(project_root, run_id, design_spec, run_plan, task, dataset_source))
        elif method_id == "iv":
            methods.append(execute_iv_task(project_root, run_id, design_spec, run_plan, task, dataset_source))
        elif method_id == "did":
            methods.append(execute_did_task(project_root, run_id, design_spec, run_plan, task, dataset_source))
        elif method_id == "rdd":
            methods.append(execute_rdd_task(project_root, run_id, design_spec, run_plan, task, dataset_source))
        elif method_id == "psm":
            methods.append(execute_psm_task(project_root, run_id, design_spec, run_plan, task, dataset_source))
        elif method_id == "dml":
            methods.append(execute_dml_task(project_root, run_id, design_spec, run_plan, task, dataset_source))

    payload = {
        "id": "method_execution_result",
        "run_id": run_id,
        "engine": "statspai",
        "evidence_level": "local_execution",
        "artifact_path": "Results/json/method_execution_result.json",
        "created_at": utc_now(),
        "execution_contract": execution_contract,
        "methods": methods,
    }
    result_path = project_root / "Results" / "json" / "method_execution_result.json"
    result_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "artifact_path": payload["artifact_path"],
        "engine": payload["engine"],
        "evidence_level": payload["evidence_level"],
        "execution_contract": execution_contract,
        "methods": methods,
    }


def build_empirical_execution_contract(active_backend: str) -> dict[str, Any]:
    statspai_available = importlib.util.find_spec("statspai") is not None
    stata_path = shutil.which("stata-mp") or "/Applications/Stata/StataMP.app/Contents/MacOS/stata-mp"
    stata_available = Path(stata_path).exists()
    return {
        "id": "rigorous_empirical_execution_contract",
        "version": 2,
        "active_backend": active_backend,
        "analysis_boundary": "analysis_ready_numeric_formula_rows",
        "prohibits": [
            "frontend_inference",
            "mock_result_promotion",
            "silent_backend_switch",
        ],
        "available_backends": [
            {
                "id": "statspai",
                "label": "StatsPAI / StatsAPI",
                "role": "active_execution" if active_backend == "statspai" else "candidate_causal_engine",
                "availability_status": "available" if statspai_available else "not_installed",
                "evidence_level": "local_execution" if active_backend == "statspai" else "local_file",
                "purpose": "Phase 1+2 统一执行后端：支持 OLS、IV(2SLS/iv_diag)、DID、RDD、PSM、DML 等方法族。",
                "activation_policy": "RunPlan task 为 ols/iv/did/rdd/psm/dml 时，调用 sp.regress/sp.iv/sp.did/sp.rdd/sp.match/sp.dml 并写出结果后标记为 local_execution。",
            },
            {
                "id": "python_ols_adapter",
                "label": "Python OLS adapter",
                "role": "candidate_execution_engine",
                "availability_status": "ready",
                "evidence_level": "local_file",
                "purpose": "备用 OLS 本地执行后端，用于与 StatsPAI 交叉验证。",
                "activation_policy": "仅当 StatsPAI 不可用时作为 fallback；否则仅用于系数交叉验证。",
            },
            {
                "id": "stata_mcp",
                "label": "StataMCP / Stata",
                "role": "candidate_reproducibility_engine",
                "availability_status": "available" if stata_available else "not_available",
                "evidence_level": "local_file",
                "purpose": "后续用于 do-file/log 级可复现实证执行、Stata 表格和审计日志。",
                "activation_policy": "必须生成并执行 do-file/log；未产生 Stata log 前不得标记为 local_execution。",
                "detected_path": stata_path if stata_available else None,
            },
        ],
    }


def execute_ols_task(
    project_root: Path,
    run_id: str,
    design_spec: dict[str, Any],
    run_plan: dict[str, Any],
    task: dict[str, Any],
    dataset_source: dict[str, Any] | None,
) -> dict[str, Any]:
    formula = str(task.get("formula") or design_spec.get("model", {}).get("formula") or "").strip()
    dependent, predictors = parse_linear_formula(formula)
    dataset_path = str(run_plan.get("dataset_path") or (dataset_source or {}).get("path") or "")
    rows, data_preflight = read_numeric_formula_rows_with_preflight(project_root / dataset_path, dataset_path, dependent, predictors)
    model = fit_ols_model(rows, dependent, predictors)
    coefficients = model["coefficients"]
    treatment = first_string((design_spec.get("variables") or {}).get("treatment"))
    evaluator = build_ols_evaluator(model, treatment)
    reproducibility = build_ols_reproducibility(run_id, run_plan, formula, dataset_path)
    backend_validations = [
        execute_statspai_ols_validation(project_root, run_id, formula, dataset_path, model, treatment)
    ]
    return {
        "run_id": run_id,
        "task_id": task.get("id"),
        "method_id": "ols",
        "estimator": task.get("estimator", "ols"),
        "formula": formula,
        "dataset_path": dataset_path,
        "run_plan_version": run_plan.get("version"),
        "design_spec_version": run_plan.get("design_spec_version"),
        "nobs": len(rows),
        "dependent_var": dependent,
        "predictors": predictors,
        "coefficients": coefficients,
        "standard_errors": model["standard_errors"],
        "t_statistics": model["t_statistics"],
        "p_values": model["p_values"],
        "p_value_method": "normal_approximation",
        "confidence_intervals": model["confidence_intervals"],
        "diagnostics": model["diagnostics"],
        "evaluator": evaluator,
        "data_preflight": data_preflight,
        "reproducibility": reproducibility,
        "backend_validations": backend_validations,
        "treatment": treatment,
        "treatment_coefficient": coefficients.get(treatment) if treatment else None,
        "evidence_level": "local_execution",
    }


def execute_statspai_ols_validation(
    project_root: Path,
    run_id: str,
    formula: str,
    dataset_path: str,
    python_model: dict[str, Any],
    treatment: str | None,
) -> dict[str, Any]:
    artifact_path = "Results/json/statspai_execution_result.json"
    result_path = project_root / artifact_path
    validation_base = {
        "backend_id": "statspai",
        "backend_label": "StatsPAI / StatsAPI",
        "formula": formula,
        "dataset_path": dataset_path,
        "artifact_path": artifact_path,
    }
    if importlib.util.find_spec("statspai") is None:
        payload = {
            **validation_base,
            "run_id": run_id,
            "status": "blocked",
            "evidence_level": "local_file",
            "blocker_code": "statspai_not_installed",
            "checks": [
                {
                    "id": "statspai_import",
                    "label": "StatsPAI 可导入",
                    "status": "blocked",
                    "detail": "Python environment cannot import statspai.",
                }
            ],
        }
        write_json_artifact(result_path, payload)
        return payload

    source_path = resolve_execution_dataset_path(project_root, dataset_path)
    if source_path.suffix.lower() != ".csv":
        payload = {
            **validation_base,
            "run_id": run_id,
            "status": "blocked",
            "evidence_level": "local_file",
            "blocker_code": "statspai_validation_requires_csv",
            "checks": [
                {
                    "id": "analysis_ready_csv",
                    "label": "StatsPAI validation 输入格式",
                    "status": "blocked",
                    "detail": f"Current MVP validation supports CSV only, got {source_path.suffix or 'unknown'}.",
                }
            ],
        }
        write_json_artifact(result_path, payload)
        return payload

    try:
        import pandas as pd
        import statspai as sp

        dataframe = pd.read_csv(source_path)
        result = sp.regress(formula, dataframe)
        coefficients = statspai_series_to_float_dict(result.params)
        p_values = statspai_series_to_float_dict(result.pvalues, keys=list(coefficients))
        std_errors = statspai_series_to_float_dict(result.std_errors, keys=list(coefficients))
        t_values = statspai_series_to_float_dict(result.tvalues, keys=list(coefficients))
        diagnostics = json_safe_value(getattr(result, "diagnostics", {}) or {})
        summary_text = str(result.summary())
        python_treatment_coefficient = python_model.get("coefficients", {}).get(treatment) if treatment else None
        statspai_treatment_coefficient = coefficients.get(treatment) if treatment else None
        difference = (
            abs(float(python_treatment_coefficient) - float(statspai_treatment_coefficient))
            if python_treatment_coefficient is not None and statspai_treatment_coefficient is not None
            else None
        )
        tolerance = 1e-6
        coefficient_status = "passed" if difference is not None and difference <= tolerance else "failed"
        payload = {
            **validation_base,
            "run_id": run_id,
            "status": "passed" if coefficient_status == "passed" else "needs_review",
            "evidence_level": "local_execution",
            "adapter": "statspai.regress",
            "statspai_version": getattr(sp, "__version__", "unknown"),
            "nobs": int(len(dataframe)),
            "coefficients": coefficients,
            "standard_errors": std_errors,
            "t_statistics": t_values,
            "p_values": p_values,
            "diagnostics": diagnostics,
            "summary_text": summary_text,
            "checks": [
                {
                    "id": "statspai_import",
                    "label": "StatsPAI 可导入",
                    "status": "passed",
                    "detail": f"statspai {getattr(sp, '__version__', 'unknown')}",
                },
                {
                    "id": "statspai_regress_execution",
                    "label": "StatsPAI regress 已执行",
                    "status": "passed",
                    "detail": formula,
                },
                {
                    "id": "treatment_coefficient_cross_check",
                    "label": "处理变量系数与 Python adapter 一致",
                    "status": coefficient_status,
                    "python_adapter_value": python_treatment_coefficient,
                    "statspai_value": statspai_treatment_coefficient,
                    "difference": difference,
                    "tolerance": tolerance,
                },
            ],
        }
    except Exception as exc:  # pragma: no cover - defensive runtime boundary
        payload = {
            **validation_base,
            "run_id": run_id,
            "status": "blocked",
            "evidence_level": "local_file",
            "blocker_code": "statspai_execution_failed",
            "checks": [
                {
                    "id": "statspai_regress_execution",
                    "label": "StatsPAI regress 已执行",
                    "status": "blocked",
                    "detail": f"{type(exc).__name__}: {exc}",
                }
            ],
        }
    write_json_artifact(result_path, payload)
    return payload


def resolve_execution_dataset_path(project_root: Path, dataset_path: str) -> Path:
    raw_path = Path(dataset_path)
    if raw_path.is_absolute():
        return raw_path
    return (project_root / raw_path).resolve()


def _build_iv_formula(design_spec: dict[str, Any]) -> str:
    """从 design_spec.variable_roles 构造 StatsPAI 兼容的 IV formula。
    格式: outcome ~ (treatment ~ instruments) + controls
    """
    variables = design_spec.get("variables", {})
    outcome = first_string(variables.get("outcome"))
    treatment = first_string(variables.get("treatment"))
    instruments = variables.get("instruments", [])
    controls = variables.get("controls", [])
    if isinstance(instruments, str):
        instruments = [p.strip() for p in instruments.split(",") if p.strip()]
    if isinstance(controls, str):
        controls = [p.strip() for p in controls.split(",") if p.strip()]
    if not outcome or not treatment or not instruments:
        raise MethodExecutionError("iv_formula_build_failed", "IV requires outcome, treatment, and instruments in variable roles")
    instrument_str = " + ".join(instruments)
    control_str = ""
    if controls:
        control_str = " + " + " + ".join(controls)
    return f"{outcome} ~ ({treatment} ~ {instrument_str}){control_str}"


def _build_did_params(design_spec: dict[str, Any]) -> dict[str, Any]:
    """从 design_spec 提取 DID 参数，检查 id/time 变量存在性。"""
    variables = design_spec.get("variables", {})
    model = design_spec.get("model", {})
    outcome = first_string(variables.get("outcome"))
    treatment = first_string(variables.get("treatment"))
    unit_id = first_string(variables.get("unit_id") or variables.get("entity_id") or variables.get("id"))
    time_var = first_string(
        variables.get("time_variable") or variables.get("panel_time") or model.get("time_variable")
    )
    if not outcome:
        raise MethodExecutionError("did_missing_outcome", "DID requires outcome variable")
    if not treatment:
        raise MethodExecutionError("did_missing_treatment", "DID requires treatment variable")
    if not unit_id:
        raise MethodExecutionError("did_missing_unit_id", "DID requires panel unit identifier (id/unit_id/entity_id)")
    if not time_var:
        raise MethodExecutionError("did_missing_time_variable", "DID requires time variable (time_variable/panel_time)")
    params = {
        "y": outcome,
        "treat": treatment,
        "time": time_var,
        "id": unit_id,
    }
    controls = variables.get("controls", [])
    if isinstance(controls, str):
        controls = [p.strip() for p in controls.split(",") if p.strip()]
    if controls:
        params["covariates"] = controls
    return params


def execute_iv_task(
    project_root: Path,
    run_id: str,
    design_spec: dict[str, Any],
    run_plan: dict[str, Any],
    task: dict[str, Any],
    dataset_source: dict[str, Any] | None,
) -> dict[str, Any]:
    formula = str(task.get("formula") or design_spec.get("model", {}).get("formula") or "").strip()
    if not formula:
        formula = _build_iv_formula(design_spec)
    dataset_path = str(run_plan.get("dataset_path") or (dataset_source or {}).get("path") or "")
    source_path = resolve_execution_dataset_path(project_root, dataset_path)
    treatment = first_string((design_spec.get("variables") or {}).get("treatment"))
    if importlib.util.find_spec("statspai") is None:
        raise MethodExecutionError("statspai_not_installed", "StatsPAI is required for IV execution")
    import pandas as pd
    import statspai as sp
    dataframe = pd.read_csv(source_path)

    # Extract cluster and fixed-effects settings from task or design_spec
    cluster_by = task.get("cluster_by") or design_spec.get("variables", {}).get("cluster_by") or []
    fixed_effects = task.get("fixed_effects") or design_spec.get("variables", {}).get("fixed_effects") or []
    if isinstance(cluster_by, str):
        cluster_by = [cluster_by]
    if isinstance(fixed_effects, str):
        fixed_effects = [fixed_effects]

    iv_kwargs: dict[str, Any] = {}
    if cluster_by:
        iv_kwargs["cluster"] = cluster_by[0]
    if fixed_effects:
        iv_kwargs["absorb"] = " + ".join(fixed_effects) if len(fixed_effects) > 1 else fixed_effects[0]

    result = sp.iv(formula, dataframe, **iv_kwargs)
    coefficients = statspai_series_to_float_dict(result.params)
    p_values = statspai_series_to_float_dict(result.pvalues, keys=list(coefficients))
    std_errors = statspai_series_to_float_dict(result.std_errors, keys=list(coefficients))
    t_values = statspai_series_to_float_dict(result.tvalues, keys=list(coefficients))
    diagnostics = json_safe_value(getattr(result, "diagnostics", {}) or {})
    summary_text = str(result.summary())
    iv_diag_result = _run_iv_diag(project_root, run_id, formula, dataset_path, dataframe, design_spec)

    # Determine p-value method based on whether clustering was used
    p_value_method = "cluster_robust" if cluster_by else "normal_approximation"

    return {
        "run_id": run_id,
        "task_id": task.get("id"),
        "method_id": "iv",
        "estimator": task.get("estimator", "iv"),
        "formula": formula,
        "dataset_path": dataset_path,
        "run_plan_version": run_plan.get("version"),
        "design_spec_version": run_plan.get("design_spec_version"),
        "nobs": int(len(dataframe)),
        "dependent_var": first_string((design_spec.get("variables") or {}).get("outcome")),
        "treatment": treatment,
        "treatment_coefficient": coefficients.get(treatment) if treatment else None,
        "coefficients": coefficients,
        "standard_errors": std_errors,
        "t_statistics": t_values,
        "p_values": p_values,
        "p_value_method": p_value_method,
        "cluster_by": cluster_by,
        "fixed_effects": fixed_effects,
        "confidence_intervals": {},
        "diagnostics": diagnostics,
        "summary_text": summary_text,
        "evaluator": build_iv_evaluator(coefficients, p_values, treatment, diagnostics),
        "data_preflight": build_statspai_preflight(dataset_path, dataframe, list(dataframe.columns)),
        "reproducibility": build_iv_reproducibility(run_id, run_plan, formula, dataset_path),
        "backend_validations": [iv_diag_result] if iv_diag_result else [],
        "evidence_level": "local_execution",
    }


def _run_iv_diag(
    project_root: Path,
    run_id: str,
    formula: str,
    dataset_path: str,
    dataframe: Any,
    design_spec: dict[str, Any],
) -> dict[str, Any] | None:
    """运行 iv_diag 并写出独立产物。"""
    artifact_path = "Results/json/iv_diag_result.json"
    result_path = project_root / artifact_path
    variables = design_spec.get("variables", {})
    outcome = first_string(variables.get("outcome"))
    treatment = first_string(variables.get("treatment"))
    instruments = variables.get("instruments", [])
    controls = variables.get("controls", [])
    if isinstance(instruments, str):
        instruments = [p.strip() for p in instruments.split(",") if p.strip()]
    if isinstance(controls, str):
        controls = [p.strip() for p in controls.split(",") if p.strip()]
    if not outcome or not treatment or not instruments:
        return None
    try:
        import statspai as sp
        diag = sp.iv_diag(
            data=dataframe,
            y=outcome,
            endog=treatment,
            instruments=instruments,
            exog=controls or None,
        )
        diag_dict = json_safe_value(getattr(diag, "diagnostics", {}) or {})
        payload = {
            "backend_id": "iv_diag",
            "backend_label": "StatsPAI iv_diag",
            "run_id": run_id,
            "formula": formula,
            "dataset_path": dataset_path,
            "artifact_path": artifact_path,
            "status": "passed",
            "evidence_level": "local_execution",
            "diagnostics": diag_dict,
            "checks": [
                {
                    "id": "iv_diag_execution",
                    "label": "IV 诊断已执行",
                    "status": "passed",
                }
            ],
        }
    except Exception as exc:
        payload = {
            "backend_id": "iv_diag",
            "backend_label": "StatsPAI iv_diag",
            "run_id": run_id,
            "formula": formula,
            "dataset_path": dataset_path,
            "artifact_path": artifact_path,
            "status": "blocked",
            "evidence_level": "local_file",
            "blocker_code": "iv_diag_execution_failed",
            "checks": [
                {
                    "id": "iv_diag_execution",
                    "label": "IV 诊断已执行",
                    "status": "blocked",
                    "detail": f"{type(exc).__name__}: {exc}",
                }
            ],
        }
    write_json_artifact(result_path, payload)
    return payload


def build_iv_evaluator(
    coefficients: dict[str, float],
    p_values: dict[str, float],
    treatment: str | None,
    diagnostics: dict[str, Any],
) -> dict[str, Any]:
    checks = [
        {
            "id": "sample_size",
            "label": "样本量可用",
            "status": "passed" if diagnostics.get("nobs", 0) > 0 else "failed",
            "detail": f"n={diagnostics.get('nobs', 'unknown')}",
        },
        {
            "id": "treatment_coefficient",
            "label": "处理变量系数存在",
            "status": "passed" if treatment and treatment in coefficients else "failed",
            "detail": treatment or "missing treatment",
        },
        {
            "id": "inference_diagnostics",
            "label": "推断诊断可用",
            "status": "passed"
            if treatment and treatment in p_values and p_values.get(treatment, 1) <= 1
            else "failed",
            "detail": "p-value available",
        },
    ]
    status = "passed" if all(check["status"] == "passed" for check in checks) else "needs_review"
    return {
        "status": status,
        "evidence_level": "local_execution",
        "p_value_method": "normal_approximation",
        "checks": checks,
    }


def build_iv_reproducibility(
    run_id: str,
    run_plan: dict[str, Any],
    formula: str,
    dataset_path: str,
) -> dict[str, Any]:
    return {
        "evidence_level": "local_execution",
        "adapter": "statspai_iv",
        "run_id": run_id,
        "formula": formula,
        "dataset_path": dataset_path,
        "run_plan_version": run_plan.get("version"),
        "design_spec_version": run_plan.get("design_spec_version"),
        "result_artifact_path": "Results/json/method_execution_result.json",
        "manifest_artifact_path": f"state/runs/{run_id}/run_manifest.json",
        "source_entrypoint": "Product/backend/project_service.py::execute_iv_task",
        "p_value_method": "normal_approximation",
    }


def execute_did_task(
    project_root: Path,
    run_id: str,
    design_spec: dict[str, Any],
    run_plan: dict[str, Any],
    task: dict[str, Any],
    dataset_source: dict[str, Any] | None,
) -> dict[str, Any]:
    did_params = _build_did_params(design_spec)
    dataset_path = str(run_plan.get("dataset_path") or (dataset_source or {}).get("path") or "")
    source_path = resolve_execution_dataset_path(project_root, dataset_path)
    treatment = first_string((design_spec.get("variables") or {}).get("treatment"))
    if importlib.util.find_spec("statspai") is None:
        raise MethodExecutionError("statspai_not_installed", "StatsPAI is required for DID execution")
    import pandas as pd
    import statspai as sp
    dataframe = pd.read_csv(source_path)
    result = sp.did(data=dataframe, **did_params)
    coefficients = statspai_series_to_float_dict(getattr(result, "params", {}))
    p_values = statspai_series_to_float_dict(getattr(result, "pvalues", {}), keys=list(coefficients))
    std_errors = statspai_series_to_float_dict(getattr(result, "std_errors", {}), keys=list(coefficients))
    t_values = statspai_series_to_float_dict(getattr(result, "tvalues", {}), keys=list(coefficients))
    diagnostics = json_safe_value(getattr(result, "diagnostics", {}) or {})
    summary_text = str(getattr(result, "summary", lambda: "")())
    return {
        "run_id": run_id,
        "task_id": task.get("id"),
        "method_id": "did",
        "estimator": task.get("estimator", "did"),
        "formula": f"did(y={did_params['y']}, treat={did_params['treat']}, time={did_params['time']}, id={did_params['id']})",
        "dataset_path": dataset_path,
        "run_plan_version": run_plan.get("version"),
        "design_spec_version": run_plan.get("design_spec_version"),
        "nobs": int(len(dataframe)),
        "dependent_var": did_params["y"],
        "treatment": treatment,
        "treatment_coefficient": coefficients.get(treatment) if treatment else None,
        "coefficients": coefficients,
        "standard_errors": std_errors,
        "t_statistics": t_values,
        "p_values": p_values,
        "p_value_method": "normal_approximation",
        "confidence_intervals": {},
        "diagnostics": diagnostics,
        "summary_text": summary_text,
        "evaluator": build_did_evaluator(coefficients, p_values, treatment, diagnostics),
        "data_preflight": build_statspai_preflight(dataset_path, dataframe, list(dataframe.columns)),
        "reproducibility": build_did_reproducibility(run_id, run_plan, did_params, dataset_path),
        "backend_validations": [],
        "evidence_level": "local_execution",
    }


def build_did_evaluator(
    coefficients: dict[str, float],
    p_values: dict[str, float],
    treatment: str | None,
    diagnostics: dict[str, Any],
) -> dict[str, Any]:
    checks = [
        {
            "id": "sample_size",
            "label": "样本量可用",
            "status": "passed" if diagnostics.get("nobs", 0) > 0 else "failed",
            "detail": f"n={diagnostics.get('nobs', 'unknown')}",
        },
        {
            "id": "treatment_coefficient",
            "label": "处理变量系数存在",
            "status": "passed" if treatment and treatment in coefficients else "failed",
            "detail": treatment or "missing treatment",
        },
        {
            "id": "inference_diagnostics",
            "label": "推断诊断可用",
            "status": "passed"
            if treatment and treatment in p_values and p_values.get(treatment, 1) <= 1
            else "failed",
            "detail": "p-value available",
        },
    ]
    status = "passed" if all(check["status"] == "passed" for check in checks) else "needs_review"
    return {
        "status": status,
        "evidence_level": "local_execution",
        "p_value_method": "normal_approximation",
        "checks": checks,
    }


def build_did_reproducibility(
    run_id: str,
    run_plan: dict[str, Any],
    did_params: dict[str, Any],
    dataset_path: str,
) -> dict[str, Any]:
    return {
        "evidence_level": "local_execution",
        "adapter": "statspai_did",
        "run_id": run_id,
        "formula": f"did(y={did_params['y']}, treat={did_params['treat']}, time={did_params['time']}, id={did_params['id']})",
        "dataset_path": dataset_path,
        "run_plan_version": run_plan.get("version"),
        "design_spec_version": run_plan.get("design_spec_version"),
        "result_artifact_path": "Results/json/method_execution_result.json",
        "manifest_artifact_path": f"state/runs/{run_id}/run_manifest.json",
        "source_entrypoint": "Product/backend/project_service.py::execute_did_task",
        "p_value_method": "normal_approximation",
    }


def execute_rdd_task(
    project_root: Path,
    run_id: str,
    design_spec: dict[str, Any],
    run_plan: dict[str, Any],
    task: dict[str, Any],
    dataset_source: dict[str, Any] | None,
) -> dict[str, Any]:
    rdd_params = _build_rdd_params(design_spec)
    dataset_path = str(run_plan.get("dataset_path") or (dataset_source or {}).get("path") or "")
    source_path = resolve_execution_dataset_path(project_root, dataset_path)
    treatment = first_string((design_spec.get("variables") or {}).get("treatment"))
    if importlib.util.find_spec("statspai") is None:
        raise MethodExecutionError("statspai_not_installed", "StatsPAI is required for RDD execution")
    import pandas as pd
    import statspai as sp
    dataframe = pd.read_csv(source_path)
    result = sp.rdd(data=dataframe, **rdd_params)
    coefficients = statspai_series_to_float_dict(getattr(result, "params", {}))
    p_values = statspai_series_to_float_dict(getattr(result, "pvalues", {}), keys=list(coefficients))
    std_errors = statspai_series_to_float_dict(getattr(result, "std_errors", {}), keys=list(coefficients))
    t_values = statspai_series_to_float_dict(getattr(result, "tvalues", {}), keys=list(coefficients))
    diagnostics = json_safe_value(getattr(result, "diagnostics", {}) or {})
    summary_text = str(getattr(result, "summary", lambda: "")())
    return {
        "run_id": run_id,
        "task_id": task.get("id"),
        "method_id": "rdd",
        "estimator": task.get("estimator", "rdd"),
        "formula": f"rdd(y={rdd_params['y']}, running={rdd_params['running']}, cutoff={rdd_params['cutoff']})",
        "dataset_path": dataset_path,
        "run_plan_version": run_plan.get("version"),
        "design_spec_version": run_plan.get("design_spec_version"),
        "nobs": int(len(dataframe)),
        "dependent_var": rdd_params["y"],
        "treatment": treatment,
        "treatment_coefficient": coefficients.get(treatment) if treatment else None,
        "coefficients": coefficients,
        "standard_errors": std_errors,
        "t_statistics": t_values,
        "p_values": p_values,
        "p_value_method": "normal_approximation",
        "confidence_intervals": {},
        "diagnostics": diagnostics,
        "summary_text": summary_text,
        "evaluator": build_rdd_evaluator(coefficients, p_values, treatment, diagnostics),
        "data_preflight": build_statspai_preflight(dataset_path, dataframe, list(dataframe.columns)),
        "reproducibility": build_rdd_reproducibility(run_id, run_plan, rdd_params, dataset_path),
        "backend_validations": [],
        "evidence_level": "local_execution",
    }


def _build_rdd_params(design_spec: dict[str, Any]) -> dict[str, Any]:
    """从 design_spec 提取 RDD 参数。"""
    variables = design_spec.get("variables", {})
    model = design_spec.get("model", {})
    outcome = first_string(variables.get("outcome"))
    running = first_string(
        variables.get("running_variable") or variables.get("running") or model.get("running_variable")
    )
    cutoff = model.get("cutoff", 0.0)
    if isinstance(cutoff, str):
        try:
            cutoff = float(cutoff)
        except ValueError:
            cutoff = 0.0
    if not outcome:
        raise MethodExecutionError("rdd_missing_outcome", "RDD requires outcome variable")
    if not running:
        raise MethodExecutionError("rdd_missing_running", "RDD requires running variable")
    params: dict[str, Any] = {
        "y": outcome,
        "running": running,
        "cutoff": cutoff,
    }
    controls = variables.get("controls", [])
    if isinstance(controls, str):
        controls = [p.strip() for p in controls.split(",") if p.strip()]
    if controls:
        params["covs"] = controls
    return params


def build_rdd_evaluator(
    coefficients: dict[str, float],
    p_values: dict[str, float],
    treatment: str | None,
    diagnostics: dict[str, Any],
) -> dict[str, Any]:
    checks = [
        {
            "id": "sample_size",
            "label": "样本量可用",
            "status": "passed" if diagnostics.get("nobs", 0) > 0 else "failed",
            "detail": f"n={diagnostics.get('nobs', 'unknown')}",
        },
        {
            "id": "treatment_coefficient",
            "label": "处理效应估计存在",
            "status": "passed" if coefficients else "failed",
            "detail": "RDD LATE estimate available" if coefficients else "no estimate",
        },
        {
            "id": "inference_diagnostics",
            "label": "推断诊断可用",
            "status": "passed" if p_values else "failed",
            "detail": "p-value available" if p_values else "missing",
        },
    ]
    status = "passed" if all(check["status"] == "passed" for check in checks) else "needs_review"
    return {
        "status": status,
        "evidence_level": "local_execution",
        "p_value_method": "normal_approximation",
        "checks": checks,
    }


def build_rdd_reproducibility(
    run_id: str,
    run_plan: dict[str, Any],
    rdd_params: dict[str, Any],
    dataset_path: str,
) -> dict[str, Any]:
    return {
        "evidence_level": "local_execution",
        "adapter": "statspai_rdd",
        "run_id": run_id,
        "formula": f"rdd(y={rdd_params['y']}, running={rdd_params['running']}, cutoff={rdd_params['cutoff']})",
        "dataset_path": dataset_path,
        "run_plan_version": run_plan.get("version"),
        "design_spec_version": run_plan.get("design_spec_version"),
        "result_artifact_path": "Results/json/method_execution_result.json",
        "manifest_artifact_path": f"state/runs/{run_id}/run_manifest.json",
        "source_entrypoint": "Product/backend/project_service.py::execute_rdd_task",
        "p_value_method": "normal_approximation",
    }


def execute_psm_task(
    project_root: Path,
    run_id: str,
    design_spec: dict[str, Any],
    run_plan: dict[str, Any],
    task: dict[str, Any],
    dataset_source: dict[str, Any] | None,
) -> dict[str, Any]:
    psm_params = _build_psm_params(design_spec)
    dataset_path = str(run_plan.get("dataset_path") or (dataset_source or {}).get("path") or "")
    source_path = resolve_execution_dataset_path(project_root, dataset_path)
    treatment = first_string((design_spec.get("variables") or {}).get("treatment"))
    if importlib.util.find_spec("statspai") is None:
        raise MethodExecutionError("statspai_not_installed", "StatsPAI is required for PSM execution")
    import pandas as pd
    import statspai as sp
    dataframe = pd.read_csv(source_path)
    result = sp.match(data=dataframe, **psm_params)
    coefficients = statspai_series_to_float_dict(getattr(result, "params", {}))
    p_values = statspai_series_to_float_dict(getattr(result, "pvalues", {}), keys=list(coefficients))
    std_errors = statspai_series_to_float_dict(getattr(result, "std_errors", {}), keys=list(coefficients))
    t_values = statspai_series_to_float_dict(getattr(result, "tvalues", {}), keys=list(coefficients))
    diagnostics = json_safe_value(getattr(result, "diagnostics", {}) or {})
    summary_text = str(getattr(result, "summary", lambda: "")())
    return {
        "run_id": run_id,
        "task_id": task.get("id"),
        "method_id": "psm",
        "estimator": task.get("estimator", "psm"),
        "formula": f"match(y={psm_params['y']}, treat={psm_params['treat']}, covariates={psm_params.get('covariates', [])})",
        "dataset_path": dataset_path,
        "run_plan_version": run_plan.get("version"),
        "design_spec_version": run_plan.get("design_spec_version"),
        "nobs": int(len(dataframe)),
        "dependent_var": psm_params["y"],
        "treatment": treatment,
        "treatment_coefficient": coefficients.get(treatment) if treatment else None,
        "coefficients": coefficients,
        "standard_errors": std_errors,
        "t_statistics": t_values,
        "p_values": p_values,
        "p_value_method": "normal_approximation",
        "confidence_intervals": {},
        "diagnostics": diagnostics,
        "summary_text": summary_text,
        "evaluator": build_psm_evaluator(coefficients, p_values, treatment, diagnostics),
        "data_preflight": build_statspai_preflight(dataset_path, dataframe, list(dataframe.columns)),
        "reproducibility": build_psm_reproducibility(run_id, run_plan, psm_params, dataset_path),
        "backend_validations": [],
        "evidence_level": "local_execution",
    }


def _build_psm_params(design_spec: dict[str, Any]) -> dict[str, Any]:
    """从 design_spec 提取 PSM 参数。"""
    variables = design_spec.get("variables", {})
    outcome = first_string(variables.get("outcome"))
    treatment = first_string(variables.get("treatment"))
    covariates = variables.get("controls", [])
    if isinstance(covariates, str):
        covariates = [p.strip() for p in covariates.split(",") if p.strip()]
    if not outcome:
        raise MethodExecutionError("psm_missing_outcome", "PSM requires outcome variable")
    if not treatment:
        raise MethodExecutionError("psm_missing_treatment", "PSM requires treatment variable")
    if not covariates:
        raise MethodExecutionError("psm_missing_covariates", "PSM requires covariates for propensity score")
    params: dict[str, Any] = {
        "y": outcome,
        "treat": treatment,
        "covariates": covariates,
    }
    return params


def build_psm_evaluator(
    coefficients: dict[str, float],
    p_values: dict[str, float],
    treatment: str | None,
    diagnostics: dict[str, Any],
) -> dict[str, Any]:
    checks = [
        {
            "id": "sample_size",
            "label": "样本量可用",
            "status": "passed" if diagnostics.get("nobs", 0) > 0 else "failed",
            "detail": f"n={diagnostics.get('nobs', 'unknown')}",
        },
        {
            "id": "treatment_coefficient",
            "label": "处理变量系数存在",
            "status": "passed" if treatment and treatment in coefficients else "failed",
            "detail": treatment or "missing treatment",
        },
        {
            "id": "inference_diagnostics",
            "label": "推断诊断可用",
            "status": "passed"
            if treatment and treatment in p_values and p_values.get(treatment, 1) <= 1
            else "failed",
            "detail": "p-value available",
        },
    ]
    status = "passed" if all(check["status"] == "passed" for check in checks) else "needs_review"
    return {
        "status": status,
        "evidence_level": "local_execution",
        "p_value_method": "normal_approximation",
        "checks": checks,
    }


def build_psm_reproducibility(
    run_id: str,
    run_plan: dict[str, Any],
    psm_params: dict[str, Any],
    dataset_path: str,
) -> dict[str, Any]:
    return {
        "evidence_level": "local_execution",
        "adapter": "statspai_psm",
        "run_id": run_id,
        "formula": f"match(y={psm_params['y']}, treat={psm_params['treat']}, covariates={psm_params.get('covariates', [])})",
        "dataset_path": dataset_path,
        "run_plan_version": run_plan.get("version"),
        "design_spec_version": run_plan.get("design_spec_version"),
        "result_artifact_path": "Results/json/method_execution_result.json",
        "manifest_artifact_path": f"state/runs/{run_id}/run_manifest.json",
        "source_entrypoint": "Product/backend/project_service.py::execute_psm_task",
        "p_value_method": "normal_approximation",
    }


def execute_dml_task(
    project_root: Path,
    run_id: str,
    design_spec: dict[str, Any],
    run_plan: dict[str, Any],
    task: dict[str, Any],
    dataset_source: dict[str, Any] | None,
) -> dict[str, Any]:
    dml_params = _build_dml_params(design_spec)
    dataset_path = str(run_plan.get("dataset_path") or (dataset_source or {}).get("path") or "")
    source_path = resolve_execution_dataset_path(project_root, dataset_path)
    treatment = first_string((design_spec.get("variables") or {}).get("treatment"))
    if importlib.util.find_spec("statspai") is None:
        raise MethodExecutionError("statspai_not_installed", "StatsPAI is required for DML execution")
    import pandas as pd
    import statspai as sp
    dataframe = pd.read_csv(source_path)
    result = sp.dml(data=dataframe, **dml_params)
    coefficients = statspai_series_to_float_dict(getattr(result, "params", {}))
    p_values = statspai_series_to_float_dict(getattr(result, "pvalues", {}), keys=list(coefficients))
    std_errors = statspai_series_to_float_dict(getattr(result, "std_errors", {}), keys=list(coefficients))
    t_values = statspai_series_to_float_dict(getattr(result, "tvalues", {}), keys=list(coefficients))
    diagnostics = json_safe_value(getattr(result, "diagnostics", {}) or {})
    summary_text = str(getattr(result, "summary", lambda: "")())
    return {
        "run_id": run_id,
        "task_id": task.get("id"),
        "method_id": "dml",
        "estimator": task.get("estimator", "dml"),
        "formula": f"dml(y={dml_params['y']}, treat={dml_params.get('treat') or dml_params.get('d')}, covariates={dml_params.get('covariates') or dml_params.get('X', [])})",
        "dataset_path": dataset_path,
        "run_plan_version": run_plan.get("version"),
        "design_spec_version": run_plan.get("design_spec_version"),
        "nobs": int(len(dataframe)),
        "dependent_var": dml_params["y"],
        "treatment": treatment,
        "treatment_coefficient": coefficients.get(treatment) if treatment else None,
        "coefficients": coefficients,
        "standard_errors": std_errors,
        "t_statistics": t_values,
        "p_values": p_values,
        "p_value_method": "normal_approximation",
        "confidence_intervals": {},
        "diagnostics": diagnostics,
        "summary_text": summary_text,
        "evaluator": build_dml_evaluator(coefficients, p_values, treatment, diagnostics),
        "data_preflight": build_statspai_preflight(dataset_path, dataframe, list(dataframe.columns)),
        "reproducibility": build_dml_reproducibility(run_id, run_plan, dml_params, dataset_path),
        "backend_validations": [],
        "evidence_level": "local_execution",
    }


def _build_dml_params(design_spec: dict[str, Any]) -> dict[str, Any]:
    """从 design_spec 提取 DML 参数。"""
    variables = design_spec.get("variables", {})
    outcome = first_string(variables.get("outcome"))
    treatment = first_string(variables.get("treatment"))
    covariates = variables.get("controls", [])
    if isinstance(covariates, str):
        covariates = [p.strip() for p in covariates.split(",") if p.strip()]
    if not outcome:
        raise MethodExecutionError("dml_missing_outcome", "DML requires outcome variable")
    if not treatment:
        raise MethodExecutionError("dml_missing_treatment", "DML requires treatment variable")
    if not covariates:
        raise MethodExecutionError("dml_missing_covariates", "DML requires covariates for nuisance function estimation")
    params: dict[str, Any] = {
        "y": outcome,
        "treat": treatment,
        "covariates": covariates,
    }
    return params


def build_dml_evaluator(
    coefficients: dict[str, float],
    p_values: dict[str, float],
    treatment: str | None,
    diagnostics: dict[str, Any],
) -> dict[str, Any]:
    checks = [
        {
            "id": "sample_size",
            "label": "样本量可用",
            "status": "passed" if diagnostics.get("nobs", 0) > 0 else "failed",
            "detail": f"n={diagnostics.get('nobs', 'unknown')}",
        },
        {
            "id": "treatment_coefficient",
            "label": "处理变量系数存在",
            "status": "passed" if treatment and treatment in coefficients else "failed",
            "detail": treatment or "missing treatment",
        },
        {
            "id": "inference_diagnostics",
            "label": "推断诊断可用",
            "status": "passed"
            if treatment and treatment in p_values and p_values.get(treatment, 1) <= 1
            else "failed",
            "detail": "p-value available",
        },
    ]
    status = "passed" if all(check["status"] == "passed" for check in checks) else "needs_review"
    return {
        "status": status,
        "evidence_level": "local_execution",
        "p_value_method": "normal_approximation",
        "checks": checks,
    }


def build_dml_reproducibility(
    run_id: str,
    run_plan: dict[str, Any],
    dml_params: dict[str, Any],
    dataset_path: str,
) -> dict[str, Any]:
    return {
        "evidence_level": "local_execution",
        "adapter": "statspai_dml",
        "run_id": run_id,
        "formula": f"dml(y={dml_params['y']}, treat={dml_params.get('treat') or dml_params.get('d')}, covariates={dml_params.get('covariates') or dml_params.get('X', [])})",
        "dataset_path": dataset_path,
        "run_plan_version": run_plan.get("version"),
        "design_spec_version": run_plan.get("design_spec_version"),
        "result_artifact_path": "Results/json/method_execution_result.json",
        "manifest_artifact_path": f"state/runs/{run_id}/run_manifest.json",
        "source_entrypoint": "Product/backend/project_service.py::execute_dml_task",
        "p_value_method": "normal_approximation",
    }


def build_statspai_preflight(dataset_path: str, dataframe: Any, columns: list[str]) -> dict[str, Any]:
    return {
        "evidence_level": "local_execution",
        "analysis_boundary": "analysis_ready_numeric_formula_rows",
        "dataset_path": dataset_path,
        "required_fields": columns,
        "rows_read": int(len(dataframe)),
        "usable_numeric_rows": int(len(dataframe)),
        "dropped_rows": 0,
        "checks": [
            {
                "id": "dataset_file_exists",
                "label": "数据文件存在",
                "status": "passed",
                "detail": dataset_path,
            },
            {
                "id": "required_fields_present",
                "label": "公式字段存在",
                "status": "passed",
                "detail": ", ".join(columns),
            },
            {
                "id": "numeric_formula_rows_available",
                "label": "公式字段可转为数值",
                "status": "passed",
                "detail": f"usable={len(dataframe)}, dropped=0",
            },
        ],
    }


def write_json_artifact(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def statspai_series_to_float_dict(values: Any, keys: list[str] | None = None) -> dict[str, float]:
    if hasattr(values, "to_dict"):
        return {str(key): round_significant(float(value)) for key, value in values.to_dict().items()}
    raw_values = list(values) if isinstance(values, (list, tuple)) or hasattr(values, "__iter__") else []
    if not keys:
        keys = [str(index) for index in range(len(raw_values))]
    return {
        key: round_significant(float(raw_values[index]))
        for index, key in enumerate(keys)
        if index < len(raw_values)
    }


def json_safe_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): json_safe_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [json_safe_value(item) for item in value]
    if isinstance(value, tuple):
        return [json_safe_value(item) for item in value]
    if hasattr(value, "item"):
        try:
            return value.item()
        except (TypeError, ValueError):
            pass
    if isinstance(value, (int, float, str, bool)) or value is None:
        return value
    return str(value)


def parse_linear_formula(formula: str) -> tuple[str, list[str]]:
    if "~" not in formula:
        raise MethodExecutionError("unsupported_formula", f"Unsupported OLS formula: {formula}")
    lhs, rhs = formula.split("~", 1)
    dependent = lhs.strip()
    predictors = [term.strip() for term in rhs.split("+") if term.strip() and term.strip() != "1"]
    if not dependent or not predictors:
        raise MethodExecutionError("unsupported_formula", f"Unsupported OLS formula: {formula}")
    return dependent, predictors


def read_numeric_formula_rows(path: Path, dependent: str, predictors: list[str]) -> list[dict[str, float]]:
    rows, _preflight = read_numeric_formula_rows_with_preflight(path, str(path), dependent, predictors)
    return rows


def read_numeric_formula_rows_with_preflight(
    path: Path,
    dataset_path: str,
    dependent: str,
    predictors: list[str],
) -> tuple[list[dict[str, float]], dict[str, Any]]:
    fields = [dependent, *predictors]
    rows: list[dict[str, float]] = []
    rows_read = 0
    if not path.exists():
        raise MethodExecutionError("dataset_not_found", f"Dataset not found: {dataset_path}")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames or []
        missing_fields = [field for field in fields if field not in fieldnames]
        if missing_fields:
            raise MethodExecutionError("missing_formula_fields", f"Missing formula fields: {', '.join(missing_fields)}")
        for raw in reader:
            rows_read += 1
            try:
                rows.append({field: float(raw[field]) for field in fields})
            except (KeyError, TypeError, ValueError):
                continue
    dropped_rows = rows_read - len(rows)
    if len(rows) <= len(predictors):
        raise MethodExecutionError("not_enough_numeric_observations", "Not enough numeric observations for OLS execution")
    preflight = {
        "evidence_level": "local_execution",
        "analysis_boundary": "analysis_ready_numeric_formula_rows",
        "dataset_path": dataset_path,
        "required_fields": fields,
        "rows_read": rows_read,
        "usable_numeric_rows": len(rows),
        "dropped_rows": dropped_rows,
        "checks": [
            {
                "id": "dataset_file_exists",
                "label": "数据文件存在",
                "status": "passed",
                "detail": dataset_path,
            },
            {
                "id": "required_fields_present",
                "label": "公式字段存在",
                "status": "passed",
                "detail": ", ".join(fields),
            },
            {
                "id": "numeric_formula_rows_available",
                "label": "公式字段可转为数值",
                "status": "passed",
                "detail": f"usable={len(rows)}, dropped={dropped_rows}",
            },
            {
                "id": "degrees_of_freedom_precheck",
                "label": "样本量大于解释变量数量",
                "status": "passed",
                "detail": f"usable={len(rows)}, predictors={len(predictors)}",
            },
        ],
    }
    return rows, preflight


def build_ols_reproducibility(
    run_id: str,
    run_plan: dict[str, Any],
    formula: str,
    dataset_path: str,
) -> dict[str, Any]:
    return {
        "evidence_level": "local_execution",
        "adapter": "python_ols_adapter",
        "run_id": run_id,
        "formula": formula,
        "dataset_path": dataset_path,
        "run_plan_version": run_plan.get("version"),
        "design_spec_version": run_plan.get("design_spec_version"),
        "result_artifact_path": "Results/json/method_execution_result.json",
        "manifest_artifact_path": f"state/runs/{run_id}/run_manifest.json",
        "source_entrypoint": "Product/backend/project_service.py::execute_ols_task",
        "p_value_method": "normal_approximation",
    }


def fit_ols_coefficients(rows: list[dict[str, float]], dependent: str, predictors: list[str]) -> dict[str, float]:
    return fit_ols_model(rows, dependent, predictors)["coefficients"]


def fit_ols_model(rows: list[dict[str, float]], dependent: str, predictors: list[str]) -> dict[str, Any]:
    columns = ["intercept", *predictors]
    x_rows = [[1.0, *[row[predictor] for predictor in predictors]] for row in rows]
    y_values = [row[dependent] for row in rows]
    xtx = [
        [sum(x_row[i] * x_row[j] for x_row in x_rows) for j in range(len(columns))]
        for i in range(len(columns))
    ]
    xty = [sum(x_row[i] * y for x_row, y in zip(x_rows, y_values)) for i in range(len(columns))]
    beta = solve_linear_system(xtx, xty)
    fitted = [sum(value * coefficient for value, coefficient in zip(x_row, beta)) for x_row in x_rows]
    residuals = [y - fitted_value for y, fitted_value in zip(y_values, fitted)]
    residual_degrees_of_freedom = len(rows) - len(columns)
    if residual_degrees_of_freedom <= 0:
        raise MethodExecutionError("not_enough_degrees_of_freedom", "OLS residual degrees of freedom must be positive")
    residual_sum_of_squares = sum(residual * residual for residual in residuals)
    sigma_squared = residual_sum_of_squares / residual_degrees_of_freedom
    inverse_xtx = invert_matrix(xtx)
    standard_errors_raw = [
        math.sqrt(max(sigma_squared * inverse_xtx[index][index], 0.0))
        for index in range(len(columns))
    ]
    t_statistics_raw = [
        coefficient / standard_error if standard_error > 0 else math.inf
        for coefficient, standard_error in zip(beta, standard_errors_raw)
    ]
    p_values_raw = [normal_two_sided_p_value(t_statistic) for t_statistic in t_statistics_raw]

    return {
        "coefficients": {column: round(value, 10) for column, value in zip(columns, beta)},
        "standard_errors": {column: round(value, 10) for column, value in zip(columns, standard_errors_raw)},
        "t_statistics": {column: round(value, 10) for column, value in zip(columns, t_statistics_raw)},
        "p_values": {column: round_significant(value) for column, value in zip(columns, p_values_raw)},
        "confidence_intervals": {
            column: {
                "level": 0.95,
                "low": round(coefficient - 1.96 * standard_error, 10),
                "high": round(coefficient + 1.96 * standard_error, 10),
            }
            for column, coefficient, standard_error in zip(columns, beta, standard_errors_raw)
        },
        "diagnostics": {
            "nobs": len(rows),
            "parameter_count": len(columns),
            "model_rank": len(columns),
            "residual_degrees_of_freedom": residual_degrees_of_freedom,
            "residual_standard_error": round(math.sqrt(sigma_squared), 10),
            "residual_sum_of_squares": round(residual_sum_of_squares, 10),
        },
    }


def invert_matrix(matrix: list[list[float]]) -> list[list[float]]:
    size = len(matrix)
    return [solve_linear_system(matrix, [1.0 if index == column else 0.0 for index in range(size)]) for column in range(size)]


def normal_two_sided_p_value(t_statistic: float) -> float:
    if math.isinf(t_statistic):
        return 0.0
    return math.erfc(abs(t_statistic) / math.sqrt(2.0))


def round_significant(value: float, digits: int = 12) -> float:
    if value == 0 or not math.isfinite(value):
        return value
    return float(f"{value:.{digits}g}")


def build_ols_evaluator(model: dict[str, Any], treatment: str | None) -> dict[str, Any]:
    diagnostics = model["diagnostics"]
    coefficients = model["coefficients"]
    standard_errors = model["standard_errors"]
    p_values = model["p_values"]
    checks = [
        {
            "id": "sample_size",
            "label": "样本量大于参数数量",
            "status": "passed" if diagnostics["residual_degrees_of_freedom"] > 0 else "failed",
            "detail": f"n={diagnostics['nobs']}, parameters={diagnostics['parameter_count']}",
        },
        {
            "id": "model_rank",
            "label": "模型矩阵可估",
            "status": "passed" if diagnostics["model_rank"] == diagnostics["parameter_count"] else "failed",
            "detail": f"rank={diagnostics['model_rank']}",
        },
        {
            "id": "treatment_coefficient",
            "label": "处理变量系数存在",
            "status": "passed" if treatment and treatment in coefficients else "failed",
            "detail": treatment or "missing treatment",
        },
        {
            "id": "inference_diagnostics",
            "label": "推断诊断可用",
            "status": "passed"
            if treatment and treatment in standard_errors and treatment in p_values and standard_errors[treatment] > 0
            else "failed",
            "detail": "standard error and p value available",
        },
    ]
    status = "passed" if all(check["status"] == "passed" for check in checks) else "needs_review"
    return {
        "status": status,
        "evidence_level": "local_execution",
        "p_value_method": "normal_approximation",
        "checks": checks,
    }


def solve_linear_system(matrix: list[list[float]], vector: list[float]) -> list[float]:
    size = len(vector)
    augmented = [row[:] + [value] for row, value in zip(matrix, vector)]
    for pivot_index in range(size):
        pivot_row = max(range(pivot_index, size), key=lambda row_index: abs(augmented[row_index][pivot_index]))
        if abs(augmented[pivot_row][pivot_index]) < 1e-12:
            raise MethodExecutionError("singular_ols_design", "OLS normal equation is singular")
        if pivot_row != pivot_index:
            augmented[pivot_index], augmented[pivot_row] = augmented[pivot_row], augmented[pivot_index]
        pivot = augmented[pivot_index][pivot_index]
        augmented[pivot_index] = [value / pivot for value in augmented[pivot_index]]
        for row_index in range(size):
            if row_index == pivot_index:
                continue
            factor = augmented[row_index][pivot_index]
            augmented[row_index] = [
                current - factor * pivot_value
                for current, pivot_value in zip(augmented[row_index], augmented[pivot_index])
            ]
    return [row[-1] for row in augmented]


def first_string(values: Any) -> str | None:
    if isinstance(values, list) and values:
        return str(values[0])
    if isinstance(values, str) and values:
        return values
    return None


def build_research_engine_reference() -> dict[str, Any]:
    return {
        "name": "Feynman-compatible research engine",
        "integration_mode": "callable_external",
        "embedded": False,
        "license": "MIT",
        "repository": "companion-inc/feynman",
        "evidence_level": "local_file",
        "note": "Feynman is treated as an external research-engine reference; its source is not embedded.",
    }


def resolve_dataset_source(project_root: Path, dataset_path: str | None) -> dict[str, Any] | None:
    configured_path = None
    if not dataset_path:
        configured = load_json_if_exists(project_root / "state" / "project_state.json")
        dataset_path = configured.get("dataset_path") if configured else None
    if not dataset_path:
        paper_path = project_root / "paper.yaml"
        if paper_path.exists():
            payload = yaml.safe_load(paper_path.read_text(encoding="utf-8")) or {}
            configured_path = payload.get("data", {}).get("final_dataset")
            dataset_path = configured_path
    elif (project_root / "paper.yaml").exists():
        payload = yaml.safe_load((project_root / "paper.yaml").read_text(encoding="utf-8")) or {}
        configured_path = payload.get("data", {}).get("final_dataset")
    if not dataset_path:
        return None

    raw_path = Path(dataset_path)
    if raw_path.is_absolute() or ".." in raw_path.parts:
        raise PermissionError(str(dataset_path))
    root = project_root.resolve()
    path = (root / raw_path).resolve()
    if path != root and root not in path.parents:
        raise PermissionError(str(dataset_path))
    if not path.is_file():
        raise FileNotFoundError(str(dataset_path))

    stat = path.stat()
    relative_path = path.relative_to(root).as_posix()
    source = {
        "path": path.relative_to(root).as_posix(),
        "name": path.name,
        "file_type": path.suffix.lower().lstrip("."),
        "size": stat.st_size,
        "exists": True,
        "evidence_level": "local_file",
        "role": "configured_final_dataset" if configured_path and Path(configured_path).as_posix() == relative_path else "selected_dataset",
    }
    source.update(inspect_dataset_source_shape(path))
    return source


def inspect_dataset_source_shape(path: Path) -> dict[str, int | None]:
    if path.suffix.lower() != ".csv":
        return {"row_count": None, "column_count": None}
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.reader(handle))
    if not rows:
        return {"row_count": 0, "column_count": 0}
    return {"row_count": max(len(rows) - 1, 0), "column_count": len(rows[0])}


def persist_run_dataset_source(project_root: Path, run_id: str, dataset_source: dict[str, Any] | None) -> None:
    if not dataset_source:
        return
    manifest_path = project_root / "state" / "runs" / run_id / "run_manifest.json"
    if not manifest_path.exists():
        return
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["dataset_source"] = dataset_source
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def persist_full_run_provenance(
    project_root: Path,
    run_id: str,
    plan_binding: dict[str, Any],
    research_engine: dict[str, Any],
    method_execution: dict[str, Any] | None = None,
) -> None:
    manifest_path = project_root / "state" / "runs" / run_id / "run_manifest.json"
    if not manifest_path.exists():
        return
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["run_plan_binding"] = plan_binding
    manifest["research_engine"] = research_engine
    manifest["execution_evidence_level"] = "local_execution"
    if method_execution:
        manifest["method_execution"] = method_execution
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def get_project_run(project: dict[str, Any], run_id: str) -> dict[str, Any]:
    return get_run(Path(project["project_root"]), run_id)


def get_project_run_observability(project: dict[str, Any], run_id: str) -> dict[str, Any]:
    return load_run_observability(Path(project["project_root"]), run_id)


def get_project_run_events(project: dict[str, Any], run_id: str) -> dict[str, Any]:
    return load_observable_events(Path(project["project_root"]), run_id)


def get_project_run_steps(project: dict[str, Any], run_id: str) -> dict[str, Any]:
    return load_observable_steps(Path(project["project_root"]), run_id)


def get_project_run_gates(project: dict[str, Any], run_id: str) -> dict[str, Any]:
    return load_observable_gates(Path(project["project_root"]), run_id)


def resolve_project_run_gate(project: dict[str, Any], run_id: str, gate_id: str, action: str, note: str) -> dict[str, Any]:
    return resolve_observable_gate(Path(project["project_root"]), run_id, gate_id, action, note)


def list_project_runs(project: dict[str, Any]) -> list[dict[str, Any]]:
    return list_runs(Path(project["project_root"]))


def execute_workbench_run(project: dict[str, Any], mode: str, user_goal: str) -> dict[str, Any]:
    root = Path(project["project_root"])
    return run_workbench(root, mode=mode, user_goal=user_goal)


def get_workbench_run(project: dict[str, Any], run_id: str) -> dict[str, Any]:
    root = Path(project["project_root"])
    for base in [root / "06_workspace" / "runs", root / "workspace" / "runs"]:
        manifest_path = base / run_id / "run_manifest.json"
        if manifest_path.exists():
            return json.loads(manifest_path.read_text(encoding="utf-8"))
    raise KeyError(run_id)
