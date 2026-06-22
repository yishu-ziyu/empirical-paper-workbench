# Agent Runtime Preflight

Status: PASS
Generated: 2026-06-22T20:09:30

## Commands

### `python3 scripts/20_validate_workflow_contracts.py`

- exit: 0

stdout:

```text
PASS workflows=11 report=artifacts/workflow_contract_validation.md
```

### `python3 scripts/21_route_next_workflow.py`

- exit: 0

stdout:

```text
NEXT 02_literature: 文献检索与综述
- query_plan.json: not found at litreview/query_plan.json
- literature_candidates.csv: not found at litreview/literature_candidates.csv
- references.bib: not found at references.bib
- contribution_matrix.md: not found at litreview/contribution_matrix.md
report=artifacts/workflow_router_report.md
```

### `python3 scripts/22_validate_agent_specs.py`

- exit: 0

stdout:

```text
PASS agent_specs=10 report=artifacts/agent_spec_validation_report.md
```

### `python3 scripts/23_workflow_runbook.py`

- exit: 0

stdout:

```text
NEXT 02_literature: 文献检索与综述
workflows=10 missing_specs=0 report=artifacts/workflow_runbook_report.md json=artifacts/workflow_runbook_state.json
```

### `python3 scripts/24_validate_runbook_api.py`

- exit: 0

stdout:

```text
PASS workflows=10 report=artifacts/workflow_api_validation_report.md
```

### `python3 scripts/26_validate_context_strategy.py`

- exit: 0

stdout:

```text
PASS report=artifacts/context_strategy_validation_report.md
```

### `python3 scripts/27_validate_tool_adapters.py`

- exit: 0

stdout:

```text
PASS adapters=11 trace_events=3 report=artifacts/tool_adapter_validation_report.md
```

### `python3 scripts/28_agent_orchestrator.py --mode dry-run --no-trace`

- exit: 0

stdout:

```text
PASS mode=dry-run selected=11 executed=0 blocked=7 route=02_literature report=artifacts/orchestrator_report.md
dry-run wrote no artifacts; pass --write-artifacts to persist a plan
browser_preview: blocked reason=blocked_side_effect,command_not_allowlisted,placeholder_command
causal_analysis_runner: blocked reason=adapter_not_allowed,blocked_side_effect,command_not_allowlisted
cnki_browser_hqu: blocked reason=adapter_not_allowed,blocked_side_effect,command_not_allowlisted,human_auth_required,network_required
data_gate_runner: planned reason=none
latex_compile: blocked reason=blocked_side_effect,command_not_allowlisted
literature_metadata_verifier: planned reason=none
pdf_fetch_scansci: blocked reason=adapter_not_allowed,blocked_side_effect,command_not_allowlisted,human_auth_required,network_required
policy_rollout_builder: blocked reason=adapter_not_allowed,blocked_side_effect,command_not_allowlisted
reproduction_verify: planned reason=none
workflow_preflight: blocked reason=command_not_allowlisted,recursive_preflight
workflow_runbook: planned reason=none
```

### `python3 scripts/28_agent_orchestrator.py --mode execute --adapter reproduction_verify --no-trace`

- exit: 0

stdout:

```text
PASS mode=execute selected=1 executed=1 blocked=0 route=02_literature report=artifacts/orchestrator_report.md
```

### `python3 scripts/29_validate_orchestrator.py`

- exit: 0

stdout:

```text
PASS report=artifacts/orchestrator_validation_report.md
```

### `python3 scripts/30_test_orchestrator_negative.py`

- exit: 0

stdout:

```text
PASS missing trace_path rejected
```

### `python3 scripts/31_validate_skill_subagent_registry.py`

- exit: 0

stdout:

```text
PASS report=artifacts/skill_subagent_validation_report.md
```

### `python3 scripts/32_test_skill_subagent_negative.py`

- exit: 0

stdout:

```text
PASS missing 10_defense binding rejected
```

### `python3 scripts/33_validate_plugin_package.py`

- exit: 0

stdout:

```text
PASS report=artifacts/plugin_package_validation_report.md
```

### `python3 -m json.tool artifacts/workflow_runbook_state.json`

- exit: 0

stdout:

