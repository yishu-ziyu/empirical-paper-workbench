#!/usr/bin/env python3
"""
Generate a review candidate for Fig5-2 using province-year relations.

The candidate is not wired into the manuscript. It visualizes the first-stage
relationship and reduced-form outcome relationships behind the OLS/RF/IV
comparison, avoiding repeated individual-level points.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
import matplotlib.font_manager as fm
import numpy as np
import pandas as pd
from matplotlib.font_manager import FontProperties

matplotlib.use("Agg")
import matplotlib.pyplot as plt


FIGURE_DIR = Path(__file__).resolve().parent
ROOT = FIGURE_DIR.parents[1]
DATA = ROOT / "01_data" / "reproduced" / "cfps_panel_v5_rebuilt.csv"
TABLE5_2 = ROOT / "03_results" / "panel_main" / "table5_2_ols_rf_iv.csv"
CANDIDATE_DIR = FIGURE_DIR / "candidates" / "figure_review_2026-04-29"
STEM = "Candidate_Fig5_2_FirstStage_ReducedForm_Relation"


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


def style_axis(ax) -> None:
    ax.tick_params(axis="both", labelsize=8.5, colors="#222222")
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontproperties(cjk_font(8.5))
    ax.grid(axis="y", alpha=0.18, linewidth=0.7, color="#6B7280")
    ax.grid(axis="x", visible=False)
    ax.spines["left"].set_color("#444444")
    ax.spines["bottom"].set_color("#444444")
    ax.spines["left"].set_linewidth(0.8)
    ax.spines["bottom"].set_linewidth(0.8)


def weighted_line(x: pd.Series, y: pd.Series, weight: pd.Series) -> tuple[np.ndarray, np.ndarray, float]:
    x_arr = x.to_numpy(dtype=float)
    y_arr = y.to_numpy(dtype=float)
    w_arr = weight.to_numpy(dtype=float)
    slope, intercept = np.polyfit(x_arr, y_arr, 1, w=np.sqrt(w_arr))
    x_line = np.linspace(float(np.nanmin(x_arr)), float(np.nanmax(x_arr)), 100)
    y_line = slope * x_line + intercept
    return x_line, y_line, float(slope)


def weighted_mean(values: pd.Series, weights: pd.Series) -> float:
    valid = values.notna() & weights.notna()
    if not valid.any():
        return np.nan
    return float(np.average(values[valid], weights=weights[valid]))


def build_province_year() -> pd.DataFrame:
    cols = ["provcd", "year", "ln_robot", "bartik_iv", "ln_wage", "manu_dummy"]
    df = pd.read_csv(DATA, usecols=cols)
    province_year = (
        df.groupby(["provcd", "year"], as_index=False)
        .agg(
            n_individuals=("provcd", "size"),
            n_wage=("ln_wage", "count"),
            n_manu=("manu_dummy", "count"),
            bartik_iv=("bartik_iv", "first"),
            ln_robot=("ln_robot", "first"),
            ln_wage_mean=("ln_wage", "mean"),
            manu_share=("manu_dummy", "mean"),
        )
        .sort_values(["year", "provcd"])
    )
    return province_year


def build_bins(province_year: pd.DataFrame, bin_count: int = 8) -> pd.DataFrame:
    data = province_year.copy()
    data["bartik_bin"] = pd.qcut(data["bartik_iv"], q=bin_count, labels=False, duplicates="drop") + 1
    rows: list[dict[str, float]] = []
    for bin_id, group in data.groupby("bartik_bin", sort=True):
        rows.append(
            {
                "bartik_bin": int(bin_id),
                "province_year_cells": int(len(group)),
                "n_individuals": int(group["n_individuals"].sum()),
                "bartik_iv_mean": weighted_mean(group["bartik_iv"], group["n_individuals"]),
                "ln_robot_mean": weighted_mean(group["ln_robot"], group["n_individuals"]),
                "ln_wage_mean": weighted_mean(group["ln_wage_mean"], group["n_wage"]),
                "manu_share": weighted_mean(group["manu_share"], group["n_manu"]),
            }
        )
    return pd.DataFrame(rows)


def build_summary(province_year: pd.DataFrame) -> pd.DataFrame:
    table = pd.read_csv(TABLE5_2)
    rows: list[dict[str, object]] = []
    specs = [
        ("first_stage_descriptive", "ln_robot", "bartik_iv", "n_individuals"),
        ("reduced_form_descriptive_wage", "ln_wage_mean", "bartik_iv", "n_wage"),
        ("reduced_form_descriptive_manu", "manu_share", "bartik_iv", "n_manu"),
    ]
    for name, y_col, x_col, w_col in specs:
        data = province_year[[x_col, y_col, w_col]].dropna()
        _, _, slope = weighted_line(data[x_col], data[y_col], data[w_col])
        rows.append(
            {
                "source": "province_year_descriptive",
                "relation": name,
                "x": x_col,
                "y": y_col,
                "weighted_slope": slope,
                "province_year_cells": int(len(data)),
                "weight_sum": int(data[w_col].sum()),
            }
        )
    for _, row in table.iterrows():
        if row["model"] == "reduced_form":
            rows.append(
                {
                    "source": "table5_2_reduced_form",
                    "relation": row["outcome"],
                    "x": row["variable"],
                    "y": row["outcome_label"],
                    "weighted_slope": float(row["coef"]),
                    "province_year_cells": np.nan,
                    "weight_sum": int(row["nobs"]),
                }
            )
    return pd.DataFrame(rows)


def draw_panel(ax, data: pd.DataFrame, bins: pd.DataFrame, y_col: str, weight_col: str, title: str, ylabel: str) -> None:
    panel = data[["bartik_iv", y_col, weight_col, "year"]].dropna()
    max_n = panel[weight_col].max()
    sizes = 28 + 130 * np.sqrt(panel[weight_col] / max_n)
    year_colors = {2020: "#2F4A5A", 2022: "#8C4B3F"}
    for year, group in panel.groupby("year", sort=True):
        ax.scatter(
            group["bartik_iv"],
            group[y_col],
            s=sizes.loc[group.index],
            facecolors="white",
            edgecolors=year_colors.get(int(year), "#4B5563"),
            linewidths=1.05,
            alpha=0.82,
            label=str(int(year)),
        )

    x_line, y_line, _ = weighted_line(panel["bartik_iv"], panel[y_col], panel[weight_col])
    ax.plot(x_line, y_line, color="#111111", linewidth=1.25, label="加权拟合线")

    bin_y = {
        "ln_robot": "ln_robot_mean",
        "ln_wage_mean": "ln_wage_mean",
        "manu_share": "manu_share",
    }[y_col]
    ax.scatter(
        bins["bartik_iv_mean"],
        bins[bin_y],
        s=34,
        marker="D",
        color="#111111",
        alpha=0.95,
        label="Bartik 分箱均值",
        zorder=4,
    )
    ax.set_title(title, fontproperties=cjk_font(10.5, "bold"), pad=8)
    ax.set_xlabel("Bartik 工具变量", fontproperties=cjk_font(9.5))
    ax.set_ylabel(ylabel, fontproperties=cjk_font(9.5))
    style_axis(ax)


def main() -> None:
    CANDIDATE_DIR.mkdir(parents=True, exist_ok=True)
    province_year = build_province_year()
    bins = build_bins(province_year)
    summary = build_summary(province_year)

    fig, axes = plt.subplots(1, 3, figsize=(12.2, 3.9))
    draw_panel(
        axes[0],
        province_year,
        bins,
        "ln_robot",
        "n_individuals",
        "（a）一阶段：Bartik 与机器人暴露",
        "省级机器人密度对数",
    )
    draw_panel(
        axes[1],
        province_year,
        bins,
        "ln_wage_mean",
        "n_wage",
        "（b）简化式：Bartik 与工资对数",
        "省份-年份平均工资对数",
    )
    draw_panel(
        axes[2],
        province_year,
        bins,
        "manu_share",
        "n_manu",
        "（c）简化式：Bartik 与制造业就业",
        "省份-年份制造业就业率",
    )

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(
        handles,
        labels,
        loc="lower center",
        ncol=4,
        frameon=False,
        prop=cjk_font(8.7),
        bbox_to_anchor=(0.5, -0.015),
    )
    fig.tight_layout(rect=(0, 0.08, 1, 1), w_pad=2.0)
    fig.savefig(CANDIDATE_DIR / f"{STEM}.pdf", format="pdf", dpi=300, bbox_inches="tight")
    fig.savefig(CANDIDATE_DIR / f"{STEM}.png", format="png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    province_year.to_csv(CANDIDATE_DIR / f"{STEM}_source_province_year.csv", index=False)
    bins.to_csv(CANDIDATE_DIR / f"{STEM}_source_bartik_bins.csv", index=False)
    summary.to_csv(CANDIDATE_DIR / f"{STEM}_summary.csv", index=False)
    print(f"字体加载成功: {CHINESE_FONT_NAME} ({CHINESE_FONT_PATH})")
    print(f"生成完成：{CANDIDATE_DIR / STEM}")


if __name__ == "__main__":
    main()
