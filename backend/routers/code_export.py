"""REST endpoints for code file export (T-09).

POST /sessions/{session_id}/translate-code
    跑 agent ``translate_code``，把 ``code_translations`` 写入 session。
    HITL 写章路径不会自动进该节点，所以必须显式调用（或由 GET 首次下载填充）。

GET /sessions/{session_id}/code-export?format=py|do|R|m
    返回对应格式的代码文件下载（Content-Disposition: attachment）。

支持 4 种格式：
- ``py``    → Python (.py)
- ``do``    → Stata (.do)
- ``R``     → R (.R)
- ``m``     → EViews (.m)

session state 里的 ``code_translations`` 由 agent ``translate_code`` 节点
（T-09）写入，是 ``[{"lang", "code", "filename"}, ...]`` 列表。

Router self-registration: the integration phase will move the
``app.include_router`` call into ``main.py``. For now, importing this
module attaches the router to ``main.app`` so tests and dev runs reach
the endpoint without touching ``main.py`` (per T-09 file boundaries).
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field

from auth import get_optional_user, require_session_ownership
from facade import facade
from models.user import User
from schemas.responses import TranslateCodeResponse

router = APIRouter()

# format query 值 → code_translations 里的 lang 值
_FORMAT_TO_LANG: Dict[str, str] = {
    "py": "py",
    "do": "stata",
    "R": "r",
    "m": "eviews",
}

# 默认文件名（当 translation 缺 filename 时用）
_DEFAULT_FILENAME: Dict[str, str] = {
    "py": "analysis.py",
    "stata": "analysis.do",
    "r": "analysis.R",
    "eviews": "analysis.m",
}

# Content-Type per format
_CONTENT_TYPE: Dict[str, str] = {
    "py": "text/x-python",
    "stata": "text/x-stata",
    "r": "text/x-r",
    "eviews": "text/x-eviews",
}

_OUTCOME_KEYS = ("outcome", "outcome_col", "dv")
_TREATMENT_KEYS = ("treatment", "treatment_col", "iv")

# Placeholder output of translate_code when there is no Python and no named spec.
_STUB_MARKERS = ("无 Python 代码可翻译", "无 Python 代码")
_TAKEABLE_NEEDLES: Dict[str, tuple[str, ...]] = {
    "stata": ("import delimited", "xtreg", "reghdfe", "regress "),
    "r": ("read.csv", "feols", "felm", "lm("),
    "py": ("read_csv", "smf.ols", "sm.OLS"),
    "eviews": ("import ", "ls "),
}


def _find_translation(translations: List[Any], lang: str) -> Dict[str, Any]:
    """从 code_translations 列表里找指定 lang 的条目。"""
    for t in translations:
        if isinstance(t, dict) and t.get("lang") == lang:
            return t
    return {}


_OUTCOME_KEYS = ("outcome", "outcome_col", "dv")
_TREATMENT_KEYS = ("treatment", "treatment_col", "iv")


def _has_named_column(source: Any, keys: tuple[str, ...]) -> bool:
    if not isinstance(source, dict):
        return False
    for key in keys:
        raw = source.get(key)
        if raw is not None and str(raw).strip():
            return True
    return False


def _has_real_direction_columns(state: Any) -> bool:
    """True only when direction/spec names a real outcome and treatment.

    Empty sessions must not GET-autofill a fabricated y ~ treat script.
    """
    spec = state.get("main_specification") if isinstance(state, dict) else None
    rd = state.get("research_direction") if isinstance(state, dict) else None
    has_outcome = _has_named_column(spec, _OUTCOME_KEYS) or _has_named_column(
        rd, _OUTCOME_KEYS
    )
    has_treatment = _has_named_column(spec, _TREATMENT_KEYS) or _has_named_column(
        rd, _TREATMENT_KEYS
    )
    return has_outcome and has_treatment


def _is_stub_code(code: Any) -> bool:
    text = str(code or "").strip()
    if not text:
        return True
    return any(marker in text for marker in _STUB_MARKERS)


def _is_takeable(code: Any, lang: str) -> bool:
    """True when the file is runnable Stata/R/Python, not an empty stub."""
    text = str(code or "")
    if _is_stub_code(text):
        return False
    needles = _TAKEABLE_NEEDLES.get(lang) or ()
    return any(needle in text for needle in needles)


def _has_python_source(state: Any) -> bool:
    if not isinstance(state, dict):
        return False
    for ch in state.get("body_chapters") or []:
        if isinstance(ch, dict) and "```python" in str(ch.get("content") or ""):
            return True
    return False


def _can_rebuild_takeable(state: Any) -> bool:
    """Only run translate_code when it can emit real scripts, not stubs."""
    return _has_real_direction_columns(state) or _has_python_source(state)


class TranslateCodeResponse(BaseModel):
    ok: bool = True
    code_translations: List[Dict[str, Any]] = Field(default_factory=list)


@router.post(
    "/sessions/{session_id}/translate-code",
    response_model=TranslateCodeResponse,
)
async def translate_code_endpoint(
    session_id: str,
    current_user: Optional[User] = Depends(get_optional_user),
) -> TranslateCodeResponse:
    """Run translate_code so GET /code-export can return Stata / R files."""
    require_session_ownership(session_id, current_user)
    result = facade.run_translate_code(session_id)
    return TranslateCodeResponse(
        ok=True,
        code_translations=list(result.get("code_translations") or []),
    )


@router.get("/sessions/{session_id}/code-export")
async def export_code(
    session_id: str,
    format: str = "py",
    current_user: Optional[User] = Depends(get_optional_user),
):
    """导出代码文件。

    Parameters
    ----------
    session_id : str
        会话 ID。
    format : str
        代码格式：``py`` / ``do`` / ``R`` / ``m``。默认 ``py``。

    Returns
    -------
    PlainTextResponse
        带 ``Content-Disposition: attachment; filename="..."`` 的代码文本。

    Raises
    ------
    HTTPException
        - 404: session 不存在，或 no takeable translation (empty stubs are not files)
        - 400: 不支持的 format
    """
    require_session_ownership(session_id, current_user)
    if format not in _FORMAT_TO_LANG:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported format: {format!r}. "
                f"Supported: {sorted(_FORMAT_TO_LANG.keys())}"
            ),
        )

    lang = _FORMAT_TO_LANG[format]
    state = facade.get_state(session_id)
    translations = state.get("code_translations") or []
    entry = _find_translation(translations, lang)
    if not _is_takeable(entry.get("code"), lang) and _can_rebuild_takeable(state):
        # HITL write never runs the graph translate_code node. Fill or replace
        # stubs on first download when a real spec or Python fences exist.
        result = facade.run_translate_code(session_id)
        translations = result.get("code_translations") or []
        entry = _find_translation(translations, lang)
    if not _is_takeable(entry.get("code"), lang):
        raise HTTPException(
            status_code=404,
            detail=(
                "No takeable code translation in this session. "
                "POST /sessions/{id}/translate-code after generate, "
                "or set a research direction with outcome and treatment."
            ),
        )

    code = entry.get("code", "")
    filename = entry.get("filename") or _DEFAULT_FILENAME[lang]
    content_type = _CONTENT_TYPE[lang]

    return PlainTextResponse(
        content=code,
        media_type=content_type,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )


# 路由注册统一在 main.py include_router，不再 import 侧自注册。
