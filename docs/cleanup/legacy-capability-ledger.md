# Legacy capability disposition ledger

Source reviewed: `实证论文项目模板/` at
`bb1e9b645f0e797de9967002a90219be5923dbfd` plus its four linked worktrees.
The encrypted U1 recovery snapshot preserves every dirty and untracked file.

The acceptance rule is product value plus executable proof. A capability is
not retained merely because the legacy checkout contains more code.

## Capability decisions

| Legacy candidate | Current econpaper evidence | Decision |
|------------------|----------------------------|----------|
| Pipeline orchestration and resume (`orchestrator_v2.py`, `runtime/pipeline.py`) | LangGraph graph/fan-in tests, facade resume tests, and backend journey tests cover the web product's state transitions | Delete legacy implementation; its filesystem-step model is a second product architecture |
| Empirical tool loop and trajectory (`empirical_agent/`) | `agent/engine/estimate_agent.py` owns bounded tool use; `backend/run_store.py` owns append-only traces and checkpoints; sandbox and run-artifact tests cover both | Delete as redundant; no missing product behavior found |
| Pi JSON-RPC runtime (`pi_runtime/`) | No import, subprocess call, configuration key, loader, or product test references it; current providers use the LLM router and the estimate sandbox | Delete as an unused alternative runtime |
| Literature search (`runtime/literature_search.py`) | `search_literature` supports Crossref, Semantic Scholar, Apodex, explicit source/degradation labels, DOI deduplication, method anchors, and threat hops | Delete as a strict subset of current behavior |
| Automatic data acquisition (`runtime/data_acquire.py`) | Current product contract begins with user upload and preserves provenance; upload and cleaning tests exercise that boundary | Do not migrate: unattended local scanning and World Bank download would expand product scope and data authority |
| Design card (`runtime/design_card.py`) | Research direction, main specification, design chat, threat cards, and approval endpoints are product-owned and tested | Delete as redundant |
| Specification curve (`runtime/spec_curve.py`) | `agent/design/spec_curve.py` and `agent/tests/test_spec_curve.py` already provide the current contract | Delete as redundant |
| CLI/demo/resume commands (`Product/cli/`, `runtime/cli.py`) | ADR-0010 and the root README define one web product; no current command installs or imports these modules | Delete as obsolete product surface |

No candidate passed the migration gate. The useful behavior already exists in
the product with stronger tests, or conflicts with the approved web-only scope.
Copying any legacy module would create a second owner for the same behavior.

## Checkout and nested-repository decisions

| Checkout | U1-preserved state at review | Product reference | Decision |
|----------|------------------------------|-------------------|----------|
| legacy main `bb1e9b645f0e` | 26 modified, 271 deleted, untracked content | Source material only until U4 finishes | Delete in U6 |
| `worktree-agent-ae417c42` `e9a6e10bea6f` | untracked content | none | Delete in U6 |
| `l7-tuning` `77dd55e86026` | 8 modified plus untracked content | none | Delete in U6 |
| `l8-dod` `d4ab7b383711` | untracked content | none | Delete in U6 |
| `brief-step-cards` `8f295d332290` | untracked content | none | Delete in U6 after U4 has resolved notes |
| nested `demo-project-shell` `8131cab80625` | modified and untracked content, no remote | none | Delete in U6; recovery bundle and dirty snapshot are the only warranted preservation |
| nested `penguin-harness` `d14be6fce255` | clean upstream clone | none | Delete in U6; reproducible from canonical upstream |

Historical specs may still name the legacy checkout while U4 consolidates
their useful facts. Product Python, configuration, installation, and tests do
not resolve files through it.

## Executable evidence

Run with the entire legacy checkout temporarily unavailable:

```text
agent/tests/test_graph_fanin.py
agent/tests/test_prewrite_convergence.py
agent/tests/test_search_literature.py
agent/tests/test_spec_curve.py
agent/tests/test_sandbox.py
agent/tests/test_estimate_agent.py
backend/tests/test_facade.py
backend/tests/test_run_artifacts.py
backend/tests/test_journey.py
backend/tests/test_upload.py
```

Result: 90 Agent tests and 76 backend tests passed with the entire legacy
checkout renamed out of its expected path. A repository search outside
historical specs/plans/handoffs finds no legacy-path product consumer.
