# econpaper

> 网页端实证论文工作台：明确研究意图 → 检查数据可行性 → 确认可执行设计 → 识别与稳健 → 逐章写作与评审 → 导出

econpaper 是这个仓库唯一的产品（[ADR-0010](docs/adr/0010-one-product-merge.md)）。用户上传真实数据集（CSV、CHARLS 等），和 Agent 一起把研究意图落成可执行的计量设计，得到可复现的估计结果，再逐章写成论文，导出 LaTeX / PDF / Word 和分析代码（Python / Stata / R / EViews）。

产品定义以 [核心产品契约](docs/product/core-product-contract.md) 为准。

## 文档目录

完整目录见 [docs/README.md](docs/README.md)。常用入口：

| 主题 | 文档 |
|---|---|
| 产品：契约、流程、术语、用户手册 | [docs/product/](docs/product/README.md) |
| 功能规格与前端交互基线 | [docs/specs/](docs/specs/README.md) |
| 后端 / Agent 行为契约 | [docs/contracts/](docs/contracts/README.md) |
| HTTP / WebSocket API | [docs/api/](docs/api/README.md) |
| 架构决策 | [docs/adr/](docs/adr/README.md) |
| 设计与动效 | [docs/design/](docs/design/README.md) |
| 本地开发与依赖 | [docs/dev/](docs/dev/README.md) |
| 部署 | [docs/deployment/](docs/deployment/README.md) |
| 验收与独立评审记录 | [docs/acceptance/](docs/acceptance/README.md) · [docs/reviews/](docs/reviews/README.md) |
| 文档怎么写、怎么同步 | [docs/conventions.md](docs/conventions.md) |

参与开发前先读 [AGENTS.md](AGENTS.md)。

## 快速开始

需要 **Python 3.12**（3.14 下 numpy / pydantic 装不上；Makefile 默认 `PY ?= python3.12`）、Node、PostgreSQL 16+。本地源码依赖 StatsPAI 的位置见 [docs/dev/dependencies.md](docs/dev/dependencies.md)。

```bash
make install   # 一次性安装前后端与 agent 依赖
make dev       # 前端 http://localhost:5173 · 后端 http://localhost:8000 · API 文档 /docs
make verify    # 冒烟检查（需要服务已运行）
```

runner 的启动前置条件见 [docs/dev/local-runner.md](docs/dev/local-runner.md)，Docker 生产部署见 [docs/deployment/](docs/deployment/README.md)。

## 开发命令

| 命令 | 作用 |
|---|---|
| `make dev` | 同时启动前端和后端 |
| `make install` | 安装全部依赖 |
| `make test` | API 漂移检查 + agent / backend / frontend 测试 |
| `make verify` | 三件套冒烟检查 |
| `make docs-check` | 文档断链、孤儿文档、超长文档检查 |
| `make gen-api` | 导出 OpenAPI 规范并生成前端类型 |
| `make smoke-agent` | 验证 Agent graph 可 import |
| `make health` | 后端 `/health` 检查 |
| `make docker-up` / `docker-down` / `docker-logs` / `docker-ps` / `docker-clean` | Docker Compose 管理 |
| `make clean` | 清空依赖和缓存 |

## 仓库结构

| 目录 | 内容 |
|---|---|
| `frontend/` | Vite + React 18 + TypeScript + Tailwind 工作台 |
| `backend/` | FastAPI 服务：`routers/`、`schemas/`、`services/`、`facade/`（路由层与 Agent 层的契约边界）、durable runner |
| `agent/` | LangGraph 图与节点：`nodes/`、`engine/`（计量）、`cleaning/`、`find_data/`、`find_lit/`、`llm/`（多模型路由）、`prompts/`、`templates/` |
| `eval/` | 可选的离线评测，不属于产品运行时 |
| `fixtures/` | 样例数据与研究设定（如 CHARLS DID） |
| `deploy/` | 部署配置 |
| `docs/` | 全部项目文档 |
| `scripts/` | 检查与运维脚本 |
| `runtime/`、`agent-learning/` | Agent 任务状态与去敏学习记录（见 AGENTS.md） |

技术栈：前端 Vite + React 18 + TypeScript + Tailwind；后端 FastAPI + uvicorn；Agent 用 LangGraph + PostgresSaver；计量引擎是 [StatsPAI](https://github.com/brycewang-stanford/StatsPAI)（统一入口 `sp.causal.<method>()`）；排版用 LaTeX + Pandoc。

## 许可

MIT
