# WORKFLOW_STATUS

Last updated: 2026-06-18

## Goal Mode

目标：把当前实证论文项目推进成本科生可用、可审计、可交付的实证论文生产流水线。用户输入研究题目和可用数据后，系统最终应交付 `paper_draft.docx / paper_draft.pdf`；证据不足时必须交付半成品论文、红标问题清单和下一步补齐动作，而不是伪造成完整论文。

本文件是连续执行控制面。后续每完成一个阶段必须更新本文件；阶段验收通过后自动进入下一阶段，不询问“是否继续”；只有触发停机条件才暂停。

## Current Diagnosis

- 主仓库：`/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板`。
- CHARLS DID 仓库：`/Users/mahaoxuan/Desktop/经济学论文/StatspAI_跑通一次_CHARLS_DID`，定位为 proof case 和 runtime 来源样例，不作为后续产品开发主仓库。
- 当前产品主入口：FastAPI 根路径 `/`、`/react`、`/react/` 服务 `Product/web-dist/index.html`，来源是 `Product/web-react`。
- 旧工作台入口：`/legacy` 已改为 307 重定向到 `/`；`Product/web` 只作为历史源码保留，不再作为产品验收面。
- 已完成的纠偏：P0 后端/API 和 React P0 控制面板已经对齐，`GET/POST /api/v1/projects/{project_id}/product-control/p0-phase` 可用；P0 面板不再依赖 legacy UI。
- 当前阶段判断：P0/P1 验收包已收口；P2-P12 已完成到方法规格预检；P13-P16 已继续推进到阻断交付分支。P13 用真实 CSV 表头校验 P12 公式后发现 `parent_education`、`experience` 不存在；P14 因此没有创建运行编号、没有运行模型；P15 已交付半成品论文和红标问题清单；P16 已生成用户验收包。当前真实阻断是数据缺列，不是流程停在 P12。项目内动态工作流仪表盘为 `docs/product-control/workflow-dashboard.html`，状态源为 `docs/product-control/workflow-dashboard-state.json`。
- 当前 Demo 题目：`父母受教育水平对子女工资收入的影响`。它是用于验证完整产品链路的固定样例，不代表产品最终只能服务这个题目。
- 真实产品形态：面向本科生和初级研究者的可审计论文初稿生产流水线。它不是单题目脚本，也不是无证据的一次性论文生成器；正向用户承诺是生成 `paper_draft.pdf / .docx`，证据不足时生成半成品论文、红标缺口和问题清单。
- 固定首交付物：`paper_draft.pdf / paper_draft.docx`。审计报告、问题清单、证据账本和运行日志是支撑物，不应替代论文初稿成为第一用户体验。
- 已知测试基线：P0 目标回归曾通过；全量 pytest 仍存在历史/环境/React 契约相关失败，后续必须先建立 scoped baseline，再扩大修复范围。

## Phase Status

Current phase: P16 blocked delivery branch is ready. Real project now has a P7 editable draft, P8 approval, a saved P11 source contract, an approved formal VariableRoleSet, a P12 preflight artifact, P13 dataset-column approval evidence, P14 blocked execution ledger, P15 draft export package, and P16 user acceptance packet. The demo line has been pushed forward; it cannot claim a complete empirical paper because the real CSV lacks `parent_education` and `experience`.

Completed phases:

- Phase 0 - Project audit and workflow planning.
- Phase 1 - Current React entrypoint recovery and baseline.
- Phase 2 - Product Control P0 port to React main UI.
- Phase 3 - P1-A real literature and citation evidence chain.
- Phase 4 - P1-B real data field binding and variable role evidence.
- Phase 5 - P1-C method execution evidence and run ledger.
- Phase 6 - Acceptance package, cleanup, and handoff.
- P2 - Execution readiness ledger, field supplementation draft, design decontamination, and Product Control status.
- P3 - DraftPackage blocked branch: half-finished paper draft, issue list, audit report, Product API, and React Product Control status.
- P4 - Parent education field source candidates: metadata-only CFPS scan, stale source path detection, Product API, and React Product Control status.
- P5 - VariableRoleSet draft preflight: parent education construction draft, hukou/outcome/control review items, Product API, and React Product Control status.
- P6 - Human signoff and promotion path: P5 signoff packet, complete-signoff gate, editable draft promotion service, Product API, and React Product Control status.
- P7 - UI signoff console: five editable human-decision inputs, recommended defaults from P6, editable-draft promotion button, mobile-safe Product Control layout, and no formal/model execution.
- P8 - Formal VariableRoleSet approval gate: separate reviewer/note/confirmation approval, stale-approval guard, Product API, React Product Control status, and no DesignSpec/RunPlan/run/model execution.
- P9 - Formal VariableRoleSet save gate: P8-approved draft save contract, dataset/source metadata guard, Product API, React Product Control status, and no DesignSpec/RunPlan/run/model execution.
- P10 - Product Control current gate center: current blocker first, P0-P8 collapsed as history, P9 detail visible, mobile-safe review surface, and no DesignSpec/RunPlan/run/model execution.
- P11 - Source Metadata Completion Path: Product API and React form to save source contract into the latest editable draft only; complete contract unlocks P9 readiness but does not write formal VariableRoleSet/DesignSpec/RunPlan/run/model.
- P11A - Source Contract Review Kit: P11 GET now returns recommended dataset path candidates, field review items from P5/P4 evidence, missing-source status, and no-model boundary; React displays the kit before the JSON form.
- P11B - Per-field Source Confirmation Editor: React P11 now renders editable rows for each required source field and builds the existing `field_bindings` payload from those rows; JSON remains as an audit preview.
- P11C - Source Contract Readiness Check: React P11 now computes missing signing items before save, displays readiness, and keeps the save button disabled until all required source rows and human signoff fields are complete.
- P11D - Row Human Confirmation Gate: React P11 now requires each source row to be explicitly checked by a human before save; prefilled candidate rows remain `human_confirmation` gaps until checked.
- P11E - Human Signoff Readable Rows: React P11 source rows now keep visible labels for dataset column, source field, source path, and evidence level on desktop/mobile; mobile page-level horizontal overflow is fixed while the save gate remains unchanged.
- P11F - Human Signoff Review Queue: React P11 now shows a compact queue of the 9 required source fields, their confirmation status, missing items, and next action before the long form; it does not save source contract or unlock P9.
- P11G - Source Contract Signoff Workspace: React P11 now presents a two-pane signoff workspace with current status cards, review queue, collapsed source review kit, source contract form, non-overlapping action bar, desktop/mobile screenshots, and the no-model boundary; it still does not save source contract or unlock P9.
- P11-Human - Real Source Contract Save: saved `Data/Final/cfps_robot_reallocation.csv`, reviewer/note, parent education construction, and 9 field source bindings into the latest editable draft source contract; this unlocks P9 readiness only.
- P11H - Saved Next-Step State: React now shows `P11 已签收`, `已解锁 P9 正式变量表保存`, dataset path, and the next action `回到 P9 正式保存`; it still shows no P12, no run id, and no model execution.
- P9-Human - Formal VariableRoleSet Save: saved the P8-approved, P11-sourced roles into `state/product/variable_roles.json`; P9 GET now reports `formal_variable_roles_saved` instead of inviting repeated saves.
- P12-0 - Design Tree / Pre-PRD: created `docs/product-control/p12-p16-design-tree.md`, updated dashboard state to `p12_design_tree_ready`, and defined P12-P16 acceptance, fallback, and stop conditions before DesignSpec work.
- P12 - DesignSpec Preflight: generated a reviewable method-spec preflight from the formal VariableRoleSet, wrote JSON/Review artifacts, exposed Product API GET/POST, and kept formal DesignSpec/RunPlan/run/model blocked.
- P13 - RunPlan Approval: validated P12 required columns against the real CSV, archived stale old robot formal DesignSpec/RunPlan, and blocked RunPlan approval because `parent_education` and `experience` are missing.
- P14 - Execution Evidence Ledger: wrote a blocked execution ledger with `run_id=null` and `executed_regression=false`.
- P15 - Draft Generation And Export: preserved the existing half-finished `Submissions/parent_education_wage_paper_draft.docx` path and wrote `Manuscripts/generated/parent_education_wage_p15_issue_list.md`.
- P16 - User Acceptance And Satisfaction Loop: wrote a user acceptance packet that marks `can_claim_complete_paper=false` and `current_user_outcome=半成品论文 + 红标问题清单`.

Remaining phases:

- Data repair for the complete-paper branch：补齐或合并 `parent_education` 与 `experience` 后，重新运行 P13-P16，才允许进入真实模型结果和完整论文分支。

Current blocker: 真实数据集 `Data/Final/cfps_robot_reallocation.csv` 的表头没有 `parent_education` 和 `experience`。P12 baseline 公式为 `ln_wage ~ parent_education + age + female + urban + edu_last + experience`，所以 P13 正确阻断 RunPlan，P14 正确不运行模型。旧机器人题目的 `state/product/design_spec.json` 和 `state/product/run_plan.json` 已归档到 `state/product/archive/p13_p16_stale_formal_state/`，不能再作为当前题目证据。当前可交付物是半成品论文包和红标问题清单，不是完整实证结果。

North Star control file: `Tasks/north-star-product-plan.md`。后续复杂阶段按 `追问 -> 调研 -> 原型 -> 规格 -> 拆任务 -> 实现 -> 复核` 执行；P12-P16 进入 SDD / BDD / TDD 前必须先过设计树门禁，先写清设计树、分支、阻断和 QA 计划，再写规格和行为、失败测试、最小实现和验证。

Visual workflow dashboard: `docs/product-control/workflow-dashboard.html`。它是项目内动态中文控制面，通过 `/workflow-dashboard` 打开并每 3 秒轮询 `/api/v1/workflow-dashboard/state`；状态源为 `docs/product-control/workflow-dashboard-state.json`。当前 H1 为 `论文生产流水线控制台`，首屏先回答三句话：`现在能交付什么`、`还缺什么`、`下一步做什么`；当前门禁为 `P16 半成品交付包已生成`，阻断为真实 CSV 缺字段，禁止动作是不伪造结果。阶段变化后必须同步更新本文件、`Tasks/todo.md` 和该 JSON。

## Latest P13-P16 Verification

- SDD/BDD：`Tasks/parent-education-wage-p13-p16-demo-closure-bdd.md`。
- 核心功能：新增 P13-P16 demo closure，继续推进 Demo 线；缺真实字段时走阻断交付分支，而不是停在 P12 或伪造回归结果。
- 真实产物：`Results/json/parent_education_wage_p13_run_plan_approval.json`、`Results/json/parent_education_wage_p14_execution_evidence_ledger.json`、`Results/json/parent_education_wage_p15_draft_export_package.json`、`Results/json/parent_education_wage_p16_user_acceptance_packet.json`、`Manuscripts/generated/parent_education_wage_p15_issue_list.md`。
- 真实结论：P13 required columns 为 `ln_wage,parent_education,age,female,urban,edu_last,experience`；真实 CSV 缺 `parent_education`、`experience`；P14 `run_id=null`、`executed_regression=false`；P16 `can_claim_complete_paper=false`。
- 旧状态清理：旧机器人题目的正式方法规格和运行计划已从活跃状态归档到 `state/product/archive/p13_p16_stale_formal_state/`。
- 防误报修复：GET 在 P13-P16 产物不存在时只返回 `p13_p16_closure_not_run`，不会凭 P12 临时合成 P16；P12 题目/变量/公式含旧机器人痕迹时返回 409；字段齐全时必须实际执行最小 OLS 后才返回 run id。
- TDD RED：`python3 -m pytest tests/test_parent_education_wage_p13_p16_demo_closure.py -q` 首次 3 failed，原因是 P13-P16 API 不存在，仪表盘没有三句话管理层摘要。
- 防误报 RED：新增 GET-before-POST、stale P12、字段齐全必须真跑 OLS 三个边界测试后，`python3 -m pytest tests/test_parent_education_wage_p13_p16_demo_closure.py -q` 曾 3 failed，原因是旧实现会合成 P16、接收旧 P12、创建未执行 run id。
- 目标测试：`PYTHONDONTWRITEBYTECODE=1 python3 -m pytest tests/test_parent_education_wage_p13_p16_demo_closure.py tests/test_workflow_dashboard_artifact.py -q -p no:cacheprovider`，13 passed。
- 阶段回归：`PYTHONDONTWRITEBYTECODE=1 python3 -m pytest tests/test_parent_education_wage_p9_formal_variable_role_save.py tests/test_parent_education_wage_p10_product_control_ia.py tests/test_parent_education_wage_p11_source_metadata_contract.py tests/test_parent_education_wage_p12_design_tree.py tests/test_parent_education_wage_p12_design_spec_preflight.py tests/test_parent_education_wage_p13_p16_demo_closure.py tests/test_workflow_dashboard_artifact.py -q -p no:cacheprovider`，45 passed。
- Python 编译：P13-P16 service、workbench、`Product/app.py` 和 dashboard service 编译通过。
- 前端构建：`cd Product/web-react && npm run build` 通过，保留既有 Vite chunk size warning。
- API smoke：`http://127.0.0.1:8780/api/v1/projects/proj_empirical_paper_template_main/product-control/p13-p16-demo-closure` POST 返回 `demo_closure_blocked_branch_ready`、缺 `parent_education`/`experience`、无 run id、无模型结果。
- 浏览器 QA：`http://127.0.0.1:8780/workflow-dashboard` 桌面 1440px 和移动端 390px 均显示 `现在能交付什么`、`还缺什么`、`下一步做什么`、`P16 半成品交付包已生成`、`P13 运行计划校验`、`不伪造回归结果`；无横向溢出。截图为 `Product/output/playwright/workflow-dashboard-p16-blocked-closure-desktop.png`、`Product/output/playwright/workflow-dashboard-p16-blocked-closure-mobile.png`。

