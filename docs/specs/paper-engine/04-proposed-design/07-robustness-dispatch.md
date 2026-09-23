# 稳健性同一张分派表

> 上级：[Proposed Design](../04-proposed-design.md)


`robustness_check` 读 `main_specification.method`，禁止在 IV/RD/SCM 上再跑一遍 `y ~ treat` 的 OLS。

| method | 套餐 | 失败 |
| --- | --- | --- |
| `ols` / `did`（TWFE 主估计） | 现有：`cluster_levels` 上 `feols`；异质性交互；`wild_cluster_bootstrap` | 无 cluster 则 `degraded=True, reason="no_cluster_or_groups"`，`diagnostics` 仍写出（算已跑） |
| `did`（CS 主估计） | 交替 `control_group` / `notyet_cutoff`；不做 OLS 重拟合 | 不能跑则 `reason="cs_battery_failed"` |
| `iv` | `statspai.ivreg(..., cluster=level)`；可选 `vce="wild"`。**不是** `feols(y ~ treat)` | `reason="iv_battery_failed"` |
| `rd` | `rdrobust` 换 `kernel` / `bwselect` / `donut` | `reason="rd_battery_failed"` |
| `scm` | 已有 `synth_time_placebo` / in-space | 已有 error 记入 diagnostics |
| 公式对不上方法 | 不跑 OLS 冒充 | `degraded=True, reason="ols_battery_on_non_ols"`，`diagnostics=[{...}]` |

节点始终写 `produced_by="robustness_check"` 和 `diagnostics`（可为 `[]`）。这样 `_robustness_ran` 为真，空表是可见降级，不是“没跑”。

---
