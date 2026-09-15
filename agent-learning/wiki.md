# econpaper Codex Experience Wiki

这里保存 Codex 开发过程跨任务成立的模式。它不替代论文证据账本、研究设计记录或产品运行数据库。

## Pattern index

| ID | 问题 | 根因 | 已验证处理 | Run records |
|---|---|---|---|---|
| FD-plan-confirm-gate | FIND-DATA plan must not rank as a confirmed-design match before confirm | Unconfirmed `session.design` is missing/draft | POST plan returns 409; GET is `status=missing`; R-sources table is plan-only | `agent-learning/raw/2026-09-15_fd-be-plan.md` |
| FIND-merge-stack-on-infer | FIND G0/plan/suggest + FL search need one tip with INFER confirm lock | Sibling write-sets share G0 `2a663915`; OpenAPI/STATE overlap | Stack on INFER `0ad7e0ae`; union routers/schemas; regen OpenAPI; confirm=`status`+`confirmed is True` | `agent-learning/raw/2026-09-15_fm-e-build-find-merge-1.md` |
| EVAL-top5-not-catalog | V1 eval must not use classic-5 as gold or require a submodule | Catalog identity conflated with EVAL-top5 | Optional `eval/` harness + submodule stub; flag off product path; refuse catalog/farm ids | `agent-learning/raw/2026-09-15_eval-top5.md` |

## Skill impact

| 日期 | 目标 Skill | 原子修改 | 固定验证集前 → 后 | 决定 | 原因 |
|---|---|---|---|---|---|

## Rejected proposals

记录被拒绝的 diff 摘要、退化指标、数据类型和适用环境，避免重复试错。

## 晋升门槛

- 至少 4 份相关运行记录，并同时包含成功与失败。
- 写清问题、根因、动作协议、适用与不适用条件。
- 一次只 create 或 patch 一个 Skill。
- 在目标模型、数据类型、研究方法和工具环境运行固定验证案例与 `make test`；涉及运行链路时再跑 `make verify` 和真实用户路径。
- 未提高主指标，或造成研究可追溯性、人工审批、恢复门槛退化时回滚 Skill；Wiki 与拒绝记录保留。
