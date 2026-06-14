#!/usr/bin/env python3
"""
Generate selected manuscript figures from structured result CSV files.

This script intentionally avoids hard-coded coefficient values. Current final
Stata redraws for Fig4-1, Fig5-1, Fig5-3, and Fig5-4 are in
02_code/39_generate_manuscript_figures_stata.do. The default Python entry point
is retained for Fig5-2 only, because that comparison figure is still generated
from the shared table5_2 CSV here.
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
PANEL_HET = ROOT / "03_results" / "panel_heterogeneity"
ARCHIVE_DIR = FIGURE_DIR / "archive" / "replaced_2026-05-05_split_figures"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def as_float(value: str) -> float:
    return float(value) if value not in ("", None) else np.nan


def find_chinese_font() -> tuple[str, str]:
    """Return a concrete macOS CJK font file so Chinese glyphs are embedded."""
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
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / f"{stem}.pdf", format="pdf", dpi=300, bbox_inches="tight")
    fig.savefig(FIGURE_DIR / f"{stem}.png", format="png", dpi=300, bbox_inches="tight")


def save_archived_figure(fig, stem: str) -> None:
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(ARCHIVE_DIR / f"{stem}.pdf", format="pdf", dpi=300, bbox_inches="tight")
    fig.savefig(ARCHIVE_DIR / f"{stem}.png", format="png", dpi=300, bbox_inches="tight")


def significance_marker(pvalue: float) -> str:
    if pvalue < 0.01:
        return "***"
    if pvalue < 0.05:
        return "**"
    if pvalue < 0.1:
        return "*"
    return ""


plt.rcParams.update(
    {
        "font.family": CHINESE_FONT_NAME,
        "font.sans-serif": [CHINESE_FONT_NAME, "DejaVu Sans"],
        "font.size": 10,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.alpha": 0.15,
        "lines.linewidth": 1.5,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "axes.unicode_minus": False,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
    }
)


def generate_fig5_1() -> None:
    rows = read_csv(PANEL_MAIN / "table5_1_baseline_iv.csv")
    iv_rows = [r for r in rows if r["variable"] == "ln_robot"]
    order = ["ln_wage", "manu_dummy", "ISEI_score", "part_time"]
    by_outcome = {r["outcome"]: r for r in iv_rows}

    comparison_rows = read_csv(PANEL_MAIN / "table5_2_ols_rf_iv.csv")
    ols_by_outcome = {
        r["outcome"]: as_float(r["coef"])
        for r in comparison_rows
        if r["model"] == "ols"
    }

    outcomes_en = order
    outcomes_cn = [by_outcome[o]["outcome_label"] for o in order]
    iv_coefs = [as_float(by_outcome[o]["coef"]) for o in order]
    iv_errors = [as_float(by_outcome[o]["se"]) for o in order]
    iv_pvals = [as_float(by_outcome[o]["pvalue"]) for o in order]
    ols_coefs = [ols_by_outcome.get(o) for o in order]

    y = np.arange(len(outcomes_en))
    height = 0.35
    fig, ax = plt.subplots(figsize=(7.2, 4.6))

    ols_vals = [v if v is not None else 0 for v in ols_coefs]
    ax.barh(y - height / 2, ols_vals, height=height, color="#C9CED3", label="OLS", alpha=0.95)

    iv_colors = ["#2F4A5A", "#2F4A5A", "#2F4A5A", "#8C4B3F"]
    ax.barh(
        y + height / 2,
        iv_coefs,
        xerr=iv_errors,
        height=height,
        color=iv_colors,
        label="IV-2SLS",
        alpha=0.95,
        error_kw={"linewidth": 1.2, "capthick": 1.2, "ecolor": "black"},
    )

    ax.axvline(x=0, color="#222222", linewidth=0.9, zorder=0)
    for i, (c, e, p) in enumerate(zip(iv_coefs, iv_errors, iv_pvals)):
        sig = significance_marker(p)
        if not sig:
            continue
        text_x = c + e + 0.03 if c >= 0 else c - e - 0.08
        ax.text(text_x, i + height / 2, sig, va="center", ha="left", fontproperties=cjk_font(10, "bold"))

    labels = [f"{cn}\n({en})" for en, cn in zip(outcomes_en, outcomes_cn)]
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontproperties=cjk_font(9))
    ax.set_xlabel("系数估计值", fontproperties=cjk_font(10))
    ax.legend(loc="lower right", frameon=False, prop=cjk_font(9))
    ax.set_xlim(-0.15, 1.35)
    style_axis(ax)
    ax.set_title("图5-1 工业机器人对劳动者配置结果的影响（IV-2SLS估计）", pad=10, fontproperties=cjk_font(11, "bold"))

    save_figure(fig, "Fig5_1_Coefplot_AllOutcomes")
    plt.close(fig)


def generate_fig5_2() -> None:
    rows = read_csv(PANEL_MAIN / "table5_2_ols_rf_iv.csv")
    order = ["ols", "reduced_form", "iv_2sls"]
    labels = {
        "ols": "OLS\n机器人密度对数",
        "reduced_form": "Reduced Form\nBartik 工具变量",
        "iv_2sls": "IV-2SLS\n机器人密度对数",
    }
    by_key = {(r["outcome"], r["model"]): r for r in rows}

    def series(outcome: str) -> tuple[list[float], list[float], list[float], list[float], list[float]]:
        coefs = [as_float(by_key[(outcome, m)]["coef"]) for m in order]
        errors = [as_float(by_key[(outcome, m)]["se"]) for m in order]
        pvals = [as_float(by_key[(outcome, m)]["pvalue"]) for m in order]
        lower = [c - 1.96 * e for c, e in zip(coefs, errors)]
        upper = [c + 1.96 * e for c, e in zip(coefs, errors)]
        return coefs, errors, lower, upper, pvals

    wage_coefs, wage_errors, wage_lower, wage_upper, wage_pvals = series("ln_wage")
    manu_coefs, manu_errors, manu_lower, manu_upper, manu_pvals = series("manu_dummy")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.2, 4.7))
    y = np.arange(len(order))[::-1]

    def draw_panel(ax, coefs, lower, upper, pvals, title: str, xlim: tuple[float, float]) -> None:
        xerr = np.array([[c - lo for c, lo in zip(coefs, lower)], [hi - c for c, hi in zip(coefs, upper)]])
        ax.errorbar(
            coefs,
            y,
            xerr=xerr,
            fmt="o",
            markersize=6.5,
            color="#2F4A5A",
            ecolor="#222222",
            elinewidth=1.3,
            capsize=4,
            capthick=1.3,
            zorder=3,
        )
        ax.axvline(x=0, color="#222222", linewidth=0.9, zorder=0)
        for yi, c, hi, p in zip(y, coefs, upper, pvals):
            sig = significance_marker(p)
            if sig:
                ax.text(hi + (xlim[1] - xlim[0]) * 0.025, yi, sig, va="center", ha="left", fontproperties=cjk_font(9, "bold"))
        ax.set_yticks(y)
        ax.set_yticklabels([labels[m] for m in order], fontproperties=cjk_font(8.2))
        ax.set_xlabel("系数估计值及 95% 置信区间", fontproperties=cjk_font(10))
        if title:
            ax.set_title(title, fontproperties=cjk_font(11, "bold"))
        ax.set_xlim(*xlim)
        style_axis(ax)

    draw_panel(ax1, wage_coefs, wage_lower, wage_upper, wage_pvals, "（a）工资对数", (-0.02, 0.39))
    draw_panel(ax2, manu_coefs, manu_lower, manu_upper, manu_pvals, "（b）制造业就业", (-0.01, 0.14))

    save_archived_figure(fig, "Fig5_2_OLS_RF_IV")
    save_archived_figure(fig, "Fig5_2_OLS_RF_IV_Coefficients")
    plt.close(fig)

    split_specs = [
        (
            wage_coefs,
            wage_lower,
            wage_upper,
            wage_pvals,
            "",
            (-0.02, 0.39),
            "Fig5_2a_Wage_OLS_RF_IV",
        ),
        (
            manu_coefs,
            manu_lower,
            manu_upper,
            manu_pvals,
            "",
            (-0.01, 0.14),
            "Fig5_2b_Manufacturing_OLS_RF_IV",
        ),
    ]
    for coefs, lower, upper, pvals, title, xlim, stem in split_specs:
        split_fig, split_ax = plt.subplots(figsize=(5.6, 3.35))
        draw_panel(split_ax, coefs, lower, upper, pvals, title, xlim)
        save_figure(split_fig, stem)
        plt.close(split_fig)


def generate_fig5_4() -> None:
    rows = read_csv(PANEL_HET / "table5_5_clds_mechanism.csv")
    mechanisms_en = [r["variable"] for r in rows]
    mechanisms_cn = [r["outcome"] for r in rows]
    coefs = [as_float(r["coef"]) for r in rows]
    errors = [as_float(r["se"]) for r in rows]
    pvals = [as_float(r["pvalue"]) for r in rows]

    colors = ["#2F4A5A" if p < 0.1 else "#C9CED3" for p in pvals]
    y = np.arange(len(mechanisms_en))
    fig, ax = plt.subplots(figsize=(7.0, 4.4))

    ax.barh(
        y,
        coefs,
        xerr=errors,
        height=0.5,
        color=colors,
        edgecolor="white",
        linewidth=0.6,
        error_kw={"linewidth": 1.2, "capthick": 1.2, "ecolor": "black"},
        alpha=0.95,
    )
    ax.axvline(x=0, color="#222222", linewidth=0.9)

    for i, (c, e, p) in enumerate(zip(coefs, errors, pvals)):
        sig = significance_marker(p)
        if not sig:
            continue
        text_x = c + e + 0.025 if c >= 0 else c - e - 0.025
        ha = "left" if c >= 0 else "right"
        ax.text(text_x, i, sig, va="center", ha=ha, fontproperties=cjk_font(9, "bold"))

    labels = [f"{cn}\n({en})" for en, cn in zip(mechanisms_en, mechanisms_cn)]
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontproperties=cjk_font(8.5))
    ax.set_xlabel("系数估计值", fontproperties=cjk_font(10))
    ax.set_xlim(-0.85, 0.2)
    style_axis(ax)
    ax.set_title("图5-4 机器人暴露与 CLDS 调整变量：补充分析结果", pad=10, fontproperties=cjk_font(11, "bold"))

    save_figure(fig, "Fig5_4_CLDS_Adjustment_Results")
    plt.close(fig)


def main() -> None:
    print(f"字体加载成功: {CHINESE_FONT_NAME} ({CHINESE_FONT_PATH})")
    generate_fig5_2()
    print("生成完成：Fig5_2a_Wage_OLS_RF_IV；Fig5_2b_Manufacturing_OLS_RF_IV")
    print("提示：Fig4-1 请运行 generate_fig4_1.py；Fig5-1 请运行 generate_fig5_1_faceted_candidate.py；Fig5-3 多年份趋势请运行 generate_candidate_figures.py。")


if __name__ == "__main__":
    main()
