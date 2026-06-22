# P11G Source Contract Signoff Workspace BDD

## SDD

P11G 的目标是把 P11-Human 从“后台状态列表里的长表单”整理成一个本科生可以实际操作的签收工作台。它不替用户完成真实 source contract，不保存正式 VariableRoleSet，不进入 P12，也不跑模型。

设计原则：

- 当前任务必须一眼可见：补齐 source contract，回到 P9。
- 审核队列和编辑表单要形成一个工作台，而不是上下堆叠的日志块。
- 保存按钮和 no-model 边界要固定在签收区域底部，避免用户滚动后丢失当前动作。
- 移动端改为单列步骤，不允许页面级横向溢出。

## BDD

### 行为 1：P11 显示签收工作台而不是普通长表单

Given 用户进入 Product Control 当前门禁
When P11 source metadata contract 需要人工补齐
Then 页面展示 `Source Contract Signoff` 工作台
And 工作台展示当前状态、已确认字段数、缺口数和 P9 返回条件

验证的业务规则：用户先理解当前要完成什么，再开始填写字段。

### 行为 2：审核队列和编辑表单双栏组织

Given P11 有 9 个 required source fields
When 用户查看 P11G 工作台
Then 左侧或上方显示 `Review queue`
And 右侧或下方显示 `Source contract form`
And 队列项仍显示 status、missing 和 action

验证的业务规则：队列负责判断，表单负责编辑，两者不要混成一坨状态文本。

### 行为 3：保存动作固定在工作台底部

Given 用户滚动查看字段来源行
When source contract 仍有缺口
Then `Save source contract` 保持 disabled
And 粘性 action bar 显示 no-model 边界和当前 readiness

验证的业务规则：用户不会误以为 P11G 已经批准正式保存或可以跑模型。

### 行为 4：P11G 不越过 P11-Human/P9/P12

Given 用户查看或编辑 P11G 工作台
When 真实 source contract 尚未保存
Then P9 仍应阻断
And P11G 不写正式 VariableRoleSet，不写 DesignSpec/RunPlan，不创建 run id，不执行模型

验证的业务规则：P11G 是 UI/UX 收束，不是审批越权。

## 边界条件

- P11G 不决定 CFPS 波次。
- P11G 不决定 `parent_education` 最终构造口径。
- P11G 不提供“一键全部确认”。
- P11G 不自动提交 P11 source contract。
- P11G 不改 P11/P9 后端契约。
