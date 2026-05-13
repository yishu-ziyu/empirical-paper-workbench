# Phase P1-UI BDD: Observable Execution Console Density

## 背景

P1-B 到 P1-D 已经把真实数据源、变量角色、HITL gate、step/event 接到执行页，但页面视觉仍像大号论文卡片：字号过大、圆角过大、空间浪费、信息层级不利于扫读。实证执行页应更像 CoPaper/StatsPAI 风格的工作台：紧凑、可操作、证据清晰、首屏能看到关键 run 上下文。

## 行为用例

### 行为 1：实证执行页使用紧凑控制台样式

Given 用户进入实证执行页  
When 页面渲染运行选择、当前运行、数据源、变量角色  
Then 该页面应使用独立的 console/dense 样式作用域  
And 字体应回到系统 sans-serif，避免论文正文感。

业务规则：执行页是操作台，不是论文阅读页。

### 行为 2：首屏关键上下文必须压缩为信息网格

Given 当前 run 已有 dataset_source 和 variable_roles  
When 页面渲染  
Then 运行选择、当前运行、数据源、变量角色应在紧凑网格中呈现  
And 面板圆角与内边距应小于普通展示卡片。

业务规则：用户应在首屏快速确认 run、数据源和变量理解。

### 行为 3：Step/Event 列表应强调扫读

Given steps/events 很长  
When 页面渲染 Step Board 与 Event Stream  
Then 列表项应使用小字号、轻边框、固定最大高度和紧凑间距  
And 不应出现超大标题撑满屏幕。

业务规则：可观察执行是审计流，优先信息密度和可扫读性。
