# 第二层 Workflow Registry

本目录是第二层入口。

第一层解决“这个 CHARLS 样例能不能跑通”。第二层解决“换一个题目时，Agent 怎么复用这套流程”。

## 文件

| 文件 | 作用 |
|---|---|
| `registry.json` | 10 步 workflow 合同 |
| `agents/*.agent.md` | 十步 Agent 规格 |
| `schemas/workflow_io.schema.json` | workflow 输入输出 schema |
| `schemas/runbook_state.schema.json` | runbook JSON 状态 schema |
| `memory_index.json` | 第二层记忆和上下文加载索引 |
| `schemas/memory_index.schema.json` | memory index schema |
| `tool_adapters.json` | 第二层工具 adapter registry |
| `schemas/tool_adapters.schema.json` | tool adapter registry schema |
| `schemas/agent_trace.schema.json` | trace JSONL 单事件 schema |
| `orchestrator_policy.json` | P3 编排器安全策略 |
| `schemas/orchestrator_policy.schema.json` | 编排器策略 schema |
| `schemas/orchestrator_run_state.schema.json` | 编排器运行状态 schema |
| `skill_subagent_registry.json` | P4 Skill / Subagent / Workflow / Adapter 注册表 |
| `schemas/skill_subagent_registry.schema.json` | P4 注册表 schema |
| `api_contract.md` | 第三层产品工作台 API contract |
| `evals/charls_agent_eval.md` | 当前 CHARLS 样例的十步 eval |
| `../scripts/20_validate_workflow_contracts.py` | 校验合同结构 |
| `../scripts/21_route_next_workflow.py` | 根据当前产物状态推荐下一步 |
| `../scripts/22_validate_agent_specs.py` | 校验十步 Agent spec |
| `../scripts/23_workflow_runbook.py` | 生成第二层本地 runbook |
| `../scripts/24_validate_runbook_api.py` | 校验 runbook JSON/API contract |
| `../scripts/25_agent_runtime_preflight.py` | 未来 hook/orchestrator 可复用的确定性 preflight |
| `../scripts/26_validate_context_strategy.py` | 校验记忆分层、加载配置和写回边界 |
| `../scripts/27_validate_tool_adapters.py` | 校验工具 adapter 和 trace 日志 |
| `../scripts/28_agent_orchestrator.py` | P3 policy-gated orchestrator |
| `../scripts/29_validate_orchestrator.py` | 校验 orchestrator 策略和运行状态 |
| `../scripts/30_test_orchestrator_negative.py` | orchestrator validator 负向测试 |
| `../scripts/31_validate_skill_subagent_registry.py` | 校验 Skill / Subagent 注册层 |
| `../scripts/32_test_skill_subagent_negative.py` | Skill / Subagent 注册层负向测试 |
| `../scripts/33_validate_plugin_package.py` | 校验 P5 plugin package，并在临时第二项目中验证可迁移 |
| `../plugins/statspai-empirical-workflow-runtime/` | P5 可迁移 plugin/package |

## 运行

```bash
python3 scripts/20_validate_workflow_contracts.py
python3 scripts/21_route_next_workflow.py
python3 scripts/22_validate_agent_specs.py
python3 scripts/23_workflow_runbook.py
python3 scripts/24_validate_runbook_api.py
python3 scripts/25_agent_runtime_preflight.py
python3 scripts/26_validate_context_strategy.py
python3 scripts/27_validate_tool_adapters.py
python3 scripts/28_agent_orchestrator.py --mode dry-run
python3 scripts/29_validate_orchestrator.py
python3 scripts/30_test_orchestrator_negative.py
python3 scripts/31_validate_skill_subagent_registry.py
python3 scripts/32_test_skill_subagent_negative.py
python3 scripts/33_validate_plugin_package.py
```

## 第二层的定义

每个 workflow 都要回答：

- 这一步谁来做。
- 输入是什么。
- 必须交付什么文件。
- 用什么 Gate 验收。
- 哪些判断必须交给人。
- 失败后回退到哪里。

## 当前边界

这里还不是完整 runtime。

当前状态：

- P0 已完成：可读、可校验、可路由的工作流合同。
- P1 已完成前五步：`01_design` 到 `05_causal_analysis` 已拆成 Agent spec、统一 IO schema、失败码和 CHARLS 最小 eval。
- P2 已完成后五步：`06_writing` 到 `10_defense` 已拆成 Agent spec、失败码和 CHARLS 最小 eval。
- P3 已完成本地 runbook：`scripts/23_workflow_runbook.py` 可从当前项目状态生成 `artifacts/workflow_runbook_report.md`。
- P4 已完成 JSON/API contract：`scripts/23_workflow_runbook.py` 同步生成 `artifacts/workflow_runbook_state.json`，第三层可按 `workflows/api_contract.md` 读取状态。
- Runtime Gap P0 已完成：`scripts/25_agent_runtime_preflight.py` 把关键校验收束成一条确定性 preflight 命令。
- Runtime Gap P1 已完成：`tasks/context-loading-strategy.md` 和 `workflows/memory_index.json` 拆清常驻规则、按需 workflow、长文档参考、写回边界和未来 Skill 边界。
- Runtime Gap P2 已完成：`workflows/tool_adapters.json` 和 `artifacts/agent_trace_log.jsonl` 建立项目级工具 adapter 与最小 trace/replay 线索。
- Runtime Gap P3 已完成：`scripts/28_agent_orchestrator.py` 可按 `workflows/orchestrator_policy.json` 做 dry-run 或安全白名单执行，并写 trace/report/state。
- Runtime Gap P4 已完成：`.codex/skills/statspai-empirical-workflow/`、`.codex/agents/statspai-*.toml` 和 `workflows/skill_subagent_registry.json` 建立项目级 Skill / Subagent 注册层。
- Runtime Gap P5 已完成：`plugins/statspai-empirical-workflow-runtime/` 把注册层打包成可迁移 plugin/package，并通过临时第二项目安装验证。
- 当前第二层仍不是完整产品 runtime；它是 workflow/agent/spec/eval/API-contract/preflight/orchestrator 层。