## Latest P12 Verification

- SDD/BDD：`Tasks/parent-education-wage-p12-design-spec-preflight-bdd.md`。
- 核心功能：新增 P12 DesignSpec Preflight，把正式 `state/product/variable_roles.json` 转成可审阅方法规格预检。
- 真实产物：`Results/json/parent_education_wage_p12_design_spec_preflight.json` 和 `Reviews/parent_education_wage_p12_design_spec_preflight.md`。
- 方法草案：baseline OLS，公式为 `ln_wage ~ parent_education + age + female + urban + edu_last + experience`；DID/IV/RDD 标记阻断，PSM/DML 只作为候选预检。
- TDD RED：`python3 -m pytest tests/test_parent_education_wage_p12_design_spec_preflight.py -q` 首次 4 failed，原因是 P12 API/服务尚不存在。
- 目标测试：`python3 -m pytest tests/test_parent_education_wage_p12_design_spec_preflight.py -q`，4 passed。
- P12/dashboard 最小回归：`python3 -m pytest tests/test_parent_education_wage_p12_design_spec_preflight.py tests/test_parent_education_wage_p12_design_tree.py tests/test_workflow_dashboard_artifact.py -q`，14 passed。
- 阶段回归：`python3 -m pytest tests/test_parent_education_wage_p9_formal_variable_role_save.py tests/test_parent_education_wage_p10_product_control_ia.py tests/test_parent_education_wage_p11_source_metadata_contract.py tests/test_parent_education_wage_p12_design_tree.py tests/test_parent_education_wage_p12_design_spec_preflight.py tests/test_workflow_dashboard_artifact.py -q`，39 passed。
- Python 编译：`python3 -m py_compile Product/backend/product_control_p9_variable_role_save_service.py Product/backend/product_control_p12_design_spec_preflight_service.py Program/workbench/parent_education_wage_design_spec_preflight.py Product/app.py Product/backend/workflow_dashboard_service.py` 通过。
- 前端构建：`cd Product/web-react && npm run build` 通过，保留既有 Vite chunk size warning。
- 当前代码 API smoke：`http://127.0.0.1:8779/api/v1/projects/proj_empirical_paper_template_main/product-control/p12-design-spec-preflight` GET/POST 返回 `design_spec_preflight_ready_for_review`、公式 `ln_wage ~ parent_education + age + female + urban + edu_last + experience`、`can_write_design_spec=false`、`can_create_run_id=false`、`can_execute_model=false`。
- 浏览器 QA：Browser plugin required `node_repl js` 入口未暴露，本轮按前端测试规范回退到普通 Playwright。`http://127.0.0.1:8779/workflow-dashboard` 桌面 1440px 和移动端 390px 均显示 `P12 DesignSpec 预检已生成`、`P13 RunPlan Approval`、`不运行模型` 和 `预检产物`；状态轮询显示 `状态已更新 · 2026-06-18 17:06:10`；无横向溢出、无 offscreen 元素、无相关 console error、无框架错误 overlay。截图为 `Product/output/playwright/workflow-dashboard-p12-design-spec-preflight-desktop.png`、`Product/output/playwright/workflow-dashboard-p12-design-spec-preflight-mobile.png`。
- 仪表盘状态：`docs/product-control/workflow-dashboard-state.json` 已更新为 `status_code=p12_design_spec_preflight_ready`、`current_gate=P12 DesignSpec 预检已生成`、`next_action=下一步进入 P13 RunPlan Approval 前的人工作业`。
- 正式层边界：P12 只写预检 JSON/Review，不写 `state/product/design_spec.json`，不写 `state/product/run_plan.json`，不创建 run id，不执行模型。

## Latest P12-0 Verification

- SDD/BDD：`Tasks/parent-education-wage-p12-0-design-tree-bdd.md`。
- 核心功能：新增 `docs/product-control/p12-p16-design-tree.md`，在 P12 实现前写清 P12 DesignSpec Preflight、P13 RunPlan Approval、P14 Model Execution And Evidence Ledger、P15 Draft Generation And Export、P16 User Acceptance And Satisfaction Loop。
- 用户路径：P12-0 让项目主导者先看见下一棵树；下一步只进入 P12 DesignSpec Preflight，不直接写 RunPlan，不创建 run id，不运行模型。
- 仪表盘状态：`docs/product-control/workflow-dashboard-state.json` 已更新为 `status_code=p12_design_tree_ready`、`current_gate=P12-0 设计树已完成`、`next_action=下一步进入 P12 DesignSpec Preflight`。
- TDD RED：`python3 -m pytest tests/test_parent_education_wage_p12_design_tree.py -q` 首次 3 failed，原因是 P12-0 设计树文件不存在，仪表盘仍停在 `formal_variable_role_save_ready`。
- 目标测试：`python3 -m pytest tests/test_parent_education_wage_p12_design_tree.py tests/test_workflow_dashboard_artifact.py -q`，10 passed。
- 阶段回归：`python3 -m pytest tests/test_parent_education_wage_p9_formal_variable_role_save.py tests/test_parent_education_wage_p10_product_control_ia.py tests/test_parent_education_wage_p11_source_metadata_contract.py tests/test_parent_education_wage_p12_design_tree.py tests/test_workflow_dashboard_artifact.py -q`，35 passed。
- 前端构建：`cd Product/web-react && npm run build` 通过，保留既有 Vite chunk size warning。
- 浏览器 QA：当前代码服务 `http://127.0.0.1:8777` 下，`/workflow-dashboard` 桌面 1440px 和移动端 390px 均显示 `论文生产流水线控制台`、`老板先看这里`、`P12-0 设计树已完成`、`下一步进入 P12 DesignSpec Preflight`、`不运行模型`；无横向溢出，无相关 console error。截图为 `Product/output/playwright/workflow-dashboard-p12-design-tree-desktop.png`、`Product/output/playwright/workflow-dashboard-p12-design-tree-mobile.png`。
- 正式层边界：P12-0 只写设计树和仪表盘状态，不写 `state/product/design_spec.json`，不写 `state/product/run_plan.json`，不创建 run id，不执行模型。

## Latest P9H Verification

- SDD/BDD：`Tasks/parent-education-wage-p9h-formal-save-completion-bdd.md`。
- 核心功能：P9-Human 已把 P8-approved、P11-sourced 的变量角色正式保存到 `state/product/variable_roles.json`。
- 保存结果：`status=formal_variable_roles_saved`，`dataset_path=Data/Final/cfps_robot_reallocation.csv`，roles 为 `ln_wage`、`parent_education`、`age/female/urban/edu_last/experience`，正式 VariableRoleSet `status=approved`、`version=3`。
- 修复缺陷：P9 POST 成功后，GET 曾继续返回 `formal_variable_role_save_ready`，会误导用户重复保存。已新增回归测试并修复为 GET 返回 `formal_variable_roles_saved`、`can_save_formal_variable_roles=false`、`can_enter_design_spec_preflight=true`。
- 回归：`python3 -m pytest tests/test_parent_education_wage_p9_formal_variable_role_save.py -q`，7 passed；`python3 -m pytest tests/test_parent_education_wage_p9_formal_variable_role_save.py tests/test_parent_education_wage_p10_product_control_ia.py tests/test_parent_education_wage_p11_source_metadata_contract.py tests/test_workflow_dashboard_artifact.py -q`，31 passed。
- 当前代码 API smoke：8777 当前代码服务上，P9 GET 返回 `formal_variable_roles_saved`、`can_save_formal_variable_roles=false`、`can_enter_design_spec_preflight=true`、`can_create_run_id=false`、`can_execute_model=false`。
- React 视觉修复：P9H/P10 当前门禁摘要在 390px 移动端已改为单列布局，避免右侧状态清单覆盖标题和正文。
- 浏览器 QA：`http://127.0.0.1:8777/?topic=empirical-paper-template-main&mode=human-review&api_base=http://127.0.0.1:8777&v=p9h-p12-tree-final3` 桌面 1440px 和移动端 390px 均可见 `产品控制`、`P9 正式变量表保存`、`正式变量表已保存`、`不能进入正式论文`、`仍不能运行模型`；无横向溢出，无相关 console error；移动端 `.product-control-gate-summary` 为单列且无重叠。截图为 `Product/output/playwright/product-control-p9h-saved-current-code-desktop.png`、`Product/output/playwright/product-control-p9h-saved-current-code-mobile.png`。
- 正式层边界：P9-Human 只写正式 VariableRoleSet；不写 DesignSpec/RunPlan，不创建 run id，不执行模型。

## Latest P11H Verification

- SDD/BDD：`Tasks/parent-education-wage-p11h-source-contract-saved-next-step-bdd.md`。
- 核心功能：P11-Human 真实保存 source contract 后，React 页面显示 `P11 已签收`、`已解锁 P9 正式变量表保存`、dataset path 和 `下一步：回到 P9 正式保存`。
- 用户路径：保存 source contract 后只回到 P9 正式保存；页面继续明确 `仍不能进入 P12`、`仍不能创建 run id`、`仍不能运行模型`。
- 正式层边界：P11H 不写正式 VariableRoleSet，不写 DesignSpec/RunPlan，不创建 run id，不执行模型。
- TDD：`python3 -m pytest tests/test_parent_education_wage_p11_source_metadata_contract.py -q` 新增 P11H React 契约后先失败 1 项，原因是 React 尚未暴露 `sourceContractSaved` 和 saved next-step panel；实现后 13 passed。
- 邻近回归：`python3 -m pytest tests/test_parent_education_wage_p9_formal_variable_role_save.py tests/test_parent_education_wage_p10_product_control_ia.py tests/test_parent_education_wage_p11_source_metadata_contract.py -q`，24 passed。
- React build：`cd Product/web-react && npm run build` 通过，仍有既有 Vite chunk size warning。
- 真实 P11-Human 保存：通过 8776 真实页面写入 `Data/Final/cfps_robot_reallocation.csv`、reviewer/note、9 个字段来源、逐行 human confirmation 和 `max(father_education, mother_education)` construction。
- API smoke：P11 返回 `source_metadata_contract_ready_for_p9_save`、missing fields 为空、`can_return_to_p9_formal_save=true`、`can_execute_model=false`；P9 返回 `formal_variable_role_save_ready`、`can_save_formal_variable_roles=true`、`can_enter_design_spec_preflight=false`、`can_create_run_id=false`、`can_execute_model=false`。
- 浏览器 smoke：`http://127.0.0.1:8776/?topic=empirical-paper-template-main&mode=human-review&api_base=http://127.0.0.1:8776&v=p11h-final-2` 桌面和 390px 移动端均可见 P11 已签收、P9 已解锁、9/9 fields、missing none、no P12/run/model；horizontalOverflow=false、offscreenCount=0、console messages=0。截图为 `Product/output/playwright/product-control-p11h-saved-next-step-final2-desktop.png`、`Product/output/playwright/product-control-p11h-saved-next-step-final2-mobile.png`。
- 当前真实项目状态：P11-Human/P11H 已完成；下一阶段是 P9-Human 正式变量表保存，不是 P12 或模型执行。

