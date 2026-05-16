# P2-S BDD：SupervisorPlan 绑定已确认 ResearchQuestion / TopicSession

## 背景

P2-R 已把首页确认的选题保存为 `state/product/research_question.json`。P2-S 的目标是让本地 Codex Supervisor 生成计划时消费这份已确认研究上下文，而不是只读取 VariableRoleSet、DesignSpec、RunPlan。SupervisorPlan 仍然只能提出计划、风险、证据要求和子 Agent 分工，不得直接改写正式研究状态。

## 行为 1：没有已确认选题时必须阻塞 SupervisorPlan

Given 项目已有 approved VariableRoleSet、DesignSpec、RunPlan
And `state/product/research_question.json` 不存在或状态不是 `confirmed`
When 用户请求生成 SupervisorPlan
Then API 必须返回 `409`
And 错误码必须是 `research_question_required`
And 系统不得写入 `state/product/supervisor_plan.json`

业务含义：Supervisor 不能围绕一个未确认研究问题生成后续执行计划。

## 行为 2：SupervisorPlan 必须记录输入选题版本和 TopicSession

Given ResearchQuestion 已 confirmed
And VariableRoleSet、DesignSpec、RunPlan 均已 approved
When 本地 Codex 生成 SupervisorPlan
Then SupervisorPlan 必须包含 `input_research_question`
And 其中必须记录 question、version、topic_session_id、evidence_level、path
And `input_state_versions` 必须包含 `research_question_version`
And `input_evidence` 必须包含 `research_question_path`

业务含义：下一轮任务队列和人工审批能追溯这份计划到底基于哪一个选题。

## 行为 3：本地 Codex Prompt 必须携带已确认选题

Given ResearchQuestion 已 confirmed
When 系统调用本地 Codex 生成 SupervisorPlan
Then 传给 Codex 的 prompt 必须包含 `confirmed_research_question`
And 必须包含 `topic_session_id`
And 必须继续声明不可改写 VariableRoleSet、DesignSpec、RunPlan

业务含义：大模型中控不是凭项目名泛泛规划，而是围绕用户确认的研究问题工作。

## 行为 4：首页审阅台必须显示计划绑定的选题上下文

Given SupervisorPlan 已生成并绑定 TopicSession
When 用户打开首页 SupervisorPlan 审阅台
Then 默认摘要应显示绑定选题
And 展开详情后能看到 TopicSession 和 ResearchQuestion 版本
And 页面仍需提示人工确认后才允许派工

业务含义：用户先看到计划为什么存在、围绕什么问题规划，再决定是否展开高噪声细节。

## 边界

- 本轮不实现 SupervisorPlan approve/reject/needs_revision API。
- 本轮不把 SupervisorPlan 拆成真实 Agent Task Queue。
- 本轮不允许 Codex 自动修改 ResearchQuestion、VariableRoleSet、DesignSpec 或 RunPlan。
