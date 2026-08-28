"""Describe the session CSV for the data_desc chapter.

Reads ``state.csv_path``. Does not invent CHARLS or other datasets.
"""
from __future__ import annotations

from typing import Any, Mapping

# Wide CSVs (castle-style) keep a bounded describe table.
_EDA_COL_CAP = 40


def _fmt(value: Any) -> str:
    if value is None:
        return "—"
    if isinstance(value, float):
        return f"{value:.4g}"
    return str(value)


def compute_csv_eda(state: Mapping[str, Any]) -> tuple[str, str]:
    """Return (data_summary, markdown describe table) from the uploaded CSV."""
    csv_path = state.get("csv_path")
    if not csv_path:
        return "", ""
    try:
        import pandas as pd

        header = pd.read_csv(csv_path, nrows=0)
        all_cols = [str(c) for c in header.columns]
        k = len(all_cols)
        cols = all_cols[:_EDA_COL_CAP]
        df = pd.read_csv(csv_path, usecols=cols)
    except Exception:
        return "", ""
    if df.empty and k == 0:
        return "", ""

    n = len(df)
    col_list = ", ".join(cols)
    if k > _EDA_COL_CAP:
        summary = (
            f"{n} 行 × {k} 列（描述统计列上限 {_EDA_COL_CAP}）；列：{col_list} …"
        )
    else:
        summary = f"{n} 行 × {k} 列；列：{col_list}"

    lines = [
        "表 1 描述统计（由上传 CSV 计算，非占位）",
        "",
        "| 变量 | N | 均值 | 标准差 | 最小 | 最大 | 缺失 |",
        "|---|---|---|---|---|---|---|",
    ]
    for col in cols:
        s = df[col]
        numeric = False
        try:
            numeric = bool(pd.api.types.is_numeric_dtype(s))
        except Exception:
            numeric = False
        count = int(s.count())
        missing = int(s.isna().sum())
        if numeric and count:
            mean = float(s.mean())
            std = float(s.std()) if count > 1 else None
            lo = float(s.min())
            hi = float(s.max())
        else:
            mean = std = lo = hi = None
        lines.append(
            f"| {col} | {count} | {_fmt(mean)} | {_fmt(std)} | {_fmt(lo)} | {_fmt(hi)} | {missing} |"
        )
    if k > _EDA_COL_CAP:
        lines.append(f"| … | 其余 {k - _EDA_COL_CAP} 列未列入本表 | — | — | — | — | — |")
    return summary, "\n".join(lines)
