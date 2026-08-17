"""generate_outline 节点 (T-06)。

调 LLM 生成 6 章 outline (intro / lit_review / data_desc / methods /
results / conclusion)。

HITL 简化策略 (同 T-04): 此节点**不调 interrupt()**。LangGraph 的 interrupt
在单元测试里不好模拟，故采用 state-driven 简化:
- 若 ``state.user_adjusted_outline`` 存在 (用户在前端拖拽调整后通过
  POST /sessions/{id}/resume 写入)，直接采用，跳过 LLM；
- 否则调 ``call_llm`` 生成大纲文案，并回写固定 6 章结构。

``call_llm`` 是模块级函数，测试通过
``monkeypatch.setattr(nodes.generate_outline, "call_llm", fake)`` 替换。
"""
from __future__ import annotations

from typing import Any

from prompts.outline import build_outline_prompt
from protocols import GenerateOutlineOutput
from state import EconPaperState


def call_llm(prompt: str) -> str:
    """调 LLM 生成大纲文案。

    走 ``llm.call_llm``（运行时 MiniMax；pytest 为占位）。测试通过
    ``monkeypatch.setattr(nodes.generate_outline, "call_llm", ...)`` 替换为
    fake，故必须是模块级函数。
    """
    from llm.call_llm import call_llm as unified_call

    return unified_call(prompt, node_type="outline")


def generate_outline(state: EconPaperState) -> GenerateOutlineOutput:
    """生成 6 章 outline，写入 state.outline。

    HITL resume 路径: state.user_adjusted_outline 存在时直接采用。
    """
    adjusted = state.get("user_adjusted_outline")
    if adjusted:
        return {"outline": adjusted, "current_chapter_index": 0}

    rd: Any = state.get("research_direction")
    if not isinstance(rd, dict):
        rd = {}

    prompt = build_outline_prompt(rd)
    llm_summary = call_llm(prompt)

    from engine.readiness import SLOT_REQUIREMENTS, estimate_ran

    outline = [
        {
            "type": "intro",
            "title": "引言",
            "research_question": rd.get("question", ""),
            "llm_summary": llm_summary,
        },
        {"type": "lit_review", "title": "文献综述"},
        {"type": "data_desc", "title": "数据描述"},
        {"type": "methods", "title": "方法", "method": rd.get("method", "")},
        {"type": "results", "title": "结果"},
        {"type": "conclusion", "title": "结论"},
    ]
    literature_n = len(state.get("literature_entries") or [])
    has_row = estimate_ran(state)
    for chapter in outline:
        chapter["bind"] = {
            "requires": list(SLOT_REQUIREMENTS.get(chapter["type"], ("identification",))),
            "has_treatment_row": has_row,
            "literature_n": literature_n,
        }

    # ADR-0004 Stage 2: 文献条目非空时，给 lit_review 章节加大纲注释，
    # 提示后续 generate_chapter 引用这些文献。
    literature_entries = state.get("literature_entries", []) or []
    for chapter in outline:
        if chapter.get("type") == "lit_review" and literature_entries:
            top_titles = ", ".join(
                str(e.get("title", ""))[:30] for e in literature_entries[:3]
            )
            chapter["literature_hint"] = (
                f"建议引用 {len(literature_entries)} 篇文献，含：{top_titles}"
            )

    # 初始化 current_chapter_index=0，触发 generate_chapter 索引流循环 6 章
    # （否则 generate_chapter 走 legacy 流，只生成 1 章就被 route_after_chapter 当作 idx=None 跳到 translate_code）
    return {"outline": outline, "current_chapter_index": 0}
