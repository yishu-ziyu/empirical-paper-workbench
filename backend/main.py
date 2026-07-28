"""FastAPI application entrypoint for the econpaper backend."""

from __future__ import annotations

import sys
from pathlib import Path

# 把 econpaper/agent/ 加到 sys.path 末尾，让 `from graph import graph` / `from nodes...` 可用。
# 用 append 而非 insert：backend/ 必须优先（避免 agent/config.py 覆盖 backend/config.py）。
# 测试环境由 backend/tests/conftest.py 做同样的事。
_AGENT_DIR = Path(__file__).resolve().parent.parent / "agent"
if str(_AGENT_DIR) not in sys.path:
    sys.path.append(str(_AGENT_DIR))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root() -> dict[str, str]:
    return {"service": "econpaper-backend", "version": "0.1.0"}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


from routers.charls import router as charls_router  # noqa: E402
from routers.chapter import router as chapter_router  # noqa: E402
from routers.code_export import router as code_export_router  # noqa: E402
from routers.doc_export import router as doc_export_router  # noqa: E402
from routers.eda import router as eda_router  # noqa: E402
from routers.outline import router as outline_router  # noqa: E402
from routers.progress import router as progress_router  # noqa: E402
from routers.review import router as review_router  # noqa: E402
from routers.sample import router as sample_router  # noqa: E402
from routers.sessions import router as sessions_router  # noqa: E402
from routers.ws import router as ws_router  # noqa: E402

app.include_router(eda_router)
app.include_router(sessions_router)
app.include_router(ws_router)
app.include_router(outline_router)
app.include_router(chapter_router)
app.include_router(sample_router)
app.include_router(charls_router)
app.include_router(code_export_router)
app.include_router(doc_export_router)
app.include_router(progress_router)
app.include_router(review_router)
