# Statistical Adapter Contract Plan

Date: 2026-05-28

## Node Goal

P7-G defines a CLI-first Statistical Adapter Contract for Auto Mode. It normalizes existing statistical execution artifacts into a common schema that downstream paper-package, quality-gate, and manuscript agents can consume without guessing backend-specific fields.

This node does not run models. It reads existing execution/evidence JSON and writes a contract report plus human review Markdown.

## BDD Behaviors

### Behavior 1: Normalize local method execution results

Given `method_execution_result.json` contains local OLS or IV methods
When the contract is built
Then each method is normalized into a common result record with method id, engine, evidence level, dataset, formula, nobs, focal coefficient, inference, diagnostics, and reproducibility refs.

Business rule: 后续 Auto Mode 不能为每个执行后端单独猜字段。

### Behavior 2: Normalize CGSS OLS and Ordered Logit evidence

Given CGSS results evidence contains OLS and Ordered Logit primary results
When the contract is built
Then both are normalized under the same statistical result contract
And ordered outcome levels and sample consistency are preserved.

Business rule: OLS 与有序模型要能被同一论文包链路消费。

### Behavior 3: Expose capability and missing-field matrix

Given supported and incomplete method families are present
When the capability matrix is produced
Then contract-ready methods are counted
And incomplete methods expose missing required fields instead of being silently trusted.

Business rule: 统计适配器必须明确可消费程度。

### Behavior 4: Write review artifacts without execution or formal writeback

Given contract outputs are written
When CLI finishes
Then JSON and Markdown review files exist
And no model is rerun
And formal manuscript, bibliography, DesignSpec, RunPlan, product state, and execution artifacts are not modified.

Business rule: P7-G 是契约层，不是执行层。

### Behavior 5: Block when no statistical source exists

Given no statistical source artifacts are supplied
When the contract is built
Then it returns `blocked_missing_statistical_sources`
And it does not invent normalized results.

Business rule: 没有执行证据时不能伪造统计结果契约。

## Boundary Conditions

- No model execution.
- No StatsPAI/Stata/Python backend invocation.
- No formal manuscript writeback.
- No formal bibliography or project bibliography writeback.
- No DesignSpec or RunPlan writeback.
- No `state/product/*` writeback.
- No overwrite of source execution artifacts.

## Verification

- RED: `python3 -m unittest tests.test_statistical_adapter_contract -v` fails because `Program.workbench.statistical_adapter_contract` does not exist.
- GREEN: target tests pass after minimal contract implementation.
- Real run writes `Results/json/statistical_adapter_contract.json` and `Reviews/statistical_adapter_contract.md`.
