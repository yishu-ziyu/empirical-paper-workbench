"""T-02: generate_title 节点契约测试。

从 backend/tests/test_graph.py 抽取而来（ADR-0003 Stage C 命名约定：
generate_title 是 agent 节点，测试归 agent/tests/）。

契约：
- generate_title 调用 LLM 生成标题
- 把 \\title{...} 写入 state.title_chapter
- title_chapter.type == "title"
"""
from agent.nodes.generate_title import generate_title

from conftest import make_state


def test_generate_title_calls_llm_and_writes_title_chapter(mock_llm_for):
    """generate_title calls the LLM and writes \\title{...} into title_chapter."""
    recorder = mock_llm_for("generate_title", return_value="Test Title")
    state = make_state(uploaded_datasets=[])
    result = generate_title(state)
    title_chapter = result.get("title_chapter")
    assert title_chapter is not None, "generate_title wrote no title_chapter"
    assert title_chapter.get("type") == "title", (
        f"expected type=title, got {title_chapter.get('type')!r}"
    )
    assert title_chapter["generation_source"] == "mock"
    assert title_chapter["generation_degraded"] is True
    assert title_chapter.get("content") == "\\title{Test Title}", (
        f"expected '\\title{{Test Title}}', "
        f"got {title_chapter.get('content')!r}"
    )
    assert len(recorder.calls) > 0, "generate_title did not call the LLM"


def test_generate_title_uses_data_summary_in_prompt(mock_llm_for):
    """generate_title 把数据集摘要编进 prompt。"""
    recorder = mock_llm_for("generate_title", return_value="Title")
    state = make_state(
        uploaded_datasets=[
            {"path": "/tmp/x.csv", "format": "csv", "columns": ["a", "b"]}
        ]
    )
    generate_title(state)
    assert len(recorder.calls) == 1
    prompt = recorder.calls[0]["args"][0]
    assert "数据集" in prompt


def test_generate_title_includes_research_question(mock_llm_for):
    recorder = mock_llm_for("generate_title", return_value="教育回报")
    generate_title(
        make_state(
            research_direction={"question": "教育对收入的影响", "method": "DiD"}
        )
    )
    prompt = recorder.calls[0]["args"][0]
    assert "教育对收入的影响" in prompt
    assert "DiD" in prompt


def test_generate_title_strips_latex_wrapper(mock_llm_for):
    mock_llm_for("generate_title", return_value="\\title{干净标题}\n多余一行")
    result = generate_title(make_state())
    assert result["title_chapter"]["title"] == "干净标题"
    assert result["title_chapter"]["content"] == "\\title{干净标题}"


def test_generate_title_without_estimate_does_not_name_findings(mock_llm_for):
    """无估计时标题只写方向，不要点名未跑过的发现。"""
    recorder = mock_llm_for("generate_title", return_value="年龄与收入")
    generate_title(
        make_state(research_direction={"question": "年龄与收入", "method": "OLS"})
    )
    prompt = recorder.calls[0]["args"][0]
    assert "不要点名" in prompt
    assert "发现" in prompt


def test_generate_title_with_estimate_allows_direction(mock_llm_for):
    """估计已跑时标题可读估计方向，仍不编造未出现的发现。"""
    from conftest import make_write_ready_state

    recorder = mock_llm_for("generate_title", return_value="年龄与收入")
    generate_title(make_write_ready_state())
    prompt = recorder.calls[0]["args"][0]
    assert "估计" in prompt
    assert "方向" in prompt


def test_title_call_llm_delegates_to_unified(monkeypatch):
    seen = {}

    def fake_unified(prompt, node_type="default", system=None):
        seen["node_type"] = node_type
        seen["prompt"] = prompt
        return "Live Title"

    monkeypatch.setattr("agent.llm.call_llm.call_llm", fake_unified)
    from agent.nodes.generate_title import call_llm

    assert call_llm("p") == "Live Title"
    assert seen["node_type"] == "title"
    assert seen["prompt"] == "p"
