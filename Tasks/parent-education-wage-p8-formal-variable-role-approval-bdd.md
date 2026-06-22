# P8 Formal VariableRoleSet Approval BDD

## 目标

P8 把 P7 生成的可编辑变量角色草稿，推进到一个单独的正式批准门禁。P8 只记录正式变量角色保存许可；不写 DesignSpec，不写 RunPlan，不创建 run id，不跑模型。

## 行为

### 行为 1：没有 P7 draft 时不能进入 P8

Given 项目已有 P5 preflight 和 P6 signoff packet
When 用户还没有完成 P7 editable draft promotion
Then P8 API 返回 `blocked_missing_p7_variable_role_draft`
And `can_approve_formal_variable_roles=false`
And 不写 `state/product/variable_role_formal_approvals.json`

业务规则：正式变量角色批准必须基于一个可审阅草稿，不能跳过 P7。

### 行为 2：P7 draft 存在后，P8 返回待批准包

Given 用户已通过 P7 生成 `state/product/variable_roles_drafts.json`
When 页面读取 P8 状态
Then API 返回 `formal_variable_role_approval_required`
And 暴露 latest draft id、roles、source signoff/preflight 和 approval prompts
And 仍然不允许正式写入

业务规则：P8 是二次确认面，不是自动保存正式变量表。

### 行为 3：缺少审批元数据时不能批准

Given P7 draft 已存在
When 请求 P8 approve 但缺少 reviewer、note 或确认短语
Then API 返回 409
And 不写 approval file
And 不修改正式变量表

业务规则：正式批准必须可追责，不能靠空 payload 解锁。

### 行为 4：P8 approve 只解锁正式变量角色保存，不写其他正式状态

Given P7 draft 已存在
When 用户带 reviewer、note 和确认短语批准 P8
Then P8 写 `state/product/variable_role_formal_approvals.json`
And 仍不直接写 `state/product/variable_roles.json`
When 用户随后调用正式变量角色保存接口
Then `state/product/variable_roles.json` 才被写入
And `state/product/design_spec.json`、`state/product/run_plan.json` 哈希不变
And 不创建 run id、不跑模型

业务规则：P8 只给 VariableRoleSet 保存放行，不代表研究设计、运行计划或模型执行已经获批。

### 行为 5：React 产品控制台必须显示 P8 审批路径

Given P7 draft 已存在或尚未存在
When 用户打开 Product Control
Then 页面显示 P8 正式变量角色审批状态、reviewer/note/确认短语输入和批准按钮
And 文案明确“不写 RunPlan；不跑模型”

业务规则：用户必须知道自己是在批准正式变量角色保存，而不是批准模型执行。

### 行为 6：P8 approval 必须绑定审批时的 draft roles 快照

Given 用户已对某个 P7 draft 完成 P8 approval
When 最新 draft id 改变，或同一个 draft id 的 roles 在 approval 后被改动
Then 原 approval 不能继续解锁正式变量角色保存
And 正式保存接口必须返回 409
And `state/product/variable_roles.json` 保持不变

业务规则：P8 批准的是一个具体版本的变量角色草稿，不是给任意后续 roles 或被篡改草稿签空白支票。
