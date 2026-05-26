# P5-E2a 正式包证据材料化

- Status: `evidence_materialized`
- Patch proposal: `Submissions/formal_package/reproducibility/evidence_registry_patch_proposal.json`
- 正式层写回：未发生
- 最终 PDF/docx：未生成

## 已材料化证据

- `figure_manifest` -> `Results/json/figure_manifest.json` (no_rendered_figures_registered)
- `robustness_matrix` -> `Results/json/robustness_matrix.json` (robustness_items_need_review)
- `limitations_register` -> `Results/json/limitations_register.json` (limitations_need_human_review)

## 跳过项

- 无。

## Warnings

- `limitations_need_human_review`
- `no_rendered_figures_registered`
- `robustness_items_need_review`

## 下一步

- `rerun_formal_pdf_export_preflight`：让 P5-D 读取新材料化的证据文件，确认哪些缺口已经消除。
