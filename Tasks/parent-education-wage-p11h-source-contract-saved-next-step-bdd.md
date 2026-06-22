# P11H Source Contract Saved Next-Step BDD

## SDD

P11H 的目标是补齐 P11-Human 签收后的产品闭环：当 source contract 已经保存到 editable draft，页面不能继续像“还在填写缺口”一样含糊，也不能暗示已经可以跑模型。它必须把下一步从 P11 清楚交给 P9。

设计原则：

- 签收成功后先显示结论，而不是继续让用户猜当前状态。
- 结论必须说清楚“P11 已签收，只解锁 P9 正式变量表保存”。
- 页面必须继续显示禁止越级边界：不能进 P12、不能创建 run id、不能跑模型。
- 签收前的 review queue 和 source contract form 仍保留，方便用户复核和修正。

## BDD

### 行为 1：P11 保存成功后显示签收完成结论

Given 用户已经补齐 dataset path、9 个字段来源、reviewer、note 和确认码
When P11 source contract POST 返回 `source_metadata_contract_ready_for_p9_save`
Then React P11 工作台显示 `P11 已签收`
And 显示 `已解锁 P9 正式变量表保存`
And 显示保存的 dataset path

验证的业务规则：用户完成 P11 后必须知道自己完成了什么，而不是继续面对一个长表单。

### 行为 2：P11 完成后下一步只允许回到 P9

Given P11 已经签收完成
When 用户查看 P11 工作台
Then 页面显示 `下一步：回到 P9 正式保存`
And 不显示运行模型入口
And 不暗示 P12 已经可以直接开始

验证的业务规则：P11 只把 source contract 补齐，不能越级进入方法规格或模型执行。

### 行为 3：签收完成态仍保留禁止越级边界

Given P11 source contract 已经保存
When 用户查看完成态面板
Then 页面显示 `仍不能进入 P12`
And 显示 `仍不能创建 run id`
And 显示 `仍不能运行模型`

验证的业务规则：即便 P11 完成，正式变量表、DesignSpec 和 RunPlan 的后续门禁仍然有效。

## 边界条件

- P11H 不自动点击 P9 保存。
- P11H 不写正式 VariableRoleSet。
- P11H 不写 DesignSpec 或 RunPlan。
- P11H 不创建 run id，不执行模型。
- P11H 不替用户判断 CFPS 波次、父母教育构造或字段口径是否学术上最终成立。