```text
{
    "version": "0.4",
    "layer": "second",
    "status": "partial",
    "source_registry": "workflows/registry.json",
    "source_artifact_registry": "Tasks/artifact-registry.md",
    "api_contract": "workflows/api_contract.md",
    "current_route": {
        "next_workflow_id": "02_literature",
        "next_workflow_name": "\u6587\u732e\u68c0\u7d22\u4e0e\u7efc\u8ff0",
        "reason": [
            "query_plan.json: not found at litreview/query_plan.json",
            "literature_candidates.csv: not found at litreview/literature_candidates.csv",
            "references.bib: not found at references.bib",
            "contribution_matrix.md: not found at litreview/contribution_matrix.md"
        ]
    },
    "artifact_status": {
        "present": 3,
        "partial": 0,
        "missing": 0,
        "external": 0
    },
    "spec_coverage": {
        "core_workflows": 10,
        "missing_specs": []
    },
    "workflows": [
        {
            "id": "01_design",
            "step": "01",
            "name": "\u9009\u9898\u4e0e\u7814\u7a76\u8bbe\u8ba1",
            "purpose": "\u628a idea \u53d8\u6210\u53ef\u68c0\u9a8c\u7684\u7814\u7a76\u95ee\u9898\u3001\u8bc6\u522b\u53e3\u5f84\u548c\u98ce\u9669\u6e05\u5355\u3002",
            "agents": [
                "ResearchDesignAgent",
                "DesignAuditor"
            ],
            "inputs": [
                "idea",
                "data_clue",
                "policy_or_treatment_clue"
            ],
            "required_outputs": [
                {
                    "artifact": "research_design.md",
                    "path_hint": "research_design.md"
                },
                {
                    "artifact": "causal_question.yaml",
                    "path_hint": "causal_question.yaml"
                },
                {
                    "artifact": "design_risk.md",
                    "path_hint": "design_risk.md"
                }
            ],
            "gates": [
                {
                    "name": "one_sentence_design",
                    "type": "human"
                },
                {
                    "name": "artifact_presence",
                    "type": "automated",
                    "command": "python3 scripts/21_route_next_workflow.py"
                }
            ],
            "human_checkpoints": [
                "\u9898\u76ee\u662f\u5426\u503c\u5f97\u7ee7\u7eed",
                "\u8d21\u732e\u662f\u5426\u8db3\u4ee5\u6210\u6587",
                "\u8bc6\u522b\u5047\u8bbe\u662f\u5426\u53ef\u4ee5\u63a5\u53d7"
            ],
            "stop_conditions": [
                "treatment \u4e0d\u6e05\u695a",
                "outcome \u4e0d\u6e05\u695a",
                "\u6570\u636e\u4e0d\u80fd\u56de\u7b54\u95ee\u9898",
                "\u8d21\u732e\u5f31\u5230\u4e0d\u503c\u5f97\u7ee7\u7eed"
            ],
            "rollback_to": null,
            "skills": [
                "aer-topic-selection"
            ],
            "failure_codes": [
                "DESIGN_TREATMENT_UNCLEAR",
                "DESIGN_OUTCOME_UNCLEAR",
                "DESIGN_NO_CONTRIBUTION",
                "DESIGN_DATA_NOT_SUPPORTING",
                "DESIGN_HUMAN_REQUIRED"
            ],
            "current_issues": [],
            "spec_path": "workflows/agents/01_design.agent.md"
        },
        {
            "id": "02_literature",
            "step": "02",
            "name": "\u6587\u732e\u68c0\u7d22\u4e0e\u7efc\u8ff0",
            "purpose": "\u5efa\u7acb\u68c0\u7d22\u8ba1\u5212\u3001\u5019\u9009\u6c60\u3001closest papers \u548c\u8d21\u732e\u77e9\u9635\u3002",
            "agents": [
                "LiteratureSearchAgent",
                "MetadataVerifier",
                "PDFFetchAgent"
            ],
            "inputs": [
                "research_design.md",
                "concept_families",
                "method_keywords"
            ],
            "required_outputs": [
                {
                    "artifact": "query_plan.json",
                    "path_hint": "litreview/query_plan.json"
                },
                {
                    "artifact": "literature_candidates.csv",
                    "path_hint": "litreview/literature_candidates.csv"
                },
                {
                    "artifact": "references.bib",
                    "path_hint": "references.bib"
                },
                {
                    "artifact": "contribution_matrix.md",
                    "path_hint": "litreview/contribution_matrix.md"
                }
            ],
            "gates": [
                {
                    "name": "metadata_verified",
                    "type": "automated",
                    "command": "python3 scripts/15_verify_bibliography.py"
                },
                {
                    "name": "closest_papers_selected",
                    "type": "human"
                }
            ],
            "human_checkpoints": [
                "closest papers \u662f\u5426\u9009\u5bf9",
                "\u672c\u6587\u771f\u6b63 gap \u662f\u4ec0\u4e48"
            ],
            "stop_conditions": [
                "\u627e\u4e0d\u5230\u6700\u8fd1\u6587\u732e",
                "\u5f15\u7528\u65e0\u6cd5\u6838\u9a8c",
                "\u7efc\u8ff0\u53ea\u662f\u7f57\u5217"
            ],
            "rollback_to": "01_design",
            "skills": [
                "literature-review",
                "citation-management"
            ],
            "failure_codes": [
                "LIT_NO_CLOSEST_PAPERS",
                "LIT_METADATA_UNVERIFIED",
                "LIT_FULLTEXT_BLOCKED",
                "LIT_REVIEW_IS_LIST",
                "LIT_HUMAN_CLOSEST_REQUIRED"
            ],
            "current_issues": [
                "query_plan.json: not found at litreview/query_plan.json",
                "literature_candidates.csv: not found at litreview/literature_candidates.csv",
                "references.bib: not found at references.bib",
                "contribution_matrix.md: not found at litreview/contribution_matrix.md"
            ],
            "spec_path": "workflows/agents/02_literature.agent.md"
        },
        {
            "id": "03_paper_reading",
            "step": "03",
            "name": "\u8bba\u6587\u9605\u8bfb\u4e0e\u62c6\u89e3",
            "purpose": "\u628a\u6838\u5fc3\u6587\u732e\u8bfb\u5230\u8868\u683c\u3001\u65b9\u6cd5\u3001\u5c40\u9650\u548c\u53ef\u5f15\u7528\u8bc1\u636e\u4f4d\u7f6e\u3002",
            "agents": [
                "PaperReadingAgent",
                "EvidenceAuditor"
            ],
            "inputs": [
                "literature_candidates.csv",
                "pdf_or_html_files"
            ],
            "required_outputs": [
                {
                    "artifact": "lit_reading_notes/",
                    "path_hint": "litreview/notes/compressed/"
                },
                {
                    "artifact": "span_index.json",
                    "path_hint": "litreview/notes/span_index.json"
                },
                {
                    "artifact": "reading_state.md",
                    "path_hint": "litreview/notes/reading_state.md"
                }
            ],
            "gates": [
                {
                    "name": "source_spans_bound",
                    "type": "automated"
                },
                {
                    "name": "literature_role_confirmed",
                    "type": "human"
                }
            ],
            "human_checkpoints": [
                "\u6bcf\u7bc7\u6838\u5fc3\u6587\u732e\u5728\u672c\u6587\u91cc\u627f\u62c5\u4ec0\u4e48\u89d2\u8272"
            ],
            "stop_conditions": [
                "\u6838\u5fc3\u6587\u732e\u6ca1\u6709\u5168\u6587",
                "\u53ea\u6709\u6458\u8981\u7ea7\u7b14\u8bb0",
                "claim \u6ca1\u6709\u8bc1\u636e\u4f4d\u7f6e"
            ],
            "rollback_to": "02_literature",
            "skills": [
                "pdf",
                "paper-lookup",
                "literature-review"
            ],
            "failure_codes": [
                "READING_FULLTEXT_MISSING",
                "READING_ABSTRACT_ONLY",
                "READING_SPAN_MISSING",
                "READING_CLAIM_UNBOUND"
            ],
            "current_issues": [
                "lit_reading_notes/: not found at litreview/notes/compressed/",
                "span_index.json: not found at litreview/notes/span_index.json",
                "reading_state.md: not found at litreview/notes/reading_state.md"
            ],
            "spec_path": "workflows/agents/03_paper_reading.agent.md"
        },
        {
            "id": "04_data_gate",
            "step": "04",
            "name": "\u6570\u636e\u83b7\u53d6\u4e0e\u6e05\u6d17",
            "purpose": "\u8bc1\u660e\u6570\u636e\u80fd\u652f\u6491\u7814\u7a76\u95ee\u9898\uff0c\u5e76\u7559\u4e0b\u53ef\u590d\u73b0\u7684\u6570\u636e\u53e3\u5f84\u3002",
            "agents": [
                "DataPreparationAgent",
                "DataGateAuditor"
            ],
            "inputs": [
                "raw_data",
                "research_design.md",
                "variable_definitions_from_literature"
            ],
            "required_outputs": [
                {
                    "artifact": "data_contract.md",
                    "path_hint": "artifacts/data_contract.md"
                },
                {
                    "artifact": "sample_attrition.csv",
                    "path_hint": "artifacts/sample_attrition.csv"
                },
                {
                    "artifact": "variable_dictionary.csv",
                    "path_hint": "artifacts/variable_dictionary.csv"
                },
                {
                    "artifact": "analysis_ready.*",
                    "path_hint": "artifacts/did_sample.pkl"
                },
                {
                    "artifact": "data_gate_report.md",
                    "path_hint": "artifacts/data_gate_report.md"
                }
            ],
            "gates": [
                {
                    "name": "data_gate_script",
                    "type": "automated",
                    "command": "python3 scripts/04_data_gate.py"
                },
                {
                    "name": "variable_mapping_confirmed",
                    "type": "human"
                }
            ],
            "human_checkpoints": [
                "\u53d8\u91cf\u66ff\u4ee3\u662f\u5426\u5408\u7406",
                "\u6570\u636e\u9650\u5236\u662f\u5426\u8981\u6c42\u6539\u9898"
            ],
            "stop_conditions": [
                "\u5904\u7406\u7ec4\u6216\u5bf9\u7167\u7ec4\u7f3a\u5931",
                "\u6837\u672c\u6d41\u5931\u65e0\u6cd5\u89e3\u91ca",
                "\u6587\u732e\u53e3\u5f84\u6620\u5c04\u4e0d\u4e0a"
            ],
            "rollback_to": "01_design",
            "skills": [
                "StatsPAI_skill",
                "polars",
                "spreadsheets:Spreadsheets"
            ],
            "failure_codes": [
                "DATA_RAW_MISSING",
                "DATA_KEY_VARIABLE_MISSING",
                "DATA_SAMPLE_ATTRITION_UNEXPLAINED",
                "DATA_PANEL_INVALID",
                "DATA_HUMAN_VARIABLE_REQUIRED"
            ],
            "current_issues": [
                "data_contract.md: not found at artifacts/data_contract.md",
                "sample_attrition.csv: not found at artifacts/sample_attrition.csv",
                "variable_dictionary.csv: not found at artifacts/variable_dictionary.csv",
                "analysis_ready.*: not found at artifacts/did_sample.pkl",
                "data_gate_report.md: not found at artifacts/data_gate_report.md"
            ],
            "spec_path": "workflows/agents/04_data_gate.agent.md"
        },
        {
            "id": "05_causal_analysis",
            "step": "05",
            "name": "\u7edf\u8ba1\u5206\u6790\u4e0e\u56e0\u679c\u63a8\u65ad",
            "purpose": "\u8dd1\u4e3b\u6a21\u578b\u3001\u8bc6\u522b\u8bca\u65ad\u3001\u7a33\u5065\u6027\u548c\u5931\u8d25\u98ce\u9669\u8bb0\u5f55\u3002",
            "agents": [
                "CausalAnalysisAgent",
                "IdentificationAuditor",
                "RobustnessAuditor"
            ],
            "inputs": [
                "analysis_ready.*",
                "causal_question.yaml",
                "contribution_matrix.md"
            ],
            "required_outputs": [
                {
                    "artifact": "tables/",
                    "path_hint": "tables/"
                },
                {
                    "artifact": "figures/",
                    "path_hint": "figures/"
                },
                {
                    "artifact": "model_log.md",
                    "path_hint": "model_log.md"
                },
                {
                    "artifact": "robustness_report.md",
                    "path_hint": "robustness_report.md"
                }
            ],
            "gates": [
                {
                    "name": "rerun_core_models",
                    "type": "automated",
                    "command": "python3 scripts/05_event_study.py && python3 scripts/06_table2.py && python3 scripts/08_robustness.py"
                },
                {
                    "name": "claim_strength_confirmed",
                    "type": "human"
                }
            ],
            "human_checkpoints": [
                "\u7ed3\u679c\u662f\u5426\u8db3\u4ee5\u652f\u6491\u4e3b\u5f20",
                "\u662f\u5426\u56de\u9000\u6539\u8bbe\u8ba1"
            ],
            "stop_conditions": [
                "placebo \u660e\u663e\u5931\u8d25",
                "\u7ed3\u679c\u9ad8\u5ea6\u654f\u611f",
                "\u8bc6\u522b\u5047\u8bbe\u7ad9\u4e0d\u4f4f"
            ],
            "rollback_to": "01_design",
            "skills": [
                "StatsPAI_skill",
                "aer-identification",
                "aer-robustness",
                "pyfixest"
            ],
            "failure_codes": [
                "CAUSAL_ESTIMAND_UNCLEAR",
                "CAUSAL_PLACEBO_FAILS",
                "CAUSAL_RESULT_OVERCLAIMED",
                "CAUSAL_ROLLOUT_DATA_INCOMPLETE",
                "CAUSAL_HUMAN_CLAIM_REQUIRED"
            ],
            "current_issues": [
                "tables/: not found at tables/",
                "figures/: not found at figures/",
                "model_log.md: not found at model_log.md",
                "robustness_report.md: not found at robustness_report.md"
            ],
            "spec_path": "workflows/agents/05_causal_analysis.agent.md"
        },
        {
            "id": "06_writing",
            "step": "06",
            "name": "\u8bba\u6587\u5199\u4f5c",
            "purpose": "\u628a\u7814\u7a76\u8bbe\u8ba1\u3001\u6587\u732e\u3001\u6570\u636e\u548c\u7ed3\u679c\u7ec4\u7ec7\u6210\u8bc1\u636e\u7ea6\u675f\u4e0b\u7684\u8349\u7a3f\u3002",
            "agents": [
                "WritingAgent",
                "ClaimBinder"
            ],
            "inputs": [
                "research_design.md",
                "contribution_matrix.md",
                "data_gate_report.md",
                "tables/",
                "figures/"
            ],
            "required_outputs": [
                {
                    "artifact": "paper.tex",
                    "path_hint": "paper.tex"
                },
                {
                    "artifact": "paper.pdf",
                    "path_hint": "paper.pdf"
                }
            ],
            "gates": [
                {
                    "name": "latex_compile",
                    "type": "automated",
                    "command": "xelatex -interaction=nonstopmode paper.tex"
                },
                {
                    "name": "main_claim_confirmed",
                    "type": "human"
                }
            ],
            "human_checkpoints": [
                "\u8bba\u6587\u4e3b\u7ebf",
                "\u8d21\u732e\u8868\u8ff0",
                "\u7ed3\u8bba\u4fdd\u5b88\u7a0b\u5ea6"
            ],
            "stop_conditions": [
                "\u7ed3\u679c\u89e3\u91ca\u8d85\u8fc7\u8bc1\u636e",
                "\u8d21\u732e\u53e5\u8bf4\u4e0d\u6e05",
                "\u7ae0\u8282\u4e92\u76f8\u4e0d\u4e00\u81f4"
            ],
            "rollback_to": "05_causal_analysis",
            "skills": [
                "paper-writing",
                "aer-introduction",
                "scientific-writing"
            ],
            "failure_codes": [
                "WRITING_CLAIM_UNBOUND",
                "WRITING_OVERCLAIMED_RESULT",
                "WRITING_CONTRIBUTION_UNCLEAR",
                "WRITING_SECTION_MISMATCH",
                "WRITING_HUMAN_CLAIM_REQUIRED"
            ],
            "current_issues": [
                "paper.tex: not found at paper.tex",
                "paper.pdf: not found at paper.pdf"
            ],
            "spec_path": "workflows/agents/06_writing.agent.md"
        },
        {
            "id": "07_revision",
            "step": "07",
            "name": "\u8bba\u6587\u4fee\u6539\u4e0e\u6da6\u8272",
            "purpose": "\u5148\u4fee\u5ba1\u7a3f\u98ce\u9669\u548c\u8bba\u8bc1\u7ed3\u6784\uff0c\u518d\u505a\u8bed\u8a00\u6da6\u8272\u3002",
            "agents": [
                "ReviewerAgent",
                "RevisionPlanner",
                "PolishAgent"
            ],
            "inputs": [
                "paper.tex",
                "paper.pdf",
                "tables/",
                "figures/"
            ],
            "required_outputs": [
                {
                    "artifact": "review_report.md",
                    "path_hint": "review_report.md"
                },
                {
                    "artifact": "revision_plan.md",
                    "path_hint": "revision_plan.md"
                },
                {
                    "artifact": "draft_revised.*",
                    "path_hint": "draft_revised.*"
                }
            ],
            "gates": [
                {
                    "name": "major_concerns_resolved",
                    "type": "human"
                },
                {
                    "name": "paper_compile_after_revision",
                    "type": "automated",
                    "command": "xelatex -interaction=nonstopmode paper.tex"
                }
            ],
            "human_checkpoints": [
                "\u54ea\u4e9b\u95ee\u9898\u63a5\u53d7",
                "\u54ea\u4e9b\u98ce\u9669\u5199\u6210\u5c40\u9650",
                "\u662f\u5426\u9700\u8981\u65b0\u589e\u5206\u6790"
            ],
            "stop_conditions": [
                "\u53ea\u6539\u8bed\u8a00\u4e0d\u6539\u8bba\u8bc1",
                "\u4fee\u6539\u540e\u548c\u7ed3\u679c\u4e0d\u4e00\u81f4"
            ],
            "rollback_to": "06_writing",
            "skills": [
                "peer-review",
                "edit-article",
                "aer-robustness"
            ],
            "failure_codes": [
                "REVISION_LANGUAGE_ONLY",
                "REVISION_RESULT_MISMATCH",
                "REVISION_MAJOR_UNRESOLVED",
                "REVISION_NEW_ANALYSIS_UNVERIFIED",
                "REVISION_HUMAN_DECISION_REQUIRED"
            ],
            "current_issues": [
                "review_report.md: not found at review_report.md",
                "revision_plan.md: not found at revision_plan.md",
                "draft_revised.*: not found at draft_revised.*"
            ],
            "spec_path": "workflows/agents/07_revision.agent.md"
        },
        {
            "id": "08_format_citation",
            "step": "08",
            "name": "\u5f15\u7528\u7ba1\u7406\u4e0e\u6392\u7248",
            "purpose": "\u628a\u8bba\u6587\u6574\u7406\u6210\u5f15\u7528\u3001\u8868\u56fe\u3001\u6392\u7248\u4e00\u81f4\u7684\u53ef\u63d0\u4ea4\u6587\u4ef6\u3002",
            "agents": [
                "CitationFormatAgent",
                "ReferenceVerifier",
                "LayoutAgent"
            ],
            "inputs": [
                "paper.tex",
                "references.bib",
                "paper_tables/",
                "figures/"
            ],
            "required_outputs": [
                {
                    "artifact": "verified_bibliography.csv",
                    "path_hint": "verified_bibliography.csv"
                },
                {
                    "artifact": "paper.pdf",
                    "path_hint": "paper.pdf"
                }
            ],
            "gates": [
                {
                    "name": "bibliography_verified",
                    "type": "automated",
                    "command": "python3 scripts/15_verify_bibliography.py"
                },
                {
                    "name": "layout_clean",
                    "type": "automated"
                }
            ],
            "human_checkpoints": [
                "\u76ee\u6807\u671f\u520a\u6216\u5b66\u6821\u683c\u5f0f\u662f\u5426\u63a5\u53d7"
            ],
            "stop_conditions": [
                "\u5047\u5f15\u7528",
                "\u6f0f\u5f15\u7528",
                "\u8868\u56fe\u7f16\u53f7\u4e0d\u4e00\u81f4",
                "\u8868\u683c\u4e0d\u53ef\u8bfb"
            ],
            "rollback_to": "07_revision",
            "skills": [
                "citation-management",
                "aer-tables-figures",
                "latex:latex-compile"
            ],
            "failure_codes": [
                "FORMAT_FAKE_CITATION",
                "FORMAT_MISSING_CITATION",
                "FORMAT_UNUSED_REFERENCE",
                "FORMAT_TABLE_UNREADABLE",
                "FORMAT_LAYOUT_WARNING"
            ],
            "current_issues": [
                "verified_bibliography.csv: not found at verified_bibliography.csv",
                "paper.pdf: not found at paper.pdf"
            ],
            "spec_path": "workflows/agents/08_format_citation.agent.md"
        },
        {
            "id": "09_replication",
            "step": "09",
            "name": "\u8bba\u6587\u590d\u73b0\u4e0e\u53ef\u590d\u73b0\u7814\u7a76",
            "purpose": "\u786e\u8ba4\u4ee3\u7801\u3001\u6570\u636e\u5165\u53e3\u3001\u73af\u5883\u548c\u8bba\u6587\u6570\u5b57\u80fd\u8ffd\u6eaf\u3002",
            "agents": [
                "ReproAgent",
                "EnvironmentAgent",
                "ArtifactAuditor"
            ],
            "inputs": [
                "scripts/",
                "run_manifest.json",
                "paper.tex",
                "tables/",
                "figures/"
            ],
            "required_outputs": [
                {
                    "artifact": "run_manifest.json",
                    "path_hint": "run_manifest.json"
                },
                {
                    "artifact": "repro_report.md",
                    "path_hint": "repro_report.md"
                },
                {
                    "artifact": "replication/README.md",
                    "path_hint": "replication/README.md"
                }
            ],
            "gates": [
                {
                    "name": "repro_hash_check",
                    "type": "automated",
                    "command": "python3 verify_repro.py"
                },
                {
                    "name": "data_release_boundary",
                    "type": "human"
                }
            ],
            "human_checkpoints": [
                "\u54ea\u4e9b\u6570\u636e\u80fd\u516c\u5f00",
                "\u54ea\u4e9b\u53ea\u80fd\u5199\u8bbf\u95ee\u8bf4\u660e"
            ],
            "stop_conditions": [
                "\u8def\u5f84\u4e0d\u53ef\u590d\u73b0",
                "\u7ed3\u679c\u548c\u8bba\u6587\u4e0d\u4e00\u81f4",
                "\u6570\u636e\u6743\u9650\u8fb9\u754c\u4e0d\u6e05"
            ],
            "rollback_to": "05_causal_analysis",
            "skills": [
                "aer-replication"
            ],
            "failure_codes": [
                "REPRO_HASH_DRIFT",
                "REPRO_PATH_PRIVATE",
                "REPRO_OUTPUT_UNTRACED",
                "REPRO_DATA_BOUNDARY_UNCLEAR",
                "REPRO_ENV_UNDOCUMENTED"
            ],
            "current_issues": [
                "run_manifest.json: not found at run_manifest.json",
                "repro_report.md: not found at repro_report.md",
                "replication/README.md: not found at replication/README.md"
            ],
            "spec_path": "workflows/agents/09_replication.agent.md"
        },
        {
            "id": "10_defense",
            "step": "10",
            "name": "\u5ba1\u7a3f\u56de\u590d\u4e0e\u5b66\u672f\u7b54\u8fa9",
            "purpose": "\u628a\u5ba1\u7a3f\u610f\u89c1\u53d8\u6210\u6709\u8bc1\u636e\u3001\u6709\u6539\u52a8\u4f4d\u7f6e\u7684\u56de\u5e94\u77e9\u9635\u3002",
            "agents": [
                "DefenseAgent",
                "EvidenceRouter",
                "ResponseWriter"
            ],
            "inputs": [
                "review_comments",
                "paper.tex",
                "revision_log.md",
                "tables/",
                "figures/"
            ],
            "required_outputs": [
                {
                    "artifact": "response_matrix.md",
                    "path_hint": "response_matrix.md"
                },
                {
                    "artifact": "defense_qa.md",
                    "path_hint": "defense_qa.md"
                },
                {
                    "artifact": "revision_log.md",
                    "path_hint": "revision_log.md"
                }
            ],
            "gates": [
                {
                    "name": "all_comments_answered",
                    "type": "human"
                },
                {
                    "name": "evidence_paths_exist",
                    "type": "automated"
                }
            ],
            "human_checkpoints": [
                "\u54ea\u4e9b\u8ba9\u6b65",
                "\u54ea\u4e9b\u575a\u6301",
                "\u6700\u7ec8\u7b54\u8fa9\u53e3\u5f84"
            ],
            "stop_conditions": [
                "\u6f0f\u56de\u610f\u89c1",
                "\u53ea\u89e3\u91ca\u4e0d\u4fee\u6539",
                "\u65b0\u589e\u5206\u6790\u65e0\u6cd5\u590d\u73b0"
            ],
            "rollback_to": "07_revision",
            "skills": [
                "aer-rebuttal",
                "aer-submission"
            ],
            "failure_codes": [
                "DEFENSE_COMMENT_UNANSWERED",
                "DEFENSE_NO_MANUSCRIPT_EDIT",
                "DEFENSE_EVIDENCE_MISSING",
                "DEFENSE_OVERDEFENDED",
                "DEFENSE_NEW_ANALYSIS_UNREPRODUCED"
            ],
            "current_issues": [
                "response_matrix.md: not found at response_matrix.md",
                "defense_qa.md: not found at defense_qa.md",
                "revision_log.md: not found at revision_log.md"
            ],
            "spec_path": "workflows/agents/10_defense.agent.md"
        }
    ]
}
```

