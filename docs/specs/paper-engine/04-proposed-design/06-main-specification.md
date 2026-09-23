# `MainSpecification` 与主表契约

> 上级：[Proposed Design](../04-proposed-design.md)


`DirectionSpec.to_main_specification` 按 `method` 写出下面形状。`produced_by="set_direction"`。

公共键：`method`, `outcome`, `treatment`, `controls`, `cluster`, `cluster_levels`, `heterogeneity_groups`, `produced_by`。

| method | 额外键 | 估计器调用（禁止用诊断当主表） | `treatment` 行标签 |
| --- | --- | --- | --- |
| `ols` | `formula = "y ~ treat + controls"` | `statspai.feols(formula, data=df, cluster=cluster)`；失败则 `statsmodels.formula.api.ols` | 处理列名 |
| `did` | `time_col`, `id_col`, `first_treat_col?`, `feols_formula = "y ~ treat + controls \| id + time"` | 默认 `statspai.feols(feols_formula, data=df, cluster=id_col)`。仅当识别里 Bacon forbidden 超阈 **且** `first_treat_col` 有值：改走 `statspai.callaway_santanna(df, y=outcome, g=first_treat_col, t=time_col, i=id_col)`。没有队列列就保持 TWFE，并 `degraded` | TWFE：处理列名；CS：`ATT` |
| `iv` | `endogenous`, `instruments`, `iv_formula = "y ~ (endog ~ z1+z2) + controls"` | **`statspai.ivreg(iv_formula, data=df, cluster=cluster)`**。禁止把 `iv_diag.beta_2sls` 当主表。`iv_diag` 只留在识别节点 | 内生列名 |
| `rd` | `running_var`, `cutoff` | `statspai.rdrobust(df, y=outcome, x=running_var, c=cutoff)` | `RD` |
| `scm` | `unit_col`, `treated_unit`, `treatment_time` | `statspai.synth(df, outcome=..., unit=..., time=..., treated_unit=..., treatment_time=...)` | `SCM_gap` |

`estimate` 节点写出（扩现有 `EstimateOutput`，不是新 TypedDict 名）：

```python
estimate = {
    "status": "ok" | "error" | "degraded",
    "produced_by": "estimate",
    "method": "iv",
    "estimator": "statspai.ivreg",  # 或 feols / rdrobust / synth / callaway_santanna / statsmodels.ols
    "n": 1200,
    "coef": 0.1234,
    "se": 0.0456,
    "p": 0.0078,
    "treatment": "endog",          # 与 treatment_row 第一列一致
    "treatment_row": "| endog | 0.1234 | 0.0456 | 0.0078 |",
    "formula": "y ~ (endog ~ z) + x1",
}
results = "\n".join([
    "# 主结果",
    "",
    f"估计器：`{estimate['estimator']}`",
    f"公式：`{estimate['formula']}`",
    f"N = {estimate['n']}",
    "",
    "| 变量 | 系数 | SE | p |",
    "|------|------|----|---|",
    estimate["treatment_row"],
])
```

系数、SE、p 一律 `f"{x:.4f}"`。缺 SE/p 时该格为 `—`（Unicode em dash 与现 `_fmt` 一致），但 `treatment_row` 整行字符串仍是接地的唯一针。

CS / RD / SCM 走 `CausalResult`：**不要** `float(result)`（该类无 `__float__`）。统一助手：

```python
def effect_from_fit(fit) -> tuple[float | None, float | None, float | None, int | None]:
    """抽出 (coef, se, p, n)。"""
    if hasattr(fit, "estimate") and not hasattr(fit, "params"):
        # CausalResult: rdrobust / synth / callaway_santanna
        coef = float(fit.estimate)
        se = None if fit.se is None else float(fit.se)
        p = None if fit.pvalue is None else float(fit.pvalue)
        n = None if getattr(fit, "n_obs", None) is None else int(fit.n_obs)
        return coef, se, p, n
    # EconometricResults（feols / ivreg）：沿用现有 _coef_se_p + nobs
    ...
```

缺公式或列：`status="error"`，`results` 为错误句，`treatment_row` 为空。结果章就绪失败（`no_results`），不让模型补系数。

---
