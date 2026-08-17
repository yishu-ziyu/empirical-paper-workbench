# econpaper

> 网页端实证论文工作台：上传数据 → 设定方向 → 识别与稳健 → 逐章写 → 导出

**econpaper 是这个工作区唯一的产品，当前做网页端。** 上传真实数据集（CSV/CHARLS），设定研究方向，跑识别与稳健，再逐章写成文。输出 LaTeX / PDF / Word 和可复现的分析代码。

## 核心功能

- **对话式论文生成**：上传 CSV → 设定方向 → 逐章生成 → 导出论文，全程无需写代码
- **章节式交互**：6 章标准论文结构（引言、文献综述、数据描述、实证方法、实证结果、结论），每章暂停等你审阅
- **HITL 评审**：AI 自动 5 维评审（内生性、识别策略、稳健性、贡献、可读性）+ 人工决策
- **多格式导出**：LaTeX（4 套模板）/ PDF / Word / 分析代码（Python / Stata / R / EViews）
- **CHARLS 原生支持**：自动检测 CHARLS 数据集，提供变量名映射向导
- **8 步数据清洗**：profiling → 合并 → 缺失值 → 异常值 → 变量构造 → 筛选 → 平衡性 → 留痕

## 快速开始

### 前置要求

- **Python 3.12**（项目锁定版本）。系统默认 `python3` 可能是 3.14，在 3.14 下 numpy 需源码编译、pydantic 与 typing-extensions 冲突，依赖装不上。请确保有 `python3.12`（如没有：`brew install python@3.12` 或 `pyenv install 3.12`）。Makefile 用 `PY ?= python3.12`，可用 `make install PY=python3.12` 覆盖。
- `StatsPAI`、`stata-code` 需与 `econpaper/` 同级目录（`make install` 自动 `pip install -e`）。

### 开发环境

```bash
# 1. 装依赖（一次性）
make install

# 2. 启动开发服务器
make dev
```

启动后：
- **前端**：<http://localhost:5173>
- **后端 API**：<http://localhost:8000>
- **API 文档**：<http://localhost:8000/docs>

```bash
# 3. 验证
make verify
```

### Docker 部署（生产环境）

```bash
# 1. 从模板创建环境变量文件并编辑
cp .env.docker .env
# 编辑 .env：至少设置 LLM_API_KEY 和 JWT_SECRET_KEY

# 2. 构建并启动
make docker-up

# 3. 访问
# 前端：http://localhost
# API 文档：http://localhost/docs
```

## 技术栈

| 层 | 技术 |
|------|------|
| 前端 | Vite + React 18 + TypeScript + Tailwind + tremor + motion |
| 后端 | FastAPI + uvicorn（reload 模式）|
| Agent 框架 | LangGraph（Hybrid 架构） + PostgresSaver |
| 计量引擎 | StatsPAI（38 种方法统一入口 `sp.causal.<method>()`）|
| 代码翻译 | stata-code（Python → Stata / R / EViews）|
| 排版 | LaTeX + Pandoc（一键转 Word）|
| 数据库 | PostgreSQL 16+（checkpoint 持久化）|

## 项目结构

```
econpaper/
├── frontend/         # Vite + React 18 前端应用
│   ├── src/
│   │   ├── components/   # UI 组件（三栏布局、编辑器、向导等）
│   │   ├── lib/          # WebSocket 客户端
│   │   └── types/        # OpenAPI 生成的类型定义
│   └── ...
├── backend/          # FastAPI + uvicorn 后端服务
│   ├── routers/        # 11 个路由模块
│   ├── schemas/        # Pydantic 响应模型
│   ├── services/       # 业务逻辑
│   └── facade.py       # AgentFacade（路由层与 Agent 层的契约边界）
├── agent/            # LangGraph graph 定义 + 13 个节点实现
│   ├── nodes/          # upload_data, clean_data, generate_chapter 等
│   ├── cleaning/       # 8 步数据清洗流程
│   ├── prompts/        # 6 章模板 prompt
│   ├── llm/            # LLM 路由（多提供商支持）
│   └── templates/      # 4 套 LaTeX 模板
└── docs/             # 文档
    ├── api/            # API 文档（OpenAPI 规范 + 端点说明）
    ├── adr/            # 架构决策记录（7 个 ADR）
    ├── specs/          # 产品规格
    ├── user-guide.md   # 用户手册
    └── deployment.md   # 部署文档
```

## 文档

| 文档 | 说明 |
|------|------|
| [API 文档](docs/api/README.md) | 完整端点列表、请求/响应格式、WebSocket 协议、curl 示例 |
| [用户手册](docs/user-guide.md) | 快速开始教程、功能导览、FAQ |
| [部署文档](docs/deployment.md) | 环境要求、安装步骤、配置表、故障排查 |
| [OpenAPI 规范](docs/api/openapi.json) | OpenAPI 3.1 完整规范（25 个端点） |
| [架构决策记录](docs/adr/) | 7 个 ADR 覆盖关键设计决策 |

## 开发命令

| 命令 | 作用 |
|------|------|
| `make dev` | 并发起 frontend + backend |
| `make install` | 装齐所有依赖 |
| `make verify` | 三件套冒烟检查 |
| `make smoke-agent` | Agent graph 可 import 验证 |
| `make health` | 后端 /health 端点检查 |
| `make test` | 运行测试套件 |
| `make clean` | 清空依赖和缓存 |
| `make gen-api` | 导出 OpenAPI schema + 生成前端类型 |
| `make docker-up` | Docker Compose 构建并启动 |
| `make docker-down` | Docker Compose 停止服务 |
| `make docker-logs` | 查看容器实时日志 |
| `make docker-ps` | 查看容器状态 |
| `make docker-clean` | 清理所有 Docker 资源（含数据卷） |

## 上游依赖

| 仓库 | 说明 |
|------|------|
| [StatsPAI](https://github.com/yishu-ziyu/StatsPAI) | 38 种计量方法统一入口（private fork） |
| [AERS](https://github.com/yishu-ziyu/Auto-Empirical-Research-Skills) | prompt/skill 库（不 pip install） |
| [stata-code](https://github.com/yishu-ziyu/stata-code) | Python → Stata/R/EViews 代码翻译引擎 |

需与 `econpaper/` 同级目录，`make install` 自动 pip install -e。

## 当前状态

- **产品身份**：一个网页产品。旧两仓说法作废（ADR-0010）。
- **主路径**：上传数据 → 设定方向 → 清洗 → 识别验真 → 文献 → 估计 / 设定表 → 稳健性 → 6 章写作 + 评审 → 导出。
- **Journey**：8 站；可介入 {选题, 数据, 识别, 稳健, 写作}。
- **样例**：CHARLS DID 说明在 `fixtures/charls_did/`，不是第二个产品。

## 许可

MIT