### `python3 -m json.tool workflows/schemas/runbook_state.schema.json`

- exit: 0

stdout:

```text
{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "StatspAI Workflow Runbook State",
    "type": "object",
    "required": [
        "version",
        "layer",
        "status",
        "source_registry",
        "source_artifact_registry",
        "api_contract",
        "current_route",
        "artifact_status",
        "spec_coverage",
        "workflows"
    ],
    "additionalProperties": false,
    "properties": {
        "version": {
            "type": "string"
        },
        "layer": {
            "type": "string",
            "enum": [
                "second"
            ]
        },
        "status": {
            "type": "string",
            "enum": [
                "pass",
                "partial"
            ]
        },
        "source_registry": {
            "type": "string"
        },
        "source_artifact_registry": {
            "type": "string"
        },
        "api_contract": {
            "type": "string"
        },
        "current_route": {
            "type": "object",
            "required": [
                "next_workflow_id",
                "next_workflow_name",
                "reason"
            ],
            "additionalProperties": false,
            "properties": {
                "next_workflow_id": {
                    "type": [
                        "string",
                        "null"
                    ]
                },
                "next_workflow_name": {
                    "type": [
                        "string",
                        "null"
                    ]
                },
                "reason": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                }
            }
        },
        "artifact_status": {
            "type": "object",
            "required": [
                "present",
                "partial",
                "missing",
                "external"
            ],
            "additionalProperties": false,
            "properties": {
                "present": {
                    "type": "integer"
                },
                "partial": {
                    "type": "integer"
                },
                "missing": {
                    "type": "integer"
                },
                "external": {
                    "type": "integer"
                }
            }
        },
        "spec_coverage": {
            "type": "object",
            "required": [
                "core_workflows",
                "missing_specs"
            ],
            "additionalProperties": false,
            "properties": {
                "core_workflows": {
                    "type": "integer"
                },
                "missing_specs": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                }
            }
        },
        "workflows": {
            "type": "array",
            "items": {
                "type": "object",
                "required": [
                    "id",
                    "step",
                    "name",
                    "purpose",
                    "agents",
                    "inputs",
                    "required_outputs",
                    "gates",
                    "human_checkpoints",
                    "stop_conditions",
                    "rollback_to",
                    "skills",
                    "failure_codes",
                    "current_issues",
                    "spec_path"
                ],
                "additionalProperties": false,
                "properties": {
                    "id": {
                        "type": "string"
                    },
                    "step": {
                        "type": "string"
                    },
                    "name": {
                        "type": "string"
                    },
                    "purpose": {
                        "type": "string"
                    },
                    "agents": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "inputs": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "required_outputs": {
                        "type": "array"
                    },
                    "gates": {
                        "type": "array"
                    },
                    "human_checkpoints": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "stop_conditions": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "rollback_to": {
                        "type": [
                            "string",
                            "null"
                        ]
                    },
                    "skills": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "failure_codes": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "current_issues": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "spec_path": {
                        "type": [
                            "string",
                            "null"
                        ]
                    }
                }
            }
        }
    }
}
```

