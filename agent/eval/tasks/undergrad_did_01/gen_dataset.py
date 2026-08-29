"""undergrad_did_01 数据集生成脚本（seed 固定，可重复生成 dataset.csv）。

【生成设定 —— 即"生成脚本注释"】
- 随机种子：20260828（numpy default_rng，全流程唯一随机源）
- 结构：200 个个体 × 8 期（2010-2017），平衡面板，共 1600 行
- 处理：id<=100 为处理组；政策 2015 年落地（公共处理时点，无交错）。
  公共时点设计保证 Goodman-Bacon 分解的 forbidden 权重为 0，
  固定管线会走 TWFE（statspai.feols）而不是 Callaway-Sant'Anna。
- 真实 DGP：
      income = 3000 + 80*(educ-12) + 15*(age-45) + unit_fe
               + 20*(year-2010) + 2.5*treat + e
      unit_fe ~ N(0, 120)，e ~ N(0, 2.5)，treat 与 e 独立（随机试点）
  真实 ATT = 2.5。个体固定效应与时间趋势被双向固定效应吸收，
  e 的方差取得小（2.5）是为了让 |coef-2.5|<=0.6 的容差在抽样噪声下
  以约 2.4 个标准差的裕量通过（SE≈0.25），避免基线分数卡抖动。
- 干扰项（无关控制变量，与 DGP 无关，考察 agent 会不会乱塞控制变量）：
      shoe_size ~ N(25, 3)      逐行
      rainfall  ~ N(800, 120)   逐个体（时间不变）
- 5% 随机缺失（MCAR）：age / educ 两列各独立以 5% 概率置 NaN。
  注：id/year/treat/income 保持完整。缺失不放在 income 上是有意的——
  实测 StatsPAI bacon_decomposition 对 y 含 NaN 不报错但会静默返回
  beta_twfe=0.0（错误值，星级逻辑只看 forbidden share 所以不暴露）；
  而按行 dropna 又会把平衡面板搞成非平衡直接抛
  MethodIncompatibility。协变量缺失则完全无此问题，下游估计自动降行。
  如需复现该缺陷可把 MISSING_ON_INCOME 打开。
- 列清单：id, year, treat, income, age, educ, shoe_size, rainfall, first_treat
      first_treat = 处理组 2015 / 对照组 0，仅存档（供未来 CS 估计用），
      默认不进 research_direction，否则识别验真会附加跑 CS 诊断，
      其 warn 状态会把星级从 3 星压到 2 星。
- 自检：用 statsmodels 以 C(id)+C(year) 双向固定效应重估 treat 系数，
  要求 |coef-2.5|<=0.6 且 p<0.05，不满足则非零退出。

【为什么 dataset.csv 本身不带注释行】
upload_data / identification_verify / estimate 三个节点都用裸的
``pd.read_csv(path)`` 读数据，不传 comment 参数；文件头注释行会被当成
表头，直接污染列名。生成说明放在本文件头 + task.json 的
dataset_generation 字段，dataset.csv 必须保持纯 CSV。

用法：
    backend/.venv/bin/python agent/eval/tasks/undergrad_did_01/gen_dataset.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 20260828
N_UNITS = 200
YEARS = list(range(2010, 2018))  # 8 期
TREAT_YEAR = 2015
TRUE_ATT = 2.5
MISSING_RATE = 0.05
# 缺失是否也打在结果变量 income 上（默认关）：
# 打开后 StatsPAI bacon_decomposition 会静默返回 beta_twfe=0.0（见文件头注释）
MISSING_ON_INCOME = False

HERE = Path(__file__).resolve().parent
CSV_PATH = HERE / "dataset.csv"


def build_frame() -> pd.DataFrame:
    """按文件头注释里的 DGP 生成面板。"""
    rng = np.random.default_rng(SEED)

    ids = np.repeat(np.arange(1, N_UNITS + 1), len(YEARS))
    year = np.tile(np.array(YEARS), N_UNITS)
    treated_group = (ids <= N_UNITS // 2).astype(int)
    treat = ((treated_group == 1) & (year >= TREAT_YEAR)).astype(int)

    unit_fe = rng.normal(0.0, 120.0, N_UNITS).repeat(len(YEARS))
    base_age = rng.normal(45.0, 8.0, N_UNITS).repeat(len(YEARS))
    age = base_age + (year - YEARS[0])  # 随年份自然增长
    educ = rng.normal(12.0, 3.0, N_UNITS).repeat(len(YEARS))  # 时间不变
    shoe_size = rng.normal(25.0, 3.0, N_UNITS * len(YEARS))
    rainfall = rng.normal(800.0, 120.0, N_UNITS).repeat(len(YEARS))

    e = rng.normal(0.0, 2.5, N_UNITS * len(YEARS))
    income = (
        3000.0
        + 80.0 * (educ - 12.0)
        + 15.0 * (age - 45.0)
        + unit_fe
        + 20.0 * (year - YEARS[0])
        + TRUE_ATT * treat
        + e
    )

    df = pd.DataFrame(
        {
            "id": ids,
            "year": year,
            "treat": treat,
            "income": income,
            "age": age,
            "educ": educ,
            "shoe_size": shoe_size,
            "rainfall": rainfall,
            "first_treat": np.where(treated_group == 1, TREAT_YEAR, 0),
        }
    )

    # 5% MCAR 缺失：协变量列各自独立置 NaN（id/year/treat/income 完整）
    missing_cols = ["age", "educ"] + (["income"] if MISSING_ON_INCOME else [])
    for col in missing_cols:
        mask = rng.random(len(df)) < MISSING_RATE
        df.loc[mask, col] = np.nan
    return df


def self_check(df: pd.DataFrame) -> tuple[float, float]:
    """用 statsmodels 双向固定效应重估，等价于管线里 TWFE 的语义。

    statspai.feols 需要 pyfixest（当前环境未装），这里用
    C(id)+C(year) 虚拟变量验证 DGP 本身能恢复真实 ATT，与管线解耦。
    """
    import statsmodels.formula.api as smf

    fit = smf.ols(
        "income ~ treat + age + educ + C(id) + C(year)",
        data=df,
    ).fit()
    return float(fit.params["treat"]), float(fit.pvalues["treat"])


def main() -> int:
    df = build_frame()
    df.to_csv(CSV_PATH, index=False)

    coef, p = self_check(df)
    n_missing = int(df[["age", "educ"]].isna().sum().sum())
    print(f"dataset.csv 已生成：{CSV_PATH}")
    print(f"  行数={len(df)}  列={list(df.columns)}")
    print(f"  缺失单元格（age/educ）={n_missing}")
    print(f"  TWFE 自检：coef={coef:.4f}  p={p:.6f}  (真实 ATT={TRUE_ATT})")
    ok = abs(coef - TRUE_ATT) <= 0.6 and p < 0.05
    print(f"  容差检查：{'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
