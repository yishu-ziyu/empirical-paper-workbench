"""T-07 RED tests for 6 chapter prompt templates.

每个模板必须：
1. 暴露 SYSTEM_PROMPT / USER_TEMPLATE / render() 三个符号
2. SYSTEM_PROMPT 非空字符串
3. USER_TEMPLATE 含任务规格里指定的占位符
4. render(**kwargs) 返回 (system, user) tuple，且占位符被替换为传入值
5. get_prompt(chapter_type) 返回对应模块
"""
from __future__ import annotations

import pytest

from agent.prompts import get_prompt


# ---------------------------------------------------------------------------
# 每个模板的占位符契约（任务规格里指定）
# ---------------------------------------------------------------------------
_REVISION = ["low_dims", "revision_suggestions"]

TEMPLATE_CONTRACTS = {
    "intro": ["research_question", "data_summary", *_REVISION],
    # ADR-0009 Stage 3: lit_review 新增 citation_indices 占位符（[1][2] 引用标记）
    "lit_review": ["research_question", "key_references", "citation_indices", *_REVISION],
    "data_desc": ["data_summary", "eda_results", *_REVISION],
    "methods": ["method", "research_question", *_REVISION],
    "results": ["results", "robustness_table", "method", *_REVISION],
    "conclusion": ["results", "research_question", *_REVISION],
}


# ---------------------------------------------------------------------------
# get_prompt 路由
# ---------------------------------------------------------------------------
def test_get_prompt_returns_module_for_all_six_types():
    """get_prompt 对 6 种 chapter_type 都返回带 render() 的对象。"""
    for chapter_type in (
        "intro",
        "lit_review",
        "data_desc",
        "methods",
        "results",
        "conclusion",
    ):
        mod = get_prompt(chapter_type)
        assert mod is not None, f"get_prompt({chapter_type!r}) returned None"
        assert callable(getattr(mod, "render", None)), (
            f"get_prompt({chapter_type!r}).render is not callable"
        )


def test_get_prompt_unknown_type_raises():
    """未知 chapter_type 抛 ValueError（防止 silent fallback 掩盖 bug）。"""
    with pytest.raises(ValueError):
        get_prompt("unknown_type")


# ---------------------------------------------------------------------------
# 每个模板的结构契约
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "chapter_type, placeholders",
    list(TEMPLATE_CONTRACTS.items()),
)
def test_template_has_non_empty_system_prompt(chapter_type, placeholders):
    """每个模板有非空 SYSTEM_PROMPT。"""
    mod = get_prompt(chapter_type)
    assert hasattr(mod, "SYSTEM_PROMPT"), (
        f"{chapter_type} template missing SYSTEM_PROMPT"
    )
    assert isinstance(mod.SYSTEM_PROMPT, str)
    assert len(mod.SYSTEM_PROMPT.strip()) > 0


@pytest.mark.parametrize(
    "chapter_type, placeholders",
    list(TEMPLATE_CONTRACTS.items()),
)
def test_template_user_template_contains_required_placeholders(
    chapter_type, placeholders
):
    """USER_TEMPLATE 必须包含任务规格里指定的全部占位符。"""
    mod = get_prompt(chapter_type)
    assert hasattr(mod, "USER_TEMPLATE"), (
        f"{chapter_type} template missing USER_TEMPLATE"
    )
    template = mod.USER_TEMPLATE
    for ph in placeholders:
        assert "{" + ph + "}" in template, (
            f"{chapter_type} USER_TEMPLATE missing placeholder {{{ph}}}"
        )


@pytest.mark.parametrize(
    "chapter_type, placeholders",
    list(TEMPLATE_CONTRACTS.items()),
)
def test_render_returns_tuple_and_replaces_placeholders(chapter_type, placeholders):
    """render(**kwargs) 返回 (system, user) tuple，占位符被替换。"""
    mod = get_prompt(chapter_type)
    kwargs = {ph: f"<VALUE-{ph}>" for ph in placeholders}
    system, user = mod.render(**kwargs)

    assert isinstance(system, str)
    assert isinstance(user, str)
    assert len(system) > 0
    assert len(user) > 0

    # 替换后的值必须在 user 里出现
    for ph in placeholders:
        assert f"<VALUE-{ph}>" in user, (
            f"{chapter_type} render() did not substitute {{{ph}}}"
        )

    # 不能残留未替换的占位符
    for ph in placeholders:
        assert "{" + ph + "}" not in user, (
            f"{chapter_type} render() left placeholder {{{ph}}} unreplaced"
        )


def test_render_revision_defaults_are_empty_not_none():
    """缺省弱维 / 建议时不把 None 写进 prompt。"""
    mod = get_prompt("methods")
    _, user = mod.render(method="DID", research_question="Q")
    assert "None" not in user
    assert "上一轮弱维：" in user


