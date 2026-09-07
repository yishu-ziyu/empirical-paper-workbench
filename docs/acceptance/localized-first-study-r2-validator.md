# Localized first study — independent validator round 2 (C8–C12 + C7)

Date: 2026-09-07
Validator: independent (did not implement; did not treat `docs/acceptance/localized-first-study-implementer.md` or `docs/acceptance/localized-first-study-r2-implementer.md` as proof)
Repo: `/Users/mahaoxuan/Desktop/经济学论文/econpaper`
Branch: `review/localized-first-study`
HEAD: `001461bf37847782e6351421e4db1700ee15f73f` (`git rev-parse HEAD` matches expected)
Working tree at start: clean
Contract: `docs/acceptance/localized-first-study.md` (Status **left open**)
Historical REJECT: `docs/acceptance/localized-first-study-validator.md` **not edited** (`git diff HEAD --` on that file is empty; file still starts with `## Verdict: REJECT`)
Scope: C8–C12 REQUEST CHANGES bar; C7 quality gates on this HEAD. C1/C2/C10/C11 docs re-read. Did not connect to, reload, or kill the user's daily browser on 5173/8000. Product code was not edited. This file is the only write. Did not merge. Did not push.

Named relaxations honored: isolated browser (this validator used vitest + archived screenshots, not the daily 5173/8000 session); no backend snapshot diff; paper/claim original language allowed.

## Verdict: ACCEPT

C8–C12 programs pass on this HEAD. C7 local gates exited 0; PR #32 CI check runs on `headRefOid` `001461bf37847782e6351421e4db1700ee15f73f` are SUCCESS. Historical C1–C7 REJECT file remains the round-1 record. This ACCEPT does not close contract Status, does not merge, and does not claim every product capability is ready to ship.

Screenshot lag is recorded below. Contract C12 explicitly asks to record whether a zh-rail `IV estimate 0.13…` dump is still in **source on this HEAD**. It is not.

## C8 — language switch does not re-run restore

Command:

```bash
cd frontend && npx vitest run src/__tests__/languageSwitchDisplayOnly.test.tsx
```

Output (tail):

```
 ✓ src/__tests__/languageSwitchDisplayOnly.test.tsx (10 tests) 514ms
 Test Files  1 passed (1)
      Tests  10 passed (10)
```

(Full frontend later: 419 passed / 0 failed.)

Test file read: `frontend/src/__tests__/languageSwitchDisplayOnly.test.tsx`.

- Restore snapshot GET is counted via `snapshotRestoreGets` (`method === 'GET'` and `/\/sessions\/sess-lang\/?$/`). Research writes are a separate filter. The test is **not** only “ignore GET”.
- Fake `EventSource` constructor counter.
- Scene A: Evidence tab, exact `run-ols-exact` / `run-iv-exact`, Compare `data-expanded=true`, zh→en→zh; tab stays evidence; selected ids unchanged; Compare still open; restore GET count unchanged; EventSource count unchanged; no claim/promote/run writes.
- Scene B: live `spec_run` `run-spec-live`; same EventSource instance; `closed === false`; restore GET unchanged.
- Scene C: evidence tab, selected `run-ols-exact`, promote help open across language switch; restore GET unchanged.
- Unsaved expectation text is a dedicated test (`unsaved expectation text survives language switch with no PUT`), not typed inside the App Scene C block. Covered.
- Stable translator: `stable translator identity still reads the new language after switch` asserts `new Set(seen).size === 1` while zh/en/zh labels change.

Source (not “delete `t` to silence lint”):

- `frontend/src/lib/i18n.tsx`: `t = useCallback(..., [])` reads `dict[langRef.current]`. Comment: “Stable identity: language switch must re-render UI (lang in context) without giving workspace restore a new `t` dependency.”
- `frontend/src/lib/workspace.ts`: `tRef.current = t`; restore effect deps are `[applySnapshot, handleUploadRunError, returnToUploadDesk, showGlobalError]`; comment: “t / language is intentionally not a dependency: restore is session-bound.” Recovery strings use `tRef.current(...)`.
- `setWorkbenchTab('overview')` exists only inside that restore effect when `snapshotHasResearchContent(data)` — language switch does not re-enter the effect (Scene A: `queryByTestId('overview-view')` is null).

