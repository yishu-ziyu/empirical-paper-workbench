# econpaper API 文档

> 版本：0.1.0 | 基础 URL：`http://localhost:8000`

econpaper 后端 API 基于 FastAPI 构建，提供论文生成全流程的 REST + WebSocket 接口。

## 快速开始

```bash
# 启动后端
cd backend && . .venv/bin/activate && uvicorn main:app --reload --port 8000

# 交互式文档（启动后访问）
open http://localhost:8000/docs
open http://localhost:8000/redoc
```

## 端点一览

| Router | 端点 | 方法 | 说明 |
|--------|------|------|------|
| sessions | `/upload` | POST | 上传 CSV 文件，创建 session，运行 graph pipeline |
| sessions | `/sessions` | POST | 创建空 session（不上传文件） |
| sessions | `/sessions/{id}` | GET | 查询 session 状态（用于 localStorage 恢复校验） |
| sessions | `/sessions/{id}/export` | GET | 导出论文源码（format=tex 当前仅支持 LaTeX） |
| outline | `/sessions/{id}/direction` | POST | 设置研究方向，生成大纲 |
| outline | `/sessions/{id}/resume` | POST | 用户调整大纲后重跑 generate_outline |
| chapter | `/sessions/{id}/generate-chapter` | POST | 生成指定章节（写入 current_chapter → 跑节点 → 返回章节） |
| chapter | `/sessions/{id}/approve-chapter` | POST | 审批章节，标记 status="approved" |
| chapter | `/sessions/{id}/rollback` | POST | 回滚到指定版本 |
| chapter | `/sessions/{id}/regenerate` | POST | 重新生成当前章 |
| chapter | `/sessions/{id}/chapters/{index}/versions` | GET | 获取指定章节的所有版本历史 |
| eda | `/sessions/{id}/eda` | POST | 探索性数据分析（describe / corr / missing / plot / scatter / regression） |
| sample | `/sessions/{id}/transform` | POST | 变量重编码与构造（sub-step 5） |
| sample | `/sessions/{id}/filter` | POST | 样本筛选（sub-step 6） |
| sample | `/sessions/{id}/balance` | POST | 面板平衡性检查（sub-step 7） |
| charls | `/sessions/{id}/charls/detect` | GET | CHARLS 数据集检测 |
| charls | `/sessions/{id}/charls/confirm` | POST | 确认 CHARLS 向导配置 |
| code_export | `/sessions/{id}/code-export` | GET | 导出代码文件（py / do / R / m） |
| doc_export | `/sessions/{id}/doc-export` | GET | 导出文档（tex / pdf / docx） |
| progress | `/sessions/{id}/progress` | GET | 查询论文完成进度 |
| review | `/sessions/{id}/review` | GET | 获取当前章的评审信息 |
| review | `/sessions/{id}/review/decision` | POST | 提交 HITL 评审决策（accept / reject / force_pass） |
| ws | `/sessions/{id}/stream` | WS | WebSocket 实时流推送 |
| — | `/` | GET | 服务根路径（返回服务信息） |
| — | `/health` | GET | 健康检查 |

## 端点详情

### 上传 & Session 管理

#### POST /upload

上传 CSV 文件，创建 session，运行完整的 LangGraph pipeline。

**请求体**：`multipart/form-data`

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file | File | 是 | CSV 文件（最大 50MB） |

**响应 200**：

```json
{
  "session_id": "uuid-string",
  "dataset_meta": {
    "columns": ["var1", "var2", ...],
    "rows": 1000,
    "dtypes": {"var1": "int64", "var2": "object"},
    "missing_count": 42
  }
}
```

**错误码**：400（非 CSV 文件）、413（超过大小限制）、422（解析失败）

---

#### POST /sessions

创建空 session（不上传文件）。

**响应 200**：

```json
{
  "session_id": "uuid-string"
}
```

---

#### GET /sessions/{session_id}

查询 session 是否存在及是否包含数据集。用于前端 localStorage 恢复校验。

**响应 200**：

```json
{
  "session_id": "uuid-string",
  "exists": true,
  "has_dataset": true
}
```

**错误码**：404（session 不存在）

---

### 研究方向 & 大纲

#### POST /sessions/{session_id}/direction

设置研究方向，运行 set_direction + generate_outline 节点，返回 6 章大纲。

**请求体**：

