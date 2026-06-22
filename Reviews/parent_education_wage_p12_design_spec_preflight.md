# P12 DesignSpec Preflight Review

- status: `design_spec_preflight_ready_for_review`
- topic: 父母受教育水平对子女工资收入的影响
- dataset: Data/Final/cfps_robot_reallocation.csv
- formula: `ln_wage ~ parent_education + age + female + urban + edu_last + experience`
- can_write_design_spec: `False`
- can_write_run_plan: `False`
- can_create_run_id: `False`
- can_execute_model: `False`

## Method Readiness

- ols: ready / blockers: none
- did: blocked / blockers: missing_panel_time
- iv: blocked / blockers: missing_instrument
- rdd: blocked / blockers: missing_running_variable
- psm: ready / blockers: none
- dml: ready / blockers: none

## Human Review Required

- confirm_baseline_ols_as_first_design_spec
- confirm_parent_education_endogeneity_limitation
- confirm_no_did_iv_rdd_without_extra_identification_fields
- approve_before_formal_design_spec_write

## Boundary

P12 only writes this preflight review package. It does not write formal DesignSpec, RunPlan, run id, or model results.
