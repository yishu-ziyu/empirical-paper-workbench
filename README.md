# econpaper

> 中文原生 + 极致章节交互 + LaTeX/Word 兼容的经济学论文 AI 协作工具

Web SaaS 产品。用户上传真实数据集（CHARLS/CFPS/CGSS 或 CSV/Excel/JSON/Parquet），通过 LangGraph 编排的 Agent 章节式生成实证论文，每章暂停等用户反馈，最终输出 LaTeX 源码 + Pandoc 转换的 Word + 可复现的 Python/Stata/R/EViews 代码。

完整设计见 [docs/specs/copaper-pivot-v1.md](docs/specs/copaper-pivot-v1.md)。

## 仓库结构

```
econpaper/
├── frontend/      # Vite + React 18 + react-router + Tailwind + tremor + motion
├── backend/       # FastAPI + uvicorn + LangGraph
├── agent/         # LangGraph graph 定义 + 节点实现
└── docs/          # spec + ADRs
```

上游依赖（workspace 同级目录，editable install）：

- `../StatsPAI/` — 38 种计量方法统一入口 `sp.causal.<method>()`
- `../Auto-Empirical-Research-Skills/` (AERS) — prompt/skill 库（不 pip install）
- `../stata-code/` — Python → Stata/R/EViews 代码翻译引擎

## 启动开发环境

### 1. 装依赖（一次性）

```bash
make install
```

等价于：

```bash
# frontend
cd frontend && npm install

# backend (含上游 editable 包)
cd backend && python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
pip install -e ../StatsPAI
pip install -e ../stata-code  # 若存在 setup.py / pyproject.toml

# agent
cd agent && python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
```

> **注意**：上游 `StatsPAI` / `stata-code` 仓库需已 clone 到 `/Users/mahaoxuan/Desktop/经济学论文/` 同级目录。Python 需 ≥ 3.10（numpy 2.1 要求）。

### 2. 起开发服务器

```bash
make dev
```

后台并发起：

- **Frontend** — Vite dev server，<http://localhost:5173>
- **Backend** — FastAPI uvicorn (reload 模式)，<http://localhost:8000>

单独起某一个：

```bash
make dev-frontend
make dev-backend
```

### 3. 验证

```bash
# backend 健康检查
curl http://localhost:8000/health
# 期望：{"status":"ok"}

# agent graph 冒烟测试
make smoke-agent
# 期望：graph ok: <_Graph object at ...>

# 一键全栈验证
make verify
```

## 常用命令

| 命令 | 作用 |
|---|---|
| `make dev` | 并发起 frontend + backend |
| `make install` | 装齐 frontend + backend + agent 依赖 |
| `make verify` | 三件套冒烟检查 |
| `make smoke-agent` | agent graph 可 import 验证 |
| `make health` | backend /health 端点 |
| `make test` | 跑测试套件（占位） |
| `make clean` | 清 node_modules / .venv / __pycache__ |

## 开发约定

- **Agent 框架**：LangGraph（Hybrid 架构），graph 编排 + 节点内 ReAct loop
- **HITL**：LangGraph `interrupt()` + `Command(resume=...)`
- **Checkpointer**：开发 `InMemorySaver`，生产 `PostgresSaver`
- **测试 seam**：graph 整体行为（pytest）+ 前端三栏交互（Playwright + Vitest）
- **提交前**：`make verify` 必须 all green

## 状态

- **当前 ticket**：T-01 Workspace bootstrap（本 README + Makefile 即其交付物之一）
- **下一步**：T-02..T-11 tracer-bullet tickets，见 [.scratch/copaper-pivot-v1/issues/](.scratch/copaper-pivot-v1/issues/)

## 上游贡献策略

StatsPAI / AERS / stata-code 三仓 private fork，**不 push 回上游**，仅本地加中文扩展 skill。同步上游走本地 rebase，不破坏 fork commit history。
