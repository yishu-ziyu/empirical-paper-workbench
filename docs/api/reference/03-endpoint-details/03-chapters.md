# 章节生成

> 上级：[端点详情](../03-endpoint-details.md)


## POST /sessions/{session_id}/generate-chapter

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

## POST /sessions/{session_id}/approve-chapter

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

## POST /sessions/{session_id}/rollback

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

## POST /sessions/{session_id}/regenerate

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

## GET /sessions/{session_id}/chapters/{chapter_index}/versions

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
