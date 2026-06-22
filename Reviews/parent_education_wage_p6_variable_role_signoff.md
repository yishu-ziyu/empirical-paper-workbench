# P6 人工签收与提升路径

- 题目：父母受教育水平对子女工资收入的影响
- 状态：`variable_role_draft_promoted_for_editing`
- outcome 草案：`ln_wage`
- treatment 草案：`parent_education`
- 父母教育构造建议：`max(father_education, mother_education)`
- controls 草案：age, female, urban, edu_last, experience
- 可编辑 draft 写入：完整签收后可以
- 正式 VariableRoleSet 写回：否
- 执行回归：否

## 待人工签收项
- `confirm_preferred_cfps_wave`
- `confirm_parent_education_construction`
- `confirm_hukou_role`
- `confirm_outcome_and_controls`
- `approve_before_formal_variable_roles_write`

## 页面推荐默认值
- `confirm_preferred_cfps_wave`：`confirmed_current_p4_sources`
- `confirm_parent_education_construction`：`max(father_education, mother_education)`
- `confirm_hukou_role`：`control_or_heterogeneity_candidate`
- `confirm_outcome_and_controls`：`ln_wage_with_age_female_urban_edu_last_experience`
- `approve_before_formal_variable_roles_write`：`draft_only_no_formal_write`

## 已生成草稿
- draft id：`variable_roles_draft_parent_education_wage_p6_20260617T1752108259430000`
- 写入边界：`draft_only_until_formal_variable_role_approval`
