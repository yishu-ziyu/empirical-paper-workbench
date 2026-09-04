.PHONY: dev dev-frontend dev-backend dev-runner install install-frontend install-backend install-agent health test test-agent test-backend test-frontend smoke-agent verify-deps verify clean gen-api check-api-drift \
        docker-up docker-down docker-build docker-logs docker-ps docker-clean

# Python 版本：项目锁定 3.12（3.14 下 numpy/pydantic 依赖装不上）。
# 可用 PY=python3.12 覆盖，需机器上存在 python3.12。
PY ?= python3.12
DEPENDENCY_ROOT ?= $(if $(ECONPAPER_DEPENDENCY_ROOT),$(ECONPAPER_DEPENDENCY_ROOT),../dependencies)
FRONTEND_URL ?= http://127.0.0.1:5173
BACKEND_URL ?= http://127.0.0.1:8000

# import 根：与 backend/Dockerfile 的 ENV PYTHONPATH="/app:/app/backend" 同构。
# 一份定义，dev-backend / gen-api 共用 —— 加新 target 时前缀 $(PYPATH) 即可，别再手写 PYTHONPATH=..。
# 用绝对路径：cd 之后相对的 .. 会失效。
PYPATH := PYTHONPATH=$(CURDIR):$(CURDIR)/backend

# 默认并发起 frontend + backend；Ctrl-C 同时杀掉
dev:
	@trap 'kill 0' INT TERM; \
		$(MAKE) dev-backend & \
		$(MAKE) dev-runner & \
		$(MAKE) dev-frontend & \
		wait

dev-frontend:
	cd frontend && npm run dev

# host 绑 127.0.0.1 而非 0.0.0.0：开发机不暴露到局域网。
# 容器内必须 0.0.0.0，见 backend/Dockerfile CMD（docker-compose 已收窄映射到 127.0.0.1:8000）
dev-backend:
	cd backend && . .venv/bin/activate 2>/dev/null || true; \
		DEBUG=true $(PYPATH) uvicorn main:app --reload --reload-dir . --reload-dir ../agent --host 127.0.0.1 --port 8000

dev-runner:
	cd backend && . .venv/bin/activate 2>/dev/null || true; \
		DEBUG=true $(PYPATH) python -m runner

# 一次性装齐所有依赖
install: install-frontend install-backend install-agent

install-frontend:
	cd frontend && npm install

# In-place LangGraph 0.x → v1 upgrades can remove overlapping prebuilt files.
install-backend:
	cd backend && $(PY) -m venv .venv || true; \
	. .venv/bin/activate; \
	pip install -r requirements.txt; \
	pip install --force-reinstall --no-deps "langgraph-prebuilt==1.1.0"; \
	pip install "pyfixest==0.60.0" || true
	backend/.venv/bin/python -m pip install -e "$(DEPENDENCY_ROOT)/StatsPAI"

install-agent:
	cd agent && $(PY) -m venv .venv || true; \
	. .venv/bin/activate; \
	pip install -r requirements.txt; \
	pip install --force-reinstall --no-deps "langgraph-prebuilt==1.1.0"; \
	pip install "pyfixest==0.60.0" || true
	agent/.venv/bin/python -m pip install -e "$(DEPENDENCY_ROOT)/StatsPAI"

# 验证 backend 健康检查
health:
	@curl --fail --silent --show-error $(BACKEND_URL)/health

# 测试入口：三个分项严格传播失败，任一失败 make 即失败。
# pytest 必须给 --basetemp（全新目录）：否则沙箱拦截 mkdir 会误报 198 个 error（环境噪音，非代码问题）。
test: check-api-drift test-agent test-backend test-frontend
	@echo "[test] agent + backend + frontend 全部通过"

test-agent:
	@echo "[test-agent] agent/tests（agent/.venv）"
	$(PYPATH) agent/.venv/bin/python -m pytest -q --tb=line -p no:cacheprovider \
		--basetemp=$$(mktemp -d /tmp/ep-agent-XXXXXX) agent/tests

test-backend:
	@echo "[test-backend] backend/tests（backend/.venv）"
	$(PYPATH) backend/.venv/bin/python -m pytest -q --tb=line -p no:cacheprovider \
		--basetemp=$$(mktemp -d /tmp/ep-backend-XXXXXX) backend/tests

test-frontend:
	@echo "[test-frontend] vitest run"
	cd frontend && npm test

# 验证 graph 可 import（agent 冒烟测试）
smoke-agent:
	agent/.venv/bin/python -c "from agent.graph import graph; print('graph ok:', graph)"

# 两个运行环境都必须指向当前工作区的 StatsPAI 源码，不接受旧 editable install 或 PyPI 副本。
verify-deps:
	@echo "[verify-deps] agent StatsPAI editable source"; agent/.venv/bin/python -c "from agent.upstream import get_dependency_status as status; item = status()['statspai']; assert item['installed'] and item['source_matches_repo'], item"
	@echo "[verify-deps] backend StatsPAI editable source"; backend/.venv/bin/python -c "from agent.upstream import get_dependency_status as status; item = status()['statspai']; assert item['installed'] and item['source_matches_repo'], item"

