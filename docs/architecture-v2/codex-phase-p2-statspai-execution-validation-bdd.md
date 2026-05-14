# Codex Phase P2-N BDD: StatsPAI Execution Validation

## 背景

P2-K 已经把 StatsPAI / StataMCP 暴露为候选后端，但候选后端不等于真实执行证据。P2-N 的最小目标不是一口气复刻 CoPaper，而是让已批准 RunPlan 的 baseline OLS 能被 StatsPAI 真实调用一次，生成独立产物和交叉验证结果。

## 行为 1：StatsPAI 可用时必须进入执行层

Given 项目已经确认 VariableRoleSet、DesignSpec 和 RunPlan  
And RunPlan 包含 OLS baseline task  
And 本地 Python 环境可以 import `statspai`  
When 用户启动 full run  
Then 方法执行结果必须包含 `backend_validations`  
And 其中 `statspai` validation 的 `status` 为 `passed`  
And `evidence_level` 为 `local_execution`

业务规则：StatsPAI 不能只停留在 UI 候选后端；只要本地可用且任务边界支持，就必须产生一次真实执行证据。

## 行为 2：StatsPAI 必须写出独立产物

Given StatsPAI validation 已执行  
When full run 完成  
Then 项目必须写出 `Results/json/statspai_execution_result.json`  
And 产物中包含 formula、dataset_path、nobs、系数、p 值、诊断和 summary text

业务规则：真实执行必须可追溯，不能只把第三方库结果临时留在内存中。

## 行为 3：StatsPAI 结果必须和主 Python OLS 结果交叉验证

Given Python OLS adapter 与 StatsPAI 都完成同一公式估计  
When 系统生成 evaluator checks  
Then treatment 系数必须在容差内一致  
And validation checks 必须记录比较对象、容差和差异值

业务规则：StatsPAI 在 MVP 中先作为 secondary validation backend，不替代主 adapter；它的价值是帮助发现执行差异。

## 行为 4：StatsPAI 不可用或不支持输入时必须结构化阻塞

Given StatsPAI 无法 import 或输入数据不是当前 adapter 支持的 CSV numeric formula rows  
When full run 进入后端验证  
Then validation 必须返回 `blocked`  
And 说明 blocker code  
And 不能把 blocked validation 标记为 `local_execution`

业务规则：没有真实调用就不能宣称真实执行；阻塞也要成为可审计产物。

## 边界条件

- 本阶段只覆盖 OLS baseline 的 StatsPAI 二次验证。
- StataMCP/Stata 仍需下一步生成 do-file/log 后才能升级为 `local_execution`。
- DID / IV / RDD / PSM / DML 仍在方法目录和前置条件检查层，不在本阶段直接执行。
