# Review

## 2026-06-18 P13-P16 Demo Closure

### 行为覆盖

- [x] 行为 1：P13 归档旧机器人题目的活跃方法规格和运行计划，避免污染父母教育工资 Demo 线。
- [x] 行为 2：P13 用真实 CSV 表头校验 P12 公式，缺 `parent_education` 和 `experience` 时阻断运行计划。
- [x] 行为 3：P14 在 P13 阻断时不创建运行编号，不运行模型，只写执行证据账本。
- [x] 行为 4：P15 交付半成品论文路径和红标问题清单。
- [x] 行为 5：P16 生成用户验收包，并明确 `can_claim_complete_paper=false`。
- [x] 行为 6：仪表盘首屏先回答“现在能交付什么 / 还缺什么 / 下一步做什么”。
- [x] 行为 7：GET 在 P13-P16 未执行前不能凭空宣称 P16 已完成。
- [x] 行为 8：旧机器人题目的 P12 预检不能被改名成父母教育工资闭环。
- [x] 行为 9：字段齐全时，P14 必须先实际执行最小 OLS，才允许返回 run id。

### 测试覆盖

- SDD/BDD：`Tasks/parent-education-wage-p13-p16-demo-closure-bdd.md`。
- RED：`python3 -m pytest tests/test_parent_education_wage_p13_p16_demo_closure.py -q` 首次 3 failed，原因是 P13-P16 API 不存在，仪表盘没有三句话摘要。
- 防误报 RED：新增 GET-before-POST、stale P12、字段齐全必须真跑 OLS 三个边界测试后，`python3 -m pytest tests/test_parent_education_wage_p13_p16_demo_closure.py -q` 曾 3 failed，原因是旧实现会合成 P16、接收旧 P12、创建未执行 run id。
- 目标测试：`PYTHONDONTWRITEBYTECODE=1 python3 -m pytest tests/test_parent_education_wage_p13_p16_demo_closure.py tests/test_workflow_dashboard_artifact.py -q -p no:cacheprovider`，13 passed。
- 阶段回归：`PYTHONDONTWRITEBYTECODE=1 python3 -m pytest tests/test_parent_education_wage_p9_formal_variable_role_save.py tests/test_parent_education_wage_p10_product_control_ia.py tests/test_parent_education_wage_p11_source_metadata_contract.py tests/test_parent_education_wage_p12_design_tree.py tests/test_parent_education_wage_p12_design_spec_preflight.py tests/test_parent_education_wage_p13_p16_demo_closure.py tests/test_workflow_dashboard_artifact.py -q -p no:cacheprovider`，45 passed。
- Python 编译：P13-P16 service、workbench、`Product/app.py` 和 dashboard service 通过。
- React build：`cd Product/web-react && npm run build` 通过，保留既有 Vite chunk size warning。
- 浏览器 QA：`http://127.0.0.1:8780/workflow-dashboard` 桌面 1440px 和 390px 移动端均可见三句话结论、P16 当前门禁、P13 中文分支和“不伪造回归结果”；无横向溢出。

### 实现范围

- `Program/workbench/parent_education_wage_p13_p16_demo_closure.py`：新增 P13-P16 闭环器、P12 污染校验、GET not-run 状态和最小 OLS 执行器。
- `Product/backend/product_control_p13_p16_demo_closure_service.py`：新增 Product API 服务层。
- `Product/app.py`：新增 P13-P16 GET/POST 路由，并提供 `/workflow-dashboard-state.json` 作为仪表盘 JSON 兜底。
- `Results/json/parent_education_wage_p13_run_plan_approval.json`、`parent_education_wage_p14_execution_evidence_ledger.json`、`parent_education_wage_p15_draft_export_package.json`、`parent_education_wage_p16_user_acceptance_packet.json`：真实闭环产物。
- `Manuscripts/generated/parent_education_wage_p15_issue_list.md`：红标问题清单。
- `docs/product-control/workflow-dashboard.html`、`docs/product-control/workflow-dashboard-state.json`：控制台改为 P16 阻断交付视图，分支标题中文化。
- `tests/test_parent_education_wage_p13_p16_demo_closure.py`、`tests/test_parent_education_wage_p12_design_tree.py`、`tests/test_workflow_dashboard_artifact.py`：新增和更新 P13-P16 契约测试。
- `WORKFLOW_STATUS.md`、`Tasks/todo.md`、`Tasks/current-stage.md`、`Tasks/handoff.md`：同步当前阶段。

### 剩余风险

- 当前是 P16 阻断交付分支，不是完整论文成功分支。
- 真实 CSV 缺 `parent_education` 和 `experience`，补齐前不能运行父母教育工资模型。
- 当前本地服务为 `http://127.0.0.1:8780`；如重启服务，需要重新确认 API 和仪表盘状态。

## 2026-06-18 P12 DesignSpec Preflight

### 行为覆盖

- [x] 行为 1：没有 approved `state/product/variable_roles.json` 时，P12 阻断并要求先完成 P9-Human。
- [x] 行为 2：P9 已保存后，P12 生成可审阅候选 DesignSpec，包含研究问题、变量角色、baseline OLS 和公式。
- [x] 行为 3：方法清单区分 OLS 可预检、DID/IV/RDD 阻断、PSM/DML 候选预检。
- [x] 行为 4：P12 只写预检 JSON 和 Review，不写正式 DesignSpec/RunPlan，不创建 run id，不跑模型。
- [x] 行为 5：Product API 暴露 P12 GET/POST 当前状态和 no-model 边界。

### 测试覆盖

- SDD/BDD：`Tasks/parent-education-wage-p12-design-spec-preflight-bdd.md`。
- RED：`python3 -m pytest tests/test_parent_education_wage_p12_design_spec_preflight.py -q` 首次失败 4 项，原因是 P12 API/服务尚不存在。
- 目标测试：`python3 -m pytest tests/test_parent_education_wage_p12_design_spec_preflight.py -q`，4 passed。
- P12/dashboard 最小回归：`python3 -m pytest tests/test_parent_education_wage_p12_design_spec_preflight.py tests/test_parent_education_wage_p12_design_tree.py tests/test_workflow_dashboard_artifact.py -q`，14 passed。
- 阶段回归：`python3 -m pytest tests/test_parent_education_wage_p9_formal_variable_role_save.py tests/test_parent_education_wage_p10_product_control_ia.py tests/test_parent_education_wage_p11_source_metadata_contract.py tests/test_parent_education_wage_p12_design_tree.py tests/test_parent_education_wage_p12_design_spec_preflight.py tests/test_workflow_dashboard_artifact.py -q`，39 passed。
- Python 编译：P9/P12 services、P12 workbench、`Product/app.py` 和 dashboard service 编译通过。
- React build：`cd Product/web-react && npm run build` 通过，保留既有 Vite chunk size warning。
- API smoke：8779 当前代码服务下，P12 GET/POST 返回 `design_spec_preflight_ready_for_review`，并保持 `can_write_design_spec=false`、`can_create_run_id=false`、`can_execute_model=false`。
- 浏览器 QA：Browser plugin required `node_repl js` 入口未暴露，本轮回退普通 Playwright；8779 `/workflow-dashboard` 桌面 1440px 和移动端 390px 均无横向溢出、无 offscreen 元素、无相关 console error，截图为 `Product/output/playwright/workflow-dashboard-p12-design-spec-preflight-desktop.png`、`Product/output/playwright/workflow-dashboard-p12-design-spec-preflight-mobile.png`。

### 实现范围

- `Program/workbench/parent_education_wage_design_spec_preflight.py`：新增 P12 预检生成器。
- `Product/backend/product_control_p12_design_spec_preflight_service.py`：新增 Product API 服务层。
- `Product/app.py`：新增 P12 GET/POST 路由。
- `Results/json/parent_education_wage_p12_design_spec_preflight.json`：真实项目预检 JSON。
- `Reviews/parent_education_wage_p12_design_spec_preflight.md`：真实项目人工审阅报告。
- `docs/product-control/workflow-dashboard-state.json`、`docs/product-control/workflow-dashboard.html`、`Tasks/workflow-dashboard-bdd.md`：仪表盘推进到 P12 预检完成态。

### 剩余风险

- P12 预检不是正式 DesignSpec；下一步仍需 P13 RunPlan Approval。
- 不能创建 run id，不能运行模型，不能把预检草案冒充最终论文证据。

## 2026-06-18 P12-0 Design Tree / Pre-PRD

### 行为覆盖

- [x] 行为 1：P12-0 承接 P9 已保存状态，并只打开 P12 DesignSpec Preflight。
- [x] 行为 2：设计树覆盖 P12-P16，并写清验收标准、回退路径和停机条件。
- [x] 行为 3：仪表盘显示 `P12-0 设计树已完成`，并继续禁止 run id 和模型执行。

### 测试覆盖

- SDD/BDD：`Tasks/parent-education-wage-p12-0-design-tree-bdd.md`。
- RED：`python3 -m pytest tests/test_parent_education_wage_p12_design_tree.py -q`，3 failed；原因是 `docs/product-control/p12-p16-design-tree.md` 不存在，仪表盘状态仍为 `formal_variable_role_save_ready`。
- 目标测试：`python3 -m pytest tests/test_parent_education_wage_p12_design_tree.py tests/test_workflow_dashboard_artifact.py -q`，10 passed。

### 实现范围

- `docs/product-control/p12-p16-design-tree.md`：新增 P12-P16 设计树、验收、回退、停机条件和不允许改动范围。
- `docs/product-control/workflow-dashboard-state.json`：当前状态更新为 `p12_design_tree_ready`。
- `docs/product-control/workflow-dashboard.html`：静态 fallback 同步到 P12-0。
- `tests/test_parent_education_wage_p12_design_tree.py`：新增 P12-0 行为测试。
- `tests/test_workflow_dashboard_artifact.py`、`Tasks/workflow-dashboard-bdd.md`：仪表盘期望切到 P12-0。
- `WORKFLOW_STATUS.md`、`Tasks/todo.md`、`Tasks/current-stage.md`、`Tasks/handoff.md`：同步当前阶段。

### 剩余风险

- P12-0 不是 DesignSpec；下一阶段仍必须按 SDD/BDD/TDD 做 P12 DesignSpec Preflight。
- 当前仍不得创建 run id 或运行模型。

## 2026-06-18 P9H/P10 Mobile Gate Summary QA

### 行为覆盖

- [x] 行为 1：P9H 保存完成后，产品页当前门禁摘要在 390px 移动端不再重叠。
- [x] 行为 2：移动端仍显示 P9 已保存、不能进入正式论文、不能运行模型的边界。
- [x] 行为 3：该修复只改布局，不改 P9/P12 状态机，不创建 run id，不运行模型。

### 测试覆盖

- RED：`python3 -m pytest tests/test_parent_education_wage_p10_product_control_ia.py -q` 新增移动端单列契约后先失败 1 项，原因是 `.product-control-gate-summary` 在移动端仍保持多列。
- 目标测试：`python3 -m pytest tests/test_parent_education_wage_p10_product_control_ia.py -q`，5 passed。
- 阶段回归：`python3 -m pytest tests/test_parent_education_wage_p9_formal_variable_role_save.py tests/test_parent_education_wage_p10_product_control_ia.py tests/test_parent_education_wage_p11_source_metadata_contract.py tests/test_parent_education_wage_p12_design_tree.py tests/test_workflow_dashboard_artifact.py -q`，35 passed。
- React build：`cd Product/web-react && npm run build` 通过，保留既有 Vite chunk size warning。
- 浏览器 QA：`http://127.0.0.1:8777` 下，仪表盘和产品页的桌面 1440px、移动端 390px 均无横向溢出、无相关 console error；产品页移动端 `.product-control-gate-summary` 为单列且无重叠。

### 实现范围

- `Product/web-react/src/styles.css`：在 720px 以下把 `.product-control-gate-summary` 和阶段历史 summary 切到单列，避免状态清单挤压标题区。
- `tests/test_parent_education_wage_p10_product_control_ia.py`：新增 P9H/P10 移动端当前门禁布局契约。
- `Product/output/playwright/`：更新 P12-0 仪表盘和 P9H 产品页桌面/移动端截图。

### 剩余风险

- 产品页仍是工程工作台，不是 CEO 仪表盘；给管理层看的主入口是 `/workflow-dashboard`。
- Browser 插件 JS 运行入口当前不可用，本轮使用本地 Playwright 作为可视化 QA 回退路径。

## 2026-06-18 P9H Formal Save Completion

### 行为覆盖

- [x] 行为 1：P9-Human 把已批准、已签收 source contract 的角色写入正式 `state/product/variable_roles.json`。
- [x] 行为 2：P9 POST 成功后，后续 GET 显示 `formal_variable_roles_saved`，不再提示重复保存。
- [x] 行为 3：P9H 解锁 P12 DesignSpec Preflight，但仍禁止创建 run id 和模型执行。

### 测试覆盖

- SDD/BDD：`Tasks/parent-education-wage-p9h-formal-save-completion-bdd.md`。
- RED：`python3 -m pytest tests/test_parent_education_wage_p9_formal_variable_role_save.py -q` 新增 P9H 完成态回归后先失败 1 项，原因是 GET 仍返回 `formal_variable_role_save_ready`。
- 目标测试：`python3 -m pytest tests/test_parent_education_wage_p9_formal_variable_role_save.py -q`，7 passed。
- 邻近回归：`python3 -m pytest tests/test_parent_education_wage_p9_formal_variable_role_save.py tests/test_parent_education_wage_p10_product_control_ia.py tests/test_parent_education_wage_p11_source_metadata_contract.py tests/test_workflow_dashboard_artifact.py -q`，31 passed。

### 实现范围

- `Product/backend/product_control_p9_variable_role_save_service.py`：新增 formal role set 完成态识别，避免保存后继续提示 ready。
- `tests/test_parent_education_wage_p9_formal_variable_role_save.py`：新增 POST 后 re-GET 完成态断言。
- `Tasks/parent-education-wage-p9h-formal-save-completion-bdd.md`：记录 P9H 完成态行为。
- `state/product/variable_roles.json`：真实项目正式变量角色已保存。

### 剩余风险

- P9H 只保存正式变量角色；没有写 DesignSpec/RunPlan，没有创建 run id，没有运行模型。
- 8776 旧服务进程可能仍加载旧代码；当前代码验收应使用 8777 或重启服务。

## 2026-06-18 P11H Source Contract Saved Next-Step

### 行为覆盖

- [x] 行为 1：P11-Human 真实保存 source contract 后，页面显示 `P11 已签收` 和 `已解锁 P9 正式变量表保存`。
- [x] 行为 2：页面把下一步限定为 `下一步：回到 P9 正式保存`，不引导进入 P12。
- [x] 行为 3：页面继续显示 `仍不能进入 P12`、`仍不能创建 run id`、`仍不能运行模型`。
- [x] 行为 4：P11H 不写正式 VariableRoleSet、DesignSpec、RunPlan、run id 或模型结果。

### 测试覆盖

- SDD/BDD：`Tasks/parent-education-wage-p11h-source-contract-saved-next-step-bdd.md`。
- RED：`python3 -m pytest tests/test_parent_education_wage_p11_source_metadata_contract.py -q` 新增 P11H React 契约后先失败 1 项，原因是 React 尚未暴露 `sourceContractSaved` 和 saved next-step panel。
- 目标测试：`python3 -m pytest tests/test_parent_education_wage_p11_source_metadata_contract.py -q`，13 passed。
- P9/P10/P11 邻近回归：`python3 -m pytest tests/test_parent_education_wage_p9_formal_variable_role_save.py tests/test_parent_education_wage_p10_product_control_ia.py tests/test_parent_education_wage_p11_source_metadata_contract.py -q`，24 passed。
- React build：`cd Product/web-react && npm run build` 通过，保留既有 Vite chunk size warning。
- 真实保存验收：8776 真实页面已保存 `Data/Final/cfps_robot_reallocation.csv`、reviewer/note、9 个字段来源、逐行 human confirmation 和 `max(father_education, mother_education)` construction。
- API smoke：P11 返回 `source_metadata_contract_ready_for_p9_save`、missing fields 为空、`can_return_to_p9_formal_save=true`、`can_execute_model=false`；P9 返回 `formal_variable_role_save_ready`、`can_save_formal_variable_roles=true`、`can_enter_design_spec_preflight=false`、`can_create_run_id=false`、`can_execute_model=false`。
- 浏览器 smoke：8776 真实入口桌面和 390px 移动端均显示 P11 已签收、P9 已解锁、9/9 fields、missing none、no P12/run/model；horizontalOverflow=false、offscreenCount=0、console messages=0。截图为 `Product/output/playwright/product-control-p11h-saved-next-step-final2-desktop.png`、`Product/output/playwright/product-control-p11h-saved-next-step-final2-mobile.png`。

### 实现范围

- `Tasks/parent-education-wage-p11h-source-contract-saved-next-step-bdd.md`：P11H SDD/BDD。
- `tests/test_parent_education_wage_p11_source_metadata_contract.py`：新增 P11H React 契约测试。
- `Product/web-react/src/components/ProductControlP0Panel.tsx`：新增 saved source contract 状态、review rehydrate、9/9 source row 状态和 P9 next-step panel。
- `Product/web-react/src/styles.css`：新增 P11 saved next-step panel 样式，并修复移动端 locked tab strip 横向溢出。
- `WORKFLOW_STATUS.md`、`Tasks/todo.md`、`Tasks/current-stage.md`、`Tasks/handoff.md`、`docs/product-control/workflow-dashboard-state.json`：同步 P11H 完成和 P9 当前门禁。

### 剩余风险

- P11H 只完成 source contract 签收，不等于已写正式变量表。
- 当前下一步是 P9-Human 正式保存；P9 成功前不能开始 P12-0、P12、RunPlan、run id 或模型执行。

## 2026-06-18 Workflow Dashboard

### 行为覆盖

- [x] 行为 1：仪表盘显示 `追问 -> 调研 -> 原型 -> 规格 -> 拆任务 -> 实现 -> 复核` 七阶段，并标注当前 `实现 / 复核` 与下一步 `P9 / 设计树`。
- [x] 行为 2：仪表盘首屏提供 CEO 摘要，显示 `老板先看这里`、项目目标、当前结论、需要老板判断和下一步动作。
- [x] 行为 3：仪表盘显示 `P11 已签收`、`P9 正式变量表保存`、`需要人工保存正式变量表`、`P12 暂停` 和 `不运行模型`；机器错误码只保留在状态 JSON，不作为主界面文案。
- [x] 行为 4：仪表盘显示 P9 正式保存 -> P12-0 设计树 -> P16 用户验收的分支树，并明确回退路径和禁止跳到运行编号。
- [x] 行为 5：仪表盘提供中文人工验收清单，并从 `docs/product-control/README.md` 可发现。
- [x] 行为 6：仪表盘从 `docs/product-control/workflow-dashboard-state.json` 轮询渲染，HTML 不再是唯一状态源。
- [x] 行为 7：FastAPI 提供 `/workflow-dashboard` 和 `/api/v1/workflow-dashboard/state`，状态 API 禁用缓存。

### 测试覆盖

- SDD/BDD：`Tasks/workflow-dashboard-bdd.md`。
- RED：`python3 -m pytest tests/test_workflow_dashboard_artifact.py -q` 新增动态状态测试后先失败 6 项，原因是 `docs/product-control/workflow-dashboard-state.json` 尚不存在，FastAPI 动态入口也未实现。
- 目标测试：`python3 -m pytest tests/test_workflow_dashboard_artifact.py -q`，6 passed。
- 中文化 RED：`python3 -m pytest tests/test_workflow_dashboard_artifact.py -q` 在旧英文 fallback 和旧状态 JSON 下失败 6 项；随后把用户可见文案改为中文，机器错误码只保留在状态 JSON。
- 中文化目标测试：`python3 -m pytest tests/test_workflow_dashboard_artifact.py -q`，6 passed。
- CEO 摘要 RED：`python3 -m pytest tests/test_workflow_dashboard_artifact.py -q` 先失败 1 项，原因是页面和状态 JSON 还没有 `老板先看这里` 摘要层；实现后目标测试扩展为 7 passed。
- 浏览器 smoke：`http://127.0.0.1:8788/workflow-dashboard` 桌面和 390px 移动端均请求 `/api/v1/workflow-dashboard/state`，状态响应 200 且 `Cache-Control: no-store`；页面 H1 为 `论文生产流水线控制台`，CEO 摘要可见，旧英文状态未出现，offscreen elements=0，移动端 bodyScrollWidth=390。截图为 `Product/output/playwright/workflow-dashboard-desktop-ceo.png`、`Product/output/playwright/workflow-dashboard-mobile-ceo.png`。

### 实现范围

- `docs/product-control/workflow-dashboard.html`：改为动态轮询渲染的项目控制仪表盘，保留静态 fallback。
- `docs/product-control/workflow-dashboard-state.json`：新增仪表盘机器可读状态源。
- `Product/backend/workflow_dashboard_service.py`：新增状态 JSON 读取服务。
- `Product/app.py`：新增 `/workflow-dashboard` 页面路由和 `/api/v1/workflow-dashboard/state` 状态 API。
- `docs/product-control/README.md`：把工作流仪表盘加入产品控制文档阅读顺序。
- `tests/test_workflow_dashboard_artifact.py`：新增仪表盘契约测试。
- `Tasks/workflow-dashboard-bdd.md`：新增仪表盘 BDD。
- `WORKFLOW_STATUS.md`、`Tasks/todo.md`、`Tasks/handoff.md`：同步控制面状态。

### 剩余风险

- 当前仪表盘采用短轮询，不是 WebSocket/SSE push；阶段变化时仍需要更新 `workflow-dashboard-state.json`。
- 该仪表盘不替用户完成 P9-Human，也不解锁 P12/RunPlan/model。

## 2026-06-18 P11G Source Contract Signoff Workspace

### 行为覆盖

- [x] 行为 1：P11 当前门禁详情显示 `Source Contract Signoff` 工作台，而不是直接把用户丢进长表单。
- [x] 行为 2：工作台把 `Review queue` 和 `Source contract form` 分成左右两栏；用户先看字段队列，再填写 source contract。
- [x] 行为 3：底部 action bar 明确 `No model run`，保存按钮在 source metadata 缺口存在时继续 disabled。
- [x] 行为 4：P11G 不新增正式 VariableRoleSet、DesignSpec、RunPlan、run id 或模型执行入口。

### 测试覆盖

- SDD/BDD：`Tasks/parent-education-wage-p11g-source-contract-signoff-workspace-bdd.md`。
- RED：`python3 -m pytest tests/test_parent_education_wage_p11_source_metadata_contract.py -q` 新增 P11G React 契约测试后先失败 1 项，原因是 `Source Contract Signoff` workspace 尚不存在。
- 目标测试：`python3 -m pytest tests/test_parent_education_wage_p11_source_metadata_contract.py -q`，12 passed。
- P9/P10/P11 邻近回归：`python3 -m pytest tests/test_parent_education_wage_p9_formal_variable_role_save.py tests/test_parent_education_wage_p10_product_control_ia.py tests/test_parent_education_wage_p11_source_metadata_contract.py -q`，23 passed。
- P2-P11 scoped 回归：`python3 -m pytest tests/test_parent_education_wage_p2_execution_readiness.py tests/test_parent_education_wage_p3_draft_package.py tests/test_parent_education_wage_p4_field_source_candidates.py tests/test_parent_education_wage_p5_variable_role_preflight.py tests/test_parent_education_wage_p6_variable_role_signoff.py tests/test_parent_education_wage_p8_formal_variable_role_approval.py tests/test_parent_education_wage_p9_formal_variable_role_save.py tests/test_parent_education_wage_p10_product_control_ia.py tests/test_parent_education_wage_p11_source_metadata_contract.py -q`，61 passed。
- React build：`cd Product/web-react && npm run build` 通过，保留既有 Vite chunk size warning。
- 浏览器 smoke：8776 真实入口桌面和 390px 移动端均有 `Source Contract Signoff`、`Review queue`、`Source contract form`、9 个 queue items、9 个 source rows、9 个 checkbox、disabled 保存按钮和 `No model run`；P11G 自身 horizontal overflow=false，action bar 不遮挡字段行。截图为 `Product/output/playwright/product-control-p11g-signoff-workspace-final-desktop.png`、`Product/output/playwright/product-control-p11g-signoff-workspace-final-mobile.png`。
- 独立审查：code-reviewer Agent `Socrates` PASS；未发现 P11-Human/P9/P12 绕过、保存门禁绕过、CSS 全局污染或文档状态误报。

### 实现范围

- `Tasks/parent-education-wage-p11g-source-contract-signoff-workspace-bdd.md`：P11G SDD/BDD。
- `tests/test_parent_education_wage_p11_source_metadata_contract.py`：新增 P11G React 契约测试。
- `Product/web-react/src/components/ProductControlP0Panel.tsx`：重组 P11 为状态条、review queue、source contract form、折叠 review kit 和 action bar。
- `Product/web-react/src/styles.css`：新增 P11G 工作台、两栏布局、状态条、form pane、review pane、action bar 和移动端样式。
- `WORKFLOW_STATUS.md`、`Tasks/todo.md`、`Tasks/current-stage.md`、`Tasks/handoff.md`：同步 P11G 阶段状态。

### 剩余风险

- P11G 只把 P11-Human 做成可用 UI，不替用户判断真实 CFPS 波次、父母教育构造、hukou 角色或控制变量口径。
- 真实 source contract 仍未保存；P9 继续阻断是正确状态。
- P11G 目标测试仍偏静态字符串契约；当前用浏览器 smoke 弥补，后续可补 Playwright/DOM 自动断言，把 disabled save、no-model 和 390px 无横向溢出纳入自动测试。
- 390px 移动端 P11G 自身无横向溢出，但页面下方旧 locked tab strip 仍被浏览器检测为 offscreen；不影响本阶段工作台使用，后续应作为全局移动端清理项。
- P12 仍必须等 P11-Human 和 P9 正式 VariableRoleSet 保存成功后再开始。

## 2026-06-18 P11F Human Signoff Review Queue

### 行为覆盖

- [x] 行为 1：P11 source metadata 表单前显示 `Human signoff review queue`，用户先看到审核队列，再进入长表单。
- [x] 行为 2：队列覆盖 9 个 required source fields，并逐项显示字段名、status、missing items 和 action。
- [x] 行为 3：预填候选值不会自动变成人工签收；未勾选 human confirmation 的行仍显示 `ready_for_human_confirmation`，而不是 `confirmed_source_row`。
- [x] 行为 4：P11F 不新增正式 VariableRoleSet、DesignSpec、RunPlan、run id 或模型执行入口。

### 测试覆盖

- SDD/BDD：`Tasks/parent-education-wage-p11f-human-signoff-review-queue-bdd.md`。
- RED：`python3 -m pytest tests/test_parent_education_wage_p11_source_metadata_contract.py -q` 新增 P11F React 契约测试后先失败 1 项，原因是 review queue 尚不存在。
- 目标测试：`python3 -m pytest tests/test_parent_education_wage_p11_source_metadata_contract.py -q`，11 passed。
- P9/P10/P11 邻近回归：`python3 -m pytest tests/test_parent_education_wage_p9_formal_variable_role_save.py tests/test_parent_education_wage_p10_product_control_ia.py tests/test_parent_education_wage_p11_source_metadata_contract.py -q`，22 passed。
- P2-P11 scoped 回归：`python3 -m pytest tests/test_parent_education_wage_p2_execution_readiness.py tests/test_parent_education_wage_p3_draft_package.py tests/test_parent_education_wage_p4_field_source_candidates.py tests/test_parent_education_wage_p5_variable_role_preflight.py tests/test_parent_education_wage_p6_variable_role_signoff.py tests/test_parent_education_wage_p8_formal_variable_role_approval.py tests/test_parent_education_wage_p9_formal_variable_role_save.py tests/test_parent_education_wage_p10_product_control_ia.py tests/test_parent_education_wage_p11_source_metadata_contract.py -q`，60 passed。
- React build：`cd Product/web-react && npm run build` 通过，保留既有 Vite chunk size warning。
- API smoke：8776 当前代码服务上，P11 返回 `source_metadata_contract_required`；正式层边界仍为 `can_save_formal_variable_roles=false`、`can_enter_design_spec_preflight=false`、`can_create_run_id=false`、`can_execute_model=false`。
- 浏览器 smoke：8776 真实入口桌面和 390px 移动端均有 review queue；queue items=9、source rows=9、row fields=36、checkboxes=9、保存按钮 disabled、readiness 包含 `human_confirmation`；页面级 horizontal overflow=false；console errors=0；截图为 `Product/output/playwright/product-control-p11f-review-queue-desktop.png`、`Product/output/playwright/product-control-p11f-review-queue-mobile.png`。

### 实现范围

- `Tasks/parent-education-wage-p11f-human-signoff-review-queue-bdd.md`：P11F SDD/BDD。
- `tests/test_parent_education_wage_p11_source_metadata_contract.py`：新增 P11F React 契约测试。
- `Product/web-react/src/components/ProductControlP0Panel.tsx`：新增 source row review item/status/missing/action 计算，并在 P11 长表单前渲染审核队列。
- `Product/web-react/src/styles.css`：新增审核队列桌面/移动端样式。
- `WORKFLOW_STATUS.md`、`Tasks/todo.md`、`Tasks/current-stage.md`、`Tasks/handoff.md`：同步 P11F 阶段状态。

### 剩余风险

- P11F 只是签收体验改进，不替用户判断 CFPS 波次、父母教育构造、hukou 角色或控制变量口径。
- 真实 source contract 仍未保存；P9 继续阻断是正确状态。
- 本轮尝试派出独立 code-reviewer Agent，但当前会话 subagent thread 已满，未能启动；后续进入 P11-Human/P9 前应再次做独立审查。
- P11 页面仍是长表单；后续 P11-Human 需要真实人工签收，之后才能回到 P9。
- P12 仍必须等 P11-Human 和 P9 正式 VariableRoleSet 保存成功后再开始。

## 2026-06-18 P11E Human Signoff Readable Rows

### 行为覆盖

- [x] 行为 1：每个 P11 source row 的四个输入框都有可见标签：`dataset column`、`source field`、`source path`、`evidence level`。
- [x] 行为 2：390px 移动端隐藏表头后，字段行仍能靠行内标签读懂，不需要横向滚动页面。
- [x] 行为 3：行内标签不会替代人工确认；9 个 source rows 仍各自需要 human confirmation checkbox。
- [x] 行为 4：P11E 不新增正式 VariableRoleSet、DesignSpec、RunPlan、run id 或模型执行入口。

### 测试覆盖

- SDD/BDD：`Tasks/parent-education-wage-p11e-human-signoff-readable-rows-bdd.md`。
- RED：`python3 -m pytest tests/test_parent_education_wage_p11_source_metadata_contract.py -q` 新增 P11E React 契约测试后先失败 1 项，原因是 row field labels 尚不存在。
- 目标测试：`python3 -m pytest tests/test_parent_education_wage_p11_source_metadata_contract.py -q`，10 passed。
- P9/P10/P11 邻近回归：`python3 -m pytest tests/test_parent_education_wage_p9_formal_variable_role_save.py tests/test_parent_education_wage_p10_product_control_ia.py tests/test_parent_education_wage_p11_source_metadata_contract.py -q`，21 passed。
- P2-P11 scoped 回归：`python3 -m pytest tests/test_parent_education_wage_p2_execution_readiness.py tests/test_parent_education_wage_p3_draft_package.py tests/test_parent_education_wage_p4_field_source_candidates.py tests/test_parent_education_wage_p5_variable_role_preflight.py tests/test_parent_education_wage_p6_variable_role_signoff.py tests/test_parent_education_wage_p8_formal_variable_role_approval.py tests/test_parent_education_wage_p9_formal_variable_role_save.py tests/test_parent_education_wage_p10_product_control_ia.py tests/test_parent_education_wage_p11_source_metadata_contract.py -q`，59 passed。
- React build：`cd Product/web-react && npm run build` 通过，保留既有 Vite chunk size warning。
- API smoke：8776 当前代码服务上，P11 返回 `source_metadata_contract_required`；P9 仍返回 `blocked_missing_dataset_source_metadata`，`can_enter_design_spec_preflight=false`，`can_create_run_id=false`，`can_execute_model=false`。
- 浏览器 smoke：8776 真实入口桌面和 390px 移动端均有 9 个 source rows、36 个可见字段标签、9 个 row human confirmation checkbox、disabled 保存按钮和 `human_confirmation` readiness 缺口；页面级 horizontal overflow=false；console errors=0；截图为 `Product/output/playwright/product-control-p11e-readable-rows-desktop.png`、`Product/output/playwright/product-control-p11e-readable-rows-mobile.png`。

