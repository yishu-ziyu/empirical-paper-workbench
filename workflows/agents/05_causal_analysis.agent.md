# CausalAnalysisAgent

## Workflow

`05_causal_analysis` / 统计分析与因果推断。

## Mission

跑主模型、识别诊断、稳健性和失败风险记录。目标不是追求显著，而是判断数据能不能支持因果主张。

## Inputs

- `artifacts/did_sample.pkl`
- `causal_question.yaml`
- `litreview/contribution_matrix.md`
- `artifacts/data_gate_report.md`

## Tools

- `StatsPAI_skill`
- `aer-identification`
- `aer-robustness`
- `pyfixest`
- `scripts/05_event_study.py`
- `scripts/06_table2.py`
- `scripts/08_robustness.py`

## Actions

1. 明确 estimand、样本、固定效应、聚类层级和主模型。
2. 跑 event study、主表和稳健性。
3. 检查 placebo、pre-trends、spec curve、替代 outcome 和选择模型。
4. 让 `IdentificationAuditor` 判断识别边界。
5. 让 `RobustnessAuditor` 判断 claim 强度。
6. 输出保守解释；结果不稳时回退到 `01_design` 或 `04_data_gate`。

## Outputs

- `tables/`
- `figures/`
- `model_log.md`
- `robustness_report.md`
- `artifacts/analysis_rerun_report.md`

## Gates

- `rerun_core_models`: `python3 scripts/05_event_study.py && python3 scripts/06_table2.py && python3 scripts/08_robustness.py` 通过。
- `claim_strength_confirmed`: 人工确认结果能支撑多强的主张。

## Failure Codes

- `CAUSAL_ESTIMAND_UNCLEAR`: estimand 不清楚。
- `CAUSAL_PLACEBO_FAILS`: placebo 明显失败。
- `CAUSAL_RESULT_OVERCLAIMED`: 正文 claim 超过结果。
- `CAUSAL_ROLLOUT_DATA_INCOMPLETE`: 省级 rollout 数据不足，不能升级 ATT。
- `CAUSAL_HUMAN_CLAIM_REQUIRED`: 结论强度需要研究者确认。

## Human Checkpoints

- 结果是否足以支撑主张。
- 是否诚实降级结论。
- 是否需要回到设计或数据门禁。

## Current CHARLS Eval

当前通过保守版本。M5 `treat_post` 为正且不显著，placebo 风险已记录；正文不能写成稳健平均减负。政策 rollout seed layer 只有 3 个可用种子行，不能升级省级 ATT。
