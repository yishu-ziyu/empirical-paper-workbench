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

---

# Browser Journey Audit（2026-09-06 实弹走查，J–Q）

> **优先级与承接关系（superseding audit conclusion）**：上文 C1–C29 验收包（含 C14 Surprise 确定性规则 — PASS、C20 Cursor 行为 — PASS (R5)）是**旧 canonical seeded walk 的历史验收结果**，按其当时的放宽条件（R1–R6）成立，原样保留不改写。本节 J–Q 是在真实浏览器中以**第一次使用者身份**实弹走查得出的**更高优先级审计结论**：Surprise 自然语言判定失效（白名单只认 4 个固定短语）与 Agent Cursor 运行时缺陷（菱形不移动、节奏断裂、不 yield、label 脱靶）**不得再按 C14/C20 的 PASS 解读为"已完全通过"**——旧验收走的是可命中白名单的种子文案与放宽 R5 下的静止光标，与首用者输入自然语言、要求 3–4s 收束编舞的真实产品契约不是同一判据。

走查者：主 agent 本人在 ZCode 内置浏览器（IAB）+ 受管 Chrome 1440×900 中，以第一次使用者身份从空桌完整走完 Card canonical journey 23 步（含 7 个刷新点、Cursor 专项、错误注入）。**未修改任何生产代码**；唯二环境操作：① 重启 backend+runner（stdio 重定向到文件，见 J0）；② 审计浏览器 localStorage 清理/注入 `econpaper_session_id` 以模拟首用与跨浏览器恢复。

- 走查会话：`abd6efd9-bf6c-416d-9667-4016d7e43ae8`（后端真值全程用 REST 双向核对）
- 视口：IAB 主走查 1309×818（IAB 面板实际渲染尺寸；`setViewportSize(1440)` 报告值与实际渲染不符，属 ZCode 工具怪癖非产品问题）；1440×900 专项在受管 Chrome 补做（Overview/Question/Evidence/Paper 四页）
- 证据归档：`docs/acceptance/assets/card-browser-journey-audit-2026-09-06/`（11 个文件，已用 sips 核对）
- 结论速览：**B. mostly coherent but Card-specific**（依据见文末判断）

## J. Browser Journey Audit（逐步记录）

