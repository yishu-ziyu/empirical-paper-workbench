# P1 中文化界面文案 BDD

## 背景

当前产品主流程已经进入可视化验收阶段，但页面仍混用英文产品对象名和中文说明，例如 `Workspace Home`、`Data & Design`、`Run Plan`、`FindingCard`、`Review & Export`。这会让用户在验收产品流程时被迫理解内部工程术语。

本阶段目标是把所有用户可见页面文案替换为同义中文。API 字段名、状态枚举、文件路径、DOM id、CSS class、测试里的协议名称不属于本阶段翻译范围。

## 行为 1：一级导航必须使用中文研究生命周期名称

Given 用户打开实证工作台  
When 查看左侧一级导航和顶部标题  
Then 应看到“工作台首页 / 数据与设计 / 实证执行 / 结果与草稿 / 审阅与导出”  
And 不应看到 `Workspace Home`、`Data & Design`、`Execution`、`Results & Draft`、`Review & Export`

## 行为 2：核心阶段页面的标题和表单标签必须中文化

Given 用户进入数据、设计、执行、结果、审阅页面  
When 查看页面标题、面板标题、表单字段和按钮  
Then 应看到“变量角色集”“研究设计方案”“执行计划”“结果论断卡”“草稿证据绑定”“正文候选”“导出包验收台”等中文表达  
And 不应把 `VariableRoleSet`、`DesignSpec`、`RunPlan`、`FindingCard`、`Manuscript candidates` 作为主展示文案

## 行为 3：执行与导出页面必须把内部英文面板名称改成中文

Given 用户查看实证执行和审阅导出页  
When 查看运行轨迹和导出包验收区域  
Then 应看到“阶段看板”“事件流”“人工确认点”“产物与证据”“前沿工程评估器”  
And 不应看到 `Step Board`、`Event Stream`、`Human-in-the-loop`、`Artifacts / Evidence`、`Frontier-Eng evaluator`

## 行为 4：动态渲染文案必须避免英文操作标签

Given 页面通过 JavaScript 渲染工作流、状态、空状态和导出包信息  
When 用户查看渲染后的说明  
Then 应看到中文状态和操作说明，例如“已就绪”“已阻塞”“打开数据与设计”“本轮评估通过”  
And 不应看到 `Queued`、`Planning`、`Reviewing`、`ready`、`blocked`、`Open Data & Design` 这类英文展示词

## 边界

- 保留机器契约：`run_id`、`dataset_source`、`evidence_level`、`export_status`、`preview_ready`、`local_file`、`local_execution`、API 路径、文件路径不翻译。
- 保留数据字段名：`wage`、`trained`、`edu`、`experience` 等来自真实数据或模型公式的变量名不翻译。
- 保留方法论来源在内部数据结构中的英文标识，但页面展示用“前沿工程闭环/前沿工程评估器”等中文表达。
