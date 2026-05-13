# Phase P1-A BDD: HITL Gate Resolve Frontend

## 背景

P0 已经让前端读取真实 run observability，并展示 steps、events、gates 和 artifacts。P1-A 的目标是把 HITL gate 从只读展示推进到可处理：用户在页面上确认、驳回或调整 gate，系统调用真实 API 写回 gates/events/manifest，然后刷新同一个 run 的 observability。

## 行为用例

### 行为 1：开放 gate 必须给出可执行动作

Given 用户打开实证执行页并选择一个真实 run  
And 该 run 的 `gates.items` 中存在 `status != "resolved"` 的 gate  
When 页面渲染 HITL gate 区域  
Then 每个开放 gate 必须显示 confirm、reject、adjust 三类动作按钮  
And 按钮不得再显示 “P1 接入” 的禁用占位文案。

业务规则：HITL 是产品闭环的一部分，不是静态审计面板。

### 行为 2：处理 gate 时必须提交用户说明

Given 用户在开放 gate 下填写处理说明  
When 用户点击 confirm、reject 或 adjust  
Then 前端必须向 `POST /api/v1/projects/{project_id}/runs/{run_id}/gates/{gate_id}/resolve` 发送 `{ action, note }`  
And `action` 只能来自 confirm、reject、adjust。

业务规则：每次人工介入都要有可审计解释，不能只有状态变化。

### 行为 3：处理成功后必须刷新真实 observability

Given gate resolve API 返回成功  
When 前端收到响应  
Then 页面必须重新读取当前 `project_id/run_id` 的 observability  
And gate、event stream、manifest-derived 状态必须来自刷新后的文件。

业务规则：页面不伪造成功状态，仍以真实运行轨迹为准。

### 行为 4：处理失败时不能吞掉错误

Given gate resolve API 返回错误  
When 前端捕获异常  
Then 页面必须在实证执行页显示错误信息  
And 原 gate 仍然可见，用户可以修正后重试。

业务规则：HITL 失败本身也是需要用户看见的产品状态。

### 行为 5：已处理 gate 必须显示处理结果且避免重复写入

Given 某个 gate 已经是 `status == "resolved"`  
When 页面渲染该 gate  
Then 必须显示 resolution 的 action、note、resolved_at  
And 不再显示可重复提交的 confirm/reject/adjust 动作。

业务规则：人工介入是有审计边界的一次性决策，不能无提示重复覆盖。

## 边界条件

- P1-A 不做多人并发冲突解决；后端返回错误时前端展示错误并允许重试。
- P1-A 不做用户身份系统；actor 仍由后端记录为当前本地执行上下文。
- P1-A 不启动新 run，只处理当前已选择 run 的 gate；数据集启动真实 run 属于 P1-B。
