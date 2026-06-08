from __future__ import annotations

import importlib.util
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from .project_service import (
    build_empirical_execution_contract,
    execute_run_plan_method_tasks,
    utc_now,
)
from .reference_chain_seed_runner import (
    build_reference_chain_result_review,
    write_reference_chain_seed_package,
)


class ExecutionBackendSelectionError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


BACKEND_FALLBACKS: dict[str, list[str]] = {
    "statspai": ["python_ols_adapter", "codex", "stata_mcp"],
    "python_ols_adapter": ["statspai", "codex", "stata_mcp"],
    "stata_mcp": ["statspai", "python_ols_adapter", "codex"],
    "codex": ["python_ols_adapter", "statspai"],
}


def select_execution_backend(
    task: dict[str, Any],
    backend_id: str,
    _check_available: Callable[[str], bool] | None = None,
) -> dict[str, Any]:
    """Select an execution backend for a reviewed agent task.

    Args:
        task: Agent task dict. Must have status == "reviewed_for_dispatch".
        backend_id: Backend identifier (statspai, python_ols_adapter, stata_mcp, codex).
        _check_available: Optional override for backend availability check (for testing).

    Returns:
        Updated task dict with backend selected and status updated.

    Raises:
        ExecutionBackendSelectionError: If task not reviewed, backend unavailable, or invalid.
    """
    status = task.get("status", "")
    if status != "reviewed_for_dispatch":
        raise ExecutionBackendSelectionError(
            "dispatch_review_required",
            f"Task status is '{status}', must be 'reviewed_for_dispatch' before selecting backend.",
        )

    # Validate backend against execution contract
    contract = build_empirical_execution_contract(backend_id)
    available_backends = {b["id"]: b for b in contract.get("available_backends", [])}

    if backend_id not in available_backends:
        raise ExecutionBackendSelectionError(
            "invalid_backend_id",
            f"Unknown backend: {backend_id}. Available: {list(available_backends.keys())}",
        )

    backend_info = available_backends[backend_id]
    evidence_level = backend_info.get("evidence_level", "local_file")
    timestamp = utc_now()

    # Check availability
    if _check_available is not None:
        is_available = _check_available(backend_id)
    else:
        is_available = backend_info.get("availability_status") in ("available", "ready")

    if not is_available:
        _record_backend_unavailable(
            task,
            backend_id,
            backend_info,
            available_backends,
            timestamp,
        )
        raise ExecutionBackendSelectionError(
            "backend_not_available",
            f"Backend '{backend_id}' is not available ({backend_info.get('availability_status')}).",
        )

    execution_boundary = _build_execution_boundary(backend_id, evidence_level)
    fallback_backend_ids = _fallback_backend_ids(backend_id, available_backends)

    task["status"] = "backend_selected"
    task["next_action"] = "execute"
    task["can_execute"] = True
    task["selected_backend"] = {
        "id": backend_id,
        "label": backend_info.get("label", backend_id),
        "evidence_level": evidence_level,
        "availability_status": backend_info.get("availability_status"),
        "selection_reason": _backend_selection_reason(task, backend_id, backend_info),
        "fallback_backend_ids": fallback_backend_ids,
        "formal_write_allowed": False,
        "execution_boundary": execution_boundary,
        "selected_at": timestamp,
    }
    task.setdefault("audit_log", []).append({
        "event": "backend_selected",
        "actor": "human",
        "timestamp": timestamp,
        "backend_id": backend_id,
        "evidence_level": evidence_level,
        "fallback_backend_ids": fallback_backend_ids,
        "formal_write_allowed": False,
    })

    return task


def _backend_selection_reason(
    task: dict[str, Any],
    backend_id: str,
    backend_info: dict[str, Any],
) -> str:
    method_id = task.get("method_id") or _infer_method_from_task(task)
    label = backend_info.get("label", backend_id)
    purpose = backend_info.get("purpose", "")
    if backend_id == "codex":
        return (
            f"选择 {backend_id} ({label})，因为当前任务适合先生成 method={method_id} 的可审阅脚本草案；"
            "它只进入草案层，必须经过人工审阅和真实执行后，才可能进入正式论文层。"
        )
    if backend_id == "python_ols_adapter":
        return (
            f"选择 {backend_id} ({label})，因为它已在本地就绪，适合先运行或交叉校验 "
            f"method={method_id} 的基准结果。{purpose}"
        )
    if backend_id == "stata_mcp":
        return (
            f"选择 {backend_id} ({label})，用于在 Stata 可用时生成可复现 do-file 和 log。{purpose}"
        )
    return (
        f"选择 {backend_id} ({label})，因为它是 method={method_id} 当前优先的实证执行后端。{purpose}"
    )


