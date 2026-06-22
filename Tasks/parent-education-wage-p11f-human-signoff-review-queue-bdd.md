# P11F Human Signoff Review Queue BDD

## SDD

P11F 的目标不是替用户完成真实 source contract，也不是进入 P12。目标是把 P11-Human 前的长表单变成可扫读的审核队列：用户先看到每个字段来源行的状态、缺口和确认要求，再进入逐行编辑与勾选。

业务规则：

- P11F 只改变 React 人工签收体验，不改变 P11 后端 payload。
- 每个 required source field 都必须有一个审核队列项。
- 队列项必须显示字段名、是否已确认、缺少哪些项，以及下一步动作。
- 队列项不得把预填候选当作人工确认。
- P11F 不保存 source contract，不写正式 VariableRoleSet，不写 DesignSpec/RunPlan，不创建 run id，不执行模型。

## BDD Behaviors

### 行为 1：用户先看到审核队列，而不是直接面对长表单

Given P11 source metadata 页面已经拿到 required source fields
When 用户进入 P11 Source Metadata 面板
Then 页面在逐字段编辑器前展示 `Human signoff review queue`

验证的业务规则：本科生用户应先看到“还有哪些字段要审”，而不是直接在长表单里迷路。

### 行为 2：每个字段行都有独立状态

Given P11 有 9 个 source rows
When React 渲染审核队列
Then 每个队列项都显示 field、status、missing items 和 action

验证的业务规则：签收任务必须按字段可追踪，不能只给一个总缺口字符串。

### 行为 3：行级状态不会替代人工确认

Given 某个 source row 已经预填 dataset column、source field、source path 和 evidence level
When 用户尚未勾选 row human confirmation
Then 队列项仍显示需要 human confirmation，保存按钮仍不能启用

验证的业务规则：候选值只是建议，不能等同于用户确认。

### 行为 4：正式层边界不变

Given 用户查看或编辑 P11F 审核队列
When 页面刷新、编辑字段或勾选 checkbox
Then P11F 不写正式 VariableRoleSet，不写 DesignSpec/RunPlan，不创建 run id，不执行模型

验证的业务规则：P11F 是用户体验收束，不是审批越权。

## Boundary Conditions

- P11F 不决定 CFPS 波次。
- P11F 不决定 `parent_education` 最终构造口径。
- P11F 不决定 hukou 是控制变量还是异质性变量。
- P11F 不提供“一键全部确认”。
- P11F 不自动提交 P11 source contract。
