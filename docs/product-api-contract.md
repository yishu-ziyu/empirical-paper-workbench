# 多项目产品后端最小 API 契约

## 1. 目标

这份契约先只定义能支撑「多项目管理 + 触发 `run_paper` + 查看结果」的最小后端表面，刻意不展开权限、数据库抽象、任务队列、WebSocket 推送等后续能力。

设计原则：

- 先包住当前仓库已经稳定存在的产物：`state/project_state.json`、`Results/index.json`、`Results/json/project_snapshot.json`、生成稿件。
- 先支持多项目，不把后端绑死在单一项目根目录。
- 第一版尽量允许标准库级别的黑盒集成测试，不要求 `pytest`、`requests`、`httpx` 等额外包。

## 2. 范围与假设

- Base URL：`/api/v1`
- 内容类型：请求与响应默认 `application/json; charset=utf-8`
- 鉴权：第一版本地开发可先不做；如果后续加鉴权，不改变资源形状，只补请求头规则
- 时间格式：统一 ISO 8601 UTC 时间戳
- 路径字段：`project_root`、`state_path`、`results_index_path` 为服务端管理路径，面向可信内部产品使用，不应直接暴露给不可信公网客户端

## 3. 资源模型

### 3.1 Project

```json
{
  "id": "proj_01HXYZ...",
  "slug": "robot-labor-match",
  "title": "工业机器人应用对劳动力市场匹配效率的影响",
  "project_root": "/abs/path/to/project",
  "language": "zh",
  "current_stage": "question-definition",
  "dataset_exists": false,
  "last_run_mode": "dry-run",
  "created_at": "2026-04-25T03:10:00Z",
  "updated_at": "2026-04-25T03:10:00Z"
}
```

字段对齐说明：

- `current_stage`、`dataset_exists`、`last_run_mode` 可直接映射当前 `state/project_state.json`
- `slug`、`title`、`language` 可直接映射当前 `paper.yaml`

### 3.2 Run

```json
{
  "id": "run_01HXYZ...",
  "project_id": "proj_01HXYZ...",
  "mode": "dry-run",
  "status": "queued",
  "started_at": "2026-04-25T03:11:00Z",
  "finished_at": null,
  "state_path": null,
  "results_index_path": null,
  "artifact_count": 0,
  "error": null
}
```

`status` 枚举：

- `queued`
- `running`
- `succeeded`
- `failed`

执行完成后，`Run` 对象补齐：

```json
{
  "id": "run_01HXYZ...",
  "project_id": "proj_01HXYZ...",
  "mode": "dry-run",
  "status": "succeeded",
  "started_at": "2026-04-25T03:11:00Z",
  "finished_at": "2026-04-25T03:11:03Z",
  "state_path": "state/project_state.json",
  "results_index_path": "Results/index.json",
  "artifact_count": 4,
  "state": {
    "current_stage": "question-definition",
    "last_run_mode": "dry-run",
    "dataset_exists": false
  },
  "results": {
    "mode": "dry-run",
    "current_stage": "question-definition",
    "artifacts": [
      {
        "kind": "json",
        "path": "Results/json/project_snapshot.json",
        "description": "Structured project snapshot",
        "exists": true
      }
    ]
  },
  "artifact_paths": [
    "state/project_state.json",
    "Results/index.json",
    "Results/json/project_snapshot.json",
    "Manuscripts/generated/paper_draft.md",
    "Manuscripts/generated/paper_draft.tex"
  ],
  "error": null
}
```

字段对齐说明：

- `state` 来自 `state/project_state.json`
- `results` 来自 `Results/index.json`
- `artifact_paths` 是为前端和测试方便做的扁平展开，不替代文件本身

### 3.3 Error

统一错误形状：

```json
{
  "error": {
    "code": "project_not_found",
    "message": "Project proj_missing does not exist.",
    "details": {}
  }
}
```

最小错误码集合：

- `invalid_request`
- `project_not_found`
- `run_not_found`
- `run_failed`
- `conflict`

## 4. 端点契约

### 4.1 `GET /api/v1/health`

用途：健康检查、测试等待服务启动

`200 OK`

```json
{
  "status": "ok",
  "service": "econ-paper-product-api",
  "version": "0.1.0"
}
```

### 4.2 `GET /api/v1/projects`

用途：列出已注册项目

`200 OK`

```json
{
  "items": [
    {
      "id": "proj_01HXYZ...",
      "slug": "robot-labor-match",
      "title": "工业机器人应用对劳动力市场匹配效率的影响",
      "project_root": "/abs/path/to/project",
      "language": "zh",
      "current_stage": "question-definition",
      "dataset_exists": false,
      "last_run_mode": "dry-run",
      "created_at": "2026-04-25T03:10:00Z",
      "updated_at": "2026-04-25T03:10:00Z"
    }
  ]
}
```

