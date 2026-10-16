# econpaper 本地目录整合记录

- Date: 2026-10-06
- Task ID / state file: WORKSPACE-DIRECTORY-MERGE-1 / runtime/tasks/20261006-workspace-directory-merge.md
- Git context: main@db5f5b62；未提交、未推送
- Model and tool environment: Codex；implementer 与只读 validator；本机 Python 3.12 两个已有环境
- Dataset class: 上游公开 Card 样例，不含用户原始数据
- Task: 源码、研究配套与证据统一到一个真实项目目录
- Result: pass
- Verification commands: python3 scripts/check_workspace_layout.py；make verify-deps；agent/.venv/bin/python -m pytest agent/tests/test_upstream.py -q；make docs-check；python3 scripts/check_docs.py --changed main
- Output evidence locations: .local/workspace-merge/；docs/acceptance/workspace-directory-merge.md

## 成功动作

迁移前记录文件哈希、软链接及依赖 Git 状态。真实移动完整目录，更新两个环境的
editable 路径与来源元数据，不重新安装或变更依赖。独立核验 6729 项。
backend 与 agent 经产品 OLS 入口复算，公开样例的样本量、列数与系数前后完全相同。

## 失败动作与根因

初版验收错误地在 agent 环境导入 backend 的 FastAPI 数据加载模块，该环境不包含
Web 依赖。按环境职责修正：backend 走实际 Card 加载入口，两环境走产品估计入口；
本地估计检查使用临时认证密钥，不读取或改动真实凭据。修正后先捕获基线再迁移。

## 可复现条件

保留本机迁移清单，再运行验收程序。两项文档检查通过，4 份既有冻结超长文档仍为警告。
网页全流程与镜像构建不在此次已运行验证中。

## 候选模式

整合本地源码依赖时同时核对配置默认值、editable 定位文件、来源元数据、容器上下文
和实际估计结果；文件移动成功本身不足以证明运行路径保持。
