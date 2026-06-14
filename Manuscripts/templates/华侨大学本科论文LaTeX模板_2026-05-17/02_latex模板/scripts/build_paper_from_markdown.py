#!/usr/bin/env python3
"""Build a thesis PDF from the current HQU LaTeX template and a Markdown paper."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = Path(
    "/Users/mahaoxuan/Desktop/学术灵感项目_2026-04-07/final/04_paper/论文v2.1_完整版.md"
)


def run(cmd: list[str], cwd: Path | None = None, input_text: str | None = None) -> str:
    result = subprocess.run(
        cmd,
        cwd=cwd,
        input=input_text,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"command failed: {' '.join(cmd)}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
    return result.stdout


def md_to_latex(markdown: str, *, top_level_chapter: bool = False) -> str:
    cmd = [
        "pandoc",
        "-f",
        "markdown+tex_math_dollars+pipe_tables+simple_tables+multiline_tables",
        "-t",
        "latex",
        "--wrap=preserve",
    ]
    if top_level_chapter:
        cmd.append("--top-level-division=chapter")
    return run(cmd, input_text=markdown)


def strip_heading_number(line: str) -> str:
    match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
    if not match:
        return line
    hashes, title = match.groups()
    title = re.sub(r"^\d+(?:\.\d+)*\s+", "", title)
    return f"{hashes} {title}"


def promote_body_headings(markdown: str) -> str:
    lines: list[str] = []
    for line in markdown.splitlines():
        if line.startswith("#### "):
            line = "### " + line[5:]
        elif line.startswith("### "):
            line = "## " + line[4:]
        elif line.startswith("## "):
            line = "# " + line[3:]
        line = strip_heading_number(line)
        lines.append(line)
    return "\n".join(lines).strip() + "\n"


def split_markdown(markdown: str) -> dict[str, str]:
    title_match = re.search(r"^#\s+(.+?)\s*$", markdown, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else "本科毕业论文"

    zh_start = markdown.index("**摘要**") + len("**摘要**")
    kw_match = re.search(r"^\*\*关键词\*\*[：:]\s*(.+?)\s*$", markdown, re.MULTILINE)
    if not kw_match:
        raise ValueError("Cannot find Chinese keywords line.")
    zh_abstract = markdown[zh_start : kw_match.start()].strip()
    zh_keywords = kw_match.group(1).strip()

    en_start_match = re.search(r"^\*\*Abstract\*\*\s*$", markdown, re.MULTILINE)
    en_kw_match = re.search(r"^\*\*Keywords\*\*[：:]\s*(.+?)\s*$", markdown, re.MULTILINE)
    if not en_start_match or not en_kw_match:
        raise ValueError("Cannot find English abstract or keywords.")
    en_abstract = markdown[en_start_match.end() : en_kw_match.start()].strip()
    en_keywords = en_kw_match.group(1).strip()

    body_start = markdown.index("## 1 ")
    refs_start = markdown.index("## 参考文献")
    appendix_start = markdown.index("## 附录")
    body = markdown[body_start:refs_start].strip()
    references = markdown[refs_start + len("## 参考文献") : appendix_start].strip()
    appendix = markdown[appendix_start + len("## 附录") :].strip()

    return {
        "title": title,
        "zh_abstract": zh_abstract,
        "zh_keywords": zh_keywords,
        "en_abstract": en_abstract,
        "en_keywords": en_keywords,
        "body": body,
        "references": references,
        "appendix": appendix,
    }


def tex_string(value: str) -> str:
    return md_to_latex(value).strip()


def build_tex(parts: dict[str, str]) -> str:
    title = parts["title"]
    title_main = title
    title_subtitle = ""
    if "：" in title:
        title_main, title_subtitle = title.split("：", 1)
    elif ":" in title:
        title_main, title_subtitle = title.split(":", 1)
    title_main = title_main.strip()
    title_subtitle = title_subtitle.strip()

    body_latex = md_to_latex(promote_body_headings(parts["body"]), top_level_chapter=True)
    refs_latex = md_to_latex(parts["references"])
    appendix_latex = md_to_latex(promote_body_headings(parts["appendix"]), top_level_chapter=True)
    zh_abstract = md_to_latex(parts["zh_abstract"])
    en_abstract = md_to_latex(parts["en_abstract"])

    return rf"""\documentclass[UTF8, zihao=-4, a4paper, openany, fontset=none]{{ctexrep}}

