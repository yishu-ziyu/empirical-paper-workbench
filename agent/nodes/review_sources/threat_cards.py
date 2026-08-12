"""CHARLS 识别威胁卡：生成约束 + 评审检查清单。

卡按 n_waves_min 过滤。默认波是两期，交错 DID 卡不会被激活。
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from dataset_profiles import load_profile

_CARDS_PATH = (
    Path(__file__).resolve().parents[2] / "dataset_profiles" / "threat_cards.yaml"
)

_THREAT_DIM_CAP = 0.4


def load_threat_cards() -> List[Dict[str, Any]]:
    """读 threat_cards.yaml。文件缺失时返回空列表，不炸图。"""
    if not _CARDS_PATH.is_file():
        return []
    with _CARDS_PATH.open(encoding="utf-8") as fh:
        payload = yaml.safe_load(fh) or {}
    cards = payload.get("cards") or []
    return [card for card in cards if isinstance(card, dict) and card.get("id")]


def resolve_n_waves(state: Dict[str, Any]) -> int:
    """选中波次数。state['selected_waves'] 优先，否则 CHARLS 默认两期。"""
    selected = state.get("selected_waves")
    if isinstance(selected, list) and selected:
        return len(selected)
    profile = load_profile("charls") or {}
    default_waves = profile.get("default_waves") or []
    if isinstance(default_waves, list) and default_waves:
        return len(default_waves)
    return 2


def is_charls_context(state: Dict[str, Any]) -> bool:
    """数据或方向点名 CHARLS 才启用威胁卡。"""
    profile = str(state.get("dataset_profile") or "").lower()
    if profile == "charls":
        return True
    blob = " ".join(
        [
            str(state.get("data_summary") or ""),
            str(state.get("research_direction") or ""),
            str(state.get("research_question") or ""),
        ]
    ).lower()
    return "charls" in blob


def active_threat_cards(state: Dict[str, Any]) -> List[Dict[str, Any]]:
    """当前样本激活的卡。非 CHARLS 或 n_waves 不够的卡直接丢掉。"""
    if not is_charls_context(state):
        return []
    n_waves = resolve_n_waves(state)
    active: List[Dict[str, Any]] = []
    for card in load_threat_cards():
        minimum = int(card.get("n_waves_min") or 1)
        if n_waves >= minimum:
            active.append(card)
    return active


def format_threat_constraints(cards: List[Dict[str, Any]]) -> str:
    """给 generate_chapter 用的约束文本。无卡时返回空串。"""
    lines = []
    for card in cards:
        constraint = (card.get("constraint") or "").strip()
        if constraint:
            lines.append(f"- [{card.get('id')}] {constraint}")
    return "\n".join(lines)


def apply_threat_caps(
    rubric: Dict[str, Any],
    content: str,
    cards: List[Dict[str, Any]],
) -> List[str]:
    """命中未处理威胁：对应维压到 0.4 以下。返回触发的卡 id。"""
    text = (content or "").lower()
    triggered: List[str] = []
    for card in cards:
        checks = [str(item).lower() for item in (card.get("check") or []) if item]
        if not checks:
            continue
        if any(item in text for item in checks):
            continue
        triggered.append(str(card.get("id")))
        for dim in card.get("dims") or []:
            if dim in rubric and isinstance(rubric[dim], (int, float)):
                rubric[dim] = min(float(rubric[dim]), _THREAT_DIM_CAP)
    return triggered
