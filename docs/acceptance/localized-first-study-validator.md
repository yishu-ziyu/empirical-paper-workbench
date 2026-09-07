# Localized first study — independent validator (C1–C7)

Date: 2026-09-07
Validator: independent (did not implement; did not treat implementer conversation or `docs/acceptance/localized-first-study-implementer.md` as proof)
Repo: `/Users/mahaoxuan/Desktop/经济学论文/econpaper`
Branch: `review/localized-first-study`
HEAD: `87c5e5b726911130d4490efd10194ed4241817a5`
Working tree: **dirty** (uncommitted localized-first-study work on this checkout; this validator did not commit, push, or merge)
Contract: `docs/acceptance/localized-first-study.md`
Scope: C1–C7.
Contract Status: **not edited** (left `open`).

Did not connect to, reload, or kill the user's daily browser on port 5173. Did not kill user processes. Product code was not edited. This file is the only write.

## Verdict: REJECT

C3 source still hardcodes stacked bilingual core chrome on Paper Results (explicitly in C3 coverage). Named C6 screenshot gaps are recorded as facts and are **not** the reject reason. C7 quality gates this validator ran exited 0. This REJECT does not claim all product capabilities are ready to ship. It does not close the contract Status.

## Failures (do not paraphrase)

`frontend/src/components/WorkbenchArtifact.tsx:498` - Paper Results summary is hardcoded stacked chrome `Research trace · 研究记录` - C3 source grep + zh/en paper screenshots + `WorkbenchArtifact.test.tsx:194` still asserts `/Research trace · 研究记录/`. Same root cause as the next Paper strings.

`frontend/src/components/ChapterWriter.tsx:147` - Paper Results stale copy is hardcoded `Stale · needs regeneration` - C3 source grep.

`frontend/src/components/ChapterWriter.tsx:161` - Paper grounded badge is hardcoded `'基于证据' : '未 grounded'` (zh + leftover English `grounded`) - C3 source grep. Same Paper Results surface.

`frontend/src/components/ChapterWriter.tsx:169` - jump control is hardcoded `View Claim / Evidence` (not language-split) - C3 source grep. Same Paper Results surface.

`frontend/src/components/EvidenceView.tsx:138,149,155,166,192,206,234` - provenance titles hardcoded stacked `Result · 结果数字`, `Specification · 研究设定`, `Estimator · 估计量`, `Run · 运行`, `Dataset · 数据集`, `Code · 代码`, header `Evidence · 结论与来源` - C3 source grep. Not in `cardCanonicalLiterals` banned list, so that test is green while source still stacks.

`frontend/src/components/OverviewView.tsx` - Overview chrome hardcoded Chinese (`数据集`, `样本行数`, `主方法`, `上次运行`, `研究进度`, station labels `数据清洗`/`设计设定`/…) with no `useT` - C3 source read. EN screenshots `en-unevaluated-no-criteria-1280.png` and `en-unevaluated-unresolved-1280.png` show this Chinese Overview under an English-selected header.

`frontend/src/components/EvidenceLab.tsx:715` - Evidence matrix history control hardcoded English `History {n} (Preview · {n} runs)` - C3 source grep. Not bilingual stack; leftover English on the zh Evidence path.

C3 `cardCanonicalLiterals.test.ts` only bans a closed regex (`New study · 回工作台`, `Evidence Lab（证据实验室）`, …). Those exact literals are gone from product source (only remain in that test). That is **not** sufficient for C3: Paper Results still stacks.

## C1 — capability inventory

Program: read `docs/product/capability-inventory.md`.

Covered required capabilities: 数据导入和清洗、数据探索、研究问题、预期、分析方案、单次估计、多方案比较、诊断与稳健性、文献、Agent 演示、结论确认、章节编辑/回滚、证据关联、文档和代码导出、会话恢复、登录与归属、界面语言、上手入口、运行部署.

Each section contains: 用户任务、界面入口、生产执行路径、持久化对象、已有验证、适用范围、依赖条件、限制、允许对外使用的描述、下一步, plus 状态.

Statuses used are only the four allowed values (some items combine two allowed phrases for different scopes, e.g. Card vs 自带数据). No completion percentage.

Card coefficients recorded as 复现待核: local 0.0747/0.1315 vs CI 0.0740/0.1323; not attributed to verified platform float error.

文稿语言: inventory states there is no independent manuscript-language switch.

C1 program matches the contract. Not used to override C3.

## C2 — terminology

Program: read `docs/product/terminology.md`.

Required display mappings present:

- Canonical = 当前主分析 / Primary analysis
- Promote = 设为主分析 / Set as primary analysis
- Claim Ledger = 研究结论 / Research claims
- Stale = 证据已更新，请重新核对 / Evidence updated — review needed
- Provenance = 数据与计算来源 / Data & calculation sources
- Grounded = 已关联当前证据 / Linked to current evidence

File states these are 展示语言 and do not require renaming backend objects. 文稿语言未实现 is written honestly.

C2 program matches the contract. Not used to override C3.