| # | 步骤 | 用户看到什么 | 唯一 primary | 下一步是否明显 | 记录 |
| --- | --- | --- | --- | --- | --- |
| 1 Empty desk | 标语+一句研究入口+3 建议 chip+深色 Try Card 按钮+底部 composer | Try Card（唯一实心深色钮）；composer 输入框默认聚焦但"开始"disabled | 是（视觉权重最高） | 无下游术语泄漏 ✓；"Card"无解释（轻 friction）；**900 高度下 composer 按钮行被折叠线截断**（i01） |
| 2 Try Card | 跳转 Question 页，Teaching case · Card 1995 徽章 | — | 是 | **首次 boot 失败 ×2**（见 J-0 环境事件）；第 3 次成功 |
| 3 RQ | 六段式研究问题卡（Outcome/Treatment/Causal threat/Candidate identification/Estimand），全部中英双注；Estimand 同时给出 OLS association 与 IV LATE | Save expectation（页内）+ 右栏"确认 Admissible Space"（双入口） | 基本明显 | 右栏在数据仍在清洗时就开始推"下一步"（轻微时序张力）；**RQ 卡上方浮着"第1/6章已批准"写作进度横幅**（上下文错位，f02） |
| 4 Expectation | 预填英文默认文本+Confidence 下拉 | Save expectation | 是 | 保存后无可见确认反馈（无 toast/状态变化），PUT 200 静默成功 |
| 5 Design | 右栏"下一步·需要你确认→查看规格空间" | 查看规格空间 | 是，引导清晰 | — |
| 6 Admissible Space | 12 条规格卡：人话理由+spec_id+维度取值 | Freeze admissible space | 是，唯一决策 | 右栏"下一步"未更新为"冻结"（重复展示旧引导） |
| 7 Freeze | Frozen 时间戳+冻结按钮 disabled+primary 变 Run specifications | Run specifications | 是 | 左栏状态同步"Admissible space frozen" ✓；后端 frozen_at 一致 ✓ |
| 8 Run specs | **无 busy 反馈**（点击后 3s 采样：状态行无变化、右栏仍"空闲"）；20s 内 12 条真实估计完成 | Run specifications | 否——**完成信号缺失** | 完成后停留 Design 页：无完成提示、无"去 Evidence"引导，右栏反而显示"当前没有阻塞决策"；左栏 Evidence 仍"暂无主结果"（对首用者＝跑了没结果）。**journey 中最大断层** |
| 9 Evidence Lab | 首屏顺序：Results space+Surprise → Choice matrix → Compare → Challenge → Claim ✓（D 通过） | 页内三个动作（Show preview/Accept challenge/Review claim） | 否——右栏不指路，用户必须自己在左栏发现 Evidence | — |
| 10 Surprise | 卡片仅显示 "Expected" + 预期原文回显；**无 Unexpected 判定、无 Observed 行** | — | — | 后端 `surprise={status:Expected,kind:null,observed:null}`——**白名单失效**（见 L/P） |
| 11 Show preview | 右栏出现 "Run this preview?"（明示 canonical stays put）；Cursor 启动，标签 "Looking" → ~60s 后变 "Experience linear ↔ quadratic" | Run Preview | 是（提案卡明确） | Cursor 12s 静止采样（见 N） |
| 12 Cursor 演示 | 高亮双行（evidence.spec.experience.linear/quadratic，语义 id） | — | — | 菱形全程停在左上角不移动 |
| 13 OLS/IV 对比 | Compare 卡：βA→βB 0.0747→0.0932 · Δ 0.0185 · 24.7%，intent "Experience functional form changed"，Changed/Unchanged 全对；**矩阵行点击（cursor-pointer）与 History 2 按钮是死交互**——刷新后 OLS↔IV identification 对比（0.0747→0.1315）无法重建 | Promote to canonical / Revert | 是 | Δ 算术正确 ✓ |
| 14 changed/unchanged | 文本正确（Changed: experience/demographics/region；Unchanged: estimator/identification） | — | — | **无视觉淡化效果**（unchanged 仅文字列出） |
| 15 Challenge | 中性文案双语（Effective F=14.14 + "强度诊断本身不能证明工具变量有效"）；点击后 1s 无 busy 提示，9s 后 Accepted | Accept challenge | 是 | 后端 resulting_runs→iv_region_dummies preview ✓ |
| 16–17 新 evidence/stale | Claim Ledger 头变 "New evidence available · 结论需要重新审视" | Review claim | 是 | evidence_revision 1→3，claim stale=True（后端确认）✓ |
| 18 Review/redraft | Review claim 纯展示展开 ✓；Review new evidence 触发后端 draft v2 | Review new evidence | 是 | v2、based_on rev3、stale 清除 ✓ |
| 19 Approve | Approve claim → Approved 徽章，按钮消失 | Approve claim | 是 | approved_by_user=True ✓ |
| 20 Promote | Claim 卡显式报 mismatch："当前 Claim 依赖 IV specification，但正式主规格不是该 IV" + **[Promote supporting specification]** + [Write Results] | Promote supporting specification | 是（mismatch 时动作就地出现，引导好） | canonical_spec_id=iv_region_dummies、coef 0.13150383…（真实 IV 公式）✓ |
| 21 Write Results | Results 章：真实数字（0.1315/0.05496/0.0168/N=3010，OLS 0.0747 对照 1.76 倍）、claim-type 诚实声明（"不就个体层面作强断言"）、Linked Evidence 面板（"证据变了正文要跟着重写"）、Research trace 折叠 | 批准本章 / 重新生成 | 是 | promote 后章节 stale（C24）→ 批准本章后 grounded 仍 False（wording/needs-regen 门），**且批准后无任何重写入口**（见 K-8） |
| 22–23 Paper→Linked Evidence | View Claim / Evidence → 回 Evidence（breadcrumb 变 Evidence、Approved 可见）✓；"查看完整证据 →"同链路 | View Claim / Evidence | 是 | 注：走查中两次"点击无跳转"为审计者坐标缩放操作误差，el.click() 复核通过（方法论更正，非产品缺陷） |

