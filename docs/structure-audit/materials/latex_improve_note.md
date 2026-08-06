# LaTeX PDF 美化说明（runtime/latex_pdf.py）

日期：2026-08-06

## 改了什么

中文学术 PDF 生成器（`runtime/latex_pdf.py`）一轮加固：字体、章节、摘要、粗体转义、表格保持 booktabs。

## 要点

1. **中文字体回退**  
   `fontset=none` + 运行时 `fc-list` 探测，主字体优先 `Songti SC` → `STSong` → `PingFang SC`；粗体 `PingFang SC`，斜体 `Kaiti SC`；无衬线/等宽用 `PingFang SC`。

2. **章节**  
   - `##` → `\section`，`###` → `\subsection`，`####` → `\subsubsection`  
   - 剥掉标题里已有的「一、 / （一） / 1.」避免与 ctex 中文编号重复  
   - ctex：节号 `一、二、…`，小节 `（一）（二）…`  
   - `## 摘要` 不再进正文（只进 abstract 环境）  
   - 支持引用块、水平线、pipe 表 → booktabs

3. **摘要**  
   从 `## 摘要` 抽取；可选 `关键词：` 行单独加粗输出；`\abstractname = 摘 要`。

4. **粗体 / 行内**  
   先占位保护 `**bold**` / `*em*` / `` `code` `` / 链接 / 数学，再 escape TeX 特殊字符，最后回填。修复旧实现「escape 后粗体丢失」的 bug。

5. **列表**  
   修正 enumerate 却 `\end{itemize}` 的 bug；item/enumerate 分开收尾。

6. **源 md 容错**  
   若整篇被包在 ` ```markdown ... ``` ` 里，先 unwrap 再转。

## 重编译

- 源：`Manuscripts/generated/parent_education_wage_full_pipeline_paper.md`  
  （已去掉误包的外层 fence）
- 产物：`Submissions/parent_education_wage_loop_paper.pdf`（6 页）  
- 中间：`Submissions/latex_build/parent_education_wage/parent_education_wage_loop_paper.tex`  
- 引擎：xelatex，2 pass，ok

## 调用

```bash
python3 -c "from pathlib import Path; from runtime.latex_pdf import render_markdown_paper_to_pdf; print(render_markdown_paper_to_pdf(Path('Manuscripts/generated/parent_education_wage_full_pipeline_paper.md')).to_dict())"
```

连续环 `_package` 仍走同一入口，无需改编排。
