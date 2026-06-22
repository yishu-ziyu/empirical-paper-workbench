# Parent Education Wage Final PDF Export BDD

## 背景

用户明确验收标准：给出选题和数据集后，系统必须能把论文跑成最终 PDF，而不是只停在可审阅初稿、交付 zip 或内部证据账本。

本阶段不改 UI。目标是补齐无头产品能力：完整初稿和真实模型证据就绪后，后端可以生成 PDF 文件，并通过组件状态暴露给任意后续 UI。

## 行为 1：完整初稿未就绪时不能生成 PDF

Given P16 验收包不存在，或 `can_claim_complete_paper=false`
When 调用 final PDF 导出
Then 系统返回阻断状态
And 不写出 `Submissions/parent_education_wage_final_paper.pdf`

业务规则：PDF 不能绕过模型执行、完整初稿和验收包门禁。

## 行为 2：完整初稿就绪后写出 PDF、HTML 源和导出账本

Given P16 显示完整论文初稿已经就绪
And Markdown 初稿存在
When 调用 final PDF 导出
Then 系统写出 PDF 文件
And 写出 HTML 渲染源
And 写出 JSON 导出账本和 Markdown 审阅记录
And JSON 记录 PDF 的路径、大小和 SHA256

业务规则：用户要拿到真实 PDF 文件，同时系统要能审计它从哪个初稿导出。

## 行为 3：后端 API 能直接触发和读取 PDF 状态

Given 项目已注册
When 调用 `POST /api/v1/projects/{project_id}/product-control/final-pdf`
Then 成功时返回 201 和 `final_pdf_ready`
When 调用 `GET /api/v1/projects/{project_id}/product-control/final-pdf`
Then 返回已有 PDF 导出状态或可生成状态

业务规则：UI 不应该自己拼路径或跑命令；PDF 是后端命令能力。

## 行为 4：Headless 状态暴露 final_pdf 独立组件

Given PDF 已生成
When UI 读取 `headless-state`
Then components 中包含 `final_pdf`
And 组件状态为 `completed`
And 组件不包含布局字段

业务规则：未来 UI 设计师可以把 PDF 状态画成按钮、树节点、时间线或其他形式，而不依赖旧页面结构。

## 边界

- 本阶段先在固定 demo adapter 上完成 PDF 闭环。
- PDF 导出不重新估计模型，不改变数据，不改写 P13-P16 证据。
- 后续任意题目/任意数据集需要把固定 adapter 抽象成通用 route adapter。
