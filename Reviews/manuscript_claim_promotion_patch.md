# Claim Promotion Patch

- 状态：`claim_promotion_patch_ready`
- ready_for_apply：`true`
- applied：`false`
- formal_writeback_allowed：`false`

## Patch Operation

- type：`add_claim_to_approved_finding`
- target_path：`Results/json/approved_findings.json`
- source_finding_id：`finding_trained_effect`
- source_table_id：`regression_table_1`
- proposal_id：`main-results::finding_trained_effect::claim_proposal`
- claim_text：草案提案：在 iv 规格中，ln_robot 对 ln_wage 的估计系数为 0.199384322747（SE=0.0793435494782, p=0.0119807291718, N=34315）。

## Next Action

- `apply_claim_promotion_patch_after_human_confirm`
