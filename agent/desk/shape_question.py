"""与 frontend/src/lib/shapeQuestion.ts 对齐的本地整理逻辑。"""
from __future__ import annotations

import re
from typing import Any

COMPARE_OPTIONS = [
    {"id": "policy", "label": "政策有没有效果"},
    {"id": "who", "label": "谁受到了影响"},
    {"id": "gap", "label": "差距有没有变大"},
]
OUTCOME_OPTIONS = [
    {"id": "work", "label": "工作和退休"},
    {"id": "wage", "label": "工资或收入"},
    {"id": "health", "label": "健康或消费"},
]
COMPARE_TEXT = {
    "policy": "比较政策前后",
    "who": "比较受影响更大的人和更小的人",
    "gap": "比较不同群体之间的差距",
}
OUTCOME_TEXT = {
    "work": "看就业、工时或退休",
    "wage": "看工资或收入",
    "health": "看健康或消费",
}

CONVERSATION_REPLY = (
    "你好！你可以随便说一句最近想研究的现象或问题，我会陪你一步步把它变成可检验的研究问题。"
    "如果已经有数据，也可以直接上传。"
)

# This is a conservative degraded-mode boundary, not a topic template. It only
# looks for language that explicitly signals a research task or relationship.
RESEARCH_INTENT_PATTERN = re.compile(
    r"研究|论文|课题|导师|老师让|开题|复现|数据|问什么|能发|"
    r"是否|有没有|会不会|影响|效应|关系|相关|导致|提高|降低|差异|变化|比较|"
    r"research|study|whether|effect|impact|relationship|data",
    re.I,
)


def has_research_intent(text: str) -> bool:
    """Conservatively decide whether degraded mode may enter research shaping."""
    return bool(RESEARCH_INTENT_PATTERN.search(re.sub(r"\s+", " ", text).strip()))


def user_intent_title(text: str) -> str:
    """Return the user's own wording; the fallback must not invent research content."""
    cleaned = re.sub(r"\s+", " ", text).strip()
    return cleaned or "这还是一个方向，还不是一个可以估计的问题。"


def next_prompt(answers: dict[str, str]) -> dict[str, Any] | None:
    if not answers.get("compare"):
        return {"id": "compare", "question": "你现在更想弄清哪一件事？", "options": COMPARE_OPTIONS}
    if not answers.get("outcome"):
        return {"id": "outcome", "question": "结果你更想看哪一类？", "options": OUTCOME_OPTIONS}
    return None


def reflect(text: str, answers: dict[str, str]) -> str:
    if not text.strip():
        return "你先说，我听着。"
    if not answers.get("compare"):
        return "我先保留你的原话。现在只确认要比较什么。"
    if not answers.get("outcome"):
        return f"比较这边有了：{COMPARE_TEXT[answers['compare']]}。还差结果看什么。"
    return "可以停在这里了。拿着这个问题往下走。"


def shape_question(text: str, answers: dict[str, str] | None = None) -> dict[str, Any]:
    answers = answers or {}
    if not has_research_intent(text):
        return {
            "intent": "conversation",
            "title": "",
            "comparison": "还没定",
            "outcome": "还没定",
            "heard": [],
            "missing": [],
            "ready": False,
            "reflection": CONVERSATION_REPLY,
        }
    missing: list[str] = []
    if not answers.get("compare"):
        missing.append("还不知道要比较什么")
    if not answers.get("outcome"):
        missing.append("还不知道结果看什么")
    return {
        "intent": "research",
        "title": user_intent_title(text),
        "comparison": COMPARE_TEXT.get(answers["compare"], "还没定") if answers.get("compare") else "还没定",
        "outcome": OUTCOME_TEXT.get(answers["outcome"], "还没定") if answers.get("outcome") else "还没定",
        "heard": [],
        "missing": missing,
        "ready": bool(answers.get("compare") and answers.get("outcome")),
        "reflection": reflect(text, answers),
    }
