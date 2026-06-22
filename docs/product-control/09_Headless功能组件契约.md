# Headless 功能组件契约

本文档回答一个产品层问题：先不讨论 UI，系统能力是否已经完整，以及后续 UI 是否能自由重画。

## 当前结论

固定 demo 线已经完成“数据修复 -> 最小模型执行 -> 交付包 -> PDF 导出”的无头执行链路，但没有完成“选题 + 数据集 -> 课程论文级 PDF”的产品闭环。完整视觉设计不是当前阻断；当前阻断是论文审阅和 CHARLS-like Agent pipeline 尚未接入。

当前系统已经完成了一条固定题目的可审计 demo 主线：用户题目进入系统、任务简报、变量草案、source contract、正式变量表、方法预检、RunPlan 审批、阻断执行账本、半成品论文、红标问题清单、用户验收包、P17 数据修复预检、P18 修复数据写入、真实 OLS 执行、可审阅 delivery package、PDF 导出和 headless 状态接口。

P18 已写出 `Data/Interim/parent_education_wage_repaired.csv`，不覆盖 `Data/Final/cfps_robot_reallocation.csv`。P13-P16 已用修复数据重新跑通，P14 真实执行最小 OLS。Delivery Package 已写出 `Submissions/parent_education_wage_delivery_manifest.json`、`Submissions/parent_education_wage_delivery_README.md` 和 `Submissions/parent_education_wage_delivery_package.zip`。Final PDF Export 已写出 `Submissions/parent_education_wage_final_paper.pdf`。

但是当前 PDF 只能标记为 `pdf_export_smoke_only`。它缺少文献闭环、识别策略、表图、稳健性、claim audit、复现门和课程论文级内容密度，不能声称 submission ready，也不能作为课程论文级交付物。纠偏入口是 `Tasks/charls-proofcase-to-agent-product-correction.md`。

同时，系统现在有 `GET /api/v1/projects/{project_id}/product-control/headless-state`，用于把当前能力暴露为 UI 无关组件。React 旧页面仍存在，但未来 UI 可以绕过旧面板，直接消费 headless view model。

## 产品完成门槛

固定 demo 线已经满足下列无头执行链路门槛：

1. P18 能在人工确认后生成新的修复数据集，不覆盖原始正式数据。
2. 修复数据集补齐 `parent_education` 和 `experience` 后，P13-P16 能重新跑通。
3. 字段齐全分支能产生真实 `run_id`、模型结果、表格、日志和证据链。
4. 当前分支能输出 `paper_draft.docx`、Markdown 草稿和 PDF 导出样稿，但还未完成论文审阅。
5. blocked 分支继续能输出半成品论文、红标问题清单和下一步行动，不伪装成完整论文。
6. Headless 状态接口对外暴露稳定组件状态、动作、证据、产物和阻断原因。
7. Delivery Package 能把完整初稿、修复数据、模型证据和审阅材料打成可审阅交付包。
8. Final PDF Export 能把 Markdown 草稿渲染成真实 PDF 文件，并生成 HTML 源、JSON 导出账本和 Review；这只证明导出链路可用。

尚未满足的产品完成门槛：

1. 论文审阅：章节、篇幅、文献、方法、表图、稳健性、claim audit 和复现检查尚未完成。
2. CHARLS-like Agent pipeline：尚未把医保 proof case 中已经成功的 CLI 论文生产链路封装成第二层 Agent 可调度节点。
3. 任意题目/任意数据集：当前仍是固定 adapter，不是通用产品能力。

## Headless 组件原则

每个功能组件必须先作为无头能力存在，再由 UI 选择如何呈现。

无头能力只暴露：

- 当前状态：`status`
- 给用户看的摘要：`user_summary`
- 下一步主动作：`primary_action`
- 可选动作：`actions`
- 阻断原因：`blockers`
- 证据和产物：`evidence`、`artifacts`
- 审计记录：`audit`

无头能力不暴露：

- 页面布局
- 卡片结构
- 字体、颜色、间距
- 折叠面板策略
- 内部调试文本
- 固定 demo 的脚本路径

## 标准组件清单

| 组件 | 用户含义 | 当前状态 | 解耦要求 |
| --- | --- | --- | --- |
| Topic Intake | 用户提出研究问题 | 已有固定 demo 绑定 | 抽成项目创建和题目绑定接口 |
| Task Brief | 系统把题目变成研究任务 | 已有任务简报链路 | 输出用户可确认的 brief，不依赖 UI 文案 |
| Agent Queue | 展示系统接下来要做什么 | 已有阶段队列和门禁 | 用任务状态树表示，不直接渲染相位日志 |
| Evidence Ledger | 管理数据、字段、结论证据 | 部分已有 | 作为所有正式输出的统一证据门禁 |
| Variable Gate | 变量角色和字段来源确认 | P7-P11 已证明 | 对外暴露字段、证据等级、人工确认动作 |
| Method Gate | 方法设计和 RunPlan 审批 | P12-P13 已证明 | 对外暴露可运行性、公式检查和审批动作 |
| Execution Run | 模型执行和结果记录 | 已完成真实最小 OLS | 字段齐全时必须产生真实 run evidence |
| Draft Package | 草稿和问题清单 | PDF 样稿与 blocked 分支都已证明 | 分清 PDF smoke draft、course-paper draft 与 blocked draft |
| Delivery Package | 可审阅交付包 | 已生成 manifest/readme/zip | 打包产物和证据，不宣称投稿终稿 |
| Final PDF | 论文 PDF 结果 | 已生成 PDF 导出样稿 | 只声明 PDF 导出成功；课程论文 ready 必须等论文审阅完成 |
| Review Export | 用户验收和导出预检 | 已完成完整初稿验收包 | 输出可验收状态，不把开发状态暴露给用户 |
| Data Repair | 数据修复候选和写入 | P17/P18 已完成 | P18 必须是显式人工确认后的写入动作 |
| Workflow Status | 全局进度和下一步 | Headless 状态接口已完成 | 输出组件状态模型，不绑定具体视觉样式 |

## 统一响应形状

每个组件对 UI 暴露同一类 view model：

```json
{
  "component_id": "data_repair",
  "label": "数据修复",
  "status": "blocked | ready | waiting_review | completed",
  "user_summary": "还缺父母教育和工作经验字段，需要先确认修复方案。",
  "primary_action": {
    "id": "approve_repair_plan",
    "label": "确认修复方案",
    "enabled": true
  },
  "actions": [],
  "blockers": [],
  "artifacts": [],
  "evidence": [],
  "audit": []
}
```

UI 可以把这个 view model 画成树、时间线、卡片、表格或对话流；业务组件不关心视觉形式。

## 接口边界

读状态用 `GET`。改变系统状态用显式 `POST` command。任何 command 必须写审计记录，且不能顺手写入下游正式产物。

固定 demo 题目只能作为 route adapter 存在：

- `parent-education-wage` adapter 负责定位本地 CSV、候选源表和字段映射。
- 通用产品组件只认识标准契约，不直接 import 固定题目脚本。

## 后续开发顺序

1. 设计师后续可以从 headless endpoint 重新设计 UI，不需要继承当前 React 面板结构。
2. 下一步先建立 Course Paper Quality Gate，对齐 CHARLS 医保 proof case。
3. 再把 `parent-education-wage` 固定 adapter 抽成 CHARLS-like Agent Pipeline Adapter。
4. 若要扩展到任意题目，需要把固定 adapter 抽成通用 route adapter。
