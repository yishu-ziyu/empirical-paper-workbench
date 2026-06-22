# Product Control P0 Phase BDD

目标：把 P0-A/B/C/D 当作一个连续阶段包推进。P0-A 的 topic binding 是上游门禁，P0-B 生成当前项目的 Agent Queue，P0-C 审计证据状态，P0-D 输出作品集验收包。

## 行为 1：P0-B 必须从项目 topic binding 生成 Agent Queue

Given `state/product/topic_binding.json` 已确认当前项目题目
When 运行 P0-B
Then 系统必须写出 approved `state/product/supervisor_plan.json`
And 写出 `state/product/agent_task_queue.json`
And Agent Queue 必须包含 6 个任务：ResearchBriefAgent、DataAgent、VariableAgent、MethodAgent、ExecutionAgent、EvidenceAuditAgent。

业务规则：Agent Queue 是当前项目的任务组织层，不得复用旧题目的运行态。

## 行为 2：P0-B 不能把当前任务直接变成执行授权

Given P0-B 已生成 Agent Queue
When 用户查看任务
Then 每个任务默认仍需 dispatch review
And `can_execute` 必须为 false。

业务规则：P0-B 只是让用户理解和审阅分工，不等于真实执行。

## 行为 3：P0-C 必须把证据状态说清楚

Given P0-A topic audit 通过且 P0-B Queue 已生成
When 运行 P0-C
Then 系统必须写出 `Results/json/product_control_demo_evidence_audit.json`
And 写出 `Reviews/product_control_demo_evidence_audit.md`
And 报告必须区分已具备的 local_file 证据、待补真实文献、待确认数据变量、待执行结果和正式层边界。

业务规则：Evidence Audit 不是假装已经完成研究，而是明确哪些证据已经有、哪些还没有。

## 行为 4：P0-D 必须生成可讲述的作品集包

Given P0-A/B/C 已完成
When 运行 P0-D
Then 系统必须写出 `docs/product-control/07_作品集Demo脚本.md`
And 写出作品集 package JSON/Review
And 文档必须包含 3 分钟讲述、流程图、Agent 分工图、证据链状态和下一步路线。

业务规则：P0 的阶段目标是让产品能被验收和讲清楚，不只是后端状态通过。

## 行为 5：P0 阶段必须能从产品 API 触发

Given 项目已经注册到 Product registry
When 调用 `POST /api/v1/projects/{project_id}/product-control/p0-phase`
Then 系统必须按该 project_id 的真实项目目录运行 P0-A/B/C/D
And 返回同一份 P0 阶段报告、项目身份和作品集产物路径。

业务规则：P0 不应只停留在终端脚本，而要成为产品层可复用的阶段能力。

## 行为 6：P0 阶段能力必须支持其他题目

Given 项目 topic binding 换成另一个实证题目
When 运行 P0-B/C/D
Then 输出中的 topic、slug、路径和 Agent Queue 输入都必须来自该项目 topic binding，而不是固定父母教育工资。

业务规则：父母教育工资是当前验收线，不是最终产品能力的硬编码边界。
