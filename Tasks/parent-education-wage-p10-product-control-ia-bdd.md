# P10 Product Control Information Architecture BDD

目标：把 Product Control 从 P0-P9 线性堆叠改成当前门禁优先的审阅台，让用户打开页面先看到现在卡在哪里、为什么卡、下一步补什么，同时保留历史阶段证据。

## 行为 1：当前门禁摘要必须在 Product Control 顶部

Given 真实项目已经完成 P7 draft 和 P8 approval
And P9 因 source contract incomplete 被阻断
When 用户打开 React 主入口
Then Product Control 顶部必须先显示 `当前门禁`
And 显示 `P9 正式变量表保存`
And 显示 `blocked_missing_dataset_source_metadata`
And 显示不能写正式变量表、不能创建 run id、不能跑模型。

业务规则：用户不应从 P0 开始读一遍历史流程，当前决策点必须是第一屏信息。

## 行为 2：历史阶段默认折叠为摘要

Given P0-P8 已经有各自状态
When 用户查看 Product Control
Then P0-P8 只能出现在 `阶段历史` 折叠区
And 折叠区默认关闭
And 摘要文案必须说明 P7 已完成、P8 已审批、P9 正在等待 source metadata。

业务规则：历史阶段是证据，不是当前操作主线。默认展开所有阶段会制造噪音。

## 行为 3：P9 细节仍然可操作但不越权

Given P9 仍缺 dataset/source metadata
When 用户查看当前门禁的 P9 详情
Then 保存按钮必须禁用
And 页面必须显示 `missing_source_metadata_fields`
And 页面必须保留 `不写 DesignSpec；不写 RunPlan；不跑模型`
And 页面不能出现 `运行模型` 操作。

业务规则：信息架构整理不能弱化正式层边界，也不能把阻断态伪装成可执行态。

## 边界

- P10 只改 Product Control 信息架构和文案，不写正式 `state/product/variable_roles.json`。
- P10 不补 source metadata，不进入 DesignSpec preflight。
- P10 不创建 run id，不执行模型。
- P10 不重写主工作台其它阶段页面。