### J-0 环境事件（非产品代码缺陷，但暴露部署脆弱性）

- **Card boot 前两次失败（BrokenPipeError: upload_pipeline execution failed，1 秒内 accept→claim→fail，trace 空）**：根因＝runner 进程的 stdout/stderr 指向已死的管道（lsof 证实 fd1/fd2 同一 PIPE；读端是上一个 ZCode 会话的 shell，会话退出后管道断裂）。runner 平时不写 stdout 所以活着，**一旦执行 run 就写进度→BrokenPipe→run 被标 FAILED**。14:10 同进程成功、14:27 起全挂的时间线吻合。stdio 重定向到文件后第 3 次 boot 成功。
  - 审计含义：① 失败横幅"数据处理失败，请重新选择文件"与左栏"Data card_1995.csv·3010 行"、右栏"run 2969cbbd **仍在进行**，恢复后从这里接上"、右栏"下一步：确认 Admissible Space"**同屏四种矛盾信号**（i02）；② 无"重试 Card"入口（只有 重新选择文件/上传数据，都会脱离教学案例）；③ 会话视图内**没有任何回空桌/新论文入口**（"+ 新论文"只在空桌有，面包屑"项目"点击无效，URL `/` 恢复上次会话）——首用者只有清 localStorage 才能回到空桌。
- 跨浏览器恢复：把 `econpaper_session_id` 写入另一个干净浏览器的 localStorage → 完整恢复同一研究（含 Evidence/Paper 状态）。状态所有权在后端这一点经三种浏览器环境验证。

## K. First-time User Friction Log

1. **"Card" 不可解释**：空桌唯一深色按钮 "Try a real study · Card"，Card 是内部代号，无 tooltip/副标题。
2. **Run specifications 静默 20 秒**：点击后无 busy 态、无完成态、无去向引导；右栏说"当前没有阻塞决策"。首用者最可能此刻流失（我本人也在此刻停下来翻左栏）。
3. **Surprise 沉默**：改写自己的预期（产品鼓励"我会保留你的原话"）后，Surprise 卡退化为 "Expected"——高光时刻直接消失，且**无任何解释**。
4. **矩阵行/History 2 死交互**：cursor-pointer 假可供性，点击无效果；Compare 卡刷新后退回 "Select two specifications to compare." 且无控件可重建。
5. **无回桌入口**：会话视图内没有 "+ 新论文"/回空桌路径；失败态也没有"重试 Card"。
6. **Overview "主方法 — 未设定"**：冻结 12 条规格后立即看 Overview 仍写"未设定"（指 canonical 未 promote，但字面矛盾）。
7. **Review claim 双入口语义**：stale 时 "Review claim"（纯展示）与 "Review new evidence"（触发后端）按钮文案相似，首用者不易分清哪个才产生新版本。
8. **批准后的 stale 章节无出口**：章节 approved 且 grounded=False（needs-regeneration），但 重新生成/编辑/回滚 全部消失——"证据变了正文要跟着重写"的承诺没有兑现路径（未穷尽 Writing/Preview/History 三个 tab，谨慎表述为"当前视图无入口"）。
9. **静默失败**（见 E）：保存失败无任何提示。
10. 小项：composer 在 900 高度折叠线以下；"Technical details" 折叠里藏着方法/期刊/学位选择器（位置与命名可疑）；Question 页混入"第1/6章已批准"横幅；表单字段缺 id/name（a11y issue ×7）。

## L. Context Leaks

- **Question/Design 页**：右栏无 IV>OLS/Show me/Evidence challenge 泄漏 ✓（逐页核对）。
- **Evidence 页**：无 Question 阶段动作 ✓。
- **Paper 页**：正文+审批+Linked Evidence ✓；"第1/6章已批准，下一章：引言"横幅**出现在 RQ 页**（写作状态回流到研究问题面——轻度错位）。
- **Surprise 白名单**不算页面泄漏，但属于"上下文感知失灵"：系统在数据与预期明显矛盾时仍宣布 "Expected"，向用户输出与事实相反的研究状态。
- Rail 内无 Evidence 专属动作（契约预期 Show me/Challenge 进 rail；当前构建这些动作只在页内或缺失）——与契约 C 有出入，但无"错误上下文"泄漏。
- 左栏各页状态与后端一致（暂无主结果→β 0.1315 语义自洽）；`/degradation` 高频轮询（~15 次/2 分钟）是噪音非泄漏。

