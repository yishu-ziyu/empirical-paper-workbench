# Auto Mode Formal Package Selected Route Execution Preflight Current Blocked Record

## Component Effect

P7-Z is the selected route execution preflight after the P7-Y export / acceptance router.

User-facing effect: this node turns one human-selected P7-Y route into a single execution preflight for PDF export, DOCX export, package manifest generation, or manual acceptance. In the current run, P7-Y has not recorded any route, so P7-Z stays blocked and produces no selected route execution plan.

## BDD Coverage

### Behavior 1: PDF route becomes an execution preflight without exporting

Given P7-Y recorded `formal_pdf_export_preflight`
When P7-Z runs
Then P7-Z creates one `pdf_export` execution preflight
And it does not render or export a PDF.

Business rule: route preflight can prepare the next command, but it must not perform the final artifact action.

### Behavior 2: DOCX, package manifest, and manual acceptance routes map to their own outputs

Given P7-Y recorded a DOCX, package manifest, or manual acceptance route
When P7-Z runs
Then P7-Z maps the route to the matching planned output and next command.

Business rule: each route must preserve the user's selected output type.

### Behavior 3: Current blocked P7-Y blocks selected route preflight

Given the current P7-Y router is `blocked_by_export_acceptance_preflight`
When P7-Z runs
Then P7-Z reports `blocked_by_export_acceptance_router`
And no selected route execution plan is generated.

Business rule: P7-Z cannot invent a selected route.

### Behavior 4: Missing, invalid, or unrecorded router output blocks preflight

Given the P7-Y router report is missing, has a wrong schema, or has no recorded route
When P7-Z runs
Then P7-Z blocks selected route execution preflight.

Business rule: the preflight only consumes a clean P7-Y route ledger.

### Behavior 5: Unknown or mismatched selected route blocks the contract

Given P7-Y reports an unknown route, a mismatched selected plan item, or no selected plan item
When P7-Z runs
Then P7-Z blocks with a selected route contract issue.

Business rule: execution preflight must exactly match the route P7-Y recorded.

### Behavior 6: Bad selected plan contract blocks preflight

Given the selected plan item is already completed, already rendered, or points outside the formal package
When P7-Z runs
Then P7-Z blocks selected route execution preflight.

Business rule: the next route must remain pending and inside the formal package boundary.

### Behavior 7: Router side effects block preflight

Given P7-Y already exported, rendered, wrote formal state, or allowed product-state writes
When P7-Z runs
Then P7-Z blocks selected route execution preflight.

Business rule: P7-Z expects P7-Y to be a route ledger, not an execution result.

### Behavior 8: P7-Z writes report and review only

Given P7-Z runs in any state
When outputs are written
Then only the selected route preflight JSON and Markdown review are written.

Business rule: P7-Z must not render PDF/DOCX, generate a package manifest, perform manual acceptance, or write `state/product/*`.

## Current Run Boundary

The current run remains blocked because P7-Y has no recorded route.

Observed CLI output:

```text
status=blocked_by_export_acceptance_router
can_request_selected_route_execution=false
requires_explicit_route_execute_command=false
selected_route_execution_plan=0
selected_route_executed=false
export_or_acceptance_executed=false
rendered_pdf=false
rendered_docx=false
package_manifest_generated=false
manual_acceptance_performed=false
this_command_wrote_formal_state=false
can_write_product_state=false
```

Observed JSON facts:

```text
source_status=blocked_by_export_acceptance_preflight
source_router.status=blocked_by_export_acceptance_preflight
source_router.route_recorded=false
source_router.routed_action=
next_action.id=record_export_acceptance_route
```

Blocking reasons:

```text
export_acceptance_router_not_route_recorded
export_acceptance_router_cannot_route
export_acceptance_router_route_not_recorded
export_acceptance_router_routed_action_missing
export_acceptance_router_metadata_incomplete
export_acceptance_router_confirmation_missing
```

## Downstream Connection

P7-AA must read this as a blocked selected route preflight. It must not enter selected route execute because:

- `can_request_selected_route_execution=false`
- `requires_explicit_route_execute_command=false`
- `selected_route_execution_plan=[]`
- no route-specific next command exists

The earliest valid next condition remains a clean P7-Y recorded route, which itself requires P7-X to be ready and a human-confirmed route decision.

## Verification

Fresh checks run on 2026-05-31:

```text
python3 -m unittest tests.test_auto_mode_formal_package_selected_route_execution_preflight -v
python3 -m py_compile Program/auto_mode_formal_package_selected_route_execution_preflight.py Program/workbench/auto_mode_formal_package_selected_route_execution_preflight.py tests/test_auto_mode_formal_package_selected_route_execution_preflight.py
python3 Program/auto_mode_formal_package_selected_route_execution_preflight.py --project-root .
jq -r ... Results/json/auto_mode_formal_package_selected_route_execution_preflight.json
test ! -e state/product/auto_mode_formal_package_selected_route_execution_preflight.json
python3 -m unittest tests.test_auto_mode_formal_package_export_acceptance_router tests.test_auto_mode_formal_package_selected_route_execution_preflight tests.test_auto_mode_formal_package_selected_route_execute -v
```

Results:

- Target tests: 9 OK.
- Adjacent regression: 26 OK.
- Python compilation: OK.
- CLI real run: exit 0 with blocked status.
- Product state file: absent.
- Existing PDF/DOCX/manifest files: present from older work but not modified by this run.

## Pause

Pause after P7-Z current blocked selected route execution preflight. P7-AA must not be treated as ready until P7-Y records one clean route.
