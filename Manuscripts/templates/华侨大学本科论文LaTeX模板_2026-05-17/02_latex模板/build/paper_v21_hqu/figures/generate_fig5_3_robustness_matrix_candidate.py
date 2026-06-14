#!/usr/bin/env python3
"""
Generate a candidate all-outcome robustness matrix for the Figure 5-3 review.

The output is a review candidate only. It is intentionally written under the
candidates directory and does not replace the manuscript's current Figure 5-3.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
import matplotlib.font_manager as fm
import numpy as np
import pandas as pd
from matplotlib.font_manager import FontProperties
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle

matplotlib.use("Agg")
import matplotlib.pyplot as plt


FIGURE_DIR = Path(__file__).resolve().parent
ROOT = FIGURE_DIR.parents[1]
INPUT_CSV = ROOT / "03_results" / "panel_main" / "robustness_clean.csv"
CANDIDATE_DIR = FIGURE_DIR / "candidates" / "figure_review_2026-04-29"
OUTPUT_STEM = "Candidate_Fig5_3_AllOutcome_Robustness_Matrix"

OUTCOME_ORDER = ["ln_wage", "manu_dummy", "ISEI_score", "part_time"]
OUTCOME_LABELS = {
    "ln_wage": "工资对数",
    "manu_dummy": "制造业就业",
    "ISEI_score": "ISEI 得分",
    "part_time": "兼职就业",
}
SPEC_ORDER = ["baseline", "age_lt55", "winsor_1_99", "exclude_muni"]
SPEC_LABELS = {
    "baseline": "基准估计",
    "age_lt55": "剔除55岁及以上样本",
    "winsor_1_99": "1%缩尾处理",
    "exclude_muni": "剔除直辖市",
}

POSITIVE = "#2F6B4F"
NEGATIVE = "#A04A3A"
NEUTRAL = "#8A8F98"
GRID = "#D8DEE3"
TEXT = "#222222"


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
        "axes.unicode_minus": False,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    }
)


def significance_stars(pvalue: float) -> str:
    if pvalue < 0.01:
        return "***"
    if pvalue < 0.05:
        return "**"
    if pvalue < 0.1:
        return "*"
    return ""


def significance_alpha(pvalue: float) -> float:
    if pvalue < 0.01:
        return 0.34
    if pvalue < 0.05:
        return 0.25
    if pvalue < 0.1:
        return 0.16
    return 0.06


def coefficient_text(coef: float, pvalue: float) -> str:
    stars = significance_stars(pvalue)
    if abs(coef) >= 1:
        number = f"{coef:.2f}"
    elif abs(coef) >= 0.1:
        number = f"{coef:.3f}"
    else:
        number = f"{coef:.3f}"
    return f"{number}{stars}"


def prepare_source(df: pd.DataFrame) -> pd.DataFrame:
    source = df.copy()
    source["outcome_label"] = source["outcome"].map(OUTCOME_LABELS)
    source["spec_label"] = source["spec"].map(SPEC_LABELS)
    source["ci_low"] = source["coef"] - 1.96 * source["se"]
    source["ci_high"] = source["coef"] + 1.96 * source["se"]
    source["sign"] = np.sign(source["coef"]).astype(int)
    source["significant_10pct"] = source["pval"] < 0.1
    source["significant_5pct"] = source["pval"] < 0.05
    source["significant_1pct"] = source["pval"] < 0.01
    return source[
        [
            "outcome",
            "outcome_label",
            "spec",
            "spec_label",
            "coef",
            "se",
            "ci_low",
            "ci_high",
            "pval",
            "stars",
            "nobs",
            "sign",
            "significant_10pct",
            "significant_5pct",
            "significant_1pct",
        ]
    ]


def draw_matrix(source: pd.DataFrame) -> None:
    by_key = {(row.outcome, row.spec): row for row in source.itertuples(index=False)}
    fig, ax = plt.subplots(figsize=(10.8, 5.4))

    ax.set_xlim(-0.5, len(SPEC_ORDER) + 0.95)
    ax.set_ylim(-0.85, len(OUTCOME_ORDER) - 0.5)
    ax.invert_yaxis()

    ax.set_xticks(np.arange(len(SPEC_ORDER)))
    ax.set_xticklabels([SPEC_LABELS[s] for s in SPEC_ORDER], fontproperties=cjk_font(10))
    ax.xaxis.tick_top()
    ax.tick_params(axis="x", pad=8, length=0)

    ax.set_yticks(np.arange(len(OUTCOME_ORDER)))
    ax.set_yticklabels([OUTCOME_LABELS[o] for o in OUTCOME_ORDER], fontproperties=cjk_font(10, "bold"))
    ax.tick_params(axis="y", pad=8, length=0)

    for spine in ax.spines.values():
        spine.set_visible(False)

    row_ranges: dict[str, float] = {}
    for outcome in OUTCOME_ORDER:
        subset = source[source["outcome"] == outcome]
        max_abs = float(np.nanmax(np.abs(np.r_[subset["ci_low"].to_numpy(), subset["ci_high"].to_numpy()])))
        row_ranges[outcome] = max(max_abs, 0.01)

    for y, outcome in enumerate(OUTCOME_ORDER):
        outcome_rows = source[source["outcome"] == outcome]
        baseline = by_key[(outcome, "baseline")]
        baseline_sign = np.sign(baseline.coef)
        same_direction_count = int((np.sign(outcome_rows["coef"]) == baseline_sign).sum())
        sig_count = int((outcome_rows["pval"] < 0.1).sum())

        for x, spec in enumerate(SPEC_ORDER):
            row = by_key[(outcome, spec)]
            color = POSITIVE if row.coef > 0 else NEGATIVE if row.coef < 0 else NEUTRAL
            alpha = significance_alpha(row.pval)
            ax.add_patch(
                Rectangle(
                    (x - 0.47, y - 0.39),
                    0.94,
                    0.78,
                    facecolor=color,
                    edgecolor=GRID,
                    linewidth=0.8,
                    alpha=alpha,
                    zorder=0,
                )
            )

            scale = row_ranges[outcome]
            ci_low = np.clip(row.ci_low / scale, -1, 1)
            ci_high = np.clip(row.ci_high / scale, -1, 1)
            coef_scaled = np.clip(row.coef / scale, -1, 1)
            start = x + ci_low * 0.32
            end = x + ci_high * 0.32
            dot = x + coef_scaled * 0.32

            ax.plot([x, x], [y - 0.30, y + 0.03], color="#FFFFFF", linewidth=1.0, alpha=0.85, zorder=1)
            ax.plot([start, end], [y - 0.11, y - 0.11], color=TEXT, linewidth=1.2, solid_capstyle="round", zorder=3)
            ax.scatter([dot], [y - 0.11], s=35, color=color, edgecolor="white", linewidth=0.7, zorder=4)
            ax.text(
                x,
                y + 0.19,
                coefficient_text(row.coef, row.pval),
                ha="center",
                va="center",
                color=TEXT,
                fontproperties=cjk_font(9, "bold" if row.pval < 0.1 else "normal"),
            )

        summary = f"{same_direction_count}/4同向\n{sig_count}/4显著"
        ax.text(
            len(SPEC_ORDER) + 0.18,
            y,
            summary,
            ha="left",
            va="center",
            color=TEXT,
            fontproperties=cjk_font(9),
        )

    ax.text(
        len(SPEC_ORDER) + 0.18,
        -0.62,
        "一致性",
        ha="left",
        va="center",
        color=TEXT,
        fontproperties=cjk_font(10, "bold"),
    )

    for x in np.arange(-0.5, len(SPEC_ORDER) - 0.5 + 1, 1):
        ax.axvline(x, color="#EEF1F4", linewidth=0.7, zorder=-1)
    for y in np.arange(-0.5, len(OUTCOME_ORDER) - 0.5 + 1, 1):
        ax.axhline(y, color="#EEF1F4", linewidth=0.7, zorder=-1)

    legend_items = [
        Line2D([0], [0], marker="o", color="none", markerfacecolor=POSITIVE, markeredgecolor="white", markersize=8, label="正向系数"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor=NEGATIVE, markeredgecolor="white", markersize=8, label="负向系数"),
        Line2D([0], [0], color=TEXT, linewidth=1.3, label="95%置信区间"),
        Line2D([0], [0], color="none", marker=None, label="* p<0.10, ** p<0.05, *** p<0.01"),
    ]
    ax.legend(
        handles=legend_items,
        loc="lower center",
        bbox_to_anchor=(0.5, -0.22),
        ncol=4,
        frameon=False,
        prop=cjk_font(9),
        handlelength=1.8,
        columnspacing=1.4,
    )

    fig.subplots_adjust(left=0.12, right=0.90, top=0.82, bottom=0.20)

    CANDIDATE_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(CANDIDATE_DIR / f"{OUTPUT_STEM}.pdf", format="pdf", dpi=300, bbox_inches="tight")
    fig.savefig(CANDIDATE_DIR / f"{OUTPUT_STEM}.png", format="png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    df = pd.read_csv(INPUT_CSV)
    expected_pairs = {(outcome, spec) for outcome in OUTCOME_ORDER for spec in SPEC_ORDER}
    actual_pairs = set(zip(df["outcome"], df["spec"]))
    missing = expected_pairs - actual_pairs
    if missing:
        raise ValueError(f"robustness_clean.csv 缺少这些 outcome/spec 组合：{sorted(missing)}")

    df = df[df["outcome"].isin(OUTCOME_ORDER) & df["spec"].isin(SPEC_ORDER)].copy()
    df["outcome"] = pd.Categorical(df["outcome"], categories=OUTCOME_ORDER, ordered=True)
    df["spec"] = pd.Categorical(df["spec"], categories=SPEC_ORDER, ordered=True)
    df = df.sort_values(["outcome", "spec"])

    source = prepare_source(df)
    CANDIDATE_DIR.mkdir(parents=True, exist_ok=True)
    source.to_csv(CANDIDATE_DIR / f"{OUTPUT_STEM}_source.csv", index=False, encoding="utf-8-sig")
    draw_matrix(source)


if __name__ == "__main__":
    main()
