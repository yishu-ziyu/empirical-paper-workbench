#!/usr/bin/env python3
"""35_integrity_audit.py — 论文数字一致性审计。

检查：
  1. paper.md 中的所有 4 位+小数必须能在 tables/ 的 CSV 中找到（容差 0.001）
  2. 禁止出现已知捏造指纹（E-value=1.18, Acemoglu 0.5% 等）
  3. 回归表必须存在

用法:
    python3 scripts/35_integrity_audit.py
    python3 scripts/35_integrity_audit.py --paper path/to/paper.md

退出码:
    0 = CLEAN（所有数字可追溯，无禁止模式）
    1 = BLOCKED（有未登记数字或禁止模式）
    2 = 工具错误
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# ── 已知捏造指纹 ──────────────────────────────────────────────

FORBIDDEN_PATTERNS: list[tuple[str, str, str]] = [
    # (pattern, severity, teaching_note)
    ("E-value=1.18", "BLOCKER", "E-value 必须从实际数据计算，禁止写印象数字"),
    ("Acemoglu 0.5%", "BLOCKER", "Acemoglu & Restrepo 的弹性需要查原论文"),
    ("Dauth 0.4%", "BLOCKER", "Dauth et al. 的弹性需要查原论文"),
    ("Sobel 30/70%", "BLOCKER", "Sobel test 中介比例必须实际运行"),
    ("Baron-Kenny 1986", "BLOCKER", "Baron & Kenny 1986 未在本研究使用"),
    ("2005-2007 基期", "BLOCKER", "Bartik 工具变量基期需在 design 中确认"),
    ("剔除 2014 年", "BLOCKER", "剔除某年的稳健性检验必须真的跑过"),
    ("OLS 系数被高估", "BLOCKER", "方向性判断必须基于实际结果，禁止凭印象"),
]

# ── 数字提取 ──────────────────────────────────────────────────

NUMBER_RE = re.compile(r"\d+\.\d{3,}")


def _extract_numbers(text: str) -> set[str]:
    """Extract all 4+ decimal numbers from text."""
    return set(NUMBER_RE.findall(text))


def _load_table_numbers(tables_dir: Path) -> set[str]:
    """Extract all numbers from CSV tables."""
    nums: set[str] = set()
    for csv_path in tables_dir.glob("*.csv"):
        try:
            text = csv_path.read_text(encoding="utf-8")
            nums.update(NUMBER_RE.findall(text))
        except Exception:
            pass
    return nums


# ── 审计维度 ──────────────────────────────────────────────────

def audit_table_numbers(paper_path: Path, tables_dir: Path) -> list[dict]:
    """Check that every number in paper.md appears in regression tables."""
    findings = []

    if not paper_path.exists():
        return [{"severity": "BLOCKER", "id": "ANC-001",
                 "what": f"Paper not found: {paper_path}",
                 "fix": f"Run 06_writing.py first to generate {paper_path}"}]

    if not tables_dir.exists() or not list(tables_dir.glob("*.csv")):
        return [{"severity": "BLOCKER", "id": "ANC-002",
                 "what": "No regression tables found in tables/",
                 "fix": "Run 05_causal_analysis to generate regression tables"}]

    paper_text = paper_path.read_text(encoding="utf-8")
    table_nums = _load_table_numbers(tables_dir)

    paper_nums = _extract_numbers(paper_text)
    if not paper_nums:
        return [{"severity": "INFO", "id": "ANC-000",
                 "what": "No 4+ decimal numbers found in paper — nothing to audit"}]

    unregistered = []
    for pn in sorted(paper_nums, key=float):
        pv = float(pn)
        found = any(abs(pv - float(tn)) < 0.001 for tn in table_nums)
        if not found:
            unregistered.append(pn)

    if unregistered:
        findings.append({
            "severity": "BLOCKER",
            "id": "ANC-003",
            "what": f"{len(unregistered)} number(s) in paper not traceable to tables: {unregistered[:10]}",
            "fix": "Either register these numbers in claim_register.md or correct the paper text",
            "teaching": "Every 4+ decimal number in the paper must have a source in the regression tables. LLM-generated 'approximations' rarely match exactly.",
        })

    if not findings:
        findings.append({"severity": "INFO", "id": "ANC-000",
                         "what": f"All {len(paper_nums)} numbers in paper are traceable to tables"})

    return findings


def audit_forbidden_patterns(paper_path: Path) -> list[dict]:
    """Check for known fabrication fingerprints."""
    findings = []

    if not paper_path.exists():
        return []

    text = paper_path.read_text(encoding="utf-8").lower()

    for pattern, severity, note in FORBIDDEN_PATTERNS:
        if pattern.lower() in text:
            findings.append({
                "severity": severity,
                "id": f"FORB-{len(findings)+1:03d}",
                "what": f"Forbidden pattern '{pattern}' found in paper",
                "fix": f"Remove '{pattern}' and replace with verified numbers from evidence",
                "teaching": note,
            })

    if not findings:
        findings.append({"severity": "INFO", "id": "FORB-000",
                         "what": "No forbidden fabrication patterns found"})

    return findings


def audit_table_consistency(tables_dir: Path) -> list[dict]:
    """Check that regression tables have consistent structure."""
    findings = []

    did_table = tables_dir / "table2_did.csv"
    hetero_table = tables_dir / "table2_heterogeneity.csv"

    if did_table.exists():
        import csv
        with open(did_table, newline="", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
        if rows:
            required_cols = {"model", "coef", "se", "pvalue", "nobs"}
            actual_cols = set(rows[0].keys())
            missing = required_cols - actual_cols
            if missing:
                findings.append({
                    "severity": "BLOCKER",
                    "id": "CONS-001",
                    "what": f"table2_did.csv missing columns: {missing}",
                    "fix": "Regenerate table with all required columns",
                    "teaching": "Regression tables must have consistent schema for downstream consumption",
                })

    if hetero_table.exists():
        import csv
        with open(hetero_table, newline="", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
        if rows:
            required_cols = {"group", "coef", "se", "pvalue", "nobs"}
            actual_cols = set(rows[0].keys())
            missing = required_cols - actual_cols
            if missing:
                findings.append({
                    "severity": "BLOCKER",
                    "id": "CONS-002",
                    "what": f"table2_heterogeneity.csv missing columns: {missing}",
                    "fix": "Regenerate table with all required columns",
                    "teaching": "Heterogeneity tables must have consistent schema",
                })

    if not findings:
        findings.append({"severity": "INFO", "id": "CONS-000",
                         "what": "All regression tables have consistent structure"})

    return findings


# ── Main ──────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description="论文数字一致性审计")
    parser.add_argument("--paper", default="Manuscripts/generated/paper.md",
                        help="Path to paper markdown (default: Manuscripts/generated/paper.md)")
    parser.add_argument("--tables", default="tables",
                        help="Path to tables directory (default: tables)")
    parser.add_argument("--write", action="store_true",
                        help="Write audit report to artifacts/integrity_audit_report.md")
    args = parser.parse_args()

    paper_path = ROOT / args.paper
    tables_dir = ROOT / args.tables

    # Run all audit dimensions
    all_findings = []
    all_findings.extend(audit_table_numbers(paper_path, tables_dir))
    all_findings.extend(audit_forbidden_patterns(paper_path))
    all_findings.extend(audit_table_consistency(tables_dir))

    # Determine verdict
    blockers = [f for f in all_findings if f["severity"] == "BLOCKER"]
    warnings = [f for f in all_findings if f["severity"] == "WARNING"]
    infos = [f for f in all_findings if f["severity"] == "INFO"]

    # Print report
    print("=" * 60)
    print("  Integrity Audit Report")
    print("=" * 60)
    print(f"  Paper:    {paper_path}")
    print(f"  Tables:   {tables_dir}")
    print(f"  Findings: {len(blockers)} blocker(s), {len(warnings)} warning(s), {len(infos)} info")
    print()

    for f in all_findings:
        icon = {"BLOCKER": "❌", "WARNING": "⚠️", "INFO": "✅"}.get(f["severity"], "?")
        print(f"  {icon} [{f['id']}] {f['what']}")
        if f.get("fix"):
            print(f"      Fix: {f['fix']}")
        if f.get("teaching"):
            print(f"      Note: {f['teaching']}")
        print()

    verdict = "CLEAN" if not blockers else "BLOCKED"
    print(f"  Verdict: {verdict}")
    print("=" * 60)

    # Write report if requested
    if args.write:
        report_path = ROOT / "artifacts" / "integrity_audit_report.md"
        lines = [
            "# Integrity Audit Report",
            f"",
            f"**Verdict**: {verdict}",
            f"**Paper**: {paper_path}",
            f"**Tables**: {tables_dir}",
            f"",
            f"## Findings ({len(blockers)} blockers, {len(warnings)} warnings)",
            f"",
        ]
        for f in all_findings:
            icon = {"BLOCKER": "❌", "WARNING": "⚠️", "INFO": "✅"}.get(f["severity"], "?")
            lines.append(f"### {icon} [{f['id']}] {f['severity']}")
            lines.append(f"")
            lines.append(f"{f['what']}")
            if f.get("fix"):
                lines.append(f"")
                lines.append(f"**Fix**: {f['fix']}")
            if f.get("teaching"):
                lines.append(f"")
                lines.append(f"**Note**: {f['teaching']}")
            lines.append(f"")

        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text("\n".join(lines), encoding="utf-8")
        print(f"  Report written: {report_path}")

    return 0 if not blockers else 1


if __name__ == "__main__":
    sys.exit(main())
