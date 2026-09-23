# 研究方向 & 大纲

> 上级：[端点详情](../03-endpoint-details.md)


## POST /sessions/{session_id}/direction

设置研究方向，运行 set_direction + identification_verify。识别通过后写入
Table 1 描述统计与主设定方程（`prewrite_gate=awaiting_estimate`），**不**自动跑
estimate → robustness → outline。继续估计见
[prewrite-confirm.md](../../prewrite-confirm.md)。

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

**响应 202**：durable run（`run_id` / `events_url`）。成功后 snapshot 含
`table1`、`specification_equation`、`prewrite_gate`，**没有**新的 `estimate` / `outline`。

---

## POST /sessions/{session_id}/prewrite/confirm

方向预览确认后，从 `run_estimate` 接到大纲。契约与 payload 见
[prewrite-confirm.md](../../prewrite-confirm.md)。

**请求体**（两段确认后才能跑估计）：

```json
{
  "action": "continue_estimate",
  "table1Confirmed": true,
  "specConfirmed": true,
  "qType": "heterogeneity",
  "specMode": "interaction"
}
```

`action=record_confirms` 只落盘旗标（200）。`qType === heterogeneity` 且设定无
交互时 `blockingDecision.isBlock=true`，估计 409。详见
[prewrite-confirm.md](../../prewrite-confirm.md)。

**请求头**：`Idempotency-Key`（必填）。

**响应 202**：与 `POST /direction` 相同的 `RunAcceptedResponse`（仅 `continue_estimate`）。

---

## POST /sessions/{session_id}/resume

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
