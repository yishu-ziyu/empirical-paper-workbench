# 导出

> 上级：[端点详情](../03-endpoint-details.md)


## POST /sessions/{session_id}/translate-code

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

## GET /sessions/{session_id}/code-export?format=py

导出代码文件。format 取值：`py`（Python）、`do`（Stata）、`R`（R）、`m`（EViews）。

session 尚无 takeable `code_translations` 时：若方向点名了 outcome+treatment，或章节含 ```python 代码块，GET 会先跑 `translate_code` 再返回文件。空 session、只有 question 的方向、以及「无 Python 代码可翻译」占位不会当作 200 文件返回（不编造 `y ~ treat`）。

**响应 200**：`PlainTextResponse`，Content-Disposition: attachment。

**错误码**：400（不支持 format）、404（无 code_translations 且不足以自动填充）

---

## GET /sessions/{session_id}/doc-export?format=tex&template=cn_journal

导出文档。format 取值：`tex`（LaTeX）、`pdf`（PDF）、`docx`（Word）。template 取值：`cn_journal` / `undergraduate` / `master_thesis` / `english_submission`。

**响应 200**：tex → PlainTextResponse；pdf / docx → FileResponse。

**错误码**：400（不支持 format）、503（编译工具不可用）

---

## GET /sessions/{session_id}/export?format=tex

简单导出（当前仅支持 LaTeX）。

**响应 200**：`application/x-tex` 文本。

---
