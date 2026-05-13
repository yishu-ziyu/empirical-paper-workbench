# Phase P2-A BDD: 数据质量画像

目标：把 CoPaper/StatsPAI 式“先读数据、再判断能否进入模型”的产品步骤落到当前工作台。数据集不再只是一个文件列表，而是进入变量角色、研究设计和执行计划之前的可审计研究对象。

## 行为 1：数据集 API 返回质量画像

Given 项目 `Data` 目录里存在可读取的 CSV 数据集  
When 前端请求 `/api/v1/projects/{project_id}/datasets`  
Then 每个数据集条目必须包含 `quality_profile`  
And `quality_profile.evidence_level` 必须是 `local_file`  
And 必须包含行数、列数、缺失值、字段类型摘要和检查项  

业务规则：数据质量画像来自本地文件证据，不允许伪装成真实清洗或真实回归结果。

## 行为 2：缺失值会阻塞进入“ready”

Given CSV 数据里存在空单元格  
When 系统生成质量画像  
Then `missing_cells` 必须大于 0  
And `readiness_status` 必须是 `needs_review`  
And 检查项里必须标记缺失值检查为 `warning`

业务规则：有缺失值的数据可以继续展示，但需要人工确认处理策略后再进入研究设计。

## 行为 3：无缺失且有样本的数据可以 ready

Given CSV 数据存在字段和至少一行样本  
And 没有空单元格  
When 系统生成质量画像  
Then `readiness_status` 必须是 `ready`  
And 缺失率必须是 0

业务规则：ready 只表示“可进入变量角色确认”，不表示模型或论文结论已成立。

## 行为 4：暂不支持的文件类型仍保留证据

Given 数据文件是 dta/xlsx/parquet 等当前未做内容解析的格式  
When 系统列出数据集  
Then 条目仍然保留 `evidence_level=local_file`  
And `quality_profile.supported` 必须是 false  
And `readiness_status` 必须是 `not_profiled`

业务规则：不能因为暂不解析就把真实文件从工作台隐藏；但 UI 必须清楚说明尚未完成质量画像。

## 行为 5：前端必须展示数据质量画像

Given 数据集 API 返回了 `quality_profile`  
When 用户进入“数据与变量”页面  
Then 页面必须显示质量画像面板  
And 用户能看到缺失率、字段类型、ready 状态、证据等级和字段画像  

业务规则：数据页的第一目标是让用户判断“这份数据是否能进入研究设计”，而不是只看到文件名。

## 边界条件

- 本阶段只解析 CSV 的内容；dta/xlsx/parquet 先列入 `not_profiled`。
- 类型识别只做轻量推断：所有非空样本都能转成数字则是 numeric，否则是 text。
- `ready` 不代表清洗完成，只代表当前数据文件没有结构性空洞，允许进入变量角色确认。
