# Product

本目录承载 C 版本产品骨架：

- `app.py`：FastAPI 应用入口
- `serve_product.py`：本地启动脚本
- `backend/`：项目注册表、工作区管理、运行触发
- `web/`：前端静态页面
- `state/projects.json`：已注册项目
- `workspaces/`：通过产品向导创建的新项目工作区

## Driver Principle

本产品线默认按 `Codex-only driver` 设计：

- 多代理协作由产品编排层承接
- 不把“额外接一个外部模型服务”作为系统成立前提
- 重点放在工作流编排、handoff、review loop 和可追溯产物
