# econpaper Codex Run Record

- Date: 2026-09-02
- Task ID / state file: 20260902-durable-upload-recovery / runtime/tasks/20260902-durable-upload-recovery.md
- Commit / Git context: chore/local-workspace-cleanup; uncommitted mixed worktree
- Model and tool environment: Codex local workspace; Python 3.12; PostgreSQL 16; Vitest; Vite; in-app browser
- Dataset class / research method（不含原始数据）: synthetic panel CSV; no user dataset
- Task: Make upload and cleaning durable across API/browser/Runner interruption, and revoke all execution authority when the Session is deleted.
- Result: pass
- Session / run ID: dynamically generated acceptance runs; removed after verification
- Verification commands: focused pytest and Vitest; make test; PostgreSQL-only pytest; npm run build; make verify; make smoke-agent; make verify-deps; make check-api-drift; git diff --check; browser fault injection
- Output evidence locations: docs/plans/2026-09-02-1324-fix-durable-upload-recovery-plan.md; backend/tests/test_postgres_upload_recovery.py; backend/tests/test_run_execution.py; frontend/src/lib/__tests__/runEvents.test.ts; frontend/src/__tests__/App.test.tsx

## 成功动作

- Admission now durably binds one UUIDv4 upload key to one Session, one upload Run, one accepted event, and one private input artifact.
- The API returns 202 without running cleaning; a separately reclaimable Runner executes the pure upload pipeline in an epoch-scoped workspace.
- Lease fencing prevents stale workers from publishing progress, terminal state, Session readiness, or authoritative output paths.
- Session deletion revokes database authority first, then terminates the active process tree and removes Session-owned artifacts without touching another Session.
- Frontend recovery persists the upload intent and Run handle, resolves ambiguous acceptance without retransmitting the file, and combines SSE with durable status polling.
- A real browser run survived API SIGKILL and restart, then changed from recovery state to READY on the same page without a second refresh.

## 失败动作与根因

- EventSource error handling alone did not recover a half-open Vite proxy connection; a coalesced one-second status watchdog now runs while every durable Run is active.
- A previous cleaning report remained visible during the next upload because upload intent did not clear that snapshot; new upload admission now clears it before network work.
- Five legacy tests still expected synchronous 200 uploads and no idempotency key; they now exercise the accepted 202 contract, explicitly run the worker, and inspect database Run events plus epoch-scoped artifacts.
- Final adversarial review found bounded-upload, event-loop blocking, S3 publication/delete, refresh ordering, expired-lease, failed-attempt cleanup, and public-contract gaps. Each concrete gap received a regression test and passed; an independent validator rejected two remaining blocker claims after checking cascade and process-tree evidence.

## 可复现条件

- Select a CSV and wait until the frontend persists the Session and active upload Run.
- Refresh the page, terminate the API while the Run remains active, let the Runner finish, then restart the API.
- Without another refresh, the page resolves the same Run, shows the dataset as ready, removes the direction block, and enables direction submission after the required fields are filled.
- Delete the Session during a blocking upload child and verify the process tree exits within one second and no delayed result or artifact becomes authoritative.

## 候选模式

- Treat file acceptance and database admission as a recoverable protocol with reconciliation, not as an in-memory request lifecycle.
- Put long work behind a lease-fenced worker and an OS-terminable process boundary; keep persistence authority in the parent.
- Use SSE for responsiveness and bounded status polling for durability because half-open connections may emit neither data nor a useful error.
- Re-run acceptance from the public contract after delegation; implementation review alone does not expose runtime gaps.

只记录可复核动作、去敏 ID 和证据位置；不得复制用户原始数据、论文正文、凭据、私人对话或隐藏推理。
