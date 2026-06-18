# Runtime Gap P1: Context Loading Strategy

目标：让第二层 workflow 具备可控记忆。Agent 每次开始任务时，先知道该加载什么、该跳过什么、该把新经验写到哪里。

## 结论

本项目采用“少量常驻 + 按需加载 + 明确写回”的记忆结构。

不是把所有文档塞进上下文。

## 记忆分层

| 层级 | 类型 | 位置 | 加载时机 | 写回规则 |
|---|---|---|---|---|
| 系统/组织规则 | 指令型记忆 | 系统提示、根级规则 | 每轮常驻 | 项目不能覆盖 |
| 项目规则 | 指令型记忆 | `AGENTS.md`、`tasks/agent-loop.md` | 每轮常驻 | 只写稳定规则 |
| 流水线合同 | 程序记忆 | `tasks/pipeline-contract.md`、`workflows/registry.json` | 做十步流水线时加载 | 合同变更要同步 schema/校验 |
| Agent 规格 | 程序记忆 | `workflows/agents/*.agent.md` | 只加载当前步骤对应文件 | 由第二层 spec 维护 |
| 项目状态 | 情景记忆 | `tasks/todo.md`、`artifacts/*_report.md` | 每轮读任务清单；报告按需读 | 完成后写证据和风险 |
| 领域证据 | 语义记忆 | `litreview/`、`artifacts/`、`templates/aers/` | 按研究任务检索加载 | 不整包读 PDF，不假装已读 |
| 本地私有记忆 | 本地记忆 | `.agent-memory/local/`、`*.local` | 只在本机需要时读取 | 不进 Git，不放 cookie/密码 |
| 用户全局记忆 | 学习型记忆 | Codex/Claude memory | 任务相关时检索 | 只能作为线索，必须本地复核 |
| 角色记忆 | 子代理记忆 | 未来 `.codex/agents/` 或等价目录 | 调用对应角色时加载 | 各角色隔离，不互相污染 |

## 加载配置

| 场景 | 必读 | 按需读 | 禁止默认读 |
|---|---|---|---|
| 普通项目轮次 | `AGENTS.md`、`tasks/todo.md`、`tasks/agent-loop.md` | 最近相关 artifact | 原始数据、PDF 全文、所有历史报告 |
| 十步流水线任务 | 普通项目轮次 + `tasks/pipeline-contract.md`、`workflows/registry.json` | 当前 `workflows/agents/<step>.agent.md`、`artifacts/workflow_runbook_state.json` | 所有 Agent spec 一次性全读 |
| 文献任务 | 普通项目轮次 + `tasks/literature-workflow.md` | `litreview/query_plan.json`、候选池、贡献矩阵、相关慢读笔记 | 未解析 PDF 批量读入 |
| 论文慢读 | 当前文献 PDF/HTML 解析文本、`reading_state.md` | 对应 source spans、压缩笔记 | 只读摘要后写结论 |
| 数据门禁 | `tasks/data-workflow.md`、`artifacts/data_contract.md` | 变量字典、样本流失、面板审计、相关脚本 | 原始大数据全量读入上下文 |
| 因果分析 | `causal_question.yaml`、`model_log.md`、`robustness_report.md` | 当前模型脚本、表格、稳健性报告 | 已废弃模型口径 |
| 写作/修订 | `paper.tex`、`claim_audit.md`、`revision_plan.md` | 文献证据、模型报告、表图 notes | 只做语言美容 |
| 第三层/API | `workflows/api_contract.md`、`artifacts/workflow_runbook_state.json` | schema、runbook 报告 | 直接调用原始研究数据 |

## 写回配置

| 新信息 | 写到哪里 | 条件 |
|---|---|---|
| 稳定规则 | `AGENTS.md` 或专项策略文档 | 会长期影响所有 Agent |
| 用户纠正 | `tasks/lessons.md` | 能改善后续执行方式 |
| 当前任务进度 | `tasks/todo.md` | 已完成、阻塞、风险、下一步 |
| 校验结果 | `artifacts/*_report.md` | 脚本可复跑或人工可验收 |
| 机器状态 | `artifacts/*.json` | 第三层产品需要读取 |
| 私人路径/账号入口 | `.agent-memory/local/` 或 `*.local` | 不进 Git，不含密钥 |
| 密码、cookie、VPN 会话 | 不写入项目记忆 | 只能临时使用 |

## 上下文预算

- `AGENTS.md` 控制在 200 行以内，只放全局规则和入口。
- `tasks/agent-loop.md` 放执行纪律，不放长篇资源清单。
- `tasks/pipeline-contract.md` 是十步合同，只有流水线任务加载。
- `workflows/agents/*.agent.md` 按步骤加载，不全量常驻。
- `litreview/`、`artifacts/`、`templates/` 是检索型资料，按任务拿证据。
- PDF 和原始数据不直接常驻上下文，先解析成 span、表格或报告。

## Skill 边界

| 内容 | 现在位置 | 未来形态 |
|---|---|---|
| 十步流水线合同 | `tasks/pipeline-contract.md`、`workflows/registry.json` | `empirical-paper-workflow` Skill |
| 文献获取/慢读 | `tasks/literature-workflow.md`、`litreview/` | `literature-agent` Skill |
| 数据门禁 | `tasks/data-workflow.md`、`scripts/04_data_gate.py` | `data-gate` Skill |
| 因果识别/稳健性 | AER skills + 本地 scripts | `causal-audit` Skill |
| 写作/修订 | `revision_plan.md`、`claim_audit.md` | `paper-revision` Skill |
| 预检验收 | `scripts/25_agent_runtime_preflight.py` | Hook target |

## 验收

P1 完成标准：

- `workflows/memory_index.json` 能机器读取。
- `workflows/schemas/memory_index.schema.json` 能说明结构。
- `scripts/26_validate_context_strategy.py` 能检查 P1 关键文件、加载配置、写回配置和上下文预算。
- `scripts/25_agent_runtime_preflight.py` 包含 P1 校验。
- `tasks/todo.md` 记录完成证据。
