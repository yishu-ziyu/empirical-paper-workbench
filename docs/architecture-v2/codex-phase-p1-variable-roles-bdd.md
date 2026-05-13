# Phase P1-D BDD: Variable Roles Confirmation Surface

## 背景

P1-C 已经让执行页展示 run 使用的数据文件和最小 shape。下一步要把“系统如何理解这份数据”从 step metadata 中提升到可见产品对象：outcome、treatment、controls、instruments 必须直接出现在执行页，并和 `gate_dataset_fields` 的 HITL 状态绑定。P1-D 第一轮只做变量角色展示和确认状态，不做完整变量编辑器。

## 行为用例

### 行为 1：observability API 暴露变量角色理解

Given run 的 `dataset_intake` step metadata 包含 `key_variables`  
When 前端请求 run observability  
Then response 顶层必须包含 `variable_roles`  
And `variable_roles.evidence_level` 必须是 `local_execution`  
And `variable_roles.roles` 必须包含 outcome、treatment、controls、instruments。

业务规则：变量角色是本次执行的数据理解结果，不应只藏在 step JSON 里。

### 行为 2：变量角色绑定 HITL gate 状态

Given run 有 `gate_dataset_fields`  
When 读取 observability  
Then `variable_roles.confirmation_gate_id` 必须指向该 gate  
And `variable_roles.confirmation_status` 必须反映 gate 的 open/resolved 状态。

业务规则：系统识别变量后，用户必须知道是否已经人工确认。

### 行为 3：执行页展示变量角色确认面板

Given observability response 包含 `variable_roles`  
When 用户进入实证执行页  
Then 页面显示 outcome、treatment、controls、instruments  
And 显示确认状态与 evidence badge。

业务规则：用户需要在同一个执行页看到“数据文件”和“变量理解”，才能决定是否通过 HITL gate。

### 行为 4：缺少变量角色时不伪造

Given 历史 run 没有 `variable_roles`  
When 页面渲染变量角色面板  
Then 页面显示“未记录变量角色”  
And 不应从当前配置静默补齐历史 run。

业务规则：缺失证据必须显式暴露，不能用当前配置覆盖历史运行。

## 边界条件

- P1-D 第一轮不做变量编辑和写回，只做展示与 gate 状态绑定。
- 若用户要调整变量角色，仍通过现有 `adjust` gate action 记录意图；后续再补结构化变量修改 API。
- 变量角色证据等级使用 `local_execution`，因为它来自本次 run 的执行轨迹，而不是单纯本地文件存在性。
