# P1-J Claim Review / Accept-for-writing BDD

日期：2026-05-13

## 背景

P1-I 已经让 Results & Draft 从成功 full-run 中生成最小 FindingCard，并把 FindingCard 绑定到 `Results/json/analysis_result.json`、`run_id`、`run_plan_version` 和 `evidence_level=local_execution`。

下一步不能直接把 finding 写入论文正文。按照 CoPaper / StatsPAI / Feynman-style 研究工作流，自动执行结果必须先进入 review layer：用户确认该论断是否可以进入正文、是否需要修改、或是否拒绝。

本阶段只实现最小审阅状态，不实现完整论文编辑器。

## 行为 1：未审阅 FindingCard 默认不能写入正文

Given 项目已有成功 full-run  
And `Results/json/analysis_result.json` 能生成 FindingCard  
When 用户打开 Results & Draft  
Then FindingCard 的 `review_status` 为 `needs_review`  
And `can_write_to_draft=false`  
And 页面必须显示它仍需审阅

业务规则：真实执行结果不是论文论断本身，必须经过人工审阅后才能进入正文。

## 行为 2：用户 approve 后 FindingCard 可写入正文

Given Results & Draft 返回一个 FindingCard  
When 用户对该 FindingCard 提交 `action=approve` 和 note  
Then 后端把审阅决定持久化到项目状态  
And 再次读取 Results & Draft 时该 FindingCard 的 `review_status=approved`  
And `can_write_to_draft=true`  
And 审阅记录包含 `actor=user`、`evidence_level=local_file`、`run_id`、`artifact_path`

业务规则：approve 是用户本地决策证据，不是模型自动生成证据，所以 evidence_level 是 `local_file`。

## 行为 3：reject / needs_revision 不允许写入正文

Given Results & Draft 返回一个 FindingCard  
When 用户提交 `action=reject` 或 `action=needs_revision`  
Then 后端保存该审阅决定  
And 再次读取 Results & Draft 时 `can_write_to_draft=false`  
And 页面显示拒绝或需修改原因

业务规则：拒绝和待修改状态必须保留历史，不应删除原始 finding 或伪装为通过。

## 行为 4：非法 finding 或非法 action 必须被拒绝

Given 用户提交 claim review  
When `finding_id` 不属于当前 latest successful full-run  
Then API 返回 404 `finding_not_found`  
When action 不是 `approve`、`reject`、`needs_revision`  
Then API 返回 400 `invalid_review_action`

业务规则：用户只能审阅真实存在且可追溯的 finding；状态枚举必须稳定，否则后续 Draft/Review/Export 无法可靠判断。

## 行为 5：前端 FindingCard 必须提供 claim review 操作

Given Results & Draft 页面显示 FindingCard  
When FindingCard 处于任意 review 状态  
Then 页面显示 `approve`、`needs_revision`、`reject` 三类操作  
And 用户提交后调用 claim review API  
And 成功后刷新 Results & Draft evidence binding  
And 页面显示 `review_status`、`can_write_to_draft`、note 和 evidence_level

业务规则：Agent 聊天不能替代审阅动作；审阅必须绑定到具体 FindingCard。

## 边界条件

- 本阶段只保存当前 latest successful full-run 的 FindingCard review，不做跨 run comparison。
- 本阶段不自动修改 `paper_draft.md`，只暴露 `can_write_to_draft` 状态，后续 Manuscript 阶段再消费。
- 本阶段把用户审阅状态保存为项目本地状态文件；是否提交到 git 后续单独决定。
- Feynman 目前仍作为 callable external research engine provenance，不把 Feynman 源码嵌入本项目。
