# P2-J BDD: Stata DTA 字段画像

## 背景

P2-I 已经把真实数据导入/绑定后的字段画像入口打通，但真实 CFPS `.dta` 仍停留在 `blocked/not_profiled`。这会让用户看见数据文件，却无法知道里面有哪些变量，也无法进入后续人工变量角色确认。

本阶段目标不是直接运行真实 CFPS 回归，而是先安全读取 Stata 文件元数据：字段名、变量标签、Stata 类型、样本数和字段数。字段画像仍然只是 `local_file` 证据，不得自动写入 VariableRoleSet、DesignSpec 或 RunPlan。

## 行为 1：有效 DTA import 可以生成字段画像

Given 用户已经显式复制或绑定一个有效 `.dta` 文件  
When 用户点击“生成字段画像”  
Then 后端应以 metadata-only 方式读取 Stata 元数据，返回 `status=profiled`、`readiness_status=ready`、字段列表、样本数、字段数和 `evidence_level=local_file`。

业务规则：用户应先看见真实 DTA 的变量字典，再决定哪些字段可以进入变量角色确认。

## 行为 2：DTA 字段画像必须保留 Stata 语义

Given `.dta` 文件包含变量标签、Stata storage type 和 display format  
When 字段画像生成成功  
Then 每个字段应包含 `name`、`label`、`inferred_type`、`stata_type` 和 `display_format`；前端应能显示标签/类型，而不是只显示普通 CSV 推断结果。

业务规则：DTA 不是普通表格文件，变量标签和 Stata 类型是研究者判断变量含义的重要证据。

## 行为 3：DTA 画像不读取整张大表

Given 用户绑定的真实 DTA 可能很大  
When 后端生成字段画像  
Then `quality_profile.row_count_source` 应标记为 `metadata_only`，并在检查项中说明没有加载完整数据。

业务规则：字段画像是轻量安全步骤，不应因为几百 MB 的真实数据导致页面或服务卡死。

## 行为 4：损坏或无法解析的 DTA 不伪造字段

Given 用户绑定的文件扩展名是 `.dta`，但内容损坏或当前读取器无法解析  
When 用户请求字段画像  
Then 系统应返回 `blocked/not_profiled`、空字段列表和明确阻塞原因，而不是抛 500 或伪造变量字典。

业务规则：无法证明的数据结构不能进入研究流程。

## 行为 5：DTA 字段画像仍不改写研究状态

Given DTA 字段画像生成成功  
When 用户查看画像结果  
Then `can_feed_variable_roles` 仍为 `false`，并明确下一步是人工审阅字段画像，再手动确认 VariableRoleSet。

业务规则：变量角色确认是人工决策，不是解析器副作用。

## 边界

- 本阶段只接入 DTA metadata reader，不接入 XLSX/Parquet 深度 schema。
- 本阶段不把 DTA 字段自动写入 VariableRoleSet。
- 本阶段不运行真实 CFPS 回归。
- 如果运行环境缺少安全 DTA reader，应返回 blocked，而不是中断服务。
