#!/usr/bin/env python3
"""
Generate candidate figures for the table/figure review pass.

These outputs are review candidates. They are not inserted into the manuscript
unless the text and captions are revised in a separate step.
"""
from __future__ import annotations

import csv
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
PROJECT_ROOT = ROOT.parent
CANDIDATE_DIR = FIGURE_DIR / "candidates" / "figure_review_2026-04-29"
MULTIWAVE_CSV = (
    PROJECT_ROOT
    / "workflow"
    / "results"
    / "run_archive"
    / "multiwave_experiment_v1_20260418"
    / "data_snapshots"
    / "final_cfps_multiwave_full_experiment_v1_20260418.csv"
)
PANEL_HET = ROOT / "03_results" / "panel_heterogeneity"
DESCRIPTIVE = ROOT / "03_results" / "descriptive" / "table4_1_descriptive_stats_current.csv"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def as_float(value: str) -> float:
    if value in ("", None):
        return np.nan
    return float(value)


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


def style_axis(ax, grid_axis: str = "x") -> None:
    ax.tick_params(axis="both", labelsize=9, colors="#222222")
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontproperties(cjk_font(9))
    ax.grid(axis=grid_axis, alpha=0.18, linewidth=0.7, color="#6B7280")
    ax.grid(axis="y" if grid_axis == "x" else "x", visible=False)
    ax.spines["left"].set_color("#444444")
    ax.spines["bottom"].set_color("#444444")
    ax.spines["left"].set_linewidth(0.8)
    ax.spines["bottom"].set_linewidth(0.8)


def save_figure(fig, stem: str) -> None:
    CANDIDATE_DIR.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(CANDIDATE_DIR / f"{stem}.pdf", format="pdf", dpi=300, bbox_inches="tight")
    fig.savefig(CANDIDATE_DIR / f"{stem}.png", format="png", dpi=300, bbox_inches="tight")


def generate_multiwave_exposure_trend() -> None:
    cols = ["year", "provcd", "ln_robot_exp", "bartik_iv_exp"]
    df = pd.read_csv(MULTIWAVE_CSV, usecols=cols)
    df = df.dropna(subset=["year", "provcd", "ln_robot_exp", "bartik_iv_exp"])
    province_year = df.drop_duplicates(subset=["year", "provcd"])
    trend = (
        province_year.groupby("year")
        .agg(
            ln_robot_mean=("ln_robot_exp", "mean"),
            ln_robot_p25=("ln_robot_exp", lambda s: s.quantile(0.25)),
            ln_robot_p75=("ln_robot_exp", lambda s: s.quantile(0.75)),
            bartik_mean=("bartik_iv_exp", "mean"),
            province_count=("provcd", "nunique"),
        )
        .reset_index()
        .sort_values("year")
    )

    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    ax.fill_between(
        trend["year"].to_numpy(),
        trend["ln_robot_p25"].to_numpy(),
        trend["ln_robot_p75"].to_numpy(),
        color="#D8DEE3",
        alpha=0.8,
        label="省份四分位区间",
    )
    ax.plot(
        trend["year"],
        trend["ln_robot_mean"],
        marker="o",
        markersize=5,
        color="#2F4A5A",
        linewidth=1.8,
        label="年度省份均值",
    )
    ax.set_xticks(trend["year"].astype(int).tolist())
    ax.set_xlabel("CFPS 调查年份", fontproperties=cjk_font(10))
    ax.set_ylabel("省级工业机器人密度对数", fontproperties=cjk_font(10))
    ax.legend(frameon=False, prop=cjk_font(9), loc="upper left")
    style_axis(ax, grid_axis="y")
    save_figure(fig, "Candidate_Multiwave_Robot_Exposure_Trend")
    fig.savefig(FIGURE_DIR / "Fig5_3_Multiwave_Robot_Exposure_Trend.pdf", format="pdf", dpi=300, bbox_inches="tight")
    fig.savefig(FIGURE_DIR / "Fig5_3_Multiwave_Robot_Exposure_Trend.png", format="png", dpi=300, bbox_inches="tight")
    trend.to_csv(CANDIDATE_DIR / "Candidate_Multiwave_Robot_Exposure_Trend_source.csv", index=False)
    plt.close(fig)


