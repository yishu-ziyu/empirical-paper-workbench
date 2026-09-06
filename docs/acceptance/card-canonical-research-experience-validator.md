# Validator report: Card Canonical Research Experience (C1–C29)

Date: 2026-09-06  
Branch: `review/workbench-v2` @ `226546b` (dirty working tree; Card work uncommitted)  
Evaluator: independent validator. Did not implement. Did not treat implementer summaries as proof.  
Chrome DevTools MCP: **not connected** (`Could not find DevToolsActivePort`). Live 1280/1440 re-walk was not possible. Browser checks use archived PNGs + `m5-dom-assertions.json` + `m5-errors.json` + live `GET /sessions/5cafe0c4-00e9-41d5-85ef-24792cf71d75` and `GET .../research` on the still-running 5173/8000.

## Verdict: ACCEPT

Named relaxations R1–R6 were applied as written, not expanded. Previous REQUEST CHANGES (incomplete M5 archive, recovery falling back to `card_1995.csv` / `待确认方向`, no C20/C23 browser proof) is closed by the current pack for session `5cafe0c4-00e9-41d5-85ef-24792cf71d75`.

---

## Commands run (this validator)

`make test` (includes `check-api-drift`):

```
[check-api-drift] ✅ openapi.json 与后端代码同步
[check-api-drift] ✅ docs/api/openapi.json 与后端代码同步
[check-api-drift] ✅ types/api.ts 与 openapi.json 同步
809 passed, 1 skipped, 4 warnings in 32.28s
416 passed, 8 skipped, 32 warnings in 110.73s
 Test Files  53 passed (53)
      Tests  345 passed (345)
[test] agent + backend + frontend 全部通过
```

Skip counts vs R4 / baseline: agent 1 skip, backend 8 skip, frontend 0 skip. No new skip. Frontend test count 344 → 345 (added coverage, not a skip).

`cd frontend && npx tsc --noEmit` → `TSC_EXIT:0`

`cd frontend && npm run lint` → `Found 6 warnings and 0 errors.` `LINT_EXIT:0`

`cd frontend && npm run build`:

```
tsc -b && vite build
✓ 499 modules transformed.
✓ built in 1.60s
BUILD_EXIT:0
```

`make verify` (5173 and 8000 up):

```
[verify-deps] agent StatsPAI editable source
[verify-deps] backend StatsPAI editable source
[verify] econpaper frontend http://127.0.0.1:5173
[verify] econpaper backend http://127.0.0.1:8000
{"status":"ok"}[verify] agent import
graph ok
VERIFY_EXIT:0
```

Grep `0.0747|0.1315|14.214` in `frontend/`: no matches. R2 holds.

Grep `from 'gsap'` / `@gsap` in `frontend/src`: no matches. Agent Cursor uses `motion`.

Live session `5cafe0c4-00e9-41d5-85ef-24792cf71d75`: `research.teaching_case=card_1995`; dataset rows=3010; columns include `lwage,educ,nearc4,exper,expersq,black,smsa,south` (wooldridge extract, not 9-col); `frozen_at=2026-09-06T09:10:12+00:00`; 12 defs; 14 specification_runs (12 exploratory + OLS linear preview + IV region-dummy preview); comparable OLS·1966 region dummies **0.074693…** / IV **0.131503…** / `F_eff=14.138…`; canonical estimate coef=0.13150383625543327, formula includes `smsa66`+`reg66*`; claim `approved_by_user=true` with three wordings; Results `grounded=true` content includes educ 0.1315038….

---

## Checks

### C1 空桌 Card 入口 — PASS

`DeskPage.test.tsx`: `data-testid="desk-try-card"` text includes `Try a real study` and `Card`.  
`App.test.tsx`: click calls `POST /demos/card`, not `/samples/course-panel.csv`.  
`m5-empty-desk-1280x800.png` (same bytes as `m1-empty-desk-1280x800.png`): button `Try a real study · Card` on empty desk, distinct from left-rail `课设样例：年龄与收入`. DOM `empty-desk.deskTryCard="Try a real study · Card"`.

### C2 teaching-case 标记 — PASS