C8 pass.

## C9 — core path single-language display

Commands:

```bash
cd frontend && npx vitest run \
  src/components/__tests__/OverviewView.test.tsx \
  src/components/__tests__/EvidenceView.test.tsx \
  src/components/__tests__/ResearchLabPanels.test.tsx \
  src/components/__tests__/EvidenceLab.test.tsx \
  src/components/__tests__/AgentCursorLayer.test.tsx \
  src/components/__tests__/AgentRail.test.tsx \
  src/lib/__tests__/i18nPresentation.test.ts
```

Output (tail):

```
 Test Files  7 passed (7)
      Tests  58 passed (58)
```

(Those 7 files plus C8/C10 in one combined run: 9 files, 71 passed.)

Grep of OverviewView / EvidenceView / ResearchLabPanels / EvidenceLab / AgentCursorLayer / AgentRail / App.tsx for quoted Chinese chrome: user-facing hardcoded Chinese strings were **not** found (only comments). Banned stacked literals (`New study · 回工作台`, `Evidence Lab（…）`, `Research trace · 研究记录`, …) appear only in `cardCanonicalLiterals.test.ts` (the ban list). `npx vitest run src/__tests__/cardCanonicalLiterals.test.ts`: 3 passed.

`frontend/src/lib/i18nPresentation.ts` read:

- Criterion labels from `kind` / `operator` / estimator refs, not stored English `label` as Chinese UI (`displayCriterionLabel`).
- Spec label/rationale by semantic id (`presentation.spec.${specId}.*`); no write-back.
- Surprise expected/observed from criteria + run coefs (`displaySurpriseObserved`).
- Compare why / dimension names structured.
- Assumptions: closed key map plus prefix fallbacks; return `raw` if unknown; **not written back**.

`App.tsx` and `AgentRail.tsx` on this HEAD call `displaySurpriseObserved(...)` for the decision/rail observed sentence, with `t('agent.unexpectedObserved')` fallback. `AgentRail.test.tsx` asserts:

```
expect(screen.getByTestId('agent-cursor-prompt')).toHaveTextContent('IV 估计 0.1300 > OLS 估计 0.0800')
expect(screen.getByTestId('agent-cursor-prompt')).not.toHaveTextContent('IV estimate')
```

`AgentCursorLayer.tsx`: zh uses `presentation.intentZh || t('agent.looking')` (`正在查看`); en uses `presentation.intent || t('agent.looking')` (`Looking`); identity `t('agent.identity')` = 研究助手 / Agent.

ResearchLabPanels still **stores** English criterion labels (`label: 'IV estimate < OLS estimate'`) when constructing structured criteria. Display goes through `displayCriterionLabel`. Language-switch test after reveal shows zh `IV 估计 < OLS 估计` then en `IV estimate < OLS estimate` with `onSave` not called.

**Screenshot vs source (not a C9 source fail):** several archived zh shots still print backend `IV estimate 0.1315 > OLS estimate 0.0747` on the rail. Source on **this HEAD** does not dump that string (see AgentRail test + `displaySurpriseObserved`). Same for Compare `identification` in mid-demo shots vs `displayDimension` (`evidence.dim.identification` → 识别 / Identification) and zh-claims assumption parentheticals vs `displayAssumption` in `EvidenceLab.tsx`.

**Residual, not used as REJECT:** Paper write-blocked path still shows snapshot `write_blockers` code `canonical_mismatch` as decision reason (`App.tsx` `reason: ws.writeBlockers[0]`) and backend 409 message `当前 Claim 依赖 IV specification，但正式主规格不是该 IV。` (`backend/services/research_lab.py`). Machine code / pre-existing integrity toast. Claim **buttons/status/help** on the claims shots are in the UI language (设为主分析 / 写结果章 / 已批准 / 当前证据支持). Claim wording variants remain original English (allowed).