### `python3 -m json.tool workflows/memory_index.json`

- exit: 0

stdout:

```text
{
    "version": "0.1",
    "layer": "second",
    "purpose": "Define what memory is loaded, when it is loaded, and where new durable information is written.",
    "memory_classes": [
        {
            "id": "system_instruction",
            "kind": "instruction",
            "scope": "system",
            "shared": true,
            "default_load": true,
            "paths": [],
            "update_policy": "Not editable from this project."
        },
        {
            "id": "project_instruction",
            "kind": "instruction",
            "scope": "project",
            "shared": true,
            "default_load": true,
            "paths": [
                "AGENTS.md",
                "tasks/agent-loop.md"
            ],
            "update_policy": "Stable project rules only."
        },
        {
            "id": "workflow_procedure",
            "kind": "procedural",
            "scope": "project",
            "shared": true,
            "default_load": false,
            "paths": [
                "tasks/pipeline-contract.md",
                "workflows/registry.json",
                "workflows/agents/",
                "workflows/api_contract.md"
            ],
            "update_policy": "Keep registry, agent specs, schemas, and validators in sync."
        },
        {
            "id": "project_episode",
            "kind": "episodic",
            "scope": "project",
            "shared": true,
            "default_load": true,
            "paths": [
                "tasks/todo.md",
                "tasks/lessons.md",
                "artifacts/*_report.md"
            ],
            "update_policy": "Record completed work, verification evidence, and remaining risks."
        },
        {
            "id": "domain_semantic",
            "kind": "semantic",
            "scope": "project",
            "shared": true,
            "default_load": false,
            "paths": [
                "litreview/",
                "artifacts/",
                "templates/aers/",
                "tasks/aers-docs-skill-map.md"
            ],
            "update_policy": "Add evidence with source paths, spans, tables, or reports."
        },
        {
            "id": "local_private",
            "kind": "local",
            "scope": "local",
            "shared": false,
            "default_load": false,
            "paths": [
                ".agent-memory/local/",
                "*.local"
            ],
            "update_policy": "Local-only notes. Do not store secrets, cookies, or VPN sessions."
        },
        {
            "id": "user_global_learning",
            "kind": "learning",
            "scope": "user",
            "shared": false,
            "default_load": false,
            "paths": [
                "Codex memory",
                "Claude memory"
            ],
            "update_policy": "Use as retrieval hints; verify local project state before claiming current facts."
        },
        {
            "id": "role_agent_memory",
            "kind": "role",
            "scope": "agent",
            "shared": false,
            "default_load": false,
            "paths": [
                ".codex/agents/",
                "workflows/agents/"
            ],
            "update_policy": "Keep role memory isolated by task and return summarized results to the lead agent."
        }
    ],
    "load_profiles": [
        {
            "id": "default_turn",
            "always": [
                "AGENTS.md",
                "tasks/todo.md",
                "tasks/agent-loop.md"
            ],
            "conditional": [
                "recent relevant artifacts"
            ],
            "never_default": [
                "raw data",
                "all PDFs",
                "all historical reports"
            ]
        },
        {
            "id": "workflow_task",
            "always": [
                "AGENTS.md",
                "tasks/todo.md",
                "tasks/agent-loop.md",
                "tasks/pipeline-contract.md",
                "workflows/registry.json"
            ],
            "conditional": [
                "workflows/agents/<current_step>.agent.md",
                "artifacts/workflow_runbook_state.json"
            ],
            "never_default": [
                "all workflows/agents/*.agent.md at once"
            ]
        },
        {
            "id": "literature_task",
            "always": [
                "AGENTS.md",
                "tasks/todo.md",
                "tasks/literature-workflow.md"
            ],
            "conditional": [
                "litreview/query_plan.json",
                "litreview/literature_candidates.csv",
                "litreview/contribution_matrix.md",
                "litreview/notes/compressed/<paper>.md"
            ],
            "never_default": [
                "unparsed PDFs"
            ]
        },
        {
            "id": "data_gate_task",
            "always": [
                "AGENTS.md",
                "tasks/todo.md",
                "tasks/data-workflow.md",
                "artifacts/data_contract.md"
            ],
            "conditional": [
                "artifacts/variable_dictionary.csv",
                "artifacts/sample_attrition.csv",
                "artifacts/panel_audit.csv",
                "scripts/04_data_gate.py"
            ],
            "never_default": [
                "raw data files"
            ]
        },
        {
            "id": "product_api_task",
            "always": [
                "AGENTS.md",
                "tasks/todo.md",
                "workflows/api_contract.md",
                "artifacts/workflow_runbook_state.json"
            ],
            "conditional": [
                "workflows/schemas/*.schema.json",
                "artifacts/workflow_runbook_report.md"
            ],
            "never_default": [
                "raw research data"
            ]
        }
    ],
    "write_targets": [
        {
            "id": "stable_rules",
            "paths": [
                "AGENTS.md",
                "tasks/context-loading-strategy.md"
            ],
            "allowed_content": "Long-lived instructions and loading rules."
        },
        {
            "id": "user_corrections",
            "paths": [
                "tasks/lessons.md"
            ],
            "allowed_content": "Durable lessons from explicit user corrections."
        },
        {
            "id": "task_progress",
            "paths": [
                "tasks/todo.md"
            ],
            "allowed_content": "Status, evidence, next task, and remaining risk."
        },
        {
            "id": "validation_reports",
            "paths": [
                "artifacts/*_report.md"
            ],
            "allowed_content": "Repeatable validation results."
        },
        {
            "id": "machine_state",
            "paths": [
                "artifacts/*.json"
            ],
            "allowed_content": "Third-layer readable state, no secrets."
        },
        {
            "id": "local_private_notes",
            "paths": [
                ".agent-memory/local/",
                "*.local"
            ],
            "allowed_content": "Local non-secret notes that must not be committed."
        }
    ],
    "forbidden_memory": [
        "passwords",
        "API keys",
        "cookies",
        "VPN sessions",
        "CNKI session tokens",
        "raw personal data extracts"
    ],
    "context_budget": {
        "max_project_instruction_lines": 200,
        "load_current_agent_spec_only": true,
        "load_raw_pdf_by_default": false,
        "load_raw_data_by_default": false,
        "prefer_summary_artifacts": true
    },
    "validators": [
        "scripts/26_validate_context_strategy.py",
        "scripts/25_agent_runtime_preflight.py"
    ]
}
```

