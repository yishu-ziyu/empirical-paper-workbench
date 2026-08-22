# Handoff: F11 - Docker 部署配置

## 目标
为 econpaper 实现完整的 Docker 部署方案，包括 Dockerfile（后端 + 前端构建）、docker-compose 编排（后端 + 前端 + PostgreSQL + Nginx 反向代理）、环境区分（dev/prod），让一条命令即可启动全栈应用。

## 背景
- 后端：FastAPI + uvicorn，端口 8000，依赖 `requirements.txt`
- 前端：Vite + React，开发模式端口 5173，生产构建输出到 `dist/`
- 数据库：SQLite 默认，生产需切换到 PostgreSQL（`DATABASE_URL` + `CHECKPOINT_DB_URL`）
- 用户体系（F10）已完成 ✅，需要 PostgreSQL 做持久化
- 当前无 Dockerfile 或 docker-compose.yml（仅 agent/.venv 下有 langsmith 的无关 yaml）
- 根目录已有 Makefile，`make dev` 启动开发环境

## 具体改动

### 1. 后端 Dockerfile

创建 `backend/Dockerfile`：

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# 安装系统依赖（psycopg2 需要 libpq）
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 安装额外依赖（auth 需要）
RUN pip install --no-cache-dir "passlib[bcrypt]" python-jose[cryptography] sqlalchemy asyncpg aiosqlite psycopg2-binary

# 复制代码
COPY . .

# 复制 agent 目录（后端依赖 agent/graph.py）
COPY ../agent /app/agent

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. 前端 Dockerfile（多阶段构建）

创建 `frontend/Dockerfile`：

```dockerfile
# Build stage
FROM node:20-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

# Serve stage
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 3. Nginx 配置

创建 `nginx.conf`（项目根目录或 `deploy/nginx.conf`）：

```nginx
server {
    listen 80;
    server_name localhost;

    # 前端静态文件
    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # 后端 API 代理
    location /api/ {
        rewrite ^/api(/.*)$ $1 break;
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # WebSocket 代理
    location /ws/ {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

### 4. docker-compose.yml

创建项目根目录 `docker-compose.yml`：

```yaml
version: "3.8"

services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: econpaper
      POSTGRES_USER: econpaper
      POSTGRES_PASSWORD: ${DB_PASSWORD:-econpaper_dev}
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U econpaper"]
      interval: 5s
      timeout: 5s
      retries: 5
    ports:
      - "5432:5432"

  backend:
    build: ./backend
    depends_on:
      postgres:
        condition: service_healthy
    environment:
      - DATABASE_URL=postgresql+asyncpg://econpaper:${DB_PASSWORD:-econpaper_dev}@postgres:5432/econpaper
      - CHECKPOINT_DB_URL=postgresql://econpaper:${DB_PASSWORD:-econpaper_dev}@postgres:5432/econpaper
      - JWT_SECRET_KEY=${JWT_SECRET_KEY:?set JWT_SECRET_KEY}
      - JWT_ALGORITHM=HS256
      - ACCESS_TOKEN_EXPIRE_HOURS=24
      - CORS_ORIGINS=http://localhost:80
      - UPLOAD_DIR=/data/uploads
      - DEBUG=false
    volumes:
      - uploads:/data/uploads
    ports:
      - "8000:8000"

  frontend:
    build: ./frontend
    depends_on:
      - backend
    ports:
      - "80:80"

volumes:
  pgdata:
  uploads:
```

### 5. 环境区分

创建 `deploy/` 目录，放环境配置文件：

- `deploy/.env.prod` — 生产环境变量模板（含 JWT_SECRET_KEY 占位）
- `deploy/.env.dev` — 开发环境变量（与默认值一致）

### 6. 更新 Makefile

在 `Makefile` 中添加 Docker targets：

```makefile
docker-build:
    docker compose build

docker-up:
    docker compose up -d

docker-down:
    docker compose down

docker-logs:
    docker compose logs -f

docker-clean:
    docker compose down -v
```

### 7. 更新 .gitignore

添加 Docker 相关忽略（如果不在已有 .gitignore 中）：
```
.env
.env.prod
```

### 8. 测试

- 运行 `docker compose build` 成功
- 运行 `docker compose up -d` 启动成功
- 访问 `http://localhost/health` 返回 200
- 访问 `http://localhost/` 返回前端页面
- 注册/登录流程正常
- 上传 CSV 文件正常
- 前端测试：`cd frontend && npm test`（153 passed）
- 后端测试：`cd agent && source .venv/bin/activate && python -m pytest tests/ -q`（357 passed）

## 依赖
- 前置：F10（用户体系）✅ — 需要 PostgreSQL 做用户持久化
- 后置：CI/CD 流水线（F13）依赖本任务
- 不阻塞 F12（S3 文件存储）

## 验收标准
- [ ] `docker compose build` 构建成功
- [ ] `docker compose up -d` 启动后三个容器（postgres/backend/frontend）正常运行
- [ ] 访问 `http://localhost/health` 返回 `{"status":"ok"}`
- [ ] 访问 `http://localhost/` 加载前端页面（econpaper v0 标题可见）
- [ ] 注册用户 → 登录 → 上传 CSV → 正常流程跑通
- [ ] 停止容器后重新 `docker compose up -d`，数据不丢失（PostgreSQL 卷持久化）
- [ ] 前端测试（153 passed）仍然通过
- [ ] 后端测试（357 passed）仍然通过