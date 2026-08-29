"""HITL_pause node -- 识别策略 0 星截断后的图内中断点。

在 identification_verify 判定 0 星（完全不可信）时，流程在此通过
LangGraph 的 ``interrupt()`` 暂停，等待用户调整研究对象/识别方法后
resume。模拟函数不直接在节点内改写方向，而是把当前诊断结果作为
interrupt 内容返回给前端，由上游（facade / 前端）收集用户新方向后
以 ``Command(resume=...)`` 恢复，恢复值会写入 ``research_direction``。

节点不 import fastapi，纯函数，输入 state 返回待合并的 dict，与现有
节点风格一致。
"""
from __future__ import annotations

from typing import Any, Dict

from langgraph.types import interrupt

from ..state import EconPaperState


def hitl_pause(state: EconPaperState) -> Dict[str, Any]:
    """识别策略 0 星截断的图内中断点。

    1. 读取 ``state.identification_diag``（含星级与诊断明细）。
    2. 调用 ``interrupt()`` 暂停，payload 携带诊断信息与提示。
    3. 恢复时把用户新方向写入 ``research_direction`` 并清空
       ``hitl_pause_reason``，随后图会重回 identification_verify 重新验证。

    返回：``{"research_direction": new_direction, "hitl_pause_reason": None}``。
    """
    diag = state.get("identification_diag") or {}
    payload = {
        "reason": "identification_0star",
        "message": "识别策略完全不可信（0星），流程已截断。请调整研究设计后继续。",
        "diag": diag,
    }
    # 图内中断：等待上游 resume。resume 值应为新的 research_direction dict。
    new_direction = interrupt(payload)
    if not isinstance(new_direction, dict):
        # 非法 resume 值：保持原方向，避免污染状态
        new_direction = state.get("research_direction")
    return {
        "research_direction": new_direction,
        "hitl_pause_reason": None,
    }


__all__ = ["hitl_pause"]