### `python3 -m json.tool workflows/schemas/memory_index.schema.json`

- exit: 0

stdout:

```text
{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "StatspAI Memory Index",
    "type": "object",
    "required": [
        "version",
        "layer",
        "purpose",
        "memory_classes",
        "load_profiles",
        "write_targets",
        "forbidden_memory",
        "context_budget",
        "validators"
    ],
    "additionalProperties": false,
    "properties": {
        "version": {
            "type": "string"
        },
        "layer": {
            "type": "string",
            "enum": [
                "second"
            ]
        },
        "purpose": {
            "type": "string"
        },
        "memory_classes": {
            "type": "array",
            "items": {
                "type": "object",
                "required": [
                    "id",
                    "kind",
                    "scope",
                    "shared",
                    "default_load",
                    "paths",
                    "update_policy"
                ],
                "additionalProperties": false,
                "properties": {
                    "id": {
                        "type": "string"
                    },
                    "kind": {
                        "type": "string",
                        "enum": [
                            "instruction",
                            "procedural",
                            "episodic",
                            "semantic",
                            "local",
                            "learning",
                            "role"
                        ]
                    },
                    "scope": {
                        "type": "string",
                        "enum": [
                            "system",
                            "project",
                            "local",
                            "user",
                            "agent"
                        ]
                    },
                    "shared": {
                        "type": "boolean"
                    },
                    "default_load": {
                        "type": "boolean"
                    },
                    "paths": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "update_policy": {
                        "type": "string"
                    }
                }
            }
        },
        "load_profiles": {
            "type": "array",
            "items": {
                "type": "object",
                "required": [
                    "id",
                    "always",
                    "conditional",
                    "never_default"
                ],
                "additionalProperties": false,
                "properties": {
                    "id": {
                        "type": "string"
                    },
                    "always": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "conditional": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "never_default": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    }
                }
            }
        },
        "write_targets": {
            "type": "array",
            "items": {
                "type": "object",
                "required": [
                    "id",
                    "paths",
                    "allowed_content"
                ],
                "additionalProperties": false,
                "properties": {
                    "id": {
                        "type": "string"
                    },
                    "paths": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "allowed_content": {
                        "type": "string"
                    }
                }
            }
        },
        "forbidden_memory": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "context_budget": {
            "type": "object",
            "required": [
                "max_project_instruction_lines",
                "load_current_agent_spec_only",
                "load_raw_pdf_by_default",
                "load_raw_data_by_default",
                "prefer_summary_artifacts"
            ],
            "additionalProperties": false,
            "properties": {
                "max_project_instruction_lines": {
                    "type": "integer"
                },
                "load_current_agent_spec_only": {
                    "type": "boolean"
                },
                "load_raw_pdf_by_default": {
                    "type": "boolean"
                },
                "load_raw_data_by_default": {
                    "type": "boolean"
                },
                "prefer_summary_artifacts": {
                    "type": "boolean"
                }
            }
        },
        "validators": {
            "type": "array",
            "items": {
                "type": "string"
            }
        }
    }
}
```

### `python3 -m json.tool workflows/tool_adapters.json`

- exit: 0

stdout:

```text
{
    "version": "0.1",
    "layer": "second",
    "purpose": "Project-level tool adapter registry for the empirical paper workflow runtime.",
    "adapters": [
        {
            "id": "workflow_preflight",
            "category": "workflow_validation",
            "description": "Run deterministic second-layer workflow checks before runtime or product handoff.",
            "workflows": [
                "all"
            ],
            "owner_agents": [
                "RouterAgent",
                "ArtifactAuditor"
            ],
            "commands": [
                "python3 scripts/25_agent_runtime_preflight.py"
            ],
            "inputs": [
                "workflows/registry.json",
                "workflows/agents/",
                "workflows/schemas/",
                "artifacts/workflow_runbook_state.json"
            ],
            "outputs": [
                "artifacts/agent_runtime_preflight_report.md"
            ],
            "network_required": false,
            "human_auth_required": false,
            "side_effect_level": "writes_reports",
            "allowed_in_orchestrator": true,
            "risks": [
                "Preflight can refresh report timestamps but must not change research estimates."
            ],
            "verification": [
                "report status is PASS",
                "runtime runbook remains executable"
            ],
            "trace_required": true
        },
        {
            "id": "workflow_runbook",
            "category": "workflow_state",
            "description": "Generate current workflow route, coverage, gates, failure codes, and JSON state.",
            "workflows": [
                "all"
            ],
            "owner_agents": [
                "RouterAgent"
            ],
            "commands": [
                "python3 scripts/23_workflow_runbook.py",
                "python3 scripts/24_validate_runbook_api.py"
            ],
            "inputs": [
                "workflows/registry.json",
                "Tasks/artifact-registry.md"
            ],
            "outputs": [
                "artifacts/workflow_runbook_report.md",
                "artifacts/workflow_runbook_state.json",
                "artifacts/workflow_api_validation_report.md"
            ],
            "network_required": false,
            "human_auth_required": false,
            "side_effect_level": "writes_state",
            "allowed_in_orchestrator": true,
            "risks": [
                "State can be stale if artifact registry is stale."
            ],
            "verification": [
                "runbook reports NEXT none or next workflow",
                "API validation PASS"
            ],
            "trace_required": true
        },
        {
            "id": "literature_metadata_verifier",
            "category": "literature",
            "description": "Validate bibliography keys, citation coverage, and unused or incomplete references.",
            "workflows": [
                "02_literature",
                "08_format_citation"
            ],
            "owner_agents": [
                "MetadataVerifier",
                "ReferenceVerifier"
            ],
            "commands": [
                "python3 scripts/15_verify_bibliography.py"
            ],
            "inputs": [
                "paper.tex",
                "references.bib"
            ],
            "outputs": [
                "verified_bibliography.csv",
                "artifacts/bibliography_verification_report.md"
            ],
            "network_required": false,
            "human_auth_required": false,
            "side_effect_level": "writes_reports",
            "allowed_in_orchestrator": true,
            "risks": [
                "Metadata completeness is structural; DOI truth still needs source checks when disputed."
            ],
            "verification": [
                "fail count is 0",
                "unused references are 0 or justified"
            ],
            "trace_required": true
        },
        {
            "id": "pdf_fetch_scansci",
            "category": "literature_fetch",
            "description": "Fetch legally available PDFs or institutional-access PDFs when the user is authenticated.",
            "workflows": [
                "02_literature",
                "03_paper_reading"
            ],
            "owner_agents": [
                "PDFFetchAgent"
            ],
            "commands": [
                "scansci-pdf run"
            ],
            "inputs": [
                "DOI",
                "BibTeX",
                "institution access when authorized"
            ],
            "outputs": [
                "lit_pdfs/",
                "references.bib candidate entries"
            ],
            "network_required": true,
            "human_auth_required": true,
            "side_effect_level": "external_download",
            "allowed_in_orchestrator": false,
            "risks": [
                "Requires legal access boundary; cannot store cookies or VPN sessions."
            ],
            "verification": [
                "downloaded file exists",
                "failure reason recorded",
                "legal access mode documented"
            ],
            "trace_required": true
        },
        {
            "id": "cnki_browser_hqu",
            "category": "literature_fetch",
            "description": "Use the user's already-authenticated HQU VPN browser session for CNKI retrieval.",
            "workflows": [
                "02_literature",
                "03_paper_reading"
            ],
            "owner_agents": [
                "PDFFetchAgent",
                "PaperReadingAgent"
            ],
            "commands": [
                "Chrome user session"
            ],
            "inputs": [
                "user-authenticated HQU VPN",
                "CNKI page URL",
                "paper title"
            ],
            "outputs": [
                "lit_pdfs/cnki_vpn_test/",
                "parsed text when available"
            ],
            "network_required": true,
            "human_auth_required": true,
            "side_effect_level": "browser_download",
            "allowed_in_orchestrator": false,
            "risks": [
                "Credential-gated; must not persist session secrets; must record source and access boundary."
            ],
            "verification": [
                "PDF exists",
                "pdftotext or parser can read file",
                "source URL or title recorded"
            ],
            "trace_required": true
        },
        {
            "id": "data_gate_runner",
            "category": "data",
            "description": "Audit analysis-ready data, variables, attrition, and panel structure.",
            "workflows": [
                "04_data_gate"
            ],
            "owner_agents": [
                "DataPreparationAgent",
                "DataGateAuditor"
            ],
            "commands": [
                "python3 scripts/04_data_gate.py"
            ],
            "inputs": [
                "artifacts/did_sample.pkl",
                "research_design.md",
                "causal_question.yaml"
            ],
            "outputs": [
                "artifacts/data_contract.md",
                "artifacts/data_gate_report.md",
                "artifacts/sample_attrition.csv",
                "artifacts/variable_dictionary.csv",
                "artifacts/panel_audit.csv"
            ],
            "network_required": false,
            "human_auth_required": false,
            "side_effect_level": "writes_reports",
            "allowed_in_orchestrator": true,
            "risks": [
                "Cannot judge whether variable proxies are academically acceptable."
            ],
            "verification": [
                "data gate report exists",
                "variable dictionary exists",
                "panel audit exists"
            ],
            "trace_required": true
        },
        {
            "id": "causal_analysis_runner",
            "category": "statistics",
            "description": "Run core DID, robustness, supplemental figures, tables, and revision robustness checks.",
            "workflows": [
                "05_causal_analysis",
                "07_revision"
            ],
            "owner_agents": [
                "CausalAnalysisAgent",
                "IdentificationAuditor",
                "RobustnessAuditor"
            ],
            "commands": [
                "python3 scripts/05_event_study.py",
                "python3 scripts/06_table2.py",
                "python3 scripts/08_robustness.py",
                "python3 scripts/09_supplemental.py",
                "python3 scripts/10_aer_regtable.py",
                "python3 scripts/13_revision_robustness.py"
            ],
            "inputs": [
                "artifacts/did_sample.pkl",
                "causal_question.yaml",
                "model_log.md"
            ],
            "outputs": [
                "tables/",
                "figures/",
                "paper_tables/",
                "artifacts/analysis_rerun_report.md",
                "artifacts/revision_robustness_report.md"
            ],
            "network_required": false,
            "human_auth_required": false,
            "side_effect_level": "rewrites_results",
            "allowed_in_orchestrator": false,
            "risks": [
                "Can change tables and figures; must be followed by project-specific reproducibility checks."
            ],
            "verification": [
                "model report updated",
                "table and figure files exist",
                "claim language remains aligned"
            ],
            "trace_required": true
        },
        {
            "id": "latex_compile",
            "category": "document_build",
            "description": "Compile the paper and bibliography into a readable PDF.",
            "workflows": [
                "06_writing",
                "07_revision",
                "08_format_citation"
            ],
            "owner_agents": [
                "WritingAgent",
                "LayoutAgent"
            ],
            "commands": [
                "xelatex -interaction=nonstopmode paper.tex",
                "bibtex paper",
                "xelatex -interaction=nonstopmode paper.tex",
                "xelatex -interaction=nonstopmode paper.tex"
            ],
            "inputs": [
                "paper.tex",
                "references.bib",
                "paper_tables/",
                "figures/"
            ],
            "outputs": [
                "paper.pdf",
                "paper.log"
            ],
            "network_required": false,
            "human_auth_required": false,
            "side_effect_level": "build_artifacts",
            "allowed_in_orchestrator": true,
            "risks": [
                "Warnings may be hidden unless paper.log is inspected."
            ],
            "verification": [
                "paper.pdf exists",
                "no undefined citation/reference",
                "no overfull table warnings for final pass"
            ],
            "trace_required": true
        },
        {
            "id": "reproduction_verify",
            "category": "replication",
            "description": "Run a template-safe runtime reproducibility smoke check.",
            "workflows": [
                "09_replication"
            ],
            "owner_agents": [
                "ReproAgent",
                "ArtifactAuditor"
            ],
            "commands": [
                "python3 scripts/23_workflow_runbook.py"
            ],
            "inputs": [
                "workflows/registry.json",
                "workflows/agents/"
            ],
            "outputs": [
                "artifacts/workflow_runbook_report.md",
                "artifacts/workflow_runbook_state.json"
            ],
            "network_required": false,
            "human_auth_required": false,
            "side_effect_level": "read_only",
            "allowed_in_orchestrator": true,
            "risks": [
                "This only verifies runtime wiring; paper-specific reproducibility must be added per project."
            ],
            "verification": [
                "workflow runbook command exits 0"
            ],
            "trace_required": true
        },
        {
            "id": "browser_preview",
            "category": "human_review",
            "description": "Open generated reports or PDFs in Chrome for user-facing inspection.",
            "workflows": [
                "all"
            ],
            "owner_agents": [
                "LeadAgent"
            ],
            "commands": [
                "open -a 'Google Chrome' <path>"
            ],
            "inputs": [
                "paper.pdf",
                "artifacts/*_report.md",
                "tasks/*.md"
            ],
            "outputs": [
                "Chrome window/tab"
            ],
            "network_required": false,
            "human_auth_required": false,
            "side_effect_level": "local_preview",
            "allowed_in_orchestrator": true,
            "risks": [
                "Opening the wrong artifact can mislead manual review."
            ],
            "verification": [
                "requested artifact path opened after generation"
            ],
            "trace_required": true
        },
        {
            "id": "policy_rollout_builder",
            "category": "policy_data",
            "description": "Build the seed policy rollout layer for future province-level ATT upgrades.",
            "workflows": [
                "05x_policy_rollout_data_layer"
            ],
            "owner_agents": [
                "PolicyDataAgent",
                "MergeAuditor"
            ],
            "commands": [
                "python3 scripts/16_build_policy_rollout.py"
            ],
            "inputs": [
                "data/policy/urbmi_ncms_rollout_sources.csv"
            ],
            "outputs": [
                "data/policy/policy_rollout_clean.csv",
                "artifacts/policy_rollout_merge_report.md"
            ],
            "network_required": false,
            "human_auth_required": false,
            "side_effect_level": "writes_policy_data",
            "allowed_in_orchestrator": false,
            "risks": [
                "Seed layer is not enough to upgrade identification design."
            ],
            "verification": [
                "merge report exists",
                "usable_for_att boundary recorded"
            ],
            "trace_required": true
        }
    ]
}
```

