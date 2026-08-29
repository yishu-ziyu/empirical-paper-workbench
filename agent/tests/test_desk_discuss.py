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
    assert later["title"] == "导师让我用 CHARLS 做点养老的"


def test_heuristic_preserves_explicit_digital_economy_question():
    result = heuristic_discuss("我想研究数字经济发展是否提高了制造业企业的生产率")

    assert result["title"] == "我想研究数字经济发展是否提高了制造业企业的生产率"
    assert "用工" not in result["title"]
    assert "工资" not in result["title"]


def test_heuristic_preserves_unseen_research_domain_without_a_template():
    notes = "我想研究绿色金融是否降低了高耗能企业的碳排放"

    result = heuristic_discuss(notes)

    assert result["title"] == notes


def test_heuristic_greeting_stays_in_conversation_instead_of_becoming_a_paper():
    result = heuristic_discuss("ni'hao")

    assert result["intent"] == "conversation"
    assert result["title"] == ""
    assert result["question"] == ""
    assert result["options"] == []
    assert "研究" in result["reflection"]


def test_heuristic_intent_boundary_is_generic_not_domain_specific():
    for greeting in ["你好", "hello", "test"]:
        assert heuristic_discuss(greeting)["intent"] == "conversation"

    for research_note in [
        "导师让我用 CHARLS 做点养老的",
        "感觉数字经济能发，但不知道问什么",
        "我想研究绿色金融是否降低了高耗能企业的碳排放",
    ]:
        assert heuristic_discuss(research_note)["intent"] == "research"


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


def test_discuss_honors_llm_conversation_intent(monkeypatch):
    payload = {
        "intent": "conversation",
        "reflection": "你好！你可以随便说一句最近想研究的现象或问题。",
        "title": "不应出现的论文题目",
        "question": "不应追问比较什么",
        "options": [{"id": "policy", "label": "政策有没有效果"}],
        "ready": False,
    }
    monkeypatch.setattr(
        "desk.socratic.call_llm",
        lambda *args, **kwargs: __import__("json").dumps(payload),
    )

    result = discuss("你好")

    assert result["intent"] == "conversation"
    assert result["reflection"].startswith("你好")
    assert result["title"] == ""
    assert result["question"] == ""
    assert result["options"] == []


def test_discuss_rejects_llm_title_that_replaces_explicit_outcome(monkeypatch):
    payload = {
        "title": "数字经济发展之后，企业的用工和工资发生了什么变化？",
        "question": "你现在更想弄清哪一件事？",
        "options": [{"id": "policy", "label": "政策有没有效果"}],
        "ready": False,
    }
    monkeypatch.setattr(
        "desk.socratic.call_llm",
        lambda *args, **kwargs: __import__("json").dumps(payload),
    )

    result = discuss("我想研究数字经济发展是否提高了制造业企业的生产率")

    assert result["source"] == "llm"
    assert result["title"] == "我想研究数字经济发展是否提高了制造业企业的生产率"
