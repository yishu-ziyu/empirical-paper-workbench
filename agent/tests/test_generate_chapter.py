"""T-07 / T-08a RED tests for generate_chapter node.

契约：
1. generate_chapter(state) 读 state['current_chapter_index'] + state['outline']
2. 从 outline[idx] 取章节 type，加载模板
3. render(state) 用 state 字段填充模板占位符
4. 调 call_llm(system, user)（注意是 system+user 两参数，不是单 prompt）
5. 写回 state['body_chapters'][idx]，新章节含 {**chapter_spec, content, status: "generated"}
6. call_llm 是模块级函数，测试 monkeypatch 它
7. intro 端到端：mock LLM 返回含"研究背景"的内容，断言 body_chapters[0].content 含"研究背景"
"""
from __future__ import annotations

import pytest

from agent.nodes.generate_chapter import generate_chapter

from conftest import make_state, make_write_ready_state


@pytest.fixture
def recorder(mock_llm_for):
    """generate_chapter LLM recorder（基于根 conftest mock_llm_for 工厂）。"""
    return mock_llm_for("generate_chapter", return_value="MOCK CHAPTER CONTENT")


# ---------------------------------------------------------------------------
# 基本契约
# ---------------------------------------------------------------------------
def test_generate_chapter_writes_to_body_chapters(recorder, six_chapter_outline):
    """generate_chapter 把生成的章节写到 state['body_chapters'][idx]。"""
    state = make_write_ready_state(
        current_chapter_index=0,
        outline=six_chapter_outline,
        research_question="教育对收入的影响",
        data_summary="5 行 3 列",
    )
    result = generate_chapter(state)

    assert "body_chapters" in result
    out = result["body_chapters"][0]
    assert out["type"] == "intro"
    assert out["title"] == "引言"
    assert out["content"] == "MOCK CHAPTER CONTENT"
    assert out["status"] == "generated"


def test_generate_chapter_preserves_other_body_chapters(
    recorder, six_chapter_outline
):
    """generate_chapter 写 body_chapters[idx] 时，其他位置的已有章节保留。"""
    existing = {
        "type": "intro",
        "title": "引言",
        "content": "OLD INTRO",
        "status": "approved",
        "versions": ["OLD INTRO"],
        "chapter_index": 0,
    }
    state = make_write_ready_state(
        current_chapter_index=1,  # 写第 1 章
        outline=six_chapter_outline,
        body_chapters=[existing],
        research_question="Q",
        key_references="REF",
    )
    result = generate_chapter(state)
    # chapter 0 保留
    assert result["body_chapters"][0]["content"] == "OLD INTRO"
    assert result["body_chapters"][0]["status"] == "approved"
    # chapter 1 新生成
    assert result["body_chapters"][1]["type"] == "lit_review"
    assert result["body_chapters"][1]["status"] == "generated"


def test_generate_chapter_calls_llm_with_system_and_user(
    recorder, six_chapter_outline
):
    """generate_chapter 必须调 call_llm(system, user) 两参数（不是单 prompt）。"""
    state = make_write_ready_state(
        current_chapter_index=0,
        outline=six_chapter_outline,
        research_question="RQ",
        data_summary="DS",
    )
    generate_chapter(state)
    assert len(recorder.calls) == 1, "generate_chapter did not call LLM"
    system, user = recorder.calls[0]["args"]
    assert isinstance(system, str) and len(system) > 0
    assert isinstance(user, str) and len(user) > 0
    # user prompt 必须含被替换的研究问题
    assert "RQ" in user
    assert "DS" in user


def test_generate_chapter_no_index_returns_empty(recorder):
    """无 current_chapter_index 时返回空 dict（no-op）。"""
    state = make_state(
        research_question="q",
        data_summary="d",
    )
    result = generate_chapter(state)
    assert result == {}


def test_generate_chapter_unknown_type_raises(recorder):
    """未知 chapter_type 抛错（不要 silent fallback 成 intro，掩盖 bug）。"""
    outline = [{"type": "unknown_xyz", "title": "x"}]
    state = make_write_ready_state(
        current_chapter_index=0,
        outline=outline,
    )
    with pytest.raises(ValueError):
        generate_chapter(state)


