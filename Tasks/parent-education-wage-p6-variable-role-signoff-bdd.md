# P6 人工签收与提升路径 BDD

## 阶段目标

把 P5 的变量方案草稿变成一个人工可签收的产品步骤。系统只能整理建议，不能替用户确认研究口径；用户签收完整后，优先提升到可编辑的 `state/product/variable_roles_drafts.json` 草稿。正式 `state/product/variable_roles.json` 仍需要更强的显式授权，本阶段默认不写。

## P5 的白话解释

P5 做的是“变量方案预检”：系统根据已经找到的字段线索，整理出一份待审阅方案，说明工资用哪个字段、父母教育怎么构造、户口字段可能怎么用、控制变量有哪些。它不是正式采用，也不会跑模型。它的价值是让人知道“现在要确认什么”，而不是替人做最终决定。

## 行为用例

### 行为 1：P6 读取 P5 并生成签收包

Given P5 已经生成 `variable_role_preflight_ready_for_review`
When 用户刷新 P6 签收状态
Then 系统生成 `variable_role_signoff_required`，列出所有需要人工确认的项，并且不写正式 VariableRoleSet。

业务规则：P6 的第一步是把 P5 草案转成“待签收清单”，不是自动接受草案。

### 行为 2：签收项不完整时不能提升

Given P6 签收包存在
When 用户只确认了部分签收项
Then 系统返回 `variable_role_signoff_incomplete`，不写 `variable_roles_drafts.json`，不改 `variable_roles.json`。

业务规则：少确认任何一个关键口径，系统都不能进入可编辑变量角色草稿。

### 行为 3：完整签收后只提升到可编辑草稿

Given 用户确认了优先波次、父母教育构造、hukou 角色、outcome/control 和“只提升到草稿”
When 用户请求 promotion target 为 `editable_draft`
Then 系统写入 `state/product/variable_roles_drafts.json`，生成 pending draft，并保持正式 `variable_roles.json` 不变。

业务规则：P6 允许“进入可编辑草稿”，但不能把草稿伪装成正式变量角色。

### 行为 4：正式写入必须被单独阻断

Given 用户请求 promotion target 为 `formal_variable_roles`
When 没有显式 `allow_formal_write=true`
Then 系统返回 `formal_variable_roles_write_blocked`，并保持正式 `variable_roles.json` 不变。

业务规则：正式变量角色写回是更高风险动作，不能被 P6 的普通签收自动触发。

### 行为 5：Product API 暴露 P6 状态和提升动作

Given 项目已登记到 Product API
When 前端 GET P6 状态或 POST 刷新 P6
Then GET 不隐式生成，POST 生成签收包，promotion endpoint 只在完整签收时写草稿。

业务规则：产品面要能看见签收状态，并且写入动作必须显式调用。

### 行为 6：React 产品控制面展示 P6，但不提供绕过确认的模型执行

Given React 主入口显示 Product Control
When P6 状态存在或缺失
Then 页面展示 P6 人工签收、待确认项数、promotion target、formal write=false 和刷新按钮，不出现“跑模型”入口。

业务规则：用户能看懂下一步是“确认变量口径”，而不是被引导去直接跑回归。

## 需要用户确认的边界

- 优先 CFPS 波次是否固定为 P4 当前推荐来源。
- `parent_education` 是否采用 `max(father_education, mother_education)`，还是 mean 或父母分别进入模型。
- `hukou` 是控制变量、异质性变量，还是只保留为候选。
- outcome 是否使用 `ln_wage`，controls 是否保留 `age/female/urban/edu_last/experience`。
- 何时允许从可编辑 draft 写入正式 `state/product/variable_roles.json`。

## 不允许改动的范围

- 不执行回归，不创建 run id。
- 不写正式 `state/product/design_spec.json` 或 `state/product/run_plan.json`。
- 未获得更强授权前，不覆盖正式 `state/product/variable_roles.json`。
- 不移动、复制或修改原始 CFPS 数据文件。
