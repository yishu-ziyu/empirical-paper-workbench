# Orchestrator Policy

Use `workflows/orchestrator_policy.json` as the execution boundary.

Default posture:

- `dry-run` first.
- `execute` only for `allow_execute_adapters`.
- Use exact command allowlist.
- Do not use shell command composition.
- Block network, human auth, placeholder commands, recursive preflight, and high side effects.

Current safe execution subset:

- `workflow_runbook`
- `literature_metadata_verifier`
- `data_gate_runner`
- `reproduction_verify`

Current blocked or dry-run-only examples:

- `pdf_fetch_scansci`: network and human auth.
- `cnki_browser_hqu`: browser session and human auth.
- `causal_analysis_runner`: rewrites results.
- `latex_compile`: build artifact; keep outside automated execute until explicitly allowed.
- `workflow_preflight`: recursive preflight.
