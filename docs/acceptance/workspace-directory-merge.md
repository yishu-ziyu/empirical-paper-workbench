# 验收契约：三个本地目录统一管理

Status: closed

## Change

只保留一个项目入口 `empirical-paper-workbench/`；原论文工作区放到
`research/`，原验收证据放到 `evidence/`。已有开发环境仍能加载源码依赖并执行估计。

## Not this

不以软链接冒充迁移，不删除研究材料，不将材料或证据加入 Git 或 Docker 构建上下文；
不提交、不推送、不覆盖原有本地提交和临时页面，不改写历史评审结论。

## Evaluator

主代理运行迁移前后真实依赖加载与 Card 估计；独立只读 validator 按此契约核对。
迁移前文件清单与验收结果保存在 `.local/workspace-merge/`，不进入 Git。

## Checks

- [x] C1 `python3 scripts/check_workspace_layout.py` 成功：两个旧目录消失，真实目录位于本项目 `research/`、`evidence/`。
- [x] C2 同一程序逐文件核对迁移前 SHA256、相对软链接和 StatsPAI 分支/改动；只更新研究工作区的 README、AGENTS，原文保存在本机证据目录。
- [x] C3 同一程序在 backend、agent 两个已有环境中确认依赖源码来自新位置；backend 经产品 Card 加载入口取数据，两个环境经产品 OLS 入口得到与迁移前相同的样本数及系数。
- [x] C4 `make verify-deps`、现有依赖路径测试、`make docs-check`、`python3 scripts/check_docs.py --changed main` 成功；绝对路径和原有相对配置覆盖行为保持。
- [x] C5 验收程序确认 `research/`、`evidence/` 被 Git 和 Docker 忽略；原有 HEAD 与临时页面不变。
- [x] C6 独立 validator 判 ACCEPT；主代理阅读最终 diff，交付唯一入口与实际验证结果。

## Evidence

2026-10-06 闭环。主代理与独立 validator 均执行相同验收程序，结果一致。

- `.local/workspace-merge/manifest.json`：迁移前 6729 项清单、原分支及临时页哈希、基线估计；`before-check.log` 按预期因旧目录仍存在退出 1。
- `.local/workspace-merge/result.json`：`passed=true`，6729 项完整；两环境均为 3010 行、34 列，OLS 引擎 `statspai.feols`，系数 `0.07400899420057198`，迁移前后完全一致。
- `make verify-deps` 通过；依赖路径测试先红（2 failed）后绿（6 passed）；原有绝对、相对、含空格配置边界通过。
- 实施者运行相关数据路径/诚实性测试共 21 项、Card 研究入口与九列边界测试 19 项，均通过；主代理与 validator 独立重跑依赖路径 6 项。
- 两项文档检查、`git diff --check` 通过；仅原有 4 份冻结超长历史文档警告。StatsPAI `git fsck --no-dangling` 通过。
- validator 判 ACCEPT。主代理核对最终 diff：复用已有依赖路径规则，没有新增运行时依赖或抽象；历史评审文件不变。
- 主项目仍为 `main@db5f5b62`，原有 5 个本地提交及临时页保持；未提交、未推送。合并后目录约 3.0 GiB。

网页全流程与 Docker 镜像构建未运行；本次验收范围为目录管理、内容保存及受影响的实际源码加载和估计路径。

## Named relaxations

无。仅验证本次目录整理影响的加载、估计与管理路径，不改变网页功能；服务未运行时不宣称网页端全流程通过。
