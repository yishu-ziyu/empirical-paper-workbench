#!/usr/bin/env python3
"""
Generate the current faceted manuscript redraw for Fig5-1.

The script also keeps a dated candidate copy for visual-review traceability.
"""
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib
import matplotlib.font_manager as fm
import numpy as np
from matplotlib.font_manager import FontProperties

matplotlib.use("Agg")
import matplotlib.pyplot as plt


FIGURE_DIR = Path(__file__).resolve().parent
ROOT = FIGURE_DIR.parents[1]
PANEL_MAIN = ROOT / "03_results" / "panel_main"
CANDIDATE_DIR = FIGURE_DIR / "candidates" / "figure_review_2026-04-29"
ARCHIVE_DIR = FIGURE_DIR / "archive" / "replaced_2026-05-05_split_figures"
SOURCE_CSV = PANEL_MAIN / "table5_1_baseline_iv.csv"
COMBINED_STEM = "Fig5_1_Faceted_CoreOutcomes"
CANDIDATE_STEM = "Candidate_Fig5_1_Faceted_CoreOutcomes"

OUTCOME_ORDER = ["ln_wage", "manu_dummy", "ISEI_score", "part_time"]
OUTCOME_LABELS = {
    "ln_wage": "工资对数",
    "manu_dummy": "制造业就业",
    "ISEI_score": "ISEI 得分",
    "part_time": "兼职就业",
}
PANEL_LABELS = ["(a)", "(b)", "(c)", "(d)"]
SPLIT_OUTPUTS = {
    "ln_wage": ("Fig5_1a_Wage_IV_Coefficient", "图5-1a 工资对数"),
    "manu_dummy": ("Fig5_1b_Manufacturing_IV_Coefficient", "图5-1b 制造业就业"),
    "ISEI_score": ("Fig5_1c_ISEI_IV_Coefficient", "图5-1c ISEI 得分"),
    "part_time": ("Fig5_1d_PartTime_IV_Coefficient", "图5-1d 兼职就业"),
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def as_float(value: str) -> float:
    return float(value) if value not in ("", None) else np.nan


def find_chinese_font() -> tuple[str, str]:
    preferred = [
        "STHeiti",
        "PingFang SC",
        "PingFang HK",
        "Heiti TC",
        "Hiragino Sans GB",
        "Songti SC",
        "Arial Unicode MS",
        "Kaiti SC",
    ]
    available = {f.name for f in fm.fontManager.ttflist}
    for font_name in preferred:
        if font_name in available:
            font_path = fm.findfont(fm.FontProperties(family=font_name), fallback_to_default=False)
            return font_name, font_path
    raise RuntimeError("未找到可用中文字体，请安装 Songti SC / PingFang SC / Arial Unicode MS。")


CHINESE_FONT_NAME, CHINESE_FONT_PATH = find_chinese_font()


def cjk_font(size: float = 10, weight: str = "normal") -> FontProperties:
    return FontProperties(fname=CHINESE_FONT_PATH, size=size, weight=weight)


plt.rcParams.update(
    {
        "font.family": CHINESE_FONT_NAME,
        "font.sans-serif": [CHINESE_FONT_NAME, "DejaVu Sans"],
        "font.size": 10,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.unicode_minus": False,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    }
)


def significance_marker(pvalue: float) -> str:
    if pvalue < 0.01:
        return "***"
    if pvalue < 0.05:
        return "**"
    if pvalue < 0.1:
        return "*"
    return ""


def style_axis(ax) -> None:
    ax.tick_params(axis="both", labelsize=8.5, colors="#222222")
    ax.tick_params(axis="y", length=0)
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontproperties(cjk_font(8.5))
    ax.grid(axis="x", alpha=0.18, linewidth=0.7, color="#6B7280")
    ax.grid(axis="y", visible=False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_color("#444444")
    ax.spines["bottom"].set_linewidth(0.8)


def set_panel_limits(outcome: str, lower: float, upper: float) -> tuple[float, float]:
    span = upper - lower
    pad = max(span * 0.42, 0.035)
    x_min = min(lower, 0) - pad
    x_max = max(upper, 0) + pad
    if outcome == "ISEI_score":
        x_min = min(x_min, -0.1)
    return x_min, x_max


def draw_single_axis(ax, row: dict[str, object], title: str) -> None:
    marker_color = "#2F4A5A"
    outcome = str(row["outcome"])
    coef = float(row["coef"])
    lower = float(row["ci_lower_95"])
    upper = float(row["ci_upper_95"])
    pvalue = float(row["pvalue"])
    x_min, x_max = set_panel_limits(outcome, lower, upper)
    pad = (x_max - x_min) * 0.04

    ax.axvline(0, color="#222222", linewidth=0.9, zorder=0)
    ax.errorbar(
        [coef],
        [0],
        xerr=[[coef - lower], [upper - coef]],
        fmt="o",
        markersize=6.8,
        capsize=4,
        capthick=1.2,
        color=marker_color,
        ecolor="#222222",
        elinewidth=1.25,
        zorder=3,
    )
    stars = significance_marker(pvalue)
    label_x = upper + pad if coef >= 0 else lower - pad
    label_ha = "left" if coef >= 0 else "right"
    ax.text(
        label_x,
        0,
        f"{coef:.3f}{stars}",
        va="center",
        ha=label_ha,
        fontproperties=cjk_font(9.2, "bold"),
        color="#222222",
    )
    if title:
        ax.set_title(title, loc="left", pad=8, fontproperties=cjk_font(11, "bold"))
    ax.set_yticks([0])
    ax.set_yticklabels(["机器人暴露对数"], fontproperties=cjk_font(8.8))
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(-0.48, 0.48)
    ax.set_xlabel("IV-2SLS 系数及 95% 置信区间", fontproperties=cjk_font(9))
    ax.text(
        0.0,
        -0.34,
        f"N={int(row['nobs']):,}；F={float(row['first_stage_f']):.2f}",
        transform=ax.get_yaxis_transform(),
        va="center",
        ha="left",
        fontproperties=cjk_font(8.2),
        color="#555555",
    )
    style_axis(ax)


def prepare_rows() -> list[dict[str, object]]:
    rows = [r for r in read_csv(SOURCE_CSV) if r["variable"] == "ln_robot"]
    by_outcome = {r["outcome"]: r for r in rows}
    missing = [outcome for outcome in OUTCOME_ORDER if outcome not in by_outcome]
    if missing:
        raise ValueError(f"table5_1_baseline_iv.csv 缺少主结果行: {missing}")

    prepared: list[dict[str, object]] = []
    for outcome in OUTCOME_ORDER:
        row = by_outcome[outcome]
        coef = as_float(row["coef"])
        se = as_float(row["se"])
        pvalue = as_float(row["pvalue"])
        lower = coef - 1.96 * se
        upper = coef + 1.96 * se
        prepared.append(
            {
                "outcome": outcome,
                "outcome_label": OUTCOME_LABELS[outcome],
                "variable": row["variable"],
                "variable_label": row["variable_label"],
                "coef": coef,
                "se": se,
                "ci_lower_95": lower,
                "ci_upper_95": upper,
                "pvalue": pvalue,
                "stars": row.get("stars") or significance_marker(pvalue),
                "nobs": int(float(row["nobs"])),
                "r2": as_float(row["r2"]),
                "first_stage_f": as_float(row["first_stage_f"]),
                "dwh_p": as_float(row["dwh_p"]),
                "source_csv": str(SOURCE_CSV.relative_to(ROOT)),
            }
        )
    return prepared


def write_source_data(rows: list[dict[str, object]]) -> None:
    CANDIDATE_DIR.mkdir(parents=True, exist_ok=True)
    out_path = CANDIDATE_DIR / f"{CANDIDATE_STEM}_source.csv"
    fields = [
        "outcome",
        "outcome_label",
        "variable",
        "variable_label",
        "coef",
        "se",
        "ci_lower_95",
        "ci_upper_95",
        "pvalue",
        "stars",
        "nobs",
        "r2",
        "first_stage_f",
        "dwh_p",
        "source_csv",
    ]
    with out_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def draw_faceted_coefficients(rows: list[dict[str, object]]) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(9.2, 5.7))

    for ax, panel, row in zip(axes.ravel(), PANEL_LABELS, rows):
        draw_single_axis(ax, row, f"{panel} {row['outcome_label']}")

    fig.subplots_adjust(wspace=0.34, hspace=0.58)
    CANDIDATE_DIR.mkdir(parents=True, exist_ok=True)
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(ARCHIVE_DIR / f"{COMBINED_STEM}.pdf", format="pdf", dpi=300, bbox_inches="tight")
    fig.savefig(ARCHIVE_DIR / f"{COMBINED_STEM}.png", format="png", dpi=300, bbox_inches="tight")
    fig.savefig(CANDIDATE_DIR / f"{CANDIDATE_STEM}.pdf", format="pdf", dpi=300, bbox_inches="tight")
    fig.savefig(CANDIDATE_DIR / f"{CANDIDATE_STEM}.png", format="png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def draw_split_coefficients(rows: list[dict[str, object]]) -> None:
    for row in rows:
        outcome = str(row["outcome"])
        stem, _ = SPLIT_OUTPUTS[outcome]
        fig, ax = plt.subplots(figsize=(5.5, 2.25))
        draw_single_axis(ax, row, "")
        fig.tight_layout()
        fig.savefig(FIGURE_DIR / f"{stem}.pdf", format="pdf", dpi=300, bbox_inches="tight")
        fig.savefig(FIGURE_DIR / f"{stem}.png", format="png", dpi=300, bbox_inches="tight")
        plt.close(fig)


def main() -> None:
    rows = prepare_rows()
    write_source_data(rows)
    draw_faceted_coefficients(rows)
    draw_split_coefficients(rows)
    for row in rows:
        stem, _ = SPLIT_OUTPUTS[str(row["outcome"])]
        print(FIGURE_DIR / f"{stem}.png")
    print(CANDIDATE_DIR / f"{CANDIDATE_STEM}_source.csv")


if __name__ == "__main__":
    main()
