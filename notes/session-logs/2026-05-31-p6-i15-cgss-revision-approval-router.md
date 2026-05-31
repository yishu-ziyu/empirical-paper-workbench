# 2026-05-31 P6-I15 Session Log

## Component Effect

P6-I15 routes the CGSS revision approval record into the next workflow step.

It tells the product:

- keep waiting when the decision is `defer`;
- return to queue editing when the decision is `revise`;
- rebuild or stop when the decision is `reject`;
- generate draft Agent work orders only when the decision is `approve` and an approved queue sidecar exists.

In the current real state, it waits. No Agent receives a work order.

## Current Real Run

- JSON: `Results/json/cgss_social_capital_happiness_revision_approval_router.json`
- Review: `Reviews/cgss_social_capital_happiness_revision_approval_router.md`
- Source approval status: `pending_human_revision_queue_decision`
- Decision: `defer`
- Route status: `waiting_for_human_revision_queue_decision`
- Route: `wait_for_human_confirmation`
- Work orders: `0`
- Written work orders: `[]`
- Formal writeback allowed: `false`
- Product state write allowed: `false`

## Downstream Connection

Downstream nodes should treat this as the workflow router after the approval ledger.

- a UI can show the current route as "waiting for human confirmation";
- a route controller can branch to revise, reject, or approved work-order generation;
- P6-I13 work-order generation should run only after this router sees an approved queue route;
- current `defer` means no Agent packet files should be created.

## Verification

- Target test: `python3 -m unittest tests.test_cgss_revision_approval_router -v` -> 5 OK.
- Scoped P6-I regression: `python3 -m unittest tests.test_topic_to_paper_capability_audit tests.test_cgss_topic_variable_discovery tests.test_cgss_minimal_model tests.test_cgss_ordered_robustness tests.test_cgss_results_evidence_package tests.test_cgss_variable_role_review_draft tests.test_cgss_literature_seed_package tests.test_cgss_literature_source_verification_preflight tests.test_cgss_verified_bibliography_candidates tests.test_cgss_literature_review_draft_packet tests.test_cgss_method_structure_gate_packet tests.test_cgss_revision_task_queue tests.test_cgss_revision_work_orders tests.test_cgss_revision_queue_approval tests.test_cgss_revision_approval_router -v` -> 59 OK.
- Compile: `python3 -m py_compile Program/cgss_revision_approval_router.py Program/workbench/cgss_revision_approval_router.py tests/test_cgss_revision_approval_router.py` -> OK.
- Real CLI: `python3 Program/cgss_revision_approval_router.py --project-root .` -> `waiting_for_human_revision_queue_decision`, `route=wait_for_human_confirmation`, `work_orders=0`.

## Pause Point

Pause after P6-I15. The next logical stage is either a real human approval decision or a downstream route result review, but it should not run automatically in this stage.
