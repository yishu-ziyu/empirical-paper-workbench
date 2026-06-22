# P1-C 方法执行账本

- 题目：父母受教育水平对子女工资收入的影响
- 状态：`blocked_missing_required_fields`
- execution_allowed：false
- run id：未创建
- 正式 RunPlan 写回：否
- 正式论文写回：否

## 阻塞原因
- `missing_required_fields`

## 缺失字段
- `father_education`
- `hukou`
- `mother_education`
- `parent_education`

## 方法候选
- `IV` | blocked | reasons=missing_required_fields
- `DID` | blocked | reasons=missing_required_fields
- `DML` | blocked | reasons=missing_required_fields

## StatsPAI 边界
- allowed_after: `analysis_ready_dataframe`
- forbidden: `sp.paper`