```json
{
  "question": "教育对收入的影响",
  "dv": "收入",
  "iv": "教育年限",
  "controls": ["年龄", "性别", "地区"],
  "method": "ols",
  "template": "cn_journal"
}
```

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| question | string | 是 | — | 研究问题 |
| dv | string | 是 | — | 因变量 |
| iv | string | 是 | — | 自变量 |
| controls | string[] | 否 | [] | 控制变量 |
| method | string | 是 | — | 计量方法 |
| template | string | 否 | "cn_journal" | 模板（cn_journal / undergraduate / master_thesis / english_submission） |

**响应 200**：

```json
{
  "outline": [
    {"type": "intro", "title": "引言", "research_question": "..."},
    {"type": "lit_review", "title": "文献综述", "research_question": null},
    ...
  ],
  "research_direction": {...}
}
```

---

#### POST /sessions/{session_id}/resume

用户调整大纲后重跑 generate_outline。

**请求体**：

```json
{
  "outline": [
    {"type": "intro", "title": "引言", "research_question": "..."},
    ...
  ]
}
```

**响应 200**：

```json
{
  "ok": true,
  "outline": [...]
}
```

---

### 章节生成

#### POST /sessions/{session_id}/generate-chapter

生成指定章节。合法 type：`intro` / `lit_review` / `data_desc` / `methods` / `results` / `conclusion`。

**请求体**：

```json
{
  "chapter": {
    "type": "intro",
    "title": "引言",
    "method": null,
    "research_question": "教育对收入的影响"
  },
  "render_kwargs": {}
}
```

**响应 200**：

```json
{
  "chapter": {
    "type": "intro",
    "title": "引言",
    "content": "## 引言\n\n...",
    "status": "generated",
    "versions": [],
    "chapter_index": 0
  },
  "body_chapters": [...]
}
```

**错误码**：400（未知 chapter_type）

---

#### POST /sessions/{session_id}/approve-chapter

审批章节，标记 status="approved"。

**请求体**：

```json
{
  "chapter_type": "intro"
}
```

`chapter_type` 可选，缺省时审批最后生成的章节。

**响应 200**：

```json
{
  "ok": true,
  "chapter": {...},
  "body_chapters": [...]
}
```

---

#### POST /sessions/{session_id}/rollback

回滚到指定版本。

**请求体**：

```json
{
  "chapter_index": 0,
  "version_index": 0
}
```

**响应 200**：

```json
{
  "chapter": {...},
  "body_chapters": [...]
}
```

---

#### POST /sessions/{session_id}/regenerate

重新生成指定章节。

**请求体**：

```json
{
  "chapter_index": 0
}
```

**响应 200**：

```json
{
  "chapter": {...},
  "body_chapters": [...]
}
```

---

#### GET /sessions/{session_id}/chapters/{chapter_index}/versions

获取指定章节的所有版本。

**响应 200**：

```json
{
  "chapter_index": 0,
  "count": 3,
  "versions": [
    {"index": 0, "preview": "## 引言\n\n教育作为人力资本的核心...（前50字）"},
    {"index": 1, "preview": "## 引言\n\n教育投资是影响个体...（前50字）"}
  ]
}
```

---

### 探索性数据分析 (EDA)

#### POST /sessions/{session_id}/eda

运行 EDA 动作。合法 action：`describe` / `corr` / `missing` / `plot` / `scatter` / `regression`。

**请求体**：

```json
{
  "action": "describe"
}
```

**describe 响应 200**：

```json
{
  "action": "describe",
  "result": {
    "columns": ["variable", "count", "mean", "std", "min", "max", "missing"],
    "rows": [
      {"variable": "age", "count": 1000, "mean": 45.2, "std": 12.3, "min": 18, "max": 80, "missing": 5},
      ...
    ]
  }
}
```

**corr 响应 200**：

```json
{
  "action": "corr",
  "result": {
    "variables": ["age", "income", "education"],
    "matrix": [[1.0, 0.3, 0.5], [0.3, 1.0, 0.2], [0.5, 0.2, 1.0]]
  }
}
```

**missing 响应 200**：

```json
{
  "action": "missing",
  "result": {
    "columns": ["variable", "missing_count", "missing_pct"],
    "rows": [
      {"variable": "income", "missing_count": 15, "missing_pct": 0.015},
      ...
    ]
  }
}
```

**错误码**：400（无效 action）

---

### 数据清洗（样本构造）

#### POST /sessions/{session_id}/transform

