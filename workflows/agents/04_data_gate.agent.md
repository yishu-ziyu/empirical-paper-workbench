# DataPreparationAgent

## Workflow

`04_data_gate` / 数据获取与清洗。

## Mission

证明数据能支撑研究设计，并留下可复现的数据口径。这里交付 analysis-ready 数据，不交付模糊的 Excel 手工清洗。

## Inputs

- 原始 CHARLS 数据。
- `research_design.md`
- 文献中的变量定义。
- 研究设计中的 treatment、control、post、outcome。

## Tools

- `StatsPAI_skill`
- `polars`
- `spreadsheets:Spreadsheets`
- `scripts/04_data_gate.py`

## Actions

1. 检查原始数据入口和权限边界。
2. 构造变量字典。
3. 审计缺失、重复、样本流失和面板结构。
4. 生成 analysis-ready 数据。
5. 让 `DataGateAuditor` 检查变量口径是否和文献、研究设计一致。

## Outputs

- `artifacts/data_contract.md`
- `artifacts/sample_attrition.csv`
- `artifacts/variable_dictionary.csv`
- `artifacts/did_sample.pkl`
- `artifacts/data_gate_report.md`

## Gates

- `data_gate_script`: `python3 scripts/04_data_gate.py` 通过。
- `variable_mapping_confirmed`: 人工确认变量替代合理。

## Failure Codes

- `DATA_RAW_MISSING`: 原始数据缺失。
- `DATA_KEY_VARIABLE_MISSING`: treatment、post、outcome 或 ID 缺失。
- `DATA_SAMPLE_ATTRITION_UNEXPLAINED`: 样本流失无法解释。
- `DATA_PANEL_INVALID`: 面板结构不稳定。
- `DATA_HUMAN_VARIABLE_REQUIRED`: 变量替代必须人工确认。

## Human Checkpoints

- 变量替代是否合理。
- 样本流失是否改变研究问题。
- 数据限制是否要求回到 `01_design`。

## Current CHARLS Eval

当前通过。证据：`scripts/04_data_gate.py`、`artifacts/data_contract.md`、`artifacts/sample_attrition.csv`、`artifacts/variable_dictionary.csv`、`artifacts/did_sample.pkl`、`artifacts/data_gate_report.md` 均存在。
