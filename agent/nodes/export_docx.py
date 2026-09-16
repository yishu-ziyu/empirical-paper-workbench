"""export_docx 节点 (T-10).

把 6 章内容填充到 LaTeX 模板，编译生成 PDF + docx。

流程：
1. 从 ``state['title_chapter']`` 提取标题，从 ``state['body_chapters']`` 提取正文章节
2. 选择模板（``state['export_template']``，默认 ``cn_journal``）
3. Jinja2 渲染模板 → LaTeX 源码
4. ``compile_pdf`` 调 ``latexmk -xelatex`` 生成 PDF（subprocess）
5. ``convert_docx`` 优先 ``pandoc``（Word-only ``\\mathrm{Ident}`` →
   ``\\text{Ident}`` so Mac Word keeps one ``m:t`` run）；缺失或失败时写最小 OOXML ``.docx``
6. 返回 ``{"latex_source", "pdf_path", "docx_path", "degraded"}``
   ``latex_source`` / ``paper.tex`` / ``compile_pdf`` stay on literature
   ``\\mathrm``; the rewrite is only the Word/pandoc input.

降级策略：``latexmk`` 不可用时 ``pdf_path=None``。docx 在 pandoc 缺失时
仍写 OOXML，但 ``degraded=True``。仅当转换完全失败时 ``docx_path=None``。
``latex_source`` 始终可用。测试通过
``monkeypatch.setattr("nodes.export_docx.compile_pdf", fake)`` 替换编译函数，
故 ``compile_pdf`` / ``convert_docx`` 必须是模块级函数。
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path
from typing import Any, List, Optional, Tuple

# macOS BasicTeX/Full TeX 安装在 /Library/TeX/texbin，uvicorn 进程可能 PATH 不含此目录
_TEX_BIN = "/Library/TeX/texbin"
if os.path.isdir(_TEX_BIN) and _TEX_BIN not in os.environ.get("PATH", ""):
    os.environ["PATH"] = _TEX_BIN + os.pathsep + os.environ.get("PATH", "")

from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from ..engine.outline_bodies import chapter_has_body
from ..nodes.estimate import looks_like_coef_table, splice_missing_table_rows
from ..protocols import ExportDocxOutput
from ..state import EconPaperState

# 模板目录：agent/templates/
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"

# 支持的模板名（与文件名去掉 .tex 一致）
TEMPLATE_NAMES = {
    "cn_journal",
    "undergraduate",
    "master_thesis",
    "english_submission",
}

# Product / DirectionForm short names → canonical TEMPLATE_NAMES.
# Sample write loop and MethodSelector send these aliases.
TEMPLATE_ALIASES = {
    "undergrad": "undergraduate",
    "master": "master_thesis",
    "en_submission": "english_submission",
}


def normalize_template(template_name: str) -> str:
    """Map FE aliases onto canonical template files. Canonical names pass through."""
    return TEMPLATE_ALIASES.get(template_name, template_name)

# Jinja2 环境：不转义（LaTeX 源码原样输出），保留尾换行
_env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=False,
    keep_trailing_newline=True,
    trim_blocks=False,
    lstrip_blocks=False,
)


# ---------------------------------------------------------------------------
# 纯函数：从 state.title_chapter / state.body_chapters 提取 title / sections
# ---------------------------------------------------------------------------
def _extract_title(title_chapter: Any) -> str:
    """从 title_chapter 提取干净的标题文本。

    优先取 ``title`` 字段（非 ``\\title{...}`` 形式）；
    否则从 ``content`` 里解析 ``\\title{...}``；都没有则返回 "Untitled"。
    """
    if not isinstance(title_chapter, dict):
        return "Untitled"
    raw_title = (title_chapter.get("title") or "").strip()
    if raw_title and not raw_title.startswith("\\title"):
        return raw_title
    content = title_chapter.get("content") or ""
    m = re.search(r"\\title\{([^}]*)\}", content)
    if m:
        return m.group(1).strip()
    return "Untitled"


def _escape_tex_plain(text: str) -> str:
    """Escape LaTeX specials. `%` must not start a comment (truncates `在 1% …`)."""
    return (
        text.replace("\\", r"\textbackslash{}")
        .replace("&", r"\&")
        .replace("%", r"\%")
        .replace("#", r"\#")
        .replace("_", r"\_")
        .replace("{", r"\{")
        .replace("}", r"\}")
        .replace("~", r"\textasciitilde{}")
        .replace("^", r"\textasciicircum{}")
        .replace("$", r"\$")
    )


_CITE_RE = re.compile(r"\\(cite|ref|eqref)\{[^}]*\}")
# Multiline ``$$…$$`` must stay one chunk. Line-by-line ``[^$]+`` left the
# interior of a display block (``\ln``, ``_{i}``) to ``_escape_tex_plain``.
_MATH_BOLD_RE = re.compile(
    r"(\$\$[\s\S]+?\$\$|\$[^$\n]+\$|\*\*[^*]+\*\*)"
)
_EQ_ENV_OPEN_RE = re.compile(r"^\\begin\{equation\*?\}")
_EQ_ENV_CLOSE_RE = re.compile(r"\\end\{equation\*?\}$")
_MATH_MACROS: Tuple[Tuple[str, str], ...] = (
    ("varepsilon", "ε"),
    ("rightarrow", "→"),
    ("Rightarrow", "⇒"),
    ("epsilon", "ε"),
    ("partial", "∂"),
    ("approx", "≈"),
    ("infty", "∞"),
    ("cdot", "·"),
    ("times", "×"),
    ("alpha", "α"),
    ("beta", "β"),
    ("gamma", "γ"),
    ("delta", "δ"),
    ("theta", "θ"),
    ("lambda", "λ"),
    ("sigma", "σ"),
    ("omega", "ω"),
    ("Delta", "Δ"),
    ("Sigma", "Σ"),
    ("Omega", "Ω"),
    ("leq", "≤"),
    ("geq", "≥"),
    ("neq", "≠"),
    ("mu", "μ"),
    ("phi", "φ"),
    ("psi", "ψ"),
    ("pi", "π"),
    ("tau", "τ"),
    ("rho", "ρ"),
    ("pm", "±"),
    ("ln", "ln"),
    ("log", "log"),
    ("exp", "exp"),
    ("max", "max"),
    ("min", "min"),
    ("sum", "∑"),
    ("prod", "∏"),
)


def _escape_tex_text(text: str) -> str:
    """Escape markdown prose. Keep ``$…$`` / ``$$…$$`` and ``\\cite``/``\\ref``/``\\eqref``.

    Bodies are markdown-only: unmatched ``$`` is escaped so it cannot open math.
    Already-emitted cite/ref commands are held out so escaping does not break them.
    """
    held: List[str] = []

    def _hold(match: re.Match[str]) -> str:
        held.append(match.group(0))
        return f"\x00CITE{len(held) - 1}\x00"

    protected = _CITE_RE.sub(_hold, text)
    chunks = _MATH_BOLD_RE.split(protected)
    out: List[str] = []
    for chunk in chunks:
        if chunk.startswith("$$") and chunk.endswith("$$") and len(chunk) >= 4:
            out.append(chunk)
        elif (
            chunk.startswith("$")
            and chunk.endswith("$")
            and len(chunk) >= 2
            and not chunk.startswith("$$")
        ):
            out.append(chunk)
        elif chunk.startswith("**") and chunk.endswith("**") and len(chunk) >= 4:
            out.append(r"\textbf{" + _escape_tex_plain(chunk[2:-2]) + "}")
        else:
            out.append(_escape_tex_plain(chunk))
    merged = "".join(out)
    for i, original in enumerate(held):
        merged = merged.replace(f"\x00CITE{i}\x00", original)
    return merged


def _is_display_math_open(stripped: str) -> bool:
    return (
        stripped == "$$"
        or stripped.startswith("$$")
        or stripped.startswith("\\[")
        or bool(_EQ_ENV_OPEN_RE.match(stripped))
    )


def _is_display_math_one_line(stripped: str) -> bool:
    if stripped.startswith("$$") and stripped.endswith("$$") and len(stripped) > 2:
        return True
    if stripped.startswith("\\[") and stripped.endswith("\\]") and len(stripped) > 3:
        return True
    if _EQ_ENV_OPEN_RE.match(stripped) and _EQ_ENV_CLOSE_RE.search(stripped):
        return True
    return False


def _is_display_math_close(stripped: str) -> bool:
    return (
        stripped == "$$"
        or stripped.endswith("$$")
        or stripped.endswith("\\]")
        or bool(_EQ_ENV_CLOSE_RE.search(stripped))
    )


def _is_md_table_line(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith("|") and stripped.count("|") >= 2


def _is_md_table_sep(line: str) -> bool:
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", c or "") for c in cells)


def _md_table_to_latex(rows: List[str]) -> str:
    parsed: List[List[str]] = []
    for row in rows:
        if _is_md_table_sep(row):
            continue
        cells = [c.strip() for c in row.strip().strip("|").split("|")]
        if cells:
            parsed.append(cells)
    if not parsed:
        return ""
    ncol = max(len(r) for r in parsed)
    lines = [r"\begin{tabular}{" + "l" * ncol + "}", r"\toprule"]
    for i, cells in enumerate(parsed):
        padded = cells + [""] * (ncol - len(cells))
        lines.append(" & ".join(_escape_tex_text(c) for c in padded) + r" \\")
        if i == 0:
            lines.append(r"\midrule")
    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    return "\n".join(lines)


def markdown_to_latex(text: str, section_title: str = "") -> str:
    """Turn chapter markdown into LaTeX so ATX hashes are not BodyText.

    `# 主结果` / `## 模型设定` become subsections. A heading that repeats
    the chapter ``\\section`` title is dropped. `%` is escaped so
    ``在 1% 水平上`` is not cut off by a TeX comment.
    """
    source = (text or "").replace("\r\n", "\n")
    lines = source.split("\n")
    out: List[str] = []
    i = 0
    heading_re = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
    while i < len(lines):
        raw = lines[i]
        heading = heading_re.match(raw.strip())
        if heading:
            title = heading.group(2).strip()
            if section_title and title == section_title:
                i += 1
                continue
            level = len(heading.group(1))
            if level == 1:
                cmd = "subsection*"
            elif level >= 3:
                cmd = "subsubsection"
            else:
                cmd = "subsection"
            out.append(f"\\{cmd}{{{_escape_tex_text(title)}}}")
            i += 1
            continue
        if _is_md_table_line(raw) or _is_md_table_sep(raw):
            block: List[str] = []
            while i < len(lines) and (
                _is_md_table_line(lines[i]) or _is_md_table_sep(lines[i])
            ):
                block.append(lines[i])
                i += 1
            converted = _md_table_to_latex(block)
            if converted:
                out.append(converted)
            continue
        stripped = raw.strip()
        if _is_display_math_open(stripped):
            # Keep the whole display block as TeX. Escaping each line turns
            # ``\ln`` / ``_{i}`` into ``\textbackslash\{\}ln`` / ``\_\{i\}``.
            block = [raw]
            i += 1
            if not _is_display_math_one_line(stripped):
                while i < len(lines):
                    block.append(lines[i])
                    end = lines[i].strip()
                    i += 1
                    if _is_display_math_close(end):
                        break
            out.append("\n".join(block))
            continue
        if not raw.strip():
            out.append("")
            i += 1
            continue
        out.append(_escape_tex_text(raw))
        i += 1
    return "\n".join(out)


def _ordered_body_chapters(
    body_chapters: List[Any], state: Optional[dict] = None
) -> List[dict]:
    """Walk outline order when present so export is six-chapter, not intro-only."""
    chapters = [ch for ch in (body_chapters or []) if isinstance(ch, dict)]
    outline = (state or {}).get("outline") or [] if isinstance(state, dict) else []
    types = [
        str(entry.get("type") or "").strip()
        for entry in outline
        if isinstance(entry, dict) and str(entry.get("type") or "").strip()
    ]
    if not types:
        return chapters
    by_type: dict[str, dict] = {}
    extras: List[dict] = []
    for ch in chapters:
        chapter_type = str(ch.get("type") or "").strip()
        if chapter_type and chapter_type not in by_type:
            by_type[chapter_type] = ch
        elif not chapter_type:
            extras.append(ch)
    ordered = [by_type[chapter_type] for chapter_type in types if chapter_type in by_type]
    seen = set(types)
    ordered.extend(
        ch
        for ch in chapters
        if str(ch.get("type") or "").strip()
        and str(ch.get("type") or "").strip() not in seen
    )
    ordered.extend(extras)
    return ordered


def _extract_sections(
    body_chapters: List[Any], state: Optional[dict] = None
) -> List[dict]:
    """正文章节 → ``{title, content}``. Skip empty outline pads.

    Empty ``{}`` slots from generate_chapter's 6-way pad used to become
    ``Untitled section`` Heading1s. Heading-only drafts are also dropped.
    Only chapters with body text are kept. Content is markdown→LaTeX so
    leftover ``#`` / ``##`` do not survive.
    """
    state = state or {}
    spec = state.get("main_specification") if isinstance(state, dict) else {}
    estimate = state.get("estimate") if isinstance(state, dict) else {}
    if not isinstance(spec, dict):
        spec = {}
    if not isinstance(estimate, dict):
        estimate = {}
    sections: List[dict] = []
    for ch in _ordered_body_chapters(body_chapters, state):
        if not chapter_has_body(ch):
            continue
        content = ch.get("content") or ""
        title = (ch.get("title") or "").strip()
        if not title:
            # Body with no title: keep the text. Prefer type, else 未命名.
            title = str(ch.get("type") or "").strip() or "未命名"
        chapter_type = str(ch.get("type") or "")
        if chapter_type == "results" or looks_like_coef_table(content):
            content = splice_missing_table_rows(content, spec, estimate)
        sections.append(
            {
                "title": _escape_tex_text(title),
                "content": markdown_to_latex(content, section_title=title),
            }
        )
    return sections


# ---------------------------------------------------------------------------
# ADR-0009: references_list → \begin{thebibliography} 渲染
# ---------------------------------------------------------------------------
def _render_bibliography(references_list: List[Any]) -> str:
    """把 references_list 渲染为 LaTeX ``thebibliography`` 环境。

    - 空列表返回空字符串（调用方据此决定是否插入）；
    - 每条 ``\\bibitem{[index]} text``；
    - ``thebibliography{N}`` 的 N 取 ``len(references_list)``（最宽编号占位）。
    """
    if not references_list:
        return ""
    lines: List[str] = []
    n = len(references_list)
    lines.append(f"\\begin{{thebibliography}}{{{n}}}")
    for ref in references_list:
        if not isinstance(ref, dict):
            continue
        idx = ref.get("index", 0)
        text = ref.get("text", "")
        lines.append(f"\\bibitem{{[{idx}]}} {text}")
    lines.append("\\end{thebibliography}")
    return "\n".join(lines)


def _append_bibliography(tex_source: str, references_list: List[Any]) -> str:
    """在 ``\\end{document}`` 前插入 thebibliography 环境。

    references_list 为空时原样返回 tex_source。
    """
    bib = _render_bibliography(references_list)
    if not bib:
        return tex_source
    if "\\end{document}" in tex_source:
        return tex_source.replace("\\end{document}", bib + "\n\\end{document}")
    # 无 \end{document} 兜底：直接追加
    return tex_source + "\n" + bib + "\n"


# ---------------------------------------------------------------------------
# render_template（纯函数，易测）
# ---------------------------------------------------------------------------
def render_template(
    template_name: str,
    title: str,
    author: str,
    chapters: List[dict],
    abstract: Optional[str] = None,
    date: str = "",
) -> str:
    """用 Jinja2 把 title/author/chapters 填进 ``{template_name}.tex``。

    未知模板名抛 ``ValueError``。``undergrad`` 等产品别名先归一化。
    """
    template_name = normalize_template(template_name)
    if template_name not in TEMPLATE_NAMES:
        raise ValueError(
            f"Unknown template: {template_name!r}; "
            f"expected one of {sorted(TEMPLATE_NAMES)}"
        )
    try:
        tmpl = _env.get_template(f"{template_name}.tex")
    except TemplateNotFound as exc:
        raise ValueError(f"Template not found: {template_name}") from exc
    return tmpl.render(
        title=title,
        author=author,
        chapters=chapters,
        abstract=abstract,
        date=date,
    )


# ---------------------------------------------------------------------------
# 编译函数（subprocess，可被测试 monkeypatch 替换）
# ---------------------------------------------------------------------------
def compile_pdf(tex_source: str, output_dir: str) -> Optional[str]:
    """编译 PDF。

    优先用 ``latexmk -xelatex``（自动多次跑解析引用）；不可用时
    fallback 到直接调 ``xelatex`` 两次（第一次生成 .aux，第二次解析引用）。

    成功返回 PDF 绝对路径字符串；两者都不可用或编译失败时返回 None。
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    tex_path = out / "paper.tex"
    tex_path.write_text(tex_source, encoding="utf-8")

    # 首选 latexmk
    if shutil.which("latexmk") is not None:
        try:
            subprocess.run(
                [
                    "latexmk",
                    "-xelatex",
                    "-no-shell-escape",
                    "-interaction=nonstopmode",
                    "-halt-on-error",
                    "-outdir",
                    str(out),
                    str(tex_path),
                ],
                check=True,
                capture_output=True,
                timeout=120,
            )
            pdf_path = out / "paper.pdf"
            if pdf_path.exists():
                return str(pdf_path)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            pass  # fall through to xelatex

    # Fallback: 直接调 xelatex（跑两次解析交叉引用）
    if shutil.which("xelatex") is None:
        return None
    try:
        for _ in range(2):
            subprocess.run(
                [
                    "xelatex",
                    "-no-shell-escape",
                    "-interaction=nonstopmode",
                    "-halt-on-error",
                    "-output-directory",
                    str(out),
                    str(tex_path),
                ],
                check=True,
                capture_output=True,
                timeout=120,
                cwd=str(out),
            )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return None

    pdf_path = out / "paper.pdf"
    return str(pdf_path) if pdf_path.exists() else None


