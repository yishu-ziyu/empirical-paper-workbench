# P12 DesignSpec Preflight BDD

## 目标

P12 把 P9 已正式保存的 VariableRoleSet 转成可审阅的方法规格预检。它只生成预检产物和候选设计建议，不写正式 `state/product/design_spec.json`，不写 RunPlan，不创建 run id，不运行模型。

## 行为用例

### 行为 1：没有正式变量表时阻断

Given 项目没有 approved `state/product/variable_roles.json`
When 用户请求 P12 DesignSpec Preflight
Then 系统返回 `blocked_missing_formal_variable_roles`，并提示先完成 P9-Human。

业务规则：P12 只能承接 P9 已正式保存的变量角色，不能从草稿或审批记录直接推导方法规格。

### 行为 2：P9 已保存后生成候选 DesignSpec

Given P9 已保存正式变量表，包含 dataset path、outcome、treatment 和 controls
When 用户运行 P12 DesignSpec Preflight
Then 系统生成候选 DesignSpec，包含研究问题、变量角色、baseline OLS 识别策略和公式。

业务规则：P12 是“规格预检”，它要让项目主导者看见下一步方法设计长什么样，而不是直接跑模型。

### 行为 3：方法清单必须区分可行与阻断

Given 正式变量表只有 outcome、treatment 和 controls，没有工具变量、面板时间或 running variable
When P12 生成方法预检
Then OLS 可预检，DID/IV/RDD 必须标记阻断原因，PSM/DML 只能作为候选预检方法，不得自动执行。

业务规则：系统必须解释为什么不能乱用 DID/IV/RDD，避免本科生把模型名当作任意按钮。

### 行为 4：P12 只写预检产物，不写正式层

Given P12 运行前正式 DesignSpec、RunPlan 状态为空或已有哈希
When 用户运行 P12 DesignSpec Preflight
Then 只允许写 `Results/json/parent_education_wage_p12_design_spec_preflight.json` 和 `Reviews/parent_education_wage_p12_design_spec_preflight.md`，正式 DesignSpec、RunPlan、run id 和模型结果不变化。

业务规则：P12 不能越过人工确认直接进入 P13/P14。

### 行为 5：API 暴露 P12 当前状态

Given 项目注册在 Product API 中
When 用户调用 `GET/POST /api/v1/projects/{project_id}/product-control/p12-design-spec-preflight`
Then GET 读取现有预检或返回可刷新状态，POST 显式生成预检，响应包含 no-model 边界。

业务规则：产品控制台必须能从 API 获取 P12 状态，不能只靠本地文件。

## 边界条件

- 不确认正式 DesignSpec。
- 不写 `state/product/design_spec.json`。
- 不写 `state/product/run_plan.json`。
- 不创建 run id。
- 不运行回归或调用 StatsPAI/Stata。
- 如果正式变量表缺 dataset path 或角色不完整，P12 必须阻断。
