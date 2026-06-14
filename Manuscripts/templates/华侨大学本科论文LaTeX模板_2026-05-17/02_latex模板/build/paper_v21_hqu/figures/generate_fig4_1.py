#!/usr/bin/env python3
"""
Generate Fig4-1 for the manuscript.

The figure uses province-year level observations, because both ln_robot and
bartik_iv vary at the province-year level in the two-wave baseline data.
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


def style_axis(ax, grid_axis: str = "y") -> None:
    ax.tick_params(axis="both", labelsize=9, colors="#222222")
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontproperties(cjk_font(9))
    ax.grid(axis=grid_axis, alpha=0.18, linewidth=0.7, color="#6B7280")
    ax.grid(axis="x" if grid_axis == "y" else "y", visible=False)
    ax.spines["left"].set_color("#444444")
    ax.spines["bottom"].set_color("#444444")
    ax.spines["left"].set_linewidth(0.8)
    ax.spines["bottom"].set_linewidth(0.8)


def save_figure(fig) -> None:
    fig.tight_layout(w_pad=2.2)
    fig.savefig(FIGURE_DIR / "Fig4_1_IV_Distribution.pdf", format="pdf", dpi=300, bbox_inches="tight")
    fig.savefig(FIGURE_DIR / "Fig4_1_IV_Distribution.png", format="png", dpi=300, bbox_inches="tight")
    fig.savefig(FIGURE_DIR / "Fig4_1_IV_FirstStage_Relation.pdf", format="pdf", dpi=300, bbox_inches="tight")
    fig.savefig(FIGURE_DIR / "Fig4_1_IV_FirstStage_Relation.png", format="png", dpi=300, bbox_inches="tight")


def main() -> None:
    df = pd.read_csv(DATA)
    province_year = (
        df[["provcd", "year", "ln_robot", "bartik_iv"]]
        .dropna()
        .drop_duplicates(subset=["provcd", "year"])
        .sort_values(["year", "provcd"])
    )

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.4, 4.6))

    ax1.hist(
        province_year["ln_robot"],
        bins=18,
        color="#AEB7BE",
        edgecolor="white",
        linewidth=0.7,
        density=False,
    )
    ax1.set_title("（a）省级工业机器人密度对数分布", fontproperties=cjk_font(11, "bold"), pad=10)
    ax1.set_xlabel("省级工业机器人密度对数", fontproperties=cjk_font(10))
    ax1.set_ylabel("省份-年份观测数", fontproperties=cjk_font(10))
    style_axis(ax1, grid_axis="y")

    x = province_year["bartik_iv"].to_numpy()
    y = province_year["ln_robot"].to_numpy()
    slope, intercept = np.polyfit(x, y, 1)
    x_line = np.linspace(x.min(), x.max(), 100)
    y_line = slope * x_line + intercept

    ax2.scatter(
        x,
        y,
        s=42,
        facecolors="white",
        edgecolors="#2F4A5A",
        linewidths=1.2,
        alpha=0.95,
    )
    ax2.plot(x_line, y_line, color="#111111", linewidth=1.4)
    ax2.set_title("（b）Bartik 工具变量与机器人密度对数", fontproperties=cjk_font(11, "bold"), pad=10)
    ax2.set_xlabel("Bartik 工具变量", fontproperties=cjk_font(10))
    ax2.set_ylabel("省级工业机器人密度对数", fontproperties=cjk_font(10))
    style_axis(ax2, grid_axis="y")

    save_figure(fig)
    province_year.to_csv(FIGURE_DIR / "Fig4_1_IV_FirstStage_Relation_source.csv", index=False)
    print(f"字体加载成功: {CHINESE_FONT_NAME} ({CHINESE_FONT_PATH})")
    print("生成完成：Fig4_1_IV_Distribution / Fig4_1_IV_FirstStage_Relation")


if __name__ == "__main__":
    main()