### 实现范围

- `Tasks/parent-education-wage-p11e-human-signoff-readable-rows-bdd.md`：P11E SDD/BDD。
- `tests/test_parent_education_wage_p11_source_metadata_contract.py`：新增 P11E React 契约测试。
- `Product/web-react/src/components/ProductControlP0Panel.tsx`：给 P11 row inputs 增加可见 label wrapper，并保留原 checkbox 门禁。
- `Product/web-react/src/styles.css`：新增 P11 row label 样式，修复 P11 移动端单列布局和阶段 tab 页面级横向溢出。
- `WORKFLOW_STATUS.md`、`Tasks/todo.md`、`Tasks/current-stage.md`、`Tasks/handoff.md`：同步 P11E 阶段状态。

### 剩余风险

- P11E 只解决“看得懂字段行”和移动端不溢出，不替用户判断 CFPS 波次、父母教育构造、hukou 角色或控制变量口径。
- P11 页面仍偏长；后续应把 P11-Human/P12 前的签收体验拆成更像审核队列的步骤。
- 本轮尝试派出独立 code-reviewer Agent，但当前会话 subagent thread 已满，未能启动；后续进入 P11-Human/P9 前应再次做独立审查。
- P12 仍必须等 P11-Human 和 P9 正式 VariableRoleSet 保存成功后再开始。

## 2026-06-18 P11D Row Human Confirmation Gate

### 行为覆盖

- [x] 行为 1：P11 逐字段来源行显示人工确认 checkbox，候选预填不会自动算作已签收。
- [x] 行为 2：`Source contract readiness` 把未勾选的字段行列为 `<field>:human_confirmation` 缺口。
- [x] 行为 3：只要 reviewer、note、dataset/source 字段或逐行确认缺口仍存在，`保存 source contract` 按钮保持禁用。
- [x] 行为 4：P11D 不新增正式 VariableRoleSet、DesignSpec、RunPlan、run id 或模型执行入口。

### 测试覆盖

- SDD/BDD：`Tasks/parent-education-wage-p11d-row-human-confirmation-bdd.md`。
- RED：`python3 -m pytest tests/test_parent_education_wage_p11_source_metadata_contract.py -q` 新增 P11D React 契约测试后先失败 1 项，原因是 row human confirmation 尚不存在。
- 目标测试：`python3 -m pytest tests/test_parent_education_wage_p11_source_metadata_contract.py -q`，9 passed。
- P9/P10/P11 邻近回归：`python3 -m pytest tests/test_parent_education_wage_p9_formal_variable_role_save.py tests/test_parent_education_wage_p10_product_control_ia.py tests/test_parent_education_wage_p11_source_metadata_contract.py -q`，20 passed。
- P2-P11 scoped 回归：`python3 -m pytest tests/test_parent_education_wage_p2_execution_readiness.py tests/test_parent_education_wage_p3_draft_package.py tests/test_parent_education_wage_p4_field_source_candidates.py tests/test_parent_education_wage_p5_variable_role_preflight.py tests/test_parent_education_wage_p6_variable_role_signoff.py tests/test_parent_education_wage_p7_variable_role_signoff_ui.py tests/test_parent_education_wage_p8_formal_variable_role_approval.py tests/test_parent_education_wage_p9_formal_variable_role_save.py tests/test_parent_education_wage_p10_product_control_ia.py tests/test_parent_education_wage_p11_source_metadata_contract.py -q`，61 passed。
- React build：`cd Product/web-react && npm run build` 通过，保留既有 Vite chunk size warning。
- API smoke：8774 当前代码服务上，P11 返回 `source_metadata_contract_required`；P9 仍返回 `blocked_missing_dataset_source_metadata`，`can_enter_design_spec_preflight=false`，`can_create_run_id=false`，`can_execute_model=false`。
- 浏览器 smoke：8774 真实入口桌面和 390px 移动端均有 9 个 source rows、9 个 row human confirmation checkbox、disabled 保存按钮和 `human_confirmation` readiness 缺口；console errors=0；截图为 `Product/output/playwright/product-control-p11d-row-confirmation-desktop.png`、`Product/output/playwright/product-control-p11d-row-confirmation-mobile.png`。

### 实现范围

- `Tasks/parent-education-wage-p11d-row-human-confirmation-bdd.md`：P11D SDD/BDD。
- `tests/test_parent_education_wage_p11_source_metadata_contract.py`：新增 P11D React 契约测试。
- `Product/web-react/src/components/ProductControlP0Panel.tsx`：新增 `confirmed` row state、`handleP11SourceFieldRowConfirmChange`、`confirmedSourceFieldRows`、`human_confirmation` readiness 缺口和 checkbox UI。
- `Product/web-react/src/styles.css`：扩展 P11 字段表格列和 checkbox 样式。
- `WORKFLOW_STATUS.md`、`Tasks/todo.md`、`Tasks/current-stage.md`、`Tasks/handoff.md`：同步 P11D 阶段状态。

### 剩余风险

- P11D 只是前端显式确认门禁，不替用户判断字段口径是否学术上正确。
- 桌面和移动端没有重叠，但 P11 表单仍偏长；后续 UX 阶段应继续收敛字段确认体验。
- 本轮尝试派出独立 code-reviewer Agent，但当前会话 subagent thread 已满，未能启动；后续进入 P11-Human/P9 前应再次做独立审查。
- P12 仍必须等 P11-Human 和 P9 正式 VariableRoleSet 保存成功后再开始。

## 2026-06-18 P11C Source Contract Readiness Check

### 行为覆盖

- [x] 行为 1：P11 表单显示 `Source contract readiness`，并给出 `needs_source_metadata_review` 或 `ready_to_save_source_contract`。
- [x] 行为 2：readiness check 会列出具体缺口，包括 reviewer、note、confirmation、dataset path、parent education construction，以及每个 source row 的 dataset/source/path/evidence 缺口。
- [x] 行为 3：缺口存在时 `保存 source contract` 按钮禁用，避免把明显不完整的 source contract 交给后端 409。
- [x] 行为 4：P11C 不新增正式 VariableRoleSet、DesignSpec、RunPlan、run id 或模型执行入口。

### 测试覆盖

- SDD/BDD：`Tasks/parent-education-wage-p11c-source-contract-readiness-bdd.md`。
- RED：`python3 -m pytest tests/test_parent_education_wage_p11_source_metadata_contract.py -q` 新增 P11C React 契约测试后先失败 1 项，原因是 readiness check 尚不存在。
- 目标测试：`python3 -m pytest tests/test_parent_education_wage_p11_source_metadata_contract.py -q`，8 passed。
- P9/P10/P11 邻近回归：`python3 -m pytest tests/test_parent_education_wage_p9_formal_variable_role_save.py tests/test_parent_education_wage_p10_product_control_ia.py tests/test_parent_education_wage_p11_source_metadata_contract.py -q`，19 passed。
- P2-P11 scoped 回归：`python3 -m pytest tests/test_parent_education_wage_p2_execution_readiness.py tests/test_parent_education_wage_p3_draft_package.py tests/test_parent_education_wage_p4_field_source_candidates.py tests/test_parent_education_wage_p5_variable_role_preflight.py tests/test_parent_education_wage_p6_variable_role_signoff.py tests/test_parent_education_wage_p7_variable_role_signoff_ui.py tests/test_parent_education_wage_p8_formal_variable_role_approval.py tests/test_parent_education_wage_p9_formal_variable_role_save.py tests/test_parent_education_wage_p10_product_control_ia.py tests/test_parent_education_wage_p11_source_metadata_contract.py -q`，60 passed。
- React build：`cd Product/web-react && npm run build` 通过，保留既有 Vite chunk size warning。
- API smoke：8773 当前代码服务上，P11 返回 `source_metadata_contract_required`；P9 仍返回 `blocked_missing_dataset_source_metadata`，`can_create_run_id=false`，`can_execute_model=false`。
- 浏览器 smoke：8773 真实入口桌面和 390px 移动端均可见 `Source contract readiness`、`needs_source_metadata_review` 和 9 个 source rows；保存按钮 disabled；console errors=0；截图为 `Product/output/playwright/product-control-p11c-readiness-desktop.png`、`Product/output/playwright/product-control-p11c-readiness-mobile.png`。

### 实现范围

- `Tasks/parent-education-wage-p11c-source-contract-readiness-bdd.md`：P11C SDD/BDD。
- `tests/test_parent_education_wage_p11_source_metadata_contract.py`：新增 P11C React 契约测试。
- `Product/web-react/src/components/ProductControlP0Panel.tsx`：新增 `p11SourceContractMissingItems`、`p11ReadinessMissingItems`、`p11SourceContractReady` 和 readiness 状态区；保存按钮改由 readiness 统一门禁。
- `Product/web-react/src/styles.css`：新增 readiness 状态区桌面/移动端样式。
- `WORKFLOW_STATUS.md`、`Tasks/todo.md`、`Tasks/current-stage.md`、`Tasks/handoff.md`：同步 P11C 阶段状态。

### 剩余风险

- P11C 只做前端保存前自检，不替用户决定真实字段来源或保存真实 source contract。
- 当前真实项目仍缺人工 reviewer/note 签收，P9 仍应阻断在 `blocked_missing_dataset_source_metadata`。
- P12 仍必须等 P11-Human 和 P9 正式 VariableRoleSet 保存成功后再开始。

## 2026-06-18 P11B Per-Field Source Confirmation Editor

### 行为覆盖

- [x] 行为 1：P11 页面从 `source_contract_review_kit.field_review_items` 和 required source fields 生成 9 个可编辑 source rows。
- [x] 行为 2：用户编辑 dataset column、source field、source path、evidence level 后，保存时由 `sourceFieldRows` 构造原有 P11 `field_bindings` payload。
- [x] 行为 3：`field_bindings JSON preview` 只作为预览和兜底，不再是本科生用户的主操作入口。
- [x] 行为 4：P11B 不新增模型执行、正式 VariableRoleSet 写入、DesignSpec、RunPlan 或 run id 入口。

### 测试覆盖

- SDD/BDD：`Tasks/parent-education-wage-p11b-per-field-source-confirmation-bdd.md`。
- RED：`python3 -m pytest tests/test_parent_education_wage_p11_source_metadata_contract.py -q` 新增 P11B React 契约测试后先失败 1 项，原因是 per-field editor 尚不存在。
- 目标测试：`python3 -m pytest tests/test_parent_education_wage_p11_source_metadata_contract.py -q`，7 passed。
- P9/P10/P11 邻近回归：`python3 -m pytest tests/test_parent_education_wage_p9_formal_variable_role_save.py tests/test_parent_education_wage_p10_product_control_ia.py tests/test_parent_education_wage_p11_source_metadata_contract.py -q`，18 passed。
- P2-P11 scoped 回归：`python3 -m pytest tests/test_parent_education_wage_p2_execution_readiness.py tests/test_parent_education_wage_p3_draft_package.py tests/test_parent_education_wage_p4_field_source_candidates.py tests/test_parent_education_wage_p5_variable_role_preflight.py tests/test_parent_education_wage_p6_variable_role_signoff.py tests/test_parent_education_wage_p7_variable_role_signoff_ui.py tests/test_parent_education_wage_p8_formal_variable_role_approval.py tests/test_parent_education_wage_p9_formal_variable_role_save.py tests/test_parent_education_wage_p10_product_control_ia.py tests/test_parent_education_wage_p11_source_metadata_contract.py -q`，59 passed。
- React build：`cd Product/web-react && npm run build` 通过，保留既有 Vite chunk size warning。
- API smoke：8772 当前代码服务上，P11 返回 `source_metadata_contract_required`；P9 仍返回 `blocked_missing_dataset_source_metadata`，`can_create_run_id=false`，`can_execute_model=false`。
- 浏览器 smoke：8772 真实入口桌面和 390px 移动端均可见 `Per-field source confirmation`、`field_bindings JSON preview` 和 9 个 source rows，console errors=0；截图为 `Product/output/playwright/product-control-p11b-field-editor-desktop.png`、`Product/output/playwright/product-control-p11b-field-editor-mobile.png`。

### 实现范围

- `Tasks/parent-education-wage-p11b-per-field-source-confirmation-bdd.md`：P11B SDD/BDD。
- `tests/test_parent_education_wage_p11_source_metadata_contract.py`：新增 P11B React 契约测试。
- `Product/web-react/src/components/ProductControlP0Panel.tsx`：新增 `sourceFieldRows`、逐字段 row editor、row-to-`field_bindings` payload 构造和 JSON preview。
- `Product/web-react/src/styles.css`：新增 P11B 字段表桌面/移动端布局。
- `WORKFLOW_STATUS.md`、`Tasks/todo.md`、`Tasks/current-stage.md`、`Tasks/handoff.md`：同步 P11B 阶段状态。

### 剩余风险

- P11B 仍未替用户保存真实 source contract；下一步必须由 P11-Human 完成真实签收。
- 移动端可读但页面较长；后续可考虑按字段分组或折叠，但本轮无重叠遮挡。
- 本轮尝试派出独立 code-reviewer Agent，但当前会话 subagent thread 已满，未能启动；后续进入 P11-Human/P9 前应再次做独立审查。
- P12 仍必须等 P11-Human 和 P9 正式 VariableRoleSet 保存成功后再开始。

## 2026-06-18 P11A Source Contract Review Kit

### 行为覆盖

- [x] 行为 1：P11 GET 返回 `source_contract_review_kit`，包含 required fields、recommended dataset path、dataset path candidates、field review items 和 no-model boundary。
- [x] 行为 2：字段候选来自 P5/P4 证据；`father_education`、`mother_education` 能显示 preferred candidate、source path 和 evidence level，但仍标记为 `needs_human_confirmation`。
- [x] 行为 3：缺少候选的字段仍出现在 field review items 中，并标记为 `missing_recommended_source`，不会被隐藏。
- [x] 行为 4：React P11 面板展示 `Source review kit`、recommended dataset path 和 field review items，用户不再只面对 `field_bindings` JSON。
- [x] 边界：P11A 不保存 source contract，不写正式 VariableRoleSet，不写 DesignSpec/RunPlan，不创建 run id，不执行模型。

### 测试覆盖

- SDD/BDD：`Tasks/parent-education-wage-p11a-source-contract-review-kit-bdd.md`。
- RED：`python3 -m pytest tests/test_parent_education_wage_p11_source_metadata_contract.py -q` 新增 P11A 测试后先失败 2 项，原因是 API 和 React 尚未暴露 review kit。
- 目标测试：`python3 -m pytest tests/test_parent_education_wage_p11_source_metadata_contract.py -q`，6 passed。
- P9/P10/P11/P11A 邻近回归：`python3 -m pytest tests/test_parent_education_wage_p9_formal_variable_role_save.py tests/test_parent_education_wage_p10_product_control_ia.py tests/test_parent_education_wage_p11_source_metadata_contract.py -q`，17 passed。
- P1-P11 scoped 回归：`python3 -m pytest tests/test_parent_education_wage_literature_evidence_ledger.py tests/test_parent_education_wage_data_field_binding_ledger.py tests/test_parent_education_wage_method_execution_ledger.py tests/test_parent_education_wage_p2_execution_readiness.py tests/test_parent_education_wage_p3_draft_package.py tests/test_parent_education_wage_p4_field_source_candidates.py tests/test_parent_education_wage_p5_variable_role_preflight.py tests/test_parent_education_wage_p6_variable_role_signoff.py tests/test_parent_education_wage_p7_variable_role_signoff_ui.py tests/test_parent_education_wage_p8_formal_variable_role_approval.py tests/test_parent_education_wage_p9_formal_variable_role_save.py tests/test_parent_education_wage_p10_product_control_ia.py tests/test_parent_education_wage_p11_source_metadata_contract.py -q`，73 passed。
- Python 编译：`python3 -m py_compile Product/backend/product_control_p11_source_metadata_service.py Product/app.py tests/test_parent_education_wage_p11_source_metadata_contract.py` 通过。
- React build：`cd Product/web-react && npm run build` 通过，仍有既有 Vite chunk size warning。
- API smoke：8771 当前代码服务上，P11 返回 `source_metadata_contract_required`、`source_contract_review_kit.status=needs_human_source_contract_review`、`field_item_count=9`、`can_execute_model=false`；P9 仍返回 `blocked_missing_dataset_source_metadata`。
- 浏览器 smoke：8771 真实入口桌面和 390px 移动端均可见 `Source review kit` 和 `recommended dataset path`，console errors=0；截图为 `Product/output/playwright/product-control-p11a-review-kit-desktop.png`、`Product/output/playwright/product-control-p11a-review-kit-mobile.png`。

### 实现范围

- `Tasks/parent-education-wage-p11a-source-contract-review-kit-bdd.md`：P11A SDD/BDD。
- `tests/test_parent_education_wage_p11_source_metadata_contract.py`：新增 P11A API 和 React 契约测试。
- `Product/backend/product_control_p11_source_metadata_service.py`：新增 source contract review kit 构造逻辑。
- `Product/web-react/src/components/ProductControlP0Panel.tsx`：新增 P11 review kit 类型、默认值预填和展示区。
- `Product/web-react/src/styles.css`：新增 P11 review kit 桌面/移动端布局。

### 剩余风险

- P11A 只是签收辅助，不是人工签收本身；真实 source contract 仍未保存。
- `field_bindings` 仍是 JSON textarea，P11A 只把候选摊开；更理想的本科生体验应进一步拆成逐字段确认控件。
- P12 仍必须等 P11-Human 和 P9 正式变量表保存成功后再开始。

## 2026-06-18 P11 Source Metadata Completion Path

### 行为覆盖

- [x] 行为 1：P11 GET 展示最新 editable draft、P8 approval 后仍缺的 source metadata 字段，包含 dataset path、`ln_wage`、`parent_education`、controls 和父母教育 source fields。
- [x] 行为 2：P11 POST 不完整 source contract 返回 `source_metadata_contract_incomplete`，P9 仍为 `blocked_missing_dataset_source_metadata`。
- [x] 行为 3：完整 source contract 只更新最新 editable draft 的 `source_contract.status=complete`，并让 P9 GET 变成 `formal_variable_role_save_ready`。
- [x] 行为 4：React Product Control 提供 `P11 Source Metadata` 表单，用户能填写 dataset path、field_bindings、reviewer、note、confirmation 和 `parent_education construction`。
- [x] 边界：P11 不写正式 VariableRoleSet、DesignSpec、RunPlan，不创建 run id，不执行模型；P9 仍需单独保存正式变量表。

### 测试覆盖

- BDD：`Tasks/parent-education-wage-p11-source-metadata-contract-bdd.md`。
- RED：`python3 -m pytest tests/test_parent_education_wage_p11_source_metadata_contract.py -q` 首次失败 4 项，原因是 P11 API、服务和 React 表单不存在。
- 目标测试：`python3 -m pytest tests/test_parent_education_wage_p11_source_metadata_contract.py -q`，4 passed。
- P9/P10/P11 邻近回归：`python3 -m pytest tests/test_parent_education_wage_p9_formal_variable_role_save.py tests/test_parent_education_wage_p10_product_control_ia.py tests/test_parent_education_wage_p11_source_metadata_contract.py -q`，15 passed。
- Python 编译：`python3 -m py_compile Product/backend/product_control_p11_source_metadata_service.py Product/backend/product_control_p9_variable_role_save_service.py Product/app.py tests/test_parent_education_wage_p11_source_metadata_contract.py` 通过。
- React build：`cd Product/web-react && npm run build` 通过，仍有既有 Vite chunk size warning。

### 实现范围

- `Tasks/parent-education-wage-p11-source-metadata-contract-bdd.md`：P11 行为契约。
- `tests/test_parent_education_wage_p11_source_metadata_contract.py`：P11 API、draft-only 写入、P9 解锁和 React 契约测试。
- `Product/backend/product_control_p11_source_metadata_service.py`：P11 source contract packet、保存门禁和 latest draft 写回。
- `Product/app.py`：新增 P11 GET/POST API 和 payload。
- `Product/web-react/src/components/ProductControlP0Panel.tsx`：P11 source metadata 表单和 P9 联动刷新。
- `Product/web-react/src/styles.css`：P11 表单和移动端布局。

### 剩余风险

- 真实项目 source contract 尚未由用户填写；当前 P9 仍应阻断。
- P11 当前用 JSON textarea 承载 `field_bindings`，比最终本科生体验偏技术；后续可把它拆成字段表格，但不阻断当前功能闭环。
- P12 仍必须等 P9 正式 VariableRoleSet 保存成功后再开始。

## 2026-06-18 P10 Product Control Current Gate IA

### 行为覆盖

- [x] 行为 1：Product Control 顶部先显示当前门禁摘要，而不是让用户从 P0-P9 线性历史里找状态。
- [x] 行为 2：P0-P8 默认折叠为 `产品控制 P0-P8 阶段历史`，摘要说明 P7 已完成、P8 已审批、P9 等待 source metadata。
- [x] 行为 3：P9 当前阻断详情仍保留，保存按钮禁用，缺失字段和 `blocked_missing_dataset_source_metadata` 可见。
- [x] 行为 4：页面继续明确 `不写 DesignSpec；不写 RunPlan；不跑模型`，且没有“运行模型”入口。
- [x] 审查闭环：修复了当前门禁摘要硬编码为等待态的问题；摘要现在从 P9 API 状态动态读取，避免将来 P9 变 ready 后页面仍误报 blocked。

### 测试覆盖

- SDD：`Tasks/north-star-product-plan.md`。
- BDD：`Tasks/parent-education-wage-p10-product-control-ia-bdd.md`。
- RED：`python3 -m pytest tests/test_parent_education_wage_p10_product_control_ia.py -q` 首次失败 3 项，原因是当前门禁摘要、历史折叠和 Product Control 优先级尚未实现。
- 目标/契约回归：`python3 -m pytest tests/test_parent_education_wage_p10_product_control_ia.py tests/test_product_control_p0_stage_panel.py tests/test_web_react_api_base_contract.py -q`，15 passed, 11 subtests passed。
- P1-P10 scoped 回归：`python3 -m pytest tests/test_parent_education_wage_literature_evidence_ledger.py tests/test_parent_education_wage_data_field_binding_ledger.py tests/test_parent_education_wage_method_execution_ledger.py tests/test_parent_education_wage_p2_execution_readiness.py tests/test_parent_education_wage_p3_draft_package.py tests/test_parent_education_wage_p4_field_source_candidates.py tests/test_parent_education_wage_p5_variable_role_preflight.py tests/test_parent_education_wage_p6_variable_role_signoff.py tests/test_parent_education_wage_p7_variable_role_signoff_ui.py tests/test_parent_education_wage_p8_formal_variable_role_approval.py tests/test_parent_education_wage_p9_formal_variable_role_save.py tests/test_parent_education_wage_p10_product_control_ia.py -q`，67 passed。
- React build：`cd Product/web-react && npm run build` 通过，仍有既有 Vite chunk size warning。
- API smoke：P9 GET 仍返回 `blocked_missing_dataset_source_metadata`，`can_save_formal_variable_roles=false`、`can_create_run_id=false`、`can_execute_model=false`。
- 浏览器 smoke：8769 真实入口桌面和 390px 移动端均可见当前门禁摘要、折叠历史、P9 阻断和禁用保存状态，且无“运行模型”入口；截图为 `output/playwright/product-control-p10-current-gate.png`、`output/playwright/product-control-p10-mobile.png`。
- 独立审查：本轮未能派出新的独立 Agent 复核，因为当前会话可用 thread 已满；已做手动窄范围审查并修复动态摘要问题。

### 实现范围

- `Tasks/north-star-product-plan.md`：北极星目标、P10-P16 阶段路线、SDD/BDD/TDD 规则、停机条件和禁改范围。
- `Tasks/parent-education-wage-p10-product-control-ia-bdd.md`：P10 行为契约。
- `tests/test_parent_education_wage_p10_product_control_ia.py`：P10 React 信息架构和边界测试。
- `Product/web-react/src/App.tsx`：Product Control 在阶段导航前渲染。
- `Product/web-react/src/components/ProductControlP0Panel.tsx`：当前门禁摘要、历史折叠和 P9 当前详情。
- `Product/web-react/src/styles.css`：P10 当前门禁、历史折叠和移动端样式。

### 剩余风险

- P10 没有补齐 source metadata；真实项目仍应停在 P9 的 `blocked_missing_dataset_source_metadata`。
- 下一阶段 P11 需要把 dataset path、`ln_wage`、`parent_education`、controls 的字段来源做成人工确认路径。
- Vite chunk size warning 仍存在，属于既有前端体积问题，不阻断 P10。

## 2026-06-18 P9 Formal Variable Role Save Gate

### 行为覆盖

- [x] 行为 1：没有 P8 approval 时，P9 返回 `blocked_missing_p8_formal_approval`，不能保存正式变量表。
- [x] 行为 2：有 P8 approval 但 dataset/source metadata 不完整时，P9 返回 `blocked_missing_dataset_source_metadata`。
- [x] 行为 3：P9 save 缺 reviewer、note、确认码、source draft、dataset 或 roles 时返回 409，不写正式状态。
- [x] 行为 4：P9 save 只从 P8 已批准的 draft 写正式 `state/product/variable_roles.json`，不写 DesignSpec、RunPlan、run id 或模型结果。
- [x] 行为 5：POST payload 不能替换已批准 roles 或 dataset path。
- [x] 行为 6：React Product Control 显示 P9 保存面板、缺失 source metadata、确认码和“不写 DesignSpec；不写 RunPlan；不跑模型”。
- [x] 审查闭环：只有 `dataset_column` 的弱字段绑定不能通过 P9；字段绑定必须有可审计 `source_path` 和 `evidence_level`，派生变量的 source fields 也要满足同样要求。

### 测试覆盖

- BDD：`Tasks/parent-education-wage-p9-formal-variable-role-save-bdd.md`。
- RED：`python3 -m pytest tests/test_parent_education_wage_p9_formal_variable_role_save.py -q` 先失败 6 项，原因是 P9 API 和 React 面板不存在。
- 目标测试：`python3 -m pytest tests/test_parent_education_wage_p9_formal_variable_role_save.py -q`，7 passed。
- P6/P7/P8/P9 回归：`python3 -m pytest tests/test_parent_education_wage_p6_variable_role_signoff.py tests/test_parent_education_wage_p7_variable_role_signoff_ui.py tests/test_parent_education_wage_p8_formal_variable_role_approval.py tests/test_parent_education_wage_p9_formal_variable_role_save.py -q`，26 passed。
- P1-P9 回归：`python3 -m pytest tests/test_parent_education_wage_literature_evidence_ledger.py tests/test_parent_education_wage_data_field_binding_ledger.py tests/test_parent_education_wage_method_execution_ledger.py tests/test_parent_education_wage_p2_execution_readiness.py tests/test_parent_education_wage_p3_draft_package.py tests/test_parent_education_wage_p4_field_source_candidates.py tests/test_parent_education_wage_p5_variable_role_preflight.py tests/test_parent_education_wage_p6_variable_role_signoff.py tests/test_parent_education_wage_p7_variable_role_signoff_ui.py tests/test_parent_education_wage_p8_formal_variable_role_approval.py tests/test_parent_education_wage_p9_formal_variable_role_save.py -q`，63 passed。
- 产品控制 scoped 回归：`python3 -m pytest tests/test_product_control_p0_phase.py tests/test_product_control_p0_stage_panel.py tests/test_product_control_demo_topic_binding_audit.py -q`，14 passed。
- Python 编译：`python3 -m py_compile Product/backend/product_control_p9_variable_role_save_service.py Product/app.py tests/test_parent_education_wage_p9_formal_variable_role_save.py` 通过。
- React build：`cd Product/web-react && npm run build` 通过，仍有既有 Vite chunk size warning。
- API smoke：8769 新服务上 P8 返回 `formal_variable_role_approval_recorded`；P9 返回 `blocked_missing_dataset_source_metadata`，完整响应显示 `source_contract.status=incomplete`、`dataset_path=""`、`analysis_dataset_available=false`、`field_bindings={}`、`derived_variables={}`，因此正式保存、run id 和模型执行都保持关闭。
- 浏览器 smoke：`http://127.0.0.1:8769/?topic=empirical-paper-template-main&mode=human-review&api_base=http://127.0.0.1:8769` 桌面和 390px 移动端均可见 P9 面板、缺失字段、禁用保存状态，且无“运行模型”入口；截图为 `output/playwright/product-control-p9-desktop.png`、`output/playwright/product-control-p9-mobile.png`。
- 恢复后 Playwright CLI 快照：同一 8769 页面可打开，P9 面板、`blocked_missing_dataset_source_metadata`、字段缺口和禁用保存按钮可见。
- 独立审查：code-reviewer Agent `Kierkegaard` 初审 request changes；指出 source metadata 完整性门禁过弱，以及 React 保存失败丢失具体阻断原因。已补强后端审计字段要求、弱绑定回归测试和前端错误信息展示。

### 实现范围

- `Tasks/parent-education-wage-p9-formal-variable-role-save-bdd.md`：P9 行为契约。
- `tests/test_parent_education_wage_p9_formal_variable_role_save.py`：P9 API、source metadata、payload mismatch、React 契约测试。
- `Product/backend/product_control_p9_variable_role_save_service.py`：P9 保存门禁和正式变量表写入合同。
- `Product/app.py`：新增 P9 GET/POST API 和 payload。
- `Product/web-react/src/components/ProductControlP0Panel.tsx`：React P9 保存面板。
- `Product/web-react/src/styles.css`：P9 表单和移动端样式。

### 剩余风险

- 真实项目 P9 被 source metadata 阻断；这是正确状态，不是失败。
- Product Control 页面混乱问题已由 P10 当前门禁中心收口；下一阶段应做 P11 source metadata 补齐路径。
- P9 不是 DesignSpec/RunPlan/model 入口；source metadata 补齐并正式保存通过后，才进入 DesignSpec preflight。

## 2026-06-18 P8 Formal Variable Role Approval Gate

### 行为覆盖

- [x] 行为 1：没有 P7/P6 editable draft 时，P8 返回 `blocked_missing_p7_variable_role_draft`，不能批准正式变量角色。
- [x] 行为 2：P7 editable draft 存在时，P8 GET 暴露待审 draft，但仍不写正式 `variable_roles.json`。
- [x] 行为 3：P8 POST 缺 reviewer、note 或确认码时返回 409，不写 approval，不解锁正式保存。
- [x] 行为 4：P8 approve 只记录 `state/product/variable_role_formal_approvals.json`；随后旧 `PUT /variable-roles` 只有在 approval 对当前最新 draft 生效、且 latest draft roles、approval `source_draft_roles`、PUT roles 三者一致时才可写正式 VariableRoleSet。
- [x] 行为 5：React Product Control 显示 P8 审批面板、reviewer/note/confirmation、确认码和“不写 RunPlan；不跑模型”。
- [x] 审查闭环：P8 approval 绑定当前最新 `source_draft_id` 和审批当刻的 roles 快照，旧 approval 不能解锁新 draft，审批 A 不能写入不同 roles，同一 draft id 的 roles 被篡改后原 approval 失效；P8 不写 DesignSpec、RunPlan、run id 或模型结果。

### 测试覆盖