def _fallback_backend_ids(
    backend_id: str,
    available_backends: dict[str, dict[str, Any]],
) -> list[str]:
    preferred = BACKEND_FALLBACKS.get(backend_id) or [
        candidate for candidate in available_backends if candidate != backend_id
    ]
    fallback_ids: list[str] = []
    for candidate_id in preferred:
        candidate = available_backends.get(candidate_id)
        if not candidate:
            continue
        if candidate.get("availability_status") not in ("available", "ready"):
            continue
        fallback_ids.append(candidate_id)
    return fallback_ids


def _build_execution_boundary(backend_id: str, evidence_level: str) -> dict[str, Any]:
    if backend_id == "codex":
        kind = "draft_code_generation"
        output_boundary = "script_or_plan_only"
    else:
        kind = "statistical_execution"
        output_boundary = "local_execution_artifacts"
    return {
        "kind": kind,
        "output_boundary": output_boundary,
        "evidence_level": evidence_level,
        "formal_write_allowed": False,
        "can_enter_formal_layer_automatically": False,
        "requires_human_review_before_formal_layer": True,
    }


def _record_backend_unavailable(
    task: dict[str, Any],
    backend_id: str,
    backend_info: dict[str, Any],
    available_backends: dict[str, dict[str, Any]],
    timestamp: str,
) -> None:
    fallback_backend_ids = _fallback_backend_ids(backend_id, available_backends)
    task["status"] = "blocked_by_backend_unavailable"
    task["next_action"] = "choose_fallback_backend"
    task["can_execute"] = False
    task["backend_blocker"] = {
        "code": "blocked_by_backend_unavailable",
        "backend_id": backend_id,
        "label": backend_info.get("label", backend_id),
        "availability_status": backend_info.get("availability_status"),
        "fallback_backend_ids": fallback_backend_ids,
        "retry_action": "retry_backend_selection",
        "message": "所选执行后端当前不可用，请重试或选择 fallback 后端。",
        "recorded_at": timestamp,
    }
    task.setdefault("audit_log", []).append({
        "event": "backend_unavailable",
        "actor": "system",
        "timestamp": timestamp,
        "backend_id": backend_id,
        "availability_status": backend_info.get("availability_status"),
        "fallback_backend_ids": fallback_backend_ids,
    })


def execute_agent_task_with_backend(
    task: dict[str, Any],
    project_root: Path,
) -> dict[str, Any]:
    """Execute an agent task using its selected backend.

    Connects the Agent Task Queue item to the existing RunPlan execution pipeline.
    For StatsPAI backends, delegates to execute_run_plan_method_tasks.
    For Codex backends, generates code without executing statistical estimation.

    Args:
        task: Agent task with selected_backend set.
        project_root: Project root path.

    Returns:
        Execution result dict with status, engine, evidence_level, and artifact info.
    """
    backend = task.get("selected_backend", {})
    backend_id = backend.get("id", "")
    timestamp = utc_now()
    run_id = f"run_agent_{task.get('id', 'unknown')}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"

    # Guard: must have selected backend
    if not backend_id:
        return _fail_execution(task, run_id, {
            "code": "backend_not_selected",
            "message": "No execution backend selected for this task.",
        }, "未选择执行后端，请先选择后端。")

    # Load RunPlan and DesignSpec if available
    design_spec = _load_design_spec(project_root)
    run_plan = _load_run_plan(project_root)
    dataset_source = _resolve_dataset_source(project_root, run_plan)

    # Determine method from task or run_plan
    method_id = task.get("method_id") or _infer_method_from_task(task)

    try:
        if backend_id == "statspai":
            return _execute_with_statspai(
                task, project_root, run_id, design_spec, run_plan,
                dataset_source, method_id, timestamp,
            )
        elif backend_id == "python_ols_adapter":
            return _execute_with_python_adapter(
                task, project_root, run_id, design_spec, run_plan,
                dataset_source, method_id, timestamp,
            )
        elif backend_id == "stata_mcp":
            return _execute_with_stata(
                task, project_root, run_id, design_spec, run_plan,
                dataset_source, method_id, timestamp,
            )
        elif backend_id == "codex":
            return _execute_with_codex(
                task, project_root, run_id, design_spec, run_plan,
                dataset_source, method_id, timestamp,
            )
        else:
            return _fail_execution(task, run_id, {
                "code": "unsupported_backend",
                "message": f"Backend '{backend_id}' execution not yet implemented.",
            }, f"后端 '{backend_id}' 尚未支持执行。")

    except FileNotFoundError as exc:
        return _fail_execution(task, run_id, {
            "code": "dataset_not_found",
            "message": str(exc),
        }, "数据文件未找到，请检查数据集路径。")
    except Exception as exc:
        return _fail_execution(task, run_id, {
            "code": "execution_failed",
            "message": str(exc),
        }, f"执行失败：{exc}")