变量重编码与构造（sub-step 5）。支持类型：`log_transform` / `onehot` / `label` / `bin` / `interaction` / `policy_dummy`。

**请求体示例（log_transform）**：

```json
{
  "type": "log_transform",
  "column": "income"
}
```

**请求体示例（interaction）**：

```json
{
  "type": "interaction",
  "column": "education",
  "other_column": "experience"
}
```

**响应 200**：

```json
{
  "constructed_vars": ["log_income"]
}
```

---

#### POST /sessions/{session_id}/filter

样本筛选（sub-step 6）。

**请求体**：

```json
{
  "conditions": [
    {"col": "age", "op": ">=", "val": 18},
    {"col": "income", "op": ">", "val": 0}
  ]
}
```

**响应 200**：

```json
{
  "n_before": 1000,
  "n_after": 950,
  "conditions": [...]
}
```

---

#### POST /sessions/{session_id}/balance

面板平衡性检查（sub-step 7）。

**请求体**：

```json
{
  "panel_id": "id",
  "time_col": "year"
}
```

**响应 200**：

```json
{
  "balanced": 500,
  "unbalanced": 50,
  "n_periods": 5,
  "attrition_rate": 0.1
}
```

**错误码**：400（panel_id 或 time_col 缺失）

---

### CHARLS 数据集

#### GET /sessions/{session_id}/charls/detect

检测上传的数据集是否为 CHARLS 格式。

**响应 200**：

```json
{
  "dataset_type": "CHARLS",
  "charls_config": {
    "variable_mapping": {...},
    "waves": [1, 2, 3, 4, 5],
    "filter_presets": [...]
  }
}
```

非 CHARLS 数据集时 `charls_config` 为 null。

---

#### POST /sessions/{session_id}/charls/confirm

确认 CHARLS 向导配置，写入 session state。

**请求体**：

```json
{
  "variable_mapping": {"ID": "id", "wave": "wave"},
  "waves": [1, 2, 3],
  "filter_presets": [{"col": "age", "op": ">=", "val": 50}]
}
```

**响应 200**：

```json
{
  "ok": true,
  "charls_config": {...}
}
```

---

### 导出

#### POST /sessions/{session_id}/translate-code

跑 `translate_code` 节点，把 `code_translations` 写入 session。HITL 写章路径不会自动进该节点，所以写完后要显式调用，或依赖 GET `/code-export` 在首次下载时填充。

**响应 200**：

```json
{
  "ok": true,
  "code_translations": [
    {"lang": "py", "code": "...", "filename": "analysis.py"},
    {"lang": "stata", "code": "...", "filename": "analysis.do"},
    {"lang": "r", "code": "...", "filename": "analysis.R"},
    {"lang": "eviews", "code": "...", "filename": "analysis.m"}
  ]
}
```

**错误码**：404（session 不存在）、503（translate_code 节点不可用）

---

#### GET /sessions/{session_id}/code-export?format=py

导出代码文件。format 取值：`py`（Python）、`do`（Stata）、`R`（R）、`m`（EViews）。