## M. Recovery / Refresh Findings（7 个刷新点全测）

| 刷新点 | 结果 | 备注 |
| --- | --- | --- |
| A1 Expectation 保存后 | **PASS** | 中文预期完整恢复；localStorage 无业务状态伪造（符合 C7） |
| A2 Freeze 后 | **PASS** | 会话恢复但**视图落 Overview**（不记忆上次页面；确定性落点，轻微摩擦） |
| A3 Runs 后 | **PASS**（状态）/ 见 J-8（完成信号缺失是产品问题，不是恢复问题） | 左栏 Evidence"暂无主结果"与 12 runs 并存的语义张力 |
| A4 Challenge 后 | **PASS** | Accepted + "New evidence available" + Preview·2 runs 去重全部恢复 |
| A5 Approve 后 | **PASS** | Approved 徽章、stale 清除 |
| A6 Promote 后 | **PASS** | 左栏 Evidence 升级为 "β 0.1315"；mismatch 消失 |
| A7 Results 后 | **PASS** | 章节正文（含全精度系数）与 1/6 状态保留；Teaching badge 持续 |
| 加分项：跨浏览器恢复 + IAB guest 崩溃恢复（两次 about:blank 重置） | **PASS** | 唯一 localStorage 业务指针 `econpaper_session_id`，其余全后端——架构主张兑现 |

**结论：刷新恢复机制全部通过，无前端 local state 伪造恢复的迹象。**

## N. Agent Cursor Interaction Findings

实测事实（对照契约 C17–C20 与 card-ux-coherence 第 3 条）：

| 检查项 | 结果 | 证据 |
| --- | --- | --- |
| 语义目标契约（拒绝坐标/CSS/XPath） | ✓ | 高亮/光标均为 `data-testid=agent-cursor-highlight-<semantic-id>`（evidence.spec.experience.linear/quadratic、evidence.choice.experience）；control.ts 拒绝坐标 |
| 自动选中 OLS→IV | **未观察到** | Show preview 流只做 experience-form 对比（0.0747→0.0932）；OLS↔IV identification 对比需要手动，且刷新后无法重建 |
| Compare 自动出现 | ✓ | preview 运行后 Compare 卡自动出现，Δ 算术正确 |
| Δ 正确 | ✓ | 0.0932−0.0747=0.0185，24.7% |
| unchanged 淡化 | ✗ | 仅文字 "Unchanged: estimator, identification"，无视觉淡化 |
| estimator/identification 指出 | ✓（文字） | intent "Experience functional form changed" 正确对应实际变化 |
| Cursor label 贴目标 | **部分** | 高亮框贴合目标行（getBoundingClientRect 证实）；**菱形光标本体全程不动**（初始 24,96 → 结束仍在附近），标签随动画留在左上角 |
| scroll/resize 后仍贴合 | **半通过** | 高亮框 refit ✓（滚动后 443/382px 落在视口内）；**label 脱靶** ✗（i13：标签悬在左上角栏上） |
| 用户输入 yield | ✗ | 可信 cua pointer/keyboard 输入后 transform 无变化、无 paused 属性 |
| replay | 半通过 | Replay 重启脚本（label 回 "Little changed"）但 8s 内无步进 |
| cancel | ✓（视觉） | 控件移除、opacity→0；layer DOM 残留（不可交互，小瑕疵） |
| 节奏 | ✗ **严重偏离设计** | 契约"约 3-4s 收束"；实测首演 "Looking" 静止 ≥12s、整脚本 ~60s 级推进；Replay 8s 零推进 |
| "只看 Cursor+UI 变化能否理解结果为何变化" | **弱** | 光标不移动+节奏断裂后，只剩高亮框和 Compare 文字在讲故事；不看右栏文字的用户能靠高亮行猜到"这两行变了"，但"为什么变"的因果链几乎完全依赖文字 |

