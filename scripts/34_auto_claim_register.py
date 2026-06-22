#!/usr/bin/env python3
"""34_auto_claim_register.py — Auto-populate claim_register.md from regression tables.

Reads all CSV files in tables/, extracts numeric values (coefficients, SE,
p-values, N, R², CI bounds), and generates claim_register.md entries.

Rules:
  1. Deduplicate — skip numbers already in claim_register.md
  2. Preserve existing manual entries — append only new ones
  3. Use monotonic auto_id (C-NNN) continuing from last existing entry
  4. Write to evidence/claim_register.md
  5. Update evidence/evidence_bank.md §4 with regression table references
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TABLES_DIR = ROOT / "tables"
EVIDENCE_DIR = ROOT / "evidence"
CLAIM_REGISTER = EVIDENCE_DIR / "claim_register.md"
EVIDENCE_BANK = EVIDENCE_DIR / "evidence_bank.md"

# ── Section mapping by table file ──────────────────────────────────────

SECTION_MAP = {
    "table2_did.csv": "§4.1",
    "table2_did_multi_spec.csv": "§5",
    "table2_heterogeneity.csv": "§4.2",
    "table_dml.csv": "§5",
    "table_glm.csv": "§5",
    "table_iv.csv": "§5",
    "table_panel.csv": "§5",
    "table_psm.csv": "§5",
}

# ── Columns to extract ─────────────────────────────────────────────────

NUMERIC_COLUMNS = {
    "coef", "se", "pvalue", "ci_lower", "ci_upper",
    "nobs", "r2", "pseudo_r2", "f_stat", "partial_r2",
    "n_units", "n_treated", "n_control", "n_matched",
    "aic",
}

# ── Claim register helpers ─────────────────────────────────────────────

CLAIM_HEADER = """# Claim Register

Auto-generated from regression tables. Manual entries may be interleaved.

