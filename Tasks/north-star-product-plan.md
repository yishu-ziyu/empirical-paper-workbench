# North Star Product Plan

更新时间：2026-06-18

## 北极星目标

把当前项目推进成一个本科生可用、可审计、可交付的实证论文生产流水线：用户输入研究题目和可用数据后，系统能生成 `paper_draft.docx / paper_draft.pdf`；当证据不足时，必须生成半成品论文、红标问题清单和下一步补齐动作，而不是伪造成完整论文。

## 产品成功标准

- 用户能从一个入口看到当前研究卡在哪里、为什么卡、下一步由谁补什么。
- 用户能获得固定首交付物：完整或半成品 `paper_draft.docx / paper_draft.pdf`。
- 所有正式写入都有人工审批和证据链：VariableRoleSet、DesignSpec、RunPlan、Run、Results、Draft。
- 没有真实数据、字段来源、模型运行或引用证据时，页面必须明确阻断，不能包装成成功。
- 固定 demo 题目只是压力测试样例，产品结构必须能迁移到其它本科生题目。
- 每阶段都有 BDD、测试、最小验证、状态文档和交付总结。

## Pre-PRD Design Tree Gate

P12-P16 这类复杂阶段进入 SDD/BDD/TDD 前，必须先过一轮 `Grill -> Research -> Prototype -> PRD/SDD -> Issues -> Implement -> Review` 的前置门。

这道门的目的不是增加文档，而是防止产品路径和实现路径混在一起。每个大阶段开始前必须先回答：

- 当前用户决策是什么，用户为什么要在这里停下。
- 这个阶段有哪些可能分支：成功、阻断、回退、半成品交付、人工确认、禁止自动化。
- 哪些对象是后台正式层，哪些对象应该被翻译成用户能理解的页面语言。
- 哪些操作只能生成 draft/preflight，哪些操作才允许写正式层。
- 最小原型长什么样，用户第一眼应该看懂什么。
- 任务如何拆成有阻塞关系的小票，而不是一个大阶段名。
- 人类 QA 应该怎么验收：URL、面板、按钮状态、禁用状态、禁止出现的入口。

没有完成这道门时，不进入实现；只允许继续补设计树、原型目标、issue graph 或 QA 计划。

## SDD / BDD / TDD 执行规则

### SDD

每个大阶段先写规格，至少包含：

- 用户是谁。
- 用户要完成什么。
- 系统必须交付什么文件或状态。
- 系统不能越过哪些边界。
- 成功和阻断分别如何呈现。

### BDD

每个用户可见阶段写 3-8 条 Given / When / Then 行为，解释业务规则。BDD 先于实现。

### TDD

每阶段先写能失败的自动化测试，再做最小实现。测试至少覆盖：

- 正常路径。
- 阻断路径。
- 正式层不越权。
- 前端是否把当前状态讲清楚。

## 阶段路线

### P10 - Product Control 当前门禁中心

目标：解决页面混乱，让第一屏回答“现在卡在哪里、为什么、下一步补什么”。

验收：

- Product Control 顶部有当前门禁摘要。
- P0-P8 历史阶段默认折叠。
- P9 source metadata 阻断和 no-model 边界可见。
- 页面通过桌面和移动端浏览器验收。

### P11 - Source Metadata Completion Path

目标：把 P4/P5 候选字段转成可人工确认的 source contract。

验收：

- 用户能选择 dataset path。
- 用户能把 `ln_wage`、`parent_education`、controls 绑定到字段来源。
- 派生变量必须写清 construction 和 source fields。
- 预填候选字段必须逐行人工确认，未确认行不能保存 source contract。
- 完成前 P9 仍阻断；完成后 P9 才允许保存正式 VariableRoleSet。

### P12 - DesignSpec Preflight

目标：正式变量表保存后，生成方法设计预检，不直接跑模型。

验收：

- DesignSpec 草案读取正式 VariableRoleSet。
- 方法选择解释为什么选 OLS/DID/IV/PSM 或阻断。
- 缺少识别条件时生成问题清单。
- 不写 RunPlan，不创建 run id。

### P13 - RunPlan Approval

目标：把可执行方法转成可审阅 RunPlan。

验收：

- RunPlan 明确数据、样本、变量、公式、稳健性、输出路径。
- 人工批准前不能创建 run id。
- blocked 方法不能被塞进 RunPlan。

### P14 - Model Execution And Evidence Ledger

目标：批准后执行最小可复现模型，形成结果证据账本。

验收：

- 生成 run id。
- 输出日志、表格、模型结果 JSON。
- 失败时生成可读错误和修复建议。
- 结果不能直接写入论文正文，必须先进入 evidence ledger。

### P15 - Draft Generation And Export

目标：把证据链转成论文初稿或半成品论文。

验收：

- 生成 `paper_draft.docx`，可行时生成 `paper_draft.pdf`。
- 论文中不确定或缺证据部分明确标红或列入问题清单。
- 结果表、引用、变量口径都有 provenance。

### P16 - User Acceptance And Satisfaction Loop

目标：让用户能签收、要求修改、导出或回到补证路径。

验收：

- 用户能看到交付物质量、缺口和下一步。
- 用户能决定导出、修订或补证。
- 系统生成最终交付总结和复现清单。

## 必须停下问用户的情况

- 需要删除或大规模重写现有文件。
- 需要安装新依赖。
- 需要外部服务、API key 或付费模型。
- 测试连续两次失败且不是本地可修问题。
- 需要决定研究题目、数据口径、变量含义或论文主张。
- 需要把草稿提升为正式论文、正式引用或正式模型结论。

## 不允许改动的范围

- 不手改原始数据。
- 不把候选字段直接写成正式变量。
- 不把 preflight 当作 approval。
- 不把半成品论文伪装成完整论文。
- 不为了视觉整理重写 Product 全部前端。
- 不把固定 demo 题目写死成产品边界。
