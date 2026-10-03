"""Map a title-first design draft onto the columns of the attached data.

``propose_design`` reads only the title / question and fills generic slot
names (``wages`` / ``schooling`` / ``treated`` / ``period``). On the formal
own-data path those names are then enforced against ``/direction`` by
``align_direction``, so a draft whose slots are not real columns can never
run (``design_execution_mismatch``). This module, used only when the session
already has a dataset, asks the generate model to choose actual columns from
the dataset schema and codebook, then validates every name against the
schema. The model never confirms anything: the result is still a draft.

Fail-safe: when the model is unavailable or answers garbage, slot names that
are not real columns are cleared (left for the user to choose) instead of
being kept as fake column names.
"""

from __future__ import annotations

import json
import re
from typing import Any, Callable, Mapping, Optional, Sequence

from .spec import norm_method

_MAX_PROMPT_COLUMNS = 600
_MAX_LABEL_CHARS = 48
_MAX_VALUE_EXAMPLES = 6
_MAX_CONTROLS = 12

_SCALAR_SLOTS = ("outcome", "treatment", "group", "treated", "period", "time_col", "id_col")
_LIST_SLOTS = ("controls", "heterogeneity_groups", "instruments")

_SYSTEM = (
    "你是计量经济学研究助理。根据学生的研究问题和数据集的列清单，"
    "为研究设计草稿挑选**数据里真实存在的列名**。只输出一个 JSON 对象，不要输出其他文字。"
)

_JSON_BLOCK = re.compile(r"\{.*\}", re.DOTALL)


def _column_lines(dataset: Mapping[str, Any]) -> list[str]:
    columns = [str(c) for c in dataset.get("columns") or []][:_MAX_PROMPT_COLUMNS]
    var_labels = dataset.get("variable_labels") or {}
    val_labels = dataset.get("value_labels") or {}
    dtypes = dataset.get("dtypes") or {}
    lines = []
    for col in columns:
        label = str(var_labels.get(col) or "")[:_MAX_LABEL_CHARS]
        parts = [col]
        if dtypes.get(col):
            parts.append(str(dtypes[col]))
        if label:
            parts.append(label)
        codes = val_labels.get(col) or {}
        if codes:
            sample = "; ".join(
                f"{k}={str(v)[:12]}" for k, v in list(codes.items())[:_MAX_VALUE_EXAMPLES]
            )
            parts.append(f"值标签: {sample}")
        lines.append(" | ".join(parts))
    return lines


def build_mapping_prompt(
    title: str,
    question: str,
    draft: Mapping[str, Any],
    dataset: Mapping[str, Any],
) -> str:
    named = draft.get("method") or "ols"
    return "\n".join(
        [
            f"研究题目：{title}",
            f"研究问题：{question or '（同题目）'}",
            f"规则初判的方法：{named}（学生在问题里明确点名的方法必须保留）",
            f"数据：{dataset.get('name') or '已上传数据'}，{dataset.get('rows') or '?'} 行。",
            "列清单（列名 | 类型 | 变量标签 | 值标签示例）：",
            *_column_lines(dataset),
            "",
            "请返回 JSON，键如下（没有就给空字符串或空数组，所有列名必须逐字来自上面的列清单）：",
            '{"method": "ols|iv|did|rd|scm", "outcome": "", "treatment": "", '
            '"controls": [], "heterogeneity_groups": [], "instruments": [], '
            '"group": "", "treated": "", "period": "", "time_col": "", "id_col": "", '
            '"notes": ["每条一句：列的口径、编码、缺失代码等需要学生注意的事实"], '
            '"question_to_user": "若有一项会改变分析的歧义，用一句话问学生；否则空字符串"}',
            "规则：",
            "- outcome 是被解释变量，treatment 是核心解释变量；controls 只放学生提到或常规必需的控制变量，最多 12 个。",
            "- 学生想看不同群体间的差异时，把分组列放进 heterogeneity_groups。",
            "- method=iv 时 instruments 放工具变量列；method=did 时 treated（处理组标识）和 period（政策后时期标识）放列名。",
            "- 不要编造列名；拿不准时留空并在 question_to_user 里问。",
        ]
    )


def _parse_json(text: str) -> Optional[dict]:
    if not isinstance(text, str):
        return None
    match = _JSON_BLOCK.search(text)
    if not match:
        return None
    try:
        value = json.loads(match.group(0))
    except json.JSONDecodeError:
        return None
    return value if isinstance(value, dict) else None


def _clean_list(values: Any, columns: set[str], dropped: list[str]) -> list[str]:
    if isinstance(values, str):
        values = [v.strip() for v in values.split(",")]
    out: list[str] = []
    for value in values or []:
        name = str(value or "").strip()
        if not name:
            continue
        if name not in columns:
            dropped.append(name)
            continue
        if name not in out:
            out.append(name)
    return out


def _clear_unknown_slots(draft: dict, columns: set[str]) -> list[str]:
    cleared = []
    for slot in _SCALAR_SLOTS:
        value = str(draft.get(slot) or "").strip()
        if value and value not in columns:
            draft[slot] = ""
            cleared.append(value)
    return cleared