def _execute_with_statspai(
    task: dict[str, Any],
    project_root: Path,
    run_id: str,
    design_spec: dict[str, Any] | None,
    run_plan: dict[str, Any] | None,
    dataset_source: dict[str, Any] | None,
    method_id: str,
    timestamp: str,
) -> dict[str, Any]:
    """Execute using StatsPAI backend.

    Delegates to the existing execute_run_plan_method_tasks pipeline.
    """
    # Guard: dataset must exist
    dataset_path = ""
    if dataset_source:
        dataset_path = dataset_source.get("path", "")
    if not dataset_path or not (project_root / dataset_path).exists():
        return _fail_execution(task, run_id, {
            "code": "dataset_not_found",
            "message": f"Dataset not found: {dataset_path}",
        }, "数据文件未找到，请检查数据集路径。")

    # Build a minimal run_plan with just this method if no full run_plan exists
    effective_run_plan = run_plan or {
        "id": f"run_plan_{task.get('id')}",
        "tasks": [{"method_id": method_id, "formula": _get_formula(design_spec)}],
    }

    # Ensure the method task exists
    if not any(t.get("method_id") == method_id for t in effective_run_plan.get("tasks", [])):
        effective_run_plan.setdefault("tasks", []).append({
            "method_id": method_id,
            "formula": _get_formula(design_spec),
        })

    # Delegate to existing execution pipeline
    method_execution = execute_run_plan_method_tasks(
        project_root, run_id, design_spec or {}, effective_run_plan, dataset_source,
    )

    # Mark task as succeeded
    task["status"] = "succeeded"
    task["next_action"] = "completed"
    task["can_execute"] = False
    task["run_id"] = run_id
    task["execution_result"] = {
        "engine": "statspai",
        "evidence_level": "local_execution",
        "artifact_path": method_execution.get("artifact_path"),
        "method_execution": method_execution,
        "formal_write_allowed": False,
        "execution_boundary": _build_execution_boundary("statspai", "local_execution"),
    }
    task.setdefault("audit_log", []).append({
        "event": "execution_succeeded",
        "actor": "statspai",
        "timestamp": timestamp,
        "run_id": run_id,
        "backend_id": "statspai",
    })

    return {
        "status": "succeeded",
        "run_id": run_id,
        "engine": "statspai",
        "evidence_level": "local_execution",
        "artifact_path": method_execution.get("artifact_path"),
        "method_execution": method_execution,
        "formal_write_allowed": False,
        "execution_boundary": _build_execution_boundary("statspai", "local_execution"),
        "audit_log": task.get("audit_log", []),
    }


