# P1-F/P1-G DesignSpec 与 RunPlan 状态机 BDD

## 背景

产品主链路已经推进到：

`Dataset -> VariableRoleSet -> DesignSpec -> RunPlan -> Run -> Results -> Draft -> Review/Export`

当前 `VariableRoleSet` 已经是项目级状态对象，保存到 `state/product/variable_roles.json`。下一步不能直接进入 execution，而必须先形成可审计的 `DesignSpec` 与 `RunPlan`。

## 行为 1：DesignSpec draft 必须读取已确认 VariableRoleSet

Given 项目已经确认 `VariableRoleSet`

When 用户打开 DesignSpec API

Then 系统返回 `status=draft` 的 DesignSpec

And 其中包含 research question、outcome、treatment、controls、fixed effects、cluster_by、estimator、formula

And `evidence_level` 必须为 `local_file`

业务规则：研究设计不能重新猜变量，必须从用户确认过的 VariableRoleSet 生成 draft。

## 行为 2：保存 DesignSpec 必须写入可审计项目状态

Given 用户已经检查 draft DesignSpec

When 用户提交识别策略、模型公式、估计方法、固定效应、聚类标准误和确认说明

Then 系统写入 `state/product/design_spec.json`

And 状态为 `approved`

And 写入 `decision_events.action=confirm_design_spec`

业务规则：研究设计是论文主链路对象，不是前端表单临时值。

## 行为 3：DesignSpec approved 后 workflow_contract 必须进入 RunPlan

Given VariableRoleSet 和 DesignSpec 均已 approved

When 用户读取 `/overview`

Then `design_spec` stage 为 `completed`

And `design_unconfirmed` blocker 被移除

And `next_action.id=confirm_run_plan`

And full run 仍因 `run_plan_missing` 被阻止

业务规则：确认研究设计后仍不能直接跑完整实证，必须先确认执行计划。

## 行为 4：RunPlan draft 必须读取已确认 DesignSpec

Given DesignSpec 已经 approved

When 用户打开 RunPlan API

Then 系统返回 `status=draft` 的 RunPlan

And 至少包含 baseline regression 任务

And 每个任务绑定 DesignSpec 与 dataset

业务规则：RunPlan 是 DesignSpec 到 Execution 的桥，不是独立生成的任务列表。

## 行为 5：保存 RunPlan 后 full run 才能启动

Given DesignSpec 已 approved 且用户确认 RunPlan

When 系统写入 `state/product/run_plan.json`

Then `run_plan` stage 为 `completed`

And `run_readiness.can_start_full_run=true`

And blockers 为空

And `next_action.id=start_full_run`

业务规则：完整实证执行必须有变量角色、研究设计和执行计划三者共同支撑。

## 行为 6：前端必须提供 DesignSpec 与 RunPlan 确认表单

Given 用户进入 Data & Design 或 Execution

When VariableRoleSet 已 approved

Then Research Design 页面必须显示 DesignSpec 编辑器

And Execution 页面必须显示 RunPlan 编辑器

And 保存后必须刷新对应状态与 workflow contract

业务规则：产品主行动不再停留在 run selector，而是按研究生命周期推进。

## 本轮边界

- 本轮不执行真实回归。
- 本轮不生成 Findings、Manuscript、Artifacts。
- RunPlan 先支持 baseline regression、robustness placeholder、outputs 三类结构。
- 所有状态文件使用 `evidence_level=local_file`，真实执行仍由后续 run 产物标记为 `local_execution`。
