# Codex Phase P2-H BDD: Real Dataset Import Apply

## 背景

P2-G 已经让真实数据候选文件生成 `ready_for_review` 预检，但用户还不能把数据正式纳入当前项目。
P2-H 的目标是补上显式确认动作：用户必须在预检通过后，选择复制到项目、仅绑定外部引用，或取消预检。

同时产品有两个部署版本：

- 纯本地版本：可以读取本机真实数据仓库，允许复制到项目或仅绑定本地外部引用。
- 线上版本：不能读取用户本机路径，必须走云上传或云对象存储；本阶段先在 API 上拒绝 `runtime_mode=cloud` 的本机路径绑定。

## 行为 1：本地版本可以把预检文件复制到项目

Given 项目存在一条 `ready_for_review` 的真实数据预检  
And 用户选择本地版本的“确认导入到项目”  
When 系统执行 apply  
Then 源文件保持不变  
And 目标文件出现在项目 `Data/Raw/<filename>`  
And apply 结果记录 action、目标路径、文件大小、SHA256、证据等级和人工说明  
And datasets API 可以把新项目内文件列为本地数据集

业务规则：复制是正式导入动作，必须由用户显式确认并留下可验证文件证据。

## 行为 2：本地版本可以只绑定外部引用

Given 项目存在一条 `ready_for_review` 的真实数据预检  
And 用户选择“只绑定引用，不复制文件”  
When 系统执行 apply  
Then 项目 `Data/Raw` 不新增数据副本  
And apply 结果记录 source path、binding mode、文件大小、SHA256 和证据等级  
And 状态明确这是外部引用，不是项目内副本

业务规则：大文件可以不复制，但必须明确它仍然依赖本机外部路径。

## 行为 3：用户可以取消一条预检

Given 项目存在一条 `ready_for_review` 的真实数据预检  
When 用户选择取消预检  
Then 预检状态变为 `cancelled`  
And 不创建项目数据文件  
And 取消动作写入 manifest，避免误把该预检继续推进到变量角色或 RunPlan

业务规则：错误选择的数据必须能明确废弃，而不是残留为待处理状态。

## 行为 4：线上版本不能直接绑定本机路径

Given 预检来源是本机真实数据仓库路径  
When 用户以 `runtime_mode=cloud` 请求复制或绑定  
Then API 返回结构化错误 `cloud_upload_required`  
And 不创建项目文件或绑定记录

业务规则：线上应用无法读取用户本地文件；线上版本必须通过上传或云对象存储接入数据。

## 行为 5：前端把预检后的三个动作讲清楚

Given 页面已经展示一条 `ready_for_review` 预检  
When 用户查看导入/绑定预检面板  
Then 页面提供“确认导入到项目”“只绑定引用”“取消预检”三个动作  
And 文案说明复制会生成项目内文件，绑定不会复制源文件  
And 动作调用真实 apply API

业务规则：用户需要知道每个按钮的后果，不能把工程术语暴露成模糊操作。

## 边界条件

- `copy_to_project_raw` 只允许在本地版本执行。
- `bind_external_reference` 只允许在本地版本执行。
- `cancel` 不创建任何数据文件。
- 已取消或已 applied 的预检不能重复 apply。
- 本阶段不修改 `paper.yaml`、VariableRoleSet、DesignSpec 或 RunPlan。
- 线上版本的数据上传和云对象存储属于后续功能，本阶段只拒绝本机路径。
