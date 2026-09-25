# econpaper Codex Task State

> 复制为稳定 Task ID 文件。只保存新会话恢复下一步所需的当前工作集。

- Task ID: REFRESH-LOCK-AND-P3-MAKER
- Status: complete
- Git context（分支可选）: worktree `empirical-paper-workbench-wt-refresh-lock`，分支 `fix/refresh-lock-and-p3`，基于 `66d49f0b`
- Goal: 修复 `docs/reviews/20260925-retro-review-9e830281.md` 列出的 6 项问题（P1 SSE 断开致 SQLite 写锁死 + 4 个 P3 + `git diff --check`），提交候选版本供独立评审
- Hard bar: 每项先写复现失败测试，红转绿都留证据；不弱化断言、不新造第二套状态系统；`make test` / lint / build / `git diff --check` / `make docs-check` / `check_docs.py --changed main` 全绿
- Session / run ID: 无（本任务不产生用户研究数据）
- Current research stage: n/a
- Current review / approval gate: 交独立评审（新一轮，看不到本文件）
- Verified facts:
  - P1 根因：`routers/run_execution.py:stream_run_events` 的 `generate()` 在客户端断开时被 Starlette 的 anyio cancel scope 取消；未加保护时这次取消会在同一 task 里对后续每个 await（含 DB session 的 close）重新投递，可能让 aiosqlite 连接半开半关
  - 修复：`await repo.events_after(...)` / `await repo.get(...)` 及 `_sse_connections` 计数释放全部包一层 `asyncio.shield`，让 DB 往返（含 session close）作为独立 task 跑完
  - 诚实记录：本地用真实 uvicorn + 真实 TCP 断开（250 次随机时机 + 20 次强制命中查询窗口的确定性重放 + 300 次并发批量断开）在当前依赖版本（SQLAlchemy 2.0.36 / Starlette 0.38.6 / aiosqlite）下没有复现出锁死或连接泄漏——每次 `ROLLBACK` 都正常收尾。组件测试因此改为直接断言"被取消时 DB 往返协程本身有没有被允许跑完"（shield 的直接效果），而不是断言下游 SQLite 症状
  - P3 幂等 key 根因：`services/formal_binding.py` 的会话请求台账（record_confirms 用）和 `run_repository.py` 的 runs 表幂等（continue_estimate 用）是两套独立存储，共享同一个 HTTP `Idempotency-Key` 头但互不知道对方用过这个 key
  - P3 busy 清空根因：`workspace.ts` 的 `continueEstimate` 的 `finally` 块无条件 `setDirectionBusy(false)`，即使这次调用自己从未把它设成 true（因为是刷新恢复的另一个 run 在跑）
  - P3 上传忙根因：`uploadResponse()` 对所有非 2xx 一律 `new RunRequestError(status)`，丢失了 409 body 里的 `detail.code`，`handleUploadRunError` 因此无法分辨 `session_busy` 和真失败
  - P3 换数据提示根因：后端 `supersede_dataset` 清空 `main_specification` 但保留 `research_direction` 摘要；前端从未读取/暴露 `main_specification`，右栏的 `blockingDecision` 推导链因此没有对应分支
- Current hypothesis: 无遗留假设；6 项均已定位到具体代码行并修复
- Changed files:
  - `backend/routers/run_execution.py`（P1 asyncio.shield）
  - `backend/services/formal_binding.py`（`ledger_claims_key`）
  - `backend/run_repository.py`（`_reject_cross_ledger_key`）
  - `backend/facade/session_store.py`（`mutate_state(idempotency_key=...)`）
  - `backend/facade/__init__.py`（`record_prewrite_confirms` 传 key）
  - `backend/services/formal_chain.py`（删多余空行）
  - `frontend/src/lib/workspace.ts`（`ownsDirectionBusy`、`uploadResponse` 409 解析、`handleUploadRunError` busy 分支、`mainSpecification` 状态）
  - `frontend/src/lib/i18n.tsx`（`app.uploadBusy`）
  - `frontend/src/lib/i18nWorkbench.ts`（`decision.directionStale*`）
  - `frontend/src/components/PrewriteConfirmCard.tsx` / `WorkbenchArtifact.tsx`（`hasActiveRun`）
  - `frontend/src/App.tsx`（`decision.directionStale` 分支）
  - `backend/tests/test_run_execution.py`、`backend/tests/test_formal_chain_binding.py`
  - `frontend/src/components/__tests__/PrewriteConfirmCard.test.tsx`、
    `frontend/src/lib/__tests__/workspaceConfirmationOwnership.test.tsx`、
    `frontend/src/lib/__tests__/workspaceCommandIdempotency.test.tsx`、
    `frontend/src/__tests__/App.test.tsx`
  - `docs/api/prewrite-confirm.md`、`docs/specs/frontend-interaction-current.md`、
    `docs/notes/devlog.md`、`docs/reviews/README.md`、
    `docs/reviews/20260925-retro-review-9e830281.md`（从主 checkout 复制）
- Failed paths: 无未解决的失败路径；P1 的"真实环境复现"路径本身没有失败（见上方诚实记录），不是遗留缺口
- Data / output evidence locations: 无用户数据；P1 的临时 e2e 验证用了 `/tmp/p1_e2e/`（仓库外，未提交）
- Test evidence:
  - `make test` → agent 1088 passed + 2 skipped；backend 736 passed + 8 skipped + 13 subtests；frontend 562 passed（75 files），全部 exit 0
  - `cd frontend && node_modules/.bin/oxlint` → 0 error（既有 warning 不算）；`npm run build`（`tsc -b && vite build`）→ exit 0
  - `git diff --check` → 0；`make docs-check` → 0（4 条 frozen-oversized WARN 是既有文件，未改动）；`python3 scripts/check_docs.py --changed main` → 0
  - 6 项问题逐一用 `git stash` 隔离对应源码文件，验证新测试红→绿：
    - P1: `backend/tests/test_run_execution.py::test_sse_disconnect_mid_query_lets_the_db_round_trip_finish`
    - 幂等: `backend/tests/test_formal_chain_binding.py::test_confirm_key_reused_for_estimate_is_idempotency_conflict` / `test_estimate_key_reused_for_confirm_is_idempotency_conflict`
    - busy 清空: `frontend/.../workspaceConfirmationOwnership.test.tsx` 里的 `keeps directionBusy set when continueEstimate 409s...`
    - 按钮仍可点: `frontend/.../PrewriteConfirmCard.test.tsx` 里的 `P3: keeps start-estimate disabled...`
    - 上传忙: `frontend/.../workspaceCommandIdempotency.test.tsx` 里的 `reports session_busy on attach as busy...`
    - 换数据提示: `frontend/src/__tests__/App.test.tsx` 里的 `P3: 换数据后右栏提示重新核查研究方向...`
  - `make verify` 未运行（本任务未起三进程冒烟；`make test` 已覆盖静态检查）
- Pending external state: 无。worktree 里 `backend/.venv`、`agent/.venv`、`frontend/node_modules` 的软链已删除；本任务启动的临时 uvicorn 进程（端口 8931）已 kill
- Next action: 交独立评审判定候选 SHA（见交付时的 `git log -1`）；不在本任务范围：证据溯源代码层（P2）、VoiceOver、完整 Tab 顺序、真实数据验收、P1 在 Postgres 下的表现
- Updated at: 2026-09-25

不得写入凭据、用户原始数据、未公开论文正文、私人对话或隐藏推理。
