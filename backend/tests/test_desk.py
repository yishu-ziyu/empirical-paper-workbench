def test_desk_discuss_returns_one_question(client):
    resp = client.post(
        "/desk/discuss",
        json={"notes": "导师让我用 CHARLS 做点养老的", "turns": []},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"]
    assert data["ready"] is False
    assert data["question"]
    assert len(data["options"]) <= 3


def test_desk_discuss_preserves_explicit_research_variables(client):
    resp = client.post(
        "/desk/discuss",
        json={
            "notes": "我想研究数字经济发展是否提高了制造业企业的生产率",
            "turns": [],
        },
    )

    assert resp.status_code == 200
    title = resp.json()["title"]
    assert title == "我想研究数字经济发展是否提高了制造业企业的生产率"


def test_desk_discuss_greeting_returns_conversation_guidance(client):
    resp = client.post(
        "/desk/discuss",
        json={"notes": "ni'hao", "turns": []},
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["intent"] == "conversation"
    assert data["title"] == ""
    assert data["question"] == ""
    assert data["options"] == []
    assert "研究" in data["reflection"]


def test_desk_transcribe_rejects_empty(client):
    resp = client.post(
        "/desk/transcribe",
        files={"file": ("clip.webm", b"", "audio/webm")},
    )
    assert resp.status_code == 400


def test_desk_speak_rejects_empty(client):
    resp = client.post("/desk/speak", json={"text": "   "})
    assert resp.status_code == 400


def test_desk_discuss_can_become_ready(client):
    resp = client.post(
        "/desk/discuss",
        json={
            "notes": "导师让我用 CHARLS 做点养老的",
            "turns": [
                {"id": "policy", "question": "比较什么", "answer": "政策有没有效果"},
                {"id": "work", "question": "结果看什么", "answer": "工作和退休"},
            ],
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["ready"] is True
    assert data["question"] == ""
