# Phase P2-B BDD: 方法技能集目录

日期：2026-05-13

目标：把 CoPaper/StatsPAI 式方法体系先做成可审计的本地能力目录，而不是直接伪装已经执行 DID/IV/RDD/PSM/DML。

## 行为 1：RunPlan draft 返回方法技能集目录

Given 项目已经确认 VariableRoleSet 和 DesignSpec  
When 用户请求 `GET /api/v1/projects/{project_id}/run-plan`  
Then 响应必须包含 `method_catalog`  
And `method_catalog.evidence_level` 必须是 `local_file`  
And 目录必须列出 OLS、DID、IV、RDD、PSM、DML  

业务规则：方法技能集是本地产品契约和方法论索引，不是统计执行结果，因此不能标记为 `local_execution`。

## 行为 2：每个方法声明前置变量要求和当前状态

Given 已确认变量角色包含 outcome、treatment、controls，但没有 instruments、panel/time、running_variable  
When 系统生成方法技能集目录  
Then OLS 必须是 `ready`  
And IV 必须是 `blocked`，blocker 包含 `missing_instrument`  
And DID 必须是 `blocked`，blocker 包含 `missing_panel_time`  
And RDD 必须是 `blocked`，blocker 包含 `missing_running_variable`  

业务规则：用户不能只看到“支持 IV/RDD/DID”，必须看到为什么当前论文还不能跑这些方法。

## 行为 3：RunPlan 默认任务只包含 ready 的基准方法

Given 方法技能集目录中 OLS ready、IV/DID/RDD blocked  
When 系统生成 RunPlan draft  
Then `tasks` 默认必须只包含可执行的 `baseline_regression`  
And 该任务必须绑定 `method_id=ols`  
And 不允许把 blocked 方法加入默认执行计划  

业务规则：方法目录用于解释和规划，执行计划只放当前真的可运行的任务。

## 行为 4：前端研究设计页展示方法技能集

Given 用户打开研究设计页面  
When run plan 已读取  
Then 页面必须显示方法技能集面板  
And 用户必须能看到每个方法的中文名称、状态、前置要求、阻塞原因和 evidence_level  

业务规则：方法选择不是隐藏在 JSON 编辑框里，而是用户可读的产品决策面板。方法目录属于研究设计判断，执行页只负责执行计划和运行轨迹，避免继续拥挤。

## 边界条件

- 本阶段不执行 StatsPAI，也不生成新的回归结果。
- 本阶段不自动推荐复杂识别策略，只显示方法是否具备最低前置条件。
- 当前角色集中没有 panel/time/running_variable 的正式字段，先通过 `fixed_effects`、`cluster_by`、`instruments` 和方法专属缺口做保守判断。
- 后续真实 StatsPAI adapter 接入后，方法目录可以升级为 `local_execution` 级诊断，但本阶段仍是 `local_file`。
