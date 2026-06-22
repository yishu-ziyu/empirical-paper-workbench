# P11B Per-Field Source Confirmation SDD / BDD

Date: 2026-06-18

## North Star Slice

P11B turns source metadata signoff from a technical JSON task into a human-readable field checklist. The user should confirm each required model field against a dataset column, source path, and evidence level before P9 can formally save the VariableRoleSet.

## Scope

- In scope: React Product Control P11 UI, client payload construction, P11 behavior tests, workflow status notes.
- Out of scope: writing formal `VariableRoleSet`, writing `DesignSpec`, writing `RunPlan`, creating run id, executing model.
- Stop condition: if the API contract must delete or rewrite existing P11 state files, pause for product decision.

## SDD Contract

P11B keeps the existing backend source contract shape:

```json
{
  "dataset_path": "Data/Final/cfps_robot_reallocation.csv",
  "field_bindings": {
    "ln_wage": {
      "dataset_column": "ln_wage",
      "source_field": "ln_wage",
      "source_path": "Data/Final/cfps_robot_reallocation.csv",
      "evidence_level": "local_file"
    }
  },
  "derived_variables": {
    "parent_education": {
      "source_fields": ["father_education", "mother_education"],
      "construction": "max(father_education, mother_education)"
    }
  }
}
```

The frontend may render this as rows, but the POST payload must remain compatible with the P11A backend.

## BDD Behaviors

### Behavior 1: GET review kit drives source rows

Given P11 GET returns `source_contract_review_kit.field_review_items`
When the P11 panel loads
Then the page renders a per-field confirmation editor with one editable row per required field.

Business rule: 用户应该确认每一个模型字段的数据来源，而不是手写内部 JSON。

### Behavior 2: row edits build field_bindings

Given the user edits dataset column, source path, or evidence level for a row
When the user saves P11 source metadata
Then the POST payload builds `field_bindings` from the edited rows.

Business rule: UI 表单是主入口，JSON 只是可审计预览。

### Behavior 3: incomplete confirmation stays blocked

Given some required source metadata is still empty
When the user saves P11
Then P11 returns incomplete status and P9 stays blocked.

Business rule: 易用性不能绕过真实数据来源门禁。

### Behavior 4: P11B does not add model execution

Given P11B is a source confirmation step
When the user views or saves P11
Then the page still does not expose model execution or formal downstream write controls.

Business rule: 现在解决的是“能否可信地写正式变量角色”，不是跑模型。

## Acceptance Checks

- P11 test file includes a React contract test for `sourceFieldRows`, `handleP11SourceFieldRowChange`, and `p11FieldBindingsFromRows`.
- P11 backend tests still pass for incomplete and complete source contracts.
- React build passes.
- Browser smoke confirms `Per-field source confirmation` is visible on desktop and mobile.
