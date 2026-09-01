"""FastAPI application entrypoint for the econpaper backend."""

from __future__ import annotations

import logging
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError as PydanticValidationError

from config import settings


# ---------------------------------------------------------------------------
# Lifespan: create database tables on startup
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: create DB tables on startup, clean up on shutdown."""
    from database import create_tables

    await create_tables()

    try:
        from agent.llm.ssot import load_ssot
        from agent.llm.router import router as llm_router

        load_ssot()
        llm_router.reload()
        gen = llm_router.get_config("generate")
        rev = llm_router.get_config("review")
        print(
            f"✓ LLM generate={gen.provider}/{gen.model} "
            f"review={rev.provider}/{rev.model}"
        )
    except Exception as exc:
        print(f"⚠ LLM router init failed (will mock): {exc}")

    # Initialize S3 connection if configured.
    if settings.S3_ENDPOINT_URL:
        try:
            from storage.s3 import s3_fs
            # Trigger lazy connection test.
            s3_fs.client
            print(f"✓ S3 connected: {settings.S3_ENDPOINT_URL}")
        except Exception as exc:
            print(f"⚠ S3 connection failed (degraded): {exc}")

    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=settings.CORS_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Global exception handlers (F7: 异常处理与降级 UX)
# ---------------------------------------------------------------------------
logger = logging.getLogger("econpaper")


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Return structured JSON for known HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "detail": exc.detail,
            "code": exc.status_code,
            "degraded": exc.status_code >= 500,
        },
    )


@app.exception_handler(PydanticValidationError)
async def validation_exception_handler(
    request: Request, exc: PydanticValidationError
) -> JSONResponse:
    """Return 422 with field-level errors for pydantic validation failures."""
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation error",
            "detail": exc.errors(),
            "code": 422,
            "degraded": False,
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all: return 500 with request_id for debugging."""
    request_id = str(uuid.uuid4())
    logger.error("Request %s failed: %s", request_id, exc)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "request_id": request_id,
            "degraded": True,
            "detail": str(exc) if settings.DEBUG else "An unexpected error occurred",
        },
    )


# Override FastAPI's default 404 handler for completely unknown routes.
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: Exception) -> JSONResponse:
    """Return structured JSON for unknown routes (not just HTTPException)."""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "detail": "Not Found",
            "code": 404,
            "degraded": False,
        },
    )


@app.get("/")
def root() -> dict[str, str]:
    return {"service": "econpaper-backend", "version": "0.1.0"}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


from routers.analysis import router as analysis_router  # noqa: E402
from routers.agent_spike import router as agent_spike_router  # noqa: E402
from routers.auth import router as auth_router  # noqa: E402
from routers.charls import router as charls_router  # noqa: E402
from routers.chapter import router as chapter_router  # noqa: E402
from routers.desk import router as desk_router  # noqa: E402
from routers.code_export import router as code_export_router  # noqa: E402
from routers.doc_export import router as doc_export_router  # noqa: E402
from routers.eda import router as eda_router  # noqa: E402
from routers.labels import router as labels_router  # noqa: E402
from routers.outline import router as outline_router  # noqa: E402
from routers.paper_draft import router as paper_draft_router  # noqa: E402
from routers.progress import router as progress_router  # noqa: E402
from routers.review import router as review_router  # noqa: E402
from routers.runs import router as runs_router  # noqa: E402
from routers.sample import router as sample_router  # noqa: E402
from routers.sessions import router as sessions_router  # noqa: E402
from routers.ws import router as ws_router  # noqa: E402

app.include_router(auth_router)
app.include_router(agent_spike_router)
app.include_router(analysis_router)
app.include_router(eda_router)
app.include_router(sessions_router)
app.include_router(ws_router)
app.include_router(labels_router)
app.include_router(outline_router)
app.include_router(paper_draft_router)
app.include_router(chapter_router)
app.include_router(desk_router)
app.include_router(sample_router)
app.include_router(charls_router)
app.include_router(code_export_router)
app.include_router(doc_export_router)
app.include_router(progress_router)
app.include_router(review_router)
app.include_router(runs_router)