## Latest Workflow Dashboard Verification

- BDD：`Tasks/workflow-dashboard-bdd.md`。
- 核心功能：新增 `docs/product-control/workflow-dashboard.html` 和 `docs/product-control/workflow-dashboard-state.json`，作为项目内可动态更新的中文工作流仪表盘，显示 CEO 摘要、追问、调研、原型、规格、拆任务、实现、复核七阶段、当前/下一阶段、当前门禁、阻断点、P12-P16 分支树和人工验收清单。
- 当前状态表达：页面明确 `P9 已正式保存`、`P12 DesignSpec 预检已生成`、`P13 RunPlan Approval` 和 `不运行模型`；机器错误码只保留在状态 JSON，不作为主界面文案。
- 发现入口：`docs/product-control/README.md` 已把 `workflow-dashboard.html` 放在阅读顺序第 0 位。
- TDD：`python3 -m pytest tests/test_workflow_dashboard_artifact.py -q` 新增动态状态测试后先失败 6 项，原因是 `docs/product-control/workflow-dashboard-state.json` 和 FastAPI 动态入口尚不存在；实现后通过。
- FastAPI 入口：`/workflow-dashboard` 返回 HTML，`/api/v1/workflow-dashboard/state` 每次读取状态 JSON，并返回 `Cache-Control: no-store`。
- 中文化验收：旧英文 fallback 和旧状态 JSON 下目标测试先失败 6 项；改成中文主界面后 `python3 -m pytest tests/test_workflow_dashboard_artifact.py -q` 6 passed。浏览器复核 `http://127.0.0.1:8788/workflow-dashboard` 桌面和 390px 移动端均显示中文标题、中文阶段、中文阻断和中文人工验收清单；旧英文状态未出现，控制台无错误，状态 API 返回 200/no-store，offscreen elements=0。截图为 `Product/output/playwright/workflow-dashboard-desktop-chinese.png`、`Product/output/playwright/workflow-dashboard-mobile-chinese.png`。
- CEO 可读性验收：新增 `老板先看这里` 摘要层后目标测试扩展为 7 passed；浏览器复核桌面和 390px 移动端均显示 `论文生产流水线控制台`、项目目标、当前结论、需要老板判断、下一步动作；旧英文状态未出现，控制台无错误，状态 API 返回 200/no-store，offscreen elements=0。截图为 `Product/output/playwright/workflow-dashboard-desktop-ceo.png`、`Product/output/playwright/workflow-dashboard-mobile-ceo.png`。
- P12 最新浏览器 QA 待本阶段用当前代码服务刷新：目标是桌面 1440px 和移动端 390px 均显示 `P12 DesignSpec 预检已生成`、CEO 摘要、P12-P16 分支、人工验收清单；截图输出到 `Product/output/playwright/workflow-dashboard-p12-design-spec-preflight-desktop.png`、`Product/output/playwright/workflow-dashboard-p12-design-spec-preflight-mobile.png`。
- 正式层边界：该仪表盘只是动态项目控制面，不保存 source contract，不重复写正式 VariableRoleSet，不写 DesignSpec/RunPlan，不创建 run id，不执行模型。

## Latest P11G Verification

- SDD/BDD：`Tasks/parent-education-wage-p11g-source-contract-signoff-workspace-bdd.md`。
- 核心功能：React P11 从长表单升级为 `Source Contract Signoff` 工作台，包含状态条、左侧 `Review queue`、右侧 `Source contract form`、默认折叠的 `Source review kit` 和底部 action bar。
- 用户路径：用户先看 9 个字段的审核队列，再填写 dataset path、reviewer/note、字段来源、evidence level 和逐行 confirmation；保存按钮在缺口存在时继续 disabled。
- 正式层边界：P11G 不保存真实 source contract，不写正式 VariableRoleSet，不写 DesignSpec/RunPlan，不创建 run id，不执行模型；页面明确 `No model run`。
- TDD：`python3 -m pytest tests/test_parent_education_wage_p11_source_metadata_contract.py -q` 新增 P11G 测试后先失败 1 项，原因是 React 尚未暴露 `Source Contract Signoff` workspace；实现后 12 passed。
- 邻近回归：`python3 -m pytest tests/test_parent_education_wage_p9_formal_variable_role_save.py tests/test_parent_education_wage_p10_product_control_ia.py tests/test_parent_education_wage_p11_source_metadata_contract.py -q`，23 passed。
- P2-P11 scoped 回归：`python3 -m pytest tests/test_parent_education_wage_p2_execution_readiness.py tests/test_parent_education_wage_p3_draft_package.py tests/test_parent_education_wage_p4_field_source_candidates.py tests/test_parent_education_wage_p5_variable_role_preflight.py tests/test_parent_education_wage_p6_variable_role_signoff.py tests/test_parent_education_wage_p8_formal_variable_role_approval.py tests/test_parent_education_wage_p9_formal_variable_role_save.py tests/test_parent_education_wage_p10_product_control_ia.py tests/test_parent_education_wage_p11_source_metadata_contract.py -q`，61 passed。
- React build：`cd Product/web-react && npm run build` 通过，仍有既有 Vite chunk size warning。
- 浏览器 smoke：`http://127.0.0.1:8776/?topic=empirical-paper-template-main&mode=human-review&api_base=http://127.0.0.1:8776&v=p11g-signoff-workspace-final-2` 桌面和 390px 移动端均可见 workspace、review queue、source contract form 和 `No model run`；queue items=9、source rows=9、checkboxes=9、保存按钮 disabled、P11G 自身 horizontal overflow=false、action bar 不遮挡字段行。截图为 `Product/output/playwright/product-control-p11g-signoff-workspace-final-desktop.png`、`Product/output/playwright/product-control-p11g-signoff-workspace-final-mobile.png`。
- 独立审查：code-reviewer Agent `Socrates` 窄范围复核 PASS，未发现 P11-Human/P9/P12 绕过、保存门禁绕过、CSS 全局污染或文档阶段误报；唯一低风险建议是后续把 P11G 的静态 React 契约升级为 Playwright/DOM 自动断言。
- 当前真实项目状态：P11G 只是把 P11-Human 做成可用 UI；真实 source contract 尚未由用户保存，P9 仍应阻断。P12 不得启动。

## Latest P11F Verification

- SDD/BDD：`Tasks/parent-education-wage-p11f-human-signoff-review-queue-bdd.md`。
- 核心功能：React P11 在长表单前新增 `Human signoff review queue`，逐项显示 9 个 required source fields 的状态、缺口和下一步动作。
- 用户路径：用户先看队列判断哪些字段只是候选预填、哪些字段还缺 source metadata，再到下方逐行编辑并勾选 human confirmation。
- 正式层边界：P11F 不改后端 payload，不保存 source contract，不写正式 VariableRoleSet，不写 DesignSpec/RunPlan，不创建 run id，不执行模型。
- TDD：`python3 -m pytest tests/test_parent_education_wage_p11_source_metadata_contract.py -q` 新增 P11F 测试后先失败 1 项，原因是 React 尚未暴露 review queue；实现后 11 passed。
- 邻近回归：`python3 -m pytest tests/test_parent_education_wage_p9_formal_variable_role_save.py tests/test_parent_education_wage_p10_product_control_ia.py tests/test_parent_education_wage_p11_source_metadata_contract.py -q`，22 passed。
- P2-P11 scoped 回归：`python3 -m pytest tests/test_parent_education_wage_p2_execution_readiness.py tests/test_parent_education_wage_p3_draft_package.py tests/test_parent_education_wage_p4_field_source_candidates.py tests/test_parent_education_wage_p5_variable_role_preflight.py tests/test_parent_education_wage_p6_variable_role_signoff.py tests/test_parent_education_wage_p8_formal_variable_role_approval.py tests/test_parent_education_wage_p9_formal_variable_role_save.py tests/test_parent_education_wage_p10_product_control_ia.py tests/test_parent_education_wage_p11_source_metadata_contract.py -q`，60 passed。
- React build：`cd Product/web-react && npm run build` 通过，仍有既有 Vite chunk size warning。
- API smoke：`GET http://127.0.0.1:8776/api/v1/projects/proj_empirical_paper_template_main/product-control/p11-source-metadata-contract` 返回 `source_metadata_contract_required`；正式层边界仍为 `can_save_formal_variable_roles=false`、`can_enter_design_spec_preflight=false`、`can_create_run_id=false`、`can_execute_model=false`。
- 浏览器 smoke：`http://127.0.0.1:8776/?topic=empirical-paper-template-main&mode=human-review&api_base=http://127.0.0.1:8776&v=p11f-review-queue` 桌面和 390px 移动端均可见 review queue；queue items=9、source rows=9、row fields=36、checkboxes=9、保存按钮 disabled、readiness 包含 `human_confirmation`；页面级 horizontal overflow=false；console errors=0；截图为 `Product/output/playwright/product-control-p11f-review-queue-desktop.png`、`Product/output/playwright/product-control-p11f-review-queue-mobile.png`。
- 审查说明：已尝试派出独立 code-reviewer Agent，但当前会话 subagent thread 已满，未能启动；本阶段已做主线代码审查、API smoke、浏览器截图和回归测试。后续进入 P11-Human/P9 前仍应再做独立审查。
- 当前真实项目状态：P11F 只是让 P11-Human 签收前的判断更清楚；真实 source contract 尚未由用户保存，P9 仍应阻断。P12 不得启动。

## Latest P11E Verification

- SDD/BDD：`Tasks/parent-education-wage-p11e-human-signoff-readable-rows-bdd.md`。
- 核心功能：React P11 字段来源行新增可见标签 `dataset column`、`source field`、`source path`、`evidence level`；移动端隐藏表头后仍能看懂每个输入框含义。
- 用户路径：P11 仍显示 9 个 source rows、36 个 row fields、9 个独立 human confirmation checkbox；保存按钮在 `human_confirmation` 等缺口存在时继续 disabled。
- 正式层边界：P11E 不改后端 payload，不保存 source contract，不写正式 VariableRoleSet，不写 DesignSpec/RunPlan，不创建 run id，不执行模型。
- TDD：`python3 -m pytest tests/test_parent_education_wage_p11_source_metadata_contract.py -q` 新增 P11E 测试后先失败 1 项，原因是 React 字段行没有可见标签；实现后 10 passed。
- 邻近回归：`python3 -m pytest tests/test_parent_education_wage_p9_formal_variable_role_save.py tests/test_parent_education_wage_p10_product_control_ia.py tests/test_parent_education_wage_p11_source_metadata_contract.py -q`，21 passed。
- P2-P11 scoped 回归：`python3 -m pytest tests/test_parent_education_wage_p2_execution_readiness.py tests/test_parent_education_wage_p3_draft_package.py tests/test_parent_education_wage_p4_field_source_candidates.py tests/test_parent_education_wage_p5_variable_role_preflight.py tests/test_parent_education_wage_p6_variable_role_signoff.py tests/test_parent_education_wage_p8_formal_variable_role_approval.py tests/test_parent_education_wage_p9_formal_variable_role_save.py tests/test_parent_education_wage_p10_product_control_ia.py tests/test_parent_education_wage_p11_source_metadata_contract.py -q`，59 passed。
- React build：`cd Product/web-react && npm run build` 通过，仍有既有 Vite chunk size warning。
- API smoke：`GET http://127.0.0.1:8776/api/v1/projects/proj_empirical_paper_template_main/product-control/p11-source-metadata-contract` 返回 `source_metadata_contract_required`；P9 仍返回 `blocked_missing_dataset_source_metadata`，`can_enter_design_spec_preflight=false`，`can_create_run_id=false`，`can_execute_model=false`。
- 浏览器 smoke：`http://127.0.0.1:8776/?topic=empirical-paper-template-main&mode=human-review&api_base=http://127.0.0.1:8776&v=p11e-readable-rows6` 桌面和 390px 移动端均有 9 个 source rows、36 个字段标签、9 个确认框、disabled 保存按钮和 `human_confirmation` readiness 缺口；页面级 horizontal overflow=false；console errors=0；截图为 `Product/output/playwright/product-control-p11e-readable-rows-desktop.png`、`Product/output/playwright/product-control-p11e-readable-rows-mobile.png`。
- 审查说明：已尝试派出独立 code-reviewer Agent，但当前会话 subagent thread 已满，未能启动；本阶段已做主线代码审查、API smoke、浏览器截图和回归测试。后续进入 P11-Human/P9 前仍应再做独立审查。
- 当前真实项目状态：P11E 让 P11-Human 签收更可读，但真实 source contract 尚未由用户保存，P9 仍应阻断。P12 不得启动。

