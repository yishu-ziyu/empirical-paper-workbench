# Product Control P0 Stage Panel BDD

目标：把 P0 阶段包从本地 JSON/API 产物变成用户能在产品首页读取、刷新和据此决策的控制面板。

## 行为 1：GET 接口必须只读返回已有 P0 阶段报告

Given 注册项目目录中已经存在 `Results/json/product_control_p0_phase.json`
When 调用 `GET /api/v1/projects/{project_id}/product-control/p0-phase`
Then 系统必须返回该报告
And 不重新生成 SupervisorPlan、Agent Queue、Evidence Audit 或作品集包。

业务规则：读取状态和刷新状态必须分开，避免用户只是查看页面就改写阶段产物。

## 行为 2：没有 P0 报告时必须显式提示需要生成

Given 注册项目目录中不存在 `Results/json/product_control_p0_phase.json`
When 调用只读 GET 接口或打开首页控制面板
Then 系统必须返回/展示 `p0_phase_report_missing`
And 提供刷新 P0 阶段包的动作。

业务规则：缺状态不是静默失败，也不能伪造已完成。

## 行为 3：首页必须展示 P0 阶段核心状态

Given P0 阶段报告存在
When 用户进入工作台首页
Then 页面必须展示 topic、P0 状态、Agent 任务数量、Evidence Audit 状态和作品集脚本路径。

业务规则：用户要先理解项目状态，再决定是否进入文献、数据或方法执行。

## 行为 4：首页必须暴露证据缺口和正式层边界

Given Evidence Audit 中存在 `needs_evidence`
When 首页渲染 P0 控制面板
Then 每个 `needs_evidence` 检查都必须可见
And 页面必须显示“不能进入正式论文”的边界。

业务规则：产品不能把审阅层状态包装成真实研究完成。

## 行为 5：刷新动作必须调用 POST 并重新读取面板状态

Given 用户点击刷新 P0 阶段包
When POST 成功返回
Then 前端必须更新 `state.productControlP0Data`
And 重新渲染 P0 控制面板。

业务规则：刷新是显式动作；成功后用户看到的是最新阶段报告。

## 行为 6：Agent Queue 不得显示为可执行

Given P0 阶段报告中的 Agent Queue 默认需要派工审阅
When 首页渲染 P0 控制面板
Then 页面必须显示 `待派工审阅`
And 不得出现自动执行按钮。

业务规则：P0 阶段只完成控制和审阅，不授予执行权限。
