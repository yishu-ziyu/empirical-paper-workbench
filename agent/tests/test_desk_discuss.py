from desk.heuristic import heuristic_discuss
from desk.socratic import discuss


def test_heuristic_asks_one_thing():
    first = heuristic_discuss("导师让我用 CHARLS 做点养老的")
    assert first["source"] == "heuristic"
    assert first["ready"] is False
    assert first["question"]
    assert len(first["options"]) <= 3


def test_heuristic_two_turns_ready():
    later = heuristic_discuss(
        "导师让我用 CHARLS 做点养老的",
        [
            {"id": "policy", "answer": "政策有没有效果"},
            {"id": "work", "answer": "工作和退休"},
        ],
    )
    assert later["ready"] is True
    assert later["question"] == ""
    assert later["title"]


def test_discuss_falls_back_when_llm_is_mock():
    result = discuss("导师让我用 CHARLS 做点养老的")
    assert result["source"] == "heuristic"
    assert "CHARLS" in " ".join(result["heard"]) or "养老" in result["title"]


def test_discuss_ask_requires_model_explain(monkeypatch):
    monkeypatch.setattr("desk.socratic.call_llm", lambda *args, **kwargs: "not-json")
    try:
        discuss(
            "导师让我用 CHARLS 做点养老的",
            [{"id": "ask", "question": "总消费差距还是分类？", "answer": "总消费是什么意思？"}],
        )
    except RuntimeError as exc:
        assert "explain" in str(exc)
    else:
        raise AssertionError("ask must not fall back to heuristic")


def test_discuss_uses_llm_json(monkeypatch):
    payload = {
        "reflection": "我听到了 CHARLS 和养老。",
        "title": "养老金并轨之后，临近退休的人是不是更早离开劳动力市场？",
        "heard": ["CHARLS", "养老"],
        "comparison": "还没定",
        "outcome": "还没定",
        "question": "你更想弄清政策有没有效果，还是谁受到了影响？",
        "options": [
            {"id": "policy", "label": "政策有没有效果"},
            {"id": "who", "label": "谁受到了影响"},
        ],
        "ready": False,
    }
    monkeypatch.setattr("desk.socratic.call_llm", lambda *args, **kwargs: __import__("json").dumps(payload))
    result = discuss("导师让我用 CHARLS 做点养老的")
    assert result["source"] == "llm"
    assert result["question"]
    assert result["ready"] is False
    assert len(result["options"]) == 2
