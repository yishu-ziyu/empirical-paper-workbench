# P2-C OLS Execution Adapter BDD

## 背景

P2-B 已经把 OLS、DID、IV、RDD、PSM、DML 做成 `local_file` 级方法准入目录。下一步不能继续只展示方法目录，必须让至少一个 ready 方法真正执行并留下 `local_execution` 证据。

本阶段先做最小 OLS baseline 适配器。它读取 approved RunPlan 中 `method_id=ols` 的 task、已确认 DesignSpec 的公式和本地数据集，生成可追溯的 OLS 执行结果。DID/IV/RDD/PSM/DML 不在本阶段执行。

## 行为 1：approved OLS RunPlan 生成本地执行结果

Given 项目已经确认 VariableRoleSet、DesignSpec 和 RunPlan  
And RunPlan 中存在 `method_id=ols` 的 ready baseline task  
When 用户启动 full run  
Then 系统必须生成 `Results/json/method_execution_result.json`  
And 该文件的 `evidence_level` 必须是 `local_execution`  
And `engine` 必须说明这是本地 OLS 执行适配器。

业务含义：方法目录不能停留在“看起来可执行”，至少 OLS baseline 要真的从数据跑出结果。

## 行为 2：OLS 结果必须绑定 RunPlan、数据集和公式

Given OLS 适配器执行完成  
When 前端或后端读取 run 对象  
Then run 必须暴露 `method_execution`  
And 其中必须包含 `run_plan_version`、`dataset_path`、`formula`、`method_id=ols`、`nobs` 和 treatment 系数。

业务含义：结果不是孤立数字，必须能追到哪个 RunPlan、哪份数据和哪个公式。

## 行为 3：run manifest 必须记录方法执行产物

Given full run 成功  
When 用户查看 observability manifest  
Then `run_manifest.json` 必须包含 `method_execution`  
And 指向 `Results/json/method_execution_result.json`  
And 证据等级为 `local_execution`。

业务含义：Execution 页面和后续 Findings 能把“执行轨迹”和“方法结果”连起来。

## 行为 4：unsupported 方法不能被静默执行

Given 用户手动把 RunPlan task 改成当前适配器不支持的方法，例如 `iv`  
When 用户启动 full run  
Then API 必须返回结构化错误 `unsupported_run_plan_method`  
And 不得伪造 `local_execution` 方法结果。

业务含义：DID/IV/RDD 等方法在未实现前只能展示准入状态，不能假装已经能执行。

## 行为 5：OLS 数据不足时返回结构化失败

Given RunPlan 中存在 `method_id=ols` 的 task  
And 数据集中可用于公式的数值观测不足以估计 OLS  
When 用户启动 full run  
Then API 必须返回结构化错误 `method_execution_failed`  
And 错误消息必须说明具体失败原因，例如 `not_enough_numeric_observations`  
And 不得写出 `Results/json/method_execution_result.json`。

业务含义：真实执行失败要成为可解释的产品状态，不能变成后端 500，也不能写出伪成功产物。
