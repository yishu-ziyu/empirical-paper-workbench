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

## GET /sessions/{session_id}/replication-script

复现脚本：研究中**实际执行**的估计调用，按运行顺序排列（`backend/services/replication.py`）。与 `code-export` 不同，不经过 `translate_code`。

- 覆盖：研究台账的设定运行，以及固定分派产生的主估计（OLS、IV、RD、SCM、DiD）。每个调用按估计器在调用处写下的 `call` 记录还原；旧的设定运行记录没有 `call` 时，按 spec_run 的默认调用还原。
- 每份数据文件读入前校验 sha256，不符时 `SystemExit`。设定运行和主估计读不同文件时，各自加载。
- 不纳入、并在脚本末尾写明原因：估计 Agent 路径（其报告的代码尚未核实为实际执行）、不认识的估计器。研究时失败的运行保留为注释。
- 尚未覆盖：稳健性检验与设定曲线、设定运行之外的识别诊断、清洗步骤、描述统计表。

**响应 200**：`text/x-python`，`Content-Disposition: attachment; filename="replication.py"`。

**错误码**：404（会话没有设定运行）。

---

## GET /sessions/{session_id}/replication-package

复现包 zip：`replication.py`、每份被读取的数据文件 `data_<sha256 前 8 位>.csv`（研究时读取的那份文件，字节相同）、`README.md`。解压后运行 `python replication.py` 即可复现。

**响应 200**：`application/zip`，`Content-Disposition: attachment; filename="replication-package.zip"`。

**错误码**：404（没有设定运行）、409（分析数据文件已不存在，或与记录的 sha256 不一致）。

验收与证据：[复现脚本验收契约](../../../acceptance/replication-script.md)。

---

## GET /sessions/{session_id}/code-export?format=py

导出**翻译版**代码文件，由 `translate_code` 生成，不是实际运行的代码，数值未核对。要实际运行的代码请用上面的复现脚本。format 取值：`py`（Python）、`do`（Stata）、`R`（R）、`m`（EViews）。

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
