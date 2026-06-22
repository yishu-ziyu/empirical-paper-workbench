# P9 Formal VariableRoleSet Save BDD

## 目标

P9 把 P8 已批准的变量角色草稿推进到正式 `VariableRoleSet` 保存路径。P9 不是模型执行入口；它只在 roles、dataset path 和 source metadata 同时满足保存合同后写入正式变量角色表。

## 行为

### 行为 1：没有 P8 approval 时不能进入正式保存

Given 用户已通过 P7 生成 editable draft
When P8 approval 还不存在或已失效
Then P9 返回 `blocked_missing_p8_formal_approval`
And `can_save_formal_variable_roles=false`
And 不修改 `state/product/variable_roles.json`

业务规则：P7 草稿不是正式保存授权。

### 行为 2：P8 approval 存在但 source metadata 不完整时仍不能保存

Given P8 approval 已记录
When 最新 draft 缺少 dataset path 或 roles 所需字段的 source metadata
Then P9 返回 `blocked_missing_dataset_source_metadata`
And 明确列出缺失字段
And 不允许进入 DesignSpec preflight

业务规则：正式变量表必须绑定可审计数据来源，不能只保存变量名。

### 行为 3：保存动作需要独立确认

Given P8 approval 有效且 source metadata 完整
When P9 POST 缺 reviewer、note 或确认短语
Then API 返回 409
And 不写正式变量表
And 不写 DesignSpec、RunPlan 或 run id

业务规则：正式保存是单独人工动作，不能被页面刷新或空 payload 触发。

### 行为 4：正式保存只能使用 P8 批准的 draft 和 source contract

Given P8 approval 有效且 source metadata 完整
When 用户确认 P9 save
Then P9 写入 `state/product/variable_roles.json`
And roles 等于 P8 approval 的 `source_draft_roles`
And dataset/source metadata 等于最新 draft 的 source contract
And `state/product/design_spec.json`、`state/product/run_plan.json` 哈希不变
And 不创建 run id、不跑模型

业务规则：P9 只把已批准草稿提升为正式变量角色表，不顺带批准研究设计或执行。

### 行为 5：payload 不能替换 roles 或 dataset

Given P8 approval 有效且 source metadata 完整
When P9 POST payload 试图提交不同 roles 或 dataset path
Then API 返回 409
And 正式变量表保持不变

业务规则：P9 不是一个绕过 P8 的自由编辑口；修改变量或数据后必须回到草稿和审批流程。

### 行为 6：React 产品控制台必须展示 P9 保存路径

Given 用户打开 Product Control
When P9 状态读取完成
Then 页面显示正式保存状态、dataset/source metadata 缺口、保存确认输入和保存按钮
And 文案明确“不写 DesignSpec；不写 RunPlan；不跑模型”

业务规则：用户要看到当前能不能正式保存，以及为什么不能保存。
