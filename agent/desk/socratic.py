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
先判断学生这句话是在提供答案，还是在求助。如果学生说不知道、不清楚、看不懂、请你推荐或请你判断，你必须切换成研究助理：直接给出一个明确建议和理由，降低下一步的回答难度；禁止把同一个问题原样问回去。
数据集、变量字段、方法可行性和文献事实属于系统应当调查与判断的专业事实，不要要求学生凭记忆回答。你可以说明当前建议和仍需由系统核验的事项，但不得假装已经检查过尚未提供的数据。
没有数据字典或检索证据时，只能把数据集称为“候选”，不得断言它一定包含某个具体字段。
只有研究偏好、课程约束、数据访问权限和最终取舍需要学生确认。
不要写论文，不要给大纲，不要解释你在做什么，也不要替用户改写研究问题。
只输出一个 JSON 对象，不要 Markdown。"""

GUIDANCE_RE = re.compile(
    r"不知道|不清楚|不确定|没想好|不太懂|不懂|不了解|"
    r"你觉得|你建议|推荐|帮我(?:选|判断)|怎么选|什么意思|哪(?:些|个).{0,8}合适",
    re.I,
)


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

如果最近一条回答是在求解释、求推荐、表示不确定或把判断交给你：
- 先在 explain 中给出一个明确建议和理由；推荐项放在 options 第一位；
- 不要重复上一轮问题；下一问只能确认学生容易回答的偏好、约束或是否采用建议；
- 如果问题涉及数据源或字段，说明系统接下来会核验什么，不要反问学生是否知道字段。
如果最近一条是在直接回答，就吸收它并继续推进，不要把所有自由输入都当成追问。

请输出：
{{
  "intent": "research 或 conversation",
  "reflection": "对用户当前输入的自然回应，不超过两句",
  "question": "下一句只问一件缺的事，不超过 20 个字；问题已可估计则为空字符串",
  "options": [{{"id": "a", "label": "短选项"}}],
  "explain": "用户求解释、求推荐或表示不确定时，给出明确建议、理由和系统将核验的事项；否则为空字符串",
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


def _needs_guidance(turns: list[dict[str, str]]) -> bool:
    if not turns:
        return False
    latest = turns[-1]
    return str(latest.get("id") or "") == "ask" or bool(
        GUIDANCE_RE.search(str(latest.get("answer") or ""))
    )


def _same_question(left: str, right: str) -> bool:
    def normalize(value: str) -> str:
        return re.sub(r"[\s，。！？、；：,.!?;:]", "", value).lower()

    normalized_left = normalize(left)
    return bool(normalized_left and normalized_left == normalize(right))


def _asks_student_for_dataset_schema(question: str) -> bool:
    asks_availability = re.search(r"(?:能否|是否|能不能|有没有|可不可以|能).*(?:吗|？|\?)", question)
    asks_schema = re.search(r"拿到|包含|提供|字段|变量|教育年限|数据字典", question)
    return bool(asks_availability and asks_schema)


def _take_ownership_of_expert_facts(result: dict[str, Any]) -> dict[str, Any]:
    """数据字段是否存在是系统的查证任务，不是给学生出的考题。"""
    if not _asks_student_for_dataset_schema(str(result.get("question") or "")):
        return result
    existing = str(result.get("explain") or "").strip()
    ownership = "具体字段由我来核验，不需要你凭记忆判断。"
    result["explain"] = f"{existing} {ownership}".strip()
    result["question"] = "你手上已经有数据文件吗？"
    result["options"] = [
        {"id": "data_in_hand", "label": "已有数据"},
        {"id": "data_accessible", "label": "可以申请"},
        {"id": "data_no_access", "label": "还没有"},
    ]
    return result


def _finish_guidance_turn(
    result: dict[str, Any], turns: list[dict[str, str]]
) -> dict[str, Any]:
    """求助轮不能把专业判断原样退还给学生。"""
    if not _needs_guidance(turns):
        return result
    reflection = str(result.get("reflection") or "")
    if re.search(r"学生|用户|接下来(?:给|需要)", reflection):
        result["reflection"] = "我来替你判断，先给你一个可以直接采用的方案。"
    latest_question = str(turns[-1].get("question") or "")
    if _same_question(str(result.get("question") or ""), latest_question):
        result["question"] = "先按我的建议继续，可以吗？"
        result["options"] = [
            {"id": "accept_recommendation", "label": "按建议继续"},
            {"id": "compare_recommendation", "label": "再比较一下"},
        ]
    return result


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
    asking = _needs_guidance(turns)
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
    result = _take_ownership_of_expert_facts(
        _finish_guidance_turn(_normalize(parsed, notes), turns)
    )
    if asking and not result.get("explain"):
        raise RuntimeError("desk explain missing")
    return result