Live `GET /sessions/{id}`: `research.teaching_case == "card_1995"`.  
UI: `Teaching case · Card 1995` on question / frozen / evidence / recovery shots. Badge remains on Question after paper (`m5-recovery-claim-question-1280x800.png`, `m5-question-1440x900.png`). Not presented as the user’s own study at boot. Walker `teaching:false` after `prepare-paper` is the header subtitle switching to `iv · lwage ~ educ`; the teaching badge is still on the Question surface.

### C3 真实 Card 数据 — PASS

Live dataset rows=3010; columns include required `lwage,educ,nearc4,exper,expersq,black,smsa,south`. Backend `test_card_demo_boots_3010_rows_required_columns_and_provenance`.  
`frontend/src/__tests__/cardCanonicalLiterals.test.ts` + grep: no `0.0747|0.1315|14.214` in frontend source.

### C4 Question / estimand — PASS

`m5-question-1280x800.png` / 1440: Outcome / Treatment / Causal threat / Candidate identification / Estimand. Live question object matches. `WorkbenchArtifact.test.tsx` + `SnapshotRecovery.test.tsx`.

### C5 Expectation 可恢复 — PASS

Backend PUT/GET tests still in the 416. Live expectation text `I expect OLS to be positive. If ability creates upward bias, IV may be smaller.` with history/confidence.  
Browser: freeze-recovery and post-claim-recovery screenshots still show that textarea. `SnapshotRecovery.test.tsx` storage-clear path. No frontend `setItem` of expectation as a business store.

### C6 Admissible space freeze — PASS

Live: 12 definitions; `frozen_at` set. Screenshots: `Admissible space frozen` / `Frozen 2026/9/6 17:10:12` at 1280 (during walk) and 1440 (same session). Compare results not visible on the freeze frame. Backend freeze-before-results / 409-unfrozen tests in suite.

### C7 状态来自 backend snapshot — PASS

`test_snapshot_research_matches_research_read_model` in backend suite.  
Grep: no `localStorage`/`sessionStorage` writes of `teaching_case` / research_lab / expectation as business copies. `SnapshotRecovery.test.tsx` asserts `econpaper_research_lab` / `econpaper_expectation` remain null.

### C8 M1 门禁 — PASS

`make test` green; skip counts unchanged vs R4; `npm run build` green. Browser empty desk → question → frozen at 1280; 1440 frozen of same session. `m5-errors.json` is `[]`. DOM `errors: []` on those frames. `scrollWidth==clientWidth`.

### C9 多条真实 SpecificationRun — PASS

Live `specification_runs=14` (≥2). Each has spec id, choices, estimator, formula, covariance, analysis_dataset (path/hash/name), producer_run_id, coef/se/p/n, status, provenance, created_at, relation.  
`test_card_ols_and_iv_runs_are_real`. Comparable pair is extract-path 0.0747/0.1315, not winsorize ~0.0687.

### C10 preview 不覆盖 canonical — PASS

`test_preview_does_not_change_canonical_estimate`. Live: preview OLS linear 0.0932 and preview IV exist with `relation=preview`; canonical remains IV 0.131503… (`source_run_id` of the promoted IV). `m5-run-preview-1280x800.png` matrix shows 0.0932 while Preview proposal says canonical unchanged until promote.

### C11 Promote / Revert — PASS

`test_promote_updates_canonical_and_revert_restores`. UI still exposes Promote / Revert on Evidence Lab screenshots.

### C12 Evidence Lab 三层 — PASS

`EvidenceLab.test.tsx`. Browser: results space + CI dots + OLS/IV grouping (`m5-cursor-1280x800.png`, `m5-compare-1440x900.png`); choice matrix; Compare βA→βB / Δ abs / Δ % / changed/unchanged (`m5-compare-1280x800.png`).

### C13 OLS vs IV identification — PASS

`test_compare_ols_iv_names_identification`.  
`m5-compare-1280x800.png` and DOM `compare`: `βA → βB 0.0747 → 0.1315 · Δ 0.0568 · 76.1%`, intent `Identification strategy changed`, Changed: estimator, identification. Live formulas: OLS `lwage ~ educ + exper + expersq + black + smsa + south + smsa66 + reg66*`; IV `(educ ~ nearc4)` plus the same controls; covariance HC1 vs nonrobust recorded. R2: not UI constants.

### C14 Surprise 确定性规则 — PASS