- BDD：`Tasks/parent-education-wage-p8-formal-variable-role-approval-bdd.md`。
- RED：`python3 -m pytest tests/test_parent_education_wage_p8_formal_variable_role_approval.py -q` 先失败 5 项，原因是 P8 API 和 React 面板不存在；独立审查后新增 stale approval、roles mismatch、same-draft-id role mutation 三条绕过测试，均先复现失败。
- 目标测试：`python3 -m pytest tests/test_parent_education_wage_p8_formal_variable_role_approval.py -q`，8 passed。
- P6/P7/P8 回归：`python3 -m pytest tests/test_parent_education_wage_p6_variable_role_signoff.py tests/test_parent_education_wage_p7_variable_role_signoff_ui.py tests/test_parent_education_wage_p8_formal_variable_role_approval.py -q`，19 passed。
- P1-P8 回归：`python3 -m pytest tests/test_parent_education_wage_literature_evidence_ledger.py tests/test_parent_education_wage_data_field_binding_ledger.py tests/test_parent_education_wage_method_execution_ledger.py tests/test_parent_education_wage_p2_execution_readiness.py tests/test_parent_education_wage_p3_draft_package.py tests/test_parent_education_wage_p4_field_source_candidates.py tests/test_parent_education_wage_p5_variable_role_preflight.py tests/test_parent_education_wage_p6_variable_role_signoff.py tests/test_parent_education_wage_p7_variable_role_signoff_ui.py tests/test_parent_education_wage_p8_formal_variable_role_approval.py -q`，56 passed。
- 产品控制 scoped 回归：`python3 -m pytest tests/test_product_control_demo_topic_binding_audit.py tests/test_product_control_p0_phase.py tests/test_product_control_p0_stage_panel.py -q`，14 passed。
- Python 编译：`python3 -m py_compile Product/backend/product_control_p8_variable_role_approval_service.py Product/backend/product_control_p6_variable_role_signoff_service.py Product/app.py` 通过。
- React build：`cd Product/web-react && npm run build` 通过，仍有既有 Vite chunk size warning。
- API smoke：`GET http://127.0.0.1:8768/api/v1/projects/proj_empirical_paper_template_main/product-control/p8-variable-role-approval` 返回 200，状态为 `blocked_missing_p7_variable_role_draft`，所有 DesignSpec/RunPlan/run/model 写入能力均为 false。
- 浏览器 smoke：`http://127.0.0.1:8768/?topic=empirical-paper-template-main&mode=human-review&api_base=http://127.0.0.1:8768` 可见 P8 面板、阻断状态和“不写 RunPlan；不跑模型”；桌面与 390px 移动端截图为 `artifacts/ui-checks/product-control-p8-variable-role-approval-desktop.png`、`artifacts/ui-checks/product-control-p8-variable-role-approval-mobile.png`。
- 独立审查：code-reviewer Agent `Mendel` 初审为 request changes；指出旧 P8 approval 可解锁新 draft、且 approval 未绑定正式 PUT roles。code-reviewer Agent `Bernoulli` 复审为 request changes；指出同一 draft id 的 roles 被篡改后旧逻辑仍可放行。已补回归并修复为：正式保存前必须验证 approval 对当前最新 draft 生效，且 latest draft roles、approval `source_draft_roles`、PUT roles 三者完全一致。code-reviewer Agent `Ampere` 最终窄范围复核 PASS。

### 实现范围

- `Tasks/parent-education-wage-p8-formal-variable-role-approval-bdd.md`：P8 行为契约。
- `tests/test_parent_education_wage_p8_formal_variable_role_approval.py`：P8 API、正式保存门禁、React 契约测试。
- `Product/backend/product_control_p8_variable_role_approval_service.py`：P8 审批包和 approval ledger。
- `Product/backend/product_control_p6_variable_role_signoff_service.py`：正式 VariableRoleSet 保存门禁改为必须存在对当前最新 draft 生效的 P8 approval，且 latest draft roles、approval `source_draft_roles`、PUT roles 三者必须一致。
- `Product/app.py`：新增 P8 GET/POST API 和 payload。
- `Product/web-react/src/components/ProductControlP0Panel.tsx`：React P8 审批面板。
- `Product/web-react/src/styles.css`：P8 表单和移动端样式。

### 剩余风险

- 真实项目仍没有用户点击 P7 promotion 生成的 editable draft，因此 P8 在真实项目上正确阻断；我没有替用户提交 P7 或 P8。
- P8 是正式保存前的审批门禁，不是 DesignSpec/RunPlan/model 入口；下一步应做 P9 正式 VariableRoleSet editor/save 验收。
- 当前 Vite bundle size warning 仍存在，属于既有前端体积问题，不阻断 P8。

## 2026-06-18 P7 Variable Role Signoff UI

### 行为覆盖

- [x] 行为 1：P6 signoff packet 给 React 页面返回五项 `recommended_decisions`，用户不用猜 JSON payload。
- [x] 行为 2：React Product Control P6 面板显示五项可编辑确认输入、默认值、`draft_only_no_formal_write` 和“确认并生成可编辑草稿”按钮。
- [x] 行为 3：完整页面签收只调用 editable draft promotion；测试验证会写 `state/product/variable_roles_drafts.json`，不会改写正式 `state/product/variable_roles.json`。
- [x] 审查闭环：P7 promoted draft 之后，旧 `PUT /variable-roles` 仍必须 409 阻断，不能把 editable draft 误当正式写入批准。
- [x] 移动端闭环：390px 视口下 Product Control 和 P6 表单无横向溢出。

### 测试覆盖

- BDD：`Tasks/parent-education-wage-p7-variable-role-signoff-ui-bdd.md`。
- RED：`python3 -m pytest tests/test_parent_education_wage_p7_variable_role_signoff_ui.py -q` 先失败 3 项，原因是缺少 `recommended_decisions`、React 表单和用默认值 promotion 的能力。
- 目标测试：`python3 -m pytest tests/test_parent_education_wage_p7_variable_role_signoff_ui.py -q`，3 passed。
- P6+P7 回归：`python3 -m pytest tests/test_parent_education_wage_p6_variable_role_signoff.py tests/test_parent_education_wage_p7_variable_role_signoff_ui.py -q`，11 passed。
- P2-P7 回归：`python3 -m pytest tests/test_parent_education_wage_p2_execution_readiness.py tests/test_parent_education_wage_p3_draft_package.py tests/test_parent_education_wage_p4_field_source_candidates.py tests/test_parent_education_wage_p5_variable_role_preflight.py tests/test_parent_education_wage_p6_variable_role_signoff.py tests/test_parent_education_wage_p7_variable_role_signoff_ui.py -q`，33 passed。
- 产品控制 scoped 回归：`python3 -m pytest tests/test_parent_education_wage_literature_evidence_ledger.py tests/test_parent_education_wage_data_field_binding_ledger.py tests/test_parent_education_wage_method_execution_ledger.py tests/test_parent_education_wage_p2_execution_readiness.py tests/test_parent_education_wage_p3_draft_package.py tests/test_parent_education_wage_p4_field_source_candidates.py tests/test_parent_education_wage_p5_variable_role_preflight.py tests/test_parent_education_wage_p6_variable_role_signoff.py tests/test_parent_education_wage_p7_variable_role_signoff_ui.py tests/test_product_control_p0_stage_panel.py tests/test_product_control_p0_phase.py tests/test_web_react_api_base_contract.py tests/test_p3_react_input_tabs.py -q`，71 passed, 11 subtests passed。
- Python 编译：`python3 -m py_compile Program/workbench/parent_education_wage_variable_role_signoff.py Program/parent_education_wage_variable_role_signoff.py Product/backend/product_control_p6_variable_role_signoff_service.py Product/app.py tests/test_parent_education_wage_p7_variable_role_signoff_ui.py` 通过。
- React build：`cd Product/web-react && npm run build` 通过，仍有既有 Vite chunk size warning。
- API smoke：P6 GET/POST 返回 `variable_role_signoff_required` 和五项 `recommended_decisions`；旧正式保存口仍返回 409 `p6_variable_role_draft_required`。未对真实项目调用 `/promote`。
- 浏览器 smoke：真实入口桌面和 390px 移动端均显示五项输入、默认值、草稿按钮和“不写正式 VariableRoleSet；不跑模型”；横向溢出 false，console errors=0；截图为 `artifacts/ui-checks/product-control-p7-variable-role-signoff-desktop.png` 与 `artifacts/ui-checks/product-control-p7-variable-role-signoff-mobile.png`。
- 独立审查：code-reviewer Agent `Herschel` 初审为 request changes；指出 P7 promotion 后旧正式保存口会误开正式 `variable_roles.json` 写入。已补回归测试并修复后端门禁：P7 draft 之后仍需 P8 单独正式批准，否则正式保存口返回 409，且 `variable_roles.json`、`design_spec.json`、`run_plan.json` 哈希保持不变。

### 实现范围

- `Tasks/parent-education-wage-p7-variable-role-signoff-ui-bdd.md`：P7 行为契约。
- `tests/test_parent_education_wage_p7_variable_role_signoff_ui.py`：P7 后端默认值、React 契约和 editable draft promotion 测试。
- `Product/backend/product_control_p6_variable_role_signoff_service.py`：P7 后继续阻断正式 VariableRoleSet 保存，直到 P8 正式批准文件存在。
- `Program/workbench/parent_education_wage_variable_role_signoff.py`：补 `recommended_decisions` 和 Review 默认值输出。
- `Product/web-react/src/components/ProductControlP0Panel.tsx`：P6 五项签收表单、promotion 调用、成功/错误反馈。
- `Product/web-react/src/styles.css`：P6 表单样式和移动端主工作区/Product Control 横向溢出修复。
- `Results/json/parent_education_wage_p6_variable_role_signoff.json`、`Reviews/parent_education_wage_p6_variable_role_signoff.md`：真实 P6/P7 签收材料刷新。

### 剩余风险

- 真实项目尚未由我代替用户执行 `/promote`；用户需要在页面确认五项口径后点击“确认并生成可编辑草稿”。
- P7 只生成 editable draft；即使 draft 已生成，正式 VariableRoleSet 仍需要 P8 审批/编辑路径，旧正式保存口不会因此解锁。
- 当前仍不能创建 run id、写 RunPlan 或执行模型。

## 2026-06-17 P6 Human Signoff And Promotion Path

### 行为覆盖

- [x] 行为 1：P6 读取 P5 草案并生成待签收清单，不写正式变量角色。
- [x] 行为 2：签收项不完整时不能提升，也不能写草稿或正式状态。
- [x] 行为 3：完整签收后只写可编辑 draft，不覆盖正式 VariableRoleSet。
- [x] 行为 4：请求正式写回但没有更强授权时会被阻断。
- [x] 行为 5：Product Control 暴露 P6 GET/POST/promotion endpoint。
- [x] 行为 6：React 主入口显示 P6 签收状态、`editable_draft` 和 `formal write=false`。
- [x] 审查闭环 1：旧 `PUT /variable-roles` 不能绕过 P6 直接写正式变量角色。
- [x] 审查闭环 2：`formal_variable_roles` target 即使带 `allow_formal_write=true` 也稳定阻断。
- [x] 审查闭环 3：重复 P6 promotion 不用固定 id 覆盖旧 draft。

### 测试覆盖

- RED：`python3 -m pytest tests/test_parent_education_wage_p6_variable_role_signoff.py -q` 先失败 6 项，原因是 P6 module/API/React 状态不存在。
- 目标测试：`python3 -m pytest tests/test_parent_education_wage_p6_variable_role_signoff.py -q`，8 passed。
- Python 编译：`python3 -m py_compile Program/workbench/parent_education_wage_variable_role_signoff.py Program/parent_education_wage_variable_role_signoff.py Product/backend/product_control_p6_variable_role_signoff_service.py Product/app.py tests/test_parent_education_wage_p6_variable_role_signoff.py` 通过。
- 真实项目生成：`python3 Program/parent_education_wage_variable_role_signoff.py --project-root .` 通过，输出 `variable_role_signoff_required`。
- P2-P6 回归：`python3 -m pytest tests/test_parent_education_wage_p2_execution_readiness.py tests/test_parent_education_wage_p3_draft_package.py tests/test_parent_education_wage_p4_field_source_candidates.py tests/test_parent_education_wage_p5_variable_role_preflight.py tests/test_parent_education_wage_p6_variable_role_signoff.py -q`，30 passed。
- 产品控制 scoped 回归：`python3 -m pytest tests/test_parent_education_wage_literature_evidence_ledger.py tests/test_parent_education_wage_data_field_binding_ledger.py tests/test_parent_education_wage_method_execution_ledger.py tests/test_parent_education_wage_p2_execution_readiness.py tests/test_parent_education_wage_p3_draft_package.py tests/test_parent_education_wage_p4_field_source_candidates.py tests/test_parent_education_wage_p5_variable_role_preflight.py tests/test_parent_education_wage_p6_variable_role_signoff.py tests/test_product_control_p0_stage_panel.py tests/test_product_control_p0_phase.py tests/test_web_react_api_base_contract.py tests/test_p3_react_input_tabs.py -q`，68 passed, 11 subtests passed。
- React build：`cd Product/web-react && npm run build` 通过，仍有既有 Vite chunk size warning。
- API smoke：P6 GET/POST 返回 `variable_role_signoff_required`；旧正式保存口返回 409 `p6_variable_role_draft_required`。
- 浏览器 smoke：P6 签收状态可见，`editable_draft` 可见，`formal write=false` 可见，无横向溢出，console errors=0；截图 `artifacts/ui-checks/product-control-p6-variable-role-signoff.png`。
- 独立审查：code-reviewer Agent `Feynman` 初审为 request changes；指出的 1 high、2 medium、1 low 已分别通过守卫、稳定阻断、唯一 draft id 和 React 文案修正闭环。

### 实现范围

- `Tasks/parent-education-wage-p6-variable-role-signoff-bdd.md`：P6 行为契约和边界。
- `Program/workbench/parent_education_wage_variable_role_signoff.py`：P6 签收包与 promotion 逻辑。
- `Program/parent_education_wage_variable_role_signoff.py`：P6 CLI。
- `Product/backend/product_control_p6_variable_role_signoff_service.py`：P6 Product Control 服务。
- `Product/app.py`：新增 P6 GET/POST/promotion API，并对父母教育工资链路的正式变量角色保存增加 P6 draft 门禁。
- `Product/web-react/src/components/ProductControlP0Panel.tsx`、`Product/web-react/src/styles.css`：React 产品控制面显示 P6。
- `Results/json/parent_education_wage_p6_variable_role_signoff.json`、`Reviews/parent_education_wage_p6_variable_role_signoff.md`：真实 P6 审阅层产物。

### 剩余风险

- 真实项目尚未执行 promotion，因为签收项需要用户确认。
- P6 只允许进入可编辑 draft；正式 VariableRoleSet 仍需单独审批。
- 当前仍不能创建 run id 或执行模型。

## 2026-06-17 P5 VariableRoleSet Draft Preflight

### 行为覆盖

- [x] 行为 1：P5 消费 P4 字段候选并生成可审阅 VariableRoleSet draft preflight。
- [x] 行为 2：`parent_education` 只进入构造草案，`decision_status=requires_human_confirmation`。
- [x] 行为 3：不写正式 VariableRoleSet、DesignSpec、RunPlan，不创建 run id，不执行回归。
- [x] 行为 4：Product Control 暴露 P5 状态，GET 只读，POST 才显式生成。
- [x] 行为 5：React 主入口显示 `P5 VariableRoleSet`、`parent_education` 和 `requires_human_confirmation`。

### 测试覆盖

- RED：`python3 -m pytest tests/test_parent_education_wage_p5_variable_role_preflight.py -q` 先失败，原因是 P5 module/API/React 状态不存在。
- 目标测试：`python3 -m pytest tests/test_parent_education_wage_p5_variable_role_preflight.py -q`，6 passed。
- 真实项目生成：`python3 Program/parent_education_wage_variable_role_preflight.py --project-root .` 通过，输出 `variable_role_preflight_ready_for_review`。
- P2/P3/P4/P5 回归：`python3 -m pytest tests/test_parent_education_wage_p2_execution_readiness.py tests/test_parent_education_wage_p3_draft_package.py tests/test_parent_education_wage_p4_field_source_candidates.py tests/test_parent_education_wage_p5_variable_role_preflight.py -q`，22 passed。
- 产品控制 scoped 回归：`python3 -m pytest tests/test_parent_education_wage_literature_evidence_ledger.py tests/test_parent_education_wage_data_field_binding_ledger.py tests/test_parent_education_wage_method_execution_ledger.py tests/test_parent_education_wage_p2_execution_readiness.py tests/test_parent_education_wage_p3_draft_package.py tests/test_parent_education_wage_p4_field_source_candidates.py tests/test_parent_education_wage_p5_variable_role_preflight.py tests/test_product_control_p0_stage_panel.py tests/test_product_control_p0_phase.py tests/test_web_react_api_base_contract.py tests/test_p3_react_input_tabs.py -q`，60 passed, 11 subtests passed。
- Python 编译：`python3 -m py_compile Program/workbench/parent_education_wage_variable_role_preflight.py Program/parent_education_wage_variable_role_preflight.py Product/backend/product_control_p5_variable_role_preflight_service.py Product/app.py tests/test_parent_education_wage_p5_variable_role_preflight.py` 通过。
- React build：`cd Product/web-react && npm run build` 通过，仍有既有 Vite chunk size warning。
- API smoke：`GET/POST http://127.0.0.1:8766/api/v1/projects/proj_empirical_paper_template_main/product-control/p5-variable-role-preflight` 均返回 `variable_role_preflight_ready_for_review`。
- 浏览器 smoke：`http://127.0.0.1:8766/?topic=empirical-paper-template-main&mode=human-review&api_base=http://127.0.0.1:8766` 可见 P5 面板；`parent_education=requires_human_confirmation`、`formal write=false`、无横向溢出、console errors=0；截图 `artifacts/ui-checks/product-control-p5-variable-role-preflight.png`。
- Scoped diff check：`git diff --check -- Product/app.py Product/web-react/src/components/ProductControlP0Panel.tsx Product/web-react/src/styles.css WORKFLOW_STATUS.md Tasks/todo.md Tasks/current-stage.md Tasks/handoff.md Tasks/review.md` 通过。
- 独立审查：code-reviewer Agent `Newton` 返回 no blocking findings；非阻断缺口为 React 自动化测试偏静态、缺少 P1-B/P2 输入缺失场景。已补缺失输入 `input_warnings` 和 `test_bdd_p5d_missing_data_context_is_explicit_warning_not_silent_default`，并重新跑上述回归/API/浏览器验证。

### 实现范围

- `Tasks/parent-education-wage-p5-variable-role-preflight-bdd.md`：P5 行为契约。
- `outputs/parent_education_wage_p5_resource_research.md` 与 `.provenance.md`：P5 资源调研记录。
- `Program/workbench/parent_education_wage_variable_role_preflight.py`：P5 草案预检生成器。
- `Program/parent_education_wage_variable_role_preflight.py`：P5 CLI。
- `Product/backend/product_control_p5_variable_role_preflight_service.py`：P5 Product Control 服务。
- `Product/app.py`：新增 `GET/POST /product-control/p5-variable-role-preflight`。
- `Product/web-react/src/components/ProductControlP0Panel.tsx`：React 产品控制面显示 P5。
- `Product/web-react/src/styles.css`：P5 状态块纳入当前产品控制面样式。
- `Results/json/parent_education_wage_p5_variable_role_preflight.json`、`Reviews/parent_education_wage_p5_variable_role_preflight.md`：真实 P5 审阅层产物。

### 剩余风险

- P5 是草案预检，不是正式 VariableRoleSet。
- `parent_education` 构造、优先 CFPS 波次、`hukou` 角色和 outcome/control 仍需人工确认。
- 当前仍不能创建 run id 或写完整实证结果章节。

## 2026-06-17 P4 Field Source Candidates

### 行为覆盖

- [x] 行为 1：P4 使用当前存在的 CFPS 数据根目录，并把旧 `/Users/mahaoxuan/Desktop/实证数据库/...` 路径记录为 stale source。
- [x] 行为 2：只读扫描 Stata 变量标签，为 `father_education` 和 `mother_education` 生成候选字段。
- [x] 行为 3：`parent_education` 只标为 `constructable_needs_review`，不自动确定构造口径。
- [x] 行为 4：不写正式 VariableRoleSet、DesignSpec、RunPlan，不创建 run id，不执行回归。
- [x] 行为 5：Product Control 暴露 P4 状态，GET 只读，POST 才显式生成；React 主入口显示 P4 字段来源。

### 测试覆盖

- RED：`python3 -m pytest tests/test_parent_education_wage_p4_field_source_candidates.py -q` 先失败，原因是 P4 module/API/React 状态不存在；修正测试夹具后得到目标 RED。
- 目标测试：`python3 -m pytest tests/test_parent_education_wage_p4_field_source_candidates.py -q`，5 passed。
- P2/P3/P4 回归：`python3 -m pytest tests/test_parent_education_wage_p2_execution_readiness.py tests/test_parent_education_wage_p3_draft_package.py tests/test_parent_education_wage_p4_field_source_candidates.py -q`，16 passed。
- 产品控制 scoped 回归：`python3 -m pytest tests/test_parent_education_wage_literature_evidence_ledger.py tests/test_parent_education_wage_data_field_binding_ledger.py tests/test_parent_education_wage_method_execution_ledger.py tests/test_parent_education_wage_p2_execution_readiness.py tests/test_parent_education_wage_p3_draft_package.py tests/test_parent_education_wage_p4_field_source_candidates.py tests/test_product_control_p0_stage_panel.py tests/test_product_control_p0_phase.py tests/test_web_react_api_base_contract.py tests/test_p3_react_input_tabs.py -q`，54 passed, 11 subtests passed。
- Python 编译：`python3 -m py_compile Program/workbench/parent_education_wage_field_source_candidates.py Program/parent_education_wage_field_source_candidates.py Product/backend/product_control_p4_field_source_service.py Product/app.py tests/test_parent_education_wage_p4_field_source_candidates.py` 通过。
- React build：`cd Product/web-react && npm run build` 通过，仍有既有 Vite chunk size warning。
- 真实项目生成：`python3 Program/parent_education_wage_field_source_candidates.py --project-root . --data-root "/Users/mahaoxuan/Desktop/论文核心素材库/01_原始数据/实证数据库/A001CFPS中国家庭追踪调查"` 通过，输出 `field_source_candidates_ready_for_review`、`candidate_count=52`。
- API smoke：`GET/POST http://127.0.0.1:8766/api/v1/projects/proj_empirical_paper_template_main/product-control/p4-field-source-candidates` 均返回 `field_source_candidates_ready_for_review`。
- 浏览器 smoke：`http://127.0.0.1:8766/?topic=empirical-paper-template-main&mode=human-review&api_base=http://127.0.0.1:8766` 可见 P4 面板；`father_education=candidate_found`、`mother_education=candidate_found`、候选数 52；截图 `artifacts/ui-checks/product-control-p4-field-source.png`。

### 实现范围

- `Tasks/parent-education-wage-p4-field-source-bdd.md`：P4 行为契约。
- `Program/workbench/parent_education_wage_field_source_candidates.py`：metadata-only CFPS 字段来源候选生成器。
- `Program/parent_education_wage_field_source_candidates.py`：P4 CLI。
- `Product/backend/product_control_p4_field_source_service.py`：P4 Product Control 服务。
- `Product/app.py`：新增 `GET/POST /api/v1/projects/{project_id}/product-control/p4-field-source-candidates`。
- `Product/web-react/src/components/ProductControlP0Panel.tsx`：React 产品控制面显示 P4 字段来源。
- `Product/web-react/src/styles.css`：P3/P4 阶段块纳入当前产品控制面样式。
- `Results/json/parent_education_wage_p4_field_source_candidates.json`、`Reviews/parent_education_wage_p4_field_source_candidates.md`：真实 P4 审阅层产物。

### 剩余风险

- P4 找到的是候选字段，不是正式 VariableRoleSet。
- 需要人工确认优先波次、`parent_education` 构造口径和 `hukou` 角色。
- 当前仍不能创建 run id 或写完整实证结果章节。

## 2026-06-17 P3 DraftPackage Blocked Branch

### 行为覆盖

- [x] 行为 1：P2 阻断态生成 `blocked_draft_package_ready`，不是只停在执行准入诊断。
- [x] 行为 2：生成用户可打开的 `Submissions/parent_education_wage_paper_draft.docx`。
- [x] 行为 3：同步生成 Markdown 源、问题清单和审计报告。
- [x] 行为 4：不写正式 VariableRoleSet、DesignSpec、RunPlan，不创建 run id，不执行回归。
- [x] 行为 5：Product Control 暴露 P3 状态，GET 只读，POST 才显式生成。
- [x] 行为 6：React 产品控制面展示 `P3 DraftPackage`、`paper_draft.docx`、半成品状态和 issue 数。

### 测试覆盖

- RED：`python3 -m pytest tests/test_parent_education_wage_p3_draft_package.py -q` 首次失败，原因是 P3 module/API/React 状态不存在。
- 目标测试：`python3 -m pytest tests/test_parent_education_wage_p3_draft_package.py -q`，5 passed。
- P2/P3 回归：`python3 -m pytest tests/test_parent_education_wage_p2_execution_readiness.py tests/test_parent_education_wage_p3_draft_package.py -q`，11 passed。
- 阶段回归：`python3 -m pytest tests/test_parent_education_wage_literature_evidence_ledger.py tests/test_parent_education_wage_data_field_binding_ledger.py tests/test_parent_education_wage_method_execution_ledger.py tests/test_parent_education_wage_p2_execution_readiness.py tests/test_parent_education_wage_p3_draft_package.py tests/test_product_control_p0_stage_panel.py tests/test_product_control_p0_phase.py tests/test_web_react_api_base_contract.py tests/test_p3_react_input_tabs.py -q`，49 passed, 11 subtests passed。
- Python 编译：`python3 -m py_compile Program/workbench/parent_education_wage_draft_package.py Program/parent_education_wage_draft_package.py Product/backend/product_control_p3_draft_package_service.py Product/app.py tests/test_parent_education_wage_p3_draft_package.py` 通过。
- 真实项目生成：`python3 Program/parent_education_wage_draft_package.py --project-root .` 通过，输出 `blocked_draft_package_ready`。
- docx 可读性：用 `python-docx` 打开 `Submissions/parent_education_wage_paper_draft.docx`，确认包含题目和 `【红标】父母教育字段尚未绑定`。
- React build：`cd Product/web-react && npm run build` 通过，仍有既有 Vite chunk size warning。
- Scoped diff check：P3 相关文件 `git diff --check` 通过。

### 实现范围

- `Tasks/parent-education-wage-p3-draft-package-bdd.md`：P3 行为契约。
- `Program/workbench/parent_education_wage_draft_package.py`：P3 DraftPackage 生成器。
- `Program/parent_education_wage_draft_package.py`：P3 CLI。
- `Product/backend/product_control_p3_draft_package_service.py`：P3 Product Control 服务。
- `Product/app.py`：新增 `GET/POST /api/v1/projects/{project_id}/product-control/p3-draft-package`。
- `Product/web-react/src/components/ProductControlP0Panel.tsx`：React 产品控制面显示 P3 DraftPackage。
- `Results/json/parent_education_wage_p3_draft_package.json`、`Manuscripts/generated/parent_education_wage_paper_draft.md`、`Submissions/parent_education_wage_paper_draft.docx`、`Manuscripts/generated/parent_education_wage_issue_list.md`、`Reviews/parent_education_wage_draft_audit_report.md`：真实 P3 交付物。

### 剩余风险

- 当前是半成品论文包，不是完整论文；父母教育字段缺失仍阻断真实回归和完整结果章节。
- `hukou` 候选仍需人工绑定。
- 下一阶段应进入 P4 字段来源补证和正式变量角色草案预检。

## 2026-06-17 P2 Execution Readiness

### 行为覆盖

- [x] 行为 1：字段补证只生成候选，不直接写正式 `state/product/variable_roles.json`。
- [x] 行为 2：变量口径只进入 draft；父母教育合成规则必须等待人工确认。
- [x] 行为 3：`Tasks/parent-education-wage/design.json` 旧 robot code stub 已修复，但不写正式 DesignSpec。
- [x] 行为 4：字段仍缺失时，P2 输出 blocked execution-readiness ledger，不创建 run id。
- [x] 行为 5：Product Control 暴露 P2 状态，GET 只读，POST 才显式刷新。

### 测试覆盖

- RED：`python3 -m pytest tests/test_parent_education_wage_p2_execution_readiness.py -q` 首次失败，原因是 P2 module/API/React 状态不存在。
- 目标测试：`python3 -m pytest tests/test_parent_education_wage_p2_execution_readiness.py -q`，6 passed。
- 阶段回归：`python3 -m pytest tests/test_parent_education_wage_literature_evidence_ledger.py tests/test_parent_education_wage_data_field_binding_ledger.py tests/test_parent_education_wage_method_execution_ledger.py tests/test_parent_education_wage_p2_execution_readiness.py tests/test_product_control_p0_stage_panel.py tests/test_product_control_p0_phase.py tests/test_web_react_api_base_contract.py tests/test_p3_react_input_tabs.py -q`，44 passed, 11 subtests passed。
- Python 编译：`python3 -m py_compile Program/workbench/parent_education_wage_execution_readiness.py Program/parent_education_wage_execution_readiness.py Product/backend/product_control_p2_execution_readiness_service.py Product/app.py` 通过。
- 真实项目生成：`python3 Program/parent_education_wage_execution_readiness.py --project-root .` 通过，输出 `blocked_missing_parent_education_fields`。
- P1-C refresh：`python3 Program/parent_education_wage_method_execution_ledger.py --project-root .` 通过，P1-C 阻断原因收敛为 `missing_required_fields`。
- React build：`cd Product/web-react && npm run build` 通过，仍有既有 Vite chunk size warning。
- 设计污染复验：`rg -n "robot_exposure|bartik_iv|robot_density|ln_robot|行业机器人" Tasks/parent-education-wage/design.json || true` 无输出。
- Scoped diff check：P2 相关文件 `git diff --check` 通过。

### 实现范围

- `Tasks/parent-education-wage-p2-execution-readiness-bdd.md`：P2 行为契约。
- `Program/workbench/parent_education_wage_execution_readiness.py`：P2 执行准入账本生成器。
- `Program/parent_education_wage_execution_readiness.py`：P2 CLI。
- `Product/backend/product_control_p2_execution_readiness_service.py`：P2 Product Control 服务。
- `Product/app.py`：新增 `GET/POST /api/v1/projects/{project_id}/product-control/p2-execution-readiness`。
- `Product/web-react/src/components/ProductControlP0Panel.tsx`：React 产品控制面显示 P2 执行准入。
- `Product/web-react/src/styles.css`：P2 状态块样式。
- `Results/json/parent_education_wage_p2_execution_readiness.json`、`Reviews/parent_education_wage_p2_execution_readiness.md`：真实 P2 审阅层产物。

### 剩余风险

- `father_education`、`mother_education`、`parent_education` 仍缺真实字段来源。
- `hukou` 只是候选字段命中，尚未人工绑定。
- 当前不能进入正式 VariableRoleSet、DesignSpec、RunPlan 或方法执行。

## 2026-06-17 P0/P1 Acceptance Package

### 行为覆盖

- [x] React 主入口、P0 控制面、P1-A 文献证据、P1-B 字段绑定和 P1-C 方法执行 blocked ledger 已收拢成一个验收包。
- [x] 固定 Demo 题目被记录为产品链路压力测试样例，不被写成最终产品范围。
- [x] legacy 运行入口已从验收路径移除；`/legacy` 重定向到 `/`，`Product/web` 只保留为历史源码。
- [x] 正式层边界清楚：当前不写 bibliography、VariableRoleSet、RunPlan、manuscript，也不伪造 run id。

### 测试覆盖

- 验收包文件：`Reviews/parent_education_wage_p0_p1_acceptance_package.md`
- Scoped 回归：`python3 -m pytest tests/test_parent_education_wage_literature_evidence_ledger.py tests/test_parent_education_wage_data_field_binding_ledger.py tests/test_parent_education_wage_method_execution_ledger.py tests/test_product_control_p0_stage_panel.py tests/test_product_control_p0_phase.py tests/test_web_react_api_base_contract.py tests/test_p3_react_input_tabs.py -q`，38 passed, 11 subtests passed。
- Python 编译：P1-A/P1-B/P1-C Program、backend service 和 `Product/app.py` 编译通过。
- React build：`cd Product/web-react && npm run build` 通过，仍有既有 Vite chunk size warning。

### 剩余风险

- 旧 `Product/web` 物理文件未删除；本轮只从运行和验收路径移除。
- 下一阶段必须先补真实父母教育字段并审阅 `hukou` 候选，不能直接跑方法。

## 2026-06-17 P1-C Method Execution Ledger

### 行为覆盖

- [x] 行为 1：核心字段缺失时不能创建 run id 或伪造回归结果。
- [x] 行为 2：方法账本记录旧 `robot_exposure` code_stub 污染和 StatsPAI 使用边界。
- [x] 行为 3：即使不能执行，也写出 blocked/failure ledger。
- [x] 行为 4：Product API 的 GET 只读返回已有账本或 missing 状态，POST 才显式生成账本。
- [x] 行为 5：React 当前产品控制面展示 `P1-C 方法执行`、run id、方法数和缺失字段数。

### 测试覆盖

