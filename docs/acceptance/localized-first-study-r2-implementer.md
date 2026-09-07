# Localized first study — round 2 implementer

Date: 2026-09-07  
Branch: `review/localized-first-study`  
Round 2 start HEAD: `c9d36387ea6e2f554376fa046527b802a825387c`  
This HEAD: `d47a19c` (`fix(i18n): keep language switch display-only on the Card path`).  
Contract: `docs/acceptance/localized-first-study.md` (Status **open**; C1–C7 not weakened; C8–C12 are the new bar).  
Did not merge. Did not enter Phase C. Did not implement issue #30, DiD, or Research Continuity.  
Did not rewrite `docs/acceptance/localized-first-study-validator.md`.  
Did not write `localized-first-study-r2-validator.md`.

Will's S used: *Concise Language* (shortest accurate words); *Stay Out of the Way*; contextual help is pull and closable.

## Change

Chinese and English users can each finish a Card study in one UI language. Switching language only rerenders display: it does not restore the session snapshot, jump to Overview, drop Compare, or rebuild EventSource. Promote/Stale help matches research semantics. Capability inventory routes match production.

## Not this

Not a second UI. Not regex translation of backend sentences. Not writing translated labels back into criterion/specification/claim state. Not deleting `t` from restore deps only to silence lint.

## P0-1 — language switch is display-only

Root cause confirmed: `I18nProvider` rebuilt `t` every render; `useWorkspace` restore effect depended on `t` and `handleUploadRunError` (which depended on `t`). Language switch re-ran restore: `GET /sessions/{id}`, `setWorkbenchTab('overview')`, abort/reattach EventSource, unmount EvidenceLab.

Fix:

- `frontend/src/lib/i18n.tsx`: `langRef` + `useCallback` so `t` identity is stable; `t()` reads `langRef.current`; context still updates `lang`.
- `frontend/src/lib/workspace.ts`: `tRef` for recovery strings; restore effect and pending-upload recovery no longer depend on `t`. Restore stays bound to mount / stored session / session epoch.

Proof: `frontend/src/__tests__/languageSwitchDisplayOnly.test.tsx` (10 tests).

- Stable `t` identity across zh→en→zh; next render returns the new language.
- **Scene A** (Results & evidence, OLS+IV selected, Compare open, zh→en→zh):
  - still on Results & evidence (`rail-evidence` `aria-current=true`, `evidence-lab` mounted, `overview-view` absent)
  - `data-selected-ids="run-ols-exact,run-iv-exact"` unchanged
  - Compare `data-expanded="true"`
  - snapshot restore GET (`GET .../sessions/sess-lang` exact, not `/evidence` or `/degradation`) count unchanged
  - EventSource constructor count unchanged
  - no claim/promote/canonical/expectation/specification writes
- **Scene B** (spec_run in progress): same EventSource instance, not closed, restore GET count unchanged.
- **Scene C**: selected run + help details survive language switch; restore GET count unchanged.
- Existing C4 non-GET filters kept.

## P0-2 — single-language chrome

Presentation adapter: `frontend/src/lib/i18nPresentation.ts` (pure functions, unit tests). No regex of arbitrary backend sentences. Display only; stored labels unchanged.

| Surface | zh / en |
|---|---|
| OverviewView | 数据集 / Dataset; 样本行数 / Sample size; 主方法 / Main method; 上次运行 / Last run; 研究进度 / Study progress; 主结果 / Main result; 变量·系数·标准误·p 值 |
| EvidenceView | 当前主张 / Current claim; 回归结果 / Regression; 识别·稳健性; 设定详情; 数据与计算来源; 可溯源 n/m 层 / Traceable n/m layers; 完全可溯源 / Fully traceable |
| ResearchQuestion | Card estimand via teaching-case keys, not stored English as Chinese UI |
| Expectation criterion | Generated from kind/operator/refs: `IV 估计 < OLS 估计` / `IV estimate < OLS estimate`. Stored label remains `IV estimate < OLS estimate` |
| Analysis plans | Spec id → zh/en label/rationale (`ols_linear_exper` … `iv_region_dummies`) |
| Results & evidence | Surprise expected/observed from criteria+runs; compare why from changed dims; dim names via `t('evidence.dim.*')` including identification; claim explanation + 「查看原文」 / “View original” |
| Agent Cursor | zh: 研究助手 + 正在查看 / `intentZh` only. en: Agent + Looking / `intent` only. Player data still has both fields. Switch does not replay |