def _xml_escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _restore_overescaped_tex(text: str) -> str:
    """Undo ``\\textbackslash{}`` + ``\\{\\}`` / ``\\_`` double-escaping."""
    text = text.replace("\\textbackslash\\{\\}", "\\")
    text = text.replace("\\textbackslash{}", "\\")
    text = text.replace("\\{\\}", "\\")
    text = text.replace("\\_", "_")
    text = text.replace("\\{", "{")
    text = text.replace("\\}", "}")
    text = text.replace("\\$", "$")
    text = text.replace("\\#", "#")
    return text


def _apply_math_macros(text: str, *, unwrap_braces: bool = False) -> str:
    """Turn TeX math macros into readable unicode. Leaves ``\\textbf`` alone."""
    text = re.sub(
        r"\\(?:text|mathrm|operatorname|mathbf|mathit)\*?\{([^{}]*)\}",
        r"\1",
        text,
    )
    text = re.sub(r"\\(?:left|right)\s*", "", text)
    text = re.sub(r"\\frac\{([^{}]+)\}\{([^{}]+)\}", r"(\1)/(\2)", text)
    text = re.sub(r"\\hat\{([^{}]+)\}", lambda m: m.group(1) + "\u0302", text)
    text = re.sub(r"\\bar\{([^{}]+)\}", lambda m: m.group(1) + "\u0304", text)
    text = re.sub(r"\\tilde\{([^{}]+)\}", lambda m: m.group(1) + "\u0303", text)
    text = (
        text.replace("\\qquad", " ")
        .replace("\\quad", " ")
        .replace("\\,", " ")
        .replace("\\;", " ")
        .replace("\\:", " ")
    )
    for name, repl in sorted(_MATH_MACROS, key=lambda kv: -len(kv[0])):
        text = re.sub(rf"\\{re.escape(name)}(?![a-zA-Z])", repl, text)
    text = re.sub(r"_\{([^{}]+)\}", r"_\1", text)
    text = re.sub(r"\^\{([^{}]+)\}", r"^\1", text)
    if unwrap_braces:
        text = re.sub(r"\{([^{}]+)\}", r"\1", text)
        text = re.sub(r"[ \t]+", " ", text).strip()
    return text


