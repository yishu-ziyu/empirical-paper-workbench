# CGSS Course Paper Review Revision List BDD

日期：2026-06-19

## 背景

当前 CGSS 论文生产链已经能在浏览器中输入题目、启动论文生产链，并展示 CGSS PDF、论文审阅组件和 10 个 Agent 节点。

下一步不是视觉重设计，而是把“论文审阅尚未完成”推进为用户能一键触发、能读懂、能继续修改的修订清单。

目标路径：

```text
CGSS PDF / Markdown 草稿
-> 论文审阅报告
-> 用户可读修订清单
-> Headless state 回读审阅状态和下一步动作
```

## 行为 1：浏览器内一键生成 CGSS 论文审阅报告

Given 用户已进入 CGSS 项目 `proj_cgss_social_capital_happiness`
And headless state 显示 PDF 样稿已生成但论文审阅尚未完成
When 用户点击论文审阅组件中的生成审阅动作
Then 前端应调用 CGSS 项目的 `POST /product-control/course-paper-quality`
And 后端应写出 CGSS 专属审阅报告 `Results/json/cgss_social_capital_happiness_course_paper_quality_report.json`。

业务规则：用户不应该离开浏览器或手动运行脚本；审阅报告必须绑定当前 CGSS 项目，不能写到父母教育工资默认路径。

## 行为 2：审阅输入必须绑定当前 PDF 的 Markdown 来源

Given CGSS final-pdf 或 paper assembly manifest 记录了 `source_markdown`
When 系统生成课程论文质量报告
Then 它必须读取该 Markdown 草稿作为审阅输入
And 报告中应保留草稿路径、PDF/HTML 来源和质量报告路径。

业务规则：PDF ready 只是导出烟测，不等于论文质量通过；审阅必须回到可检查、可修订的 Markdown 来源。

## 行为 3：修订清单必须用用户能读懂的条目呈现

Given 论文审阅报告已经生成
When UI 渲染论文审阅组件
Then 默认可见区域应展示用户可读修订清单
And 每条修订项应包含标题、原因、建议负责人、关联章节或证据路径
And 不把原始 JSON、内部 verdict code 或 P 阶段编号作为默认主文案。

业务规则：本阶段的交付物是可行动的修订清单，不是让用户阅读调试报告。

## 行为 4：Headless state 必须回读审阅完成状态

Given CGSS 专属课程论文审阅报告已经存在
When UI 重新读取 `GET /product-control/headless-state`
Then `course_paper_quality` 组件应显示报告已生成
And 暴露 `review_summary`、`top_priorities`、`quality_report_path` 和下一步动作
And 不能继续只显示“论文审阅尚未完成”。

业务规则：第三层 UI 只消费 headless 功能组件契约；审阅报告生成后，状态必须能被任意未来 UI 回读。

## 行为 5：审阅未通过时不能声称课程论文已交付

Given 论文审阅报告 verdict 不是 `ready_for_review`
When UI 展示 CGSS 论文生产状态
Then 页面可以显示 PDF 样稿和修订清单
But 必须标记为 `needs_revision`
And 不显示“课程论文已完成”或“可最终提交”。

业务规则：质量报告是门禁，不是装饰；未通过时只能进入修订循环，不能把可运行样稿包装成最终交付。

## 行为 6：审阅通过时进入人工终审，而不是自动正式发布

Given 论文审阅报告 verdict 为 `ready_for_review`
When UI 展示下一步
Then 状态应进入人工终审或最终审阅队列
And 不自动写正式 bibliography、正式提交包、发布链接或外部仓库。

业务规则：即便课程论文质量门通过，正式交付仍需要人工确认，不能由一键审阅动作自动发布。

## 需要确认的边界条件

- 修订清单是否只展示 top priorities，还是同时展示章节缺口、证据缺口、引用缺口三组明细。
- CGSS 审阅通过后的下一步名称：`人工终审`、`最终审阅`、还是 `交付前确认`。
- 是否需要同时生成 Markdown 版修订清单，例如 `Reviews/cgss_social_capital_happiness_course_paper_revision_list.md`，供浏览器外阅读。
- 本阶段是否只做 CGSS 专属切片，还是同时要求父母教育工资项目共享同一 UI 行为。

## 本阶段不做

- 不重画 UI 视觉系统。
- 不重新生成 CGSS PDF。
- 不重跑统计模型。
- 不写正式提交包。
- 不发布到 GitHub、Vercel 或任何外部平台。
