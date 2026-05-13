# Codex Phase P2-G BDD: Real Dataset Bind Preflight

## 背景

P2-F 已经把 `/Users/mahaoxuan/Desktop/实证数据库` 作为只读真实数据候选池接入 Data & Design。
P2-G 的目标不是马上复制或运行真实数据，而是先提供可审计的“导入/绑定预检”：
用户选择一个候选文件后，系统记录来源、目标路径、策略、检查项和下一步动作，但不得修改外部原始数据，也不得直接替换当前项目数据。

## 行为 1：候选池文件可以生成导入/绑定预检

Given 项目存在只读真实数据候选池  
And 用户选择的外部数据文件位于候选池根目录内  
When 用户请求生成导入/绑定预检  
Then API 返回 `status=ready_for_review` 的预检对象  
And 预检对象包含 source path、target path、strategy、checks、manifest path  
And 证据等级为 `local_file`

业务规则：真实数据进入项目之前，必须先成为可审计决策对象。

## 行为 2：预检只写状态，不复制或修改数据文件

Given 用户选择一个外部候选数据文件  
When 系统生成导入/绑定预检  
Then 外部源文件仍在原路径  
And 项目目标路径尚未出现数据副本  
And 预检对象明确 `will_mutate_source=false`、`will_create_project_file=false`

业务规则：预检不是导入执行，不能把“检查”伪装成“使用真实数据运行”。

## 行为 3：候选池外部路径必须被拒绝

Given 用户提交一个不在真实数据候选池根目录下的路径  
When 用户请求生成导入/绑定预检  
Then API 返回结构化错误 `invalid_external_dataset_path`

业务规则：不能让任意本机路径绕过候选池和 provenance 边界。

## 行为 4：数据页展示最新导入/绑定预检

Given 已生成导入/绑定预检  
When 用户打开“数据与设计”页面  
Then 页面在真实数据候选池下显示最新预检状态  
And 显示来源、目标、策略、检查项和“尚未导入/绑定”的提示

业务规则：用户需要能看到自己刚才做的是预检，不是已经完成导入。

## 行为 5：真实数据卡片提供预检动作

Given 真实数据候选池中存在候选文件  
When 用户浏览“数据与设计”页面  
Then 每个候选卡片提供“生成导入/绑定预检”动作  
And 动作调用真实 API，不只是在前端本地切换状态

业务规则：P2-G 要把候选池推进为可操作产品路径，而不是静态陈列。

## 边界条件

- 本阶段不执行复制、移动、软链接或覆盖 `paper.yaml`。
- 本阶段不把外部候选数据写入 VariableRoleSet / DesignSpec / RunPlan。
- 默认 target path 为 `Data/Raw/<source_filename>`，仅作为预检目标。
- 只有候选池根目录内的已存在数据文件可生成预检。
- DTA/XLSX/CSV 都可生成预检；深度变量画像仍属于后续步骤。
