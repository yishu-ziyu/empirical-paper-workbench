"""空桌的苏格拉底讨论：一次只问一件事，产出一张问题卡。"""
from __future__ import annotations

import json
import re
from typing import Any

from desk.heuristic import heuristic_discuss
from llm.call_llm import call_llm

SYSTEM = """你是实证经济学研究的讨论者，不是聊天机器人。
用苏格拉底方式：把念头收成一句问句，再只追问一件事。
不要写论文，不要给大纲，不要解释你在做什么，不要复述用户原话。
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
  "title": "正在成形的研究问题，必须是一句完整问句",
  "question": "下一句只问一件缺的事，不超过 20 个字；问题已可估计则为空字符串",
  "options": [{{"id": "a", "label": "短选项"}}],
  "explain": "仅当用户在问选项是什么意思时，用一两句人话解释；否则必须是空字符串",
  "ready": false
}}
要求：options 最多 3 个，label 不超过 8 个字，不要括号和举例；ready 为 true 时 question 为空、options 为空；用中文。"""


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
    title = str(data.get("title") or "").strip()
    if not title:
        title = heuristic_discuss(notes, [])["title"]
    return {
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