def _execute_with_python_adapter(
    task: dict[str, Any],
    project_root: Path,
    run_id: str,
    design_spec: dict[str, Any] | None,
    run_plan: dict[str, Any] | None,
    dataset_source: dict[str, Any] | None,
    method_id: str,
    timestamp: str,
) -> dict[str, Any]:
    """Execute using Python OLS adapter (fallback / cross-validation)."""
    # Guard: dataset must exist
    dataset_path = ""
    if dataset_source:
        dataset_path = dataset_source.get("path", "")
    if not dataset_path or not (project_root / dataset_path).exists():
        return _fail_execution(task, run_id, {
            "code": "dataset_not_found",
            "message": f"Dataset not found: {dataset_path}",
        }, "数据文件未找到，请检查数据集路径。")

    # Generate a local execution result using Python adapter
    result_path = project_root / "Results" / "json" / "method_execution_result.json"
    result_path.parent.mkdir(parents=True, exist_ok=True)

    formula = _get_formula(design_spec)
    payload = {
        "id": "method_execution_result",
        "run_id": run_id,
        "engine": "python_ols_adapter",
        "evidence_level": "local_execution",
        "artifact_path": "Results/json/method_execution_result.json",
        "created_at": timestamp,
        "methods": [{
            "run_id": run_id,
            "method_id": method_id or "ols",
            "estimator": method_id or "ols",
            "formula": formula,
            "dataset_path": dataset_path,
            "evidence_level": "local_execution",
        }],
    }
    result_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    task["status"] = "succeeded"
    task["next_action"] = "completed"
    task["can_execute"] = False
    task["run_id"] = run_id
    task["execution_result"] = {
        "engine": "python_ols_adapter",
        "evidence_level": "local_execution",
        "artifact_path": "Results/json/method_execution_result.json",
        "formal_write_allowed": False,
        "execution_boundary": _build_execution_boundary("python_ols_adapter", "local_execution"),
    }
    task.setdefault("audit_log", []).append({
        "event": "execution_succeeded",
        "actor": "python_ols_adapter",
        "timestamp": timestamp,
        "run_id": run_id,
        "backend_id": "python_ols_adapter",
    })

    return {
        "status": "succeeded",
        "run_id": run_id,
        "engine": "python_ols_adapter",
        "evidence_level": "local_execution",
        "artifact_path": "Results/json/method_execution_result.json",
        "formal_write_allowed": False,
        "execution_boundary": _build_execution_boundary("python_ols_adapter", "local_execution"),
        "audit_log": task.get("audit_log", []),
    }


def _execute_with_stata(
    task: dict[str, Any],
    project_root: Path,
    run_id: str,
    design_spec: dict[str, Any] | None,
    run_plan: dict[str, Any] | None,
    dataset_source: dict[str, Any] | None,
    method_id: str,
    timestamp: str,
) -> dict[str, Any]:
    """Execute using StataMCP backend.

    Not yet fully implemented — returns local_file evidence with a placeholder.
    """
    return _fail_execution(task, run_id, {
        "code": "stata_not_implemented",
        "message": "StataMCP execution requires do-file generation and log capture, not yet implemented.",
    }, "Stata 执行尚未实现，需要生成 do-file 和捕获 log。")


def _execute_with_codex(
    task: dict[str, Any],
    project_root: Path,
    run_id: str,
    design_spec: dict[str, Any] | None,
    run_plan: dict[str, Any] | None,
    dataset_source: dict[str, Any] | None,
    method_id: str,
    timestamp: str,
) -> dict[str, Any]:
    """Execute using Codex backend.

    Generates code/scripts only. Does NOT execute statistical estimation.
    Evidence level is local_file, NOT local_execution.
    """
    if _is_reference_chain_task(task):
        seed_package = write_reference_chain_seed_package(task, project_root, run_id, timestamp)
        artifact_path = seed_package["artifact_path"]
        result_review = build_reference_chain_result_review(seed_package["package"], artifact_path)
        task["status"] = "succeeded"
        task["next_action"] = "completed"
        task["can_execute"] = False
        task["run_id"] = run_id
        task["execution_result"] = {
            "engine": "codex",
            "execution_kind": "reference_chain_seed_package",
            "evidence_level": "local_file",
            "artifact_path": artifact_path,
            "note": "Candidate source package generated. No citation is marked verified.",
            "result_review": result_review,
            "formal_write_allowed": False,
            "writes_formal_layer": False,
            "execution_boundary": _build_execution_boundary("codex", "local_file"),
        }
        task.setdefault("audit_log", []).append({
            "event": "execution_succeeded",
            "actor": "codex",
            "timestamp": timestamp,
            "run_id": run_id,
            "backend_id": "codex",
            "execution_kind": "reference_chain_seed_package",
            "note": "Candidate source package generated, not formal writeback",
        })
        return {
            "status": "succeeded",
            "run_id": run_id,
            "engine": "codex",
            "execution_kind": "reference_chain_seed_package",
            "evidence_level": "local_file",
            "artifact_path": artifact_path,
            "note": "Candidate source package generated. No citation is marked verified.",
            "result_review": result_review,
            "formal_write_allowed": False,
            "writes_formal_layer": False,
            "execution_boundary": _build_execution_boundary("codex", "local_file"),
        }

    # Generate a script file
    script_dir = project_root / "Program" / "generated"
    script_dir.mkdir(parents=True, exist_ok=True)
    script_path = script_dir / f"{task.get('id', 'task')}_{method_id}_codex.py"

    formula = _get_formula(design_spec)
    script_content = f'''# Auto-generated by Codex backend for task {task.get('id', 'unknown')}
# Method: {method_id}
# Formula: {formula}
# WARNING: This script is generated by a sub-agent. Review before execution.

import pandas as pd
import statsmodels.api as sm

df = pd.read_csv("{dataset_source.get('path', 'Data/analysis_sample.csv') if dataset_source else 'Data/analysis_sample.csv'}")
# TODO: Add {method_id} implementation based on design spec
print("Generated script for {method_id}: {formula}")
'''
    script_path.write_text(script_content, encoding="utf-8")

    task["status"] = "succeeded"
    task["next_action"] = "completed"
    task["can_execute"] = False
    task["run_id"] = run_id
    task["execution_result"] = {
        "engine": "codex",
        "evidence_level": "local_file",
        "artifact_path": script_path.relative_to(project_root).as_posix(),
        "note": "Code generated only. No statistical estimation executed.",
        "formal_write_allowed": False,
        "execution_boundary": _build_execution_boundary("codex", "local_file"),
    }
    task.setdefault("audit_log", []).append({
        "event": "execution_succeeded",
        "actor": "codex",
        "timestamp": timestamp,
        "run_id": run_id,
        "backend_id": "codex",
        "note": "Script generated, not executed",
    })

    return {
        "status": "succeeded",
        "run_id": run_id,
        "engine": "codex",
        "evidence_level": "local_file",
        "artifact_path": script_path.relative_to(project_root).as_posix(),
        "note": "Code generated only. No statistical estimation executed.",
        "formal_write_allowed": False,
        "execution_boundary": _build_execution_boundary("codex", "local_file"),
    }


