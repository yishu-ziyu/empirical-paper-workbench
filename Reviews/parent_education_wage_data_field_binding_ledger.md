# P1-B 数据字段绑定账本

- 题目：父母受教育水平对子女工资收入的影响
- 状态：`blocked_missing_parent_education_fields`
- 候选变量数：12
- matched：8
- missing：4
- 不写正式变量角色
- 不写 DesignSpec / RunPlan

## 阻塞原因
- `missing_parent_education_source_fields`

## 字段绑定
- `ln_wage` (Y) | matched | Data/Final/cfps_robot_reallocation.csv | 对数工资收入
- `wage` (Y) | matched | Data/Final/analysis_sample.csv | 工资收入
- `father_education` (X) | missing | missing | 父亲受教育水平
- `mother_education` (X) | missing | missing | 母亲受教育水平
- `parent_education` (X) | missing | missing | 父母受教育水平
- `edu_last` (control) | matched | Data/Final/cfps_robot_reallocation.csv | 子女受教育年限
- `age` (control) | matched | Data/Final/cfps_robot_reallocation.csv | 年龄
- `female` (control) | matched | Data/Final/cfps_robot_reallocation.csv | 性别
- `urban` (control) | matched | Data/Final/cfps_robot_reallocation.csv | 城乡户籍或居住地
- `experience` (control) | matched | Data/Final/analysis_sample.csv | 工作经验
- `hukou` (moderator) | missing | missing | 户口状态
- `province` (moderator) | matched | Data/Final/charls_did_analysis_sample.csv | 省份

## 审阅门禁
- `parent_education_source_fields_required`
- `wage_measurement_definition_review`
- `child_education_control_role_review`
- `sample_and_year_coverage_review`
