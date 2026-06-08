"""POST /api/supervisor/plan — intake-time plan draft endpoint.

Used by App.tsx when the user picks `codex-supervisor` mode. Returns an
8-stage plan draft with topic-bound inspector guidance that
SupervisorPlanReview.tsx renders above the BriefPanel. Approval (onApprove
callback) then mounts the BriefPanel.

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
    """Return the 8-stage plan draft for the brief tab.

    The stage skeleton is shared with the project supervisor plan, while the
    inspector copy is scoped to the user's topic so the preview does not
    smuggle in a fixed research case.
    """
    return {
        "topic": req.topic,
        "stages": get_default_plan_draft(),
        "inspector": {
            "inputs_used": [
                f"用户输入研究方向: {req.topic}",
                f"用户补充说明: {req.note or '暂无'}",
            ],
            "assumptions": [
                f"研究问题边界需围绕『{req.topic}』确认",
                "识别假设等待数据结构、变量角色和方法选择完成后再固定",
            ],
            "evidence_required": [
                "题目对应的数据来源、样本口径和变量角色需要进入审阅",
                "方法前置条件需要由 MethodAgent 核验并写入任务队列",
                "每个产物需要绑定日志、结果文件和证据等级",
            ],
            "risks": [
                "如果数据或变量无法匹配，需要回到题目和数据线索确认",
                "未核验变量和方法只进入任务草案，不进入正式论文状态",
            ],
            "formal_boundary": [
                "当前输出保存为任务规划和审阅材料",
                "正式变量、方法、运行计划和论文正文写入需要显式确认",
            ],
        },
        "evidence_level": "preview_draft",
    }
