"""设计对话：从苏格拉底式聊天里逐渐抽出研究设定卡（dv/iv/controls/method）。

与 socratic.py（问题收敛）互补：这里的目标是把"研究设定"在对话中被问清楚，
一次只问一件事，已知信息即时回填设定卡。LLM 走统一通道；解析失败或 mock
时退回本地启发式（关键词信号 + 数据列匹配）。
"""
from __future__ import annotations

import json
import re
from typing import Any

from desk.heuristic import heuristic_discuss
from desk.shape_question import SIGNALS
from llm.call_llm import call_llm

SYSTEM = """你是实证经济学研究助手，正在和学生对话，把一个模糊念头收成可估计的研究设定。
规则：
1. 从对话与数据列里抽取已知设定（question/dv/iv/controls/method），已知就填，未知留 null；
2. 一次只问一件事，先问最关键的缺失：结果变量 → 处理/比较 → 方法 → 控制变量；
3. 方法只能从 OLS/DiD/IV/RD/SCM 里推荐，并给一句理由；
4. reply 不超过两句话，不要列表，不要论文腔。
只输出一个 JSON 对象，不要 Markdown。"""

METHOD_SIGNALS = [
    ("DiD", re.compile(r"政策|前后|试点|改革|效果| DID |did|双重差分|梯度", re.I)),
    ("IV", re.compile(r"内生|工具变量| iv |IV|因果识别不了", re.I)),
    ("RD", re.compile(r"断点|临界|分数线|rd|RDD", re.I)),
    ("SCM", re.compile(r"合成控制|对照地区|scm", re.I)),
]


def _prompt(notes: str, turns: list[dict[str, str]], columns: list[str]) -> str:
    history = "还没有。"
    if turns:
        history = "\n".join(
            f"- {item.get('role', 'user')}：{item.get('text', '')}" for item in turns[-8:]
        )
    cols = "、".join(columns) if columns else "（未知，学生还没给数据）"
    return f"""学生的念头：
{notes.strip() or '（还没说）'}

对话历史（最近 8 条）：
{history}

这份数据的可用列：{cols}

请输出：
{{
  "reply": "你对学生说的下一句话：确认一件已知的事 + 只追问一件缺的事",
  "design": {{
    "question": "成形中的研究问句，未知为 null",
    "dv": "结果变量（必须是数据列名或 null）",
    "iv": "处理/自变量（必须是数据列名或 null）",
    "controls": ["控制变量列名"],
    "method": "OLS/DiD/IV/RD/SCM 或 null"
  }},
  "need": "当前最缺的一件事，一句话",
  "ready": false
}}
用中文；design 里只允许用给定列名（question 除外）。"""


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


def _filter_to_columns(value: Any, columns: list[str]) -> Any:
    """LLM 给的列名必须是数据列；对不上就丢弃（不编造）。"""
    if value is None:
        return None
    text = str(value).strip()
    if not columns:
        return text or None
    lowered = {c.lower(): c for c in columns}
    return lowered.get(text.lower())


def _filter_controls(values: Any, columns: list[str]) -> list[str]:
    if not isinstance(values, list) or not columns:
        return []
    lowered = {c.lower(): c for c in columns}
    return [lowered[str(v).strip().lower()] for v in values if str(v).strip().lower() in lowered]


def _heuristic_method(notes: str, turns: list[dict[str, str]]) -> str | None:
    text = (notes + " " + " ".join(str(t.get("text", "")) for t in turns)).lower()
    for method, pattern in METHOD_SIGNALS:
        if pattern.search(text):
            return method
    if re.search(r"相关|影响|关系", text):
        return "OLS"
    return None


def _heuristic_columns(notes: str, turns: list[dict[str, str]], columns: list[str]) -> dict[str, Any]:
    """从念头+对话里找被点名的数据列（关键词信号优先，如 最低工资→wage 列）。"""
    text = (notes + " " + " ".join(str(t.get("text", "")) for t in turns)).lower()
    known = {
        "income": ("收入", "工资", "income"),
        "lnincome": ("收入", "lnincome"),
        "cigsale": ("香烟", "烟", "cigsale"),
        "employ": ("就业", "employ"),
        "health": ("健康", "health"),
        "treat": ("处理", "政策组", "treat"),
        "year": ("年份", "year"),
        "state": ("州", "省", "地区", "state"),
    }
    dv = iv = None
    controls: list[str] = []
    for col in columns:
        clues = known.get(col.lower())
        if clues and any(c in text for c in clues if isinstance(c, str)):
            if dv is None and col.lower() in ("income", "lnincome", "cigsale", "employ", "health"):
                dv = col
            elif col.lower() in ("treat", "state"):
                iv = iv or col
            else:
                controls.append(col)
    return {"dv": dv, "iv": iv, "controls": controls}


def heuristic_design_chat(
    notes: str, turns: list[dict[str, str]], columns: list[str]
) -> dict[str, Any]:
    """本地降级：LLM 不可用时仍能对话式推进（信号匹配 + 列名点名）。"""
    discuss = heuristic_discuss(notes, turns)
    cols = _heuristic_columns(notes, turns, columns)
    method = _heuristic_method(notes, turns)
    question = discuss.get("title") if discuss.get("ready") else None
    design = {
        "question": question,
        "dv": cols.get("dv"),
        "iv": cols.get("iv"),
        "controls": cols.get("controls", []),
        "method": method,
    }
    need = (
        "结果变量是什么" if not design["dv"]
        else "处理或比较是什么" if not design["iv"]
        else "想用哪类方法" if not design["method"]
        else "设定齐了，确认就能跑"
    )
    return {
        "reply": discuss.get("reflection") or f"我理解你在关注：{need}。",
        "design": design,
        "need": need,
        "ready": bool(design["question"] and design["dv"] and design["iv"] and design["method"]),
        "source": "heuristic",
    }


def design_chat(
    notes: str, turns: list[dict[str, str]] | None = None, columns: list[str] | None = None
) -> dict[str, Any]:
    """设计对话主入口：LLM 优先，mock/解析失败回退启发式。"""
    turns = list(turns or [])
    columns = list(columns or [])
    try:
        raw = call_llm(_prompt(notes, turns, columns), node_type="desk", system=SYSTEM)
        parsed = _extract_json(raw)
        if not parsed or not isinstance(parsed.get("design"), dict):
            raise ValueError("design chat parse failed")
    except Exception:
        if any(str(t.get("id") or "") == "ask" for t in turns):
            raise
        return heuristic_design_chat(notes, turns, columns)
    design_raw = parsed.get("design") or {}
    design = {
        "question": str(design_raw.get("question") or "").strip() or None,
        "dv": _filter_to_columns(design_raw.get("dv"), columns),
        "iv": _filter_to_columns(design_raw.get("iv"), columns),
        "controls": _filter_controls(design_raw.get("controls"), columns),
        "method": str(design_raw.get("method") or "").strip().upper() or None,
    }
    if design["method"] and design["method"] not in {"OLS", "DID", "IV", "RD", "SCM"}:
        design["method"] = None
    ready = bool(design["question"] and design["dv"] and design["iv"] and design["method"])
    return {
        "reply": str(parsed.get("reply") or "").strip() or "我们继续。",
        "design": design,
        "need": str(parsed.get("need") or "").strip(),
        "ready": ready,
        "source": "llm",
    }


__all__ = ["design_chat", "heuristic_design_chat"]
