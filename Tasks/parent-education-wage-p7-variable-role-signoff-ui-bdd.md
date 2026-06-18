# P7 页面签收台 BDD

## 目标

把 P6 的五项人工确认从“读报告或调 API”推进为产品页面里的签收动作。用户在页面确认 CFPS 来源、父母教育构造、hukou 角色、outcome/control 和写回边界后，系统只生成可编辑 VariableRoleSet 草稿；不写正式 `state/product/variable_roles.json`，不生成 RunPlan，不跑模型。

## 行为 1：后端给页面提供推荐确认项

Given P5 preflight 已经生成，且 P6 signoff packet 可以读取
When Product Control 请求 P6 signoff
Then 返回值必须包含五项 `recommended_decisions`，并与 P5/P6 当前建议一致

业务规则：页面不能让用户猜“该填什么”。系统应把当前建议作为可审查默认值暴露出来，但仍要求用户显式提交。

## 行为 2：React 页面展示签收表单

Given 用户打开 Product Control 主入口
When P6 signoff 状态加载完成
Then 页面必须显示五个签收输入、`确认并生成可编辑草稿` 按钮、`draft_only_no_formal_write` 边界，并且不能提供“运行模型”入口

业务规则：确认动作必须发生在产品页面，而不是要求用户理解 JSON/API；P7 仍不是模型执行阶段。

## 行为 3：完整页面签收只提升到可编辑草稿

Given 用户按推荐默认值提交五项签收
When 前端调用 P6 promote endpoint
Then API 返回 `variable_role_draft_promoted_for_editing`，写入 `state/product/variable_roles_drafts.json`，但正式变量角色文件哈希不变

业务规则：P7 解决“在哪里确认、怎么确认”的用户体验问题；它不越权进入正式 VariableRoleSet，也不跑回归。

## 需要人工确认的边界

- 如果用户不接受默认 CFPS 波次或字段来源，P7 页面允许改文本，但本阶段不自动重新扫描数据。
- 如果用户把 hukou 从候选改成控制变量，仍只写草稿，不直接进入正式模型。
- 如果用户希望正式写回，需要后续单独的正式 VariableRoleSet 审批阶段。

## 禁止改动范围

- 不写 `state/product/variable_roles.json`。
- 不写 `state/product/design_spec.json`。
- 不写 `state/product/run_plan.json`。
- 不创建 run id。
- 不调用 StatsPAI/Stata/Python 回归执行器。
