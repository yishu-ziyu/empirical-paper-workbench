"""Describe the session CSV for the data_desc chapter.

Reads ``state.csv_path``. Does not invent CHARLS or other datasets.
"""
from __future__ import annotations

from typing import Any, Mapping


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

        df = pd.read_csv(csv_path)
    except Exception:
        return "", ""
    if df.empty and len(df.columns) == 0:
        return "", ""

    n, k = len(df), len(df.columns)
    cols = ", ".join(str(c) for c in df.columns)
    summary = f"{n} 行 × {k} 列；列：{cols}"

    lines = [
        "表 1 描述统计（由上传 CSV 计算，非占位）",
        "",
        "| 变量 | N | 均值 | 标准差 | 最小 | 最大 | 缺失 |",
        "|---|---|---|---|---|---|---|",
    ]
    for col in df.columns:
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
    return summary, "\n".join(lines)
