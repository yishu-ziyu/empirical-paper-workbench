"""#3: 重生成必须读 revision_suggestions，首轮不能出现 None。"""
from __future__ import annotations

from agent.nodes.generate_chapter import generate_chapter
from agent.nodes.review_chapter import review_chapter

from conftest import make_state, make_write_ready_state


def test_regenerate_user_prompt_contains_revision_suggestions(mock_llm_for):
    """带 revision_suggestions[idx] 的 state 跑 generate_chapter，user 含这句话。"""
    recorder = mock_llm_for("generate_chapter", return_value="NEW METHODS")
    outline = [{"type": "methods", "title": "方法", "method": "DID"}]
    state = make_write_ready_state(
        current_chapter_index=0,
        outline=outline,
        method="DID",
        research_question="医保对住院的影响",
        revision_suggestions=["补平行趋势"],
        review_rubrics=[{"endogeneity": 0.4, "identification": 0.3,
                         "robustness": 0.8, "contribution": 0.7, "readability": 0.8}],
        review_iteration=1,
    )
    generate_chapter(state)
    assert recorder.calls, "generate_chapter 未调 LLM"
    _, user = recorder.calls[0]["args"]
    assert "补平行趋势" in user
    assert "endogeneity" in user or "identification" in user
    assert "不得只增加关键词" in user


def test_first_round_prompt_has_no_none(mock_llm_for):
    """首轮无评审时 user prompt 不出现虚构 None。"""
    recorder = mock_llm_for("generate_chapter", return_value="INTRO")
    outline = [{"type": "intro", "title": "引言"}]
    state = make_write_ready_state(
        current_chapter_index=0,
        outline=outline,
        research_question="Q",
        data_summary="D",
    )
    generate_chapter(state)
    _, user = recorder.calls[0]["args"]
    assert "None" not in user


def test_review_output_still_omits_body_chapters():
    """ReviewOutput 仍不含 body_chapters（只读契约）。"""
    chapter = {
        "type": "methods",
        "title": "方法",
        "content": "本文使用 DID。" + "内容" * 80,
        "status": "generated",
        "versions": ["本文使用 DID。"],
        "chapter_index": 0,
    }
    state = make_state(
        review_enabled=True,
        current_chapter_index=1,
        body_chapters=[chapter],
        research_direction="CHARLS 医保",
    )
    result = review_chapter(state)
    assert "body_chapters" not in result
