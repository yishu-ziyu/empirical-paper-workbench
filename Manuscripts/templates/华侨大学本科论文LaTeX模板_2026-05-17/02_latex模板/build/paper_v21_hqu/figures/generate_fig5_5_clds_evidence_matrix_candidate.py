#!/usr/bin/env python3
"""
Generate a candidate evidence-matrix figure for the CLDS supplementary analysis.

The figure is deliberately separate from the manuscript Fig5-5 files. It reads
the frozen Table 5-5 CLDS CSV and writes only candidate-review outputs.
"""
from __future__ import annotations

import csv
from pathlib import Path
from textwrap import fill

import matplotlib
import matplotlib.font_manager as fm
from matplotlib.font_manager import FontProperties

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle


FIGURE_DIR = Path(__file__).resolve().parent
ROOT = FIGURE_DIR.parents[1]
SOURCE_CSV = ROOT / "03_results" / "panel_heterogeneity" / "table5_5_clds_mechanism.csv"
OUT_DIR = FIGURE_DIR / "candidates" / "figure_review_2026-04-29"
OUT_STEM = OUT_DIR / "Candidate_Fig5_5_CLDS_Evidence_Matrix"


VARIABLE_META = {
    "need_training": {
        "domain": "培训与技能",
        "label": "是否需要培训",
        "meaning": "培训需求未呈现普遍上升，边际负向。",
    },
    "skill_time": {
        "domain": "培训与技能",
        "label": "掌握技能所需时间",
        "meaning": "技能吸收时间缩短，提示岗位学习路径可能变化。",
    },
    "tech_training": {
        "domain": "培训与技能",
        "label": "是否参加技术培训",
        "meaning": "正式技术培训参与没有稳定变化。",
    },
    "cert_mismatch": {
        "domain": "资格适配",
        "label": "证书-岗位不匹配",
        "meaning": "资格信号与岗位要求的错位上升。",
    },
    "searched_recent": {
        "domain": "求职状态",
        "label": "最近3个月是否找工作",
        "meaning": "近期求职行为弱增加，仅作边际线索。",
    },
    "search_duration": {
        "domain": "求职状态",
        "label": "求职持续时间",
        "meaning": "没有证据支持求职持续时间稳定延长。",
    },
}


