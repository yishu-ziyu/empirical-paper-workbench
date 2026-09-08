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
# ARM64 multimark (via pyfixest/maketables) builds a C extension.
# Keep the compiler and headers in an unshipped build stage.
FROM base AS dependencies
COPY backend/requirements.txt .
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM base AS runtime
COPY --from=dependencies /install /usr/local
COPY backend/requirements.txt /app/requirements.txt

# ------------------------------------------------------------------
# 复制源码
# ------------------------------------------------------------------
# Fetch the public pinned extract once at build time; runtime is offline.
COPY deploy/dependencies-card.json /app/deploy/dependencies-card.json
COPY scripts/check_card_package.py /app/scripts/check_card_package.py
ENV ECONPAPER_CARD_CSV=/opt/econpaper/card/data_card1995.csv
RUN python /app/scripts/check_card_package.py --fetch --data-only
COPY backend/ ./backend/
COPY agent/    ./agent/

# 项目根 /app + backend 目录加入 Python path：
# - /app          使 `import agent`（/app/agent 包）/ `import backend`（命名空间包）唯一解析
# - /app/backend  使 backend 各模块底部 `from config import settings` 唯一命中 /app/backend/config.py
# 均无需进程级 sys.path 拼接，依赖 import 路径而非顺序。
ENV PYTHONPATH="/app:/app/backend"

# ------------------------------------------------------------------
# 运行时
# ------------------------------------------------------------------
EXPOSE 8000

# healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
