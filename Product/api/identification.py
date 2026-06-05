"""POST /api/identification/audit — 6th tab real statspai diagnostics endpoint.

Task 44 (ui-gap-fill) — Phase 1 P1: replace placeholder tab with real statspai calls.

行为契约 (BDD 行为 1, 2, 3):
    1. 真实数据: 3 张卡 (pretrend / weak_iv / dag) 来自 statspai 真实诊断
    2. 数据来源: 该端点调 statspai 跑 pretrends / first_stage / anderson_rubin,
       必要时从 results.json + design.json 提取, 统一返回结构化 JSON
    3. 失败兜底: statspai 不可用 / results.json 不是 statspai 格式 →
       返回 `{error, reason}` + 各 card `source=unavailable`, 不抛 500

请求:
    POST /api/identification/audit
    { "results_path": "Results/xxx/results.json", "design_path": "Tasks/xxx/design.json" }

响应 (200):
    {
      "method": "IV",
      "pretrend": { "joint_pvalue": ..., "coefficients": [...], "source": "..." },
      "weak_iv": { "partial_r2": ..., "ar_pvalue": ..., "source": "..." },
      "dag": { "spec": "...", "mermaid": "...", "adjustment_sets": [...], "source": "..." }
    }

    or, 失败兜底:
    {
      "error": "no_artifacts",
      "reason": "...",
      "pretrend": { "source": "unavailable" },
      "weak_iv": { "source": "unavailable" },
      "dag": { "source": "unavailable" }
    }
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from Product.backend.identification_audit_service import run_identification_audit


router = APIRouter()


class IdentificationAuditRequest(BaseModel):
    results_path: str = Field(min_length=1, description="results.json 路径 (相对 REPO_ROOT 或绝对)")
    design_path: str = Field(min_length=1, description="design.json 路径 (相对 REPO_ROOT 或绝对)")


@router.post("/api/identification/audit")
def post_identification_audit(req: IdentificationAuditRequest) -> dict:
    """跑 6th tab 识别审计. 端点边界 try/except — 业务层 service 永远不抛."""
    try:
        payload = run_identification_audit(req.results_path, req.design_path)
        return payload
    except Exception as exc:  # noqa: BLE001 — endpoint boundary
        # service 已经被设计为不抛, 这里只是双保险 (防止 service 内部未来重构漏掉兜底)
        raise HTTPException(
            status_code=500,
            detail=f"identification audit failed: {exc}",
        ) from exc