C9 pass on this HEAD source + tests.

## C10 — Promote / Stale help semantics

Read `docs/product/terminology.md` and `frontend/src/lib/i18nWorkbench.ts`.

- Promote: 设为主分析 / Set as primary analysis. Help: 改论文和导出默认引用的主结果；已有结论仍绑定当时的证据. UI: `evidence.helpPromoteMore` “已有结论仍绑定形成它时的证据。结论与主分析不一致时显示 mismatch。系统不会改写结论。”
- Stale: 证据已更新，请重新核对 / Evidence updated — review needed. Help: 相关证据更新了，旧结论不能继续当作已核对. UI: `claim.helpStaleMore` “新的相关证据或证据集合变化才会让结论变成 stale。设为主分析或恢复已有运行本身不会。mismatch 与 stale 是不同状态。”

Command:

```bash
cd frontend && npx vitest run src/__tests__/helpSemantics.test.ts
```

```
 ✓ src/__tests__/helpSemantics.test.ts (3 tests) 2ms
```

Forbidden phrases (including `研究结论所依据的数字…都会跟着当前主分析走` and `估计或主分析变了，旧结论不能继续当作已核对`) are absent.

C10 pass.

## C11 — inventory paths and restore honesty

Read `docs/product/capability-inventory.md` against `docs/api/openapi.json`.

- Upload: inventory `POST /upload`. OpenAPI `"/upload": { "post": ... }`. No `/uploads` in the inventory.
- Export: inventory `GET /sessions/{id}/doc-export` and `GET /sessions/{id}/code-export`. OpenAPI `"/sessions/{session_id}/doc-export"` GET and `"/sessions/{session_id}/code-export"` GET.
- Restore: “当前浏览器里的最近研究会话可在刷新或重新打开后恢复.” Limits: no project list, no cross-device discovery. Status: 已在明确范围验证 **(current browser session id only)**.
- 界面语言 status: **已有实现但缺完整端到端证据** (not 已在明确范围验证). Matches C11: this validator accepts C8/C9 on source+tests, but inventory correctly does not over-claim end-to-end UI language.

C11 pass.

## C12 — round 2 evidence files

`docs/acceptance/assets/localized-first-study/` listing (this validator):

Required pairs present:

| Scene | zh | en |
|---|---|---|
| empty desk | `zh-empty-desk-1280.png`, `zh-empty-desk-1440.png` | `en-empty-desk-1280.png`, `en-empty-desk-1440.png` |
| question+expectation | `zh-question-1280.png`, `zh-question-1440.png` | `en-question-1280.png`, `en-question-1440.png` |
| analysis plans | `zh-plans-1280.png`, `zh-plans-1440.png` | `en-plans-1280.png` (no en 1440; 1280/1440 cover other core pages) |
| results & evidence | `zh-evidence-1280.png`, `zh-evidence-1440.png` | `en-evidence-1280.png`, `en-evidence-1440.png` |
| Agent Cursor mid-demo | `zh-agent-cursor-mid-demo-1280.png` | `en-agent-cursor-mid-demo-1280.png` |
| research claim | `zh-claims-1280.png`, `zh-claims-1440.png` | `en-claims-1280.png`, `en-claims-1440.png` |
| Paper Results | `zh-paper-1280.png`, `zh-paper-1440.png` | `en-paper-1280.png`, `en-paper-1440.png` |
| evidence provenance | `zh-evidence-provenance-1280.png` | `en-evidence-provenance-1280.png` |

Language-switch continuous evidence: `zh-evidence-compare-open-1280.png` → `en-evidence-compare-after-switch-1280.png`. Same Results & evidence tab, same OLS/IV pair (0.0747 / 0.1315), Compare still open. STALE.md states these two are valid C8 evidence.