- RED：`python3 -m pytest tests/test_parent_education_wage_method_execution_ledger.py -q` 首次失败，原因是 P1-C method execution ledger 模块不存在。
- 目标测试：`python3 -m pytest tests/test_parent_education_wage_method_execution_ledger.py -q`，5 passed。
- 阶段回归：`python3 -m pytest tests/test_parent_education_wage_literature_evidence_ledger.py tests/test_parent_education_wage_data_field_binding_ledger.py tests/test_parent_education_wage_method_execution_ledger.py tests/test_product_control_p0_stage_panel.py tests/test_product_control_p0_phase.py tests/test_web_react_api_base_contract.py tests/test_p3_react_input_tabs.py -q`，38 passed, 11 subtests passed。
- Python 编译：`python3 -m py_compile Program/workbench/parent_education_wage_literature_evidence_ledger.py Program/parent_education_wage_literature_evidence_ledger.py Product/backend/product_control_p1_literature_service.py Program/workbench/parent_education_wage_data_field_binding_ledger.py Program/parent_education_wage_data_field_binding_ledger.py Product/backend/product_control_p1_data_field_service.py Program/workbench/parent_education_wage_method_execution_ledger.py Program/parent_education_wage_method_execution_ledger.py Product/backend/product_control_p1_method_service.py Product/app.py` 通过。
- React build：`cd Product/web-react && npm run build` 通过，仍有既有 Vite chunk size warning。
- 真实项目生成：`python3 Program/parent_education_wage_method_execution_ledger.py --project-root .` 通过。

### 实现范围

- `Program/workbench/parent_education_wage_method_execution_ledger.py`：新增 P1-C 方法执行账本生成器。
- `Program/parent_education_wage_method_execution_ledger.py`：新增 CLI。
- `Product/backend/product_control_p1_method_service.py`：新增 Product Control P1-C 读/刷新服务。
- `Product/app.py`：新增 `GET/POST /api/v1/projects/{project_id}/product-control/p1-method-execution`。
- `Product/web-react/src/components/ProductControlP0Panel.tsx`：在当前 React 产品控制面显示 P1-C 方法执行状态。
- `Product/web-react/src/styles.css`：复用 P1 状态块样式。
- `Results/json/parent_education_wage_method_execution_ledger.json`、`Reviews/parent_education_wage_method_execution_ledger.md`：真实项目 P1-C blocked ledger。

### 剩余风险

- 当前 `execution_allowed=false`、`run_id=null`，没有真实方法执行结果。
- IV/DID/DML 全部 blocked；缺失字段为 `father_education`、`mother_education`、`parent_education`、`hukou`。
- `Tasks/parent-education-wage/design.json` 仍有旧 robot code_stub 污染，必须先修正设计草案。

## 2026-06-17 P1-B Data Field Binding Ledger

### 行为覆盖

- [x] 行为 1：从当前 `Tasks/parent-education-wage/variables.yaml` 读取候选变量，并和真实字段来源对账。
- [x] 行为 2：字段绑定证据只能进入审阅层，不能覆盖正式 `state/product/variable_roles.json`、DesignSpec 或 RunPlan。
- [x] 行为 3：P1-B 同时输出机器可读 JSON 和人工审阅 Markdown。
- [x] 行为 4：Product API 的 GET 只读返回已有账本或 missing 状态，POST 才显式生成账本。
- [x] 行为 5：React 当前产品控制面展示 `P1-B 数据字段`、候选变量数、matched/missing 数和字段缺口状态。

### 测试覆盖

- RED：`python3 -m pytest tests/test_parent_education_wage_data_field_binding_ledger.py -q` 首次失败，原因是 P1-B data field binding 模块不存在。
- 目标测试：`python3 -m pytest tests/test_parent_education_wage_data_field_binding_ledger.py -q`，5 passed。
- 阶段回归：`python3 -m pytest tests/test_parent_education_wage_literature_evidence_ledger.py tests/test_parent_education_wage_data_field_binding_ledger.py tests/test_product_control_p0_stage_panel.py tests/test_product_control_p0_phase.py tests/test_web_react_api_base_contract.py tests/test_p3_react_input_tabs.py -q`，33 passed, 11 subtests passed。
- Python 编译：`python3 -m py_compile Program/workbench/parent_education_wage_literature_evidence_ledger.py Program/parent_education_wage_literature_evidence_ledger.py Product/backend/product_control_p1_literature_service.py Program/workbench/parent_education_wage_data_field_binding_ledger.py Program/parent_education_wage_data_field_binding_ledger.py Product/backend/product_control_p1_data_field_service.py Product/app.py` 通过。
- React build：`cd Product/web-react && npm run build` 通过，仍有既有 Vite chunk size warning。
- 真实项目生成：`python3 Program/parent_education_wage_data_field_binding_ledger.py --project-root .` 通过。

### 实现范围

- `Program/workbench/parent_education_wage_data_field_binding_ledger.py`：新增 P1-B 数据字段绑定账本生成器。
- `Program/parent_education_wage_data_field_binding_ledger.py`：新增 CLI。
- `Product/backend/product_control_p1_data_field_service.py`：新增 Product Control P1-B 读/刷新服务。
- `Product/app.py`：新增 `GET/POST /api/v1/projects/{project_id}/product-control/p1-data-field-binding`。
- `Product/web-react/src/components/ProductControlP0Panel.tsx`：在当前 React 产品控制面显示 P1-B 数据字段绑定状态。
- `Product/web-react/src/styles.css`：复用 P1 状态块样式。
- `Results/json/parent_education_wage_data_field_binding_ledger.json`、`Reviews/parent_education_wage_data_field_binding_ledger.md`：真实项目 P1-B 审阅层产物。

### 剩余风险

- 当前 12 个候选变量中 8 个 matched、4 个 missing；缺失字段为 `father_education`、`mother_education`、`parent_education`、`hukou`。
- 因核心解释变量缺失，不能进入正式变量角色确认，也不能强跑方法执行。
- `state/product/variable_roles.json` 仍是旧 training/wage 示例；本轮刻意未覆盖。

## 2026-06-17 P1-A Literature Evidence Ledger

### 行为覆盖

- [x] 行为 1：从当前 `Tasks/parent-education-wage/literature.md` 生成 seed/candidate/verified 分层账本。
- [x] 行为 2：未核验文献不能写入正式 bibliography、正式论文或 processed verified bibliography。
- [x] 行为 3：P1-A 同时输出机器可读 JSON 和人工审阅 Markdown。
- [x] 行为 4：Product API 的 GET 只读返回已有账本或 missing 状态，POST 才显式生成账本。
- [x] 行为 5：React 当前产品控制面展示 `P1-A 文献证据`、真实文献候选数、verified 数和外部核验缺口。

### 测试覆盖

- RED：`python3 -m pytest tests/test_parent_education_wage_literature_evidence_ledger.py -q` 首次失败，原因是 P1-A ledger 模块不存在。
- 回归红灯：真实项目生成时发现 parser 把 frontmatter/downstream consumers 误识别为检索 seed；补充测试后失败复现，再修复为只读取 `## 待检索方向` 段落。
- 目标测试：`python3 -m pytest tests/test_parent_education_wage_literature_evidence_ledger.py -q`，5 passed。
- 阶段回归：`python3 -m pytest tests/test_parent_education_wage_literature_evidence_ledger.py tests/test_product_control_p0_stage_panel.py tests/test_product_control_p0_phase.py tests/test_web_react_api_base_contract.py tests/test_p3_react_input_tabs.py -q`，28 passed, 11 subtests passed。
- Python 编译：`python3 -m py_compile Program/workbench/parent_education_wage_literature_evidence_ledger.py Program/parent_education_wage_literature_evidence_ledger.py Product/backend/product_control_p1_literature_service.py Product/app.py Product/backend/product_control_phase_service.py tests/test_parent_education_wage_literature_evidence_ledger.py tests/test_product_control_p0_stage_panel.py` 通过。
- React build：`cd Product/web-react && npm run build` 通过，仍有既有 Vite chunk size warning。
- 真实项目生成：`python3 Program/parent_education_wage_literature_evidence_ledger.py --project-root .` 通过。

### 实现范围

- `Program/workbench/parent_education_wage_literature_evidence_ledger.py`：新增 P1-A 文献证据账本生成器。
- `Program/parent_education_wage_literature_evidence_ledger.py`：新增 CLI。
- `Product/backend/product_control_p1_literature_service.py`：新增 Product Control P1-A 读/刷新服务。
- `Product/app.py`：新增 `GET/POST /api/v1/projects/{project_id}/product-control/p1-literature-ledger`。
- `Product/web-react/src/components/ProductControlP0Panel.tsx`：在当前 React 产品控制面显示 P1-A 文献证据状态。
- `Product/web-react/src/styles.css`：新增 P1-A 状态块样式。
- `Results/json/parent_education_wage_literature_evidence_ledger.json`、`Reviews/parent_education_wage_literature_evidence_ledger.md`：真实项目 P1-A 审阅层产物。

### 剩余风险

- 当前只有 4 个检索 seed，`verified_count=0`；尚未访问外部数据库、DOI、Google Scholar、CNKI、OpenAlex 或用户本地 Zotero/PDF。
- P1-A 产物不能支持正式论文 claim，也不能写正式 bibliography。
- 下一阶段应进入 P1-B 数据字段绑定和变量角色证据；文献外部核验需要单独授权或人工材料。

## 2026-06-17 React Main Entry P0 Correction

### 行为覆盖

- [x] 行为 1：P0 前端验收目标从 `Product/web` 旧静态工作台切换到 `Product/web-react` 当前主入口。
- [x] 行为 2：React 主入口新增 `ProductControlP0Panel`，展示 P0 状态、Agent task、Evidence Audit、`needs_evidence` 和正式层边界。
- [x] 行为 3：刷新按钮显式调用 `POST /api/v1/projects/{project_id}/product-control/p0-phase`，普通加载只读 `GET`。
- [x] 行为 4：P0 面板只显示 `待派工审阅` / `dispatch_review_required`，不提供自动执行入口。
- [x] 行为 5：`/legacy` 运行时重定向到 `/`，旧工作台不再作为产品验收入口。

### 测试覆盖

- RED：`python3 -m pytest tests/test_product_control_p0_stage_panel.py -q` 首次 4 项 React P0 测试失败，原因是 `ProductControlP0Panel` 不存在、App 未挂载、React 样式缺失。
- 目标测试：`python3 -m pytest tests/test_product_control_p0_stage_panel.py tests/test_product_control_p0_phase.py -q`，9 passed。
- React 基线：`python3 -m pytest tests/test_web_react_api_base_contract.py tests/test_p3_react_input_tabs.py -q`，14 passed, 11 subtests passed。
- React build：`cd Product/web-react && npm run build` 通过，输出到 `Product/web-dist`。
- Python 编译：`python3 -m py_compile Product/app.py Product/backend/product_control_phase_service.py tests/test_product_control_p0_stage_panel.py` 通过。

### 实现范围

- `Product/web-react/src/components/ProductControlP0Panel.tsx`：新增 React P0 控制面板。
- `Product/web-react/src/App.tsx`：在当前主工作台挂载 P0 控制面板。
- `Product/web-react/src/styles.css`：新增 P0 面板样式，并恢复 React 契约要求的软灰主题 token。
- `Product/app.py`：`/legacy` 改为 307 重定向到 `/`。
- `tests/test_product_control_p0_stage_panel.py`：前端验收从 legacy 改为 React 主入口，并新增 legacy redirect 回归。

### 剩余风险

- `Product/web` 文件仍保留为历史源码，但运行时入口已移除；若后续确认无引用，可以单独做归档/删除阶段。
- 本轮未扩大到 P1 真实文献、变量和方法执行证据链。
- 全量 pytest 未重跑，本轮只跑当前阶段 scoped 验收。

## 2026-06-17 P0 Stage Control Panel

### 行为覆盖

- [x] 行为 1：`GET /api/v1/projects/{project_id}/product-control/p0-phase` 只读返回已有 P0 report，不刷新阶段产物。
- [x] 行为 2：没有 P0 report 时返回 `p0_phase_report_missing`，并提供显式刷新入口。
- [x] 行为 3：React 主入口新增 `产品控制 P0` 面板，展示 topic、P0 状态、Agent 任务数、Evidence Audit 和作品集脚本路径。
- [x] 行为 4：面板展示 `needs_evidence` 缺口和“不能进入正式论文”的正式层边界。
- [x] 行为 5：刷新按钮显式调用 POST，并更新 `state.productControlP0Data`。
- [x] 行为 6：P0 面板只显示 `待派工审阅`，不提供自动执行入口。

### 测试覆盖

- RED：`python3 -m pytest tests/test_product_control_p0_stage_panel.py -q` 首次 6 项失败，原因是 GET 返回 405、前端没有 P0 面板/刷新函数/证据缺口展示。
- 目标测试：`python3 -m pytest tests/test_product_control_p0_stage_panel.py -q`，6 passed。
- 相关回归：`python3 -m pytest tests/test_product_control_p0_stage_panel.py tests/test_product_control_p0_phase.py tests/test_product_control_demo_topic_binding_audit.py tests/test_research_question_topic_session.py tests/test_frontend_chinese_copy.py -q`，23 passed。
- 语法检查：`python3 -m py_compile Product/backend/product_control_phase_service.py Product/backend/product_control_demo_audit_service.py Product/app.py tests/test_product_control_p0_stage_panel.py` 通过；React build 在后续纠偏阶段通过。
- Runtime preflight：`python3 scripts/25_agent_runtime_preflight.py` 输出 `PASS report=artifacts/agent_runtime_preflight_report.md`。
- Scoped diff check：本轮相关文件 `git diff --check` 通过。
- 全量 pytest：`python3 -m pytest tests -q` 输出 1457 passed、31 failed、3 skipped；失败集中在 LLM provider 配置、旧 React/P3 视觉契约、main-results 审计和 wrapper 设计接口，未作为本轮通过标准。

### 实现范围

- `Product/backend/product_control_phase_service.py`：新增只读 P0 report 服务；P0 report 增加 `agent_tasks`、`evidence_checks` 和 `formal_boundary`。
- `Product/app.py`：新增 `GET /api/v1/projects/{project_id}/product-control/p0-phase`。
- 旧记录：最初 P0 面板误落在 `Product/web` legacy 工作台；该入口已在 React Main Entry P0 Correction 中纠偏。
- `Product/web-react/src/components/ProductControlP0Panel.tsx`：当前主入口 P0 API client、面板渲染和刷新处理。
- `Product/web-react/src/styles.css`：当前主入口 `product-control-p0-*` 样式。
- `Tests/Tasks`：新增 BDD、目标测试，并更新 todo/current-stage/handoff/manifest/round-log。

### 手动/API 验收

1. 启动服务：`python3 -m uvicorn Product.app:app --host 127.0.0.1 --port 8891`。
2. 打开 React 主入口：`http://127.0.0.1:8891/?topic=父母受教育水平对子女工资收入的影响&mode=codex-supervisor`。
3. 产品 API 主仓库项目：`proj_empirical_paper_template_main` 已注册到本地产品壳，指向 `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板`。
4. API 验收：`GET /api/v1/projects/proj_empirical_paper_template_main/product-control/p0-phase` 返回 `p0_phase_ready_for_review`、topic 为“父母受教育水平对子女工资收入的影响”、6 个 Agent tasks、3 个 `needs_evidence`。
5. React 静态契约验收：`ProductControlP0Panel.tsx` 包含 `product-control-p0-panel`、`handleRefreshProductControlP0`、`needs_evidence`、`待派工审阅`、`不能进入正式论文`；`/legacy` 307 重定向到 `/`。

### 剩余风险

- Playwright 截图级浏览器验收仍需在运行服务后补。
- FastAPI 根路径 `/` 当前服务 React build；`/legacy` 不再作为工作台入口。
- P0 CLI 摘要尚未实现，但前端/API 已满足当前验收。
- 全量 pytest 仍有 31 个历史/环境相关失败；本轮没有扩大范围修复。

## 2026-05-25 P3-B React Workbench Design Contract

### 行为覆盖

- [x] 行为 1：React 工作台明确 10 个一级模块，后续不再按后端技术对象随意堆页面。
- [x] 行为 2：每个模块默认只显示当前决策和少量关键信号，详情通过右侧 Drawer 或按需展开。
- [x] 行为 3：视觉语言锁定黑白灰、低对比、DottedSurface、禁止防守性文案和非 SaaS landing page。
- [x] 行为 4：交互路径从输入题目开始，逐步进入任务书、递归搜索、变量确认、方法前提、执行实验、finding 审阅、证据绑定和导出预检。

### 测试覆盖

- RED：`python3 -m unittest tests.test_p3_design_contract -v` 首次失败，原因是 `docs/architecture-v2/codex-phase-p3-react-workbench-design-contract.md` 尚不存在。
- 目标测试：`python3 -m unittest tests.test_p3_design_contract -v`，4 tests OK。

### 实现范围

- `docs/architecture-v2/codex-phase-p3-react-workbench-design-contract.md`：新增 React 工作台模块设计契约，定义 10 个模块、信息披露、右侧 Drawer、视觉语言和实现顺序。
- `tests/test_p3_design_contract.py`：新增契约测试，防止后续模块接入时重新回到信息过载和防守性文案。
- `Tasks/todo.md`、`Tasks/review.md`、`Tasks/manifest.md`、`Tasks/decision-log.md`、`Tasks/handoff.md`、`Tasks/lessons.md`：写回本轮状态、设计决策和后续规则。

### 手动验收

1. 打开 `docs/architecture-v2/codex-phase-p3-react-workbench-design-contract.md`。
2. 检查“模块设计契约”是否覆盖研究入口、任务队列、递归搜索、数据与变量、方法设计、执行实验、结果解释、论文草稿、复现导出、Agent 审计。
3. 检查每个模块是否说明主屏默认显示什么、详情在哪里展开、什么动作会进入正式层确认。
4. 打开 `http://127.0.0.1:8770/react`，当前页面仍是输入器和阶段导航；下一轮会按该契约接第一个真实模块。

### 剩余风险

- 本轮是设计契约和测试锁定，未新增可见 UI 模块；视觉验收仍沿用上一轮 `/react` 输入器和点阵背景页面。
- 右侧审计 Drawer、任务队列和递归搜索还没有在 React 新入口实现；P3-C 必须按契约逐个接入，而不是一次性铺满。
- Three.js 引入后 Vite 仍有 bundle size warning；后续模块化时需要考虑 lazy loading 或 chunk 拆分。

## 2026-05-22 Long-run Optimization Protocol

### 行为覆盖

- [x] 行为 1：当长程任务超过两轮或出现重复失败时，执行者有明确入口读取协议并记录轮次。
- [x] 行为 2：当同类微调进入平台期时，流程要求先定位瓶颈，再选择结构性不同的策略跃迁。
- [x] 行为 3：策略跃迁后的完成声明必须绑定证据路径，不能只依赖骨架文档、mock JSON 或 UI 状态。
- [ ] 未覆盖行为：下一轮真实 P2-AA 或研究执行任务尚未按新模板跑完整闭环。

### 测试覆盖

- 测试文件：无代码改动，未新增自动化测试。
- 运行命令：使用文件存在性、关键词检索和 diff 空白检查验证文档落点。
- 结果：`test -f`、`rg` 链路检索和 `git diff --check` 均通过。

### 实现范围

- 新增 `docs/architecture-v2/long-run-optimization-protocol.md`：项目级长时间优化协议。
- 新增 `Tasks/round-log.md`：轮次账本与首轮流程固化记录。
- 更新 `Tasks/long-run-iteration-plan.md`、`Tasks/workflow.md`、`Tasks/manifest.md`、`Tasks/decision-log.md`、`Tasks/todo.md`：把协议接入现有任务入口。

### 手动验收

1. 打开 `Tasks/todo.md`，确认下一轮开始前有明确待办要求使用 `Tasks/round-log.md`。
2. 打开 `Tasks/round-log.md`，确认模板包含目标、平台期、瓶颈、策略、回滚点和证据路径。
3. 打开 `docs/architecture-v2/long-run-optimization-protocol.md`，确认平台期触发与策略跃迁规则完整。

### 剩余风险

- 本轮只固化流程，不证明下一轮执行者一定遵守；需要在下一次 P2-AA 或研究执行任务中实际使用并补充 round entry。

## 2026-05-17 Pipeline MVP Review

### 行为覆盖

- [x] 首页先显示研究选题入口，已确认选题为“机器人应用是否影响劳动力市场匹配效率？”。
- [x] SupervisorPlan 显示 Codex 计划、中控边界和人工审批状态；已批准计划显示 `人工审批 已批准`。
- [x] Agent Task Queue 默认摘要优先，任务已人工派工审阅，但 `can_execute=false`，不会直接执行。
- [x] Data & Variables 区分真实字段候选、候选草稿和正式 VariableRoleSet。
- [x] Design / Execution 显示方法 workflow checklist：OLS ready，DID/IV/RDD 继续展示缺少的前置条件。
- [x] Results & Draft 显示 FindingCard、Manuscript candidate 和 provenance。
- [x] Review & Export 显示 Reviewer Scorecard、Verifier Gates；`can_export_docx=false` 时最终 docx 导出按钮 disabled。

### 测试覆盖

- RED：新增两条前端契约后，目标测试先失败，原因分别是 approved SupervisorPlan 仍显示 `尚未审批`，以及 docx 最终导出按钮缺少稳定 id。
- 目标测试：`python3 -m unittest tests.test_supervisor_plan.SupervisorPlanFrontendTests tests.test_verifier_export_gates.VerifierExportGatesFrontendTests -v`，6 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，258 tests OK，skipped=1。
- 静态检查：`python3 -m py_compile Product/app.py Product/backend/*.py` 通过；`node --check Product/web/assets/app.js` 通过；`git diff --check` 通过。

### 实现范围

- `Product/web/assets/app.js`：新增 SupervisorPlan 人工审阅 label 兼容逻辑；已批准状态不再误报未审批。
- `Product/web/index.html`：更新静态资源版本，并给 docx 最终导出按钮增加稳定 id。
- `tests/test_supervisor_plan.py`：锁定 approved SupervisorPlan 的前端文案行为。
- `tests/test_verifier_export_gates.py`：锁定 docx 最终导出按钮选择器，方便浏览器验收。
- `Tasks/*`：记录 Pipeline MVP Review 的真实验收、风险和下一步。

### 手动验收

1. 打开 `http://127.0.0.1:8768/?v=20260517-pipeline-mvp-review-final2`。
2. 首页检查：选题已确认；智能中控区域显示 Codex Supervisor 计划，人工审批为 `已批准`。
3. 首页 Agent Task Queue 检查：摘要在前，任务详情可展开；3 个任务都已审阅但仍不能执行。
4. 点击 `数据与设计`：确认真实字段候选、草稿和正式变量角色没有混在一起。
5. 点击 `实证执行 / 工具 -> 研究设计细节`：确认 OLS 可执行，DID/IV/RDD 显示阻塞原因。
6. 点击 `结果与草稿`：确认 FindingCard 与正文候选都能看到来源和证据等级。
7. 点击 `审阅与导出`：确认评分卡、核验门、8 个 verifier rows；`docx 最终导出` 按钮 disabled。
8. 截图留档：`artifacts/ui-checks/pipeline-mvp-home.png`、`pipeline-mvp-data-variables.png`、`pipeline-mvp-execution.png`、`pipeline-mvp-review-export.png`。

### 剩余风险

- 当前浏览器验收修改了 gitignored runtime 状态 `state/product/agent_task_queue.json`，3 个任务为已审阅但不可执行；这是验收状态，不应误当成可提交配置。
- 当前 MVP 仍未把 reviewed task 接入真实执行后端选择；StatsPAI/Python/StataMCP 的任务调度、日志和 evaluator checks 是 P2-AA。
- Verifier 当前正确阻断最终 docx 导出；还没有实现最终 docx 生成与写回审批。
- 真实 `.dta`、DID/IV/RDD/PSM/DML 仍未形成 `local_execution` 证据，页面只展示前置条件和阻塞原因。

## 2026-05-17 P2-V Human Dispatch Audit

### 行为覆盖

- [x] 队列 item 创建后不能直接执行，`can_execute=false`。
- [x] 未经审阅的 item 暴露 `dispatch_review_required` 阻塞。
- [x] 用户批准派工后，item 进入 `reviewed_for_dispatch`，记录 reviewer、note、timestamp、`evidence_level=local_file`。
- [x] 用户阻断派工后，item 进入 `blocked` 并保留阻断原因。
- [x] 派工审阅不修改 ResearchQuestion、VariableRoleSet、DesignSpec、RunPlan 或 SupervisorPlan。
- [x] 前端默认折叠输入证据、输出要求、风险和审计日志，只保留派工动作。

### 测试覆盖

- RED：`python3 -m unittest tests/test_agent_task_dispatch_audit.py -v` 首轮失败原因符合预期：缺少 `can_execute`、dispatch-review API 404、前端缺少 `reviewDispatch`。
- 目标测试：`python3 -m unittest tests/test_agent_task_dispatch_audit.py -v`，5 tests OK。
- 相邻回归：`python3 -m unittest tests/test_agent_task_queue.py tests/test_product_workflow_contract.py -v`，21 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，239 tests OK，skipped=1。
- 静态检查：`python3 -m py_compile Product/app.py Product/backend/*.py` 通过；`node --check Product/web/assets/app.js` 通过；`git diff --check` 通过。

### 实现范围

- `docs/architecture-v2/codex-phase-p2-dispatch-audit-bdd.md`：新增派工审阅行为契约。
- `tests/test_agent_task_dispatch_audit.py`：新增后端/API/前端契约测试。
- `Product/backend/task_dispatch_service.py`：新增派工审阅状态机。
- `Product/backend/agent_task_queue_service.py`：扩展队列 item 默认字段和响应摘要。
- `Product/app.py`：新增 dispatch-review API。
- `Product/web/assets/app.js`：新增派工审阅 API、渲染和事件处理。
- `Product/web/assets/styles.css`：新增派工审阅区和五列摘要样式。

### 手动验收

1. 启动服务：`python3 -m uvicorn Product.app:app --host 127.0.0.1 --port 8768`。
2. 打开 `http://127.0.0.1:8768/?v=20260517-p2v-dispatch-audit`。
3. 首页 `Agent 任务队列` 应显示任务摘要和派工审阅区。
4. `查看任务详情` 默认折叠；展开后才看到输入证据、输出要求、风险和审计日志。
5. 点击第一项 `批准派工` 后，摘要中的已审阅数量应增加，任务状态显示已通过派工审阅，下一步为选择执行后端。
6. 浏览器自动化验收结果：队列可见、3 个批准按钮可见、5 个 details 默认折叠、点击批准后显示已审阅/选择执行后端、console errors=0。

### 剩余风险

- P2-V 仍不执行子 Agent；批准派工后只是进入 `reviewed_for_dispatch`，后续还要做执行后端选择和真实日志产出。
- 本轮浏览器成功态使用本地 gitignored `state/product/supervisor_plan.json` 和 `state/product/agent_task_queue.json` 做验收状态，不会提交到仓库。
- StatsPAI/StataMCP/Python 的真实调度仍是 P2-X/P2-W 后续任务；不能把派工审阅误解成统计后端已经执行。
- 真实 CFPS 字段候选仍需 P2-W 写入正式 VariableRoleSet，再重建 DesignSpec / RunPlan 后才能进入论文分析。

## 验证记录

