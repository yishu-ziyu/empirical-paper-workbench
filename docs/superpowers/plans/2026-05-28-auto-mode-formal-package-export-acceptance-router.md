# P7-Y Auto Mode Formal Package Export / Acceptance Router

## Component Effect

P7-Y turns the P7-X export / acceptance preflight into an explicit human route record. It does not render PDF/DOCX, does not generate the final package manifest, and does not perform manual acceptance; it only records which later command is allowed when P7-X is ready and the route is explicitly confirmed.

## BDD Behaviors

1. Given P7-X is ready and the decision is `defer`
   When the router runs
   Then it waits without recording a route.

   业务规则：没有人工选择时，导出/验收链路保持等待。

2. Given P7-X is ready and the decision is `pdf_export`
   When the route is confirmed with reviewer and note
   Then it records `formal_pdf_export_preflight` as the next route without exporting anything.

   业务规则：明确选择后只进入下一道命令入口，不在 router 内直接导出。

3. Given the current real P7-X output is blocked
   When the CLI runs with default paths
   Then it blocks and records no route.

   业务规则：上游预检没通过时，不能选择导出或验收动作。

4. Given the selected decision is unknown or not present in the P7-X plan
   When the router runs
   Then it blocks the route.

   业务规则：人工路线必须来自上游批准的计划。

5. Given a non-defer route is missing confirmation, reviewer, or note
   When the router runs
   Then it blocks before route recording.

   业务规则：进入导出/验收前必须留下可追溯人工授权。

6. Given P7-X contains render, acceptance, formal-state, or product-state side effects
   When the router runs
   Then it blocks the route.

   业务规则：router 只接受纯预检结果，不能接收已发生副作用的上游。

7. Given any P7-Y report is written
   When outputs are generated
   Then it writes JSON/Markdown review only and never writes `state/product/*`, PDF, DOCX, manifest, or acceptance files.

   业务规则：本节点只记录路由，不生产最终交付物。

## Boundary Conditions

- This node may write only its router JSON and Markdown review.
- It must not render, export, accept, repair, or promote formal files.
- Non-defer decisions require `--confirm-route`, reviewer, and note.
- Current real checkout should remain blocked because P7-X is blocked.

## Checklist

- [x] RED: add router behavior tests.
- [x] GREEN: implement minimal router workbench and CLI.
- [x] Run real blocked-state command.
- [x] Update `Tasks/todo.md` with component effect and next hop.
