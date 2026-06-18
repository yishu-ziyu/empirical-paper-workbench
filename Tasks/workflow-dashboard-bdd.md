# Workflow Dashboard BDD

## SDD

目标：在项目文件夹内提供一个可通过本地服务动态更新的中文工作流仪表盘，用来持续提醒当前开发处于哪一步、设计树开到了哪一支、当前阻断点是什么、下一步应该走哪个门禁。

这个仪表盘不是正式产品 UI，不替代 React 主入口；它是项目管理和开发过程控制面，给项目主导者和后续 Agent 使用。

## 行为 1：显示中文开发阶段

Given 项目正在按 `追问 -> 调研 -> 原型 -> 规格 -> 拆任务 -> 实现 -> 复核` 推进
When 用户打开工作流仪表盘
Then 页面展示这 7 个阶段
And 标出当前阶段为 `规格 / 复核`
And 标出下一阶段为 `P13 / RunPlan Approval`

验证的业务规则：开发者不会忘记 P12 预检只是可审阅草案，下一步仍必须进入 P13 人工批准。

## 行为 2：显示老板能一眼看懂的经营摘要

Given 老板或项目主导者第一次打开仪表盘
When 页面首屏加载完成
Then 页面必须显示 `老板先看这里`
And 显示项目目标为 `给本科生交付可审计的论文初稿`
And 显示当前结论为 `P9 已正式保存，P12 DesignSpec 预检已生成`
And 显示需要老板判断的事项为 `是否把 P12 预检提升为正式 DesignSpec 审阅入口`
And 显示下一步为 `P13 RunPlan Approval 前的人工作业`

验证的业务规则：仪表盘必须先回答管理问题，而不是先抛给老板一堆开发术语。

## 行为 3：显示当前项目 gate 和阻断点

Given 当前项目已完成 P9-Human
And P12-0 设计树已写入项目文档
And P12 DesignSpec 预检 JSON 与 Review 已生成
When 用户查看工作流仪表盘
Then 页面显示当前门禁为 `P12 DesignSpec 预检已生成`
And 显示当前阻断为 `等待人工审阅 P12 预检并进入 P13 RunPlan Approval`
And 显示 P14 模型执行仍暂停

验证的业务规则：仪表盘必须反映真实阶段，不把 P12 预检草案误报成正式 DesignSpec、RunPlan、run id 或模型执行。

## 行为 4：显示 P12-P16 设计树分支

Given 后续阶段不是一条直线
When 用户查看工作流仪表盘
Then 页面显示 DesignSpec 预检、RunPlan 审批、模型执行证据账本、初稿导出、用户验收的分支关系
And 标出回退路径：方法口径或任务拆分不清时回到 P12-0
And 标出禁止路径：不能直接从 P12/P13 跳到运行编号或模型执行

验证的业务规则：团队看到的是设计树，而不是单线程 todo。

## 行为 5：显示人工验收清单

Given 每个阶段完成后都需要人类验收
When 用户查看工作流仪表盘
Then 页面显示人工验收清单
And 清单包含打开页面、当前面板、预检产物、禁止入口、截图证据

验证的业务规则：Review 阶段必须给人类明确验收动作，而不是只说测试通过。

## 行为 6：从机器可读状态源动态渲染

Given 项目状态写在 `docs/product-control/workflow-dashboard-state.json`
When 用户通过仪表盘页面查看状态
Then 页面必须包含状态源 endpoint、轮询逻辑和 `renderDashboardState` 渲染函数
And 当前阶段、阻断点、分支树和 QA 清单必须由状态源字段渲染，而不是只能手改 HTML 文案

验证的业务规则：仪表盘必须从单一状态源更新，避免 `WORKFLOW_STATUS.md`、任务清单和 HTML 三处手工同步造成漂移。

## 行为 7：通过本地 FastAPI 提供实时入口

Given 用户启动本项目 FastAPI 服务
When 用户访问 `/workflow-dashboard` 和 `/api/v1/workflow-dashboard/state`
Then `/workflow-dashboard` 返回仪表盘 HTML
And `/api/v1/workflow-dashboard/state` 返回当前 dashboard JSON
And 响应禁用缓存，避免浏览器显示旧状态

验证的业务规则：动态仪表盘应该有一个稳定 localhost 入口，不能只依赖 file:// 打开静态文件。

## 边界条件

- 仪表盘不需要新依赖。
- 仪表盘不自动改写 `WORKFLOW_STATUS.md`。
- 仪表盘不替代 `WORKFLOW_STATUS.md`，而是通过 `workflow-dashboard-state.json` 把当前关键状态可视化。
- 如果后续阶段状态变化，必须同步更新 `WORKFLOW_STATUS.md`、`Tasks/todo.md` 和 `workflow-dashboard-state.json`；HTML 应从 JSON 动态读取。
- 真正 push 式 WebSocket/SSE 暂不做；当前实时性采用短轮询。
