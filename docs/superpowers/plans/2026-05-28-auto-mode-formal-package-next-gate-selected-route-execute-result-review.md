# P7-AO Auto Mode Formal Package Next Gate Selected Route Execute Result Review

## Component Effect

P7-AO reviews the P7-AN selected route execute gate output and the recorded selected route execute manifest before any route-specific artifact executor can run.

It does not render PDF/DOCX, generate a package manifest, perform manual acceptance, run route-specific artifact commands, or write `state/product/*`.

## BDD Behaviors

1. Given P7-AN executed selected route execute and the manifest is clean, when P7-AO reviews the result, then it marks the route-specific artifact executor input as ready.
   - Business rule: only a confirmed selected route execute manifest can feed artifact execution.
2. Given the current P7-AN output is blocked, when P7-AO reviews it, then no manifest review or executor input is produced.
   - Business rule: blocked upstream execution cannot advance the formal package chain.
3. Given P7-AN is missing, schema-invalid, incomplete, or has blockers, when P7-AO reviews it, then it blocks on P7-AN.
   - Business rule: upstream execute evidence must be complete and clean.
4. Given the selected route execute report path, status, or result summary disagrees with P7-AN, when P7-AO reviews it, then it blocks on the result contract.
   - Business rule: P7-AN and the delegated selected route execute report must describe the same event.
5. Given the selected route execute manifest is missing, schema-invalid, or marks any artifact/formal-state action as already done, when P7-AO reviews it, then it blocks on manifest review.
   - Business rule: the manifest is only permission to run the next executor, not evidence that artifacts were already produced.
6. Given P7-AO writes outputs, when it completes, then it writes only result-review JSON/Markdown and not `state/product/*`.
   - Business rule: review nodes do not mutate formal product state.
7. Given the CLI is run against the current blocked P7-AN state, when defaults are used, then it writes a blocked result review.
   - Business rule: default CLI behavior is safe in the current repository state.

## Boundary Conditions

- Current real repository state is expected to remain blocked until P7-AM/P7-AN have real ready inputs.
- Downstream must still use existing selected route execute report and manifest paths.
- P7-AO can only approve the input record for route-specific artifact execution; it does not run that executor.