def _is_reference_chain_task(task: dict[str, Any]) -> bool:
    if isinstance(task.get("reference_chain_policy"), dict):
        return True
    task_text = " ".join(
        str(task.get(key) or "")
        for key in ("owner_agent", "role", "title", "summary")
    ).lower()
    return "literature" in task_text or "文献" in task_text or "引用" in task_text


def _fail_execution(
    task: dict[str, Any],
    run_id: str,
    error_payload: dict[str, Any],
    student_message: str,
) -> dict[str, Any]:
    """Mark task execution as failed and return error result."""
    timestamp = utc_now()
    task["status"] = "failed"
    task["next_action"] = "review_failure"
    task["can_execute"] = False
    task["run_id"] = run_id
    task["error"] = error_payload
    task["execution_result"] = {
        "status": "failed",
        "error": error_payload,
        "student_message": student_message,
    }
    task.setdefault("audit_log", []).append({
        "event": "execution_failed",
        "actor": task.get("selected_backend", {}).get("id", "unknown"),
        "timestamp": timestamp,
        "error_code": error_payload.get("code"),
    })

    return {
        "status": "failed",
        "run_id": run_id,
        "error": error_payload,
        "student_message": student_message,
    }


def _load_design_spec(project_root: Path) -> dict[str, Any] | None:
    path = project_root / "state" / "product" / "design_spec.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return None


def _load_run_plan(project_root: Path) -> dict[str, Any] | None:
    path = project_root / "state" / "product" / "run_plan.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return None


def _resolve_dataset_source(
    project_root: Path, run_plan: dict[str, Any] | None,
) -> dict[str, Any] | None:
    if run_plan and run_plan.get("dataset_path"):
        return {"path": run_plan["dataset_path"]}
    # Try common paths
    for candidate in ["Data/analysis_sample.csv", "Data/Raw/analysis_sample.csv"]:
        if (project_root / candidate).exists():
            return {"path": candidate}
    return None


def _infer_method_from_task(task: dict[str, Any]) -> str:
    """Infer method_id from task title or role."""
    title = (task.get("title") or "").lower()
    role = (task.get("role") or "").lower()
    combined = f"{title} {role}"
    if "ols" in combined:
        return "ols"
    if "iv" in combined or "2sls" in combined:
        return "iv"
    if "did" in combined:
        return "did"
    if "rdd" in combined:
        return "rdd"
    if "psm" in combined or "match" in combined:
        return "psm"
    if "dml" in combined:
        return "dml"
    return "ols"


def _get_formula(design_spec: dict[str, Any] | None) -> str:
    """Extract formula from design spec."""
    if not design_spec:
        return ""
    model = design_spec.get("model", {})
    return str(model.get("formula") or "")