| ID | Section | Claim | Value | Source | Path | Status | Type | Note |
|----|---------|-------|-------|--------|------|--------|------|------|
"""


def _parse_existing_claims(text: str) -> tuple[set[str], set[str], int]:
    """Extract existing claim IDs, registered values, and last auto_id number."""
    existing_ids: set[str] = set()
    existing_values: set[str] = set()
    last_auto_num = 0

    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("| C-"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 10:
            continue
        claim_id = parts[1]
        value = parts[4]
        existing_ids.add(claim_id)
        existing_values.add(value)
        # Track highest auto_id number
        m = re.match(r"C-(\d+)", claim_id)
        if m:
            last_auto_num = max(last_auto_num, int(m.group(1)))

    return existing_ids, existing_values, last_auto_num


def _next_auto_id(existing_ids: set[str], last_num: int) -> str:
    """Generate next monotonic auto_id."""
    n = last_num + 1
    while f"C-{n:03d}" in existing_ids:
        n += 1
    return f"C-{n:03d}"


def _format_value(val: str) -> str:
    """Format numeric value for display."""
    try:
        f = float(val)
        if f == int(f) and abs(f) > 1e-9:
            return str(int(f))
        return val
    except ValueError:
        return val


def _column_label(col: str) -> str:
    """Human-readable column label."""
    labels = {
        "coef": "coefficient",
        "se": "standard error",
        "pvalue": "p-value",
        "ci_lower": "CI lower bound",
        "ci_upper": "CI upper bound",
        "nobs": "N (observations)",
        "r2": "R²",
        "pseudo_r2": "pseudo-R²",
        "f_stat": "F-statistic",
        "partial_r2": "partial R²",
        "n_units": "N (units)",
        "n_treated": "N (treated)",
        "n_control": "N (control)",
        "n_matched": "N (matched)",
        "aic": "AIC",
    }
    return labels.get(col, col)


def generate_claims_from_tables() -> list[dict]:
    """Read all CSV tables and generate claim dicts."""
    claims = []

    for csv_path in sorted(TABLES_DIR.glob("*.csv")):
        filename = csv_path.name
        section = SECTION_MAP.get(filename, "§5")
        table_label = filename.replace(".csv", "").replace("_", " ").title()

        try:
            with open(csv_path, newline="", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
        except Exception as e:
            print(f"  ⚠ Skipping {filename}: {e}", file=sys.stderr)
            continue

        if not rows:
            continue

        for row_idx, row in enumerate(rows):
            model_name = row.get("model", row.get("group", f"row_{row_idx}"))
            label = row.get("label", "")
            if label:
                model_display = f"{model_name} ({label})"
            else:
                model_display = model_name

            for col, val in row.items():
                if col not in NUMERIC_COLUMNS:
                    continue
                if not val or val.strip() == "":
                    continue
                try:
                    float(val)
                except ValueError:
                    continue

                claims.append({
                    "section": section,
                    "model": model_display,
                    "column": col,
                    "value": val,
                    "source_file": filename,
                    "source_path": f"$.{model_name}.{col}",
                    "type": "verbatim",
                    "note": "Auto-generated from regression output",
                })

    return claims


def build_claim_register() -> tuple[int, int]:
    """Build/update claim_register.md. Returns (added, total)."""
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

    # Read existing
    existing_text = CLAIM_REGISTER.read_text(encoding="utf-8") if CLAIM_REGISTER.exists() else ""
    existing_ids, existing_values, last_num = _parse_existing_claims(existing_text)

    # Generate new claims
    new_claims = generate_claims_from_tables()

    added = 0
    lines = []
    if not existing_text:
        lines.append(CLAIM_HEADER)
    else:
        # Keep existing content, just append new claims
        lines = existing_text.splitlines()

    for claim in new_claims:
        if claim["value"] in existing_values:
            continue

        claim_id = _next_auto_id(existing_ids, last_num)
        last_num = int(claim_id.split("-")[1])
        existing_ids.add(claim_id)
        existing_values.add(claim["value"])

        col_label = _column_label(claim["column"])
        description = f"{col_label} for {claim['model']}"
        display_value = _format_value(claim["value"])

        line = (
            f"| {claim_id} | {claim['section']} | {description} | {display_value} "
            f"| {claim['source_file']} | {claim['source_path']} | approved "
            f"| {claim['type']} | {claim['note']} |"
        )
        lines.append(line)
        added += 1

    CLAIM_REGISTER.write_text("\n".join(lines) + "\n", encoding="utf-8")
    total = len(existing_values)
    return added, total


def build_evidence_bank() -> None:
    """Update evidence_bank.md §4 with regression table references."""

    table_entries = []
    for csv_path in sorted(TABLES_DIR.glob("*.csv")):
        filename = csv_path.name
        section = SECTION_MAP.get(filename, "§5")
        table_label = filename.replace(".csv", "").replace("_", " ").title()

        # Count rows and columns
        try:
            with open(csv_path, newline="", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                fieldnames = reader.fieldnames or []
        except Exception:
            continue

        n_rows = len(rows)
        n_cols = len(fieldnames)
        numeric_cols = [c for c in fieldnames if c in NUMERIC_COLUMNS]

        table_entries.append(
            f"### {table_label}\n\n"
            f"- **File**: `tables/{filename}`\n"
            f"- **Section**: {section}\n"
            f"- **Rows**: {n_rows} | **Columns**: {n_cols}\n"
            f"- **Numeric fields**: {', '.join(numeric_cols)}\n"
            f"- **Claim register**: {n_rows * len(numeric_cols)} potential entries\n"
        )

    bank_content = f"""# Evidence Bank

## §4 回归表证据

This section documents all regression tables used as evidence sources.

{chr(10).join(table_entries)}
"""

    EVIDENCE_BANK.write_text(bank_content, encoding="utf-8")


# ── Main ───────────────────────────────────────────────────────────────

def main() -> int:
    print("=" * 60)
    print("  Auto Claim Register Builder")
    print("=" * 60)
    print(f"  Tables dir: {TABLES_DIR}")
    print(f"  Output:     {CLAIM_REGISTER}")
    print()

    if not TABLES_DIR.exists() or not list(TABLES_DIR.glob("*.csv")):
        print("  ❌ No CSV tables found in tables/", file=sys.stderr)
        return 1

    added, total = build_claim_register()
    build_evidence_bank()

    print(f"  ✅ Added {added} new entries to claim_register.md")
    print(f"  ✅ Total registered values: {total}")
    print(f"  ✅ Updated evidence_bank.md §4")
    print()
    print(f"  claim_register.md: {CLAIM_REGISTER}")
    print(f"  evidence_bank.md:  {EVIDENCE_BANK}")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