### `python3 -m json.tool workflows/schemas/tool_adapters.schema.json`

- exit: 0

stdout:

```text
{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "StatspAI Tool Adapter Registry",
    "type": "object",
    "required": [
        "version",
        "layer",
        "purpose",
        "adapters"
    ],
    "additionalProperties": false,
    "properties": {
        "version": {
            "type": "string"
        },
        "layer": {
            "type": "string",
            "enum": [
                "second"
            ]
        },
        "purpose": {
            "type": "string"
        },
        "adapters": {
            "type": "array",
            "items": {
                "type": "object",
                "required": [
                    "id",
                    "category",
                    "description",
                    "workflows",
                    "owner_agents",
                    "commands",
                    "inputs",
                    "outputs",
                    "network_required",
                    "human_auth_required",
                    "side_effect_level",
                    "allowed_in_orchestrator",
                    "risks",
                    "verification",
                    "trace_required"
                ],
                "additionalProperties": false,
                "properties": {
                    "id": {
                        "type": "string"
                    },
                    "category": {
                        "type": "string"
                    },
                    "description": {
                        "type": "string"
                    },
                    "workflows": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "owner_agents": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "commands": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "inputs": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "outputs": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "network_required": {
                        "type": "boolean"
                    },
                    "human_auth_required": {
                        "type": "boolean"
                    },
                    "side_effect_level": {
                        "type": "string"
                    },
                    "allowed_in_orchestrator": {
                        "type": "boolean"
                    },
                    "risks": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "verification": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "trace_required": {
                        "type": "boolean"
                    }
                }
            }
        }
    }
}
```

### `python3 -m json.tool workflows/schemas/agent_trace.schema.json`

- exit: 0

stdout:

```text
{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "StatspAI Agent Trace Event",
    "type": "object",
    "required": [
        "run_id",
        "event_id",
        "timestamp",
        "mode",
        "actor",
        "workflow_id",
        "adapter_id",
        "decision",
        "action",
        "status",
        "reason",
        "failure_code",
        "commands",
        "command_results",
        "inputs",
        "outputs",
        "verification",
        "evidence"
    ],
    "additionalProperties": false,
    "properties": {
        "run_id": {
            "type": "string"
        },
        "event_id": {
            "type": "string"
        },
        "timestamp": {
            "type": "string"
        },
        "mode": {
            "type": "string",
            "enum": [
                "dry-run",
                "execute",
                "record"
            ]
        },
        "actor": {
            "type": "string"
        },
        "workflow_id": {
            "type": "string"
        },
        "adapter_id": {
            "type": "string"
        },
        "decision": {
            "type": "string",
            "enum": [
                "planned",
                "executed",
                "blocked",
                "failed",
                "recorded"
            ]
        },
        "action": {
            "type": "string"
        },
        "status": {
            "type": "string",
            "enum": [
                "pass",
                "fail",
                "blocked",
                "recorded"
            ]
        },
        "reason": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "failure_code": {
            "type": [
                "string",
                "null"
            ]
        },
        "commands": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "command_results": {
            "type": "array",
            "items": {
                "type": "object",
                "required": [
                    "command",
                    "argv",
                    "returncode",
                    "started_at",
                    "ended_at",
                    "stdout_summary",
                    "stderr_summary"
                ],
                "additionalProperties": false,
                "properties": {
                    "command": {
                        "type": "string"
                    },
                    "argv": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "returncode": {
                        "type": "integer"
                    },
                    "started_at": {
                        "type": "string"
                    },
                    "ended_at": {
                        "type": "string"
                    },
                    "stdout_summary": {
                        "type": "string"
                    },
                    "stderr_summary": {
                        "type": "string"
                    }
                }
            }
        },
        "inputs": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "outputs": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "verification": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "evidence": {
            "type": "array",
            "items": {
                "type": "string"
            }
        }
    }
}
```

### `python3 -m json.tool workflows/orchestrator_policy.json`

- exit: 0

stdout:

