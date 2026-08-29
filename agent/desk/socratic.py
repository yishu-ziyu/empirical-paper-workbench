"""空桌的苏格拉底讨论：一次只问一件事，产出一张问题卡。"""
from __future__ import annotations

import json
import re
from typing import Any

from .heuristic import heuristic_discuss
from .shape_question import CONVERSATION_REPLY, has_research_intent, user_intent_title
from ..llm.call_llm import call_llm

SYSTEM = """你是实证经济学研究产品里的对话助手。
先判断用户有没有表达研究意图。问候、闲聊、测试文字或还没有研究含义的输入，应自然回应并邀请用户说出研究现象；不要强行生成论文问题。
只有存在研究意图时，才用苏格拉底方式围绕用户原话追问一件事。
不要写论文，不要给大纲，不要解释你在做什么，也不要替用户改写研究问题。
只输出一个 JSON 对象，不要 Markdown。"""


def _prompt(notes: str, turns: list[dict[str, str]]) -> str:
    history = "还没有。"
    if turns:
        history = "\n".join(
            f"- 问：{item.get('question', '')}\n  答：{item.get('answer', '')}"
            for item in turns
        )
    return f"""学生倒出来的念头：
{notes.strip() or '（还没写）'}

已经走过的确认：
{history}

如果最近一条回答是在问某个选项是什么意思，先用一句人话解释那个选项，再继续原来那件待确认的事。解释不超过两句。不要把讨论带去别的方向。

请输出：
{{
  "intent": "research 或 conversation",
  "reflection": "对用户当前输入的自然回应，不超过两句",
  "question": "下一句只问一件缺的事，不超过 20 个字；问题已可估计则为空字符串",
  "options": [{{"id": "a", "label": "短选项"}}],
  "explain": "仅当用户在问选项是什么意思时，用一两句人话解释；否则必须是空字符串",
  "ready": false
}}
要求：intent 为 conversation 时，question 和 options 必须为空、ready 必须为 false；不要改写或补全用户的研究问题；options 最多 3 个，label 不超过 8 个字，不要括号和举例；ready 为 true 时 question 为空、options 为空；用中文。"""


def _extract_json(raw: str) -> dict[str, Any] | None:
    text = raw.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    match = re.search(r"\{.*\}", text, flags=re.S)
    if not match:
        return None
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def _normalize(data: dict[str, Any], notes: str) -> dict[str, Any]:
    intent = str(data.get("intent") or "").strip().lower()
    if intent not in {"research", "conversation"}:
        intent = "research" if has_research_intent(notes) else "conversation"
    if intent == "conversation":
        return {
            "intent": "conversation",
            "reflection": str(data.get("reflection") or "").strip() or CONVERSATION_REPLY,
            "title": "",
            "heard": [],
            "comparison": "还没定",
            "outcome": "还没定",
            "question": "",
            "options": [],
            "explain": "",
            "ready": False,
            "source": "llm",
        }
    options_in = data.get("options") or []
    options: list[dict[str, str]] = []
    for idx, item in enumerate(options_in[:3]):
        if not isinstance(item, dict):
            continue
        label = str(item.get("label") or "").strip()
        if not label:
            continue
        label = re.sub(r"（.*?）|\(.*?\)", "", label).strip() or label
        options.append({"id": str(item.get("id") or f"opt{idx + 1}"), "label": label})
    heard_in = data.get("heard") or []
    heard = [str(x).strip() for x in heard_in if str(x).strip()]
    ready = bool(data.get("ready"))
    question = "" if ready else str(data.get("question") or "").strip()
    if ready:
        options = []
    # The user's wording is the source of truth. Model output may guide the
    # discussion, but it must not silently replace the research intent.
    title = user_intent_title(notes)
    return {
        "intent": "research",
        "reflection": str(data.get("reflection") or "").strip() or "我先听你把念头说完整。",
        "title": title,
        "heard": heard,
        "comparison": str(data.get("comparison") or "还没定").strip() or "还没定",
        "outcome": str(data.get("outcome") or "还没定").strip() or "还没定",
        "question": question,
        "options": options,
        "explain": str(data.get("explain") or "").strip(),
        "ready": ready,
        "source": "llm",
    }


def discuss(notes: str, turns: list[dict[str, str]] | None = None) -> dict[str, Any]:
    """走统一 LLM 通道。解析失败或 mock 时退回本地启发式。"""
    turns = turns or []
    fallback = heuristic_discuss(notes, turns)
    asking = bool(turns and str(turns[-1].get("id") or "") == "ask")
    try:
        raw = call_llm(_prompt(notes, turns), node_type="desk", system=SYSTEM)
    except Exception:
        if asking:
            raise
        return fallback
    parsed = _extract_json(raw)
    if not parsed:
        if asking:
            raise RuntimeError("desk explain missing")
        return fallback
    result = _normalize(parsed, notes)
    if asking and not result.get("explain"):
        raise RuntimeError("desk explain missing")
    return result