## Latest P11D Verification

- SDD/BDD：`Tasks/parent-education-wage-p11d-row-human-confirmation-bdd.md`。
- 核心功能：React P11 表单新增逐字段 `confirmed` checkbox；预填候选值不再等于人工确认，未勾选行会进入 `human_confirmation` 缺口。
- 用户路径：页面显示 `confirmed rows：0/9`；保存按钮在 reviewer/note/source row 任一缺口存在时保持 disabled；用户必须逐行确认后才可提交 source contract。
- 正式层边界：P11D 不改 P11 后端 payload，不保存 source contract，不写正式 VariableRoleSet，不写 DesignSpec/RunPlan，不创建 run id，不执行模型。
- TDD：`python3 -m pytest tests/test_parent_education_wage_p11_source_metadata_contract.py -q` 新增 P11D 测试后先失败 1 项，原因是 React 尚未暴露 row human confirmation；实现后 9 passed。
- 邻近回归：`python3 -m pytest tests/test_parent_education_wage_p9_formal_variable_role_save.py tests/test_parent_education_wage_p10_product_control_ia.py tests/test_parent_education_wage_p11_source_metadata_contract.py -q`，20 passed。
- P2-P11 scoped 回归：`python3 -m pytest tests/test_parent_education_wage_p2_execution_readiness.py tests/test_parent_education_wage_p3_draft_package.py tests/test_parent_education_wage_p4_field_source_candidates.py tests/test_parent_education_wage_p5_variable_role_preflight.py tests/test_parent_education_wage_p6_variable_role_signoff.py tests/test_parent_education_wage_p7_variable_role_signoff_ui.py tests/test_parent_education_wage_p8_formal_variable_role_approval.py tests/test_parent_education_wage_p9_formal_variable_role_save.py tests/test_parent_education_wage_p10_product_control_ia.py tests/test_parent_education_wage_p11_source_metadata_contract.py -q`，61 passed。
- React build：`cd Product/web-react && npm run build` 通过，仍有既有 Vite chunk size warning。
- API smoke：`GET http://127.0.0.1:8774/api/v1/projects/proj_empirical_paper_template_main/product-control/p11-source-metadata-contract` 返回 `source_metadata_contract_required`；P9 仍返回 `blocked_missing_dataset_source_metadata`，`can_enter_design_spec_preflight=false`，`can_create_run_id=false`，`can_execute_model=false`。
- 浏览器 smoke：`http://127.0.0.1:8774/?topic=empirical-paper-template-main&mode=human-review&api_base=http://127.0.0.1:8774&v=p11d-row-confirmation` 桌面和 390px 移动端均可见 9 个 source rows 和 9 个 row human confirmation checkbox；保存按钮 disabled；readiness 显示 `human_confirmation`；console errors=0；截图为 `Product/output/playwright/product-control-p11d-row-confirmation-desktop.png`、`Product/output/playwright/product-control-p11d-row-confirmation-mobile.png`。
- 审查说明：已尝试派出独立 code-reviewer Agent，但当前会话 subagent thread 已满，未能启动；本阶段已做主线代码审查、API smoke、浏览器截图和回归测试。后续进入 P11-Human/P9 前仍应再做独立审查。
- 当前真实项目状态：P11D 让 P11-Human 签收更可靠，但真实 source contract 尚未由用户保存，P9 仍应阻断。P12 不得启动。

## Latest P11C Verification

- SDD/BDD：`Tasks/parent-education-wage-p11c-source-contract-readiness-bdd.md`。
- 核心功能：React P11 表单新增 `Source contract readiness`，由 `p11SourceContractMissingItems` 计算 reviewer、note、confirmation、dataset path、parent education construction 和 9 个 source rows 的缺口。
- 用户路径：页面显示 `needs_source_metadata_review` 或 `ready_to_save_source_contract`；缺口存在时保存按钮禁用，并显示具体缺口，如 `reviewer；note` 或 `ln_wage:source_path`。
- 正式层边界：P11C 不改 P11 后端契约，不保存 source contract，不写正式 VariableRoleSet，不写 DesignSpec/RunPlan，不创建 run id，不执行模型。
- TDD：`python3 -m pytest tests/test_parent_education_wage_p11_source_metadata_contract.py -q` 新增 P11C 测试后先失败 1 项，原因是 React 尚未暴露 readiness check；实现后 8 passed。
- 邻近回归：`python3 -m pytest tests/test_parent_education_wage_p9_formal_variable_role_save.py tests/test_parent_education_wage_p10_product_control_ia.py tests/test_parent_education_wage_p11_source_metadata_contract.py -q`，19 passed。
- P2-P11 scoped 回归：`python3 -m pytest tests/test_parent_education_wage_p2_execution_readiness.py tests/test_parent_education_wage_p3_draft_package.py tests/test_parent_education_wage_p4_field_source_candidates.py tests/test_parent_education_wage_p5_variable_role_preflight.py tests/test_parent_education_wage_p6_variable_role_signoff.py tests/test_parent_education_wage_p7_variable_role_signoff_ui.py tests/test_parent_education_wage_p8_formal_variable_role_approval.py tests/test_parent_education_wage_p9_formal_variable_role_save.py tests/test_parent_education_wage_p10_product_control_ia.py tests/test_parent_education_wage_p11_source_metadata_contract.py -q`，60 passed。
- React build：`cd Product/web-react && npm run build` 通过，仍有既有 Vite chunk size warning。
- API smoke：`GET http://127.0.0.1:8773/api/v1/projects/proj_empirical_paper_template_main/product-control/p11-source-metadata-contract` 返回 `source_metadata_contract_required`；P9 仍返回 `blocked_missing_dataset_source_metadata`，`can_create_run_id=false`，`can_execute_model=false`。
- 浏览器 smoke：`http://127.0.0.1:8773/?topic=empirical-paper-template-main&mode=human-review&api_base=http://127.0.0.1:8773&v=p11c-readiness` 桌面和 390px 移动端均可见 `Source contract readiness`、`needs_source_metadata_review` 和 9 个 source rows；保存按钮 disabled；console errors=0；截图为 `Product/output/playwright/product-control-p11c-readiness-desktop.png`、`Product/output/playwright/product-control-p11c-readiness-mobile.png`。
- 当前真实项目状态：P11C 让 P11-Human 更可操作，但真实 source contract 尚未由用户保存，P9 仍应阻断。P12 不得启动。

## Latest P11B Verification

- SDD/BDD：`Tasks/parent-education-wage-p11b-per-field-source-confirmation-bdd.md`。
- 核心功能：React P11 表单新增 `Per-field source confirmation`，按 9 个 required source fields 渲染 dataset column、source field、source path、evidence level 输入行。
- 用户路径：用户不再必须手写 `field_bindings` JSON；保存时由 `sourceFieldRows` 生成原有 P11 POST payload，`field_bindings JSON preview` 只作为可审计预览。
- 正式层边界：P11B 不改后端正式写入规则，不保存 source contract，不写正式 VariableRoleSet，不写 DesignSpec/RunPlan，不创建 run id，不执行模型。
- TDD：`python3 -m pytest tests/test_parent_education_wage_p11_source_metadata_contract.py -q` 新增 P11B 测试后先失败 1 项，原因是 React 尚未暴露 per-field editor；实现后 7 passed。
- 邻近回归：`python3 -m pytest tests/test_parent_education_wage_p9_formal_variable_role_save.py tests/test_parent_education_wage_p10_product_control_ia.py tests/test_parent_education_wage_p11_source_metadata_contract.py -q`，18 passed。
- P2-P11 scoped 回归：`python3 -m pytest tests/test_parent_education_wage_p2_execution_readiness.py tests/test_parent_education_wage_p3_draft_package.py tests/test_parent_education_wage_p4_field_source_candidates.py tests/test_parent_education_wage_p5_variable_role_preflight.py tests/test_parent_education_wage_p6_variable_role_signoff.py tests/test_parent_education_wage_p7_variable_role_signoff_ui.py tests/test_parent_education_wage_p8_formal_variable_role_approval.py tests/test_parent_education_wage_p9_formal_variable_role_save.py tests/test_parent_education_wage_p10_product_control_ia.py tests/test_parent_education_wage_p11_source_metadata_contract.py -q`，59 passed。
- React build：`cd Product/web-react && npm run build` 通过，仍有既有 Vite chunk size warning。
- API smoke：`GET http://127.0.0.1:8772/api/v1/projects/proj_empirical_paper_template_main/product-control/p11-source-metadata-contract` 返回 `source_metadata_contract_required`，P9 仍返回 `blocked_missing_dataset_source_metadata`，`can_create_run_id=false`，`can_execute_model=false`。
- 浏览器 smoke：`http://127.0.0.1:8772/?topic=empirical-paper-template-main&mode=human-review&api_base=http://127.0.0.1:8772&v=p11b-field-editor` 桌面和 390px 移动端均可见 `Per-field source confirmation`、`field_bindings JSON preview` 和 9 个 source rows，console errors=0；截图为 `Product/output/playwright/product-control-p11b-field-editor-desktop.png`、`Product/output/playwright/product-control-p11b-field-editor-mobile.png`。
- 独立审查：本轮尝试派出 code-reviewer Agent，但当前会话 subagent thread 已满，未能启动；已做本地手动审查和运行态截图检查。后续进入 P11-Human/P9 前应再做一次独立审查。
- 当前真实项目状态：P11B 只是让人工 source contract 签收更可操作；真实 source contract 尚未由用户保存，P9 仍应阻断。P12 不得启动。

## Latest P11A Verification

- SDD/BDD：`Tasks/parent-education-wage-p11a-source-contract-review-kit-bdd.md`。
- 核心功能：P11 GET 新增 `source_contract_review_kit`，从 P5/P4 证据和项目 Data 目录生成 dataset path candidates、field review items、recommended source、missing-source 状态和 no-model boundary。
- 用户路径：React P11 面板在保存表单前展示 `Source review kit`、recommended dataset path、field review items 和字段候选，用户不再只面对 `field_bindings` JSON textarea。
- 正式层边界：P11A 只读生成候选签收包，不替用户保存 source contract，不写正式 VariableRoleSet，不写 DesignSpec/RunPlan，不创建 run id，不执行模型。
- TDD：`python3 -m pytest tests/test_parent_education_wage_p11_source_metadata_contract.py -q` 首次新增 P11A 测试失败 2 项，原因是 API 和 React 尚未暴露 review kit；实现后 6 passed。
- 邻近回归：`python3 -m pytest tests/test_parent_education_wage_p9_formal_variable_role_save.py tests/test_parent_education_wage_p10_product_control_ia.py tests/test_parent_education_wage_p11_source_metadata_contract.py -q`，17 passed。
- P1-P11 scoped 回归：`python3 -m pytest tests/test_parent_education_wage_literature_evidence_ledger.py tests/test_parent_education_wage_data_field_binding_ledger.py tests/test_parent_education_wage_method_execution_ledger.py tests/test_parent_education_wage_p2_execution_readiness.py tests/test_parent_education_wage_p3_draft_package.py tests/test_parent_education_wage_p4_field_source_candidates.py tests/test_parent_education_wage_p5_variable_role_preflight.py tests/test_parent_education_wage_p6_variable_role_signoff.py tests/test_parent_education_wage_p7_variable_role_signoff_ui.py tests/test_parent_education_wage_p8_formal_variable_role_approval.py tests/test_parent_education_wage_p9_formal_variable_role_save.py tests/test_parent_education_wage_p10_product_control_ia.py tests/test_parent_education_wage_p11_source_metadata_contract.py -q`，73 passed。
- Python 编译：`python3 -m py_compile Product/backend/product_control_p11_source_metadata_service.py Product/app.py tests/test_parent_education_wage_p11_source_metadata_contract.py` 通过。
- React build：`cd Product/web-react && npm run build` 通过，仍有既有 Vite chunk size warning。
- API smoke：`GET http://127.0.0.1:8771/api/v1/projects/proj_empirical_paper_template_main/product-control/p11-source-metadata-contract` 返回 `source_metadata_contract_required`，`source_contract_review_kit.status=needs_human_source_contract_review`，`field_item_count=9`，`can_execute_model=false`；P9 仍返回 `blocked_missing_dataset_source_metadata`。
- 浏览器 smoke：`http://127.0.0.1:8771/?topic=empirical-paper-template-main&mode=human-review&api_base=http://127.0.0.1:8771&v=p11a-review-kit` 桌面和 390px 移动端均可见 `Source review kit` 和 `recommended dataset path`，console errors=0；截图为 `Product/output/playwright/product-control-p11a-review-kit-desktop.png`、`Product/output/playwright/product-control-p11a-review-kit-mobile.png`。
- 当前真实项目状态：P11A 已让人工 source contract 签收更可操作；真实 source contract 尚未由用户保存，P9 仍应阻断。P12 不得启动。

