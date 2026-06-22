# P4 字段来源候选审计

- 题目：父母受教育水平对子女工资收入的影响
- 状态：`field_source_candidates_ready_for_review`
- 选中数据根目录：`/Users/mahaoxuan/Desktop/论文核心素材库/01_原始数据/实证数据库/A001CFPS中国家庭追踪调查`
- 扫描 .dta 文件数：36
- 候选字段数：52
- 只读元数据扫描：是
- 正式 VariableRoleSet 写回：否
- 正式 DesignSpec 写回：否
- 正式 RunPlan 写回：否
- 执行回归：否

## 字段候选
- `father_education` | candidate_found | 父亲受教育水平
  - `feduc` | 父亲最高学历 | `2010cfps/cfps2010adult_202008.dta`
  - `tb4_a_f` | 父亲最高学历 | `2010cfps/cfps2010adult_202008.dta`
  - `feduc` | 父亲最高学历 | `2010cfps/cfps2010child_201906.dta`
  - `tb4_a_f` | 父亲最高学历 | `2010cfps/cfps2010child_201906.dta`
  - `feduc` | 父亲最高学历 | `2010cfps/cfps2010famconf_202008.dta`
- `mother_education` | candidate_found | 母亲受教育水平
  - `meduc` | 母亲最高学历 | `2010cfps/cfps2010adult_202008.dta`
  - `tb4_a_m` | 母亲最高学历 | `2010cfps/cfps2010adult_202008.dta`
  - `meduc` | 母亲最高学历 | `2010cfps/cfps2010child_201906.dta`
  - `tb4_a_m` | 母亲最高学历 | `2010cfps/cfps2010child_201906.dta`
  - `meduc` | 母亲最高学历 | `2010cfps/cfps2010famconf_202008.dta`
- `parent_education` | constructable_needs_review | 父母受教育水平
- `hukou` | candidate_found | 户口状态
  - `adulthkcode` | 成人户口所在地与出生地地址匹配 | `2010cfps/cfps2010adult_202008.dta`
  - `ind_mig` | 户口是否在本区县 | `2010cfps/cfps2010adult_202008.dta`
  - `qa2` | 您现在的户口状况是 | `2010cfps/cfps2010adult_202008.dta`
  - `qa201acode` | 您现在的户口落在什么地方（省编码）-清理 | `2010cfps/cfps2010adult_202008.dta`
  - `qa302` | 您3岁时户口状况是 | `2010cfps/cfps2010adult_202008.dta`

## 过期路径
- `/Users/mahaoxuan/Desktop/实证数据库/A001CFPS中国家庭追踪调查/2011cfps/cfps2011adult_202202(1).dta`

## 人工确认
- `confirm_parent_education_construction`
- `confirm_preferred_cfps_wave`
- `confirm_hukou_role`
- `approve_before_formal_variable_roles_write`
