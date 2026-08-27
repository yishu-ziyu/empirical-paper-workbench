"""REST endpoints for code file export (T-09).

POST /sessions/{session_id}/translate-code
    跑 agent ``translate_code``，把 ``code_translations`` 写入 session。
    HITL 写章路径不会自动进该节点，所以必须显式调用。

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

router = APIRouter()
_REGISTERED = False

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


def _find_translation(translations: List[Any], lang: str) -> Dict[str, Any]:
    """从 code_translations 列表里找指定 lang 的条目。"""
    for t in translations:
        if isinstance(t, dict) and t.get("lang") == lang:
            return t
    return {}


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
        - 404: session 不存在，或 session 无 code_translations
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

    state = facade.get_state(session_id)
    translations = state.get("code_translations") or []
    if not translations:
        raise HTTPException(
            status_code=404,
            detail=(
                "No code translations in this session. "
                "Run the paper pipeline (translate_code node) first."
            ),
        )

    lang = _FORMAT_TO_LANG[format]
    entry = _find_translation(translations, lang)
    if not entry:
        raise HTTPException(
            status_code=404,
            detail=f"No {lang!r} translation in session",
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


# ---------------------------------------------------------------------------
# self-registration（与 chapter.py / eda.py 模式一致）
# ---------------------------------------------------------------------------
def _self_register() -> None:
    """Attach this router to the FastAPI app on import.

    The integration phase will move ``app.include_router`` into ``main.py``
    explicitly. Self-registering here lets tests (which import this module)
    and dev runs reach the endpoint without modifying ``main.py`` (T-09
    file-boundary constraint). Idempotent via the ``_REGISTERED`` flag.
    """
    global _REGISTERED
    if _REGISTERED:
        return
    try:
        from main import app  # noqa: PLC0415

        app.include_router(router)
        _REGISTERED = True
    except Exception:
        # main not importable yet (e.g. during partial builds) — skip silently.
        pass


_self_register()
