# Handoff

## 2026-06-18 重启前接手摘要

当前主仓库仍是 `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板`。本轮已经把 Demo 线推到 P16 阻断交付分支，并修掉控制台和 API 的三类误报：GET 未执行前不能声称 P16 完成；旧机器人 P12 预检不能改名冒充父母教育工资题目；字段齐全时必须实际执行最小 OLS 后才允许返回 run id。

当前真实产品状态：

- 可交付：`Submissions/parent_education_wage_paper_draft.docx` 半成品论文路径、`Manuscripts/generated/parent_education_wage_p15_issue_list.md` 红标问题清单、P13-P16 JSON/Review 证据包。
- 不可声称：不能说已经跑出父母教育工资模型，不能说已经生成完整实证论文。
- 当前阻断：`Data/Final/cfps_robot_reallocation.csv` 缺 `parent_education` 和 `experience`，所以 P13 不批准 RunPlan，P14 `run_id=null`、`executed_regression=false`。
- 下一步：数据修复分支。补齐或合并 `parent_education`，构造 `experience`，然后重跑 P13-P16，进入真实模型结果和完整论文初稿分支。

重启后快速恢复：

```bash
cd "/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板"
uvicorn Product.app:app --host 127.0.0.1 --port 8781
```

验收入口：

- 管理层仪表盘：`http://127.0.0.1:8781/workflow-dashboard`
- 状态 API：`http://127.0.0.1:8781/api/v1/workflow-dashboard/state`
- P13-P16 API：`http://127.0.0.1:8781/api/v1/projects/proj_empirical_paper_template_main/product-control/p13-p16-demo-closure`

最近验证：

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest tests/test_parent_education_wage_p13_p16_demo_closure.py tests/test_workflow_dashboard_artifact.py -q -p no:cacheprovider
# 13 passed

PYTHONDONTWRITEBYTECODE=1 python3 -m pytest tests/test_parent_education_wage_p9_formal_variable_role_save.py tests/test_parent_education_wage_p10_product_control_ia.py tests/test_parent_education_wage_p11_source_metadata_contract.py tests/test_parent_education_wage_p12_design_tree.py tests/test_parent_education_wage_p12_design_spec_preflight.py tests/test_parent_education_wage_p13_p16_demo_closure.py tests/test_workflow_dashboard_artifact.py -q -p no:cacheprovider
# 45 passed

cd Product/web-react && npm run build
# pass; only existing Vite chunk-size warning
```

最新截图证据：

- `Product/output/playwright/workflow-dashboard-p16-hardened-desktop.png`
- `Product/output/playwright/workflow-dashboard-p16-hardened-mobile.png`

已关闭本轮启动的 `uvicorn` 服务和已完成 sub agents。重启后不要从旧 P12 或旧机器人题目恢复；以 `WORKFLOW_STATUS.md`、`Tasks/todo.md`、`Tasks/review.md` 和本摘要为准。

## 2026-06-17 项目管理重置

当前主线已经收敛到 `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板`。CHARLS DID 已物理收拢到 `/Users/mahaoxuan/Desktop/经济学论文/StatspAI_跑通一次_CHARLS_DID`，只作为第一阶段 proof case 和第二层 runtime 来源样例，不作为后续产品开发主仓库。桌面旧入口 `/Users/mahaoxuan/Desktop/StatspAI_跑通一次_CHARLS_DID` 保留为符号链接，避免旧路径断掉。

新增入口：`Tasks/project-management-reset-2026-06-17.md`。

产品交付标准已固定：第一版不是以后台诊断报告作为主体验，而是以 `paper_draft.pdf / paper_draft.docx` 作为首交付物。成功分支输出完整论文初稿；阻断分支输出半成品论文、红标缺口、`issue_list.md` 和 `audit_report.md`。这条规则已写入 `docs/product-control/08_Draft-first交付标准.md`，后续 UI/API/工作流都要围绕 DraftPackage 设计。

P0 已完成后端/API 长程阶段包：新增题目绑定 BDD、P0 阶段 BDD、目标测试、后端审计服务、P0 阶段服务和 API。真实项目已写出 `Results/json/product_control_demo_topic_binding_audit.json`、`state/product/supervisor_plan.json`、`state/product/agent_task_queue.json`、`Results/json/product_control_demo_evidence_audit.json`、`Reviews/product_control_demo_evidence_audit.md`、`docs/product-control/07_作品集Demo脚本.md`、`Results/json/product_control_demo_portfolio_package.json`、`Reviews/product_control_demo_portfolio_package.md` 和 `Results/json/product_control_p0_phase.json`。当前结论为 `p0_phase_ready_for_review`，topic audit critical_issue_count=0。父母教育工资只是当前项目的 topic binding，来源为 `state/product/topic_binding.json`，不是产品代码里的硬编码题目；测试已覆盖第二个题目 `数字普惠金融对家庭创业的影响`，防止 P0 退化成 demo 临时补丁。

旧 `supervisor_plan.json` 和 `agent_task_queue.json` 已归档到 `state/product/archive/p0a_current_topic_rebind_20260617/`，不要把它们直接改字复用。当前 `state/product/supervisor_plan.json` 和 `state/product/agent_task_queue.json` 是 P0-B 从 topic binding 重新生成的审阅层产物；队列默认 `can_execute=false`，后续不能跳过人工派工审阅。

当前排序：

1. P3 父母教育字段来源补证：定位 `father_education`、`mother_education` 或 `parent_education` 的真实字段来源。
2. `hukou` 候选审阅：P2 已找到 `qa2` 等候选，但尚未人工绑定。
3. 正式变量角色草案预检：只有字段来源确认后，才允许从 draft 进入正式 VariableRoleSet 审阅流程。
4. 方法执行预检：只有 VariableRoleSet、DesignSpec、RunPlan 均通过后，才允许创建真实 run id。
5. P1-A 外部/人工文献核验：只在拿到 metadata/DOI/全文来源和人工批准后，才能进入正式 bibliography。

P0 前端控制面板已完成并迁入当前 React 主入口。`Product/web-react/src/components/ProductControlP0Panel.tsx` 读取 `GET /api/v1/projects/{project_id}/product-control/p0-phase`；刷新按钮显式调用 `POST /api/v1/projects/{project_id}/product-control/p0-phase`。面板展示 topic、P0 状态、Agent 任务数、Evidence Audit、`needs_evidence` 缺口、作品集脚本路径和 `待派工审阅`，不会出现自动执行入口。当前真实 `Results/json/product_control_p0_phase.json` 已刷新为新结构，包含 `agent_tasks`、`evidence_checks` 和 `formal_boundary`。

P1-A 文献证据账本已完成本地审阅层闭环：`GET /api/v1/projects/{project_id}/product-control/p1-literature-ledger` 只读返回已有账本或 missing 状态；`POST /api/v1/projects/{project_id}/product-control/p1-literature-ledger` 显式生成账本。真实项目产物为 `Results/json/parent_education_wage_literature_evidence_ledger.json` 和 `Reviews/parent_education_wage_literature_evidence_ledger.md`。当前只有 4 个检索 seed，`verified_count=0`，所有 citation records 均 `can_support_claims=false`；不得把它当成已核验文献包。

P1-B 数据字段绑定账本已完成审阅层闭环：`GET /api/v1/projects/{project_id}/product-control/p1-data-field-binding` 只读返回已有账本或 missing 状态；`POST /api/v1/projects/{project_id}/product-control/p1-data-field-binding` 显式生成账本。真实项目产物为 `Results/json/parent_education_wage_data_field_binding_ledger.json` 和 `Reviews/parent_education_wage_data_field_binding_ledger.md`。当前 12 个候选变量中 8 个 matched、4 个 missing；缺口是 `father_education`、`mother_education`、`parent_education`、`hukou`。正式 `state/product/variable_roles.json` 未改写。

P1-C 方法执行账本已完成 blocked ledger：`GET /api/v1/projects/{project_id}/product-control/p1-method-execution` 只读返回已有账本或 missing 状态；`POST /api/v1/projects/{project_id}/product-control/p1-method-execution` 显式生成账本。真实项目产物为 `Results/json/parent_education_wage_method_execution_ledger.json` 和 `Reviews/parent_education_wage_method_execution_ledger.md`。当前 `execution_allowed=false`、`run_id=null`，IV/DID/DML 全部 blocked；P2 修复 `Tasks/parent-education-wage/design.json` 后，P1-C 阻断原因已收敛为 required fields 缺失。

P2 执行准入已完成审阅层闭环：`GET /api/v1/projects/{project_id}/product-control/p2-execution-readiness` 只读返回已有账本或 missing 状态；`POST /api/v1/projects/{project_id}/product-control/p2-execution-readiness` 显式生成账本。真实项目产物为 `Results/json/parent_education_wage_p2_execution_readiness.json` 和 `Reviews/parent_education_wage_p2_execution_readiness.md`。当前 `status=blocked_missing_parent_education_fields`、`execution_preflight_allowed=false`、`run_id=null`；`hukou` 找到候选但未绑定，父亲教育/母亲教育/父母教育字段仍缺。正式 `state/product/variable_roles.json`、`state/product/design_spec.json`、`state/product/run_plan.json` 未改写。

P3 DraftPackage 已完成阻断分支交付：`GET /api/v1/projects/{project_id}/product-control/p3-draft-package` 只读返回已有包或 missing 状态；`POST /api/v1/projects/{project_id}/product-control/p3-draft-package` 显式生成半成品论文包。真实项目产物为 `Results/json/parent_education_wage_p3_draft_package.json`、`Submissions/parent_education_wage_paper_draft.docx`、`Manuscripts/generated/parent_education_wage_paper_draft.md`、`Manuscripts/generated/parent_education_wage_issue_list.md` 和 `Reviews/parent_education_wage_draft_audit_report.md`。当前状态为 `blocked_draft_package_ready`；docx 包含红标，明确父母教育字段尚未绑定，不能报告回归结果或因果结论。P3 未写正式 VariableRoleSet、DesignSpec、RunPlan，未创建 run id，未执行回归。

P4 字段来源候选已完成：`GET /api/v1/projects/{project_id}/product-control/p4-field-source-candidates` 只读返回已有账本或 missing 状态；`POST /api/v1/projects/{project_id}/product-control/p4-field-source-candidates` 显式只读扫描 CFPS Stata 元数据并生成候选账本。真实项目产物为 `Results/json/parent_education_wage_p4_field_source_candidates.json` 和 `Reviews/parent_education_wage_p4_field_source_candidates.md`。本轮扫描选中 `/Users/mahaoxuan/Desktop/论文核心素材库/01_原始数据/实证数据库/A001CFPS中国家庭追踪调查`，扫描 36 个 `.dta`、21546 个字段标签，生成 52 个候选；`father_education` 和 `mother_education` 均为 `candidate_found`，`parent_education` 为 `constructable_needs_review`，`hukou` 为 `candidate_found`。P4 只读元数据，不载入整份原始数据，不写正式 VariableRoleSet、DesignSpec、RunPlan，未创建 run id，未执行回归。

P5 VariableRoleSet draft preflight 已完成：`GET/POST /api/v1/projects/{project_id}/product-control/p5-variable-role-preflight` 暴露草案预检。真实项目产物为 `Results/json/parent_education_wage_p5_variable_role_preflight.json` 和 `Reviews/parent_education_wage_p5_variable_role_preflight.md`。当前 outcome 草案为 `ln_wage`，treatment 草案为 `parent_education`，父母教育构造建议为 `max(father_education, mother_education)`，controls 草案为 `age/female/urban/edu_last/experience`。P5 不写正式 `state/product/variable_roles.json`。

P6 人工签收/提升路径已完成：`GET/POST /api/v1/projects/{project_id}/product-control/p6-variable-role-signoff` 暴露签收包，`POST /product-control/p6-variable-role-signoff/promote` 在完整签收后只能写 `state/product/variable_roles_drafts.json` 的 editable draft。真实项目产物为 `Results/json/parent_education_wage_p6_variable_role_signoff.json` 和 `Reviews/parent_education_wage_p6_variable_role_signoff.md`。旧 `PUT /api/v1/projects/{project_id}/variable-roles` 在没有 P6 promoted draft 时返回 409 `p6_variable_role_draft_required`，不能绕过 P6 直接写正式变量角色。

P7 页面签收台已完成：React Product Control 的 P6 面板现在直接显示五项确认输入、推荐默认值和“确认并生成可编辑草稿”按钮。默认值为 `confirmed_current_p4_sources`、`max(father_education, mother_education)`、`control_or_heterogeneity_candidate`、`ln_wage_with_age_female_urban_edu_last_experience`、`draft_only_no_formal_write`。页面提交只调用 editable draft promotion，不写正式 VariableRoleSet，不写 DesignSpec，不写 RunPlan，不创建 run id，不跑模型。独立审查指出过一个高风险绕过：P7 promoted draft 后旧 `PUT /variable-roles` 曾会误写正式变量表；当前已修复为即使 P7 draft 存在，正式保存口也必须等 P8 单独批准，否则返回 409。真实项目未由我代替用户点击 promotion；下一位 Agent 不要把 P7 测试通过误读成真实项目已签收，更不要把 editable draft 误读成正式 VariableRoleSet。

P8 正式变量角色审批门禁已完成：`GET/POST /api/v1/projects/{project_id}/product-control/p8-variable-role-approval` 已接入，React Product Control 现在显示 P8 审批面板、reviewer、note、confirmation 和“批准正式变量角色保存”。审批确认码为 `approve_formal_variable_roles_after_review`。P8 approval 只写 `state/product/variable_role_formal_approvals.json`，不直接写正式 `state/product/variable_roles.json`。独立审查后已收紧：approval 必须对当前最新 P7/P6 editable draft 生效，latest draft roles、approval `source_draft_roles`、PUT roles 三者必须一致；旧 approval 不能解锁新 draft，审批 A 不能写入不同 roles，同一 draft id 的 roles 被篡改后原 approval 也会失效。用户已完成 P7 promotion；我已按用户授权提交真实项目 P8 approval，只批准变量角色保存门禁，不批准 DesignSpec/RunPlan/model。

P9 正式变量表保存门禁已完成：`GET/POST /api/v1/projects/{project_id}/product-control/p9-variable-role-formal-save` 已接入，React Product Control 现在显示 P9 保存面板、dataset/source metadata 缺口、reviewer、note、confirmation 和“保存正式变量表”。确认码为 `save_formal_variable_roles_from_p8_approved_draft`。P9 只有在 P8 approval 有效、dataset path 存在、所有 approved role 字段有 source metadata、payload 未替换 source draft/roles/dataset 时，才会写正式 `state/product/variable_roles.json`；即便保存成功，也不写 DesignSpec、RunPlan，不创建 run id，不跑模型。真实项目当前 P9 正确阻断为 `blocked_missing_dataset_source_metadata`，缺 `dataset_path`、`ln_wage`、`parent_education`、`age`、`female`、`urban`、`edu_last`、`experience`。下一位 Agent 不要为了“继续推进”硬写正式变量表；应先做 P11 dataset/source metadata 补齐路径。

北极星计划已建立：`Tasks/north-star-product-plan.md` 是后续产品推进控制文件。目标不是单题目 demo，而是本科生可用、可审计、可交付的实证论文生产流水线；第一用户体验仍固定为 `paper_draft.docx / paper_draft.pdf`。后续 P10-P16 都必须先写 SDD/BDD，再写失败测试，再做最小实现和验证；每阶段结束更新 `WORKFLOW_STATUS.md`、`Tasks/todo.md`、`Tasks/review.md` 和本 handoff。

P10 Product Control 当前门禁中心已完成：React Product Control 现在先显示当前门禁摘要，明确当前卡在 `P9 正式变量表保存` 和 `blocked_missing_dataset_source_metadata`；P0-P8 默认折叠为阶段历史；P9 当前阻断详情仍可见，保存按钮禁用，页面明确 `不写 DesignSpec；不写 RunPlan；不跑模型`。P10 只做信息架构整理，没有补 source metadata，没有写正式 VariableRoleSet，也没有创建 run id 或跑模型。桌面和 390px 移动端验收截图为 `output/playwright/product-control-p10-current-gate.png`、`output/playwright/product-control-p10-mobile.png`。

P11 Source Metadata Completion Path 已完成产品实现：`GET/POST /api/v1/projects/{project_id}/product-control/p11-source-metadata-contract` 已接入，React Product Control 当前门禁详情新增 `P11 Source Metadata` 表单。用户可填写 dataset path、`field_bindings` JSON、reviewer、note、confirmation 和 `parent_education construction`。P11 只更新最新 editable draft 的 `source_contract`；完整后只让 P9 进入 `formal_variable_role_save_ready`。P11 不写正式 `state/product/variable_roles.json`，不写 DesignSpec/RunPlan，不创建 run id，不执行模型。

P11A Source Contract Review Kit 已完成：P11 GET 现在返回 `source_contract_review_kit`，包括 recommended dataset path、dataset path candidates、9 个 field review items、P5/P4 preferred candidate、missing-source 状态和 no-model boundary。React P11 面板在 JSON 表单前展示 `Source review kit`，让用户先看候选证据再确认。P11A 只读，不保存 source contract，不写正式层，不跑模型。

P11B Per-field Source Confirmation Editor 已完成：React P11 表单新增 `Per-field source confirmation`，把 9 个 required source fields 拆成 dataset column、source field、source path、evidence level 可编辑行；保存时生成原 P11 `field_bindings` payload，`field_bindings JSON preview` 只作为审计预览。P11B 不保存真实 source contract，不写正式层，不跑模型。

P11C Source Contract Readiness Check 已完成：React P11 表单新增 `Source contract readiness`，保存前列出 reviewer、note、confirmation、dataset path、parent education construction 和 source rows 的具体缺口；缺口存在时保存按钮禁用。P11C 不保存真实 source contract，不写正式层，不跑模型。

P11D Row Human Confirmation Gate 已完成：React P11 表单新增逐字段人工确认 checkbox；预填候选行默认未确认，readiness 会把未勾选行列为 `<field>:human_confirmation`。P11D 不改后端 P11 payload，不保存真实 source contract，不写正式层，不跑模型。

P11E Human Signoff Readable Rows 已完成：React P11 字段来源行在桌面和移动端都显示 `dataset column`、`source field`、`source path`、`evidence level` 标签；390px 移动端页面级 horizontal overflow=false；9 个 source rows、36 个字段标签、9 个 human confirmation checkbox 和 disabled 保存按钮均已浏览器验收。P11E 不改后端 payload，不保存真实 source contract，不写正式层，不跑模型。

P11F Human Signoff Review Queue 已完成：React P11 在长表单前新增 `Human signoff review queue`，按 9 个 required source fields 展示 status、missing items 和 action；用户可以先按队列检查，再到下方逐行编辑并勾选 human confirmation。P11F 不改后端 payload，不保存真实 source contract，不写正式层，不跑模型。浏览器验收截图为 `Product/output/playwright/product-control-p11f-review-queue-desktop.png` 和 `Product/output/playwright/product-control-p11f-review-queue-mobile.png`。

P11G Source Contract Signoff Workspace 已完成：React P11 现在显示 `Source Contract Signoff` 工作台，包含状态条、左侧 `Review queue`、右侧 `Source contract form`、默认折叠的 `Source review kit` 和底部 action bar。保存按钮在 source metadata 缺口存在时继续 disabled，页面明确 `No model run`。P11G 不改后端 payload，不保存真实 source contract，不写正式层，不跑模型。浏览器验收截图为 `Product/output/playwright/product-control-p11g-signoff-workspace-final-desktop.png` 和 `Product/output/playwright/product-control-p11g-signoff-workspace-final-mobile.png`。

P11-Human / P11H 已完成：真实项目已通过 P11 表单保存 source contract，dataset path 为 `Data/Final/cfps_robot_reallocation.csv`，9 个 required source fields 均有 dataset column/source field/source path/evidence level 和逐行 human confirmation；`parent_education` construction 为 `max(father_education, mother_education)`。P11 返回 `source_metadata_contract_ready_for_p9_save`，P9 返回 `formal_variable_role_save_ready`。React 已显示 `P11 已签收`、`已解锁 P9 正式变量表保存`、`下一步：回到 P9 正式保存`，同时明确不能进入 P12、不能创建 run id、不能运行模型。浏览器验收截图为 `Product/output/playwright/product-control-p11h-saved-next-step-final2-desktop.png` 和 `Product/output/playwright/product-control-p11h-saved-next-step-final2-mobile.png`。

P9-Human / P9H 已完成：已把 P8-approved、P11-sourced 的变量角色正式保存到 `state/product/variable_roles.json`，状态为 `approved`，dataset path 为 `Data/Final/cfps_robot_reallocation.csv`。P9 POST 成功后曾发现 GET 仍返回 `formal_variable_role_save_ready` 的误导性完成态 bug；已补 `Tasks/parent-education-wage-p9h-formal-save-completion-bdd.md` 和回归测试，当前 P9 GET 返回 `formal_variable_roles_saved`、`can_save_formal_variable_roles=false`、`can_enter_design_spec_preflight=true`、`can_create_run_id=false`、`can_execute_model=false`。P9H 不写 DesignSpec/RunPlan，不创建 run id，不跑模型。

P12-0 Design Tree / Pre-PRD 已完成：`docs/product-control/p12-p16-design-tree.md` 已写清 P12 DesignSpec Preflight、P13 RunPlan Approval、P14 Model Execution And Evidence Ledger、P15 Draft Generation And Export、P16 User Acceptance And Satisfaction Loop 的输入、产出、验收标准、回退路径和停机条件。P12-0 是进入 P12 前的树形规划，不是方法规格实现，不写 `state/product/design_spec.json`，不写 RunPlan，不创建 run id，不跑模型。

P12-0 可视化与移动端 QA 已完成：当前代码服务 `http://127.0.0.1:8777` 下，`/workflow-dashboard` 桌面和 390px 移动端均显示 CEO 摘要、P12-0 当前门禁、P12 DesignSpec 下一步、P12-P16 分支和 `不运行模型`；产品页 P9H 当前门禁摘要在 390px 移动端已切为单列，不再重叠。截图为 `Product/output/playwright/workflow-dashboard-p12-design-tree-desktop.png`、`Product/output/playwright/workflow-dashboard-p12-design-tree-mobile.png`、`Product/output/playwright/product-control-p9h-saved-current-code-desktop.png`、`Product/output/playwright/product-control-p9h-saved-current-code-mobile.png`。

P12 DesignSpec Preflight 已完成：`GET/POST /api/v1/projects/{project_id}/product-control/p12-design-spec-preflight` 已接入。真实项目已写出 `Results/json/parent_education_wage_p12_design_spec_preflight.json` 和 `Reviews/parent_education_wage_p12_design_spec_preflight.md`，状态为 `design_spec_preflight_ready_for_review`，baseline 公式为 `ln_wage ~ parent_education + age + female + urban + edu_last + experience`。P12 只写预检产物；不写正式 `state/product/design_spec.json`，不写 `state/product/run_plan.json`，不创建 run id，不跑模型。

P13-P16 阻断交付分支已完成：`GET/POST /api/v1/projects/{project_id}/product-control/p13-p16-demo-closure` 已接入。真实项目已写出 `Results/json/parent_education_wage_p13_run_plan_approval.json`、`Results/json/parent_education_wage_p14_execution_evidence_ledger.json`、`Results/json/parent_education_wage_p15_draft_export_package.json`、`Results/json/parent_education_wage_p16_user_acceptance_packet.json` 和 `Manuscripts/generated/parent_education_wage_p15_issue_list.md`。P13 校验真实 CSV 后发现缺 `parent_education`、`experience`；P14 `run_id=null`、`executed_regression=false`；P16 标记 `can_claim_complete_paper=false`。旧机器人题目的活跃 `state/product/design_spec.json` 和 `state/product/run_plan.json` 已归档到 `state/product/archive/p13_p16_stale_formal_state/`。

项目内动态中文工作流仪表盘已新增并升级为 CEO 可读：`docs/product-control/workflow-dashboard.html`，状态源为 `docs/product-control/workflow-dashboard-state.json`。启动 FastAPI 后访问 `/workflow-dashboard`，页面会短轮询 `/api/v1/workflow-dashboard/state`；首屏 H1 为 `论文生产流水线控制台`，先显示 `老板先看这里` 和三句话结论：`现在能交付什么`、`还缺什么`、`下一步做什么`。当前门禁是 `P16 半成品交付包已生成`，阻断是真实 CSV 缺字段，禁止动作是不伪造结果。`docs/product-control/README.md` 已把它放在阅读顺序第 0 位。阶段变化后必须同步更新该 JSON、`WORKFLOW_STATUS.md` 和 `Tasks/todo.md`。

下一阶段不是继续空转 P13，而是数据修复后重跑 P13-P16：补齐或合并 `parent_education`，构造 `experience`，然后再让 P13 批准运行计划。不要把当前 P16 阻断分支误报为完整论文完成，也不要复用旧机器人题目的方法规格、运行计划或结果。

Phase 6 验收包已完成：`Reviews/parent_education_wage_p0_p1_acceptance_package.md` 是本轮 P0/P1 接手入口。它明确当前 Demo 线是产品链路压力测试样例，不是最终产品范围；当前没有正式 bibliography、正式 VariableRoleSet、正式 RunPlan、正式 manuscript 或真实 run id。

旧工作台不再是产品入口：`/legacy` 现在 307 重定向到 `/`，避免后续继续在 `Product/web` 上做产品验收。`Product/web` 文件只作为历史源码留存，不能再作为 P0/P1 成功标准。

并行但不抢主线的任务：`02_literature`、P2-AA execution backend selection、P2-M 真实变量候选提升。所有功能/API/产品流程/用户可见交互仍按本仓库 BDD/TDD 规则执行。

## 2026-05-25 补充：P3-B React Workbench 设计契约完成

当前 React 新入口已经不只是输入器原型，而有了后续模块接入前的设计契约。新增契约文件为 `docs/architecture-v2/codex-phase-p3-react-workbench-design-contract.md`，对应自动化测试为 `tests/test_p3_design_contract.py`。

已锁定的产品规则：

- 一级模块为：研究入口、任务队列、递归搜索、数据与变量、方法设计、执行实验、结果解释、论文草稿、复现导出、Agent 审计。
- 主屏默认只显示当前决策和 3-5 个关键信号；日志、证据、风险、权限、成本、产物详情进入右侧 Drawer 或按需展开。
- 视觉语言继续使用黑白灰、低对比、DottedSurface；不使用彩色状态色，不写“当前只验证...”这类防守性文案。
- 正式层写回必须显式确认；Auto / Agent 只能先进入 draft / exploratory / needs_human_review。

验证证据：

- `python3 -m unittest tests.test_p3_design_contract -v`：4 tests OK。

下一轮第一件事：P3-C 按该契约实现右侧审计 Drawer 和任务队列首个真实模块。不要把旧前端功能整块搬进 React，也不要在首屏摊开 Agent 队列、证据台和执行日志。

## 2026-05-25 补充：P2-AB 质量收口完成

当前 P2-AB 已从“CLI 能跑但前端契约漂移”修复到“CLI + 首页 + Agent Console 重新对齐”。核心变化：

- `Product/cli.py auto-research` 已能以研究题目创建本地 Auto Research Run，默认 `mode=auto` / `execution_policy=best_available`。
- `Product/backend/auto_research_service.py` 写入能力状态、递归搜索计划、文献线索、变量候选、方法候选、证据缺口、研究报告和 exploratory 草稿。
- 自动产物仍是草案层：`artifact_policy.status=needs_human_review`、`can_promote=false`，不会覆盖 VariableRoleSet、DesignSpec、RunPlan、FindingCard 或 Manuscript 正式层。
- 前端首页恢复 topic-first 入口，未确认题目时不再默认铺开全部工作台细节。
- Agent Console 的身份、权限、能力、成本和审计日志只在右侧 drawer 展开；主工作区只保留可扫读 Agent 列表。

验证证据：

- `python3 -m unittest discover -s tests -v`：282 tests OK，skipped=1。
- `node --check Product/web/assets/app.js`：通过。
- `python3 -m py_compile Product/cli.py Product/backend/auto_research_service.py Product/backend/registry.py Product/backend/identity_service.py Product/backend/permission_service.py Product/backend/capability_registry.py Product/backend/cost_service.py Product/app.py`：通过。
- `git diff --check -- <本轮 scoped files>`：通过。
- Playwright 浏览器验收截图：`journey-final-verify.png`、`journey-agent-drawer-clean-verify.png`。

下一轮第一件事：P2-AC 做 Auto Research execution adapter selection，把已生成的 topic/intake/candidates 接到真实 StatsPAI/Python 执行计划，但仍必须先写 evaluator checks 和人工审阅 gate，不允许直接晋升正式结论。

## 2026-05-22 补充：长程优化协议

本轮已把“平台期识别 -> 策略跃迁 -> 打破-修复 -> 证据验收”固化为项目流程。下一轮如果继续 P2-AA、方法执行、论文生成或产品状态机任务，先读取 `docs/architecture-v2/long-run-optimization-protocol.md`，并在 `Tasks/round-log.md` 写入本轮目标、当前最好结果、平台期判断、瓶颈、下一策略、回滚点和证据路径。

