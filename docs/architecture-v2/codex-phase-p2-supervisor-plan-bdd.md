# P2-P BDD：本地 Codex Supervisor 研究执行计划

## 背景

P2-O 已经把本地 Codex Supervisor 作为智能中控层暴露在 `workflow_contract.intelligence_layer` 中，但这还只是 provider readiness。P2-P 的目标是让本地 Codex 生成一份可持久化、可审阅的研究执行计划，同时保持产品状态边界：Supervisor 只能提出计划、风险、证据要求和子 Agent 分工，不能直接篡改已确认的 VariableRoleSet、DesignSpec 或 RunPlan。

## 行为 1：执行开关关闭时必须阻塞生成

Given 本机能检测到 Codex CLI
And `EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC` 未启用
When 用户请求生成 SupervisorPlan
Then API 必须返回 `409`
And 错误码必须说明 `local_codex_execution_not_enabled`
And 系统不得写入 `state/product/supervisor_plan.json`

业务含义：不能把“检测到 Codex”伪装成“已经由大模型生成计划”。

## 行为 2：启用本地 Codex 后必须持久化待审计划

Given VariableRoleSet、DesignSpec、RunPlan 均已 approved
And 本地 Codex 执行开关已启用
When 用户请求生成 SupervisorPlan
Then 系统必须调用本地 Codex
And 把返回计划保存到 `state/product/supervisor_plan.json`
And 计划状态必须是 `needs_review`
And 证据等级必须是 `local_execution`

业务含义：SupervisorPlan 是真实本地模型执行产物，不是前端 mock 或硬编码建议。

## 行为 3：SupervisorPlan 不得直接改写人工确认状态

Given 已存在 approved VariableRoleSet、DesignSpec、RunPlan
When 本地 Codex 生成 SupervisorPlan
Then 这三个已确认文件的内容和版本不得被修改
And SupervisorPlan 只能引用这些状态作为输入证据
And 下一步必须是人工确认或驳回计划

业务含义：LLM 是中控和审阅者，不是绕过 HITL gate 的写权限主体。

## 行为 4：首页必须展示可审阅的 SupervisorPlan

Given 项目已有 `state/product/supervisor_plan.json`
When 用户打开工作台首页
Then 智能中控面板必须展示计划状态、下一步、风险、证据要求和子 Agent 分工
And 必须提供生成计划入口
And 文案必须说明计划需要人工确认

业务含义：用户能从产品界面理解大模型中控实际做了什么，而不是只看到 provider 状态。

## 边界

- 本轮不让 Codex 直接保存 VariableRoleSet / DesignSpec / RunPlan。
- 本轮不自动派出真实子 Agent 执行清洗、建模或写作。
- 本轮不默认启用 `EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC`；本地版本必须显式打开执行开关。
