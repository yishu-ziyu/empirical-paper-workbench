# P2-D Method Execution Evidence UI BDD

本轮目标：把 P2-C 生成的 `Results/json/method_execution_result.json` 从后端产物升级为用户可见的产品证据。用户在实证执行和结果审阅时，必须能直接看到本轮 OLS 使用的数据、公式、样本量、处理变量系数和证据等级。

## 行为 1：Observability 一等暴露方法执行结果

Given 项目已经完成一次 successful full run，并且 `run_manifest.json` 或 `Results/json/method_execution_result.json` 记录了 `method_execution`

When 前端读取 `GET /api/v1/projects/{project_id}/runs/{run_id}/observability`

Then API 顶层必须返回 `method_execution`，其中包含 `engine`、`artifact_path`、`evidence_level=local_execution` 和至少一个 method item。

业务规则：方法执行不是普通附件，必须和 run steps/events/gates 一样成为可观察执行证据。

## 行为 2：Execution 页面显示方法执行证据

Given 当前 run 的 observability 包含 `method_execution`

When 用户打开“实证执行”

Then 页面必须显示方法执行面板，展示 engine、method_id、formula、nobs、treatment coefficient、artifact path 和 `local_execution` 证据徽章。

业务规则：用户不应该翻 JSON 文件才知道这次回归是否真的执行。

## 行为 3：缺少方法执行结果时显示可恢复空状态

Given 某个历史 run 没有 `method_execution`

When 用户查看该 run

Then 页面必须显示“尚未生成方法执行证据”的空状态，而不是把旧 `analysis_result.json` 伪装成方法执行。

业务规则：缺证据必须显式可见，不能用漂亮文案掩盖。

## 行为 4：Results & Draft 绑定方法执行证据

Given 最新 successful full run 同时存在 `analysis_result.json` 和 `method_execution_result.json`

When 用户读取 `GET /api/v1/projects/{project_id}/results-draft`

Then FindingCard 必须包含 `method_evidence`，绑定 `method_id`、`formula`、`nobs`、`treatment_coefficient` 和方法执行产物路径。

业务规则：结果论断不仅要绑定旧分析 JSON，也要绑定真实方法执行适配器产物。

## 行为 5：FindingCard 前端显示方法证据来源

Given Results & Draft 返回的 finding 带有 `method_evidence`

When 用户打开“结果与草稿”

Then FindingCard 必须显示“方法执行证据”行，并展示方法、公式、样本量、处理变量系数和本地执行证据等级。

业务规则：用户审阅结果时，应能区分“统计结果 JSON”和“方法执行适配器证据”。

## 边界条件

- 本轮只处理 `ols` 方法执行结果的展示，不引入 DID/IV/RDD/PSM/DML 的真实估计器。
- `analysis_result.json` 仍保留标准误、p 值和草稿绑定来源；`method_execution_result.json` 先作为额外执行证据，不替代完整统计报告。
- 缺少 `method_execution` 时不阻塞旧 run 查看，但必须显示空状态。