关键约束：不能把设计文档、mock JSON、UI 状态或任务骨架当作真实执行证明；真实完成必须能追到命令、日志、测试输出或结果文件。

更新时间：2026-05-17 22:20 CST

## 当前目标

继续开发 `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板`。当前主线是把真实数据、LLM Supervisor、Agent Task Queue、方法执行和论文产物串成可审计 AI 实证研究流水线。P2-V 到 P2-Z 的 Pipeline MVP Review 已完成：选题入口、SupervisorPlan 审批、Agent Task Queue 派工审阅、候选变量/正式变量隔离、方法 workflow checklist、Reviewer Scorecard、Verifier Export Gates 已通过一次浏览器端到端验收。下一步进入 P2-AA：让已人工派工审阅的任务选择真实执行后端，并产出可审计日志、结果和 evaluator checks。

## 已完成事项

- P2-A 数据质量画像已完成：`Product/backend/overview_service.py` 的 datasets API 现在把数据文件升级为可审计研究对象，CSV 返回 `quality_profile`，包含样本量、字段数、缺失值、字段类型和检查项；未解析格式保留 `local_file` 证据并标记 `not_profiled`。
- P2-A 前端已完成：`Product/web/index.html`、`Product/web/assets/app.js`、`Product/web/assets/styles.css` 在“数据与设计”页新增 `数据质量画像` 面板；数据集、质量画像、变量角色编辑器按纵向 clean workbench 顺序展示，避免与右侧属性检查器挤压。
- P2-A 中文化补丁已完成：`tests/test_frontend_chinese_copy.py` 防止 `dataset_quality_profile` / `confirm_variable_roles` 这类内部标签重新作为可见 eyebrow 文案出现。
- 确认 git 根目录是 `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板`。
- 读取项目级 `AGENTS.md`，确认本项目默认 BDD + TDD。
- 读取 `docs/architecture-v2/README.md`、`api-contract-v2.md`、`technical-architecture.md`、`kimi-observable-execution-ui-handoff-2026-05-10.md`、`codex-phase-a-bdd.md`。
- 运行基线测试：`python3 -m unittest discover -s tests -v`，结果 48 tests OK，skipped=1 是预期外部 API 集成测试跳过。
- 用浏览器读取 StatsPAI 文章 `https://www.statspai.com/zh/blog/statspai-agent-era-statistics-ecosystem`，并继续读取其关键子链接：StatsPAI 首页、博客列表、加入、更新日志、隐私、条款、CoPaper、GitHub、Issues。
- 新增方法论沉淀：`docs/architecture-v2/statspai-methodology-synthesis-2026-05-12.md`。
- 新增 P0 前端 BDD：`docs/architecture-v2/codex-phase-p0-observable-ui-bdd.md`，共 7 条行为。
- 新增前端行为测试：`tests/test_observable_execution_frontend.py`。
- 修改 `Product/web/index.html`、`Product/web/assets/app.js`、`Product/web/assets/styles.css`，把 `实证执行` 页面接到真实 `/api/v1/projects/{project_id}/runs/{run_id}/observability`。
- 浏览器验收发现旧服务 8765 进程未加载当前代码，改用 8877 启动当前工作树验证。
- 针对历史 run 缺少 `state/runs/{run_id}` 观测文件的 404 边界补了第 7 条 BDD 和最小前端恢复态。
- 新增 P1 gate resolve BDD：`docs/architecture-v2/codex-phase-p1-gate-resolve-bdd.md`。
- 在 `Product/backend/observability_service.py`、`Product/backend/project_service.py`、`Product/app.py` 中实现 `POST /api/v1/projects/{project_id}/runs/{run_id}/gates/{gate_id}/resolve`。
- 扩展 `tests/test_observable_execution.py`，验证 resolve 后写回 gate、追加 `hitl_gate_resolved` 事件、更新 manifest open gate 数、拒绝非法 action。
- 新增 P1-A 前端 BDD：`docs/architecture-v2/codex-phase-p1-gate-resolve-frontend-bdd.md`。
- 扩展 `tests/test_observable_execution_frontend.py` 到 10 条行为，覆盖开放 gate 三类动作、note 提交、成功刷新、错误展示、已处理 gate resolution 展示。
- 修改 `Product/web/assets/app.js`，增加 `v2api.runs.resolveGate`、`resolveObservableGate`、gate note textarea、confirm/reject/adjust 按钮和 resolved gate 展示。
- 修改 `Product/web/assets/styles.css`，增加 gate note 和 resolution 样式。
- 修改 `Product/web/index.html`，给 CSS/JS 加 `?v=20260512-p1a` 版本 query，避免本地浏览器继续执行旧缓存。
- 浏览器在 `http://127.0.0.1:8765/?v=20260512-p1a` 完成真实 gate resolve 验收：`gate_dataset_fields` 从待确认变为已处理，显示 action/note/resolved_at，事件流出现 resolved 事件。
- 新增 P1-B 数据入口 BDD：`docs/architecture-v2/codex-phase-p1-dataset-run-bdd.md`。
- 扩展 `Product/backend/overview_service.py`：`GET /api/v1/projects/{project_id}/datasets` 从项目 `Data/` 目录扫描本地数据文件，返回 `evidence_level=local_file`、相对路径、文件类型、大小、行列数和 configured/candidate role。
- 扩展 `Product/app.py` 和 `Product/backend/project_service.py`：`POST /api/v1/projects/{project_id}/runs` 接收 `dataset_path`，拒绝绝对路径、`..` 和不存在文件，并在 run response 与 `state/runs/{run_id}/run_manifest.json` 中持久化 `dataset_source`。
- 新增 `tests/test_dataset_frontend.py`，并扩展 `tests/test_api_contract_v2.py`、`tests/test_product_v1_local.py`，覆盖 P1-B 数据集列表、dataset_source 持久化、非法路径拒绝和前端按钮行为。
- 修改 `Product/web/assets/app.js`：数据与变量页显示本地数据文件的 evidence/path/shape/role，并提供“用此数据启动试运行”按钮；创建 run 时把 `dataset_path` 传给后端。
- 修改 `Product/web/index.html`，静态资源版本更新到 `?v=20260512-p1b3`。
- 浏览器在 `http://127.0.0.1:8765/?v=20260512-p1b3` 验收 P1-B：点击数据页按钮后生成 `run_fc725d15b3c0`，manifest 写入 `dataset_source.path=Data/Final/analysis_sample.csv` 和 `evidence_level=local_file`。
- 新增 P1-C BDD：`docs/architecture-v2/codex-phase-p1-run-dataset-source-ui-bdd.md`。
- 扩展 `Product/backend/observability_service.py`：`GET /observability` 顶层返回 `dataset_source`，并保持与 `manifest.dataset_source` 一致。
- 扩展 `Product/backend/project_service.py`：解析 dataset source 时写入 `role`、`row_count`、`column_count`，CSV shape 来自本地文件检查。
- 扩展 `tests/test_observable_execution.py`：新增 observability 顶层 dataset_source 行为测试，确认 `row_count=12`、`column_count=4`、`evidence_level=local_file`。
- 扩展 `tests/test_observable_execution_frontend.py`：新增执行页 Run 数据源面板静态行为测试。
- 修改 `Product/web/index.html`、`Product/web/assets/app.js`、`Product/web/assets/styles.css`：新增 `observable-dataset-source` 面板，显示数据文件名、项目相对路径、shape、file_type、role 和 evidence badge。
- 浏览器在 `http://127.0.0.1:8765/?v=20260512-p1c` 验收 P1-C：从数据页启动 `run_641c9770a1a8`，执行页显示完整 Run 数据源证据。
- 新增 P1-D BDD：`docs/architecture-v2/codex-phase-p1-variable-roles-bdd.md`。
- 扩展 `Product/backend/observability_service.py`：从 `dataset_intake` step metadata 提取 `key_variables`，顶层返回 `variable_roles`，并绑定 `gate_dataset_fields` 的 open/resolved 状态。
- 扩展 `tests/test_observable_execution.py`：新增 variable_roles API 行为测试，覆盖 outcome、treatment、controls、instruments 和 confirmation gate/status。
- 扩展 `tests/test_observable_execution_frontend.py`：新增变量角色确认面板静态行为测试。
- 修改 `Product/web/index.html`、`Product/web/assets/app.js`、`Product/web/assets/styles.css`：新增 `observable-variable-roles` 面板，显示 outcome/treatment/controls/instruments、gate id、确认状态和 evidence badge。
- 浏览器在 `http://127.0.0.1:8765/?v=20260512-p1d` 验收 P1-D：执行页显示 `gate=gate_dataset_fields · status=open`、`outcome=wage`、`treatment=trained`、`controls=edu, experience`。
- 新增 P1-UI BDD：`docs/architecture-v2/codex-phase-p1-observable-console-density-bdd.md`，把“实证执行页必须像执行控制台而不是论文卡片堆叠”固化为行为约束。
- 扩展 `tests/test_observable_execution_frontend.py`：新增行为 13，覆盖 `execution-control-panel`、`execution-context-grid`、system font、8px 圆角、两列上下文网格、artifact 证据条目不溢出、metadata 可换行。
- 修改 `Product/web/index.html`：运行选择面板增加 `execution-control-panel`，run 摘要、Run 数据源、变量角色确认合并到 `execution-context-grid`。
- 修改 `Product/web/assets/styles.css`：对 `#view-empirical-execution` 使用 scoped system font、小圆角、小内边距、紧凑面板、可扫读 step/event/gate/artifact 列表；移动端折叠为单列并消除 metadata 横向溢出。
- 浏览器在 `http://127.0.0.1:8765/?v=20260512-p1ui3` 验收 P1-UI：桌面 1512x982 下无横向溢出，移动端 390x844 下 `overflowCount=0`。
- 新增产品重置文档：`docs/architecture-v2/product-flow-reset-2026-05-12.md`。
- 产品重置核心判断：当前产品混乱不是单个面板问题，而是 Run/Step/Gate/Artifact 过早成为主对象，Dataset、VariableRoleSet、DesignSpec、RunPlan 没有形成用户主路径。
- 新增产品级 workflow contract BDD：`docs/architecture-v2/product-workflow-contract-bdd.md`，固化 Dataset -> VariableRoleSet -> ResearchQuestion -> DesignSpec -> RunPlan -> Run -> Results -> Draft -> Review/Export 的主链路。
- 新增 `tests/test_product_workflow_contract.py`，覆盖首页下一步、run blocking、5 个主工作区、workflow spine、变量角色优先、Run Plan 预检。
- 扩展 `Product/backend/overview_service.py`：`GET /api/v1/projects/{project_id}/overview` 返回 `workflow_contract`，其中 `next_action.id=confirm_variable_roles`，`run_readiness.can_start_full_run=false`，blockers 为 `variable_roles_unconfirmed/design_unconfirmed/run_plan_missing`。
- 修改 `Product/web/index.html`：一阶导航改为 `Workspace Home / Data & Design / Execution / Results & Draft / Review & Export`；研究设计和 Agent 控制台降为工具入口；首页新增 `product-next-action` 与 `workflow-spine`；Data & Design 新增 `variable-role-workflow-card`；Execution 新增 `run-plan-preflight` 和 `run-blockers`。
- 修改 `Product/web/assets/app.js`：新增 `renderWorkflowContract`、`renderVariableRoleWorkflow`、`renderExecutionPreflight`、`openDesignAction`；数据卡片不再直接触发 run，而是进入“检查并确认变量角色”。
- 修改 `Product/web/assets/styles.css`：全局视觉从厚重 serif/米色卡片转为 system font、低噪声白/灰绿工作台；新增 workflow spine、next action、variable role、run preflight/blocker 样式。
- 新增 P1-E BDD：`docs/architecture-v2/codex-phase-p1-variable-role-confirmation-bdd.md`，把变量角色确认定义为真实产品状态对象，而不是 run log 中的临时 gate note。
- 新增 `tests/test_variable_role_confirmation.py`，覆盖变量角色 draft、PUT 保存、workflow contract 解锁、前端编辑器和 Execution preflight 后继阻塞。
- 新增 `Product/backend/variable_role_service.py`，从项目数据文件推断 draft VariableRoleSet，并把用户确认结果保存到 `state/product/variable_roles.json`。
- 扩展 `Product/app.py`，新增 `GET /api/v1/projects/{project_id}/variable-roles` 与 `PUT /api/v1/projects/{project_id}/variable-roles`。
- 扩展 `Product/backend/overview_service.py`，`GET /overview` 会读取已确认 VariableRoleSet；确认后 `variable_roles` stage 变为 completed，`next_action.id=confirm_design_spec`，`variable_roles_unconfirmed` blocker 被移除。
- 扩展 `Product/web/index.html`、`Product/web/assets/app.js`、`Product/web/assets/styles.css`，Data & Variables 页新增 VariableRoleSet 编辑器，可编辑 outcome、treatment、controls、instruments、fixed_effects、cluster_by 和 note，保存后刷新 workflow contract。
- 浏览器验收已创建真实项目状态：`state/product/variable_roles.json`，其中 `roles.outcome=["wage"]`、`roles.treatment=["trained"]`、`roles.controls=["edu","experience"]`，`status=approved`，`evidence_level=local_file`。

## 已验证证据

- P2-A TDD 失败证据：`python3 -m unittest tests.test_dataset_quality_profile -v` 首次有效失败为 `KeyError: 'quality_profile'` 和前端缺少 `data-quality-profile-panel`，说明目标行为尚未实现。
- P2-A 目标测试：`python3 -m unittest tests.test_frontend_chinese_copy tests.test_dataset_quality_profile -v`，11 tests OK。
- P2-A 全量回归：`python3 -m unittest discover -s tests -v`，148 tests OK，skipped=1。
- P2-A 静态检查：`python3 -m py_compile Program/run_paper.py Program/workbench/observability.py Product/backend/observability_service.py Product/backend/project_service.py Product/backend/overview_service.py Product/app.py` 通过；`node --check Product/web/assets/app.js` 通过。
- P2-A API 验收：`GET /api/v1/projects/proj_undergraduate_thesis/datasets` 返回 `analysis_sample.csv`，`quality_profile.evidence_level=local_file`、`readiness_status=ready`、`row_count=12`、`column_count=4`、`missing_rate=0`、`numeric_column_count=4`。
- P2-A 可视化验收：Safari + Computer Use 打开 `http://127.0.0.1:8765/?v=20260513-p2a`，进入“数据与设计”后可见 `数据质量画像`、样本 12、缺失率 0%、字段画像和中文 `确认变量角色` 标签；布局纵向排列，不再与右侧属性检查器挤压。
- `git status --short --branch` 输出：`## main...origin/main`。
- 基线测试输出：`Ran 48 tests in 4.487s`，`OK (skipped=1)`。
- StatsPAI 核心文章 DOM 抽取到的标题和章节包括：为什么是 Python、StatsPAI 包在做什么、方法覆盖、面向 Agent 的设计、时间线、接下来、参与。
- TDD 失败证据：新增 `tests.test_observable_execution_frontend` 后，最初 6 条测试因 DOM/JS/CSS 缺少 P0 observability 元素和函数而失败；第 7 条历史 run 恢复态测试也先失败。
- P1-A 前端 TDD 失败证据：新增行为 5-8 后，`python3 -m unittest tests.test_observable_execution_frontend -v` 先有 4 条失败，原因是前端缺少 `data-gate-resolve-action`、`resolveGate`、刷新和 `gate.resolution` 展示。
- 最终回归：`python3 -m unittest discover -s tests -v`，`Ran 59 tests in 5.570s`，`OK (skipped=1)`。
- 编译/语法：`python3 -m py_compile Program/run_paper.py Program/workbench/observability.py Product/backend/observability_service.py Product/backend/project_service.py Product/app.py` 通过；`node --check Product/web/assets/app.js` 通过。
- 手动验收：`http://127.0.0.1:8877` 打开实证执行页，`run_3ffe1e6c1f53` 渲染完整 steps、events、HITL gates 和 artifact evidence；切换到旧 run `run_c617f095b232` 显示“缺少可观察执行轨迹”和“点击启动试运行”的恢复提示；Step 卡片宽度 368.8px，小于 387.8px 容器宽度，无横向撑破。
- P1 API 验证：`tests.test_observable_execution.ObservableExecutionTests.test_bdd_3_gate_resolve_api_updates_gate_event_and_manifest` 通过，确认 `gates.json`、`run_events.jsonl`、`run_manifest.json` 都被更新。
- P1-A 浏览器验收：真实页面显示 confirm/reject/adjust 和 note；填写“浏览器验收：确认数据字段进入后续分析。”并点击确认后，`gate_dataset_fields` 显示 `action=confirm` 和 resolved_at，事件流包含 resolved 事件；浏览器 console error 为 0。
- P1-B TDD 失败证据：datasets API 最初仍返回 `_meta.evidence_level=mock`；run endpoint 最初未返回 `dataset_source`；前端测试最初找不到 `data-start-dataset-run` 和 run payload `dataset_path`。
- P1-B 最终回归：`python3 -m unittest discover -s tests -v`，`Ran 65 tests in 11.121s`，`OK (skipped=1)`。
- P1-B 编译/语法：`python3 -m py_compile Product/backend/overview_service.py Product/backend/project_service.py Product/app.py Program/run_paper.py Program/workbench/observability.py Product/backend/observability_service.py` 通过；`node --check Product/web/assets/app.js` 通过。
- P1-B API 验证：`GET /api/v1/projects/proj_undergraduate_thesis/datasets` 返回 `analysis_sample.csv`，`row_count=12`、`column_count=4`、`role=configured_final_dataset`、`evidence_level=local_file`。
- P1-B 手动验收：`run_fc725d15b3c0` 的 `state/runs/run_fc725d15b3c0/run_manifest.json` 包含 `dataset_source`，浏览器 console errors/warnings 为 0。
- P1-C TDD 失败证据：新增 `test_bdd_3_observability_exposes_dataset_source_as_run_evidence` 后先失败，原因是 observability 顶层没有 `dataset_source`；新增前端测试先失败，原因是页面缺少 `observable-dataset-source`。
- P1-C 目标测试：`python3 -m unittest tests.test_observable_execution -v`，4 tests OK；`python3 -m unittest tests.test_observable_execution_frontend -v`，11 tests OK；`tests.test_product_v1_local.ProductV1LocalTests.test_run_endpoint_records_selected_dataset_source` 通过。
- P1-C 最终回归：`python3 -m unittest discover -s tests -v`，`Ran 67 tests in 36.309s`，`OK (skipped=1)`。
- P1-C 编译/语法：`python3 -m py_compile Product/backend/observability_service.py Product/backend/project_service.py Product/app.py` 通过；`node --check Product/web/assets/app.js` 通过。
- P1-C API 验证：`GET /api/v1/projects/proj_undergraduate_thesis/runs/run_641c9770a1a8/observability` 顶层和 manifest 都包含 `dataset_source.path=Data/Final/analysis_sample.csv`、`evidence_level=local_file`、`role=configured_final_dataset`、`row_count=12`、`column_count=4`。
- P1-C 浏览器验收：执行页 Run 数据源面板文本为 `analysis_sample.csv / Data/Final/analysis_sample.csv / 本地文件 / 12 行 · 4 列 / csv / configured_final_dataset / exists=true`，console errors/warnings=0。
- P1-D TDD 失败证据：新增 API 测试后先 `KeyError: variable_roles`；新增前端测试后先失败，原因是缺少 `observable-variable-roles`。
- P1-D 目标测试：`python3 -m unittest tests.test_observable_execution -v`，5 tests OK；`python3 -m unittest tests.test_observable_execution_frontend -v`，12 tests OK。
- P1-D 最终回归：`python3 -m unittest discover -s tests -v`，`Ran 69 tests in 8.408s`，`OK (skipped=1)`。
- P1-D 编译/语法：`python3 -m py_compile Product/backend/observability_service.py Product/backend/project_service.py Product/app.py` 通过；`node --check Product/web/assets/app.js` 通过。
- P1-D API 验证：`GET /api/v1/projects/proj_undergraduate_thesis/runs/run_641c9770a1a8/observability` 返回 `variable_roles.evidence_level=local_execution`、`confirmation_gate_id=gate_dataset_fields`、`confirmation_status=open`。
- P1-D 浏览器验收：变量角色确认面板显示 `outcome=wage`、`treatment=trained`、`controls=edu, experience`、`instruments=未识别`，console errors/warnings=0。
- P1-UI TDD 失败证据：新增行为 13 后先失败，原因是 `index.html` 缺少 `execution-control-panel`。
- P1-UI 目标测试：`python3 -m unittest tests.test_observable_execution_frontend -v`，13 tests OK。
- P1-UI 最终回归：`python3 -m unittest discover -s tests -v`，`Ran 70 tests in 5.553s`，`OK (skipped=1)`。
- P1-UI 编译/语法：`python3 -m py_compile Program/run_paper.py Program/workbench/observability.py Product/backend/observability_service.py Product/backend/project_service.py Product/app.py` 通过；`node --check Product/web/assets/app.js` 通过。
- P1-UI 浏览器验收：桌面 computed style 显示 `font=-apple-system, "system-ui", "Segoe UI", sans-serif`、`panelRadius=8px`、`panelPadding=12px`、`contextColumns=451.594px 677.406px`、`overflowCount=0`；移动端 390x844 显示 `contextColumns=319px`、`toolbarDirection=column`、`overflowCount=0`、`metadataWhiteSpace=pre-wrap`。
- 产品重置 TDD 失败证据：`python3 -m unittest tests.test_product_workflow_contract -v` 最初 2 条 API 测试因 `KeyError: workflow_contract` 报错，4 条前端测试因缺少新 IA 和新渲染函数失败。
- 产品重置目标测试：`python3 -m unittest tests.test_product_workflow_contract tests.test_dataset_frontend tests.test_observable_execution_frontend -v`，23 tests OK。
- 产品重置最终回归：`python3 -m unittest discover -s tests -v`，`Ran 76 tests in 6.385s`，`OK (skipped=1)`。
- 产品重置编译/语法：`python3 -m py_compile Program/run_paper.py Program/workbench/observability.py Product/backend/observability_service.py Product/backend/project_service.py Product/backend/overview_service.py Product/app.py` 通过；`node --check Product/web/assets/app.js` 通过。
- 产品重置浏览器验收：重启 8765 后打开 `http://127.0.0.1:8765/?v=20260512-flow2`；Workspace Home 显示 5 个工作区、`confirm_variable_roles` 和 9 个 workflow spine 阶段；Data & Design 显示真实数据文件并只引导变量角色确认；Execution 显示 `can_start_full_run=false` 和 3 个 blockers 后再显示 run evidence；桌面和 390x844 移动端无横向溢出；console errors/warnings=0。
- P1-E TDD 失败证据：`python3 -m unittest tests.test_variable_role_confirmation -v` 首次 5 条失败，原因是变量角色 API 尚未实现、前端缺少编辑器和保存 API。
- P1-E 目标测试：`python3 -m unittest tests.test_variable_role_confirmation -v`，`Ran 5 tests`，OK。
- P1-E 目标回归：`python3 -m unittest tests.test_variable_role_confirmation tests.test_product_workflow_contract tests.test_dataset_frontend tests.test_observable_execution_frontend tests.test_api_contract_v2 -v`，`Ran 39 tests`，OK。
- P1-E 全量回归：`python3 -m unittest discover -s tests -v`，`Ran 81 tests in 8.594s`，`OK (skipped=1)`。
- P1-E 编译/语法：`python3 -m py_compile Product/app.py Product/backend/overview_service.py Product/backend/variable_role_service.py Product/backend/project_service.py Product/backend/observability_service.py Program/run_paper.py Program/workbench/observability.py` 通过；`node --check Product/web/assets/app.js` 通过。
- P1-E 浏览器验收：`http://127.0.0.1:8765/?v=20260513-p1e` 显示 VariableRoleSet 编辑器；保存后状态为 `approved · local_file`，meta 为 `Data/Final/analysis_sample.csv · version=1 · evidence_level=local_file`；Overview API 返回 `next_action.id=confirm_design_spec`，blockers 只剩 `design_unconfirmed/run_plan_missing`；Execution preflight 仍显示 `CAN_START_FULL_RUN=FALSE`；console errors/warnings=0。

## 关键文件路径

- `Product/app.py`
- `Product/backend/project_service.py`
- `Product/backend/observability_service.py`
- `Product/backend/overview_service.py`
- `Product/backend/variable_role_service.py`
- `Product/backend/project_service.py`
- `Product/app.py`
- `Product/web/index.html`
- `Product/web/assets/app.js`
- `Product/web/assets/styles.css`
- `tests/test_observable_execution.py`
- `tests/test_observable_execution_frontend.py`
- `tests/test_dataset_frontend.py`
- `tests/test_product_v1_local.py`
- `tests/test_api_contract_v2.py`
- `tests/test_agent_cluster_frontend_interactions.py`
- `docs/architecture-v2/kimi-observable-execution-ui-handoff-2026-05-10.md`
- `docs/architecture-v2/statspai-methodology-synthesis-2026-05-12.md`
- `docs/architecture-v2/codex-phase-p0-observable-ui-bdd.md`
- `docs/architecture-v2/codex-phase-p1-gate-resolve-bdd.md`
- `docs/architecture-v2/codex-phase-p1-gate-resolve-frontend-bdd.md`
- `docs/architecture-v2/codex-phase-p1-dataset-run-bdd.md`
- `docs/architecture-v2/codex-phase-p1-run-dataset-source-ui-bdd.md`
- `docs/architecture-v2/codex-phase-p1-variable-roles-bdd.md`
- `docs/architecture-v2/codex-phase-p1-observable-console-density-bdd.md`
- `docs/architecture-v2/product-flow-reset-2026-05-12.md`
- `docs/architecture-v2/product-workflow-contract-bdd.md`
- `tests/test_product_workflow_contract.py`
- `tests/test_variable_role_confirmation.py`
- `docs/architecture-v2/codex-phase-p1-variable-role-confirmation-bdd.md`
- `state/product/variable_roles.json`

## 不能重复探索的结论

- 不要把上层 `/Users/mahaoxuan/Desktop/经济学论文` 当作 git 根目录；真实 repo 是 `实证论文项目模板`。
- 当前 P0 不需要大面积重构 UI；应在现有 `实证执行` 页面接真实 observability。
- `GET /api/v1/projects/{project_id}/runs/{run_id}/observability` 后端已经存在；本轮主要补前端真实消费。
- StatsPAI 方法论要求系统分层：Skill/Agent 编排负责“做什么”，StatsPAI/统计包负责“怎么做”；前端不能伪装执行结果，必须显示 evidence_level。
- 8765 端口已重启为当前工作树的 `python3 -m uvicorn Product.app:app --host 127.0.0.1 --port 8765`；浏览器静态资源可能缓存旧 JS，因此 `index.html` 已更新为 `?v=20260513-p1e` 版本 query。
- 旧 run 可能只有 run store JSON，没有 `state/runs/{run_id}` 下的 observability 文件；前端必须把它当作可恢复历史状态处理。
- Gate resolve 已完成后端和前端最小闭环；不要再回退到“P1 接入”禁用按钮。
- P1-B 当前只实现“选择项目内本地数据文件并启动 run”，不是 multipart 上传；这是为了先打通 CoPaper/StatsPAI 式真实数据入口和可追溯 run source，不把 UI 做成伪上传。
- `dataset_path` 必须限制在项目目录内的相对路径；绝对路径和 `..` 已按安全边界拒绝。
- P1-C 只做文件级数据理解证据，不做变量级 schema 编辑；下一步必须进入变量/角色确认，不应把文件级 shape 误当成完整数据理解。
- P1-D 只把变量角色作为一等可见对象展示，并绑定 HITL gate 状态；还没有结构化变量编辑/写回 API。
- P1-UI 已确认此前执行页视觉问题不是单个 bug，而是信息架构和密度问题：不要回到大号 serif、24px 圆角、分散大卡片的论文式布局；实证执行页应保持 scoped system font、8px 控制台卡片和上下文网格。
- 产品主流程已重置为 Project -> Dataset -> VariableRoleSet -> ResearchQuestion -> DesignSpec -> RunPlan -> Run -> Results -> Draft -> Review/Export；不要再把 run selector 作为首页主行动。
- VariableRoleSet 已经是产品级本地状态，保存路径为 `state/product/variable_roles.json`；`workflow_contract` 已读取该状态，不要再把变量角色确认只写在 run gate 或 note 里。
- DesignSpec 和 RunPlan 已经是产品级本地状态，保存路径分别为 `state/product/design_spec.json`、`state/product/run_plan.json`；`workflow_contract` 已读取这两个 approval 并推进到 `start_full_run`。
- Feynman 当前不是源码依赖；本轮按用户参考采用 `callable_external` 研究引擎设计，只把 `embedded=false`、license、repository 等 provenance 写入 run metadata。
- P1-H 已新增 `POST /api/v1/projects/{project_id}/runs/full`，不要再把旧 dry-run 按钮当作产品主行动。
- Results & Draft 已有最小 evidence binding；不要再把 drafts API 当作唯一草稿入口。
- FindingCard 的系数、标准误、p 值和样本量必须来自 `Results/json/analysis_result.json`，不要从 Markdown 草稿解析。
- FindingCard review 是用户本地决策证据，`evidence_level=local_file`；真实估计结果仍是 `local_execution`。
- 旧 review 不应自动套用到新 run；当前实现要求 persisted review 的 `run_id` 和 `artifact_path` 与当前 finding 匹配。
- StatsPAI/StatsAPI 现在已经不是单纯候选后端：对 CSV OLS full run，系统会真实调用 `statspai.regress()` 并写出独立 `Results/json/statspai_execution_result.json`。但这只覆盖当前 OLS validation，不代表 DID/IV/RDD/PSM/DML 已接入。
- 本地 Codex 已作为 provider readiness 暴露到 `workflow_contract.intelligence_layer`，但实际执行开关默认关闭。不要把“可检测到 Codex CLI”误写成“Supervisor 已经真实派工”。
- 当前大模型中控边界：工程状态机负责可复现和审计；本地 Codex Supervisor 应负责计划、派工、审阅和失败恢复。下一步必须让 Supervisor 产出可持久化 plan artifact，而不是继续只在 UI 上展示 agent 名称。