def _render_tex_math(text: str) -> str:
    """Unwrap ``$…$`` / ``$$…$$`` and render the interior as unicode."""

    def _display(match: re.Match[str]) -> str:
        return _apply_math_macros(match.group(1), unwrap_braces=True)

    text = re.sub(r"\$\$(.+?)\$\$", _display, text, flags=re.S)
    text = re.sub(r"\\\[(.+?)\\\]", _display, text, flags=re.S)
    text = re.sub(
        r"\\begin\{equation\*?\}(.+?)\\end\{equation\*?\}",
        _display,
        text,
        flags=re.S,
    )
    text = re.sub(
        r"\$([^$\n]+)\$",
        lambda m: _apply_math_macros(m.group(1), unwrap_braces=True),
        text,
    )
    return text


def _strip_tex_markup(text: str) -> str:
    """Drop TeX commands but keep brace prose (\\textbf{结果} → 结果).

    Math is rendered to unicode (``\\ln(\\text{homicide}_{i})`` →
    ``ln(homicide_i)``) so Word never shows ``\\{\\}ln`` / ``\\_``.
    """
    text = re.sub(r"(?<!\\)%.*", "", text)
    text = _restore_overescaped_tex(text)
    text = _render_tex_math(text)
    text = re.sub(r"\\(?:begin|end)\{[^}]+\}", "", text)
    text = re.sub(r"\\(?:maketitle|tableofcontents)\b", "", text)
    text = re.sub(
        r"\\(?:label|cite|citep|citet|ref|pageref|footnote)\*?\{[^}]*\}",
        "",
        text,
    )
    text = _apply_math_macros(text, unwrap_braces=False)
    keep_arg = re.compile(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?\{([^{}]*)\}")
    prev = None
    while prev != text:
        prev = text
        text = keep_arg.sub(r"\1", text)
    text = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?", "", text)
    return (
        text.replace("\\%", "%")
        .replace("\\&", "&")
        .replace("\\_", "_")
        .replace("\\{", "{")
        .replace("\\}", "}")
        .strip()
    )


def _prelude_section(raw: str) -> Optional[dict]:
    """Pre-\\section body (abstract / leftover) as a docx section."""
    if not raw or not raw.strip():
        return None
    abs_m = re.search(
        r"\\begin\{abstract\}(.*?)\\end\{abstract\}", raw, flags=re.S | re.I
    )
    if abs_m:
        content = _strip_tex_markup(abs_m.group(1))
        leftover = _strip_tex_markup(raw[: abs_m.start()] + raw[abs_m.end() :])
        if leftover:
            content = f"{content}\n{leftover}" if content else leftover
        if content:
            return {"title": "摘要", "content": content}
        return None
    content = _strip_tex_markup(raw)
    if not content:
        return None
    return {"title": "摘要", "content": content}


def _sections_from_tex(tex_source: str) -> Tuple[str, List[dict]]:
    title_m = re.search(r"\\title\{([^}]*)\}", tex_source or "")
    title = title_m.group(1).strip() if title_m else "Untitled"
    body = tex_source or ""
    if "\\begin{document}" in body:
        body = body.split("\\begin{document}", 1)[1]
    if "\\end{document}" in body:
        body = body.split("\\end{document}", 1)[0]
    parts = re.split(r"\\section\{([^}]*)\}", body)
    sections: List[dict] = []
    prelude = _prelude_section(parts[0] if parts else "")
    if prelude:
        sections.append(prelude)
    for i in range(1, len(parts), 2):
        content = parts[i + 1] if i + 1 < len(parts) else ""
        sections.append(
            {
                "title": parts[i].strip() or "Untitled section",
                "content": _strip_tex_markup(content),
            }
        )
    return title, sections


def _w_paragraph(text: str, *, heading: bool = False) -> str:
    style = "<w:pPr><w:pStyle w:val=\"Heading1\"/></w:pPr>" if heading else ""
    return (
        "<w:p>"
        f"{style}"
        "<w:r><w:t xml:space=\"preserve\">"
        f"{_xml_escape(text)}"
        "</w:t></w:r></w:p>"
    )


def _is_readable_equation_line(line: str) -> bool:
    """Standalone regression line → Word OMML, not a BodyText dump."""
    stripped = line.strip()
    if not stripped or "=" not in stripped:
        return False
    if re.search(r"[\u4e00-\u9fff]", stripped):
        return False
    return bool(re.search(r"[α-ωΑ-Ωβ]|_|\bln\b|\blog\b|\bexp\b", stripped))


def _w_omath_paragraph(text: str) -> str:
    return (
        "<w:p>"
        "<w:pPr><w:jc w:val=\"center\"/></w:pPr>"
        "<m:oMathPara><m:oMath><m:r>"
        f"<m:t xml:space=\"preserve\">{_xml_escape(text.strip())}</m:t>"
        "</m:r></m:oMath></m:oMathPara>"
        "</w:p>"
    )


def _write_simple_docx(path: Path, title: str, sections: List[dict]) -> None:
    """Write a minimal OOXML docx. No pandoc / python-docx required."""
    paras = [_w_paragraph(title or "Untitled", heading=True)]
    for section in sections:
        paras.append(_w_paragraph(str(section.get("title") or ""), heading=True))
        body = str(section.get("content") or "")
        for line in body.splitlines() or [""]:
            if _is_readable_equation_line(line):
                paras.append(_w_omath_paragraph(line))
            else:
                paras.append(_w_paragraph(line))
    document_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'
        ' xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math">'
        f"<w:body>{''.join(paras)}<w:sectPr/></w:body></w:document>"
    )
    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/word/document.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
        "</Types>"
    )
    rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
        'Target="word/document.xml"/>'
        "</Relationships>"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", rels)
        zf.writestr("word/document.xml", document_xml)


