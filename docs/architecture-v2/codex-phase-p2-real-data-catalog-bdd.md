# Phase P2-F BDD: 真实数据候选池

目标：把 `/Users/mahaoxuan/Desktop/实证数据库` 这类真实数据仓库接入产品视野，但保持只读。产品先让用户看清“有什么数据、来自哪里、能否画像、是否适合进入变量确认”，不直接把外部数据伪装成当前论文项目数据。

## 行为 1：项目数据 API 返回外部真实数据库候选池

Given 当前机器存在一个真实数据仓库  
When 用户打开 Data & Variables 页面或调用 `/api/v1/projects/{project_id}/datasets`  
Then API 必须返回 `external_catalog`，其中包含候选数据文件、来源根目录、证据等级和只读状态  

业务规则：真实数据仓库是候选池，不是当前项目的 `Data/` 目录，必须显式标记 `read_only: true` 和 `role: external_candidate_dataset`。

## 行为 2：CSV 外部候选数据要返回轻量画像

Given 外部真实数据库里有 CSV 文件  
When API 扫描候选池  
Then API 必须返回字段数、样本预览行数、缺失率、数值字段数、文本字段数和 `profile_scope: catalog_preview`  

业务规则：外部 CSV 可以做轻量预览画像，但不能为了页面加载读取超大文件全量内容。

## 行为 3：暂未解析的外部格式仍要可见

Given 外部真实数据库里有 DTA/XLSX 等暂未内容解析的文件  
When API 扫描候选池  
Then 这些文件必须保留在候选池中，并标记 `readiness_status: not_profiled`  

业务规则：暂未画像不等于没有价值；用户仍然需要看到 CFPS/CGSS/CLDS/IFR 等真实数据资产。

## 行为 4：前端必须把外部候选池与项目内数据分开

Given API 返回外部候选池和项目内 `Data/` 目录数据  
When 用户打开 Data & Variables 页面  
Then 页面必须单独渲染“真实数据候选池”，并说明这些数据需要导入或绑定后才会进入当前项目  

业务规则：防止用户误以为外部数据库已经被当前论文 run 使用。

## 行为 5：外部候选池必须支持空状态

Given 当前机器没有配置或找不到真实数据仓库  
When 用户打开 Data & Variables 页面  
Then 页面必须给出清晰空状态，而不是报错或隐藏该区域  

业务规则：产品应适配不同机器，不把本机路径写死成唯一依赖。

## 边界条件

- P2-F 只做只读目录扫描和轻量画像，不复制、不上传、不修改原始数据。
- CSV 外部画像使用预览样本，不承诺全量统计。
- DTA/XLSX/Parquet 的内容级读取放到后续 P2-G。
- 外部数据进入回归前，必须先经过导入/绑定、变量角色确认、DesignSpec、RunPlan。
