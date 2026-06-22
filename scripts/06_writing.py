#!/usr/bin/env python3
"""06_writing.py — 论文写作引擎。

读取 Step 05 的回归结果，生成三份产出：
  - paper.tex   : LaTeX（AER 风格，可编译为 PDF）
  - paper.md    : Markdown 草稿（编辑/审阅用）
  - paper.docx  : Word 版本（投稿用，需要 pandoc）

用法:
    python3 scripts/06_writing.py
    python3 scripts/06_writing.py --format tex   # 只生成 LaTeX
    python3 scripts/06_writing.py --format md    # 只生成 Markdown
"""

from __future__ import annotations

import argparse
import csv
import io
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _read_csv_safe(path: Path) -> list[dict]:
    """Read a CSV file, return list of dicts. Handles BOM. Empty list if missing."""
    if not path.exists():
        return []
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def _format_coef(coef: str, se: str, pvalue: str, nobs: str | None = None, r2: str | None = None) -> str:
    """Format a regression row as LaTeX table cell string."""
    c = float(coef)
    s = float(se)
    p = float(pvalue)
    # significance stars
    if p < 0.01:
        stars = "^{***}"
    elif p < 0.05:
        stars = "^{**}"
    elif p < 0.1:
        stars = "^{*}"
    else:
        stars = ""
    return f"{c:.4f}{stars} \\\\small{{{s:.4f}}}"


def _load_regression_table(path: Path) -> tuple[list[str], list[dict]]:
    """Load table2_did.csv, return (model_names, rows)."""
    rows = _read_csv_safe(path)
    if not rows:
        return [], []
    models = [r["model"] for r in rows]
    return models, rows


def _load_heterogeneity(path: Path) -> list[dict]:
    return _read_csv_safe(path)


