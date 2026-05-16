# P2-U Agent Task Queue BDD

更新时间：2026-05-17

## 目标

把已经人工批准的 `SupervisorPlan` 转换成可持久化、可审阅的 `Agent Task Queue`。队列是“派工前的产品对象”，不是自动执行器：它只能从 approved plan 派生任务摘要、owner agent、输入证据、输出要求、阻塞项和审计记录，不能直接改写 `VariableRoleSet`、`DesignSpec` 或 `RunPlan`。

## 行为用例

### 行为 1：没有 approved SupervisorPlan 时禁止创建任务队列

Given 项目还没有 `state/product/supervisor_plan.json`，或已有计划但状态仍是 `needs_review` / `needs_revision` / `rejected`  
When 用户请求创建 Agent Task Queue  
Then API 返回 409，并给出 `supervisor_plan_required` 或 `supervisor_plan_not_approved`  
And 系统不得创建 `state/product/agent_task_queue.json`

业务规则：子 Agent 派工必须经过人工审批，不能从未审计划或被退回计划直接进入执行。

### 行为 2：approved SupervisorPlan 可以生成摘要优先的任务队列

Given `SupervisorPlan.status=approved` 且 `can_dispatch=true`  
When 用户创建 Agent Task Queue  
Then 系统写入 `state/product/agent_task_queue.json`  
And 队列标记 `evidence_level=local_file`  
And 每个任务包含 `owner_agent`、`title`、`input_evidence`、`output_requirements`、`blockers`、`risk_flags` 和初始 `audit_log`  
And 队列包含 `ui_contract.summary_first=true` 与 `details_collapsed_by_default=true`

业务规则：队列来自本地已批准计划，因此是可审计的本地文件证据；前端默认只露出派工摘要，细节按需展开。

### 行为 3：GET API 可恢复已持久化队列

Given 项目已有 `state/product/agent_task_queue.json`  
When 页面刷新或新会话调用 GET API  
Then API 返回同一份任务队列及其来源 `SupervisorPlan` 版本、路径和任务摘要  
And 若尚未创建队列，GET 返回 `status=empty` 且说明下一步是否可创建

业务规则：长时间任务不能依赖聊天上下文；队列必须跨 session 恢复。

### 行为 4：创建队列不得篡改已确认研究状态

Given 已确认的 `ResearchQuestion`、`VariableRoleSet`、`DesignSpec`、`RunPlan` 和 approved `SupervisorPlan`  
When 用户创建 Agent Task Queue  
Then 这些正式研究状态文件内容保持不变  
And 只有 `state/product/agent_task_queue.json` 被新增或刷新

业务规则：Agent Task Queue 是派工层，不是研究设定写回层。

### 行为 5：前端默认显示任务摘要，详情折叠

Given 页面加载到 approved `SupervisorPlan` 和已创建的 Agent Task Queue  
When 用户停留在 Overview  
Then 页面显示任务总数、排队数、阻塞数、owner agents 和一个主操作  
And 每个任务只显示标题、owner agent、状态和阻塞摘要  
And 输入证据、输出要求、风险、审计日志默认放进 `details` 折叠区

业务规则：避免一进页面就把高噪声信息铺满屏幕，降低用户短时记忆负担。

### 行为 6：前端在未创建队列时给出明确下一步

Given `SupervisorPlan` 已 approved 但还没有 Agent Task Queue  
When 用户查看 Overview  
Then 页面显示“创建 Agent 任务队列”主按钮  
And 文案说明队列只会创建派工草案，不会自动执行或改写研究状态

业务规则：用户能清楚知道当前按钮的真实后果。

## 边界条件

- 本阶段不真正启动子 Agent 执行任务。
- 本阶段不接入 StatsPAI / StataMCP 的真实执行层。
- 本阶段不把任务结果写回变量角色、设计方案、RunPlan、Finding 或 Manuscript。
- 若 `SupervisorPlan.subagent_dispatch` 为空，创建队列应被阻断并提示 `subagent_dispatch_required`。
- 后续阶段再做“人工批准任务队列 -> 进入真实 Agent 执行队列”。
