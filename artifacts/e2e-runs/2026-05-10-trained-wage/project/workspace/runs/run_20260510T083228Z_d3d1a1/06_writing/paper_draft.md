# Paper Draft

This draft is generated from inspected sources and preserves the matching-efficiency boundary.

## Source Snapshot
# en

英文稿、回复信、补充附录等英文手稿材料放这里。



# generated

自动生成的中间稿放这里。第一阶段至少保留：

- `paper_draft.md`
- `paper_draft.tex`
- 后续的 `paper_draft.docx`



## Question

> effect of trained on wage

- **Outcome**: `wage`
- **Treatment**: `trained`
- **Design (auto-detected)**: `observational`

## Data

- Sample size: **12** rows, **4** columns.
- Missingness: none detected in the analysis frame.
- Outcome `wage`: mean=11.750, sd=1.118, median=11.550, n=12.
- Treatment `trained` distribution: 0=6 (50.0%), 1=6 (50.0%)

Mean covariates by treatment arm:

| covariate | 0 | 1 | std-diff |
|---|---|---|---|
| edu | 12.667 | 13.500 | 0.837 |
| experience | 3.167 | 3.333 | 0.112 |

## Identification

**Verdict**: OK

- [INFO] *power* — MDE at 80% power: 1.8084 (raw units); n_treated=6, n_control=6.

## Estimator

- **Method**: OLS with robust SE (baseline)
- **Function**: `sp.regress()`
- **Rationale**: Start with OLS as baseline. If endogeneity is a concern, follow up with matching or IV.
- **Key assumptions**: E[ε|X]=0 (exogeneity), Correct functional form

## Results

- **trained**: 1.8505 (SE = 0.0573)

## Robustness

- Estimate: 1.8505
- Ci Width: 0.2245

## References

_(No explicit citations attached — see `workflow.result.cite()` if available.)_


# templates

模板文件放这里。

- `paper.md.j2`：Markdown 草稿模板
- `paper.tex.j2`：LaTeX 草稿模板
- `reference.docx`：后续用于稳定 Word 样式的 Pandoc 参考模板

如果 `reference.docx` 暂时不存在，`Program/export_docx.py` 会先用 Pandoc 默认样式导出。



# zh

中文稿、中文摘要、中文说明材料放这里。