# Pandoc maps ``\mathrm{Homicide}`` to letter-split OMML (each letter its
# own ``m:t``). Mac Word then shows a blank equation. ``\text{Homicide}``
# stays one run. Literature source / PDF keep ``\mathrm``.
_MATHRM_IDENT_RE = re.compile(r"\\mathrm\*?\{([^{}]*)\}")


def rewrite_mathrm_to_text_for_word(tex: str) -> str:
    """Word/docx-only: ``\\mathrm{Ident}`` → ``\\text{Ident}``.

    Do not use this on the PDF/xelatex source. Nested braces are left
    alone (``[^{}]*``) so we never rewrite past a math group.
    """
    return _MATHRM_IDENT_RE.sub(r"\\text{\1}", tex or "")


def convert_docx(tex_source: str, output_dir: str) -> Optional[str]:
    """tex → docx. Prefer pandoc; if missing or failing, write a simple OOXML file.

    Pandoc input is a Word-only copy with ``\\mathrm{Ident}`` rewritten
    to ``\\text{Ident}``. ``paper.tex`` stays the original literature
    source so the PDF/xelatex path is not mutated.

    成功返回 docx 绝对路径；pandoc 与 fallback 都失败时返回 None。
    """
    convert_docx.used_ooxml_fallback = False
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    tex_path = out / "paper.tex"
    tex_path.write_text(tex_source, encoding="utf-8")
    word_tex_path = out / "paper_word.tex"
    word_tex_path.write_text(
        rewrite_mathrm_to_text_for_word(tex_source), encoding="utf-8"
    )
    docx_path = out / "paper.docx"

    if shutil.which("pandoc") is not None:
        try:
            subprocess.run(
                [
                    "pandoc",
                    str(word_tex_path),
                    "-o",
                    str(docx_path),
                    "--from=latex",
                    "--to=docx",
                ],
                check=True,
                capture_output=True,
                timeout=120,
            )
            if docx_path.exists() and docx_path.stat().st_size > 0:
                convert_docx.used_ooxml_fallback = False
                return str(docx_path)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            pass

    try:
        title, sections = _sections_from_tex(tex_source)
        _write_simple_docx(docx_path, title, sections)
    except OSError:
        return None
    convert_docx.used_ooxml_fallback = True
    return str(docx_path) if docx_path.exists() else None