Allowed leftovers: variable names, formulas, OLS/IV, β/SE/p/N, Card 1995, user free text, claim original wording.

## P0-3 — Promote / Stale help

Forbidden phrases removed from `docs/product/terminology.md` and `frontend/src/lib/i18nWorkbench.ts`.

Promote: changing primary analysis changes the result paper/export cite by default. Existing claims stay bound to the evidence that formed them. Mismatch if they disagree. The system does not rewrite claims.

Stale: new relevant evidence or a changed evidence set. Promote/revert do not themselves make a claim stale. Mismatch ≠ stale.

Regression: `frontend/src/__tests__/helpSemantics.test.ts`.

## P1-4 — inventory

`docs/product/capability-inventory.md`:

- Upload: `POST /upload` (not `/uploads`)
- Export: `GET /sessions/{id}/doc-export` and `GET /sessions/{id}/code-export`
- Session restore: 「当前浏览器里的最近研究会话可在刷新或重新打开后恢复。」 No project list / cross-device claim.
- UI language status kept **已有实现但缺完整端到端证据** (C8/C9 tests pass locally; paper chapter write on the isolated Card was blocked by pre-existing `canonical_mismatch`; EvidenceView provenance timeline is not the Card-after-spec-run surface).

`app.welcomeHint` no longer says 登录后可以恢复 / “Signed-in studies can be restored later”.

## P1-5 — screenshots

Isolated ports **5174 / 8001** (`ECONPAPER_LOCAL_STATE_ROOT=/tmp/econpaper-lfs-r2`). Did not connect to, reload, or kill user processes on 5173/8000. Playwright launched a separate Chrome (`channel: 'chrome'`, new context). Chrome DevTools MCP could not attach (`DevToolsActivePort` missing); did not fall back to the daily profile.

Language-switch continuous evidence:

- `zh-evidence-compare-open-1280.png` — Compare open, OLS+IV selected, zh chrome
- `en-evidence-compare-after-switch-1280.png` — same tab, same run pair, Compare still open, en chrome

Also: zh/en empty desk 1280+1440; question 1280+1440; plans; results & evidence 1280+1440; Agent Cursor mid-demo; research claim; Paper (empty body: write blocked by `canonical_mismatch`); overview.

Deleted wrong round-1 EN unevaluated shots. Remaining round-1 files listed in `docs/acceptance/assets/localized-first-study/STALE.md`.

## Commands run (copied output)

### make test

```text
[check-api-drift] ✅ openapi.json 与后端代码同步
[check-api-drift] ✅ docs/api/openapi.json 与后端代码同步
[check-api-drift] ✅ types/api.ts 与 openapi.json 同步
819 passed, 1 skipped, 4 warnings in 61.25s
451 passed, 8 skipped, 32 warnings in 131.95s
 Test Files  58 passed (58)
      Tests  419 passed (419)
[test] agent + backend + frontend 全部通过
```

No new skip (agent 1 skipped, backend 8 skipped unchanged). Frontend 419 vs round-1 403: added tests only.

### frontend tsc / lint / build

```text
npx tsc --noEmit   # 0
npm run lint       # 0 errors; existing only-export-components warnings
npm run build
✓ built in 1.76s
```

### make check-api-drift

Included in `make test` above; 0.

## Residual

- AgentRail still dumps backend English surprise observed (`IV estimate 0.1315 > OLS estimate 0.0747`) on the zh path. Not in C9 listed surfaces; not changed.
- Isolated Card paper chapter was not written (`canonical_mismatch`). Paper chrome is single-language; results chapter body is empty.
- After Card spec runs, Results & evidence is EvidenceLab, not EvidenceView’s provenance timeline.

## Next

Independent validator writes `docs/acceptance/localized-first-study-r2-validator.md`. Do not merge.
