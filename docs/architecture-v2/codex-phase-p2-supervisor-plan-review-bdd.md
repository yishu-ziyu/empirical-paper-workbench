# P2-T BDD：SupervisorPlan 人工审批状态机

## 背景

P2-S 已经让 SupervisorPlan 绑定 confirmed ResearchQuestion / TopicSession。下一步必须给这份计划增加人工审批状态机。只有用户明确 approved 的计划才允许进入后续 Agent Task Queue；rejected 或 needs_revision 都只能保留审阅记录，不能派工。

## 行为 1：没有计划时不能审批

Given 项目尚未生成 `state/product/supervisor_plan.json`
When 用户提交 approve / reject / needs_revision
Then API 必须返回 `409`
And 错误码必须是 `supervisor_plan_required`

业务含义：不能审批一份不存在的大模型计划。

## 行为 2：approve 后计划可以进入任务队列前置状态

Given SupervisorPlan 状态为 `needs_review`
When 用户提交 `approve`
Then 系统必须把 `status` 改为 `approved`
And 写入人工审阅事件、审阅备注、审阅时间
And `can_dispatch` 必须为 `true`
And `next_action.id` 必须指向创建 Agent Task Queue

业务含义：只有人工确认后的计划，才是后续派工的合法输入。

## 行为 3：reject / needs_revision 后不得派工

Given SupervisorPlan 状态为 `needs_review`
When 用户提交 `reject` 或 `needs_revision`
Then 系统必须保存审阅决定
And `can_dispatch` 必须为 `false`
And 下一步必须指向重新生成或修改计划

业务含义：不满意的计划只能沉淀为审阅记录，不能继续执行。

## 行为 4：审批不得改写正式研究状态

Given 已存在 approved VariableRoleSet、DesignSpec、RunPlan 和 confirmed ResearchQuestion
When 用户审批 SupervisorPlan
Then 这些正式研究状态文件不得发生内容变化

业务含义：审批计划只是批准计划本身，不等于批准修改研究设定。

## 行为 5：前端必须提供显式审批动作

Given 首页已有 SupervisorPlan
When 用户查看审阅台
Then 页面必须展示 approve、reject、needs_revision 三个明确动作
And 操作后刷新 SupervisorPlan
And 文案必须说明只有 approved 才能进入任务队列

业务含义：用户知道自己在批准什么，也知道批准后的后果。

## 边界

- 本轮只审批 SupervisorPlan，不创建 Agent Task Queue。
- 本轮不允许审批动作改写 ResearchQuestion、VariableRoleSet、DesignSpec 或 RunPlan。
- 本轮不默认启用本地 Codex 执行。