def test_data_desc_appends_describe_table_from_csv(recorder, tmp_path):
    """Hollow LLM prose still gets a real describe table from the session CSV."""
    csv_path = tmp_path / "castle.csv"
    csv_path.write_text(
        "l_homicide,post,sid,year\n"
        "1.2,0,1,1980\n"
        "1.4,0,1,1981\n"
        "2.1,1,2,1980\n"
        "2.4,1,2,1981\n",
        encoding="utf-8",
    )
    state = make_write_ready_state(
        current_chapter_index=2,
        csv_path=str(csv_path),
        data_summary="",
        eda_results="",
    )
    result = generate_chapter(state)
    content = result["body_chapters"][2]["content"]
    assert "l_homicide" in content
    assert "post" in content
    assert "表 1" in content
    _, user = recorder.calls[0]["args"]
    assert "l_homicide" in user
    assert "4 行" in user
    assert "表 1" in user


def test_data_desc_csv_eda_overrides_hollow_placeholders(recorder, tmp_path):
    """Uploaded CSV, not a leftover CHARLS/HTTP stub, fills the data_desc prompt."""
    csv_path = tmp_path / "castle.csv"
    csv_path.write_text(
        "l_homicide,post,sid,year\n"
        "1.2,0,1,1980\n"
        "1.4,0,1,1981\n"
        "2.1,1,2,1980\n"
        "2.4,1,2,1981\n",
        encoding="utf-8",
    )
    state = make_write_ready_state(
        current_chapter_index=2,
        csv_path=str(csv_path),
        data_summary="CHARLS 5 列 1000 行",
        eda_results="hollow",
    )
    generate_chapter(state)
    _, user = recorder.calls[0]["args"]
    assert "CHARLS" not in user
    assert "hollow" not in user
    assert "l_homicide" in user
    assert "4 行" in user


# ---------------------------------------------------------------------------
# 6 种 chapter_type 都能跑通
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "chapter_type, required_fields",
    [
        ("intro", {"research_question": "Q", "data_summary": "D"}),
        ("lit_review", {"research_question": "Q", "key_references": "REF"}),
        ("data_desc", {"data_summary": "D", "eda_results": "EDA"}),
        ("methods", {"method": "OLS", "research_question": "Q"}),
        ("results", {"results": "R", "method": "OLS"}),
        ("conclusion", {"results": "R", "research_question": "Q"}),
    ],
)
def test_generate_chapter_all_six_types(
    recorder, chapter_type, required_fields
):
    """6 种 chapter_type 都能加载模板 + render + 调 LLM + 写回 body_chapters。"""
    outline = [{"type": chapter_type, "title": chapter_type}]
    state = make_write_ready_state(
        current_chapter_index=0,
        outline=outline,
        **required_fields,
    )
    result = generate_chapter(state)
    out = result["body_chapters"][0]
    assert out["type"] == chapter_type
    assert out["status"] == "generated"
    expected = "MOCK CHAPTER CONTENT"
    if chapter_type == "results":
        table = (state.get("results") or "").strip()
        if table:
            expected = expected + "\n\n" + table
    assert out["content"] == expected
    assert out["versions"][0] == out["content"]
    # 检查 LLM 被调用且 user prompt 含所有占位符的值
    assert len(recorder.calls) == 1
    _, user = recorder.calls[0]["args"]
    for v in required_fields.values():
        assert v in user, f"{chapter_type}: user prompt missing value {v!r}"


# ---------------------------------------------------------------------------
# intro 端到端：mock LLM 返回含"研究背景"的内容，验证写回 body_chapters
# ---------------------------------------------------------------------------
def test_intro_end_to_end_contains_required_section(
    recorder, six_chapter_outline
):
    """intro 端到端：mock LLM 返回含"研究背景"的内容，body_chapters[0].content 含"研究背景"。

    这是 T-07 验收的"intro 端到端跑通"在 agent 层的等价测试。
    前端 ChapterWriter.test.tsx 测 UI 渲染；这里测 agent 节点 → LLM → 写回链路。
    """
    recorder.return_value = (
        "# 引言\n\n## 研究背景\n教育回报是劳动经济学的经典议题...\n\n"
        "## 研究问题\n本文研究教育对收入的影响。\n\n"
        "## 论文结构\n..."
    )
    state = make_write_ready_state(
        current_chapter_index=0,
        outline=six_chapter_outline,
        research_question="教育对收入的影响",
        data_summary="CHARLS 2018，5 列 1000 行",
    )
    result = generate_chapter(state)
    content = result["body_chapters"][0]["content"]
    assert "研究背景" in content
    assert "研究问题" in content
    assert "论文结构" in content


def test_intro_generated_contribution_section_is_stripped(recorder, six_chapter_outline):
    recorder.return_value = (
        "## 研究背景\n背景。\n\n"
        "## 研究问题\n年龄和收入是否相关。\n\n"
        "## 贡献\n本文有三点边际贡献。\n\n"
        "## 论文结构\n后文给出估计。"
    )
    state = make_write_ready_state(
        current_chapter_index=0,
        outline=six_chapter_outline,
        research_question="年龄与收入",
        data_summary="24 行课设样例",
    )
    result = generate_chapter(state)
    content = result["body_chapters"][0]["content"]
    assert "研究背景" in content
    assert "边际贡献" not in content
    assert "## 贡献" not in content