## 下一步第一件事

写 P2-AA BDD 和失败测试：新增 Agent Task Queue execution backend selection。重点是 `reviewed_for_dispatch` 任务只能先选择 StatsPAI/Python/StataMCP 这类执行后端和执行边界；选择后端仍不等于执行；执行必须产生日志、结果文件、evaluator checks 和 `local_execution` 证据。禁止后端选择动作自动改写 ResearchQuestion、VariableRoleSet、DesignSpec、RunPlan、FindingCard 或 Manuscript。

## 未解决风险

- `Product/serve_product.py` 直接运行会因 `ModuleNotFoundError: No module named 'Product'` 失败；模块方式启动或 `uvicorn Product.app:app` 可用，后续可单独补入口测试和修复。
- P1-B 还没有 multipart 上传；当前入口要求数据文件已经存在于项目 `Data/` 目录下。
- `state/product/variable_roles.json`、`state/product/design_spec.json`、`state/product/run_plan.json`、`state/product/finding_reviews.json`、`state/product/manuscript_candidate_reviews.json`、`state/product/manuscript_candidate_promotions.json`、`state/product/export_package_manifest.json` 是浏览器/API 验收创建的真实本地运行状态；当前未纳入 git 跟踪，后续提交前需要决定是否作为样例状态保留、迁移到 fixtures，或继续作为 gitignored runtime artifacts。
- StatsPAI 独立验证目前只覆盖 CSV OLS；真实 CFPS `.dta` 还没有进入 StatsPAI/StataMCP 执行层，DTA 仍停在字段画像和变量角色候选流程。
- StataMCP/Stata 仍未产生日志、do-file、结果 JSON 或 evaluator checks，不能标记为 `local_execution`。
- DID/IV/RDD/PSM/DML 当前只有方法工作流 checklist 和前置条件阻塞，还没有真实 StatsPAI/StataMCP/Python 执行后端。
- 前端隐藏页面也渲染了一份方法工作流 DOM，浏览器可见面板正常，但后续可做 accessibility/DOM 去重。
- 本地 Codex Supervisor 已可见但未执行派工；`EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC` 未启用时必须继续 blocked，避免把工程状态机伪装成大模型中控。
- 真实 CFPS 变量角色候选仍是启发式。启发式意思是“根据字段名、标签和简单规则猜测”，它只能帮用户缩小审阅范围，不能直接进入论文分析；P2-W 已把它和正式 VariableRoleSet 用 draft 状态隔开，但后续仍需用户编辑保存、DesignSpec/RunPlan 重新确认和真实执行后才可作为研究证据。

## 2026-05-17 Pipeline MVP Review 交接增量

### 当前目标

对 P2-V 到 P2-Z 做一次真实产品闭环验收，确认当前系统已经不是单页功能堆叠，而是“选题 -> 智能中控计划 -> 人工派工审阅 -> 变量/方法/结果/导出 gate”的 AI 实证研究流水线 MVP。

### 已完成事项

- 修复 SupervisorPlan 审批状态显示：旧本地状态如果只有 `status=approved`、没有 `human_review.action`，页面现在显示 `人工审批 已批准`。
- 给 Review & Export 的 `docx 最终导出` 按钮增加稳定 id `verifier-final-export-button`，便于自动化确认 `can_export_docx=false` 时保持 disabled。
- 更新 `Product/web/index.html` 静态资源版本到 `20260517-pipeline-mvp-review`，避免浏览器缓存旧 JS/CSS。
- 保存 4 张浏览器验收截图到 `artifacts/ui-checks/`。

### 已验证证据

- 目标补丁测试：`python3 -m unittest tests.test_supervisor_plan.SupervisorPlanFrontendTests tests.test_verifier_export_gates.VerifierExportGatesFrontendTests -v`，6 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，258 tests OK，skipped=1。
- 静态检查：`python3 -m py_compile Product/app.py Product/backend/*.py` 通过；`node --check Product/web/assets/app.js` 通过；`git diff --check` 通过。
- 浏览器验收入口：`http://127.0.0.1:8768/?v=20260517-pipeline-mvp-review-final2`。
- 浏览器验收 10 项全部通过：topic-first home、confirmed ResearchQuestion、Codex Supervisor 说明、approved SupervisorPlan 当前显示、Agent Queue 摘要优先、dispatch reviewed 但不执行、candidate/formal VariableRoleSet 分离、方法 checklist ready/blocked、Finding/Manuscript provenance、Review Export verifier gates。
- 浏览器验收 API 状态：ResearchQuestion `confirmed/local_file`；SupervisorPlan `approved/can_dispatch=true/local_execution`；Agent Queue `ready_for_dispatch` 且 3 个任务都 `dispatch_reviewed`、`can_execute=false`；Verifier Checks `status=failed`、`can_export_docx=false`、8 个 checks。
- 浏览器验收结果：`errors=[]`、`badResponses=[]`。

### 关键文件路径

- `Product/web/assets/app.js`
- `Product/web/index.html`
- `tests/test_supervisor_plan.py`
- `tests/test_verifier_export_gates.py`
- `artifacts/ui-checks/pipeline-mvp-home.png`
- `artifacts/ui-checks/pipeline-mvp-data-variables.png`
- `artifacts/ui-checks/pipeline-mvp-execution.png`
- `artifacts/ui-checks/pipeline-mvp-review-export.png`

### 不能重复探索的结论

- Agent Task Queue 的 `dispatch_reviewed` 仍不是执行授权；它只说明用户看过派工任务，下一步必须选择真实执行后端。
- `can_execute=false` 是刻意边界，不能为了“看起来完成”而在 UI 或 API 中放开。
- Review & Export 的 export package、preview 和 scorecard 都不能替代 verifier gates；`docx_export_preflight` blocked 时最终 docx 导出必须 disabled。
- SupervisorPlan 的 approved 状态要能兼容旧本地状态文件，不能因为缺少新版 `human_review` 字段而误导用户“尚未审批”。

### 下一步第一件事

P2-AA：给 Agent Task Queue 增加执行后端选择层。按 BDD/TDD 先定义 `reviewed_for_dispatch -> backend_selected -> execution_ready`，再接 StatsPAI/Python/StataMCP 的真实日志、结果文件和 evaluator checks。仍不允许后端选择动作直接改写研究设定或论文正文。

### 未解决风险

- 当前截图文件是验收产物，若仓库规则不跟踪 `artifacts/ui-checks/*.png`，需要在最终报告中给出本地路径而不是强行纳入版本控制。
- `state/product/agent_task_queue.json` 是本次浏览器验收修改过的 gitignored runtime 状态：3 个任务都已人工审阅，但仍不可执行。
- StatsPAI 真实执行目前只覆盖当前 CSV OLS 验证；真实 CFPS `.dta` 和 DID/IV/RDD/PSM/DML 仍不能标记为 `local_execution`。
- 本地 Codex Supervisor 默认仍是“可生成计划 artifact / 可审阅”，不是已启用的自动派工执行器。

## 2026-05-17 P2-V Human Dispatch Audit 交接增量

### 当前目标

把 P2-U 生成的 Agent Task Queue 从“可派工草案”推进到“每项任务必须人工派工审阅”的执行前安全层。

### 已完成事项

- 新增 BDD：`docs/architecture-v2/codex-phase-p2-dispatch-audit-bdd.md`。
- 新增测试：`tests/test_agent_task_dispatch_audit.py`。
- 新增服务：`Product/backend/task_dispatch_service.py`。
- 扩展 `Product/backend/agent_task_queue_service.py`：队列 item 统一带 `can_execute=false`、`next_action`、`dispatch_readiness`、`dispatch_review`。
- 扩展 `Product/app.py`：新增 `PUT /api/v1/projects/{project_id}/agent-task-queue/tasks/{task_id}/dispatch-review`。
- 扩展 `Product/web/assets/app.js` 和 `Product/web/assets/styles.css`：前端显示派工审阅区，支持批准、要求修改、阻断。

### 已验证证据

- `python3 -m unittest tests/test_agent_task_dispatch_audit.py -v`：5 tests OK。
- `python3 -m unittest tests/test_agent_task_queue.py tests/test_product_workflow_contract.py -v`：21 tests OK。
- `python3 -m unittest discover -s tests -v`：239 tests OK，skipped=1。
- `python3 -m py_compile Product/app.py Product/backend/*.py`：通过。
- `node --check Product/web/assets/app.js`：通过。
- `git diff --check`：通过。
- 浏览器自动化验收 `http://127.0.0.1:8768/?v=20260517-p2v-dispatch-audit`：队列可见，3 个批准按钮可见，5 个 details 默认折叠，点击首个 `批准派工` 后显示已审阅/选择执行后端，console errors=0。

### 不能重复探索的结论

- 队列创建不是执行授权；`ready_for_dispatch` 只是“草案可审阅”。
- `approve` 派工审阅不是启动任务；P2-V 仍保持 `can_execute=false`，后续必须单独做执行后端选择和真实任务调度。
- `dispatch_review_required` 放在 `dispatch_readiness.blockers`，不是旧的 task-level `blockers`，以免破坏 P2-U 的队列摘要语义。
- 派工审阅只能写 `state/product/agent_task_queue.json`，不能修改 ResearchQuestion、VariableRoleSet、DesignSpec、RunPlan 或 SupervisorPlan。

### 下一步第一件事

已完成 P2-W；继续看下方 P2-W 交接增量，下一步改为 P2-X 方法工作流 checklist。

## 2026-05-17 P2-W Real VariableRoleCandidate Promotion 交接增量

### 当前目标

把 P2-L 的 `approved_candidate` 从“候选被审阅过”推进到“可以生成正式 VariableRoleSet 草稿”，但继续阻止它直接改写正式研究状态。

### 已完成事项

- 新增 BDD：`docs/architecture-v2/codex-phase-p2-real-variable-role-promotion-bdd.md`。
- 新增测试：`tests/test_real_variable_role_promotion.py`。
- 扩展 `Product/backend/variable_role_service.py`：新增 `state/product/variable_roles_drafts.json`、promotion、draft applied 标记和正式保存 provenance。
- 扩展 `Product/app.py`：新增 `POST /api/v1/projects/{project_id}/variable-role-candidates/{candidate_id}/promote`。
- 扩展 `Product/web/assets/app.js` 和 `Product/web/assets/styles.css`：候选卡新增“基于候选创建变量角色草稿”，正式编辑区显示“正式变量角色”，保存动作仍走 `handleSaveVariableRoles()`。

### 已验证证据

- RED：`python3 -m unittest tests.test_real_variable_role_promotion -v` 首次 4 条失败，原因是 promote API 404 且前端缺少“候选建议 / 正式变量角色 / promoteVariableRoleCandidate”。
- 目标测试：`python3 -m unittest tests.test_real_variable_role_promotion -v`，4 tests OK。
- 相邻回归：`python3 -m unittest tests.test_real_variable_role_promotion tests.test_variable_role_candidates tests.test_variable_role_confirmation -v`，17 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，243 tests OK，skipped=1。
- 静态检查：`python3 -m py_compile Product/app.py Product/backend/variable_role_service.py` 通过；`node --check Product/web/assets/app.js` 通过；`git diff --check` 通过。
- 浏览器验收：`http://127.0.0.1:8768/?v=20260517-p2w-real-variable-promotion` 可见 `候选建议`、`正式变量角色` 和 1 个 promotion 按钮；点击后出现草稿/保存入口，`badResponses=[]`、`consoleErrors=[]`；截图 `/tmp/p2w-real-variable-promotion-clean.png`。

### 不能重复探索的结论

- `approved_candidate` 不是正式变量角色，只代表候选建议已被人工审阅。
- Promotion 只创建 `variable_role_set_draft`，写入 `state/product/variable_roles_drafts.json`，不能覆盖 `state/product/variable_roles.json`。
- 只有用户在正式变量角色编辑器中显式保存，`PUT /variable-roles` 才能把草稿 provenance 写入正式状态。
- Promotion 也不负责重建 DesignSpec/RunPlan；这些是下一阶段方法工作流和状态失效/重确认问题。

### 下一步第一件事

P2-X：为 DesignSpec/RunPlan 增加方法工作流 checklist，让 OLS/DID/IV/RDD/PSM/DML 的前置条件、诊断和 evaluator checks 成为可审计产品状态。

## 2026-05-17 P2-X Method Workflow Checklist 交接增量

### 当前目标

把 DesignSpec/RunPlan 中的方法选择从自由文本任务，升级为带前置条件、诊断要求和阻塞原因的可审计方法工作流。P2-X 的边界是“方法准入”，不是“所有方法已经真实执行”。

### 已完成事项

- 新增 BDD：`docs/architecture-v2/codex-phase-p2-method-workflow-checklist-bdd.md`。
- 新增测试：`tests/test_method_workflow_checklist.py`。
- 新增服务：`Product/backend/method_workflow_service.py`。
- 扩展 `Product/backend/design_spec_service.py`：保存 RunPlan 前调用方法工作流检查，blocked 方法返回 `method_workflow_blocked`。
- 扩展 `Product/app.py`：新增 `GET /api/v1/projects/{project_id}/method-workflows`，并让 RunPlan 保存 API 返回 blocked method details。
- 扩展 `Product/web/index.html`、`Product/web/assets/app.js`、`Product/web/assets/styles.css`：Research Design 和 Execution 页面显示方法工作流卡片，细节默认折叠。
- 更新 `tests/test_ols_execution_adapter.py`：unsupported/blocked IV 不再允许先保存进 RunPlan 再到 full run 阶段失败，而是在 RunPlan approval 阶段被拒绝。

### 已验证证据

- RED：`python3 -m unittest tests.test_method_workflow_checklist -v` 首次 5 条失败，原因是 `/method-workflows` 404、blocked DID RunPlan 仍返回 200、前端缺少 `method-workflow-panel`。
- 目标测试：`python3 -m unittest tests.test_method_workflow_checklist -v`，5 tests OK。
- 相邻回归：`python3 -m unittest tests.test_method_workflow_checklist tests.test_method_skill_catalog tests.test_design_run_plan_state_machine tests.test_ols_execution_adapter -v`，27 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，248 tests OK，skipped=1，耗时 39.867s。
- 静态检查：`python3 -m py_compile Product/app.py Product/backend/method_workflow_service.py Product/backend/design_spec_service.py Product/backend/overview_service.py` 通过；`node --check Product/web/assets/app.js` 通过；`git diff --check` 通过。
- 浏览器验收：`http://127.0.0.1:8768/?v=20260517-p2x-method-workflow` 的 Research Design 页面可见 `OLS：可执行`、`DID：缺少时间变量、处理时点`、`IV：缺少工具变量`、`RDD：缺少断点运行变量`、`PSM：可预检`、`DML：可预检`；`detailsInitiallyOpen=0`，点击 `查看方法要求` 后 `firstDetailOpen=true`，`errors=[]`，`badResponses=[]`；截图 `/tmp/p2x-method-workflow.png`。

### 关键文件路径

- `docs/architecture-v2/codex-phase-p2-method-workflow-checklist-bdd.md`
- `tests/test_method_workflow_checklist.py`
- `Product/backend/method_workflow_service.py`
- `Product/backend/design_spec_service.py`
- `Product/app.py`
- `Product/web/index.html`
- `Product/web/assets/app.js`
- `Product/web/assets/styles.css`

### 不能重复探索的结论

- `method_catalog` 仍是本地方法准入目录；`method_workflows` 是 RunPlan 保存前的执行准入门，二者不要混成一个对象。
- Blocked DID/IV/RDD 等方法必须在 RunPlan approval 前被拒绝，不要回到“先保存成功，full run 时再失败”的模式。
- PSM/DML 的 `ready` 只代表具备 outcome/treatment/covariates 可预检，不代表已经真实执行。
- 除非真实 StatsPAI/StataMCP/Python 后端写出日志和结果产物，否则 DID/IV/RDD/PSM/DML 不能标记 `local_execution`。

### 下一步第一件事

P2-Y：写 Reviewer Scorecard BDD 和失败测试，把 AI/审稿意见转换为 5 个评分维度、证据绑定和后续任务建议；建议任务必须等待人工接受，不能自动写入 Agent Task Queue。

## 2026-05-14 P2-N/P2-O StatsPAI Validation 与 LLM Supervisor 交接增量

### 当前目标

把系统从“工程状态机 + 候选统计后端”推进到“统计执行有独立验证、智能中控状态可见”。用户指出没有底层大模型中控会偏离产品构想，本轮已把本地 Codex Supervisor 显式接入 workflow contract，但实际 Codex 派工尚未启用。

### 已完成事项

- 新增 `docs/architecture-v2/codex-phase-p2-statspai-execution-validation-bdd.md`。
- 扩展 `tests/test_ols_execution_adapter.py`，要求 StatsPAI 可用时生成独立 validation artifact。
- 扩展 `Product/backend/project_service.py`，新增 `execute_statspai_ols_validation()`，调用 `statspai.regress()` 并写出 `Results/json/statspai_execution_result.json`。
- 扩展 `tests/test_observable_execution_frontend.py`、`Product/web/assets/app.js`、`Product/web/assets/styles.css`，在实证执行页展示“独立后端验证”。
- 扩展 `tests/test_product_workflow_contract.py`，要求 `workflow_contract.intelligence_layer` 声明 LLM Supervisor。
- 扩展 `Product/backend/overview_service.py`，新增 `build_intelligence_layer_contract()`，读取本地 Codex provider readiness。
- 扩展 `Product/web/index.html`、`Product/web/assets/app.js`、`Product/web/assets/styles.css`，首页新增“智能中控”面板。

### 已验证证据

- 全量回归：`python3 -m unittest discover -s tests -v`，203 tests OK，skipped=1。
- 静态检查：`node --check Product/web/assets/app.js` 通过；`python3 -m py_compile Product/backend/overview_service.py Product/backend/project_service.py Product/app.py` 通过。
- API：`GET /api/v1/providers/local-codex` 返回 `available=true`、`path=/Users/mahaoxuan/.local/bin/codex`、`version=codex-cli 0.130.0`、`execution_enabled=false`。
- API：首页 overview 返回 `workflow_contract.intelligence_layer.status=blocked`，blocker 为 `local_codex_execution_not_enabled`，并包含 `pipeline_data/pipeline_design/pipeline_execution/pipeline_manuscript` 派工计划。
- 可视化：Chrome + Computer Use 打开 `http://127.0.0.1:8765/?v=20260514-p2n-supervisor1`，首页显示“智能中控”“本地 Codex Supervisor 未启用”“允许执行=否”和派工计划。
- 可视化/API：点击“启动完整实证执行”后，最终复核 run `run_bb423547439c` 的 observability 返回“独立后端验证”“passed”“statspai.regress”“Results/json/statspai_execution_result.json”。

### 不能重复探索的结论

- 当前不是“完全没有模型接入”，而是“模型 provider 可检测，但还没有作为执行中控运行”。这两者必须区分。
- StatsPAI 现在已实际参与 CSV OLS validation；不要再把它全部归类为未接入候选能力。
- StataMCP/Stata 仍是候选后端，尚未执行 do-file 或产生日志，不能与 StatsPAI 本轮进展混同。
- LLM Supervisor 的下一步不是继续加静态 Agent 卡片，而是生成可审计 plan artifact，并在开关启用时真实调用 Codex。

### 下一步第一件事

写 P2-P BDD/TDD：Supervisor plan artifact。未启用 `EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC` 时 API 返回 blocked；启用后调用本地 Codex，生成阶段计划、风险、派工建议、审阅要求和下一步动作，并写入本地状态文件供首页/Agents/Execution 使用。

### 未解决风险

- 真实 LLM 派工未完成；当前只是 readiness contract 和 UI 呈现。
- StatsPAI validation 只覆盖当前 CSV OLS；真实 CFPS DTA 执行、DID/IV/RDD/PSM/DML、robust/cluster 标准误仍未完成。
- 当前启发式变量候选不能进入论文分析；必须由用户正式保存 VariableRoleSet，并重建 DesignSpec/RunPlan。
- 线上版大模型与数据执行边界尚未设计：本地版可用 Codex/local data，线上版必须用云模型和上传/云对象数据。

## 2026-05-13 P1-R Clean Workbench Visual Pass 交接增量

### 当前目标

回应用户指出的“前端页面依然很脏、不够干净”和截图中的变量角色入口重叠问题。保持现有 FastAPI + vanilla 前端，不换框架，先把信息架构和视觉密度清理到可继续开发的状态。

### 已完成事项

- 阅读并参考 JupyterLab 主工作区/侧边栏/属性检查器、Grafana dashboard panel、OpenMetadata 数据资产与质量证据的公开产品文档。
- 新增 `docs/architecture-v2/codex-phase-p1-clean-workbench-bdd.md`。
- 新增 `tests/test_clean_workbench_visual_contract.py`，覆盖清洁背景、变量入口无重叠、右侧属性检查器、record/list 替代嵌套大卡片、保留现有技术栈。
- 修改 `Product/web/index.html`：加入 `clean-workbench-shell`，静态资源版本改为 `20260513-clean1`，右侧文案改为“属性检查器”。
- 修改 `Product/web/assets/app.js`：重写 `renderVariableRoleWorkflow()` 输出 `research-record-card`、`record-meta-grid`、`research-step-list` 和 `compact-action-row`。
- 修改 `Product/web/assets/styles.css`：去掉 archive shell 的纸格背景和厚重阴影，新增 clean surface、inspector rail、record/list、长路径换行和单列变量入口布局。

### 已验证证据

- TDD 失败证据：`python3 -m unittest tests.test_clean_workbench_visual_contract -v` 首次 4 失败 1 通过，失败原因符合预期。
- 目标测试：`python3 -m unittest tests.test_clean_workbench_visual_contract tests.test_archive_interface_visual_contract tests.test_frontend_chinese_copy -v`，15 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，137 tests OK，skipped=1。
- 静态检查：`python3 -m py_compile Program/run_paper.py Program/workbench/observability.py Product/backend/observability_service.py Product/backend/project_service.py Product/app.py` 通过；`node --check Product/web/assets/app.js` 通过。
- 可视化验收：Safari + Computer Use 打开 `http://127.0.0.1:8765/?v=20260513-clean1`，点击右侧“数据与设计”后，变量角色入口显示为单列记录布局，未再出现截图中的文本重叠。

### 不能重复探索的结论

- 当前视觉问题不是要继续加“个人档案感”，而是要把研究工作台做干净、可扫读、可操作。
- `variable-role-workflow-layout` 不能再使用 `grid-template-columns: minmax(0, 1fr) auto`；长路径和中文说明必须允许换行。
- 右侧栏应作为属性检查器和相邻记录索引，不应承担大面积装饰。

### 下一步第一件事

继续 P1-P：为 Review & Export 增加显式写回审批或 docx 导出预检的 BDD/TDD。若继续视觉方向，优先清理 Results & Draft / Review & Export 的记录密度和右侧属性检查器联动，而不是添加新装饰。

### 未解决风险

- Browser plugin 和 Playwright MCP 本轮均出现连接/传输问题；已用 Safari + Computer Use 兜底，但还需要后续恢复 Browser 自动化截图链路。
- P1-R 只做了第一轮清洁视觉 pass；Artifacts / Agents 还没做成完整的证据架和审计时间线。
- 当前仍有大量 P1 变更处于工作区，提交时需要 scoped stage，避免把 runtime artifacts 或无关状态混入。

## 2026-05-13 P1-F/P1-G DesignSpec 与 RunPlan 交接增量

## 2026-05-13 P1-O Review & Export Package Workbench 交接增量

### 当前目标

把 `export_status=preview_ready` 的 manuscript candidate 接入 Review & Export 工作区，并吸收用户提供的 Frontier-Eng 方法论：baseline/export preview -> evaluator checks -> feedback -> next_iteration。

### 已完成事项

- 新增 `docs/architecture-v2/codex-phase-p1-review-export-package-bdd.md`，定义 4 条 Review & Export 行为。
- 新增 `tests/test_review_export_package.py`，覆盖 export package API、evaluator checks、Frontier-Eng iteration log 和前端工作台。
- 扩展 `Product/backend/manuscript_candidate_service.py`，新增 export package 组装逻辑。
- 扩展 `Product/app.py`，新增 `GET /api/v1/projects/{project_id}/export-package`。
- 扩展 `Product/web/index.html`、`Product/web/assets/app.js`、`Product/web/assets/styles.css`，Review & Export 页面新增导出包验收台。

### 已验证证据

- 失败测试：`python3 -m unittest tests.test_review_export_package -v` 首次 4 条失败，原因符合预期。
- 目标测试：`python3 -m unittest tests.test_review_export_package -v`，4 tests OK。
- 目标回归：`python3 -m unittest tests.test_manuscript_consumption tests.test_results_draft_evidence_binding tests.test_review_export_package -v`，31 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，122 tests OK，skipped=1。
- 静态检查：`node --check Product/web/assets/app.js` 通过；相关 Python `py_compile` 通过。
- Chrome 可视化验收：`http://127.0.0.1:8765/?v=20260513-p1o` 点击 `Review & Export` 可见导出包验收台；截图为 `/tmp/empirical-workbench-review-export-p1o.png`。

### 不能重复探索的结论

- Review & Export 不是“直接下载/写回”的页面，而是最终产物进入前的 evaluator checkpoint。
- `can_write_back=false` 是当前安全边界，不是缺陷。
- Frontier-Eng 当前只借鉴闭环结构，不引入官方 benchmark 或复刻其完整仓库。

### 下一步第一件事

P1-P：围绕“显式写回审批”或“docx 导出预检”写 BDD，再写失败测试。不要直接实现覆盖源草稿。

### 当前目标

把产品主流程从 `confirm_design_spec` 推进到 `start_full_run`。已完成 DesignSpec 和 RunPlan 的 BDD、失败测试、最小后端服务、API、前端表单、workflow contract 状态推进和浏览器验收。

### 已完成事项

- 新增 `docs/architecture-v2/codex-phase-p1-design-run-plan-bdd.md`，定义 6 条 DesignSpec/RunPlan 行为。
- 新增 `tests/test_design_run_plan_state_machine.py`，覆盖 5 条 API 状态机行为和 2 条前端表单/保存行为。
- 新增 `Product/backend/design_spec_service.py`，负责读取/保存 `state/product/design_spec.json`、`state/product/run_plan.json`，并从 approved VariableRoleSet/DesignSpec 生成 draft。
- 扩展 `Product/app.py`，新增 `GET/PUT /api/v1/projects/{project_id}/design-spec` 和 `GET/PUT /api/v1/projects/{project_id}/run-plan`。
- 扩展 `Product/backend/overview_service.py`，让 `workflow_contract` 读取 approved VariableRoleSet、DesignSpec、RunPlan，依次解除 `design_unconfirmed` 和 `run_plan_missing`。
- 扩展 `Product/web/index.html`、`Product/web/assets/app.js`、`Product/web/assets/styles.css`，Data & Design 页面能保存 DesignSpec，Execution 页面能保存 RunPlan。

### 已验证证据

- 失败测试：`python3 -m unittest tests.test_design_run_plan_state_machine -v` 首次 7 条失败，失败原因是 API 404 和前端缺少确认表单/函数。
- 目标测试：`python3 -m unittest tests.test_design_run_plan_state_machine -v`，7 tests OK。
- 目标回归：`python3 -m unittest tests.test_design_run_plan_state_machine tests.test_variable_role_confirmation tests.test_product_workflow_contract tests.test_dataset_frontend tests.test_observable_execution_frontend tests.test_api_contract_v2 -v`，46 tests OK。
- 静态检查：`node --check Product/web/assets/app.js` 通过；`python3 -m py_compile Product/app.py Product/backend/overview_service.py Product/backend/variable_role_service.py Product/backend/design_spec_service.py Product/backend/project_service.py Product/backend/observability_service.py Program/run_paper.py Program/workbench/observability.py` 通过。
- 浏览器验收：`http://127.0.0.1:8765/?v=20260513-p1fg` 保存 DesignSpec 后 `next_action=confirm_run_plan`，保存 RunPlan 后 `next_action=start_full_run`、blockers 为空、`can_start_full_run=true`，console errors/warnings=0。
- 全量回归：`python3 -m unittest discover -s tests -v`，88 tests OK，skipped=1，耗时 83.833s。