\usepackage[
  a4paper,
  top=3.80cm,
  bottom=3.80cm,
  left=3.20cm,
  right=3.20cm,
  headheight=18pt,
  headsep=0.80cm,
  footskip=1.00cm
]{{geometry}}

\usepackage{{fontspec}}
\setCJKmainfont{{Songti SC}}
\setCJKsansfont{{Heiti SC}}
\setCJKmonofont{{Songti SC}}
\setCJKfamilyfont{{song}}{{Songti SC}}
\setCJKfamilyfont{{hei}}{{Heiti SC}}
\newcommand{{\songti}}{{\CJKfamily{{song}}}}
\newcommand{{\heiti}}{{\CJKfamily{{hei}}}}
\setmainfont{{Times New Roman}}

\usepackage{{amsmath, amssymb}}
\usepackage{{graphicx}}
\usepackage{{booktabs}}
\usepackage{{longtable}}
\usepackage{{array}}
\usepackage{{calc}}
\usepackage{{caption}}
\usepackage{{fancyhdr}}
\usepackage{{tocloft}}
\usepackage{{enumitem}}
\usepackage{{microtype}}
\usepackage[hidelinks]{{hyperref}}
\newcounter{{none}}
\makeatletter
\newsavebox\pandoc@box
\newcommand*\pandocbounded[1]{{%
  \sbox\pandoc@box{{#1}}%
  \ifdim\wd\pandoc@box>\linewidth
    \resizebox{{\linewidth}}{{!}}{{#1}}%
  \else
    #1%
  \fi
}}
\makeatother

\newcommand{{\hqubodyfont}}{{\songti\fontsize{{12pt}}{{21pt}}\selectfont}}
\AtBeginDocument{{\hqubodyfont}}
\setlength{{\parindent}}{{2em}}
\setlength{{\parskip}}{{0pt}}
\setlength{{\emergencystretch}}{{3em}}

\renewcommand{{\thechapter}}{{\arabic{{chapter}}}}
\renewcommand{{\thesection}}{{\thechapter.\arabic{{section}}}}
\renewcommand{{\thesubsection}}{{\thesection.\arabic{{subsection}}}}
\renewcommand{{\thesubsubsection}}{{\thesubsection.\arabic{{subsubsection}}}}
\setcounter{{secnumdepth}}{{3}}
\numberwithin{{equation}}{{chapter}}
\renewcommand{{\theequation}}{{\thechapter-\arabic{{equation}}}}
\renewcommand{{\thetable}}{{\thechapter-\arabic{{table}}}}
\renewcommand{{\thefigure}}{{\thechapter-\arabic{{figure}}}}

\ctexset{{
  chapter = {{
    name = {{}},
    number = \arabic{{chapter}},
    aftername = \quad,
    format = \centering\bfseries\songti\fontsize{{16pt}}{{21pt}}\selectfont,
    beforeskip = 24pt,
    afterskip = 18pt
  }},
  section = {{
    format = \bfseries\songti\fontsize{{14pt}}{{21pt}}\selectfont,
    beforeskip = 18pt,
    afterskip = 6pt
  }},
  subsection = {{
    format = \bfseries\songti\fontsize{{12pt}}{{21pt}}\selectfont,
    beforeskip = 12pt,
    afterskip = 6pt
  }},
  subsubsection = {{
    format = \songti\fontsize{{12pt}}{{21pt}}\selectfont,
    beforeskip = 6pt,
    afterskip = 0pt
  }}
}}

\setcounter{{tocdepth}}{{2}}
\renewcommand{{\cftchapfont}}{{\songti\fontsize{{12pt}}{{20pt}}\selectfont\bfseries}}
\renewcommand{{\cftchappagefont}}{{\songti\fontsize{{12pt}}{{20pt}}\selectfont\bfseries}}
\renewcommand{{\cftsecfont}}{{\songti\fontsize{{12pt}}{{20pt}}\selectfont}}
\renewcommand{{\cftsecpagefont}}{{\songti\fontsize{{12pt}}{{20pt}}\selectfont}}
\renewcommand{{\cftsubsecfont}}{{\songti\fontsize{{12pt}}{{20pt}}\selectfont}}
\renewcommand{{\cftsubsecpagefont}}{{\songti\fontsize{{12pt}}{{20pt}}\selectfont}}
\setlength{{\cftbeforechapskip}}{{6pt}}

\DeclareCaptionLabelFormat{{hqulabel}}{{#1#2}}
\DeclareCaptionLabelSeparator{{hququad}}{{\quad}}
\captionsetup{{
  font={{small}},
  labelfont={{bf}},
  labelformat=hqulabel,
  labelsep=hququad,
  justification=centering
}}
\captionsetup[table]{{position=top}}
\captionsetup[figure]{{position=bottom}}

\newcommand{{\thesistitle}}{{{tex_string(title_main)}}}
\newcommand{{\thesissubtitle}}{{{tex_string(title_subtitle)}}}
\newcommand{{\thesiscollege}}{{经济与金融学院}}
\newcommand{{\thesismajor}}{{经济学}}
\newcommand{{\thesisgrade}}{{2022级}}
\newcommand{{\thesisstudentid}}{{20224105022}}
\newcommand{{\thesisauthor}}{{马浩宣}}
\newcommand{{\thesisadvisor}}{{杜宇洪 副教授}}
\newcommand{{\thesisdate}}{{2026年5月}}
\newcommand{{\thesisfulltitle}}{{\thesistitle —— \thesissubtitle}}

\fancypagestyle{{hqufront}}{{%
  \fancyhf{{}}
  \fancyhead[C]{{\zihao{{-5}}\leftmark}}
  \fancyfoot[C]{{\zihao{{-5}}\thepage}}
  \renewcommand{{\headrulewidth}}{{0.4pt}}
  \renewcommand{{\footrulewidth}}{{0pt}}
}}

\fancypagestyle{{hqumain}}{{%
  \fancyhf{{}}
  \fancyhead[L]{{\zihao{{-5}}\thesistitle}}
  \fancyhead[R]{{\zihao{{-5}}华侨大学本科毕业论文}}
  \fancyfoot[C]{{\zihao{{-5}}\thepage}}
  \renewcommand{{\headrulewidth}}{{0.4pt}}
  \renewcommand{{\footrulewidth}}{{0pt}}
}}

\newcommand{{\makehqucover}}{{%
  \clearpage
  \begingroup
  \newgeometry{{top=2.50cm,bottom=2.50cm,left=3.00cm,right=2.50cm}}
  \thispagestyle{{empty}}
  \centering
  \includegraphics[width=2.6cm]{{assets/hqu-emblem.png}}\par
  \vspace{{0.2cm}}
  \includegraphics[width=5.8cm]{{assets/hqu-wordmark.png}}\par
  \vspace{{0.8cm}}
  {{\heiti\fontsize{{20pt}}{{26pt}}\selectfont 本科毕业论文（设计）\par}}
  \vspace{{1.2cm}}
  {{\heiti\fontsize{{22pt}}{{30pt}}\selectfont \thesistitle\par}}
  \vspace{{0.25cm}}
  {{\heiti\fontsize{{18pt}}{{26pt}}\selectfont —— \thesissubtitle\par}}
  \vspace{{1.5cm}}
  {{\zihao{{3}}
  \renewcommand{{\arraystretch}}{{1.55}}
  \begin{{tabular}}{{|>{{\centering\arraybackslash}}p{{3.2cm}}|>{{\centering\arraybackslash}}p{{8.5cm}}|}}
    \hline
    学\quad 院 & \thesiscollege \\
    \hline
    专\quad 业 & \thesismajor \\
    \hline
    年\quad 级 & \thesisgrade \\
    \hline
    学\quad 号 & \thesisstudentid \\
    \hline
    姓\quad 名 & \thesisauthor \\
    \hline
    指导老师 & \thesisadvisor \\
    \hline
  \end{{tabular}}\par}}
  \vfill
  {{\songti\zihao{{-4}}华侨大学教务处印制\par}}
  \vspace{{0.3cm}}
  {{\bfseries\zihao{{-4}}\thesisdate\par}}
  \restoregeometry
  \endgroup
  \clearpage
}}

\newcommand{{\makeintegritypage}}{{%
  \clearpage
  \thispagestyle{{empty}}
  \begin{{center}}
    {{\heiti\fontsize{{16pt}}{{24pt}}\selectfont 华侨大学本科毕业论文（设计）诚信承诺书}}
  \end{{center}}
  \vspace{{1.0cm}}
  本人（姓名）\underline{{\makebox[3.0cm]{{\thesisauthor}}}}\quad
  学号\underline{{\makebox[3.0cm]{{\thesisstudentid}}}}\quad
  专业\underline{{\makebox[3.0cm]{{\thesismajor}}}}\par
  \vspace{{0.5cm}}
  郑重承诺：所呈交的毕业论文（设计）是在指导教师指导下自主完成。\par
  \vspace{{0.3cm}}
  论文题目：\underline{{\makebox[8.6cm]{{\thesisfulltitle}}}}\par
  \vspace{{0.3cm}}
  毕业论文（设计）选题和研究内容中不存在不正当引用、抄袭、伪造、篡改、代写、买卖等行为，如有违规行为，本人愿意承担一切责任。
  \vspace{{2.0cm}}
  \begin{{flushright}}
    承诺人（签名）：\underline{{\makebox[4cm]{{}}}}\\[1.2cm]
    年\quad 月\quad 日
  \end{{flushright}}
  \clearpage
}}

\newenvironment{{abstractzh}}{{%
  \clearpage
  \pagenumbering{{Roman}}
  \pagestyle{{hqufront}}
  \markboth{{摘要}}{{摘要}}
  \chapter*{{\texorpdfstring{{\heiti 摘\quad 要}}{{摘要}}}}
  \addcontentsline{{toc}}{{chapter}}{{摘要}}
}}{{\par}}

\newcommand{{\keywordszh}}[1]{{%
  \par\noindent\textbf{{关键词：}}#1\par
}}

\newenvironment{{abstracten}}{{%
  \clearpage
  \markboth{{Abstract}}{{Abstract}}
  \chapter*{{Abstract}}
  \addcontentsline{{toc}}{{chapter}}{{Abstract}}
}}{{\par}}

\newcommand{{\keywordsen}}[1]{{%
  \par\noindent\textbf{{Keywords:}} #1\par
}}

\newcommand{{\hqufronttoc}}{{%
  \clearpage
  \markboth{{目录}}{{目录}}
  \renewcommand{{\contentsname}}{{\texorpdfstring{{目\quad 录}}{{目录}}}}
  \tableofcontents
  \clearpage
  \pagenumbering{{arabic}}
  \pagestyle{{hqumain}}
}}

\begin{{document}}

\makehqucover
\makeintegritypage

\begin{{abstractzh}}
{zh_abstract}
\keywordszh{{{tex_string(parts["zh_keywords"])}}}
\end{{abstractzh}}

\begin{{abstracten}}
{en_abstract}
\keywordsen{{{tex_string(parts["en_keywords"])}}}
\end{{abstracten}}

\hqufronttoc

{body_latex}

\chapter*{{参考文献}}
\addcontentsline{{toc}}{{chapter}}{{参考文献}}
{refs_latex}

\appendix
\chapter*{{附录}}
\addcontentsline{{toc}}{{chapter}}{{附录}}
{appendix_latex}

\end{{document}}
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--build-dir", type=Path, default=ROOT / "build" / "paper_v21_hqu")
    args = parser.parse_args()

    source = args.source.expanduser().resolve()
    build_dir = args.build_dir.expanduser().resolve()
    build_dir.mkdir(parents=True, exist_ok=True)
    output = args.output.expanduser().resolve() if args.output else None
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
    (build_dir / "assets").mkdir(exist_ok=True)
    shutil.copy2(ROOT / "assets" / "hqu-emblem.png", build_dir / "assets" / "hqu-emblem.png")
    shutil.copy2(ROOT / "assets" / "hqu-wordmark.png", build_dir / "assets" / "hqu-wordmark.png")

    source_figures = source.parent / "figures"
    if source_figures.exists():
        build_figures = build_dir / "figures"
        if build_figures.exists():
            shutil.rmtree(build_figures)
        shutil.copytree(source_figures, build_figures)

    markdown = source.read_text(encoding="utf-8")
    parts = split_markdown(markdown)
    tex = build_tex(parts)
    tex_path = build_dir / "paper_v21_hqu.tex"
    tex_path.write_text(tex, encoding="utf-8")

    for _ in range(2):
        run(["xelatex", "-interaction=nonstopmode", "-halt-on-error", tex_path.name], cwd=build_dir)

    pdf_path = build_dir / "paper_v21_hqu.pdf"
    if not pdf_path.exists():
        raise FileNotFoundError(pdf_path)
    if output:
        shutil.copy2(pdf_path, output)
        print(f"copied: {output}")
    print(f"built: {pdf_path}")
    print(f"source: {source}")
    print(f"tex: {tex_path}")


if __name__ == "__main__":
    main()
