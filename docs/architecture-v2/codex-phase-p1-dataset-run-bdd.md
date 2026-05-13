# Phase P1-B BDD: Dataset Source To Observable Run

## 背景

CoPaper 的产品路径从“上传/选择数据”开始，StatsPAI/Stata PAI 的方法路径要求每次统计执行都能追溯数据来源。P1-B 的第一步是把数据入口从 mock 空状态推进到本地文件证据：系统列出项目内真实数据文件，用户启动 run 时带上数据来源，run response 和 observability manifest 都记录该数据来源。

## 行为用例

### 行为 1：数据页必须列出项目内真实数据文件

Given 项目目录存在 `Data/Final/analysis_sample.csv`  
When 前端或测试请求 `GET /api/v1/projects/{project_id}/datasets`  
Then API 返回 `_meta.evidence_level == "local_file"`  
And `items` 至少包含该数据文件的 path、name、file_type、size、evidence_level  
And 如果该文件是 `paper.yaml` 中的 `data.final_dataset`，必须标记为 configured final dataset。

业务规则：数据入口不能继续伪装成 Phase A mock；有本地数据就必须作为可追溯证据展示。

### 行为 2：没有数据文件时仍保留可解释空状态

Given 项目目录没有可识别数据文件  
When 请求 datasets API  
Then API 返回 `items=[]`  
And `_meta.evidence_level == "local_file"`  
And empty_state 说明系统已经检查过项目目录。

业务规则：空状态也是本地文件检查结果，不是 mock 研究结论。

### 行为 3：启动 run 时必须记录用户选择的数据来源

Given 用户选择 `Data/Final/analysis_sample.csv`  
When 调用 `POST /api/v1/projects/{project_id}/runs` 并提交 `dataset_path`  
Then run response 必须包含 `dataset_source`  
And `dataset_source.evidence_level == "local_file"`  
And `dataset_source.path` 等于用户选择的项目内相对路径。

业务规则：执行不是孤立动作，必须能追溯本次 run 使用的数据源。

### 行为 4：observable manifest 必须持久化数据来源

Given run 成功完成  
When 读取 `state/runs/{run_id}/run_manifest.json` 或 observability API  
Then manifest 必须包含相同的 `dataset_source`  
And evidence_level 必须是 `local_file`。

业务规则：刷新页面、换 session 或交接给下一轮 Agent 后，数据来源仍可恢复。

### 行为 5：非法数据路径不能启动执行

Given 用户提交不存在或越过项目根目录的数据路径  
When 调用 run API  
Then API 必须返回结构化错误  
And 不应启动 run 或写入新的 observable artifacts。

业务规则：本地文件证据只能来自项目目录内的可验证文件。

## 边界条件

- P1-B 第一轮不做 multipart 上传；先支持已在项目目录内的数据文件选择。
- P1-B 第一轮不改写 `paper.yaml` 的变量配置；如果选择了非 configured final dataset，只记录 source，后续再做 schema/变量确认 gate。
- P1-B 第一轮只支持项目内相对路径；绝对路径和 `..` 越界路径返回错误。