- 2026-05-12：`python3 -m unittest discover -s tests -v`，48 tests OK，skipped=1。
- 2026-05-12：`python3 -m unittest tests.test_observable_execution_frontend -v`，先失败，原因是 P0 前端 DOM/JS/CSS 还没有真实 observability 元素和函数。
- 2026-05-12：补第 7 条历史 run 边界后，`python3 -m unittest tests.test_observable_execution_frontend -v` 先失败，原因是缺少 `handleMissingRunObservability` 和 404 恢复态。
- 2026-05-12：`python3 -m unittest tests.test_observable_execution_frontend -v`，7 tests OK。
- 2026-05-12：`python3 -m unittest tests.test_observable_execution -v`，2 tests OK。
- 2026-05-12：`python3 -m unittest tests.test_agent_cluster_frontend_interactions -v`，10 tests OK。
- 2026-05-12：`node --check Product/web/assets/app.js`，通过。
- 2026-05-12：`python3 -m py_compile Program/run_paper.py Program/workbench/observability.py Product/backend/observability_service.py Product/backend/project_service.py Product/app.py`，通过。
- 2026-05-12：`python3 -m unittest discover -s tests -v`，55 tests OK，skipped=1，最终一次耗时 4.065s。
- 2026-05-12：本地服务 `python3 -m uvicorn Product.app:app --host 127.0.0.1 --port 8877` 启动成功；浏览器打开 `http://127.0.0.1:8877`。
- 2026-05-12：浏览器点击“实证执行”后，真实 run `run_3ffe1e6c1f53` 渲染 Step Board、Event Stream、Human-in-the-loop、Artifacts / Evidence。
- 2026-05-12：浏览器切换到历史 run `run_c617f095b232`，页面显示“缺少可观察执行轨迹”和“点击启动试运行”的恢复提示。
- 2026-05-12：浏览器量测 Step 卡片宽度 368.8px，小于 387.8px 容器宽度，修复长 metadata 撑破面板的问题。
- 2026-05-12：API 验证 `GET /api/v1/projects/proj_undergraduate_thesis/runs/run_3ffe1e6c1f53/observability` 返回 `_meta.evidence_level=local_execution`、7 个 steps、24 个 events、2 个 gates。
- 2026-05-12：新增 P1 gate resolve 测试后先失败，`POST /api/v1/projects/{project_id}/runs/{run_id}/gates/{gate_id}/resolve` 返回 404，确认失败原因是路由/服务未实现。
- 2026-05-12：`python3 -m unittest tests.test_observable_execution.ObservableExecutionTests.test_bdd_3_gate_resolve_api_updates_gate_event_and_manifest -v`，通过。
- 2026-05-12：`python3 -m unittest tests.test_observable_execution -v`，3 tests OK。
- 2026-05-12：最终回归 `python3 -m unittest discover -s tests -v`，56 tests OK，skipped=1，耗时 5.193s。
- 2026-05-12：新增 P1-A 前端行为 5-8 后，`python3 -m unittest tests.test_observable_execution_frontend -v` 先失败 4 条，原因是前端缺少 gate resolve 控件、API client、刷新和 resolved 展示。
- 2026-05-12：实现 P1-A 前端后，`python3 -m unittest tests.test_observable_execution_frontend -v`，10 tests OK。
- 2026-05-12：`node --check Product/web/assets/app.js`，通过。
- 2026-05-12：`python3 -m py_compile Program/run_paper.py Program/workbench/observability.py Product/backend/observability_service.py Product/backend/project_service.py Product/app.py`，通过。
- 2026-05-12：最终回归 `python3 -m unittest discover -s tests -v`，59 tests OK，skipped=1，耗时 5.570s。
- 2026-05-12：浏览器打开 `http://127.0.0.1:8765/?v=20260512-p1a`，实证执行页显示 confirm/reject/adjust 和 note。
- 2026-05-12：浏览器填写 `gate_dataset_fields` 处理说明并点击确认后，页面显示 `action=confirm`、note、resolved_at；事件流包含 resolved 事件；console errors=0。
- 2026-05-12：P1-B 新增/扩展数据入口测试后先失败，失败原因包括 datasets API 仍为 `mock`、run response 缺少 `dataset_source`、前端缺少数据集启动按钮和 `dataset_path` payload。
- 2026-05-12：`python3 -m unittest tests.test_api_contract_v2.ApiContractV2Tests.test_bdd_3_datasets_list_local_files_as_local_file_evidence -v`，通过。
- 2026-05-12：`python3 -m unittest tests.test_product_v1_local.ProductV1LocalTests.test_run_endpoint_records_selected_dataset_source -v`，通过。
- 2026-05-12：`python3 -m unittest tests.test_product_v1_local.ProductV1LocalTests.test_run_endpoint_rejects_invalid_dataset_source -v`，通过。
- 2026-05-12：`python3 -m unittest tests.test_dataset_frontend -v`，4 tests OK。
- 2026-05-12：`node --check Product/web/assets/app.js`，通过。
- 2026-05-12：`python3 -m py_compile Product/backend/overview_service.py Product/backend/project_service.py Product/app.py Program/run_paper.py Program/workbench/observability.py Product/backend/observability_service.py`，通过。
- 2026-05-12：`python3 -m unittest discover -s tests -v`，65 tests OK，skipped=1，耗时 11.121s。
- 2026-05-12：API 验证 `GET /api/v1/projects/proj_undergraduate_thesis/datasets` 返回 `analysis_sample.csv`，`row_count=12`、`column_count=4`、`role=configured_final_dataset`、`evidence_level=local_file`。
- 2026-05-12：API 验证 `POST /api/v1/projects/proj_undergraduate_thesis/runs` 携带 `dataset_path=Data/Final/analysis_sample.csv` 后生成 `run_b87d95f7d053`，response 与 manifest 都包含 `dataset_source`。
- 2026-05-12：浏览器打开 `http://127.0.0.1:8765/?v=20260512-p1b3`，数据页显示真实本地数据文件；点击“用此数据启动试运行”生成 `run_fc725d15b3c0`，manifest 包含 `dataset_source.evidence_level=local_file`；console errors/warnings=0。
- 2026-05-12：P1-C 新增 observability 顶层 dataset_source 测试后先失败，原因是 API 只在 `manifest.dataset_source` 中返回；新增前端数据源面板测试后先失败，原因是 HTML/JS/CSS 缺少 `observable-dataset-source`。
- 2026-05-12：`python3 -m unittest tests.test_observable_execution.ObservableExecutionTests.test_bdd_3_observability_exposes_dataset_source_as_run_evidence -v`，通过。
- 2026-05-12：`python3 -m unittest tests.test_observable_execution_frontend.ObservableExecutionFrontendTests.test_bdd_11_execution_page_shows_run_dataset_source -v`，通过。
- 2026-05-12：`python3 -m unittest tests.test_observable_execution -v`，4 tests OK。
- 2026-05-12：`python3 -m unittest tests.test_observable_execution_frontend -v`，11 tests OK。
- 2026-05-12：`python3 -m unittest tests.test_product_v1_local.ProductV1LocalTests.test_run_endpoint_records_selected_dataset_source -v`，通过。
- 2026-05-12：`python3 -m py_compile Product/backend/observability_service.py Product/backend/project_service.py Product/app.py`，通过。
- 2026-05-12：`node --check Product/web/assets/app.js`，通过。
- 2026-05-12：`python3 -m unittest discover -s tests -v`，67 tests OK，skipped=1，耗时 36.309s。
- 2026-05-12：API 验证 `GET /api/v1/projects/proj_undergraduate_thesis/runs/run_641c9770a1a8/observability` 返回顶层 `dataset_source` 和 `manifest.dataset_source`，均包含 `path=Data/Final/analysis_sample.csv`、`evidence_level=local_file`、`role=configured_final_dataset`、`row_count=12`、`column_count=4`。
- 2026-05-12：浏览器打开 `http://127.0.0.1:8765/?v=20260512-p1c`，从数据页启动 `run_641c9770a1a8`，执行页 Run 数据源面板显示 `analysis_sample.csv`、相对路径、本地文件、12 行 4 列、csv、configured_final_dataset；console errors/warnings=0。
- 2026-05-12：P1-D 新增 variable_roles API 测试后先失败，原因是 observability 顶层缺少 `variable_roles`；新增前端测试后先失败，原因是缺少 `observable-variable-roles`。
- 2026-05-12：`python3 -m unittest tests.test_observable_execution.ObservableExecutionTests.test_bdd_5_observability_exposes_variable_roles_and_confirmation_gate -v`，通过。
- 2026-05-12：`python3 -m unittest tests.test_observable_execution_frontend.ObservableExecutionFrontendTests.test_bdd_12_execution_page_shows_variable_roles_confirmation -v`，通过。
- 2026-05-12：`python3 -m unittest tests.test_observable_execution -v`，5 tests OK。
- 2026-05-12：`python3 -m unittest tests.test_observable_execution_frontend -v`，12 tests OK。
- 2026-05-12：`python3 -m py_compile Product/backend/observability_service.py Product/backend/project_service.py Product/app.py`，通过。
- 2026-05-12：`node --check Product/web/assets/app.js`，通过。
- 2026-05-12：`python3 -m unittest discover -s tests -v`，69 tests OK，skipped=1，耗时 8.408s。
- 2026-05-12：API 验证 `GET /api/v1/projects/proj_undergraduate_thesis/runs/run_641c9770a1a8/observability` 返回 `variable_roles.evidence_level=local_execution`、`confirmation_gate_id=gate_dataset_fields`、`confirmation_status=open`。
- 2026-05-12：浏览器打开 `http://127.0.0.1:8765/?v=20260512-p1d`，变量角色确认面板显示 `outcome=wage`、`treatment=trained`、`controls=edu, experience`、`instruments=未识别`；console errors/warnings=0。
- 2026-05-12：P1-UI 新增紧凑控制台行为后，`python3 -m unittest tests.test_observable_execution_frontend.ObservableExecutionFrontendTests.test_bdd_13_execution_page_uses_dense_console_layout -v` 先失败，原因是缺少 `execution-control-panel`。
- 2026-05-12：实现 P1-UI 后，`python3 -m unittest tests.test_observable_execution_frontend -v`，13 tests OK。
- 2026-05-12：`python3 -m py_compile Program/run_paper.py Program/workbench/observability.py Product/backend/observability_service.py Product/backend/project_service.py Product/app.py`，通过。
- 2026-05-12：`node --check Product/web/assets/app.js`，通过。
- 2026-05-12：最终回归 `python3 -m unittest discover -s tests -v`，70 tests OK，skipped=1，耗时 5.553s。
- 2026-05-12：浏览器打开 `http://127.0.0.1:8765/?v=20260512-p1ui3`，实证执行页桌面 computed style：system font、panel radius 8px、padding 12px、context grid 两列、overflowCount=0。
- 2026-05-12：移动端 390x844 验收：上下文网格折叠单列、toolbar 为 column、metadata `pre-wrap`、overflowCount=0。
- 2026-05-12：产品重置新增 `tests/test_product_workflow_contract.py` 后先失败：2 条 API 测试因 `KeyError: workflow_contract` 报错，4 条前端测试因缺少 5 个工作区、`renderWorkflowContract`、`data-open-design-action`、`renderExecutionPreflight` 失败。
- 2026-05-12：实现产品重置后，`python3 -m unittest tests.test_product_workflow_contract tests.test_dataset_frontend tests.test_observable_execution_frontend -v`，23 tests OK。
- 2026-05-12：`python3 -m py_compile Program/run_paper.py Program/workbench/observability.py Product/backend/observability_service.py Product/backend/project_service.py Product/backend/overview_service.py Product/app.py`，通过。
- 2026-05-12：`node --check Product/web/assets/app.js`，通过。
- 2026-05-12：最终回归 `python3 -m unittest discover -s tests -v`，76 tests OK，skipped=1，耗时 6.385s。
- 2026-05-12：重启 8765 后浏览器打开 `http://127.0.0.1:8765/?v=20260512-flow2`；Workspace Home 显示 5 个工作区、`confirm_variable_roles` 下一步、9 个 workflow spine 阶段；console errors/warnings=0。
- 2026-05-12：Data & Design 浏览器验收显示 `analysis_sample.csv`、`Data/Final/analysis_sample.csv`、`本地文件`、`12 行 · 4 列 · csv · configured_final_dataset` 和“检查并确认变量角色”，页面文本不再包含“用此数据启动试运行”。
- 2026-05-12：Execution 浏览器验收显示 `can_start_full_run=false`、`variable_roles_unconfirmed`、`design_unconfirmed`、`run_plan_missing`，并保留当前 run evidence；桌面和 390x844 移动端均无横向溢出。
- 2026-05-13：P1-E 新增 `tests/test_variable_role_confirmation.py` 后，`python3 -m unittest tests.test_variable_role_confirmation -v` 首次 5 条失败；失败原因为变量角色 API 404、前端缺少 `variable-role-confirmation-form`、`renderVariableRoleEditor` 与保存 API。
- 2026-05-13：实现 P1-E 后，`python3 -m unittest tests.test_variable_role_confirmation -v`，5 tests OK。
- 2026-05-13：P1-E 目标回归 `python3 -m unittest tests.test_variable_role_confirmation tests.test_product_workflow_contract tests.test_dataset_frontend tests.test_observable_execution_frontend tests.test_api_contract_v2 -v`，39 tests OK。
- 2026-05-13：P1-E 编译/语法 `python3 -m py_compile Product/app.py Product/backend/overview_service.py Product/backend/variable_role_service.py Product/backend/project_service.py Product/backend/observability_service.py Program/run_paper.py Program/workbench/observability.py` 通过；`node --check Product/web/assets/app.js` 通过。
- 2026-05-13：P1-E 最终回归 `python3 -m unittest discover -s tests -v`，81 tests OK，skipped=1，耗时 8.594s。
- 2026-05-13：浏览器打开 `http://127.0.0.1:8765/?v=20260513-p1e`；Data & Variables 显示 VariableRoleSet 编辑器，初始 draft 为 `outcome=wage`、`treatment=trained`、`controls=edu, experience`。
- 2026-05-13：浏览器填写 note 并保存后，VariableRoleSet 状态为 `approved · local_file`，meta 为 `Data/Final/analysis_sample.csv · version=1 · evidence_level=local_file`，`state/product/variable_roles.json` 写入真实本地状态。
- 2026-05-13：保存后 Overview API 显示 `workflow_contract.next_action.id=confirm_design_spec`，blockers 只剩 `design_unconfirmed`、`run_plan_missing`；Execution preflight 继续显示 `CAN_START_FULL_RUN=FALSE`，console errors/warnings=0。
- 2026-05-13：交接收尾后复查 `python3 -m unittest tests.test_variable_role_confirmation -v`，5 tests OK；`node --check Product/web/assets/app.js` 通过；`curl http://127.0.0.1:8765/` 确认 CSS/JS 版本为 `20260513-p1e`；`curl /overview` 确认 `confirm_design_spec` 和 `design_unconfirmed/run_plan_missing`，未出现 `variable_roles_unconfirmed`。
- 2026-05-13：P1-F/P1-G 新增 `tests/test_design_run_plan_state_machine.py` 后，`python3 -m unittest tests.test_design_run_plan_state_machine -v` 首次 7 条失败；失败原因为 DesignSpec/RunPlan API 返回 404，前端缺少 `design-spec-confirmation-form`、`run-plan-confirmation-form`、`renderDesignSpecEditor`、`renderRunPlanEditor` 和保存 API。
- 2026-05-13：实现 P1-F/P1-G 后，`python3 -m unittest tests.test_design_run_plan_state_machine -v`，7 tests OK。
- 2026-05-13：P1-F/P1-G 目标回归 `python3 -m unittest tests.test_design_run_plan_state_machine tests.test_variable_role_confirmation tests.test_product_workflow_contract tests.test_dataset_frontend tests.test_observable_execution_frontend tests.test_api_contract_v2 -v`，46 tests OK。
- 2026-05-13：P1-F/P1-G 编译/语法 `node --check Product/web/assets/app.js` 通过；`python3 -m py_compile Product/app.py Product/backend/overview_service.py Product/backend/variable_role_service.py Product/backend/design_spec_service.py Product/backend/project_service.py Product/backend/observability_service.py Program/run_paper.py Program/workbench/observability.py` 通过。
- 2026-05-13：浏览器打开 `http://127.0.0.1:8765/?v=20260513-p1fg`；初始 `workflow_contract.next_action.id=confirm_design_spec`，blockers 为 `design_unconfirmed/run_plan_missing`，页面存在 DesignSpec 与 RunPlan 表单。
- 2026-05-13：浏览器保存 DesignSpec 后，页面状态为 `approved · local_file`，Overview API 显示 `workflow_contract.next_action.id=confirm_run_plan`，blockers 只剩 `run_plan_missing`，`state/product/design_spec.json` 写入真实本地状态。
- 2026-05-13：浏览器保存 RunPlan 后，页面状态为 `approved · local_file`，Overview API 显示 `workflow_contract.next_action.id=start_full_run`、blockers 为空、`can_start_full_run=true`，`state/product/run_plan.json` 写入真实本地状态；console errors/warnings=0，Execution 页面无横向溢出。
- 2026-05-13：P1-F/P1-G 最终回归 `python3 -m unittest discover -s tests -v`，88 tests OK，skipped=1，耗时 83.833s。
- 2026-05-13：P1-H 新增 `tests/test_full_run_from_run_plan.py` 后，`python3 -m unittest tests.test_full_run_from_run_plan -v` 首次 3 条失败；失败原因为 `POST /api/v1/projects/{project_id}/runs/full` 返回 405，前端缺少 `observable-run-full-button`、`v2api.runs.startFull`、`createFullRunFromPlan`。
- 2026-05-13：实现 P1-H 后，`python3 -m unittest tests.test_full_run_from_run_plan -v`，3 tests OK。
- 2026-05-13：P1-H 目标回归 `python3 -m unittest tests.test_full_run_from_run_plan tests.test_design_run_plan_state_machine tests.test_product_v1_local tests.test_observable_execution tests.test_observable_execution_frontend tests.test_product_workflow_contract -v`，39 tests OK。
- 2026-05-13：P1-H 编译/语法 `node --check Product/web/assets/app.js` 通过；`python3 -m py_compile Product/app.py Product/backend/project_service.py Product/backend/design_spec_service.py Product/backend/overview_service.py Product/backend/observability_service.py` 通过。
- 2026-05-13：重启 8765 后浏览器打开 `http://127.0.0.1:8765/?v=20260513-p1h`；Overview API 显示 `next_action=start_full_run`、blockers 为空、`can_start_full_run=true`；Execution 页面完整执行按钮存在且未禁用。
- 2026-05-13：浏览器点击“启动完整实证执行”后生成 `run_c424d6a11af7`；run store 显示 `mode=full-run`、`status=succeeded`、`execution_evidence_level=local_execution`、`plan_binding.run_plan_version=1`、`research_engine.embedded=false`。
- 2026-05-13：`GET /api/v1/projects/proj_undergraduate_thesis/runs/run_c424d6a11af7/observability` 返回 `_meta.evidence_level=local_execution`，manifest 包含 `run_plan_binding.evidence_level=local_file` 与 `research_engine.integration_mode=callable_external`。
- 2026-05-13：浏览器 console errors/warnings=0；run selector 选中 `run_c424d6a11af7 · succeeded · full-run`。
- 2026-05-13：P1-H 最终回归 `python3 -m unittest discover -s tests -v`，91 tests OK，skipped=1，耗时 6.591s。

## 风险

- `run_3ffe1e6c1f53` 的 `gate_dataset_fields` 已在浏览器验收中被处理；继续验收开放 gate 时使用 `gate_research_question` 或重新启动试运行。
- `Product/serve_product.py` 直接执行会因为顶层包导入路径失败，后续应单独补测试修复。
- Playwright 选择下拉时一次 `browser_select_option` 权限审核超时，改用页面内 JS 派发 change 事件完成验收。
- 当前数据入口只支持项目内相对路径，不支持 multipart 上传或任意外部路径。
- VariableRoleSet 已可结构化编辑并持久化，但 `state/product/variable_roles.json` 当前是本地 runtime artifact，未决定是否纳入版本控制或迁移为 fixture。
- DesignSpec/RunPlan 已可结构化确认并持久化，但 `state/product/design_spec.json`、`state/product/run_plan.json` 当前是本地 runtime artifacts，未决定是否纳入版本控制或迁移为 fixture。
- P1-UI 只修正了实证执行页，没有重做数据页、研究设计页和 Agent 控制台的视觉一致性。
- `workflow_contract` 已读取真实已确认 VariableRoleSet、DesignSpec、RunPlan 状态；`start_full_run` 已接入非开发式完整执行按钮与后端路径。
- full run 仍复用当前 `Program/run_paper.py` 本地 pipeline；Feynman 目前只作为 callable external research engine metadata 和后续 provider 设计方向，并未实际调用 Feynman CLI。

## 未完成项

- P1-I 已完成：Results & Draft 能从 `run_c424d6a11af7` 生成最小 FindingCard 和 DraftSection evidence binding。
- multipart 上传或外部文件导入。
- `Product/serve_product.py` 直接执行入口修复。
- 继续把 CoPaper/StatsPAI 的步骤方法论落到“用户调整变量角色 -> 系统重跑识别/建模 -> 产物更新”的闭环。
- Findings / Manuscript / Artifacts / Agents 还未展开为完整 8 板块工作台；现在 Results & Draft 已有最小 evidence binding，下一步应做 claim review / accept-for-writing 状态。

## 2026-05-13 P1-I Results & Draft Evidence Binding

- 失败测试：`python3 -m unittest tests.test_results_draft_evidence_binding -v` 首次有效失败为 API 404 和前端缺少 `results-findings-list`、`draft-evidence-sections`、`v2api.resultsDraft.get`、`renderResultsDraftEvidence`。
- 目标测试：`python3 -m unittest tests.test_results_draft_evidence_binding -v`，4 tests OK。
- 目标回归：`python3 -m unittest tests.test_results_draft_evidence_binding tests.test_full_run_from_run_plan tests.test_design_run_plan_state_machine tests.test_product_workflow_contract tests.test_api_contract_v2 -v`，31 tests OK。
- 静态检查：`node --check Product/web/assets/app.js` 通过；`python3 -m py_compile Product/app.py Product/backend/results_draft_service.py Product/backend/draft_service.py Product/backend/project_service.py` 通过。
- API 验收：`GET /api/v1/projects/proj_undergraduate_thesis/results-draft` 返回 `latest_run_id=run_c424d6a11af7`，FindingCard 绑定 `Results/json/analysis_result.json`，DraftSection 绑定 `Manuscripts/generated/paper_draft.md` 和 `claim_evidence_level=local_execution`。
- 浏览器验收：`http://127.0.0.1:8765/?v=20260513-p1i` 的 Results & Draft 页面显示 `trained effect on wage`、`run_id=run_c424d6a11af7`、`run_plan_version=1`、`Results/json/analysis_result.json`；草稿章节显示 `本地文件` 和 `真实执行`；overflowCount=0，console errors/warnings=0。
- 全量回归：`python3 -m unittest discover -s tests -v`，95 tests OK，skipped=1，耗时 6.788s。

## 2026-05-13 P1-J Claim Review / Accept-for-writing

- 失败测试：`python3 -m unittest tests.test_results_draft_evidence_binding -v` 首次 P1-J 失败为 `KeyError: review_status`、review API 404、前端缺少 `reviewFinding` / `data-finding-review-action`。
- 目标测试：`python3 -m unittest tests.test_results_draft_evidence_binding -v`，8 tests OK。
- 目标回归：`python3 -m unittest tests.test_results_draft_evidence_binding tests.test_full_run_from_run_plan tests.test_design_run_plan_state_machine tests.test_product_workflow_contract tests.test_api_contract_v2 -v`，35 tests OK。
- 静态检查：`node --check Product/web/assets/app.js` 通过；`python3 -m py_compile Product/app.py Product/backend/results_draft_service.py Product/backend/draft_service.py Product/backend/project_service.py` 通过。
- API 验收：`PUT /api/v1/projects/proj_undergraduate_thesis/results-draft/findings/finding_trained_effect/review` 返回 `review_status=approved`、`evidence_level=local_file`、`run_id=run_c424d6a11af7`、`artifact_path=Results/json/analysis_result.json`、`can_write_to_draft=true`。
- 浏览器验收：`http://127.0.0.1:8765/?v=20260513-p1j` 的 Results & Draft 页面显示 `review_status=approved`、`accept-for-writing=yes`、approve/needs_revision/reject 三个操作、审阅备注和 `review evidence: 本地文件`；overflowCount=0，console errors/warnings=0。
- 全量回归：`python3 -m unittest discover -s tests -v`，99 tests OK，skipped=1，耗时 13.177s。

## 2026-05-13 P1-K Manuscript Consumption

- 失败测试：`python3 -m unittest tests.test_manuscript_consumption -v` 首次 5 条失败；API 测试因 `/api/v1/projects/{project_id}/manuscript-candidates` 返回 404，前端测试因缺少 `manuscript-candidates-list`、`v2api.manuscriptCandidates.get`、`renderManuscriptCandidates`、provenance 渲染标识失败。
- 目标测试：`python3 -m unittest tests.test_manuscript_consumption -v`，5 tests OK。
- 目标回归：`python3 -m unittest tests.test_manuscript_consumption tests.test_results_draft_evidence_binding tests.test_full_run_from_run_plan tests.test_design_run_plan_state_machine tests.test_product_workflow_contract tests.test_api_contract_v2 -v`，40 tests OK。
- 静态检查：`node --check Product/web/assets/app.js` 通过；`python3 -m py_compile Product/app.py Product/backend/manuscript_candidate_service.py Product/backend/results_draft_service.py Product/backend/draft_service.py Product/backend/project_service.py` 通过。
- 全量回归：`python3 -m unittest discover -s tests -v`，104 tests OK，skipped=1，耗时 5.858s。
- API 验收：`GET /api/v1/projects/proj_undergraduate_thesis/manuscript-candidates` 返回 `latest_run_id=run_c424d6a11af7`，1 个 candidate `manuscript_candidate_finding_trained_effect_results`，正文包含 `trained`、`wage`、`1.8505`、`0.0573`、`9.18e-10`、`12`，并绑定 `source_draft`、`result_artifact`、`review_decision` provenance。
- 浏览器验收：`http://127.0.0.1:8765/?v=20260513-p1k` 的 Results & Draft 页面显示 1 个 Manuscript candidate；页面不存在 `overwrite-paper-draft` 写回按钮；candidate 卡片横向溢出数量为 0；console errors/warnings=0。

## 2026-05-13 P1-L Manuscript Candidate Review

- 失败测试：`python3 -m unittest tests.test_manuscript_consumption -v` 扩展后首次 5 条失败；失败原因为 candidate 缺少 `review_status`，candidate review API 返回 404，非法 action 未结构化拒绝，前端缺少 `can-promote`、`candidate_review`、`reviewManuscriptCandidate` 和 `data-candidate-review-action`。
- 目标测试：`python3 -m unittest tests.test_manuscript_consumption -v`，10 tests OK。
- 目标回归：`python3 -m unittest tests.test_manuscript_consumption tests.test_results_draft_evidence_binding tests.test_full_run_from_run_plan tests.test_design_run_plan_state_machine tests.test_product_workflow_contract tests.test_api_contract_v2 -v`，45 tests OK。
- 静态检查：`node --check Product/web/assets/app.js` 通过；`python3 -m py_compile Product/app.py Product/backend/manuscript_candidate_service.py Product/backend/results_draft_service.py Product/backend/draft_service.py Product/backend/project_service.py` 通过。
- 全量回归：`python3 -m unittest discover -s tests -v`，109 tests OK，skipped=1，耗时 7.453s。
- API 验收：`PUT /api/v1/projects/proj_undergraduate_thesis/manuscript-candidates/manuscript_candidate_finding_trained_effect_results/review` 返回 `review_status=approved`、`evidence_level=local_file`、`can_promote=true`；再次 `GET /manuscript-candidates` 返回 `candidate_review.path=state/product/manuscript_candidate_reviews.json`。
- 浏览器验收：`http://127.0.0.1:8765/?v=20260513-p1l` 的 Results & Draft 页面显示 `review_status=approved`、`can-promote=yes`、candidate review provenance、approve/needs_revision/reject 操作；页面无 `overwrite-paper-draft`，overflowCount=0，console errors/warnings=0。

## 风险更新

- P1-J 已完成：FindingCard 有持久化 review 状态，approved 才允许后续写入正文。
- P1-K 已完成：Manuscript candidates 只消费 `can_write_to_draft=true` 的 approved finding，仍不直接覆盖源草稿。
- P1-L 已完成：Manuscript candidate 有独立审阅/确认状态，approved 后 `can_promote=true`。
- 下一步 P1-M 应设计 promote/write-back/export preflight，仍不要直接覆盖源草稿。
- `state/product/finding_reviews.json` 是浏览器/API 验收创建的本地状态，后续提交前需决定保留、迁移 fixture，或作为 runtime artifact。
- `state/product/manuscript_candidate_reviews.json` 是浏览器/API 验收创建的本地状态，后续提交前需决定保留、迁移 fixture，或作为 runtime artifact。

## 2026-05-16 P2-R ResearchQuestion / TopicSession

- 失败测试：`python3 -m unittest tests.test_research_question_topic_session tests.test_product_workflow_contract.ProductWorkflowFrontendContractTests -v` 首次有效失败为 5 条 `/research-question/current` 404 和 1 条前端缺少 `researchQuestion` API binding。
- 目标测试：同一命令再次运行，15 tests OK。
- 核心回归：`python3 -m unittest tests.test_research_question_topic_session tests.test_product_workflow_contract tests.test_supervisor_plan tests.test_design_run_plan_state_machine tests.test_variable_role_confirmation -v`，36 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，219 tests OK，skipped=1，耗时 24.443s。
- 静态检查：`python3 -m py_compile Program/run_paper.py Program/workbench/observability.py Product/backend/observability_service.py Product/backend/project_service.py Product/backend/research_question_service.py Product/backend/overview_service.py Product/app.py` 通过；`node --check Product/web/assets/app.js` 通过；`git diff --check` 通过。
- API 验收：`PUT /api/v1/projects/proj_undergraduate_thesis/research-question/current` 写入中文选题后，返回 `status=confirmed`、`topic_session_id=topic_session_v2`、`evidence_level=local_file`、`path=state/product/research_question.json`。
- 浏览器验收：`http://localhost:8767/?v=20260516-p2r-topic-session1&fresh=1` 刷新后显示 `从已有选题继续：机器人应用是否影响劳动力市场匹配效率？`，工作台区域自动展开，`overview-question` 为同一中文选题；console errors=[]。

## 风险更新

- P2-R 已完成：ResearchQuestion 现在是后端可审计状态，跨 Session 不再只靠 localStorage。
- `state/product/research_question.json` 是本地 runtime artifact，未纳入 git；如果后续要作为演示 fixture，需要单独迁移。
- 当前只支持单个 current TopicSession；多选题候选池、版本比较、选题废弃/回滚还未做。
- SupervisorPlan 还未消费 ResearchQuestion state；P2-S 应把它作为 plan artifact 输入，但继续禁止自动覆盖 VariableRoleSet、DesignSpec、RunPlan。

## 2026-05-13 P1-M Manuscript Promote Preflight

- 失败测试：`python3 -m unittest tests.test_manuscript_consumption -v` 扩展后首次失败；失败原因为 `/api/v1/projects/{project_id}/manuscript-candidates/{candidate_id}/promote` 返回 404，前端缺少 `promotion_status`、`ready_for_export`、`can_write_back`、`promoteManuscriptCandidate` 和 `data-candidate-promote-action`。
- 目标测试：`python3 -m unittest tests.test_manuscript_consumption -v`，15 tests OK。
- 目标回归：`python3 -m unittest tests.test_manuscript_consumption tests.test_results_draft_evidence_binding tests.test_full_run_from_run_plan tests.test_design_run_plan_state_machine tests.test_product_workflow_contract tests.test_api_contract_v2 -v`，50 tests OK。
- 静态检查：`node --check Product/web/assets/app.js` 通过；`python3 -m py_compile Product/app.py Product/backend/manuscript_candidate_service.py Product/backend/results_draft_service.py Product/backend/draft_service.py Product/backend/project_service.py` 通过。
- 全量回归：`python3 -m unittest discover -s tests -v`，114 tests OK，skipped=1，耗时 8.459s。
- API 验收：`POST /api/v1/projects/proj_undergraduate_thesis/manuscript-candidates/manuscript_candidate_finding_trained_effect_results/promote` 返回 `promotion_status=ready_for_export`、`evidence_level=local_file`、`can_export=true`、`can_write_back=false`，并写入 `state/product/manuscript_candidate_promotions.json`。
- 浏览器验收：`http://127.0.0.1:8765/?v=20260513-p1m` 的 Results & Draft 页面显示 `ready_for_export`、`can_write_back=no`、`promotion_state`、`promotion evidence` 和“进入导出前检查”按钮；页面无 `overwrite-paper-draft`，overflowCount=0，console errors/warnings=0。

## 风险更新

- P1-M 已完成：approved Manuscript candidate 可以进入 `ready_for_export`，但仍不会直接覆盖 `paper_draft.md`。
- P1-N 已完成：`ready_for_export` candidate 可以生成 write-back preview 和 export package manifest，但仍不会直接覆盖 `paper_draft.md`。
- 下一步 P1-O 应把 export preflight 接入 Review & Export 页面，设计最终导出包浏览、docx 预检或显式写回审批。
- `state/product/manuscript_candidate_promotions.json` 是浏览器/API 验收创建的本地状态，后续提交前需决定保留、迁移 fixture，或作为 runtime artifact。
- `state/product/export_package_manifest.json` 和 `Manuscripts/generated/previews/manuscript_candidate_finding_trained_effect_results.md` 是 API 验收创建的本地状态，后续提交前需决定保留、迁移 fixture，或作为 runtime artifact。

## 2026-05-13 P1-N Export Preflight Preview

- 失败测试：`python3 -m unittest tests.test_manuscript_consumption -v` 扩展后首次失败；失败原因为 `/api/v1/projects/{project_id}/manuscript-candidates/{candidate_id}/export-preflight` 返回 404，前端缺少 `export_status`、`preview_ready`、`writeback_preview_path`、`exportPreflightManuscriptCandidate`、`data-candidate-export-preflight-action` 和 `export_package`。
- 目标测试：`python3 -m unittest tests.test_manuscript_consumption -v`，19 tests OK。
- 目标回归：`python3 -m unittest tests.test_manuscript_consumption tests.test_results_draft_evidence_binding tests.test_full_run_from_run_plan tests.test_design_run_plan_state_machine tests.test_product_workflow_contract tests.test_api_contract_v2 -v`，54 tests OK。
- 静态检查：`node --check Product/web/assets/app.js` 通过；`python3 -m py_compile Product/app.py Product/backend/manuscript_candidate_service.py Product/backend/results_draft_service.py Product/backend/draft_service.py Product/backend/project_service.py` 通过。
- 全量回归：`python3 -m unittest discover -s tests -v`，118 tests OK，skipped=1，耗时 8.764s。
- 收尾复查：更新 `Tasks/` 状态文件后再次运行 `python3 -m unittest discover -s tests -v`，118 tests OK，skipped=1，耗时 6.338s。
- API 验收：`POST /api/v1/projects/proj_undergraduate_thesis/manuscript-candidates/manuscript_candidate_finding_trained_effect_results/export-preflight` 返回 `export_status=preview_ready`、`preview_path=Manuscripts/generated/previews/manuscript_candidate_finding_trained_effect_results.md`、`manifest_path=state/product/export_package_manifest.json`、`can_write_back=false`。
- 产物验收：preview 文件保留原 draft 内容并追加 `writeback_preview: do not overwrite source draft automatically` 标记、candidate/run/run_plan 信息和 proposed results paragraph；manifest 记录 `source_draft_path`、`writeback_preview_path`、`candidate_promotion_path`、`result_artifact_path`、`evidence_level=local_file`、`can_write_back=false`。
- 前端验收：`curl http://127.0.0.1:8765/` 确认 CSS/JS 版本为 `20260513-p1n`；JS 静态检查确认 `export_status`、`preview_ready`、`writeback_preview_path`、`v2api.manuscriptCandidates.exportPreflightCandidate`、`exportPreflightManuscriptCandidate`、`data-candidate-export-preflight-action`、`export_package` 均存在，且没有 `overwrite-paper-draft`。Playwright 最终浏览器传输中断，未完成 P1-N 的截图级复验。

## 2026-05-13 P1-O Review & Export Package Workbench

- 失败测试：`python3 -m unittest tests.test_review_export_package -v` 首次 4 条失败；失败原因为 `/api/v1/projects/{project_id}/export-package` 返回 404，前端缺少 `export-package-workbench`、`export-evaluator-checks`、`frontier-iteration-log`、`data-open-results-draft`。
- 目标测试：`python3 -m unittest tests.test_review_export_package -v`，4 tests OK。
- 目标回归：`python3 -m unittest tests.test_manuscript_consumption tests.test_results_draft_evidence_binding tests.test_review_export_package -v`，31 tests OK。
- 静态检查：`node --check Product/web/assets/app.js` 通过；`python3 -m py_compile Product/backend/manuscript_candidate_service.py Product/app.py` 通过。
- 全量回归：`python3 -m unittest discover -s tests -v`，122 tests OK，skipped=1，耗时 9.485s。
- 全量编译：`python3 -m py_compile Program/run_paper.py Program/workbench/observability.py Product/backend/observability_service.py Product/backend/project_service.py Product/backend/manuscript_candidate_service.py Product/app.py` 通过。
- API 验收：`GET /api/v1/projects/proj_undergraduate_thesis/export-package` 返回 `_meta.evidence_level=local_file`、`export_status=preview_ready`、`evaluator_status=passed`、`can_write_back=false`、5 个 passed evaluator checks 和 Frontier-Eng iteration log。
- Chrome 可视化验收：`http://127.0.0.1:8765/?v=20260513-p1o` 点击 `Review & Export` 后显示“导出包验收台”、导出包路径、evaluator checks、Frontier-Eng iteration log；点击“回到 Results & Draft 查看候选来源”可返回候选来源页。截图：`/tmp/empirical-workbench-review-export-p1o.png`。

## 风险更新

