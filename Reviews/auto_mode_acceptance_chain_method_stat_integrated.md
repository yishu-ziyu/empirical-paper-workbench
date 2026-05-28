# Auto Mode Acceptance Chain

- 状态：needs_human_final_review
- Package readiness：needs_human_final_review
- 正式论文写回：否
- 正式 bibliography 写回：否
- 正式 product state 写回：否

## 组件状态
- `dataset_motherlode_index`: needs_human_dataset_index_review (Results/json/dataset_motherlode_index.json)
- `literature_discovery_seed`: needs_human_literature_discovery_review (Results/json/literature_discovery_seed.json)
- `level3_manuscript_quality_gate`: needs_human_level3_quality_review (Results/json/level3_manuscript_quality_gate_reference_marker_candidate.json)
- `method_knowledge_base`: needs_human_method_kb_review (Results/json/method_knowledge_base.json)
- `statistical_adapter_contract`: needs_human_statistical_adapter_review (Results/json/statistical_adapter_contract.json)

## Method Knowledge Base
- 状态：needs_human_method_kb_review
- 推荐检查数：6
- Proposal rules can block：False
- Reviewed canonical blocking rules：0

## Statistical Adapter Contract
- 状态：needs_human_statistical_adapter_review
- Normalized results：6
- Contract-ready results：6
- Observed methods：iv, ols, ordered_logit

## Repair Queue
- 无自动修复阻断；等待人工 final review。

## 人工审阅清单
- `review_dataset_motherlode_candidates`
- `review_literature_discovery_seed`
- `review_level3_quality_gate`
- `review_method_knowledge_base`
- `review_statistical_adapter_contract`
- `decide_formal_promotion_or_auto_mode_repair`

## 产物信任层
- 真实运行产物: results_evidence_package.json, paper.pdf, statistical_adapter_contract.json
- 草稿层产物: paper.md, literature_review_packet.json, method_knowledge_base.json
- 需要人工审阅: method_gate.md, reviewer_report.md, revision_task_queue.md, method_knowledge_base.md, statistical_adapter_contract.md
