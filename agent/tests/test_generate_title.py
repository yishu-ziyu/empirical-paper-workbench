"""T-02: generate_title 节点契约测试。

从 backend/tests/test_graph.py 抽取而来（ADR-0003 Stage C 命名约定：
generate_title 是 agent 节点，测试归 agent/tests/）。

契约：
- generate_title 调用 LLM 生成标题
- 把 \\title{...} 写入 state.title_chapter
- title_chapter.type == "title"
"""
from nodes.generate_title import generate_title

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
