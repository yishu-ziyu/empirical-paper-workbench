# P0/P1 验收包：父母教育工资 Demo 线

生成日期：2026-06-17

## 当前结论

这条固定题目线已经完成 P0 到 P1-C 的产品控制闭环验证，但没有进入正式论文、正式 bibliography、正式 VariableRoleSet 或真实方法执行。

- Demo 题目：父母受教育水平对子女工资收入的影响
- 产品形态：复杂实证研究工作流控制台的固定样例，不是产品最终只能服务的题目。
- 当前主入口：React 主入口，由 FastAPI `/`、`/react`、`/react/` 服务 `Product/web-dist/index.html`。
- 旧入口边界：`/legacy` 已重定向到 `/`；`Product/web` 只作为历史源码保留，不再作为产品验收面。

## 阶段验收

### P0 产品控制

- 状态：`p0_phase_ready_for_review`
- 任务数：6
- Evidence Audit：`p0_evidence_audit_ready`
- Portfolio package：`portfolio_demo_package_ready`
- Agent Queue：默认 `can_execute=false`，下一步是人工派工审阅，不自动执行任务。

对应产物：

- `Results/json/product_control_p0_phase.json`
- `state/product/supervisor_plan.json`
- `state/product/agent_task_queue.json`
- `Reviews/product_control_demo_evidence_audit.md`
- `Reviews/product_control_demo_portfolio_package.md`

### P1-A 文献证据

- 状态：`needs_external_literature_verification`
- 本地检索 seed：4 条
- 已核验文献：0 条
- 当前 citation records 均为 `seed`，`can_support_claims=false`
- 阻塞原因：`external_or_manual_literature_search_required`、`human_bibliography_approval_required`

对应产物：

- `Results/json/parent_education_wage_literature_evidence_ledger.json`
- `Reviews/parent_education_wage_literature_evidence_ledger.md`

验收边界：不能把 4 个 seed 写入正式 bibliography，也不能把它们当成已核验文献引用。

### P1-B 数据字段绑定

- 状态：`blocked_missing_parent_education_fields`
- 候选变量：12 个
- matched：8 个
- missing：4 个
- 缺失字段：`father_education`、`mother_education`、`parent_education`、`hukou`
- 阻塞原因：`missing_parent_education_source_fields`

对应产物：

- `Results/json/parent_education_wage_data_field_binding_ledger.json`
- `Reviews/parent_education_wage_data_field_binding_ledger.md`

验收边界：只生成审阅层字段账本，不覆盖 `state/product/variable_roles.json`、`state/product/design_spec.json` 或 `state/product/run_plan.json`。

### P1-C 方法执行

- 状态：`blocked_missing_required_fields`
- `execution_allowed=false`
- `run_id=null`
- 方法候选：IV、DID、DML 全部 blocked
- 阻塞原因：`missing_required_fields`、`design_code_stub_topic_contamination`
- 旧题污染位置：`Tasks/parent-education-wage/design.json` 的 code stub 仍残留 robot 题目变量。

对应产物：

- `Results/json/parent_education_wage_method_execution_ledger.json`
- `Reviews/parent_education_wage_method_execution_ledger.md`

验收边界：没有创建 fake run id，没有伪造回归结果；StatsPAI 只允许在 analysis-ready dataframe 后进入 EDA、pre-flight、identification、estimation、diagnostics，禁止调用 `sp.paper`。

## 已通过验证

- `python3 -m pytest tests/test_parent_education_wage_literature_evidence_ledger.py tests/test_parent_education_wage_data_field_binding_ledger.py tests/test_parent_education_wage_method_execution_ledger.py tests/test_product_control_p0_stage_panel.py tests/test_product_control_p0_phase.py tests/test_web_react_api_base_contract.py tests/test_p3_react_input_tabs.py -q`
  - 结果：38 passed, 11 subtests passed
- `python3 -m py_compile Program/workbench/parent_education_wage_literature_evidence_ledger.py Program/parent_education_wage_literature_evidence_ledger.py Product/backend/product_control_p1_literature_service.py Program/workbench/parent_education_wage_data_field_binding_ledger.py Program/parent_education_wage_data_field_binding_ledger.py Product/backend/product_control_p1_data_field_service.py Program/workbench/parent_education_wage_method_execution_ledger.py Program/parent_education_wage_method_execution_ledger.py Product/backend/product_control_p1_method_service.py Product/app.py`
  - 结果：通过
- `cd Product/web-react && npm run build`
  - 结果：通过；仍保留 Vite chunk size warning
- `python3 Program/parent_education_wage_literature_evidence_ledger.py --project-root .`
  - 结果：写出 P1-A ledger/review
- `python3 Program/parent_education_wage_data_field_binding_ledger.py --project-root .`
  - 结果：写出 P1-B ledger/review
- `python3 Program/parent_education_wage_method_execution_ledger.py --project-root .`
  - 结果：写出 P1-C ledger/review

## 未解决问题

- 尚未进行外部/人工文献检索，当前没有可进入正式 bibliography 的核验文献。
- 尚未定位父母教育和 hukou 的真实字段，当前不能创建正式 VariableRoleSet。
- `Tasks/parent-education-wage/design.json` 仍有旧 robot 题目 code stub 污染，当前不能执行方法。
- Vite build 仍有既有 chunk size warning。
- `Product/web` 历史源码仍在仓库内；运行入口已经移除，但物理删除属于破坏性清理，应单独授权后做。

## 下一步

1. 补 P1-B 字段证据：从 CFPS/CHARLS/其他真实数据源定位父亲教育、母亲教育、父母教育合成变量和 hukou 字段，或明确变量口径调整。
2. 修复 `Tasks/parent-education-wage/design.json`：移除 robot exposure / bartik IV / robot density 等旧题 code stub。
3. 字段和 design 通过后，再生成正式 VariableRoleSet draft、DesignSpec draft 和 RunPlan draft。
4. 只有 RunPlan 前置条件通过后，才进入 StatsPAI/Python/Stata 执行层并创建真实 run id。
5. 文献侧单独做外部检索和人工 bibliography approval，不把 seed 直接提升为引用。
