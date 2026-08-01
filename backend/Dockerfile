# ============================================================
# econpaper backend — Python 3.12-slim + uvicorn
# ============================================================
FROM python:3.12-slim AS base

# 避免 Python 写 .pyc 和 stdout 缓冲
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# ------------------------------------------------------------------
# 先装依赖层（利用 Docker layer caching）
# ------------------------------------------------------------------
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ------------------------------------------------------------------
# 复制源码
# ------------------------------------------------------------------
COPY backend/ ./backend/
COPY agent/    ./agent/

# 把 agent 目录加到 Python path（与 backend/main.py 的 sys.path.append 一致）
ENV PYTHONPATH="/app/agent:${PYTHONPATH}"

# ------------------------------------------------------------------
# 运行时
# ------------------------------------------------------------------
EXPOSE 8000

# healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]