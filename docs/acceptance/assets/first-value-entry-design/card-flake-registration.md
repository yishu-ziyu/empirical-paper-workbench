## 状态

根因：**待查**。独立缺陷诊断，不属于阶段 C 展示与首次体验，不在 PR #33 追加修复。

## 已知现象与证据

PR #33 首轮 CI 的 `test_card_spec_run.py::test_empty_criteria_write_run_read_is_unevaluated` 失败；同 commit 重跑通过。历史记录位于 `docs/acceptance/runner-logging-lifecycle.md`、PR #33。通过重跑只能证明间歇性，不能确定根因。

合并基线 `c02eb05a12b99a435def10ba613eb99c5ac18201`：`backend/tests/test_card_spec_run.py` 的 `_finish` 只断言 `asyncio.run(process_one_run(owner=owner, run_id=run_id))` 为 True。runner 即使记录 FAILED 也可能返回 True，因此此断言只说明处理过任务，不能证明成功终态或研究结果已提交。PR 里“2 核慢机时序问题”的归因未经证实，撤回；不得把读取不到 completed runs 直接等同读取可见性问题。

## 诊断采集（保留首个失败，不重试到绿）

在 `_finish` 返回及研究状态读取的前后采集同一 run_id：

- run.status、run.error、run.attempt（若存储字段不同保留原名并注明映射）、owner 与时间戳。
- 终态事件类型、顺序与时间，是否出现重复或缺失终态。
- result 是否存在及其引用/位置，避免复制敏感数据。
- completed specification runs 数量；每条的身份与执行状态，和请求的设定数量对照。
- 相关异常栈、执行/提交/读取时间及事务边界；环境信息作为上下文，不预先当根因。

## 先区分三条路径

1. 业务执行失败：FAILED/error 与执行异常对应；返回 True 不应当作成功。
2. 终态提交异常：业务结果已产生但 result/终态/事件提交不一致；查失败发生在哪个提交边界。
3. 读取可见性问题：先有证据证明成功终态与 result 已持久化，再查不同读取视图/事务看到的 completed runs。

## 后续验收要求

- 留下可复核的失败快照，解释返回 True 与真实终态的区别。
- 根因依据上述分类证据确定；证据不足继续标待查。
- 修复前复现失败，修复后验证同一路径，并证明真实业务 FAILED 不会被测试误认成功。
- 禁止直接增加固定 sleep、放宽业务断言或重试到绿。任何等待机制须由已证实的生命周期条件驱动。

本 issue 仅登记；本轮不改测试或研究引擎。