## E. Error / recovery（补充在 K 之外单列）

注入 PUT /research/expectation → 503（页面级 fetch 补丁，非破坏性）：

- UI **不假成功** ✓（无成功 toast）；
- 后端真值未被污染 ✓（version 2 原文不变）；
- 但**完全静默**：无错误提示、无重试指引，textarea 保留未保存文本让用户误以为已保存；同时抛出 `unhandledrejection: Error: HTTP 503`（未接管的 promise rejection）。
- Card boot 真实失败场景见 J-0（矛盾信号 + 无重试入口）。

## F. Browser technical evidence

- console（1440 受管 Chrome 全程）：无 uncaught exception、无 React 错误；唯一 error 为匿名模式 `/api/auth/me` 401 ×2（噪音）；a11y issue "form field should have id or name" ×7；vite dev 日志若干。
- network：业务请求全部 200/304；`/degradation` 高频轮询；**字体来自 fonts.googleapis.com/gstatic**（运行时外网依赖，离线/受限网络下衬线排版会退化——部署面风险）。
- 布局：document 级 `scrollWidth==clientWidth` 在 Overview/Question/Evidence/Paper 四页（1309 与 1440 两档）均成立，无横向溢出元素；1440 下 Question 页 header 副标题处有一灰色叠层残影（f02，小视觉瑕疵）。
- IAB 工具怪癖（非产品问题）：视口设置与实际渲染不符、guest 两次重置、合成 click 挂起（全程用原生 el.click()+IIFE evaluate 规避）。

## O. Top 5 moments of product value

1. **Freeze 的一瞬间**：12 条规格卡从"提案"变成"承诺"，primary 明确切换为 Run specifications，左栏状态同步——"先冻结再看结果"的纪律被 UI 落实。
2. **Evidence Lab 首屏**：散点图里 OLS 灰点与 IV 蓝点肉眼分离，预期原文回显在卡上——"证据优先"的第一印象成立（顺序 D 通过）。
3. **Challenge→stale→redraft 链**：点 Accept 后右栏立即"Accepted"、Claim 头变"New evidence available"、Review new evidence 生成 v2（based_on rev3）——证据修订→结论重审的因果链真实可见，全程后端持有。
4. **Promote mismatch 引导**："当前 Claim 依赖 IV specification，但正式主规格不是该 IV"+ 一键 Promote supporting specification——canonical 语义被翻译成了首用者能懂的一句话。
5. **Results 章的诚实**：真实数字（0.1315/0.0550/0.0168/N=3010）+ "主张类型为 association，不就个体层面作强断言" + Linked Evidence "证据变了正文要跟着重写" + 未 grounded 徽章不撒谎——这是整个产品最"像研究工具"的一段。

## P. Top 5 moments of confusion

1. **Run specifications 点击后的 20 秒真空**（J-8）：无 busy、无完成、无去向；右栏"当前没有阻塞决策"与 12 条正在跑的估计并存。
2. **自己改写预期后 Surprise 消失**（L/P 核心）：关键词白名单只认 4 个短语（"iv may be smaller"/"iv smaller"/"iv 可能比 ols 更小"/"iv可能比ols更小"，research_lab.py:576-587），"IV 应该更小…"不命中——首用者的个性化输入**静默杀死**产品最高光机制，且卡上没有任何"为什么没意外"的解释。
3. **失败态的四种矛盾信号**（J-0，i02）：红条说失败、左栏说数据在、右栏说仍在进行、下一步说去冻结——首用者无从判断该信哪个，也没有重试 Card 的路径。
4. **Cursor 的存在感悖论**：一个不移动的光标 + 超长静止（≥12s "Looking"）+ 脱靶标签——用户会怀疑它坏了（本次审计中确实像坏了），比没有更糟。
5. **死可供性三连**：矩阵行 cursor-pointer 无效果、History 2 无效果、会话内无回桌入口——每次都让用户怀疑自己点错了地方。

## Q. What breaks when imagining the same journey as DiD

把 Card journey 原样想象成 DiD（政策评估前后对比）走一遍，按当前实现会断在这里：