### 关键文件路径

- `docs/architecture-v2/codex-phase-p1-design-run-plan-bdd.md`
- `tests/test_design_run_plan_state_machine.py`
- `Product/backend/design_spec_service.py`
- `Product/backend/overview_service.py`
- `Product/app.py`
- `Product/web/index.html`
- `Product/web/assets/app.js`
- `Product/web/assets/styles.css`
- `state/product/design_spec.json`
- `state/product/run_plan.json`

### 不能重复探索的结论

- DesignSpec/RunPlan 是产品级状态，不是某一次 run 的事件日志；它们必须放在 `state/product/`，供跨 Session 的 `workflow_contract` 恢复。
- full run readiness 必须依赖 approved VariableRoleSet、DesignSpec、RunPlan 三者同时存在；不能只凭数据或变量角色启动完整执行。
- RunPlan 的下一步不是静态展示结果，而是驱动 P1-H 的 `start_full_run`，并绑定后续 Results / Draft / Artifacts / Agents。

### 下一步第一件事

写 P1-I Results & Draft evidence binding BDD 和失败测试：确认 full-run 产出的 `analysis_result.json`、`Results/index.json`、`paper_draft.md` 能在 Results & Draft 页面形成可审计 FindingCard / DraftSection。

### 未解决风险

- `start_full_run` 已有真实产品 API/UI 闭环；下一步风险转移到 Results & Draft 是否正确绑定 full-run 产物。
- `state/product/*.json` 是本地浏览器验收产物，提交前要决定是否保留为样例状态或迁移为 fixture。
- Findings / Manuscript / Artifacts / Agents 仍未展开；应等 full run 与结果绑定稳定后再扩展。

## 2026-05-13 P1-H Full Run From RunPlan 交接增量

### 当前目标

把 `workflow_contract.next_action=start_full_run` 变成真实产品执行路径。已完成 BDD、失败测试、后端 full-run API、RunPlan provenance 绑定、前端主行动按钮和浏览器 full-run 验收。

### 已完成事项

- 新增 `docs/architecture-v2/codex-phase-p1-full-run-from-run-plan-bdd.md`，定义 full run 必须从 approved RunPlan 启动，并把 Feynman 作为 callable external research engine 参考写入 provenance。
- 新增 `tests/test_full_run_from_run_plan.py`，覆盖缺少 approved RunPlan 时阻断、approved RunPlan 启动 full run、前端主按钮和 API 契约。
- 扩展 `Product/backend/project_service.py`，新增 `execute_full_run_from_run_plan()`、`build_run_plan_binding()`、`build_research_engine_reference()`、`persist_full_run_provenance()`。
- 扩展 `Product/app.py`，新增 `POST /api/v1/projects/{project_id}/runs/full`。
- 扩展 `Product/web/index.html` 与 `Product/web/assets/app.js`，Execution ready 后显示“启动完整实证执行”主按钮，并调用 full-run API。

### 已验证证据

- 失败测试：`python3 -m unittest tests.test_full_run_from_run_plan -v` 首次 3 条失败；2 条 API 测试因 `/runs/full` 返回 405，1 条前端测试因缺少 `observable-run-full-button`、`v2api.runs.startFull`、`createFullRunFromPlan` 失败。
- 目标测试：`python3 -m unittest tests.test_full_run_from_run_plan -v`，3 tests OK。
- 目标回归：`python3 -m unittest tests.test_full_run_from_run_plan tests.test_design_run_plan_state_machine tests.test_product_v1_local tests.test_observable_execution tests.test_observable_execution_frontend tests.test_product_workflow_contract -v`，39 tests OK。

- 静态检查：`node --check Product/web/assets/app.js` 通过；`python3 -m py_compile Product/app.py Product/backend/project_service.py Product/backend/design_spec_service.py Product/backend/overview_service.py Product/backend/observability_service.py` 通过。
- 浏览器验收：`http://127.0.0.1:8765/?v=20260513-p1h` 中 Execution preflight 显示 `start_full_run` ready；点击“启动完整实证执行”生成 `run_c424d6a11af7`。
- API 验收：`run_c424d6a11af7` 的 run store 返回 `mode=full-run`、`status=succeeded`、`execution_evidence_level=local_execution`、`plan_binding.run_plan_version=1`、`research_engine.embedded=false`、`research_engine.integration_mode=callable_external`。
- Observability 验收：`GET /observability` 返回 `_meta.evidence_level=local_execution`，manifest 包含 `run_plan_binding.evidence_level=local_file` 与 Feynman-compatible external engine metadata。
- 全量回归：`python3 -m unittest discover -s tests -v`，`Ran 91 tests in 6.591s`，`OK (skipped=1)`。

### 关键文件路径

- `docs/architecture-v2/codex-phase-p1-full-run-from-run-plan-bdd.md`
- `tests/test_full_run_from_run_plan.py`
- `Product/backend/project_service.py`
- `Product/app.py`
- `Product/web/index.html`
- `Product/web/assets/app.js`
- `state/runs/run_c424d6a11af7.json`
- `state/runs/run_c424d6a11af7/run_manifest.json`
- `state/runs/run_c424d6a11af7/run_steps.json`
- `state/runs/run_c424d6a11af7/run_events.jsonl`
- `state/runs/run_c424d6a11af7/gates.json`

### 不能重复探索的结论

- Feynman 不应被复制进项目；短期按 external callable research engine 处理，中期吸收 provider、skill、workflow、provenance 设计。
- Full run 必须绑定 approved RunPlan provenance；不能只从当前数据集或旧 dry-run 直接启动。
- `execution_evidence_level=local_execution` 属于执行产物；`plan_binding.evidence_level=local_file` 属于输入契约。

### 下一步第一件事

写 P1-I Results & Draft evidence binding BDD 和失败测试：从 full run `run_c424d6a11af7` 读取 `Results/json/analysis_result.json`、`Results/index.json`、`Manuscripts/generated/paper_draft.md`，在 Results & Draft 页面显示最小 FindingCard / DraftSection，并绑定 run_id、RunPlan version、artifact path、evidence_level。

### 未解决风险

- Full run 目前复用 `Program/run_paper.py` + StatsPAI，本轮没有实际调用 Feynman CLI。
- Results & Draft 还没消费 `run_c424d6a11af7` 的结果文件。
- 后续提交前仍要处理 `state/product/*.json` 与 `state/runs/run_c424d6a11af7*` 是否保留为 fixture 或 runtime artifact。

## 2026-05-13 P1-I/P1-J Results, Draft, Claim Review 交接增量

### 当前目标

把 full-run 结果推进到 Results & Draft，并增加最小 claim review / accept-for-writing 状态。当前 `finding_trained_effect` 已经 approved，可以作为下一步 Manuscript 候选段落生成的输入。

### 已完成事项

- 新增 `docs/architecture-v2/codex-phase-p1-results-draft-evidence-binding-bdd.md`，定义 FindingCard / DraftSection evidence binding。
- 新增 `docs/architecture-v2/codex-phase-p1-claim-review-bdd.md`，定义 FindingCard 人工审阅与 accept-for-writing 行为。
- 扩展 `tests/test_results_draft_evidence_binding.py` 到 8 条行为，覆盖 no full-run、FindingCard evidence binding、DraftSection binding、approve/reject/needs_revision、非法 action/finding 和前端 claim review。
- 新增/扩展 `Product/backend/results_draft_service.py`，读取最新 successful full-run、`Results/json/analysis_result.json`、`Manuscripts/generated/paper_draft.md`，并把 review 状态持久化到 `state/product/finding_reviews.json`。
- 扩展 `Product/app.py`，新增 `GET /api/v1/projects/{project_id}/results-draft` 和 `PUT /api/v1/projects/{project_id}/results-draft/findings/{finding_id}/review`。
- 扩展 `Product/web/assets/app.js`、`Product/web/assets/styles.css`、`Product/web/index.html`，Results & Draft 页面显示 FindingCard、DraftSection evidence binding、review_status、accept-for-writing、审阅备注和 approve/needs_revision/reject 操作。

### 已验证证据

- P1-I 失败测试：`python3 -m unittest tests.test_results_draft_evidence_binding -v` 首次有效失败为 API 404 和前端缺少 `results-findings-list`、`draft-evidence-sections`、`v2api.resultsDraft.get`、`renderResultsDraftEvidence`。
- P1-J 失败测试：同一测试文件扩展后，首次失败为 `KeyError: review_status`、review API 404、前端缺少 `reviewFinding` / `data-finding-review-action`。
- 目标测试：`python3 -m unittest tests.test_results_draft_evidence_binding -v`，8 tests OK。
- 目标回归：`python3 -m unittest tests.test_results_draft_evidence_binding tests.test_full_run_from_run_plan tests.test_design_run_plan_state_machine tests.test_product_workflow_contract tests.test_api_contract_v2 -v`，35 tests OK。
- 静态检查：`node --check Product/web/assets/app.js` 通过；`python3 -m py_compile Product/app.py Product/backend/results_draft_service.py Product/backend/draft_service.py Product/backend/project_service.py` 通过。
- API 验收：`GET /api/v1/projects/proj_undergraduate_thesis/results-draft` 返回 `latest_run_id=run_c424d6a11af7`、`finding_trained_effect`、`review_status=needs_review`、`can_write_to_draft=false`；随后 `PUT .../review` approve 返回 `review_status=approved`、`evidence_level=local_file`、`can_write_to_draft=true`。
- 浏览器验收：`http://127.0.0.1:8765/?v=20260513-p1j` 的 Results & Draft 页面显示 `review_status=approved`、`accept-for-writing=yes`、approve/needs_revision/reject 三个操作、审阅备注、`review evidence: 本地文件`；overflowCount=0，console errors/warnings=0。
- 全量回归：`python3 -m unittest discover -s tests -v`，99 tests OK，skipped=1，耗时 13.177s。

### 关键文件路径

- `docs/architecture-v2/codex-phase-p1-results-draft-evidence-binding-bdd.md`
- `docs/architecture-v2/codex-phase-p1-claim-review-bdd.md`
- `tests/test_results_draft_evidence_binding.py`
- `Product/backend/results_draft_service.py`
- `Product/app.py`
- `Product/web/index.html`
- `Product/web/assets/app.js`
- `Product/web/assets/styles.css`
- `Results/json/analysis_result.json`
- `Manuscripts/generated/paper_draft.md`
- `state/product/finding_reviews.json`

### 不能重复探索的结论

- Results & Draft 已经消费 `run_c424d6a11af7` 的结果文件；不要再把 P1-I 当作未完成。
- FindingCard 的数值来自 `Results/json/analysis_result.json`，不要从 Markdown 草稿反向解析。
- `approve/reject/needs_revision` 是用户审阅状态，证据等级为 `local_file`；估计结果仍是 `local_execution`。
- review 只在 `run_id` 和 `artifact_path` 匹配当前 finding 时生效，避免新 run 误用旧审阅。

### 下一步第一件事

写 P1-L Manuscript candidate review/promote BDD 和失败测试：候选段落必须支持人工确认、驳回或要求修改；确认后的 candidate 才能进入 promote/write-back/export，并保留 candidate review provenance。

### 未解决风险

- `state/product/finding_reviews.json` 是本地验收状态，后续提交前要决定是否保留、迁移 fixture 或继续作为 runtime artifact。
- P1-K 已实现；当前 approved finding 已生成 Manuscript 段落候选，但候选本身还没有独立 review/promote 状态。
- Feynman 目前仍是 callable external research engine provenance，没有实际调用 CLI。

## 2026-05-13 P1-K Manuscript Consumption 交接增量

### 当前目标

让 Manuscript 阶段只消费已审阅、可写入正文的 FindingCard，生成可审阅正文段落候选，并保留草稿、结果文件和人工审阅决定的 provenance。已完成 BDD、失败测试、后端服务/API、前端渲染、API 验收和浏览器验收。

### 已完成事项

- 新增 `docs/architecture-v2/codex-phase-p1-manuscript-consumption-bdd.md`，定义 approved FindingCard、空状态、provenance 和前端展示行为。
- 新增 `tests/test_manuscript_consumption.py`，覆盖未 approved 不生成候选、approved 生成候选、provenance 绑定、rejected 不生成候选、前端容器/API/渲染函数。
- 新增 `Product/backend/manuscript_candidate_service.py`，从 `GET /results-draft` 的 `review_status=approved`、`can_write_to_draft=true` FindingCard 派生 `manuscript_section_candidate`。
- 扩展 `Product/app.py`，新增 `GET /api/v1/projects/{project_id}/manuscript-candidates`。
- 扩展 `Product/web/index.html`、`Product/web/assets/app.js`、`Product/web/assets/styles.css`，Results & Draft 页面显示 Manuscript candidates 和 `source_draft`、`result_artifact`、`review_decision` provenance。

### 已验证证据

- 失败测试：`python3 -m unittest tests.test_manuscript_consumption -v` 首次 5 条失败，原因是 `/manuscript-candidates` API 404 和前端缺少 candidate 容器/API/渲染函数。
- 目标测试：`python3 -m unittest tests.test_manuscript_consumption -v`，5 tests OK。
- 目标回归：`python3 -m unittest tests.test_manuscript_consumption tests.test_results_draft_evidence_binding tests.test_full_run_from_run_plan tests.test_design_run_plan_state_machine tests.test_product_workflow_contract tests.test_api_contract_v2 -v`，40 tests OK。
- 静态检查：`node --check Product/web/assets/app.js` 通过；`python3 -m py_compile Product/app.py Product/backend/manuscript_candidate_service.py Product/backend/results_draft_service.py Product/backend/draft_service.py Product/backend/project_service.py` 通过。
- 全量回归：`python3 -m unittest discover -s tests -v`，104 tests OK，skipped=1。
- API 验收：`GET /api/v1/projects/proj_undergraduate_thesis/manuscript-candidates` 返回 `manuscript_candidate_finding_trained_effect_results`，绑定 `finding_trained_effect`、`run_c424d6a11af7`、`run_plan_version=1`。
- 浏览器验收：`http://127.0.0.1:8765/?v=20260513-p1k` 的 Results & Draft 页面显示 1 个 candidate，无 `overwrite-paper-draft` 写回按钮，横向溢出数量为 0，console errors/warnings=0。

### 关键文件路径

- `docs/architecture-v2/codex-phase-p1-manuscript-consumption-bdd.md`
- `tests/test_manuscript_consumption.py`
- `Product/backend/manuscript_candidate_service.py`
- `Product/app.py`
- `Product/web/index.html`
- `Product/web/assets/app.js`
- `Product/web/assets/styles.css`
- `state/product/finding_reviews.json`
- `Results/json/analysis_result.json`
- `Manuscripts/generated/paper_draft.md`

### 不能重复探索的结论

- approved FindingCard 不是最终正文；它只能生成 Manuscript candidate，不能直接覆盖 `paper_draft.md`。
- Manuscript candidate 必须绑定 `source_draft`、`result_artifact`、`review_decision`，否则用户无法审计文本从何而来。
- rejected / needs_revision FindingCard 不得生成 candidate。
- 本阶段不调用 LLM 改写正文；先锁定证据和状态机。

### 下一步第一件事

写 P1-L BDD：候选段落必须支持人工确认、驳回、要求修改；确认后的 candidate 才能进入 promote/write-back/export。新增 candidate review 状态应持久化到 `state/product/`，并在前端展示 candidate review provenance。

### 未解决风险

- Manuscript candidate 当前是派生响应，尚未单独持久化候选审阅状态。
- 还没有 promote/write-back/export，因此不会自动更新 `Manuscripts/generated/paper_draft.md` 或生成最终 docx。
- `state/product/finding_reviews.json` 仍是本地 runtime artifact，提交前要决定是否保留为 fixture 或继续 gitignore。

## 2026-05-13 P1-M Manuscript Promote Preflight 交接增量

### 当前目标

把 approved Manuscript candidate 推进到导出前检查状态，但仍不直接改写 `Manuscripts/generated/paper_draft.md`。当前 `manuscript_candidate_finding_trained_effect_results` 已进入 `promotion_status=ready_for_export`。

### 已完成事项

- 新增 `docs/architecture-v2/codex-phase-p1-manuscript-promote-preflight-bdd.md`，定义 promote 只生成本地可审计 preflight 状态。
- 扩展 `tests/test_manuscript_consumption.py` 到 15 条行为，覆盖未审阅/被拒绝 candidate 不得 promote、approved candidate 生成 promotion preflight、缺失 candidate 结构化拒绝、前端 promote 操作。
- 扩展 `Product/backend/manuscript_candidate_service.py`，新增 `save_project_manuscript_candidate_promotion()`、`load_candidate_promotions()`、`promotion_state` provenance。
- 扩展 `Product/app.py`，新增 `POST /api/v1/projects/{project_id}/manuscript-candidates/{candidate_id}/promote`。
- 扩展 `Product/web/assets/app.js`、`Product/web/assets/styles.css`、`Product/web/index.html`，Results & Draft 页面显示 `promotion_status`、`can_write_back`、promotion evidence 和“进入导出前检查”操作；静态资源版本更新到 `?v=20260513-p1m`。

### 已验证证据

- 失败测试：`python3 -m unittest tests.test_manuscript_consumption -v` 首次 P1-M 失败为 `/promote` API 404 和前端缺少 promote preflight 标识。
- 目标测试：`python3 -m unittest tests.test_manuscript_consumption -v`，15 tests OK。
- 目标回归：`python3 -m unittest tests.test_manuscript_consumption tests.test_results_draft_evidence_binding tests.test_full_run_from_run_plan tests.test_design_run_plan_state_machine tests.test_product_workflow_contract tests.test_api_contract_v2 -v`，50 tests OK。
- 静态检查：`node --check Product/web/assets/app.js` 通过；`python3 -m py_compile Product/app.py Product/backend/manuscript_candidate_service.py Product/backend/results_draft_service.py Product/backend/draft_service.py Product/backend/project_service.py` 通过。
- 全量回归：`python3 -m unittest discover -s tests -v`，114 tests OK，skipped=1。
- API 验收：`POST /api/v1/projects/proj_undergraduate_thesis/manuscript-candidates/manuscript_candidate_finding_trained_effect_results/promote` 返回 `promotion_status=ready_for_export`、`can_export=true`、`can_write_back=false`，并写入 `state/product/manuscript_candidate_promotions.json`。
- 浏览器验收：`http://127.0.0.1:8765/?v=20260513-p1m` 的 Results & Draft 页面显示 `ready_for_export`、`can_write_back=no`、`promotion_state`、`promotion evidence` 和“进入导出前检查”按钮；无 `overwrite-paper-draft`，overflowCount=0，console errors/warnings=0。

### 关键文件路径

- `docs/architecture-v2/codex-phase-p1-manuscript-promote-preflight-bdd.md`
- `tests/test_manuscript_consumption.py`
- `Product/backend/manuscript_candidate_service.py`
- `Product/app.py`
- `Product/web/index.html`
- `Product/web/assets/app.js`
- `Product/web/assets/styles.css`
- `state/product/manuscript_candidate_promotions.json`

### 不能重复探索的结论

- Promote 不等于 write-back；`can_write_back=false` 是刻意边界。
- 只有 approved candidate 可以 promote；`needs_revision` 和 `rejected` 必须返回 409 `candidate_review_required`。
- Promotion 必须落到 `state/product/manuscript_candidate_promotions.json`，不能只存在前端状态。

### 下一步第一件事

写 P1-N BDD：`ready_for_export` candidate 如何生成可审计 write-back draft 或 export package manifest。第一版仍不要直接覆盖 `Manuscripts/generated/paper_draft.md`，应先产出独立 manifest / patch / preview。

### 未解决风险

- `state/product/manuscript_candidate_promotions.json` 是本地 runtime artifact，提交前需决定是否保留、迁移 fixture 或继续 gitignore。
- 还没有真正 write-back、docx export 或 export package manifest。
- Feynman 目前仍是 callable external research engine provenance，没有实际调用 CLI。

## 2026-05-13 P1-N Export Preflight Preview 交接增量

### 当前目标

把 `promotion_status=ready_for_export` 的正文候选推进到可检查的导出预检状态：生成 write-back preview 和 export package manifest，但仍不覆盖源草稿。

### 已完成事项

- 新增 `docs/architecture-v2/codex-phase-p1-export-preflight-bdd.md`，定义未 promote 不可导出、ready candidate 生成 preview/manifest、缺失 candidate 返回 404、前端显示 export preflight 预览。
- 扩展 `tests/test_manuscript_consumption.py` 到 19 条行为，先确认 `/export-preflight` API 404 和前端缺少 export preflight 识别符。
- 扩展 `Product/backend/manuscript_candidate_service.py`，新增 export preflight 状态读写、preview 文件生成、export package manifest 和 `export_package` provenance。
- 扩展 `Product/app.py`，新增 `POST /api/v1/projects/{project_id}/manuscript-candidates/{candidate_id}/export-preflight`。
- 扩展 `Product/web/assets/app.js`、`Product/web/assets/styles.css`、`Product/web/index.html`，在 Results & Draft candidate 卡片显示 `preview_ready`、preview path、manifest path、export evidence 和“生成写回预览”操作。

### 已验证证据

- 目标测试：`python3 -m unittest tests.test_manuscript_consumption -v`，19 tests OK。
- 相邻回归：`python3 -m unittest tests.test_manuscript_consumption tests.test_results_draft_evidence_binding tests.test_full_run_from_run_plan tests.test_design_run_plan_state_machine tests.test_product_workflow_contract tests.test_api_contract_v2 -v`，54 tests OK。
- 静态检查：`node --check Product/web/assets/app.js` 通过；`python3 -m py_compile Product/app.py Product/backend/manuscript_candidate_service.py Product/backend/results_draft_service.py Product/backend/draft_service.py Product/backend/project_service.py` 通过。
- 全量回归：`python3 -m unittest discover -s tests -v`，118 tests OK，skipped=1；更新 `Tasks/` 后收尾复查同命令仍为 118 tests OK，skipped=1。
- API 验收：candidate 当前返回 `export_status=preview_ready`、`writeback_preview_path=Manuscripts/generated/previews/manuscript_candidate_finding_trained_effect_results.md`、`export_manifest_path=state/product/export_package_manifest.json`、`can_write_back=false`、`export_package` provenance。

### 关键文件路径

- `docs/architecture-v2/codex-phase-p1-export-preflight-bdd.md`
- `tests/test_manuscript_consumption.py`
- `Product/backend/manuscript_candidate_service.py`
- `Product/app.py`
- `Product/web/index.html`
- `Product/web/assets/app.js`
- `Product/web/assets/styles.css`
- `state/product/export_package_manifest.json`
- `Manuscripts/generated/previews/manuscript_candidate_finding_trained_effect_results.md`

### 不能重复探索的结论

- Export preflight 不等于 source draft write-back；`can_write_back=false` 仍是刻意边界。
- `export-preflight` 只允许 `promotion_status=ready_for_export` 的 candidate；未 promote candidate 必须返回 409 `candidate_promotion_required`。
- Preview 和 manifest 都是 `local_file` 证据；不应只在前端显示导出状态。

### 下一步第一件事

写 P1-O BDD：Review & Export 页面应如何消费 `export_status=preview_ready` 的 candidate，显示最终导出包、docx 预检或显式写回审批。第一版仍不要自动覆盖 `Manuscripts/generated/paper_draft.md`。

### 未解决风险

- Playwright 在 P1-N 最终视觉复验时 transport closed；已用 API、HTML asset 和 JS identifier fallback 复核，但缺少最终截图级验收。
- `state/product/export_package_manifest.json` 和 preview 文件是本地 runtime artifacts，提交前需决定是否保留、迁移 fixture 或继续 gitignore。
- 还没有真正 docx export、最终导出包浏览或显式写回审批。

## 2026-05-13 P1-Q Chinese Copy + Archive Interface 交接增量

### 当前目标

把现有产品页面从普通控制台卡片堆叠，升级为中文化的个人研究档案界面：用户进入页面后能看到研究生命周期、当前研究对象、相邻笔记、证据等级和可验收产物，而不是被迫理解英文内部对象名或后端目录。

### 已完成事项

- 新增中文化 BDD：`docs/architecture-v2/codex-phase-p1-chinese-copy-bdd.md`。
- 新增档案界面 BDD：`docs/architecture-v2/codex-phase-p1-archive-interface-bdd.md`。
- 新增中文文案测试：`tests/test_frontend_chinese_copy.py`。
- 新增档案视觉契约测试：`tests/test_archive_interface_visual_contract.py`。
- 更新 `Product/web/index.html`：静态资源版本为 `20260513-archive1`，增加 `archive-shell`、`个人研究档案`、`本地证据`、右侧 `archive-inspector`、`研究档案`、`相邻笔记`、`证据图例`、`收藏架`。
- 更新 `Product/web/assets/app.js`：增加 `archivePageNotes`、`mountArchiveInspector()`、`updateArchiveInspector()`，让右侧相邻笔记可切换主工作区并随当前页面更新说明。
- 更新 `Product/web/assets/styles.css`：新增纸张网格、档案 note、证据 ledger、收藏架、hover、focus-visible、loading、empty、error 等状态样式。

### 已验证证据

- 失败测试：`python3 -m unittest tests.test_archive_interface_visual_contract -v` 首次 4 条失败，原因是缺少 `研究档案`、`archive-inspector`、`archive-ledger`、hover/focus/loading/empty/error 状态。
- 目标测试：`python3 -m unittest tests.test_archive_interface_visual_contract -v`，5 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，132 tests OK，skipped=1。
- JS 语法：`node --check Product/web/assets/app.js` 通过。
- Python 编译：`python3 -m py_compile Program/run_paper.py Program/workbench/observability.py Product/backend/observability_service.py Product/backend/project_service.py Product/app.py` 通过。
- 静态服务：`curl http://127.0.0.1:8765/?v=20260513-archive1` 返回新版 HTML 和 asset version。
- 可视化验收：Browser/IAB 与 Playwright 连接异常后，使用 Safari + Computer Use 打开 `http://127.0.0.1:8765/?v=20260513-archive1`；页面显示 `个人研究档案`、右侧 `档案索引`、`相邻笔记`、`证据图例` 和 `收藏架`。点击右侧 `数据与设计` 后，主工作区切换到变量角色编辑器，右侧当前笔记同步为 `数据与设计`。

### 关键文件路径

- `docs/architecture-v2/codex-phase-p1-chinese-copy-bdd.md`
- `docs/architecture-v2/codex-phase-p1-archive-interface-bdd.md`
- `tests/test_frontend_chinese_copy.py`
- `tests/test_archive_interface_visual_contract.py`
- `Product/web/index.html`
- `Product/web/assets/app.js`
- `Product/web/assets/styles.css`

### 不能重复探索的结论

- 本轮是视觉和信息架构层升级，不改变 P1 后端状态机，不引入 React/Vite/Next。
- 右侧 `相邻笔记` 第一版是静态导航 + 当前页面高亮，不是真正双向链接数据库。
- 档案气质参考 Maggie Appleton / Andy Matuschak / read.cv / 豆瓣收藏架，但不得复制原始插画、品牌、文字或完整页面结构。
- 视觉元素必须服务信息：证据图例、相邻页面、收藏架、当前研究对象说明都必须可解释，不做纯装饰渐变球或空 hero。

### 下一步第一件事

继续 P1-P：显式写回审批或 docx 导出预检。若先做界面细化，应只在当前 archive shell 内迭代真实页面，例如把 Export package、Artifacts、Agents 也改成“档案条目/证据架/审计时间线”，不要重新做 landing page。

### 未解决风险

- 真正 backlinks / graph、可折叠旁注和手绘解释层还没实现。
- Safari 验收可见浏览器侧边栏，但产品主体渲染正确；Browser/IAB 和 Playwright 本轮连接不稳定。
- 当前 `archive-inspector` 的收藏架条目仍是静态概览，后续应绑定真实 artifacts/export package 数据。

## 2026-05-13 P1-P Writeback Approval + DOCX Preflight 交接增量

### 当前目标

把 Review & Export 从“导出包展示”推进到“证据验收台”：用户必须先显式批准写回，系统才允许生成 docx 导出预检清单；这一步仍然不直接覆盖源草稿，也不直接生成 docx。

### 已完成事项

- 新增 BDD：`docs/architecture-v2/codex-phase-p1-writeback-docx-preflight-bdd.md`。
- 扩展测试：`tests/test_review_export_package.py` 新增写回审批、docx 预检、拒绝阻断和 clean evidence bench 的行为测试。
- 扩展后端：`Product/backend/manuscript_candidate_service.py` 新增 `save_project_writeback_approval()`、`save_project_docx_export_preflight()` 和导出包状态聚合。
- 扩展 API：`Product/app.py` 新增两个 POST endpoint：
  - `/api/v1/projects/{project_id}/export-package/{candidate_id}/writeback-approval`
  - `/api/v1/projects/{project_id}/export-package/{candidate_id}/docx-preflight`
