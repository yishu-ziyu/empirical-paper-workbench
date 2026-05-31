# P7-BC Auto Mode Formal Package Next Gate Manifested Routed Next Gate Run Preflight

## Goal

Add a P7-BC preflight node that consumes the P7-BB explicit routed next-gate entry gate result plus the recorded entry manifest, then prepares the manifested routed next-gate command run plan without running that command.

## BDD Behaviors

1. Given P7-BB recorded an entry manifest and the manifest is clean, When P7-BC runs, Then it returns `ready_for_manifested_routed_next_gate_run_preflight` and exposes one downstream command input record.
   - Business rule: P7-BC is a connector from recorded entry manifest to the next command gate.
2. Given the current P7-BB result is blocked or missing, When P7-BC runs, Then it returns `blocked_by_explicit_routed_next_gate_entry_gate` and has no command plan.
   - Business rule: the main chain cannot skip the explicit entry gate.
3. Given P7-BB has wrong schema, is not manifest-recorded, or did not execute the entry gate, When P7-BC runs, Then it blocks on the P7-BB gate.
   - Business rule: only a real recorded manifest can unlock manifested command preflight.
4. Given P7-BB and the manifest disagree on route, next gate, manifest path, or operation count, When P7-BC runs, Then it blocks on the run contract.
   - Business rule: the command run plan must be tied to the exact manifest recorded by P7-BB.
5. Given the manifest is missing, invalid, or not manifested, When P7-BC runs, Then it blocks on the routed entry manifest.
   - Business rule: no manifest means no manifested command run.
6. Given the manifest contains side-effect or boundary signals, When P7-BC runs, Then it blocks on the manifested run boundary.
   - Business rule: a preflight cannot continue from an artifact that already crossed the execution boundary.
7. Given the manifest operation is missing, duplicated, unknown, or marked as already running the next command, When P7-BC runs, Then it blocks on the manifested run contract.
   - Business rule: the downstream command gate needs exactly one clean operation.
8. Given the CLI reads the current blocked repo state, When P7-BC runs with defaults, Then it writes blocked report/review only and does not create command workspace or product state.
   - Business rule: the current product effect is visible but non-destructive.

## Boundary Conditions

- P7-BC must not run the next-gate command.
- P7-BC must not enter the next gate.
- P7-BC must not export PDF/DOCX, generate package manifest, perform manual acceptance, or write `state/product/*`.
- The next execute step remains a separate P7-BD gate.

## Verification

1. Run the new test module and confirm RED before implementation.
2. Implement the smallest wrapper around the existing manifested command preflight component.
3. Run the new test module, py_compile, the Auto Mode formal-package test family, the real CLI, and staged diff whitespace check.
