# Product Pipeline Artifact Map

日期：2026-06-19

## 产品定义

本项目只按一个产品目标推进：

> 用户输入题目和数据，系统判断研究问题是否清楚，整理文献和变量，生成方法方案和执行预检，能跑就跑模型，不能跑就明确阻断原因，生成论文初稿或半成品论文，给出审阅报告和修订清单，最后交付 PDF/DOCX、证据包、复现说明。

不要再用“第一版 / 第二版 / P0-P18”定义产品。P 编号、workflow 名称、proof case 名称只作为工程证据，不作为用户看到的产品语言。

## 产品流水线

```text
1. 题目和数据输入
2. 研究问题清晰度判断
3. 文献和变量整理
4. 方法方案和执行预检
5. 模型执行或阻断说明
6. 论文初稿或半成品论文
7. 审阅报告和修订清单
8. PDF/DOCX、证据包、复现说明交付
```

## 当前可用样例

### CGSS 社会资本与幸福感

用途：证明“题目 -> 数据发现 -> 变量候选 -> 文献种子 -> 方法门 -> 模型结果 -> 论文草稿 -> PDF -> 论文审阅”的论文生产链已经有连续产物。

项目 ID：`proj_cgss_social_capital_happiness`

题目：`互联网使用是否提升居民主观幸福感？来自 CGSS 2012-2023 的证据`

边界：当前 PDF 是样稿，课程论文质量门显示还需修订，不能声称已经完成最终课程论文。

### 父母教育与工资

用途：证明“字段缺口 -> 数据修复 -> 最小 OLS 执行 -> 完整初稿 -> PDF 导出”的执行分支已经跑通。

项目 ID：`proj_empirical_paper_template_main`

题目：`父母受教育水平对子女工资收入的影响`

边界：已有真实模型和 PDF，但论文质量报告指出仍缺文献综述、识别策略、稳健性、参考文献、claim audit 和复现门，不能声称投稿级或完整课程论文。

### CHARLS DID proof case

用途：作为严格 proof case 和 runtime 来源，证明真实研究可以从 idea + 数据跑到论文、表图、复现包。

边界：不作为当前产品主仓库，不把 CHARLS 数据、论文、哈希基线复制进主产品仓库。

## 产物账本

| 产品步骤 | 当前可用产物 | 真实状态 | 缺口 |
|---|---|---|---|
| 1. 题目和数据输入 | `Product/state/projects.json`；CGSS 项目注册；父母教育工资项目注册；`Results/json/cgss_social_capital_happiness_data_discovery.json` | 有项目注册和本地数据发现；CGSS 推荐 `CGSS2023.dta`，记录 11326 行、439 个字段和问卷/编码表证据 | 用户侧输入和数据选择还没有统一成一个干净的首屏流程；项目注册里仍有大量旧测试项目和历史样例 |
| 2. 研究问题清晰度判断 | `Tasks/parent-education-wage/brief.md`；`Results/json/cgss_social_capital_happiness_run_plan_seed.json`；`workflows/agents/01_design.agent.md` | 有研究问题草案和 workflow 节点，但用户看不到一个统一的“研究问题是否清楚”判定 | 需要一个用户可读判定：题目、对象、Y、X、数据、识别口径、当前风险 |
| 3. 文献和变量整理 | `Results/json/cgss_social_capital_happiness_literature_seed_package.json`；`Results/json/cgss_social_capital_happiness_variable_candidates.json`；`Results/json/parent_education_wage_p4_field_source_candidates.json`；`state/product/variable_roles.json` | CGSS 有文献种子、变量候选和数据字段发现；父母教育工资有正式变量角色和字段来源 | 文献多数仍是 seed 或候选，不能直接当正式 bibliography；变量整理和人工确认入口没有统一产品语言 |
| 4. 方法方案和执行预检 | `Results/json/cgss_social_capital_happiness_method_gate.json`；`Results/json/cgss_social_capital_happiness_design_spec_draft.json`；`Results/json/parent_education_wage_p12_design_spec_preflight.json` | 有方法门、设计草案和执行预检；父母教育工资公式已形成 `ln_wage ~ parent_education + age + female + urban + edu_last + experience` | 需要把“可跑 / 不能跑 / 为什么”作为一个统一产品组件，而不是散在多个 P 文件 |
| 5. 模型执行或阻断说明 | `Results/json/cgss_social_capital_happiness_minimal_model.json`；`Results/json/cgss_social_capital_happiness_ordered_robustness.json`；`Results/json/cgss_social_capital_happiness_results_evidence_package.json`；`Results/json/parent_education_wage_p14_execution_evidence_ledger.json` | CGSS 有 OLS / Ordered Logit 结果证据；父母教育工资最小 OLS 已执行，`run_id=parent_education_wage_ols_20260618145856`，`nobs=12582` | 结果解释、稳健性等级、是否能支持 claim 还没有统一审计输出 |
| 6. 论文初稿或半成品论文 | `Manuscripts/generated/cgss_social_capital_happiness_paper.md`；`Submissions/cgss_social_capital_happiness/paper.pdf`；`Manuscripts/generated/parent_education_wage_complete_paper_draft.md`；`Submissions/parent_education_wage_paper_draft.docx` | 两条样例都已经有用户可打开的论文草稿或 PDF/DOCX | 草稿质量参差不齐；需要明确“草稿可打开”和“论文质量通过”是两回事 |
| 7. 审阅报告和修订清单 | `Results/json/cgss_social_capital_happiness_course_paper_quality_report.json`；`Results/json/cgss_social_capital_happiness_revision_task_queue.json`；`Tasks/cgss-course-paper-review-revision-list-bdd.md` | CGSS 质量报告已经存在：当前约 5399 中文字符，缺 Theory/Context，多个章节过短，状态为需要扩写/修订 | 需要把审阅报告变成浏览器内可读修订清单，并能一键生成/刷新/回读 |
| 8. PDF/DOCX、证据包、复现说明交付 | `Results/json/cgss_social_capital_happiness_pdf_preflight.json`；`Submissions/cgss_social_capital_happiness/paper.pdf`；`Results/json/parent_education_wage_final_pdf_export.json`；`Submissions/parent_education_wage_final_paper.pdf`；`Submissions/parent_education_wage_delivery_package.zip` | PDF 导出和交付包能力存在；父母教育工资已有 PDF hash 和交付包 | 复现说明、证据包、质量门、最终人工验收还没有被收束成一个用户可理解的终态 |

