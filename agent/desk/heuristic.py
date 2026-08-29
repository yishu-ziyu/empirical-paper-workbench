"""LLM 不可用时的本地降级：仍一次只问一件事。"""
from __future__ import annotations

from typing import Any

from desk.shape_question import next_prompt, shape_question


def _answers_from_turns(turns: list[dict[str, str]]) -> dict[str, str]:
    answers: dict[str, str] = {}
    for item in turns:
        option_id = str(item.get("id") or "")
        if option_id in {"policy", "who", "gap"}:
            answers["compare"] = option_id
        elif option_id in {"work", "wage", "health"}:
            answers["outcome"] = option_id
    return answers


def heuristic_discuss(notes: str, turns: list[dict[str, str]] | None = None) -> dict[str, Any]:
    turns = turns or []
    draft = shape_question(notes, _answers_from_turns(turns))
    prompt = next_prompt(_answers_from_turns(turns))
    return {
        "intent": draft["intent"],
        "reflection": draft["reflection"],
        "title": draft["title"],
        "heard": [item["label"] for item in draft["heard"]],
        "comparison": draft["comparison"],
        "outcome": draft["outcome"],
        "question": (
            ""
            if draft["intent"] == "conversation" or draft["ready"] or not prompt
            else prompt["question"]
        ),
        "options": (
            []
            if draft["intent"] == "conversation" or draft["ready"] or not prompt
            else prompt["options"]
        ),
        "explain": "",
        "ready": draft["ready"],
        "source": "heuristic",
    }
