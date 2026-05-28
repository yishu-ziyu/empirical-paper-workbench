# Method Knowledge Base Plan

Date: 2026-05-28

## Node Goal

P7-F turns the existing methodology boundary, AER-like proposal metadata, and method-gate heuristics into a CLI-first Method Knowledge Base that MethodAgent can query before formal method design or Auto Mode acceptance.

This node is read-only with respect to formal research state. It can produce JSON and Markdown review artifacts, but it cannot promote proposal rules to canonical rules or write formal product state.

## BDD Behaviors

### Behavior 1: Separate canonical and proposal method sources

Given `Program/methodology/README.md`, canonical rules, and proposal YAML files exist
When Method KB indexes the methodology library
Then it reports canonical and proposal sources separately
And proposal sources are marked non-blocking for formal export
And reviewed canonical blocking rules are the only rules allowed to block formal export.

Business rule: 未人工 review 的外部技能只能提示，不能成为正式门禁。

### Behavior 2: Query CGSS OLS + Ordered Logit method checks

Given a query mentions CGSS, subjective happiness, social capital, OLS, and Ordered Logit
When Method KB assembles relevant checks
Then it returns checks for ordered outcomes, OLS interpretation limits, endogeneity risk, controls, robustness, heterogeneity, mechanisms, and candidate citation verification.

Business rule: 方法知识库要服务 MethodAgent 的具体设计审阅，不只是列目录。

### Behavior 3: Recommend AER-like standards without over-enforcement

Given profile `aer_like`
When Method KB assembles policy
Then AER-like standards are recommended
And proposal rules remain recommendation-only until canonical review.

Business rule: 顶刊标准可以提高要求，但 proposal 不越权。

### Behavior 4: Write review artifacts without formal writeback

Given Method KB output is written
When CLI finishes
Then JSON and Markdown review files exist
And formal manuscript, bibliography, DesignSpec, RunPlan, product state, and canonical rules are not modified.

Business rule: P7-F 是知识库/审阅层，不写正式层。

### Behavior 5: Block if methodology sources are missing

Given no methodology README or rules exist
When Method KB indexes the project
Then it returns `blocked_missing_methodology_sources`
And it does not invent checks from absent sources.

Business rule: 没有规则来源时不能伪造知识库状态。

## Boundary Conditions

- No network access.
- No external repository sync.
- No proposal-to-canonical promotion.
- No formal manuscript writeback.
- No formal bibliography or project bibliography writeback.
- No `state/product/*` writeback.
- No canonical rule creation in this node.

## Verification

- RED: `python3 -m unittest tests.test_method_knowledge_base -v` fails because `Program.workbench.method_knowledge_base` does not exist.
- GREEN: target tests pass after minimal CLI implementation.
- Real run writes `Results/json/method_knowledge_base.json` and `Reviews/method_knowledge_base.md`.
