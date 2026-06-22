# P5 VariableRoleSet Draft Preflight BDD

## 目标

把 P4 的真实 CFPS 字段来源候选转成可人工签收的 VariableRoleSet draft preflight。P5 只生成审阅层草案和人工决策清单，不覆盖正式 `state/product/variable_roles.json`，不写 DesignSpec，不写 RunPlan，不创建 run id，不执行回归。

## 资源调研结论

- P4 真实输入：`Results/json/parent_education_wage_p4_field_source_candidates.json`，已发现 `father_education`、`mother_education` 候选，`parent_education` 可构造但需人工确认。
- P1-B/P2 补充输入：`Results/json/parent_education_wage_data_field_binding_ledger.json` 与 `Results/json/parent_education_wage_p2_execution_readiness.json`，提供 outcome、control、sample 和既有阻断原因。
- 正式层边界：`state/product/variable_roles.json` 当前仍是旧 training/wage 示例，P5 不能直接覆盖；`state/product/design_spec.json` 和 `state/product/run_plan.json` 也不能写。
- 用户第一体验：P5 仍服务最终 `paper_draft.pdf / .docx`，但本阶段优先解除“变量角色不可审阅”的结构性阻断。

## 行为 1：P5 消费 P4 候选并生成变量角色草案预检

Given P4 字段来源候选中存在 `father_education`、`mother_education` 和 `hukou` 候选
When 运行 P5 VariableRoleSet draft preflight
Then 输出必须包含 source candidate、preferred candidate、evidence level 和 source path
And 状态为 `variable_role_preflight_ready_for_review`

业务规则：P5 不是重新扫数据，而是把 P4 的候选整理成用户可审阅的变量角色草案。

## 行为 2：父母教育只能进入构造草案

Given `father_education` 和 `mother_education` 均有候选
When 生成 `parent_education` treatment 草案
Then `parent_education` 的构造口径必须标记为 `requires_human_confirmation`
And 默认建议可以是 `max(father_education, mother_education)`，但不能自动成为正式变量

业务规则：字段存在不等于口径已确认，父母教育构造必须保留人工签收点。

## 行为 3：P5 不能写正式状态或执行模型

Given 项目中可能已有正式 `state/product/variable_roles.json`
When 运行 P5
Then 正式 VariableRoleSet、DesignSpec、RunPlan 内容不能改变
And `run_id` 必须为 null
And `executed_regression` 必须为 false

业务规则：P5 只是 preflight，不允许跳过人工确认直接进入正式研究状态。

## 行为 4：Product Control API 的 GET/POST 边界清楚

Given P5 产物尚不存在
When 调用 GET `/product-control/p5-variable-role-preflight`
Then 只能返回 missing 状态
When 调用 POST `/product-control/p5-variable-role-preflight`
Then 才生成 P5 JSON/Review 产物

业务规则：GET 不做隐式写入，POST 才是显式刷新。

## 行为 5：React 主入口展示 P5 审阅状态

Given P5 API 可读
When 打开当前 React 产品控制面
Then 页面必须展示 `P5 VariableRoleSet`、`parent_education`、`requires_human_confirmation` 和刷新按钮
And 不提供一键写正式 VariableRoleSet 的按钮

业务规则：用户在主产品入口看到下一步人工签收任务，而不是被带去旧 UI 或隐藏状态文件。

## 需要人工确认但不阻断本阶段的问题

- 采用哪个 CFPS 波次作为首版工资/父母教育分析样本。
- `parent_education` 用 `max`、`mean`，还是父母教育分别进入模型。
- `hukou` 是控制变量、异质性分组，还是暂不进入模型。
- `ln_wage` 与 `wage` 的优先 outcome 口径。
- P5 草案何时由人工动作 promote 到正式 `state/product/variable_roles.json`。
