# P5 VariableRoleSet 草案预检

- 题目：父母受教育水平对子女工资收入的影响
- 状态：`variable_role_preflight_ready_for_review`
- outcome 草案：`ln_wage`
- treatment 草案：`parent_education`
- parent_education 构造建议：`max(father_education, mother_education)`
- controls 草案：age, female, urban, edu_last, experience
- 正式 VariableRoleSet 写回：否
- 正式 DesignSpec 写回：否
- 正式 RunPlan 写回：否
- 执行回归：否

## 字段绑定草案
- `father_education` | candidate_selected_for_review | `feduc` | 父亲最高学历
- `mother_education` | candidate_selected_for_review | `meduc` | 母亲最高学历
- `parent_education` | constructable_needs_review | `none` |
- `hukou` | candidate_selected_for_review | `qa2` | 您现在的户口状况是

## 人工确认
- `confirm_preferred_cfps_wave`
- `confirm_parent_education_construction`
- `confirm_hukou_role`
- `confirm_outcome_and_controls`
- `approve_before_formal_variable_roles_write`