def test_results_chapter_blocked_without_estimate(recorder):
    state = make_state(
        current_chapter_index=0,
        outline=[{"type": "results", "title": "结果"}],
        identification_diag={"report": "ok"},
    )
    result = generate_chapter(state)
    assert result.get("write_blocked") is True
    assert "no_results" in result.get("write_blockers", [])
    assert "body_chapters" not in result


def test_intro_blocked_without_identification(recorder):
    state = make_state(
        current_chapter_index=0,
        outline=[{"type": "intro", "title": "引言"}],
    )
    result = generate_chapter(state)
    assert result.get("write_blocked") is True
    assert "no_identification" in result.get("write_blockers", [])


def test_intro_writes_with_only_identification(recorder):
    state = make_state(
        current_chapter_index=0,
        outline=[{"type": "intro", "title": "引言"}],
        identification_diag={"report": "ok"},
        research_question="Q",
        data_summary="D",
    )
    result = generate_chapter(state)
    assert result.get("write_blocked") is not True
    assert result["body_chapters"][0]["type"] == "intro"


def test_bind_fills_empty_research_question(recorder):
    """同名空键由 bind_chapter_kwargs 用研究方向补上。"""
    state = make_write_ready_state(
        current_chapter_index=0,
        outline=[{"type": "intro", "title": "引言"}],
        research_question="",
        data_summary="D",
    )
    generate_chapter(state)
    _, user = recorder.calls[0]["args"]
    assert "年龄与收入" in user


def test_bind_formats_key_references_from_literature_entries(recorder):
    """key_references 真值来自 literature_entries，不来自空 HTTP 键。"""
    state = make_write_ready_state(
        current_chapter_index=0,
        outline=[{"type": "lit_review", "title": "文献综述"}],
    )
    generate_chapter(state)
    _, user = recorder.calls[0]["args"]
    assert "T" in user
    assert "2020" in user


def test_methods_bind_uses_association_system(recorder):
    """OLS / association 的方法章 system 不含「解决内生性」。"""
    state = make_write_ready_state(
        current_chapter_index=0,
        outline=[{"type": "methods", "title": "方法", "method": "ols"}],
    )
    generate_chapter(state)
    system, user = recorder.calls[0]["args"]
    assert "解决内生性" not in system
    assert "ols" in user.lower()


def test_results_appends_tool_table_when_estimate_ok(recorder):
    """结果章 content / versions[0] = 解读 + 当前主表。"""
    state = make_write_ready_state(
        current_chapter_index=0,
        outline=[{"type": "results", "title": "结果"}],
    )
    result = generate_chapter(state)
    ch = result["body_chapters"][0]
    table = (state.get("results") or "").strip()
    assert ch["content"] == "MOCK CHAPTER CONTENT\n\n" + table
    assert ch["versions"][0] == ch["content"]
    assert "| age |" in ch["content"]
    assert state["estimate"]["treatment_row"] in ch["content"]


def test_results_appends_degraded_fe_dropped_line(recorder):
    """Degraded pooled-OLS fallback still splices the table, including the FE line."""
    ready = make_write_ready_state()
    estimate = dict(ready["estimate"])
    estimate["status"] = "degraded"
    estimate["estimator"] = "statsmodels.ols"
    table = "# 主结果\n\nFE dropped; pooled OLS\n\n| treat | 0.1 | 0.1 | 0.1 |"
    state = make_write_ready_state(
        current_chapter_index=0,
        outline=[{"type": "results", "title": "结果"}],
        estimate=estimate,
        results=table,
    )
    result = generate_chapter(state)
    content = result["body_chapters"][0]["content"]
    assert "FE dropped; pooled OLS" in content
    assert "| treat |" in content


def test_results_skips_splice_when_estimate_not_ok(recorder):
    """estimate.status 不是 ok：只写 prose，不拼表。"""
    ready = make_write_ready_state()
    estimate = dict(ready["estimate"])
    estimate["status"] = "error"
    state = make_write_ready_state(
        current_chapter_index=0,
        outline=[{"type": "results", "title": "结果"}],
        estimate=estimate,
    )
    result = generate_chapter(state)
    ch = result["body_chapters"][0]
    assert ch["content"] == "MOCK CHAPTER CONTENT"
    assert ch["versions"][0] == "MOCK CHAPTER CONTENT"
    assert "| age |" not in ch["content"]
