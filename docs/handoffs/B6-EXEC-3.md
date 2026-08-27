# 执行3：CS 主估计的稳健性不要再套 y ~ treat

你是 cmux 同窗口执行会话。批次 1–5 已收下。本批只改稳健性分派。
不要问确认。读完就改、跑测试、写 STATUS。

产品根：`/Users/mahaoxuan/Desktop/经济学论文/econpaper`
设计：`docs/specs/paper-engine.md`「稳健性同一张分派表」里 `did`（CS 主估计）那一行。

## 现在错在哪

`robustness_check` 把 `method=="did"` 全丢进 `else`：聚类 `feols` + 异质性 + wild cluster。主估计若已是 `statspai.callaway_santanna`，稳健性仍在重跑 `y ~ treat` 的 OLS。

设计：

- DiD **TWFE** 主估计：保持现有套餐（`cluster_levels` 上 `feols` 等）
- DiD **CS** 主估计：交替 `control_group` / `notyet_cutoff`；不做 OLS 重拟合
- 不能跑则 `reason="cs_battery_failed"`，仍写 `produced_by="robustness_check"` 和 `diagnostics`

StatsPAI：`statspai.callaway_santanna(df, y=..., g=..., t=..., i=..., control_group=..., notyet_cutoff=...)`。
`control_group` 为 `'nevertreated'` 或 `'notyettreated'`。`notyet_cutoff` 为 `'period'` 或 `'cohort'`。

## Goal

主估计器是 CS 时，稳健性只动 CS 旋钮，不再跑 `y ~ treat` 的 feols 套餐。

## Hard bar

在 `agent/tests/test_robustness_check.py` 追加：

1. 夹具：`statspai.dgp_did` 写成 CSV；`main_specification.method=="did"`，有 `outcome` / `first_treat_col`（或 `g`）/ `time_col` / `id_col`；`state.estimate.estimator == "statspai.callaway_santanna"`。
   - `robustness_results.produced_by == "robustness_check"`
   - `reason` 不是 `ols_battery_on_non_ols`（那是 IV/RD 缺公式的拒绝码）
   - `robustness` 里 **没有** `type=="clustering"` 的 feols 行
   - 成功：至少两行变体（例如 `nevertreated` 与 `notyettreated`，或两个 `notyet_cutoff`），且能看出调的是 CS
   - 失败：`reason == "cs_battery_failed"`，`diagnostics` 非空，`summary_table` 说明没跑 OLS 套餐
2. 现有 `test_robustness_check_basic`（TWFE / `y ~ treat` + cluster）必须仍绿。判断 CS 的依据是 `state.estimate.estimator == "statspai.callaway_santanna"`，不要把所有 `method=="did"` 都改成 CS。

## 只许改

- `agent/nodes/robustness_check.py`
- `agent/tests/test_robustness_check.py`

## 禁止改

`estimate.py`，`graph.py`，`prewrite.py`，`identification_verify.py`，章节/评审文件。
不要为了造主估计去改估计节点。夹具里直接写入 `estimate.estimator`。

## 测试

```bash
cd /Users/mahaoxuan/Desktop/经济学论文/econpaper
./agent/.venv/bin/python -m pytest agent/tests/test_robustness_check.py -q --tb=short
```

## 做完写

`docs/handoffs/B6-EXEC-3.STATUS.md`

```text
status: done
ran:
changed:
risk:
```

现在开工。