## C3 — language-split chrome (FAIL)

Commands this validator ran:

```bash
cd frontend && npx vitest run \
  src/__tests__/cardCanonicalLiterals.test.ts \
  src/__tests__/DeskPage.test.tsx \
  src/__tests__/App.test.tsx \
  src/components/__tests__/ResearchLabPanels.test.tsx \
  src/components/__tests__/EvidenceLab.test.tsx \
  src/components/__tests__/AgentRail.test.tsx \
  src/components/__tests__/DocExportDialog.test.tsx \
  src/components/__tests__/CodeExportDialog.test.tsx
```

Copied result (exit 0):

```
 Test Files  8 passed (8)
      Tests  128 passed (128)
   Start at  20:05:59
   Duration  3.50s (transform 1.48s, setup 1.10s, import 2.31s, tests 5.00s, environment 6.10s)
```

Grep leftover stacked chrome in `frontend/src` excluding tests (this validator):

```
frontend/src/components/WorkbenchArtifact.tsx
498:                  Research trace · 研究记录

frontend/src/components/ChapterWriter.tsx
147:          Stale · needs regeneration
161:            {chapter.grounded !== false ? '基于证据' : '未 grounded'}
169:            View Claim / Evidence

frontend/src/components/EvidenceView.tsx
138:      title: 'Result · 结果数字',
149:      title: 'Specification · 研究设定',
155:      title: 'Estimator · 估计量',
166:      title: 'Run · 运行',
192:      title: 'Dataset · 数据集',
206:      title: 'Code · 代码',
234:          Evidence · 结论与来源

frontend/src/components/EvidenceLab.tsx
715:                            History {groupRuns.length} (Preview · {groupRuns.length} runs)
```

`frontend/index.html` default `lang="zh-CN"`. `htmlLangAttr` maps zh→`zh-CN`, en→`en`. Empty-desk CTA keys: zh `体验一项真实研究` / en `Explore a real study`; hint zh `教育与工资的经典公开案例`. Desk/App/ResearchLabPanels/EvidenceLab/AgentRail **listed** stacked titles (`New study · 回工作台`, `Boot failed · 启动失败`, `Evidence Lab（证据实验室）`, `Try a real study · Card`) are not in product source.

C3 still fails because Paper Results (and related evidence/overview chrome) remain stacked or language-hardcoded.

## C4 — language switch is display-only

Command:

```bash
cd frontend && npx vitest run src/__tests__/languageSwitchDisplayOnly.test.tsx
```

Copied result (exit 0):

```
 ✓ src/__tests__/languageSwitchDisplayOnly.test.tsx (6 tests) 266ms
 Test Files  2 passed (2)
      Tests  7 passed (7)
```

(The 7 includes TaskHelp in the same invocation; language-switch file alone is 6 tests.)

Tests intercept `fetch`, cover unsaved expectation (no PUT / `onSave`), spec_run (research write count unchanged), approved claim (no claim/promote/canonical/expectation/specification mutating calls), post-reveal locked criterion (no translated-label PUT; criterion text stays `IV estimate < OLS estimate`), help open/close (no research writer). `frontend/src` has **no** `XMLHttpRequest` usage. This validator found **no** backend session snapshot before/after diff program to re-run.

C4 frontend fetch intercept matches the spirit of “language switch does not write research.” The contract program also asked for `XMLHttpRequest` intercept + backend snapshot diff; those pieces were not present to re-run. Incomplete program is recorded; reject is C3, not C4.

## C5 — task-side help, no forced wizard

Command:

```bash
cd frontend && npx vitest run src/components/__tests__/TaskHelp.test.tsx
```

Copied result (exit 0):

```
 ✓ src/components/__tests__/TaskHelp.test.tsx (1 test) 92ms
```

Test: summary visible; details pull; Enter toggles; close; Tab leaves to another button; no focus trap; toggling help does not fire a save callback.

Source: `TaskHelp` on confirm-plans (`ResearchLabPanels.tsx` `help-confirm-plans`), promote (`EvidenceLab.tsx` `help-promote`), stale claim (`help-stale`), OLS/IV `MethodHelp`. Agent Cursor `showMe` is opt-in (`AgentRail.tsx`). No forced eight-step tour on Desk. CHARLS wizard is a separate own-data path, not the Card empty-desk CTA.

Isolated-browser keyboard trap was not re-driven in a live browser by this validator (C6 screenshot `zh-help-confirm-plans-1280.png` shows pull help “收起说明”). C5 is not the reject.

## C6 — screenshots (gaps as facts, not automatic reject)

Required files present:

- zh/en empty desk 1280 and 1440
- zh/en question 1280 and 1440
- zh/en evidence 1280 and 1440
- zh/en paper 1280 and 1440

Also present: zh/en claims 1280/1440, zh plans 1280/1440, en plans 1280, zh/en run 1280, zh/en jump-evidence 1280, zh help-confirm-plans 1280, zh/en unevaluated-no-criteria 1280, zh/en unevaluated-unresolved 1280.

Gaps (facts):

