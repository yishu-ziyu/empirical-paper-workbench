# P1-I Results & Draft Evidence Binding BDD

## 背景

P1-H 已经把主链路推进到真实 full run：

`Dataset -> VariableRoleSet -> DesignSpec -> RunPlan -> Run -> Results -> Draft -> Review/Export`

当前缺口不是继续运行，而是把 full-run 产物变成用户可审阅的研究对象：

- `FindingCard`：可写入论文的结果论断，必须绑定 run、RunPlan、结果 JSON 和证据等级。
- `DraftSection`：生成草稿的章节入口，必须绑定草稿文件、run、结果证据和文件证据。

本轮只做最小闭环，不扩展完整 Manuscript 编辑器、Artifacts 页面或 Agent 控制台。

## 行为 1：没有成功 full run 时 Results & Draft 不得伪造结果

Given 项目没有任何 `mode=full-run` 且 `status=succeeded` 的 run  
When 前端或客户端请求 Results & Draft evidence binding  
Then 后端返回 409 `full_run_required`  
And 响应不得返回 mock finding  
And 响应说明下一步应先启动完整实证执行

业务规则：结果页不能用 mock 结果顶替真实执行产物；没有成功 full run 就必须明确阻断。

## 行为 2：成功 full run 后必须生成最小 FindingCard

Given 项目存在成功的 full run  
And `Results/json/analysis_result.json` 包含 StatsPAI workflow result payload  
And run manifest 绑定了 `run_plan_binding`  
When 请求 Results & Draft evidence binding  
Then 后端返回最新 full run 的 `run_id`  
And 返回至少一个 FindingCard  
And FindingCard 包含 treatment coefficient、standard error、p value、sample size、model type  
And FindingCard 绑定 `run_id`、`run_plan_version`、`artifact_path=Results/json/analysis_result.json`  
And FindingCard 的 `evidence_level` 为 `local_execution`

业务规则：结果论断必须来自真实执行轨迹，而不是草稿文本或静态文件名。

## 行为 3：DraftSection 必须同时显示文件证据和结果证据

Given full run 已生成 `Manuscripts/generated/paper_draft.md`  
And 草稿中的章节来自本地生成文件  
When 请求 Results & Draft evidence binding  
Then 后端返回 draft sections  
And 每个 DraftSection 包含 `source_path`、`source_evidence_level=local_file`  
And 每个 DraftSection 绑定 `run_id`、`artifact_path`、`claim_evidence_level=local_execution`

业务规则：草稿文件本身是本地文件证据，但草稿中的结论必须追溯到 full-run 结果证据。

## 行为 4：前端 Results & Draft 必须显示 FindingCard 和 Draft evidence binding

Given Results & Draft API 返回 findings 和 draft sections  
When 用户打开 Results & Draft 工作区  
Then 页面显示 FindingCard 列表  
And 页面显示 DraftSection 证据绑定列表  
And UI 可见 `local_execution` 与 `local_file` 两类证据等级  
And UI 可见 run_id、RunPlan version、artifact path

业务规则：用户不应只看到“草稿文件可用”，而要能看到哪些论断来自哪次执行和哪些文件。

## 边界条件

- 本轮只读取最新成功 full run，不做 run comparison。
- 本轮只生成 baseline treatment finding，不自动生成异质性、机制或稳健性 finding。
- 本轮不判断 finding 是否可以直接写入终稿；claim review 留到后续 Results/Review 阶段。
- 本轮不实际调用 Feynman CLI；只继承 P1-H 的 callable external research engine provenance。
