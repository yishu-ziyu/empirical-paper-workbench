# Workflow

## 主链路

1. `dataset`
2. `variable_roles`
3. `research_question`
4. `design_spec`
5. `run_plan`
6. `execution`
7. `results`
8. `draft`
9. `review_export`

## 当前状态

- `dataset`：已存在本地文件 `Data/Final/analysis_sample.csv`，证据等级为 `local_file`。
- `variable_roles`：已确认并保存到 `state/product/variable_roles.json`，证据等级为 `local_file`。
- `design_spec`：已确认并保存到 `state/product/design_spec.json`，证据等级为 `local_file`。
- `run_plan`：已确认并保存到 `state/product/run_plan.json`，证据等级为 `local_file`。
- `execution`：已有本地 full run `run_c424d6a11af7`，证据等级为 `local_execution`；manifest 已绑定 RunPlan provenance 和 Feynman-compatible external engine metadata。
- `results`：已通过 `GET /api/v1/projects/{project_id}/results-draft` 从 full-run 结果文件生成最小 FindingCard，证据等级为 `local_execution`。
- `draft`：已有 `Manuscripts/generated/paper_draft.md`，并已在 Results & Draft 页面绑定到 DraftSection evidence binding；草稿文件证据为 `local_file`，论断证据为 `local_execution`。P1-K 已新增 Manuscript candidates，当前只从 approved FindingCard 派生可审阅正文段落候选，不覆盖源草稿。
- `review_export`：已具备 FindingCard claim review、Manuscript candidate review、promote preflight、export preflight preview 和 Review & Export package workbench；`finding_trained_effect` 当前 `review_status=approved`、`can_write_to_draft=true`，`manuscript_candidate_finding_trained_effect_results` 当前 `review_status=approved`、`can_promote=true`、`promotion_status=ready_for_export`、`can_export=true`、`export_status=preview_ready`、`evaluator_status=passed`、`can_write_back=false`，审阅、promotion、export preflight 和 package evaluator 证据均为 `local_file`。下一步应设计显式写回审批或 docx 导出预检。
- `archive_interface`：已完成中文化和档案型全局界面；`Product/web/index.html` 提供 `archive-shell`/`archive-inspector`，`Product/web/assets/app.js` 提供相邻笔记切换，`Product/web/assets/styles.css` 提供纸张网格、证据 ledger、收藏架与交互状态。当前为前端信息架构层，不改变后端 API 或状态机。
- `clean_workbench`：已完成第一轮清洁视觉修正；`archive-shell` 去掉纸格背景和厚重阴影，右侧变为 `inspector-rail` 属性检查器，变量角色确认入口改为 `research-record-card` + `research-step-list`，解决 Data & Design 截图中的重叠问题。
- `dataset_quality_profile`：已完成第一轮数据质量画像；`analysis_sample.csv` 返回 `row_count=12`、`column_count=4`、`missing_rate=0`、字段类型与 readiness，证据等级为 `local_file`。
- `external_data_catalog`：已完成第一轮真实数据候选池；`GET /datasets` 返回 `/Users/mahaoxuan/Desktop/实证数据库` 下 223 个候选数据文件，全部 `read_only=true`、`evidence_level=local_file`，前端“数据与设计”页与项目内数据分开展示。
- `method_catalog`：已完成第一轮方法技能集目录；RunPlan 返回 OLS/DID/IV/RDD/PSM/DML 前置条件，OLS/PSM/DML 当前 ready，DID/IV/RDD 当前 blocked，证据等级为 `local_file`，不代表真实 StatsPAI 执行。
- `method_execution`：已完成第一轮 OLS 本地执行适配器；approved OLS RunPlan 可生成 `Results/json/method_execution_result.json`，证据等级为 `local_execution`，并写入 run response 与 `run_manifest.json`。当前只支持 OLS，unsupported 方法和不可估数据会结构化失败。
- `method_execution_ui`：已完成第一轮方法执行证据展示；`observability.method_execution` 和 `findings[].method_evidence` 都绑定 `Results/json/method_execution_result.json`，页面可见 adapter、公式、样本量、处理变量系数和证据等级。
- `ols_evaluator`：已完成第一轮 OLS evaluator evidence；`method_execution_result.json` 包含标准误、t 统计量、p 值、置信区间、残差诊断和命名 checks，FindingCard 页面显示中文方法证据摘要。

## 当前要求

- 内部生成 `Markdown` 和 `LaTeX` 中间稿。
- 最终稳定导出 `docx`。
- 每次运行都保留可验证的中间产物。
- 产品主行动必须优先围绕研究生命周期，不把 run/step/gate/artifact 作为首页主对象。
- P1-P 已完成；Review & Export 已具备显式写回审批和 docx 预检状态，但仍不覆盖源草稿、不直接生成最终 docx。
- P2-F 已完成；P2-G 开始前必须继续按 BDD/TDD：先定义真实数据源导入/绑定预检行为，避免移动、修改或误提交 `/Users/mahaoxuan/Desktop/实证数据库` 中的原始数据。
- P1-Q 已完成；后续视觉优化必须继续服务研究档案和证据浏览，不回到普通 SaaS landing page。
- P1-R 已完成；后续视觉优化必须保持干净工作台、属性检查器、record/list 和审计线索，不回到纸格背景和大卡片嵌套。
- Feynman 参考路线：短期不嵌入源码；以 callable external research engine 的 provider/provenance 设计进入本项目。
