# P7-AM Auto Mode Formal Package Next Gate Workflow Continuation Result Review

## Goal

Review the P7-AL workflow continuation execute result and the selected route execution preflight it produced. This node must not run continuation commands, execute selected routes, export PDF/DOCX, generate package manifests, perform manual acceptance, or write `state/product/*`.

## BDD Behaviors

1. Given P7-AL completed a workflow continuation and the selected route execution preflight is ready, when P7-AM reviews both reports, then it records one accepted selected route preflight record and allows continuation to explicit route execution.
   - Business rule: continuation result review is a read-only gate between running selected route preflight and later route execution.
2. Given the current P7-AL report is blocked, when P7-AM runs, then it blocks and records no selected route preflight record.
   - Business rule: a blocked continuation execute report cannot be treated as evidence for downstream route execution.
3. Given P7-AL is missing, has the wrong schema, did not complete execution, returned non-zero, or has blockers, when P7-AM reviews it, then P7-AM blocks on the execute report.
   - Business rule: the source execute report must prove the continuation command actually ran cleanly.
4. Given P7-AL route, continuation report path, review path, or continuation status does not match a known continuation contract, when P7-AM reviews it, then P7-AM blocks on the result contract.
   - Business rule: downstream review cannot trust mismatched report paths or route types.
5. Given the selected route execution preflight is missing, invalid, not ready, has blockers, violates boundaries, or exposes a mismatched plan, when P7-AM reviews it, then P7-AM blocks on the selected route preflight report.
   - Business rule: only a clean selected route preflight may be handed to the later explicit route execution command.
6. Given P7-AM writes its outputs, when the report and Markdown are persisted, then only P7-AM review artifacts are written and `state/product/*` is untouched.
   - Business rule: result review is a gate, not a formal-state writer.
7. Given the CLI is run with the current blocked P7-AL report, when defaults are used, then it writes a blocked result review with zero selected route preflight records.
   - Business rule: the default local chain must reflect the current real blocked state.

## Boundary Conditions

- P7-AM consumes only P7-AL execute report and the selected route execution preflight report referenced by P7-AL.
- P7-AM must not run `auto_mode_formal_package_selected_route_execution_preflight` again.
- P7-AM must not execute selected route commands.
- P7-AM must not export or accept formal package artifacts.
- P7-AM must not write `state/product/*`.
- Current real repository state is expected to remain blocked because P7-AL is blocked by P7-AK.

## Verification Plan

- RED: `python3 -m unittest tests.test_auto_mode_formal_package_next_gate_workflow_continuation_result_review -v` should fail because the P7-AM module does not exist yet.
- GREEN: implement the workbench module and CLI.
- Real blocked run: run the CLI against `Results/json/auto_mode_formal_package_next_gate_workflow_continuation_execute.json`.
- Regression: run P7-A through P7-AM unittest suite.
