# StatspAI Runtime Bootstrap BDD

目标：把当前项目补齐 P0-P3 runtime 底座，再安装 P5 注册层 package。

## 行为 1：目标项目能获得 P0-P3 runtime 文件

Given 目标项目缺少 `workflows/registry.json` 和 runtime scripts
When 执行 bootstrap
Then 项目根目录应出现 workflow registry、agent specs、schemas、tool adapters、orchestrator policy 和 P0-P3 校验脚本。

业务规则：第二项目必须先有 runtime 底座，P5 注册层才有挂载位置。

## 行为 2：P5 package 能安装到目标项目

Given 目标项目已具备 P0-P3 runtime 底座
When 运行 `statspai-empirical-workflow-runtime` 安装脚本
Then `.codex/skills`、`.codex/agents`、`skill_subagent_registry.json` 和两个注册层 validator 应被安装。

业务规则：迁移的不是 CHARLS 论文产物，而是可复用的 Skill/Subagent 注册能力。

## 行为 3：目标项目 preflight 能闭环

Given P0-P3 底座和 P5 注册层都已安装
When 运行 `python3 scripts/25_agent_runtime_preflight.py`
Then 它应生成 `artifacts/agent_runtime_preflight_report.md`，且状态为 PASS。

业务规则：第二项目不是“文件复制成功”就算完成，必须能被机器验收。

## 行为 4：迁移不复制 CHARLS 论文产物

Given package 来源是 CHARLS DID 项目
When 安装到实证论文项目模板
Then 不应复制 CHARLS 数据、表格、论文 PDF、`verify_repro.py` 或哈希基线。

业务规则：目标项目得到 runtime 能力，不继承 CHARLS 研究结果。

## 边界

- 模板项目没有 `verify_repro.py`，所以模板版 `reproduction_verify` 只能做 runtime 自检，不能冒充论文哈希复现。
- 目标项目已有大量历史文件和未提交改动，本次只新增 runtime 相关文件，不改论文和产品代码。
