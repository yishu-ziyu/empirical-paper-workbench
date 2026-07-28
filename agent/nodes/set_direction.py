"""set_direction 节点 (T-06)。

把 backend endpoint 写入 ``state.research_direction`` 的用户输入透传确认。
后续 graph 集成时可在此处做校验 / 规范化（method 是否在 38 种内、template
是否合法等），本 ticket 只做透传以保持 graph 流转可用。
"""
from __future__ import annotations

from protocols import SetDirectionOutput
from state import EconPaperState


def set_direction(state: EconPaperState) -> SetDirectionOutput:
    """透传 ``state.research_direction``。

    backend POST /sessions/{id}/direction 已把
    {question, dv, iv, controls, method, template} 写入 state.research_direction，
    此节点确认该字段并向下流传。
    """
    return {"research_direction": state.get("research_direction")}
