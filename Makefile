.PHONY: dev dev-frontend dev-backend install install-frontend install-backend install-agent health test clean gen-api check-api-drift

# 默认并发起 frontend + backend；Ctrl-C 同时杀掉
dev:
	@trap 'kill 0' INT TERM; \
	$(MAKE) dev-backend & \
	$(MAKE) dev-frontend & \
	wait

dev-frontend:
	cd frontend && npm run dev

dev-backend:
	cd backend && . .venv/bin/activate 2>/dev/null || true; \
	uvicorn main:app --reload --reload-dir . --reload-dir ../agent --host 0.0.0.0 --port 8000

# 一次性装齐所有依赖
install: install-frontend install-backend install-agent

install-frontend:
	cd frontend && npm install

install-backend:
	cd backend && python3 -m venv .venv || true; \
	. .venv/bin/activate; \
	pip install -r requirements.txt; \
	pip install -e ../StatsPAI || true; \
	pip install -e ../stata-code || true

install-agent:
	cd agent && python3 -m venv .venv || true; \
	. .venv/bin/activate; \
	pip install -r requirements.txt

# 验证 backend 健康检查
health:
	@curl -sS http://localhost:8000/health || echo "backend not running"

# 占位：测试入口（TDD seam 验证用）
test:
	@echo "tests TBD — T-01 only verifies dev servers start"

# 验证 graph 可 import（agent 冒烟测试）
smoke-agent:
	cd agent && . .venv/bin/activate && python -c "from graph import graph; print('graph ok:', graph)"

# 验证 frontend / backend / agent 三件套都活
verify: smoke-agent
	@echo "[verify] frontend port 5173"; curl -sS -o /dev/null -w "%{http_code}\n" http://localhost:5173 || echo "frontend not running"
	@echo "[verify] backend /health"; curl -sS http://localhost:8000/health || echo "backend not running"
	@echo "[verify] agent import"; cd agent && python -c "from graph import graph; print('graph ok')" || echo "agent import failed"

clean:
	rm -rf frontend/node_modules frontend/dist backend/.venv agent/.venv
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

# Stage D: 从 backend 导出 openapi.json 并生成 frontend types/api.ts
# 依赖：backend/.venv 已装、frontend/node_modules 已装
gen-api:
	@echo "[gen-api] 导出 openapi.json from backend"
	@cd backend && . .venv/bin/activate 2>/dev/null || true; \
	python3 -c "\
import json, sys; \
sys.path.insert(0, '.'); sys.path.append('../agent'); \
from main import app; \
open('../frontend/openapi.json', 'w').write(json.dumps(app.openapi(), indent=2, ensure_ascii=False)); \
print('[gen-api] openapi.json exported, schemas:', len(app.openapi().get('components', {}).get('schemas', {})))"
	@echo "[gen-api] 生成 frontend/src/types/api.ts"
	@cd frontend && npx openapi-typescript openapi.json -o src/types/api.ts
	@echo "[gen-api] done"

# 检查 types/api.ts 是否与当前 openapi.json 同步（CI gate）
# 若 drift，打印 diff 并 exit 1
check-api-drift:
	@echo "[check-api-drift] 重新生成 api.ts 到临时文件并 diff"
	@cd frontend && npx openapi-typescript openapi.json -o /tmp/api.drift.ts 2>/dev/null
	@if diff -q frontend/src/types/api.ts /tmp/api.drift.ts >/dev/null 2>&1; then \
		echo "[check-api-drift] ✅ types/api.ts 与 openapi.json 同步"; \
		rm -f /tmp/api.drift.ts; \
	else \
		echo "[check-api-drift] ❌ types/api.ts 与 openapi.json 不同步，请运行 make gen-api"; \
		diff frontend/src/types/api.ts /tmp/api.drift.ts || true; \
		rm -f /tmp/api.drift.ts; \
		exit 1; \
	fi
