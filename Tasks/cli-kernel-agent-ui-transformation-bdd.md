# CLI Kernel -> Agent -> UI Transformation BDD

日期：2026-06-19

## 背景

本轮改造不继续优化旧看板视觉。目标是把第一层已经证明过的 CLI 论文生产流程，作为第二层 Agent 和第三层 UI 的唯一能力内核。

验收标准从“页面展示了很多状态”改成：

```text
题目 + 数据集
-> CLI / pipeline 产出论文、表图、证据、复现和质量报告
-> Agent 只负责调度、审阅和修订队列
-> UI 只消费 headless 状态、动作和产物
```

## 行为 1：Workflow 不能再生成 mock 研究笔记

Given 用户创建一个论文生产 workflow
When workflow 被启动并推进
Then 系统应生成 10 个 CHARLS-like pipeline 节点，而不是“占位研究员笔记”。

业务规则：第二层 Agent 的任务单位必须对应论文生产链路，包括 ResearchIntent、Literature、Data、Method、Execution、Robustness、Manuscript、Reviewer、Replication、Export。

## 行为 2：Workflow 产物必须声明真实证据边界

Given workflow 节点尚未调用真实统计或写作执行器
When 节点生成 artifact
Then artifact 的 evidence_level 应是 `pipeline_contract`，并明确不能提升为正式论文、结果或提交包。

业务规则：未执行真实 CLI 的节点只能作为调度契约，不能冒充可交付成果。

## 行为 3：Headless 状态必须暴露论文审阅状态

Given PDF 导出样稿已经存在
When UI 读取 headless-state
Then 响应中必须包含 `course_paper_quality` 组件，显示是否达到课程论文级、缺哪些门、下一步动作是什么。

业务规则：PDF 文件存在不等于论文完成。UI 后续怎么设计都必须能看到论文审阅状态，而不是只看到“PDF ready”。

## 行为 4：论文审阅必须能绑定当前 PDF 的真实 Markdown 来源

Given final-pdf manifest 记录了 `source_markdown`
When 系统生成论文审阅报告
Then 它应使用该 Markdown 草稿作为输入，并把 quality report 写入 `Results/json/course_paper_quality_report.json`。

业务规则：论文审阅不能误读旧的 synthetic draft 或无关 `paper_quality_report.json`。

## 行为 5：UI 组件只消费业务契约

Given 设计师未来要重画第三层 UI
When UI 调用 headless-state
Then 每个组件只依赖 `component_id`、`status`、`user_summary`、`primary_action`、`blockers`、`artifacts`、`evidence` 和 `audit`，不依赖 P 阶段布局或旧看板结构。

业务规则：第三层 UI 必须和业务能力解耦，旧的 P 阶段调试语言只能作为开发审计，不进入默认用户体验。

## 边界条件

- 本轮不重写视觉设计。
- 本轮不把固定父母教育 demo 声称为任意题目通用能力。
- 本轮不把 PDF 导出样稿提升为课程论文级成果，除非论文审阅完成。
- 本轮允许保留旧 P0-P18 API，但新 UI/Agent 应优先消费 headless 和 pipeline 契约。