## Latest P11 Verification

- BDD：`Tasks/parent-education-wage-p11-source-metadata-contract-bdd.md`。
- 核心功能：新增 `GET/POST /api/v1/projects/{project_id}/product-control/p11-source-metadata-contract`；P11 读取最新 editable draft、P8 approval 和 P9 source metadata 缺口，POST 只把完整 source contract 写回 `state/product/variable_roles_drafts.json` 的最新草稿。
- 用户路径：React 当前门禁详情新增 `P11 Source Metadata` 表单，支持填写 dataset path、`field_bindings` JSON、reviewer、note、确认码和 `parent_education construction`；保存成功后刷新 P9 状态。
- 正式层边界：P11 不写正式 `state/product/variable_roles.json`，不写 DesignSpec、RunPlan，不创建 run id，不执行模型。完整 P11 只让 P9 GET 变成 `formal_variable_role_save_ready`，仍需用户在 P9 单独保存正式变量表。
- TDD：`python3 -m pytest tests/test_parent_education_wage_p11_source_metadata_contract.py -q` 首次失败 4 项，原因是 P11 API、服务和 React 表单不存在；实现后 4 passed。
- 邻近回归：`python3 -m pytest tests/test_parent_education_wage_p9_formal_variable_role_save.py tests/test_parent_education_wage_p10_product_control_ia.py tests/test_parent_education_wage_p11_source_metadata_contract.py -q`，15 passed。
- Python 编译：`python3 -m py_compile Product/backend/product_control_p11_source_metadata_service.py Product/backend/product_control_p9_variable_role_save_service.py Product/app.py tests/test_parent_education_wage_p11_source_metadata_contract.py` 通过。
- React build：`cd Product/web-react && npm run build` 通过，仍有既有 Vite chunk size warning。
- 当前真实项目状态：P11 产品路径已具备；真实 source contract 尚未由用户填写，P9 仍应返回 `blocked_missing_dataset_source_metadata`。P12 不得启动。

## Latest P10 Verification

- SDD：`Tasks/north-star-product-plan.md`，把北极星目标固定为本科生可用、可审计、可交付的论文生产流水线，首交付物为 `paper_draft.docx / paper_draft.pdf`。
- BDD：`Tasks/parent-education-wage-p10-product-control-ia-bdd.md`。
- 核心功能：React 主入口先显示 Product Control 当前门禁摘要，再显示研究阶段导航；P0-P8 历史阶段默认折叠，P9 当前阻断详情仍可见。
- 当前门禁：P9 状态为 `blocked_missing_dataset_source_metadata`，页面明确显示不能保存正式变量表、不能创建 run id、不能跑模型。
- 正式层边界：P10 只整理 Product Control 信息架构，不补 source metadata，不写正式 VariableRoleSet、DesignSpec、RunPlan，不创建 run id，不执行模型。
- TDD：`python3 -m pytest tests/test_parent_education_wage_p10_product_control_ia.py -q` 首次失败 3 项，原因是当前门禁摘要、历史折叠和 Product Control 优先级尚未实现；实现后 P10 目标测试通过。
- 回归：`python3 -m pytest tests/test_parent_education_wage_p10_product_control_ia.py tests/test_product_control_p0_stage_panel.py tests/test_web_react_api_base_contract.py -q`，15 passed, 11 subtests passed。
- P1-P10 scoped 回归：`python3 -m pytest tests/test_parent_education_wage_literature_evidence_ledger.py tests/test_parent_education_wage_data_field_binding_ledger.py tests/test_parent_education_wage_method_execution_ledger.py tests/test_parent_education_wage_p2_execution_readiness.py tests/test_parent_education_wage_p3_draft_package.py tests/test_parent_education_wage_p4_field_source_candidates.py tests/test_parent_education_wage_p5_variable_role_preflight.py tests/test_parent_education_wage_p6_variable_role_signoff.py tests/test_parent_education_wage_p7_variable_role_signoff_ui.py tests/test_parent_education_wage_p8_formal_variable_role_approval.py tests/test_parent_education_wage_p9_formal_variable_role_save.py tests/test_parent_education_wage_p10_product_control_ia.py -q`，67 passed。
- React build：`cd Product/web-react && npm run build` 通过，仍有既有 Vite chunk size warning。
- API smoke：`GET http://127.0.0.1:8769/api/v1/projects/proj_empirical_paper_template_main/product-control/p9-variable-role-formal-save` 返回 `blocked_missing_dataset_source_metadata`，且 `can_save_formal_variable_roles=false`、`can_create_run_id=false`、`can_execute_model=false`。
- 浏览器：`http://127.0.0.1:8769/?topic=empirical-paper-template-main&mode=human-review&api_base=http://127.0.0.1:8769&v=p10-ia2` 桌面和 390px 移动端均可见当前门禁摘要、折叠历史、P9 阻断和禁用保存状态，且无“运行模型”入口；截图为 `output/playwright/product-control-p10-current-gate.png`、`output/playwright/product-control-p10-mobile.png`。
- 审查说明：本轮未能派出新的独立 Agent 复核，因为当前会话可用 thread 已满；已做手动窄范围审查，并修复了一个会误导用户的硬编码摘要问题，使当前门禁摘要从 P9 API 状态动态读取。

## Latest P9 Verification

- BDD：`Tasks/parent-education-wage-p9-formal-variable-role-save-bdd.md`。
- 核心功能：新增 `GET/POST /api/v1/projects/{project_id}/product-control/p9-variable-role-formal-save`；P9 只能保存当前最新 P7 draft 且必须已有有效 P8 approval。
- 门禁边界：P9 POST 要求 decision、reviewer、note、确认码 `save_formal_variable_roles_from_p8_approved_draft`、source_draft_id、dataset_path 和 roles；payload 不能替换已批准 roles 或 dataset。
- Source metadata 边界：没有 dataset path、数据文件不存在，或 role 字段缺少 source metadata 时，P9 返回 `blocked_missing_dataset_source_metadata`，不写正式 `state/product/variable_roles.json`。
- 审查修复：独立 code-reviewer 指出 P9 曾把只有 `dataset_column` 的弱绑定误判为完整 source metadata。已收紧为 `source_contract.status=complete`，直接字段绑定必须有 `source_path` 和 `evidence_level`，派生变量必须有 construction 且 source fields 也满足同样审计字段。
- 正式层边界：P9 只允许在完整 source contract 下写正式 VariableRoleSet；不写 DesignSpec、RunPlan，不创建 run id，不执行模型。
- 真实项目状态：新验收服务为 `http://127.0.0.1:8769/?topic=empirical-paper-template-main&mode=human-review&api_base=http://127.0.0.1:8769`。P8 已记录，P9 返回 `blocked_missing_dataset_source_metadata`；当前 source contract 仍为 incomplete，正式保存、DesignSpec、RunPlan、run id 和模型执行全部关闭。
- 测试：P9 目标测试 7 passed；P6/P7/P8/P9 回归 26 passed；P1-P9 父母教育工资回归 63 passed；产品控制 scoped 回归 14 passed；Python compile 通过；React build 通过但保留既有 Vite chunk size warning。
- 浏览器：桌面与 390px 移动端均可见 P9 面板、缺失字段和禁用保存状态，且无“运行模型”入口；截图为 `output/playwright/product-control-p9-desktop.png`、`output/playwright/product-control-p9-mobile.png`。
- 恢复后复核：`GET http://127.0.0.1:8769/api/v1/projects/proj_empirical_paper_template_main/product-control/p9-variable-role-formal-save` 仍返回 `blocked_missing_dataset_source_metadata`，且 `can_save_formal_variable_roles=false`、`can_create_run_id=false`、`can_execute_model=false`；Playwright CLI 快照确认 8769 页面可打开、P9 面板可见、保存按钮禁用。

## Latest P8 Verification

- BDD：`Tasks/parent-education-wage-p8-formal-variable-role-approval-bdd.md`。
- 核心功能：新增 `GET/POST /api/v1/projects/{project_id}/product-control/p8-variable-role-approval`；P8 要求 reviewer、note 和确认码 `approve_formal_variable_roles_after_review`；审批只写 `state/product/variable_role_formal_approvals.json`，不直接写正式 `variable_roles.json`。
- 门禁边界：没有 P7/P6 editable draft 时，P8 返回 `blocked_missing_p7_variable_role_draft`；有 P7 draft 但缺 P8 approval 时，旧 `PUT /variable-roles` 仍 409；P8 approval 必须绑定当前最新 `source_draft_id` 和审批当刻的 `source_draft_roles` 快照，正式 PUT 的 roles 必须等于该快照，避免旧 approval 解锁新 draft、批准 A 后写入 B，或同一 draft id 被篡改后继续放行。
- 正式层边界：P8 不写 DesignSpec、RunPlan，不创建 run id，不执行模型；测试验证 `design_spec.json` 和 `run_plan.json` 哈希不变。
- 真实项目状态：`GET http://127.0.0.1:8768/api/v1/projects/proj_empirical_paper_template_main/product-control/p8-variable-role-approval` 返回 200，状态为 `blocked_missing_p7_variable_role_draft`，`can_write_formal_variable_roles=false`，`can_write_design_spec=false`，`can_write_run_plan=false`，`can_create_run_id=false`，`can_execute_model=false`。
- 独立审查：code-reviewer Agent `Mendel` 初审为 request changes；指出旧 P8 approval 可解锁新 draft、且 approval 未绑定正式 PUT roles。code-reviewer Agent `Bernoulli` 复审继续 request changes；指出同一 draft id 的 roles 若在 approval 后被篡改，旧逻辑仍会放行。已补三条回归测试并收紧后端门禁：正式保存前必须验证 approval 对当前最新 draft 生效，且 latest draft roles、approval `source_draft_roles`、PUT roles 三者完全一致。code-reviewer Agent `Ampere` 最终窄范围复核 PASS。
- 测试：P8 目标测试 8 passed；P6/P7/P8 回归 19 passed；P1-P8 父母教育工资回归 56 passed；产品控制 scoped 回归 14 passed；Python compile 通过；React build 通过但保留既有 Vite chunk size warning。
- 浏览器：新验收服务 `http://127.0.0.1:8768/?topic=empirical-paper-template-main&mode=human-review&api_base=http://127.0.0.1:8768` 可见 P8 审批面板、禁用态输入、`blocked_missing_p7_variable_role_draft` 和“不写 RunPlan；不跑模型”；桌面与 390px 移动端截图为 `artifacts/ui-checks/product-control-p8-variable-role-approval-desktop.png`、`artifacts/ui-checks/product-control-p8-variable-role-approval-mobile.png`。

## Latest P7 Verification

- BDD：`Tasks/parent-education-wage-p7-variable-role-signoff-ui-bdd.md`。
- 核心功能：P6 signoff API 返回 `recommended_decisions`；React P6 面板展示五项可编辑确认输入；按钮为“确认并生成可编辑草稿”；提交 payload 固定 `promotion_target=editable_draft`、`allow_formal_write=false`。
- 推荐默认值：`confirmed_current_p4_sources`、`max(father_education, mother_education)`、`control_or_heterogeneity_candidate`、`ln_wage_with_age_female_urban_edu_last_experience`、`draft_only_no_formal_write`。
- 真实项目边界：只刷新 P6 GET/POST 和页面状态；未替用户调用真实项目 `/promote`；未写新的正式 VariableRoleSet、DesignSpec、RunPlan；未创建 run id；未执行回归。
- 审查闭环：独立 code-reviewer 指出 P7 promotion 后旧 `PUT /variable-roles` 会误开正式写入。已补回归测试：完整 P7 promotion 后再调用正式保存必须返回 409，并验证 `variable_roles.json`、`design_spec.json`、`run_plan.json` 哈希不变。后端门禁已改为 P7 draft != formal approval，正式写入需 P8 单独批准。
- 测试：P7 目标测试 3 passed；P6+P7 回归 11 passed；P2-P7 回归 33 passed；产品控制 scoped 回归 71 passed, 11 subtests passed；Python compile 通过；React build 通过但保留既有 Vite chunk size warning。
- API：P6 GET 返回 `variable_role_signoff_required` 和五项 `recommended_decisions`；P6 POST 返回 201；旧正式保存口返回 409 `p6_variable_role_draft_required`。测试覆盖 P7 promoted draft 之后正式保存仍返回 409。
- 浏览器：真实入口 `http://127.0.0.1:8766/?topic=empirical-paper-template-main&mode=human-review&api_base=http://127.0.0.1:8766` 可见五项输入、默认值、草稿按钮和“不写正式 VariableRoleSet；不跑模型”；桌面与 390px 移动端均无横向溢出，console errors=0；截图为 `artifacts/ui-checks/product-control-p7-variable-role-signoff-desktop.png`、`artifacts/ui-checks/product-control-p7-variable-role-signoff-mobile.png`。

