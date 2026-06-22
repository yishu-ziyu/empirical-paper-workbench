# P11 Source Metadata Completion Path BDD

目标：把 P9 缺失的 dataset path 和字段来源补齐成可人工确认的 source contract。P11 只更新最新 editable draft 的 `source_contract`，让 P9 可以重新判断是否允许正式保存 VariableRoleSet；P11 自己不写正式变量表，不进入 DesignSpec，不创建 run id，不跑模型。

## 行为 1：P11 GET 展示待补 source contract

Given 真实项目已经有 P7 editable draft 和 P8 approval
And P9 返回 `blocked_missing_dataset_source_metadata`
When 用户打开 Product Control
Then P11 必须显示 `Source Metadata`
And 显示需要补齐的 dataset path 和角色字段
And 显示 `ln_wage`、`parent_education`、`age`、`female`、`urban`、`edu_last`、`experience`
And 显示补齐前不能保存正式变量表、不能进入 DesignSpec、不能创建 run id、不能跑模型。

业务规则：用户要知道“该补什么”，而不是看到一个抽象的 source metadata 报错。

## 行为 2：P11 POST 不完整 source contract 仍阻断

Given 用户提交的 source contract 缺 dataset path 或字段来源
When 系统处理 P11 POST
Then 返回 `source_metadata_contract_incomplete`
And 不写正式 `state/product/variable_roles.json`
And 不写 `state/product/design_spec.json`
And 不写 `state/product/run_plan.json`
And P9 仍返回 `blocked_missing_dataset_source_metadata`。

业务规则：补证动作必须有审计字段，不能用空字段或弱绑定绕过 P9。

## 行为 3：P11 POST 完整 source contract 只解锁 P9

Given dataset path 存在于项目内
And 所有 approved role fields 都有 `dataset_column`、`source_path`、`evidence_level`
And 派生变量 `parent_education` 有 construction 和 source fields
When 用户保存 P11 source contract
Then P11 返回 `source_metadata_contract_ready_for_p9_save`
And 最新 editable draft 写入 `source_contract.status=complete`
And P9 GET 变成 `formal_variable_role_save_ready`
And 正式 VariableRoleSet 仍未写入，DesignSpec/RunPlan 仍未写入，run id 仍未创建。

业务规则：P11 是 P9 的补证前置，不是正式保存或模型执行。

## 行为 4：React 页面提供 P11 补证入口且无模型入口

Given P9 被 source metadata 阻断
When 用户查看 Product Control 当前门禁详情
Then 页面必须显示 P11 source metadata 表单
And 用户能填写 dataset path、字段来源、evidence level 和 parent_education construction
And 页面必须保留 `不写正式 VariableRoleSet；不写 DesignSpec；不写 RunPlan；不跑模型`
And 页面不能出现 `运行模型` 操作。

业务规则：P11 必须把“怎么确认”做成产品路径，而不是让用户猜该改哪个 JSON 文件。

## 边界

- P11 不创建或复制原始数据。
- P11 不把 P4/P5 候选自动提升为正式字段来源。
- P11 不写正式 VariableRoleSet；只更新 latest editable draft 的 `source_contract`。
- P11 不写 DesignSpec、RunPlan，不创建 run id，不执行模型。
