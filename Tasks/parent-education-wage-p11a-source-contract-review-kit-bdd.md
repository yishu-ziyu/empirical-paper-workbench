# P11A Source Contract Review Kit - SDD / BDD

更新时间：2026-06-18

## SDD

用户：本科生或初级研究者，已经在 P7/P8 确认了变量角色，但还没有能力独立判断每个变量来自哪个数据文件和字段。

用户要完成什么：在进入 P9 正式变量表保存前，人工确认 `dataset_path`、每个变量的字段来源、`parent_education` 的派生口径，以及哪些字段仍不能确认。

系统必须交付什么：P11 GET 返回一个 review kit，前端在 P11 面板展示可读的候选包，包括推荐 dataset path、字段候选、缺口状态、保存所需材料和不可越权边界。

系统不能越过什么边界：P11A 不能替用户保存 source contract，不能写正式 VariableRoleSet，不能写 DesignSpec/RunPlan，不能创建 run id，不能执行模型。

成功呈现：用户能看到每个必需字段的 recommended source、evidence level、source path 和是否仍需人工确认。

阻断呈现：缺少候选时，系统列出字段名和下一步补证动作，而不是把空字段包装成可保存。

## BDD 行为

### 行为 1：P11 返回可人工确认的候选包

Given 真实项目已经有 P7 editable draft 和 P8 formal role approval
When 用户打开 P11 source metadata contract
Then 系统返回 `source_contract_review_kit`，其中包含 required fields、recommended dataset path、field review items 和 no-model boundary。

业务规则：P11 不应该只返回一组缺失字段；它必须把用户能参考的本地候选证据一起返回，帮助用户判断。

### 行为 2：字段候选来自 P5/P4 证据，不伪造完整确认

Given P5 preflight 中已经有 `father_education`、`mother_education` 等字段候选
When P11 构造 review kit
Then 对应字段应显示 preferred candidate、source path 和 evidence level，但 review status 仍为 `needs_human_confirmation`。

业务规则：候选证据可以帮助用户确认，但不能替代用户确认。

### 行为 3：缺少候选的字段必须显式标记

Given `ln_wage`、`age`、`experience` 等字段可能没有 P5 preferred candidate
When P11 构造 review kit
Then 这些字段必须出现在 field review items 中，并标为 `missing_recommended_source` 或 `needs_human_confirmation`。

业务规则：产品不能因为部分字段有候选，就隐藏其它字段的缺口。

### 行为 4：前端展示 review kit，但不提供模型执行入口

Given P11 API 返回 review kit
When 用户查看 React Product Control 页面
Then 页面应展示 `Source review kit`、recommended dataset path 和 field review items，并保留“不写正式层、不跑模型”的边界文案。

业务规则：P11A 是人工签收辅助，不是模型运行阶段。

## 需要用户确认的边界条件

- 最终使用哪一个 CFPS 波次和合并数据文件。
- `parent_education` 使用 max、mean，还是父母分别入模。
- `hukou` 是控制变量、异质性变量，还是暂不使用。
- 工资、教育、年龄、城市、经验等字段是否来自同一份分析数据，还是需要先生成中间数据。
