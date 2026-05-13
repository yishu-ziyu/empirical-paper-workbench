# Codex Phase P2-E BDD: OLS Evaluator Evidence

## Goal

`python_ols_adapter` 已经能生成 `local_execution` 级 OLS 系数。P2-E 要把它升级为可审阅的实证证据：每个 OLS 方法执行结果必须带标准误、近似 p 值、置信区间、残差自由度和 evaluator verdict，FindingCard 不能只展示裸系数。

## Behaviors

### Behavior 1: OLS method result includes inference diagnostics

Given an approved OLS RunPlan with enough numeric observations  
When the user starts a full empirical run  
Then `Results/json/method_execution_result.json` includes standard errors, t statistics, p values, confidence intervals, residual degrees of freedom, and residual standard error for the treatment coefficient.

Business rule: 系数只是点估计，不能单独作为论文证据；方法执行产物必须给出最小统计推断信息。

### Behavior 2: OLS method result includes evaluator checks

Given a completed OLS method execution  
When the method artifact is written  
Then each method item includes an `evaluator` object with a status and named checks for sample size, model rank, treatment coefficient, and inference diagnostics.

Business rule: 结果能否进入人工审阅必须先经过机器可检查的最低门槛。

### Behavior 3: Results Draft binds evaluator status to FindingCard

Given a successful full run with OLS evaluator evidence  
When the Results & Draft API builds findings  
Then `findings[].method_evidence` includes the treatment standard error, p value, confidence interval, and evaluator status.

Business rule: 结果论断卡必须让用户在同一个位置看到“系数是多少”和“这条方法证据是否通过最低检查”。

### Behavior 4: Results page renders evaluator evidence

Given a FindingCard with method evaluator evidence  
When the Results & Draft page renders  
Then the card shows evaluator status, standard error, p value, and 95% confidence interval near the method execution evidence.

Business rule: 统计证据不能只藏在 JSON 里，必须进入可视化验收路径。

### Behavior 5: Failed evaluator keeps finding review cautious

Given a method execution has missing inference diagnostics  
When the Results & Draft API builds findings  
Then `method_evidence.evaluator_status` is `needs_review` and the UI does not label it as approved evidence.

Business rule: 缺诊断的结果最多进入人工复核，不能伪装成通过的实证结论。

## Boundary Conditions

- p 值先用 normal approximation 作为最小本地实现，并在产物中标注 `p_value_method=normal_approximation`。
- 本阶段不实现稳健标准误、聚类标准误、固定效应或 DID/IV/RDD/PSM/DML evaluator。
- evaluator verdict 只是进入人工审阅前的最低门槛，不等同于经济学识别成立。
