外部验收：ACCEPT。2026-09-08 收口。

- 审阅 SHA：`0ee17abac7f6f6b72f868a4fdc27306b1adafb8e`。
- 合并前再次确认 HEAD 一致、base=main、最新 5/5 checks SUCCESS；使用 match-head-commit 保护执行 squash merge。
- Merge SHA：`c02eb05a12b99a435def10ba613eb99c5ac18201`。
- 已验证范围：runner 子进程 stdout/stderr 指向读端已关闭的同一管道，真实 POST /demos/card；修复前 FAILED，修复后 SUCCEEDED、upload_readiness=READY、7 条 run_events、产物落盘、文件通道恰一条降级记录。健康 stderr 对照也 SUCCEEDED；spawn std 流 flush 不再使健康 run 误标失败。
- 业务失败反例：业务执行器自身抛 BrokenPipeError，run 仍 FAILED，error 为 `BrokenPipeError: upload_pipeline executor failed`；RuntimeError 仍按稳定错误分类处理。不是按异常类名吞掉业务错误。
- 证据：合并树 `docs/acceptance/runner-logging-lifecycle.md` 与 `docs/acceptance/assets/runner-logging-lifecycle/`（C1/C2 summary、真实死管道 harness、业务失败反例）。本次引用已获外部 ACCEPT 的留档，没有宣称重新运行全部实验。

据此关闭 #30。结论仅限上述 logging lifecycle 与 std 流故障隔离范围；不表示所有日志故障都已解决。所有输出通道不可用时，日志仍可能丢弃。

另：撤回 PR 描述里 Card 测试失败“CI 2 核慢机放大窗口”的确定性归因及直接修轮询窗口的建议。根因待查；`_finish` 只断言 `process_one_run` 返回 True，而 FAILED 路径也可能返回 True，不能据此排除业务失败。另立 issue 诊断，独立于阶段 C。
