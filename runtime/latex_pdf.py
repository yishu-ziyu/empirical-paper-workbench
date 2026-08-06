"""Markdown empirical paper → beautiful Chinese LaTeX PDF (xelatex / ctexart).

Evaluator-friendly: returns structured compile status + paths.
"""

from __future__ import annotations

import csv
import re
import shutil
import subprocess
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

# Heading patterns already carrying Chinese ordinals (avoid "1 一、引言")
_RE_CN_SECTION_NUM = re.compile(
    r"^(?:"
    r"[一二三四五六七八九十百零〇两]+、"  # 一、二、
    r"|（[一二三四五六七八九十百零〇两]+）"  # （一）
    r"|\([一二三四五六七八九十百零〇两]+\)"
    r"|第[一二三四五六七八九十百零〇两\d]+[章节部分篇]"
    r"|\d+[\.、．]\s*"
    r")"
)
_RE_ABSTRACT_HEAD = re.compile(r"^(摘要|abstract)$", re.I)
_RE_KEYWORDS_LINE = re.compile(
    r"^(?:\*\*)?(?:关键词|关键字|Keywords?)(?:\*\*)?[：:]\s*(.+)$",
    re.I,
)
_RE_HR = re.compile(r"^(-{3,}|\*{3,}|_{3,})$")
_RE_MD_TABLE_SEP = re.compile(r"^\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _escape_tex(text: str) -> str:
    if not text:
        return ""
    repl = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    out = []
    for ch in text:
        out.append(repl.get(ch, ch))
    return "".join(out)


def _protect_math(text: str) -> tuple[str, list[str]]:
    """Pull display/inline math out so TeX escaping does not destroy it."""
    store: list[str] = []

    def _stash(m: re.Match[str]) -> str:
        store.append(m.group(0))
        return f"@@MATH{len(store) - 1}@@"

    s = text
    # display \[...\] and $$...$$
    s = re.sub(r"\\\[(.+?)\\\]", _stash, s, flags=re.S)
    s = re.sub(r"\$\$(.+?)\$\$", _stash, s, flags=re.S)
    # inline \(...\) and $...$
    s = re.sub(r"\\\((.+?)\\\)", _stash, s, flags=re.S)
    s = re.sub(r"(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)", _stash, s, flags=re.S)
    return s, store


def _restore_math(text: str, store: list[str]) -> str:
    out = text
    for i, chunk in enumerate(store):
        out = out.replace(f"@@MATH{i}@@", chunk)
    return out


def _md_inline_to_tex(text: str) -> str:
    """Convert **bold**, *italic*, `code`, [text](url); escape TeX specials safely.

    Order matters: extract markdown spans first (with already-escaped interiors),
    escape the remaining plain text, then re-inject protected spans.
    """
    if not text:
        return ""

    s, math_store = _protect_math(text)
    placeholders: list[tuple[str, str]] = []

    def stash(tex_fragment: str) -> str:
        key = f"@@PH{len(placeholders)}@@"
        placeholders.append((key, tex_fragment))
        return key

    # links → keep visible label
    s = re.sub(
        r"\[([^\]]+)\]\([^)]+\)",
        lambda m: stash(_escape_tex(m.group(1))),
        s,
    )
    # bold **...**
    s = re.sub(
        r"\*\*([^*]+)\*\*",
        lambda m: stash(r"\textbf{" + _escape_tex(m.group(1)) + "}"),
        s,
    )
    # italic *...* (not part of **)
    s = re.sub(
        r"(?<!\*)\*([^*]+)\*(?!\*)",
        lambda m: stash(r"\emph{" + _escape_tex(m.group(1)) + "}"),
        s,
    )
    # inline code
    s = re.sub(
        r"`([^`]+)`",
        lambda m: stash(r"\texttt{" + _escape_tex(m.group(1)) + "}"),
        s,
    )

    s = _escape_tex(s)
    for key, val in placeholders:
        s = s.replace(key, val)
    return _restore_math(s, math_store)


def _strip_heading_number(title: str) -> str:
    """Remove leading Chinese/Arabic ordinals so ctex can number cleanly."""
    t = title.strip()
    prev = None
    while prev != t:
        prev = t
        t = _RE_CN_SECTION_NUM.sub("", t).strip()
    return t or title.strip()


def _heading_level_and_title(line: str) -> tuple[int, str] | None:
    m = re.match(r"^(#{1,4})\s+(.+?)\s*$", line)
    if not m:
        return None
    return len(m.group(1)), m.group(2).strip()


def _is_abstract_heading(title: str) -> bool:
    return bool(_RE_ABSTRACT_HEAD.match(title.strip()))


def normalize_markdown_source(md: str) -> str:
    """Strip accidental whole-document fences (```markdown ... ```) and BOMs."""
    s = md.replace("\r\n", "\n").lstrip("\ufeff").strip()
    # whole-file fenced dump from some generators
    m = re.match(r"^```(?:markdown|md)?\s*\n([\s\S]*?)\n```\s*$", s, re.I)
    if m:
        s = m.group(1).strip()
    # leading fence only (no closing) — still unwrap first line
    if re.match(r"^```(?:markdown|md)?\s*$", s.split("\n", 1)[0], re.I):
        parts = s.split("\n", 1)
        s = parts[1] if len(parts) > 1 else s
        if s.rstrip().endswith("```"):
            s = s.rstrip()[:-3].rstrip()
    return s


def extract_title(md: str, fallback: str) -> str:
    md = normalize_markdown_source(md)
    for line in md.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def extract_abstract_and_keywords(md: str) -> tuple[str, str]:
    """Pull 摘要 section body + optional 关键词 line."""
    md = normalize_markdown_source(md)
    m = re.search(r"##\s*摘要\s*\n+(.+?)(?:\n##|\Z)", md, re.S)
    if not m:
        m = re.search(r"##\s*Abstract\s*\n+(.+?)(?:\n##|\Z)", md, re.I | re.S)
    if not m:
        return "", ""

    block = m.group(1).strip()
    keywords = ""
    lines = block.split("\n")
    kept: list[str] = []
    for ln in lines:
        km = _RE_KEYWORDS_LINE.match(ln.strip())
        if km:
            keywords = km.group(1).strip().strip("*").strip()
            continue
        if _RE_HR.match(ln.strip()):
            continue
        kept.append(ln)
    abstract = re.sub(r"\s+", " ", "\n".join(kept)).strip()
    abstract = re.sub(r"\s*-{3,}\s*$", "", abstract).strip()
    # keep a usable length for the front matter
    if len(abstract) > 900:
        abstract = abstract[:900].rstrip() + "…"
    return abstract, keywords


def _md_table_to_tex(rows: list[str]) -> str:
    """Convert a simple pipe table to booktabs tabular."""
    parsed: list[list[str]] = []
    for raw in rows:
        line = raw.strip().strip("|")
        if _RE_MD_TABLE_SEP.match(raw.strip()):
            continue
        cells = [c.strip() for c in line.split("|")]
        if cells:
            parsed.append(cells)
    if not parsed:
        return ""
    ncol = max(len(r) for r in parsed)
    colspec = "l" + "r" * max(ncol - 1, 0)
    lines = [
        r"\begin{center}",
        r"\begin{tabular}{" + colspec + "}",
        r"\toprule",
    ]
    header = parsed[0] + [""] * (ncol - len(parsed[0]))
    lines.append(" & ".join(_md_inline_to_tex(c) for c in header[:ncol]) + r" \\")
    lines.append(r"\midrule")
    for row in parsed[1:40]:
        cells = row + [""] * (ncol - len(row))
        lines.append(" & ".join(_md_inline_to_tex(c) for c in cells[:ncol]) + r" \\")
    lines.extend([r"\bottomrule", r"\end{tabular}", r"\end{center}", ""])
    return "\n".join(lines)


def markdown_to_ctex_body(md: str, *, skip_abstract_section: bool = True) -> str:
    """Convert a subset of Chinese academic markdown to LaTeX body."""
    lines = normalize_markdown_source(md).split("\n")
    body: list[str] = []
    in_list = False
    list_env = "itemize"  # or enumerate
    in_code = False
    code_buf: list[str] = []
    skip_title = True
    skipping_abstract = False
    i = 0
    n = len(lines)

    def close_list() -> None:
        nonlocal in_list, list_env
        if in_list:
            body.append(rf"\end{{{list_env}}}")
            in_list = False
            list_env = "itemize"

    def open_list(env: str) -> None:
        nonlocal in_list, list_env
        if in_list and list_env != env:
            close_list()
        if not in_list:
            body.append(rf"\begin{{{env}}}")
            in_list = True
            list_env = env

    while i < n:
        raw = lines[i]
        line = raw.rstrip()
        i += 1

        # fenced code
        if line.startswith("```"):
            if not in_code:
                close_list()
                in_code = True
                code_buf = []
            else:
                in_code = False
                body.append(r"\begin{verbatim}")
                body.extend(code_buf)
                body.append(r"\end{verbatim}")
                code_buf = []
            continue
        if in_code:
            code_buf.append(line)
            continue

        # blank
        if not line.strip():
            close_list()
            body.append("")
            continue

        # horizontal rule
        if _RE_HR.match(line.strip()):
            close_list()
            body.append(r"\par\medskip")
            continue

        # headings
        ht = _heading_level_and_title(line)
        if ht is not None:
            level, title = ht
            close_list()

            if level == 1 and skip_title:
                skip_title = False
                skipping_abstract = False
                continue

            if skip_abstract_section and _is_abstract_heading(title):
                # abstract lives in \begin{abstract}; drop body duplicate
                skipping_abstract = True
                continue

            # leaving abstract block on any other heading
            if skipping_abstract:
                skipping_abstract = False

            clean = _strip_heading_number(title)
            # map md levels → latex
            # # leftover → section; ## → section; ### → subsection; #### → subsubsection
            if level <= 2:
                cmd = r"\section"
            elif level == 3:
                cmd = r"\subsection"
            else:
                cmd = r"\subsubsection"
            body.append(cmd + "{" + _escape_tex(clean) + "}")
            continue

        if skipping_abstract:
            # still inside 摘要 body (rare if no next heading yet)
            continue

        # blockquote (single-line; multi-line consecutive > merged lightly)
        if line.lstrip().startswith(">"):
            close_list()
            q_parts: list[str] = []
            q_line = line
            while True:
                q_parts.append(re.sub(r"^\s*>\s?", "", q_line))
                if i < n and lines[i].lstrip().startswith(">"):
                    q_line = lines[i].rstrip()
                    i += 1
                else:
                    break
            quote = " ".join(p.strip() for p in q_parts if p.strip())
            body.append(r"\begin{quote}")
            body.append(_md_inline_to_tex(quote))
            body.append(r"\end{quote}")
            continue

        # markdown pipe table: collect consecutive table rows
        if line.strip().startswith("|") and "|" in line.strip()[1:]:
            close_list()
            table_rows = [line]
            while i < n and lines[i].strip().startswith("|"):
                table_rows.append(lines[i].rstrip())
                i += 1
            tex_table = _md_table_to_tex(table_rows)
            if tex_table:
                body.append(tex_table)
            else:
                for tr in table_rows:
                    body.append(r"\texttt{" + _escape_tex(tr.strip()) + r"}\\")
            continue

        # unordered list
        if re.match(r"^[-*]\s+", line):
            open_list("itemize")
            item = re.sub(r"^[-*]\s+", "", line)
            body.append(r"\item " + _md_inline_to_tex(item))
            continue

        # ordered list
        if re.match(r"^\d+\.\s+", line):
            open_list("enumerate")
            item = re.sub(r"^\d+\.\s+", "", line)
            body.append(r"\item " + _md_inline_to_tex(item))
            continue

        # indented continuation under list (treat as nested item if "- ")
        m_nested = re.match(r"^\s{2,}([-*]|\d+\.)\s+(.+)$", line)
        if m_nested and in_list:
            body.append(r"\item " + _md_inline_to_tex(m_nested.group(2)))
            continue

        close_list()
        body.append(_md_inline_to_tex(line))

    close_list()
    if in_code and code_buf:
        body.append(r"\begin{verbatim}")
        body.extend(code_buf)
        body.append(r"\end{verbatim}")
    return "\n".join(body)


def _fmt_table_cell(raw: str) -> str:
    """Round machine floats for human tables; leave labels alone."""
    s = (raw or "").strip()
    if not s:
        return ""
    # pure integer sample sizes etc.
    if re.fullmatch(r"-?\d+", s):
        return s
    try:
        v = float(s)
    except ValueError:
        return s
    # p-values
    if 0 <= v < 0.001 and "e" in s.lower():
        return "<0.001"
    if 0 < v < 0.001:
        return "<0.001"
    # typical coef/se/r2
    if abs(v) >= 1000:
        return f"{v:.0f}"
    if abs(v) >= 10:
        return f"{v:.2f}"
    return f"{v:.3f}"


def _csv_to_booktabs(path: Path, caption: str, label: str) -> str:
    if not path.exists():
        return f"% missing table {path}\n"
    with path.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.reader(fh))
    if not rows:
        return f"% empty table {path}\n"
    header, data = rows[0], rows[1:]
    ncol = max(len(header), 1)
    colspec = "l" + "r" * (ncol - 1)
    # Friendly header labels (no raw snake_case dumps when obvious)
    header_map = {
        "term": "变量",
        "coef": "系数",
        "se": "标准误",
        "p": "p 值",
        "nobs": "样本量",
        "parent_education_coef": "父母教育系数",
        "parent_education_se": "标准误",
        "parent_education_p": "p 值",
        "sample": "样本",
        "mean": "均值",
        "std": "标准差",
        "count": "观测数",
        "min": "最小",
        "max": "最大",
    }
    header_disp = [header_map.get(c.strip(), c) for c in header]
    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{" + _escape_tex(caption) + "}",
        r"\label{" + label + "}",
        r"\small",
        r"\begin{tabular}{" + colspec + "}",
        r"\toprule",
        " & ".join(_escape_tex(c) for c in header_disp) + r" \\",
        r"\midrule",
    ]
    for row in data[:40]:
        cells = list(row) + [""] * (ncol - len(row))
        fmt = [_fmt_table_cell(c) for c in cells[:ncol]]
        # first column often a variable name — keep as-is if non-numeric
        if fmt and cells[0] and not re.fullmatch(r"-?\d+(\.\d+)?([eE][+-]?\d+)?", cells[0].strip() or ""):
            fmt[0] = cells[0].strip()
        lines.append(" & ".join(_escape_tex(c) for c in fmt) + r" \\")
    lines.extend([r"\bottomrule", r"\end{tabular}", r"\end{table}", ""])
    return "\n".join(lines)


