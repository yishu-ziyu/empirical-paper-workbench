# Data Gate Report

**Data**: `/Users/mahaoxuan/Desktop/经济学论文/StatspAI_第二个样例_最低工资消费效应/artifacts/analysis_ready.pkl`


## Data Summary

- **Observations**: 60,754
- **Variables**: 22
- **Missing cells**: 16,313 (1.22%)
- **Columns**: fid, age, gender, income, pension, retire, year, expense, food, fincome1, total_asset, familysize, province_code, min_wage, min_wage_log, ln_expense, ln_food, ln_fincome1, ln_total_asset, high_minwage_growth, post, did


## Variable Roles

- **outcome**: ln_expense
- **treatment**: high_minwage_growth

## Recommended Method: IV

No panel structure detected. Consider IV or RDD if an instrument / running variable is available.

## StatsPAI Availability

- **statspai installed**: True
- **statspai version**: 1.19.0