plt.rcParams.update(
    {
        "axes.unicode_minus": False,
        "figure.facecolor": "white",
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    }
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


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
    available = {font.name for font in fm.fontManager.ttflist}
    for font_name in preferred:
        if font_name in available:
            font_path = fm.findfont(fm.FontProperties(family=font_name), fallback_to_default=False)
            return font_name, font_path
    raise RuntimeError("未找到可用中文字体，请安装 Songti SC / PingFang SC / Arial Unicode MS。")


CHINESE_FONT_NAME, CHINESE_FONT_PATH = find_chinese_font()


def cjk_font(size: float = 10, weight: str = "normal") -> FontProperties:
    return FontProperties(fname=CHINESE_FONT_PATH, size=size, weight=weight)


def significance_label(pvalue: float) -> tuple[str, str]:
    if pvalue < 0.01:
        return "***", "1%显著"
    if pvalue < 0.05:
        return "**", "5%显著"
    if pvalue < 0.1:
        return "*", "10%边际"
    return "ns", "不显著"


def direction_label(coef: float, pvalue: float) -> tuple[str, str, str]:
    if pvalue >= 0.1:
        return "≈", "无稳定\n变化", "#9AA3AF"
    if coef > 0:
        return "+", "正向", "#B84A3A"
    return "-", "负向", "#2E6F88"


def format_pvalue(pvalue: float) -> str:
    if pvalue < 0.001:
        return "p<0.001"
    return f"p={pvalue:.3f}"


def build_matrix_rows(rows: list[dict[str, str]]) -> list[dict[str, str | float | int]]:
    matrix_rows: list[dict[str, str | float | int]] = []
    max_n = max(int(float(row["nobs"])) for row in rows)
    for row in rows:
        variable = row["variable"]
        meta = VARIABLE_META[variable]
        coef = float(row["coef"])
        se = float(row["se"])
        pvalue = float(row["pvalue"])
        nobs = int(float(row["nobs"]))
        sig_stars, sig_text = significance_label(pvalue)
        direction_symbol, direction_text, direction_color = direction_label(coef, pvalue)
        matrix_rows.append(
            {
                "domain": meta["domain"],
                "variable": variable,
                "label": meta["label"],
                "coef": coef,
                "se": se,
                "pvalue": pvalue,
                "nobs": nobs,
                "nobs_share": nobs / max_n,
                "stars": sig_stars,
                "sig_text": sig_text,
                "direction_symbol": direction_symbol,
                "direction_text": direction_text,
                "direction_color": direction_color,
                "meaning": meta["meaning"],
            }
        )
    return matrix_rows


def write_source(matrix_rows: list[dict[str, str | float | int]]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    columns = [
        "domain",
        "variable",
        "label",
        "coef",
        "se",
        "pvalue",
        "nobs",
        "stars",
        "direction_text",
        "meaning",
    ]
    with OUT_STEM.with_suffix(".csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for row in matrix_rows:
            writer.writerow({column: row[column] for column in columns})


def add_text(ax, x: float, y: float, text: str, *, size: float = 10, weight: str = "normal",
             color: str = "#1F2933", ha: str = "left", va: str = "center") -> None:
    ax.text(x, y, text, fontproperties=cjk_font(size, weight), color=color, ha=ha, va=va)


def draw_badge(ax, x: float, y: float, text: str, color: str) -> None:
    width = 0.058 if len(text) <= 2 else 0.078
    height = 0.048
    patch = FancyBboxPatch(
        (x - width / 2, y - height / 2),
        width,
        height,
        boxstyle="round,pad=0.004,rounding_size=0.012",
        linewidth=0,
        facecolor=color,
        alpha=0.96,
    )
    ax.add_patch(patch)
    add_text(ax, x, y, text, size=10.5, weight="bold", color="white", ha="center")


def draw_matrix(matrix_rows: list[dict[str, str | float | int]]) -> None:
    fig, ax = plt.subplots(figsize=(10.2, 5.9))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    add_text(ax, 0.035, 0.955, "CLDS 补充分析证据矩阵", size=15, weight="bold", va="top")
    add_text(
        ax,
        0.035,
        0.907,
        "按变量类型汇总方向、显著性、样本量和辅助含义；不同量纲变量不比较系数大小。",
        size=9.5,
        color="#52606D",
        va="top",
    )

    headers = [
        ("变量类型", 0.045),
        ("CLDS 变量", 0.170),
        ("方向", 0.375),
        ("显著性", 0.495),
        ("样本量", 0.622),
        ("辅助含义", 0.748),
    ]
    header_y = 0.835
    ax.add_patch(Rectangle((0.025, header_y - 0.034), 0.95, 0.058, color="#F0F3F5", linewidth=0))
    for header, x in headers:
        add_text(ax, x, header_y, header, size=9.5, weight="bold", color="#334E68")

    row_top = 0.775
    row_h = 0.104
    max_bar_width = 0.105
    previous_domain = ""
    for idx, row in enumerate(matrix_rows):
        y = row_top - idx * row_h
        if idx % 2 == 0:
            ax.add_patch(Rectangle((0.025, y - 0.047), 0.95, 0.088, color="#FBFCFD", linewidth=0))
        ax.plot([0.025, 0.975], [y - 0.052, y - 0.052], color="#E6E8EB", linewidth=0.8)

        domain = str(row["domain"])
        if domain != previous_domain:
            add_text(ax, 0.045, y, domain, size=9.2, weight="bold", color="#243B53")
            previous_domain = domain

        add_text(ax, 0.170, y + 0.016, str(row["label"]), size=10, weight="bold")
        add_text(ax, 0.170, y - 0.019, str(row["variable"]), size=8.2, color="#6B7280")

        draw_badge(ax, 0.392, y, str(row["direction_symbol"]), str(row["direction_color"]))
        add_text(ax, 0.424, y, str(row["direction_text"]), size=8.8)

        stars = str(row["stars"])
        sig_color = "#8A2C20" if stars != "ns" else "#7B8794"
        add_text(ax, 0.495, y + 0.014, stars, size=10.5, weight="bold", color=sig_color)
        add_text(ax, 0.538, y + 0.014, str(row["sig_text"]), size=8.8, color=sig_color)
        add_text(ax, 0.495, y - 0.019, format_pvalue(float(row["pvalue"])), size=8.2, color="#6B7280")

        bar_x = 0.622
        bar_y = y - 0.012
        ax.add_patch(Rectangle((bar_x, bar_y), max_bar_width, 0.020, color="#E1E7EC", linewidth=0))
        ax.add_patch(
            Rectangle(
                (bar_x, bar_y),
                max_bar_width * float(row["nobs_share"]),
                0.020,
                color="#52606D",
                linewidth=0,
            )
        )
        add_text(ax, bar_x, y + 0.022, f"N={int(row['nobs']):,}", size=8.8, color="#334E68")

        add_text(ax, 0.748, y, fill(str(row["meaning"]), width=23), size=9.2, color="#334E68")

    add_text(
        ax,
        0.035,
        0.075,
        "证据定位：CLDS 2016/2018 合并样本的过程性参照结果；未使用 Bartik IV，不构成机制闭环检验。",
        size=8.8,
        color="#52606D",
        va="top",
    )
    add_text(
        ax,
        0.035,
        0.043,
        "方向基于机器人暴露系数符号；显著性为 * 10%、** 5%、*** 1%。",
        size=8.3,
        color="#7B8794",
        va="top",
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_STEM.with_suffix(".png"), format="png", dpi=300, bbox_inches="tight")
    fig.savefig(OUT_STEM.with_suffix(".pdf"), format="pdf", dpi=300, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    rows = read_csv(SOURCE_CSV)
    matrix_rows = build_matrix_rows(rows)
    write_source(matrix_rows)
    draw_matrix(matrix_rows)
    print(f"字体加载成功: {CHINESE_FONT_NAME} ({CHINESE_FONT_PATH})")
    print(f"候选图已生成: {OUT_STEM.with_suffix('.png')}")
    print(f"同源数据已生成: {OUT_STEM.with_suffix('.csv')}")


if __name__ == "__main__":
    main()
