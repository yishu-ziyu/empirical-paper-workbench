"""/api/search endpoint — Phase 2 递归搜索 tab.

POST /api/search
  request  : SearchRequest(topic_slug, brief_path)
  response : SearchResponse(literature_markdown, literature_path, papers, verdict_passed)
  errors   : 500 (arxiv/LLM 错误)

路由由 L2-search 拥有；不修改 L1 brief router / L3-L5 其它 router。
"""
from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException

from Product.backend.wrapper.search_service import run_search
from Product.types.research import SearchRequest, SearchResponse

router = APIRouter()

# Tasks/ 目录 = repo root / Tasks
_TASKS_ROOT = Path(__file__).resolve().parents[2] / "Tasks"


@router.post("/api/search", response_model=SearchResponse)
def post_search(req: SearchRequest) -> SearchResponse:
    """递归搜索端点: 读 brief.md → LLM 生成检索词 → arxiv 召回 → LLM 重排 → 落盘 literature.md。"""
    try:
        return run_search(req, _TASKS_ROOT)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:  # noqa: BLE001  — 顶层兜底避免 5xx 暴露内部栈
        raise HTTPException(status_code=500, detail=f"search failed: {exc}")