def _font_available(name: str) -> bool:
    """Best-effort check via fc-list (macOS/Linux)."""
    fc = shutil.which("fc-list")
    if not fc:
        return False
    try:
        r = subprocess.run(
            [fc, name, "family"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return bool((r.stdout or "").strip())
    except (OSError, subprocess.SubprocessError):
        return False


def _cjk_font_block() -> str:
    """CJK main/sans/mono with Songti / STSong / PingFang SC fallbacks."""
    main_candidates = ["Songti SC", "STSong", "Songti SC Light", "PingFang SC"]
    sans_candidates = ["PingFang SC", "Heiti SC", "STHeiti", "Songti SC"]
    mono_candidates = ["PingFang SC", "STHeiti", "Heiti SC", "Songti SC"]

    main = next((f for f in main_candidates if _font_available(f)), "PingFang SC")
    sans = next((f for f in sans_candidates if _font_available(f)), main)
    mono = next((f for f in mono_candidates if _font_available(f)), sans)

    # Bold: prefer PingFang SC Medium / PingFang SC when available
    bold = "PingFang SC" if _font_available("PingFang SC") else main
    italic = "Kaiti SC" if _font_available("Kaiti SC") else main

    return f"""% CJK fonts (auto-detected; fallbacks: Songti SC / STSong / PingFang SC)
\\setCJKmainfont{{{main}}}[
  BoldFont={{{bold}}},
  ItalicFont={{{italic}}}
]
\\setCJKsansfont{{{sans}}}
\\setCJKmonofont{{{mono}}}
"""


@dataclass
class LatexPdfResult:
    ok: bool
    tex_path: str = ""
    pdf_path: str = ""
    log_path: str = ""
    engine: str = ""
    returncode: int = -1
    pages_hint: int = 0
    errors: list[str] = field(default_factory=list)
    built_at: str = ""
    used_last_good: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _rel_to_root(path: Path, root: Path) -> str:
    """Best-effort path relative to project root (for package manifests)."""
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except Exception:
        try:
            return str(path.relative_to(root))
        except Exception:
            return str(path)


def _last_good_deliver_pdf(root: Path, slug: str) -> tuple[str, bool]:
    """Return (relative_path, ok) for an existing deliver PDF worth keeping."""
    deliver = root / "Submissions" / f"{slug}_loop_paper.pdf"
    if deliver.exists() and deliver.stat().st_size > 1000:
        return _rel_to_root(deliver, root), True
    return "", False


def build_ctex_document(
    *,
    title: str,
    body_tex: str,
    tables_tex: str,
    author: str = "",
    abstract: str = "",
    keywords: str = "",
) -> str:
    abs_block = ""
    if abstract:
        kw_line = ""
        if keywords:
            kw_line = (
                "\n\\vspace{0.6em}\\noindent"
                + r"\textbf{关键词：}"
                + _md_inline_to_tex(keywords)
                + "\n"
            )
        abs_block = (
            r"\begin{abstract}" + "\n"
            + _md_inline_to_tex(abstract)
            + "\n"
            + kw_line
            + r"\end{abstract}"
            + "\n"
        )

    font_block = _cjk_font_block()

    return rf"""% !TEX program = xelatex
% Auto-generated manuscript PDF (machine build metadata; not part of prose)
\documentclass[UTF8,a4paper,11pt,fontset=none]{{ctexart}}
\usepackage[margin=2.5cm]{{geometry}}
\usepackage{{booktabs}}
\usepackage{{longtable}}
\usepackage{{array}}
\usepackage{{tabularx}}
\usepackage{{graphicx}}
\usepackage{{hyperref}}
\usepackage{{setspace}}
\usepackage{{amsmath,amssymb}}
\usepackage{{caption}}
\usepackage{{float}}
\usepackage{{indentfirst}}
{font_block}
\hypersetup{{
  colorlinks=true,
  linkcolor=blue,
  urlcolor=blue,
  citecolor=blue
}}
\setstretch{{1.35}}
\setlength{{\parindent}}{{2em}}
\setlength{{\parskip}}{{0.35em}}
\captionsetup{{
  font=small,
  labelfont=bf,
  skip=6pt
}}
\ctexset{{
  section = {{
    format = \Large\bfseries\raggedright,
    name = {{,、}},
    number = \chinese{{section}},
    aftername = \hspace{{0.5em}},
    beforeskip = 1.4ex plus 0.3ex minus 0.1ex,
    afterskip = 0.9ex plus 0.1ex,
  }},
  subsection = {{
    format = \large\bfseries\raggedright,
    name = {{（,）}},
    number = \chinese{{subsection}},
    aftername = \hspace{{0.4em}},
    beforeskip = 1.1ex plus 0.2ex minus 0.1ex,
    afterskip = 0.7ex plus 0.1ex,
  }},
  subsubsection = {{
    format = \normalsize\bfseries\raggedright,
    beforeskip = 0.9ex plus 0.1ex,
    afterskip = 0.5ex plus 0.1ex,
  }},
}}
\renewcommand{{\abstractname}}{{摘\quad 要}}
\title{{{_escape_tex(title)}}}
\author{{{_escape_tex(author)}}}
\date{{\today}}
\begin{{document}}
\maketitle
{abs_block}
\tableofcontents
\newpage
{body_tex}

\section{{回归表}}
{tables_tex}

\section{{研究局限（补充）}}
本文主结果为可复现的 OLS 关联估计，\textbf{{不是}}因果意义上的局部平均处理效应。
文献条目若尚未完成外源核验，不得当作已发表正式综述。
正文数字以回归表为准；识别边界见正文相应章节。

\end{{document}}
"""


def render_markdown_paper_to_pdf(
    md_path: Path,
    *,
    out_dir: Path | None = None,
    slug: str = "parent_education_wage",
    title: str | None = None,
    author: str = "",
    table_specs: list[tuple[str, str, str]] | None = None,
    project_root: Path | None = None,
) -> LatexPdfResult:
    """Build ctexart .tex + compile with xelatex (2 passes).

    On compile failure, does **not** overwrite Submissions/{slug}_loop_paper.pdf.
    If a previous deliver PDF exists, pdf_path points to it with used_last_good=True.
    """
    root = project_root or ROOT
    md_path = Path(md_path)
    if not md_path.is_absolute():
        md_path = root / md_path
    if not md_path.exists():
        last_rel, has_last = _last_good_deliver_pdf(root, slug)
        errors = [f"md_missing:{md_path}"]
        if has_last:
            errors.append("using_last_good_pdf")
        return LatexPdfResult(
            ok=False,
            pdf_path=last_rel,
            errors=errors,
            used_last_good=has_last,
            built_at=_now(),
        )

    out_dir = Path(out_dir) if out_dir else root / "Submissions" / "latex_build" / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    md = normalize_markdown_source(
        md_path.read_text(encoding="utf-8", errors="replace")
    )
    title = title or extract_title(md, slug.replace("_", " "))

    abstract, keywords = extract_abstract_and_keywords(md)
    body = markdown_to_ctex_body(md, skip_abstract_section=True)
    if table_specs is None:
        table_specs = [
            (str(root / "tables" / f"{slug}_table1_desc.csv"), "描述统计", "tab:desc"),
            (str(root / "tables" / f"{slug}_table2_main_ols.csv"), "主回归 OLS+HC1", "tab:main"),
            (str(root / "tables" / f"{slug}_table_robustness.csv"), "稳健性子样本", "tab:robust"),
        ]
    tables_tex = "\n".join(
        _csv_to_booktabs(Path(p), cap, lab) for p, cap, lab in table_specs
    )
    tex = build_ctex_document(
        title=title,
        body_tex=body,
        tables_tex=tables_tex,
        author=author,
        abstract=abstract,
        keywords=keywords,
    )
    tex_path = out_dir / f"{slug}_loop_paper.tex"
    tex_path.write_text(tex, encoding="utf-8")
    tex_rel = _rel_to_root(tex_path, root)

    engine = shutil.which("xelatex") or shutil.which("lualatex") or shutil.which("pdflatex")
    if not engine:
        last_rel, has_last = _last_good_deliver_pdf(root, slug)
        errors = ["no_latex_engine"]
        if has_last:
            errors.append("using_last_good_pdf")
        return LatexPdfResult(
            ok=False,
            tex_path=tex_rel,
            pdf_path=last_rel,
            errors=errors,
            used_last_good=has_last,
            built_at=_now(),
        )

    log_path = out_dir / "xelatex_build.log"
    logs: list[str] = []
    rc = 0
    # Prefer isolated jobname when possible; keep simple name for stable artifacts.
    # Do not use -halt-on-error alone as the only stop: still break on rc!=0.
    # Avoid wiping deliver PDF on failure (copy only after success).
    for _pass in range(2):
        try:
            r = subprocess.run(
                [
                    engine,
                    "-interaction=nonstopmode",
                    "-halt-on-error",
                    "-file-line-error",
                    tex_path.name,
                ],
                cwd=str(out_dir),
                capture_output=True,
                text=True,
                timeout=180,
            )
        except subprocess.TimeoutExpired as exc:
            logs.append(f"timeout:{exc}")
            rc = 124
            break
        except Exception as exc:  # noqa: BLE001
            logs.append(f"xelatex_spawn_error:{exc}")
            rc = 125
            break
        logs.append(r.stdout[-4000:] if r.stdout else "")
        logs.append(r.stderr[-2000:] if r.stderr else "")
        rc = r.returncode
        if rc != 0:
            break
    log_path.write_text("\n---\n".join(logs), encoding="utf-8")
    log_rel = _rel_to_root(log_path, root)
    pdf_path = out_dir / f"{slug}_loop_paper.pdf"
    # also copy to Submissions root for easy open / evaluator
    deliver = root / "Submissions" / f"{slug}_loop_paper.pdf"
    if pdf_path.exists() and rc == 0 and pdf_path.stat().st_size > 1000:
        deliver.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(pdf_path, deliver)
        pages = 0
        if shutil.which("pdfinfo"):
            try:
                pr = subprocess.run(
                    ["pdfinfo", str(pdf_path)], capture_output=True, text=True, timeout=30
                )
                m = re.search(r"Pages:\s+(\d+)", pr.stdout or "")
                if m:
                    pages = int(m.group(1))
            except Exception:  # noqa: BLE001
                pages = 0
        return LatexPdfResult(
            ok=True,
            tex_path=tex_rel,
            pdf_path=_rel_to_root(deliver, root),
            log_path=log_rel,
            engine=engine,
            returncode=rc,
            pages_hint=pages,
            built_at=_now(),
            used_last_good=False,
        )
    # parse common errors
    err: list[str] = []
    blob = "\n".join(logs)
    for line in blob.splitlines():
        if "Error" in line or (line.startswith("!") if line else False):
            err.append(line[:200])
            if len(err) >= 12:
                break
    last_rel, has_last = _last_good_deliver_pdf(root, slug)
    if has_last:
        err = list(err or ["pdf_not_produced"])
        if "using_last_good_pdf" not in err:
            err.append("using_last_good_pdf")
    return LatexPdfResult(
        ok=False,
        tex_path=tex_rel,
        pdf_path=last_rel,
        log_path=log_rel,
        engine=engine,
        returncode=rc,
        errors=err or ["pdf_not_produced"],
        built_at=_now(),
        used_last_good=has_last,
    )
