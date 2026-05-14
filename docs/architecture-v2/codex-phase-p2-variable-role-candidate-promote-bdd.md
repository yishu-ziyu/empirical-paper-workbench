# Phase P2-M: 真实字段候选写回正式变量角色集 BDD

## 目标

把真实 `.dta` / 外部数据字段画像生成的 `VariableRoleCandidate` 接到正式 `VariableRoleSet` 审批流程。候选可以被载入编辑器、人工修改，并且只有用户显式保存时才写入 `state/product/variable_roles.json`。

## 行为用例

### 行为 1：未审批候选不能写入正式变量角色集

Given 用户已经从真实字段画像生成 `VariableRoleCandidate`  
And 候选状态仍然是 `needs_review`  
When 用户带着该 `candidate_id` 调用正式变量角色保存接口  
Then 系统返回 `409 variable_role_candidate_approval_required`  
And 不创建或覆盖 `state/product/variable_roles.json`

业务规则：字段候选只是机器建议，不能绕过人工审阅进入研究设计。

### 行为 2：已审批候选可以显式保存为正式变量角色集

Given 用户已经审批一个真实字段候选  
And 候选状态为 `approved_candidate`  
When 用户在正式变量角色编辑器里保存该候选  
Then 系统写入 `state/product/variable_roles.json`  
And `status=approved`  
And `evidence_level=local_file`  
And 保存 `candidate_id`、`dataset_import_id`、`dataset_import_profile_id`、`source`、`binding`

业务规则：正式变量角色集必须能追溯到真实字段画像和人工确认。

### 行为 3：人工修改后的角色以用户保存内容为准

Given 候选自动识别了 outcome、treatment、controls  
When 用户在正式编辑器中修改 controls 或 cluster_by 后保存  
Then 正式 `VariableRoleSet.roles` 使用用户保存的最终内容  
And 决策日志记录这是一次来自候选的正式确认

业务规则：机器候选只是起点，正式研究语义以人工保存版本为准。

### 行为 4：候选写回后候选状态进入已应用

Given 用户已经把候选保存成正式变量角色集  
When 再读取变量角色候选列表  
Then 对应候选状态为 `applied_to_variable_roles`  
And 记录写入的 `VariableRoleSet` 版本  

业务规则：审阅台要能分清“已确认候选”和“已经进入正式研究状态”。

### 行为 5：前端必须先载入编辑器，再保存写回

Given 用户在数据页看到已审批字段候选  
When 用户点击“载入正式编辑器”  
Then outcome、treatment、controls 等字段被填入变量角色编辑器  
And 页面明确提示“保存后才写入正式变量角色集”  
And 保存请求带上 `candidate_id`

业务规则：产品交互要让用户知道自己是在确认研究语义，而不是浏览一张静态卡片。

## 边界条件

- 外部引用模式下不复制大文件，正式变量角色集保存 `binding.mode=external_reference` 和源文件哈希。
- 云端版本不能读取本地路径，后续需要把同一状态机接到上传/对象存储路径。
- 本阶段不自动生成 DesignSpec；DesignSpec 仍由下一阶段读取已批准的 VariableRoleSet 后生成。
