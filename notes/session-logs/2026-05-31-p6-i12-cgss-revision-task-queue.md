# 2026-05-31 P6-I12 Session Log

## Component Effect

P6-I12 turns the CGSS literature and method review packets into a structured draft-layer revision task queue.

It tells the next reviewer or agent:

- which four agent roles are involved;
- which eight tasks are queued;
- which evidence each task should read;
- where each task would write after approval;
- what boundaries each task must not cross.

It does not execute tasks, create `Reviews/agent_packets/...` files, write `state/product/agent_task_queue.json`, write manuscript sections, or write formal state.

## Current Real Run

- JSON: `Results/json/cgss_social_capital_happiness_revision_task_queue.json`
- Review: `Reviews/cgss_social_capital_happiness_revision_task_queue.md`
- Status: `needs_human_revision_queue_approval`
- Agent packets: `4`
- Agent tasks: `8`
- Agents: `LiteratureAgent`, `MethodAgent`, `WriterAgent`, `ReviewerAgent`
- Task status: `queued_for_human_approved_revision`
- Promotion allowed: `false`
- Blocking reasons: `revision_queue_needs_human_approval`

## Downstream Connection

Downstream nodes should treat this as a queue waiting for human approval.

- a UI can show the four agent packets and eight tasks as an approval board;
- an approval router can decide defer, approve, revise, or reject;
- work-order generation should consume this queue only after approval;
- no downstream node should create agent packet files or product-state task queues from this output alone.

## Verification

- Target test: `python3 -m unittest tests.test_cgss_revision_task_queue -v` -> 8 OK.
- Scoped P6-I regression: `python3 -m unittest tests.test_topic_to_paper_capability_audit tests.test_cgss_topic_variable_discovery tests.test_cgss_minimal_model tests.test_cgss_ordered_robustness tests.test_cgss_results_evidence_package tests.test_cgss_variable_role_review_draft tests.test_cgss_literature_seed_package tests.test_cgss_literature_source_verification_preflight tests.test_cgss_verified_bibliography_candidates tests.test_cgss_literature_review_draft_packet tests.test_cgss_method_structure_gate_packet tests.test_cgss_revision_task_queue -v` -> 45 OK.
- Compile: `python3 -m py_compile Program/cgss_revision_task_queue.py Program/workbench/cgss_revision_task_queue.py tests/test_cgss_revision_task_queue.py` -> OK.
- Real CLI: `python3 Program/cgss_revision_task_queue.py --project-root .` -> `needs_human_revision_queue_approval`, `agent_tasks=8`.

## Pause Point

Pause after P6-I12. The next logical stage is the revision work-order approval/gate, but it should not run automatically in this stage.
