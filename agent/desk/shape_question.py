"""与 frontend/src/lib/shapeQuestion.ts 对齐的本地整理逻辑。"""
from __future__ import annotations

import re
from typing import Any

SIGNALS = [
    ("charls", "CHARLS", re.compile(r"charls|中国健康与养老|养老追踪", re.I)),
    ("cfps", "CFPS", re.compile(r"cfps|家庭追踪", re.I)),
    ("cgss", "CGSS", re.compile(r"cgss|综合社会调查", re.I)),
    ("pension", "养老", re.compile(r"养老|退休|养老金|并轨")),
    ("digital", "数字经济", re.compile(r"数字经济|数字化|互联网")),
    ("wage", "最低工资", re.compile(r"最低工资|调薪|工资")),
    ("reproduce", "想复现一篇", re.compile(r"复现|那篇|看了篇|模仿")),
    ("advisor", "导师给的方向", re.compile(r"导师|老师让|作业|开题")),
]

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


def extract_heard(text: str) -> list[dict[str, str]]:
    return [{"id": sid, "label": label} for sid, label, pat in SIGNALS if pat.search(text)]


def next_prompt(answers: dict[str, str]) -> dict[str, Any] | None:
    if not answers.get("compare"):
        return {"id": "compare", "question": "你现在更想弄清哪一件事？", "options": COMPARE_OPTIONS}
    if not answers.get("outcome"):
        return {"id": "outcome", "question": "结果你更想看哪一类？", "options": OUTCOME_OPTIONS}
    return None


def _pick_title(text: str, heard: list[dict[str, str]], answers: dict[str, str]) -> str:
    ids = {item["id"] for item in heard}
    compare = answers.get("compare")
    outcome = answers.get("outcome")
    if "pension" in ids:
        if compare == "who":
            return "养老金变化之后，临近退休的人是不是比更年轻的人更早离开劳动力市场？"
        if outcome == "health":
            return "养老金变化之后，老年人的消费和健康有没有跟着变？"
        return "养老金并轨之后，临近退休的人是不是更早离开劳动力市场？"
    if "digital" in ids:
        if compare == "gap" or outcome == "wage":
            return "数字经济发展有没有拉大不同技能工人的工资差距？"
        return "数字经济发展之后，企业的用工和工资发生了什么变化？"
    if "wage" in ids:
        return "最低工资上调之后，低技能工人的就业是不是下降了？"
    if "reproduce" in ids:
        return "把那篇论文的问题放到中国数据上，重新问一遍。"
    cleaned = re.sub(r"\s+", " ", text).strip().rstrip("。！？.!?")
    if 12 <= len(cleaned) <= 48:
        return f"{cleaned}？"
    if len(cleaned) > 48:
        return f"{cleaned[:36]}…？"
    return "这还是一个方向，还不是一个可以估计的问题。"


def reflect(text: str, heard: list[dict[str, str]], answers: dict[str, str]) -> str:
    names = [item["label"] for item in heard]
    if not names:
        return "我听到了一些念头，但还抓不住一个可以估计的对象。" if text.strip() else "你先说，我听着。"
    if not answers.get("compare"):
        return f"我听到了{'、'.join(names)}。现在比较像一个方向，还不太像一个问题。"
    if not answers.get("outcome"):
        return f"比较这边有了：{COMPARE_TEXT[answers['compare']]}。还差结果看什么。"
    return "可以停在这里了。拿着这个问题往下走。"


def shape_question(text: str, answers: dict[str, str] | None = None) -> dict[str, Any]:
    answers = answers or {}
    heard = extract_heard(text)
    missing: list[str] = []
    if not answers.get("compare"):
        missing.append("还不知道要比较什么")
    if not answers.get("outcome"):
        missing.append("还不知道结果看什么")
    if not heard:
        missing.append("还听不太清具体对象")
    return {
        "title": _pick_title(text, heard, answers),
        "comparison": COMPARE_TEXT.get(answers["compare"], "还没定") if answers.get("compare") else "还没定",
        "outcome": OUTCOME_TEXT.get(answers["outcome"], "还没定") if answers.get("outcome") else "还没定",
        "heard": heard,
        "missing": missing,
        "ready": bool(answers.get("compare") and answers.get("outcome")),
        "reflection": reflect(text, heard, answers),
    }
