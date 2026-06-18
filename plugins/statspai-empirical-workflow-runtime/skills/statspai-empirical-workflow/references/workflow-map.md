# Workflow Map

This project has ten core workflows:

1. `01_design`: research question, causal design, design risk.
2. `02_literature`: search plan, candidates, references, contribution matrix.
3. `03_paper_reading`: slow reading, source spans, reading state.
4. `04_data_gate`: data contract, attrition, variables, analysis-ready data.
5. `05_causal_analysis`: main estimates, diagnostics, robustness.
6. `06_writing`: evidence-bound paper draft.
7. `07_revision`: reviewer risks, structure, claim revision.
8. `08_format_citation`: references, tables, figures, layout.
9. `09_replication`: manifest, hashes, replication boundary.
10. `10_defense`: response matrix, defense Q&A, revision log.

Use `workflows/registry.json` as the source of truth. Use `workflows/agents/*.agent.md` for step-specific agent instructions.

The optional workflow `05x_policy_rollout_data_layer` is a future upgrade path. It must not change the current claim until official rollout timing covers the CHARLS provinces and is human-approved.