## Latest P6 Verification

- BDD：`Tasks/parent-education-wage-p6-variable-role-signoff-bdd.md`。
- 真实产物：`Results/json/parent_education_wage_p6_variable_role_signoff.json`、`Reviews/parent_education_wage_p6_variable_role_signoff.md`。
- 核心状态：`status=variable_role_signoff_required`；签收项 5 个；签收完整后可进入 `editable_draft`；正式写回仍为 `can_write_formal_variable_roles=false`。
- 真实项目边界：未执行 promotion payload；未写新的正式 VariableRoleSet、DesignSpec、RunPlan；未创建 run id；未执行回归。
- 审查闭环：独立 code-reviewer 指出旧 `PUT /variable-roles` 可绕过 P6、formal target 语义不稳、固定 draft id 会覆盖旧草稿、React 文案偏强；均已补测试和修复。
- 测试：P6 目标测试 8 passed；P2-P6 回归 30 passed；产品控制 scoped 回归 68 passed, 11 subtests passed；Python compile 通过；React build 通过但保留既有 Vite chunk size warning。
- API/浏览器：P6 GET 返回 200、POST 返回 201，均为 `variable_role_signoff_required`；旧正式保存口在无 P6 promoted draft 时返回 409 `p6_variable_role_draft_required`；浏览器截图 `artifacts/ui-checks/product-control-p6-variable-role-signoff.png` 可见 P6 签收状态、`editable_draft`、`formal write=false`，无横向溢出、console error 为 0。

## Latest P5 Verification

- BDD：`Tasks/parent-education-wage-p5-variable-role-preflight-bdd.md`。
- 资源调研：`outputs/parent_education_wage_p5_resource_research.md`，provenance sidecar 为 `outputs/parent_education_wage_p5_resource_research.provenance.md`。
- 真实产物：`Results/json/parent_education_wage_p5_variable_role_preflight.json`、`Reviews/parent_education_wage_p5_variable_role_preflight.md`。
- 核心状态：`status=variable_role_preflight_ready_for_review`；outcome 草案 `ln_wage`；treatment 草案 `parent_education`；构造建议 `max(father_education, mother_education)`；controls 草案 `age/female/urban/edu_last/experience`。
- 正式层边界：`can_write_formal_variable_roles=false`；未写正式 VariableRoleSet、DesignSpec、RunPlan；未创建 run id；未执行回归。
- 人工确认项：`confirm_preferred_cfps_wave`、`confirm_parent_education_construction`、`confirm_hukou_role`、`confirm_outcome_and_controls`、`approve_before_formal_variable_roles_write`。
- 测试：P5 目标测试 6 passed；P2/P3/P4/P5 回归 22 passed；产品控制 scoped 回归 60 passed, 11 subtests passed；Python compile 通过；React build 通过但保留既有 Vite chunk size warning。
- API/浏览器：`GET/POST /api/v1/projects/proj_empirical_paper_template_main/product-control/p5-variable-role-preflight` 返回 `variable_role_preflight_ready_for_review`；浏览器截图 `artifacts/ui-checks/product-control-p5-variable-role-preflight.png` 可见 P5 面板、`parent_education=requires_human_confirmation`、`formal write=false`、无横向溢出、console error 为 0。
- 独立审查：第三方 code-reviewer Agent `Newton` 返回 no blocking findings；其指出缺少 P1-B/P2 输入缺失场景测试，已闭环补 `input_warnings` 和缺失输入测试。

## Latest P4 Verification

- BDD：`Tasks/parent-education-wage-p4-field-source-bdd.md`。
- 真实产物：`Results/json/parent_education_wage_p4_field_source_candidates.json`、`Reviews/parent_education_wage_p4_field_source_candidates.md`。
- 真实数据扫描：选中 `/Users/mahaoxuan/Desktop/论文核心素材库/01_原始数据/实证数据库/A001CFPS中国家庭追踪调查`；metadata-only 扫描 36 个 `.dta`、21546 个 Stata 字段标签；生成 52 个候选。
- 核心状态：`father_education=candidate_found`、`mother_education=candidate_found`、`parent_education=constructable_needs_review`、`hukou=candidate_found`。
- 测试：P2/P3/P4 回归 16 passed；产品控制 scoped 回归 54 passed, 11 subtests passed；Python compile 通过；React build 通过但保留既有 Vite chunk size warning。
- API/浏览器：`GET/POST /api/v1/projects/proj_empirical_paper_template_main/product-control/p4-field-source-candidates` 返回 `field_source_candidates_ready_for_review`；浏览器截图 `artifacts/ui-checks/product-control-p4-field-source.png`。

## Phases And Acceptance Criteria

### Phase 0 - Project Audit And Workflow Planning

目标：确认真实项目结构、当前阶段、入口错位、后续连续执行边界。

验收标准：

- `WORKFLOW_STATUS.md` 存在，并写明当前阶段、完成阶段、剩余阶段、停机条件、禁改范围。
- 明确 `Product/web-react`/`Product/web-dist` 是当前主产品入口，`Product/web` 是 legacy。
- 明确 P0 已有能力与当前缺口：P0 backend/API 可用，但主 React UI 尚未接入。
- 后续阶段都有可验证验收标准和最小验证命令。

最小验证：

- `test -f WORKFLOW_STATUS.md`
- `rg -n "WEB_DIST_ROOT|/legacy|product-control/p0-phase" Product/app.py`
- `rg -n "AgentTaskQueuePanel|SystemStatusBar|product-control" Product/web-react/src tests/test_*product_control* tests/test_*react*`

状态：completed

### Phase 1 - Current React Entrypoint Recovery And Baseline

目标：先把当前 React 主入口作为唯一产品开发目标，避免继续在 legacy 页面上误开发。

验收标准：

- React 主入口的阶段结构、状态栏、Agent Queue、执行面和验收面被整理成当前可信地图。
- P0/P1 后续 UI 只规划进入 `Product/web-react/src`，legacy 只保留兼容说明。
- 建立 scoped baseline：React 构建、React 静态契约、P0 API 合同分别可运行或明确失败原因。
- 在 `WORKFLOW_STATUS.md` 中记录当前 React 已有能力、缺口、测试结果。

预计修改范围：

- `WORKFLOW_STATUS.md`
- `Tasks/review.md`
- `Tasks/todo.md`
- 只在必要时改 `Product/web-react/src/*` 的命名/入口接线，不做视觉重设计

最小验证：

- `cd Product/web-react && npm run build`
- `python3 -m pytest tests/test_web_react_api_base_contract.py tests/test_p3_react_input_tabs.py -q`
- `python3 -m pytest tests/test_product_control_p0_phase.py -q`

状态：completed

### Phase 2 - Product Control P0 Port To React Main UI

目标：把 P0 控制能力从 legacy 工作台迁入当前 React 主入口，并保持只读/显式刷新/不自动派工的边界。

验收标准：

- React 主入口可见 `产品控制 P0` 或等价产品控制区，展示 topic、P0 状态、Agent task 数、Evidence Audit、needs_evidence、formal boundary、portfolio script。
- React 使用 `GET /api/v1/projects/{project_id}/product-control/p0-phase` 读取已有报告；刷新必须显式调用 POST。
- P0 UI 不提供自动执行 Agent 的入口，只显示 `dispatch_review_required` 或等价人工审阅状态。
- Legacy 面板不再被描述为当前产品入口；文档和验收说明同步纠偏。
- 新增或迁移测试覆盖 React 主入口，而不是只测 `Product/web`。

预计修改范围：

- `Product/web-react/src/App.tsx`
- `Product/web-react/src/components/ProductControlP0Panel.tsx` 或同级现有组件
- `Product/web-react/src/styles.css`
- `tests/test_*product_control*` 中新增 React 主入口契约测试
- `Tasks/review.md`
- `WORKFLOW_STATUS.md`

最小验证：

- `cd Product/web-react && npm run build`
- `python3 -m pytest tests/test_product_control_p0_phase.py tests/test_product_control_p0_stage_panel.py -q`
- 新增 React P0 契约测试

状态：completed

### Phase 3 - P1-A Real Literature And Citation Evidence Chain

目标：把 P0 的 `真实文献候选/引用核验` 缺口推进为可审计的 P1-A 文献证据链。

验收标准：

- 生成固定 Demo 题目的 literature candidate ledger，区分 seed、candidate、verified、rejected。
- 每条可用文献必须有来源、题目、作者/年份、链接或本地来源、适配理由、引用状态。
- 不能把未核验来源写入正式 bibliography 或正式论文。
- Agent Queue/产品控制面能显示 P1-A 状态和剩余缺口。
- 无外部访问或密钥时，必须以 local/manual-assisted evidence 记录限制，不伪造已核验。

预计修改范围：

- `Product/backend/*literature*` 或新增小型 evidence service
- `Program/*literature*` 或 `scripts/*literature*`
- `Results/json/*literature*`
- `Reviews/*literature*`
- `Tasks/parent-education-wage/*`
- `Product/web-react/src/*` 只接入状态展示
- `WORKFLOW_STATUS.md`

最小验证：

- 文献 ledger schema/contract 测试
- 相关 Python 编译
- 产品控制 API 或 React 状态展示测试

状态：completed

### Phase 4 - P1-B Real Data Field Binding And Variable Role Evidence

目标：把 `真实数据字段绑定与变量角色确认` 缺口推进为可审阅证据，而不是让题目、变量和数据各说各话。

验收标准：

- 固定 Demo 题目的 outcome、treatment/exposure、controls、sample、time/unit 字段有候选来源和证据等级。
- 变量角色先进入 draft/candidate，不直接覆盖正式 `state/product/variable_roles.json`。
- 数据字段绑定必须记录来源文件、字段名、标签/类型、样本覆盖、缺失或不可用原因。
- 产品面显示哪些变量已可用、哪些仍缺证据、哪些需要人工确认。
- 不把 CHARLS/CFPS/CGSS 等数据源混用成一个未说明的数据事实。

预计修改范围：

- `Product/backend/variable_role_service.py` 或相邻服务
- `Results/json/*variable*`
- `Reviews/*variable*`
- `Tasks/parent-education-wage/*`
- `Product/web-react/src/*` 状态展示
- `WORKFLOW_STATUS.md`

最小验证：

- 变量候选/草稿 contract 测试
- 不覆盖正式变量文件的回归测试
- scoped Python 编译

状态：completed

### Phase 5 - P1-C Method Execution Evidence And Run Ledger

目标：把 `方法执行 run id 和结果证据` 做成可复现、可审计的执行账本。

验收标准：

- 只有通过方法前置条件的设计允许进入执行；blocked DID/IV/RDD 等方法必须说明缺口。
- 执行结果必须包含 run id、输入数据指纹、公式/模型、样本量、主要估计量、诊断、artifact path。
- StatsPAI 只在数据清洗后用于 EDA、pre-flight、识别/估计、诊断/robustness；不调用 `sp.paper()` 生成正式论文。
- 方法执行证据可以被 Results/Draft/Verifier 消费，但不能直接覆盖正式 manuscript。
- 失败运行也要留下 failure ledger，不能静默吞掉。

预计修改范围：

- `Product/backend/execution_backend_service.py`
- `Product/backend/statspai_adapter.py`
- `Product/backend/project_service.py`
- `Program/*execution*`
- `Results/json/*method_execution*`
- `Reviews/*execution*`
- `Product/web-react/src/*` 状态展示
- `WORKFLOW_STATUS.md`

最小验证：