def map_design_to_data(
    draft: Mapping[str, Any],
    dataset: Mapping[str, Any],
    *,
    title: str,
    question: str = "",
    llm: Optional[Callable[[str], str]] = None,
) -> dict[str, Any]:
    """Return a new draft whose slots name real columns of ``dataset``.

    ``llm`` takes a prompt and returns text; defaults to the generate role.
    """
    columns = {str(c) for c in dataset.get("columns") or []}
    out = dict(draft)
    out["interactions"] = [dict(i) for i in draft.get("interactions") or []]
    if not columns:
        return out

    rule_method = norm_method(draft.get("method")) or "ols"
    explicit_method = rule_method != "ols"
    dropped: list[str] = []
    proposal: dict[str, Any] = {"source": "rule", "notes": [], "question_to_user": ""}

    answer = None
    try:
        if llm is None:
            from ..llm.call_llm import call_llm

            def llm(prompt: str) -> str:  # type: ignore[no-redef]
                return call_llm(prompt, node_type="generate", system=_SYSTEM)

        answer = _parse_json(llm(build_mapping_prompt(title, question, draft, dataset)))
    except Exception as exc:  # model down: keep the draft honest instead
        proposal["error"] = type(exc).__name__

    if answer is None:
        cleared = _clear_unknown_slots(out, columns)
        for item in out["interactions"]:
            if item.get("left") not in columns or item.get("right") not in columns:
                item["left"] = item["right"] = item["term"] = ""
        out["interactions"] = [i for i in out["interactions"] if i.get("term")]
        proposal["cleared"] = cleared
        proposal["notes"].append("未能自动对应数据列，请在设计里选择实际列。")
        out["proposal"] = proposal
        return out

    proposal["source"] = "llm"
    method = norm_method(answer.get("method")) or rule_method
    if explicit_method:
        method = rule_method
    out["method"] = method

    for slot in _SCALAR_SLOTS:
        value = str(answer.get(slot) or "").strip()
        if value and value not in columns:
            dropped.append(value)
            value = ""
        out[slot] = value
    treatment = out.get("treatment") or ""
    out["controls"] = [
        c for c in _clean_list(answer.get("controls"), columns, dropped)
        if c not in (out.get("outcome"), treatment)
    ][:_MAX_CONTROLS]
    groups = [
        g for g in _clean_list(answer.get("heterogeneity_groups"), columns, dropped)
        if g not in (out.get("outcome"), treatment)
    ]
    out["heterogeneity_groups"] = groups
    instruments = _clean_list(answer.get("instruments"), columns, dropped)
    if method == "iv":
        out["instruments"] = instruments

    interactions: list[dict[str, str]] = []
    if method == "did":
        treated, period = out.get("treated") or "", out.get("period") or ""
        if treated and period:
            interactions.append(
                {"kind": "did", "left": treated, "right": period, "term": f"{treated}:{period}"}
            )
        if not out.get("group"):
            out["group"] = treated
    if method == "did":
        # The 2x2 term already crosses treated and period; a het item on the
        # same columns would duplicate it (treated:period:treated).
        did_cols = {out.get("treated"), out.get("period")}
        groups = [g for g in groups if g not in did_cols]
        out["heterogeneity_groups"] = groups
    if treatment:
        for group in groups:
            if group == treatment:
                continue
            interactions.append(
                {"kind": "het", "left": treatment, "right": group, "term": f"{treatment}:{group}"}
            )
    out["interactions"] = interactions
    if groups and method == "ols":
        out["qType"] = "heterogeneity"

    notes = answer.get("notes")
    if isinstance(notes, list):
        proposal["notes"] = [str(n)[:200] for n in notes if str(n).strip()][:8]
    proposal["question_to_user"] = str(answer.get("question_to_user") or "")[:300]
    if dropped:
        proposal["dropped"] = sorted(set(dropped))
    out["proposal"] = proposal
    return out


def apply_design_overrides(
    draft: Mapping[str, Any],
    overrides: Mapping[str, Any],
    columns: Sequence[str],
) -> dict[str, Any]:
    """Apply user edits to a draft. Unknown column names raise ``ValueError``."""
    known = {str(c) for c in columns}
    out = dict(draft)
    out["interactions"] = [dict(i) for i in draft.get("interactions") or []]

    def check(name: str) -> str:
        name = str(name or "").strip()
        if name and known and name not in known:
            raise ValueError(f"unknown_column:{name}")
        return name

    if overrides.get("method"):
        method = norm_method(overrides["method"])
        if method is None:
            raise ValueError("unknown_method")
        out["method"] = method
    for slot in _SCALAR_SLOTS:
        if slot in overrides and overrides[slot] is not None:
            out[slot] = check(overrides[slot])
    for slot in _LIST_SLOTS:
        if slot in overrides and overrides[slot] is not None:
            out[slot] = [check(v) for v in overrides[slot] if str(v or "").strip()]

    touched = any(k in overrides and overrides[k] is not None for k in
                  ("method", "treatment", "treated", "period", "heterogeneity_groups"))
    if touched:
        interactions = []
        if out.get("method") == "did" and out.get("treated") and out.get("period"):
            interactions.append({"kind": "did", "left": out["treated"], "right": out["period"],
                                 "term": f"{out['treated']}:{out['period']}"})
        if out.get("method") == "did":
            did_cols = {out.get("treated"), out.get("period")}
            out["heterogeneity_groups"] = [
                g for g in out.get("heterogeneity_groups") or [] if g not in did_cols
            ]
        if out.get("treatment"):
            for group in out.get("heterogeneity_groups") or []:
                if group == out["treatment"]:
                    continue
                interactions.append({"kind": "het", "left": out["treatment"], "right": group,
                                     "term": f"{out['treatment']}:{group}"})
        out["interactions"] = interactions
        if out.get("method") == "ols":
            out["qType"] = "heterogeneity" if out.get("heterogeneity_groups") else "average"
        elif out.get("method") in {"did", "iv", "rd", "scm"}:
            out["qType"] = "causal"
    if overrides.get("qType"):
        out["qType"] = str(overrides["qType"])
    proposal = dict(out.get("proposal") or {})
    proposal["edited_by_user"] = sorted(
        k for k, v in overrides.items() if v is not None
    )
    out["proposal"] = proposal
    return out


__all__ = ["apply_design_overrides", "build_mapping_prompt", "map_design_to_data"]
