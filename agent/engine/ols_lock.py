"""OLS hard lock: OLS / unspecified forms must not claim panel TWFE.

When the research direction is OLS, or the form does not ask for panel/DiD,
generate-chapter, the estimate path, and prompts must not inject or claim
双向固定效应 / TWFE / feols / xtreg / reghdfe. The public estimator label
is OLS / regress / lm.

Leftover gaps this module closes (issue #24):
- Denial-span masking after 不是/并非/不要 used to skip contrast claims
  such as 「而是采用双向固定效应」.
- Spec sentences such as 「加入州固定效应与年份固定效应」 never used the
  literal 双向固定效应, so a token-only lock missed them.

There is intentionally no negation window. Any hit is a TWFE claim.
"""
from __future__ import annotations

import re
from typing import Any, Mapping

from ..design.spec import norm_method


OLS_ESTIMATOR_LABEL = "OLS"
OLS_LABELS = frozenset({"OLS", "regress", "lm"})

_PANEL_DID_TOKENS = frozenset(
    {
        "did",
        "difference-in-differences",
        "difference_in_differences",
        "diff-in-diff",
        "diff_in_diff",
        "panel",
        "twfe",
        "fe",
        "event-study",
        "event_study",
        "event study",
    }
)
_CAUSAL_NON_OLS = frozenset({"iv", "rd", "scm"})

# Public estimator names that must not appear under the OLS lock.
_FORBIDDEN_ESTIMATOR_RE = re.compile(
    r"statspai\.feols|\bfeols\b|\breghdfe\b|\bxtreg\b|\bfelm\b",
    re.IGNORECASE,
)
_TWFE_LITERAL_RE = re.compile(
    r"双向\s*固定效应|双向\s*FE|two[-\s]?way\s+fixed\s+effects?|\bTWFE\b",
    re.IGNORECASE,
)
# Spec-style pair: 「加入州固定效应与年份固定效应」
_FE_PAIR_RE = re.compile(
    r"(?:加入了?|控制了?|纳入了?|吸收了?|采用了?|使用了?)?"
    r"[^。；，,\n]{0,12}固定效应\s*(?:与|和|及|、)\s*"
    r"[^。；，,\n]{0,12}固定效应"
)
# Entity or time FE named without the 双向固定效应 token.
_ENTITY_TIME_FE_RE = re.compile(
    r"(个体|单位|实体|州|省|省份|城市|县|行业|企业|"
    r"年份|年度|时间|波次|时期)固定效应"
)
_CONTRAST_TWFE_RE = re.compile(r"而是采用双向固定效应")

OLS_PROMPT_LOCK = (
    "【OLS 硬锁】本文计量方法是 OLS（Stata regress / R lm），"
    "不是面板或倍差法。禁止写入或主张：双向固定效应、TWFE、"
    "feols、xtreg、reghdfe、felm；"
    "禁止对比句「而是采用双向固定效应」；"
    "禁止设定句「加入州固定效应与年份固定效应」或任何"
    "个体/州/年份（实体+时间）固定效应。"
    "估计器标签必须写 OLS / regress / lm，不得写成 feols。"
)

_LITERAL_SUBS: tuple[tuple[re.Pattern[str], str], ...] = (
    (_CONTRAST_TWFE_RE, "而是采用 OLS"),
    (_FE_PAIR_RE, "采用 OLS 估计"),
    (_ENTITY_TIME_FE_RE, "OLS"),
    (re.compile(r"statspai\.feols", re.IGNORECASE), "OLS"),
    (re.compile(r"\bfeols\b", re.IGNORECASE), "OLS"),
    (re.compile(r"\breghdfe\b", re.IGNORECASE), "regress"),
    (re.compile(r"\bxtreg\b", re.IGNORECASE), "regress"),
    (re.compile(r"\bfelm\b", re.IGNORECASE), "lm"),
    (
        re.compile(r"two[-\s]?way\s+fixed\s+effects?", re.IGNORECASE),
        "OLS",
    ),
    (re.compile(r"\bTWFE\b", re.IGNORECASE), "OLS"),
    (re.compile(r"双向\s*FE"), "OLS"),
    (re.compile(r"双向\s*固定效应"), "OLS"),
)


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def method_token(state: Mapping[str, Any] | None, method: Any = None) -> str:
    """Best-effort method string. Direction/spec beat a leftover chapter method."""
    payload = _as_mapping(state)
    spec = _as_mapping(payload.get("main_specification"))
    rd = _as_mapping(payload.get("research_direction"))
    raw = spec.get("method") or rd.get("method") or method or ""
    return str(raw).strip().lower()


def _is_panel_or_did_token(token: str) -> bool:
    if not token:
        return False
    if norm_method(token) == "did":
        return True
    compact = token.replace("-", "_").replace(" ", "_")
    return token in _PANEL_DID_TOKENS or compact in _PANEL_DID_TOKENS


def asked_panel_or_did(state: Mapping[str, Any] | None, method: Any = None) -> bool:
    """True only when the form/direction explicitly asked for panel or DiD."""
    return _is_panel_or_did_token(method_token(state, method))


def method_triggers_ols_lock(method: Any) -> bool:
    """Lock when the method is OLS or the form did not ask for panel/DiD."""
    token = str(method or "").strip().lower()
    if _is_panel_or_did_token(token):
        return False
    canonical = norm_method(token)
    if canonical in _CAUSAL_NON_OLS:
        return False
    return True


def ols_lock_active(state: Mapping[str, Any] | None, method: Any = None) -> bool:
    """OLS lock for generate-chapter / estimate / prompts."""
    return method_triggers_ols_lock(method_token(state, method))


def contains_forbidden_twfe_claim(text: str) -> bool:
    """True when ``text`` claims TWFE / feols-family estimators.

    No denial span: 「不是 OLS，而是采用双向固定效应」 is still a claim.
    """
    if not text:
        return False
    return bool(
        _FORBIDDEN_ESTIMATOR_RE.search(text)
        or _TWFE_LITERAL_RE.search(text)
        or _FE_PAIR_RE.search(text)
        or _ENTITY_TIME_FE_RE.search(text)
        or _CONTRAST_TWFE_RE.search(text)
    )


def sanitize_ols_text(text: str) -> str:
    """Rewrite TWFE / feols-family claims to OLS / regress / lm wording."""
    if not text:
        return text
    out = text
    for pattern, replacement in _LITERAL_SUBS:
        out = pattern.sub(replacement, out)
    return out


def pooled_ols_formula(formula: str) -> str:
    """Drop pyfixest ``| FE`` syntax so OLS never carries a TWFE spec."""
    src = str(formula or "").strip()
    if not src:
        return src
    return src.split("|", 1)[0].strip()


def estimator_label(raw: Any) -> str:
    """Map an internal estimator name onto the public OLS / regress / lm label."""
    token = str(raw or "").strip()
    if token in OLS_LABELS:
        return token
    if not token or token == "未提供":
        return token or "未提供"
    lowered = token.lower()
    if "feols" in lowered or "xtreg" in lowered or "reghdfe" in lowered:
        return OLS_ESTIMATOR_LABEL
    if "felm" in lowered:
        return "lm"
    if "statsmodels.ols" in lowered or lowered in {"ols", "smf.ols", "sm.ols"}:
        return OLS_ESTIMATOR_LABEL
    return OLS_ESTIMATOR_LABEL