- P1-O 已完成：Review & Export 现在能作为可视化 evaluator checkpoint 展示导出包是否可验收。
- 下一步 P1-P 应单独设计显式写回审批或 docx 导出预检；仍不能默认覆盖 `Manuscripts/generated/paper_draft.md`。
- `state/product/export_package_manifest.json`、`Manuscripts/generated/previews/manuscript_candidate_finding_trained_effect_results.md` 和 `/tmp/empirical-workbench-review-export-p1o.png` 是本地验收产物；后续提交前需要决定哪些进入 fixture、哪些保留为 runtime artifact。
- 本轮 Browser 插件连接不稳定，最终使用 Chrome + Computer Use 完成可视化验收。

## 2026-05-13 P1-R Clean Workbench Visual Pass

- 参考来源：JupyterLab 的主工作区/侧栏/属性检查器、Grafana 的 dashboard panel、OpenMetadata 的数据质量/可观测性视角。
- 失败测试：`python3 -m unittest tests.test_clean_workbench_visual_contract -v` 首次 4 失败 1 通过；失败原因为仍存在纸格背景、变量入口 auto 双列、右侧档案栏过重、缺少 record/list 结构。
- 目标测试：`python3 -m unittest tests.test_clean_workbench_visual_contract tests.test_archive_interface_visual_contract tests.test_frontend_chinese_copy -v`，15 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，137 tests OK，skipped=1，耗时 8.495s。
- 静态检查：`python3 -m py_compile Program/run_paper.py Program/workbench/observability.py Product/backend/observability_service.py Product/backend/project_service.py Product/app.py` 通过；`node --check Product/web/assets/app.js` 通过。
- 可视化验收：Browser via Node REPL 超时、Playwright MCP `Transport closed`；已使用 Safari + Computer Use 打开 `http://127.0.0.1:8765/?v=20260513-clean1`，点击“数据与设计”后确认变量角色确认入口无重叠，右侧为属性检查器。

## 风险更新

- P1-R 已解决截图中的重叠和视觉噪声问题，但它是第一轮 clean pass，不代表全部页面已经达到最终产品质感。
- Browser/Playwright 自动化链路仍需后续修复；当前视觉验收采用 Safari + Computer Use fallback。
- 后续不要再把“档案气质”理解成纸格背景和卡片堆叠，应继续围绕研究对象、证据等级、属性检查器、审计时间线迭代。

## 2026-05-13 P1-R Clean Workbench Visual Pass

- 参考来源：JupyterLab 的主工作区/侧栏/属性检查器、Grafana 的 dashboard panel、OpenMetadata 的数据质量/可观测性视角。
- 失败测试：`python3 -m unittest tests.test_clean_workbench_visual_contract -v` 首次 4 失败 1 通过；失败原因为仍存在纸格背景、变量入口 auto 双列、右侧档案栏过重、缺少 record/list 结构。
- 目标测试：`python3 -m unittest tests.test_clean_workbench_visual_contract tests.test_archive_interface_visual_contract tests.test_frontend_chinese_copy -v`，15 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，137 tests OK，skipped=1，耗时 8.495s。
- 静态检查：`python3 -m py_compile Program/run_paper.py Program/workbench/observability.py Product/backend/observability_service.py Product/backend/project_service.py Product/app.py` 通过；`node --check Product/web/assets/app.js` 通过。
- 可视化验收：Browser via Node REPL 超时、Playwright MCP `Transport closed`；已使用 Safari + Computer Use 打开 `http://127.0.0.1:8765/?v=20260513-clean1`，点击“数据与设计”后确认变量角色确认入口无重叠，右侧为属性检查器。

## 风险更新

- P1-R 已解决截图中的重叠和视觉噪声问题，但它是第一轮 clean pass，不代表全部页面已经达到最终产品质感。
- Browser/Playwright 自动化链路仍需后续修复；当前视觉验收采用 Safari + Computer Use fallback。
- 后续不要再把“档案气质”理解成纸格背景和卡片堆叠，应继续围绕研究对象、证据等级、属性检查器、审计时间线迭代。

## 2026-05-13 P1-Q Chinese Copy + Archive Interface

- 失败测试：`python3 -m unittest tests.test_archive_interface_visual_contract -v` 首次 4 条失败；失败原因是页面缺少 `研究档案`、`archive-inspector`、`archive-ledger`、hover/focus/loading/empty/error 状态标识。
- 目标测试：`python3 -m unittest tests.test_archive_interface_visual_contract -v`，5 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，132 tests OK，skipped=1，耗时 11.797s。
- 静态检查：`node --check Product/web/assets/app.js` 通过。
- 编译检查：`python3 -m py_compile Program/run_paper.py Program/workbench/observability.py Product/backend/observability_service.py Product/backend/project_service.py Product/app.py` 通过。
- 静态服务验收：`curl --max-time 5 'http://127.0.0.1:8765/?v=20260513-archive1'` 返回新版 HTML 和 `20260513-archive1` asset version。
- 可视化验收：Safari 打开 `http://127.0.0.1:8765/?v=20260513-archive1`，页面显示 `个人研究档案`、`档案索引`、`相邻笔记`、`证据图例`、`收藏架`；点击右侧 `数据与设计` 后切换到变量角色集编辑器，右侧当前档案说明同步为 `数据与设计`。

## 风险更新

- P1-Q 已完成：页面不再以英文内部对象和普通 SaaS 卡片为主要气质，已经有中文研究档案身份、右侧相邻笔记和证据图例。
- 当前右侧 `archive-inspector` 仍是第一版静态档案索引，不是真正 backlinks / graph。
- 当前收藏架条目未绑定真实 artifacts/export package API，后续应把导出包、run manifest、paper draft 等产物接成可浏览 shelf。
- Browser/IAB 和 Playwright 本轮连接异常；已通过 Safari + Computer Use 做可视化 fallback。

## 2026-05-13 P2-A Dataset Quality Profile

- 目标：把 CoPaper/StatsPAI 式流程里的“数据引入与质量理解”做成可见、可验证的研究对象，避免在变量角色、DesignSpec 或 RunPlan 阶段对不透明数据直接选方法。
- BDD：新增 `docs/architecture-v2/codex-phase-p2-data-quality-profile-bdd.md`，覆盖 datasets API 返回质量画像、缺失值进入 `needs_review`、干净 CSV 进入 `ready`、未解析格式进入 `not_profiled`、前端展示质量画像。
- 失败测试：`python3 -m unittest tests.test_dataset_quality_profile -v` 首次有效失败为 `KeyError: 'quality_profile'` 和前端缺少 `data-quality-profile-panel`，说明目标行为尚未实现。
- 目标测试：`python3 -m unittest tests.test_frontend_chinese_copy tests.test_dataset_quality_profile -v`，11 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，148 tests OK，skipped=1，耗时 6.502s。
- 静态检查：`python3 -m py_compile Program/run_paper.py Program/workbench/observability.py Product/backend/observability_service.py Product/backend/project_service.py Product/backend/overview_service.py Product/app.py` 通过；`node --check Product/web/assets/app.js` 通过。
- API 验收：`GET /api/v1/projects/proj_undergraduate_thesis/datasets` 返回 `analysis_sample.csv`，`quality_profile.evidence_level=local_file`、`readiness_status=ready`、`row_count=12`、`column_count=4`、`missing_rate=0`、`numeric_column_count=4`。
- 可视化验收：Safari + Computer Use 打开 `http://127.0.0.1:8765/?v=20260513-p2a`，进入“数据与设计”后可见 `analysis_sample.csv`、`数据质量画像`、样本 12、缺失率 0%、字段画像和中文操作标签；布局为纵向 clean workbench，不再出现两列挤压。

## 风险更新

- P2-A 已解决“方法选择前看不见数据质量”的问题，但当前质量画像只做轻量 CSV schema、缺失值和类型推断；还不是完整 StatsPAI 描述统计、平衡性检查或因果方法诊断。
- `.dta`、`.xlsx`、`.parquet` 等格式当前保留 `evidence_level=local_file` 并标记 `readiness_status=not_profiled`，后续需要接入真实解析器或 StatsPAI/Stata 侧 profiling。
- Playwright MCP 本轮仍出现 `Transport closed`；自动化视觉链路未修复前，继续使用 Safari + Computer Use、API 和静态资源检查组合验收。

## 2026-05-13 P1-P Writeback Approval + DOCX Preflight

- 失败测试：`python3 -m unittest tests.test_review_export_package -v` 首次出现 4 failures、1 error；失败原因是导出包缺少 `writeback_approval`，两个新 POST API 返回 404，前端缺少 `review-export-evidence-bench`、`writeback-approval-panel`、`docx-preflight-panel` 和 `export-evidence-table`。
- 目标测试：`python3 -m unittest tests.test_review_export_package -v`，9 tests OK。
- 相邻回归：`python3 -m unittest tests.test_review_export_package tests.test_manuscript_consumption tests.test_results_draft_evidence_binding -v`，36 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，142 tests OK，skipped=1。
- 静态检查：`python3 -m py_compile Product/backend/manuscript_candidate_service.py Product/app.py Product/backend/project_service.py Product/backend/results_draft_service.py` 通过；`node --check Product/web/assets/app.js` 通过。
- API 验收：旧 8765 服务一开始返回 404；确认是旧 uvicorn 进程后重启服务，`POST /writeback-approval` 返回 200 并写入 `state/product/writeback_approvals.json`。
- 可视化验收：Browser plugin 运行超时且 Playwright MCP `Transport closed`；已用 Safari + Computer Use 打开 `http://127.0.0.1:8765/?v=20260513-p1p`，进入“审阅与导出”，确认 `导出包验收台`、证据表、写回审批面板和 docx 预检面板可见；点击 `运行 docx 预检` 后显示 `预检通过`、`源草稿存在`、`写回预览存在`、`docx 导出命令已声明`、`docx 目标路径已声明`。

## 风险更新

- P1-P 已完成：Review & Export 现在可以承接用户显式审批，并把 docx 导出前条件写成可追溯本地状态。
- 本阶段没有真正生成 docx，也没有覆盖 `Manuscripts/generated/paper_draft.md`；这是有意保留的安全边界。
- 旧本地服务进程可能继续缓存旧路由；如果页面按钮返回 404，先重启 `python3 -m uvicorn Product.app:app --host 127.0.0.1 --port 8765`。
- Browser/Playwright 自动化链路仍需后续修复；当前验收证据来自 Safari + Computer Use 和 API/tests。

## 2026-05-13 P1-Q Chinese Copy + Archive Interface

- 失败测试：`python3 -m unittest tests.test_archive_interface_visual_contract -v` 首次 4 条失败；失败原因是页面缺少 `研究档案`、`archive-inspector`、`archive-ledger`、hover/focus/loading/empty/error 状态标识。
- 目标测试：`python3 -m unittest tests.test_archive_interface_visual_contract -v`，5 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，132 tests OK，skipped=1，耗时 11.797s。
- 静态检查：`node --check Product/web/assets/app.js` 通过。
- 编译检查：`python3 -m py_compile Program/run_paper.py Program/workbench/observability.py Product/backend/observability_service.py Product/backend/project_service.py Product/app.py` 通过。
- 静态服务验收：`curl --max-time 5 'http://127.0.0.1:8765/?v=20260513-archive1'` 返回新版 HTML 和 `20260513-archive1` asset version。
- 可视化验收：Safari 打开 `http://127.0.0.1:8765/?v=20260513-archive1`，页面显示 `个人研究档案`、`档案索引`、`相邻笔记`、`证据图例`、`收藏架`；点击右侧 `数据与设计` 后切换到变量角色集编辑器，右侧当前档案说明同步为 `数据与设计`。

## 风险更新

- P1-Q 已完成：页面不再以英文内部对象和普通 SaaS 卡片为主要气质，已经有中文研究档案身份、右侧相邻笔记和证据图例。
- 当前右侧 `archive-inspector` 仍是第一版静态档案索引，不是真正 backlinks / graph。
- 当前收藏架条目未绑定真实 artifacts/export package API，后续应把导出包、run manifest、paper draft 等产物接成可浏览 shelf。
- Browser/IAB 和 Playwright 本轮连接异常；已通过 Safari + Computer Use 做可视化 fallback。
## 2026-05-13 P2-B Method Skill Catalog

- 失败测试：`python3 -m unittest tests.test_method_skill_catalog -v` 首次失败，主要失败为 `method_catalog` 缺失、RunPlan task 缺少 `method_id`、前端缺少 `method-skill-catalog-panel`。
- 目标测试：`python3 -m unittest tests.test_method_skill_catalog tests.test_clean_workbench_visual_contract -v`，9 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，152 tests OK，skipped=1。
- 静态检查：`python3 -m py_compile Product/backend/design_spec_service.py Product/app.py Product/backend/project_service.py Product/backend/overview_service.py` 通过；`node --check Product/web/assets/app.js` 通过。
- API 验收：`GET /api/v1/projects/proj_undergraduate_thesis/run-plan` 返回 `method_catalog`，包含 OLS/DID/IV/RDD/PSM/DML；DID/IV/RDD 分别暴露缺面板时间、工具变量、断点运行变量。
- 可视化验收：Safari + Computer Use 打开 `http://127.0.0.1:8765/?v=20260513-p2b-clean`，研究设计细节页展示纵向方法技能集证据清单，无双列卡片挤压。

## 风险更新

- P2-B 已完成方法准入目录，但还不是 CoPaper/StatsPAI 的真实方法执行器。
- 当前 PSM/DML 的 ready 判断较粗，只证明有 outcome/treatment/controls，不证明估计策略充分。
- 下一步 P2-C 应优先把 OLS baseline 跑成 `local_execution` 证据，再逐步扩展 DID/IV/RDD/PSM/DML。
- Playwright MCP 仍不稳定；可视化验收当前以 Safari + Computer Use 为准。

## 2026-05-13 P2-C OLS Execution Adapter

- 目标：把 P2-B 的 OLS ready 方法从 `local_file` 级准入判断推进到 `local_execution` 级本地方法执行结果。
- BDD：新增 `docs/architecture-v2/codex-phase-p2-ols-execution-adapter-bdd.md`，覆盖 approved OLS 执行、RunPlan/数据/公式绑定、manifest 记录、unsupported method 拒绝、不可估数据结构化失败。
- 失败测试：`python3 -m unittest tests.test_ols_execution_adapter -v` 首次有效失败为缺少 `Results/json/method_execution_result.json`、`run.method_execution` 和 manifest `method_execution`；随后发现测试 fixture 共线并改为可估样本。
- 目标测试：`python3 -m unittest tests.test_ols_execution_adapter -v`，5 tests OK。
- 相邻回归：`python3 -m unittest tests.test_ols_execution_adapter tests.test_full_run_from_run_plan tests.test_method_skill_catalog tests.test_results_draft_evidence_binding -v`，20 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，157 tests OK，skipped=1。
- 静态检查：`python3 -m py_compile Program/run_paper.py Program/workbench/observability.py Product/backend/observability_service.py Product/backend/project_service.py Product/backend/overview_service.py Product/backend/design_spec_service.py Product/app.py` 通过；`node --check Product/web/assets/app.js` 通过。
- API 验收：重启 8765 后，`POST /api/v1/projects/proj_undergraduate_thesis/runs/full` 生成 `run_4c62f1721afb`，输出 `status=succeeded`、`plan_binding.tasks[0].method_id=ols`、`method_execution.evidence_level=local_execution`、`treatment_coefficient=1.8505076803`。
- 可视化验收：Playwright MCP 仍 `Transport closed`；使用 Safari + Computer Use 验证本地页面可正常加载，研究设计细节页仍显示方法技能集。P2-C 的结果展示尚未进入页面。

## 风险更新

- P2-C 已完成最小本地 OLS 执行证据，但它不是完整 StatsPAI/Stata 引擎；当前没有稳健标准误、p 值、固定效应、聚类或模型诊断。
- `Results & Draft` 仍主要读取 `Results/json/analysis_result.json`；P2-D 应把 `method_execution_result.json` 接入 Execution / Findings。
- DID/IV/RDD/PSM/DML 仍不能执行；后续每个方法都需要独立 BDD/TDD 和真实产物。

## 2026-05-13 P2-D Method Execution Evidence UI

### 行为覆盖

- [x] Observability API 暴露顶层 `method_execution`，证据等级为 `local_execution`。
- [x] “实证执行”页面显示方法执行证据，包含 adapter、artifact、公式、样本量、处理变量和系数。
- [x] 缺少方法执行产物时，页面显示可恢复空状态，不伪造执行证据。
- [x] Results & Draft API 把方法执行证据绑定到 FindingCard。
- [x] “结果与草稿”页面的结果论断卡显示方法证据来源。

### 测试覆盖

- 测试文件：`tests/test_observable_execution.py`、`tests/test_observable_execution_frontend.py`、`tests/test_results_draft_evidence_binding.py`。
- 目标测试：4 OK。
- Results Draft 回归：10 OK。
- 相邻回归：38 OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，161 OK，skipped=1。
- 静态检查：Python 编译、`node --check Product/web/assets/app.js`、`git diff --check` 均通过。

### 手动验收

- API：`/observability` 和 `/results-draft` 都返回 `engine=python_ols_adapter`、`formula=wage ~ trained + edu + experience`、`nobs=12`、`treatment_coefficient=1.8505076803`。
- 页面：Safari + Computer Use 打开 `http://127.0.0.1:8765/?v=20260513-p2d-method`，点击“实证执行”可见方法执行证据；点击“结果与草稿”可见 FindingCard 方法证据。

### 剩余风险

- 方法执行结果还没有标准误、p 值、置信区间、稳健或聚类标准误。
- Finding approve 还没有强制依赖 evaluator verdict。
- Playwright MCP 本轮仍为 `Transport closed`，视觉验收使用 Safari + Computer Use fallback。

## 2026-05-13 P2-E OLS Evaluator Evidence

### 行为覆盖

- [x] OLS 方法执行结果包含标准误、t 统计量、p 值、95% 置信区间和残差诊断。
- [x] OLS 方法执行结果包含命名 evaluator checks：样本量、模型矩阵可估、处理变量系数存在、推断诊断可用。
- [x] Results Draft API 把 evaluator 状态、标准误、p 值和置信区间绑定到 FindingCard。
- [x] Results & Draft 页面以中文紧凑摘要展示方法 evaluator 证据。
- [ ] 未覆盖：稳健标准误、聚类标准误、固定效应、DID/IV/RDD/PSM/DML 的方法级 evaluator。

### 测试覆盖

- 目标测试：`python3 -m unittest tests.test_ols_execution_adapter tests.test_results_draft_evidence_binding -v`，19 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，165 tests OK，skipped=1。
- 静态检查：`python3 -m py_compile Program/run_paper.py Program/workbench/observability.py Product/backend/observability_service.py Product/backend/project_service.py Product/backend/results_draft_service.py Product/backend/overview_service.py Product/app.py` 通过；`node --check Product/web/assets/app.js` 通过；`git diff --check` 通过。

### API / 可视化验收

- API：`POST /api/v1/projects/proj_undergraduate_thesis/runs/full` 生成 `run_a3674e9e78c6`，status=`succeeded`。
- API：`GET /api/v1/projects/proj_undergraduate_thesis/runs/run_a3674e9e78c6/observability` 返回 `p_values.trained=8.83354660202e-133`、`standard_errors.trained=0.0754664205`、`evaluator.status=passed`，四项 evaluator checks 全部 passed。
- API：`GET /api/v1/projects/proj_undergraduate_thesis/results-draft` 返回 `finding.method_evidence.evaluator_status=passed` 和 `confidence_interval.low=1.7025934962/high=1.9984218644`。
- 页面：Safari + Computer Use 打开 `http://127.0.0.1:8765/?v=20260513-p2e-eval`，点击“结果与草稿”，可见 `ols · n=12 · β=1.8505 · 标准误=0.0755 · p=8.83e-133 · 95% 置信区间 1.7026 ~ 1.9984 · 评估器通过`。

### 剩余风险

- 当前 p 值使用 `normal_approximation`，不是有限样本 t 分布；已在产物里显式标记 `p_value_method=normal_approximation`。
- 当前 OLS 标准误不是 robust/clustered；下一轮若进入真实论文口径，应先增加稳健/聚类标准误选项和 evaluator 阻断条件。
- 当前真实数据仍主要使用项目内 `Data/Final/analysis_sample.csv` 样例；用户提供的 `/Users/mahaoxuan/Desktop/实证数据库` 已初步确认包含 `CHARLS.csv`、CFPS、CLDS、CGSS 等材料，下一轮应选一个可解析数据源做真实数据接入验收。
- Playwright MCP 本轮仍不稳定；视觉验收继续使用 Safari + Computer Use fallback。

## 2026-05-13 P2-F Real Data Candidate Pool

### 行为覆盖

- [x] datasets API 返回只读 `external_catalog`，不把外部文件混入项目内 `items`。
- [x] 外部 CSV 候选数据返回最多 200 行轻量质量画像，证据等级为 `local_file`。
- [x] DTA 等暂未画像格式仍保留在候选池，并明确 `readiness_status=not_profiled`。
- [x] “数据与设计”页面把真实数据候选池和当前项目数据分开展示。
- [x] 未配置真实数据库时，前端提供空状态，不伪造数据。

### 测试覆盖

- 目标测试：`python3 -m unittest tests.test_external_data_catalog -v`，5 tests OK。
- 相邻回归：`python3 -m unittest tests.test_external_data_catalog tests.test_dataset_quality_profile -v`，11 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，170 tests OK，skipped=1。
- 静态检查：`python3 -m py_compile Product/backend/overview_service.py Product/app.py` 通过；`node --check Product/web/assets/app.js` 通过；`git diff --check` 通过。

### API / 可视化验收

- API：`GET /api/v1/projects/proj_undergraduate_thesis/datasets` 返回 `external_catalog.exists=true`、`root=/Users/mahaoxuan/Desktop/实证数据库`、`total_count=223`、`items[0].evidence_level=local_file`。
- 页面：Safari + Computer Use 打开 `http://127.0.0.1:8765/?v=20260513-p2f-realdata2`，点击“数据与设计”，可见 `真实数据候选池`、`223`、真实根目录、6 张 CFPS 候选卡、`本地文件`、`尚未画像`、`只读`。
- Browser 插件路径：Node REPL 连接 in-app Browser 超时；本轮可视化验收使用 Safari + Computer Use fallback。

### 剩余风险

- 当前仅 CSV 做轻量预览画像；DTA/XLSX/Parquet 只登记文件，不读取变量字典。
- 外部候选数据还不能导入或绑定到当前项目；变量角色、RunPlan 和 OLS 执行仍使用 `Data/Final/analysis_sample.csv`。
- 下一步 P2-G 需要显式导入/绑定预检：记录来源路径、目标路径、复制/链接策略、证据等级、用户动作和失败原因。

## 2026-05-14 P2-G Real Dataset Bind Preflight

### 行为覆盖

- [x] 用户选择真实候选池内文件时，后端生成 `ready_for_review` 导入/绑定预检。
- [x] 预检记录包含源路径、目标建议路径、策略、文件大小、证据等级、manifest 路径和检查项。
- [x] 预检拒绝候选池之外的本地路径，避免绕过 provenance 边界。
- [x] datasets API 返回最新 `external_import_preflight`，前端可回显上一条预检。
- [x] “数据与设计”页面提供候选文件预检按钮和独立预检面板。
- [ ] 未覆盖：真正 apply/import、哈希记录、DTA/XLSX/Parquet 深度变量字典、搜索/过滤候选池。

### 测试覆盖

- 目标测试：`python3 -m unittest tests.test_external_dataset_bind_preflight -v`，5 tests OK。
- 相邻回归：`python3 -m unittest tests.test_external_dataset_bind_preflight tests.test_external_data_catalog tests.test_dataset_quality_profile -v`，16 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，175 tests OK，skipped=1。
- 静态检查：`python3 -m py_compile Product/backend/overview_service.py Product/app.py` 通过；`node --check Product/web/assets/app.js` 通过；`git diff --check` 通过。

### API / 可视化验收

- API：`GET /api/v1/projects/proj_undergraduate_thesis/datasets` 返回 `external_catalog.exists=true`、`total_count=223`。
- API：`POST /api/v1/projects/proj_undergraduate_thesis/datasets/external-bind-preflight` 对 CFPS DTA 候选文件返回 `status=ready_for_review`、`evidence_level=local_file`、`target.path=Data/Raw/cfps2010adult_202008.dta`、`will_create_project_file=false`、`will_mutate_source=false`。
- 页面：Safari + Computer Use 打开 `http://127.0.0.1:8765/?v=20260513-p2g-bind1`，点击“数据与设计”，点击候选文件“生成导入/绑定预检”，预检面板显示 `待人工确认`、源文件、目标路径、策略、4 项 passed checks 和只读说明。

### 剩余风险

- 当前只是预检，没有真实导入/绑定；用户还不能把 CFPS 文件变成项目内可分析数据。
- 当前没有文件哈希，无法证明预检后文件未变化；P2-H apply/import 应补 SHA256。
- DTA/XLSX/Parquet 变量字典仍未解析；P2-H 或 P2-I 应先做安全读取和字段预览。
- Browser 插件路径仍不稳定；本轮可视化验收使用 Safari + Computer Use fallback。

## 2026-05-14 P2-H Real Dataset Import Apply

### 行为覆盖

- [x] 本地版用户确认后可把 `ready_for_review` 预检复制到项目 `Data/Raw/<filename>`，并记录目标大小和 SHA256。
- [x] 本地版用户可选择“只绑定引用”，不复制大文件，只记录外部路径、大小、SHA256 和 provenance。
- [x] 用户可取消预检，状态变为 `cancelled`，不会创建项目文件。
- [x] 线上/云端 runtime 拒绝本地路径 apply，返回 `cloud_upload_required`。
- [x] “数据与设计”页面显示三类人工动作按钮，并在 apply 后回显结果。
- [ ] 未覆盖：上传到云对象存储、DTA/XLSX/Parquet 字段读取、移动源文件后的失效提示。

### 测试覆盖

- 目标测试：`python3 -m unittest tests.test_external_dataset_import_apply -v`，5 tests OK。
- 相邻回归：`python3 -m unittest tests.test_external_dataset_import_apply tests.test_external_dataset_bind_preflight tests.test_external_data_catalog tests.test_dataset_quality_profile -v`，21 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，180 tests OK，skipped=1。
- 静态检查：`python3 -m py_compile Product/backend/overview_service.py Product/app.py` 通过；`node --check Product/web/assets/app.js` 通过；`git diff --check` 通过。

### API / 可视化验收

- API：`POST /api/v1/projects/{project_id}/datasets/external-bind-preflight/{preflight_id}/apply` 支持 `copy_to_project_raw`、`bind_external_reference`、`cancel`。
- API：`runtime_mode=cloud` 返回 409 `cloud_upload_required`，不创建本地项目文件。
- 页面：Safari + Computer Use 打开 `http://127.0.0.1:8765/?v=20260514-p2h-import1`，点击“数据与设计”，对 CFPS 预检点击“只绑定引用”，预检面板显示 `已接入`、`已绑定外部引用`、`动作：只绑定引用 · 模式：local` 和 SHA256。
- Browser 插件路径：Node REPL 连接 in-app Browser 超时；本轮可视化验收使用 Safari + Computer Use fallback。

### 剩余风险

- 当前只是“接入数据源”，不是“解析变量字典”；下一步 P2-I 必须先做安全字段画像，再允许变量角色确认消费真实数据。
- 只绑定引用依赖本地文件路径不变；后续画像/执行前必须重新检查文件存在性和 SHA256。
- 云端版本还缺上传、对象存储、隐私/脱敏、远端执行队列和云模型配置。

## 2026-05-14 P2-I Dataset Import Field Profile

### 行为覆盖

- [x] 已复制到项目的 CSV import 可以生成字段画像，字段来自真实文件，证据等级为 `local_file`。
- [x] 只绑定外部引用的 CSV import 可以生成字段画像，但仍保留外部路径依赖和哈希校验。
- [x] DTA/XLSX/Parquet 等暂未接入安全读取器的格式不会伪造字段，而是返回 `blocked/not_profiled`。
- [x] 外部绑定文件哈希变化时拒绝画像，返回 `dataset_import_source_changed`。
- [x] 已取消或未 apply 的 import 不能画像，返回 `dataset_import_not_profileable`。
- [x] 前端显示“生成字段画像”和字段画像面板，并明确不会改写 VariableRoleSet、DesignSpec 或 RunPlan。
- [ ] 未覆盖：DTA 安全变量字典读取、XLSX sheet/字段预览、Parquet schema 读取、云端上传对象画像。

### 测试覆盖

- RED：`python3 -m unittest tests.test_external_dataset_import_profile -v` 首次 6 条失败，失败原因为 profile API 404、前端缺少画像入口和画像面板。
- 目标测试：`python3 -m unittest tests.test_external_dataset_import_profile -v`，6 tests OK。
- 相邻回归：`python3 -m unittest tests.test_external_dataset_import_profile tests.test_external_dataset_import_apply tests.test_external_dataset_bind_preflight tests.test_external_data_catalog tests.test_dataset_quality_profile -v`，27 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，186 tests OK，skipped=1，最终复查耗时 27.137s。
- 静态检查：`python3 -m py_compile Product/app.py Product/backend/overview_service.py` 通过；`node --check Product/web/assets/app.js` 通过；`git diff --check` 通过。

### API / 可视化验收

- API：`POST /api/v1/projects/proj_undergraduate_thesis/datasets/imports/dataset_import_e9d864229be8/profile` 返回 `status=blocked`、`readiness_status=not_profiled`、`fields=[]`、`blocking_reason=dta 暂未接入安全字段读取器。`、`can_feed_variable_roles=false`。
- API：`GET /api/v1/projects/proj_undergraduate_thesis/datasets` 返回 `external_import_profile.status=blocked`、`external_import_profile.readiness_status=not_profiled`、`fields=0`。
- 页面静态资源：`curl http://127.0.0.1:8765/?v=20260514-p2i-profile1` 确认 `dataset-import-profile-panel` 和新版 asset version 已加载。
- 可视化验收：`npx playwright screenshot --wait-for-timeout=3000 'http://127.0.0.1:8765/?v=20260514-p2i-profile1' /tmp/empirical-workbench-p2i-home-loaded.png` 成功生成首页截图。
- 点击级可视化验收：临时使用 `/tmp/empirical-pw/node_modules` 中的 Playwright，打开页面、点击“数据与设计”、点击“生成字段画像”，生成 `/tmp/empirical-workbench-p2i-data-profile.png`；截图中显示 `字段画像 / 变量字典预览`、`dataset_import_id=dataset_import_e9d864229be8 · not_profiled`、`dta 暂未接入安全字段读取器。` 和 `不会改写 VariableRoleSet、DesignSpec 或 RunPlan`。
- Browser 工具限制：Playwright MCP 仍返回 `Transport closed`；Computer Use 对当前 in-app browser URL 返回不允许操作。本轮通过 Playwright CLI fallback 完成截图级验收。

### 剩余风险

- 当前真实 CFPS `.dta` 仍只能进入 `blocked/not_profiled`，还不能查看变量标签和 Stata 类型。
- 线上版还没有上传/云对象入口；本地绑定路径不能直接迁移到线上。
- 字段画像结果还未进入 VariableRoleSet 确认器，下一步必须先做人工确认边界，而不是自动填充研究状态。

## 2026-05-14 P2-J Stata DTA Field Profile

### 行为覆盖

- [x] 有效 DTA import 可以生成 metadata-only 字段画像，返回 `profiled/ready`。
- [x] 字段画像保留 Stata 语义：字段名、变量标签、Stata 类型、display format。
- [x] DTA 画像不读取整张大表，`row_count_source=metadata_only`。
- [x] 损坏或无法解析的 DTA 返回 `blocked/not_profiled`，不伪造字段、不抛 500。
- [x] DTA 字段画像仍不改写 VariableRoleSet、DesignSpec 或 RunPlan。
- [ ] 未覆盖：DTA 值标签 value labels、缺失值统计、抽样预览、真实 Stata do-file 执行、StatsPAI 方法执行。

### 测试覆盖

- RED：`python3 -m unittest tests.test_external_dataset_import_profile -v` 首次 3 条失败，失败原因是有效 DTA 仍 blocked、损坏 DTA 阻塞原因不精确、前端缺少变量标签/Stata 类型。
- 目标测试：`python3 -m unittest tests.test_external_dataset_import_profile -v`，7 tests OK。
- 相邻回归：`python3 -m unittest tests.test_external_dataset_import_profile tests.test_external_dataset_import_apply tests.test_external_dataset_bind_preflight tests.test_external_data_catalog tests.test_dataset_quality_profile -v`，28 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，187 tests OK，skipped=1，耗时 44.366s。
- 静态检查：`node --check Product/web/assets/app.js`、`python3 -m py_compile Product/app.py Product/backend/overview_service.py`、`git diff --check` 均通过。

