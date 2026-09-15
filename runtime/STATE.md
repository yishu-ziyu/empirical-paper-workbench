# econpaper Codex Runtime State Index

> 新会话先读本页，再按用户意图打开对应任务文件。这里是短索引，不承载完整运行历史。

| Task ID | State file | Status | Git context | Updated at | Next action |
|---|---|---|---|---|---|
| FM-E-BUILD-DID-BE-SPEC re-cut | `runtime/tasks/20260915-fm-e-build-did-spec-recut.md` | complete | `feat/fm-e-build-did-spec-recut-1` from `9f154dda` | 2026-09-15 | confirmed did missing treat×period hard-blocks; no PR |
| FM-E-BUILD-FIND-MERGE-1 | `runtime/tasks/20260915-fm-e-build-find-merge-1.md` | complete | `feat/fm-e-build-find-merge-1` @ `552cf397` | 2026-09-15 | stacked on INFER; `make test` green; no PR |
| FM-E-BUILD-INFER-MERGE-1 | `runtime/tasks/20260915-fm-e-build-infer-merge-1.md` | complete | `feat/fm-e-build-infer-merge-1` @ `759ce5d6` | 2026-09-15 | pushed; `make test` green; no PR |
| 20260915-inf-be-propose | `runtime/tasks/20260915-inf-be-propose.md` | complete | `feat/fm-e-build-inf-be-propose-1` @ `874ecb3` | 2026-09-15 | slice done; no PR |
| FM-E-BUILD-INFER-DESIGN-1 / INF-BE-confirm | `runtime/tasks/20260915-inf-be-confirm.md` | complete | `feat/fm-e-build-inf-be-confirm-1` from `2a663915` | 2026-09-15 | later slices call `locked_design()`; no PR |
| FM-E-BUILD-INFER-DESIGN-1 / DID-BE-gate recut | `runtime/tasks/20260915-fm-e-build-did-gate-recut.md` | complete | `feat/fm-e-build-did-gate-recut-1` | 2026-09-15 | pushed; no PR |
| 20260915-fd-be-plan | `runtime/tasks/20260915-fd-be-plan.md` | complete | `feat/fm-e-build-fd-be-plan-1` | 2026-09-15 | FD-BE-plan pushed; no PR |
| 20260915-fl-be-search | `runtime/tasks/20260915-fl-be-search.md` | complete | `feat/fm-e-build-fl-be-search-1` | 2026-09-15 | FL-BE-search landed; no PR |
| 20260915-fm-e-build-attach-404 | `runtime/tasks/20260915-fm-e-build-attach-404.md` | complete | `fix/fm-e-build-attach-404-1` @ `1de9dfa` | 2026-09-15 | pushed; no PR |
| 20260907-localized-first-study | `runtime/tasks/20260907-localized-first-study.md` | active | `review/localized-first-study` / PR #32 | 2026-09-07 | r2 implementer 已交；待 r2 validator；不 merge |
| 20260907-m1-empty-criteria-unevaluated | `runtime/tasks/20260907-m1-empty-criteria-unevaluated.md` | complete | PR #31 squash `87c5e5b` (reviewed `0192c74`) | 2026-09-07 | 外部 ACCEPT 已 merge |
| 20260907-m1-expectation-criterion-p0 | `runtime/tasks/20260907-m1-expectation-criterion-p0.md` | complete | `review/generic-research-spine-hardening` / PR #31 | 2026-09-07 | r2 validator ACCEPT；push PR #31；不 merge |
| 20260906-card-research-semantics-consistency | `runtime/tasks/20260906-card-research-semantics-consistency.md` | complete | `review/workbench-v2` | 2026-09-06 | validator ACCEPT；浏览器 S5–S7 过；待 CI |
| 20260906-card-canonical-research-experience | `runtime/tasks/20260906-card-canonical-research-experience.md` | complete | `review/workbench-v2` | 2026-09-06 | validator ACCEPT；CI 待 Card commit |
| 20260902-run-cancellation | `runtime/tasks/20260902-run-cancellation.md` | complete | `chore/local-workspace-cleanup` | 2026-09-02 | Select the next full-stack issue |
| 20260902-upload-event-loop | `runtime/tasks/20260902-upload-event-loop.md` | complete | `chore/local-workspace-cleanup` | 2026-09-02 | Select the next full-stack issue |
| 20260902-durable-upload-recovery | `runtime/tasks/20260902-durable-upload-recovery.md` | complete | `chore/local-workspace-cleanup` | 2026-09-02 | Select the next full-stack issue |

## 启动与写回

1. `active` / `blocked` 且与用户意图匹配：读取对应任务文件后继续。
2. 多个任务都可能匹配：先确认，不覆盖任何状态。
3. 新长任务：复制 `runtime/tasks/TEMPLATE.md` 为 `runtime/tasks/YYYYMMDD-short-slug.md`，再登记一行。
4. 里程碑、压缩、交接或退出前：先更新任务文件，再更新本表。
5. 完成后标为 `complete`，生成不可变去敏运行记录；旧任务文件保留。

不得写入凭据、用户原始数据、未公开论文正文、私人对话或隐藏推理。
