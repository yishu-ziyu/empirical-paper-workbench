# P1-H Full Run From RunPlan BDD

## 背景

产品主链路已经形成：

`Dataset -> VariableRoleSet -> DesignSpec -> RunPlan -> Run -> Results -> Draft -> Review/Export`

当前 `workflow_contract.next_action.id=start_full_run` 只说明前置状态已满足，不代表完整实证执行已经接通。本轮要把 full run 从开发试运行中分离出来：完整执行必须读取 approved `RunPlan`，并在 run 证据中绑定 VariableRoleSet、DesignSpec、RunPlan provenance。

Feynman 参考原则：

- 不嵌入 Feynman 源码。
- 短期把 Feynman 当作可调用外部研究引擎的设计参考。
- 源码层面吸收 provider、skill、workflow provenance 的结构思路。
- run metadata 明确记录 `embedded=false`，避免把外部研究引擎伪装成内置实现。

## 行为 1：缺少 approved RunPlan 时禁止 full run

Given 项目还没有 approved RunPlan

When 用户请求启动完整实证执行

Then API 返回 409

And 错误码为 `run_plan_required`

And 不创建新的 run

业务规则：完整执行必须以用户确认过的 RunPlan 为入口，不能绕过研究设计状态机。

## 行为 2：full run 必须读取 approved RunPlan 并创建可观察执行

Given VariableRoleSet、DesignSpec、RunPlan 均已 approved

When 用户启动完整实证执行

Then 系统创建 mode=`full-run` 的 run

And 调用本地 pipeline 生成 observable run 文件

And run response 包含 `plan_binding`

And `plan_binding.evidence_level=local_file`

And run 的执行证据等级为 `local_execution`

业务规则：RunPlan 是 Execution 的输入契约，真实执行轨迹是 Execution 的证据。

## 行为 3：run manifest 必须绑定研究计划 provenance

Given full run 已经完成

When 用户读取 run manifest 或 observability

Then manifest 包含 `run_plan_binding`

And 其中包含 `variable_role_set_version`、`design_spec_version`、`run_plan_version`、`dataset_path`

And manifest 包含 `research_engine`

And `research_engine.embedded=false`

And `research_engine.integration_mode=callable_external`

业务规则：借鉴 Feynman 的 workflow/provenance 设计，但不把 Feynman 源码嵌进项目。

## 行为 4：前端必须把 full run 作为 ready 后的主行动

Given `workflow_contract.run_readiness.can_start_full_run=true`

When 用户进入 Execution 页面

Then preflight 显示“启动完整实证执行”按钮

And 按钮调用 full run API

And 成功后刷新 run selector 和 observability

业务规则：用户看到的主行动应来自研究生命周期，而不是开发用 dry-run 捷径。

## 本轮边界

- 本轮不扩展 Findings / Manuscript / Artifacts / Agents 页面。
- 本轮不 fork 或复制 Feynman 源码。
- 本轮继续复用现有 `Program/run_paper.py` 本地 pipeline；Feynman 只进入 metadata 和后续 provider/skill 设计方向。
- full run 的产物必须标记为 `local_execution`，RunPlan/DesignSpec/VariableRoleSet 等输入契约标记为 `local_file`。
