# P2-W BDD: Real Variable Role Promotion

目标：把真实字段画像生成的 `VariableRoleCandidate` 从“启发式候选建议”推进为“可编辑正式变量角色草稿”，但不能静默覆盖已经确认的 `VariableRoleSet`。

业务边界：字段名、变量标签和 Stata 类型只能帮助系统提出候选。只有用户显式编辑并保存的 `VariableRoleSet` 才能进入 `DesignSpec`、`RunPlan` 和论文分析。

## 行为 1：已审批候选创建可编辑草稿

Given 一个 `VariableRoleCandidate` 的 `review_status` 是 `approved_candidate`  
When 用户点击“基于候选创建变量角色草稿”  
Then 系统创建一个 `VariableRoleSet` draft  
And draft 记录 `source_candidate_id` 和 `source_dataset` 证据  
And draft 状态是 `draft`

业务规则：候选建议即使被确认，也只进入草稿层，不能直接成为正式研究设定。

## 行为 2：创建草稿不覆盖已确认 VariableRoleSet

Given 项目已经存在一个 `status=approved` 的 `VariableRoleSet`  
When 用户从已审批候选创建草稿  
Then 现有 `state/product/variable_roles.json` 保持不变  
And 新草稿保存到 `state/product/variable_roles_drafts.json`

业务规则：新真实数据候选不能悄悄替换旧研究设定；这会导致 DesignSpec/RunPlan 失去可解释性。

## 行为 3：用户编辑并批准 promoted draft 后才写入正式状态

Given 一个 promoted draft 已存在  
When 用户编辑 outcome、treatment、controls、fixed effects 和 cluster field  
And 用户保存为 approved `VariableRoleSet`  
Then `state/product/variable_roles.json` 被更新  
And 正式状态保留 `source_candidate` 和 draft provenance

业务规则：正式变量角色是用户审阅后的研究状态，不是候选算法的直接输出。

## 行为 4：前端区分候选建议和正式变量角色

Given 页面存在真实字段候选和正式变量角色草稿  
When Data & Variables 页面渲染  
Then 候选卡片显示“候选建议”  
And 正式编辑器显示“正式变量角色”  
And “基于候选创建变量角色草稿” 与 “保存正式变量角色” 是两个不同动作

业务规则：用户必须看得懂哪一层是启发式建议，哪一层才会影响论文分析。

## 需要确认的边界

- P2-W 只创建草稿和正式保存边界，不自动重建 DesignSpec 或 RunPlan。
- P2-W 不执行任何回归，也不把候选字段写入论文正文。
- P2-W 不复制或修改原始 `.dta` 文件。
