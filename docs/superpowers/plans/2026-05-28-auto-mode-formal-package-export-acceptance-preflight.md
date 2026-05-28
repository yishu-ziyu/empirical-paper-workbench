# P7-X Auto Mode Formal Package Export / Acceptance Preflight

## Component Effect

P7-X turns a verified formal package from P7-W into an export / acceptance preflight. It does not render PDF/DOCX, does not build a final submission package, and does not write product state; it only says whether the next explicit export or acceptance command is allowed.

## BDD Behaviors

1. Given P7-W verified the promoted formal package
   When the export / acceptance preflight runs
   Then it creates a reviewable plan for PDF export, DOCX export, package manifest, and manual acceptance.

   业务规则：正式包复验通过后，下游才能进入导出或验收。

2. Given the current real P7-W output is blocked
   When the CLI runs with default paths
   Then it stays blocked and creates no export / acceptance plan.

   业务规则：当前真实链路未验证正式包，不能继续导出。

3. Given the P7-W report is missing, invalid, or not verified
   When the preflight runs
   Then it blocks before planning export.

   业务规则：导出预检必须消费有效的正式包复验结果。

4. Given verified target records are missing, not verified, or outside `Submissions/formal_package/`
   When the preflight runs
   Then it blocks with the exact target group reason.

   业务规则：导出计划不能建立在不完整或越界的正式包文件上。

5. Given the P7-W report contains product/write/render/model side effects
   When the preflight runs
   Then it blocks the export / acceptance plan.

   业务规则：P7-X 只接受只读验证报告，不接受带副作用的上游。

6. Given any P7-X report is written
   When outputs are generated
   Then it writes JSON/Markdown review only and never writes `state/product/*`, PDF, DOCX, or final package files.

   业务规则：预检节点只产出下一步门禁，不产出最终成果。

## Boundary Conditions

- This node may write only `Results/json/*` and `Reviews/*`.
- It must require a later explicit export or acceptance command.
- It does not repair formal package targets.
- It does not render or copy submission artifacts.

## Checklist

- [x] RED: add export / acceptance preflight behavior tests.
- [x] GREEN: implement minimal workbench preflight path.
- [x] Add blocked, invalid report, bad target, boundary, and CLI tests.
- [x] Run real blocked-state command.
- [x] Update `Tasks/todo.md` with component effect and next hop.