### API / 可视化验收

- API：`POST /api/v1/projects/proj_undergraduate_thesis/datasets/imports/dataset_import_e9d864229be8/profile` 返回 `status=profiled`、`readiness_status=ready`、`row_count=1279`、`column_count=723`、`row_count_source=metadata_only`、`fields=723`、`can_feed_variable_roles=false`、`blocking_reason=None`。
- API 字段样例：`pid=个人id`、`fid=家户号`、`provcd=省国标码`、`countyid=区县顺序码`、`cid=村居五位码`、`indnum=户内顺序号`。
- 页面：Playwright CLI 打开 `http://127.0.0.1:8765/?v=20260514-p2j-dta1`，点击“数据与设计”，截图 `/tmp/empirical-workbench-p2j-dta-profile.png` 显示 `已画像`、`1279 行 · 723 列`、`变量标签`、`Stata 类型`、`个人id` 和“不改写研究状态”说明。
- Browser 插件限制：Playwright MCP 仍返回 `Transport closed`；本轮继续用 Playwright CLI fallback 完成点击级验收。

### 剩余风险

- 现在只是变量字典级画像，不是实证分析；后续要接 StatsPAI/StatsAPI、StataMCP 或 Python 执行器做严格估计、诊断和稳健性。
- DTA value labels、缺失统计和抽样预览还没读取；当前只证明字段结构和样本规模。
- 字段画像尚未进入人工 VariableRoleSet 候选生成状态机；下一步 P2-K 必须先做人工审阅边界。
- 线上版仍缺上传/云对象抽象，本地 `/Users/...` 绑定不能直接用于云端。

## 2026-05-14 P2-K Rigorous Empirical Execution Contract

### 行为覆盖

- [x] full run 必须声明当前真实执行后端，不能把未调用的 StatsPAI/StataMCP 冒充为执行证据。
- [x] full run 必须列出候选实证后端，并标明可用性、角色和证据等级。
- [x] OLS 方法执行必须记录数据预检：读取行数、可用数值行、丢弃行数、必需字段和自由度检查。
- [x] OLS 方法执行必须记录可复现入口：run_id、公式、RunPlan/DesignSpec 版本、结果文件和源码入口。
- [x] Execution 页面必须把严谨执行契约、数据预检和可复现入口显示给用户。
- [ ] 未覆盖：真实 StatsPAI `sp.*` 调用、Stata do-file/log 执行、robust/cluster 标准误、固定效应、跨后端数值交叉验证。

### 测试覆盖

- RED：`python3 -m unittest tests.test_ols_execution_adapter tests.test_observable_execution_frontend -v` 首次 3 条新增行为失败，失败原因为缺少 `execution_contract`、`data_preflight` 和前端契约展示。
- 目标测试：`python3 -m unittest tests.test_ols_execution_adapter tests.test_observable_execution_frontend -v`，24 tests OK。
- 相邻回归：`python3 -m unittest tests.test_ols_execution_adapter tests.test_observable_execution_frontend tests.test_observable_execution tests.test_results_draft_evidence_binding tests.test_product_api_integration -v`，42 tests OK，skipped=1。
- 全量回归：`python3 -m unittest discover -s tests -v`，190 tests OK，skipped=1。
- 静态检查：`node --check Product/web/assets/app.js`、`python3 -m py_compile Product/app.py Product/backend/project_service.py Product/backend/design_spec_service.py Product/backend/overview_service.py Product/backend/observability_service.py`、`git diff --check` 均通过。

### API / 可视化验收

- API：`POST /api/v1/projects/proj_undergraduate_thesis/runs/full` 生成 `run_5ac7052232c8`，状态 `succeeded`，engine `python_ols_adapter`。
- API：`execution_contract.active_backend=python_ols_adapter`；StatsPAI/StatsAPI 与 StataMCP/Stata 为 candidate backend，其中 StataMCP 检测到本地 Stata 路径。
- API：`data_preflight.rows_read=12`、`usable_numeric_rows=12`、`dropped_rows=0`、`required_fields=["wage","trained","edu","experience"]`。
- API：`reproducibility.result_artifact_path=Results/json/method_execution_result.json`、`source_entrypoint=Product/backend/project_service.py::execute_ols_task`。
- 页面：Playwright CLI 打开 `http://127.0.0.1:8765/?v=20260514-p2k-rigorous4`，进入“实证执行”，确认 `严谨执行契约`、`当前执行后端`、StatsPAI、StataMCP、`数据预检`、`可复现入口` 均可见，`visibleOverflowCount=0`。
- 截图：`/tmp/empirical-workbench-p2k-rigorous-execution.png`。

### 剩余风险

- 当前仍是最小 Python OLS adapter，不是完整 StatsPAI/Stata 统计引擎。
- StatsPAI 和 StataMCP 已作为候选能力展示，但尚未实际运行、产生日志或写出独立结果文件。
- 当前 p 值仍是 normal approximation；严谨论文场景需要 robust/cluster 标准误、固定效应、样本筛选日志和跨后端复核。
- 下一步应先补字段审阅 / VariableRoleSet 候选生成状态机，再把真实 StatsPAI 或 Stata do-file 执行接入为可替换后端。

## 2026-05-14 P2-L Variable Role Candidate Review

### 行为覆盖

- [x] 已完成字段画像的真实 DTA import 可以生成 `VariableRoleCandidate`，证据等级为 `local_file`。
- [x] 候选生成必须写入 `state/product/variable_role_candidates.json`，保留数据源、字段画像 id、候选角色、候选字段表和 review event。
- [x] 候选生成和 review 不能写回正式 `state/product/variable_roles.json`。
- [x] 未画像或未 ready 的 import 不能生成候选，返回 409 `field_profile_required`。
- [x] 非法 review 动作返回 400 `invalid_variable_role_candidate_action`。
- [x] 前端“字段审阅”面板明确显示 `不会写入正式变量角色集`，并提供“候选已确认 / 需要调整 / 驳回候选”按钮。
- [ ] 未覆盖：候选字段的人工搜索/编辑、多候选比较、value labels/缺失率参与评分、把确认后的候选显式提升为正式 VariableRoleSet。

### 测试覆盖

- RED：`python3 -m unittest tests.test_variable_role_candidates -v` 首次 5 条失败，失败原因是候选 API 404 和前端缺少候选审阅面板。
- 目标测试：`python3 -m unittest tests.test_variable_role_candidates -v`，5 tests OK。
- 相邻回归：`python3 -m unittest tests.test_variable_role_candidates tests.test_external_dataset_import_profile tests.test_variable_role_confirmation -v`，17 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，195 tests OK，skipped=1，耗时 8.095s。
- 静态检查：`python3 -m py_compile Product/app.py Product/backend/variable_role_service.py Product/backend/overview_service.py Product/backend/project_service.py` 通过；`node --check Product/web/assets/app.js` 通过。

### API / 可视化验收

- API：`GET /api/v1/projects/proj_undergraduate_thesis/variable-role-candidates` 返回 200。
- 页面：Chrome + Computer Use 打开 `http://127.0.0.1:8765/?v=20260515-p2l-candidates1`，点击“数据与设计”，页面显示真实 CFPS `.dta` 字段画像、723 个字段和“字段审阅”面板。
- 页面：点击“生成变量角色候选”后，面板显示 `待人工审阅`、`evidence_level=local_file`、`候选边界 不会写入正式变量角色集`、候选 outcome/treatment/controls/instruments 和候选字段表。
- 页面：点击“候选已确认”后，按钮状态显示 `候选已确认`，review event 记录 `approve_candidate`。
- 文件边界：确认前后 `state/product/variable_roles.json` SHA256 均为 `bc8bedca4d1638d2556ad77957de146eda170cef521db24eeb7ffde5c2e94649`，mtime 均为 `1778605951`。
- Candidate 状态：最新 `variable_role_candidate_1fbe9c0ee659` 为 `approved_candidate`，`does_not_mutate_variable_role_set=true`。
- Browser 插件限制：Playwright MCP 仍返回 `Transport closed`；Node Browser client 超时。本轮使用 Chrome + Computer Use 完成点击级验收。

### 剩余风险

- 当前变量角色推断是启发式，真实 CFPS 上把 `countyid` 猜为结果变量、`kt3_a_1` 猜为处理变量；这只能证明产品状态机，不可直接用于论文。
- 正式变量角色编辑器仍使用 `analysis_sample.csv` 作为已批准数据源；下一步必须让真实 candidate 进入可编辑正式确认流程。
- DTA value labels、缺失统计和抽样预览还没参与候选建议。
- StatsPAI/StataMCP 尚未实际执行，下一阶段仍需独立日志、结果文件、evaluator checks 和跨后端验证。

## 2026-05-14 P2-M Candidate Promotion to Formal VariableRoleSet

### 行为覆盖

- [x] 未确认、需调整或被驳回的 VariableRoleCandidate 不能写入正式 VariableRoleSet。
- [x] 已确认 candidate 可以进入正式变量角色编辑器，用户编辑后的 outcome/treatment/controls/instruments 以编辑器内容为准。
- [x] 后端写回正式 VariableRoleSet 时必须保存 `candidate_id`、`dataset_import_id`、`dataset_import_profile_id`、数据来源、绑定方式和 provenance。
- [x] 成功写回后 candidate 状态必须变为 `applied_to_variable_roles`，并记录正式角色集 version。
- [x] 前端必须明确显示候选边界：载入编辑器后仍可调整，保存后才写入正式变量角色集。
- [ ] 未覆盖：多候选对比、字段搜索、value labels/缺失统计参与建议、保存后自动重建 DesignSpec/RunPlan。

### 测试覆盖

- RED：`python3 -m unittest tests.test_variable_role_candidates -v` 首次新增行为失败，原因是旧保存逻辑仍把真实候选数据路径当作非法本地数据路径，前端也没有 `pendingVariableRoleCandidateId`。
- 目标测试：`python3 -m unittest tests.test_variable_role_candidates -v`，8 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，198 tests OK，skipped=1，耗时 8.854s。
- 静态检查：`python3 -m py_compile Product/backend/variable_role_service.py Product/app.py` 通过；`node --check Product/web/assets/app.js` 通过。

### API / 可视化验收

- 页面：Chrome + Computer Use 打开 `http://127.0.0.1:8765/?v=20260514-p2m`，进入“数据与设计”。
- 页面：已确认 CFPS `.dta` candidate 显示 `候选已确认`、`候选边界 不会写入正式变量角色集`、`后续动作 可进入正式变量角色集编辑器`。
- 页面：点击“载入正式编辑器”后，变量角色编辑器显示 `draft_from_candidate · local_file`、真实 DTA 路径、`candidate_id=variable_role_candidate_495092cb7af2`、`结果变量 countyid`、控制变量候选和确认说明。
- 保护性验收：没有点击“保存变量角色集”，因为当前 CFPS 候选仍是启发式，直接保存会覆盖演示项目的 `analysis_sample.csv` 已批准变量角色。

### 剩余风险

- 当前真实 CFPS candidate 仍由启发式生成，不能直接用于论文；下一步需要字段搜索、变量标签、缺失统计和样本预览辅助人工选择。
- DesignSpec/RunPlan 还没有基于 candidate 写回后的正式 VariableRoleSet 自动刷新。
- StatsPAI/StataMCP 仍是候选后端，尚未实际执行并生成独立日志、结果文件和 evaluator checks。
- 线上版仍需要上传/云对象路径抽象；本地版可以绑定 `/Users/...`，云端不能执行本地路径。

## 2026-05-14 P2-N/P2-O StatsPAI Validation 与 LLM Supervisor

### 行为覆盖

- [x] CSV OLS full run 在 StatsPAI 可用时必须真实执行独立 validation，而不是只展示候选后端。
- [x] StatsPAI validation 必须写出独立 JSON 产物，供审计和复现。
- [x] 实证执行页必须展示独立后端验证状态、adapter、artifact、证据等级和交叉验证。
- [x] workflow contract 必须显式声明 LLM Supervisor 层，不能只靠工程状态机推进。
- [x] 首页必须展示本地 Codex Supervisor readiness、执行开关、阻塞原因和派工计划。
- [ ] 未覆盖：启用本地 Codex 后真实生成 supervisor plan artifact；Stata do-file/log 执行；StatsPAI 对 DTA/面板/IV/DID/RDD 等方法的执行。

### 测试覆盖

- RED：StatsPAI 行为首次失败为缺少 `backend_validations` 和 `Results/json/statspai_execution_result.json`；LLM Supervisor 行为首次失败为缺少 `workflow_contract.intelligence_layer` 和 `llm-supervisor-panel`。
- 目标测试：`python3 -m unittest tests.test_clean_workbench_visual_contract tests.test_ols_execution_adapter tests.test_observable_execution_frontend tests.test_product_workflow_contract -v`，40 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，203 tests OK，skipped=1，耗时 12.235s。
- 静态检查：`node --check Product/web/assets/app.js` 通过；`python3 -m py_compile Product/backend/overview_service.py Product/backend/project_service.py Product/app.py` 通过。

### API / 可视化验收

- API：`GET /api/v1/providers/local-codex` 返回 `available=true`、`path=/Users/mahaoxuan/.local/bin/codex`、`version=codex-cli 0.130.0`、`execution_enabled=false`。
- API：`GET /api/v1/projects/proj_undergraduate_thesis/overview` 返回 `workflow_contract.intelligence_layer.status=blocked`，blocker 为 `local_codex_execution_not_enabled`。
- 页面：Chrome + Computer Use 打开 `http://127.0.0.1:8765/?v=20260514-p2n-supervisor1`，首页显示“智能中控”“本地 Codex Supervisor 未启用”“允许执行=否”和派工计划。
- API / 页面：点击“启动完整实证执行”后，最终复核 run `run_bb423547439c` 的 observability 返回 `独立后端验证`、`passed`、`statspai.regress`、`Results/json/statspai_execution_result.json`。

### 剩余风险

- 本地 Codex 还没有真正进入执行层；当前只是 provider readiness + workflow contract + UI。下一步必须实现 plan artifact 和 gated execution。
- StatsPAI 只完成当前 CSV OLS 独立验证；真实 CFPS `.dta`、StataMCP、DID/IV/RDD/PSM/DML 和稳健标准误还没完成。
- LLM 输出需要持久化、审计和人工确认；不能让 Supervisor 输出直接覆盖 VariableRoleSet、DesignSpec、RunPlan 或论文正文。
- 本地版和线上版要继续分离：本地版可接 Codex、本地数据和本地统计后端；线上版必须走云模型、上传数据和云执行队列。

## 2026-05-16 P2-P Local Codex SupervisorPlan

### 行为覆盖

- [x] 未启用 `EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC` 时，SupervisorPlan 生成必须阻断，不能创建伪计划。
- [x] 启用本地 Codex 后，系统必须把计划持久化为 `state/product/supervisor_plan.json`，并标记 `status=needs_review`、`evidence_level=local_execution`。
- [x] SupervisorPlan 只能读取并引用 approved VariableRoleSet、DesignSpec、RunPlan，不得直接改写这些正式研究状态。
- [x] GET API 必须返回已保存的同一份 SupervisorPlan，支持跨 Session 恢复。
- [x] 首页必须展示 SupervisorPlan 审阅台、生成入口、证据要求、风险和子 Agent 分工。
- [ ] 未覆盖：真实 Codex subprocess 在持久 app 中生成一份生产计划；SupervisorPlan approve/reject 状态机；approved plan 到任务队列的真实派工。

### 测试覆盖

- RED：`python3 -m unittest tests.test_supervisor_plan -v` 首次 5 条失败，失败点为 API 404 和前端缺少 `supervisor-plan-panel`。
- 目标测试：`python3 -m unittest tests.test_supervisor_plan -v`，5 tests OK。
- 相邻回归：`python3 -m unittest tests.test_supervisor_plan tests.test_product_workflow_contract tests.test_design_run_plan_state_machine -v`，20 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，208 tests OK，skipped=1。
- 静态检查：`node --check Product/web/assets/app.js` 通过；`python3 -m py_compile Product/backend/supervisor_plan_service.py Product/backend/codex_provider.py Product/app.py Product/backend/overview_service.py` 通过；`git diff --check` 通过。

### API / 可视化验收

- API：`GET /api/v1/projects/proj_undergraduate_thesis/supervisor-plan` 返回 `status=empty`、`provider.available=true`、`execution_enabled=false`、`next_action.label=生成 SupervisorPlan`。
- API：默认环境调用 `POST /api/v1/projects/proj_undergraduate_thesis/supervisor-plan` 返回 409 `local_codex_execution_not_enabled`。
- 页面：当前工作树服务打开 `http://127.0.0.1:8767/?v=20260516-p2p-supervisor-plan`；headless Chrome DOM 检测到 `SupervisorPlan 审阅台`、`生成 SupervisorPlan`、`本地 Codex SupervisorPlan`、`local_codex_execution_not_enabled`。
- 截图：`artifacts/ui-checks/p2p-supervisor-plan-overview.png`，1440x1100。

### 剩余风险

- SupervisorPlan 仍是待审计划，不是自动执行编排；下一步需要 approve/reject/needs_revision。
- 本轮未在真实 app 中启用 `EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC=1` 调用真实 Codex，避免在默认验收中产生不可控模型输出。
- 子 Agent 分工目前是计划字段，还没有真正拉起执行者或写入运行队列。
- StatsPAI 只恢复并验证 OLS CSV 路径；DTA、StataMCP 和更多实证方法族仍未完成。

## 2026-05-16 P2-P1 Home Progressive Disclosure

### 行为覆盖

- [x] 智能中控首屏只显示本地 Codex Supervisor 状态、证据等级、阻塞数量和派工角色数量。
- [x] Provider、可用性、允许执行、版本、阻塞项和派工计划默认折叠，点击 `查看中控详情` 后展开。
- [x] SupervisorPlan 审阅台首屏只显示状态、主按钮、人工确认说明和下一步摘要。
- [x] 版本、写入边界、阶段计划、子 Agent 分工、证据要求和风险默认折叠，点击 `查看计划详情` 后展开。
- [x] 使用原生 `details/summary`，默认不 `open`，支持键盘 focus。
- [ ] 未覆盖：移动视口截图；执行页和 Review & Export 页面同类高密度内容的进一步折叠。

### 测试覆盖

- RED：`python3 -m unittest tests.test_supervisor_plan tests.test_product_workflow_contract -v` 首次新增 2 条失败，原因是缺少 `supervisor-plan-progressive-disclosure`、`intelligence-progressive-disclosure` 和对应 summary 文案。
- 目标测试：`python3 -m unittest tests.test_supervisor_plan tests.test_product_workflow_contract -v`，15 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，210 tests OK，skipped=1。
- 静态检查：`node --check Product/web/assets/app.js` 通过；`python3 -m py_compile Program/run_paper.py Program/workbench/observability.py Product/backend/observability_service.py Product/backend/project_service.py Product/app.py` 通过；`git diff --check` 通过。

### 实现范围

- `docs/architecture-v2/codex-phase-p2-home-progressive-disclosure-bdd.md`：新增本轮信息架构行为说明。
- `tests/test_supervisor_plan.py`：锁定 SupervisorPlan 详情默认折叠。
- `tests/test_product_workflow_contract.py`：锁定智能中控详情默认折叠。
- `Product/web/assets/app.js`：重排 `renderIntelligenceLayer()` 和 `renderSupervisorPlan()`，把高噪声明细移入 `details/summary`。
- `Product/web/assets/styles.css`：新增折叠控件、决策信号行和 focus 样式。
- `Product/web/index.html`：更新资源版本。

### 手动验收

1. 打开右侧 Codex 内置浏览器：`http://127.0.0.1:8767/?v=20260516-p2p-disclosure1`。
2. 在“工作台首页”查看“智能中控”：默认只显示状态和摘要；点击 `查看中控详情` 后显示 Provider、执行开关、阻塞项、派工计划。
3. 查看 `SupervisorPlan 审阅台`：默认只显示状态、生成按钮和下一步摘要；点击 `查看计划详情` 后显示版本、边界、阶段计划、子 Agent 分工、证据要求和风险。
4. 本轮截图：`artifacts/ui-checks/p2p-home-progressive-disclosure.png`。

### 剩余风险

- 这次解决的是首页局部信息密度，不代表所有页面已经完成 clean workbench 收敛。
- SupervisorPlan 仍然只是 `needs_review` 产物；下一步必须做审批状态机。
- 详情内容仍会在 DOM text 中存在，这是原生 `details` 的正常行为；视觉和交互上默认折叠。

## 2026-05-16 P2-Q Topic-first Home

### 行为覆盖

- [x] 首页第一屏先让用户输入或选择研究选题，不再默认摊开展示所有执行/Agent/风险模块。
- [x] 用户可以点击 `从已有选题继续`，用 overview 中已有研究问题进入判断环节。
- [x] 用户可以点击 `从真实数据候选池开始`，直接进入“数据与设计”页，但不会自动绑定数据或写入变量角色。
- [x] 选题确认前，`下一步研究决策`、智能中控、SupervisorPlan 和证据 banner 默认隐藏。
- [x] 选题确认后，研究判断区展开并显示后续执行入口。
- [ ] 未覆盖：后端持久化 ResearchQuestion/TopicSession；选题绑定 SupervisorPlan 审批；线上版上传数据入口。

### 测试覆盖

- RED：`python3 -m unittest tests.test_product_workflow_contract.ProductWorkflowFrontendContractTests -v` 首次新增 3 条失败，失败原因为缺少 `research-topic-intake`、`research-workbench-after-topic` 和 `data-topic-start-action`。
- 目标测试：`python3 -m unittest tests.test_product_workflow_contract.ProductWorkflowFrontendContractTests -v`，9 tests OK。
- 相邻回归：`python3 -m unittest tests.test_product_workflow_contract tests.test_supervisor_plan -v`，18 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，213 tests OK，skipped=1。
- 静态检查：`node --check Product/web/assets/app.js` 通过；Python 编译检查通过；`git diff --check` 通过。

### 实现范围

- `docs/architecture-v2/codex-phase-p2-topic-first-home-bdd.md`：新增本轮 BDD 行为契约。
- `tests/test_product_workflow_contract.py`：锁定首页先选题、确认后展开和数据候选入口。
- `Product/web/index.html`：新增选题入口并重组首页工作台区域。
- `Product/web/assets/app.js`：新增选题状态和交互。
- `Product/web/assets/styles.css`：新增选题入口与窄视口降噪样式。

### 手动验收

1. 打开右侧 Codex 内置浏览器：`http://127.0.0.1:8767/?v=20260516-p2q-topic1`。
2. 首屏应看到 `开始一项实证研究` 和选题输入框，而不是直接看到所有执行与 Agent 面板。
3. 输入一个选题，例如“机器人应用是否影响劳动力市场匹配效率？”，点击 `进入研究判断`。
4. 页面应显示已确认选题，并展开 `下一步研究决策`、智能中控和 SupervisorPlan。
5. 刷新后可用 `从已有选题继续` 恢复本地确认状态；点击 `从真实数据候选池开始` 应切到“数据与设计”。

### 剩余风险

- 选题目前是前端本地状态，不是后端审计对象；下一步需要 ResearchQuestion/TopicSession。
- 右侧内置浏览器截图捕获超时；本轮以 DOM 检查和实际可见交互作为验收证据。
- 这轮只调整首页入口，没有完成 SupervisorPlan approve/reject/needs_revision 审批。

## 2026-05-16 P2-S SupervisorPlan Topic Binding

### 行为覆盖

- [x] 没有 confirmed ResearchQuestion 时，SupervisorPlan 生成返回 409 `research_question_required`。
- [x] 本地 Codex prompt 必须包含 `confirmed_research_question` 和 `topic_session_id`。
- [x] 生成后的 SupervisorPlan 记录 `input_research_question`、ResearchQuestion 版本和状态文件路径。
- [x] 前端 SupervisorPlan 审阅台显示绑定选题、TopicSession 和 ResearchQuestion 版本。
- [x] 生成计划仍不得改写 VariableRoleSet、DesignSpec 或 RunPlan。
- [ ] 未覆盖：真实 Codex CLI 在开启执行开关后的端到端生成验收；SupervisorPlan 审批状态机。

### 测试覆盖

- RED：`python3 -m unittest tests.test_supervisor_plan -v` 首次 5 条失败，符合预期。
- GREEN：`python3 -m unittest tests.test_supervisor_plan -v`，8 tests OK。
- 相邻回归：`python3 -m unittest tests.test_supervisor_plan tests.test_research_question_topic_session tests.test_product_workflow_contract.ProductWorkflowFrontendContractTests -v`，23 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，221 tests OK，skipped=1。
- 静态检查：Python 编译检查通过；`node --check Product/web/assets/app.js` 通过；`git diff --check` 通过。

### 实现范围

- `Product/backend/supervisor_plan_service.py`：新增 confirmed ResearchQuestion 前置条件、prompt 上下文和 plan 输入证据。
- `Product/web/assets/app.js`：审阅台显示绑定选题和版本信息。
- `Product/web/index.html`：更新资源版本。
- `tests/test_supervisor_plan.py`：扩展 BDD 测试。
- `docs/architecture-v2/codex-phase-p2-supervisor-plan-topic-binding-bdd.md`：新增行为规格。

### 手动验收

1. 打开 `http://127.0.0.1:8767/?v=20260516-p2s-supervisor-topic1`。
2. 首页用已有选题继续，确认工作台展开。
3. 查看 `SupervisorPlan 审阅台`，摘要中应出现 `绑定选题`。
4. 点击 `查看计划详情`，应看到 `TopicSession` 和 `ResearchQuestion 版本`。
5. 默认环境点击 `生成 SupervisorPlan` 仍应被 `local_codex_execution_not_enabled` 阻断，不能伪装派工。
6. 本轮截图：`artifacts/ui-checks/p2s-supervisor-topic-binding.png`。

### 剩余风险

- 当前仍然没有 approve/reject/needs_revision，所以计划不能进入真实任务队列。
- 真实 Codex 执行验收依赖 `EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC=1`，本轮暂未开启；浏览器只验证默认阻断和绑定选题展示。
- 如果项目没有 confirmed ResearchQuestion，需要先走首页选题确认，否则 SupervisorPlan 会正确阻断。

## 2026-05-16 P2-T SupervisorPlan Review State Machine

### 行为覆盖

- [x] 缺少 `state/product/supervisor_plan.json` 时，审批 API 返回 409 `supervisor_plan_required`，不能审批不存在的计划。
- [x] `approve` 会把计划标记为 `approved`，写入 `human_review`，并设置 `can_dispatch=true`。
- [x] `needs_revision` 会把计划标记为 `needs_revision`，写入人工意见，并继续阻断任务队列。
- [x] `reject` 会把计划标记为 `rejected`，写入人工意见，并继续阻断任务队列。
- [x] 非法 action 返回 400 `invalid_supervisor_plan_review_action`。
- [x] 审批不能改写 ResearchQuestion、VariableRoleSet、DesignSpec 或 RunPlan。
- [x] 前端在存在计划时提供 `批准计划`、`要求修改`、`驳回计划` 三个显式按钮。
- [ ] 未覆盖：approved SupervisorPlan 拆成真实 Agent Task Queue；真实 Codex 执行生成生产计划后的浏览器点击审批。

### 测试覆盖

- RED：`python3 -m unittest tests.test_supervisor_plan -v` 首次新增审批行为失败，原因是 review API、状态持久化和前端按钮尚未实现。
- 目标测试：`python3 -m unittest tests.test_supervisor_plan -v`，13 tests OK。
- 相邻回归：`python3 -m unittest tests.test_supervisor_plan tests.test_research_question_topic_session tests.test_product_workflow_contract.ProductWorkflowFrontendContractTests -v`，28 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，226 tests OK，skipped=1。
- 静态检查：`python3 -m py_compile Product/backend/supervisor_plan_service.py Product/app.py` 通过；`node --check Product/web/assets/app.js` 通过；`git diff --check` 通过。

### 实现范围

- `docs/architecture-v2/codex-phase-p2-supervisor-plan-review-bdd.md`：新增本轮审批状态机行为契约。
- `tests/test_supervisor_plan.py`：新增审批 API、状态保护和前端按钮测试。
- `Product/backend/supervisor_plan_service.py`：新增审批状态机和错误类型。
- `Product/app.py`：新增审批 API。
- `Product/web/assets/app.js`：新增审批请求、按钮渲染和 loading 状态。
- `Product/web/assets/styles.css`：新增审批区样式，并保持单列防重叠布局。

### 手动验收

1. 打开 `http://127.0.0.1:8767/?v=20260516-p2t-supervisor-review1`。
2. 首页进入研究判断区，查看 `SupervisorPlan 审阅台`。
3. 当前真实项目没有计划产物时，应看到 `尚未生成` 和 `生成 SupervisorPlan`，不应看到批准/驳回按钮。
4. 当后续启用本地 Codex 并生成 `supervisor_plan.json` 后，审阅台应显示 `批准计划`、`要求修改`、`驳回计划`。
5. 点击 `批准计划` 后，计划才允许进入下一步任务队列；点击另外两个动作必须继续阻断派工。
6. 本轮截图：`artifacts/ui-checks/p2t-supervisor-review-page.png`。

### 剩余风险

- 当前真实项目默认未启用 `EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC=1`，所以浏览器只验收了“无计划时不显示审批按钮”的正确状态；有计划后的按钮路径由 API/前端测试覆盖。
- P2-U 还未实现：approved SupervisorPlan 还没有拆成 Agent Task Queue。
- StatsPAI/StataMCP 仍未成为完整方法族执行后端；当前只完成 CSV OLS 独立验证和 Python OLS 主路径。
- 线上版数据上传/云执行队列仍未实现；当前 P2-T 只覆盖本地版的 SupervisorPlan 审批边界。

## 2026-05-17 P2-U Agent Task Queue

### 行为覆盖

- [x] 没有 approved SupervisorPlan 时，创建队列返回 409，前端显示阻塞原因并禁用创建按钮。
- [x] approved SupervisorPlan 可以生成 `ready_for_dispatch` 的摘要优先 Agent Task Queue。
- [x] GET API 可以跨 Session 读取已持久化队列；未创建时返回可解释空态。
- [x] 创建队列不能改写 ResearchQuestion、VariableRoleSet、DesignSpec、RunPlan 或 SupervisorPlan。
- [x] 前端默认只显示队列摘要、任务状态、负责人和阻塞；任务输入证据、输出要求、风险和审计日志默认折叠。
- [x] 前端创建队列必须是显式人工动作，并显示“不会自动执行或改写研究状态”的安全边界。
- [x] approved SupervisorPlan 如果没有 `subagent_dispatch`，不能创建空队列。
- [ ] 未覆盖：真实本地 Codex 生成生产 SupervisorPlan 后的浏览器点击 approve -> create 全链路；子 Agent 实际执行队列。

### 测试覆盖

- RED：`python3 -m unittest tests.test_agent_task_queue -v` 首次 8 条失败，原因是缺少 `/agent-task-queue` API、持久化服务和前端队列面板。
- 目标测试：`python3 -m unittest tests.test_agent_task_queue -v`，8 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，234 tests OK，skipped=1。
- 静态检查：`python3 -m py_compile Product/app.py Product/backend/agent_task_queue_service.py Product/backend/supervisor_plan_service.py` 通过；`node --check Product/web/assets/app.js` 通过；`git diff --check` 通过。
- 浏览器验收：真实项目状态下 `Agent 任务队列` 显示 `缺少 SupervisorPlan`，创建按钮 disabled，console error=0；受控 approved-plan 场景点击创建后显示 2 个任务、2 个 details 默认关闭、创建按钮消失，console error=0。

### 实现范围

- `docs/architecture-v2/codex-phase-p2-agent-task-queue-bdd.md`：新增本轮行为契约。
- `tests/test_agent_task_queue.py`：新增 API、持久化保护和前端契约测试。
- `Product/backend/agent_task_queue_service.py`：新增 Agent Task Queue 服务、阻断错误和状态文件写入。
- `Product/app.py`：新增 GET/POST Agent Task Queue API。
- `Product/web/index.html`：首页新增队列面板。
- `Product/web/assets/app.js`：新增队列读取、创建、摘要渲染和折叠详情。
- `Product/web/assets/styles.css`：新增队列视觉层，保持 clean workbench 摘要优先规则。

### 手动验收