# 验证 frontend / backend / agent 三件套都活
verify: smoke-agent verify-deps
	@echo "[verify] econpaper frontend $(FRONTEND_URL)"; \
		curl --fail --silent --show-error $(FRONTEND_URL)/ | grep -Fq '<title>econpaper</title>'
	@echo "[verify] econpaper backend $(BACKEND_URL)"; \
		curl --fail --silent --show-error $(BACKEND_URL)/openapi.json | \
		backend/.venv/bin/python -c "import json, sys; assert json.load(sys.stdin)['info']['title'] == 'econpaper-backend'"
	@curl --fail --silent --show-error $(BACKEND_URL)/health
	@echo "[verify] agent import"; agent/.venv/bin/python -c "from agent.graph import graph; print('graph ok')"

clean:
	rm -rf frontend/node_modules frontend/dist backend/.venv agent/.venv
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

# ---------------------------------------------------------------------------
# Docker 部署（F11）
# ---------------------------------------------------------------------------

# 首次启动（构建 + 后台运行）
docker-up:
	@test -f .env || { echo "缺少 .env 文件，请 cp .env.docker .env 后编辑"; exit 1; }
	docker compose up -d --build

# 停止并移除容器
docker-down:
	docker compose down

# 仅构建镜像（不启动）
docker-build:
	docker compose build

# 查看实时日志
docker-logs:
	docker compose logs -f

# 查看容器状态
docker-ps:
	docker compose ps

# 清理所有 Docker 资源（数据卷 + 镜像 + 容器）
docker-clean:
	docker compose down -v
	docker rmi econpaper-backend econpaper-frontend 2>/dev/null || true

# Stage D: 从 backend 导出 openapi.json 并生成 frontend types/api.ts
# 依赖：backend/.venv 已装、frontend/node_modules 已装
gen-api:
	@echo "[gen-api] 导出 openapi.json from backend"
	@cd backend && DEBUG=true $(PYPATH) .venv/bin/python -c "\
import json; \
from main import app; \
open('../frontend/openapi.json', 'w').write(json.dumps(app.openapi(), indent=2, ensure_ascii=False)); \
open('../docs/api/openapi.json', 'w').write(json.dumps(app.openapi(), indent=2, ensure_ascii=False)); \
print('[gen-api] openapi.json exported, schemas:', len(app.openapi().get('components', {}).get('schemas', {})))"
	@echo "[gen-api] 生成 frontend/src/types/api.ts"
	@cd frontend && npx openapi-typescript openapi.json -o src/types/api.ts
	@echo "[gen-api] done"

# API 契约同步闸门（CI gate）。两段都查，缺一不可：
#   1) openapi.json ↔ 后端代码 —— 漏了这段，改了路由不跑 gen-api 也能通过（本仓库真实踩过）
#   2) types/api.ts ↔ openapi.json
# 任一段 drift 都打印 diff 并 exit 1。
check-api-drift:
	@echo "[check-api-drift] ① 从后端代码重新导出 openapi.json"
	@cd backend && DEBUG=true $(PYPATH) .venv/bin/python -W ignore::UserWarning -c "\
import json; \
from main import app; \
open('/tmp/openapi.drift.json', 'w').write(json.dumps(app.openapi(), indent=2, ensure_ascii=False))"
	@if diff -q frontend/openapi.json /tmp/openapi.drift.json >/dev/null 2>&1; then \
		echo "[check-api-drift] ✅ openapi.json 与后端代码同步"; \
	else \
		echo "[check-api-drift] ❌ openapi.json 落后于后端代码，请运行 make gen-api"; \
		diff frontend/openapi.json /tmp/openapi.drift.json | head -40 || true; \
		exit 1; \
	fi
	@if diff -q docs/api/openapi.json /tmp/openapi.drift.json >/dev/null 2>&1; then \
		echo "[check-api-drift] ✅ docs/api/openapi.json 与后端代码同步"; \
		rm -f /tmp/openapi.drift.json; \
	else \
		echo "[check-api-drift] ❌ docs/api/openapi.json 落后于后端代码，请运行 make gen-api"; \
		diff docs/api/openapi.json /tmp/openapi.drift.json | head -40 || true; \
		rm -f /tmp/openapi.drift.json; \
		exit 1; \
	fi
	@echo "[check-api-drift] ② 重新生成 api.ts 并 diff"
	@cd frontend && npx openapi-typescript openapi.json -o /tmp/api.drift.ts 2>/dev/null
	@if diff -q frontend/src/types/api.ts /tmp/api.drift.ts >/dev/null 2>&1; then \
		echo "[check-api-drift] ✅ types/api.ts 与 openapi.json 同步"; \
		rm -f /tmp/api.drift.ts; \
	else \
		echo "[check-api-drift] ❌ types/api.ts 与 openapi.json 不同步，请运行 make gen-api"; \
		diff frontend/src/types/api.ts /tmp/api.drift.ts | head -40 || true; \
		rm -f /tmp/api.drift.ts; \
		exit 1; \
	fi
