"""批次 4：结果章数字接地纯函数。"""
from __future__ import annotations

from agent.nodes.review_sources.grounding import check_grounding

from conftest import make_write_ready_state

TREATMENT_ROW = "| age | 0.1234 | 0.0456 | 0.0078 |"


def _content_with_true_table(*extra_rows: str) -> str:
    state = make_write_ready_state()
    extras = "".join(f"\n{row}" for row in extra_rows)
    return "主估计解读。\n\n" + state["results"] + extras


def test_true_table_passes():
    """真表 + N / 常数项 → 过关。"""
    state = make_write_ready_state()
    content = _content_with_true_table("| N | 1200 |", "| 常数项 | 1.2300 |")
    assert TREATMENT_ROW in content
    assert check_grounding(state, content) == []


def test_missing_treatment_row_fails():
    """treatment_row 不是 content 子串 → missing_estimate_number。"""
    state = make_write_ready_state()
    content = (
        "解读。\n\n| 变量 | 系数 | SE | p |\n"
        "|------|------|----|---|\n| N | 1200 |"
    )
    assert TREATMENT_ROW not in content
    failures = check_grounding(state, content)
    assert "missing_estimate_number" in failures


def test_invented_age_row_fails():
    """另造 | age | 0.9999 | → invented_number。"""
    state = make_write_ready_state()
    content = _content_with_true_table(
        "| age | 0.9999 | 0.01 | 0.00 |",
        "| N | 1200 |",
        "| 常数项 | 1.2300 |",
    )
    failures = check_grounding(state, content)
    assert "invented_number" in failures
    assert "missing_estimate_number" not in failures


def test_invented_treat_alias_fails():
    """treat 视为处理变量别名，0.9999 与 coef 不同 → invented_number。"""
    state = make_write_ready_state()
    content = _content_with_true_table(
        "| treat | 0.9999 |",
        "| N | 1200 |",
        "| 常数项 | 1.2300 |",
    )
    assert "invented_number" in check_grounding(state, content)


def test_n_and_intercept_not_overflagged():
    """N / 观测 / 常数项 / intercept / _cons 不得因此失败。"""
    state = make_write_ready_state()
    content = _content_with_true_table(
        "| N | 1200 |",
        "| 观测 | 1200 |",
        "| 常数项 | 1.2300 |",
        "| intercept | 1.2300 |",
        "| _cons | 1.2300 |",
        "| city | 0.5500 | 0.01 | 0.00 |",
    )
    assert check_grounding(state, content) == []


def test_no_treatment_row_returns_empty():
    """没有 treatment_row 时返回 []，不对引言乱报。"""
    ready = make_write_ready_state()
    estimate = dict(ready["estimate"])
    estimate.pop("treatment_row", None)
    state = make_write_ready_state(estimate=estimate)
    assert check_grounding(state, "引言没有主表。") == []


def test_does_not_parse_identification_report():
    """不解析 identification_diag.report 里的小数。"""
    state = make_write_ready_state(
        identification_diag={
            "strategy": None,
            "diagnostics": [],
            "passed": True,
            "report": "识别报告里有 | treat | 0.9999 | 和 0.456，不得当正文。",
            "star_rating": None,
        }
    )
    content = _content_with_true_table("| N | 1200 |", "| 常数项 | 1.2300 |")
    assert check_grounding(state, content) == []


def test_matching_coef_is_not_invented():
    """处理行第一个 float 与 coef 差不超过 1e-4 不算另造。"""
    state = make_write_ready_state()
    content = _content_with_true_table("| age | 0.1234 |")
    assert check_grounding(state, content) == []


def test_second_full_header_is_invented_table():
    """第二张完整表头（工具表之外）→ invented_table。"""
    state = make_write_ready_state()
    content = (
        _content_with_true_table("| N | 1200 |")
        + "\n\n| 变量 | 系数 | SE | p |\n"
        "|------|------|----|---|\n| treat | 0.9999 |\n"
    )
    failures = check_grounding(state, content)
    assert "invented_table" in failures
    assert "invented_number" in failures