### 4.3 `POST /api/v1/projects`

用途：注册一个可被后端管理的论文项目

请求体：

```json
{
  "slug": "robot-labor-match",
  "title": "工业机器人应用对劳动力市场匹配效率的影响",
  "project_root": "/abs/path/to/project",
  "language": "zh"
}
```

约束：

- `slug` 在系统内唯一
- `project_root` 必须存在，并且至少能找到 `paper.yaml` 与 `Program/run_paper.py`

`201 Created`

响应体：`Project`

### 4.4 `GET /api/v1/projects/{project_id}`

用途：读取单个项目状态

`200 OK`

响应体：`Project`

`404 Not Found`

响应体：`Error`

### 4.5 `POST /api/v1/projects/{project_id}/runs`

用途：触发一次运行。第一版只要求支持 `dry-run`，`live` 可保留契约位。

请求体：

```json
{
  "mode": "dry-run"
}
```

约束：

- `mode` 允许值：`dry-run`、`live`
- 后端内部执行建议直接复用 `python3 Program/run_paper.py --project-root <project_root> [--dry-run]`

`202 Accepted`

响应体：初始 `Run`

### 4.6 `GET /api/v1/projects/{project_id}/runs`

用途：列出某个项目的历史运行

`200 OK`

```json
{
  "items": [
    {
      "id": "run_01HXYZ...",
      "project_id": "proj_01HXYZ...",
      "mode": "dry-run",
      "status": "succeeded",
      "started_at": "2026-04-25T03:11:00Z",
      "finished_at": "2026-04-25T03:11:03Z",
      "state_path": "state/project_state.json",
      "results_index_path": "Results/index.json",
      "artifact_count": 4,
      "error": null
    }
  ]
}
```

### 4.7 `GET /api/v1/projects/{project_id}/runs/{run_id}`

用途：轮询执行状态，并在完成时返回状态摘要与结果索引

`200 OK`

响应体：`Run`

`404 Not Found`

响应体：`Error`

## 5. 最小实现约束

第一版后端只要做到下面几点，就能被前端和测试接上：

1. 项目注册后能稳定获得 `project_id`
2. `POST /runs` 后能返回 `run_id`
3. `GET /runs/{run_id}` 能从 `queued/running` 过渡到 `succeeded/failed`
4. 成功时返回 `state`、`results`、`artifact_paths`
5. 这些字段的值与磁盘上的 `state/project_state.json`、`Results/index.json` 保持一致

## 6. 基于标准库的集成测试思路

测试目标不是覆盖后端内部实现，而是用黑盒方式校验契约是否成立。

建议只用 Python 标准库：

- `unittest`：组织测试
- `urllib.request`：发 HTTP 请求
- `subprocess`：可选地拉起本地服务
- `tempfile` + `shutil.copytree`：复制临时项目目录，避免污染真项目
- `json`：断言响应与产物结构
- `time`：轮询运行结果

建议覆盖的最小用例：

1. `health` 返回 `200` 且 `status=ok`
2. `POST /projects` 能成功注册一个临时复制出来的项目
3. `GET /projects` 与 `GET /projects/{id}` 能读回刚注册的项目
4. `POST /projects/{id}/runs` 触发 `dry-run` 成功
5. `GET /projects/{id}/runs/{run_id}` 最终返回 `succeeded`
6. 返回的 `artifact_paths` 至少包含：
   - `state/project_state.json`
   - `Results/index.json`
   - `Results/json/project_snapshot.json`
   - `Manuscripts/generated/paper_draft.md`
   - `Manuscripts/generated/paper_draft.tex`
7. 未知项目返回 `404` + 统一错误形状

## 7. 测试入口约定

`tests/test_product_api_integration.py` 按下面的环境变量工作：

- `PRODUCT_API_BASE_URL`
  - 必填
  - 例：`http://127.0.0.1:8000`
- `PRODUCT_API_START_CMD`
  - 可选
  - 如果提供，测试会先尝试用这个命令拉起服务，再开始探活
  - 例：`python3 Program/product_api.py`
- `PRODUCT_API_STARTUP_TIMEOUT`
  - 可选，默认 `20`
- `PRODUCT_API_POLL_TIMEOUT`
  - 可选，默认 `30`

运行方式：

```bash
python3 -m unittest tests.test_product_api_integration -v
```

如果后端尚未实现或未配置 `PRODUCT_API_BASE_URL`，测试应被整体 `skip`，而不是让现有仓库变红。

## 8. 非目标

这份最小契约暂不处理：

- 用户体系与权限模型
- 文件上传下载接口
- 结果流式推送
- 运行取消、重试、并发配额
- 数据库存储结构
- OpenAPI 自动生成细节
