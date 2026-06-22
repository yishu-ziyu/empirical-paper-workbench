# CHARLS P1 Agent Spec Eval

目标：用当前 CHARLS 样例检查第二层前五步 Agent spec 是否可执行、可验收、可失败回退。

## Eval Matrix

| Workflow | Required artifacts | Current status | Check | Result |
|---|---|---|---|---|
| `01_design` | `research_design.md`, `causal_question.yaml`, `design_risk.md` | present | `python3 scripts/21_route_next_workflow.py` | PASS |
| `02_literature` | `litreview/query_plan.json`, `litreview/literature_candidates.csv`, `references.bib`, `litreview/contribution_matrix.md` | present | `python3 scripts/15_verify_bibliography.py` | PASS |
| `03_paper_reading` | `litreview/notes/compressed/`, `litreview/notes/span_index.json`, `litreview/notes/reading_state.md` | present | 文件存在 + 慢读状态可读 | PASS |
| `04_data_gate` | `artifacts/data_contract.md`, `artifacts/sample_attrition.csv`, `artifacts/variable_dictionary.csv`, `artifacts/did_sample.pkl`, `artifacts/data_gate_report.md` | present | `python3 scripts/04_data_gate.py` | PASS |
| `05_causal_analysis` | `tables/`, `figures/`, `model_log.md`, `robustness_report.md`, `artifacts/analysis_rerun_report.md` | present | 核心分析脚本已在第一层闭环跑通 | PASS |

## Failure Injection

这些是未来自动 eval 应该模拟的失败，不在当前工作区真实删除文件。

| Workflow | Simulated missing/invalid input | Expected failure code |
|---|---|---|
| `01_design` | treatment 为空 | `DESIGN_TREATMENT_UNCLEAR` |
| `02_literature` | closest papers 未确认 | `LIT_HUMAN_CLOSEST_REQUIRED` |
| `03_paper_reading` | 核心文献只有摘要 | `READING_ABSTRACT_ONLY` |
| `04_data_gate` | outcome 字段缺失 | `DATA_KEY_VARIABLE_MISSING` |
| `05_causal_analysis` | 正文写成稳健平均减负 | `CAUSAL_RESULT_OVERCLAIMED` |

## Current Verdict

P1 对 `01-05` 通过。边界是：省级 rollout ATT 仍被 `CAUSAL_ROLLOUT_DATA_INCOMPLETE` 阻断；这不是 P1 失败，而是后续识别升级任务。
