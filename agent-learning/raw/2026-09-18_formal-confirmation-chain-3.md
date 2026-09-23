# econpaper Codex Run Record

- Date: 2026-09-18
- Task ID / state file: FORMAL-CONFIRMATION-CHAIN-3 / `runtime/tasks/20260918-formal-confirmation-chain-3.md`
- Commit / Git context: `feat/progressive-research-flow@2d83c2c9c716` + inherited uncommitted changes; no commit/push
- Model and tool environment: ChatGPT direct via DevSpace; backend/runner/frontend local; `ECONPAPER_LLM=mock`; no delegated Agent
- Dataset class / research method: deterministic synthetic CSV; OLS
- Task: repair CHAIN-2 review findings S1–S5 and investigate repeated durable-run claiming
- Result: pass
- Session / run ID: see redacted browser report under evidence root; task state does not duplicate IDs
- Verification commands: focused pytest/vitest; full `make test`; frontend lint/build; `git diff --check`; real Playwright three-process path and response-loss fault injection
- Output evidence locations: `../empirical-paper-workbench-evidence/formal-confirmation-chain-3/`

## 成功动作

- Bound confirmations and execution to opaque server-owned object identities rather than local display guesses.
- Made design revision locking and run admission transactional with the session state they validate.
- Archived superseded evidence and removed it from the current evidence read model.
- Enforced idempotency intent equivalence and recovered lost responses with the same delivery credential.
- Relinquished only still-owned stopped work while preserving lease epoch fencing; final real runs completed on first claim.

## 失败动作与根因

- Early focused regressions exposed tests that still encoded the old unbound-confirmation semantics and a too-strict alias comparison; they were corrected only where the product contract had changed and the corresponding stronger tests were added.
- The earlier mobile run repeatedly reclaimed because a transient authority probe cancellation left the worker lease RUNNING until expiry. A RED test reproduced that stopped worker did not return its lease.

## 可复现条件

- Cross-window replacement between rendering and confirmation.
- Data replacement after a successful estimate.
- Same idempotency key reused for a different action/input.
- Lost 200 confirmation response or lost 202 run-accepted response.
- Worker cancellation while its owner+epoch lease is still valid.

## 候选模式

- Approval should name an immutable observed target; never infer “the user meant current” at request arrival.
- Upstream version changes should archive dependent facts and empty the current read model, not merely set a warning bit beside stale numbers.
- Durable work that stopped locally should explicitly return a still-owned lease; fencing, not a long idle lease, provides stale-worker safety.
