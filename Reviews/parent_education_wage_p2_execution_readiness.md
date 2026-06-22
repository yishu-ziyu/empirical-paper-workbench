# P2 执行准入账本

- 题目：父母受教育水平对子女工资收入的影响
- 状态：`blocked_missing_parent_education_fields`
- execution_preflight_allowed：false
- run id：未创建
- 正式 VariableRoleSet 写回：否
- 正式 DesignSpec 写回：否
- 正式 RunPlan 写回：否

## 阻塞原因
- `missing_parent_education_fields`
- `human_variable_operationalization_required`

## 字段补证
- `father_education` | missing | candidates=none
- `mother_education` | missing | candidates=none
- `parent_education` | missing | candidates=none
- `hukou` | candidate_found | candidates=qa2, qa201acode, qa302, qa402, qn2031, qa201ccode_id

## 变量口径 Draft
- outcome: `ln_wage`
- treatment: `parent_education` | blocked_missing_parent_education_fields
- parent education construction: requires_human_confirmation

## 方法执行门
- `IV` | blocked | reasons=missing_parent_education_fields, human_variable_operationalization_required
- `DID` | blocked | reasons=missing_parent_education_fields, human_variable_operationalization_required
- `DML` | blocked | reasons=missing_parent_education_fields, human_variable_operationalization_required
