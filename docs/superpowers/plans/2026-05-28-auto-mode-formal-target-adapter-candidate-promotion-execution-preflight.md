# P7-U Auto Mode Formal Target Adapter Candidate Promotion Execution Preflight

## Component Effect

P7-U turns a human-approved verified candidate promotion ledger into a reviewed execution preflight. It tells the next node exactly which candidate targets may be promoted later, but it does not promote them.

## BDD Behaviors

1. Given P7-T contains an effective approval with approved candidate promotion items
   When Auto Mode builds the promotion execution preflight
   Then it creates an execution plan and keeps candidate promotion disabled in this command.

   业务规则：审批通过后只能进入执行前检查，不能直接写正式成果。

2. Given the current P7-T output is blocked or not approved
   When Auto Mode builds the promotion execution preflight
   Then it blocks and produces no execution plan.

   业务规则：不能绕过人工审批和上游阻断。

3. Given an approval ledger has no approved promotion plan or malformed plan items
   When Auto Mode builds the promotion execution preflight
   Then it blocks before any execute node can run.

   业务规则：执行前必须知道 candidate 来源、正式目标和校验信息。

4. Given the approval ledger reports formal-state writes, product-state writes, or boundary violations
   When Auto Mode builds the promotion execution preflight
   Then it blocks with boundary reasons.

   业务规则：上游账本一旦越界，后续 promotion 不能继续。

5. Given the repository's real P7-T output is currently blocked
   When the CLI runs with default paths
   Then it writes a blocked preflight report and leaves formal outputs untouched.

   业务规则：真实默认运行必须保持安全等待状态。

6. Given any P7-U report is written
   When outputs are generated
   Then only JSON and Markdown review files are written.

   业务规则：P7-U 是预检组件，不是执行组件。

## Boundary Conditions

- The next node must be a separate explicit execute gate.
- P7-U must not copy candidate targets into formal targets.
- P7-U must not write `state/product/*`.
- P7-U must not render PDF/DOCX, rerun models, or rewrite paper package artifacts.

## Checklist

- [x] RED: add first behavior test and confirm missing module failure.
- [x] GREEN: implement minimal workbench function.
- [x] Add remaining behavior tests incrementally.
- [x] Add CLI and real blocked-state run.
- [x] Update `Tasks/todo.md` with component effect, output, boundary, and next hop.