- method execution contract 测试
- `python3 -m py_compile` scoped 后端文件
- 能生成或读取一个 local execution/failure ledger

状态：completed

### Phase 6 - Acceptance Package, Cleanup, And Handoff

目标：形成可交付的 Demo/MVP 验收包，清楚说明功能、证据等级、不能越界的正式层边界和下一阶段。

验收标准：

- React 主入口、P0/P1 状态、证据链、执行账本和验收面可以串起来说明。
- `WORKFLOW_STATUS.md`、`Tasks/review.md`、`Tasks/handoff.md`、`Tasks/todo.md` 反映真实状态。
- scoped 测试、构建、编译结果记录完整；全量失败若仍存在，必须分类列明。
- legacy 边界明确：可保留，但不是主产品验收入口。
- 不遗留“Demo 已等于完整产品”的表述；固定题目只作为产品链路压力测试样例。

预计修改范围：

- `WORKFLOW_STATUS.md`
- `Tasks/review.md`
- `Tasks/handoff.md`
- `Tasks/todo.md`
- `docs/product-control/*`
- 可能新增 `Reviews/*acceptance*`

最小验证：

- scoped pytest suite
- React build
- Python compile for touched backend/program files
- API smoke check if local server is running or can be started without new dependency

状态：completed

## Stop Conditions

必须停止并询问用户的情况：

1. 需要删除或大规模重写现有文件。
2. 需要安装新依赖。
3. 需要访问外部服务、账号、密钥或付费 API。
4. 同一阶段测试连续失败两次，且无法通过缩小范围定位。
5. 发现当前目标和项目现有结构发生不可调和冲突。
6. 需要用户做产品决策，例如是否改变目标用户、是否替换 Demo 题目、是否批准正式论文写回。

## No-Touch Scope

未经明确授权，不允许改动：

- 原始数据、外部数据库文件和任何不可逆数据移动。
- `.env*`、密钥、账号配置、外部服务凭据。
- 正式 manuscript、正式 bibliography、正式 submission/package 产物。
- `state/product/variable_roles.json`、`state/product/design_spec.json`、`state/product/run_plan.json` 等已确认正式状态，除非阶段验收明确要求且有测试保护。
- `Product/web-dist/*` 的手工编辑；如需更新，只能由 `Product/web-react` build 产出。
- legacy UI 的删除或大规模重写；legacy 只能被标注为兼容/调试入口。
- 与当前阶段无关的大范围格式化、重命名、目录重组。
- 把固定 Demo 题目硬编码成产品全局唯一题目。
- 把 P0/P1 候选证据包装成正式论文结论。

## Current Phase Log

### P2 - Execution Readiness

修改：

- 新增 `Tasks/parent-education-wage-p2-execution-readiness-bdd.md`，把字段补证、变量口径草案、设计草案去污染、执行准入和产品面状态定义成 BDD。
- 新增 `Program/workbench/parent_education_wage_execution_readiness.py` 和 `Program/parent_education_wage_execution_readiness.py`，生成 P2 执行准入账本。
- 新增 `Product/backend/product_control_p2_execution_readiness_service.py`，并在 `Product/app.py` 暴露 `GET/POST /api/v1/projects/{project_id}/product-control/p2-execution-readiness`。
- 更新 `Product/web-react/src/components/ProductControlP0Panel.tsx` 和 `Product/web-react/src/styles.css`，在当前 React 产品控制面展示 `P2 执行准入`，刷新必须显式 POST。
- 修复 `Tasks/parent-education-wage/design.json` 的旧 robot code stub；只修改任务层草案，不写正式 `state/product/design_spec.json`。
- 生成 `Results/json/parent_education_wage_p2_execution_readiness.json` 和 `Reviews/parent_education_wage_p2_execution_readiness.md`。

验收结果：

- 当前 P2 状态为 `blocked_missing_parent_education_fields`，`execution_preflight_allowed=false`，`run_id=null`。
- `hukou` 找到候选字段：`qa2`、`qa201acode`、`qa302`、`qa402`、`qn2031`、`qa201ccode_id`，但只是候选，尚未写正式变量角色。
- `father_education`、`mother_education`、`parent_education` 仍未在当前字段来源中找到可绑定候选。
- 变量口径只生成 draft：`parent_education` 可考虑 `max(father_education, mother_education)`、`mean(...)` 或父母分别入模，必须人工确认。
- P2 重新刷新 P1-C 后，`design_code_stub_topic_contamination` 不再是阻断原因；P1-C 当前只剩 `missing_required_fields`。
- 正式层边界保持：不写 `state/product/variable_roles.json`、`state/product/design_spec.json`、`state/product/run_plan.json`，不调用 StatsPAI，不调用 `sp.paper()`，不伪造回归。

验证结果：

- RED：新增 `tests/test_parent_education_wage_p2_execution_readiness.py` 后，首次失败原因是 P2 module/API/React 状态不存在。
- `python3 -m pytest tests/test_parent_education_wage_p2_execution_readiness.py -q` 通过：6 passed。
- `python3 -m pytest tests/test_parent_education_wage_literature_evidence_ledger.py tests/test_parent_education_wage_data_field_binding_ledger.py tests/test_parent_education_wage_method_execution_ledger.py tests/test_parent_education_wage_p2_execution_readiness.py tests/test_product_control_p0_stage_panel.py tests/test_product_control_p0_phase.py tests/test_web_react_api_base_contract.py tests/test_p3_react_input_tabs.py -q` 通过：44 passed, 11 subtests passed。
- `python3 -m py_compile Program/workbench/parent_education_wage_execution_readiness.py Program/parent_education_wage_execution_readiness.py Product/backend/product_control_p2_execution_readiness_service.py Product/app.py` 通过。
- `python3 Program/parent_education_wage_execution_readiness.py --project-root .` 通过，输出 P2 JSON/Review，状态为 `blocked_missing_parent_education_fields`。
- `python3 Program/parent_education_wage_method_execution_ledger.py --project-root .` 通过；P1-C refreshed 后阻断原因为 `missing_required_fields`。
- `cd Product/web-react && npm run build` 通过；Vite 仍有既有 chunk size warning。
- `rg -n "robot_exposure|bartik_iv|robot_density|ln_robot|行业机器人" Tasks/parent-education-wage/design.json || true` 无输出。
- `git diff --check -- <P2 scoped files>` 通过。

剩余：

- 自动进入 P3：把 P2 阻断态转成用户可打开的半成品论文包；不能只给诊断账本。

当前阻塞点：父母教育字段缺失，需要字段来源补证或产品层研究范围决策。

### P3 - DraftPackage Blocked Branch

修改：

- 新增 `Tasks/parent-education-wage-p3-draft-package-bdd.md`，定义阻断态 DraftPackage 的 BDD。
- 新增 `Program/workbench/parent_education_wage_draft_package.py` 和 `Program/parent_education_wage_draft_package.py`。
- 新增 `Product/backend/product_control_p3_draft_package_service.py`。
- 更新 `Product/app.py`，新增 `GET/POST /api/v1/projects/{project_id}/product-control/p3-draft-package`。
- 更新 `Product/web-react/src/components/ProductControlP0Panel.tsx`，在当前产品控制面显示 `P3 DraftPackage`、`paper_draft.docx`、半成品状态和 issue 数。
- 真实项目写出：
  - `Results/json/parent_education_wage_p3_draft_package.json`
  - `Manuscripts/generated/parent_education_wage_paper_draft.md`
  - `Submissions/parent_education_wage_paper_draft.docx`
  - `Manuscripts/generated/parent_education_wage_issue_list.md`
  - `Reviews/parent_education_wage_draft_audit_report.md`

验收结果：

- P2 阻断状态已转成 `blocked_draft_package_ready`。
- 用户现在有可打开的半成品论文初稿 docx，而不是只看到诊断账本。
- docx 包含红标：父母教育字段尚未绑定，不能报告回归结果或因果结论。
- P3 未写正式 `VariableRoleSet`、`DesignSpec`、`RunPlan`，未创建 run id，未执行回归。

验证结果：

- RED：新增 `tests/test_parent_education_wage_p3_draft_package.py` 后，首次失败原因是 P3 module/API/React 状态不存在。
- `python3 -m pytest tests/test_parent_education_wage_p3_draft_package.py -q` 通过：5 passed。
- `python3 Program/parent_education_wage_draft_package.py --project-root .` 通过，输出 `blocked_draft_package_ready`。
- `python3 -m pytest tests/test_parent_education_wage_p2_execution_readiness.py tests/test_parent_education_wage_p3_draft_package.py -q` 通过：11 passed。
- `python3 -m pytest tests/test_parent_education_wage_literature_evidence_ledger.py tests/test_parent_education_wage_data_field_binding_ledger.py tests/test_parent_education_wage_method_execution_ledger.py tests/test_parent_education_wage_p2_execution_readiness.py tests/test_parent_education_wage_p3_draft_package.py tests/test_product_control_p0_stage_panel.py tests/test_product_control_p0_phase.py tests/test_web_react_api_base_contract.py tests/test_p3_react_input_tabs.py -q` 通过：49 passed, 11 subtests passed。
- `python3 -m py_compile Program/workbench/parent_education_wage_draft_package.py Program/parent_education_wage_draft_package.py Product/backend/product_control_p3_draft_package_service.py Product/app.py tests/test_parent_education_wage_p3_draft_package.py` 通过。
- `cd Product/web-react && npm run build` 通过；Vite 仍有既有 chunk size warning。
- `git diff --check -- <P3 scoped files>` 通过。

剩余：

- 自动进入 P4：从真实数据/字典/人工材料中定位父亲教育、母亲教育或父母教育字段；确认 `hukou` 候选是否可绑定；之后才允许进入正式变量角色草案预检。

当前阻塞点：完整论文和真实执行仍被父母教育字段缺失阻断；半成品论文包已可交付。

### Phase 6 - Acceptance Package, Cleanup, And Handoff

修改：

- 新增 `Reviews/parent_education_wage_p0_p1_acceptance_package.md`，汇总 P0/P1-A/P1-B/P1-C 当前真实状态、验收边界、验证命令和下一步。
- 更新 `WORKFLOW_STATUS.md`，将 Phase 6 标为 completed，并把剩余阶段清零。
- 更新 `Tasks/todo.md`，把 P1-A/P1-B/P1-C/Phase 6 的完成状态写入顶部工作流清单。

验收结果：

- React 主入口、P0 控制面、P1-A 文献证据、P1-B 字段绑定、P1-C 方法执行 blocked ledger 已串成一个可交付验收包。
- 固定 Demo 题目只作为产品链路压力测试样例，不被写成最终产品范围。
- `/legacy` 运行时已重定向到 `/`，旧 `Product/web` 不再作为产品验收面；物理删除历史源码属于破坏性清理，未在本阶段直接执行。
- 当前正式层边界清楚：不写正式 bibliography、不写正式 VariableRoleSet、不写正式 RunPlan、不写正式 manuscript、不伪造 run id。

验证结果：

- `python3 -m pytest tests/test_parent_education_wage_literature_evidence_ledger.py tests/test_parent_education_wage_data_field_binding_ledger.py tests/test_parent_education_wage_method_execution_ledger.py tests/test_product_control_p0_stage_panel.py tests/test_product_control_p0_phase.py tests/test_web_react_api_base_contract.py tests/test_p3_react_input_tabs.py -q` 通过：38 passed, 11 subtests passed。
- `python3 -m py_compile Program/workbench/parent_education_wage_literature_evidence_ledger.py Program/parent_education_wage_literature_evidence_ledger.py Product/backend/product_control_p1_literature_service.py Program/workbench/parent_education_wage_data_field_binding_ledger.py Program/parent_education_wage_data_field_binding_ledger.py Product/backend/product_control_p1_data_field_service.py Program/workbench/parent_education_wage_method_execution_ledger.py Program/parent_education_wage_method_execution_ledger.py Product/backend/product_control_p1_method_service.py Product/app.py` 通过。
- `cd Product/web-react && npm run build` 通过；Vite 仍有既有 chunk size warning。

剩余：

- 后续研发第一优先是补真实字段证据，并修复 `Tasks/parent-education-wage/design.json` 的旧 robot code stub；不是继续扩大 UI 面板。

当前阻塞点：none for this acceptance pass.

### Phase 0 - Project Audit And Workflow Planning

修改：

- 新增 `WORKFLOW_STATUS.md`。

验证结果：

