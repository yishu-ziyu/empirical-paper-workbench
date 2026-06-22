# P11C Source Contract Readiness Check SDD / BDD

Date: 2026-06-18

## North Star Slice

P11C makes the P11-Human step safer before the user clicks save. P11B turned `field_bindings` into editable rows; P11C adds a readiness check that tells the user exactly which signing fields are still incomplete.

## Scope

- In scope: React Product Control P11 form validation, visible readiness summary, save button gating, workflow status notes.
- Out of scope: backend contract changes, automatic source contract save, formal `VariableRoleSet` write, `DesignSpec`, `RunPlan`, run id, model execution.
- Stop condition: if completing P11C requires deciding actual CFPS wave, variable construction, or field source truth, pause for user/product decision.

## SDD Contract

P11C keeps the P11 POST payload unchanged. The frontend computes a local readiness list before save:

```text
dataset_path
reviewer
note
parent_education_construction
ln_wage:source_path
ln_wage:evidence_level
...
```

The save button is enabled only when:

- reviewer, note, confirmation, dataset path, and parent education construction are filled;
- every required source row has dataset column, source field, source path, and evidence level;
- confirmation equals `save_source_metadata_contract_for_p9_formal_save`.

## BDD Behaviors

### Behavior 1: readiness summary is visible

Given the P11 form has loaded source rows
When the user opens P11
Then the page shows `Source contract readiness` with either `ready_to_save_source_contract` or `needs_source_metadata_review`.

Business rule: 用户要在保存前看到“能不能签收”，而不是等后端报错。

### Behavior 2: missing row fields are named

Given a source row is missing dataset column, source field, source path, or evidence level
When readiness is computed
Then the readiness summary lists the exact row and missing key, such as `ln_wage:source_path`.

Business rule: 缺口必须能被本科生直接定位到具体行。

### Behavior 3: save is gated by readiness

Given any required source metadata field is missing
When the user tries to save P11
Then the save button remains disabled and P11 is not submitted.

Business rule: 前端不应该把明显不完整的签收交给后端 409。

### Behavior 4: no downstream authority changes

Given P11C only validates source contract readiness
When the page renders or the user edits rows
Then it still does not expose formal VariableRoleSet, DesignSpec, RunPlan, run id, or model execution.

Business rule: 这一步只提升签收体验，不改变正式层门禁。

## Acceptance Checks

- P11 React contract test covers `Source contract readiness`, `p11SourceContractMissingItems`, and `ready_to_save_source_contract`.
- P11 target tests pass.
- P9/P10/P11 regression passes.
- React build passes.
- Browser smoke confirms readiness summary is visible on desktop and mobile.