- No boot-failure / retry screenshot in this asset dir.
- Missing 1440: en-plans, zh-run, en-run, zh-jump-evidence, en-jump-evidence, zh-help-confirm-plans, en-help-confirm-plans (1280 also missing), zh/en unevaluated-no-criteria, zh/en unevaluated-unresolved.
- `en-unevaluated-no-criteria-1280.png` and `en-unevaluated-unresolved-1280.png` are Overview, not Unevaluated evidence. zh counterparts **are** Unevaluated (`尚未判定：尚未设置可检验的预期。` / `尚未判定：所需证据还没有产生`).
- `zh-claims-1280.png` / `en-claims-1280.png` show Results space + Surprise, not the claim-ledger block.
- EN workbench shots mix leftover Chinese in the right rail / motto / footer (`下一步`, `需要你确认`, `非阻塞建议`, `先做事，不打扰，人决定下一步。`) while English is selected. Current source uses `t('decision.next')` = `Next` and `t('decision.suggestions')` = `Other suggestions`; screenshot `非阻塞建议` is **not** in current source (`rg 非阻塞` only a comment). Treat as stale mixed-language shots vs current i18n, except where source still stacks (Paper `Research trace · 研究记录` appears in **both** zh and en paper 1280/1440 and **is** in source).
- zh evidence shots show heading `Choice matrix`; current zh key `evidence.matrix` is `设定对照`. Stale shot vs current dictionary.

Named relaxation used: isolated-browser limits / missing failure shots / missing 1440. These gaps alone would not REJECT. Source stacked Paper chrome **does**.

This validator did not open port 5173.

## C7 — quality gates (pass; does not override C3)

`make test` (exit 0), copied:

```
[check-api-drift] ✅ openapi.json 与后端代码同步
[check-api-drift] ✅ docs/api/openapi.json 与后端代码同步
[check-api-drift] ✅ types/api.ts 与 openapi.json 同步
819 passed, 1 skipped, 4 warnings in 32.08s
451 passed, 8 skipped, 32 warnings in 110.09s (0:01:50)
 Test Files  56 passed (56)
      Tests  403 passed (403)
[test] agent + backend + frontend 全部通过
```

No new skip vs contract evidence (agent 1 skipped, backend 8 skipped, frontend 0 skipped). Frontend 403 vs earlier 395 is added tests, not skips.

Surprise semantics this validator re-ran:

```bash
PYTHONPATH="$(pwd):$(pwd)/backend" backend/.venv/bin/python -m pytest -v --tb=line -p no:cacheprovider \
  --basetemp=$(mktemp -d /tmp/ep-backend-XXXXXX) \
  backend/tests/test_card_spec_run.py -k "surprise_without_criteria or surprise_ordering_mismatch"
```

```
backend/tests/test_card_spec_run.py::test_surprise_ordering_mismatch_on_real_magnitudes PASSED
backend/tests/test_card_spec_run.py::test_surprise_without_criteria_is_unevaluated PASSED
======================= 2 passed, 29 deselected in 0.06s =======================
```

`cd frontend && npx tsc --noEmit` → `TSC_EXIT:0` (no diagnostics).

`cd frontend && npm run lint` (oxlint) exit 0, copied:

```
Found 6 warnings and 0 errors.
Finished in 23ms on 139 files with 104 rules using 8 threads.
```

Warnings are `react(only-export-components)` including `htmlLangAttr` / `useT` in `i18n.tsx`. 0 errors.

`cd frontend && npm run build` exit 0, copied:

```
vite v8.2.0 building client environment for production...
✓ 501 modules transformed.
dist/index.html                     0.46 kB │ gzip:   0.30 kB
dist/assets/index-BuyQI-kR.css     48.19 kB │ gzip:  10.32 kB
dist/assets/index-Bd38TEcS.js   1,013.49 kB │ gzip: 308.50 kB
✓ built in 1.39s
```

`make check-api-drift` exit 0, copied:

```
[check-api-drift] ① 从后端代码重新导出 openapi.json
⚠ DEBUG: generated ephemeral JWT_SECRET_KEY for this process
[check-api-drift] ✅ openapi.json 与后端代码同步
[check-api-drift] ✅ docs/api/openapi.json 与后端代码同步
[check-api-drift] ② 重新生成 api.ts 并 diff
✨ openapi-typescript 7.13.0
🚀 openapi.json → /tmp/api.drift.ts [111.1ms]
[check-api-drift] ✅ types/api.ts 与 openapi.json 同步
```

A first `npx tsc` / `npm run lint` from repo root hit the dummy `tsc` shim and missing root `package.json`. Those were validator cwd mistakes, not product failures. The copied C7 programs above are the `cd frontend` re-runs.

C7 matches the contract programs. It does not prove C3.

## What would be needed for ACCEPT

Remove or language-split the stacked/hardcoded Paper Results and related chrome listed under Failures, so zh/en core path (including Paper Results) no longer shows `Research trace · 研究记录` and the other listed stacks. Re-run C3 grep + vitest; keep C7 green. Do not treat this report as a ship claim.