## 当前判断

项目不是没有产品。产品骨架已经存在，但控制面被样例名、P 阶段、workflow 名、旧测试项目和内部报告淹没了。

当前最接近完整产品路径的是：

```text
CGSS 题目
-> CGSS 数据发现
-> CGSS 变量和文献候选
-> CGSS 方法门和模型结果
-> CGSS 论文草稿和 PDF
-> CGSS 课程论文质量报告
-> 待补：浏览器内修订清单和交付验收
```

父母教育工资样例补足了另一个关键能力：

```text
字段缺口
-> 数据修复
-> 模型执行
-> 完整初稿
-> PDF / DOCX / 交付包
```

因此后续不应该再横向开新样例，也不应该继续堆 P 阶段。下一步应把 CGSS 这条线推成用户可验收产品闭环。

## 当前唯一推进线

当前产品推进线：

> CGSS 论文生产链：从现有 PDF 样稿和质量报告出发，生成浏览器内用户可读修订清单，并把下一步修订动作接回 headless state。

必须完成的最短链：

1. 把 `Results/json/cgss_social_capital_happiness_course_paper_quality_report.json` 转成用户可读修订清单。
2. 前端论文审阅组件提供一个明确动作：`生成 / 刷新审阅报告`。
3. 生成后 headless state 的 `course_paper_quality` 组件必须显示 `needs_revision`、修订优先级、证据路径和下一步。
4. 页面不能声称 CGSS 论文已完成，只能说 PDF 样稿已生成、审阅报告已生成、当前需要修订。
5. 修订清单至少覆盖：篇幅不足、章节缺失或过短、文献核验缺口、证据链缺口、人工终审前置条件。

## 停止做的事

- 不再把 P0-P18 当作产品叙事。
- 不再把“PDF 已生成”当成论文完成。
- 不再把 workflow 合同、Agent 节点、mock report 当成研究证据。
- 不再新增平行 demo 题目。
- 不再让 CHARLS、父母教育工资、CGSS 三条线竞争主线。
- 不再把任务文件继续堆成历史流水账；当前入口必须回到本文件和 `Tasks/todo.md` 顶部。

## 验收标准

用户验收只看这几件事：

- 输入题目和数据后，系统能显示这篇论文现在在哪一步。
- 如果研究问题、变量、方法或数据有问题，系统能说清楚卡点。
- 如果能跑模型，系统能跑并把结果证据记录下来。
- 系统能生成可打开的论文草稿或半成品论文。
- 系统能生成审阅报告和修订清单。
- 系统能交付 PDF/DOCX、证据包、复现说明。
- 系统不把未核验、未审阅、未复现的东西说成完成。

## 下一步执行入口

下一步从 `Tasks/cgss-course-paper-review-revision-list-bdd.md` 进入。

先写失败测试，覆盖：

- CGSS 审阅报告路径不能串到父母教育工资默认路径。
- 课程论文质量报告必须生成用户可读修订清单。
- headless state 必须回读 `review_summary` 和 `top_priorities`。
- UI 默认展示修订清单，不展示原始 JSON。
- 未通过质量门时不能显示“课程论文已完成”。

通过这些测试后，再写最小实现。