`STALE.md` read. Marks round-1 / mismatched files; EN unevaluated pair deleted; remaining marked: `zh-unevaluated-no-criteria-1280.png`, `zh-unevaluated-unresolved-1280.png`, `zh-run-1280.png`, `en-run-1280.png`, `zh-jump-evidence-1280.png`, `en-jump-evidence-1280.png`. Those files still exist on disk and are labeled stale (not presented as this HEAD). Historical REJECT file untouched.

This validator opened:

- zh/en empty desk: 体验一项真实研究 / Explore a real study; 教育与工资的经典公开案例 / A classic public study of education and wages. Single UI language.
- zh question: criterion `IV 估计 < OLS 估计`; expectation **user original** English kept (allowed).
- zh plans: 确认分析方案; spec labels in Chinese; spec ids kept (allowed).
- zh/en claims: decision/buttons/status/help in UI language; claim wording originals English (allowed); 查看原文 / View original present.
- zh paper: chrome 研究记录 / 写作 / 预览 / 历史 in Chinese (historical stacked `Research trace · 研究记录` is gone). Body empty (write blocked).
- zh/en agent cursor: 研究助手 / 正在查看 vs AGENT / English intent.
- zh provenance / evidence lab center: `预期: IV 估计 < OLS 估计` and `观察到: IV 估计 0.1315 > OLS 估计 0.0747` (structured). Rail in those PNGs still shows English `IV estimate 0.1315 > OLS estimate 0.0747`.

**Source on this HEAD for that rail sentence:** does **not** dump `IV estimate …`. `displaySurpriseObserved` + AgentRail/App. STALE.md already says not to treat the rail sentence in the compare pair as C9 proof.

C12 pass with the screenshot-lag record above.

## C7 — quality gates on this HEAD

```bash
make test
# agent: 819 passed, 1 skipped
# backend: 451 passed, 8 skipped
# frontend (inside make test): 419 passed (419)
# [test] agent + backend + frontend 全部通过
# exit 0

cd frontend && npx tsc --noEmit    # TSC_EXIT:0
cd frontend && npm run lint        # 6 warnings, 0 errors; LINT_EXIT:0
cd frontend && npx vitest run      # Tests 419 passed (419); VITEST_EXIT:0
cd frontend && npm run build       # tsc -b && vite build; built in 1.69s; exit 0
make check-api-drift               # DRIFT_EXIT:0
```

Skip counts match the prior C7 record (agent 1, backend 8). Frontend: no `test.skip` / `it.skip` / `describe.skip` under `frontend/src`. No new skip introduced in this round’s tests.

PR #32 (`gh pr view 32 --json headRefOid,statusCheckRollup`):

```
headRefOid: 001461bf37847782e6351421e4db1700ee15f73f
后端 + Agent pytest              SUCCESS
前端 类型 / 测试 / lint / 构建     SUCCESS
API 契约同步 + 前端类型            SUCCESS
Docker 镜像构建                   SUCCESS
GitGuardian Security Checks      SUCCESS
```

CI corresponds to this HEAD. Did not merge.

C7 pass.

## C1/C2 (re-read, not the r2 bar)

- C1 inventory still covers the required capability list with the required fields and allowed statuses. Card 0.0747/0.1315 vs CI 0.0740/0.1323 remains 复现待核. 文稿语言未实现.
- C2 terminology still has Canonical / Promote / Claim Ledger / Stale / Provenance / Grounded mappings. Display language only.

## Commands copied (raw tails)

`make test` (this validator):

```
819 passed, 1 skipped, 4 warnings in 47.37s
451 passed, 8 skipped, 32 warnings in 141.38s
Test Files  58 passed (58)
      Tests  419 passed (419)
[test] agent + backend + frontend 全部通过
```

`npm run lint`:

```
Found 6 warnings and 0 errors.
Finished in 38ms on 142 files with 104 rules using 8 threads.
```

Contract Status remains **open**. Parent/user closes. No merge.
