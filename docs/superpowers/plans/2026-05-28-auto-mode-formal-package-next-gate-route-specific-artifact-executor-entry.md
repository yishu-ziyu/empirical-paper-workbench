# P7-AP Auto Mode Formal Package Next Gate Route-Specific Artifact Executor Entry

## Component Effect

P7-AP turns the P7-AO selected route execute result review into a controlled entry gate for the existing route-specific artifact executor.

This node only enters the existing executor in dry-run mode. It does not render PDF/DOCX, generate package manifests, perform manual acceptance, run route-specific artifact execution, or write `state/product/*`.

## BDD Behaviors

1. Given P7-AO is ready, when P7-AP runs in dry-run mode, then it previews the artifact executor dry-run command without running it.
   - Business rule: ready handoff creates a visible next command, not an implicit export.
2. Given P7-AO is blocked, when P7-AP runs, then it blocks and produces no artifact executor entry command.
   - Business rule: blocked review cannot enter artifact execution.
3. Given P7-AO is missing, schema-invalid, not ready, or has blockers, when P7-AP runs, then it blocks on P7-AO.
   - Business rule: only clean result review can drive executor entry.
4. Given the P7-AO artifact executor input record is missing, duplicated, unknown, or path-mismatched, when P7-AP runs, then it blocks on the handoff contract.
   - Business rule: downstream executor input must be exact and single.
5. Given P7-AP runs in execute mode without confirmation, reviewer, or note, then it blocks.
   - Business rule: entering the next executor must be explicitly acknowledged.
6. Given P7-AO is ready and P7-AP is explicitly confirmed, when P7-AP executes, then it runs the existing artifact executor only in dry-run mode.
   - Business rule: this node opens the next gate but does not produce final package artifacts.
7. Given the artifact executor command file is unavailable, when P7-AP runs, then it blocks without trying to execute.
   - Business rule: command availability is part of the gate.
8. Given the CLI is run against the current blocked P7-AO state, when defaults are used, then it writes a blocked entry gate.
   - Business rule: default CLI behavior is safe in the current repository state.

## Boundary Conditions

- P7-AP consumes only P7-AO result review.
- P7-AP calls `auto_mode_formal_package_route_specific_artifact_executor.py` with `--mode dry-run`.
- Actual artifact generation remains guarded by the existing artifact executor's own execute confirmation.