- 扩展前端：`Product/web/assets/app.js` 和 `Product/web/assets/styles.css` 将 Review & Export 整理为 `review-export-evidence-bench`、`export-evidence-table`、`writeback-approval-panel`、`docx-preflight-panel`。

### 已验证证据

- 红灯测试：`python3 -m unittest tests.test_review_export_package -v` 首次失败，缺口符合预期：状态字段缺失、POST API 404、前端 clean bench 标识缺失。
- 目标测试：`python3 -m unittest tests.test_review_export_package -v`，9 tests OK。
- 相邻回归：`python3 -m unittest tests.test_review_export_package tests.test_manuscript_consumption tests.test_results_draft_evidence_binding -v`，36 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，142 tests OK，skipped=1。
- 静态检查：`python3 -m py_compile Product/backend/manuscript_candidate_service.py Product/app.py Product/backend/project_service.py Product/backend/results_draft_service.py` 通过；`node --check Product/web/assets/app.js` 通过。
- API 验收：重启 8765 后，写回审批 endpoint 返回 200，并写入 `state/product/writeback_approvals.json`。
- 可视化验收：Safari + Computer Use 打开 `http://127.0.0.1:8765/?v=20260513-p1p`，进入“审阅与导出”，审批后页面显示 `写回：已审批`；点击 `运行 docx 预检` 后页面显示 `预检通过` 和四项检查。

### 关键文件路径

- `docs/architecture-v2/codex-phase-p1-writeback-docx-preflight-bdd.md`
- `tests/test_review_export_package.py`
- `Product/backend/manuscript_candidate_service.py`
- `Product/app.py`
- `Product/web/assets/app.js`
- `Product/web/assets/styles.css`
- `state/product/writeback_approvals.json`（runtime state，不提交）
- `state/product/docx_export_preflight.json`（runtime state，不提交）

### 不能重复探索的结论

- 显式写回审批只是本地状态确认，不能自动覆盖 `Manuscripts/generated/paper_draft.md`。
- docx 预检只声明导出条件、目标路径和命令，不能在本阶段直接生成 docx。
- Review & Export 应继续保持证据验收台结构：表格列出证据路径，动作面板处理审批和预检，日志作为 Frontier-Eng 迭代说明。
- 8765 页面出现 404 时，优先检查是否是旧 uvicorn 进程未重启；本轮就是旧服务导致的，不是路由实现失败。

### 下一步第一件事

继续 P1-Q/P1-R 后续：实现真正的 docx 导出执行按钮或复现包封装前，需要先设计“执行导出”与“预检通过”之间的边界，避免把预检误当成最终导出。

### 未解决风险

- 本轮没有真正执行 `Program/export_docx.py` 生成 docx，只做导出预检。
- Browser plugin 和 Playwright MCP 仍不稳定；本轮可视化验收使用 Safari + Computer Use fallback。
- runtime state 已写入 `state/product/`，该目录应保持 ignored，不进入提交。

## 2026-05-13 P1-R Clean Workbench Visual Pass 交接增量

### 当前目标

回应用户指出的“前端页面依然很脏、不够干净”和截图中的变量角色入口重叠问题。保持现有 FastAPI + vanilla 前端，不换框架，先把信息架构和视觉密度清理到可继续开发的状态。

### 已完成事项

- 阅读并参考 JupyterLab 主工作区/侧边栏/属性检查器、Grafana dashboard panel、OpenMetadata 数据资产与质量证据的公开产品文档。
- 新增 `docs/architecture-v2/codex-phase-p1-clean-workbench-bdd.md`。
- 新增 `tests/test_clean_workbench_visual_contract.py`，覆盖清洁背景、变量入口无重叠、右侧属性检查器、record/list 替代嵌套大卡片、保留现有技术栈。
- 修改 `Product/web/index.html`：加入 `clean-workbench-shell`，静态资源版本改为 `20260513-clean1`，右侧文案改为“属性检查器”。
- 修改 `Product/web/assets/app.js`：重写 `renderVariableRoleWorkflow()` 输出 `research-record-card`、`record-meta-grid`、`research-step-list` 和 `compact-action-row`。
- 修改 `Product/web/assets/styles.css`：去掉 archive shell 的纸格背景和厚重阴影，新增 clean surface、inspector rail、record/list、长路径换行和单列变量入口布局。

### 已验证证据

- TDD 失败证据：`python3 -m unittest tests.test_clean_workbench_visual_contract -v` 首次 4 失败 1 通过，失败原因符合预期。
- 目标测试：`python3 -m unittest tests.test_clean_workbench_visual_contract tests.test_archive_interface_visual_contract tests.test_frontend_chinese_copy -v`，15 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，137 tests OK，skipped=1。
- 静态检查：`python3 -m py_compile Program/run_paper.py Program/workbench/observability.py Product/backend/observability_service.py Product/backend/project_service.py Product/app.py` 通过；`node --check Product/web/assets/app.js` 通过。
- 可视化验收：Safari + Computer Use 打开 `http://127.0.0.1:8765/?v=20260513-clean1`，点击右侧“数据与设计”后，变量角色入口显示为单列记录布局，未再出现截图中的文本重叠。

### 不能重复探索的结论

- 当前视觉问题不是要继续加“个人档案感”，而是要把研究工作台做干净、可扫读、可操作。
- `variable-role-workflow-layout` 不能再使用 `grid-template-columns: minmax(0, 1fr) auto`；长路径和中文说明必须允许换行。
- 右侧栏应作为属性检查器和相邻记录索引，不应承担大面积装饰。

### 下一步第一件事

继续 P1-P：为 Review & Export 增加显式写回审批或 docx 导出预检的 BDD/TDD。若继续视觉方向，优先清理 Results & Draft / Review & Export 的记录密度和右侧属性检查器联动，而不是添加新装饰。

### 未解决风险

- Browser plugin 和 Playwright MCP 本轮均出现连接/传输问题；已用 Safari + Computer Use 兜底，但还需要后续恢复 Browser 自动化截图链路。
- P1-R 只做了第一轮清洁视觉 pass；Artifacts / Agents 还没做成完整的证据架和审计时间线。
- 当前仍有大量 P1 变更处于工作区，提交时需要 scoped stage，避免把 runtime artifacts 或无关状态混入。

## 2026-05-13 P1-R Clean Workbench Visual Pass 交接增量

### 当前目标

回应用户指出的“前端页面依然很脏、不够干净”和截图中的变量角色入口重叠问题。保持现有 FastAPI + vanilla 前端，不换框架，先把信息架构和视觉密度清理到可继续开发的状态。

### 已完成事项

- 阅读并参考 JupyterLab 主工作区/侧边栏/属性检查器、Grafana dashboard panel、OpenMetadata 数据资产与质量证据的公开产品文档。
- 新增 `docs/architecture-v2/codex-phase-p1-clean-workbench-bdd.md`。
- 新增 `tests/test_clean_workbench_visual_contract.py`，覆盖清洁背景、变量入口无重叠、右侧属性检查器、record/list 替代嵌套大卡片、保留现有技术栈。
- 修改 `Product/web/index.html`：加入 `clean-workbench-shell`，静态资源版本改为 `20260513-clean1`，右侧文案改为“属性检查器”。
- 修改 `Product/web/assets/app.js`：重写 `renderVariableRoleWorkflow()` 输出 `research-record-card`、`record-meta-grid`、`research-step-list` 和 `compact-action-row`。
- 修改 `Product/web/assets/styles.css`：去掉 archive shell 的纸格背景和厚重阴影，新增 clean surface、inspector rail、record/list、长路径换行和单列变量入口布局。

### 已验证证据

- TDD 失败证据：`python3 -m unittest tests.test_clean_workbench_visual_contract -v` 首次 4 失败 1 通过，失败原因符合预期。
- 目标测试：`python3 -m unittest tests.test_clean_workbench_visual_contract tests.test_archive_interface_visual_contract tests.test_frontend_chinese_copy -v`，15 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，137 tests OK，skipped=1。
- 静态检查：`python3 -m py_compile Program/run_paper.py Program/workbench/observability.py Product/backend/observability_service.py Product/backend/project_service.py Product/app.py` 通过；`node --check Product/web/assets/app.js` 通过。
- 可视化验收：Safari + Computer Use 打开 `http://127.0.0.1:8765/?v=20260513-clean1`，点击右侧“数据与设计”后，变量角色入口显示为单列记录布局，未再出现截图中的文本重叠。

### 不能重复探索的结论

- 当前视觉问题不是要继续加“个人档案感”，而是要把研究工作台做干净、可扫读、可操作。
- `variable-role-workflow-layout` 不能再使用 `grid-template-columns: minmax(0, 1fr) auto`；长路径和中文说明必须允许换行。
- 右侧栏应作为属性检查器和相邻记录索引，不应承担大面积装饰。

### 下一步第一件事

继续 P1-P：为 Review & Export 增加显式写回审批或 docx 导出预检的 BDD/TDD。若继续视觉方向，优先清理 Results & Draft / Review & Export 的记录密度和右侧属性检查器联动，而不是添加新装饰。

### 未解决风险

- Browser plugin 和 Playwright MCP 本轮均出现连接/传输问题；已用 Safari + Computer Use 兜底，但还需要后续恢复 Browser 自动化截图链路。
- P1-R 只做了第一轮清洁视觉 pass；Artifacts / Agents 还没做成完整的证据架和审计时间线。
- 当前仍有大量 P1 变更处于工作区，提交时需要 scoped stage，避免把 runtime artifacts 或无关状态混入。

## 2026-05-13 P1-Q Chinese Copy + Archive Interface 交接增量

### 当前目标

把现有产品页面从普通控制台卡片堆叠，升级为中文化的个人研究档案界面：用户进入页面后能看到研究生命周期、当前研究对象、相邻笔记、证据等级和可验收产物，而不是被迫理解英文内部对象名或后端目录。

### 已完成事项

- 新增中文化 BDD：`docs/architecture-v2/codex-phase-p1-chinese-copy-bdd.md`。
- 新增档案界面 BDD：`docs/architecture-v2/codex-phase-p1-archive-interface-bdd.md`。
- 新增中文文案测试：`tests/test_frontend_chinese_copy.py`。
- 新增档案视觉契约测试：`tests/test_archive_interface_visual_contract.py`。
- 更新 `Product/web/index.html`：静态资源版本为 `20260513-archive1`，增加 `archive-shell`、`个人研究档案`、`本地证据`、右侧 `archive-inspector`、`研究档案`、`相邻笔记`、`证据图例`、`收藏架`。
- 更新 `Product/web/assets/app.js`：增加 `archivePageNotes`、`mountArchiveInspector()`、`updateArchiveInspector()`，让右侧相邻笔记可切换主工作区并随当前页面更新说明。
- 更新 `Product/web/assets/styles.css`：新增纸张网格、档案 note、证据 ledger、收藏架、hover、focus-visible、loading、empty、error 等状态样式。

### 已验证证据

- 失败测试：`python3 -m unittest tests.test_archive_interface_visual_contract -v` 首次 4 条失败，原因是缺少 `研究档案`、`archive-inspector`、`archive-ledger`、hover/focus/loading/empty/error 状态。
- 目标测试：`python3 -m unittest tests.test_archive_interface_visual_contract -v`，5 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，132 tests OK，skipped=1。
- JS 语法：`node --check Product/web/assets/app.js` 通过。
- Python 编译：`python3 -m py_compile Program/run_paper.py Program/workbench/observability.py Product/backend/observability_service.py Product/backend/project_service.py Product/app.py` 通过。
- 静态服务：`curl http://127.0.0.1:8765/?v=20260513-archive1` 返回新版 HTML 和 asset version。
- 可视化验收：Browser/IAB 与 Playwright 连接异常后，使用 Safari + Computer Use 打开 `http://127.0.0.1:8765/?v=20260513-archive1`；页面显示 `个人研究档案`、右侧 `档案索引`、`相邻笔记`、`证据图例` 和 `收藏架`。点击右侧 `数据与设计` 后，主工作区切换到变量角色编辑器，右侧当前笔记同步为 `数据与设计`。

### 关键文件路径

- `docs/architecture-v2/codex-phase-p1-chinese-copy-bdd.md`
- `docs/architecture-v2/codex-phase-p1-archive-interface-bdd.md`
- `tests/test_frontend_chinese_copy.py`
- `tests/test_archive_interface_visual_contract.py`
- `Product/web/index.html`
- `Product/web/assets/app.js`
- `Product/web/assets/styles.css`

### 不能重复探索的结论

- 本轮是视觉和信息架构层升级，不改变 P1 后端状态机，不引入 React/Vite/Next。
- 右侧 `相邻笔记` 第一版是静态导航 + 当前页面高亮，不是真正双向链接数据库。
- 档案气质参考 Maggie Appleton / Andy Matuschak / read.cv / 豆瓣收藏架，但不得复制原始插画、品牌、文字或完整页面结构。
- 视觉元素必须服务信息：证据图例、相邻页面、收藏架、当前研究对象说明都必须可解释，不做纯装饰渐变球或空 hero。

### 下一步第一件事

继续 P1-P：显式写回审批或 docx 导出预检。若先做界面细化，应只在当前 archive shell 内迭代真实页面，例如把 Export package、Artifacts、Agents 也改成“档案条目/证据架/审计时间线”，不要重新做 landing page。

### 未解决风险

- 真正 backlinks / graph、可折叠旁注和手绘解释层还没实现。
- Safari 验收可见浏览器侧边栏，但产品主体渲染正确；Browser/IAB 和 Playwright 本轮连接不稳定。
- 当前 `archive-inspector` 的收藏架条目仍是静态概览，后续应绑定真实 artifacts/export package 数据。
## 2026-05-13 P2-B Method Skill Catalog 交接增量

### 当前目标

把 CoPaper/StatsPAI 的“方法技能集”思想接入本项目的 RunPlan 前置层：用户在执行前能看到 OLS、DID、IV、RDD、PSM、DML 哪些方法具备条件，哪些缺少变量，哪些只能作为候选而不能执行。

### 已完成事项

- 新增 BDD：`docs/architecture-v2/codex-phase-p2-method-skill-catalog-bdd.md`。
- 新增测试：`tests/test_method_skill_catalog.py`，覆盖 API 方法目录、阻塞原因、默认 RunPlan task 和前端面板。
- 修改 `Product/backend/design_spec_service.py`：新增 `method_catalog` 构建逻辑；默认 `baseline_regression` task 带 `method_id=ols`；DID/IV/RDD 等缺前置条件时只进入目录，不进入执行任务。
- 修改 `Product/web/index.html`：研究设计页新增 `method-skill-catalog-panel`，静态资源版本为 `20260513-p2b-clean`。
- 修改 `Product/web/assets/app.js`：研究设计页读取 RunPlan，渲染方法技能集、要求状态和阻塞原因。
- 修改 `Product/web/assets/styles.css`：新增方法目录样式，并把方法卡片改成纵向单列，避免拥挤和 `auto` 列重叠。

### 已验证证据

- 失败测试：`python3 -m unittest tests.test_method_skill_catalog -v` 首次失败，原因符合预期：缺少 `method_catalog`、`method_id` 和前端面板。
- 目标测试：`python3 -m unittest tests.test_method_skill_catalog tests.test_clean_workbench_visual_contract -v`，9 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，152 tests OK，skipped=1。
- 静态检查：`python3 -m py_compile Product/backend/design_spec_service.py Product/app.py Product/backend/project_service.py Product/backend/overview_service.py` 通过；`node --check Product/web/assets/app.js` 通过。
- API 验收：`GET /api/v1/projects/proj_undergraduate_thesis/run-plan` 返回 `method_catalog`；OLS/PSM/DML 为 `ready`，DID 阻塞 `missing_panel_time`，IV 阻塞 `missing_instrument`，RDD 阻塞 `missing_running_variable`。
- 可视化验收：Safari + Computer Use 打开 `http://127.0.0.1:8765/?v=20260513-p2b-clean`，点击“工具：研究设计细节”，可见“方法技能集”、StatsPAI/CoPaper methodology index、OLS ready、DID/IV/RDD 阻塞原因；布局为纵向证据清单，无双列挤压。

### 不能重复探索的结论

- `method_catalog` 现在是 `local_file` 前置条件判断，不是 StatsPAI 真实执行结果；不能把它标记为 `local_execution`。
- DID/IV/RDD 缺少关键变量时不能进入默认 RunPlan task，只能展示阻塞原因。
- 方法技能集属于“研究设计细节”页面；Execution 页面先保持执行计划、运行轨迹和人工确认，不再堆方法百科。
- 视觉上不要再用双列方法卡片承载长中文说明；纵向证据清单更适合当前 clean workbench。

### 下一步第一件事

P2-C：选择一个最小真实执行适配器路径，建议先做 OLS baseline 的 `local_execution`：从 approved RunPlan 读取 `method_id=ols` 和公式，调用现有 Python/Stata/StatsPAI 可用路径生成结果 JSON、日志和 provenance，再接入 Execution/Findings。

### 未解决风险

- 还没有真正调用 StatsPAI、Stata 或 pyfixest；当前只是方法准入目录。
- PSM/DML 现在只按有无 controls/covariates 判断 ready，还没有样本量、平衡性、交叉拟合等更严格 evaluator。
- Playwright MCP 仍返回 `Transport closed`；本轮视觉验收继续使用 Safari + Computer Use。

## 2026-05-13 P2-C OLS Execution Adapter 交接增量

### 当前目标

把 P2-B 的方法准入目录推进到第一个真实方法执行产物。OLS baseline 现在不是 `local_file` 级“可执行判断”，而是会在 full run 后写出 `local_execution` 级结果文件。

### 已完成事项

- 新增 BDD：`docs/architecture-v2/codex-phase-p2-ols-execution-adapter-bdd.md`。
- 新增测试：`tests/test_ols_execution_adapter.py`，覆盖 approved OLS、manifest、unsupported method、insufficient data。
- 修改 `Product/backend/project_service.py`：full run 成功后执行本地 `python_ols_adapter`，读取 RunPlan 公式和 CSV，计算 OLS 系数并写入 `Results/json/method_execution_result.json`。
- 修改 `Product/backend/project_service.py`：新增 `MethodExecutionError`，把数据不足、公式不可估、共线设计变成结构化产品错误。
- 修改 `Product/app.py`：unsupported method 返回 409 `unsupported_run_plan_method`；方法执行失败返回 409 `method_execution_failed`。
- 修复 `plan_binding.tasks[].method_id` 在真实项目中可能为 `null` 的问题，回退使用 estimator。

### 已验证证据

- 目标测试：`python3 -m unittest tests.test_ols_execution_adapter -v`，5 tests OK。
- 相邻回归：`python3 -m unittest tests.test_ols_execution_adapter tests.test_full_run_from_run_plan tests.test_method_skill_catalog tests.test_results_draft_evidence_binding -v`，20 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，157 tests OK，skipped=1。
- 静态检查：`python3 -m py_compile Program/run_paper.py Program/workbench/observability.py Product/backend/observability_service.py Product/backend/project_service.py Product/backend/overview_service.py Product/backend/design_spec_service.py Product/app.py` 通过；`node --check Product/web/assets/app.js` 通过。
- API 验收：`POST /api/v1/projects/proj_undergraduate_thesis/runs/full` 生成 `run_4c62f1721afb`，status=`succeeded`，`plan_binding.tasks[0].method_id=ols`，`method_execution.evidence_level=local_execution`，`treatment_coefficient=1.8505076803`。
- 可视化验收：Safari + Computer Use 打开本地页面，研究设计细节页正常加载；P2-C 的方法执行结果目前主要通过 API 和本地文件验收，尚未完全接入页面展示。

### 不能重复探索的结论

- `method_catalog` 是方法准入目录，`method_execution_result.json` 才是方法执行证据。
- 当前 OLS adapter 是最小本地 Python 执行器，不是完整 StatsPAI/Stata 引擎。
- DID/IV/RDD/PSM/DML 仍不能执行，除非后续各自写 BDD/TDD 和真实产物。

### 下一步第一件事

P2-D：写 BDD 和失败测试，把 `Results/json/method_execution_result.json` 接入 Execution / Findings 页面。目标是让用户点击一次 full run 后，在页面上直接看到“OLS 已本地执行、用了哪个公式、多少样本、处理变量系数是多少、证据等级是什么”。

### 未解决风险

- OLS adapter 没有标准误、p 值、稳健标准误、固定效应或聚类。
- `Results & Draft` 目前仍主要读取 `Results/json/analysis_result.json`；P2-D 应决定是否以 `method_execution_result.json` 作为 Findings 的方法证据源。
- Playwright MCP 仍返回 `Transport closed`；视觉验收继续使用 Safari + Computer Use fallback。

## 2026-05-13 P2-D Method Execution Evidence UI 交接增量

### 当前目标

让 P2-C 生成的 `Results/json/method_execution_result.json` 不再只是后端产物，而是在“实证执行”和“结果与草稿”中作为可审阅的 `local_execution` 方法证据出现。

### 已完成事项

- 新增 BDD：`docs/architecture-v2/codex-phase-p2-method-execution-ui-bdd.md`。
- 扩展后端 `Product/backend/observability_service.py`：`load_run_observability()` 返回顶层 `method_execution`，并从 manifest 指向的 artifact JSON 读取真实执行内容。
- 扩展后端 `Product/backend/results_draft_service.py`：`get_project_results_draft()` 返回顶层 `method_execution`，每个 FindingCard 增加 `method_evidence`。
- 扩展前端 `Product/web/index.html`：新增“方法执行证据”面板，静态资源版本更新为 `20260513-p2d-method`。
- 扩展前端 `Product/web/assets/app.js`：新增 `renderObservableMethodExecution()` 和 `renderFindingMethodEvidence()`。
- 扩展前端 `Product/web/assets/styles.css`：新增方法执行证据面板与 FindingCard 证据块样式。
- 扩展测试：`tests/test_observable_execution.py`、`tests/test_observable_execution_frontend.py`、`tests/test_results_draft_evidence_binding.py`。

### 已验证证据

- 失败测试先通过 TDD 观察到预期缺口：`method_execution`、`observable-method-execution`、`method_evidence` 均不存在。
- 目标测试：4 tests OK。
- Results Draft 回归：10 tests OK。
- 相邻回归：38 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，161 tests OK，skipped=1。
- 静态检查：Python 编译、`node --check Product/web/assets/app.js`、`git diff --check` 均通过。
- API 验收：`observability` 和 `results-draft` 都返回 `engine=python_ols_adapter`、`formula=wage ~ trained + edu + experience`、`nobs=12`、`treatment_coefficient=1.8505076803`、`artifact_path=Results/json/method_execution_result.json`。
- 可视化验收：Safari + Computer Use 确认“实证执行”页和“结果与草稿”页均能看到方法执行证据。

### 不能重复探索的结论

- `method_execution_result.json` 是方法执行证据；`analysis_result.json` 仍是论文结果摘要证据。两者当前互补，不应互相替代。
- 当前 OLS 执行器是本地 Python 最小 adapter，不是完整 StatsPAI/Stata 引擎。
- FindingCard 现在可以显示方法证据，但人工 approve 仍然应该依赖后续 evaluator，而不是只看系数。

### 下一步第一件事

P2-E：为 OLS 方法执行补 evaluator。最小范围是标准误、p 值、样本量、可逆矩阵/共线性、稳健或聚类标准误预检，并把不满足门槛的 finding 标为 `needs_review`。

### 未解决风险

- 方法执行结果尚未包含标准误、p 值、置信区间、固定效应、聚类或稳健标准误。
- Results/FindingCard 还没有把 evaluator verdict 作为 approve 前置条件。
- Playwright MCP 仍返回 `Transport closed`，本轮视觉闭环使用 Safari + Computer Use。

## 2026-05-13 P2-E OLS Evaluator Evidence 交接增量

### 当前目标

把 P2-D 的“方法执行证据可见”推进到“结果论断具备最小统计推断证据”：OLS 方法执行必须给出标准误、p 值、置信区间、诊断和 evaluator verdict，并在 Results & Draft 页面直接可见。

### 已完成事项

- 新增 BDD：`docs/architecture-v2/codex-phase-p2-ols-evaluator-bdd.md`。
- 扩展 `Product/backend/project_service.py`：`fit_ols_model()` 现在计算系数、标准误、t 统计量、normal approximation p 值、95% 置信区间、残差自由度、残差标准误和残差平方和；新增 `build_ols_evaluator()` 输出命名检查。
- 扩展 `Product/backend/results_draft_service.py`：`build_method_evidence()` 绑定 `standard_error`、`p_value`、`p_value_method`、`confidence_interval`、`evaluator_status` 和完整 evaluator。
- 扩展 `Product/web/assets/app.js`：FindingCard 的方法执行证据改为中文审阅摘要，显示 `ols · n=12 · β=... · 标准误=... · p=... · 95% 置信区间 ... · 评估器通过`。
- 扩展 `Product/web/assets/styles.css`：新增 `method-evidence-summary`，避免窄卡片网格继续制造拥挤。
- 更新 `Product/web/index.html` 静态资源版本为 `20260513-p2e-eval2`，避免 Safari 继续使用旧 JS/CSS 缓存。
- 初步查看用户提供的数据目录 `/Users/mahaoxuan/Desktop/实证数据库`，确认至少存在 `外部源数据/CHARLS.csv`、CFPS、CLDS、CGSS 等真实数据材料。

### 已验证证据

- TDD 首次失败符合预期：`standard_errors`、`evaluator`、`evaluator_status` 等字段缺失。
- 目标测试：`python3 -m unittest tests.test_ols_execution_adapter tests.test_results_draft_evidence_binding -v`，19 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，165 tests OK，skipped=1。
- 静态检查：Python 编译、`node --check Product/web/assets/app.js`、`git diff --check` 均通过。
- API 验收：`POST /api/v1/projects/proj_undergraduate_thesis/runs/full` 生成 `run_a3674e9e78c6`，status=`succeeded`。
- API 验收：`observability.method_execution.methods[0]` 返回 `standard_errors.trained=0.0754664205`、`p_values.trained=8.83354660202e-133`、`confidence_intervals.trained.low=1.7025934962`、`confidence_intervals.trained.high=1.9984218644`、`evaluator.status=passed`。
- 可视化验收：Safari + Computer Use 打开 `http://127.0.0.1:8765/?v=20260513-p2e-eval`，点击“结果与草稿”，结果论断卡显示最新 run `run_a3674e9e78c6` 和紧凑方法证据摘要。

### 关键文件路径

- `Product/backend/project_service.py`
- `Product/backend/results_draft_service.py`
- `Product/web/index.html`
- `Product/web/assets/app.js`
- `Product/web/assets/styles.css`
- `tests/test_ols_execution_adapter.py`
- `tests/test_results_draft_evidence_binding.py`
- `docs/architecture-v2/codex-phase-p2-ols-evaluator-bdd.md`
- `Results/json/method_execution_result.json`
- `state/runs/run_a3674e9e78c6/run_manifest.json`

### 不能重复探索的结论

- 极小 p 值不能四舍五入为 `0`；当前使用显著数字保留，前端用科学计数法显示。
- 当前 p 值方法是 `normal_approximation`，必须继续显式暴露，不要伪装成精确 t 分布或稳健推断。
- FindingCard 方法证据不应回到窄网格布局；当前中文摘要更适合 clean workbench。
- `method_execution_result.json` 负责方法执行和推断证据，`analysis_result.json` 仍负责结果摘要和草稿绑定，两者保持分层。

### 下一步第一件事

P2-F：从 `/Users/mahaoxuan/Desktop/实证数据库` 选择一个真实且可快速解析的数据源，先做只读 inventory/profile BDD。目标不是立刻跑完整论文，而是让 Data & Design 能选择真实外部数据、生成 `local_file` 质量画像，并把字段/样本口径暴露给 VariableRoleSet。

### 未解决风险

- OLS evaluator 仍缺 robust/clustered standard errors、固定效应和有限样本 t 分布 p 值。
- Finding approve 还没有强制检查 evaluator status；当前只是显示 evaluator 证据。
- 真实数据目录可能包含大文件、Stata `.dta`、编码问题或隐私数据；P2-F 必须先做只读 inventory，不要移动或修改原始数据。
- Playwright MCP 仍不稳定；继续使用 Safari + Computer Use 做视觉闭环。

## 2026-05-13 P2-F Real Data Candidate Pool 交接增量

### 当前目标

把用户提供的 `/Users/mahaoxuan/Desktop/实证数据库` 接入产品，但只作为只读真实数据候选池，不把它伪装成当前项目已经使用的数据。

### 已完成事项

