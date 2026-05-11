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
