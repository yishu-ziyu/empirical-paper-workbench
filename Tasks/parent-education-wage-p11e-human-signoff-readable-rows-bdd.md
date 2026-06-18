# P11E Human Signoff Readable Rows BDD

## SDD

用户：本科生或初级研究者，在 P11 表单里人工确认 source contract。

目标：让用户在桌面和移动端都能看清每个字段来源行里四个输入框分别代表什么，再逐行勾选 human confirmation。P11E 只改善人工签收可读性，不替用户做字段口径决定。

系统必须交付：

- P11 每个 source row 都把 `dataset column`、`source field`、`source path`、`evidence level` 做成可见字段标签。
- row human confirmation 仍是单独 checkbox，不因预填候选值自动选中。
- readiness 继续显示 `human_confirmation` 缺口并禁用保存按钮。
- 移动端隐藏表头后，行内标签仍然可见。

不能越过的边界：

- 不保存真实 source contract。
- 不改 P11 后端 payload。
- 不写正式 VariableRoleSet、DesignSpec、RunPlan。
- 不创建 run id，不执行模型。

## BDD

### 行为 1：每个 source row 有可见字段标签

Given P11 表单展示 source metadata 字段来源行
When 用户查看任意 source row
Then 该行必须显示 `dataset column`、`source field`、`source path`、`evidence level` 四个标签

业务规则：用户不能靠记忆或表头猜输入框含义。

### 行为 2：移动端隐藏表头后仍能读懂行内容

Given 移动端布局隐藏了字段表头
When 用户逐行查看 P11 source rows
Then 行内标签仍然保留，不能只剩多个无文本输入框

业务规则：P11-Human 必须能在手机窄屏上完成审阅，不依赖桌面表头。

### 行为 3：人工确认仍然独立于字段文本

Given source row 已经预填候选 dataset column、source field、source path 和 evidence level
When 用户没有勾选 row human confirmation
Then readiness 仍必须把该行列为 `human_confirmation` 缺口

业务规则：候选值只是候选，只有人工确认动作才能解除确认缺口。

### 行为 4：P11E 不改变正式层边界

Given P11E 只调整 P11-Human 签收界面
When 用户查看页面或运行 API
Then 页面不能出现模型执行入口，P9/P12 仍必须被 source contract 和正式保存门禁阻断

业务规则：可读性改进不能被误解为 source contract 已被签收。

## 边界条件

- P11E 不决定 CFPS 波次、父母教育构造、hukou 角色或控制变量口径。
- P11E 不新增“一键确认全部”按钮。
- P11E 不把预填候选行自动设为 confirmed。
