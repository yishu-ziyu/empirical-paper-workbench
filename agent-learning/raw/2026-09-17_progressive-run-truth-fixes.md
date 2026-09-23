# econpaper Codex Run Record

- Date: 2026-09-17
- Task ID / state file: PROGRESSIVE-RUN-TRUTH-1 / `runtime/tasks/20260917-progressive-run-truth-fixes.md`
- Commit / Git context: `feat/progressive-research-flow` @ merge commit `2d83c2c9c716` + uncommitted fixes; no push
- Model and tool environment: ChatGPT via DevSpace checkout; Python 3.12 agent/backend venvs; Node 22/Vitest/Vite frontend
- Dataset class / research method（不含原始数据）: synthetic run events and existing test fixtures; no user dataset
- Task: Integrate main/#40, make progressive run disclosure truthful across ownership/recovery/truncation/blocked states, and close review/process gaps.
- Result: pass
- Session / run ID: synthetic test runs only
- Verification commands: `make test`; `make test-backend`; targeted authority/outline/WS pytest; frontend tsc/test/lint/build; PR handoff checker; YAML parse; `git diff --check`
- Output evidence locations: `docs/acceptance/progressive-run-truth-fixes.md`; frontend progress/workspace files and tests; `backend/runner.py`; `backend/tests/test_run_execution.py`; `.github/workflows/ci.yml`

## 成功动作

- Merged `main@d2f5533` before fixing; the resulting tree retains #40 and the progressive disclosure without rewriting reviewed commits.
- Replaced a global event array with run-owned (`sessionId/runId/kind`) short-term observation state; stale events and stale finalizers cannot overwrite a newer run.
- Routed fresh upload, Card upload, pending-upload recovery, active-run recovery, prewrite, and spec-run waits through one tracking seam. Spec runs keep their more truthful dedicated k/total UI.
- Made blocked text explicit, stopped inferring terminal completion from progress events, exposed truncation, and kept unknown raw node IDs in details rather than user-facing summaries.
- Added App-level SSE-to-workspace-to-footer tests, not only projector/component tests.
- Added production gating for `/spike`, PR merge-tree/handoff checks, and a single acceptance contract.
- Full-suite load exposed a runner authority false-negative. Extending one probe from 200ms to 650ms fixed short database contention while continuous failure/stuck probes still cancel within one second and terminal writes remain owner/epoch fenced.
- Final verification passed: Agent 1066, Backend 636, Frontend 504; API drift, TypeScript, lint, and production build passed.

## 失败动作与根因

- The first full backend run left a WebSocket prewrite run in `RUNNING`; isolated rerun passed. A second full run failed a different direction test with the same symptom, proving a systemic timing issue rather than a single flaky assertion.
- Root cause: the heartbeat treated two 200ms authority probe delays as lease loss after only 400ms, cancelled valid child work, and intentionally left the fenced run reclaimable in `RUNNING`.
- An interim 5s failure grace made tests green but weakened the prior sub-second cancellation contract; it was rejected and replaced with a wider single-probe timeout plus bounded continuous-failure timing.
- Browser/VoiceOver verification was not performed because this task did not start the frontend/backend services or have a browser control tool.

## 可复现条件

- Under a loaded SQLite suite, overlap progress-event writes with heartbeat authority reads; with the former 200ms timeout, a valid run could be cancelled and remain `RUNNING`.
- Feed progress from run A after run B owns the footer; the new owner check keeps B unchanged.
- Fill 200 unique progress keys, then complete an existing active key; the latest status still updates. Add a 201st key; the buffer retains the new fact and reports one omitted step.
- Refresh onto a snapshot with an active prewrite run, replay SSE events, and observe the same disclosure as a fresh run.

## 候选模式

- Treat progress UI as an owned projection of one durable run, not as a session-global event bag.
- A progress event can close an observed step but cannot prove the durable run succeeded; terminal truth comes from the run record/snapshot.
- Distinguish an explicit negative authority result from temporary inability to query authority. Keep the uncertainty window bounded and preserve write fencing.
- Generate machine-verifiable handoff facts in CI; require humans only for runtime evidence, known gaps, and disagreements.

只记录可复核动作、去敏 ID 和证据位置；不得复制用户原始数据、论文正文、凭据、私人对话或隐藏推理。
