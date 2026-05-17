# P2-X Method Workflow Checklist BDD

目标：把 OLS / DID / IV / RDD / PSM / DML 从“可点击方法名”升级为“带前置条件、诊断要求和执行阻断规则的方法工作流”。

## 行为 1：OLS 在结果变量与处理变量存在时可预检执行

Given 用户已经确认变量角色，并且 DesignSpec 中存在 outcome 与 treatment  
When 前端或后端读取 method workflows  
Then OLS 的 readiness_status 必须是 ready  
And OLS 必须声明 required_inputs 包含 outcome 与 treatment  
And OLS 必须声明 required_diagnostics 包含 sample_size、missingness、coefficient_table、residual_diagnostics

业务规则：OLS 可以作为最小 baseline，但仍然不能只显示“可运行”，必须提前声明运行后要产出的诊断证据。

## 行为 2：DID 缺少时间变量和处理时点时必须阻塞

Given 用户已经确认 outcome 与 treatment，但没有确认 panel time 或 treatment timing  
When 系统读取 method workflows  
Then DID 的 readiness_status 必须是 blocked  
And blockers 必须包含 time_variable_required 与 treatment_timing_required  
And DID 必须声明 required_diagnostics 包含 parallel_trends、event_study、sensitivity_analysis、heterogeneous_treatment_effects

业务规则：DID 不是 OLS 的一个按钮。缺少面板时间与处理时点时，它不能进入 RunPlan。

## 行为 3：IV 缺少工具变量时必须阻塞

Given 用户没有确认 instruments  
When 系统读取 method workflows  
Then IV 的 readiness_status 必须是 blocked  
And blockers 必须包含 instrument_required  
And IV 必须声明 required_diagnostics 包含 first_stage、weak_instrument_test、overidentification_test、exclusion_restriction_review

业务规则：工具变量方法必须先通过变量与识别假设的前置检查，不能只因为模型字段写了 iv 就执行。

## 行为 4：被阻塞方法不能被批准进入 RunPlan

Given DID 方法仍然 blocked  
When 用户尝试保存包含 DID task 的 RunPlan  
Then API 必须返回 409  
And error.code 必须是 method_workflow_blocked  
And 已批准 RunPlan 不得被写入 state/product/run_plan.json

业务规则：方法工作流是执行前的硬门禁，避免系统把缺证据的方法包装成正式执行计划。

## 行为 5：前端必须默认折叠方法要求

Given 用户进入研究设计或实证执行页面  
When 页面展示 method workflows  
Then 页面必须直接显示 OLS、DID、IV、RDD、PSM、DML 的状态摘要  
And 详细 required_inputs / required_diagnostics / blockers 必须放入“查看方法要求”折叠区  

业务规则：用户第一眼只需要知道“哪些能做、哪些缺什么”，细节必须可追溯但不能默认冲爆屏幕。
