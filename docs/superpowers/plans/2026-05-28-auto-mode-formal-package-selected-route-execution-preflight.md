# P7-Z Auto Mode Formal Package Selected Route Execution Preflight

## Component Effect

P7-Z consumes the P7-Y export / acceptance router and prepares the selected route for a later explicit execution command. It does not render PDF/DOCX, does not generate a package manifest, and does not perform manual acceptance; it only translates one recorded route into an execution preflight plan.

## BDD Behaviors

1. Given P7-Y recorded a `formal_pdf_export_preflight` route
   When the selected route execution preflight runs
   Then it creates one PDF route execution preflight item and performs no export.

   业务规则：选择 PDF 路线后，只能进入下一道显式 PDF 执行命令。

2. Given P7-Y recorded DOCX, package manifest, or manual acceptance routes
   When the selected route execution preflight runs
   Then it maps each route to the matching later execution command.

   业务规则：四类路线必须显式分流，不能混成一个模糊导出动作。

3. Given the current real P7-Y output is blocked
   When the CLI runs with default paths
   Then it stays blocked and creates no route execution plan.

   业务规则：没有有效人工路线时，不能进入任何导出或验收执行预检。

4. Given the P7-Y router report is missing, invalid, or not route-recorded
   When the preflight runs
   Then it blocks before planning execution.

   业务规则：本节点必须消费有效的 P7-Y route ledger。

5. Given the routed action is unknown, mismatched, or missing from the selected plan item
   When the preflight runs
   Then it blocks the selected route contract.

   业务规则：执行预检必须与 P7-Y 记录的路线完全一致。

6. Given the selected plan item is not pending, lacks explicit-command requirement, has already rendered/accepted, or has invalid source targets
   When the preflight runs
   Then it blocks the selected route contract.

   业务规则：执行预检只接受干净、待执行、可追溯的上游计划。

7. Given P7-Y reports render, export, formal-state, or product-state side effects
   When the preflight runs
   Then it blocks before execution planning.

   业务规则：本节点不能接收已经发生导出/验收副作用的路由报告。

8. Given any P7-Z report is written
   When outputs are generated
   Then it writes JSON/Markdown review only and never writes `state/product/*`, PDF, DOCX, manifest, or acceptance files.

   业务规则：P7-Z 仍是预检，不是最终执行。

## Boundary Conditions

- This node may write only its selected route preflight JSON and Markdown review.
- It must not render, export, accept, repair, or promote formal files.
- It must require a later explicit route execution command when ready.
- Current real checkout should remain blocked because P7-Y is blocked.

## Checklist

- [x] RED: add selected route execution preflight behavior tests.
- [x] GREEN: implement minimal selected route preflight workbench and CLI.
- [x] Run real blocked-state command.
- [x] Update `Tasks/todo.md` with component effect and next hop.