1. **Surprise 白名单是 Card 专属文案**：`_mentions_iv_smaller/_larger/_similar/_positive` 只覆盖 IV/OLS 排序叙事。DiD 的预期语言（"政策后应上升""平行趋势若成立"）没有任何匹配 token→Surprise 恒为 "Expected"，Show me/Challenge 的触发链随之消失。这条要泛化，判定必须从关键词白名单换成结构化 estimand（预期方向/对象/比较关系建模），而不是继续加短语。
2. **Challenge 是单剧本**：当前只有一个 scripted challenge（工具变量强度，Effective F=14.14 来自 IV 诊断）。DiD 需要 parallel-trends/pre-trend/事件研究诊断类 challenge；next_challenge 的生成器目前没有这类条目，接受挑战后能产出的 preview run 也只有 Card 空间里的规格。
3. **Agent Cursor 是固定 10 步 Card 脚本**（OLS 定位→IV 定位→对比→Δ→unchanged→intent 收束），DiD 没有"OLS vs IV"两簇可指——脚本无对象可演示；且实测其节奏/移动/yield 已坏，换方法前需先修。
4. **Claim 措辞三档与 RQ 卡的六字段**是association/IV 叙事模板；DiD 的 claim（ATT、treatment timing、平行趋势假设清单）需要另一套 unresolved-assumptions 与 Supported 措辞模板，当前 wording_exceeds_evidence 的判定域也是按这套模板写的。
5. **规格空间的维度枚举**（estimator/experience/demographics/region）写死于 Card 演示空间；DiD 的关键维度（treatment timing、cluster 层级、平行趋势敏感性）不在 Admissible Space 的语义里——冻结页可以渲染，但人话理由与"changed/unchanged"归因逻辑都基于这套枚举。
6. 顺带成立的部分：后端持有状态、evidence_revision/stale/promote 语义、Results grounded 门——这些是方法无关的，DiD 可以直接继承（这也是 verdict 给到 B 而非 A 的原因）。

---

## 最终判断

**当前 Card journey 是：B. mostly coherent but Card-specific。**

依据：

- **为什么不是 A（demo only）**：整条链的状态真值全部由后端持有并真实执行——7 个刷新点+跨浏览器+两次浏览器崩溃恢复全部通过；12 条规格是真实估计（系数随设定合理变动）；challenge 产出真实 preview run 并真实推动 evidence_revision 1→3、claim v1→v2、stale→redraft→approve、promote 改写 canonical、Results grounded 门真实咬合（批准≠grounded，needs-regeneration 生效）。这些不是演示贴纸，是可复用的研究状态机——A 评价不成立。
- **为什么还不到 C（genuinely reusable research loop）**：让一个研究者跑**自己的**研究时，这条 loop 的三个关键环节是 Card 形状的——① Surprise/Show me 链依赖白名单短语，个性化预期静默失效（本次走查实测：改一条自然的中文预期，Surprise 体验归零）；② Agent Cursor 节奏/移动/yield 坏了（且没有非 Card 的 Show me 入口）；③ Run→Evidence 交接真空、失败态矛盾信号、四处死可供性会把真实用户卡在和我一样的地方。加上单剧本 challenge、固定 cursor 脚本、"只认四种说法"的判定层——loop 的骨架可复用，**把骨架连起来让陌生研究也能跑通的肉还长在 Card 上**。
- **B 的准确含义**：作为 Card 教学案例，这条 journey 大体连贯、证据优先、状态诚实，最高光的五段（O）都成立；但要变成" reusable research loop"，需要把 surprise 判定结构化、把运行反馈补齐、把 cursor 节奏修好、把死交互清掉——这四件事做完之前，换一个数据集或换一种方法，体验会塌回表单+表格。

### 审计方法附注

- 视口：IAB 面板实际渲染 1309×818（工具限制，非产品）；1440×900 专项在受管 Chrome 完成。
- 早期两次"按钮无响应"的坐标点击后经 el.click() 复核为审计者工具缩放误差（raster 缩放），**已撤回相应产品结论**；矩阵行/History 死交互结论用 el.click() 复核后维持。
- 汇报中"busy 反馈缺失"基于 1s/3s/9s 采样帧，未排除极短暂指示；标注为采样级证据。
