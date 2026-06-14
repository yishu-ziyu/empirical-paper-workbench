# 华侨大学本科论文 LaTeX 工作流固化

更新时间：2026-05-17

## 当前状态

这套工作流已能把论文 Markdown 套入华侨大学本科毕业论文与经济与金融学院模板，并编译出可阅读的 A4 PDF。当前效果可以作为后续精修的基础版本，但还没有进入最终提交级排版。

当前稳定产物：

- 项目归档：`04_编译输出/论文v2.1_华侨大学模板版.pdf`
- 生成脚本：`02_latex模板/scripts/build_paper_from_markdown.py`
- 生成 LaTeX：`04_编译输出/论文v2.1_华侨大学模板版.tex`
- 编译日志：`04_编译输出/论文v2.1_华侨大学模板版.log`

## 核心原则

1. Markdown 是正文内容源，不直接改 PDF。
2. 学校 PDF 与学院 Word 模板是格式规范源。
3. 已提交 PDF 只能作为视觉参考源，不作为唯一规范源，因为其中也可能存在字体、字号和样式不统一的问题。
4. LaTeX 负责最终排版层：封面、诚信承诺书、摘要、目录、正文、图表、公式、参考文献和附录。
5. 所有修订都要可复现：脚本、生成的 `.tex`、`.log` 和 PDF 都要归档。

## 输入材料

正式规范材料：

- `00_原始材料/华侨大学本科毕业设计（论文）撰写要求及格式规范.pdf`
- `00_原始材料/经济与金融学院本科毕业论文格式模板.docx`

当前正文材料：

- `/Users/mahaoxuan/Desktop/学术灵感项目_2026-04-07/final/04_paper/论文v2.1_完整版.md`

参考对照材料：

- `00_原始材料/系统提交正本_工业机器人与劳动者重新配置_初稿.pdf`

## 固化流程

### 1. 归档规范材料

把学校正式 PDF、学院 Word 模板和可参考的历史 PDF 放入 `00_原始材料/`，并在 `00_原始材料/材料登记.md` 中注明用途。

### 2. 抽取格式规则

从学校 PDF 抽取硬性规则：

- A4 页面。
- 封面、诚信承诺书、摘要、目录、正文、参考文献等结构。
- 图题在图下，表题在表上。
- 正文、摘要、目录、参考文献的字号和字体要求。

从学院 Word 模板抽取实际落地规则：

- 页面边距。
- 正文字体、字号、行距、首行缩进。
- 页眉页脚。
- 目录样式。
- 表格、图题、标题层级的实际呈现方式。

### 3. 校准模板骨架

模板入口是：

- `02_latex模板/main.tex`

已验证的基础编译路径是：

```bash
xelatex -interaction=nonstopmode -halt-on-error main.tex
xelatex -interaction=nonstopmode -halt-on-error main.tex
```

在 macOS 上当前可靠字体配置：

- `ctexrep`
- `fontset=none`
- `Songti SC`
- `Heiti SC`
- `Times New Roman`

### 4. 从 Markdown 生成论文版 PDF

当前真实论文入口脚本是：

```bash
cd /Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/Manuscripts/templates/华侨大学本科论文LaTeX模板_2026-05-17/02_latex模板
python3 scripts/build_paper_from_markdown.py
```

脚本职责：

- 读取论文 Markdown。
- 抽取标题、中文摘要、英文摘要、关键词、正文、参考文献和附录。
- 将 Markdown 转为 LaTeX。
- 复制校徽、校名和论文图表资源。
- 套用 HQU 模板前置页和正文样式。
- 跑两遍 `xelatex`。
- 默认输出构建目录 PDF：`02_latex模板/build/paper_v21_hqu/paper_v21_hqu.pdf`，并保留生成的 `.tex`、`.log` 和构建目录。
- 如需额外输出项目归档 PDF 或桌面 PDF，可显式传入 `--output`。在当前 Codex 沙箱里，若 Python 复制被 macOS 权限拦截，使用 `cp` 复制构建目录中的 PDF。

### 5. 编译验证

每次生成后至少检查：

```bash
pdfinfo build/paper_v21_hqu/paper_v21_hqu.pdf
rg -n "^!|LaTeX Error|Undefined control sequence|Emergency stop|Fatal error|undefined references|There were undefined" build/paper_v21_hqu/paper_v21_hqu.log
```

合格标准：

- PDF 是 A4。
- 编译日志没有真正 LaTeX 错误。
- 目录、摘要、正文、图表和参考文献都能进入 PDF。
- 生成文件全部可追踪。

### 6. 后续精修

精修不直接改生成的 `.tex`。应优先改：

- `02_latex模板/scripts/build_paper_from_markdown.py`
- 模板规则。
- Markdown 源文档中确实属于内容结构的问题。

如果只是排版问题，应尽量在 LaTeX 模板层解决。

## 目前已知边界

- Pandoc 自动转换的 Markdown 表格还没有完全达到毕业论文三线表标准。
- 长表格会触发跨页、列宽和 overfull 提示。
- 图表标题目前仍有部分来自 Markdown 文本，语义化程度不够。
- 公式还需要编号和交叉引用规范。
- 已提交 PDF 的视觉效果有参考价值，但其中也存在字体、字号不统一问题，不能盲目照搬。

## 后续模板库方向

这套流程后续可以扩展成网站或模板库。建议每个模板至少沉淀以下字段：

- 机构名称。
- 学院或部门名称。
- 模板适用对象。
- 原始 Word/PDF 规范文件。
- 页面规则。
- 字体与字号规则。
- 标题层级规则。
- 图表规则。
- 公式规则。
- 参考文献规则。
- 编译引擎和字体依赖。
- 示例输入 Markdown。
- 示例输出 PDF。
- 已知缺陷和版本记录。
