# 执行3：批次 3 方法分派（主表必须是对的估计器）

你是 cmux 同窗口的执行会话。批次 1 已让估计在文献前跑完，但主表仍是 OLS 形。
不要问人确认。读完本文件就改代码、跑测试、写 STATUS。

## Goal

用户选 IV / RD / SCM / DiD / OLS 时，主估计走对应 StatsPAI 调用。
IV 主表是 `statspai.ivreg`，**禁止**用 `iv_diag` 当主表。
缺工具变量时 `status=error`，不准编假系数。
稳健性在非 OLS 上不准再跑 `feols(y~treat)` 套餐。

## Hard bar

1. IV fixture：`estimate.estimator=="statspai.ivreg"` 且有非空 `treatment_row`。
2. 缺 instrument：`estimate.status=="error"`，没有假系数，`treatment_row` 为空。
3. SCM / RD 主表不是 `y ~ treat` 的 OLS。
4. 对 IV 跑稳健性：不得 `feols(y~treat)`；否则 `reason="ols_battery_on_non_ols"`。
5. `identification_verify`：没有 `time_col` 不能给 DiD 出星（保持 None 或 skip，不要假装 3 星）。

## Improve

DirectionRequest 能吃进 `time_col` / `instrument` / `running` 等方法列（`extra="allow"`）。

## 产品与权威

- 根目录：`/Users/mahaoxuan/Desktop/经济学论文/econpaper`
- 设计：`docs/specs/paper-engine.md` 批次 3 + StatsPAI 调用表
- StatsPAI：`feols`，`ivreg`（`y ~ (endog ~ z) + exog`），`rdrobust`，`synth`，`callaway_santanna`
- `CausalResult` 用 `result.estimate`，不要 `float(result)`
- 禁止 git commit / push / PR

## 只许改这些文件

- `backend/routers/outline.py`（`DirectionRequest` 显式方法字段 + `extra="allow"`。不要改 DirectionResponse 已有字段）
- `agent/design/spec.py`
- `agent/nodes/set_direction.py`（投影 `charls_config` / 面板列到 main_specification）
- `agent/nodes/estimate.py`（五路分派；OLS 路径已有 `produced_by` + `treatment_row`，保留）
- `agent/nodes/robustness_check.py`（按方法分派；无工作不要在文件顶层 `import statspai`，缺库时降级不要把方向打崩）
- `agent/tests/test_estimate.py`
- `agent/tests/test_direction_spec.py`
- `agent/tests/test_robustness_check.py`
- `agent/tests/test_identification_verify.py`
- 如需夹具：`fixtures/` 下新建，不要改别人夹具语义

## 禁止改

`review_chapter.py`，`prompts/*`，`generate_chapter.py`，`generate_title.py`，
`search_literature.py`，`graph.py`，`engine/readiness.py`，`engine/prewrite.py`，
`engine/bind.py`，`protocols.py`，`state.py`，`facade.py`（除非你发现 set_direction
不经 Facade；不要为了方便去改 Facade 预写），`backend/tests/test_review.py`，
`backend/schemas/*`。

## 必须实现的机制

`DirectionSpec.to_main_specification` 必须能带上：
- OLS：`formula = y ~ treat + controls`（已有）
- IV：instrument / endog，**不要**写成普通 `y ~ treat`
- RD：running / cutoff
- SCM：unit / time / treated_unit / treatment_time
- DiD：time_col / id_col

`estimate()` 按 `spec.method` 分派。失败：`status=error`，`produced_by="estimate"`，
`treatment_row=""`，`results` 写成失败说明（可以有字，但不能有假系数行）。

`robustness_check`：
- OLS：现有聚类/异质性/安慰剂可继续，空 `cluster_levels` 直接返回，不要先 `import statspai`
- IV/RD/SCM：不要套 OLS 电池；写 `degraded` + `reason="ols_battery_on_non_ols"` 或走该方法自己的稳健性

识别：有 `time_col` 才能给 DiD 出星。缺列 = skip / `star_rating is None`，不是 0 星。

## 测试怎么跑

agent 虚拟环境有 StatsPAI / statsmodels。backend 虚拟环境没有，不要在 backend venv 跑估计单测。

```bash
cd /Users/mahaoxuan/Desktop/经济学论文/econpaper
./agent/.venv/bin/python -m pytest \
  agent/tests/test_estimate.py \
  agent/tests/test_direction_spec.py \
  agent/tests/test_robustness_check.py \
  agent/tests/test_identification_verify.py -q --tb=short
```

若 `test_robustness_check` 需要 statspai 而当前 agent venv 没有：先确认
`agent/.venv` 能否 `import statspai`；没有就 `pip install -e` 旁边的 StatsPAI，
不要改测试去跳过硬条。

## 做完写这个文件

路径：`docs/handoffs/EXEC-3.STATUS.md`

```text
status: done
ran: <命令和 pass/fail>
changed: <文件列表>
risk: <一句失败场景>
```

卡住写 `status: blocked`。现在开工。
