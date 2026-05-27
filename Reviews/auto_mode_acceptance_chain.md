# Auto Mode Acceptance Chain

- 状态：needs_auto_mode_repair
- Package readiness：needs_auto_mode_repair
- 正式论文写回：否
- 正式 bibliography 写回：否
- 正式 product state 写回：否

## 组件状态
- `dataset_motherlode_index`: needs_human_dataset_index_review (Results/json/dataset_motherlode_index.json)
- `literature_discovery_seed`: needs_human_literature_discovery_review (Results/json/literature_discovery_seed.json)
- `level3_manuscript_quality_gate`: needs_human_level3_quality_review (Results/json/level3_manuscript_quality_gate.json)

## Repair Queue
- `mark_candidate_references_for_human_review` -> LiteratureAgent
- `human_review_level3_package_artifacts` -> SupervisorAgent

## 人工审阅清单
- `review_dataset_motherlode_candidates`
- `review_literature_discovery_seed`
- `review_level3_quality_gate`
- `decide_formal_promotion_or_auto_mode_repair`

## 产物信任层
- 真实运行产物: results_evidence_package.json, paper.pdf
- 草稿层产物: paper.md, literature_review_packet.json
- 需要人工审阅: method_gate.md, reviewer_report.md, revision_task_queue.md
