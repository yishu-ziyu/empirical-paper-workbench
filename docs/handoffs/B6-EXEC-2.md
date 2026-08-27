# 执行2：Bacon 禁 TWFE 且没有队列列时，主表不许写偏误

你是 cmux 同窗口执行会话。批次 1–5 已收下。本批修主估计一条错路。
不要问确认。读完就改、跑测试、写 STATUS。

产品根：`/Users/mahaoxuan/Desktop/经济学论文/econpaper`

## 现在错在哪

`agent/nodes/estimate.py` 的 `_estimate_did`：Goodman-Bacon 禁 TWFE（`forbidden_weight_share >= 0.1`）且 **没有** `first_treat_col` 时，仍跑 TWFE / `feols`，只把 `status` 标成 `degraded`、`error=twfe_without_cohort`。`treatment_row` 和系数还在。交错处理组的偏误会进结果章主表。

设计：缺队列列时 `status=error`，`results` 是错误句，`treatment_row` 为空。不准编假系数。`_error()` 已经是这个形状。

## Goal

Bacon 已禁 TWFE、又没有队列列时，主估计走 `_error`，不要交出一张 TWFE 表。

## Hard bar

在 `agent/tests/test_estimate.py` 追加（名称自定）：

1. `identification_diag.diagnostics` 含 `{"test": "bacon_decomposition", "forbidden_weight_share": 0.4}`，`main_specification.method=="did"`，有 `formula` / `csv_path`，**没有** `first_treat_col`。
   - `estimate.status == "error"`
   - `treatment_row` 为空
   - `produced_by == "estimate"`
   - `results` 是句子，不是 `| 变量 | 系数 | SE | p |` 主表
   - `estimate` 里没有可引用的 `coef`（键不存在，或值为 None）
2. 对照：同样 Bacon 超阈，但 **有** `first_treat_col`（以及 CS 需要的 `outcome` / `time_col` / `id_col`）。不要把这条改坏。若本机 `statspai.callaway_santanna` 因数据太小失败，允许 `status` 为 error（调用失败），但 **不得** 再落到 `estimator=="statspai.feols"` 的 TWFE 主表。
3. 对照：没有 Bacon 诊断时，现有 OLS/TWFE 用例仍绿（`test_estimate_writes_treatment_row` 等）。

## 只许改

- `agent/nodes/estimate.py`
- `agent/tests/test_estimate.py`

## 禁止改

`graph.py`，`prewrite.py`，`robustness_check.py`，`identification_verify.py`，`generate_chapter.py`，评审文件。

不要为了让对照 2 变绿去改稳健性或图。

## 测试

```bash
cd /Users/mahaoxuan/Desktop/经济学论文/econpaper
./agent/.venv/bin/python -m pytest agent/tests/test_estimate.py -q --tb=short
```

## 做完写

`docs/handoffs/B6-EXEC-2.STATUS.md`

```text
status: done
ran:
changed:
risk:
```

现在开工。