session 尚无 takeable `code_translations` 时：若方向点名了 outcome+treatment，或章节含 ```python 代码块，GET 会先跑 `translate_code` 再返回文件。空 session、只有 question 的方向、以及「无 Python 代码可翻译」占位不会当作 200 文件返回（不编造 `y ~ treat`）。

**响应 200**：`PlainTextResponse`，Content-Disposition: attachment。

**错误码**：400（不支持 format）、404（无 code_translations 且不足以自动填充）

---

#### GET /sessions/{session_id}/doc-export?format=tex&template=cn_journal

导出文档。format 取值：`tex`（LaTeX）、`pdf`（PDF）、`docx`（Word）。template 取值：`cn_journal` / `undergraduate` / `master_thesis` / `english_submission`。

**响应 200**：tex → PlainTextResponse；pdf / docx → FileResponse。

**错误码**：400（不支持 format）、503（编译工具不可用）

---

#### GET /sessions/{session_id}/export?format=tex

简单导出（当前仅支持 LaTeX）。

**响应 200**：`application/x-tex` 文本。

---

### 进度

#### GET /sessions/{session_id}/progress

返回 6 章完成进度。

**响应 200**：

```json
{
  "total": 6,
  "completed": 2,
  "current": 3,
  "body_chapters": [
    {"type": "intro", "title": "引言", "status": "approved"},
    {"type": "lit_review", "title": "文献综述", "status": "approved"},
    {"type": "data_desc", "title": "数据描述", "status": "generated"},
    {"type": "methods", "title": "实证方法", "status": null},
    {"type": "results", "title": "实证结果", "status": null},
    {"type": "conclusion", "title": "结论", "status": null}
  ]
}
```

---

### HITL 评审

#### GET /sessions/{session_id}/review

获取当前章的评审信息。

**响应 200**：

```json
{
  "chapter_index": 0,
  "feedback": "理论框架清晰，但内生性讨论不足",
  "suggestions": "建议补充工具变量分析",
  "score": 0.65,
  "rubric": {
    "endogeneity": 0.5,
    "identification": 0.7,
    "robustness": 0.6,
    "contribution": 0.7,
    "readability": 0.8
  },
  "review_iteration": 1,
  "max_review_iterations": 2,
  "auto_decision": "fail"
}
```

---

#### POST /sessions/{session_id}/review/decision

提交评审决策。合法 decision：`accept` / `reject` / `force_pass`。

**请求体**：

```json
{
  "decision": "accept",
  "reviewer": "user",
  "comment": "章节内容完整，无需修改"
}
```

**响应 200**：

```json
{
  "ok": true,
  "decision": "accept",
  "chapter_index": 0,
  "next_action": "proceed"
}
```

`reject` 时 `next_action` 为 `"regenerate"`，触发重生成。

---

### 系统端点

#### GET /

```json
{"service": "econpaper-backend", "version": "0.1.0"}
```

#### GET /health

```json
{"status": "ok"}
```

---

## WebSocket 协议

### 连接

```
ws://localhost:8000/sessions/{session_id}/stream
```

### 消息类型

| type | 方向 | 说明 |
|------|------|------|
| `status` | 服务端 → 客户端 | 节点状态更新（running / done） |
| `streaming_chunk` | 服务端 → 客户端 | 章节内容流式推送 |
| `interrupt` | 服务端 → 客户端 | 推送完整章节内容，触发前端 HITL 暂停 |
| `error` | 服务端 → 客户端 | 错误信息 |

### 消息时序

```
客户端 → [wss 连接]
服务端 ← {"type": "status", "node": "upload_data", "status": "running"}
服务端 ← {"type": "status", "node": "clean_data", "status": "running"}
服务端 ← {"type": "status", "node": "generate_title", "status": "running"}
服务端 ← {"type": "streaming_chunk", "chapter_id": "title", "chunk": "## 引"}
服务端 ← {"type": "streaming_chunk", "chapter_id": "title", "chunk": "言\n\n..."}
服务端 ← {"type": "status", "node": "generate_title", "status": "done"}
服务端 ← {"type": "interrupt", "chapter_id": "title", "content": "..."}
服务端 → [关闭连接]
```

### 客户端示例

```javascript
const ws = new WebSocket(`ws://localhost:8000/sessions/${sessionId}/stream`);
ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  if (msg.type === 'streaming_chunk') {
    // 追加到编辑器
  } else if (msg.type === 'status') {
    // 更新进度条
  } else if (msg.type === 'interrupt') {
    // 显示 HITL 暂停界面
  } else if (msg.type === 'error') {
    // 显示错误
  }
};
```

---

## 认证

认证采用 httpOnly Cookie 双 token：`POST /auth/login` 成功后下发 `ep_access`（15 分钟，全站可见）与 `ep_access_refresh`（7 天，仅 `/auth` 路径）两个 HttpOnly Cookie；`POST /auth/refresh` 轮换 refresh（一次性，旧 token 即刻作废），`POST /auth/logout` 撤销 refresh 并清 Cookie。`Authorization: Bearer` 头仅为旧客户端兼容保留。登录/注册接口带限流与账号锁定（连续 5 次失败锁 10 分钟）。

---

## OpenAPI 规范

完整 OpenAPI 3.1 规范文件：[openapi.json](./openapi.json)

启动后端后也可访问：
- 交互式 Swagger UI：`http://localhost:8000/docs`
- ReDoc：`http://localhost:8000/redoc`

---

## 通用错误格式

```json
{
  "error": "Internal server error",
  "detail": "错误详情（DEBUG 模式）",
  "request_id": "uuid",
  "degraded": true
}
```

| 字段 | 说明 |
|------|------|
| `error` | 错误类型 |
| `detail` | 错误详情（生产环境仅 500 时隐藏） |
| `request_id` | 请求追踪 ID |
| `degraded` | 是否降级（>= 500 时为 true） |