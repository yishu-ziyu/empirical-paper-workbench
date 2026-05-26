# P5-E2a 正式包证据材料化

- Status: `evidence_materialized`
- Patch proposal: `Submissions/formal_package/reproducibility/evidence_registry_patch_proposal.json`
- 正式层写回：未发生
- 最终 PDF/docx：未生成

## 已材料化证据

- `approved_findings` -> `Results/json/approved_findings.json` (none)
- `citation_verification_log` -> `Results/json/citation_verification_log.json` (citation_log_needs_manual_review)
- `domain_notes` -> `Results/json/domain_notes.json` (domain_notes_need_human_review)
- `verified_context_sources` -> `Results/json/verified_context_sources.json` (verified_context_sources_need_review)

## 跳过项

- 无。

## Warnings

- `citation_log_needs_manual_review`
- `domain_notes_need_human_review`
- `verified_context_sources_need_review`

## 下一步

- `rerun_formal_pdf_export_preflight`：让 P5-D 读取新材料化的证据文件，确认哪些缺口已经消除。
