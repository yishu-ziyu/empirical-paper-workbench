#!/usr/bin/env python3
"""06_writing.py — 论文写作引擎（StatsEngine 版本）。

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
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from runtime.stats_engine import StatsEngine


def main() -> int:
    parser = argparse.ArgumentParser(description="论文写作引擎")
    parser.add_argument(
        "--format",
        choices=["all", "tex", "md", "docx"],
        default="all",
        help="Output format (default: all)",
    )
    parser.add_argument(
        "--title",
        default="",
        help="Paper title (default: from StatsEngine template)",
    )
    args = parser.parse_args()

    engine = StatsEngine(project_root=PROJECT_ROOT)

    if args.format in ("all", "tex"):
        engine.export_latex(title=args.title or None)
        tex_path = PROJECT_ROOT / "paper.tex"
        print(f"  ✅ paper.tex")

        # Try to compile LaTeX
        for latex_engine in ["xelatex", "pdflatex", "lualatex"]:
            try:
                result = subprocess.run(
                    [latex_engine, "-interaction=nonstopmode", str(tex_path)],
                    capture_output=True, text=True, timeout=120,
                    cwd=str(tex_path.parent),
                )
                pdf_path = tex_path.with_suffix(".pdf")
                if pdf_path.exists() and pdf_path.stat().st_size > 1000:
                    print(f"  ✅ paper.pdf 编译成功 ({latex_engine})")
                    break
            except (FileNotFoundError, subprocess.TimeoutExpired):
                continue
        else:
            print("  ⚠️  paper.pdf 编译跳过（需要 xelatex/pdflatex）")

    if args.format in ("all", "md"):
        engine.export_markdown(title=args.title or None)
        md_path = PROJECT_ROOT / "Manuscripts" / "generated" / "paper.md"
        print(f"  ✅ paper.md")

    if args.format in ("all", "docx"):
        md_path = PROJECT_ROOT / "Manuscripts" / "generated" / "paper.md"
        docx_path = PROJECT_ROOT / "Manuscripts" / "generated" / "paper.docx"
        if md_path.exists():
            engine.export_markdown(title=args.title or None)  # ensure md is fresh
            result = subprocess.run(
                ["pandoc", str(md_path), "-o", str(docx_path)],
                capture_output=True, text=True, timeout=60,
            )
            if result.returncode == 0:
                print(f"  ✅ paper.docx ({docx_path.stat().st_size} bytes)")
            else:
                print(f"  ⚠️  paper.docx 生成跳过（pandoc 错误: {result.stderr[:200]}）")
        else:
            print("  ⚠️  paper.md 不存在，无法生成 DOCX")

    # Write generation log
    did_path = PROJECT_ROOT / "tables" / "table2_did.csv"
    try:
        import csv
        with open(did_path, newline="", encoding="utf-8-sig") as fh:
            did_rows = list(csv.DictReader(fh))
    except Exception:
        did_rows = []

    hetero_path = PROJECT_ROOT / "tables" / "table2_heterogeneity.csv"
    try:
        import csv
        with open(hetero_path, newline="", encoding="utf-8-sig") as fh:
            hetero_rows = list(csv.DictReader(fh))
    except Exception:
        hetero_rows = []

    log_content = f"""# 论文生成日志

生成时间: {datetime.now(timezone.utc).isoformat(timespec="seconds")}
输入: {did_path}
输出: paper.tex, Manuscripts/generated/paper.md

回归结果:
- 模型数: {len(did_rows)}
- 异质性组数: {len(hetero_rows)}

生成工具: StatsEngine
"""
    (PROJECT_ROOT / "artifacts" / "writing_log.md").write_text(log_content, encoding="utf-8")
    print(f"  ✅ writing_log.md")

    return 0


if __name__ == "__main__":
    sys.exit(main())
