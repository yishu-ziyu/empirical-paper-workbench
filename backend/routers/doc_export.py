"""REST endpoints for T-10: document export (LaTeX / PDF / docx).

- GET /sessions/{id}/doc-export?format=tex|pdf|docx&template=<name>
    format=tex  → LaTeX 源码（application/x-tex）
    format=pdf  → PDF 文件（application/pdf），latexmk 不可用时 503
    format=docx → Word 文件，pandoc 不可用时 503
    template ∈ {cn_journal, undergraduate, master_thesis, english_submission}
    别名：undergrad → undergraduate，master → master_thesis，
    en_submission → english_submission
    默认 cn_journal

session 状态由 ``AgentFacade`` 持有。``export_docx`` 节点在
``agent/nodes/export_docx.py``，facade 内部 import 它。测试通过
``monkeypatch.setattr("facade.export_docx_node", fake)`` 替换节点实现。
编译失败时降级为 503 + 提示。

Router self-registration：与 chapter.py 一致，import 时把 router 挂到
``main.app``，集成阶段再移到 main.py 显式注册。不改 main.py（T-10 文件边界）。
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, PlainTextResponse

from auth import get_optional_user, require_session_ownership
from facade import facade
from models.user import User

router = APIRouter()
_REGISTERED = False

# Word docx 的 MIME 类型
_DOCX_MEDIA_TYPE = (
    "application/vnd.openxmlformats-officedocument"
    ".wordprocessingml.document"
)


@router.get("/sessions/{session_id}/doc-export")
async def export_document(
    session_id: str,
    format: str = "tex",
    template: str = "cn_journal",
    current_user: Optional[User] = Depends(get_optional_user),
):
    """导出文档：format=tex|pdf|docx，template=4 模板之一。"""
    require_session_ownership(session_id, current_user)
    result = facade.export_document(session_id, template)

    if format == "tex":
        return PlainTextResponse(
            content=result["latex_source"],
            media_type="application/x-tex",
        )

    if format == "pdf":
        pdf_path = result.get("pdf_path")
        if not pdf_path:
            raise HTTPException(
                status_code=503,
                detail="PDF compilation unavailable (latexmk not installed)",
            )
        return FileResponse(
            path=pdf_path,
            media_type="application/pdf",
            filename="paper.pdf",
        )

    if format == "docx":
        docx_path = result.get("docx_path")
        if not docx_path:
            raise HTTPException(
                status_code=503,
                detail="docx conversion unavailable (pandoc not installed)",
            )
        return FileResponse(
            path=docx_path,
            media_type=_DOCX_MEDIA_TYPE,
            filename="paper.docx",
        )

    raise HTTPException(
        status_code=400,
        detail=f"Unsupported format: {format!r}; expected tex|pdf|docx",
    )


# ---------------------------------------------------------------------------
# self-registration（与 chapter.py 模式一致）
# ---------------------------------------------------------------------------
def _self_register() -> None:
    """Attach this router to the FastAPI app on import.

    Idempotent via ``_REGISTERED``. Integration phase moves
    ``app.include_router`` into ``main.py`` explicitly. Self-registering lets
    tests + dev runs reach the endpoint without touching ``main.py`` (T-10
    file-boundary constraint).
    """
    global _REGISTERED
    if _REGISTERED:
        return
    try:
        from main import app  # noqa: PLC0415

        app.include_router(router)
        _REGISTERED = True
    except Exception:
        # main not importable yet — skip silently.
        pass


_self_register()