# ---------------------------------------------------------------------------
# 章节特化 system prompt 内容契约（任务规格 §T-07）
# ---------------------------------------------------------------------------
def test_intro_strip_contribution_drops_heading_block():
    from agent.prompts.intro import strip_contribution

    raw = (
        "## 研究背景\n背景。\n\n"
        "## 贡献\n- 数据新\n- 方法新\n\n"
        "## 论文结构\n后面写结果。"
    )
    out = strip_contribution(raw)
    assert "贡献" not in out
    assert "研究背景" in out
    assert "论文结构" in out


def test_intro_system_prompt_mentions_required_sections():
    """课设引言：背景 + 问题 + 结构，禁止贡献三条。"""
    mod = get_prompt("intro")
    sp = mod.SYSTEM_PROMPT
    assert "研究背景" in sp
    assert "研究问题" in sp
    assert "论文结构" in sp
    assert "课程论文" in sp or "课设" in sp
    assert "禁止" in sp and "贡献" in sp
    _, user = mod.render(research_question="年龄与收入", data_summary="24 行")
    assert "不要写贡献" in user
    assert "边际贡献" not in user


def test_lit_review_system_prompt_mentions_required_sections():
    """lit_review system prompt 引导写"文献回顾+研究空白+本文定位"。"""
    mod = get_prompt("lit_review")
    sp = mod.SYSTEM_PROMPT
    hits = sum(kw in sp for kw in ("文献", "研究空白", "定位", "综述"))
    assert hits >= 3, f"lit_review SYSTEM_PROMPT missing sections: {sp!r}"


def test_data_desc_system_prompt_mentions_required_sections():
    """data_desc system prompt 引导写"数据来源+变量定义+描述统计"。"""
    mod = get_prompt("data_desc")
    sp = mod.SYSTEM_PROMPT
    hits = sum(kw in sp for kw in ("数据来源", "变量定义", "描述统计", "数据描述"))
    assert hits >= 3, f"data_desc SYSTEM_PROMPT missing sections: {sp!r}"


def test_methods_system_prompt_mentions_required_sections():
    """methods 默认 system 引导写模型与解释边界（association）。"""
    mod = get_prompt("methods")
    sp = mod.SYSTEM_PROMPT
    hits = sum(
        kw in sp for kw in ("识别策略", "计量模型", "假设", "方法", "模型设定")
    )
    assert hits >= 3, f"methods SYSTEM_PROMPT missing sections: {sp!r}"
    assert "解决内生性" not in sp


def test_methods_association_render_omits_endogeneity_language():
    """{claim}=association 时渲染出的 system 不含「解决内生性」。"""
    mod = get_prompt("methods")
    system, user = mod.render(
        method="ols", research_question="年龄与收入", claim="association"
    )
    assert "解决内生性" not in system
    assert "相关" in system or "条件关联" in system
    assert "ols" in user


def test_methods_causal_render_keeps_ident_language():
    """causal_with_caveat + DID 才写识别假设。"""
    mod = get_prompt("methods")
    system, user = mod.render(
        method="did", research_question="Q", claim="causal_with_caveat"
    )
    assert "识别策略" in system
    assert "识别假设" in user


def test_results_system_forbids_redrawing_table():
    """结果章 system 只解读文末主表，禁止再画表 / 见表 2。"""
    mod = get_prompt("results")
    sp = mod.SYSTEM_PROMPT
    assert "主表已在文末" in sp
    assert "禁止再画表" in sp
    assert "见表 2" in sp


def test_lit_review_empty_table_must_not_invent_author_year():
    """编号表为空时不得教模型继续编 (Author, Year)。"""
    mod = get_prompt("lit_review")
    sp = mod.SYSTEM_PROMPT
    assert "仍使用 (Author, Year)" not in sp
    assert "编号表为空则仍使用 (Author, Year)" not in sp
    assert "不得编造篇名与年份" in sp


def test_results_system_prompt_mentions_required_sections():
    """results system prompt 引导写"基准回归+稳健性+异质性"。"""
    mod = get_prompt("results")
    sp = mod.SYSTEM_PROMPT
    hits = sum(
        kw in sp for kw in ("基准回归", "稳健性", "异质性", "结果")
    )
    assert hits >= 3, f"results SYSTEM_PROMPT missing sections: {sp!r}"


def test_conclusion_system_prompt_mentions_required_sections():
    """conclusion system prompt 引导写"主要发现+政策含义+局限与未来"。"""
    mod = get_prompt("conclusion")
    sp = mod.SYSTEM_PROMPT
    hits = sum(
        kw in sp
        for kw in ("主要发现", "政策含义", "局限", "未来", "结论")
    )
    assert hits >= 3, f"conclusion SYSTEM_PROMPT missing sections: {sp!r}"
