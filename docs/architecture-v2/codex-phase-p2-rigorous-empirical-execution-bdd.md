# P2-K Rigorous Empirical Execution Contract BDD

## 背景

P2-C 到 P2-E 已经让 OLS baseline 通过 `python_ols_adapter` 生成 `local_execution` 证据，并补上标准误、p 值、置信区间和 evaluator checks。用户进一步明确：具体数据分析和实证必须是严谨的，后续可使用 StatsPAI/StatsAPI、StataMCP/Stata 或 Python。

本阶段不把所有后端一次性做完，而是先把执行契约写进真实 run：当前实际执行后端是谁、数据进入估计前做过什么检查、哪些后端只是可用候选、哪些结果不能被伪装成真实执行。

## 行为 1：方法执行必须声明实证执行后端契约

Given 项目已经确认 VariableRoleSet、DesignSpec 和 RunPlan  
When 用户启动 full run  
Then `method_execution` 必须包含 `execution_contract`  
And `active_backend` 必须是本次真正执行的后端  
And `available_backends` 必须列出 `python_ols_adapter`、`statspai`、`stata_mcp` 的角色、可用状态和证据等级。

业务规则：产品不能只显示一个系数，必须告诉用户这次结果到底由哪个严谨执行通道产生。

## 行为 2：只有真实运行的后端可以标记为 local_execution

Given StatsPAI 和 StataMCP/Stata 在本机可能可用  
When 当前 RunPlan 仍由 Python OLS adapter 执行  
Then `python_ols_adapter` 可以标记为 `active_execution` 和 `local_execution`  
And `statspai`、`stata_mcp` 只能标记为候选后端  
And 不得把候选后端伪装为已经执行。

业务规则：严谨性来自可审计事实，不来自把工具名称写进页面。

## 行为 3：OLS 方法结果必须包含数据预检

Given OLS 适配器读取本地数据集和公式字段  
When 生成 method item  
Then method item 必须包含 `data_preflight`  
And 记录数据路径、必需字段、读取行数、可用数值行数、被丢弃行数和命名检查。

业务规则：StatsPAI 的边界要求先得到 analysis-ready DataFrame；当前 Python 路径也必须显式说明哪些数据被纳入估计。

## 行为 4：OLS 方法结果必须包含可复现执行说明

Given OLS 适配器成功写出方法执行产物  
When 用户或下一轮 Agent 查看该产物  
Then method item 必须包含 `reproducibility`  
And 记录 adapter、公式、数据路径、RunPlan/DesignSpec 版本、产物路径和源码入口。

业务规则：实证结果必须能被下一轮复跑、审计和迁移到 Stata/StatsPAI 后端，而不是只在页面上看过。

## 行为 5：Execution 页面必须展示后端契约和预检摘要

Given 当前 run 的 observability 包含 `method_execution.execution_contract`  
When 用户打开“实证执行”页面  
Then 方法执行面板必须展示执行后端、后端候选状态、数据预检和可复现入口  
And 缺少这些字段时必须保留空状态，不得编造。

业务规则：严谨执行契约必须进入可视化验收路径，用户不应该去翻 JSON 才知道是否严谨。

## 边界条件

- 本阶段只让 Python OLS adapter 成为 active backend。
- StatsPAI/StatsAPI 后端本阶段只做本地可用性探测和候选路径声明，不调用 `sp.regress` 或 `sp.causal`。
- StataMCP/Stata 后端本阶段只做本地可用性探测和可复现路径声明，不生成 do-file。
- 候选后端可用不等于本次已经使用；只有真实执行并写出产物的后端才允许 `evidence_level=local_execution`。