# ---------------------------------------------------------------------------
# 节点入口
# ---------------------------------------------------------------------------
def export_docx(state: EconPaperState) -> ExportDocxOutput:
    """把 6 章内容填充到 LaTeX 模板，编译生成 PDF + docx。

    返回::

        {
            "latex_source": str,          # 渲染后的 LaTeX 源码（始终有值）
            "pdf_path": Optional[str],    # PDF 路径，latexmk 不可用时 None
            "docx_path": Optional[str],   # docx 路径，pandoc 不可用时 None
            "degraded": bool,             # 任一编译失败为 True
        }

    ADR-0009: 若 ``state['references_list']`` 非空，在 ``\\end{document}`` 前追加
    ``\\begin{thebibliography}`` 环境。
    """
    template_name = normalize_template(state.get("export_template") or "cn_journal")

    title = _extract_title(state.get("title_chapter"))
    author = (state.get("author") or "").strip()
    abstract = state.get("abstract")
    sections = _extract_sections(state.get("body_chapters", []) or [], state)

    tex_source = render_template(
        template_name,
        title=title,
        author=author,
        chapters=sections,
        abstract=abstract,
    )

    # ADR-0009: 追加参考文献列表（references_list 为空时原样返回）
    references_list = state.get("references_list", []) or []
    tex_source = _append_bibliography(tex_source, references_list)

    # 输出目录：优先 state['workspace']，否则临时目录
    output_dir = state.get("workspace") or tempfile.mkdtemp(prefix="econpaper_export_")

    # 写 .tex 源码（无论编译是否成功，源码总要落盘）
    tex_path = Path(output_dir) / "paper.tex"
    try:
        tex_path.parent.mkdir(parents=True, exist_ok=True)
        tex_path.write_text(tex_source, encoding="utf-8")
    except OSError:
        pass

    pdf_path = compile_pdf(tex_source, output_dir)
    if hasattr(convert_docx, "used_ooxml_fallback"):
        convert_docx.used_ooxml_fallback = False
    docx_path = convert_docx(tex_source, output_dir)
    ooxml_fallback = bool(getattr(convert_docx, "used_ooxml_fallback", False))

    degraded = pdf_path is None or docx_path is None or ooxml_fallback

    return {
        "latex_source": tex_source,
        "pdf_path": pdf_path,
        "docx_path": docx_path,
        "degraded": degraded,
    }