- `test -f WORKFLOW_STATUS.md` 通过。
- `rg -n "WEB_DIST_ROOT|/legacy|product-control/p0-phase" Product/app.py` 通过，确认 `/`/`/react` 使用 React build，`/legacy` 使用旧工作台，P0 API 存在。
- `rg -n "AgentTaskQueuePanel|SystemStatusBar|product-control" Product/web-react/src tests/test_*product_control* tests/test_*react*` 通过，确认 React 当前已有状态栏/Agent Queue，但 P0 product-control UI 仍主要落在 legacy 测试与旧静态前端。
- `python3 -m pytest tests/test_product_control_p0_phase.py tests/test_product_control_p0_stage_panel.py tests/test_web_react_api_base_contract.py -q` 通过：12 passed, 11 subtests passed。

剩余：

- 进入 Phase 1：先恢复 React 主入口基线，再迁移 P0 产品控制面。

当前阻塞点：none.

### Phase 5 - P1-C Method Execution Evidence And Run Ledger

修改：

- 新增 `Program/workbench/parent_education_wage_method_execution_ledger.py`。
- 新增 `Program/parent_education_wage_method_execution_ledger.py` CLI。
- 新增 `Product/backend/product_control_p1_method_service.py`。
- 更新 `Product/app.py`，新增 `GET/POST /api/v1/projects/{project_id}/product-control/p1-method-execution`。
- 更新 `Product/web-react/src/components/ProductControlP0Panel.tsx`，在当前 React 产品控制面显示 `P1-C 方法执行`、run id、方法数和缺失字段数。
- 更新 `Product/web-react/src/styles.css`，复用 P1 状态块样式。
- 新增 `tests/test_parent_education_wage_method_execution_ledger.py`。
- 生成 `Results/json/parent_education_wage_method_execution_ledger.json` 和 `Reviews/parent_education_wage_method_execution_ledger.md`。

验收结果：

- 当前状态为 `blocked_missing_required_fields`，`execution_allowed=false`，`run_id=null`。
- 阻塞原因：`missing_required_fields` 和 `design_code_stub_topic_contamination`。
- 缺失字段：`father_education`、`mother_education`、`parent_education`、`hukou`。
- IV、DID、DML 全部 blocked，没有伪造回归结果。
- StatsPAI 边界已记录：只有 analysis-ready dataframe 后才允许 EDA/pre-flight/identification/estimation/diagnostics；禁止 `sp.paper`。

验证结果：

- RED：`python3 -m pytest tests/test_parent_education_wage_method_execution_ledger.py -q` 首次失败，原因是 P1-C method execution ledger 模块不存在。
- `python3 -m pytest tests/test_parent_education_wage_method_execution_ledger.py -q` 通过：5 passed。
- `python3 -m pytest tests/test_parent_education_wage_literature_evidence_ledger.py tests/test_parent_education_wage_data_field_binding_ledger.py tests/test_parent_education_wage_method_execution_ledger.py tests/test_product_control_p0_stage_panel.py tests/test_product_control_p0_phase.py tests/test_web_react_api_base_contract.py tests/test_p3_react_input_tabs.py -q` 通过：38 passed, 11 subtests passed。
- `python3 -m py_compile Program/workbench/parent_education_wage_literature_evidence_ledger.py Program/parent_education_wage_literature_evidence_ledger.py Product/backend/product_control_p1_literature_service.py Program/workbench/parent_education_wage_data_field_binding_ledger.py Program/parent_education_wage_data_field_binding_ledger.py Product/backend/product_control_p1_data_field_service.py Program/workbench/parent_education_wage_method_execution_ledger.py Program/parent_education_wage_method_execution_ledger.py Product/backend/product_control_p1_method_service.py Product/app.py` 通过。
- `cd Product/web-react && npm run build` 通过；Vite 仍有既有 chunk size warning。
- `python3 Program/parent_education_wage_method_execution_ledger.py --project-root .` 通过，输出 P1-C ledger 和 review。

剩余：

- 进入 Phase 6：形成验收包、同步状态文档、列明仍需外部/人工补证的问题。

当前阻塞点：none.

### Phase 4 - P1-B Real Data Field Binding And Variable Role Evidence

修改：

- 新增 `Program/workbench/parent_education_wage_data_field_binding_ledger.py`。
- 新增 `Program/parent_education_wage_data_field_binding_ledger.py` CLI。
- 新增 `Product/backend/product_control_p1_data_field_service.py`。
- 更新 `Product/app.py`，新增 `GET/POST /api/v1/projects/{project_id}/product-control/p1-data-field-binding`。
- 更新 `Product/web-react/src/components/ProductControlP0Panel.tsx`，在当前 React 产品控制面显示 `P1-B 数据字段`、候选变量数、matched/missing 数和字段缺口。
- 更新 `Product/web-react/src/styles.css`，复用 P1 状态块样式。
- 新增 `tests/test_parent_education_wage_data_field_binding_ledger.py`。
- 生成 `Results/json/parent_education_wage_data_field_binding_ledger.json` 和 `Reviews/parent_education_wage_data_field_binding_ledger.md`。

验收结果：

- 当前 `Tasks/parent-education-wage/variables.yaml` 的 12 个候选变量已与本地字段来源对账。
- matched=8：`ln_wage`、`wage`、`edu_last`、`age`、`female`、`urban`、`experience`、`province`。
- missing=4：`father_education`、`mother_education`、`parent_education`、`hukou`。
- 当前状态为 `blocked_missing_parent_education_fields`；不会强行进入正式 VariableRoleSet。
- 未覆盖 `state/product/variable_roles.json`、`state/product/design_spec.json` 或 `state/product/run_plan.json`。

验证结果：

- RED：`python3 -m pytest tests/test_parent_education_wage_data_field_binding_ledger.py -q` 首次失败，原因是 P1-B data field binding 模块不存在。
- `python3 -m pytest tests/test_parent_education_wage_data_field_binding_ledger.py -q` 通过：5 passed。
- `python3 -m pytest tests/test_parent_education_wage_literature_evidence_ledger.py tests/test_parent_education_wage_data_field_binding_ledger.py tests/test_product_control_p0_stage_panel.py tests/test_product_control_p0_phase.py tests/test_web_react_api_base_contract.py tests/test_p3_react_input_tabs.py -q` 通过：33 passed, 11 subtests passed。
- `python3 -m py_compile Program/workbench/parent_education_wage_literature_evidence_ledger.py Program/parent_education_wage_literature_evidence_ledger.py Product/backend/product_control_p1_literature_service.py Program/workbench/parent_education_wage_data_field_binding_ledger.py Program/parent_education_wage_data_field_binding_ledger.py Product/backend/product_control_p1_data_field_service.py Product/app.py` 通过。
- `cd Product/web-react && npm run build` 通过；Vite 仍有既有 chunk size warning。
- `python3 Program/parent_education_wage_data_field_binding_ledger.py --project-root .` 通过，输出 P1-B ledger 和 review。

剩余：

- 关键父母教育字段缺失，不能进入正式方法执行。
- 自动进入 Phase 5：方法执行前置和 blocked/failure run ledger。

当前阻塞点：none.

### Phase 3 - P1-A Real Literature And Citation Evidence Chain

修改：

- 新增 `Program/workbench/parent_education_wage_literature_evidence_ledger.py`，为当前 Demo 题目生成 P1-A 文献证据账本。
- 新增 `Program/parent_education_wage_literature_evidence_ledger.py` CLI。
- 新增 `Product/backend/product_control_p1_literature_service.py`。
- 更新 `Product/app.py`，新增 `GET/POST /api/v1/projects/{project_id}/product-control/p1-literature-ledger`。
- 更新 `Product/web-react/src/components/ProductControlP0Panel.tsx`，在当前 React 产品控制面显示 `P1-A 文献证据`、真实文献候选数、verified 数和外部核验缺口。
- 更新 `Product/web-react/src/styles.css`，新增 P1-A 状态块样式。
- 新增 `tests/test_parent_education_wage_literature_evidence_ledger.py`。
- 生成 `Results/json/parent_education_wage_literature_evidence_ledger.json` 和 `Reviews/parent_education_wage_literature_evidence_ledger.md`。

验收结果：

- 当前 ledger 只包含 4 个检索 seed：父母教育/家庭背景与工资、代际人力资本、微观调查工资与教育测量、教育扩张或家庭教育背景识别策略。
- `verified_count=0`，所有 citation records 都是 `seed`，`can_support_claims=false`。
- 未写入正式 bibliography、正式论文、`Data/literature/processed/verified_bibliography.csv` 或 `state/product`。
- `GET` 只读返回已有 P1-A ledger 或 missing 状态；`POST` 才显式生成 ledger。

验证结果：

- RED：`python3 -m pytest tests/test_parent_education_wage_literature_evidence_ledger.py -q` 首次失败，原因是 P1-A ledger 模块不存在。
- 回归红灯：真实项目验证暴露 parser 误把 frontmatter/downstream consumers 当成检索 seed；补充测试后红灯复现，再修复为只读取 `## 待检索方向` 段落。
- `python3 -m pytest tests/test_parent_education_wage_literature_evidence_ledger.py -q` 通过：5 passed。
- `python3 -m pytest tests/test_parent_education_wage_literature_evidence_ledger.py tests/test_product_control_p0_stage_panel.py tests/test_product_control_p0_phase.py tests/test_web_react_api_base_contract.py tests/test_p3_react_input_tabs.py -q` 通过：28 passed, 11 subtests passed。
- `python3 -m py_compile Program/workbench/parent_education_wage_literature_evidence_ledger.py Program/parent_education_wage_literature_evidence_ledger.py Product/backend/product_control_p1_literature_service.py Product/app.py Product/backend/product_control_phase_service.py tests/test_parent_education_wage_literature_evidence_ledger.py tests/test_product_control_p0_stage_panel.py` 通过。
- `cd Product/web-react && npm run build` 通过；Vite 仍有既有 chunk size warning。
- `python3 Program/parent_education_wage_literature_evidence_ledger.py --project-root .` 通过，输出 P1-A ledger 和 review。

剩余：

- 真实文献 metadata/DOI/全文来源仍需外部检索或人工核验，未进入正式 bibliography。
- 自动进入 Phase 4：真实数据字段绑定与变量角色证据。

当前阻塞点：none.

### Phase 1 - Current React Entrypoint Recovery And Baseline

修改：

- 恢复 React 主入口为唯一产品验收面。
- 恢复 React 软灰主题 token：`--color-bg: #242424`、`--color-panel: #2b2b2b`、`--color-panel-soft: #323232`、`--color-ink: #c8c8c8`。
- 更新 `Tasks/current-stage.md`、`Tasks/handoff.md`、`Tasks/review.md`，删除 legacy 作为 P0 验收面的表述。

验证结果：

- `python3 -m pytest tests/test_web_react_api_base_contract.py tests/test_p3_react_input_tabs.py -q` 通过：14 passed, 11 subtests passed。
- `cd Product/web-react && npm run build` 通过。

剩余：

- Phase 2 已自动进入并完成。

当前阻塞点：none.

### Phase 2 - Product Control P0 Port To React Main UI

修改：

- 新增 `Product/web-react/src/components/ProductControlP0Panel.tsx`。
- 更新 `Product/web-react/src/App.tsx`，在 React 主工作台挂载 P0 控制面板。
- 更新 `Product/web-react/src/styles.css`，新增 `product-control-p0-*` 样式。
- 更新 `Product/app.py`，`/legacy` 改为 307 重定向到 `/`。
- 更新 `tests/test_product_control_p0_stage_panel.py`，前端验收从 legacy 切换为 React 主入口，并新增 legacy redirect 回归。

验证结果：

- RED：`python3 -m pytest tests/test_product_control_p0_stage_panel.py -q` 首次 4 个 React P0 测试失败，原因是 React P0 组件不存在、App 未挂载、样式缺失。
- `python3 -m pytest tests/test_product_control_p0_stage_panel.py tests/test_product_control_p0_phase.py -q` 通过：9 passed。
- `python3 -m pytest tests/test_web_react_api_base_contract.py tests/test_p3_react_input_tabs.py -q` 通过：14 passed, 11 subtests passed。
- `python3 -m py_compile Product/app.py Product/backend/product_control_phase_service.py tests/test_product_control_p0_stage_panel.py` 通过。
- `cd Product/web-react && npm run build` 通过。

剩余：

- 进入 Phase 3：P1-A real literature and citation evidence chain。

当前阻塞点：none.