```text
{
    "version": "0.1",
    "layer": "second",
    "purpose": "Policy for safe local orchestration of registered tool adapters.",
    "default_mode": "dry-run",
    "trace_path": "artifacts/agent_trace_log.jsonl",
    "report_path": "artifacts/orchestrator_report.md",
    "state_path": "artifacts/orchestrator_run_state.json",
    "allow_execute_adapters": [
        "workflow_runbook",
        "literature_metadata_verifier",
        "data_gate_runner",
        "reproduction_verify"
    ],
    "dry_run_only_adapters": [
        "workflow_preflight",
        "latex_compile",
        "browser_preview"
    ],
    "blocked_adapters": [
        "pdf_fetch_scansci",
        "cnki_browser_hqu",
        "causal_analysis_runner",
        "policy_rollout_builder"
    ],
    "allowed_side_effect_levels": [
        "read_only",
        "writes_reports",
        "writes_state"
    ],
    "blocked_side_effect_levels": [
        "external_download",
        "browser_download",
        "rewrites_results",
        "build_artifacts",
        "local_preview",
        "writes_policy_data"
    ],
    "allow_network": false,
    "allow_human_auth": false,
    "allow_placeholder_commands": false,
    "allow_recursive_preflight": false,
    "command_allowlist": [
        "python3 scripts/23_workflow_runbook.py",
        "python3 scripts/24_validate_runbook_api.py",
        "python3 scripts/15_verify_bibliography.py",
        "python3 scripts/04_data_gate.py",
        "python3 scripts/27_validate_tool_adapters.py"
    ],
    "required_inputs": [
        "workflows/tool_adapters.json",
        "workflows/orchestrator_policy.json",
        "artifacts/workflow_runbook_state.json"
    ],
    "stop_conditions": [
        "adapter_not_registered",
        "adapter_not_allowed",
        "network_required",
        "human_auth_required",
        "blocked_side_effect",
        "command_not_allowlisted",
        "placeholder_command",
        "recursive_preflight",
        "command_failed"
    ]
}
```

### `python3 -m json.tool workflows/schemas/orchestrator_policy.schema.json`

- exit: 0

stdout:

```text
{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "StatspAI Orchestrator Policy",
    "type": "object",
    "required": [
        "version",
        "layer",
        "purpose",
        "default_mode",
        "trace_path",
        "report_path",
        "state_path",
        "allow_execute_adapters",
        "dry_run_only_adapters",
        "blocked_adapters",
        "allowed_side_effect_levels",
        "blocked_side_effect_levels",
        "allow_network",
        "allow_human_auth",
        "allow_placeholder_commands",
        "allow_recursive_preflight",
        "command_allowlist",
        "required_inputs",
        "stop_conditions"
    ],
    "additionalProperties": false,
    "properties": {
        "version": {
            "type": "string"
        },
        "layer": {
            "type": "string",
            "enum": [
                "second"
            ]
        },
        "purpose": {
            "type": "string"
        },
        "default_mode": {
            "type": "string",
            "enum": [
                "dry-run",
                "execute"
            ]
        },
        "trace_path": {
            "type": "string"
        },
        "report_path": {
            "type": "string"
        },
        "state_path": {
            "type": "string"
        },
        "allow_execute_adapters": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "dry_run_only_adapters": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "blocked_adapters": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "allowed_side_effect_levels": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "blocked_side_effect_levels": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "allow_network": {
            "type": "boolean"
        },
        "allow_human_auth": {
            "type": "boolean"
        },
        "allow_placeholder_commands": {
            "type": "boolean"
        },
        "allow_recursive_preflight": {
            "type": "boolean"
        },
        "command_allowlist": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "required_inputs": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "stop_conditions": {
            "type": "array",
            "items": {
                "type": "string"
            }
        }
    }
}
```

### `python3 -m json.tool workflows/schemas/orchestrator_run_state.schema.json`

- exit: 0

stdout:

```text
{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "StatspAI Orchestrator Run State",
    "type": "object",
    "required": [
        "version",
        "run_id",
        "mode",
        "status",
        "generated_at",
        "selected_adapters",
        "executed_commands",
        "blocked_adapters",
        "events",
        "report_path",
        "trace_path"
    ],
    "additionalProperties": false,
    "properties": {
        "version": {
            "type": "string"
        },
        "run_id": {
            "type": "string"
        },
        "mode": {
            "type": "string",
            "enum": [
                "dry-run",
                "execute"
            ]
        },
        "status": {
            "type": "string",
            "enum": [
                "pass",
                "fail",
                "blocked"
            ]
        },
        "generated_at": {
            "type": "string"
        },
        "selected_adapters": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "executed_commands": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "blocked_adapters": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "events": {
            "type": "array",
            "items": {
                "type": "object",
                "required": [
                    "adapter_id",
                    "decision",
                    "status",
                    "reason",
                    "failure_code",
                    "commands",
                    "command_results",
                    "inputs",
                    "outputs",
                    "verification"
                ],
                "additionalProperties": false,
                "properties": {
                    "adapter_id": {
                        "type": "string"
                    },
                    "decision": {
                        "type": "string",
                        "enum": [
                            "planned",
                            "executed",
                            "blocked",
                            "failed"
                        ]
                    },
                    "status": {
                        "type": "string",
                        "enum": [
                            "planned",
                            "pass",
                            "fail",
                            "blocked"
                        ]
                    },
                    "reason": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "failure_code": {
                        "type": [
                            "string",
                            "null"
                        ]
                    },
                    "commands": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "command_results": {
                        "type": "array"
                    },
                    "inputs": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "outputs": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "verification": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    }
                }
            }
        },
        "report_path": {
            "type": "string"
        },
        "trace_path": {
            "type": "string"
        }
    }
}
```

### `python3 -m json.tool artifacts/orchestrator_run_state.json`

- exit: 0

stdout:

```text
{
    "version": "0.1",
    "run_id": "p3-execute-20260622200927934234",
    "mode": "execute",
    "status": "pass",
    "generated_at": "2026-06-22T20:09:27+08:00",
    "selected_adapters": [
        "reproduction_verify"
    ],
    "executed_commands": [
        "python3 scripts/23_workflow_runbook.py"
    ],
    "blocked_adapters": [],
    "events": [
        {
            "adapter_id": "reproduction_verify",
            "decision": "executed",
            "status": "pass",
            "reason": [],
            "failure_code": null,
            "commands": [
                "python3 scripts/23_workflow_runbook.py"
            ],
            "command_results": [
                {
                    "command": "python3 scripts/23_workflow_runbook.py",
                    "argv": [
                        "python3",
                        "scripts/23_workflow_runbook.py"
                    ],
                    "returncode": 0,
                    "started_at": "2026-06-22T20:09:27+08:00",
                    "ended_at": "2026-06-22T20:09:27+08:00",
                    "stdout_summary": "NEXT 02_literature: \u6587\u732e\u68c0\u7d22\u4e0e\u7efc\u8ff0 workflows=10 missing_specs=0 report=artifacts/workflow_runbook_report.md json=artifacts/workflow_runbook_state.json",
                    "stderr_summary": ""
                }
            ],
            "inputs": [
                "workflows/registry.json",
                "workflows/agents/"
            ],
            "outputs": [
                "artifacts/workflow_runbook_report.md",
                "artifacts/workflow_runbook_state.json"
            ],
            "verification": [
                "workflow runbook command exits 0"
            ]
        }
    ],
    "report_path": "artifacts/orchestrator_report.md",
    "trace_path": "artifacts/agent_trace_log.jsonl"
}
```

### `python3 -m json.tool workflows/skill_subagent_registry.json`

- exit: 0

stdout:

