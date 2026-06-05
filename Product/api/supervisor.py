"""POST /api/supervisor/plan — intake-time plan draft endpoint.

Used by App.tsx when the user picks `codex-supervisor` mode. Returns the
static 8-stage plan that SupervisorPlanReview.tsx renders above the
BriefPanel. Approval (onApprove callback) then mounts the BriefPanel.

The "real" supervisor plan generation requires a registered project and
confirmed upstream states (ResearchQuestion, VariableRoleSet, DesignSpec,
RunPlan). That is served by:
  - GET  /api/v1/projects/{project_id}/supervisor-plan
  - POST /api/v1/projects/{project_id}/supervisor-plan

This endpoint is the lightweight, no-project-required preview.
"""
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from Product.backend.supervisor_plan_service import get_default_plan_draft

router = APIRouter()


class SupervisorPlanRequest(BaseModel):
    topic: str = Field(min_length=1)
    note: str = ""


@router.post("/api/supervisor/plan")
def post_supervisor_plan(req: SupervisorPlanRequest) -> dict:
    """Return the static 8-stage plan draft for the brief tab.

    Currently the plan is fully static (mirrors the DEFAULT_STAGES in
    SupervisorPlanReview.tsx) so the frontend can render without depending
    on a registered project. A future revision can dispatch to LLM
    supervisor for a per-topic draft.
    """
    return {
        "topic": req.topic,
        "stages": get_default_plan_draft(),
        "inspector": {
            "inputs_used": [
                f"用户输入研究方向: {req.topic}",
                "附件信息: 0 个本地材料 (预览阶段未扫描附件)",
            ],
            "assumptions": [
                "工具变量排他性约束: 假定工具变量仅通过内生变量影响结果变量",
                "面板数据平行趋势假定: 政策试点前处理组与对照组具有平行趋势",
            ],
            "evidence_required": [
                "数据字段画像完成率需达到 100%",
                "回归方程式设计必须明确控制个人、家庭和省份三级固定效应",
                "人工审阅确认 VariableRoleSet 方可启动正式跑码",
            ],
            "risks": [
                "【风险提示】本地数据未识别到明显的处理时点变量，可能无法直接应用经典多期DID。",
                "【环境警告】本地未检测到可用的 R 语言环境，相关 DML 估算器将被降级为 Python 线性估算。",
            ],
            "formal_boundary": [
                "此步骤属于 Plan 草案评估阶段，完全运行在 Draft Layer",
                "未经人工核验通过, 绝不会向 Manuscripts 或 formal state 目录写入任何数据",
            ],
        },
        "evidence_level": "preview_draft",
    }
