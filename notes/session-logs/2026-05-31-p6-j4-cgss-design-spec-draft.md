# 2026-05-31 P6-J4 Session Log

## Component Effect

P6-J4 is the research-design draft gate after variable-role drafting.

It tells the product:

- which dataset and variables the design uses;
- what empirical claim level is allowed;
- which models are suitable as first candidates;
- which method families are blocked and why;
- what review gates must clear before RunPlan or formal DesignSpec writeback.

For the current topic, it does not approve a formal DesignSpec. It produces a reviewable design draft.

## Current Real Run

- JSON: `Results/json/cgss_social_capital_happiness_design_spec_draft.json`
- Review: `Reviews/cgss_social_capital_happiness_design_spec_draft.md`
- Status: `needs_human_design_spec_review`
- Dataset: CGSS2023
- Model candidates: OLS baseline, Ordered Logit
- Claim boundary: `conditional_association_not_strong_causality`
- Blocked methods: DID, IV, RDD, PSM, DML
- CLI exit code: `0`

## Downstream Connection

Downstream nodes should treat this as a research-design draft, not a formal DesignSpec.

- The user should confirm whether the cross-section conditional association framing is acceptable;
- MethodAgent should keep DID, IV, RDD, PSM, and DML blocked until their required design evidence exists;
- RunPlan seed can use the draft to prepare executable commands, but should stay in draft/review state;
- Writer should use the claim boundary to avoid causal overstatement;
- ExportAgent should not use this as final paper state.

## Verification

- Target test: `python3 -m unittest tests.test_cgss_design_spec_draft -v` -> 5 OK.
- Adjacent regression: `python3 -m unittest tests.test_cgss_data_discovery tests.test_cgss_topic_variable_discovery tests.test_cgss_dataset_bound_variable_role_draft tests.test_cgss_design_spec_draft tests.test_cgss_run_plan_seed -v` -> 20 OK.
- Compile: `python3 -m py_compile Program/run_cgss_design_spec_draft.py Program/workbench/cgss_design_spec_draft.py tests/test_cgss_design_spec_draft.py` -> OK.
- Real CLI: `python3 Program/run_cgss_design_spec_draft.py --project-root .` -> `needs_human_design_spec_review`.

## Pause Point

Pause after P6-J4. The next logical stage is RunPlan seed drafting or formal DesignSpec promotion, but this stage does not auto-approve the design, run models, or write formal product state.
