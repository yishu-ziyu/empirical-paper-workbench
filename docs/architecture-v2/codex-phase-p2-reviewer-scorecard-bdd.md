# P2-Y Reviewer Scorecard BDD

## 背景

P2-X 已经把实证方法族变成 RunPlan 前的 checklist。下一步不是直接扩展更多执行器，而是把 AI/审稿人对结果和论文草稿的批评变成可审计产品状态：评分、理由、证据绑定、后续任务建议。

本阶段遵守一个边界：Reviewer Scorecard 可以提出 follow-up task suggestions，但不能自动写入 Agent Task Queue。任务队列仍需要人工显式接受。

## 行为用例

### 行为 1：没有 successful full run 时不能生成评分卡

Given 当前项目没有 `mode=full-run` 且 `status=succeeded` 的真实执行记录  
When 用户请求 reviewer scorecard  
Then API 返回 409 `full_run_required`  
And 不创建 `state/product/reviewer_scorecard.json`

业务规则：审稿评分必须绑定真实结果和草稿证据，不能基于空项目生成。

### 行为 2：评分卡必须覆盖五个审稿维度

Given 当前项目存在 successful full run 和 FindingCard  
When 用户生成 reviewer scorecard  
Then 评分卡包含 `novelty`、`identification_credibility`、`data_quality`、`clarity`、`policy_relevance`  
And 每个维度都包含 score、rationale、evidence、suggested_tasks  
And 评分卡声明 `reviewer_backend=deterministic_baseline` 和 `evidence_level=local_file`

业务规则：如果还没有真实 LLM reviewer 后端，允许用确定性 baseline evaluator，但必须明确证据等级，不能伪装成本地模型审稿执行。

### 行为 3：低分维度只产生后续任务建议，不自动修改任务队列

Given `identification_credibility` 分数低于 6  
When scorecard 被保存  
Then 评分卡返回 method diagnostics / robustness check 相关 suggested tasks  
And `state/product/agent_task_queue.json` 不被自动修改

业务规则：审稿意见是建议，不是派工指令。进入 Agent Task Queue 之前必须有人点击接受。

### 行为 4：Review & Export 页面默认折叠评分理由和后续任务

Given scorecard 已生成  
When Review & Export 页面渲染  
Then 页面显示五个评分摘要行  
And rationale、evidence、suggested tasks 默认放进 `查看理由与后续任务` 折叠区  
And `加入任务队列草案` 必须是显式按钮，不能自动执行

业务规则：评分卡应降低认知负担，先给用户看 5 个核心信号，细节按需展开。

## 边界

- 本阶段不实现真实 LLM reviewer 调用。
- 本阶段不执行 follow-up task。
- 本阶段不把建议任务自动写入 Agent Task Queue。
- 评分卡证据等级是 `local_file`，不是 `local_execution`。
