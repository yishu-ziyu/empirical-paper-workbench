# Takeaway math research notes

| 字段 | 值 |
| --- | --- |
| 文档 | Research notes（不是可交付契约） |
| 任务 | FM-E-BUILD-TAKEAWAY-1 · slice G0（Firstmate HOLD 后收窄） |
| 状态 | **BLOCKED / OPEN** — 公式门未过 |
| 日期 | 2026-09-15 |
| 基线 | `fix/fm-e-build-math-1-docx-typesetting` @ `af9056b4f274c83f7b52032e80179cee230a7f61` |

本文件只记已知失败与未决问题。不冻结 takeaway pack，不声称 MATH-1 已完成，不实现 PDF / 成稿预览 / 业务代码。

---

## Known failure（Captain 实机）

Captain 在本机打开 **live Word**（真实下载的 `.docx`，不是单测夹具）。**公式仍然是乱码**：可见转义 LaTeX，而不是可读公式。

因此：

- **MATH-1 不得视为完成。** `af9056b` 的测试绿不能覆盖 Captain 实机 Word。
- **不得写可交付的 takeaway 契约**（尤其不得写「共享公式门已可复用 MATH-1」或「preview === download 可按已修好的公式落地」）。
- 公式门状态 = **BLOCKED / OPEN**，直到有人在 Captain 同路径的 live `.docx` 里看见可读公式。

乱码形态以 Captain 实机为准（转义 `\{\}` / `\_`、裸 `\ln` / `_{i}`、残留 `$…$`，或其它）。本笔记没有那份 `.docx` 的逐字节摘录。

---

## Why unit green is not live Word

`convert_docx` **优先走 pandoc**（本机有 `pandoc` 时）。MATH-1 关键断言把 `shutil.which` 打成 `None`，只测 OOXML fallback（`_strip_tex_markup` + `_w_omath_paragraph`）。

| 路径 | 谁跑 | MATH-1 测了吗 |
| --- | --- | --- |
| `pandoc --from=latex --to=docx` | 装了 pandoc 的实机（Captain 很大概率在这条） | **否** |
| `_write_simple_docx` OMML fallback | 无 pandoc / pandoc 失败 | 是（`which is None`） |

开放结论：测试过的门和 Captain 打开的文件可能不是同一条管道。在 live pandoc `.docx` 对上之前，不能说「公式已 normalize」。

---

## Open questions

1. **Captain 看见的精确垃圾是什么？** `\{\}ln` / `\_`、`\textbackslash\{\}`、未渲染 `\ln(\text{homicide}_{i})`、残留 `$` / `$$`，还是 Word 把 OMML 画成字面 TeX？没有实机 `word/document.xml` 摘录，修哪一层都是猜。
2. **那份 `.docx` 是不是 `af9056b` 刚导出的？** 旧会话缓存、旧 runner 工件、或未包含 MATH-1 的后端都会让「基线已修」和「打开的文件」对不上。
3. **pandoc 入口有没有公式门？** live 路径把 `latex_source` 直接交给 pandoc。MATH-1 的 unicode / OMML 清洗不经过这条。pandoc 是把数学写成 OMML，还是把转义/原文 TeX 写进 BodyText？
4. **`latex_source` 在 live generate 里是否仍被双转义？** MATH-1 修了 `markdown_to_latex` 对 `$$…$$` 的按行转义。其它形态（`\[…\]`、`equation`/`align`、跨行未闭合 `$`、表单元格里的 `_`、标题里的 `_`）是否仍进 `_escape_tex_plain`，从而变成 `\_` / `\{`？
5. **Captain Word 是 Desktop / Online / WPS / LibreOffice？** 同一份 OOXML 在不同阅读器里，OMML 和字面 TeX 的观感不同。乱码是文件内容还是阅读器？
6. **PDF 与成稿预览是否同一失败？** 未在本切片验证。预览目前铺章节 markdown（含 `$` / `$$`）。在 Word 可读之前，不要订 preview === download。
7. **乱码出在哪一章、哪一条公式？** 测试锚是 methods 的 `ln(homicide_i)=β_0`。Captain 打开的若是 OLS 生成稿（别的因变量、表、行内 `$i$`），失败面可能更宽。
8. **「可编辑 Word」在公式乱码时没有验收意义。** 页即图不能当修法，但先要证明文本/OMML 路径在实机可读。

---

## Out of scope for this note

- 不实现 PDF、成稿预览、下载栏、公式渲染修复。
- 不把四入口（PDF / Word / Stata / R）写成已冻结契约。
- 不做期刊模板、Tabs 落地、DiD 变体、首页重设计。
- 不打开 Pull Request。

Takeaway pack 的其余意向（所见即所下、四入口、Word 可编辑 / PDF 可读 / OLS 代码对齐）在公式门 OPEN 期间都不是可交付合同。先有 Captain 实机 Word 可读公式，再另写契约。