```text
{
    "version": "0.1",
    "layer": "second",
    "purpose": "Register reusable project skills and native subagent specs for the empirical paper workflow runtime.",
    "skill_root": ".codex/skills",
    "native_agent_root": ".codex/agents",
    "skill_packages": [
        {
            "id": "statspai-empirical-workflow",
            "path": ".codex/skills/statspai-empirical-workflow",
            "skill_file": ".codex/skills/statspai-empirical-workflow/SKILL.md",
            "openai_metadata": ".codex/skills/statspai-empirical-workflow/agents/openai.yaml",
            "references": [
                ".codex/skills/statspai-empirical-workflow/references/workflow-map.md",
                ".codex/skills/statspai-empirical-workflow/references/orchestrator-policy.md"
            ],
            "covers_workflows": [
                "01_design",
                "02_literature",
                "03_paper_reading",
                "04_data_gate",
                "05_causal_analysis",
                "06_writing",
                "07_revision",
                "08_format_citation",
                "09_replication",
                "10_defense",
                "05x_policy_rollout_data_layer"
            ],
            "entry_commands": [
                "python3 scripts/23_workflow_runbook.py",
                "python3 scripts/24_validate_runbook_api.py",
                "python3 scripts/25_agent_runtime_preflight.py",
                "python3 scripts/28_agent_orchestrator.py --mode dry-run --no-trace"
            ],
            "safety_policy": "workflows/orchestrator_policy.json",
            "status": "registered"
        }
    ],
    "native_subagents": [
        {
            "id": "statspai-router",
            "path": ".codex/agents/statspai-router.toml",
            "role": "router",
            "covers_workflows": [
                "all"
            ],
            "allowed_adapters": [
                "workflow_runbook"
            ],
            "blocked_adapters": [
                "pdf_fetch_scansci",
                "cnki_browser_hqu",
                "causal_analysis_runner",
                "workflow_preflight"
            ],
            "status": "registered"
        },
        {
            "id": "statspai-literature",
            "path": ".codex/agents/statspai-literature.toml",
            "role": "literature",
            "covers_workflows": [
                "02_literature",
                "03_paper_reading"
            ],
            "allowed_adapters": [
                "literature_metadata_verifier"
            ],
            "blocked_adapters": [
                "pdf_fetch_scansci",
                "cnki_browser_hqu"
            ],
            "status": "registered"
        },
        {
            "id": "statspai-data-gate",
            "path": ".codex/agents/statspai-data-gate.toml",
            "role": "data",
            "covers_workflows": [
                "04_data_gate"
            ],
            "allowed_adapters": [
                "data_gate_runner"
            ],
            "blocked_adapters": [],
            "status": "registered"
        },
        {
            "id": "statspai-causal-analysis",
            "path": ".codex/agents/statspai-causal-analysis.toml",
            "role": "causal_analysis",
            "covers_workflows": [
                "05_causal_analysis",
                "05x_policy_rollout_data_layer"
            ],
            "allowed_adapters": [],
            "blocked_adapters": [
                "causal_analysis_runner",
                "policy_rollout_builder"
            ],
            "status": "registered"
        },
        {
            "id": "statspai-writing-review",
            "path": ".codex/agents/statspai-writing-review.toml",
            "role": "writing_review",
            "covers_workflows": [
                "06_writing",
                "07_revision",
                "08_format_citation",
                "10_defense"
            ],
            "allowed_adapters": [
                "literature_metadata_verifier"
            ],
            "blocked_adapters": [
                "latex_compile"
            ],
            "status": "registered"
        },
        {
            "id": "statspai-replication-verifier",
            "path": ".codex/agents/statspai-replication-verifier.toml",
            "role": "replication_verifier",
            "covers_workflows": [
                "09_replication"
            ],
            "allowed_adapters": [
                "reproduction_verify"
            ],
            "blocked_adapters": [],
            "status": "registered"
        }
    ],
    "workflow_bindings": [
        {
            "workflow_id": "01_design",
            "skill": "statspai-empirical-workflow",
            "subagents": [
                "statspai-router"
            ],
            "default_adapters": [
                "workflow_runbook"
            ],
            "human_gate": true
        },
        {
            "workflow_id": "02_literature",
            "skill": "statspai-empirical-workflow",
            "subagents": [
                "statspai-literature"
            ],
            "default_adapters": [
                "literature_metadata_verifier"
            ],
            "human_gate": true
        },
        {
            "workflow_id": "03_paper_reading",
            "skill": "statspai-empirical-workflow",
            "subagents": [
                "statspai-literature"
            ],
            "default_adapters": [
                "literature_metadata_verifier"
            ],
            "human_gate": true
        },
        {
            "workflow_id": "04_data_gate",
            "skill": "statspai-empirical-workflow",
            "subagents": [
                "statspai-data-gate"
            ],
            "default_adapters": [
                "data_gate_runner"
            ],
            "human_gate": true
        },
        {
            "workflow_id": "05_causal_analysis",
            "skill": "statspai-empirical-workflow",
            "subagents": [
                "statspai-causal-analysis"
            ],
            "default_adapters": [],
            "human_gate": true
        },
        {
            "workflow_id": "06_writing",
            "skill": "statspai-empirical-workflow",
            "subagents": [
                "statspai-writing-review"
            ],
            "default_adapters": [],
            "human_gate": true
        },
        {
            "workflow_id": "07_revision",
            "skill": "statspai-empirical-workflow",
            "subagents": [
                "statspai-writing-review"
            ],
            "default_adapters": [],
            "human_gate": true
        },
        {
            "workflow_id": "08_format_citation",
            "skill": "statspai-empirical-workflow",
            "subagents": [
                "statspai-writing-review",
                "statspai-literature"
            ],
            "default_adapters": [
                "literature_metadata_verifier"
            ],
            "human_gate": true
        },
        {
            "workflow_id": "09_replication",
            "skill": "statspai-empirical-workflow",
            "subagents": [
                "statspai-replication-verifier"
            ],
            "default_adapters": [
                "reproduction_verify"
            ],
            "human_gate": true
        },
        {
            "workflow_id": "10_defense",
            "skill": "statspai-empirical-workflow",
            "subagents": [
                "statspai-writing-review",
                "statspai-replication-verifier"
            ],
            "default_adapters": [],
            "human_gate": true
        },
        {
            "workflow_id": "05x_policy_rollout_data_layer",
            "skill": "statspai-empirical-workflow",
            "subagents": [
                "statspai-causal-analysis"
            ],
            "default_adapters": [],
            "human_gate": true
        }
    ]
}
```

### `python3 -m json.tool workflows/schemas/skill_subagent_registry.schema.json`

- exit: 0

stdout:

```text
{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "StatspAI Skill Subagent Registry",
    "type": "object",
    "required": [
        "version",
        "layer",
        "purpose",
        "skill_root",
        "native_agent_root",
        "skill_packages",
        "native_subagents",
        "workflow_bindings"
    ],
    "additionalProperties": false,
    "properties": {
        "version": {
            "type": "string"
        },
        "layer": {
            "type": "string",
            "enum": [
                "second"
            ]
        },
        "purpose": {
            "type": "string"
        },
        "skill_root": {
            "type": "string"
        },
        "native_agent_root": {
            "type": "string"
        },
        "skill_packages": {
            "type": "array",
            "items": {
                "type": "object",
                "required": [
                    "id",
                    "path",
                    "skill_file",
                    "openai_metadata",
                    "references",
                    "covers_workflows",
                    "entry_commands",
                    "safety_policy",
                    "status"
                ],
                "additionalProperties": false,
                "properties": {
                    "id": {
                        "type": "string"
                    },
                    "path": {
                        "type": "string"
                    },
                    "skill_file": {
                        "type": "string"
                    },
                    "openai_metadata": {
                        "type": "string"
                    },
                    "references": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "covers_workflows": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "entry_commands": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "safety_policy": {
                        "type": "string"
                    },
                    "status": {
                        "type": "string",
                        "enum": [
                            "registered",
                            "draft",
                            "blocked"
                        ]
                    }
                }
            }
        },
        "native_subagents": {
            "type": "array",
            "items": {
                "type": "object",
                "required": [
                    "id",
                    "path",
                    "role",
                    "covers_workflows",
                    "allowed_adapters",
                    "blocked_adapters",
                    "status"
                ],
                "additionalProperties": false,
                "properties": {
                    "id": {
                        "type": "string"
                    },
                    "path": {
                        "type": "string"
                    },
                    "role": {
                        "type": "string"
                    },
                    "covers_workflows": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "allowed_adapters": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "blocked_adapters": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "status": {
                        "type": "string",
                        "enum": [
                            "registered",
                            "draft",
                            "blocked"
                        ]
                    }
                }
            }
        },
        "workflow_bindings": {
            "type": "array",
            "items": {
                "type": "object",
                "required": [
                    "workflow_id",
                    "skill",
                    "subagents",
                    "default_adapters",
                    "human_gate"
                ],
                "additionalProperties": false,
                "properties": {
                    "workflow_id": {
                        "type": "string"
                    },
                    "skill": {
                        "type": "string"
                    },
                    "subagents": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "default_adapters": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "human_gate": {
                        "type": "boolean"
                    }
                }
            }
        }
    }
}
```

### `python3 -m json.tool plugins/statspai-empirical-workflow-runtime/.codex-plugin/plugin.json`

- exit: 0

stdout:

```text
{
    "name": "statspai-empirical-workflow-runtime",
    "version": "0.1.0",
    "description": "Portable StatspAI empirical workflow runtime registration package.",
    "author": {
        "name": "StatspAI local workflow"
    },
    "skills": "./skills/",
    "interface": {
        "displayName": "StatspAI Empirical Workflow Runtime",
        "shortDescription": "Install StatspAI workflow skills and native subagent registry.",
        "longDescription": "Packages the StatspAI ten-step empirical-paper workflow skill, native subagent specs, registry schema, and validation scripts so the registration layer can be migrated into another local research project.",
        "developerName": "StatspAI local workflow",
        "category": "Productivity",
        "capabilities": [
            "skills",
            "subagent-specs",
            "workflow-registry",
            "local-validation"
        ],
        "defaultPrompt": "Use $statspai-empirical-workflow to inspect this project's empirical-paper workflow state before planning changes."
    }
}
```

### `python3 -m json.tool plugins/statspai-empirical-workflow-runtime/package_manifest.json`

- exit: 0

stdout:

```text
{
    "name": "statspai-empirical-workflow-runtime",
    "version": "0.1.0",
    "purpose": "Move the StatspAI empirical workflow registration layer into another local project.",
    "source_stage": "Runtime Gap P5",
    "plugin_manifest": ".codex-plugin/plugin.json",
    "install_script": "scripts/install_into_project.py",
    "package_assets": {
        "skill": "skills/statspai-empirical-workflow",
        "native_agents": "assets/project/.codex/agents",
        "registry": "assets/project/workflows/skill_subagent_registry.json",
        "registry_schema": "assets/project/workflows/schemas/skill_subagent_registry.schema.json",
        "validators": [
            "assets/project/scripts/31_validate_skill_subagent_registry.py",
            "assets/project/scripts/32_test_skill_subagent_negative.py"
        ]
    },
    "target_requirements": [
        "workflows/registry.json",
        "workflows/tool_adapters.json",
        "workflows/orchestrator_policy.json",
        "scripts/23_workflow_runbook.py",
        "scripts/24_validate_runbook_api.py",
        "scripts/25_agent_runtime_preflight.py"
    ],
    "install_map": [
        {
            "source": "skills/statspai-empirical-workflow",
            "target": ".codex/skills/statspai-empirical-workflow",
            "kind": "directory"
        },
        {
            "source": "assets/project/.codex/agents",
            "target": ".codex/agents",
            "kind": "directory"
        },
        {
            "source": "assets/project/workflows/skill_subagent_registry.json",
            "target": "workflows/skill_subagent_registry.json",
            "kind": "file"
        },
        {
            "source": "assets/project/workflows/schemas/skill_subagent_registry.schema.json",
            "target": "workflows/schemas/skill_subagent_registry.schema.json",
            "kind": "file"
        },
        {
            "source": "assets/project/scripts/31_validate_skill_subagent_registry.py",
            "target": "scripts/31_validate_skill_subagent_registry.py",
            "kind": "file"
        },
        {
            "source": "assets/project/scripts/32_test_skill_subagent_negative.py",
            "target": "scripts/32_test_skill_subagent_negative.py",
            "kind": "file"
        }
    ],
    "validation_commands": [
        "python3 scripts/31_validate_skill_subagent_registry.py",
        "python3 scripts/32_test_skill_subagent_negative.py"
    ],
    "known_boundaries": [
        "This package installs the registration layer only.",
        "It expects the target project to already have the P0-P3 workflow registry, tool adapter registry, orchestrator policy, and runbook scripts.",
        "It does not install external MCP servers, browser credentials, data files, or paper-specific outputs."
    ]
}
```

### `git diff --check`

- exit: 0