1. 启动服务：`python3 -m uvicorn Product.app:app --host 127.0.0.1 --port 8768`。
2. 打开 `http://127.0.0.1:8768/?v=20260517-p2u-final-browser`。
3. 当前真实项目没有 approved SupervisorPlan，应看到 `Agent 任务队列`、`尚未创建任务队列`、`缺少 SupervisorPlan`，创建按钮为 disabled。
4. 后续启用本地 Codex 并生成计划后，先在 `SupervisorPlan 审阅台` 点击 `批准计划`；只有 approved plan 才能点击 `创建 Agent 任务队列`。
5. 创建后应只看到任务摘要和状态；点击 `查看任务详情` 才展开输入证据、输出要求、风险和审计日志。

### 剩余风险

- 当前真实项目没有 approved `state/product/supervisor_plan.json`，所以真实页面只能验收阻塞态；有 approved plan 的成功态由 API 测试和受控浏览器场景覆盖。
- P2-U 只创建派工草案，不执行子 Agent。下一步需要 P2-V 人工派工 / 执行前审计状态机。
- 受控浏览器成功态使用 route interception，目的是避免为了截图伪造当前项目状态；真实持久化行为由后端测试覆盖。
- 浏览器成功态未覆盖移动视口；本轮只验证桌面 clean workbench 信息层级。

## 2026-05-17 P2-W Real VariableRoleCandidate Promotion

### 行为覆盖

- [x] approved `VariableRoleCandidate` 可以创建可编辑 `VariableRoleSet` 草稿。
- [x] Promotion 不覆盖已经 approved 的正式 `state/product/variable_roles.json`。
- [x] 用户编辑 promoted draft 并显式保存后，正式 VariableRoleSet 保留 candidate 和 draft provenance。
- [x] 前端把 `候选建议` 和 `正式变量角色` 分区展示，候选 promotion 与正式保存是两个动作。
- [ ] 未覆盖：保存正式变量角色后自动要求 DesignSpec/RunPlan 重新确认；这是下一阶段状态失效/方法 checklist 问题。

### 测试覆盖

- RED：`python3 -m unittest tests.test_real_variable_role_promotion -v` 首次 4 条失败，原因是 promote API 404、前端缺少 `候选建议` / `正式变量角色` / `promoteVariableRoleCandidate`。
- 目标测试：`python3 -m unittest tests.test_real_variable_role_promotion -v`，4 tests OK。
- 相邻回归：`python3 -m unittest tests.test_real_variable_role_promotion tests.test_variable_role_candidates tests.test_variable_role_confirmation -v`，17 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，243 tests OK，skipped=1。
- 静态检查：`python3 -m py_compile Product/app.py Product/backend/variable_role_service.py` 通过；`node --check Product/web/assets/app.js` 通过；`git diff --check` 通过。

### 实现范围

- `docs/architecture-v2/codex-phase-p2-real-variable-role-promotion-bdd.md`：新增本轮候选 promotion 行为契约。
- `tests/test_real_variable_role_promotion.py`：新增 API、状态保护和前端分区测试。
- `Product/backend/variable_role_service.py`：新增 draft state、promotion、正式保存 provenance 和 draft applied 标记。
- `Product/app.py`：新增 promotion payload 和 API endpoint。
- `Product/web/assets/app.js`：新增 promotion API binding、按钮、loading 状态和正式编辑器载入逻辑。
- `Product/web/assets/styles.css`：新增 draft 视觉边界。

### 手动验收

1. 启动服务：`python3 -m uvicorn Product.app:app --host 127.0.0.1 --port 8768`。
2. 打开 `http://127.0.0.1:8768/?v=20260517-p2w-real-variable-promotion`。
3. 进入“数据与设计”，确认页面显示 `候选建议` 和 `正式变量角色`。
4. 点击 `基于候选创建变量角色草稿`。
5. 页面应显示草稿和保存正式变量角色入口；浏览器自动化验收记录 `badResponses=[]`、`consoleErrors=[]`，截图为 `/tmp/p2w-real-variable-promotion-clean.png`。

### 剩余风险

- 当前 promotion 仍来自启发式字段候选，不能进入论文分析；必须经过正式保存、DesignSpec/RunPlan 重新确认和真实执行。
- `state/product/variable_roles_drafts.json` 是本地 runtime artifact，gitignored，不随代码提交。
- P2-W 没有自动重建 DesignSpec/RunPlan；下一步 P2-X 应把方法工作流 checklist 和状态重确认做成产品对象。

## 2026-05-17 P2-X Method Workflow Checklist

### 行为覆盖

- [x] OLS 在存在 outcome/treatment 时显示 `ready`，并声明样本量、缺失率、系数表和残差诊断。
- [x] DID 在缺少时间变量和处理时点时显示 blocked，不能被保存为 approved RunPlan。
- [x] IV 在缺少工具变量时显示 blocked，不能被保存为 approved RunPlan。
- [x] RDD 暴露断点运行变量 blocker；PSM/DML 在 outcome/treatment/covariates 存在时仅标记为可预检。
- [x] 前端只显示方法摘要，required inputs、diagnostics、blockers 默认折叠在 `查看方法要求`。
- [ ] 未覆盖：真实 DID/IV/RDD/PSM/DML 后端执行、Stata do-file/log、StatsPAI 对非 OLS 方法的结果产物。

### 测试覆盖

- RED：`python3 -m unittest tests.test_method_workflow_checklist -v` 首次 5 条失败，原因是 `/method-workflows` 404、blocked DID RunPlan 仍返回 200、前端缺少 `method-workflow-panel`。
- 目标测试：`python3 -m unittest tests.test_method_workflow_checklist -v`，5 tests OK。
- 相邻回归：`python3 -m unittest tests.test_method_workflow_checklist tests.test_method_skill_catalog tests.test_design_run_plan_state_machine tests.test_ols_execution_adapter -v`，27 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，248 tests OK，skipped=1。
- 静态检查：`python3 -m py_compile Product/app.py Product/backend/method_workflow_service.py Product/backend/design_spec_service.py Product/backend/overview_service.py` 通过；`node --check Product/web/assets/app.js` 通过；`git diff --check` 通过。

### 实现范围

- `docs/architecture-v2/codex-phase-p2-method-workflow-checklist-bdd.md`：新增本轮方法工作流行为契约。
- `tests/test_method_workflow_checklist.py`：新增 API、RunPlan gate 和前端折叠详情测试。
- `Product/backend/method_workflow_service.py`：新增方法工作流生成和 RunPlan 准入检查。
- `Product/backend/design_spec_service.py`：保存 RunPlan 前检查 blocked 方法。
- `Product/app.py`：新增 method workflows API 和 409 blocked response。
- `Product/web/index.html`、`Product/web/assets/app.js`、`Product/web/assets/styles.css`：新增方法工作流面板和默认折叠细节。

### 手动验收

1. 启动服务：`python3 -m uvicorn Product.app:app --host 127.0.0.1 --port 8768`。
2. 打开 `http://127.0.0.1:8768/?v=20260517-p2x-method-workflow`。
3. 进入 `研究设计细节`，确认可见 `OLS：可执行`、`DID：缺少时间变量、处理时点`、`IV：缺少工具变量`、`RDD：缺少断点运行变量`、`PSM：可预检`、`DML：可预检`。
4. 页面初始不展开方法细节；点击 `查看方法要求` 后显示 required inputs、diagnostics 和 blockers。
5. 浏览器验收记录：`errors=[]`、`badResponses=[]`，截图 `/tmp/p2x-method-workflow.png`。

### 剩余风险

- P2-X 只是方法准入，不是完整统计执行；DID/IV/RDD/PSM/DML 仍需要真实执行器、日志、诊断和产物。
- PSM/DML 当前 `可预检` 容易被误读为已执行，后续 UI 可以继续强化“预检”和“真实执行”的区别。
- 隐藏的 Execution 页面也有一份 method workflow DOM，当前不影响可视化验收，后续可以做 accessibility/DOM 去重。

## 2026-05-17 P2-Y Reviewer Scorecard

### 行为覆盖

- [x] 没有 successful full run 时，Reviewer Scorecard API 返回 409 `full_run_required`，不能伪造审稿反馈。
- [x] successful full run 后，评分卡包含新颖性、识别可信度、数据质量、表达清晰度、政策相关性五个维度。
- [x] 每个评分维度包含 score、rationale、evidence、suggested_tasks 和 `local_file` 证据绑定。
- [x] 识别可信度等低分维度会生成后续任务建议，但不会自动改写 `state/product/agent_task_queue.json`。
- [x] Review & Export 页面默认只显示评分摘要；理由、证据和后续任务在 `查看理由与后续任务` 中折叠展示。
- [ ] 未覆盖：真实 LLM reviewer 后端；把用户接受的任务建议写入 proposed queue；方法族专用审稿 rubrics。

### 测试覆盖

- RED：`python3 -m unittest tests.test_reviewer_scorecard -v` 首次 4 条失败，原因是 `/reviewer-scorecard` API 404 和前端缺少 `reviewer-scorecard-panel`。
- 目标测试：`python3 -m unittest tests.test_reviewer_scorecard -v`，4 tests OK。
- 相邻回归：`python3 -m unittest tests.test_reviewer_scorecard tests.test_results_draft_evidence_binding tests.test_review_export_package -v`，25 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，252 tests OK，skipped=1。
- 静态检查：`python3 -m py_compile Product/app.py Product/backend/reviewer_score_service.py Product/backend/results_draft_service.py Product/backend/agent_task_queue_service.py` 通过；`node --check Product/web/assets/app.js` 通过；`git diff --check` 通过。

### 实现范围

- `docs/architecture-v2/codex-phase-p2-reviewer-scorecard-bdd.md`：新增审稿评分卡行为契约。
- `tests/test_reviewer_scorecard.py`：新增 API、状态保护和前端渐进披露测试。
- `Product/backend/reviewer_score_service.py`：新增评分卡读取、生成和持久化服务。
- `Product/app.py`：新增 Reviewer Scorecard API。
- `Product/web/index.html`：Review & Export 页面新增评分卡面板。
- `Product/web/assets/app.js`：新增评分卡 API client、渲染、生成和任务建议选择入口。
- `Product/web/assets/styles.css`：新增评分卡摘要、折叠详情和任务建议样式。

### 手动验收

1. 启动服务：`python3 -m uvicorn Product.app:app --host 127.0.0.1 --port 8768`。
2. 打开 `http://127.0.0.1:8768/?v=20260517-p2y-reviewer-scorecard`。
3. 进入 `复核与导出`。
4. 如为空态，点击 `生成审稿评分`。
5. 确认页面显示 `新颖性`、`识别可信度`、`数据质量`、`表达清晰度`、`政策相关性`。
6. 初始状态下评分理由不展开；点击 `查看理由与后续任务` 后，看到证据、理由和 `加入任务队列草案`。

### 剩余风险

- 当前 reviewer backend 是 deterministic baseline，不是外部审稿 Agent；不能把它当作真实学术审稿。
- 任务建议尚未形成可持久化 proposed task queue；下一步可以在 P2-Z 或后续迭代中接入人工接受后的 proposed queue。
- 评分卡没有针对 DID/IV/RDD/PSM/DML 建立独立 rubrics；需要等这些方法有真实执行产物后补齐。

## 2026-05-17 P2-Z Verifier Gates For Results, Manuscript, And Export

### 行为覆盖

- [x] 没有 export candidate 时，Verifier Checks API 返回 409 `export_candidate_required`，不能伪造导出核验状态。
- [x] 有 export package 后，系统核验结果绑定是否存在，并绑定 `Results/json/analysis_result.json`。
- [x] 系统核验复现产物：export manifest、approved RunPlan、analysis result artifact、method execution artifact 和 draft preview。
- [x] 系统核验证据等级；最终导出只允许 `local_file` 和 `local_execution`，`mock` 即使显式标记也不能通过最终导出 gate。
- [x] docx export preflight 是独立 gate；只要 docx 最终产物不存在或未完成预检，`can_export_docx=false`。
- [x] Review & Export 页面在导出包之前显示 verifier gates，最终导出按钮根据 `can_export_docx` 禁用。
- [ ] 未覆盖：真实 docx 生成并让 `docx_export_preflight` 变为 passed；这是后续写回/导出任务。

### 测试覆盖

- RED：`python3 -m unittest tests.test_verifier_export_gates -v` 首次失败，原因是 `/verifier-checks` API 404 和前端缺少 `verifier-gate-panel`。
- 目标测试：`python3 -m unittest tests.test_verifier_export_gates -v`，5 tests OK。
- 相邻回归：`python3 -m unittest tests.test_verifier_export_gates tests.test_review_export_package tests.test_manuscript_consumption -v`，33 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，257 tests OK，skipped=1。
- 静态检查：`python3 -m py_compile Product/app.py Product/backend/verifier_service.py Product/backend/manuscript_candidate_service.py` 通过；`node --check Product/web/assets/app.js` 通过；`git diff --check` 通过。

### 实现范围

- `docs/architecture-v2/codex-phase-p2-verifier-export-gates-bdd.md`：新增最终导出核验行为契约。
- `tests/test_verifier_export_gates.py`：新增 API、状态保护和前端门禁测试。
- `Product/backend/verifier_service.py`：新增 verifier gate 读取、生成和持久化服务。
- `Product/app.py`：新增 verifier checks API。
- `Product/web/index.html`：Review & Export 页面新增导出核验门面板。
- `Product/web/assets/app.js`：新增 verifier checks API client、渲染、运行核验和最终导出禁用逻辑。
- `Product/web/assets/styles.css`：新增 verifier gate 摘要、状态和 blocked/failed 视觉样式。

### 手动验收

1. 启动服务：`python3 -m uvicorn Product.app:app --host 127.0.0.1 --port 8768`。
2. 打开 `http://127.0.0.1:8768/?v=20260517-p2z-verifier-gates`。
3. 进入 `复核与导出`。
4. 确认 `导出核验门` 出现在 `审稿评分` 之后、导出包之前。
5. 点击或重新运行核验后，应看到 8 个 gate：结果绑定、复现清单、运行计划、分析结果产物、方法执行产物、草稿预览、证据等级、docx 导出预检。
6. 当前真实项目中 7 个 gate passed，`docx 导出预检` blocked；`docx 最终导出` 按钮 disabled。
7. Playwright 浏览器验收记录：`rowCount=8`、`failedRows=1`、`hasResultBinding=true`、`hasDocxPreflight=true`、`finalExportDisabled=true`、`errors=[]`、`badResponses=[]`，截图 `/tmp/p2z-verifier-gates.png`。

### 剩余风险

- P2-Z 只做最终导出前核验，不生成真实 docx；后续需要单独 BDD/TDD 实现 docx export action。
- 当前 `docx_export_preflight` blocked 是预期状态，不是失败：它说明系统不会把 preview package 误当成最终交付物。
- verifier checks 依赖当前 export package 和本地 artifact；如果用户切换 run 或重新生成 manuscript candidate，需要重新运行核验。
- DID/IV/RDD/PSM/DML 仍未有真实执行产物；这些方法未来进入结果后，verifier 需要扩展方法族专用 checks。

## 2026-05-25 P2-AB Topic-first Auto Research CLI

### 行为覆盖

- [x] 题目优先：用户只给研究题目即可创建一次 Auto Research Run。
- [x] 默认 best-available：CLI 默认 `mode=auto`、`execution_policy=best_available`，不会默认退回 dry-run。
- [x] 能力状态可审计：`local_data`、`statspai`、`cnki`、`web_search`、`agentmemory`、`llm_supervisor` 都写入 manifest 的 `capability_status`。
- [x] 递归研究搜索第一版：系统写入 `recursive_search_plan.json`、`literature_clues.jsonl`、变量候选、方法候选和证据缺口。
- [x] 安全边界：自动研究报告和 exploratory 论文草稿均 `needs_human_review`，不能自动晋升正式层。
- [x] 临时项目兼容：未注册本地项目也可以运行 CLI，并把治理状态写在项目自己的 `state/product/`。

### 测试覆盖

- RED：`python3 -m unittest tests.test_auto_research_cli -v` 首次失败，原因是 `Product/cli.py` 没有 `auto-research` 子命令。
- 目标测试：`python3 -m unittest tests.test_auto_research_cli -v`，1 test OK。
- 相邻回归：`python3 -m unittest tests.test_auto_research_cli tests.test_cli_workbench -v`，2 tests OK。
- 静态检查：`python3 -m py_compile Product/cli.py Product/backend/auto_research_service.py Product/backend/registry.py Product/backend/identity_service.py Product/backend/permission_service.py Product/backend/capability_registry.py Product/backend/cost_service.py` 通过。
- JS/格式检查：`node --check Product/web/assets/app.js` 通过；`git diff --check -- <本轮文件>` 通过。
- 手动 CLI 验收：`python3 Product/cli.py auto-research --topic "人工智能是否影响劳动收入差距" --mode auto --max-depth 2 --max-iterations 5` 返回 `status=completed`、`execution_policy=best_available`，运行目录为 `workspace/runs/run_20260524T172441Z_c063b7`。
- 初始全量回归：`python3 -m unittest discover -s tests -v`，282 tests 运行，17 failures，skipped=1。失败集中在前端契约：旧 Agent Drawer、Agent Task Queue 前端摘要、中文导航、首页 Topic-first/Product workflow、SupervisorPlan 前端面板。
- 前端契约修复后全量回归：`python3 -m unittest discover -s tests -v`，282 tests OK，skipped=1。

### 实现范围

- `docs/architecture-v2/codex-phase-p2-auto-research-cli-bdd.md`：新增 Auto Research CLI 行为契约。
- `tests/test_auto_research_cli.py`：新增题目优先 CLI、best-available manifest、候选层安全边界测试。
- `Product/backend/auto_research_service.py`：新增本地 Auto Research Run 生成器。
- `Product/cli.py`：新增 `auto-research` 子命令。
- `Product/backend/registry.py`：新增 transient runtime project 解析。
- `Product/backend/identity_service.py`、`Product/backend/permission_service.py`、`Product/backend/capability_registry.py`、`Product/backend/cost_service.py`：允许治理服务处理未注册本地项目。

### 手动验收

1. 在项目根目录运行：
   `python3 Product/cli.py auto-research --topic "人工智能是否影响劳动收入差距" --mode auto --max-depth 2 --max-iterations 5`
2. 确认 stdout JSON 中包含 `status=completed`、`mode=auto`、`execution_policy=best_available`。
3. 打开返回的 `run_root`，确认存在 `research_intent.json`、`recursive_search_plan.json`、`literature_clues.jsonl`、`variable_candidates.json`、`method_candidates.json`、`research_report.md`、`paper_draft_exploratory.md` 和 `run_manifest.json`。
4. 确认 `run_manifest.json` 中每个能力条目都有 `available/status/reason/can_promote`，且自动产物 `can_promote=false`。

### 剩余风险

- Auto Research 当前第一版只生成候选和草稿，不会真正调度子 Agent 执行，也不会把结果写入正式研究状态。
- StatsPAI/CNKI/Web/agentmemory/LLM Supervisor 目前是能力探测与审计状态，下一步需要把可用能力接入真实 execution adapter。
- 变量候选仍是轻量字段启发式，只能帮助用户审阅，不能作为论文分析变量。
- 全量测试有 17 个前端契约失败，说明当前页面和历史 BDD 契约已漂移；下一轮应先修复前端契约基线，再继续扩展 UI。

## 2026-05-25 P2-AB Frontend Contract Repair And Visual QA

### 行为覆盖

- [x] 首页首屏遵守 topic-first：用户先输入/确认研究问题，工作台细节默认隐藏或摘要化，不再一进来铺开所有能力。
- [x] 用户可以从真实数据候选池进入 Data & Design 路径，不必在没有题目时面对全部执行面板。
- [x] Agent Console 只展示可扫读 Agent 列表；点击 Agent 后，身份、权限、能力、成本和审计日志在右侧 drawer 展开。
- [x] Agent drawer 支持上一个、下一个、关闭；Agent 行支持鼠标点击和键盘激活。
- [x] Agent 产物预览在 drawer 内提供 loading、empty、error 状态，不跳转外部浏览器。
- [x] 主工作区不再重复渲染 `agent-detail-panel`，避免详情信息同时出现在列表下方和右侧 drawer。

### 测试覆盖

- 目标前端回归：`node --check Product/web/assets/app.js && python3 -m unittest tests.test_agent_cluster_frontend_interactions tests.test_frontend_chinese_copy tests.test_product_workflow_contract.ProductWorkflowFrontendContractTests -v`，25 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，282 tests OK，skipped=1。
- Python 编译：`python3 -m py_compile Product/cli.py Product/backend/auto_research_service.py Product/backend/registry.py Product/backend/identity_service.py Product/backend/permission_service.py Product/backend/capability_registry.py Product/backend/cost_service.py Product/app.py` 通过。
- JS 语法：`node --check Product/web/assets/app.js` 通过。
- 格式检查：`git diff --check -- <本轮 scoped files>` 通过。
- 浏览器验收：Playwright 打开 `http://127.0.0.1:8767/?v=20260525-p2ab-quality2`，Agent rows=17，`drawerOpen=true`，`drawerHidden=false`，`inlinePanelsAfter=0`。
- 截图留档：`journey-final-verify.png`、`journey-agent-drawer-clean-verify.png`。

### 实现范围

- `Product/web/index.html`：恢复 `research-topic-intake` / `research-workbench-after-topic` 的 topic-first DOM 契约；新增右侧 Agent drawer；删除主工作区重复 Agent 详情面板。
- `Product/web/assets/app.js`：新增 Agent drawer 打开、关闭、上/下导航、键盘激活和 drawer 内产物预览状态。
- `Product/web/assets/styles.css`：新增 Agent drawer、active row、产物预览 loading/empty/error 样式。
- `tests/test_agent_cluster_frontend_interactions.py`：作为静态契约，锁定右侧 drawer、键盘激活、产物预览和长正文样式。

### 手动验收

1. 保持服务运行：`python3 -m uvicorn Product.app:app --host 127.0.0.1 --port 8767`。
2. 打开 `http://127.0.0.1:8767/?v=20260525-p2ab-quality2`。
3. 首页应先围绕研究问题/下一步决策，不应直接展示所有 JSON、日志和 Agent 详情。
4. 点击左侧 `工具：智能体控制台`。
5. 点击任意 Agent 行，例如 `Overview`。
6. 右侧应打开 `Agent 工作详情` drawer，显示身份、权限、能力注册、成本追踪、审计日志和产物预览空状态；主页面下方不再出现第二份详情面板。

### 剩余风险

- Chrome 当前用户 Profile 对 localhost 出现白屏，Playwright 和 HTTP 请求均证明页面可渲染；更像 Chrome 扩展/Profile 层干扰。已用 Playwright 截图作为验收证据，后续可单独排查 Chrome Profile。
- Agent drawer 的产物正文预览目前是前端状态框架，真实读取 artifact body 的后端 endpoint 还没接入；下一轮需要做 artifact content API。
- CNKI 自动浏览器辅助仍受 Chrome remote debugging / 人工登录状态限制，当前只记录 `blocked_by_browser_session`。
- LLM Supervisor 真正调用 Codex 执行仍受 `EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC=1` 开关保护；未开启时只能生成可审计 blocked 状态。

## 2026-05-25 P3 React Input And Slide Tabs

### 行为覆盖

- [x] 新 React 首屏以研究题目输入为首要动作。
- [x] 文件和长文本材料以附件预览卡片呈现，不直接铺满主屏。
- [x] 工作模式选择集中在输入器底部。
- [x] 阶段滑动导航只暴露任务书、递归搜索、数据变量、方法设计、执行实验五个研究路径节点。
- [x] 新组件视觉限定为黑白灰。
- [x] 新前端独立构建到 `Product/web-dist`，不覆盖旧 `Product/web`。
- [x] 首屏不再出现防守性说明文案。
- [x] 初始页背景有低对比 Three.js 点阵波面，不再是纯黑静态背景。

### 测试覆盖

- RED：`python3 -m unittest tests.test_p3_react_input_tabs -v` 首次 5 failures，缺少 React 包、组件、样式和 App 入口。
- GREEN：`python3 -m unittest tests.test_p3_react_input_tabs -v`，5 tests OK。
- 反馈修正 RED/GREEN：新增首屏文案、低对比和 DottedSurface 契约；首次失败后修复，最终 `python3 -m unittest tests.test_p3_react_input_tabs -v`，7 tests OK。
- Build：`cd Product/web-react && npm run build`，成功生成 `Product/web-dist`。
- 静态检查：`python3 -m py_compile Product/app.py` 通过。
- 格式检查：`git diff --check -- Product/web-react Product/web-dist Product/app.py tests/test_p3_react_input_tabs.py docs/architecture-v2/codex-phase-p3-react-input-tabs-bdd.md` 通过。
- 浏览器验收：Playwright 打开 `http://127.0.0.1:8769/react/?v=20260525-p3-input-tabs-gray2`，`messages=[]`、`failed=[]`、`overflowX=false`、`inputHeight=216`、`tabCount=5`。
- 全量回归：`python3 -m unittest discover -s tests -v`，287 tests OK，skipped=1。

### 实现范围

- `Product/web-react/`：新增 React/Vite 源码、依赖、输入器、滑动标签、黑白灰样式。
- `Product/web-react/src/components/DottedSurface.tsx`：新增 Three.js 点阵背景层。
- `Product/web-dist/`：新增本地构建产物，供 `/react` 预览。
- `Product/app.py`：新增 `/react` 预览路由和 `/react/assets` 静态资源挂载。
- `.gitignore`：忽略 `Product/web-react/node_modules/`。
- `docs/architecture-v2/codex-phase-p3-react-input-tabs-bdd.md`、`tests/test_p3_react_input_tabs.py`：新增行为与测试契约。

### 手动验收

1. 启动服务：`python3 -m uvicorn Product.app:app --host 127.0.0.1 --port 8769`。
2. 打开 `http://127.0.0.1:8769/react/`。
3. 首屏应只有低对比黑白灰点阵背景、研究输入器、模式选择、发送按钮和五段滑动标签；不应出现防守性说明、Agent 队列、审计日志或大面积信息卡片。
4. 在输入框中输入题目，发送按钮变为可用；按 Enter 后下方摘要显示已接收任务。
5. 点击 `本地 Codex Supervisor`，应看到三种模式选项。
6. 点击阶段标签，滑动 cursor 应跟随选中阶段。

### 剩余风险

- Chrome 当前用户 Profile 对 `/react` 仍可能显示白屏；Playwright 渲染正常，疑似 Profile/扩展层问题，需要单独排查。
- 文件预览只在浏览器内读取，不上传后端；线上产品版本仍需实现上传、云端存储和证据绑定。
- 输入器提交只更新前端摘要，不创建正式 ResearchQuestion、Agent Task 或运行计划。
- 右侧审计 Drawer 尚未实现；这是下一轮 P3-B，不应在这轮混入。

## 2026-05-25 P3-C Intake To Analysis Workspace

### 产品进展

- 入口页恢复为单一研究输入界面：只有标题、对话框式输入器、附件入口、参数入口、模式选择和发送按钮。
- 用户提交题目后才进入 `analysis-workspace`，此时才显示阶段导航和语义分析卡片。
- 语义分析卡片现在承担“草案拆解”作用：研究对象、数据线索、方法线索、证据缺口、下一步任务。
- 卡片是 draft-only，不会写入正式 VariableRoleSet、DesignSpec、RunPlan、Findings 或 Manuscript。

### 行为覆盖

- [x] 入口页无语义卡、无阶段导航、无 Agent 队列、无审计面板。
- [x] 提交研究题目后进入分析工作台。
- [x] 分析工作台显示 5 张低噪声语义卡。
- [x] 语义卡保持黑白灰 spotlight 视觉，不引入彩色状态体系。
- [x] 输入器可以向外广播 draft，但不在输入器内部渲染卡片。

### 测试覆盖

- RED：`python3 -m unittest tests.test_p3_semantic_glow_cards tests.test_p3_react_input_tabs -v`，2 failures，原因是 App 仍在入口页渲染 `SemanticGlowCards`，且缺 `analysis-workspace`。
- GREEN：`python3 -m unittest tests.test_p3_semantic_glow_cards tests.test_p3_react_input_tabs -v`，12 tests OK。
- 类型检查：`cd Product/web-react && npx tsc --noEmit` 通过。
- Build：`cd Product/web-react && npm run build` 通过，输出 `Product/web-dist`。
- 浏览器自动验收：Playwright 打开 `/react`，初始 `initialCards=0`、`initialStages=0`；提交后 `analysisCards=5`、`stagePanel=1`。

### 实现范围

- `Product/web-react/src/App.tsx`：拆分 intake screen 与 analysis workspace。
- `Product/web-react/src/components/SemanticGlowCards.tsx`：新增 draft-only 语义分析卡片和 pointer-following GlowCard。
- `Product/web-react/src/components/ResearchCommandInput.tsx`：新增 `onDraftChange`，保留提交 payload。
- `Product/web-react/src/styles.css`：新增 analysis workspace、semantic glow card 和响应式样式。
- `Product/web-react/package.json`、`Product/web-react/package-lock.json`：补齐 React/Three 类型依赖。
- `Product/web-dist/`：更新 React 构建产物。
- `docs/architecture-v2/codex-phase-p3-semantic-glow-cards-bdd.md`、`tests/test_p3_semantic_glow_cards.py`、`tests/test_p3_react_input_tabs.py`：更新行为契约。

### 手动验收

1. 打开 `http://127.0.0.1:8770/react?v=20260525-p3c-workspace2`。
2. 初始页应只看到标题和输入器，不应看到语义卡或阶段导航。
3. 输入题目：`数字经济是否提升城市劳动力市场匹配效率？使用 CFPS 数据，考虑 DID 和工具变量。`
4. 点击右下角发送按钮。
5. 页面应切到分析工作台，顶部显示题目，下面显示阶段导航和 5 张语义卡。
6. 点击 `新任务` 应回到干净入口页。

### 剩余风险

- 当前语义卡是 deterministic draft parser，不是 LLM Supervisor 的真实语义推理；下一步要接 SupervisorPlan / TopicSession。
- 卡片仍在同一个 React route 内通过状态切换模拟“页面”；P3-D 应拆为明确阶段页面容器或路由。
- Vite build 仍提示 JS chunk 超过 500KB，主要来自 Three/framer-motion；后续需要 code splitting。
- 目前未接后端正式状态，提交不会创建正式 ResearchQuestion。

## 2026-05-25 P3-D Task Brief Demo

### 产品进展

- 提交题目后不再直接进入语义卡片区，而是先进入“任务书 Demo”阶段页。
- 主屏只显示 5 个必须判断的信号：研究题目、研究边界、数据线索、方法倾向、下一步。
- 右侧 Inspector 默认折叠高噪声细节：证据要求、风险、正式层边界、派工说明。
- 切换到 `递归搜索` 等非任务书阶段后，才显示语义卡片作为后续阶段 demo。

### 行为覆盖

- [x] 任务提交后默认进入 task brief stage page。
- [x] 主屏只保留当前决策信号，不展示全量 dashboard。
- [x] Inspector 承载证据、风险、边界、派工说明。
- [x] 语义卡从第一分析页后置到其他阶段。
- [x] Demo 不写入正式 ResearchQuestion、VariableRoleSet、DesignSpec、RunPlan、Finding 或 Manuscript。

### 测试覆盖

- RED：`python3 -m unittest tests.test_p3_task_brief_demo -v` 首次 3 failures，原因是缺 `TaskBriefDemo`、`activeStage` 和 task brief 样式。
- GREEN：`python3 -m unittest tests.test_p3_task_brief_demo tests.test_p3_semantic_glow_cards tests.test_p3_react_input_tabs -v`，16 tests OK。
- 类型检查：`cd Product/web-react && npx tsc --noEmit` 通过。
- Build：`cd Product/web-react && npm run build` 通过，仍有 chunk >500KB 警告。
- Playwright：提交题目后 `hasTaskBrief=true`、`decisions=5`、`inspectorSections=4`、`semanticCards=0`、`overflowX=false`；切到递归搜索后 `semanticCardsAfterSwitch=5`。

### 手动验收

1. 打开 `http://127.0.0.1:8770/react?v=20260525-p3d-task-brief-demo`。
2. 输入研究题目并点击发送。
3. 首个分析页应是 `任务书 Demo`，不是语义卡片。
4. 主屏只应看到 5 个决策卡。
5. 右侧 Inspector 应显示 4 个可展开条目。
6. 点击 `递归搜索` 后任务书页隐藏，语义卡才出现。

### 剩余风险

- 这是低保真 Demo，不是最终高保真 UI。
- 右侧 Inspector 当前是固定栏；是否改成抽屉、浮层或可 pin 面板，需要下一轮 grill-me 决策。
- 主屏 5 个信号是否过多或过少，需要用户看 Demo 后确认。
- 仍未接真实 `TopicSession / ResearchQuestion / SupervisorPlan` API。