def generate_region_heterogeneity() -> None:
    rows = read_csv(PANEL_HET / "table5_5_region_heterogeneity.csv")
    outcome_order = ["ln_wage", "manu_dummy", "ISEI_score"]
    outcome_labels = {"ln_wage": "工资对数", "manu_dummy": "制造业就业", "ISEI_score": "ISEI 得分"}
    region_labels = {"East": "东部", "Midwest": "中西部"}

    fig, axes = plt.subplots(1, 3, figsize=(11.2, 2.8))
    for ax, outcome in zip(axes, outcome_order):
        data = [r for r in rows if r["outcome"] == outcome]
        data.sort(key=lambda r: 0 if r["region"] == "East" else 1)
        coefs = np.array([as_float(r["coef"]) for r in data])
        ses = np.array([as_float(r["se"]) for r in data])
        lower = coefs - 1.96 * ses
        upper = coefs + 1.96 * ses
        y = np.arange(len(data))[::-1]
        colors = ["#2F4A5A" if r["region"] == "East" else "#8C4B3F" for r in data]
        xerr = np.vstack([coefs - lower, upper - coefs])
        ax.errorbar(
            coefs,
            y,
            xerr=xerr,
            fmt="s",
            markersize=6,
            capsize=3.5,
            color="#222222",
            ecolor="#222222",
            elinewidth=1.1,
        )
        ax.scatter(coefs, y, s=54, marker="s", color=colors, zorder=3)
        ax.axvline(0, color="#222222", linewidth=0.9)
        ax.set_yticks(y)
        ax.set_yticklabels([region_labels[r["region"]] for r in data], fontproperties=cjk_font(9))
        ax.set_title(outcome_labels[outcome], fontproperties=cjk_font(10, "bold"), pad=8)
        ax.set_xlabel("系数及 95% 置信区间", fontproperties=cjk_font(9))
        ax.set_ylim(-0.45, 1.45)
        xmin = float(np.nanmin(lower))
        xmax = float(np.nanmax(upper))
        pad = max((xmax - xmin) * 0.15, 0.02)
        ax.set_xlim(xmin - pad, xmax + pad)
        style_axis(ax)

    save_figure(fig, "Candidate_Region_Heterogeneity_Coefficients")
    plt.close(fig)


def generate_parttime_age_group() -> None:
    rows = read_csv(PANEL_HET / "table5_7_parttime_age_cohort_stata.csv")
    panel_a = [r for r in rows if r["panel"] == "Panel A"]
    panel_b = [
        r
        for r in rows
        if r["panel"] == "Panel B" and "联合检验" not in r["group_or_variable"]
    ]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.2, 4.4))

    def draw(ax, data, xlabel, xlim) -> None:
        y = np.arange(len(data))[::-1]
        coefs = np.array([as_float(r["coef"]) for r in data])
        ses = np.array([as_float(r["se"]) for r in data])
        lower = coefs - 1.96 * ses
        upper = coefs + 1.96 * ses
        labels = [r["group_or_variable"] for r in data]
        ax.errorbar(
            coefs,
            y,
            xerr=np.vstack([coefs - lower, upper - coefs]),
            fmt="s",
            markersize=6,
            capsize=3.5,
            color="#2F4A5A",
            ecolor="#222222",
            elinewidth=1.1,
        )
        ax.axvline(0, color="#222222", linewidth=0.9)
        ax.set_yticks(y)
        ax.set_yticklabels(labels, fontproperties=cjk_font(8.5))
        ax.set_xlabel(xlabel, fontproperties=cjk_font(9.5))
        ax.set_xlim(*xlim)
        style_axis(ax)

    draw(ax1, panel_a, "分组估计系数及 95% 置信区间", (-0.06, 0.02))
    draw(ax2, panel_b, "交互项系数及 95% 置信区间", (-0.04, 0.02))
    ax1.set_title("（a）年龄组分样本", fontproperties=cjk_font(10, "bold"))
    ax2.set_title("（b）年龄组交互项", fontproperties=cjk_font(10, "bold"))
    save_figure(fig, "Candidate_Parttime_Age_Group_Coefficients")
    plt.close(fig)


def generate_sample_availability() -> None:
    rows = read_csv(DESCRIPTIVE)
    keep = ["ln_wage", "manu_dummy", "ISEI_score", "part_time", "ln_robot", "bartik_iv"]
    labels = {
        "ln_wage": "工资对数",
        "manu_dummy": "制造业就业",
        "ISEI_score": "ISEI 得分",
        "part_time": "兼职就业",
        "ln_robot": "省级工业机器人密度对数",
        "bartik_iv": "Bartik 工具变量",
    }
    data = [r for r in rows if r["variable"] in keep]
    data.sort(key=lambda r: keep.index(r["variable"]))
    obs = np.array([as_float(r["obs"]) for r in data])
    y = np.arange(len(data))[::-1]

    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    ax.barh(y, obs, height=0.55, color="#2F4A5A", alpha=0.9)
    ax.set_yticks(y)
    ax.set_yticklabels([labels[r["variable"]] for r in data], fontproperties=cjk_font(9))
    ax.set_xlabel("非缺失观测数", fontproperties=cjk_font(10))
    for yi, value in zip(y, obs):
        ax.text(value + 550, yi, f"{int(value):,}", va="center", ha="left", fontproperties=cjk_font(8.5))
    ax.set_xlim(0, max(obs) * 1.18)
    style_axis(ax)
    save_figure(fig, "Candidate_Sample_Availability")
    plt.close(fig)


def main() -> None:
    print(f"字体加载成功: {CHINESE_FONT_NAME} ({CHINESE_FONT_PATH})")
    generate_multiwave_exposure_trend()
    generate_region_heterogeneity()
    generate_parttime_age_group()
    generate_sample_availability()
    print(f"候选图生成完成: {CANDIDATE_DIR}")


if __name__ == "__main__":
    main()
