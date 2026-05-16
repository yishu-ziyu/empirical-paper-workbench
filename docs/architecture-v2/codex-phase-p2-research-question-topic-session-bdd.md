# P2-R BDD：ResearchQuestion / TopicSession 持久化

## 背景

P2-Q 已把首页改为“先输入或选择研究选题，再进入研究判断”。但当前选题只保存在前端 `localStorage` / 页面状态里，不能跨设备恢复，也不能作为 SupervisorPlan、变量候选、DesignSpec 和 RunPlan 的共同审计上下文。

P2-R 的目标是新增后端 `ResearchQuestion / TopicSession` 状态机：用户确认选题后，系统把它保存成 `state/product/research_question.json`，但不直接改写变量角色、研究设计或执行计划。

## 行为 1：读取当前研究选题状态

**Given** 项目存在 `paper.yaml` 或 registry 中的初始研究问题  
**When** 前端或下一轮 Agent 请求当前研究选题  
**Then** API 返回一个 `ResearchQuestion` 草稿对象，包含题目文本、来源、证据等级、状态文件路径和是否已经持久化。

业务规则：项目 seed 题目可以作为“已有选题”显示，但在用户确认前，它只是可复用上下文，不是本轮人工确认过的 TopicSession。

## 行为 2：确认研究选题并持久化

**Given** 用户在首页输入一个研究选题  
**When** 用户点击 `进入研究判断`  
**Then** 系统通过后端 API 保存 `state/product/research_question.json`，状态为 `confirmed`，证据等级为 `local_file`，并记录版本、来源、人工说明和 decision event。

业务规则：研究选题是正式研究状态的上游上下文，必须跨 Session 可恢复，不能只留在浏览器本地。

## 行为 3：保存选题不能改写正式研究状态

**Given** 项目可能已经有或还没有 VariableRoleSet、DesignSpec、RunPlan  
**When** 用户确认或更新研究选题  
**Then** 系统只能写入 `research_question.json`，不得自动创建或改写 `variable_roles.json`、`design_spec.json`、`run_plan.json`。

业务规则：选题是研究入口，不是自动重跑所有研究设定的按钮。变量角色、识别设计和执行计划仍需要独立人工确认。

## 行为 4：首页确认选题后使用后端状态

**Given** 首页处于 topic-first 入口  
**When** 用户确认选题  
**Then** 前端调用后端 ResearchQuestion API，刷新 overview 后显示已确认选题，并展开研究判断区。

业务规则：localStorage 只能作为页面体验 fallback，不再是 ResearchQuestion 的权威状态。

## 行为 5：overview 暴露可审计 ResearchQuestion 状态

**Given** 研究选题已经被保存  
**When** 系统请求 `/overview`  
**Then** overview 返回 `research_question_state`，工作流中的 ResearchQuestion 阶段显示为 `completed`，后续 SupervisorPlan 和研究状态可以引用同一对象。

业务规则：后续计划、变量候选和执行任务必须能绑定到同一个研究问题上下文。

## 需要确认的边界

- 本轮不做多选题管理，只维护当前项目的 current ResearchQuestion。
- 本轮不让 ResearchQuestion 自动触发 SupervisorPlan 生成。
- 本轮不自动清空或重建 VariableRoleSet、DesignSpec、RunPlan。
- 本轮不把选题写回 `paper.yaml`，只写 `state/product/research_question.json`。
