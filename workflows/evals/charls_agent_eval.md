# CHARLS Agent Spec Eval

目标：用当前 CHARLS 样例检查第二层十步 Agent spec 是否可执行、可验收、可失败回退。

## Eval Matrix

| Workflow | Required artifacts | Current status | Check | Result |
|---|---|---|---|---|
| `01_design` | `research_design.md`, `causal_question.yaml`, `design_risk.md` | present | `python3 scripts/21_route_next_workflow.py` | PASS |
| `02_literature` | `litreview/query_plan.json`, `litreview/literature_candidates.csv`, `references.bib`, `litreview/contribution_matrix.md` | present | `python3 scripts/15_verify_bibliography.py` | PASS |
| `03_paper_reading` | `litreview/notes/compressed/`, `litreview/notes/span_index.json`, `litreview/notes/reading_state.md` | present | 文件存在 + 慢读状态可读 | PASS |
| `04_data_gate` | `artifacts/data_contract.md`, `artifacts/sample_attrition.csv`, `artifacts/variable_dictionary.csv`, `artifacts/did_sample.pkl`, `artifacts/data_gate_report.md` | present | `python3 scripts/04_data_gate.py` | PASS |
| `05_causal_analysis` | `tables/`, `figures/`, `model_log.md`, `robustness_report.md`, `artifacts/analysis_rerun_report.md` | present | 核心分析脚本已闭环跑通 | PASS |
| `06_writing` | `paper.tex`, `paper.pdf` | present | 文件存在 + 当前主叙事保守 | PASS |
| `07_revision` | `review_report.md`, `revision_plan.md`, `draft_revised.md` | present | 文件存在 + claim audit 已完成 | PASS |
| `08_format_citation` | `verified_bibliography.csv`, `paper.pdf` | present | `python3 scripts/15_verify_bibliography.py` | PASS |
| `09_replication` | `run_manifest.json`, `repro_report.md`, `replication/README.md` | present | `python3 verify_repro.py` | PASS |
| `10_defense` | `response_matrix.md`, `defense_qa.md`, `revision_log.md` | present | 文件存在 + evidence path 约束 | PASS |

## Failure Injection

这些是未来自动 eval 应该模拟的失败，不在当前工作区真实删除文件。

| Workflow | Simulated missing/invalid input | Expected failure code |
|---|---|---|
| `01_design` | treatment 为空 | `DESIGN_TREATMENT_UNCLEAR` |
| `02_literature` | closest papers 未确认 | `LIT_HUMAN_CLOSEST_REQUIRED` |
| `03_paper_reading` | 核心文献只有摘要 | `READING_ABSTRACT_ONLY` |
| `04_data_gate` | outcome 字段缺失 | `DATA_KEY_VARIABLE_MISSING` |
| `05_causal_analysis` | 正文写成稳健平均减负 | `CAUSAL_RESULT_OVERCLAIMED` |
| `06_writing` | 贡献句不能回链结果 | `WRITING_CLAIM_UNBOUND` |
| `07_revision` | 只做语言润色 | `REVISION_LANGUAGE_ONLY` |
| `08_format_citation` | 正文引用缺 BibTeX | `FORMAT_MISSING_CITATION` |
| `09_replication` | 关键表格哈希漂移 | `REPRO_HASH_DRIFT` |
| `10_defense` | 审稿意见漏回 | `DEFENSE_COMMENT_UNANSWERED` |

## Current Verdict

十步 Agent spec 通过。当前仍未解决的是研究升级任务：省级 rollout ATT 需要更完整政策时点数据；这属于后续识别升级，不属于第二层 P2 阻塞项。