`evaluate_surprise` tests still in suite. UI + live payload: Unexpected / ordering_mismatch / Expected: IV may be smaller than OLS / Observed: IV > OLS.

### C15 Challenge 可执行 — PASS

`test_accept_challenge_creates_preview_run`. Screenshot `Accept challenge` (instrument strength). Live `next_challenge.status=accepted` with `resulting_runs` pointing at a preview `iv_region_dummies`. DOM after accept: `Accepted`.

### C16 IV diagnostic 真实 — PASS

Live `F_eff=14.138670079757798` from `effective_f_test` / HC1 / controls including region dummies — not a copy string. UI `effective F=14.14`. `test_iv_diagnostic_f_comes_from_controlled_spec`.

### C17 SemanticTargetRegistry — PASS

`frontend/src/lib/agentCursor/registry.ts`. Scripts use `evidence.spec.ols` / `evidence.spec.iv` / `evidence.choice.estimator` / `evidence.choice.experience`. `control.ts` rejects `{x,y}`, `querySelector`, XPath, CSS selector strings. `agentCursor.test.ts` asserts the same.

### C18 Point 不改研究状态 — PASS

`agentCursor.test.ts`: point and Show-me script never call `runPreview` or `promote`.

### C19 Demonstrate/Preview 不改 canonical — PASS

Challenge script: `runPreview` no-op until `confirm('runPreview')`; promote not called. C10 + live canonical 0.1315 after preview runs.

### C20 Cursor 行为 — PASS (R5)

Program: 浏览器. Archive now has it.

- `m5-cursor-1280x800.png`: overlay on IV cluster, label **Agent / Looking**, rail **Cancel / Replay**. DOM: `cursor=true`, `cursorPointerEvents=none`, then `yield.paused=true`, `cancelled`.
- `m5-cursor-1440x900.png`: Agent Looking + Cancel/Replay after resize; `w=1440` `sw=1440`.
- `m5-preview-proposal-1280x800.png`: `Run this preview?` / **Run Preview**.
- Implementation: `motion` transform (`AgentCursorLayer.tsx`); `pointer-events-none`; missing-target abort; resize/scroll re-resolve highlights; `travelDurationMs(true)===0`; `data-reduced-motion`; no new GSAP import in `frontend/src`.
- Intent: Show-me script sets `Identification strategy changed` after the compare step. The 1280 cursor PNG is early (intent null → “Looking”). Claim-jump DOM later has `cursorIntent: "Little changed"`. R5: not pixel curves; semantic target, yield, reduced-motion, do not change research state. 1440 cursor sits near the header (animation start / post-resize); not used to fail under R5.

### C21 Claim Ledger 一条 — PASS

Live claim: supported / conditionally supported / unsupported wordings match spec §11; `supporting_run_ids` chain to OLS/IV spec runs; `counter_evidence` nonempty; `unresolved_assumptions` nonempty; version=1; provenance. `test_space_run_auto_drafts_card_claim_fields`. Screenshots `m5-claim-ledger-1280x800.png` / `m5-evidence-lab-1440x900.png`.

### C22 用户批准 — PASS

`test_claim_approve_required_for_results_and_bind_includes_runs`. `m5-claim-ledger-1280x800.png`: **Approve claim**. `m5-claim-approved-1280x800.png` / jump / recovery: **Approved**. Live `approved_by_user=true`.

### C23 Paper Results 消费 Claim — PASS

`m5-paper-results-1280x800.png` and `m5-paper-results-1440x900.png`: Results chapter, badge **基于证据**, Linked Evidence β=0.1315 N=3010, table educ **0.13150383625543327**, **View Claim / Evidence**. DOM `paper.grounded="基于证据"` `link=true`. `m5-claim-jump-1280x800.png` after click: Claim Ledger **Approved**. R1: placeholder LLM prose is out of scope; the number is the real spec_run. `test_unsupported_wording_is_not_grounded`; `paper-claim-link` tests.

### C24 stale — PASS

`test_promote_marks_results_stale`. ChapterWriter stale UI tests still in the 345.

### C25 浏览器 canonical journey — PASS

Same session `5cafe0c4-00e9-41d5-85ef-24792cf71d75` at 1280 then 1440.

Archived path (DOM + PNGs, looked at pixels not just names):

