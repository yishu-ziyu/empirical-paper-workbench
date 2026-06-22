# ResearchDesignAgent

## Workflow

`01_design` / 选题与研究设计。

## Mission

把用户 idea 变成一句可检验的研究设计：X 影响 Y，用 Z 识别，数据是 D，贡献是 Q。

## Inputs

- 用户 idea。
- 数据线索。
- 政策或 treatment 线索。
- 可选：已有文献线索。

## Tools

- `aer-topic-selection`
- `research_design.md`
- `causal_question.yaml`
- `design_risk.md`

## Actions

1. 提取 outcome、treatment、post、control、研究对象和时间范围。
2. 写一句话研究设计。
3. 列出可能贡献和最近文献对照。
4. 让 `DesignAuditor` 审计内生性、变量不可观测、贡献过弱和数据不匹配。
5. 只有研究问题、数据和贡献三者能对齐时，进入 `02_literature`。

## Outputs

- `research_design.md`
- `causal_question.yaml`
- `design_risk.md`

## Gates

- `one_sentence_design`: 人工确认一句话设计能说清。
- `artifact_presence`: `python3 scripts/21_route_next_workflow.py` 不再报告本步骤缺产物。

## Failure Codes

- `DESIGN_TREATMENT_UNCLEAR`: 处理变量不清楚。
- `DESIGN_OUTCOME_UNCLEAR`: 结果变量不清楚。
- `DESIGN_NO_CONTRIBUTION`: 贡献不足以成文。
- `DESIGN_DATA_NOT_SUPPORTING`: 数据无法回答问题。
- `DESIGN_HUMAN_REQUIRED`: 需要研究者决定是否继续。

## Human Checkpoints

- 这个题是否值得继续。
- 贡献是否够写成论文。
- 识别假设是否可以接受。

## Current CHARLS Eval

当前通过。证据：`research_design.md`、`causal_question.yaml`、`design_risk.md` 均存在；主张已收窄为不支持稳健平均减负。
