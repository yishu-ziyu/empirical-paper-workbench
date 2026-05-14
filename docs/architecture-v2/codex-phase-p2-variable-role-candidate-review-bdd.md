# P2-L BDD：字段审阅与 VariableRoleSet 候选状态机

更新时间：2026-05-15

## 背景

P2-J 已经能从真实 Stata `.dta` 文件生成 metadata-only 字段画像，字段名、变量标签、Stata 类型、行列数和来源哈希都来自本地文件证据。P2-L 的目标不是直接把这些字段写入正式 `VariableRoleSet`，而是先生成一个可审阅的候选状态机，让用户确认“哪些变量是结果变量、处理变量、控制变量、工具变量”。

这一步参考 CoPaper / StatsPAI 的产品路径：数据导入后先进入变量理解与角色确认，再进入研究设计和执行。系统可以提出建议，但不能替用户完成关键研究判断。

## 行为 1：已画像的真实 DTA 可以生成变量角色候选

Given 用户已经把一个真实 `.dta` 文件绑定到项目，并生成字段画像  
When 用户点击“生成变量角色候选”  
Then 系统应基于字段名、变量标签和类型生成 `VariableRoleSetCandidate`  
And 候选应标记 `evidence_level=local_file`  
And 候选状态应为 `needs_review`  
And 系统不得写入正式 `state/product/variable_roles.json`

业务规则：字段画像只能进入“候选”，不能直接成为研究状态。

## 行为 2：候选审批只改变候选状态，不写回正式变量角色集

Given 系统已经生成一个 `VariableRoleSetCandidate`  
When 用户把候选标记为“候选已确认”  
Then 候选状态应变为 `approved_candidate`  
And 候选应记录审阅动作、备注和时间  
And `can_apply_to_variable_roles=true`  
And 系统仍不得自动写入正式 `VariableRoleSet`

业务规则：审批候选和正式保存是两个动作，避免 Agent 自动改写研究设计。

## 行为 3：没有字段画像的导入不能生成候选

Given 用户只创建了外部数据绑定记录，但还没有生成字段画像  
When 用户请求生成变量角色候选  
Then API 应返回阻塞错误 `field_profile_required`  
And 前端应继续提示先生成字段画像

业务规则：不能基于文件名或猜测生成变量角色。

## 行为 4：非法审阅动作必须被拒绝

Given 已存在一个变量角色候选  
When 用户提交不属于状态机的动作  
Then API 应返回 `invalid_variable_role_candidate_action`  
And 不应修改候选状态

业务规则：审批状态机必须可审计，不能接受任意字符串。

## 行为 5：前端必须显式说明“候选不会写入正式状态”

Given 用户在“数据与设计”页面查看字段画像  
When 页面显示变量角色候选面板  
Then 用户应看到生成候选、候选审阅、证据等级、候选状态  
And 页面必须显示“不会写入正式变量角色集”  
And 只有后续手动保存 `VariableRoleSet` 才能推进 workflow contract

业务规则：产品界面要避免让用户误以为 Agent 已经替他确认研究变量。

## 边界条件

- DTA 字段画像如果是 `blocked`，不能生成候选。
- 候选可以使用启发式建议 outcome/treatment/control，但必须可被用户修改。
- `approved_candidate` 仍不是 `approved VariableRoleSet`。
- 线上版本不能读取用户本地路径；本轮只覆盖纯本地版本的 `local_file` 数据证据。