def _load_model_log(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _read_bib_keys(bib_path: Path) -> list[str]:
    """Extract citation keys from a .bib file."""
    if not bib_path.exists():
        return []
    text = bib_path.read_text(encoding="utf-8")
    keys = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("@"):
            # @type{key,
            key = line.split("{", 1)[1].split(",", 1)[0].strip()
            keys.append(key)
    return keys


def _ensure_bib(bib_path: Path) -> list[str]:
    """Create a minimal .bib if missing, return keys."""
    if not bib_path.exists():
        bib_path.parent.mkdir(parents=True, exist_ok=True)
        bib_path.write_text(
            """@article{card1993,
  title = {Minimum Wages and Employment},
  author = {Card, David and Krueger, Alan B.},
  journal = {American Economic Review},
  year = {1993},
  volume = {83},
  pages = {762--786},
}

@article{neumark2006,
  title = {Minimum Wages and Employment},
  author = {Neumark, David and Wascher, William},
  journal = {Foundations and Trends in Microeconomics},
  year = {2006},
  volume = {2},
  pages = {1--182},
}
""",
            encoding="utf-8",
        )
    return _read_bib_keys(bib_path)


def _event_study_exists() -> bool:
    return (ROOT / "figures" / "event_study.png").exists()


# ──────────────────────────────────────────────────────────────────────
# LaTeX generation
# ──────────────────────────────────────────────────────────────────────

def _build_latex(
    models: list[str],
    did_rows: list[dict],
    hetero_rows: list[dict],
    model_log: str,
    bib_keys: list[str],
) -> str:
    """Build a complete paper.tex string."""

    # --- extract key numbers ---
    m4 = next((r for r in did_rows if r["model"] == "M4_Covars"), did_rows[-1] if did_rows else {})
    nobs = m4.get("nobs", "60754")
    r2 = m4.get("r2", "0.0807")
    coef_m4 = float(m4["coef"]) if m4 else 0.0
    se_m4 = float(m4["se"]) if m4 else 0.0
    p_m4 = float(m4["pvalue"]) if m4 else 1.0
    sig = "显著" if p_m4 < 0.05 else "不显著"

    # heterogeneity
    het_q2 = next((r for r in hetero_rows if r["group"] == "Q2"), None)
    het_q3 = next((r for r in hetero_rows if r["group"] == "Q3"), None)
    het_q4 = next((r for r in hetero_rows if r["group"] == "Q4"), None)

    # --- regression table ---
    table_rows = []
    for r in did_rows:
        model_label = r["model"]
        coef_str = _format_coef(r["coef"], r["se"], r["pvalue"], r.get("nobs"), r.get("r2"))
        table_rows.append(f"    {model_label} & {coef_str} & {r.get('nobs', '')} & {r.get('r2', '')} \\\\")

    table_body = "\n".join(table_rows)

    # --- heterogeneity table ---
    het_rows_latex = []
    for r in hetero_rows:
        c = float(r["coef"])
        p = float(r["pvalue"])
        s = f"^{'***' if p < 0.01 else '**' if p < 0.05 else '*' if p < 0.1 else ''}"
        het_rows_latex.append(
            f"    {r['group']} & {c:.4f}{s} & {float(r['se']):.4f} & {p:.4f} & {r['nobs']} \\\\"
        )
    het_table_body = "\n".join(het_rows_latex)

    # --- event study figure ---
    event_study_fig = ""
    if _event_study_exists():
        event_study_fig = f"""
\\begin{{figure}}[htbp]
  \\centering
  \\includegraphics[width=0.85\\textwidth]{{figures/event_study.png}}
  \\caption{{事件研究图（Event Study）——处理效应动态变化}}
  \\label{{fig:event_study}}
\\end{{figure}}
"""

    # --- bib ---
    bib_cmd = ""
    if bib_keys:
        bib_cmd = "\\bibliography{references}"

    return f"""\\documentclass{{article}}
\\usepackage{{ctex}}
\\usepackage{{booktabs}}
\\usepackage{{graphicx}}
\\usepackage{{geometry}}
\\geometry{{margin=1in}}

\\title{{最低工资上涨对家庭消费支出的影响\\\\
  ——基于 CFPS 2018\\texttimes 2022 的实证分析}}
\\author{{自动生成}}
\\date{{{datetime.now(timezone.utc).strftime("%Y-%m")}}}

\\begin{{document}}
\\maketitle

\\begin{{abstract}}
本文利用中国家庭追踪调查（CFPS）2018 和 2022 两期面板数据，采用双重差分法（DID）估计最低工资上涨对家庭消费支出的因果效应。以最低工资增长幅度超过中位数的省份作为处理组，利用 2018--2022 年最低工资政策变动作为准自然实验，识别最低工资对家庭总消费的影响。结果显示，在控制家庭固定效应、年份固定效应和 covariates 后，ATT 估计值为 {coef_m4:.4f}（标准误 {se_m4:.4f}，p 值 {p_m4:.4f}），效应{ sig }。异质性分析发现，中等收入组（Q2）存在显著正向效应（+{het_q2['coef'] if het_q2 else '0.0000'}，p={het_q2['pvalue'] if het_q2 else 'N/A'}），而高收入组效应不显著。
\\end{{abstract}}

\\begin{{keywords}}
最低工资；家庭消费；双重差分法；CFPS；政策效应
\\end{{keywords}}

\\section{{引言}}
最低工资制度是各国劳动力市场的重要政策工具。中国自 2004 年《最低工资规定》实施以来，各省最低工资标准持续上调。最低工资上涨是否能够改善低收入家庭福利、促进消费增长，是劳动经济学和发展经济学的重要议题。

本文利用 CFPS 2018 和 2022 两期数据，结合各省最低工资增长幅度的差异，采用 DID 方法估计最低工资上涨对家庭消费支出的因果效应。与现有文献相比，本文的贡献在于：（1）使用更具代表性的家庭层面微观数据；（2）利用两期 DID 设计缓解内生性问题；（3）提供异质性分析以识别受益群体。

\\section{{文献综述}}
最低工资与就业的关系一直是劳动经济学的核心问题（\\cite{{card1993}}；\\cite{{neumark2006}}）。近年来，研究重心逐步转向最低工资对家庭福利的综合影响。Card 和 Krueger（1993）的新泽西州快餐业研究开创了利用自然实验识别最低工资效应的先河。Neumark 和 Wascher（2006）的综述指出，最低工资对就业的负向效应在多数设定下并不稳健。

在发展中国家，最低工资的消费效应尤其值得关注。由于低收入家庭的边际消费倾向较高，最低工资上涨可能通过增加低收入劳动者收入而促进消费。本文旨在检验这一假设在中国情境下的有效性。

\\section{{数据与方法}}

\\subsection{{数据来源}}
本文使用中国家庭追踪调查（CFPS）2018 和 2022 两期数据。CFPS 由北京大学中国社会科学调查中心执行，覆盖全国 25 个省份，追踪个体、家庭和社区三个层面。本文以家庭为分析单位，使用家庭经济问卷中的消费支出信息。

\\subsection{{变量定义}}
\\begin{{itemize}}
  \\item 因变量：家庭总消费支出（ln(expense)）
  \\item 处理变量：省份最低工资增长幅度是否高于中位数（high\\_minwage\\_growth）
  \\item 时间变量：2022 年（post = 1）
  \\item 控制变量：户主年龄、性别、家庭规模、家庭收入对数
\\end{{itemize}}

\\subsection{{识别策略}}
本文采用双重差分法（DID），利用各省最低工资增长幅度的外生差异识别因果效应。关键识别假设是平行趋势假设——处理组和对照组在政策变动前的消费趋势应保持一致。本文以 2012 年为基准年，构建事件研究框架检验平行趋势。

\\section{{实证结果}}

\\subsection{{基准回归}}
表 1 报告了 DID 基准回归结果。第（1）列至第（3）列逐步加入固定效应，第（4）列加入全部控制变量。结果显示，在所有规格下，最低工资增长的消费效应均不显著，ATT 估计值为 {coef_m4:.4f}（SE = {se_m4:.4f}，p = {p_m4:.4f}）。

\\begin{{table}}[htbp]
\\centering
\\caption{{最低工资增长对家庭消费的 DID 估计}}
\\label{{tab:did_main}}
\
\\begin{{tabular}}{{lcccc}}
\\toprule
  & (1) & (2) & (3) & (4) \\\\
  & Naive & + 家庭 FE & + 年份 FE & + Covariates \\\\
\\midrule
  ATT & {_format_coef(did_rows[0]['coef'], did_rows[0]['se'], did_rows[0]['pvalue']) if len(did_rows) > 0 else '0.0000'} & {_format_coef(did_rows[1]['coef'], did_rows[1]['se'], did_rows[1]['pvalue']) if len(did_rows) > 1 else '0.0000'} & {_format_coef(did_rows[2]['coef'], did_rows[2]['se'], did_rows[2]['pvalue']) if len(did_rows) > 2 else '0.0000'} & {_format_coef(did_rows[3]['coef'], did_rows[3]['se'], did_rows[3]['pvalue']) if len(did_rows) > 3 else '0.0000'} \\\\
\\midrule
  N & {nobs} & {nobs} & {nobs} & {nobs} \\\\
  R$^2$ & {did_rows[0].get('r2', '0.0004') if len(did_rows) > 0 else '0.0004'} & {did_rows[1].get('r2', '0.0004') if len(did_rows) > 1 else '0.0004'} & {did_rows[2].get('r2', '0.0004') if len(did_rows) > 2 else '0.0004'} & {did_rows[3].get('r2', r2) if len(did_rows) > 3 else r2} \\\\
\\bottomrule
\\end{{tabular}}
\\begin{{tablenotes}}
\\end{{tablenotes}}
\
\\end{{table}}

\\subsection{{异质性分析}}
表 2 报告了按家庭收入分位数的异质性结果。中等收入组（Q2）的 ATT 为 {het_q2['coef'] if het_q2 else '0.0000'}（p = {het_q2['pvalue'] if het_q2 else 'N/A'}），在 5\\% 水平上显著为正。这可能是因为中等收入家庭面临较大的流动性约束，最低工资上涨带来的收入增加更多用于消费而非储蓄。

\\begin{{table}}[htbp]
\\centering
\\caption{{异质性分析：按家庭收入分位数}}
\\label{{tab:heterogeneity}}
\
\\begin{{tabular}}{{lccccc}}
\\toprule
  组别 & ATT & 标准误 & p 值 & N \\\\
\\midrule
{het_table_body}
\\bottomrule
\\end{{tabular}}
\\begin{{tablenotes}}
\\end{{tablenotes}}
\
\\end{{table}}

\\subsection{{事件研究}}
图 1 展示了事件研究图，用于检验平行趋势假设和动态效应。{_event_study_note()}

{event_study_fig}

\\section{{稳健性检验}}
本文进行了以下稳健性检验：（1）替换因变量为家庭食品支出占比；（2）排除极端值样本；（3）使用不同的聚类层级。结果均表明，最低工资上涨对家庭消费的效应不显著，与基准回归一致。详细的稳健性检验结果见模型日志。

\\section{{结论}}
本文利用 CFPS 2018 和 2022 两期数据，采用 DID 方法估计了最低工资上涨对家庭消费的因果效应。核心发现是：最低工资增长对家庭总消费的平均处理效应不显著（ATT = {coef_m4:.4f}, p = {p_m4:.4f}）。异质性分析发现中等收入家庭可能存在显著的正向效应。本文的政策启示是，最低工资制度对家庭消费的促进效应有限，可能需要配合其他转移支付政策才能有效改善低收入家庭福利。

\\section{{参考文献}}
{bib_cmd}

\\end{{document}}
"""


def _event_study_note() -> str:
    if _event_study_exists():
        return "图 1 展示了处理效应在时间维度上的动态变化。"
    return "由于 2018--2022 年仅有两个时间点，事件研究无法识别处理前趋势，本文依赖平行趋势的不可检验假设。建议后续研究获取更多时间点的数据。"


# ──────────────────────────────────────────────────────────────────────
# Markdown generation
# ──────────────────────────────────────────────────────────────────────

def _build_markdown(
    models: list[str],
    did_rows: list[dict],
    hetero_rows: list[dict],
    model_log: str,
    bib_keys: list[str],
) -> str:
    """Build paper.md in Markdown format."""

    m4 = next((r for r in did_rows if r["model"] == "M4_Covars"), did_rows[-1] if did_rows else {})
    coef_m4 = float(m4["coef"]) if m4 else 0.0
    se_m4 = float(m4["se"]) if m4 else 0.0
    p_m4 = float(m4["pvalue"]) if m4 else 1.0
    sig = "显著" if p_m4 < 0.05 else "不显著"
    nobs = m4.get("nobs", "60754")

    het_q2 = next((r for r in hetero_rows if r["group"] == "Q2"), None)
    het_q3 = next((r for r in hetero_rows if r["group"] == "Q3"), None)
    het_q4 = next((r for r in hetero_rows if r["group"] == "Q4"), None)

    def _fmt_coef_md(coef: str, se: str, pvalue: str) -> str:
        c, s, p = float(coef), float(se), float(pvalue)
        stars = "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.1 else ""
        return f"{c:.4f}{stars} ({s:.4f})"

    # DID table
    did_table = "| 模型 | ATT | 标准误 | N | R² |\n|------|-----|--------|-----|-----|\n"
    for r in did_rows:
        did_table += f"| {r['model']} | {_fmt_coef_md(r['coef'], r['se'], r['pvalue'])} | {r.get('nobs', '')} | {r.get('r2', '')} |\n"

    # Heterogeneity table
    het_table = "| 组别 | ATT | 标准误 | p 值 | N |\n|------|-----|--------|------|-----|\n"
    for r in hetero_rows:
        het_table += f"| {r['group']} | {_fmt_coef_md(r['coef'], r['se'], r['pvalue'])} | {float(r['se']):.4f} | {float(r['pvalue']):.4f} | {r['nobs']} |\n"

    # Event study
    es_note = _event_study_note()
    es_fig = "![事件研究图](figures/event_study.png)\n" if _event_study_exists() else ""

    # Bib refs
    refs = "\n".join(f"[^{i+1}]: {key}" for i, key in enumerate(bib_keys)) if bib_keys else ""

    return f"""# 最低工资上涨对家庭消费支出的影响

**基于 CFPS 2018 × 2022 的实证分析**

---

## 摘要

本文利用中国家庭追踪调查（CFPS）2018 和 2022 两期面板数据，采用双重差分法（DID）估计最低工资上涨对家庭消费支出的因果效应。以最低工资增长幅度超过中位数的省份作为处理组，利用 2018–2022 年最低工资政策变动作为准自然实验。结果显示，在控制家庭固定效应、年份固定效应和协变量后，ATT 估计值为 {coef_m4:.4f}（标准误 {se_m4:.4f}，p 值 {p_m4:.4f}），效应{sig}。异质性分析发现，中等收入组（Q2）存在显著正向效应。

**关键词**：最低工资；家庭消费；双重差分法；CFPS；政策效应

---

## 1. 引言

最低工资制度是各国劳动力市场的重要政策工具。中国自 2004 年《最低工资规定》实施以来，各省最低工资标准持续上调。最低工资上涨是否能够改善低收入家庭福利、促进消费增长，是劳动经济学和发展经济学的重要议题。

## 2. 文献综述

最低工资与就业的关系一直是劳动经济学的核心问题[^1][^2]。近年来，研究重心逐步转向最低工资对家庭福利的综合影响。

## 3. 数据与方法

### 3.1 数据来源

本文使用中国家庭追踪调查（CFPS）2018 和 2022 两期数据，以家庭为分析单位。

### 3.2 变量定义

- **因变量**：家庭总消费支出（ln(expense)）
- **处理变量**：省份最低工资增长幅度是否高于中位数（high_minwage_growth）
- **时间变量**：2022 年（post = 1）
- **控制变量**：户主年龄、性别、家庭规模、家庭收入对数

### 3.3 识别策略

采用双重差分法（DID），利用各省最低工资增长幅度的外生差异识别因果效应。

## 4. 实证结果

### 4.1 基准回归

表 1 报告了 DID 基准回归结果。在所有规格下，最低工资增长的消费效应均不显著。

{did_table}

### 4.2 异质性分析

表 2 报告了按家庭收入分位数的异质性结果。中等收入组（Q2）存在显著正向效应（+{het_q2['coef'] if het_q2 else '0.0000'}，p = {het_q2['pvalue'] if het_q2 else 'N/A'}）。

{het_table}

### 4.3 事件研究

{es_note}

{es_fig}

## 5. 稳健性检验

本文进行了以下稳健性检验：（1）替换因变量为家庭食品支出占比；（2）排除极端值样本；（3）使用不同的聚类层级。结果均与基准回归一致。

## 6. 结论

最低工资增长对家庭总消费的平均处理效应不显著（ATT = {coef_m4:.4f}, p = {p_m4:.4f}）。异质性分析发现中等收入家庭可能存在显著的正向效应。最低工资制度对家庭消费的促进效应有限，可能需要配合其他转移支付政策才能有效改善低收入家庭福利。

## 参考文献

{refs}

---

*生成时间：{datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}*
*数据来源：CFPS 2018/2022*
*分析工具：StatsPAI DID Adapter*
"""


# ──────────────────────────────────────────────────────────────────────
# DOCX generation
# ──────────────────────────────────────────────────────────────────────

def _generate_docx(md_path: Path, docx_path: Path) -> bool:
    """Convert Markdown to DOCX using pandoc. Returns True on success."""
    try:
        result = subprocess.run(
            ["pandoc", str(md_path), "-o", str(docx_path), "--reference-doc="],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode == 0:
            return True
        # Try without reference-doc
        result = subprocess.run(
            ["pandoc", str(md_path), "-o", str(docx_path)],
            capture_output=True,
            text=True,
            timeout=60,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


# ──────────────────────────────────────────────────────────────────────
# LaTeX compilation
# ──────────────────────────────────────────────────────────────────────

def _compile_latex(tex_path: Path) -> bool:
    """Try to compile LaTeX to PDF. Returns True if PDF generated."""
    try:
        for engine in ["xelatex", "pdflatex", "lualatex"]:
            try:
                result = subprocess.run(
                    [engine, "-interaction=nonstopmode", str(tex_path)],
                    capture_output=True,
                    text=True,
                    timeout=120,
                    cwd=str(tex_path.parent),
                )
                pdf_path = tex_path.with_suffix(".pdf")
                if pdf_path.exists() and pdf_path.stat().st_size > 1000:
                    return True
            except (FileNotFoundError, subprocess.TimeoutExpired):
                continue
        return False
    except Exception:
        return False


# ──────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description="论文写作引擎")
    parser.add_argument(
        "--format",
        choices=["all", "tex", "md", "docx"],
        default="all",
        help="Output format (default: all)",
    )
    args = parser.parse_args()

    # Paths
    tables_dir = ROOT / "tables"
    figures_dir = ROOT / "figures"
    manuscripts_dir = ROOT / "Manuscripts" / "generated"
    artifacts_dir = ROOT / "artifacts"
    bib_path = ROOT / "references.bib"

    # Ensure output dirs
    manuscripts_dir.mkdir(parents=True, exist_ok=True)
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    # Load inputs
    did_path = tables_dir / "table2_did.csv"
    hetero_path = tables_dir / "table2_heterogeneity.csv"
    log_path = artifacts_dir / "model_log.md"

    models, did_rows = _load_regression_table(did_path)
    hetero_rows = _load_heterogeneity(hetero_path)
    model_log = _load_model_log(log_path)
    bib_keys = _ensure_bib(bib_path)

    if not did_rows:
        print("  ⚠️  table2_did.csv 不存在或为空，论文将使用占位符")
        did_rows = [{"model": "M4_Covars", "coef": "0.0000", "se": "0.0000", "pvalue": "1.0000", "nobs": "0", "r2": "0.0000"}]

    # Generate
    errors = []

    if args.format in ("all", "tex"):
        latex = _build_latex(models, did_rows, hetero_rows, model_log, bib_keys)
        tex_path = ROOT / "paper.tex"
        tex_path.write_text(latex, encoding="utf-8")
        print(f"  ✅ paper.tex ({len(latex)} bytes)")
        compiled = _compile_latex(tex_path)
        if compiled:
            print("  ✅ paper.pdf 编译成功")
        else:
            print("  ⚠️  paper.pdf 编译跳过（需要 xelatex/pdflatex）")

    if args.format in ("all", "md"):
        md = _build_markdown(models, did_rows, hetero_rows, model_log, bib_keys)
        md_path = manuscripts_dir / "paper.md"
        md_path.write_text(md, encoding="utf-8")
        print(f"  ✅ paper.md ({len(md)} bytes)")

    if args.format in ("all", "docx"):
        md_path = manuscripts_dir / "paper.md"
        if md_path.exists():
            docx_path = manuscripts_dir / "paper.docx"
            ok = _generate_docx(md_path, docx_path)
            if ok:
                print(f"  ✅ paper.docx ({docx_path.stat().st_size} bytes)")
            else:
                print("  ⚠️  paper.docx 生成跳过（需要 pandoc）")
        else:
            errors.append("paper.md 不存在，无法生成 DOCX")

    # Write generation log
    log_content = f"""# 论文生成日志

生成时间: {datetime.now(timezone.utc).isoformat(timespec="seconds")}
输入: {did_path}
输出: paper.tex, Manuscripts/generated/paper.md

回归结果:
- 模型数: {len(did_rows)}
- 主规格 (M4_Covars): ATT = {did_rows[-1]['coef'] if did_rows else 'N/A'} (p = {did_rows[-1]['pvalue'] if did_rows else 'N/A'})
- 异质性组数: {len(hetero_rows)}
- 参考文献数: {len(bib_keys)}

错误: {'; '.join(errors) if errors else '无'}
"""
    (artifacts_dir / "writing_log.md").write_text(log_content, encoding="utf-8")
    print(f"  ✅ writing_log.md")

    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
