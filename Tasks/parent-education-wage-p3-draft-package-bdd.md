# P3 DraftPackage BDD

目标：把 P2 的 `blocked_missing_parent_education_fields` 状态转成用户可打开的半成品论文交付包。P3 不绕过字段阻断、不执行回归、不写正式层；它把“不能完整成稿”的状态产品化为 `paper_draft.docx`、问题清单和审计报告。

## BDD-1：阻断态必须生成半成品 DraftPackage

Given P2 执行准入账本显示 `execution_preflight_allowed=false`
When 系统生成 P3 DraftPackage
Then 交付包状态应为 `blocked_draft_package_ready`
And `full_draft_ready=false`
And `draft_kind=partial_red_flagged_draft`
And 缺口必须包含父母教育字段。

业务规则：阻断状态不能只停在后台账本；用户仍应拿到能阅读的半成品论文。

## BDD-2：半成品论文必须有可打开的 docx

Given P3 DraftPackage 已生成
When 用户查看输出文件
Then 至少存在 `Submissions/parent_education_wage_paper_draft.docx`
And Markdown 源文件存在
And docx 正文包含红标缺口说明。

业务规则：第一用户体验是论文初稿文件，不是 JSON 或诊断报告。

## BDD-3：问题清单和审计报告必须和论文同时生成

Given P3 DraftPackage 已生成
When 用户查看支撑文件
Then `issue_list.md` 必须列出缺失字段、阻断原因和下一步
And `audit_report.md` 必须说明证据状态、未执行回归和正式层边界。

业务规则：半成品论文不是假装完成，而是把能写和不能写的部分分开。

## BDD-4：P3 不允许越权写正式层

Given 父母教育字段仍未绑定
When P3 DraftPackage 生成
Then 不得写 `state/product/variable_roles.json`
And 不得写 `state/product/design_spec.json`
And 不得写 `state/product/run_plan.json`
And 不得创建 run id。

业务规则：Draft-first 不等于跳过证据门禁；它只是改变用户可见交付方式。

## BDD-5：Product Control API 必须显式生成 DraftPackage

Given 当前项目已登记到 Product API
When 前端 GET P3 DraftPackage
Then 缺失时只返回 `p3_draft_package_missing`
When 前端 POST P3 DraftPackage
Then 系统才写出 DraftPackage 文件并返回产物路径。

业务规则：GET 不应该有副作用；用户或工作流显式刷新才生成新产物。

## BDD-6：React 产品面必须显示 P3 DraftPackage 状态

Given React 主入口展示产品控制面
When P3 DraftPackage 状态存在或缺失
Then 页面应显示 `P3 DraftPackage`
And 显示 `paper_draft.docx`
And 显示半成品/红标问题清单状态。

业务规则：产品面要把首交付物放到用户视野里，不能继续只显示执行准入。
