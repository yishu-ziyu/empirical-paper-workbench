# P11D Row Human Confirmation Gate SDD / BDD

Date: 2026-06-18

## North Star Slice

P11D prevents the source contract from being treated as human-reviewed just because the UI prefilled candidate values. Every required source row must be explicitly checked by the user before P11 can save the source contract.

## Scope

- In scope: React Product Control P11 source row confirmation checkbox, readiness gating, visible count of confirmed rows, workflow status notes.
- Out of scope: backend contract changes, automatic confirmation, automatic source contract save, formal `VariableRoleSet` write, `DesignSpec`, `RunPlan`, run id, model execution.
- Stop condition: if actual field truth requires choosing a CFPS wave or changing variable construction, pause for user/product decision.

## SDD Contract

The backend P11 POST payload remains unchanged. Row confirmation is a frontend gate:

```text
sourceFieldRows[].confirmed === true
```

Readiness requires:

- all P11C text fields are complete;
- every source row has dataset column, source field, source path, evidence level;
- every source row is explicitly confirmed by the user.

Unconfirmed rows appear in the missing list as:

```text
ln_wage:human_confirmation
```

## BDD Behaviors

### Behavior 1: every row has a human confirmation control

Given the P11 form has loaded source rows
When the user views the per-field source confirmation editor
Then every row exposes a checkbox labelled as a human confirmation control.

Business rule: 预填候选不等于人工签收。

### Behavior 2: readiness includes row confirmations

Given a row has complete source text fields but is not checked
When readiness is computed
Then the missing list includes `<field>:human_confirmation`.

Business rule: 完整文本字段只能说明“有值”，不能说明“已审阅”。

### Behavior 3: save stays disabled until all rows are confirmed

Given any required row is not checked
When reviewer, note, confirmation, dataset path, construction, and row text fields are otherwise complete
Then the save button remains disabled.

Business rule: P11-Human 必须是人工动作，而不是默认值保存。

### Behavior 4: no downstream authority changes

Given row confirmations only affect frontend readiness
When the user checks rows
Then the page still does not expose formal VariableRoleSet, DesignSpec, RunPlan, run id, or model execution.

Business rule: 签收体验增强不能绕过 P9/P12 门禁。

## Acceptance Checks

- P11 React contract test covers `confirmedSourceFieldRows`, `handleP11SourceFieldRowConfirmChange`, and `human_confirmation`.
- P11 target tests pass.
- P9/P10/P11 regression passes.
- React build passes.
- Browser smoke confirms the confirmation checkboxes render on desktop and mobile, and the save button stays disabled before checking.
