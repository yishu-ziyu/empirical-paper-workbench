# P9H Formal Save Completion BDD

## SDD

目标：P9 正式变量表保存成功后，产品状态必须从“可以保存”变成“已经保存，可以进入 P12-0 设计树”。这一步不启动 P12 实现，不创建 run id，不执行模型。

## 行为 1：保存后 GET 显示已保存

Given P8 approval 有效
And P11 source contract 已完整签收
And P9 POST 已写入正式 `state/product/variable_roles.json`
When 用户或前端再次读取 P9 状态
Then P9 GET 返回 `formal_variable_roles_saved`
And `can_save_formal_variable_roles=false`
And `can_enter_design_spec_preflight=true`

验证的业务规则：已经保存的正式变量表不能继续显示为“待保存”，否则会误导用户重复操作。

## 行为 2：保存后仍不允许模型执行

Given P9 已保存正式 VariableRoleSet
When 用户查看 P9 状态
Then `can_create_run_id=false`
And `can_execute_model=false`
And boundary flags 不声明本次 GET 写入了 DesignSpec、RunPlan 或模型结果

验证的业务规则：P9 保存只打开 P12-0/P12 前置设计路径，不等于可以跑模型。

## 边界条件

- 不新增依赖。
- 不改 P9 POST 的保存规则。
- 不把 P9 saved 状态误报成 P12 已完成。
- 如果最新 draft 或 approval 与已保存正式变量表不匹配，仍按原 P9 门禁重新判断。
