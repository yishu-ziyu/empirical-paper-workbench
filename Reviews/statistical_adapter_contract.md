# Statistical Adapter Contract

- 状态：needs_human_statistical_adapter_review
- normalized results：6
- 模型重跑：否
- 正式层写回：否
- 方法执行产物覆盖：否
- product state 写回：否

## Capability Matrix
- `ols`：ready=2 incomplete=0 status=contract_ready
- `ordered_logit`：ready=1 incomplete=0 status=contract_ready
- `iv`：ready=3 incomplete=0 status=contract_ready

## 人工审阅
- 核对 normalized result 是否足够支撑论文表格和方法门。
- 对 `needs_mapping_review` 的方法补齐缺失字段或保留为不可消费。
- 后续 Auto Mode 只能消费 `contract_ready` 的统计结果。
