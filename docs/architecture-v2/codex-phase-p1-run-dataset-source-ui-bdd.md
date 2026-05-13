# Phase P1-C BDD: Run Dataset Source In Observable Execution

## 背景

P1-B 已经让用户从数据页选择项目内本地数据文件，并在创建 run 时把 `dataset_source` 写入 response 和 `run_manifest.json`。P1-C 的目标是把这个来源提升为实证执行页的一等证据：用户进入某个 run 时，不需要打开 JSON 文件，就能看到本次执行使用了哪个数据文件、证据等级是什么、系统对数据做了哪些最小理解。

## 行为用例

### 行为 1：observability API 顶层暴露 run 数据来源

Given 用户用 `Data/Final/analysis_sample.csv` 启动一次 dry-run  
When 前端请求 `GET /api/v1/projects/{project_id}/runs/{run_id}/observability`  
Then response 顶层必须包含 `dataset_source`  
And `dataset_source` 必须与 `manifest.dataset_source` 一致  
And `dataset_source.evidence_level` 必须是 `local_file`。

业务规则：执行页不应从 manifest 内部猜字段；数据来源是 run 级证据，应作为一等字段给 UI 消费。

### 行为 2：数据来源保留最小数据理解证据

Given 数据来源是 CSV 文件  
When run source 被解析并写入 manifest  
Then `dataset_source` 应包含 `row_count` 和 `column_count`  
And 这些字段来自本地文件检查，而不是 mock。

业务规则：CoPaper/StatsPAI 式流程的第一步不是只保存文件名，而是证明系统确实读取了数据结构。

### 行为 3：实证执行页显示当前 run 使用的数据文件

Given 用户进入实证执行页并选择一个有 `dataset_source` 的 run  
When 页面渲染 run header 和证据面板  
Then 页面显示数据文件名、项目相对路径、文件类型、行列数、role/证据等级  
And evidence badge 必须显示“本地文件”。

业务规则：用户必须能在执行页确认“这次执行基于哪个真实数据”，而不是跳回数据页或打开 manifest。

### 行为 4：缺少数据来源时显示可恢复说明

Given 历史 run 没有 `dataset_source`  
When 页面渲染该 run  
Then 页面显示“未记录数据来源”  
And 引导用户从数据页选择本地数据后重新启动 run。

业务规则：历史 run 不能伪造数据来源；缺失证据应显式暴露。

## 边界条件

- P1-C 不做变量级 schema 编辑；只展示文件级 source 和最小 shape。
- P1-C 不做 multipart 上传；沿用 P1-B 的项目内本地数据选择。
- P1-C 不把缺失 source 的历史 run 自动补成当前 configured dataset，避免篡改历史证据。