| Step | Evidence |
| --- | --- |
| Empty desk | `m5-empty-desk-1280x800.png` |
| Try Card → Question / Expectation / estimand | `m5-question-1280x800.png` |
| Freeze | `m5-frozen-1280x800.png` Frozen 17:10:12 |
| Mid-journey recovery | `m5-recovery-frozen-1280x800.png` |
| Run specs → Evidence Lab / Surprise / Show me | continue `evidence-lab`; `m5-evidence-lab-1280x800.png` |
| OLS vs IV compare | `m5-compare-1280x800.png` 0.0747→0.1315 F=14.14 |
| Diagnose / challenge | `m5-challenge-1280x800.png` |
| Show me cursor | `m5-cursor-1280x800.png` |
| Cursor preview + Run Preview | `m5-preview-proposal-1280x800.png`, `m5-run-preview-1280x800.png` (OLS·linear 0.0932) |
| Claim approve | `m5-claim-ledger-1280x800.png`, `m5-claim-approved-1280x800.png` |
| Paper Results | `m5-paper-results-1280x800.png` |
| Claim jump | `m5-claim-jump-1280x800.png` |
| 1440 | question / frozen / evidence-lab / compare / cursor / claim-ledger / paper-results; DOM `w=1440` `sw=1440` |

Coefficients are extract-path 0.0747 / 0.1315 / F≈14.14, not sidecar ~0.0687. No 0.0687/0.0834 in the current PNG pack.  
`m5-errors.json` = `[]`; DOM `finalErrors: []`; frames `errors: []`.

Note (does not fail): `firstWalk` recorded `TimeoutError` waiting 180s for `evidence-lab` (contract itself: 12 specs may exceed 2 min). `continue` on the **same** session completed the rest. 1440 shots are a post-completion resize of that session, not a second empty-desk walk; C25 requires both viewports, which are archived, with `scrollWidth==clientWidth`.

### C26 刷新恢复 — PASS

After freeze, storage-clear refresh (`m5-recovery-frozen-1280x800.png` + DOM `recovery-frozen-question`): title **Does education increase earnings?** (not `card_1995.csv`); rail **已确认** (not 待确认方向); subtitle Teaching case · Card 1995; Question + Expectation still filled; Design **Admissible space frozen**.

After runs/claim (`m5-recovery-claim-question-1280x800.png`, `m5-recovery-claim-1280x800.png` + DOM `recovery-claim-evidence`): same Question/Expectation; rail 已确认; Claim **Approved**; Evidence Lab + Surprise + challenge Accepted; Evidence rail **β 0.1315**. Live API still has freeze, 14 runs, approved claim. `SnapshotRecovery.test.tsx` now covers teaching_case / question / freeze **and** runs+claim.

### C27 回归门禁 — PASS

`make test` 809/1skip + 416/8skip + 345; `tsc --noEmit` 0; lint 0 errors; `npm run build` 0; `check-api-drift` 0; `make verify` 0. Workbench v2 SnapshotRecovery tests in the 345. No new skip (R4).

### C28 ADR 0015 — PASS

`docs/adr/0015-card-canonical-research-experience.md`: SpecificationRun in `research_lab`; preview vs canonical (`spec_run` must not write top-level estimate); Cursor semantic-id contract; Claim Ledger truth boundary (approve before grounded Results); extract vs winsorize sidecar.

### C29 validator 独立 ACCEPT — PASS

This report is ACCEPT.

---

## What is not a fail

- Frontend hardcoded 0.0747 / 0.1315 / 14.214: absent.  
- Agent Cursor control plane: semantic ids only.  
- `spec_run` cannot persist top-level `estimate`.  
- Claim approve gate.  
- R3 nine-column path tests remain; this journey used the wooldridge extract (region specs ran).  
- R4 skip budget unchanged.  
- R1 placeholder Results prose.  
- Walker `firstWalk` 180s timeout then continue on the same session.  
- Chrome MCP still down; archive + live REST of that session used instead of a third walk.  
- After `prepare-paper`, header subtitle is `iv · lwage ~ educ` (teaching badge still on Question).  
- 1440 compare/claim-ledger PNGs crop the results-space/matrix rather than the Compare/Ledger cards; Ledger is visible on `m5-evidence-lab-1440x900.png`, and 1440 DOM has `compareDelta` 0.0747→0.1315 plus claim text.
