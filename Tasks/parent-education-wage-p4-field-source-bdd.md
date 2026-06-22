# P4 字段来源候选 BDD

目标：把 `father_education`、`mother_education`、`parent_education` 和 `hukou` 从“缺字段阻断”推进到“可审阅字段来源候选”，但不写正式 VariableRoleSet、DesignSpec 或 RunPlan。

## 行为 1：只读扫描真实 CFPS 字段来源

Given 项目中已有过期或虚拟的数据源路径
When P4 字段来源发现运行
Then 它必须优先使用当前存在的 CFPS 数据根目录，并把不存在的旧路径记录为 stale source，而不是信任旧 JSON。

业务规则：产品在复杂本地环境下运行时，文件夹迁移不能导致错误绑定。

## 行为 2：从 Stata 变量标签发现父母教育候选

Given CFPS `.dta` 文件包含变量标签 `父亲最高学历` 和 `母亲最高学历`
When P4 扫描 Stata 元数据
Then 它必须分别为 `father_education` 和 `mother_education` 生成候选字段，记录源文件、字段名、标签、证据等级和匹配原因。

业务规则：候选必须来自真实数据标签，而不是论文题目或硬编码假字段。

## 行为 3：父母教育综合变量只能进入构造草案

Given 父亲教育和母亲教育候选已经存在
When P4 生成 `parent_education` 状态
Then `parent_education` 可以标为 `constructable_needs_review`，但必须要求人工确认构造规则。

业务规则：父母教育综合口径是研究设计决策，不能由扫描器自动升格为正式变量。

## 行为 4：P4 不写正式状态也不执行回归

Given P4 已发现字段候选
When 它写出候选账本和审计报告
Then 它不得修改 `state/product/variable_roles.json`、`state/product/design_spec.json`、`state/product/run_plan.json`，不得创建 run id 或执行回归。

业务规则：字段候选是审阅层产物，不是正式执行许可。

## 行为 5：Product Control 暴露 P4 状态

Given 项目已登记到 Product API
When 用户 GET P4 endpoint
Then GET 只返回缺失状态；POST 才生成字段来源候选账本；React 主入口显示 P4 字段来源、候选数量、父母教育状态和刷新按钮。

业务规则：前端必须让用户看到 DraftPackage 后的下一步，而不是让流程停在半成品论文。

## 需要人工确认的边界

- `parent_education` 的构造口径：父母最高学历取最大值、均值、分别入模，或转为教育年限。
- 首轮执行优先使用哪个年份/波次：2010/2018/2020/2022 的字段可用性不同。
- `hukou` 使用本人户口、父母户口，还是城乡/户籍派生变量。
- 候选字段是否允许写入正式 VariableRoleSet。