- 新增 BDD：`docs/architecture-v2/codex-phase-p2-real-data-catalog-bdd.md`。
- 新增测试：`tests/test_external_data_catalog.py`，覆盖 API 候选池、CSV 轻量画像、DTA 可见性、前端面板和空状态。
- 扩展 `Product/backend/overview_service.py`：`list_project_datasets()` 返回 `external_catalog`；默认扫描 `/Users/mahaoxuan/Desktop/实证数据库`，可通过 `EMPIRICAL_DATA_LIBRARY_ROOT` 覆盖。
- 扩展 `Product/web/index.html`、`Product/web/assets/app.js`、`Product/web/assets/styles.css`：数据与设计页新增“真实数据候选池”，首屏只展示 6 张候选卡，并显示真实文件总数。
- 修复视觉验收中发现的提示不一致：页面显示 6 张卡时，底部提示现在是 `已显示前 6 个候选文件，共发现 223 个。`

### 已验证证据

- 目标测试：`python3 -m unittest tests.test_external_data_catalog -v`，5 tests OK。
- 相邻回归：`python3 -m unittest tests.test_external_data_catalog tests.test_dataset_quality_profile -v`，11 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，170 tests OK，skipped=1。
- 静态检查：`python3 -m py_compile Product/backend/overview_service.py Product/app.py`、`node --check Product/web/assets/app.js`、`git diff --check` 均通过。
- API 验收：`GET /api/v1/projects/proj_undergraduate_thesis/datasets` 返回 `external_catalog.exists=true`、`root=/Users/mahaoxuan/Desktop/实证数据库`、`total_count=223`。
- 可视化验收：Safari + Computer Use 打开 `http://127.0.0.1:8765/?v=20260513-p2f-realdata2`，点击“数据与设计”，确认真实数据候选池、6 张 CFPS 候选卡、`本地文件`、`尚未画像`、`只读` 和项目内 `analysis_sample.csv` 分开展示。

### 关键文件路径

- `Product/backend/overview_service.py`
- `Product/web/index.html`
- `Product/web/assets/app.js`
- `Product/web/assets/styles.css`
- `tests/test_external_data_catalog.py`
- `docs/architecture-v2/codex-phase-p2-real-data-catalog-bdd.md`

### 不能重复探索的结论

- `/Users/mahaoxuan/Desktop/实证数据库` 是外部真实数据候选池，不是当前项目已确认使用的数据目录。
- 外部候选文件必须保持 `read_only=true`，在没有导入/绑定 manifest 前不能进入 VariableRoleSet、DesignSpec 或 RunPlan。
- 当前只对 CSV 做轻量预览画像；DTA/XLSX/Parquet 等大文件先登记来源和大小，不在页面加载时深度解析。

### 下一步第一件事

P2-G：做“真实候选数据导入/绑定预检”。最小产品动作是选择一个候选文件，生成 import/bind preview，记录来源路径、目标路径、复制或链接策略、文件大小、证据等级和人工动作；预检通过后才允许进入变量角色确认。

### 未解决风险

- DTA/XLSX/Parquet 深度变量字典还未做，后续应引入 pandas/pyreadstat 或 StatsPAI 的安全预览路径。
- 外部候选池还没有搜索、过滤、选择、导入或绑定动作。
- 当前执行链仍使用 `Data/Final/analysis_sample.csv`；不要把 P2-F 的候选池误读为已经完成真实论文数据运行。

## 2026-05-14 P2-G Real Dataset Bind Preflight 交接增量

### 当前目标

真实数据候选池已经可以生成“导入/绑定预检”。本阶段只证明用户选择了哪个外部真实文件、计划进入哪个项目路径、检查是否通过；不会移动、复制、覆盖或绑定原始数据。

### 已完成事项

- 新增 BDD：`docs/architecture-v2/codex-phase-p2-dataset-bind-preflight-bdd.md`。
- 新增测试：`tests/test_external_dataset_bind_preflight.py`，覆盖成功预检、外部目录逃逸、缺失文件、datasets API 最新预检回读和前端预检面板。
- 扩展 `Product/backend/overview_service.py`：新增外部候选路径校验、预检构造、manifest 读写和最新预检回读；预检写入 `state/product/dataset_import_preflights.json`。
- 扩展 `Product/app.py`：新增 `POST /api/v1/projects/{project_id}/datasets/external-bind-preflight`。
- 扩展 `Product/web/index.html`、`Product/web/assets/app.js`、`Product/web/assets/styles.css`：候选卡新增“生成导入/绑定预检”，数据与设计页新增“导入/绑定预检”证据面板。

### 已验证证据

- 目标测试：`python3 -m unittest tests.test_external_dataset_bind_preflight -v`，5 tests OK。
- 相邻回归：`python3 -m unittest tests.test_external_dataset_bind_preflight tests.test_external_data_catalog tests.test_dataset_quality_profile -v`，16 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，175 tests OK，skipped=1。
- 静态检查：`python3 -m py_compile Product/backend/overview_service.py Product/app.py`、`node --check Product/web/assets/app.js`、`git diff --check` 均通过。
- API 验收：`POST /api/v1/projects/proj_undergraduate_thesis/datasets/external-bind-preflight` 对 `/Users/mahaoxuan/Desktop/实证数据库/A001CFPS中国家庭追踪调查/2010cfps/cfps2010adult_202008.dta` 返回 `status=ready_for_review`、`target.path=Data/Raw/cfps2010adult_202008.dta`、`will_mutate_source=false`、`will_create_project_file=false`。
- 可视化验收：Safari + Computer Use 打开 `http://127.0.0.1:8765/?v=20260513-p2g-bind1`，点击“数据与设计”，对 CFPS 候选文件点击“生成导入/绑定预检”，页面显示 `待人工确认`、真实源路径、目标路径、策略、4 项 passed checks 和 `尚未导入/绑定 · 源文件只读`。

### 关键文件路径

- `Product/backend/overview_service.py`
- `Product/app.py`
- `Product/web/index.html`
- `Product/web/assets/app.js`
- `Product/web/assets/styles.css`
- `tests/test_external_dataset_bind_preflight.py`
- `docs/architecture-v2/codex-phase-p2-dataset-bind-preflight-bdd.md`
- `state/product/dataset_import_preflights.json`（runtime 产物，不作为源码提交）

### 不能重复探索的结论

- 预检不是导入。`will_create_project_file=false` 和 `will_mutate_source=false` 必须保持，直到后续 P2-H 有明确 apply/import 动作。
- 外部真实数据只能来自 `external_data_library_roots()` 允许的候选池；不能接受任意本地路径，否则 provenance 边界会失效。
- 预检不能更新 VariableRoleSet、DesignSpec 或 RunPlan；这些状态只能在真实导入/绑定完成并有用户确认后消费新数据。

### 下一步第一件事

P2-H：实现显式 apply/import workflow 的 BDD。最小行为应是读取一条 `ready_for_review` 预检，用户确认后生成项目内目标 artifact 或绑定记录，记录人工动作、文件大小、哈希、目标路径、失败原因和回滚语义；仍然不能直接进入 RunPlan。

### 未解决风险

- 当前预检只做路径、大小和目标建议，不做 DTA/XLSX/Parquet 深度字段画像。
- 当前没有搜索/过滤真实候选池，223 个文件只能看首屏候选。
- 当前没有 apply/import API，因此用户还不能真正把真实数据加入项目。
- Playwright MCP 仍不稳定；视觉闭环继续使用 Safari + Computer Use。

## 2026-05-14 P2-H Real Dataset Import Apply 交接增量

### 当前目标

真实数据候选池现在已经走到“用户明确确认”的第一步：一条 `ready_for_review` 预检可以被复制到当前项目、只绑定为外部引用，或被取消。线上版和本地版的数据边界已明确分开。

### 已完成事项

- 新增 BDD：`docs/architecture-v2/codex-phase-p2-dataset-import-apply-bdd.md`。
- 新增测试：`tests/test_external_dataset_import_apply.py`，覆盖复制到项目、只绑定外部引用、取消预检、云端拒绝本地路径和前端按钮契约。
- 扩展 `Product/backend/overview_service.py`：新增 `apply_external_dataset_bind_preflight()`、`file_sha256()`、`CloudUploadRequiredError`、`DatasetPreflightStateError`。
- 扩展 `Product/app.py`：新增 `POST /api/v1/projects/{project_id}/datasets/external-bind-preflight/{preflight_id}/apply`。
- 扩展 `Product/web/index.html`、`Product/web/assets/app.js`、`Product/web/assets/styles.css`：预检面板新增三类人工动作和导入/绑定结果回显。

### 已验证证据

- 目标测试：`python3 -m unittest tests.test_external_dataset_import_apply -v`，5 tests OK。
- 相邻回归：`python3 -m unittest tests.test_external_dataset_import_apply tests.test_external_dataset_bind_preflight tests.test_external_data_catalog tests.test_dataset_quality_profile -v`，21 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，180 tests OK，skipped=1。
- 静态检查：`python3 -m py_compile Product/backend/overview_service.py Product/app.py`、`node --check Product/web/assets/app.js`、`git diff --check` 均通过。
- 可视化验收：Safari + Computer Use 打开 `http://127.0.0.1:8765/?v=20260514-p2h-import1`，在“数据与设计”页点击“只绑定引用”，页面显示 `已接入`、`已绑定外部引用`、`动作：只绑定引用 · 模式：local` 和 SHA256。

### 关键文件路径

- `Product/backend/overview_service.py`
- `Product/app.py`
- `Product/web/index.html`
- `Product/web/assets/app.js`
- `Product/web/assets/styles.css`
- `tests/test_external_dataset_import_apply.py`
- `docs/architecture-v2/codex-phase-p2-dataset-import-apply-bdd.md`
- `state/product/dataset_import_preflights.json`（runtime 产物，不作为源码提交）

### 不能重复探索的结论

- 本地版可以复制项目内副本，也可以只绑定本机外部引用；线上版不能读取用户桌面路径，必须要求上传或云对象存储。
- “只绑定引用”不会复制大文件，只记录本机路径、大小、SHA256 和 provenance；这适合本地研究工作台。
- apply/import 完成仍不能直接改写 VariableRoleSet、DesignSpec 或 RunPlan；下一阶段必须先做字段画像和变量字典预览。
- 不允许预检或 apply 默默复制大文件；复制必须是用户点击“确认导入到项目”的显式动作。

### 下一步第一件事

P2-I：读取 `dataset_import` 的结果，给已复制或已绑定的真实数据生成安全字段画像/变量字典预览。优先支持小 CSV 和可控 DTA 读取；大文件必须有大小、行数、字段读取上限和错误状态。

### 未解决风险

- DTA/XLSX/Parquet 深度字段字典仍未完成。
- 绑定引用依赖本地路径稳定性；如果原始文件移动，后续画像应显示 `source_missing` 而不是继续运行。
- 线上版本还没有上传、云对象存储、脱敏或远端执行队列。
- Browser 插件连接本轮超时；视觉验收使用 Safari + Computer Use fallback。

## 2026-05-14 P2-I Dataset Import Field Profile 交接增量

### 当前目标

真实数据已经可以被复制或绑定到项目，但在它进入变量角色、研究设计或执行计划之前，必须先经过可审计字段画像。P2-I 的目标是给已 apply 的 `dataset_import` 增加安全字段画像入口，并明确“不画像、不进入研究状态”。

### 已完成事项

- 新增 BDD：`docs/architecture-v2/codex-phase-p2-dataset-import-profile-bdd.md`。
- 新增测试：`tests/test_external_dataset_import_profile.py`，覆盖 CSV 画像、绑定引用画像、DTA 阻塞画像、源文件哈希变化拒绝、取消导入拒绝画像和前端非改写提示。
- 扩展 `Product/backend/overview_service.py`：新增 `profile_external_dataset_import()`、`build_dataset_import_profile()`、`resolve_dataset_import_profile_path()`、`latest_external_import_profile()` 和相关错误类型。
- 扩展 `Product/app.py`：新增 `POST /api/v1/projects/{project_id}/datasets/imports/{dataset_import_id}/profile`。
- 扩展 `Product/web/index.html`、`Product/web/assets/app.js`、`Product/web/assets/styles.css`：预检/导入结果区新增“生成字段画像”，Data & Design 新增“字段画像 / 变量字典预览”面板。

### 已验证证据

- RED：`python3 -m unittest tests.test_external_dataset_import_profile -v` 首次 6 条失败，失败原因是 profile API 404、前端缺少画像入口和画像面板。
- GREEN：`python3 -m unittest tests.test_external_dataset_import_profile -v`，6 tests OK。
- 相邻回归：`python3 -m unittest tests.test_external_dataset_import_profile tests.test_external_dataset_import_apply tests.test_external_dataset_bind_preflight tests.test_external_data_catalog tests.test_dataset_quality_profile -v`，27 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，186 tests OK，skipped=1。
- 静态检查：`python3 -m py_compile Product/app.py Product/backend/overview_service.py`、`node --check Product/web/assets/app.js`、`git diff --check` 均通过。
- API 验收：`POST /api/v1/projects/proj_undergraduate_thesis/datasets/imports/dataset_import_e9d864229be8/profile` 返回 `status=blocked`、`readiness_status=not_profiled`、`fields=[]`、`blocking_reason=dta 暂未接入安全字段读取器。`、`can_feed_variable_roles=false`。
- 页面验收：`curl http://127.0.0.1:8765/?v=20260514-p2i-profile1` 确认页面加载新版静态资源和 `dataset-import-profile-panel`；`npx playwright screenshot --wait-for-timeout=3000` 生成 `/tmp/empirical-workbench-p2i-home-loaded.png`；临时 Playwright 脚本点击“数据与设计”和“生成字段画像”后生成 `/tmp/empirical-workbench-p2i-data-profile.png`，页面显示 `.dta` 阻塞画像和不改写研究状态说明。

### 关键文件路径

- `Product/backend/overview_service.py`
- `Product/app.py`
- `Product/web/index.html`
- `Product/web/assets/app.js`
- `Product/web/assets/styles.css`
- `tests/test_external_dataset_import_profile.py`
- `docs/architecture-v2/codex-phase-p2-dataset-import-profile-bdd.md`
- `state/product/dataset_import_preflights.json`（runtime 产物，不作为源码提交）

### 不能重复探索的结论

- 字段画像不等于变量角色确认。`dataset_import_profile.can_feed_variable_roles=false` 必须保持，直到用户显式确认 VariableRoleSet。
- 对 DTA/XLSX/Parquet 不能伪造字段列表；没有安全读取器时必须显示 `blocked/not_profiled`。
- 已绑定外部引用在画像前必须重新计算 SHA256；哈希不一致返回 `dataset_import_source_changed`，不能继续使用旧预检状态。
- 已取消或未 apply 的 import 不能画像。

### 下一步第一件事

P2-J：优先实现 DTA 字段读取器的安全元数据模式，目标是读取变量名、变量标签、类型、样本量上限和读取错误，不加载整份大文件进入内存；如果先推进线上版，则先设计上传/云对象抽象，替代本地路径绑定。

### 未解决风险

- 当前真实 CFPS `.dta` 文件仍只能显示 `blocked/not_profiled`，用户还看不到变量字典。
- XLSX/Parquet 也还没有安全字段读取器。
- 本地版绑定引用依赖本机路径；线上版必须改成上传或云对象，不能继续使用 `/Users/...` 路径。
- Playwright CLI fallback 可用并已完成截图级验收；但 Playwright MCP 仍 `Transport closed`，Computer Use 对当前 in-app browser URL 受限，后续仍应修复主浏览器自动化链路。

## 2026-05-14 P2-J Stata DTA Field Profile 交接增量

### 当前目标

真实 CFPS `.dta` 已经不再停留在文件名/阻塞状态，系统现在能在不读取整张大表的情况下展示 Stata 变量字典。该能力仍属于数据理解层，不等于实证分析，也不会自动写入变量角色或执行计划。

### 已完成事项

- 新增 BDD：`docs/architecture-v2/codex-phase-p2-dta-field-profile-bdd.md`。
- 扩展测试：`tests/test_external_dataset_import_profile.py`，覆盖有效 DTA metadata-only 画像、损坏 DTA 阻塞画像、前端变量标签/Stata 类型展示。
- 扩展 `Product/backend/overview_service.py`：新增 `build_dta_metadata_profile()`、`blocked_dta_metadata_profile()`、`infer_stata_field_type()`。
- 扩展 `Product/web/assets/app.js` 和 `Product/web/assets/styles.css`：字段画像表显示变量标签和 Stata 类型，列宽更适合变量字典。
- 更新 `Product/web/index.html` asset version 到 `20260514-p2j-dta1`。

### 已验证证据

- RED：`python3 -m unittest tests.test_external_dataset_import_profile -v` 首次 3 条失败。
- GREEN：`python3 -m unittest tests.test_external_dataset_import_profile -v`，7 tests OK。
- 相邻回归：`python3 -m unittest tests.test_external_dataset_import_profile tests.test_external_dataset_import_apply tests.test_external_dataset_bind_preflight tests.test_external_data_catalog tests.test_dataset_quality_profile -v`，28 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，187 tests OK，skipped=1。
- API：`POST /api/v1/projects/proj_undergraduate_thesis/datasets/imports/dataset_import_e9d864229be8/profile` 返回 `profiled/ready`、`row_count=1279`、`column_count=723`、`fields=723`、`can_feed_variable_roles=false`。
- 可视化：Playwright CLI 截图 `/tmp/empirical-workbench-p2j-dta-profile.png`，页面显示真实 CFPS 变量标签和 Stata 类型。

### 关键文件路径

- `Product/backend/overview_service.py`
- `Product/web/index.html`
- `Product/web/assets/app.js`
- `Product/web/assets/styles.css`
- `tests/test_external_dataset_import_profile.py`
- `docs/architecture-v2/codex-phase-p2-dta-field-profile-bdd.md`
- `state/product/dataset_import_preflights.json`（runtime 产物，不作为源码提交）

### 不能重复探索的结论

- DTA 字段画像只读元数据，不读取全量数据；`row_count_source=metadata_only` 是有意设计。
- 字段画像不是变量角色确认；`can_feed_variable_roles=false` 需要保持，直到 P2-K 建立人工审阅状态机。
- Python/pyreadstat 只负责安全读字段，不代表完整实证分析；严谨估计要由 Python/StatsPAI/StataMCP 执行器产出日志、结果、诊断和 evaluator checks。

### 下一步第一件事

P2-K：基于 `dataset_import_profile.fields` 生成可审阅的字段候选清单，允许用户选择 outcome/treatment/controls/instruments 的候选，但保存前不得改写正式 VariableRoleSet。

### 未解决风险

- DTA value labels、缺失统计和抽样预览还没有接入。
- XLSX/Parquet 仍没有安全字段读取器。
- 真实实证执行层还需要接 StatsPAI/StatsAPI、StataMCP 或 Python 的严格 pipeline，而不是只看字段画像。
- Playwright MCP 仍 `Transport closed`；当前可视化验收使用 Playwright CLI fallback。

## 2026-05-14 P2-K Rigorous Empirical Execution Contract 交接增量

### 当前目标

把“具体数据分析和实证一定严谨”落成可审计产品契约：用户必须能看到本次 run 到底由哪个后端执行、哪些后端只是候选、数据是否通过预检，以及结果如何复现。当前真实执行后端是 Python OLS adapter；StatsPAI/StatsAPI 与 StataMCP/Stata 还没有实际调用，因此不能标为 `local_execution`。

### 已完成事项

- 新增 BDD：`docs/architecture-v2/codex-phase-p2-rigorous-empirical-execution-bdd.md`。
- 扩展测试：`tests/test_ols_execution_adapter.py` 和 `tests/test_observable_execution_frontend.py`。
- 扩展 `Product/backend/project_service.py`：
  - `build_empirical_execution_contract("python_ols_adapter")`
  - `read_numeric_formula_rows_with_preflight()`
  - `build_ols_reproducibility()`
- full run 的 `method_execution_result.json` 和 run response 现在包含：
  - `execution_contract.active_backend=python_ols_adapter`
  - candidate backends：StatsPAI/StatsAPI、StataMCP/Stata
  - `data_preflight.rows_read/usable_numeric_rows/dropped_rows/required_fields`
  - `reproducibility.result_artifact_path/source_entrypoint/run_plan_version/design_spec_version`
- 扩展 `Product/web/assets/app.js`：
  - `renderMethodExecutionContract()`
  - `renderMethodDataPreflight()`
  - `renderMethodReproducibility()`
- 扩展 `Product/web/assets/styles.css`，增加严谨执行契约和预检展示样式，并修复 Execution 页面局部溢出。
- 更新 `Product/web/index.html` 静态资源版本到 `20260514-p2k-rigorous1`。

### 已验证证据

- RED：`python3 -m unittest tests.test_ols_execution_adapter tests.test_observable_execution_frontend -v` 首次失败，原因是缺少 `execution_contract`、`data_preflight` 和前端契约展示。
- GREEN：`python3 -m unittest tests.test_ols_execution_adapter tests.test_observable_execution_frontend -v`，24 tests OK。
- 相邻回归：`python3 -m unittest tests.test_ols_execution_adapter tests.test_observable_execution_frontend tests.test_observable_execution tests.test_results_draft_evidence_binding tests.test_product_api_integration -v`，42 tests OK，skipped=1。
- 全量回归：`python3 -m unittest discover -s tests -v`，190 tests OK，skipped=1。
- 静态检查：`node --check Product/web/assets/app.js`、`python3 -m py_compile Product/app.py Product/backend/project_service.py Product/backend/design_spec_service.py Product/backend/overview_service.py Product/backend/observability_service.py`、`git diff --check` 通过。
- API：真实 full run `run_5ac7052232c8` 成功，`active_backend=python_ols_adapter`，StatsPAI 与 StataMCP 为 candidate backend；`data_preflight.rows_read=12`、`usable_numeric_rows=12`、`dropped_rows=0`。
- 可视化：Playwright CLI 打开 `http://127.0.0.1:8765/?v=20260514-p2k-rigorous4`，进入“实证执行”，页面可见“严谨执行契约 / 数据预检 / 可复现入口”，`visibleOverflowCount=0`，截图为 `/tmp/empirical-workbench-p2k-rigorous-execution.png`。

### 关键文件路径

- `Product/backend/project_service.py`
- `Product/web/index.html`
- `Product/web/assets/app.js`
- `Product/web/assets/styles.css`
- `tests/test_ols_execution_adapter.py`
- `tests/test_observable_execution_frontend.py`
- `docs/architecture-v2/codex-phase-p2-rigorous-empirical-execution-bdd.md`
- `state/runs/run_5ac7052232c8/run_manifest.json`（runtime 产物，不作为源码提交）
- `state/runs/run_5ac7052232c8/project/Results/json/method_execution_result.json`（runtime 产物，不作为源码提交）

### 不能重复探索的结论

- 安装或可检测到 StatsPAI/Stata 只代表候选能力，不代表本次 run 已执行；只有实际调用并产生日志/结果文件后才能标记为 `local_execution`。
- 当前 OLS 是最小 Python 执行器，适合 baseline/evaluator 契约，不等于完整 StatsPAI/Stata 论文级流水线。
- 数据预检必须在方法执行结果里保留，不能只在 UI 上写文案；否则无法解释样本数、丢弃行和必需字段。
- UI 必须明确显示候选后端状态，不能让用户误以为 StatsPAI/StataMCP 已经参与当前估计。

### 下一步第一件事

P2-L：基于 `dataset_import_profile.fields` 做“字段审阅 / VariableRoleSet 候选生成”状态机。它应该允许用户从真实 Stata 变量字典中挑选 outcome/treatment/controls/instruments 的候选，但保存前不得改写正式 `state/product/variable_roles.json`。

### 未解决风险

- 真实 StatsPAI `sp.*` 与 Stata do-file/log 还没有接入执行。
- 当前 p 值为 normal approximation；论文级估计还需要 robust/cluster 标准误、固定效应、样本筛选日志和跨后端一致性检查。
- DTA value labels、缺失统计和抽样预览仍未接入。
- Playwright MCP 仍不稳定；当前可视化验收使用 Playwright CLI fallback。

## 2026-05-14 P2-L Variable Role Candidate Review 交接增量

### 当前目标

把真实 DTA 字段画像推进到“可审阅变量角色候选”，但继续保护正式研究状态：候选可以生成、确认、标记需调整或驳回；正式 `state/product/variable_roles.json` 只能由后续显式变量角色编辑/保存流程写入。

### 已完成事项

- 新增 BDD：`docs/architecture-v2/codex-phase-p2-variable-role-candidate-review-bdd.md`。
- 新增测试：`tests/test_variable_role_candidates.py`。
- 扩展 `Product/backend/variable_role_service.py`：
  - `generate_project_variable_role_candidate()`
  - `review_project_variable_role_candidate()`
  - `get_project_variable_role_candidates()`
  - `FieldProfileRequiredError`
  - `InvalidVariableRoleCandidateActionError`
  - `VariableRoleCandidateNotFoundError`
- 扩展 `Product/app.py`：
  - `GET /api/v1/projects/{project_id}/variable-role-candidates`
  - `POST /api/v1/projects/{project_id}/datasets/imports/{dataset_import_id}/variable-role-candidates`
  - `PUT /api/v1/projects/{project_id}/variable-role-candidates/{candidate_id}/review`
- 扩展 `Product/web/index.html`、`Product/web/assets/app.js`、`Product/web/assets/styles.css`，新增“字段审阅”面板、候选角色摘要、候选字段表和 review 按钮。
- Chrome + Computer Use 已在真实 CFPS `.dta` 页面完成生成候选和确认候选的点击级验收。

### 已验证证据

- RED：`python3 -m unittest tests.test_variable_role_candidates -v` 首次 5 条失败，原因是候选 API 404、前端缺少候选面板和 review 操作。
- GREEN：`python3 -m unittest tests.test_variable_role_candidates -v`，5 tests OK。
- 相邻回归：`python3 -m unittest tests.test_variable_role_candidates tests.test_external_dataset_import_profile tests.test_variable_role_confirmation -v`，17 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，195 tests OK，skipped=1。
- 静态检查：`python3 -m py_compile Product/app.py Product/backend/variable_role_service.py Product/backend/overview_service.py Product/backend/project_service.py` 通过；`node --check Product/web/assets/app.js` 通过。
- API：`GET /api/v1/projects/proj_undergraduate_thesis/variable-role-candidates` 返回 200。
- 可视化：Chrome + Computer Use 打开 `http://127.0.0.1:8765/?v=20260515-p2l-candidates1`，进入“数据与设计”，点击“生成变量角色候选”后可见 `待人工审阅`、`不会写入正式变量角色集`、候选字段表和 review 按钮。
- 文件边界：点击“候选已确认”后，`state/product/variable_roles.json` SHA256 仍为 `bc8bedca4d1638d2556ad77957de146eda170cef521db24eeb7ffde5c2e94649`，mtime 仍为 `1778605951`。
- 候选状态：`state/product/variable_role_candidates.json` 最新候选为 `variable_role_candidate_1fbe9c0ee659`，`status=approved_candidate`、`evidence_level=local_file`、`does_not_mutate_variable_role_set=true`。

### 关键文件路径

- `Product/backend/variable_role_service.py`
- `Product/app.py`
- `Product/web/index.html`
- `Product/web/assets/app.js`
- `Product/web/assets/styles.css`
- `tests/test_variable_role_candidates.py`
- `docs/architecture-v2/codex-phase-p2-variable-role-candidate-review-bdd.md`
- `state/product/variable_role_candidates.json`（runtime 产物，不作为源码提交）

### 不能重复探索的结论

- 字段画像生成候选不等于正式 VariableRoleSet；候选 review 只改变 candidate 状态。
- `approved_candidate` 是“这个候选被用户看过并接受为候选”，不是“论文变量角色已经确认可执行”。
- 当前角色推断只是保守启发式，用字段名/标签猜 outcome/treatment/controls；真实 CFPS 变量仍需要下一步人工编辑和变量字典检索，不能直接进入实证执行。
- Browser/Playwright MCP 当前仍 `Transport closed`，本轮可视化验收使用 Chrome + Computer Use fallback。

### 下一步第一件事

P2-M 应先把 approved candidate 连接到“正式变量角色编辑确认”流程：用户能基于真实字段候选搜索/修改 outcome、treatment、controls、instruments，保存时才写入 `state/product/variable_roles.json`，再触发 DesignSpec/RunPlan 重新生成。之后再接 StatsPAI/StataMCP/Python 严格执行器。

### 未解决风险

- 当前启发式把 `countyid` 猜为结果变量、`kt3_a_1` 猜为处理变量，这对真实研究不可信；它只适合证明状态机链路，不适合直接进入论文。
- DTA value labels、缺失统计和抽样预览还没有进入候选评分。
- 正式变量角色编辑器仍绑定旧的 `analysis_sample.csv`，还没有消费真实 CFPS candidate。
- StatsPAI/StataMCP 仍未实际执行；严谨实证执行仍停留在 Python OLS adapter。

## 2026-05-14 P2-M Candidate Promotion to Formal VariableRoleSet 交接增量

### 当前目标

把 P2-L 已确认的真实字段候选推进到“正式变量角色编辑确认”流程：候选可以被载入编辑器、人工调整，并且只有用户点击保存后才写入正式 `VariableRoleSet`。这一步解决“真实数据还没有进入变量角色候选生成/确认”的关键缺口，但仍保护正式研究状态不被启发式自动覆盖。

