from agent.desk.heuristic import heuristic_discuss
from agent.desk.socratic import discuss


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
    monkeypatch.setattr("agent.desk.socratic.call_llm", lambda *args, **kwargs: "not-json")
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
    monkeypatch.setattr("agent.desk.socratic.call_llm", lambda *args, **kwargs: __import__("json").dumps(payload))
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
        "agent.desk.socratic.call_llm",
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
        "agent.desk.socratic.call_llm",
        lambda *args, **kwargs: __import__("json").dumps(payload),
    )

    result = discuss("我想研究数字经济发展是否提高了制造业企业的生产率")

    assert result["source"] == "llm"
    assert result["title"] == "我想研究数字经济发展是否提高了制造业企业的生产率"


def test_discuss_turns_uncertainty_into_a_recommendation_instead_of_repeating(monkeypatch):
    previous_question = "你打算用什么数据来源？"
    payload = {
        "intent": "research",
        "reflection": "学生表示不清楚，需要系统给一个方向。",
        "title": "教育的作用会不会隔代才显著",
        "question": previous_question,
        "options": [
            {"id": "cfps", "label": "CFPS"},
            {"id": "cgss", "label": "CGSS"},
        ],
        "explain": "我建议先看 CFPS，因为它更接近家庭与代际追踪场景。",
        "ready": False,
    }
    monkeypatch.setattr(
        "agent.desk.socratic.call_llm",
        lambda *args, **kwargs: __import__("json").dumps(payload),
    )

    result = discuss(
        "教育的作用会不会隔代才显著",
        [
            {
                "id": "freeform",
                "question": previous_question,
                "answer": "我不太清楚，你觉得用哪些数据会更合适？",
            }
        ],
    )

    assert "建议" in result["explain"]
    assert result["reflection"] == "我来替你判断，先给你一个可以直接采用的方案。"
    assert result["question"] != previous_question
    assert result["question"] == "先按我的建议继续，可以吗？"
    assert result["options"][0]["id"] == "accept_recommendation"


def test_discuss_owns_dataset_field_checks_instead_of_quizzing_the_student(monkeypatch):
    payload = {
        "intent": "research",
        "reflection": "CGSS 是一个候选数据源。",
        "title": "教育的作用会不会隔代才显著",
        "question": "CGSS里能拿到祖辈教育年限吗？",
        "options": [
            {"id": "yes", "label": "能直接拿到"},
            {"id": "parent", "label": "只有父亲一代"},
            {"id": "other", "label": "需要另寻数据"},
        ],
        "explain": "",
        "ready": False,
    }
    monkeypatch.setattr(
        "agent.desk.socratic.call_llm",
        lambda *args, **kwargs: __import__("json").dumps(payload),
    )

    result = discuss(
        "教育的作用会不会隔代才显著",
        [
            {
                "id": "freeform",
                "question": "你打算用什么数据来源？",
                "answer": "CGSS等专项调查",
            }
        ],
    )

    assert result["question"] == "你手上已经有数据文件吗？"
    assert result["options"] == [
        {"id": "data_in_hand", "label": "已有数据"},
        {"id": "data_accessible", "label": "可以申请"},
        {"id": "data_no_access", "label": "还没有"},
    ]
    assert "由我来核验" in result["explain"]
