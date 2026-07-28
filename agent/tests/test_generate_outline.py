"""T-06: set_direction + generate_outline 节点契约测试。

从 backend/tests/test_outline.py 迁移而来（ADR-0003 Stage C 命名约定：
generate_outline 是 agent 节点，测试归 agent/tests/）。

契约：
- set_direction 节点把研究方向写入 state
- generate_outline 生成 6 章 outline (intro/lit_review/data_desc/methods/results/conclusion)
- generate_outline 若 state 有 user_adjusted_outline 则直接采用 (HITL 简化)

HITL 简化策略: generate_outline 不调 interrupt()；从 state 读
user_adjusted_outline。
"""
from nodes.generate_outline import generate_outline
from nodes.set_direction import set_direction

from conftest import make_state


def test_set_direction_writes_research_direction():
    """set_direction 节点把用户输入的研究方向透传写入 state。"""
    rd = {
        "question": "教育对收入的影响",
        "dv": "income",
        "iv": "education",
        "controls": ["age", "gender"],
        "method": "OLS",
        "template": "cn_journal",
    }
    state = make_state(research_direction=rd)
    result = set_direction(state)
    assert "research_direction" in result
    assert result["research_direction"] == rd
    assert result["research_direction"]["question"] == "教育对收入的影响"


def test_generate_outline_creates_six_chapters(mock_llm_for):
    """generate_outline 生成 6 章 outline，6 种 type 齐全，且调用了 LLM。"""
    recorder = mock_llm_for("generate_outline")
    state = make_state(research_direction={"question": "test q", "method": "OLS"})
    result = generate_outline(state)
    outline = result["outline"]
    assert isinstance(outline, list)
    assert len(outline) == 6
    types = [ch["type"] for ch in outline]
    for expected in (
        "intro",
        "lit_review",
        "data_desc",
        "methods",
        "results",
        "conclusion",
    ):
        assert expected in types, f"outline missing chapter type: {expected}"
    # generate_outline 必须调用 call_llm (mock 记录)
    assert len(recorder.calls) > 0, "generate_outline did not call the LLM"


def test_generate_outline_uses_user_adjusted_outline(mock_llm_for):
    """state 有 user_adjusted_outline 时直接采用，且不再调 LLM (HITL resume 路径)。"""
    recorder = mock_llm_for("generate_outline")
    adjusted = [
        {"type": "intro", "title": "自定义引言"},
        {"type": "methods", "title": "自定义方法"},
    ]
    state = make_state(
        user_adjusted_outline=adjusted,
        research_direction={"question": "x", "method": "OLS"},
    )
    result = generate_outline(state)
    assert result["outline"] == adjusted
    assert len(recorder.calls) == 0, (
        "generate_outline should skip LLM when user_adjusted_outline is present"
    )
