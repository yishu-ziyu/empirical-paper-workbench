from __future__ import annotations

from pathlib import Path
from typing import Any


STATSPAI_PATH = Path("/Users/mahaoxuan/Desktop/经济学论文/StatsPAI")


def _infer_risk_level(category: str) -> str:
    high_risk = {"causal", "bayesian", "dml", "decomposition"}
    medium_risk = {"iv", "panel", "timeseries", "spatial", "survival", "robustness"}
    if category in high_risk:
        return "high"
    if category in medium_risk:
        return "medium"
    return "low"


def _infer_allowed_roles(category: str) -> list[str]:
    if category in {"regression", "causal", "panel", "timeseries", "spatial", "iv", "dml", "decomposition", "robustness", "inference", "diagnostics"}:
        return ["modeling_agent", "robustness_agent", "data_agent"]
    if category in {"output", "smart", "power"}:
        return ["modeling_agent", "writing_agent", "robustness_agent"]
    if category in {"survey", "survival"}:
        return ["modeling_agent", "data_agent"]
    return ["modeling_agent"]


def _spec_to_json_schema(spec: Any) -> dict[str, Any]:
    """Convert StatsPAI FunctionSpec params to JSON Schema."""
    properties: dict[str, Any] = {}
    required: list[str] = []
    for param in getattr(spec, "params", []):
        ptype = getattr(param, "ptype", "string")
        schema_type = "string"
        if ptype in {"int", "float"}:
            schema_type = "number"
        elif ptype == "bool":
            schema_type = "boolean"
        elif ptype in {"list", "tuple"}:
            schema_type = "array"
        properties[getattr(param, "name", "arg")] = {
            "type": schema_type,
            "description": getattr(param, "description", ""),
        }
        if getattr(param, "required", False):
            required.append(getattr(param, "name", "arg"))
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def index_statspai_capabilities(statspai_path: Path | None = None) -> list[dict[str, Any]]:
    """Index all StatsPAI functions as capabilities.

    Dynamically imports statspai to avoid hard dependency failures.
    If StatsPAI is not available, returns a minimal placeholder list.
    """
    target_path = statspai_path or STATSPAI_PATH
    try:
        import sys
        if str(target_path) not in sys.path:
            sys.path.insert(0, str(target_path))
        import statspai as sp  # type: ignore[import-untyped]
    except Exception:
        return []

    capabilities: list[dict[str, Any]] = []
    try:
        function_names = sp.list_functions()
    except Exception:
        return capabilities

    for fn_name in function_names:
        try:
            spec = sp.describe_function(fn_name)
        except Exception:
            continue
        category = getattr(spec, "category", "unknown")
        capabilities.append({
            "id": f"cap_statspai_{fn_name}",
            "namespace": "statspai",
            "name": fn_name,
            "category": category,
            "description": getattr(spec, "description", ""),
            "risk_level": _infer_risk_level(category),
            "cost_model": "local_cpu_time",
            "allowed_roles": _infer_allowed_roles(category),
            "adapter_path": "Product.backend.statspai_adapter.execute_statspai",
            "input_schema": _spec_to_json_schema(spec),
            "output_schema": {"type": "object"},
            "status": "executable",
            "assumptions": getattr(spec, "assumptions", []),
            "pre_conditions": getattr(spec, "pre_conditions", []),
            "alternatives": getattr(spec, "alternatives", []),
        })
    return capabilities


def get_statspai_info() -> dict[str, Any]:
    """Return StatsPAI installation info."""
    try:
        import statspai as sp  # type: ignore[import-untyped]
        version = getattr(sp, "__version__", "unknown")
        function_count = len(sp.list_functions())
        return {
            "available": True,
            "path": str(STATSPAI_PATH),
            "version": version,
            "function_count": function_count,
        }
    except Exception as exc:
        return {
            "available": False,
            "path": str(STATSPAI_PATH),
            "error": str(exc),
        }
