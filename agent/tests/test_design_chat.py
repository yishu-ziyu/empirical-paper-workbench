"""设计对话：启发式回退路径的确定性测试（不真调 LLM）。"""
from desk.design_chat import design_chat, heuristic_design_chat


def test_heuristic_extracts_columns_from_notes():
    notes = "我想研究最低工资对收入的影响，用加州的数据"
    out = heuristic_design_chat(notes, [], ["wage", "state", "year"])
    assert out["source"] == "heuristic"
    assert out["design"]["method"] in ("DiD", "OLS")
    assert out["need"]


def test_design_chat_mock_provider_falls_back(monkeypatch):
    """mock 通道（无 LLM）时 design_chat 走启发式，不抛异常。"""
    import llm.call_llm as call_llm_mod

    def fake_llm(*a, **kw):
        raise RuntimeError("mock provider 没有真模型")

    monkeypatch.setattr(call_llm_mod, "call_llm", fake_llm)
    out = design_chat("数字经济对工资的影响", [{"role": "user", "text": "对，就是工资"}], ["wage", "digital"])
    assert out["source"] == "heuristic"
    assert "reply" in out and "design" in out


def test_filter_keeps_only_real_columns():
    notes = "cigsale 受 retprice 影响，合成控制"
    out = heuristic_design_chat(notes, [], ["cigsale", "retprice", "state", "year"])
    d = out["design"]
    assert d["method"] == "SCM"
    assert d["dv"] == "cigsale"
