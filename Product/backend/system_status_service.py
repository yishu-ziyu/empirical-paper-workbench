"""Aggregate 11 backend services into a single status payload.

Task 41 行为 3: `/api/system/status` 端点聚合返回
{cap_count, cost_total, artifact_count, obs_status, project_id, ...}

设计原则 (解耦审计 2026-06-05):
- 单点真相源 — SystemStatusBar 一次 fetch 拿全部 4 项
- 单 service 失败 = 字段 null, 不抛 — UI graceful degradation
- 内部 try/except 包住每个 sub-aggregator
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from Product.backend.project_service import utc_now
from Product.backend.registry import get_project_by_id_or_transient


def _safe_call(label: str, fn, default: Any = None) -> Any:
    """Wrap a sub-aggregator; return default (null) on any failure."""
    try:
        return fn()
    except Exception as exc:  # noqa: BLE001 — boundary
        return {"_error": f"{label}_unavailable: {type(exc).__name__}: {exc}"}


def _aggregate_capabilities(product_root: Path, repo_root: Path, project_id: str) -> dict[str, Any]:
    """Return cap_count + 列表; from capability_registry."""
    from Product.backend.capability_registry import get_project_capabilities

    payload = get_project_capabilities(product_root, repo_root, project_id)
    cap_dict = payload.get("capability", {}) or {}
    capabilities = cap_dict.get("capabilities", []) or []
    return {
        "cap_count": len(capabilities),
        "capabilities": [
            {
                "id": cap.get("id", ""),
                "name": cap.get("name", cap.get("id", "")),
                "category": cap.get("category", "unknown"),
                "risk_level": cap.get("risk_level", "unknown"),
            }
            for cap in capabilities
        ],
    }


def _aggregate_costs(product_root: Path, repo_root: Path, project_id: str) -> dict[str, Any]:
    """Return cost_total (USD) + 按 service 拆分; from cost_service."""
    from Product.backend.cost_service import get_project_costs

    payload = get_project_costs(product_root, repo_root, project_id)
    summary = (payload.get("costs") or {}).get("summary") or {}
    events = (payload.get("costs") or {}).get("events") or []
    cost_total = float(summary.get("total_estimated_usd", 0.0) or 0.0)

    # breakdown 按 capability_id (proxy for service) 聚合
    breakdown_map: dict[str, float] = {}
    for ev in events:
        cap_id = ev.get("capability_id", "unknown") or "unknown"
        breakdown_map[cap_id] = breakdown_map.get(cap_id, 0.0) + float(ev.get("estimated_usd", 0.0) or 0.0)
    breakdown = [
        {"service": k, "amount": round(v, 4)}
        for k, v in sorted(breakdown_map.items(), key=lambda kv: -kv[1])
    ]
    return {
        "cost_total": round(cost_total, 4),
        "cost_breakdown": breakdown,
    }


def _aggregate_artifacts(product_root: Path, project_id: str) -> dict[str, Any]:
    """Return artifact_count + 列表; 跨该 project 的所有 workflow 聚合."""
    from Product.backend.workflow_service import list_workflows, load_artifacts

    # 该 project 关联的 workflow 都属于同一 product root 下的 state/.workflows/
    workflows = list_workflows(product_root)
    artifacts: list[dict[str, Any]] = []
    for wf in workflows:
        wf_project = wf.get("project_id")
        if wf_project and wf_project != project_id:
            continue
        wf_id = wf.get("id", "")
        try:
            items = load_artifacts(product_root, wf_id)
        except Exception:  # noqa: BLE001 — single workflow failure must not break aggregate
            continue
        for item in items:
            artifacts.append(
                {
                    "name": item.get("name", item.get("id", "artifact")),
                    "path": item.get("path", ""),
                    "size": item.get("size", 0),
                    "created_at": item.get("created_at", ""),
                    "workflow_id": wf_id,
                }
            )
    return {
        "artifact_count": len(artifacts),
        "artifacts": artifacts[:20],  # cap payload size — 详情展开时按需再拉
    }


def _aggregate_observability(product_root: Path, project_id: str) -> dict[str, Any]:
    """Return obs_status — 扫 state/runs/*/run_manifest.json 找该 project 最近一次 run 的状态."""
    runs_root = product_root / "state" / "runs"
    if not runs_root.exists():
        return {"obs_status": "no_runs", "obs_detail": None}

    latest: tuple[float, str, str] | None = None  # (mtime, status, run_id)
    for manifest_path in runs_root.glob("*/run_manifest.json"):
        project_field = ""
        status = "unknown"
        try:
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
            project_field = payload.get("project_id", "")
            status = payload.get("status", "unknown")
        except Exception:  # noqa: BLE001
            continue
        if project_field and project_field != project_id:
            continue
        try:
            mtime = manifest_path.stat().st_mtime
        except OSError:
            continue
        run_id = manifest_path.parent.name
        if latest is None or mtime > latest[0]:
            latest = (mtime, status, run_id)

    if latest is None:
        return {"obs_status": "no_runs", "obs_detail": None}
    return {
        "obs_status": latest[1],
        "obs_detail": {"run_id": latest[2]},
    }


def aggregate(product_root: Path, repo_root: Path, project_id: str, topic_slug: str = "") -> dict[str, Any]:
    """Single source of truth for the status bar.

    Returns a typed dict. Any sub-aggregator failure becomes ``null`` in the
    field (or ``_error`` in the diagnostic block) — never raises.
    """
    project = get_project_by_id_or_transient(product_root, repo_root, project_id)
    resolved_project_id = project.get("id", project_id)

    cap_block = _safe_call("capability_registry", lambda: _aggregate_capabilities(product_root, repo_root, resolved_project_id))
    cost_block = _safe_call("cost_service", lambda: _aggregate_costs(product_root, repo_root, resolved_project_id))
    artifact_block = _safe_call("artifact_service", lambda: _aggregate_artifacts(product_root, resolved_project_id))
    obs_block = _safe_call("observability_service", lambda: _aggregate_observability(product_root, resolved_project_id))

    def _value(block: Any, key: str, default: Any = None) -> Any:
        if isinstance(block, dict) and "_error" not in block:
            return block.get(key, default)
        return default

    def _list_value(block: Any, key: str) -> Any:
        if isinstance(block, dict) and "_error" not in block:
            return block.get(key, [])
        return []

    return {
        "_meta": {
            "evidence_level": "local_aggregate",
            "service": "system_status_service",
            "generated_at": utc_now(),
        },
        "project_id": resolved_project_id,
        "topic_slug": topic_slug,
        "cap_count": _value(cap_block, "cap_count"),
        "cost_total": _value(cost_block, "cost_total"),
        "artifact_count": _value(artifact_block, "artifact_count"),
        "obs_status": _value(obs_block, "obs_status", "unknown"),
        "capabilities": _list_value(cap_block, "capabilities"),
        "artifacts": _list_value(artifact_block, "artifacts"),
        "cost_breakdown": _list_value(cost_block, "cost_breakdown"),
        "diagnostics": {
            "capability_registry": cap_block if isinstance(cap_block, dict) and "_error" in cap_block else None,
            "cost_service": cost_block if isinstance(cost_block, dict) and "_error" in cost_block else None,
            "artifact_service": artifact_block if isinstance(artifact_block, dict) and "_error" in artifact_block else None,
            "observability_service": obs_block if isinstance(obs_block, dict) and "_error" in obs_block else None,
        },
    }