### 已完成事项

- 新增 BDD：`docs/architecture-v2/codex-phase-p2-variable-role-candidate-promote-bdd.md`。
- 扩展 `tests/test_variable_role_candidates.py`，新增 3 条 P2-M 行为测试。
- 扩展 `Product/backend/variable_role_service.py`：
  - `save_project_variable_roles(..., candidate_id=...)`
  - `VariableRoleCandidateApprovalRequiredError`
  - candidate 写回后状态更新为 `applied_to_variable_roles`
- 扩展 `Product/app.py`：
  - `VariableRolePayload.candidate_id`
  - 保存变量角色 API 对未确认 candidate 返回 409 `variable_role_candidate_approval_required`
- 扩展 `Product/web/assets/app.js`：
  - `pendingVariableRoleCandidateId`
  - `载入正式编辑器` 按钮
  - `loadVariableRoleCandidateIntoEditor()`
  - 保存变量角色集时携带 `candidate_id`

### 已验证证据

- RED：`python3 -m unittest tests.test_variable_role_candidates -v` 首次新增行为失败，失败点是旧后端按 `dataset_path` 拒绝真实 candidate，前端缺少 candidate-to-editor 状态。
- GREEN：`python3 -m unittest tests.test_variable_role_candidates -v`，8 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，198 tests OK，skipped=1。
- 静态检查：`python3 -m py_compile Product/backend/variable_role_service.py Product/app.py` 通过；`node --check Product/web/assets/app.js` 通过。
- 可视化：Chrome + Computer Use 打开 `http://127.0.0.1:8765/?v=20260514-p2m`，点击“数据与设计” -> “载入正式编辑器”，编辑器显示 `draft_from_candidate · local_file`、真实 CFPS DTA 路径、`candidate_id=variable_role_candidate_495092cb7af2` 和“保存后才写入正式变量角色集”。

### 关键文件路径

- `Product/backend/variable_role_service.py`
- `Product/app.py`
- `Product/web/assets/app.js`
- `tests/test_variable_role_candidates.py`
- `docs/architecture-v2/codex-phase-p2-variable-role-candidate-promote-bdd.md`
- `tasks/todo.md`
- `tasks/handoff.md`
- `tasks/decision-log.md`
- `tasks/manifest.md`
- `tasks/review.md`

### 不能重复探索的结论

- `approved_candidate` 不等于正式变量角色集；它只允许被载入正式编辑器。
- 从 candidate 写回正式 VariableRoleSet 时，必须保留 `candidate_id` 和数据来源 provenance，否则后续 DesignSpec/RunPlan 无法审计。
- 当前 CFPS role candidate 仍是启发式，不可自动点击保存；必须由用户人工检查后再确认。
- Browser/Playwright MCP 仍不稳定，本轮使用 Chrome + Computer Use 做点击级验收。

### 下一步第一件事

P2-N：让 DesignSpec/RunPlan 消费正式 VariableRoleSet 的真实数据来源，并增加执行前 preflight：如果正式角色来自真实 DTA candidate，则必须能解析 `source` / `binding`，明确本地版可读、云端需上传，并准备 StatsPAI/StataMCP/Python 后端执行日志与 evaluator checks。

### 未解决风险

- 字段搜索、多候选对比、value labels、缺失统计和样本预览还没进入变量角色人工选择体验。
- DesignSpec/RunPlan 尚未自动基于新正式 VariableRoleSet 刷新。
- StatsPAI/StataMCP 尚未实际执行；目前只有 Python OLS adapter 是 `local_execution`。
- 线上版不能消费 `/Users/...` 本地路径，必须在后续引入上传/云对象 source abstraction。

## 2026-05-16 P2-P Local Codex SupervisorPlan 交接增量

### 当前目标

P2-P 已把“本地 Codex Supervisor”从 readiness 面板推进为可持久化计划层：系统现在可以在显式启用 `EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC=1` 后调用本地 Codex，生成 `state/product/supervisor_plan.json`。该计划状态固定为 `needs_review`，只提出阶段计划、风险、证据要求、子 Agent 分工和下一步人工 gate；它不能直接篡改 `VariableRoleSet`、`DesignSpec` 或 `RunPlan`。

### 已完成事项

- 新增 BDD：`docs/architecture-v2/codex-phase-p2-supervisor-plan-bdd.md`。
- 新增测试：`tests/test_supervisor_plan.py`，覆盖执行开关阻断、启用后持久化计划、不改写正式研究状态、GET 返回已保存计划、前端审阅台。
- 新增后端：`Product/backend/supervisor_plan_service.py`。
- 扩展 Codex provider：`Product/backend/codex_provider.py` 新增 `run_local_codex_prompt()`。
- 扩展 API：`Product/app.py` 新增 `GET/POST /api/v1/projects/{project_id}/supervisor-plan`。
- 扩展前端：`Product/web/index.html`、`Product/web/assets/app.js`、`Product/web/assets/styles.css` 新增 `SupervisorPlan 审阅台`。
- 修复本机验证环境：当前 `statspai` 已重装为 `1.15.1`，`import statspai as sp` 后 `sp.regress` 可用；此前全量测试失败来自本地 broken namespace package，不是本轮代码回归。

### 已验证证据

- RED：`python3 -m unittest tests.test_supervisor_plan -v` 首次 5 条失败；4 条 API 是 404，1 条前端缺少审阅台。
- GREEN：`python3 -m unittest tests.test_supervisor_plan -v`，5 tests OK。
- 相邻回归：`python3 -m unittest tests.test_supervisor_plan tests.test_product_workflow_contract tests.test_design_run_plan_state_machine -v`，20 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，208 tests OK，skipped=1。
- 静态检查：`node --check Product/web/assets/app.js` 通过；`python3 -m py_compile Product/backend/supervisor_plan_service.py Product/backend/codex_provider.py Product/app.py Product/backend/overview_service.py` 通过；`git diff --check` 通过。
- API 验收：`GET /api/v1/projects/proj_undergraduate_thesis/supervisor-plan` 返回 empty plan、provider available、execution_enabled=false；`POST` 返回 409 `local_codex_execution_not_enabled`。
- 可视化验收：当前工作树服务使用 `http://127.0.0.1:8767/?v=20260516-p2p-supervisor-plan`，DOM 显示 `SupervisorPlan 审阅台`、`生成 SupervisorPlan`、`本地 Codex SupervisorPlan`、`local_codex_execution_not_enabled`；截图为 `artifacts/ui-checks/p2p-supervisor-plan-overview.png`。

### 关键文件路径

- `Product/backend/supervisor_plan_service.py`
- `Product/backend/codex_provider.py`
- `Product/app.py`
- `Product/web/index.html`
- `Product/web/assets/app.js`
- `Product/web/assets/styles.css`
- `tests/test_supervisor_plan.py`
- `docs/architecture-v2/codex-phase-p2-supervisor-plan-bdd.md`
- `artifacts/ui-checks/p2p-supervisor-plan-overview.png`

### 不能重复探索的结论

- `local_codex_status.available=true` 只代表本地 Codex CLI 可检测，不代表允许执行。未设置 `EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC=1` 时必须阻断。
- SupervisorPlan 是 review artifact，不是 write-back artifact；它不能直接改写 `state/product/variable_roles.json`、`state/product/design_spec.json` 或 `state/product/run_plan.json`。
- 当前成功路径用 fake Codex CLI 测试固定 JSON 输出；真实 Codex subprocess 的不稳定输出由 `supervisor_plan.raw.md` 留痕并经 JSON 解析约束。
- StatsPAI 本机环境已经修复为 `1.15.1`；不要把旧的 `module 'statspai' has no attribute 'regress'` 当作项目代码问题重复排查。

### 下一步第一件事

P2-Q：给 SupervisorPlan 增加显式 approve/reject/needs_revision 审批 API 和前端操作。只有 approved SupervisorPlan 才能进入任务队列或下一轮执行编排；reject/needs_revision 必须保留审阅意见并阻止派工。

### 未解决风险

- 真实 Codex 生成计划尚未在持久 app 中执行，本轮只验证了默认阻断和 fake Codex 成功路径。
- SupervisorPlan 还没有 approval 状态机；现在只是 `needs_review` artifact。
- 尚未真正启动子 Agent、StataMCP、DID/IV/RDD/PSM/DML 或真实 CFPS 执行。
- 本地版和线上版仍要拆分 provider：本地版可以调用本地 Codex 和本地统计后端，线上版必须走云模型、上传数据和云执行队列。

## 2026-05-16 P2-P1 首页渐进披露交接增量

### 当前目标

本轮解决用户指出的“屏幕信息太满、短时记忆被冲爆”的问题。首页不再默认摊开智能中控和 SupervisorPlan 的全部细节，而是先展示状态、证据等级、主动作和下一步信号；Provider、执行开关、派工、写入边界、证据要求、风险等二级信息放进原生可展开详情。

### 已完成事项

- 新增 BDD：`docs/architecture-v2/codex-phase-p2-home-progressive-disclosure-bdd.md`。
- 扩展测试：`tests/test_supervisor_plan.py` 新增 SupervisorPlan 细节折叠行为；`tests/test_product_workflow_contract.py` 新增智能中控细节折叠行为。
- 修改前端：`Product/web/assets/app.js` 的 `renderIntelligenceLayer()` 和 `renderSupervisorPlan()` 使用 `details/summary` 做渐进披露。
- 修改样式：`Product/web/assets/styles.css` 新增 `.progressive-disclosure`、`.disclosure-panel`、`.decision-signal-row`，并补齐 focus-visible。
- 更新静态资源版本：`Product/web/index.html` 改为 `20260516-p2p-disclosure1`。

### 已验证证据

- RED：`python3 -m unittest tests.test_supervisor_plan tests.test_product_workflow_contract -v` 首次新增 2 条失败，缺少 `supervisor-plan-progressive-disclosure` 和 `intelligence-progressive-disclosure`。
- GREEN：同一目标测试再次运行，15 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，210 tests OK，skipped=1。
- 静态检查：`node --check Product/web/assets/app.js` 通过；`python3 -m py_compile Program/run_paper.py Program/workbench/observability.py Product/backend/observability_service.py Product/backend/project_service.py Product/app.py` 通过；`git diff --check` 通过。
- 右侧内置浏览器验收：`http://127.0.0.1:8767/?v=20260516-p2p-disclosure1` 初始状态下 `.llm-supervisor-details.open=false`、`.supervisor-plan-details.open=false`；点击后 `llmOpen=true`、`planOpen=true`，Provider 和计划明细可见。
- 截图：`artifacts/ui-checks/p2p-home-progressive-disclosure.png`。

### 关键文件路径

- `Product/web/index.html`
- `Product/web/assets/app.js`
- `Product/web/assets/styles.css`
- `tests/test_supervisor_plan.py`
- `tests/test_product_workflow_contract.py`
- `docs/architecture-v2/codex-phase-p2-home-progressive-disclosure-bdd.md`
- `artifacts/ui-checks/p2p-home-progressive-disclosure.png`

### 不能重复探索的结论

- 首页的高噪声字段不应默认展示；用户第一眼只需要决策信号、主动作和风险数量。
- 渐进披露要保留审计能力，不是删除内容；细节必须能点击展开。
- 这次只改 UI 信息架构，不改变 SupervisorPlan API、不启用 Codex 执行、不改写 VariableRoleSet/DesignSpec/RunPlan。

### 下一步第一件事

P2-Q：给 SupervisorPlan 增加 approve/reject/needs_revision 审批 API、状态文件记录和前端操作。只有 approved SupervisorPlan 才能进入任务队列或下一轮执行编排。

### 未解决风险

- 当前渐进披露只覆盖首页智能中控和 SupervisorPlan；执行页、数据页、Review & Export 的局部密度还需要继续按同样规则收敛。
- 右侧内置浏览器已验证点击展开，但还没有做移动视口截图。
- SupervisorPlan 仍无审批状态机，不能进入真实任务队列。

## 2026-05-16 P2-Q 选题优先首页交接增量

### 当前目标

把首页从“功能全集铺开”改成“先确定研究选题，再进入判断环节”。这轮解决用户指出的核心产品路径问题：用户进来不应先看到全部 Agent、执行、证据和风险，而应先输入或选择一个研究问题。

### 已完成事项

- 新增 BDD：`docs/architecture-v2/codex-phase-p2-topic-first-home-bdd.md`。
- 扩展测试：`tests/test_product_workflow_contract.py` 增加 3 个首页选题优先行为。
- 修改 HTML：`Product/web/index.html` 新增 `research-topic-intake`，并把原首页工作台细节包进 `research-workbench-after-topic`。
- 修改 JS：`Product/web/assets/app.js` 新增选题读取、保存、确认、从已有选题继续、跳转真实数据候选池等交互。
- 修改 CSS：`Product/web/assets/styles.css` 新增选题入口样式，并在窄视口隐藏右侧 inspector、压缩侧栏，避免首屏被导航/审计信息占满。
- 后台服务：`http://127.0.0.1:8767/?v=20260516-p2q-topic1` 已用后台 `uvicorn` 进程启动，日志在 `/tmp/empirical-workbench-8767.log`。

### 已验证证据

- RED：`python3 -m unittest tests.test_product_workflow_contract.ProductWorkflowFrontendContractTests -v` 首次新增 3 条失败，缺少选题入口、隐藏工作台和数据候选入口。
- GREEN：同一目标测试再次运行，9 tests OK。
- 相邻回归：`python3 -m unittest tests.test_product_workflow_contract tests.test_supervisor_plan -v`，18 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，213 tests OK，skipped=1。
- 静态检查：`node --check Product/web/assets/app.js` 通过；Python 编译检查通过；`git diff --check` 通过。
- 右侧内置浏览器验收：初始状态 `research-workbench-after-topic` 隐藏，证据 banner 不显示；输入“机器人应用是否影响劳动力市场匹配效率？”并点击 `进入研究判断` 后，工作台区域展开并显示下一步研究决策。

### 关键文件路径

- `Product/web/index.html`
- `Product/web/assets/app.js`
- `Product/web/assets/styles.css`
- `tests/test_product_workflow_contract.py`
- `docs/architecture-v2/codex-phase-p2-topic-first-home-bdd.md`

### 不能重复探索的结论

- 首页第一屏必须服务“用户要研究什么”，不是展示系统已经有哪些模块。
- 原有智能中控、SupervisorPlan、风险和证据不是删除，而是放到选题确认后的第二层。
- 当前选题状态只是前端本地状态；这轮不能把它误写成正式 VariableRoleSet、DesignSpec、RunPlan 或 SupervisorPlan。
- `从真实数据候选池开始` 只能导航到数据与设计页，不能自动绑定数据或生成变量角色。

### 下一步第一件事

P2-R：新增后端 `ResearchQuestion` / `TopicSession` 状态机，把用户确认的选题持久化为可审计研究对象；然后让 SupervisorPlan 审批、变量候选和执行计划都绑定到这个研究对象。

### 未解决风险

- 选题目前只在前端 localStorage / 当前页面状态中保存，跨设备和后端审计不可用。
- 右侧内置浏览器截图捕获超时，本轮用 DOM 和可见交互验证替代截图。
- 选题确认后还没有驱动真实 SupervisorPlan 审批或任务队列。
- 数据页、执行页、Review & Export 页仍需要继续按“默认摘要、按需展开”收敛信息密度。

## 2026-05-16 P2-R ResearchQuestion / TopicSession 交接增量

### 当前目标

把首页“输入或选择研究选题”从前端本地状态升级为产品级 ResearchQuestion / TopicSession。用户确认选题后，系统必须保存到项目本地状态文件，供后续 SupervisorPlan、VariableRoleSet、DesignSpec、RunPlan 和跨 Session 恢复引用；但本轮明确不让选题确认自动篡改变量角色、设计方案或执行计划。

### 已完成事项

- 新增 BDD：`docs/architecture-v2/codex-phase-p2-research-question-topic-session-bdd.md`。
- 新增测试：`tests/test_research_question_topic_session.py`。
- 扩展测试：`tests/test_product_workflow_contract.py` 增加“首页确认选题必须调用后端 ResearchQuestion API”行为。
- 新增服务：`Product/backend/research_question_service.py`，保存路径为 `state/product/research_question.json`，证据等级为 `local_file`。
- 扩展 API：`GET/PUT /api/v1/projects/{project_id}/research-question/current`。
- 扩展 overview：`GET /overview` 返回 `research_question_state`，并把 workflow 中 ResearchQuestion 阶段设为 `completed` 或 `requires_confirmation`。
- 扩展前端：首页保存选题时调用后端 API，保存后刷新 overview，并继续用渐进披露隐藏后续工作台。
- 更新静态资源版本：`20260516-p2r-topic-session1`。

### 已验证证据

- RED：新增测试首次运行时 5 条后端测试因 `/research-question/current` 404 失败，1 条前端测试因缺少 `researchQuestion` API binding 失败。
- GREEN：`python3 -m unittest tests.test_research_question_topic_session tests.test_product_workflow_contract.ProductWorkflowFrontendContractTests -v`，15 tests OK。
- 核心回归：`python3 -m unittest tests.test_research_question_topic_session tests.test_product_workflow_contract tests.test_supervisor_plan tests.test_design_run_plan_state_machine tests.test_variable_role_confirmation -v`，36 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，219 tests OK，skipped=1。
- 静态检查：Python 编译、`node --check Product/web/assets/app.js`、`git diff --check` 均通过。
- 浏览器验收：内置浏览器打开 `http://localhost:8767/?v=20260516-p2r-topic-session1&fresh=1`，点击“进入研究判断”后写入 ResearchQuestion；随后刷新页面显示 `机器人应用是否影响劳动力市场匹配效率？`，工作台区域自动展开，console error 为 0。
- 状态文件验收：`state/product/research_question.json` 写入 `status=confirmed`、`topic_session_id=topic_session_v2`、`evidence_level=local_file`、`write_boundary=不会自动改写 VariableRoleSet、DesignSpec 或 RunPlan`。

### 不能重复探索的结论

- 首页确认选题不再只依赖 localStorage；localStorage 只能作为前端体验缓存，正式状态源是 `state/product/research_question.json`。
- `ResearchQuestion` 只是研究上下文入口，不是自动建模指令；保存它不得创建或改写 `variable_roles.json`、`design_spec.json`、`run_plan.json`。
- 未确认时 API 返回 project seed draft 且不创建状态文件，避免把默认题目误标成用户确认。
- 本轮没有启用真实 LLM 派工；下一步应让 SupervisorPlan 引用已确认 ResearchQuestion 并进入人工审阅。

### 下一步第一件事

P2-S：SupervisorPlan 生成时读取 `research_question_state`、VariableRoleSet、DesignSpec 和 RunPlan 的当前状态，输出可审阅 plan artifact。这个 artifact 应包含目标、风险、证据要求、子 Agent 分工、下一步动作；仍不得自动修改正式研究状态。

### 未解决风险

- 浏览器验收产生的 `state/product/research_question.json` 是 gitignored runtime state；当前为本机验收保留，后续若要做示例项目 fixture，应单独迁移。
- 浏览器插件对 textarea 填充中文时出现 clipboard/timeout 问题；本轮通过点击 seed 选题路径验证 UI 保存，再用 API 写入中文题目并刷新页面验证持久化渲染。
- 当前 ResearchQuestion API 还没有多选题/版本比较界面，只保留单个 current TopicSession。
- SupervisorPlan 还没有消费这个状态对象；这就是下一轮 P2-S 的主任务。

## 2026-05-16 P2-S SupervisorPlan 绑定选题交接增量

### 当前目标

让本地 Codex SupervisorPlan 不再围绕项目名或旧设计状态泛泛生成计划，而是显式消费已确认的 `ResearchQuestion / TopicSession`。计划仍然只是待审 artifact，不允许自动改写 `ResearchQuestion`、`VariableRoleSet`、`DesignSpec` 或 `RunPlan`。

### 已完成事项

- 新增 BDD：`docs/architecture-v2/codex-phase-p2-supervisor-plan-topic-binding-bdd.md`。
- 扩展测试：`tests/test_supervisor_plan.py` 增加缺少 confirmed ResearchQuestion 的阻断、计划输入证据、Codex prompt 绑定和前端展示。
- 修改 `Product/backend/supervisor_plan_service.py`：生成前调用 `load_saved_research_question()`，要求 `status=confirmed`，否则返回 409 `research_question_required`。
- 修改 Codex prompt：新增 `confirmed_research_question`，包含 `question`、`topic_session_id`、`version`、`evidence_level` 和 `path`。
- 修改 normalized plan：新增 `input_research_question`，并在 `input_state_versions` / `input_evidence` 中记录 ResearchQuestion 版本和路径。
- 修改 `Product/web/assets/app.js`：SupervisorPlan 审阅台摘要显示 `绑定选题`，展开后显示 `TopicSession` 和 `ResearchQuestion 版本`。
- 更新静态资源版本：`20260516-p2s-supervisor-topic1`。

### 已验证证据

- RED：`python3 -m unittest tests.test_supervisor_plan -v` 首次 5 条失败；3 条因 prompt 缺少 confirmed research question 返回 502，1 条因缺少 ResearchQuestion 时没有返回 `research_question_required`，1 条前端缺少选题绑定展示。
- GREEN：`python3 -m unittest tests.test_supervisor_plan -v`，8 tests OK。
- 相邻回归：`python3 -m unittest tests.test_supervisor_plan tests.test_research_question_topic_session tests.test_product_workflow_contract.ProductWorkflowFrontendContractTests -v`，23 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，221 tests OK，skipped=1。
- 静态检查：`python3 -m py_compile Product/backend/supervisor_plan_service.py Product/backend/research_question_service.py Product/app.py Product/backend/overview_service.py` 通过；`node --check Product/web/assets/app.js` 通过；`git diff --check` 通过。
- 浏览器验收：`http://127.0.0.1:8767/?v=20260516-p2s-supervisor-topic1` 自动识别 confirmed ResearchQuestion，`SupervisorPlan 审阅台` 显示 `绑定选题：机器人应用是否影响劳动力市场匹配效率？`，展开详情可见 TopicSession/ResearchQuestion 版本槽位，console error=0；截图保存到 `artifacts/ui-checks/p2s-supervisor-topic-binding.png`。

### 关键文件路径

- `Product/backend/supervisor_plan_service.py`
- `Product/web/assets/app.js`
- `Product/web/index.html`
- `tests/test_supervisor_plan.py`
- `docs/architecture-v2/codex-phase-p2-supervisor-plan-topic-binding-bdd.md`

### 不能重复探索的结论

- SupervisorPlan 必须基于 confirmed ResearchQuestion；project seed draft 不能当作用户确认选题。
- Codex prompt 必须携带 `confirmed_research_question` 和 `topic_session_id`，否则计划无法审计。
- 绑定选题仍不是执行授权；它只让计划有研究上下文，不允许跳过人工审批。

### 下一步第一件事

P2-T：给 SupervisorPlan 增加 approve/reject/needs_revision API、状态文件记录和前端操作。只有 approved SupervisorPlan 才能拆成 Agent Task Queue。

### 未解决风险

- 当前仍没有 SupervisorPlan 审批状态机；`needs_review` 计划不能派工。
- 本轮使用 fake Codex CLI 测试 prompt contract；真实本地 Codex 执行还需要在启用环境变量后做一次人工验收。
- 默认环境没有启用本地 Codex 执行，因此浏览器只验证了“空计划 + confirmed ResearchQuestion fallback”的绑定展示；真实 plan 的 `TopicSession` 值由 fake Codex 测试覆盖，后续开启执行开关后需要再做一次人工验收。

## 2026-05-16 P2-T SupervisorPlan Review State Machine 交接增量

### 当前目标

把本地 Codex Supervisor 生成的 `SupervisorPlan` 放进显式人工审批状态机。计划必须先被批准，才可以进入下一步 Agent Task Queue；要求修改或驳回都必须阻断派工。审批动作本身不能改写 ResearchQuestion、VariableRoleSet、DesignSpec 或 RunPlan。

### 已完成事项

- 新增 BDD：`docs/architecture-v2/codex-phase-p2-supervisor-plan-review-bdd.md`。
- 扩展测试：`tests/test_supervisor_plan.py` 覆盖审批 API、非法 action、缺少计划、不可篡改正式研究状态和前端审批按钮。
- 修改 `Product/backend/supervisor_plan_service.py`：新增 `review_project_supervisor_plan()` 和 `InvalidSupervisorPlanReviewActionError`。
- 修改 `Product/app.py`：新增 `PUT /api/v1/projects/{project_id}/supervisor-plan/review`。
- 修改 `Product/web/assets/app.js`：存在计划时渲染 `批准计划`、`要求修改`、`驳回计划`，并调用 review API。
- 修改 `Product/web/assets/styles.css`：新增审批区样式，并保持单列布局，避免把 clean workbench 又做回拥挤双列。
- 新增验收截图：`artifacts/ui-checks/p2t-supervisor-review-page.png`。

### 已验证证据

- RED：新增审批测试首次失败，原因是 review API、状态持久化和前端按钮尚未实现。
- GREEN：`python3 -m unittest tests.test_supervisor_plan -v`，13 tests OK。
- 相邻回归：`python3 -m unittest tests.test_supervisor_plan tests.test_research_question_topic_session tests.test_product_workflow_contract.ProductWorkflowFrontendContractTests -v`，28 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，226 tests OK，skipped=1。
- 静态检查：`python3 -m py_compile Product/backend/supervisor_plan_service.py Product/app.py` 通过；`node --check Product/web/assets/app.js` 通过；`git diff --check` 通过。
- 浏览器验收：`http://127.0.0.1:8767/?v=20260516-p2t-supervisor-review1` 显示 `SupervisorPlan 审阅台`、`尚未生成`、`生成 SupervisorPlan`、绑定选题和人工确认说明；当前真实项目没有 `state/product/supervisor_plan.json`，所以不显示审批按钮是正确状态。

### 关键文件路径

- `Product/backend/supervisor_plan_service.py`
- `Product/app.py`
- `Product/web/assets/app.js`
- `Product/web/assets/styles.css`
- `tests/test_supervisor_plan.py`
- `docs/architecture-v2/codex-phase-p2-supervisor-plan-review-bdd.md`
- `artifacts/ui-checks/p2t-supervisor-review-page.png`

### 不能重复探索的结论

- SupervisorPlan 审批不是变量角色确认、不是设计方案确认、也不是 RunPlan 确认；它只授权或阻断下一步派工。
- 没有计划产物时不能显示 approve/reject，因为用户不能审批不存在的东西。
- `approve` 可以设置 `can_dispatch=true`，但还不能直接启动任务；真正拆任务队列是 P2-U。
- `needs_revision` 和 `reject` 都必须保留人工意见并阻断派工，区别在于下一步是修订当前计划还是重新生成计划。

### 下一步第一件事

P2-U：读取 `status=approved` 且 `can_dispatch=true` 的 SupervisorPlan，把其中的阶段计划和子 Agent 分工拆成 `AgentTaskQueue`。队列项应包含 owner agent、输入证据、输出要求、阻塞项、状态、审计日志和人工 gate；未 approved 的计划必须返回阻断原因。

### 未解决风险

- 当前真实项目还没有生产 `supervisor_plan.json`，所以浏览器只验收了无计划状态；有计划后的按钮路径由测试覆盖，后续开启本地 Codex 执行后要做一次真实点击验收。
- P2-U 尚未实现，approved 计划不会自动变成任务队列。
- 本地 Codex 执行仍需 `EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC=1`，默认关闭是为了避免模型输出在未授权时进入项目状态。
- StatsPAI/StataMCP 的完整方法族执行仍是后续 P2-W/P2-N 工作，不属于本轮审批状态机。

## 2026-05-17 外部 UI 参考学习交接增量

### 当前目标

下载并学习 `BV16BRQBSEVy` 和 Kole Jain `mobile-app-ui` 资源，把结论沉淀为我们实证研究工作台后续 UI/交互迭代原则。

### 已完成事项

- 已下载 Bilibili 视频、metadata、缩略图、音频和本地 whisper 转写。
- 已解析 Kole Jain resources 页面，确认 `Mobile App UI` 资源包含 watch link、Figma link、`.fig` 下载和 5 张预览图。
- 已下载 `Mobile App UI.fig`、缩略图、5 张预览图，并生成 contact sheet。
- 已新增学习笔记：`docs/reference-learning/mobile-app-ui-kole-jain-bilibili-2026-05-17.md`。
- 已把大体积参考下载加入 `.gitignore`，避免把视频、模型和 Figma 二进制误提交。

### 已验证证据

- Bilibili metadata 显示标题为 `8分钟带你了解移动应用UI的一切（新手友好）`，时长约 499 秒。
- 本地转写输出：`artifacts/reference-learning/bilibili-bv16brqbsevy/transcript.txt`、`.srt`、`.json`。
- Kole Jain resource manifest 中 `mobile-app-ui` 的 Figma link 为 `https://www.figma.com/design/WwEtNcIqpDNxYZx4ZpiE7m/Mobile-App-UI?...`。
- 本地下载目录：`artifacts/reference-learning/kolejain-resources/`。

