"""批次 4 联调：结果章写出后含 treatment_row；另造处理行接地失败。

只测公开函数 generate_chapter / check_grounding。
不改产品文件。执行 1/2 未落地时本文件可以红。
"""
from __future__ import annotations

from conftest import make_write_ready_state
from agent.nodes.generate_chapter import generate_chapter

RESULTS_OUTLINE = [{"type": "results", "title": "结果"}]


def test_generate_results_content_contains_treatment_row(mock_llm_for):
    """mock LLM 只写不含表的散文时，content 仍须含 estimate.treatment_row。"""
    mock_llm_for("generate_chapter", return_value="年龄与收入呈正相关。")
    state = make_write_ready_state(
        outline=RESULTS_OUTLINE,
        current_chapter_index=0,
    )
    result = generate_chapter(state)
    content = result["body_chapters"][0]["content"]
    row = state["estimate"]["treatment_row"]
    assert row in content
    assert "年龄与收入呈正相关。" in content


def test_invented_treatment_row_is_invented_number(mock_llm_for):
    """mock LLM 另造处理行后，check_grounding 报 invented_number。

    同文的 N / 常数项不得单独构成失败原因。
    """
    from agent.nodes.review_sources.grounding import check_grounding

    prose = (
        "解读如下。\n\n"
        "| treat | 0.9999 |\n"
        "| N | 1200 |\n"
        "| 常数项 | 1.2300 |"
    )
    mock_llm_for("generate_chapter", return_value=prose)
    state = make_write_ready_state(
        outline=RESULTS_OUTLINE,
        current_chapter_index=0,
    )
    result = generate_chapter(state)
    content = result["body_chapters"][0]["content"]
    codes = check_grounding(state, content)
    assert "invented_number" in codes


def test_n_and_intercept_do_not_fail_grounding_alone():
    """真 treatment_row + N + 常数项：不得报 invented_number / missing_estimate_number。"""
    from agent.nodes.review_sources.grounding import check_grounding

    state = make_write_ready_state(outline=RESULTS_OUTLINE)
    row = state["estimate"]["treatment_row"]
    content = (
        f"解读。\n\n{row}\n"
        "| N | 1200 |\n"
        "| 常数项 | 1.2300 |"
    )
    codes = check_grounding(state, content)
    assert "invented_number" not in codes
    assert "missing_estimate_number" not in codes
