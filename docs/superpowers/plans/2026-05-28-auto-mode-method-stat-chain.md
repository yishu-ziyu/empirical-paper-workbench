# Auto Mode Method And Statistical Contract Chain Plan

Date: 2026-05-28

## Node Goal

P7-H connects the Method Knowledge Base and Statistical Adapter Contract into the Auto Mode acceptance chain. The package readiness decision must read data, literature, Level 3 manuscript quality, method-rule readiness, and statistical-result contract readiness before it can enter final human review.

This node only extends the acceptance/reporting layer. It can write a new chain JSON and Markdown review artifact, but it cannot rerun models, promote proposal method rules, or write formal manuscript, bibliography, project bibliography, DesignSpec, RunPlan, or product state.

## BDD Behaviors

### Behavior 1: Aggregate five acceptance components

Given Dataset Motherlode Index, Literature Discovery Seed, Level 3 Quality Gate, Method KB, and Statistical Adapter Contract all exist
When Auto Mode builds the acceptance chain
Then the component status list includes all five inputs
And the package readiness decision is based on all five components.

Business rule: 最终验收不能只看论文结构，还必须同时看到方法规则和统计结果契约。

### Behavior 2: Preserve human final review when method and statistics are review-ready

Given the Level 3 gate is ready for review
And Method KB is `needs_human_method_kb_review`
And Statistical Adapter Contract is `needs_human_statistical_adapter_review` with contract-ready results
When Auto Mode builds the acceptance chain
Then package readiness is `needs_human_final_review`
And the human review checklist includes Method KB and Statistical Adapter Contract review items.

Business rule: 方法规则和统计契约进入人工审阅，不因为 proposal 或审阅态自动写正式层。

### Behavior 3: Block when required method or statistical inputs are missing

Given Method KB or Statistical Adapter Contract is missing or has the wrong schema
When Auto Mode builds the acceptance chain
Then it returns `blocked_missing_acceptance_inputs`
And the missing input is routed into the repair queue with the proper owner agent.

Business rule: 缺少方法/统计契约时不能声称 paper package 已经可终审。

### Behavior 4: Repair incomplete statistical contracts

Given Statistical Adapter Contract exists
But no observed result is contract-ready
When Auto Mode builds the acceptance chain
Then package readiness becomes `needs_auto_mode_repair`
And the repair queue contains a statistical adapter repair task.

Business rule: 统计输出必须可被下游消费，不能只因为文件存在就通过。

### Behavior 5: Surface method and statistical readiness summaries

Given Method KB has recommended checks and Statistical Adapter Contract has normalized results
When Auto Mode writes the chain report
Then the JSON includes `method_readiness` and `statistical_readiness`
And the Markdown review explains both summaries.

Business rule: 人工终审需要看到方法规则数量、proposal/canonical 边界和统计结果 contract-ready 数量。

### Behavior 6: Preserve formal-layer boundaries

Given the chain writes JSON and Markdown review outputs
When the CLI finishes
Then formal manuscript, bibliography, project bibliography, DesignSpec, RunPlan, product state, model outputs, and canonical method rules are not modified.

Business rule: P7-H 是验收汇总层，不是正式发布或模型执行层。

## Boundary Conditions

- Treat Method KB and Statistical Adapter Contract as required P7-H inputs.
- Proposal method rules can require human review but cannot block formal export by themselves.
- Reviewed canonical blocking method rules remain future work because current Method KB reports zero reviewed canonical blocking rules.
- Statistical Adapter Contract is trusted only as a normalization layer over existing execution/evidence artifacts; this node does not rerun models.
- Missing required inputs produce `blocked_missing_acceptance_inputs`.
- Present but incomplete method/statistical inputs produce `needs_auto_mode_repair`.
- No formal manuscript writeback.
- No formal bibliography or project bibliography writeback.
- No DesignSpec or RunPlan writeback.
- No `state/product/*` writeback.
- No canonical method-rule promotion.
- No statistical execution artifact overwrite.

## Verification

- RED: update `tests/test_auto_mode_acceptance_chain.py` so P7-H cases fail before implementation because Method KB and Statistical Adapter Contract are not accepted or reported by the chain.
- GREEN: target Auto Mode acceptance-chain tests pass after minimal integration.
- Real run writes `Results/json/auto_mode_acceptance_chain_method_stat_integrated.json` and `Reviews/auto_mode_acceptance_chain_method_stat_integrated.md`.