### 不能重复探索的结论

- 这些参考资料不是要我们复制移动 app 或暗色风格，而是要吸收信息层级：一屏一个主任务、细节按需展开、空状态给下一步、主操作随对象状态变化。
- 对我们的产品而言，移动端导航经验对应的是“对象状态驱动的主操作”，不是把桌面工作台改成手机底部栏。
- 页面拥挤不能靠缩小字体解决，必须减少默认可见决策数量。

### 下一步第一件事

P2-U Agent Task Queue 设计时直接应用这份学习结论：队列页默认只显示任务摘要和当前阻塞，选中任务后才展开输入证据、输出要求、工具日志和 provenance。

### 未解决风险

- Bilibili 转写使用 tiny 模型，能覆盖学习要点，但不是逐字校对稿。
- Kole Jain `.fig` 已下载但未被程序化解析为 Figma 节点；本轮学习基于页面 metadata、预览图和视频转写。
- 还没有把这些原则真正落到 P2-U 页面，需要下一轮 BDD/TDD 进入实现。

## 2026-05-17 P2-U Agent Task Queue 交接增量

### 当前目标

把 approved SupervisorPlan 转成可审阅的 Agent Task Queue。队列是派工草案，不是自动执行器；它必须让用户先看到任务摘要、负责人、阻塞项和状态，再按需展开输入证据、输出要求、风险和审计日志。

### 已完成事项

- 新增 BDD：`docs/architecture-v2/codex-phase-p2-agent-task-queue-bdd.md`。
- 新增测试：`tests/test_agent_task_queue.py`，覆盖阻断、创建、恢复、不可篡改正式研究状态、前端摘要优先和空 `subagent_dispatch`。
- 新增后端服务：`Product/backend/agent_task_queue_service.py`。
- 新增 API：`GET /api/v1/projects/{project_id}/agent-task-queue` 和 `POST /api/v1/projects/{project_id}/agent-task-queue`。
- 新增状态文件契约：`state/product/agent_task_queue.json`。
- 前端首页新增 `Agent 任务队列` 面板，接入读取、显式创建、摘要 ledger、任务列表和 `details/summary` 折叠详情。
- 创建队列不会执行子 Agent，也不会改写 `ResearchQuestion`、`VariableRoleSet`、`DesignSpec`、`RunPlan` 或 `SupervisorPlan`。

### 已验证证据

- RED：`python3 -m unittest tests.test_agent_task_queue -v` 首次 8 条失败，原因是 API 404、服务缺失和前端缺少队列面板。
- GREEN：`python3 -m unittest tests.test_agent_task_queue -v`，8 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，234 tests OK，skipped=1。
- 静态检查：`python3 -m py_compile Product/app.py Product/backend/agent_task_queue_service.py Product/backend/supervisor_plan_service.py` 通过；`node --check Product/web/assets/app.js` 通过；`git diff --check` 通过。
- 浏览器真实阻塞态：`http://127.0.0.1:8768/?v=20260517-p2u-final-browser` 显示 `缺少 SupervisorPlan`，创建按钮 disabled，console error=0；截图 `/tmp/empirical-workbench-agent-task-queue-p2u-final.png`。
- 浏览器受控成功态：approved-plan 场景点击创建后显示 2 个任务、2 个详情默认折叠、创建按钮消失，console error=0；截图 `/tmp/empirical-workbench-agent-task-queue-p2u-approved.png`。

### 关键文件路径

- `Product/backend/agent_task_queue_service.py`
- `Product/app.py`
- `Product/web/index.html`
- `Product/web/assets/app.js`
- `Product/web/assets/styles.css`
- `tests/test_agent_task_queue.py`
- `docs/architecture-v2/codex-phase-p2-agent-task-queue-bdd.md`
- `state/product/agent_task_queue.json`

### 不能重复探索的结论

- Agent Task Queue 只能从 approved SupervisorPlan 创建；`needs_review`、`needs_revision`、`rejected` 或不存在的计划都必须阻断。
- 创建队列不是执行任务，不能自动调用子 Agent，也不能把 LLM 建议写入正式研究对象。
- 队列 UI 默认必须摘要优先，任务证据和审计明细按需展开，避免回到信息噪声过载。
- 当前真实项目没有 approved `state/product/supervisor_plan.json`，所以页面出现阻塞态是正确产品状态，不是 bug。

### 下一步第一件事

P2-V：给 Agent Task Queue 增加“人工派工 / 执行前审计”状态。用户应能逐项检查任务输入证据、输出要求和阻塞项，然后才允许把某个任务交给具体执行后端或子 Agent。

### 未解决风险

- 真实 Codex Supervisor 生产计划后的 approve -> create 全链路还需要在 `EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC=1` 环境下人工验收。
- 当前队列没有任务执行 worker，也没有 retry/cancel/assign 状态；P2-U 只完成可审阅派工草案。
- 成功态浏览器验收使用 route interception，避免污染当前真实项目状态；真实后端持久化行为由测试覆盖。
- 还没有移动视口视觉验收。

## 2026-05-17 P2-Y Reviewer Scorecard 交接增量

### 当前目标

把 successful full run 后的审稿反馈变成可持久化的产品对象：五维评分、证据、理由、风险和后续任务建议。它用于决定下一轮研究迭代，不直接修改 Agent Task Queue、FindingCard、Manuscript candidate 或 Export package。

### 已完成事项

- 新增 BDD：`docs/architecture-v2/codex-phase-p2-reviewer-scorecard-bdd.md`。
- 新增测试：`tests/test_reviewer_scorecard.py`，覆盖无 full run 阻断、五维评分、低分任务建议不改写队列、前端折叠详情。
- 新增后端服务：`Product/backend/reviewer_score_service.py`。
- 新增 API：`GET /api/v1/projects/{project_id}/reviewer-scorecard` 和 `POST /api/v1/projects/{project_id}/reviewer-scorecard`。
- Review & Export 页面新增 `审稿评分` 面板，默认只显示分数和信号；理由、证据和任务建议在 `查看理由与后续任务` 中展开。
- 后续任务建议只提供 `加入任务队列草案` 的显式入口提示，不自动写入 `state/product/agent_task_queue.json`。

### 已验证证据

- RED：`python3 -m unittest tests.test_reviewer_scorecard -v` 首次 4 条失败，原因是 `/reviewer-scorecard` API 404 和前端缺少 `reviewer-scorecard-panel`。
- GREEN：`python3 -m unittest tests.test_reviewer_scorecard -v`，4 tests OK。
- 相邻回归：`python3 -m unittest tests.test_reviewer_scorecard tests.test_results_draft_evidence_binding tests.test_review_export_package -v`，25 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，252 tests OK，skipped=1。
- 静态检查：`python3 -m py_compile Product/app.py Product/backend/reviewer_score_service.py Product/backend/results_draft_service.py Product/backend/agent_task_queue_service.py` 通过；`node --check Product/web/assets/app.js` 通过；`git diff --check` 通过。
- 浏览器验收：`http://127.0.0.1:8768/?v=20260517-p2y-reviewer-scorecard` 显示 5 个评分维度；details 初始打开数量为 0，点击后为 1；任务草案按钮可见；`errors=[]`、`badResponses=[]`；截图 `/tmp/p2y-reviewer-scorecard.png`。

### 关键文件路径

- `Product/backend/reviewer_score_service.py`
- `Product/app.py`
- `Product/web/index.html`
- `Product/web/assets/app.js`
- `Product/web/assets/styles.css`
- `tests/test_reviewer_scorecard.py`
- `docs/architecture-v2/codex-phase-p2-reviewer-scorecard-bdd.md`

### 不能重复探索的结论

- Reviewer Scorecard 不是论文审稿人的真实意见；当前后端是 `deterministic_baseline`，证据等级为 `local_file`，只能作为产品闭环的最小评分对象。
- 评分卡的后续任务建议不能自动进入 Agent Task Queue；必须先经过人工接受和派工审阅，否则会绕过 P2-U/P2-V 的安全边界。
- 无 successful full run 时不能生成评分卡；否则会把没有结果证据的反馈伪装成审稿意见。

### 下一步第一件事

P2-Z：给 Results、Manuscript 和 Export 增加 verifier gates。最低要求是结果核验、正文证据绑定核验、导出预检核验都以显式 gate 出现，未通过 gate 的对象不能进入最终导出。

### 未解决风险

- 当前评分是 deterministic baseline，不是真实 LLM reviewer 或外部审稿 Agent。
- 任务建议还没有真正写入 proposed queue；本轮只做显式入口和不自动改写边界。
- 评分维度是最小五维，没有引入 DID/IV/RDD 等方法族的专门审稿 rubrics。

## 2026-05-17 P2-Z Verifier Gates 交接增量

更新时间：2026-05-17 21:02 CST

### 当前目标

把 Review & Export 从“有导出包预览”推进到“最终导出前必须通过显式核验门”。P2-Z 已完成；下一步按计划第 9 节执行 AI Research Pipeline MVP Review，对 P2-V 到 P2-Z 做完整回归、浏览器端到端验收和截图留档。

### 已完成事项

- 新增 BDD：`docs/architecture-v2/codex-phase-p2-verifier-export-gates-bdd.md`。
- 新增测试：`tests/test_verifier_export_gates.py`。
- 新增服务：`Product/backend/verifier_service.py`。
- 扩展 `Product/app.py`：新增 `GET /api/v1/projects/{project_id}/verifier-checks` 和 `POST /api/v1/projects/{project_id}/verifier-checks/run`。
- 扩展 `Product/web/index.html`：Review & Export 页面新增 `verifier-gate-panel`，放在审稿评分之后、导出包之前。
- 扩展 `Product/web/assets/app.js`：新增 verifier checks API、渲染、运行核验、状态翻译和 docx 最终导出禁用逻辑。
- 扩展 `Product/web/assets/styles.css`：新增 verifier gate 的摘要、状态、blocked/failed 视觉样式。
- 当前真实项目已生成 `state/product/verifier_checks.json` runtime artifact；该文件为本地运行状态，不提交。

### 已验证证据

- RED：`python3 -m unittest tests.test_verifier_export_gates -v` 首次失败，原因是 `/verifier-checks` API 404 和前端缺少 `verifier-gate-panel`。
- GREEN：`python3 -m unittest tests.test_verifier_export_gates -v`，5 tests OK。
- 相邻回归：`python3 -m unittest tests.test_verifier_export_gates tests.test_review_export_package tests.test_manuscript_consumption -v`，33 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，257 tests OK，skipped=1。
- 静态检查：`python3 -m py_compile Product/app.py Product/backend/verifier_service.py Product/backend/manuscript_candidate_service.py` 通过；`node --check Product/web/assets/app.js` 通过；`git diff --check` 通过。
- 浏览器验收：`http://127.0.0.1:8768/?v=20260517-p2z-verifier-gates` 显示 `导出核验门`；`rowCount=8`、`failedRows=1`、`hasResultBinding=true`、`hasDocxPreflight=true`、`finalExportDisabled=true`、`errors=[]`、`badResponses=[]`；截图 `/tmp/p2z-verifier-gates.png`。

### 关键文件路径

- `Product/backend/verifier_service.py`
- `Product/app.py`
- `Product/web/index.html`
- `Product/web/assets/app.js`
- `Product/web/assets/styles.css`
- `tests/test_verifier_export_gates.py`
- `docs/architecture-v2/codex-phase-p2-verifier-export-gates-bdd.md`
- `state/product/verifier_checks.json`：浏览器/API 验收时生成的本地运行状态，gitignored，不提交。
- `/tmp/p2z-verifier-gates.png`：浏览器自动化验收截图。

### 不能重复探索的结论

- `preview_ready` export package 不是最终导出 ready；它只证明有候选包和预览文件。
- 最终 docx 导出只能读取 `verifier_checks.can_export_docx`，不能从 candidate、preview 或 export manifest 是否存在推断。
- P2-Z 不直接生成 docx，也不覆盖 `Manuscripts/generated/paper_draft.md`；它只负责核验和阻断。
- 当前 `docx_export_preflight=blocked` 是正确产品状态，因为还没有真实最终 docx 产物和独立导出动作。

### 下一步第一件事

执行计划第 9 节 `Integration Milestone: AI Research Pipeline MVP Review`：完整回归、启动 8768、浏览器按 10 步端到端验收，并保存 `artifacts/ui-checks/pipeline-mvp-home.png`、`pipeline-mvp-data-variables.png`、`pipeline-mvp-execution.png`、`pipeline-mvp-review-export.png`。

### 未解决风险

- 真实 docx 生成仍未实现；P2-Z 只是把最终导出前的安全门立起来。
- verifier checks 与当前 export package 绑定；重新生成 finding、candidate 或 export package 后必须重新运行核验。
- DID/IV/RDD/PSM/DML 未来进入真实执行后，还需要方法族专用 verifier checks。
- 当前工作区还有非本轮改动：`README.md`、`Manuscripts/templates/README.md` 和 `Manuscripts/templates/华侨大学本科论文LaTeX模板_2026-05-17/`，不要在 P2-Z commit 中暂存或回滚。

## 2026-05-25 P2-AB Topic-first Auto Research CLI 交接增量

更新时间：2026-05-25 18:10 CST

### 当前目标

把本地高效工作流从“页面驱动状态机”推进到“题目优先 CLI 驱动的 Auto Research Run”。用户给一个研究题目后，系统先创建候选层研究运行包，记录可用能力、递归搜索计划、文献线索、变量候选、方法候选、证据缺口、研究报告和 exploratory 论文草稿。

### 已完成事项

- 新增 BDD：`docs/architecture-v2/codex-phase-p2-auto-research-cli-bdd.md`。
- 新增测试：`tests/test_auto_research_cli.py`。
- 新增服务：`Product/backend/auto_research_service.py`。
- 扩展 CLI：`Product/cli.py` 新增 `auto-research` 子命令。
- 扩展 registry/governance：未注册本地项目通过 transient runtime project 进入 identity、permission、capability、cost 服务，不写入 Product 全局项目 registry。
- 更新 durable notes：`Tasks/todo.md`、`Tasks/decision-log.md`、`Tasks/manifest.md`、`Tasks/review.md`。

### 已验证证据

- RED：`python3 -m unittest tests.test_auto_research_cli -v` 首次失败，原因是 `auto-research` 子命令不存在。
- GREEN：`python3 -m unittest tests.test_auto_research_cli -v`，1 test OK。
- 相邻回归：`python3 -m unittest tests.test_auto_research_cli tests.test_cli_workbench -v`，2 tests OK。
- 静态检查：`python3 -m py_compile Product/cli.py Product/backend/auto_research_service.py Product/backend/registry.py Product/backend/identity_service.py Product/backend/permission_service.py Product/backend/capability_registry.py Product/backend/cost_service.py` 通过。
- JS/格式检查：`node --check Product/web/assets/app.js` 通过；`git diff --check -- <本轮文件>` 通过。
- 手动 CLI 验收：`python3 Product/cli.py auto-research --topic "人工智能是否影响劳动收入差距" --mode auto --max-depth 2 --max-iterations 5` 返回 `status=completed`、`execution_policy=best_available`，运行目录 `workspace/runs/run_20260524T172441Z_c063b7`。
- 全量回归：`python3 -m unittest discover -s tests -v` 当前 17 failures，skipped=1；失败均为前端契约类测试，见 `Tasks/review.md`。

### 关键文件路径

- `Product/backend/auto_research_service.py`
- `Product/cli.py`
- `Product/backend/registry.py`
- `Product/backend/identity_service.py`
- `Product/backend/permission_service.py`
- `Product/backend/capability_registry.py`
- `Product/backend/cost_service.py`
- `tests/test_auto_research_cli.py`
- `docs/architecture-v2/codex-phase-p2-auto-research-cli-bdd.md`
- `workspace/runs/{run_id}/run_manifest.json`
- `state/orchestration/literature_clues.jsonl`

### 不能重复探索的结论

- Auto Research CLI 是候选层和草稿层生成器，不是正式层写回器。
- `execution_policy=best_available` 的意思是尽量使用当前机器可用能力；不可用能力必须写入 `capability_status`，不是伪装成功。
- CNKI 第一版只能作为文献线索候选，不能静默下载全文，不能成为正式证据。
- `agentmemory` 是可选 operation memory，不是 canonical state，也不是正式 evidence。
- 未注册本地项目不应写入 Product 全局 registry；CLI 临时项目用 transient runtime project 视图即可。

### 下一步第一件事

先修复当前 17 个前端契约失败，恢复全量测试绿线。之后再做 P2-AC：把 Auto Research 的 capability registry 与真实 StatsPAI function schema / CNKI assisted search / web literature search 接起来，让候选层从“本地扫描 + 探测”升级为“可审计外部搜索 + 可执行方法候选”。

### 未解决风险

- 当前 Auto Research 不会真正运行 StatsPAI 方法、CNKI 浏览器辅助检索或 LLM Supervisor 子任务，只记录能力状态和候选产物。
- 变量候选仍是字段名启发式，不能进入论文分析。
- 全量前端契约失败说明 UI 与历史 BDD 漂移；不应在未修复前继续声称产品前端完整可用。
- 本轮未 commit；工作树有大量既有改动和未跟踪文件，需要在提交前按文件范围审查。

## 2026-05-25 P3 React Input And Slide Tabs 交接增量

更新时间：2026-05-25 18:45 CST

### 当前目标

把用户明确喜欢的两个 UI 原型先落成项目内可运行组件：Claude-style 研究输入器与滑动阶段标签。第一版只使用黑白灰，先建立干净、克制、未来感的入口质感，不继续把所有功能模块铺满屏幕。

### 已完成事项

- 新增 `Product/web-react` React/Vite 独立前端，不覆盖旧 `Product/web`。
- 新增 `ResearchCommandInput`，支持研究题目输入、文件选择、拖拽上传、长文本粘贴预览、模式选择和提交状态。
- 新增 `SlideTabs`，支持任务书、递归搜索、数据变量、方法设计、执行实验五个阶段，支持 hover、点击和键盘方向键。
- 新增 `/react` FastAPI 预览入口，构建产物位于 `Product/web-dist`。
- 新增 P3 BDD 与测试，锁定“只做两个组件、黑白灰、独立构建、不删除旧前端”的边界。
- 根据用户反馈删除首屏解释性长句和“React 切片/不展开 Agent”防守性文案。
- 新增 `DottedSurface`，用 Three.js 点阵波面作为初始页背景，并把黑白灰对比降到柔和灰阶。

### 已验证证据

- RED：`python3 -m unittest tests.test_p3_react_input_tabs -v` 首次 5 failures，缺少 React 包、组件、样式和 App 入口。
- GREEN：`python3 -m unittest tests.test_p3_react_input_tabs -v`，5 tests OK。
- 反馈修正 GREEN：`python3 -m unittest tests.test_p3_react_input_tabs -v`，7 tests OK，覆盖无防守性文案、低对比灰阶和 DottedSurface。
- Build：`cd Product/web-react && npm run build`，Vite build 成功，输出 `Product/web-dist/index.html` 和 assets。
- 静态检查：`python3 -m py_compile Product/app.py` 通过；scoped `git diff --check` 通过。
- 浏览器验收：Playwright 打开 `http://127.0.0.1:8770/react`，`messages=[]`、`canvasPresent=true`、`hasDefensiveCopy=false`、`overflowX=false`。
- 全量回归：`python3 -m unittest discover -s tests -v`，287 tests OK，skipped=1。

### 关键文件路径

- `Product/web-react/src/components/ResearchCommandInput.tsx`
- `Product/web-react/src/components/SlideTabs.tsx`
- `Product/web-react/src/components/DottedSurface.tsx`
- `Product/web-react/src/App.tsx`
- `Product/web-react/src/styles.css`
- `Product/web-react/vite.config.ts`
- `Product/web-dist/index.html`
- `Product/app.py`
- `tests/test_p3_react_input_tabs.py`
- `docs/architecture-v2/codex-phase-p3-react-input-tabs-bdd.md`
- `artifacts/ui-checks/p3-react-input-tabs.png`
- `artifacts/ui-checks/p3-react-dotted-surface.png`

### 不能重复探索的结论

- 用户已经明确喜欢给出的 Claude 输入器和滑动标签风格；下一轮 UI 不要再把它泛化成普通 SaaS 或旧档案卡片堆。
- 本阶段只做两个 primitives；Agent Task Queue、右侧审计 Drawer、全模块重排必须等这两个入口被认可后再继续。
- 第一版 UI 只使用黑白灰；状态差异用明度、边框、阴影和动效表达。
- 首屏不要放内部解释和防守性边界说明；边界说明应在审阅/提交/正式写回动作发生时出现。
- 用户希望对比度约降到 76%，避免纯黑纯白刺眼效果。
- 旧 `Product/web` 暂时保留为回退；只有新 React 入口验收满意后再删除旧前端。

### 下一步第一件事

让用户打开或查看 `http://127.0.0.1:8769/react/` 的输入器和阶段标签。如果质感通过，再做 P3-B：右侧审计 Drawer，并把输入器提交后的草案任务连接到 drawer，而不是在主屏铺开。

### 未解决风险

- 当前 Chrome 用户 Profile 对 localhost 仍可能显示白屏；Playwright 和 HTTP 证明 `/react` 可渲染，疑似 Chrome 扩展/Profile 层干扰。
- `ResearchCommandInput` 目前只保留前端状态，不上传到后端，也不创建正式研究状态。
- `SlideTabs` 只切换前端阶段说明，尚未绑定旧产品 API 或 Agent Task Queue。

## 2026-05-25 P3-C Intake To Analysis Workspace 交接增量

更新时间：2026-05-25 19:30 CST

### 当前目标

把 React 新入口从“输入时直接显示分析卡”修正为“先干净输入，提交后进入分析工作台”。

### 已完成事项

- 入口页只显示标题和 ResearchCommandInput。
- 提交后进入 `analysis-workspace`。
- 分析页显示阶段导航和 5 张 SemanticGlowCards。
- 新增/修订 BDD 与测试。
- 补齐 React/Three 类型依赖并通过 `tsc --noEmit`。

### 已验证证据

- `python3 -m unittest tests.test_p3_semantic_glow_cards tests.test_p3_react_input_tabs -v`，12 tests OK。
- `cd Product/web-react && npx tsc --noEmit`，通过。
- `cd Product/web-react && npm run build`，通过；仍有 chunk >500KB 警告。
- Playwright：初始 `initialCards=0`、`initialStages=0`；提交后 `analysisCards=5`、`stagePanel=1`。

### 关键文件路径

- `Product/web-react/src/App.tsx`
- `Product/web-react/src/components/SemanticGlowCards.tsx`
- `Product/web-react/src/components/ResearchCommandInput.tsx`
- `Product/web-react/src/styles.css`
- `docs/architecture-v2/codex-phase-p3-semantic-glow-cards-bdd.md`
- `tests/test_p3_semantic_glow_cards.py`
- `artifacts/ui-checks/p3-intake-clean-v2.png`
- `artifacts/ui-checks/p3-analysis-workspace-glow-cards-v2.png`

### 不能重复探索的结论

- 语义卡不属于第一屏。
- 第一屏不是 dashboard，不展示阶段导航、审计面板、Agent 队列、证据日志或语义分析。
- 卡片属于提交后的分析阶段，并且仍是 draft-only。
- 用户给的 GlowCard 方向适合用于后续分析卡，而不是入口页装饰。

### 下一步第一件事

做 P3-D：把 `analysis-workspace` 拆成清晰阶段页面容器。每个阶段先定义 UI 规范，再接真实工作流。

### 未解决风险

- 当前语义分析是规则式 parser，不是 LLM Supervisor。
- 当前“页面”是 React state 切换，不是真正 route。
- 构建产物 JS chunk 仍超 500KB。
- 还没有创建正式 ResearchQuestion 或后端 TopicSession。

## 2026-05-25 P3-D Task Brief Demo 交接增量

更新时间：2026-05-25 20:05 CST

### 当前目标

支持 demo-driven grill-me：先给用户看“任务书 / 研究题目确认页”的低保真 Demo，再讨论这个板块的正式 UI contract。

### 已完成事项

- 新增 `TaskBriefDemo`。
- `App.tsx` 增加 `activeStage`，默认 `brief`。
- `brief` 阶段显示任务书主屏和右侧 Inspector。
- 非 `brief` 阶段显示现有 `SemanticGlowCards`。
- 新增 P3-D BDD 和测试。
- 生成验收截图 `artifacts/ui-checks/p3-task-brief-demo.png`。

### 已验证证据

- `python3 -m unittest tests.test_p3_task_brief_demo tests.test_p3_semantic_glow_cards tests.test_p3_react_input_tabs -v`，16 tests OK。
- `cd Product/web-react && npx tsc --noEmit`，通过。
- `cd Product/web-react && npm run build`，通过；仍有 chunk >500KB 警告。
- Playwright：提交后 `hasTaskBrief=true`、`decisions=5`、`inspectorSections=4`、`semanticCards=0`；切到递归搜索后 `semanticCardsAfterSwitch=5`。

### 下一步第一件事

围绕任务书页问用户第一个 grill-me 问题：右侧 Inspector 是固定栏、抽屉，还是点击信号后在右侧展开？

### 未解决风险

- Demo 只验证信息结构，不代表最终高保真视觉。
- 尚未接后端 TopicSession / ResearchQuestion。
- 右侧 Inspector 的交互形态还未最终确认。

## 2026-06-16 parent-education-wage 继续对接入口

更新时间：2026-06-16 13:41 CST

### 当前目标

继续把“父母受教育水平对子女工资收入的影响”按十步论文流水线跑下去。当前只完成 `01_design`，下一步是 `02_literature`。

### 已完成事项

- 根目录已生成 `research_design.md`、`causal_question.yaml`、`design_risk.md`。
- `Tasks/artifact-registry.md` 已登记 01 三项产物为 `present`。
- `python3 scripts/21_route_next_workflow.py` 已推进到 `NEXT 02_literature`。
- 修复运行时 artifact registry 路径大小写，统一为 `Tasks/artifact-registry.md`。
- BDD/TDD 已落地：`Tasks/parent-education-wage-01-design-bdd.md`、`tests/test_parent_education_wage_01_design_runtime.py`。

### 已验证证据

- `python3 -m pytest tests/test_parent_education_wage_01_design_runtime.py -q`，6 passed。
- `python3 scripts/25_agent_runtime_preflight.py`，PASS。
- `git diff --check`，PASS。
- Chrome 已打开 `artifacts/workflow_router_report.md`、`artifacts/agent_runtime_preflight_report.md`、`Tasks/parent-education-wage-01-design-bdd.md`。

### 下一步第一件事

执行 `02_literature`，生成：

- `litreview/query_plan.json`
- `litreview/literature_candidates.csv`
- `references.bib`
- `litreview/contribution_matrix.md`

### 未解决风险

- 旧 `Tasks/parent-education-wage/` 内有 fallback/stub 文献和串题变量，不能继续当作真实文献或真实变量。
- 当前还没有文献矩阵、PDF 慢读、数据门禁和估计结果。
- router 报告仍展示全局 workflow 缺口；后续可拆成当前题目缺口和全局模板缺口。
# 2026-06-17 P5 VariableRoleSet Draft Preflight Handoff

- 当前阶段：P5 已完成，等待 P6 人工签收/提升路径。
- 关键产物：`Results/json/parent_education_wage_p5_variable_role_preflight.json`、`Reviews/parent_education_wage_p5_variable_role_preflight.md`。
- 资源调研：`outputs/parent_education_wage_p5_resource_research.md` 与 `.provenance.md`。
- Product API：`GET/POST /api/v1/projects/{project_id}/product-control/p5-variable-role-preflight`。
- React 面板：`Product/web-react/src/components/ProductControlP0Panel.tsx` 中 `P5 VariableRoleSet`。
- 正式层边界：P5 未写 `state/product/variable_roles.json`、`state/product/design_spec.json`、`state/product/run_plan.json`，未创建 run id，未执行回归。
- 下一步只应做 P6 promotion/signoff，不应直接跑 OLS/DID/IV/DML。
# 2026-06-17 P6 Handoff

- 当前阶段：P6 人工签收/提升路径已完成第一版。
- 真实产物：`Results/json/parent_education_wage_p6_variable_role_signoff.json`、`Reviews/parent_education_wage_p6_variable_role_signoff.md`。
- 白话解释：P5 是“系统整理的变量方案草稿”；P6 是“把你点头确认这件事做成产品流程”。没有完整确认，不会提升；确认完整后先进入可编辑草稿，不会直接跑模型。
- 当前真实状态：`variable_role_signoff_required`，5 个签收项仍待人工确认；真实项目没有执行 promotion payload。
- 正式边界：未写正式 `state/product/variable_roles.json`、`state/product/design_spec.json`、`state/product/run_plan.json`；旧 `PUT /variable-roles` 在无 P6 promoted draft 时已被阻断；未创建 run id；未执行回归。
- 下一步：用户确认优先 CFPS 波次、父母教育构造、hukou 角色、outcome/control 后，调用 P6 promotion 到 editable draft，再走正式 VariableRoleSet 审批。
